"""Smart trailing and TP extension utilities
===========================================

This module exposes `maybe_extend_take_profit` and `should_trail` used by the
position manager to extend TPs when strong momentum and hive consensus exist.
"""

from __future__ import annotations
from typing import Dict, Any, Tuple
from datetime import datetime
from typing import Optional

from hive.rick_hive_mind import aggregate_momentum_score
from foundation.rick_charter import RickCharter
from config.narration_logger import get_narration_logger


def maybe_extend_take_profit(
    position: Dict[str, Any],
    confidence: float,
    momentum_context: Dict[str, Any],
    max_extension_pct: float = 0.5,
    min_confidence: float = 0.8,
) -> Tuple[Optional[float], bool, str]:
    """Return new_tp, trailing_activated, reason.

    Guarantees: never drop below R:R charter minimum and never violate
    time-in-trade limits.
    """
    tp = position.get("take_profit")
    sl = position.get("stop_loss")
    entry = position.get("entry_price")
    direction = position.get("direction")
    if not (tp and sl and entry):
        return None, False, "no_oco"

    # momentum_context keys: momentum_score, hive_consensus, regime, volatility
    momentum_score = momentum_context.get("momentum_score", 0.0)
    hive_consensus = momentum_context.get("hive_consensus", 0.0)

    # require hive and model consensus + min confidence
    if confidence < min_confidence or hive_consensus < 0.8 or momentum_score < 0.8:
        return None, False, "no_momentum"

    # compute current R and ensure extension preserves R>= MIN_RISK_REWARD_RATIO
    try:
        if direction == "buy":
            risk = abs(entry - sl)
            reward = abs(tp - entry)
        else:
            risk = abs(sl - entry)
            reward = abs(entry - tp)
        if risk == 0:
            return None, False, "invalid_risk"
        current_rr = reward / risk
    except Exception:
        return None, False, "rr_error"

    # Proposed extension (% of existing reward) proportional to momentum score
    extension_factor = min(max_extension_pct, momentum_score * (hive_consensus * 0.75 + confidence * 0.25))
    extension_amount = reward * extension_factor
    if direction == "buy":
        proposed_tp = tp + extension_amount
    else:
        proposed_tp = tp - extension_amount

    # validate resulting R:R
    new_reward = abs(proposed_tp - entry)
    new_rr = new_reward / risk
    if new_rr < RickCharter.MIN_RISK_REWARD_RATIO:
        return None, False, "rr_violate"

    # check max hold: if position older than max hold, disallow
    entry_time = position.get("entry_time")
    if entry_time:
        try:
            from datetime import datetime, timezone
            et = datetime.fromisoformat(entry_time)
            age_seconds = (datetime.now(et.tzinfo or None) - et).total_seconds()
            if age_seconds >= RickCharter.MAX_HOLD_SECONDS if hasattr(RickCharter, 'MAX_HOLD_SECONDS') else 6*3600:
                return None, False, "hold_max"
        except Exception:
            pass

    try:
        get_narration_logger().narrate_info("SMART_TRAILING_TP_EXTENSION", {"symbol": position.get("symbol"), "old_tp": tp, "new_tp": proposed_tp, "reason": "momentum_extension"})
    except Exception:
        pass
    return proposed_tp, True, "momentum_extension"


def should_trail(position: Dict[str, Any], hive_signals: Dict[str, Any]) -> bool:
    """Decide if trailing should be used; simple rule for now.

    Returns True if trailing is worthwhile based on unrealized R and hive consensus.
    """
    try:
        current_pnl = position.get("current_pnl", 0.0)
        entry = position.get("entry_price")
        sl = position.get("stop_loss")
        if not (entry and sl):
            return False
        if position.get("quantity", 0) <= 0:
            return False
        # compute current R ratio using pnl and risk
        risk = abs(entry - sl) * position.get("quantity")
        if risk <= 0:
            return False
        current_r = current_pnl / risk
    except Exception:
        return False

    momentum = hive_signals.get("momentum_score", 0.0)
    hive_consensus = hive_signals.get("hive_consensus", 0.0)
    decision = (current_r >= 1.0 and momentum >= 0.7 and hive_consensus >= 0.8)
    try:
        get_narration_logger().narrate_info("SMART_TRAILING_DECISION", {"symbol": position.get("symbol"), "unrealized_rr": current_r, "momentum": momentum, "hive_consensus": hive_consensus, "will_trail": bool(decision)})
    except Exception:
        pass
    if current_r >= 1.0 and momentum >= 0.7 and hive_consensus >= 0.8:
        return True
    return False
"""Smart trailing and TP extension logic for N_RLC_rebuild.

This module activates only after an initial OCO (TP/SL) is in place and
all RickCharter and guardian gate checks have passed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, Tuple


@dataclass
class TrailingDecision:
    new_take_profit: float
    trailing_activated: bool
    reason: str


def _risk_reward(entry: float, tp: float, sl: float, side: str) -> float:
    if side.upper() == "BUY":
        risk = max(entry - sl, 0.0)
        reward = max(tp - entry, 0.0)
    else:
        risk = max(sl - entry, 0.0)
        reward = max(entry - tp, 0.0)
    if risk <= 0:
        return 0.0
    return reward / risk


def maybe_extend_take_profit(
    entry_price: float,
    current_tp: float,
    stop_loss: float,
    side: str,
    confidence: float,
    momentum_score: float,
    rr_min: float = 3.2,
    rr_target_boost: float = 0.5,
) -> TrailingDecision:
    """Optionally extend TP when momentum and confidence are strong.

    - Only extends TP (never moves SL).
    - Ensures resulting R:R is still >= rr_min.
    - Intentionally conservative: requires both high momentum and
      reasonably high confidence.
    """

    base_rr = _risk_reward(entry_price, current_tp, stop_loss, side)
    if base_rr < rr_min:
        return TrailingDecision(current_tp, False, "BASE_RR_BELOW_MIN")

    if momentum_score < 0.8 or confidence < 0.8:
        return TrailingDecision(current_tp, False, "MOMENTUM_OR_CONFIDENCE_TOO_LOW")

    if side.upper() == "BUY":
        distance = current_tp - entry_price
        new_tp = current_tp + distance * rr_target_boost
    else:
        distance = entry_price - current_tp
        new_tp = current_tp - distance * rr_target_boost

    new_rr = _risk_reward(entry_price, new_tp, stop_loss, side)
    if new_rr < rr_min:
        return TrailingDecision(current_tp, False, "NEW_RR_BELOW_MIN")

    return TrailingDecision(new_tp, True, "SMART_TRAILING_EXTENDED_TP")


def should_trail(position_state: Dict[str, Any], hive_signals: Dict[str, Any]) -> bool:
    """Decide whether trailing logic should be considered for this position.

    `position_state` is expected to include keys like `unrealized_rr`,
    `time_in_minutes`, `side`, etc. `hive_signals` can include regime and
    consensus fields produced by the hive/ML stack.
    """

    unrealized_rr = float(position_state.get("unrealized_rr", 0.0))
    time_in_minutes = float(position_state.get("time_in_minutes", 0.0))
    regime = str(hive_signals.get("regime", "unknown"))
    consensus = float(hive_signals.get("consensus", 0.0))

    if unrealized_rr < 1.0:
        return False
    if time_in_minutes < 5.0:
        return False
    if consensus < 0.75:
        return False
    if regime not in {"trend", "momentum"}:
        return False

    return True
