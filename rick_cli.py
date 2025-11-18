"""
RICK INTERACTIVE CLI
====================
Command-line interface with dropdown menus and real-time narration

Extras:
- --autostart: automatically perform menu actions 1, 3, 5, 6 while running
    (Start system, Verify status on interval, Reassess positions every 60s,
     Stream narration in background)
"""

import sys
import argparse
from typing import Optional
import json
from config.enhanced_task_config import (
    get_enhanced_task_config,
    SystemAction,
    TradeParameters
)
from config.narration_logger import get_narration_logger
import threading
import time
from orchestration.autonomous_controller import get_autonomous_controller
from risk.dynamic_leverage import DynamicLeverageCalculator
from validate_system import run_health_check


class RICKInteractiveCLI:
    """Interactive CLI for RICK system"""
    
    def __init__(self):
        self.config = get_enhanced_task_config()
        self.narration = get_narration_logger()
        self.running = True
        self._auto_threads_started = False
        self._autonomous = get_autonomous_controller()
        self._operator_menu = self._load_operator_menu()

    def _load_operator_menu(self):
        try:
            with open("config/operator_task_config.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            self.narration.narrate_error("OPERATOR_MENU_ERROR", str(e))
            return None
    
    def display_banner(self):
        """Display system banner"""
        print("""
╔════════════════════════════════════════════════════════════════════════════════╗
║                                                                                ║
║                  🤖 RICK HIVE MIND COLLECTIVE TRADING 🤖                       ║
║                                                                                ║
║                        Approval 841921 - LIVE SYSTEM                          ║
║                                                                                ║
║   Autonomous AI Trading | Real-Time Position Management | Closed-Loop Learning║
║                                                                                ║
╚════════════════════════════════════════════════════════════════════════════════╝
""")
    
    def display_main_menu(self):
        """Display main action dropdown (legacy + operator view)."""
        print("\n" + "="*80)
        title = "📋 SELECT ACTION (Dropdown Menu #1)"
        if self._operator_menu and self._operator_menu.get("menu_title"):
            title = self._operator_menu["menu_title"]
        print(title)
        print("="*80)
        print("1) ▶️  START - Initialize system and begin trading")
        print("2) ⏹️  STOP - Shutdown system gracefully")
        print("3) 📊 VERIFY STATUS - Check system health")
        print("4) 👤 MANUAL TRADE - Input custom trade parameters")
        print("5) 📈 REASSESS POSITIONS - Check all open trades")
        print("6) 📜 VIEW NARRATION LOG - Stream real-time events")
        print("7) 🔧 SETTINGS - Configure system parameters")
        print("8) 🌐 OPEN HIVE WEB UI - Browser interface")
        print("9) ❌ EXIT - Quit RICK CLI")
        print("="*80)
        
        choice = input("\nEnter your choice (1-9): ").strip()
        return choice
    
    def handle_choice(self, choice: str):
        """Handle menu choice"""
        if choice == "1":
            self.action_start()
        elif choice == "2":
            self.action_stop()
        elif choice == "3":
            self.action_verify_status()
        elif choice == "4":
            self.action_manual_trade()
        elif choice == "5":
            self.action_reassess()
        elif choice == "6":
            self.action_view_narration()
        elif choice == "7":
            self.action_settings()
        elif choice == "8":
            self.action_open_web_ui()
        elif choice == "9":
            self.action_exit()
        else:
            print("❌ Invalid choice. Please select 1-9.")

        # If operator task config is present, offer mapped actions
        if self._operator_menu:
            self._handle_operator_actions(choice)

    def _handle_operator_actions(self, choice: str):
        """Map numeric choice to operator actions when configured."""
        try:
            items = self._operator_menu.get("items", [])
            for item in items:
                if str(item.get("id")) == choice:
                    action = item.get("action")
                    if action == "start_autonomous":
                        self._operator_start_autonomous()
                    elif action == "stop_autonomous":
                        self._operator_stop_autonomous()
                    elif action == "manual_trade_entry":
                        self.action_manual_trade()
                    elif action == "run_health_check":
                        self._operator_health_check()
                    elif action == "tail_narration":
                        self.action_view_narration()
                    elif action == "switch_broker":
                        self._operator_switch_broker()
                    elif action == "show_positions":
                        self._operator_show_positions()
                    elif action == "exit_console":
                        self.action_exit()
                    break
        except Exception as e:
            self.narration.narrate_error("OPERATOR_ACTION_ERROR", str(e))

    # ----- Operator-specific helpers -----

    def _operator_start_autonomous(self):
        print("\n🟢 Starting AUTONOMOUS trading mode")
        self._autonomous.start_autonomous()

    def _operator_stop_autonomous(self):
        print("\n🔴 Pausing AUTONOMOUS trading mode")
        self._autonomous.stop_autonomous()

    def _operator_health_check(self):
        print("\n" + "="*80)
        print("🩺 SYSTEM HEALTH CHECK")
        print("="*80)
        # Prefer the richer summary wrapper when available
        try:
            from validate_system import run_health_check_with_summary
            results, summary = run_health_check_with_summary()
            print(summary)
            for key, info in results.items():
                status = "✅" if info.get("ok") else "❌"
                print(f"{status} {key}: {info.get('detail')}")
        except Exception:
            results = run_health_check()
            for key, info in results.items():
                status = "✅" if info.get("ok") else "❌"
                print(f"{status} {key}: {info.get('detail')}")

    def _operator_switch_broker(self):
        # Simple runtime-only switch; persists could be wired to AUTONOMOUS_CONFIG.json later.
        print("\nCurrent default broker for manual trades is runtime-configurable only.")
        print("Manual trades already allow specifying broker in the prompt.")

    def _operator_show_positions(self):
        try:
            from position_manager import get_position_manager
            pm = get_position_manager()
            summary = pm.get_position_summary()
            print("\n📊 OPEN POSITIONS SUMMARY")
            print(json.dumps(summary, indent=2))
        except Exception as e:
            self.narration.narrate_error("OPERATOR_POSITIONS_ERROR", str(e))
    
    def action_start(self):
        """START action"""
        print("\n" + "="*80)
        print("▶️  STARTING RICK SYSTEM")
        print("="*80)
        result = self.config.execute_action(SystemAction.START)
        print(result)
        print("\n✅ System is now ONLINE and AUTONOMOUS")
        print("📊 Dashboard: http://localhost:8501")
        print("📜 Narration: Check logs/ directory for real-time events")
    
    def action_stop(self):
        """STOP action"""
        print("\n" + "="*80)
        print("⏹️  STOPPING RICK SYSTEM")
        print("="*80)
        confirm = input("Are you sure? (yes/no): ").strip().lower()
        if confirm == "yes":
            result = self.config.execute_action(SystemAction.STOP)
            print(result)
            print("\n✅ System has been shutdown")
        else:
            print("❌ Stop cancelled")
    
    def action_verify_status(self):
        """VERIFY STATUS action"""
        print("\n" + "="*80)
        print("📊 SYSTEM STATUS")
        print("="*80)
        result = self.config.execute_action(SystemAction.VERIFY_STATUS)
        print(result)
        self.narration.print_tail(10)
    
    def action_manual_trade(self):
        """MANUAL TRADE action"""
        print("\n" + "="*80)
        print("👤 MANUAL TRADE INPUT")
        print("="*80)
        print("\nEnter trade parameters in plain English:")
        print("Examples:")
        print("  'Buy 10000 EURUSD at market with 2% risk'")
        print("  'Sell 5000 GBPUSD with 50 pip stop and 100 pip target'")
        print("  Or paste JSON: {\"direction\": \"buy\", \"symbol\": \"EURUSD\", ...}")
        print()
        
        trade_input = input("Enter trade parameters: ").strip()
        
        if not trade_input:
            print("❌ No input provided")
            return
        
        # Parse and submit
        try:
            parsed = self.config.manual_trade_input(trade_input)
            print("\n📊 Parsed parameters:")
            for key, value in parsed.items():
                print(f"  {key}: {value}")
            
            # Create trade parameters object
            trade_params = TradeParameters(
                symbol=parsed.get("symbol", "EURUSD"),
                direction=parsed.get("direction", "buy"),
                quantity=parsed.get("quantity", 10000),
                entry_price=parsed.get("entry_price"),
                stop_loss=parsed.get("stop_loss"),
                take_profit=parsed.get("take_profit"),
                risk_percent=parsed.get("risk_percent", 2.0),
                broker=parsed.get("broker", "oanda")
            )
            
            # Get hive analysis and plan
            plan = self.config.submit_manual_trade(trade_params)
            print(plan)
            
            # Determine dynamic leverage & position sizing if the user set risk_percent instead of quantity
            try:
                if not trade_params.quantity or trade_params.quantity <= 0:
                    pm = None
                    try:
                        from position_manager import get_position_manager
                        pm = get_position_manager()
                    except Exception:
                        pm = None

                    price_history = []
                    if pm and hasattr(pm, "get_recent_prices"):
                        price_history = pm.get_recent_prices(trade_params.symbol, lookback=50)

                    dlc = DynamicLeverageCalculator()
                    rec = dlc.calculate_for_signal(
                        trade_params.symbol,
                        float(trade_params.risk_percent / 100.0) if trade_params.risk_percent else 0.5,
                        price_history or [float(trade_params.entry_price) if trade_params.entry_price else 1.0],
                        25000.0,
                        current_positions=0,
                    )
                    trade_params.quantity = int(rec.get("position_size", trade_params.quantity or 10000))
            except Exception:
                pass

            # Ask for approval
            approve = input("\nApprove this trade? (yes/no): ").strip().lower()
            if approve == "yes":
                success, message = self.config.execute_approved_manual_trade(trade_params)
                if success:
                    print(f"✅ Trade APPROVED and EXECUTED: {message}")
                else:
                    print(f"❌ Trade APPROVAL BLOCKED: {message}")
            else:
                print("❌ Trade rejected by user")
        
        except Exception as e:
            print(f"❌ Error parsing trade: {e}")
    
    def action_reassess(self):
        """REASSESS POSITIONS action"""
        print("\n" + "="*80)
        print("📈 REASSESSING ALL OPEN POSITIONS")
        print("="*80)
        print("Fetching real-time market data for all open positions...")
        print("(Updates every minute automatically)")
        print()
        
        result = self.config.execute_action(SystemAction.REASSESS_POSITIONS)
        print(result)
        
        # Stream reassessments
        print("\n✅ Position reassessment complete. Hive is managing trades in real-time.")
        print("   Next reassessment in 60 seconds...")
    
    def action_view_narration(self):
        """VIEW NARRATION LOG action"""
        print("\n" + "="*80)
        print("📜 NARRATION LOG - Real-time System Events")
        print("="*80)
        print("Streaming latest events (Press Ctrl+C to stop)...\n")
        
        try:
            self.narration.stream_tail(20)
        except KeyboardInterrupt:
            print("\n\n✅ Stopped streaming narration log")

    def action_open_web_ui(self):
        """OPEN HIVE WEB UI action"""
        print("\n" + "="*80)
        print("🌐 STARTING HIVE WEB UI")
        print("="*80)
        print("Launching FastAPI app at http://localhost:8700 ...")
        try:
            import subprocess, sys as _sys
            # Prefer running the module directly; non-blocking
            subprocess.Popen([_sys.executable, "-m", "uvicorn", "ui.hive_web:app", "--host", "0.0.0.0", "--port", "8700"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("✅ Hive Web UI launched. Open http://localhost:8700 in your browser.")
        except Exception as e:
            print(f"❌ Failed to launch web UI via uvicorn: {e}")
            print("Attempting fallback...")
            try:
                import subprocess, sys as _sys
                subprocess.Popen([_sys.executable, "ui/hive_web.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print("✅ Hive Web UI launched (fallback). Open http://localhost:8700")
            except Exception as e2:
                print(f"❌ Fallback launch failed: {e2}")

    # ---------- AUTOSTART BUNDLE ----------
    def start_autonomous_bundle(self):
        """Autostart: run actions 1,3,5,6 automatically in background.

        - action_start() once at boot
        - action_verify_status() every 5 minutes
        - action_reassess() every 60 seconds
        - action_view_narration() continuous stream (in a thread)
        """
        if self._auto_threads_started:
            return

        print("\n🛠️  Autostart bundle enabled: will run 1,3,5,6 automatically.")

        # 1) Start system immediately
        try:
            self.action_start()
        except Exception as e:
            print(f"❌ Autostart: start failed: {e}")

        # 3) Verify status periodically
        def _verify_loop():
            import time as _t
            while self.running:
                try:
                    self.action_verify_status()
                except Exception as e:
                    self.narration.narrate_error("AUTOVERIFY_ERROR", str(e))
                _t.sleep(300)  # 5 minutes

        # 5) Reassess positions every 60 seconds
        def _reassess_loop():
            import time as _t
            while self.running:
                try:
                    self.action_reassess()
                except Exception as e:
                    self.narration.narrate_error("AUTOREASSESS_ERROR", str(e))
                _t.sleep(60)

        # 6) Stream narration in background (non-blocking)
        def _narration_loop():
            try:
                self.narration.stream_tail(20)
            except Exception as e:
                self.narration.narrate_error("AUTONARRATION_ERROR", str(e))

        vt = threading.Thread(target=_verify_loop, daemon=True)
        rt = threading.Thread(target=_reassess_loop, daemon=True)
        nt = threading.Thread(target=_narration_loop, daemon=True)
        vt.start(); rt.start(); nt.start()
        self._auto_threads_started = True
    
    def action_settings(self):
        """SETTINGS action"""
        print("\n" + "="*80)
        print("🔧 SYSTEM SETTINGS")
        print("="*80)
        print("\n1) Trading Mode")
        print("   a) Paper Practice (simulated money)")
        print("   b) Paper Real-Time (real data, fake money)")
        print("   c) Live Real Money")
        print("\n2) Broker Selection")
        print("   a) Enable/disable Oanda")
        print("   b) Enable/disable IBKR")
        print("   c) Enable/disable Coinbase")
        print("\n3) Hive Settings")
        print("   a) Toggle Autonomy")
        print("   b) Toggle Learning")
        print("   c) Toggle Dialogue")
        print("\n4) Risk Management")
        print("   a) Set Max Drawdown")
        print("   b) Set Position Size")
        print("   c) Set Daily Loss Limit")
        
        setting = input("\nSelect setting to modify (1a, 2b, etc.): ").strip()
        print(f"✅ Setting '{setting}' selected (configuration UI would load here)")
    
    def action_exit(self):
        """EXIT action"""
        confirm = input("\nExit RICK CLI? (yes/no): ").strip().lower()
        if confirm == "yes":
            print("\n" + "="*80)
            print("👋 RICK System CLI Closing")
            print("="*80)
            print("✅ Thank you for using RICK Hive Mind Collective Trading")
            print("📊 All positions remain under autonomous hive management")
            self.running = False
            sys.exit(0)
        else:
            print("❌ Exit cancelled")
    
    def run(self):
        """Run the CLI"""
        self.display_banner()
        
        print("\n🟢 RICK CLI is ready!")
        print("📊 System Status: Ready for commands")
        print("📜 All events will be logged to: logs/narration.log")
        print("🎯 Narration will stream in real-time to terminal\n")
        
        while self.running:
            try:
                choice = self.display_main_menu()
                self.handle_choice(choice)
                
                # Brief pause between actions
                time.sleep(0.5)
            
            except KeyboardInterrupt:
                print("\n\n⚠️  Interrupted by user. Use 'STOP' from menu to shutdown safely.")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                self.narration.narrate_error("CLI_ERROR", str(e))


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="RICK Interactive CLI")
    parser.add_argument("--autostart", action="store_true",
                        help="Run actions 1,3,5,6 automatically while CLI is open")
    args = parser.parse_args()

    # Runtime root name guard: ensure canonical project root resolution
    try:
        from runtime_guard import root_name_guard as _rng
        rc = _rng.main()
        if rc != 0:
            sys.exit(rc)
    except Exception as e:
        print(f"[root_name_guard] WARNING: guard check failed: {e}")

    cli = RICKInteractiveCLI()
    if args.autostart:
        # Kick off background automation, but keep CLI interactive
        cli.start_autonomous_bundle()
    cli.run()


if __name__ == "__main__":
    main()
