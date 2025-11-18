# RICK Charter & Gating Logic - Master Rule Matrix

## REQUESTED FORMAT: RULE_NAME | LOCATION | PLATFORMS | KEY_PARAMETERS

### AMENDMENT 841921: REPOSITORY IMMUTABILITY & FILE OPERATIONS CONTROL

CLAUSE_IMMUTABILITY_EFFECTIVE_TS | RULE_MATRIX_STRUCTURED.md | ALL | Effective 2025-11-16: Assistant is prohibited from renaming, deleting, or creating new files anywhere in the repository without explicit user message containing phrase "approved 841921"
CLAUSE_ALLOWED_ACTIONS | RULE_MATRIX_STRUCTURED.md | ALL | Edits to existing file contents permitted (non-structural) unless later amendment revokes; structural operations (create/rename/delete/move) blocked
CLAUSE_EXCEPTION_APPROVAL | RULE_MATRIX_STRUCTURED.md | ALL | File structural changes require explicit approval token "approved 841921" in the same user instruction
CLAUSE_AUDIT_TRAIL | RULE_MATRIX_STRUCTURED.md | ALL | Any structurally approved change must append a timestamped one-line entry to `FIXES_APPLIED.md` documenting action
CLAUSE_SCOPE | RULE_MATRIX_STRUCTURED.md | ALL | Applies to all agent automation until superseded by newer dated amendment citing token "approved 841921"


### SECTION 1: CORE CHARTER RULES (foundation/rick_charter.py)

**AUTHENTICATION**
PIN_841921 | rick_charter.py | ALL | Hardcoded constant = 841921, validate_pin() method required

**POSITION SIZING MINIMUMS**
MIN_NOTIONAL_USD | rick_charter.py | ALL | $15,000 minimum notional per trade (validate_notional method)
MIN_EXPECTED_PNL_USD | rick_charter.py | ALL | $100.0 minimum profit at takeprofit level

**RISK-REWARD REQUIREMENTS**
MIN_RISK_REWARD_RATIO | rick_charter.py | ALL | 3.2:1 minimum (enforced via validate_risk_reward method)

**POSITION MANAGEMENT**
MAX_HOLD_DURATION_HOURS | rick_charter.py | ALL | 6 hours maximum, validated via validate_hold_duration method
MAX_CONCURRENT_POSITIONS | rick_charter.py | ALL | 3 maximum open positions (enforced by Gate 2)
MAX_DAILY_TRADES | rick_charter.py | ALL | 12 maximum trades per day
DAILY_LOSS_BREAKER_PCT | rick_charter.py | ALL | -5.0% daily loss triggers hard halt

**EXECUTION TIMING**
MAX_PLACEMENT_LATENCY_MS | rick_charter.py | ALL | 300ms maximum order placement latency

**TIMEFRAME ENFORCEMENT**
ALLOWED_TIMEFRAMES | rick_charter.py | ALL | M15, M30, H1 (whitelist only - validate_timeframe returns TRUE)
REJECTED_TIMEFRAMES | rick_charter.py | ALL | M1, M5 (explicitly forbidden - validate_timeframe returns FALSE)

**SPREAD & SLIPPAGE GATES**
FX_MAX_SPREAD_ATR_MULTIPLIER | rick_charter.py | OANDA, IBKR | 0.15x ATR14 maximum allowed spread
CRYPTO_MAX_SPREAD_ATR_MULTIPLIER | rick_charter.py | Crypto | 0.10x ATR14 maximum allowed spread (tighter requirement)

**STOP LOSS REQUIREMENTS**
FX_STOP_LOSS_ATR_MULTIPLIER | rick_charter.py | OANDA, IBKR | 1.2x ATR for SL placement calculation
CRYPTO_STOP_LOSS_ATR_MULTIPLIER | rick_charter.py | Crypto | 1.5x ATR for SL placement calculation

---

### SECTION 2: INSTITUTIONAL CHARTER EXTENSIONS (rick_clean_live/foundation/rick_charter.py v3.0)

**MARGIN MANAGEMENT**
MAX_MARGIN_UTILIZATION_PCT | rick_charter.py (v3.0) | ALL | 35% maximum margin utilization (0.35 ratio)
MIN_MARGIN_USD | rick_charter.py (v3.0) | ALL | $500 minimum margin per trade

**PORTFOLIO CONSTRAINTS**
MAX_PORTFOLIO_EXPOSURE_PCT | rick_charter.py (v3.0) | ALL | 80% maximum total portfolio exposure (0.80 ratio)
CORRELATION_CAP_PCT | rick_charter.py (v3.0) | ALL | 70% maximum correlation threshold (0.70 ratio)

**CRYPTO-SPECIFIC RULES**
CRYPTO_HIVE_CONSENSUS_MIN | rick_charter.py (v3.0) | Crypto | 90% minimum hive voting consensus
CRYPTO_CONFLUENCE_MIN | rick_charter.py (v3.0) | Crypto | 4 of 5 filters must align/converge
CRYPTO_TRADING_START_HOUR | rick_charter.py (v3.0) | Crypto | 8 (8am ET start time)
CRYPTO_TRADING_END_HOUR | rick_charter.py (v3.0) | Crypto | 16 (4pm ET end time)
CRYPTO_TRADING_WEEKDAYS_ONLY | rick_charter.py (v3.0) | Crypto | TRUE (Monday-Friday only)

**FX-SPECIFIC RULES**
HIVE_CONSENSUS_MIN_FX | rick_charter.py (v3.0) | FX | 65% minimum hive voting consensus
ML_WEIGHTED_TALLY_MIN | rick_charter.py (v3.0) | FX | 0.75 minimum ML confidence score
SMART_LOGIC_FILTERS_REQUIRED | rick_charter.py (v3.0) | FX | 5 (all 5 filters must pass)

**VOLATILITY-BASED POSITION SIZING**
CRYPTO_VOLATILITY_SCALE_LOW | rick_charter.py (v3.0) | Crypto | 0.5x normal position size in low volatility
CRYPTO_VOLATILITY_SCALE_MID | rick_charter.py (v3.0) | Crypto | 1.0x normal position size in normal volatility
CRYPTO_VOLATILITY_SCALE_HIGH | rick_charter.py (v3.0) | Crypto | 1.5x normal position size in high volatility

---

### SECTION 3: GUARDIAN GATES SYSTEM (hive/guardian_gates.py)

**GATE ARCHITECTURE**
GATE_LOGIC_MODEL | guardian_gates.py | ALL | AND logic: ALL 4 gates MUST PASS before order placement
GATE_EXECUTION_ORDER | guardian_gates.py | ALL | Gate1 (margin) → Gate2 (concurrent) → Gate3 (correlation) → Gate4 (crypto-if-applicable)
GATE_PIN_REQUIREMENT | guardian_gates.py | ALL | PIN 841921 verification required in __init__
GATE_RESULT_FORMAT | guardian_gates.py | ALL | Returns (all_passed: bool, results: List[GateResult])

**GATE 1: MARGIN UTILIZATION GATE**
GATE_MARGIN_CHECK | guardian_gates.py | ALL | Block if: margin_used / NAV > 0.35 (35%)
GATE1_VALIDATION | guardian_gates.py | ALL | mu = margin_used / nav; passes if mu <= MAX_MARGIN_UTILIZATION_PCT
GATE1_FAILURE_MSG | guardian_gates.py | ALL | "Margin utilization {mu:.1%} exceeds Charter max {max_mu:.1%}"
GATE1_SUCCESS_MSG | guardian_gates.py | ALL | "Margin OK: {mu:.1%} < {max_mu:.1%}"
GATE1_PURPOSE | guardian_gates.py | ALL | Prevent over-leverage and account liquidation risk

**GATE 2: CONCURRENT POSITIONS GATE**
GATE_CONCURRENT_CHECK | guardian_gates.py | ALL | Block if: open_positions >= 3
GATE2_VALIDATION | guardian_gates.py | ALL | open_count = len(positions); passes if open_count < MAX_CONCURRENT_POSITIONS
GATE2_FAILURE_MSG | guardian_gates.py | ALL | "Open positions {open_count} >= Charter max {max_concurrent}"
GATE2_SUCCESS_MSG | guardian_gates.py | ALL | "Positions OK: {open_count} < {max_concurrent}"
GATE2_PURPOSE | guardian_gates.py | ALL | Limit concentration and avoid correlation drag

**GATE 3: CORRELATION EXPOSURE GUARD (USD BUCKET)**
GATE_CORRELATION_CHECK | guardian_gates.py | ALL | Block if: same_side_USD_exposure > 0
GATE3_SCANNING_PAIRS | guardian_gates.py | ALL | Scans for: USD, USDT, USDC, BUSD, USDP, TUSD
GATE3_LOGIC | guardian_gates.py | ALL | If (symbol contains USD) AND (position contains USD) AND (same direction) → BLOCK
GATE3_VALIDATION | guardian_gates.py | ALL | same_side_exposure = sum(units where USD-pair AND same_side); passes if = 0
GATE3_FAILURE_MSG | guardian_gates.py | ALL | "Same-side USD exposure detected: {same_side_exposure} units"
GATE3_SUCCESS_MSG | guardian_gates.py | ALL | "No correlated USD exposure"
GATE3_PURPOSE | guardian_gates.py | ALL | Prevent basket correlation disaster (all same direction)

**GATE 4: CRYPTO-SPECIFIC GATE (CONDITIONAL)**
GATE_CRYPTO_TRIGGER | guardian_gates.py | Crypto | Activated ONLY if _is_crypto(signal.symbol) returns TRUE
GATE_CRYPTO_CONSENSUS | guardian_gates.py | Crypto | Requires: hive_consensus >= RickCharter.CRYPTO_AI_HIVE_VOTE_CONSENSUS (0.90)
GATE4_TIME_WINDOW | guardian_gates.py | Crypto | Additional crypto-specific time window checks
GATE4_REGIME_CHECK | guardian_gates.py | Crypto | Regime-based validation filters
GATE4_VALIDATION | guardian_gates.py | Crypto | hive_consensus = signal.get('hive_consensus', 0.0); passes if >= 0.90
GATE4_FAILURE_MSG | guardian_gates.py | Crypto | "Hive consensus {hive_consensus:.0%} < {min_consensus:.0%} required"
GATE4_SUCCESS_MSG | guardian_gates.py | Crypto | "Crypto consensus OK: {hive_consensus:.0%} >= {min_consensus:.0%}"
GATE4_PURPOSE | guardian_gates.py | Crypto | Extra protection for volatile crypto assets

---

### SECTION 4: QUANT HEDGE RULES SYSTEM (hive/quant_hedge_rules.py)

**SYSTEM ARCHITECTURE**
QUANT_HEDGE_CLASS | quant_hedge_rules.py | ALL | QuantHedgeRules(pin: int = 841921)
QUANT_HEDGE_METHOD | quant_hedge_rules.py | ALL | analyze_market_conditions() returns QuantHedgeAnalysis
QUANT_HEDGE_PIN_REQUIREMENT | quant_hedge_rules.py | ALL | PIN 841921 verification required in __init__
QUANT_HEDGE_REGIME_DETECTOR | quant_hedge_rules.py | ALL | Integrated StochasticRegimeDetector(pin=841921)

**CONDITION 1: VOLATILITY ANALYSIS (Weight: 30%)**
VOLATILITY_CLASSIFICATION | quant_hedge_rules.py | ALL | LOW (0-1.5%), MODERATE (1.5-3.0%), HIGH (3.0-5.0%), EXTREME (5%+) annualized
VOLATILITY_THRESHOLD_LOW | quant_hedge_rules.py | ALL | 0.015 (1.5%)
VOLATILITY_THRESHOLD_MODERATE | quant_hedge_rules.py | ALL | 0.030 (3.0%)
VOLATILITY_THRESHOLD_HIGH | quant_hedge_rules.py | ALL | 0.050 (5.0%)
VOLATILITY_THRESHOLD_EXTREME | quant_hedge_rules.py | ALL | 0.075 (7.5%)
VOLATILITY_SEVERITY_GREEN | quant_hedge_rules.py | ALL | MODERATE and LOW volatility = GREEN
VOLATILITY_SEVERITY_YELLOW | quant_hedge_rules.py | ALL | HIGH volatility = YELLOW
VOLATILITY_SEVERITY_RED | quant_hedge_rules.py | ALL | EXTREME volatility = RED

**CONDITION 2: TREND STRENGTH (Weight: 25%)**
TREND_STRENGTH_ANALYSIS | quant_hedge_rules.py | ALL | Evaluates momentum strength
TREND_ALIGNMENT | quant_hedge_rules.py | ALL | Checks trend direction vs position direction
TREND_SEVERITY_MAPPING | quant_hedge_rules.py | ALL | Weighted by trend alignment with position

**CONDITION 3: CORRELATION RISK (Weight: 20%)**
CORRELATION_CLASSIFICATION | quant_hedge_rules.py | ALL | LOW (independent), MODERATE (some), HIGH (strong), EXTREME (perfect)
CORRELATION_SEVERITY_GREEN | quant_hedge_rules.py | ALL | LOW correlation = GREEN
CORRELATION_SEVERITY_YELLOW | quant_hedge_rules.py | ALL | MODERATE correlation = YELLOW
CORRELATION_SEVERITY_RED | quant_hedge_rules.py | ALL | HIGH and EXTREME correlation = RED

**CONDITION 4: VOLUME ANALYSIS (Weight: 15%)**
VOLUME_CONFIRMATION | quant_hedge_rules.py | ALL | Validates trend with volume bars
VOLUME_SEVERITY | quant_hedge_rules.py | ALL | Severity based on volume profile vs trend

**CONDITION 5: MARGIN UTILIZATION (Weight: 10%)**
MARGIN_HEALTH_CHECK | quant_hedge_rules.py | ALL | Account health validation
MARGIN_THRESHOLD_GREEN | quant_hedge_rules.py | ALL | < 35% = GREEN
MARGIN_THRESHOLD_YELLOW | quant_hedge_rules.py | ALL | 35-50% = YELLOW
MARGIN_THRESHOLD_RED | quant_hedge_rules.py | ALL | > 50% = RED

**COMPOSITE ANALYSIS**
CONDITION_WEIGHTS | quant_hedge_rules.py | ALL | volatility: 0.30, trend: 0.25, correlation: 0.20, volume: 0.15, margin: 0.10
SEVERITY_SCORE | quant_hedge_rules.py | ALL | Composite 0-100 (higher = riskier)

**RISK LEVEL CLASSIFICATION**
RISK_SAFE | quant_hedge_rules.py | ALL | Severity 0-25 → Position size multiplier 1.0x
RISK_MODERATE | quant_hedge_rules.py | ALL | Severity 25-50 → Position size multiplier 0.75x
RISK_ELEVATED | quant_hedge_rules.py | ALL | Severity 50-75 → Position size multiplier 0.5x
RISK_CRITICAL | quant_hedge_rules.py | ALL | Severity 75-100 → Position size multiplier 0.25x

**HEDGE ACTION RECOMMENDATIONS**
HEDGE_FULL_LONG | quant_hedge_rules.py | ALL | Aggressive long: all GREEN conditions, high confidence (80%+)
HEDGE_MODERATE_LONG | quant_hedge_rules.py | ALL | Conservative long: mixed conditions, moderate confidence
HEDGE_REDUCE_EXPOSURE | quant_hedge_rules.py | ALL | Cut 50%: YELLOW severity signals detected
HEDGE_CLOSE_ALL | quant_hedge_rules.py | ALL | Exit all: CRITICAL risk level (severity 75+)
HEDGE_HEDGE_SHORT | quant_hedge_rules.py | ALL | Add short: high correlation or extreme volatility
HEDGE_PAUSE_TRADING | quant_hedge_rules.py | ALL | Stop entries: ELEVATED risk signals
HEDGE_WAIT_FOR_CLARITY | quant_hedge_rules.py | ALL | Hold: uncertain market regime

**POSITION SIZING MULTIPLIER**
POSITION_SIZING_CRYPTO | quant_hedge_rules.py | Crypto | 0.5x (low vol), 1.0x (normal), 1.5x (high vol)

---

### SECTION 5: CONFIGURATION FILES

**charter.yaml Configuration**
CONFIG_VERSION | config/charter.yaml | ALL | version: 1
MIN_RISK_REWARD | config/charter.yaml | ALL | risk.min_rr: 3.2
MIN_NOTIONAL_USD | config/charter.yaml | ALL | limits.min_notional_usd: 15000
MAX_CONCURRENT_POSITIONS | config/charter.yaml | ALL | limits.max_concurrent_positions: 3
ORDER_OCO_REQUIRED | config/charter.yaml | ALL | order_policy.oco_required: true

**gates.yaml Configuration**
CONFIG_VERSION | config/gates.yaml | ALL | version: 1
HIVE_ENABLED | config/gates.yaml | ALL | rick_hive.enabled: true
HIVE_QUORUM | config/gates.yaml | ALL | rick_hive.quorum: 3
HIVE_ADVISORS | config/gates.yaml | ALL | 4 advisors: news_filter, volatility_regime, trend_bias, mean_reversion
COMPLIANCE_OCO | config/gates.yaml | ALL | compliance.enforce_oco: true
OANDA_PRACTICE_ENABLED | config/gates.yaml | OANDA | connectors.oanda_practice.enabled: true, paper: true

---

### SECTION 6: BROKER-SPECIFIC IMPLEMENTATIONS

**OANDA Charter Bridge (bridges/oanda_charter_bridge.py)**
OANDA_PRICE_FETCHER | bridges/oanda_charter_bridge.py | OANDA | get_price(instrument) → (mid, bid, ask)
OANDA_ACCOUNT_QUERY | bridges/oanda_charter_bridge.py | OANDA | get_account_summary() → (NAV, margin_used, daily_pl)
OANDA_NOTIONAL_CALCULATOR | bridges/oanda_charter_bridge.py | OANDA | usd_notional_units(instrument, mid) → units = ceil(15000/mid)
OANDA_BRACKET_LOGIC | bridges/oanda_charter_bridge.py | OANDA | bracket_for_requirements(direction, entry, units, rr=3.2, min_profit=100)
OANDA_SL_CALCULATION | bridges/oanda_charter_bridge.py | OANDA | SL = entry ± (20 pips = 0.0020)
OANDA_TP_CALCULATION | bridges/oanda_charter_bridge.py | OANDA | TP = entry ± max(3.2*risk_dist, 100/units)
OANDA_RR_ENFORCEMENT | bridges/oanda_charter_bridge.py | OANDA | Enforces 3.2:1 ratio + $100 minimum profit
OANDA_ORDER_PLACEMENT | bridges/oanda_charter_bridge.py | OANDA | place_oanda_market(instrument, units, tp, sl) → FOK order with SL/TP
OANDA_API_VERSION | bridges/oanda_charter_bridge.py | OANDA | v20 REST API endpoints
OANDA_ORDER_TYPE | bridges/oanda_charter_bridge.py | OANDA | MARKET order with timeInForce=FOK (Fill-or-Kill)
OANDA_SUPPORT_PAIRS | bridges/oanda_charter_bridge.py | OANDA | USD-quoted pairs only (EUR_USD, GBP_USD, etc.)

**IBKR Charter Bridge**
IBKR_STATUS | [Referenced in rick_charter.py] | IBKR | Status: Referenced but not yet implemented
IBKR_PLANNED_SUPPORT | risk/rick_charter.py | IBKR | Will follow same pattern as OANDA bridge

**Crypto Platform Rules**
CRYPTO_CONSENSUS_REQUIREMENT | rick_charter.py, guardian_gates.py | Crypto | 90% hive consensus (vs 65% for FX)
CRYPTO_CONFLUENCE_FILTERS | rick_charter.py | Crypto | 4 of 5 filters must align
CRYPTO_TIME_GATING | rick_charter.py | Crypto | 8am-4pm ET only
CRYPTO_CALENDAR_GATING | rick_charter.py | Crypto | Weekdays only (Mon-Fri)
CRYPTO_VOLATILITY_SCALING | rick_charter.py | Crypto | Position sizing: 0.5x to 1.5x multiplier

---

### SECTION 7: FILE LOCATIONS & VERSIONS

**PRIMARY LOCATIONS (v2.0 - Immutable)**
RICK_CHARTER_V2 | /home/ing/RICK/RICK_LIVE_CLEAN/foundation/rick_charter.py | ALL | Version 2.0_IMMUTABLE
GUARDIAN_GATES | /home/ing/RICK/RICK_LIVE_CLEAN/hive/guardian_gates.py | ALL | 4-gate system
QUANT_HEDGE | /home/ing/RICK/RICK_LIVE_CLEAN/hive/quant_hedge_rules.py | ALL | 5-condition analysis
CHARTER_CONFIG | /home/ing/RICK/RICK_LIVE_CLEAN/config/charter.yaml | ALL | Charter configuration
GATES_CONFIG | /home/ing/RICK/RICK_LIVE_CLEAN/config/gates.yaml | ALL | Gates configuration

**INSTITUTIONAL UPGRADE (v3.0)**
RICK_CHARTER_V3 | /home/ing/RICK/RICK_LIVE_CLEAN/rick_clean_live/foundation/rick_charter.py | ALL | Version 3.0_INSTITUTIONAL_2025_10_29
V3_FEATURES | rick_clean_live/foundation/rick_charter.py | ALL | Enhanced: margin limits, portfolio constraints, crypto rules, volatility scaling

**CURRENT BUILD (new_RLC_rebuild)**
CURRENT_RICK_CHARTER | /home/ing/RICK/new_RLC_rebuild/foundation/rick_charter.py | ALL | Version 2.0_IMMUTABLE (current)
CURRENT_GUARDIAN_GATES | /home/ing/RICK/new_RLC_rebuild/hive/guardian_gates.py | ALL | Current gates system
CURRENT_QUANT_HEDGE | /home/ing/RICK/new_RLC_rebuild/hive/quant_hedge_rules.py | ALL | Current hedge analysis

**DEPLOYMENT TOOLS**
INSTITUTIONAL_DEPLOY | /home/ing/RICK/RICK_LIVE_CLEAN/deploy_institutional_charter.py | ALL | One-liner institutional charter deployment

**BROKER BRIDGES**
OANDA_BRIDGE | /home/ing/RICK/RICK_LIVE_CLEAN/bridges/oanda_charter_bridge.py | OANDA | Full OANDA implementation

---

### SECTION 8: VALIDATION METHODS

**Validation Functions (rick_charter.py)**
VALIDATE_PIN | rick_charter.py | ALL | validate_pin(pin: int) → bool [pin == 841921]
VALIDATE_TIMEFRAME | rick_charter.py | ALL | validate_timeframe(timeframe: str) → bool [M15/M30/H1 allowed; M1/M5 forbidden]
VALIDATE_HOLD_DURATION | rick_charter.py | ALL | validate_hold_duration(hours: float) → bool [0 < hours ≤ 6]
VALIDATE_RISK_REWARD | rick_charter.py | ALL | validate_risk_reward(ratio: float) → bool [ratio ≥ 3.2]
VALIDATE_NOTIONAL | rick_charter.py | ALL | validate_notional(notional_usd: float) → bool [notional ≥ 15000]
VALIDATE_DAILY_PNL | rick_charter.py | ALL | validate_daily_pnl(daily_pnl_pct: float) → bool [pnl > -5.0%]
VALIDATE_COMPREHENSIVE | rick_charter.py | ALL | validate(test_key: Optional[str]) → bool [runs all checks with assertions]

---

### SECTION 9: GATE RESULT DATACLASS

**GateResult Structure (guardian_gates.py)**
GATE_NAME | guardian_gates.py | ALL | String: "margin", "concurrent", "correlation", "crypto"
PASSED | guardian_gates.py | ALL | Boolean: True if gate passed, False if rejected
REASON | guardian_gates.py | ALL | Human-readable message explaining result
DETAILS | guardian_gates.py | ALL | Dict with numeric values: {"mu": 0.25, "max": 0.35} etc

---

### SECTION 10: QUANT HEDGE ANALYSIS OUTPUT

**QuantHedgeAnalysis Structure (quant_hedge_rules.py)**
TIMESTAMP | quant_hedge_rules.py | ALL | datetime.now(timezone.utc) - analysis time
REGIME | quant_hedge_rules.py | ALL | String: market regime classification
VOLATILITY_LEVEL | quant_hedge_rules.py | ALL | String: "low", "moderate", "high", "extreme"
VOLATILITY_VALUE | quant_hedge_rules.py | ALL | Float: actual volatility percentage
CONDITIONS | quant_hedge_rules.py | ALL | List[HedgeCondition]: 5 individual conditions
SEVERITY_SCORE | quant_hedge_rules.py | ALL | Float 0-100: composite weighted severity
PRIMARY_ACTION | quant_hedge_rules.py | ALL | String: recommended main action
SECONDARY_ACTIONS | quant_hedge_rules.py | ALL | List[str]: additional considerations
POSITION_SIZE_MULTIPLIER | quant_hedge_rules.py | ALL | Float 0.25-1.5x: position sizing adjustment
RISK_LEVEL | quant_hedge_rules.py | ALL | String: "safe", "moderate", "elevated", "critical"
CONFIDENCE | quant_hedge_rules.py | ALL | Float 0-1.0: confidence in recommendation
SUMMARY | quant_hedge_rules.py | ALL | String: executive summary
DETAILED_ANALYSIS | quant_hedge_rules.py | ALL | Dict: full breakdown by condition

---

## CONSOLIDATION SUMMARY

**Total Rules:** 20+  
**Charter Versions:** 2 (v2.0 Immutable, v3.0 Institutional)  
**Guardian Gates:** 4 (ALL must pass)  
**Hedge Conditions:** 5 (weighted 30/25/20/15/10)  
**Hedge Actions:** 7 (positioning recommendations)  
**Platforms:** 3 (OANDA fully implemented, IBKR referenced, Crypto specific)  
**Configuration Files:** 2 (charter.yaml, gates.yaml)  
**Python Modules:** 3 core (rick_charter, guardian_gates, quant_hedge_rules)  
**Broker Bridges:** 1 implemented (OANDA)  
**PIN Security:** 841921 (hardcoded across all modules)  

---

**END OF MASTER MATRIX**  
Generated: 2025-11-14  
Status: COMPLETE - All files consolidated and documented
