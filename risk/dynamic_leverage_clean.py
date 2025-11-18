"""Internal clean implementation of dynamic leverage used in testing.
This file holds the primary code and avoids duplication concerns in the main module.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Dict

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

    def calculate_for_signal(self, pair: str, confidence: float, price_history: List[float], account_balance: float, current_positions: int = 0, market_conditions: str = "normal") -> LeverageResult:
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
        if recommended_leverage > self.max_leverage:
            recommended_leverage = self.max_leverage
        res = LeverageResult(
            leverage=round(recommended_leverage, 2),
            position_size=round(position_size, 2),
            risk_amount=round(risk_amount, 2),
            risk_percent=round((risk_amount / max(account_balance, 1e-8)) * 100.0, 3),
            volatility=round(volatility * 100.0, 2),
            confidence=round(confidence * 100.0, 1),
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        try:
            get_narration_logger().narrate_info("DYNAMIC_LEVERAGE_RECOMMENDATION", {"pair": pair, "confidence": confidence, "position_size": res.position_size, "leverage": res.leverage})
        except Exception:
            pass
        return res


def validate_leverage_against_venue(leverage: float, venue_max: int = 20) -> float:
    return min(leverage, float(venue_max))
