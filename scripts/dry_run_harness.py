#!/usr/bin/env python3
"""Dry-run harness for the RICK pipeline
========================================

This harness simulates a single autonomous cycle without placing live orders.
It exercises strategy selection, dynamic leverage calculation, OCO fallback, and
guardian charter gating. The goal is to validate logic end-to-end in a safe,
paper/dry-run mode, logging all decisions in narration.log.
"""

from __future__ import annotations

import random
import argparse
import time
from typing import List

from config.narration_logger import get_narration_logger
from hive.strategy_selector import get_strategy_selector
from risk.dynamic_leverage import DynamicLeverageCalculator
from risk.smart_trailing import maybe_extend_take_profit, should_trail
from foundation.rick_charter import RickCharter
from hive.guardian_gates import apply_all_gates


def sample_price_history(base: float = 1.1000, length: int = 120) -> List[float]:
    """Generate a synthetic price history with small random walk."""
    prices = [base]
    for _ in range(length - 1):
        last = prices[-1]
        last = last + random.uniform(-0.0005, 0.0007)
        prices.append(round(last, 6))
    return prices


def compute_oco_from_prices(entry_price: float, direction: str, prices: List[float]) -> (float, float):
    """Compute conservative SL and TP using naive ATR-like measure and charter rule.

    Returns (sl, tp). Ensures RR >= RickCharter.MIN_RISK_REWARD_RATIO.
    """
    import numpy as np
    vol = float(np.std(np.diff(prices))) if len(prices) > 1 else 0.001
    atr = max(0.0002, vol * (RickCharter.FX_STOP_LOSS_ATR_MULTIPLIER if hasattr(RickCharter, 'FX_STOP_LOSS_ATR_MULTIPLIER') else 1.2))
    if direction.lower() == 'buy':
        sl = entry_price - atr
        tp = entry_price + (atr * RickCharter.MIN_RISK_REWARD_RATIO)
    else:
        sl = entry_price + atr
        tp = entry_price - (atr * RickCharter.MIN_RISK_REWARD_RATIO)
    return round(sl, 6), round(tp, 6)


def run_dry_cycle(iterations: int = 1):
    logger = get_narration_logger()
    selector = get_strategy_selector()
    dlc = DynamicLeverageCalculator()

    for it in range(iterations):
        logger.narrate_info("DRY_RUN_START", {"iteration": it + 1})
        prices = sample_price_history(1.1050, length=120)
        active = selector.select_active_strategies({"market": "fx", "regime": "bull"}, max_strategies=1)
        for sid in active:
            # simulate inputs
            confidence = random.uniform(0.7, 0.95)
            rec = dlc.calculate_for_signal("EUR_USD", confidence, prices, account_balance=25000.0, current_positions=0)
            quantity = rec.position_size if hasattr(rec, 'position_size') else rec.get('position_size', 1000)
            entry = prices[-1]
            sl, tp = compute_oco_from_prices(entry, "buy", prices)

            # Charter & Gate checks
            # Compose a payload similar to a real candidate
            candidate = {
                "symbol": "EURUSD",
                "direction": "buy",
                "quantity": quantity,
                "broker": "oanda",
                "entry_price": entry,
                "stop_loss": sl,
                "take_profit": tp,
                "source_strategy": sid,
            }

            # Check guardian gates (this is read-only and safe)
            gates_ok, reason = apply_all_gates(symbol=candidate["symbol"], direction=candidate["direction"], size=candidate["quantity"], broker=candidate['broker'])
            logger.narrate_guardian_gate(candidate['symbol'], gates_ok, {"reason": str(reason)})

            if not gates_ok:
                logger.narrate_info("DRY_RUN_CANDIDATE_REJECTED", {"candidate": candidate, "reason": reason})
                continue

            # Smart trailing check
            position_state = {
                "unrealized_rr": 1.2,
                "time_in_minutes": 6.0,
                "side": "buy",
            }
            hive_signals = {"momentum_score": confidence, "consensus": confidence, "regime": "momentum"}
            trail_on = should_trail(position_state, hive_signals)
            td, extended, reason = (None, False, None)
            try:
                new_tp, activated, why = maybe_extend_take_profit({"entry_price": entry, "stop_loss": sl, "take_profit": tp, "direction": "buy"}, confidence, {"momentum_score": confidence, "hive_consensus": confidence, "regime": "momentum"})
                td = new_tp
                extended = activated
                reason = why
            except Exception:
                pass

            logger.narrate_info("DRY_RUN_CANDIDATE_PASS", {"candidate": candidate, "dynamic_leverage": rec.__dict__ if hasattr(rec, '__dict__') else rec, "trail_enabled": bool(trail_on), "tp_extended": extended, "extended_tp": td, "reason": reason})

        # short sleep between cycles
        time.sleep(0.25)
    logger.narrate_info("DRY_RUN_COMPLETE", {"iterations": iterations})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dry-run harness for RICK autonomous simulation")
    parser.add_argument("--cycles", type=int, default=1, help="Number of cycles to execute")
    args = parser.parse_args()
    run_dry_cycle(iterations=args.cycles)
#!/usr/bin/env python3
"""Dry-run harness to simulate autonomous candidate processing and manual trade flow.

This script exercises:
- AutonomousController candidate processing path (charter + gates + router)
- Manual trade submit + execute path (unified router)
- PositionManager monitoring loop (runs briefly)
- Prints recent narration log lines for operator inspection

Run from repository root: python3 scripts/dry_run_harness.py
"""

import time
import json
import os
import sys

# Ensure repository root is on sys.path so imports like `config.*` resolve
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from config.narration_logger import get_narration_logger




def main():
    print("Starting dry-run harness...")
    # Import modules lazily to avoid circular import issues
    from config.enhanced_task_config import get_enhanced_task_config, TradeParameters
    from orchestration.autonomous_controller import get_autonomous_controller
    from position_manager import get_position_manager

    cfg = get_enhanced_task_config()
    controller = get_autonomous_controller()
    pm = get_position_manager()
    narr = get_narration_logger()

    # Start position monitoring (daemon thread)
    pm.start_monitoring()

    # Show initial status
    print(cfg.execute_action(cfg.action_verify_status.__self__ if hasattr(cfg.action_verify_status, '__self__') else cfg.action_verify_status))

    # 1) Simulate autonomous candidate processing using a valid candidate
    candidate = {
        "symbol": "EURUSD",
        "direction": "buy",
        "quantity": 15000,
        "broker": "oanda",
        "entry_price": 1.1000,
        "stop_loss": 1.0900,
        "take_profit": 1.1400,
        "order_type": "market",
    }

    print("\nProcessing autonomous-style candidate (should pass charter if gates OK)...")
    try:
        # Call private processor for testing purposes
        controller._process_candidate(candidate)
    except Exception as e:
        print(f"Error processing candidate: {e}")

    time.sleep(1)

    # 2) Submit a manual trade and attempt execution (approved flow)
    print("\nSubmitting manual trade plan and executing if allowed...")
    tp = TradeParameters(
        symbol="EURUSD",
        direction="buy",
        quantity=15000,
        entry_price=1.1000,
        stop_loss=1.0900,
        take_profit=1.1400,
        risk_percent=2.0,
        broker="oanda",
    )

    plan = cfg.submit_manual_trade(tp)
    print("Hive plan preview:\n", plan)

    ok, msg = cfg.execute_approved_manual_trade(tp)
    print("Execution result:", ok, msg)

    # Let position manager run one more cycle
    time.sleep(2)

    # Print last narration lines
    print("\nRecent narration events:")
    narr.print_tail(30)

    # Stop monitoring to clean up
    pm.stop_monitoring()
    print("Dry-run harness completed.")


if __name__ == "__main__":
    main()
