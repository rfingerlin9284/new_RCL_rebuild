"""Strategy selector and edge optimizer
=====================================

Simple ranking and selection algorithm to weight your S/A‑tier
strategies and return active strategies for a given context.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import datetime
import random


@dataclass
class StrategyMeta:
    id: str
    name: str
    base_win_rate: float
    base_rr: float
    max_hold_hours: float
    markets: List[str]
    last_seen: str = ""


class StrategySelector:
    def __init__(self):
        # Minimal strategy inventory using the user's summary
        self._strategies = {
            "trap_reversal": StrategyMeta("trap_reversal", "Trap Reversal Scalper", 0.9, 1.1, 0.1, ["futures", "crypto", "fx"]),
            "institutional_sd": StrategyMeta("institutional_sd", "Institutional S&D + Liquidity Sweep", 0.72, 3.1, 4.0, ["fx", "futures", "crypto"]),
            "holy_grail_pa": StrategyMeta("holy_grail_pa", "Price Action Pack", 0.76, 2.3, 4.0, ["fx", "crypto", "equities"]),
            "break_fib": StrategyMeta("break_fib", "Break + Fib", 0.68, 2.5, 3.0, ["fx", "crypto"]),
            "ema_macd": StrategyMeta("ema_macd", "EMA+MACD Pulse", 0.67, 1.25, 0.25, ["crypto", "futures"]),
        }

        # Run-state tracking for rolling performance; in production this
        # would be persisted and aggregated across sessions.
        self._runtime_stats: Dict[str, Dict[str, Any]] = {k: {"wins": 0, "losses": 0, "pnl": 0.0} for k in self._strategies}

    def rank_strategies(self, context: Dict[str, Any]) -> List[StrategyMeta]:
        # Very simple rank: prefer strategies that support the market & have higher base win rate.
        market = context.get("market", "fx")
        viable = [s for s in self._strategies.values() if market in s.markets]
        # Apply simple live performance weight if available
        def score(s: StrategyMeta) -> float:
            rt = self._runtime_stats.get(s.id, {})
            pnl = rt.get("pnl", 0.0)
            wins = rt.get("wins", 0)
            losses = rt.get("losses", 0)
            perf_multiplier = 1.0 + (pnl / 10000.0)
            return s.base_win_rate * perf_multiplier

        viable.sort(key=score, reverse=True)
        return viable

    def select_active_strategies(self, context: Dict[str, Any], max_strategies: int = 2) -> List[str]:
        ranked = self.rank_strategies(context)
        return [s.id for s in ranked[:max_strategies]]

    def assign_capital_weights(self, ranked_strategies: List[str], total_risk_budget: float) -> Dict[str, float]:
        # proportional split by base_win_rate from inventory
        weights = {}
        total = sum([self._strategies[s].base_win_rate for s in ranked_strategies]) if ranked_strategies else 1
        for s in ranked_strategies:
            weight = (self._strategies[s].base_win_rate / total) if total > 0 else 1/len(ranked_strategies)
            weights[s] = round(weight * total_risk_budget, 4)
        return weights


_selector: StrategySelector | None = None


def get_strategy_selector() -> StrategySelector:
    global _selector
    if _selector is None:
        _selector = StrategySelector()
    return _selector
"""Strategy selection and edge weighting for N_RLC_rebuild.

This module encapsulates the S/A-tier strategies extracted from the
TurboScribe mining work and provides ranking + weighting utilities.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Any


@dataclass
class StrategyMeta:
    id: str
    name: str
    baseline_win_rate: float
    baseline_rr: float
    max_drawdown: float
    typical_hold_hours: float
    markets: List[str]


@dataclass
class StrategyRank:
    meta: StrategyMeta
    score: float
    weight: float


STRATEGIES: Dict[str, StrategyMeta] = {
    "trap_reversal_scalper": StrategyMeta(
        id="trap_reversal_scalper",
        name="Trap Reversal Scalper",
        baseline_win_rate=0.92,
        baseline_rr=1.1,
        max_drawdown=0.042,
        typical_hold_hours=0.05,
        markets=["futures", "crypto", "fx"],
    ),
    "institutional_sd_liquidity_sweep": StrategyMeta(
        id="institutional_sd_liquidity_sweep",
        name="Institutional S&D + Liquidity Sweep",
        baseline_win_rate=0.72,
        baseline_rr=3.1,
        max_drawdown=0.058,
        typical_hold_hours=3.0,
        markets=["futures", "fx", "crypto"],
    ),
    "price_action_holy_grail": StrategyMeta(
        id="price_action_holy_grail",
        name="Price Action Holy Grail Pack",
        baseline_win_rate=0.76,
        baseline_rr=2.3,
        max_drawdown=0.05,
        typical_hold_hours=3.0,
        markets=["futures", "fx", "crypto", "equities"],
    ),
    "break_fib_confluence": StrategyMeta(
        id="break_fib_confluence",
        name="Break + Fibonacci Confluence",
        baseline_win_rate=0.68,
        baseline_rr=2.5,
        max_drawdown=0.06,
        typical_hold_hours=3.0,
        markets=["fx", "crypto"],
    ),
    "ema_trend_macd_pulse": StrategyMeta(
        id="ema_trend_macd_pulse",
        name="5-min EMA Trend + MACD 1m Pulse",
        baseline_win_rate=0.67,
        baseline_rr=1.25,
        max_drawdown=0.051,
        typical_hold_hours=0.15,
        markets=["crypto", "futures"],
    ),
}


def rank_strategies(context: Dict[str, Any]) -> List[StrategyRank]:
    """Rank strategies for the current context.

    Context may include: market, volatility, regime, time_of_day,
    account_balance, recent_performance, etc. For now this uses a simple
    heuristic combining baseline stats with rough regime alignment.
    """

    market = str(context.get("market", "fx"))
    regime = str(context.get("regime", "normal"))
    recent_pnl = float(context.get("recent_pnl", 0.0))

    ranks: List[StrategyRank] = []

    for meta in STRATEGIES.values():
        if market not in meta.markets:
            continue

        score = meta.baseline_win_rate * meta.baseline_rr
        if meta.max_drawdown > 0:
            score /= (1.0 + meta.max_drawdown)

        if regime in {"trend", "momentum"} and "trend" in meta.id:
            score *= 1.1

        if recent_pnl < 0:
            score *= 0.9

        ranks.append(StrategyRank(meta=meta, score=score, weight=0.0))

    total_score = sum(r.score for r in ranks) or 1.0
    for r in ranks:
        r.weight = r.score / total_score

    ranks.sort(key=lambda r: r.score, reverse=True)
    return ranks


def select_active_strategies(context: Dict[str, Any], max_strategies: int = 3) -> List[StrategyRank]:
    ranks = rank_strategies(context)
    return ranks[:max_strategies]


def assign_capital_weights(ranks: List[StrategyRank], total_risk_budget: float) -> Dict[str, float]:
    if not ranks:
        return {}

    total_weight = sum(r.weight for r in ranks) or 1.0
    return {r.meta.id: (r.weight / total_weight) * total_risk_budget for r in ranks}
