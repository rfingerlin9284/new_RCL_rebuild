"""Dynamic leverage logic - canonical implementation.

This file was fully replaced to remove duplication and ensure a single
implementation is used by the system.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Dict, Any

import numpy as np

from config.narration_logger import get_narration_logger


@dataclass
class LeverageResult:
    leverage: float
    position_size: float
    risk_amount: float
    risk_percent: float
    volatility: float
    confidence: float
    timestamp: str


class DynamicLeverageCalculator:
    def __init__(self, max_leverage: float = 25.0, base_risk_per_trade: float = 0.002, max_position_fraction: float = 0.15) -> None:
        self.max_leverage = max_leverage
        self.base_risk_per_trade = base_risk_per_trade
        self.max_position_fraction = max_position_fraction
        self.confidence_weights: Dict[float, float] = {0.95: 1.5, 0.85: 1.2, 0.75: 1.0, 0.65: 0.7, 0.55: 0.4}

    def calculate_volatility(self, price_history: List[float], periods: int = 14) -> float:
        if len(price_history) < periods:
            return 0.02
        prices = np.array(price_history[-periods:])
        returns = np.diff(prices) / prices[:-1]
        volatility = float(np.std(returns) * np.sqrt(24.0))
        v = max(0.01, min(0.5, volatility))
        try:
            get_narration_logger().narrate_info("DYNAMIC_LEVERAGE_VOL_CALC", {"periods": periods, "volatility": v})
        except Exception:
            pass
        return v

    def _confidence_multiplier(self, confidence: float) -> float:
        for thr, mult in sorted(self.confidence_weights.items(), reverse=True):
            if confidence >= thr:
                return mult
        return 0.2

    def calculate_for_signal(self, pair: str, confidence: float, price_history: List[float], account_balance: float, current_positions: int = 0, market_conditions: str = "normal") -> Dict[str, Any]:
        volatility = self.calculate_volatility(price_history)
        confidence_mult = self._confidence_multiplier(confidence)
        market_mult = {"calm": 1.3, "normal": 1.0, "volatile": 0.7, "extreme": 0.4}.get(market_conditions, 1.0)
        position_penalty = max(0.3, 1.0 - (current_positions * 0.15))
        vol_adj = max(0.2, 1.0 - (volatility * 10.0))
        base_leverage = (1.0 / volatility) * confidence_mult * market_mult * position_penalty * vol_adj
        recommended_leverage = max(1.0, min(self.max_leverage, base_leverage))
        risk_amount = account_balance * self.base_risk_per_trade
        position_size = risk_amount * recommended_leverage
        max_position_size = account_balance * self.max_position_fraction
        if position_size > max_position_size:
            position_size = max_position_size
            recommended_leverage = position_size / max(risk_amount, 1e-8)
        recommended_leverage = min(recommended_leverage, self.max_leverage)
        rec = LeverageResult(
            leverage=round(recommended_leverage, 2),
            position_size=round(position_size, 2),
            risk_amount=round(risk_amount, 2),
            risk_percent=round((risk_amount / max(account_balance, 1e-8)) * 100.0, 3),
            volatility=round(volatility * 100.0, 2),
            confidence=round(confidence * 100.0, 1),
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        try:
            get_narration_logger().narrate_info("DYNAMIC_LEVERAGE_RECOMMENDATION", {"pair": pair, "confidence": confidence, "position_size": rec.position_size, "leverage": rec.leverage})
        except Exception:
            pass
        return rec.__dict__


def validate_leverage_against_venue(leverage: float, venue_max: int = 20) -> float:
    return min(leverage, float(venue_max))
"""Compatibility shim for risk.dynamic_leverage.

This file re-exports the clean implementation located at
`risk.dynamic_leverage_clean` to avoid duplicate definitions while
preserving the old import path used throughout the project.
"""

from risk.dynamic_leverage_clean import *  # noqa: F401,F403

"""Dynamic leverage and position sizing utilities for N_RLC_rebuild.

Provides a single authoritative implementation and emits narration
events for debugging and validation during dry-runs.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Dict, Any

import numpy as np

from config.narration_logger import get_narration_logger


@dataclass
class LeverageResult:
    leverage: float
    position_size: float
    risk_amount: float
    risk_percent: float
    volatility: float
    confidence: float
    timestamp: str


class DynamicLeverageCalculator:
    def __init__(self, max_leverage: float = 25.0, base_risk_per_trade: float = 0.002, max_position_fraction: float = 0.15) -> None:
        self.max_leverage = max_leverage
        self.base_risk_per_trade = base_risk_per_trade
        self.max_position_fraction = max_position_fraction
        self.confidence_weights: Dict[float, float] = {0.95: 1.5, 0.85: 1.2, 0.75: 1.0, 0.65: 0.7, 0.55: 0.4}

    def calculate_volatility(self, price_history: List[float], periods: int = 14) -> float:
        if len(price_history) < periods:
            return 0.02
        prices = np.array(price_history[-periods:])
        returns = np.diff(prices) / prices[:-1]
        volatility = float(np.std(returns) * np.sqrt(24.0))
        v = max(0.01, min(0.5, volatility))
        try:
            get_narration_logger().narrate_info("DYNAMIC_LEVERAGE_VOL_CALC", {"periods": periods, "volatility": v})
        except Exception:
            pass
        return v

    def _confidence_multiplier(self, confidence: float) -> float:
        for threshold, multiplier in sorted(self.confidence_weights.items(), reverse=True):
            if confidence >= threshold:
                return multiplier
        return 0.2

    def calculate_for_signal(self, pair: str, confidence: float, price_history: List[float], account_balance: float, current_positions: int = 0, market_conditions: str = "normal") -> LeverageResult:
        volatility = self.calculate_volatility(price_history)
        confidence_mult = self._confidence_multiplier(confidence)
        market_mult_map = {"calm": 1.3, "normal": 1.0, "volatile": 0.7, "extreme": 0.4}
        market_mult = market_mult_map.get(market_conditions, 1.0)
        position_penalty = max(0.3, 1.0 - (current_positions * 0.15))
        vol_adjustment = max(0.2, 1.0 - (volatility * 10.0))
        base_leverage = (1.0 / volatility) * confidence_mult * market_mult * position_penalty * vol_adjustment
        recommended_leverage = max(1.0, min(self.max_leverage, base_leverage))
        risk_amount = account_balance * self.base_risk_per_trade
        position_size = risk_amount * recommended_leverage
        max_position_size = account_balance * self.max_position_fraction
        if position_size > max_position_size:
            position_size = max_position_size
            recommended_leverage = position_size / max(risk_amount, 1e-8)
        if recommended_leverage > self.max_leverage:
            recommended_leverage = self.max_leverage
        result = LeverageResult(
            leverage=round(recommended_leverage, 2),
            position_size=round(position_size, 2),
            risk_amount=round(risk_amount, 2),
            risk_percent=round((risk_amount / max(account_balance, 1e-8)) * 100.0, 3),
            volatility=round(volatility * 100.0, 2),
            confidence=round(confidence * 100.0, 1),
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        try:
            get_narration_logger().narrate_info("DYNAMIC_LEVERAGE_RECOMMENDATION", {"pair": pair, "confidence": confidence, "position_size": result.position_size, "leverage": result.leverage})
        except Exception:
            pass
        return result


def validate_leverage_against_venue(leverage: float, venue_max: int = 20) -> float:
    return min(leverage, float(venue_max))
"""Dynamic leverage and position sizing utilities for N_RLC_rebuild.

This module calculates a conservative leverage recommendation based on
volatility, confidence, and current account state. It emits narration
events to help debug and validate recommendations during dry-runs.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Dict, Any

import numpy as np

from config.narration_logger import get_narration_logger


@dataclass
class LeverageResult:
    leverage: float
    position_size: float
    risk_amount: float
    risk_percent: float
    volatility: float
    confidence: float
    timestamp: str


class DynamicLeverageCalculator:
    """Calculate dynamic leverage and position size for a trade signal.

    This module is intentionally self-contained. Higher-level orchestration
    code is responsible for enforcing RickCharter rules (min notional,
    max concurrent positions, RR >= 3.2, etc.) using the values returned
    here together with OCO TP/SL distances.
    """

    def __init__(
        self,
        max_leverage: float = 25.0,
        base_risk_per_trade: float = 0.002,
        max_position_fraction: float = 0.15,
    ) -> None:
        self.max_leverage = max_leverage
        self.base_risk_per_trade = base_risk_per_trade
        self.max_position_fraction = max_position_fraction

        self.confidence_weights: Dict[float, float] = {
            0.95: 1.5,
            0.85: 1.2,
            0.75: 1.0,
            0.65: 0.7,
            0.55: 0.4,
        }

    def calculate_volatility(self, price_history: List[float], periods: int = 14) -> float:
        """Calculate rolling volatility from price history.

        Returns a value in [0.01, 0.5] representing 1%–50% annualised vol.
        """

        if len(price_history) < periods:
            return 0.02

        prices = np.array(price_history[-periods:])
        returns = np.diff(prices) / prices[:-1]
        volatility = float(np.std(returns) * np.sqrt(24.0))

        v = max(0.01, min(0.5, volatility))
        try:
            get_narration_logger().narrate_info("DYNAMIC_LEVERAGE_VOL_CALC", {"periods": periods, "volatility": v})
        except Exception:
            pass
        return v

    def _confidence_multiplier(self, confidence: float) -> float:
        for threshold, multiplier in sorted(self.confidence_weights.items(), reverse=True):
            if confidence >= threshold:
                return multiplier
        return 0.2

    def calculate_for_signal(
        self,
        pair: str,
        confidence: float,
        price_history: List[float],
        account_balance: float,
        current_positions: int = 0,
        market_conditions: str = "normal",
    ) -> LeverageResult:
        """Return leverage and position sizing for a candidate trade.

        This is a pure calculation: it does not talk to brokers or mutate
        any external state.
        """

        volatility = self.calculate_volatility(price_history)
        confidence_mult = self._confidence_multiplier(confidence)

        market_mult_map: Dict[str, float] = {
            "calm": 1.3,
            "normal": 1.0,
            "volatile": 0.7,
            "extreme": 0.4,
        }
        market_mult = market_mult_map.get(market_conditions, 1.0)

        position_penalty = max(0.3, 1.0 - (current_positions * 0.15))
        vol_adjustment = max(0.2, 1.0 - (volatility * 10.0))

        base_leverage = (1.0 / volatility) * confidence_mult * market_mult * position_penalty * vol_adjustment

        recommended_leverage = max(1.0, min(self.max_leverage, base_leverage))

        risk_amount = account_balance * self.base_risk_per_trade
        position_size = risk_amount * recommended_leverage

        max_position_size = account_balance * self.max_position_fraction
        if position_size > max_position_size:
            position_size = max_position_size
            recommended_leverage = position_size / max(risk_amount, 1e-8)

        if recommended_leverage > self.max_leverage:
            recommended_leverage = self.max_leverage

        result = LeverageResult(
            leverage=round(recommended_leverage, 2),
            position_size=round(position_size, 2),
            risk_amount=round(risk_amount, 2),
            risk_percent=round((risk_amount / max(account_balance, 1e-8)) * 100.0, 3),
            volatility=round(volatility * 100.0, 2),
            confidence=round(confidence * 100.0, 1),
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        try:
            get_narration_logger().narrate_info("DYNAMIC_LEVERAGE_RECOMMENDATION", {
                "pair": pair,
                "confidence": confidence,
                "position_size": result.position_size,
                "leverage": result.leverage,
            })
        except Exception:
            pass

        return result


def validate_leverage_against_venue(leverage: float, venue_max: int = 20) -> float:
    return min(leverage, float(venue_max))
"""Dynamic leverage and position sizing utility
=============================================

This module implements a DynamicLeverageCalculator adapted for the
N_RLC_rebuild project. It is intentionally conservative and integrates
with the charter and guardian gate rules via simple checks.

The main entrypoint is `calculate_for_signal(...)` which returns a dict
with `leverage`, `position_size`, `risk_amount`, `risk_percent`, etc.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import numpy as np
from typing import List, Dict, Any
from config.narration_logger import get_narration_logger

from foundation.rick_charter import RickCharter


@dataclass
class LeverageRecommendation:
    leverage: float
    position_size: float
    risk_amount: float
    risk_percent: float
    volatility: float
    confidence: float
    timestamp: str


class DynamicLeverageCalculator:
    """Calculate leverage and position sizing using volatility & confidence.

    The algorithm is based on volatility (rolling std), confidence multipliers,
    position concentration penalties and a max leverage cap enforced by the
    charter and venue.
    """

    def __init__(self, max_leverage: float = 25.0, base_risk_per_trade: float = 0.02):
        self.max_leverage = max_leverage
        self.base_risk_per_trade = base_risk_per_trade
        # Confidence weights are conservative by default
        self.confidence_weights = {
            0.95: 1.5,
            0.85: 1.2,
            0.75: 1.0,
            0.65: 0.7,
            0.5: 0.4,
        }

    def calculate_volatility(self, price_history: List[float], periods: int = 14) -> float:
        if not price_history or len(price_history) < 2:
            return 0.01
        prices = np.array(price_history[-periods:])
        returns = np.diff(prices) / prices[:-1]
        vol = float(np.std(returns) * np.sqrt(252))
        # Clamp volatility
        v = max(0.005, min(1.0, vol))
        try:
            get_narration_logger().narrate_info("DYNAMIC_LEVERAGE_VOL_CALC", {"periods": periods, "volatility": v})
        except Exception:
            pass
        return v

    def get_confidence_multiplier(self, confidence: float) -> float:
        for thr, mult in sorted(self.confidence_weights.items(), reverse=True):
            if confidence >= thr:
                return mult
        return 0.2

    def calculate_for_signal(
        self,
        pair: str,
        confidence: float,
        price_history: List[float],
        account_balance: float,
        current_positions: int = 0,
        market_conditions: str = "normal",
    ) -> Dict[str, Any]:
        volatility = self.calculate_volatility(price_history)
        confidence_mult = self.get_confidence_multiplier(confidence)

        market_mult = {"calm": 1.3, "normal": 1.0, "volatile": 0.7, "extreme": 0.4}.get(market_conditions, 1.0)
        position_penalty = max(0.3, 1.0 - (current_positions * 0.15))
        vol_adj = max(0.2, 1.0 - (volatility * 10))

        base_leverage = min(self.max_leverage, (1.0 / max(volatility, 0.0001)) * confidence_mult * market_mult * position_penalty * vol_adj)
        recommended_leverage = max(1.0, min(self.max_leverage, base_leverage))

        risk_amount = account_balance * (self.base_risk_per_trade / confidence_mult)
        position_size = max(1.0, min(account_balance * 0.15, risk_amount * recommended_leverage))
        risk_percent = (risk_amount / account_balance) * 100

        # Enforce minimum notional per Charter
        min_notional = RickCharter.MIN_NOTIONAL_USD if hasattr(RickCharter, "MIN_NOTIONAL_USD") else 15000.0
        if position_size < min_notional:
            position_size = min_notional
            # reduce leverage accordingly
            recommended_leverage = max(1.0, position_size / max(1.0, risk_amount))

        rec = LeverageRecommendation(
            leverage=round(recommended_leverage, 2),
            position_size=round(position_size, 2),
            risk_amount=round(risk_amount, 2),
            risk_percent=round(risk_percent, 2),
            volatility=round(volatility, 4),
            confidence=round(confidence, 2),
            timestamp=datetime.utcnow().isoformat(),
        )

        try:
            get_narration_logger().narrate_info("DYNAMIC_LEVERAGE_RECOMMENDATION", {
                "pair": pair,
                "confidence": confidence,
                "position_size": rec.position_size,
                "leverage": rec.leverage,
            })
        except Exception:
            pass
        return rec.__dict__


def validate_leverage_against_venue(leverage: float, venue_max: int = 20) -> float:
    return min(leverage, float(venue_max))
"""Dynamic leverage and position sizing utilities for N_RLC_rebuild.

Derived from legacy RICK futures/FX engines (read-only sources), adapted
to respect the current RickCharter constraints in this project.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Dict, Any

import numpy as np


@dataclass
class LeverageResult:
    leverage: float
    position_size: float
    risk_amount: float
    risk_percent: float
    volatility: float
    confidence: float
    timestamp: str


class DynamicLeverageCalculator:
    """Calculate dynamic leverage and position size for a trade signal.

    This module is intentionally self-contained. Higher-level orchestration
    code is responsible for enforcing RickCharter rules (min notional,
    max concurrent positions, RR >= 3.2, etc.) using the values returned
    here together with OCO TP/SL distances.
    """

    def __init__(
        self,
        max_leverage: float = 25.0,
        base_risk_per_trade: float = 0.002,
        max_position_fraction: float = 0.15,
    ) -> None:
        self.max_leverage = max_leverage
        self.base_risk_per_trade = base_risk_per_trade
        self.max_position_fraction = max_position_fraction

        self.confidence_weights: Dict[float, float] = {
            0.95: 1.5,
            0.85: 1.2,
            0.75: 1.0,
            0.65: 0.7,
            0.55: 0.4,
        }

    def calculate_volatility(self, price_history: List[float], periods: int = 14) -> float:
        """Calculate rolling volatility from price history.

        Returns a value in [0.01, 0.5] representing 1%–50% annualised vol.
        """

        if len(price_history) < periods:
            return 0.02

        prices = np.array(price_history[-periods:])
        returns = np.diff(prices) / prices[:-1]
        volatility = float(np.std(returns) * np.sqrt(24.0))

        return max(0.01, min(0.5, volatility))

    def _confidence_multiplier(self, confidence: float) -> float:
        for threshold, multiplier in sorted(self.confidence_weights.items(), reverse=True):
            if confidence >= threshold:
                return multiplier
        return 0.2

    def calculate_for_signal(
        self,
        pair: str,
        confidence: float,
        price_history: List[float],
        account_balance: float,
        current_positions: int = 0,
        market_conditions: str = "normal",
    ) -> LeverageResult:
        """Return leverage and position sizing for a candidate trade.

        This is a pure calculation: it does not talk to brokers or mutate
        any external state.
        """

        volatility = self.calculate_volatility(price_history)
        confidence_mult = self._confidence_multiplier(confidence)

        market_mult_map: Dict[str, float] = {
            "calm": 1.3,
            "normal": 1.0,
            "volatile": 0.7,
            "extreme": 0.4,
        }
        market_mult = market_mult_map.get(market_conditions, 1.0)

        position_penalty = max(0.3, 1.0 - (current_positions * 0.15))
        vol_adjustment = max(0.2, 1.0 - (volatility * 10.0))

        base_leverage = (1.0 / volatility) * confidence_mult * market_mult * position_penalty * vol_adjustment

        recommended_leverage = max(1.0, min(self.max_leverage, base_leverage))

        risk_amount = account_balance * self.base_risk_per_trade
        position_size = risk_amount * recommended_leverage

        max_position_size = account_balance * self.max_position_fraction
        if position_size > max_position_size:
            position_size = max_position_size
            recommended_leverage = position_size / max(risk_amount, 1e-8)

        if recommended_leverage > self.max_leverage:
            recommended_leverage = self.max_leverage

        return LeverageResult(
            leverage=round(recommended_leverage, 2),
            position_size=round(position_size, 2),
            risk_amount=round(risk_amount, 2),
            risk_percent=round((risk_amount / max(account_balance, 1e-8)) * 100.0, 3),
            volatility=round(volatility * 100.0, 2),
            confidence=round(confidence * 100.0, 1),
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
