"""
Hive Terminal
=============
Two-way manual dialogue interface between you, RICK, and the Hive.
- Non-interfering with autonomous engine
- Accepts natural language prompts
- Supports explicit trade execution with PIN suffix: e.g., "place trade 841921"
- Applies Charter rules; on violation, proposes auto-adjust or allows override
  (override permitted only in this terminal; requires explicit confirmation)
"""

import re
import sys
import json
import argparse
from typing import Dict, Optional
from config.narration_logger import get_narration_logger
from config.enhanced_task_config import get_enhanced_task_config, TradeParameters
from foundation.rick_charter import RickCharter
from execution.order_router import ManualTrade, place_trade

PIN = "841921"

class HiveTerminal:
    def __init__(self):
        self.narration = get_narration_logger()
        self.cfg = get_enhanced_task_config()
        self.active = True
        self.prompt = "RICK> "

    # -------- Dialogue Core --------
    def _rick_reply(self, text: str) -> str:
        """RICK translates Hive insight into plain English guidance."""
        # For now, pass-through with simple enrichment; hook ML later.
        return f"[RICK] I parsed your request: {text}"

    def _hive_insight(self, text: str) -> Dict:
        """Call into existing manual trade parser + analysis to simulate hive insight."""
        try:
            parsed = self.cfg.manual_trade_input(text)
            plan = self.cfg.submit_manual_trade(TradeParameters(**{
                "symbol": parsed.get("symbol", "EURUSD"),
                "direction": parsed.get("direction", "buy"),
                "quantity": parsed.get("quantity", 10000),
                "entry_price": parsed.get("entry_price"),
                "stop_loss": parsed.get("stop_loss"),
                "take_profit": parsed.get("take_profit"),
                "risk_percent": parsed.get("risk_percent", 2.0),
                "broker": parsed.get("broker", "oanda")
            }))
            return {"parsed": parsed, "plan": plan}
        except Exception as e:
            self.narration.narrate_error("HIVE_PARSE", str(e))
            return {"error": str(e)}

    # -------- Charter Enforcement Stub --------
    def _apply_charter_rules(self, parsed: Dict) -> (bool, str, Dict, Dict):
        """Validate against Charter; return (ok, reason, adjusted_params, suggestions).

        Checks:
        - Quantity > 0
        - Notional >= MIN_NOTIONAL_USD (requires entry_price; if absent uses placeholder 1.0)
        - Risk/Reward ratio >= MIN_RISK_REWARD_RATIO (if SL & TP provided)
        - Timeframe (if mentioned) allowed
        Returns suggestions dict for user auto-adjust.
        """
        suggestions = {}
        qty = float(parsed.get("quantity", 10000) or 0)
        entry_price = parsed.get("entry_price")
        stop = parsed.get("stop_loss")
        tp = parsed.get("take_profit")
        direction = parsed.get("direction", "buy").lower()
        timeframe = self._extract_timeframe(parsed.get("raw_text", ""))
        notional_price = entry_price if entry_price else 1.0
        notional = qty * notional_price

        # Quantity check
        if qty <= 0:
            suggestions["quantity"] = 10000
            return False, "Quantity must be > 0", parsed, suggestions

        # Notional check
        if notional < RickCharter.MIN_NOTIONAL_USD:
            needed_qty = int((RickCharter.MIN_NOTIONAL_USD / notional_price) + 0.5)
            suggestions["quantity"] = needed_qty
            suggestions["reason_notional"] = f"Increase quantity to {needed_qty} for notional ≥ ${RickCharter.MIN_NOTIONAL_USD}."

        # Risk/Reward check
        rr_ok = True
        rr_value = None
        if stop and tp and entry_price:
            try:
                entry = float(entry_price)
                sl = float(stop)
                target = float(tp)
                if direction == "buy":
                    risk = entry - sl
                    reward = target - entry
                else:
                    risk = sl - entry  # assuming SL above entry for short
                    reward = entry - target
                if risk > 0:
                    rr_value = reward / risk
                    if rr_value < RickCharter.MIN_RISK_REWARD_RATIO:
                        rr_ok = False
                        # Suggest new TP to meet RR
                        needed_reward = RickCharter.MIN_RISK_REWARD_RATIO * risk
                        if direction == "buy":
                            suggested_tp = round(entry + needed_reward, 5)
                        else:
                            suggested_tp = round(entry - needed_reward, 5)
                        suggestions["take_profit"] = suggested_tp
                        suggestions["reason_rr"] = f"Adjust take_profit to {suggested_tp} for RR ≥ {RickCharter.MIN_RISK_REWARD_RATIO}."
            except Exception:
                pass

        # Timeframe check if provided
        if timeframe and not RickCharter.validate_timeframe(timeframe):
            suggestions["timeframe"] = RickCharter.ALLOWED_TIMEFRAMES[0].value
            suggestions["reason_timeframe"] = f"Timeframe {timeframe} not allowed. Use one of {', '.join(tf.value for tf in RickCharter.ALLOWED_TIMEFRAMES)}."

        # Compose compliance decision
        failures = []
        if "reason_notional" in suggestions:
            failures.append("notional")
        if rr_ok is False:
            failures.append("risk_reward")
        if "reason_timeframe" in suggestions:
            failures.append("timeframe")

        parsed["computed_notional"] = notional
        if rr_value is not None:
            parsed["risk_reward"] = rr_value
        parsed["timeframe"] = timeframe

        if failures:
            return False, 
                "; ".join([suggestions.get(f"reason_{f}", f)]) , parsed, suggestions
        return True, "Charter compliance satisfied", parsed, suggestions

    def _extract_timeframe(self, text: str) -> Optional[str]:
        if not text:
            return None
        m = re.search(r"\b(M15|M30|H1|M1|M5|H4|D1)\b", text.upper())
        return m.group(1) if m else None

    def _looks_like_execute_command(self, text: str) -> bool:
        t = text.strip().lower()
        return (t.startswith("place trade") or t.startswith("make position") or t.startswith("execute trade")) and PIN in t

    def _extract_post_parameters(self, text: str) -> str:
        """Return trailing natural-language parameters before the PIN."""
        try:
            return text[: text.lower().rfind(PIN.lower())].strip()
        except Exception:
            return text

    # -------- Execution Flow --------
    def interactive_loop(self):
        print("\n╔══════════════════════════════════════════════════════╗")
        print("║           RICK ↔ HIVE MANUAL TERMINAL               ║")
        print("║        Two-way dialogue. PIN required to execute    ║")
        print("╚══════════════════════════════════════════════════════╝\n")
        print("Type your idea, paste a position, or ask questions.")
        print("- To execute, end with: 'place trade 841921' or 'make position 841921'.")
        print("- To quit: 'exit' or Ctrl+C.\n")

        while self.active:
            try:
                user = input(self.prompt)
                if not user:
                    continue
                if user.strip().lower() in {"exit", "quit"}:
                    print("Goodbye.")
                    break

                # Always produce Hive insight + RICK reply
                insight = self._hive_insight(user)
                if "error" in insight:
                    print(f"Error: {insight['error']}")
                    continue
                parsed = insight.get("parsed", {})
                print(insight.get("plan", ""))
                print(self._rick_reply(user))

                # If explicit execute command with PIN
                if self._looks_like_execute_command(user):
                    params_text = self._extract_post_parameters(user)
                    parsed2 = self.cfg.manual_trade_input(params_text)
                    parsed2["raw_text"] = params_text
                    ok, reason, adjusted, suggestions = self._apply_charter_rules(parsed2)
                    if not ok:
                        print(f"❌ Charter validation failed: {reason}")
                        if suggestions:
                            print("Suggested adjustments:")
                            for k,v in suggestions.items():
                                if k.startswith("reason_"): continue
                                print(f"  - {k}: {v}")
                        choice = input("Apply suggestions automatically? (yes/apply) | OVERRIDE (override) | cancel: ").strip().lower()
                        if choice in {"yes","apply","y"}:
                            for k,v in suggestions.items():
                                if k.startswith("reason_"): continue
                                adjusted[k] = v
                            print("🔧 Adjustments applied. Re-validating...")
                            ok2, reason2, adjusted2, suggestions2 = self._apply_charter_rules(adjusted)
                            if not ok2:
                                print(f"Still failing: {reason2}. Aborting.")
                                continue
                            adjusted = adjusted2
                        elif choice in {"override","o"}:
                            confirm = input("Type PIN to confirm override: ").strip()
                            if confirm != PIN:
                                print("❌ Invalid PIN. Aborting.")
                                continue
                            print("⚠️ Charter override acknowledged for this manual action only.")
                        else:
                            print("Cancelled.")
                            continue

                    tp = TradeParameters(
                        symbol=adjusted.get("symbol", "EURUSD"),
                        direction=adjusted.get("direction", "buy"),
                        quantity=adjusted.get("quantity", 10000),
                        entry_price=adjusted.get("entry_price"),
                        stop_loss=adjusted.get("stop_loss"),
                        take_profit=adjusted.get("take_profit"),
                        risk_percent=adjusted.get("risk_percent", 2.0),
                        broker=adjusted.get("broker", "oanda"),
                    )
                    mt = ManualTrade(
                        symbol=tp.symbol,
                        direction=tp.direction,
                        quantity=float(tp.quantity or 0),
                        broker=tp.broker,
                        entry_price=(float(tp.entry_price) if tp.entry_price is not None else None),
                        stop_loss=(float(tp.stop_loss) if tp.stop_loss is not None else None),
                        take_profit=(float(tp.take_profit) if tp.take_profit is not None else None),
                        order_type="market",
                    )
                    res = place_trade(pin=int(PIN), trade=mt)
                    if res.get("success"):
                        price = res.get("price") or tp.entry_price or 0
                        self.narration.narrate_trade_executed(
                            tp.symbol, tp.direction, tp.quantity, float(price), tp.broker
                        )
                        print(f"✅ Trade executed on {tp.broker.upper()} | order_id={res.get('order_id')} price={price}")
                    else:
                        err = res.get("error", "unknown error")
                        self.narration.narrate_error("MANUAL_EXECUTION", err)
                        print(f"❌ Execution failed: {err}")
            except KeyboardInterrupt:
                print("\nInterrupted. Type 'exit' to quit.")
            except Exception as e:
                self.narration.narrate_error("HIVE_TERMINAL", str(e))
                print(f"Error: {e}")


def main():
    parser = argparse.ArgumentParser(description="RICK ↔ HIVE Manual Terminal")
    args = parser.parse_args()
    HiveTerminal().interactive_loop()


if __name__ == "__main__":
    main()
