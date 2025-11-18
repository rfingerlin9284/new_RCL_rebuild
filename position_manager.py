"""
RICK REAL-TIME POSITION MANAGER
================================
Manages open positions with minute-by-minute updates, market data analysis,
and autonomous decision-making (buy/sell/hold/hedge/trail)
"""

from config.narration_logger import get_narration_logger
from hive.guardian_gates import apply_all_gates
from hive.rick_hive_mind import get_hive_mind
from risk.smart_trailing import maybe_extend_take_profit, should_trail
from foundation.autonomous_charter import AutonomousCharter
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
from enum import Enum
import threading
import time
from datetime import datetime, timedelta
import json


class PositionAction(Enum):
    """Actions the system can take on positions"""
    HOLD = "hold"
    TAKE_PROFIT = "take_profit"
    STOP_LOSS = "stop_loss"
    TIGHTEN_STOP = "tighten_stop"
    TRAIL_STOP = "trail_stop"
    ADD_TO_POSITION = "add_to_position"
    REDUCE_POSITION = "reduce_position"
    APPLY_HEDGE = "apply_hedge"
    EVALUATE_EXIT = "evaluate_exit"
    CLOSE = "close"


class MarketRegime(Enum):
    """Market regimes"""
    BULLISH = "bullish"
    BEARISH = "bearish"
    SIDEWAYS = "sideways"
    TRIAGE = "triage"  # Uncertain/transitional


@dataclass
class PositionUpdate:
    """Update for a position"""
    symbol: str
    timestamp: str
    current_price: float
    current_pnl: float
    market_regime: str
    action: str
    reason: str
    new_stop_loss: Optional[float] = None
    new_take_profit: Optional[float] = None


class RealTimePositionManager:
    """
    Manages all open positions with real-time monitoring and autonomous actions
    """
    
    def __init__(self, update_interval: int = 60):  # Default 60 seconds
        self.narration = get_narration_logger()
        self.update_interval = update_interval
        self.positions: Dict[str, Dict] = {}
        self.update_history: List[PositionUpdate] = []
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None
    
    def add_position(self, symbol: str, direction: str, quantity: float,
                    entry_price: float, broker: str = "oanda",
                    stop_loss: Optional[float] = None,
                    take_profit: Optional[float] = None):
        """Add new position to monitor"""
        self.positions[symbol] = {
            "symbol": symbol,
            "direction": direction.lower(),
            "quantity": quantity,
            "entry_price": entry_price,
            "broker": broker,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "entry_time": datetime.now().isoformat(),
            "current_price": entry_price,
            "current_pnl": 0,
            "status": "open",
            "last_action": None,
            "last_action_time": None,
            "trailing_stop_distance": None,
            "hedge_active": False,
        }
        
        self.narration.narrate_trade_executed(symbol, direction, quantity, entry_price, broker)
    
    def start_monitoring(self):
        """Start continuous position monitoring"""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitor_thread.start()
            self.narration.logger.info("🟢 Position monitoring started")
    
    def stop_monitoring(self):
        """Stop position monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.narration.logger.info("🔴 Position monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop - runs every minute"""
        while self.monitoring_active:
            try:
                self._reassess_all_positions()
                time.sleep(self.update_interval)
            except Exception as e:
                self.narration.narrate_error("POSITION_MANAGER", str(e))
    
    def _reassess_all_positions(self):
        """Reassess all open positions"""
        for symbol in list(self.positions.keys()):
            position = self.positions[symbol]
            if position["status"] == "open":
                self._reassess_position(symbol, position)
    
    def _reassess_position(self, symbol: str, position: Dict):
        """Reassess single position and take action"""
        
        # Fetch real-time market data
        current_price = self._fetch_market_price(symbol)
        position["current_price"] = current_price
        
        # Calculate P&L
        pnl = self._calculate_pnl(position, current_price)
        position["current_pnl"] = pnl

        # Track peak PnL / R multiple for giveback detection
        try:
            # Compute current R multiple if SL exists
            if position.get("entry_price") and position.get("stop_loss") and position.get("take_profit"):
                entry = float(position["entry_price"])
                sl = float(position["stop_loss"])
                tp = float(position["take_profit"])
                if position["direction"] == "buy":
                    risk = abs(entry - sl)
                    reward = abs(tp - entry)
                else:
                    risk = abs(sl - entry)
                    reward = abs(entry - tp)

                if risk > 0:
                    current_r = reward / risk
                    # store peak_r for giveback detection
                    peak_r = position.get("peak_r", 0.0)
                    if current_r > peak_r:
                        position["peak_r"] = current_r
        except Exception:
            pass
        
        # Detect market regime
        regime = self._detect_market_regime(symbol)

        # Hive analysis & smart trailing integration
        try:
            hive = get_hive_mind(pin=AutonomousCharter.PIN)
            hive_analysis = hive.delegate_analysis({"symbol": symbol, "current_price": current_price})
            momentum_context = {
                "momentum_score": hive_analysis.consensus_confidence,
                "hive_consensus": hive_analysis.consensus_confidence,
                "regime": regime,
                "volatility": None,
            }

            # Attempt to extend TP when momentum is strong
            entry = position.get("entry_price")
            sl = position.get("stop_loss")
            tp = position.get("take_profit")
            side = position.get("direction")
            if entry and sl and tp:
                try:
                    td = maybe_extend_take_profit(
                        float(entry), float(tp), float(sl), side,
                        float(hive_analysis.consensus_confidence), float(hive_analysis.consensus_confidence)
                    )
                    if td.trailing_activated and td.new_take_profit != tp:
                        position["take_profit"] = td.new_take_profit
                        self.narration.narrate_trade_modified(
                            symbol, "tp_extended", f"TP extended to {td.new_take_profit} due to hive momentum ({td.reason})"
                        )
                except Exception:
                    pass

            # Build a position state for should_trail requirements
            try:
                unrealized_rr = None
                if entry and sl and position.get("quantity"):
                    qty = float(position.get("quantity", 0.0))
                    risk_dollars = abs(float(entry) - float(sl)) * qty if qty > 0 else 0.0
                    unrealized_rr = (pnl / risk_dollars) if risk_dollars > 0 else None
                entry_time = position.get("entry_time")
                time_in_minutes = 0.0
                if entry_time:
                    try:
                        et = datetime.fromisoformat(entry_time)
                        time_in_minutes = (datetime.now(et.tzinfo or None) - et).total_seconds() / 60.0
                    except Exception:
                        time_in_minutes = 0.0

                position_state = {
                    "unrealized_rr": unrealized_rr if unrealized_rr is not None else 0.0,
                    "time_in_minutes": time_in_minutes,
                    "side": side,
                }
                hive_signals = {"momentum_score": hive_analysis.consensus_confidence,
                                "consensus": hive_analysis.consensus_confidence,
                                "regime": regime,
                                "hive_consensus": hive_analysis.consensus_confidence}

                if should_trail(position_state, hive_signals):
                    # Apply trailing stop: offset based on charter pips
                    pip = self._pip_size(symbol)
                    offset = AutonomousCharter.AUTO_TRAIL_DISTANCE_PIPS * pip
                    if position["direction"] == "buy":
                        new_sl = current_price - offset
                    else:
                        new_sl = current_price + offset
                    position["stop_loss"] = new_sl
                    position["trailing_stop_distance"] = offset
                    self.narration.narrate_trade_modified(symbol, "AUTO_TRAIL_APPLIED", f"Trailing stop applied to {new_sl}")
            except Exception:
                pass
        except Exception:
            pass
        
        # Pre-checks: auto-time-stop and auto-breakeven/giveback
        action = None
        try:
            # Auto-time-stop enforcement (major / minor)
            if AutonomousCharter.AUTO_TIME_STOP_ENABLED:
                entry_time = datetime.fromisoformat(position.get("entry_time"))
                age_hours = (datetime.now() - entry_time).total_seconds() / 3600.0
                if age_hours >= AutonomousCharter.AUTO_TIME_STOP_MAJOR_HOURS:
                    action = {"action": PositionAction.CLOSE, "reason": "Auto time-stop major (6 hours)"}
                elif age_hours >= AutonomousCharter.AUTO_TIME_STOP_MINOR_HOURS:
                    # If minor and R multiple below threshold, exit
                    rr_threshold = AutonomousCharter.AUTO_TIME_STOP_MINOR_R_THRESHOLD
                    peak_r = position.get("peak_r", 0.0)
                    current_r = None
                    try:
                        if position.get("entry_price") and position.get("stop_loss") and position.get("take_profit"):
                            entry = float(position["entry_price"])
                            sl = float(position["stop_loss"])
                            tp = float(position["take_profit"])
                            if position["direction"] == "buy":
                                risk = abs(entry - sl)
                                reward = abs(tp - entry)
                            else:
                                risk = abs(sl - entry)
                                reward = abs(entry - tp)
                            if risk > 0:
                                current_r = reward / risk
                    except Exception:
                        current_r = None

                    if current_r is None or current_r < rr_threshold:
                        action = {"action": PositionAction.CLOSE, "reason": "Auto time-stop minor: low R multiple"}

            # Auto-breakeven (move SL to breakeven + offset) and giveback detection
            if action is None and AutonomousCharter.AUTO_BE_ENABLED:
                # Compute current R multiple using pnl and risk if stop exists
                try:
                    if position.get("entry_price") and position.get("stop_loss"):
                        entry = float(position["entry_price"])
                        sl = float(position["stop_loss"])
                        risk_dollars = abs(entry - sl) * position["quantity"]
                        if risk_dollars > 0:
                            current_r_from_pnl = pnl / risk_dollars
                        else:
                            current_r_from_pnl = None
                    else:
                        current_r_from_pnl = None
                except Exception:
                    current_r_from_pnl = None

                if current_r_from_pnl is not None and current_r_from_pnl >= AutonomousCharter.AUTO_BE_R_THRESHOLD:
                    # Move stop to breakeven with offset pips
                    pip = self._pip_size(symbol)
                    offset = AutonomousCharter.AUTO_BE_OFFSET_PIPS * pip
                    if position["direction"] == "buy":
                        new_sl = position["entry_price"] + offset
                    else:
                        new_sl = position["entry_price"] - offset
                    # Avoid repeatedly moving stop if already tightened
                    if not position.get("breakeven_applied"):
                        position["stop_loss"] = new_sl
                        position["breakeven_applied"] = True
                        self.narration.narrate_trade_modified(
                            symbol,
                            "breakeven_applied",
                            f"Stop moved to breakeven at {new_sl} (offset {AutonomousCharter.AUTO_BE_OFFSET_PIPS} pips)"
                        )

                # Giveback: if peak_r recorded and current_r_from_pnl drops below configured threshold, close
                if AutonomousCharter.AUTO_GIVEBACK_ENABLED:
                    peak_r = position.get("peak_r", 0.0)
                    if peak_r >= AutonomousCharter.AUTO_GIVEBACK_THRESHOLD_R:
                        # Compute current R from pnl if available
                        try:
                            if position.get("entry_price") and position.get("stop_loss"):
                                entry = float(position["entry_price"])
                                sl = float(position["stop_loss"])
                                risk = abs(entry - sl)
                                if risk > 0:
                                    current_r = ( (position.get("take_profit") - entry) / risk ) if position.get("take_profit") else current_r_from_pnl
                                else:
                                    current_r = None
                            else:
                                current_r = current_r_from_pnl
                        except Exception:
                            current_r = current_r_from_pnl

                        if current_r is not None and current_r <= AutonomousCharter.AUTO_GIVEBACK_THRESHOLD_R:
                            action = {"action": PositionAction.CLOSE, "reason": "Auto giveback threshold hit"}
        except Exception:
            action = None

        # Early loss mitigation: if current PnL drops below 50% of position risk, consider reduction/close
        try:
            if position.get("entry_price") and position.get("stop_loss"):
                entry = float(position["entry_price"])
                sl = float(position["stop_loss"])
                qty = float(position.get("quantity", 0.0))
                risk_dollars = abs(entry - sl) * qty
                if risk_dollars > 0 and pnl < -0.5 * risk_dollars:
                    # Close small losses early to limit erosion
                    action = {"action": PositionAction.CLOSE, "reason": "Early loss cut: -50% risk"}
        except Exception:
            pass

        if action is None:
            action = self._determine_action(symbol, position, current_price, pnl, regime)
        
        # Execute action
        self._execute_action(symbol, position, action, regime)
        
        # Record update
        update = PositionUpdate(
            symbol=symbol,
            timestamp=datetime.now().isoformat(),
            current_price=current_price,
            current_pnl=pnl,
            market_regime=regime,
            action=action["action"].value,
            reason=action["reason"],
            new_stop_loss=action.get("new_stop_loss"),
            new_take_profit=action.get("new_take_profit"),
        )
        self.update_history.append(update)
        
        # Narrate
        self.narration.narrate_position_reassess(symbol, pnl, action["action"].value, action["reason"])
    
    def _calculate_pnl(self, position: Dict, current_price: float) -> float:
        """Calculate current P&L"""
        entry_price = position["entry_price"]
        quantity = position["quantity"]
        direction = position["direction"]
        
        if direction == "buy":
            pnl = (current_price - entry_price) * quantity
        else:  # sell
            pnl = (entry_price - current_price) * quantity
        
        return pnl
    
    def _fetch_market_price(self, symbol: str) -> float:
        """Fetch current market price"""
        # Connect to broker API for real data
        # For now, return mock
        import random
        base_prices = {
            "EURUSD": 1.1050,
            "GBPUSD": 1.2750,
            "USDJPY": 110.50,
            "AUDUSD": 0.7350,
        }
        base = base_prices.get(symbol, 1.0)
        # Add random walk
        return base + random.uniform(-0.005, 0.005)
    
    def _detect_market_regime(self, symbol: str) -> str:
        """Detect current market regime"""
        # Analyze 5-period and 20-period moving averages
        # Check volatility
        # Determine if BULLISH, BEARISH, SIDEWAYS, or TRIAGE
        
        # For now, return based on price movement
        import random
        return random.choice([
            MarketRegime.BULLISH.value,
            MarketRegime.BEARISH.value,
            MarketRegime.SIDEWAYS.value,
        ])

    def _pip_size(self, symbol: str) -> float:
        """Return pip size based on currency pair conventions"""
        try:
            if symbol.endswith("JPY"):
                return 0.01
        except Exception:
            pass
        return 0.0001
    
    def _determine_action(self, symbol: str, position: Dict, 
                         current_price: float, pnl: float, regime: str) -> Dict:
        """Determine what action to take"""
        
        action = PositionAction.HOLD
        reason = "Position performing as expected"
        
        # CHECK 1: Take Profit Target
        if position["take_profit"] and current_price >= position["take_profit"]:
            action = PositionAction.TAKE_PROFIT
            reason = "Take profit target reached"
        
        # CHECK 2: Stop Loss
        elif position["stop_loss"] and current_price <= position["stop_loss"]:
            action = PositionAction.STOP_LOSS
            reason = "Stop loss triggered - cutting losses"
        
        # CHECK 3: Profit Target - Tighten Stop
        elif pnl > 0 and pnl > position["entry_price"] * position["quantity"] * 0.01:
            action = PositionAction.TIGHTEN_STOP
            reason = f"Position profitable (+{pnl:.2f}) - moving stop to breakeven"
        
        # CHECK 4: Trailing Stop on Momentum
        elif regime == MarketRegime.BULLISH.value and position["direction"] == "buy":
            if not position.get("trailing_stop_distance"):
                position["trailing_stop_distance"] = current_price * 0.02  # 2% trail
                action = PositionAction.TRAIL_STOP
                reason = "Bullish regime - enabling trailing stop"
        
        # CHECK 5: Hedging on Regime Change
        elif regime == MarketRegime.TRIAGE.value and not position.get("hedge_active"):
            action = PositionAction.APPLY_HEDGE
            reason = f"Market regime transitioning - applying quantitative hedge"
            position["hedge_active"] = True
        
        # CHECK 6: Significant Loss - Evaluate Exit
        elif pnl < -(position["entry_price"] * position["quantity"] * 0.05):  # -5%
            action = PositionAction.EVALUATE_EXIT
            reason = "Significant loss accumulating - evaluating exit"
        
        # CHECK 7: Partial Take Profit on Large Gains
        elif pnl > position["entry_price"] * position["quantity"] * 0.05:  # +5% profit
            action = PositionAction.REDUCE_POSITION
            reason = f"Strong profit (+{pnl:.2f}) - reducing position size for risk management"
        
        return {
            "action": action,
            "reason": reason,
            "new_stop_loss": position.get("new_stop_loss"),
            "new_take_profit": position.get("new_take_profit"),
        }
    
    def _execute_action(self, symbol: str, position: Dict, action: Dict, regime: str):
        """Execute the determined action"""
        
        action_type = action["action"]
        
        if action_type == PositionAction.TAKE_PROFIT:
            self._close_position(symbol, position, "take_profit")
        
        elif action_type == PositionAction.STOP_LOSS:
            self._close_position(symbol, position, "stop_loss")
        
        elif action_type == PositionAction.TIGHTEN_STOP:
            position["stop_loss"] = position["entry_price"]
            self.narration.narrate_trade_modified(
                symbol,
                "stop_tightened",
                f"Stop loss moved to breakeven at {position['entry_price']}"
            )
        
        elif action_type == PositionAction.TRAIL_STOP:
            self.narration.narrate_trade_modified(
                symbol,
                "trailing_activated",
                f"Trailing stop enabled with 2% distance"
            )
        
        elif action_type == PositionAction.APPLY_HEDGE:
            self.narration.narrate_trade_modified(
                symbol,
                "hedge_applied",
                f"Quantitative hedge applied - regime: {regime}"
            )
        
        elif action_type == PositionAction.REDUCE_POSITION:
            reduce_qty = position["quantity"] * 0.5  # Close 50%
            self.narration.narrate_trade_modified(
                symbol,
                "partial_close",
                f"Closed 50% of position ({reduce_qty}) to lock in profits"
            )
        
        elif action_type == PositionAction.EVALUATE_EXIT:
            self.narration.narrate_trade_modified(
                symbol,
                "exit_evaluation",
                f"Evaluating exit for significant loss"
            )
    
    def _close_position(self, symbol: str, position: Dict, reason: str):
        """Close a position"""
        pnl = position["current_pnl"]
        position["status"] = "closed"
        
        self.narration.narrate_trade_closed(symbol, pnl, reason)
    
    def get_position(self, symbol: str) -> Optional[Dict]:
        """Get position details"""
        return self.positions.get(symbol)
    
    def get_all_positions(self) -> Dict:
        """Get all positions"""
        return {k: v for k, v in self.positions.items() if v["status"] == "open"}
    
    def get_position_summary(self) -> Dict:
        """Get summary of all positions"""
        open_positions = self.get_all_positions()
        total_pnl = sum(p["current_pnl"] for p in open_positions.values())
        
        return {
            "open_positions": len(open_positions),
            "total_pnl": total_pnl,
            "positions": {
                symbol: {
                    "direction": p["direction"],
                    "quantity": p["quantity"],
                    "entry_price": p["entry_price"],
                    "current_price": p["current_price"],
                    "pnl": p["current_pnl"],
                    "status": p["status"],
                }
                for symbol, p in open_positions.items()
            }
        }
    
    def export_update_history(self, filepath: str = "position_updates.json"):
        """Export position update history"""
        history_dicts = [asdict(update) for update in self.update_history]
        with open(filepath, 'w') as f:
            json.dump(history_dicts, f, indent=2)


# Global instance
_position_manager: Optional[RealTimePositionManager] = None


def get_position_manager() -> RealTimePositionManager:
    """Get or create global position manager"""
    global _position_manager
    if _position_manager is None:
        _position_manager = RealTimePositionManager(update_interval=60)
    return _position_manager


if __name__ == "__main__":
    mgr = get_position_manager()
    
    # Add test position
    mgr.add_position("EURUSD", "buy", 10000, 1.1050, "oanda", stop_loss=1.1000, take_profit=1.1100)
    
    # Start monitoring
    mgr.start_monitoring()
    
    # Let it run for a bit
    print("Monitoring positions (press Ctrl+C to stop)...")
    try:
        while True:
            time.sleep(5)
            summary = mgr.get_position_summary()
            print(f"\n📊 Position Summary: {json.dumps(summary, indent=2)}")
    except KeyboardInterrupt:
        mgr.stop_monitoring()
        print("\nMonitoring stopped")
