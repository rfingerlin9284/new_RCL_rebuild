# RICK Charter & Gating Logic - Quick Reference Structure

## STRUCTURED LIST FORMAT (as requested)
RULE_NAME | LOCATION | PLATFORMS | KEY_PARAMETERS

---

## CORE CHARTER RULES

### Authentication & Versioning
PIN_841921 | rick_charter.py | ALL | Authentication requirement - hardcoded
CHARTER_V2_IMMUTABLE | foundation/rick_charter.py | ALL | Version 2.0 (RBOTzilla phase 2)
CHARTER_V3_INSTITUTIONAL | rick_clean_live/foundation/rick_charter.py | ALL | Version 3.0 (2025-10-29 upgrade)

### Risk Management Floors
MIN_NOTIONAL_USD | rick_charter.py | ALL | $15,000 minimum per trade
MIN_RISK_REWARD_RATIO | rick_charter.py | ALL | 3.2:1 minimum (Charter compliance)
MIN_EXPECTED_PNL_USD | rick_charter.py | ALL | $100.0 minimum profit at takeprofit
DAILY_LOSS_BREAKER_PCT | rick_charter.py | ALL | -5.0% daily loss = hard halt
MAX_HOLD_DURATION_HOURS | rick_charter.py | ALL | 6 hours maximum position hold
MAX_PLACEMENT_LATENCY_MS | rick_charter.py | ALL | 300ms maximum order placement time

### Position Management
MAX_CONCURRENT_POSITIONS | rick_charter.py, charter.yaml | ALL | 3 maximum open positions
MAX_DAILY_TRADES | rick_charter.py | ALL | 12 maximum daily trades
MAX_MARGIN_UTILIZATION_PCT | rick_charter.py (V3) | ALL | 35% maximum (0.35) NAV
MAX_PORTFOLIO_EXPOSURE_PCT | rick_charter.py (V3) | ALL | 80% maximum (0.80) NAV
CORRELATION_CAP_PCT | rick_charter.py (V3) | ALL | 70% maximum correlation threshold
MIN_MARGIN_USD | rick_charter.py (V3) | ALL | $500 minimum margin per trade

### Timeframe Enforcement
ALLOWED_TIMEFRAMES | rick_charter.py | ALL | M15, M30, H1 only (whitelist)
REJECTED_TIMEFRAMES | rick_charter.py | ALL | M1, M5 explicitly forbidden (blacklist)
TIMEFRAME_VALIDATION | rick_charter.py | ALL | validate_timeframe() method enforces

### Spread & Slippage Gates
FX_MAX_SPREAD_ATR_MULTIPLIER | rick_charter.py | OANDA, IBKR | 0.15x ATR14 maximum
CRYPTO_MAX_SPREAD_ATR_MULTIPLIER | rick_charter.py | Crypto | 0.10x ATR14 maximum (tighter)
FX_STOP_LOSS_ATR_MULTIPLIER | rick_charter.py | OANDA, IBKR | 1.2x ATR for SL placement
CRYPTO_STOP_LOSS_ATR_MULTIPLIER | rick_charter.py | Crypto | 1.5x ATR for SL placement

---

## GUARDIAN GATE SYSTEM (4 Cascading Gates)

### Gate 1: Margin Utilization Gate
GATE_MARGIN | guardian_gates.py | ALL | Threshold: NAV margin_used ≤ 35%
MARGIN_UTILIZATION_CHECK | guardian_gates.py | ALL | Blocks if margin_used/NAV > 0.35
GATE1_REJECTION_MSG | guardian_gates.py | ALL | "Margin utilization {mu:.1%} exceeds Charter max 35%"
GATE1_PASS_MSG | guardian_gates.py | ALL | "Margin OK: {mu:.1%} < 35%"

### Gate 2: Concurrent Positions Gate
GATE_CONCURRENT | guardian_gates.py | ALL | Threshold: open_positions < 3
CONCURRENT_POSITIONS_CHECK | guardian_gates.py | ALL | Blocks if open_count >= 3
GATE2_REJECTION_MSG | guardian_gates.py | ALL | "Open positions {count} >= Charter max 3"
GATE2_PASS_MSG | guardian_gates.py | ALL | "Positions OK: {count} < 3"

### Gate 3: Correlation Exposure Gate (USD Bucket)
GATE_CORRELATION | guardian_gates.py | ALL | Block same-side USD exposure
USD_PAIRS_SCANNED | guardian_gates.py | ALL | [USD, USDT, USDC, BUSD, USDP, TUSD]
CORRELATION_LOGIC | guardian_gates.py | ALL | If symbol AND position both USD + same direction = BLOCK
GATE3_REJECTION_MSG | guardian_gates.py | ALL | "Same-side USD exposure detected: {units} units"
GATE3_PASS_MSG | guardian_gates.py | ALL | "No correlated USD exposure"

### Gate 4: Crypto-Specific Gate (Conditional)
GATE_CRYPTO | guardian_gates.py | Crypto only | Activated if _is_crypto(symbol)
CRYPTO_HIVE_CONSENSUS_MIN | guardian_gates.py | Crypto | 90% minimum (CRYPTO_AI_HIVE_VOTE_CONSENSUS)
CRYPTO_TIME_WINDOW | guardian_gates.py | Crypto | Additional time-window checks
CRYPTO_REGIME_CHECK | guardian_gates.py | Crypto | Regime-based validation
GATE4_REJECTION_MSG | guardian_gates.py | Crypto | "Hive consensus {x}% < 90% required"

---

## GUARDIAN GATES EXECUTION MODEL
GATE_LOGIC_MODEL | guardian_gates.py | ALL | AND logic - ALL 4 gates must PASS
GATE_ORDER | guardian_gates.py | ALL | Margin → Concurrent → Correlation → Crypto(if applicable)
GATE_RESULT | guardian_gates.py | ALL | (all_passed: bool, results: List[GateResult])
GATE_FAILURE_LOGGING | guardian_gates.py | ALL | Logs all failed gate names
PIN_REQUIREMENT | guardian_gates.py | ALL | PIN 841921 verification required at init

---

## QUANT HEDGE RULES SYSTEM (5 Weighted Conditions)

### Condition 1: Volatility Analysis (Weight: 30%)
VOLATILITY_ANALYSIS | quant_hedge_rules.py | ALL | Analyzes market volatility
VOLATILITY_LOW_LEVEL | quant_hedge_rules.py | ALL | 0-1.5% annualized = GREEN
VOLATILITY_MODERATE_LEVEL | quant_hedge_rules.py | ALL | 1.5-3.0% annualized = YELLOW
VOLATILITY_HIGH_LEVEL | quant_hedge_rules.py | ALL | 3.0-5.0% annualized = YELLOW
VOLATILITY_EXTREME_LEVEL | quant_hedge_rules.py | ALL | 5%+ annualized = RED
VOLATILITY_SEVERITY | quant_hedge_rules.py | ALL | HIGH/EXTREME → RED, MODERATE/LOW → GREEN

### Condition 2: Trend Strength (Weight: 25%)
TREND_STRENGTH_ANALYSIS | quant_hedge_rules.py | ALL | Evaluates momentum quality
REGIME_DETECTOR_INTEGRATION | quant_hedge_rules.py | ALL | StochasticRegimeDetector(pin=841921)
TREND_SEVERITY | quant_hedge_rules.py | ALL | Mapped from trend alignment with position

### Condition 3: Correlation Risk (Weight: 20%)
CORRELATION_RISK_ANALYSIS | quant_hedge_rules.py | ALL | Evaluates asset correlation
CORRELATION_LOW | quant_hedge_rules.py | ALL | Independent movement = GREEN
CORRELATION_MODERATE | quant_hedge_rules.py | ALL | Some correlation = YELLOW
CORRELATION_HIGH | quant_hedge_rules.py | ALL | Strong correlation = RED (diversification risk)
CORRELATION_EXTREME | quant_hedge_rules.py | ALL | Perfect correlation = RED
CORRELATION_SEVERITY | quant_hedge_rules.py | ALL | HIGH/EXTREME → RED, MODERATE → YELLOW, LOW → GREEN

### Condition 4: Volume Analysis (Weight: 15%)
VOLUME_ANALYSIS | quant_hedge_rules.py | ALL | Confirms trend with volume bars
VOLUME_CONFIRMATION | quant_hedge_rules.py | ALL | Volume-weighted confirmation check
VOLUME_SEVERITY | quant_hedge_rules.py | ALL | Severity based on volume profile

### Condition 5: Margin Utilization (Weight: 10%)
MARGIN_UTILIZATION_CHECK | quant_hedge_rules.py | ALL | Account health check
MARGIN_THRESHOLD | quant_hedge_rules.py | ALL | Compare against 35% MAX_MARGIN_UTILIZATION_PCT
MARGIN_SEVERITY | quant_hedge_rules.py | ALL | GREEN < 35%, YELLOW 35-50%, RED > 50%

### Hedge Analysis Results
SEVERITY_SCORE | quant_hedge_rules.py | ALL | 0-100 composite score (higher = riskier)
RISK_LEVEL_SAFE | quant_hedge_rules.py | ALL | Severity 0-25 = SAFE
RISK_LEVEL_MODERATE | quant_hedge_rules.py | ALL | Severity 25-50 = MODERATE
RISK_LEVEL_ELEVATED | quant_hedge_rules.py | ALL | Severity 50-75 = ELEVATED
RISK_LEVEL_CRITICAL | quant_hedge_rules.py | ALL | Severity 75-100 = CRITICAL

### Hedge Action Recommendations
HEDGE_ACTION_FULL_LONG | quant_hedge_rules.py | ALL | Aggressive long - all GREEN, high confidence
HEDGE_ACTION_MODERATE_LONG | quant_hedge_rules.py | ALL | Conservative long - mixed conditions
HEDGE_ACTION_REDUCE_EXPOSURE | quant_hedge_rules.py | ALL | Cut 50% - YELLOW severity signals
HEDGE_ACTION_CLOSE_ALL | quant_hedge_rules.py | ALL | Exit all - CRITICAL risk level
HEDGE_ACTION_HEDGE_SHORT | quant_hedge_rules.py | ALL | Add short hedge - high correlation/volatility
HEDGE_ACTION_PAUSE_TRADING | quant_hedge_rules.py | ALL | Stop entries - ELEVATED risk signals
HEDGE_ACTION_WAIT_FOR_CLARITY | quant_hedge_rules.py | ALL | Hold & monitor - uncertain regime
POSITION_SIZE_MULTIPLIER | quant_hedge_rules.py | Crypto | 0.25x (low vol) to 1.5x (high vol)

---

## CONFIGURATION FILES

### charter.yaml Configuration
CONFIG_VERSION | config/charter.yaml | ALL | version: 1
CHARTER_MIN_RR | config/charter.yaml | ALL | risk.min_rr: 3.2
CHARTER_MIN_NOTIONAL | config/charter.yaml | ALL | limits.min_notional_usd: 15000
CHARTER_MAX_CONCURRENT | config/charter.yaml | ALL | limits.max_concurrent_positions: 3
ORDER_POLICY_OCO | config/charter.yaml | ALL | order_policy.oco_required: true

### gates.yaml Configuration
GATES_VERSION | config/gates.yaml | ALL | version: 1
HIVE_ENABLED | config/gates.yaml | ALL | rick_hive.enabled: true
HIVE_QUORUM | config/gates.yaml | ALL | rick_hive.quorum: 3
HIVE_ADVISORS | config/gates.yaml | ALL | news_filter, volatility_regime, trend_bias, mean_reversion (4 advisors)
COMPLIANCE_OCO | config/gates.yaml | ALL | compliance.enforce_oco: true
OANDA_CONNECTOR | config/gates.yaml | OANDA | oanda_practice enabled, paper: true

---

## BROKER-SPECIFIC IMPLEMENTATIONS

### OANDA Charter Bridge
OANDA_BRIDGE_FILE | bridges/oanda_charter_bridge.py | OANDA | Full implementation
OANDA_GET_PRICE | oanda_charter_bridge.py | OANDA | Fetch bid/ask (v20 API)
OANDA_ACCOUNT_SUMMARY | oanda_charter_bridge.py | OANDA | Returns (NAV, margin_used, daily_pl)
OANDA_USD_NOTIONAL | oanda_charter_bridge.py | OANDA | units = ceil(15000.0 / mid) [USD-quoted pairs only]
OANDA_BRACKET_CALCULATION | oanda_charter_bridge.py | OANDA | bracket_for_requirements(direction, entry, units, rr=3.2, min_profit=100.0)
OANDA_RR_ENFORCEMENT | oanda_charter_bridge.py | OANDA | risk_dist = 20pips; profit_dist = MAX(3.2*risk, 100/units)
OANDA_SL_CALCULATION | oanda_charter_bridge.py | OANDA | SL = entry ± risk_dist (20 pips)
OANDA_TP_CALCULATION | oanda_charter_bridge.py | OANDA | TP = entry ± profit_dist (enforced 3.2:1 ratio + $100 min)
OANDA_MARKET_ORDER | oanda_charter_bridge.py | OANDA | FOK (Fill-or-Kill) with attached SL/TP
OANDA_API_ENDPOINT | oanda_charter_bridge.py | OANDA | /v3/accounts/{id}/orders (POST)

### IBKR Charter Bridge
IBKR_BRIDGE_STATUS | [Referenced but not fully implemented] | IBKR | Requires similar bridge to OANDA
IBKR_SUPPORT_PLATFORMS | rick_charter.py | IBKR | Listed alongside OANDA

### Crypto-Specific Platform Rules
CRYPTO_CONSENSUS_THRESHOLD | rick_charter.py, guardian_gates.py | Crypto | 90% hive consensus (vs 65% FX)
CRYPTO_CONFLUENCE_MIN | rick_charter.py | Crypto | 4 of 5 filters must align
CRYPTO_TRADING_WINDOW | rick_charter.py | Crypto | 8am-4pm ET (CRYPTO_TRADING_START_HOUR=8, END_HOUR=16)
CRYPTO_WEEKDAYS_ONLY | rick_charter.py | Crypto | Monday-Friday only (CRYPTO_TRADING_WEEKDAYS_ONLY=True)
CRYPTO_VOLATILITY_SCALE_LOW | rick_charter.py | Crypto | 0.5x position sizing
CRYPTO_VOLATILITY_SCALE_MID | rick_charter.py | Crypto | 1.0x position sizing (normal)
CRYPTO_VOLATILITY_SCALE_HIGH | rick_charter.py | Crypto | 1.5x position sizing

---

## VALIDATION FUNCTIONS (from rick_charter.py)

VALIDATE_PIN | rick_charter.py | ALL | validate_pin(pin: int) → bool
VALIDATE_TIMEFRAME | rick_charter.py | ALL | validate_timeframe(timeframe: str) → bool
VALIDATE_HOLD_DURATION | rick_charter.py | ALL | validate_hold_duration(hours: float) → bool
VALIDATE_RISK_REWARD | rick_charter.py | ALL | validate_risk_reward(ratio: float) → bool
VALIDATE_NOTIONAL | rick_charter.py | ALL | validate_notional(notional_usd: float) → bool
VALIDATE_DAILY_PNL | rick_charter.py | ALL | validate_daily_pnl(daily_pnl_pct: float) → bool
VALIDATE_ALL | rick_charter.py | ALL | validate(test_key: Optional[str]) → bool (comprehensive test)

---

## EXECUTION FLOW (Signal Processing)

1. SIGNAL_ENTRY | All modules | Order triggered by signal
2. PIN_VERIFY | rick_charter.py | Verify PIN 841921
3. TIMEFRAME_CHECK | rick_charter.py | Verify M15/M30/H1 only
4. NOTIONAL_CHECK | rick_charter.py | Verify $15,000 minimum
5. RISK_REWARD_CHECK | rick_charter.py | Verify 3.2:1 minimum
6. GATE1_MARGIN | guardian_gates.py | Check margin_used/NAV ≤ 35%
7. GATE2_CONCURRENT | guardian_gates.py | Check open_count < 3
8. GATE3_CORRELATION | guardian_gates.py | Check no same-side USD exposure
9. GATE4_CRYPTO | guardian_gates.py | Check crypto hive_consensus (if crypto)
10. ALL_GATES_PASSED | guardian_gates.py | All 4 gates AND logic
11. HEDGE_ANALYSIS | quant_hedge_rules.py | 5-condition analysis for sizing
12. ORDER_PLACEMENT | oanda_charter_bridge.py | Place market order with SL/TP
13. POST_TRADE_MONITORING | quant_hedge_rules.py | Ongoing hedge recommendations

---

## FILE LOCATIONS SUMMARY

PRIMARY:
- /home/ing/RICK/RICK_LIVE_CLEAN/foundation/rick_charter.py (v2.0)
- /home/ing/RICK/RICK_LIVE_CLEAN/hive/guardian_gates.py
- /home/ing/RICK/RICK_LIVE_CLEAN/hive/quant_hedge_rules.py
- /home/ing/RICK/RICK_LIVE_CLEAN/config/charter.yaml
- /home/ing/RICK/RICK_LIVE_CLEAN/config/gates.yaml

INSTITUTIONAL UPGRADE:
- /home/ing/RICK/RICK_LIVE_CLEAN/rick_clean_live/foundation/rick_charter.py (v3.0)

CURRENT BUILD:
- /home/ing/RICK/new_RLC_rebuild/foundation/rick_charter.py (v2.0)
- /home/ing/RICK/new_RLC_rebuild/hive/guardian_gates.py
- /home/ing/RICK/new_RLC_rebuild/hive/quant_hedge_rules.py

BROKER INTEGRATION:
- /home/ing/RICK/RICK_LIVE_CLEAN/bridges/oanda_charter_bridge.py

DEPLOYMENT:
- /home/ing/RICK/RICK_LIVE_CLEAN/deploy_institutional_charter.py

---

## QUICK STATISTICS

Total Rules Consolidated: 20+
Charter Versions: 2 (v2.0 Immutable, v3.0 Institutional)
Guardian Gates: 4 (ALL must pass)
Hedge Conditions: 5 (weighted analysis)
Hedge Actions: 7 (positioning recommendations)
Platforms: 3 (OANDA, IBKR reference, Crypto)
Configuration Files: 2 (YAML)
Python Modules: 3 (rick_charter, guardian_gates, quant_hedge_rules)
Broker Bridges: 1 (OANDA implemented)
PIN: 841921 (hardcoded across all modules)

---

## END OF QUICK REFERENCE
Document Generated: 2025-11-14
Status: Complete and Consolidated
