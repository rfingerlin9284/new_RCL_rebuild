#!/usr/bin/env python3
"""Unified CLI controller for the RICK multi-platform trading stack."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from textwrap import dedent
from typing import Callable, Dict, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
LOGS_DIR = ROOT / "logs"
ENV_CANDIDATES = [
    ".env.oanda_only",
    ".env.coinbase_advanced",
    "env_new2.env",
    ".env",
]
OANDA_API_BASE = {
    "practice": "https://api-fxpractice.oanda.com",
    "live": "https://api-fxtrade.oanda.com",
}

MenuFunc = Callable[[], None]


def load_env_files() -> List[str]:
    loaded: List[str] = []
    for name in ENV_CANDIDATES:
        path = ROOT / name
        if not path.exists():
            continue
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if line.lower().startswith("export "):
                line = line.split(" ", 1)[1]
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ[key.strip()] = value.strip().strip('"').strip("'")
        loaded.append(name)
    return loaded


def run_process(cmd: Sequence[str], label: str, check: bool = False) -> int:
    print(f"\n=== {label} ===")
    try:
        result = subprocess.run(cmd, cwd=ROOT, check=check)
    except FileNotFoundError as exc:
        print(f"❌ Missing executable: {exc}")
        return 1
    except subprocess.CalledProcessError as exc:
        print(f"❌ {label} failed with code {exc.returncode}")
        return exc.returncode
    else:
        print(f"✅ {label} completed")
        return result.returncode


def start_all_platforms() -> None:
    load_env_files()
    run_process(["python3", "auto_diagnostic_monitor.py", "--full-check"], "Full system diagnostic")

    launches = [
        ("OANDA (integrity guarded)", ["bash", "start_with_integrity.sh"]),
        ("Coinbase Safe Mode (paper)", ["python3", "coinbase_safe_mode_engine.py"]),
    ]
    ib_engine = ROOT / "ibkr_gateway" / "ibkr_trading_engine.py"
    if ib_engine.exists():
        launches.append(("IBKR Gateway", ["python3", str(ib_engine)]))

    for label, command in launches:
        try:
            subprocess.Popen(command, cwd=ROOT)
            print(f"🚀 {label} launch requested")
        except FileNotFoundError as exc:
            print(f"⚠️ Skipped {label}: {exc}")


def ensure_requests() -> bool:
    try:
        import requests  # noqa: F401
    except Exception as exc:  # pragma: no cover
        print(f"❌ requests import failed: {exc}")
        return False
    return True


def resolve_oanda_credentials() -> Optional[Tuple[str, str, str]]:
    practice_token = os.environ.get("OANDA_PRACTICE_TOKEN")
    practice_account = os.environ.get("OANDA_PRACTICE_ACCOUNT_ID")
    live_token = os.environ.get("OANDA_LIVE_TOKEN")
    live_account = os.environ.get("OANDA_LIVE_ACCOUNT_ID")
    if practice_token and practice_account:
        return "practice", practice_token, practice_account
    if live_token and live_account:
        return "live", live_token, live_account
    return None


def close_all_oanda_positions() -> None:
    load_env_files()
    if not ensure_requests():
        return
    creds = resolve_oanda_credentials()
    if creds is None:
        print("❌ OANDA credentials not found in environment")
        return
    env_name, token, account = creds
    import requests  # type: ignore
    base = OANDA_API_BASE[env_name]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"🔴 Closing all {env_name.upper()} OANDA positions for account {account}")
    url = f"{base}/v3/accounts/{account}/openPositions"
    try:
        response = requests.get(url, headers=headers, timeout=10)
    except Exception as exc:
        print(f"❌ Failed to query positions: {exc}")
        return
    if response.status_code != 200:
        print(f"❌ API error {response.status_code}: {response.text}")
        return
    positions = response.json().get("positions", [])
    if not positions:
        print("✅ No open positions to close")
        return
    for pos in positions:
        instrument = pos.get("instrument")
        close_url = f"{base}/v3/accounts/{account}/positions/{instrument}/close"
        payload = {"longUnits": "ALL", "shortUnits": "ALL"}
        try:
            resp = requests.put(close_url, headers=headers, json=payload, timeout=10)
        except Exception as exc:
            print(f"❌ Close {instrument} failed: {exc}")
            continue
        if resp.status_code == 200:
            print(f"✅ Closed {instrument}")
        else:
            print(f"⚠️ {instrument} close response {resp.status_code}: {resp.text}")


def show_oanda_positions() -> None:
    load_env_files()
    if not ensure_requests():
        return
    creds = resolve_oanda_credentials()
    if creds is None:
        print("❌ OANDA credentials not found in environment")
        return
    env_name, token, account = creds
    import requests  # type: ignore
    base = OANDA_API_BASE[env_name]
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{base}/v3/accounts/{account}/openPositions"
    try:
        response = requests.get(url, headers=headers, timeout=10)
    except Exception as exc:
        print(f"❌ Failed to query positions: {exc}")
        return
    if response.status_code != 200:
        print(f"❌ API error {response.status_code}: {response.text}")
        return
    positions = response.json().get("positions", [])
    if not positions:
        print("✅ No open OANDA positions")
        return
    print(f"\n{env_name.upper()} OANDA Positions (account {account})")
    print("Instrument        Units        Avg Price    Unrealized P&L")
    print("-" * 56)
    for pos in positions:
        instrument = pos.get("instrument", "?")
        long_side = pos.get("long", {})
        short_side = pos.get("short", {})
        if float(long_side.get("units", "0")) != 0:
            units = float(long_side.get("units", "0"))
            price = float(long_side.get("averagePrice", "0"))
            pnl = float(long_side.get("unrealizedPL", "0"))
        else:
            units = float(short_side.get("units", "0"))
            price = float(short_side.get("averagePrice", "0"))
            pnl = float(short_side.get("unrealizedPL", "0"))
        print(f"{instrument:<16}{units:>10.0f}    {price:>12.5f}    {pnl:>14.2f}")
    print("-" * 56)


def run_hive_reassessment() -> None:
    run_process(["python3", "hive_position_advisor.py"], "Hive mind position reassessment")


def run_full_audit() -> None:
    script = ROOT / "scripts" / "auto_memory_backup.sh"
    if script.exists():
        run_process(["bash", str(script)], "Auto memory backup")
    else:
        print("⚠️ auto_memory_backup.sh not found")
    run_process(["python3", "memory_baseline.py", "audit"], "Baseline audit")


def run_quick_status() -> None:
    summary = {
        "engines": {},
        "logs": {},
    }
    processes = {
        "oanda_trading_engine.py": "OANDA Engine",
        "coinbase_safe_mode_engine.py": "Coinbase Engine",
        "ibkr_trading_engine.py": "IBKR Gateway",
    }
    for pattern, label in processes.items():
        code = subprocess.run(["pgrep", "-af", pattern], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        summary["engines"][label] = "RUNNING" if code.returncode == 0 else "STOPPED"
    perf_file = LOGS_DIR / "safe_mode_performance.json"
    if perf_file.exists():
        try:
            payload = json.loads(perf_file.read_text())
        except json.JSONDecodeError:
            summary["logs"]["safe_mode_performance"] = "Corrupt JSON"
        else:
            summary["logs"]["safe_mode_performance"] = payload
    else:
        summary["logs"]["safe_mode_performance"] = "Not found"
    print("\nENGINE STATUS")
    for label, state in summary["engines"].items():
        emoji = "🟢" if state == "RUNNING" else "🔴"
        print(f"  {emoji} {label}: {state}")
    print("\nSAFE MODE PERFORMANCE")
    perf = summary["logs"].get("safe_mode_performance")
    if isinstance(perf, dict):
        print(json.dumps(perf, indent=2))
    else:
        print(perf)


def run_full_diagnostic() -> None:
    run_process(["python3", "auto_diagnostic_monitor.py", "--full-check"], "Full system diagnostic")


def show_menu(options: Dict[str, Tuple[str, MenuFunc]]) -> None:
    banner = dedent(
        """
        ================================================================================
        🧠 RICK CONTROL CENTER — PIN 841921 REQUIRED FOR LIVE ACTIONS
        ================================================================================
        Select an option to orchestrate the trading system:
        """
    )
    while True:
        print(banner)
        for key, (label, _) in options.items():
            print(f"  {key}. {label}")
        print("  X. Exit")
        choice = input("\nChoice: ").strip().upper()
        if choice == "X":
            print("👋 Goodbye")
            return
        if choice in options:
            _, handler = options[choice]
            handler()
            input("\nPress Enter to return to the menu...")
        else:
            print("❌ Invalid choice")
            input("Press Enter to try again...")


def main() -> None:
    if not sys.stdin.isatty():
        print("❌ Interactive terminal required")
        sys.exit(1)
    load_env_files()
    options: Dict[str, Tuple[str, MenuFunc]] = {
        "1": ("Launch Coinbase + OANDA + IBKR (diagnostic + start)", start_all_platforms),
        "2": ("Run full diagnostic suite", run_full_diagnostic),
        "3": ("Capture audit + snapshot receipts", run_full_audit),
        "4": ("Close all OANDA positions", close_all_oanda_positions),
        "5": ("Show OANDA open positions", show_oanda_positions),
        "6": ("Manual hive mind reassessment", run_hive_reassessment),
        "7": ("Quick status overview", run_quick_status),
    }
    show_menu(options)


if __name__ == "__main__":
    main()
