#!/usr/bin/env python3
"""
RICK Charter Enforcement Module - RBOTzilla UNI Phase 2
Immutable trading constants and enforcement logic.
PIN: 841921 | Generated: 2025-09-26

EXTRACTED FROM: WSL Ubuntu /home/ing/RICK/RICK_LIVE_CLEAN
READ ONLY ACCESS - No modifications to source

================================================================================
CONSOLIDATION DOCUMENTATION INTEGRATION
================================================================================

REFERENCE DOCUMENTS (See /home/ing/RICK/new_RLC_rebuild/):
  • CONSOLIDATION_INDEX.md - Master navigation guide (KEPT SEPARATE for records)
  • CHARTER_AND_GATING_CONSOLIDATION.md - Complete charter reference
  • CHARTER_GATING_QUICK_REFERENCE.md - Quick lookup tables
  • RULE_MATRIX_STRUCTURED.md - Master inventory matrix
  • CONSOLIDATION_DELIVERY.md - Project status & statistics

CORE RULES ENFORCED (All Platforms: OANDA, IBKR, Crypto):
  ✓ MIN_NOTIONAL_USD = $15,000 (minimum position value)
  ✓ MIN_RISK_REWARD_RATIO = 3.2:1 (risk/reward ratio requirement)
  ✓ MIN_EXPECTED_PNL_USD = $100.0 (minimum expected profit at TP)
  ✓ MAX_HOLD_DURATION_HOURS = 6 (max time position can stay open)
  ✓ MAX_CONCURRENT_POSITIONS = 3 (maximum open trades)
  ✓ DAILY_LOSS_BREAKER_PCT = -5.0% (stop trading if daily loss exceeds)
  ✓ ALLOWED_TIMEFRAMES = M15, M30, H1 (only these timeframes permitted)
  ✓ REJECTED_TIMEFRAMES = M1, M5 (explicitly forbidden)

GUARDIAN GATES (4 Cascading - ALL must PASS):
  1. Margin Utilization Gate: margin_used / NAV ≤ 35%
  2. Concurrent Positions Gate: open_positions < 3
  3. Correlation Guard: no same-side USD exposure
  4. Crypto Specific Gate: hive_consensus ≥ 90% (if crypto only)

PLATFORM-SPECIFIC RULES:
  • OANDA: 11 features (pricing, brackets, SL/TP calculations)
  • CRYPTO: Specialized rules (90% consensus, time gates, scaling)
  • FX: Institutional rules (65% consensus, ML confidence)

================================================================================
"""

import logging
from typing import Dict, List, Optional, Union
from datetime import timedelta
from enum import Enum

class TimeFrame(Enum):
    """Allowed trading timeframes"""
    M15 = "M15"
    M30 = "M30"
    H1 = "H1"

class RejectedTimeFrame(Enum):
    """Explicitly rejected timeframes"""
    M1 = "M1"
    M5 = "M5"

class RickCharter:
    """
    RICK Charter Core Enforcement - Immutable Constants
    All values are hardcoded for safety and cannot be overridden.
    
    ============================================================================
    CHARTER RULES REFERENCE (See CONSOLIDATION docs for full details)
    ============================================================================
    
    UNIVERSAL RULES (Applied to ALL platforms: OANDA, IBKR, Crypto):
    
    1. NOTIONAL REQUIREMENT
       MIN_NOTIONAL_USD = $15,000
       └─ No position can be opened below this notional value
       └─ If notional < $15,000 → REJECTED at gate
       └─ Platform: ALL
    
    2. RISK-REWARD RATIO
       MIN_RISK_REWARD_RATIO = 3.2:1
       └─ Required ratio of potential profit to potential loss
       └─ If ratio < 3.2 → REJECTED at guardian gate
       └─ Calculation: (TP - Entry) / (Entry - SL) ≥ 3.2
       └─ Platform: ALL
    
    3. MINIMUM PROFIT AT TARGET
       MIN_EXPECTED_PNL_USD = $100.0
       └─ Gross profit at take profit must be at least $100
       └─ If PnL at TP < $100 → REJECTED
       └─ Ensures meaningful trades (not micro trades)
       └─ Platform: ALL
    
    4. MAXIMUM HOLD TIME
       MAX_HOLD_DURATION_HOURS = 6
       └─ Position cannot stay open longer than 6 hours
       └─ At 6-hour mark → FORCE CLOSE at market
       └─ Prevents overnight risk accumulation
       └─ Platform: ALL
    
    5. CONCURRENT POSITION LIMIT
       MAX_CONCURRENT_POSITIONS = 3
       └─ Maximum 3 open positions at any time
       └─ If 3 open → No new trades until one closes
       └─ Platform: ALL
    
    6. DAILY LOSS BREAKER
       DAILY_LOSS_BREAKER_PCT = -5.0%
       └─ If cumulative daily loss ≥ -5% → Stop all new trades
       └─ Existing positions still managed autonomously
       └─ Prevents catastrophic daily losses
       └─ Platform: ALL
    
    7. ALLOWED TIMEFRAMES
       ALLOWED_TIMEFRAMES = [M15, M30, H1]
       └─ Only these timeframes permitted for trade entry signals
       └─ M15: 15-minute candles
       └─ M30: 30-minute candles
       └─ H1: 1-hour candles
       └─ Platform: ALL
    
    8. REJECTED TIMEFRAMES
       REJECTED_TIMEFRAMES = [M1, M5]
       └─ M1 (1-minute) and M5 (5-minute) explicitly forbidden
       └─ Too noisy for institutional trading
       └─ Any signal from M1/M5 → REJECTED
       └─ Platform: ALL
    
    EXECUTION CONSTRAINTS:
    
    9. MAXIMUM DAILY TRADES
       MAX_DAILY_TRADES = 12
       └─ Maximum 12 new trades per day
       └─ After 12 trades → Stop new entries
       └─ Existing positions still managed
    
    10. ORDER PLACEMENT LATENCY
        MAX_PLACEMENT_LATENCY_MS = 300
        └─ Orders must execute within 300ms
        └─ If latency > 300ms → Retry or reject
    
    SPREAD & SLIPPAGE GATES:
    
    11. FX SPREAD GATE
        FX_MAX_SPREAD_ATR_MULTIPLIER = 0.15
        └─ FX spreads cannot exceed 0.15x ATR14
        └─ Prevents trading in tight spreads
        └─ Platform: OANDA, IBKR (FX pairs)
    
    12. CRYPTO SPREAD GATE
        CRYPTO_MAX_SPREAD_ATR_MULTIPLIER = 0.10
        └─ Crypto spreads cannot exceed 0.10x ATR14
        └─ More restrictive than FX
        └─ Platform: Coinbase
    
    13. STOP LOSS SIZING (FX)
        FX_STOP_LOSS_ATR_MULTIPLIER = 1.2
        └─ FX SL must be at least 1.2x ATR14 away from entry
        └─ Prevents whipsaws in low volatility
        └─ Platform: OANDA, IBKR
    
    14. STOP LOSS SIZING (Crypto)
        CRYPTO_STOP_LOSS_ATR_MULTIPLIER = 1.5
        └─ Crypto SL must be at least 1.5x ATR14 away
        └─ Higher requirement due to crypto volatility
        └─ Platform: Coinbase
    
    ============================================================================
    GUARDIAN GATES (4 Cascading Checks - ALL must PASS)
    ============================================================================
    
    See: hive/guardian_gates.py for complete implementation
    
    Gate 1: MARGIN UTILIZATION
      └─ Check: margin_used / NAV ≤ 35%
      └─ Pass → Continue to Gate 2
      └─ Fail → REJECT trade
    
    Gate 2: CONCURRENT POSITIONS
      └─ Check: current_open_positions < 3
      └─ Pass → Continue to Gate 3
      └─ Fail → REJECT trade
    
    Gate 3: CORRELATION GUARD
      └─ Check: no same-side USD exposure
      └─ Pass → Continue to Gate 4
      └─ Fail → REJECT trade
    
    Gate 4: CRYPTO CONSENSUS (if crypto only)
      └─ Check: hive_consensus ≥ 90%
      └─ Pass → EXECUTE trade
      └─ Fail → REJECT trade
    
    ============================================================================
    QUANT HEDGE SYSTEM (5 Weighted Conditions)
    ============================================================================
    
    See: hive/quant_hedge_rules.py for complete implementation
    
    Condition 1: VOLATILITY (Weight: 30%)
      └─ Severity levels: LOW, MODERATE, ELEVATED, CRITICAL
      └─ ATR-based calculation
      └─ Triggers hedge if ELEVATED or CRITICAL
    
    Condition 2: TREND STRENGTH (Weight: 25%)
      └─ Momentum analysis
      └─ ADX-based trend detection
      └─ Weak trends increase hedge probability
    
    Condition 3: CORRELATION RISK (Weight: 20%)
      └─ Position diversification check
      └─ USD correlation analysis
      └─ High correlation increases hedge
    
    Condition 4: VOLUME CONFIRMATION (Weight: 15%)
      └─ Trend validation via volume
      └─ Low volume = weak signal
      └─ Can trigger hedge or pause
    
    Condition 5: MARGIN UTILIZATION (Weight: 10%)
      └─ Account health check
      └─ High utilization = reduce exposure
    
    HEDGE ACTIONS (7 Possible Recommendations):
      1. FULL_LONG → Aggressive long (all GREEN, high confidence)
      2. MODERATE_LONG → Conservative long (mixed conditions)
      3. REDUCE_EXPOSURE → Cut 50% (YELLOW signals)
      4. CLOSE_ALL → Exit all positions (CRITICAL risk)
      5. HEDGE_SHORT → Add short hedge (correlation/vol risk)
      6. PAUSE_TRADING → Stop new entries (ELEVATED risk)
      7. WAIT_FOR_CLARITY → Hold & monitor (uncertain market)
    
    ============================================================================
    PLATFORM-SPECIFIC IMPLEMENTATIONS
    ============================================================================
    
    See: bridges/oanda_charter_bridge.py (OANDA integration)
    
    OANDA Features:
      ✓ Dynamic spread monitoring
      ✓ Bracket order enforcement (SL + TP)
      ✓ ATR14 calculation per pair
      ✓ Slippage tracking
      ✓ Latency measurement
      ✓ Commission model: Spread only (pip-based)
      ✓ Pricing: Bid-Ask spread
      ✓ Timeframe: M15, M30, H1 (per charter)
      ✓ Leverage: Per pair rules
      ✓ Order types: Market, Limit, Stop
      ✓ Position sizing: Dynamic via charter
    
    CRYPTO Features (Coinbase):
      ✓ 90% hive consensus required
      ✓ Time-based gates (market hours check)
      ✓ Volume confirmation required
      ✓ Position scaling available
      ✓ Higher SL requirement (1.5x ATR)
    
    FX Features (IBKR):
      ✓ 65% hive consensus
      ✓ ML confidence scoring
      ✓ Institutional sizing
      ✓ Standard SL (1.2x ATR)
    
    ============================================================================
    USAGE REFERENCE
    ============================================================================
    
    Complete documentation in:
      /home/ing/RICK/new_RLC_rebuild/CONSOLIDATION_INDEX.md (MASTER INDEX - kept separate)
      /home/ing/RICK/new_RLC_rebuild/CHARTER_AND_GATING_CONSOLIDATION.md
      /home/ing/RICK/new_RLC_rebuild/CHARTER_GATING_QUICK_REFERENCE.md
      /home/ing/RICK/new_RLC_rebuild/RULE_MATRIX_STRUCTURED.md
      /home/ing/RICK/new_RLC_rebuild/CONSOLIDATION_DELIVERY.md
    
    ============================================================================
    """

    # CORE AUTHENTICATION
    PIN = 841921
    CHARTER_VERSION = "2.0_IMMUTABLE"

    # TRADING CONSTRAINTS
    MAX_HOLD_DURATION_HOURS = 6
    MAX_HOLD_DURATION = timedelta(hours=MAX_HOLD_DURATION_HOURS)

    # RISK MANAGEMENT
    DAILY_LOSS_BREAKER_PCT = -5.0  # -5% daily loss halt
    MIN_NOTIONAL_USD = 15000
    MIN_EXPECTED_PNL_USD = 100.0  # Gross PnL at TP must be >= $100

    # Minimum risk-reward ratio (guide compliance: 3.2)
    MIN_RISK_REWARD_RATIO = 3.2

    # TIMEFRAME ENFORCEMENT
    ALLOWED_TIMEFRAMES = [TimeFrame.M15, TimeFrame.M30, TimeFrame.H1]
    REJECTED_TIMEFRAMES = [RejectedTimeFrame.M1, RejectedTimeFrame.M5]

    # EXECUTION LIMITS
    MAX_CONCURRENT_POSITIONS = 3
    MAX_DAILY_TRADES = 12
    MAX_PLACEMENT_LATENCY_MS = 300  # Maximum 300ms for order placement

    # SPREAD & SLIPPAGE GATES
    FX_MAX_SPREAD_ATR_MULTIPLIER = 0.15    # 0.15x ATR14
    CRYPTO_MAX_SPREAD_ATR_MULTIPLIER = 0.10 # 0.10x ATR14

    # STOP LOSS REQUIREMENTS
    FX_STOP_LOSS_ATR_MULTIPLIER = 1.2      # 1.2x ATR
    CRYPTO_STOP_LOSS_ATR_MULTIPLIER = 1.5  # 1.5x ATR

    @classmethod
    def validate_pin(cls, pin: int) -> bool:
        """Validate PIN for charter access"""
        return pin == cls.PIN

    @classmethod
    def validate_timeframe(cls, timeframe: str) -> bool:
        """Validate if timeframe is allowed"""
        # Check if it's in allowed timeframes
        allowed_values = [tf.value for tf in cls.ALLOWED_TIMEFRAMES]
        if timeframe in allowed_values:
            return True

        # Explicitly reject forbidden timeframes
        rejected_values = [tf.value for tf in cls.REJECTED_TIMEFRAMES]
        if timeframe in rejected_values:
            return False

        # Unknown timeframe - reject by default
        return False

    @classmethod
    def validate_hold_duration(cls, hours: float) -> bool:
        """Validate position hold duration"""
        return 0 < hours <= cls.MAX_HOLD_DURATION_HOURS

    @classmethod
    def validate_risk_reward(cls, risk_reward_ratio: float) -> bool:
        """Validate risk-reward ratio meets minimum"""
        return risk_reward_ratio >= cls.MIN_RISK_REWARD_RATIO

    @classmethod
    def validate_notional(cls, notional_usd: float) -> bool:
        """Validate minimum notional size"""
        return notional_usd >= cls.MIN_NOTIONAL_USD

    @classmethod
    def validate_daily_pnl(cls, daily_pnl_pct: float) -> bool:
        """Validate daily PnL hasn't hit breaker"""
        return daily_pnl_pct > cls.DAILY_LOSS_BREAKER_PCT

    @classmethod
    def validate(cls, test_key: Optional[str] = None) -> bool:
        """
        Charter validation test
        Returns True if all charter constants are properly set
        """
        try:
            # Test all core constants exist and are correct type
            assert cls.PIN == 841921, "PIN mismatch"
            assert isinstance(cls.MAX_HOLD_DURATION_HOURS, int), "Hold duration type error"
            assert cls.MAX_HOLD_DURATION_HOURS == 6, "Hold duration value error"
            assert cls.DAILY_LOSS_BREAKER_PCT == -5.0, "Loss breaker error"
            assert cls.MIN_NOTIONAL_USD == 15000, "Notional minimum error"
            assert cls.MIN_RISK_REWARD_RATIO == 3.2, "Risk reward error"
            assert cls.MIN_EXPECTED_PNL_USD == 100.0, "Expected PnL minimum error"

            # Test timeframe enforcement
            assert cls.validate_timeframe("M15") == True, "M15 should be allowed"
            assert cls.validate_timeframe("M30") == True, "M30 should be allowed"
            assert cls.validate_timeframe("H1") == True, "H1 should be allowed"
            assert cls.validate_timeframe("M1") == False, "M1 should be rejected"
            assert cls.validate_timeframe("M5") == False, "M5 should be rejected"

            # Test validation functions
            assert cls.validate_hold_duration(6) == True, "6h should be valid"
            assert cls.validate_hold_duration(7) == False, "7h should be invalid"
            assert cls.validate_risk_reward(3.2) == True, "3.2 RR should be valid"
            assert cls.validate_risk_reward(3.1) == False, "3.1 RR should be invalid"
            assert cls.validate_notional(15000) == True, "15k should be valid"
            assert cls.validate_notional(14999) == False, "14999 should be invalid"
            assert cls.validate_daily_pnl(-4.9) == True, "-4.9% should be valid"
            assert cls.validate_daily_pnl(-5.1) == False, "-5.1% should hit breaker"

            logging.info("RICK Charter validation PASSED ✅")
            return True

        except AssertionError as e:
            logging.error(f"RICK Charter validation FAILED: {e}")
            return False
        except Exception as e:
            logging.error(f"RICK Charter validation ERROR: {e}")
            return False

    @classmethod
    def get_charter_summary(cls) -> Dict[str, Union[int, float, str, List[str]]]:
        """Return complete charter summary for logging"""
        return {
            "pin": cls.PIN,
            "version": cls.CHARTER_VERSION,
            "max_hold_hours": cls.MAX_HOLD_DURATION_HOURS,
            "daily_loss_breaker": cls.DAILY_LOSS_BREAKER_PCT,
            "min_notional_usd": cls.MIN_NOTIONAL_USD,
            "min_risk_reward": cls.MIN_RISK_REWARD_RATIO,
            "min_expected_pnl_usd": cls.MIN_EXPECTED_PNL_USD,
            "allowed_timeframes": [tf.value for tf in cls.ALLOWED_TIMEFRAMES],
            "rejected_timeframes": [tf.value for tf in cls.REJECTED_TIMEFRAMES],
            "max_concurrent": cls.MAX_CONCURRENT_POSITIONS,
            "max_daily_trades": cls.MAX_DAILY_TRADES
        }

# Charter enforcement on module import
if __name__ == "__main__":
    # Self-test on direct execution
    result = RickCharter.validate("test")
    print(f"Charter Validation: {'PASS' if result else 'FAIL'}")
    if result:
        summary = RickCharter.get_charter_summary()
        print("Charter Summary:", summary)
else:
    # Validate on import
    _validation_result = RickCharter.validate()
    if not _validation_result:
        raise ImportError("RICK Charter validation failed - module import blocked")