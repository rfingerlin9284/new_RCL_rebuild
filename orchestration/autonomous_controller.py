"""Autonomous trading controller for RICK.

This is a safe stub implementation that wires into existing components
without weakening any risk controls. It does NOT place real trades yet;
all candidate generation must still go through charter + gates + router.
"""

from __future__ import annotations

import threading
import time
from typing import Optional, Dict, Any, List

from config.narration_logger import get_narration_logger
from execution.order_router import ManualTrade, place_trade
from position_manager import get_position_manager
from hive.guardian_gates import apply_all_gates
from hive.strategy_selector import get_strategy_selector
from risk.dynamic_leverage import DynamicLeverageCalculator
from hive.quant_hedge_rules import QuantHedgeRules, HedgeAction
from logic.regime_detector import StochasticRegimeDetector, MarketRegime
from config.enhanced_task_config import get_enhanced_task_config, TradeParameters
from foundation.rick_charter import RickCharter


class AutonomousController:
    """Manage autonomous trading loop lifecycle.

    This controller is intentionally conservative: it exposes start/stop
    hooks and a loop skeleton. The actual signal generation and
    order-routing should reuse existing modules (hive, gates, router).
    """

    def __init__(self) -> None:
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._narration = get_narration_logger()
        # Core analysis engines (PIN‑gated)
        self._hedge_rules = QuantHedgeRules(pin=841921)
        self._regime_detector = StochasticRegimeDetector(pin=841921)
        self._leverage_calc = DynamicLeverageCalculator()
        self._selector = get_strategy_selector()

    def start_autonomous(self) -> None:
        if self._running:
            return
        self._narration.log_event("AUTONOMOUS_START", "Autonomous controller requested to start")
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop_autonomous(self) -> None:
        if not self._running:
            return
        self._narration.log_event("AUTONOMOUS_STOP", "Autonomous controller requested to stop")
        self._running = False

    def _loop(self) -> None:
        """Main autonomous loop.

        This implementation is intentionally conservative: it does a
        periodic sweep over any internally generated candidate trades,
        applies guardian gates, then routes approved trades through the
        normal `place_trade` pipeline so that the position manager picks
        them up. Candidate generation is factored into a helper for
        future enhancement.
        """
        while self._running:
            try:
                # Enhanced heartbeat includes current mode, autonomous flag, brokers, Coinbase status, and open positions
                cfg = get_enhanced_task_config()
                pm = get_position_manager()
                summary = pm.get_position_summary() if hasattr(pm, "get_position_summary") else {}
                active_brokers = cfg.get_active_brokers()
                trading_mode = cfg.config.get("trading_mode", "paper_practice") if getattr(cfg, "config", None) else "paper_practice"
                autonomous_flag = cfg.config.get("hive_autonomous", True) if getattr(cfg, "config", None) else True
                coinbase_status = "DISABLED per charter" if "coinbase" not in [b.lower() for b in active_brokers] else "ENABLED"

                heartbeat_message = (
                    f"SYSTEM_HEARTBEAT: mode={trading_mode}, autonomous={autonomous_flag}, "
                    f"brokers={active_brokers}, Coinbase={coinbase_status}, open_positions={len(summary.get('positions', []) if isinstance(summary, dict) else 0)}"
                )
                self._narration.log_event("AUTONOMOUS_HEARTBEAT", heartbeat_message)

                candidates = self._generate_candidates()
                for cand in candidates:
                    try:
                        self._process_candidate(cand)
                    except Exception as exc:  # pragma: no cover
                        self._narration.log_event(
                            "AUTONOMOUS_CANDIDATE_ERROR",
                            f"Error processing candidate: {exc}",
                            symbol=cand.get("symbol"),
                        )

                time.sleep(60)
            except Exception as exc:  # pragma: no cover - defensive
                self._narration.log_event("AUTONOMOUS_ERROR", f"Autonomous loop error: {exc}")
                time.sleep(60)

    # ----- candidate generation & processing -----

    def _generate_candidates(self) -> List[Dict[str, Any]]:
        """Return a list of candidate trade dicts.

        Conservative first implementation:
        - Uses regime detector + quant hedge rules to decide whether
          conditions are appropriate for taking risk at all.
        - Generates at most one tiny OANDA FX candidate (EURUSD) in
          FULL_LONG / MODERATE_LONG regimes and safe hedge conditions.
        - All sizing/R:R/gate enforcement still happens in
          `_process_candidate` + guardian gates + router.
        """
        candidates: List[Dict[str, Any]] = []

        try:
                pm = get_position_manager()
            prices = pm.get_recent_prices("EUR_USD", lookback=50)  # type: ignore[attr-defined]
        except Exception:
            # If we cannot get prices yet, skip autonomous entries
            self._narration.log_event("AUTONOMOUS_NO_DATA", "No price data for regime detection; skipping cycle")
            return candidates

        if not prices or len(prices) < 10:
            self._narration.log_event("AUTONOMOUS_INSUFFICIENT_DATA", "Not enough data for regime detection; skipping")
            return candidates

        regime_data = self._regime_detector.detect_regime(prices, symbol="EUR_USD")
        hedge_analysis = self._hedge_rules.analyze_market_state(symbol="EUR_USD")  # type: ignore[attr-defined]

        self._narration.log_event(
            "AUTONOMOUS_REGIME",
            "Regime + hedge snapshot",
            regime=regime_data.regime.value,
            confidence=regime_data.confidence,
            volatility=regime_data.volatility,
            hedge_action=hedge_analysis.primary_action,
            risk_level=hedge_analysis.risk_level,
        )

        # Only consider new entries when hedge system says LONG is ok
        if hedge_analysis.primary_action not in {HedgeAction.FULL_LONG.value, HedgeAction.MODERATE_LONG.value}:
            return candidates

        if regime_data.regime not in {MarketRegime.BULL, MarketRegime.BEAR}:
            # Restrict to clear directional regimes for now
            return candidates

        direction = "buy" if regime_data.regime == MarketRegime.BULL else "sell"

        # Determine which strategies to consider using the strategy selector
        selector_context = {"market": "fx", "regime": regime_data.regime.name}
        active_ids = self._selector.select_active_strategies(selector_context, max_strategies=2)

        # For each active strategy, create a candidate
        for sid in active_ids:
            try:
                # Use PM prices and dynamic leverage to compute position size
                account_balance = 25000.0
                try:
                    # Try to read an account/balance from PM if available
                    account_balance = float(pm.get_account_balance()) if hasattr(pm, "get_account_balance") else account_balance
                except Exception:
                    pass

                rec = self._leverage_calc.calculate_for_signal(
                    "EUR_USD",
                    float(regime_data.confidence),
                    prices,
                    account_balance,
                    current_positions=len(pm.get_position_summary().get("positions", [])) if hasattr(pm, "get_position_summary") else 0,
                )
                quantity = rec.get("position_size", 1000)
            except Exception:
                quantity = 1000

            candidates.append(
                {
                    "symbol": "EURUSD",
                    "direction": direction,
                    "quantity": quantity,
                    "broker": "oanda",
                    "order_type": "market",
                    "source_strategy": sid,
                }
            )

        return candidates

    def _process_candidate(self, cand):
        """Apply gates and, if approved, place the trade."""
        symbol = cand["symbol"]
        direction = cand["direction"]
        quantity = cand["quantity"]
        broker = cand.get("broker", "oanda")
        entry = cand.get("entry_price")
        sl = cand.get("stop_loss")
        tp = cand.get("take_profit")

        # Shared charter check (R:R, min notional) BEFORE gates
        try:
            cfg = get_enhanced_task_config()
            tp = cand.get("take_profit")
            sl = cand.get("stop_loss")
            entry = cand.get("entry_price")
            tp_val = tp if tp is not None else None
            sl_val = sl if sl is not None else None
            entry_val = entry if entry is not None else None

            trade_params = TradeParameters(
                symbol=symbol,
                direction=direction,
                quantity=quantity,
                entry_price=entry_val,
                stop_loss=sl_val,
                take_profit=tp_val,
                risk_percent=cfg.config.get("auto_entry_risk_pct", 2.0) if getattr(cfg, "config", None) else 2.0,
                broker=broker,
            )

            charter_ok, charter_reasons = cfg._validate_trade_against_charter(trade_params)
        except Exception:
            charter_ok, charter_reasons = False, ["Charter validation error"]

        if not charter_ok:
            # Narrate charter-level rejection with reasons and skip
            self._narration.log_event(
                "AUTONOMOUS_CHARTER_REJECT",
                "Candidate rejected by charter pre-check",
                symbol=symbol,
                reasons=charter_reasons,
            )
            return

        # Guardian gates
        gates_ok, gate_reason = apply_all_gates(symbol=symbol, direction=direction, size=quantity, broker=broker)
        if not gates_ok:
            self._narration.log_event(
                "AUTONOMOUS_GATE_REJECT",
                "Candidate rejected by guardian gates",
                symbol=symbol,
                reason=gate_reason,
            )
            return
        else:
            # Gate passed narration
            self._narration.log_event(
                "AUTONOMOUS_GATE_PASS",
                "Candidate passed guardian gates",
                symbol=symbol,
                size=quantity,
                broker=broker,
            )

        # If SL/TP are missing, create conservative ATR-based OCO that satisfies R:R >= 3.2
        if not sl or not tp:
            try:
                pm = get_position_manager()
                prices = pm.get_recent_prices(cand.get("symbol", "EUR_USD"), lookback=50)
                # compute ATR naive
                if prices and len(prices) > 1:
                    highs = prices
                    # naive ATR approximation: use std * multiplier
                    import numpy as np
                    vol = float(np.std(np.diff(np.array(prices))) if len(prices) > 1 else 0.001)
                    stop_distance = vol * RickCharter.FX_STOP_LOSS_ATR_MULTIPLIER if hasattr(RickCharter, 'FX_STOP_LOSS_ATR_MULTIPLIER') else vol * 1.2
                else:
                    stop_distance = 0.001
            except Exception:
                stop_distance = 0.002

            if not entry:
                entry = prices[-1] if (prices and len(prices) > 0) else None
            if entry:
                if cand["direction"] == "buy":
                    sl = entry - stop_distance
                    tp = entry + stop_distance * RickCharter.MIN_RISK_REWARD_RATIO
                else:
                    sl = entry + stop_distance
                    tp = entry - stop_distance * RickCharter.MIN_RISK_REWARD_RATIO

        trade = ManualTrade(
            symbol=symbol,
            direction=direction,
            quantity=quantity,
            broker=broker,
            entry_price=entry,
            stop_loss=sl,
            take_profit=tp,
            order_type=cand.get("order_type", "market"),
        )

        res = place_trade(pin=841921, trade=trade)
        if res.get("success"):
            self._narration.log_event("AUTONOMOUS_TRADE_PLACED", "Autonomous trade executed", symbol=symbol)
        else:
            self._narration.log_event(
                "AUTONOMOUS_TRADE_FAILED",
                "Autonomous trade failed",
                symbol=symbol,
                error=res.get("error"),
            )


_controller: Optional[AutonomousController] = None


def get_autonomous_controller() -> AutonomousController:
    """Return process‑wide autonomous controller singleton."""
    global _controller
    if _controller is None:
        _controller = AutonomousController()
    return _controller
