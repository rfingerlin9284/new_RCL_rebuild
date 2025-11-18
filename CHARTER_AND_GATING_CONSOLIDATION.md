# RICK Charter and Gating Logic Consolidation
**Generated: 2025-11-14**  
**PIN: 841921 | Audit Complete**

## EXECUTIVE SUMMARY
This document consolidates all charter enforcement rules and guardian gating logic discovered across the RICK project. The analysis identifies:
- **3 core charter modules** (2 versions: immutable and institutional)
- **4 guardian gates** (pre-trade validation system)
- **5 quant hedge conditions** (multi-condition analysis)
- **2 configuration formats** (YAML + Python constants)
- **1 broker-specific bridge** (OANDA implementation)

---

## PART 1: CHARTER ENFORCEMENT RULES

### 1.1 RICK CHARTER (Foundation Module)

**Files:**
- RICK_LIVE_CLEAN/foundation/rick_charter.py
- new_RLC_rebuild/foundation/rick_charter.py
- RICK_LIVE_CLEAN/rick_clean_live/foundation/rick_charter.py

**Versions Found:**
- V2.0_IMMUTABLE (original)
- V3.0_INSTITUTIONAL_2025_10_29 (institutional upgrade)

#### Core Constants - UNIVERSAL (All Versions)

| RULE | VALUE | LOCATION | PLATFORMS | VALIDATION |
|------|-------|----------|-----------|------------|
| PIN_AUTHENTICATION | 841921 | rick_charter.py | ALL | validate_pin() |
| MIN_NOTIONAL_USD | 15000 | rick_charter.py | ALL | validate_notional() |
| MIN_RISK_REWARD_RATIO | 3.2:1 | rick_charter.py | ALL | validate_risk_reward() |
| MIN_EXPECTED_PNL_USD | 100.0 | rick_charter.py | ALL | validate_daily_pnl() |
| MAX_HOLD_DURATION_HOURS | 6 | rick_charter.py | ALL | validate_hold_duration() |
| MAX_CONCURRENT_POSITIONS | 3 | rick_charter.py | ALL | gates.yaml |
| MAX_DAILY_TRADES | 12 | rick_charter.py | ALL | N/A |
| DAILY_LOSS_BREAKER_PCT | -5.0% | rick_charter.py | ALL | Hard halt |
| MAX_PLACEMENT_LATENCY_MS | 300 | rick_charter.py | ALL | Execution constraint |

#### Timeframe Enforcement

**Allowed Timeframes:**
- M15 (15-minute)
- M30 (30-minute)
- H1 (1-hour)

**Rejected Timeframes:**
- M1 (1-minute) - EXPLICITLY FORBIDDEN
- M5 (5-minute) - EXPLICITLY FORBIDDEN

**Validation Logic:** `validate_timeframe(timeframe: str) -> bool`
- Returns TRUE only for M15, M30, H1
- Returns FALSE for any M1 or M5
- Defaults to FALSE for unknown timeframes

#### Spread & Slippage Gates

| CONSTRAINT | VALUE | PLATFORM | VALIDATION |
|------------|-------|----------|------------|
| FX_MAX_SPREAD_ATR_MULTIPLIER | 0.15x ATR14 | OANDA/IBKR | Spread check |
| CRYPTO_MAX_SPREAD_ATR_MULTIPLIER | 0.10x ATR14 | Crypto | Tighter spread |

#### Stop Loss Requirements

| PARAMETER | VALUE | PLATFORM | USAGE |
|-----------|-------|----------|-------|
| FX_STOP_LOSS_ATR_MULTIPLIER | 1.2x ATR | OANDA/IBKR | SL placement |
| CRYPTO_STOP_LOSS_ATR_MULTIPLIER | 1.5x ATR | Crypto | Larger buffer |

#### Institutional Charter Extensions (V3.0)

**File:** rick_clean_live/foundation/rick_charter.py

| RULE | VALUE | ADDED_VERSION | PURPOSE |
|------|-------|---|---------|
| MAX_MARGIN_UTILIZATION_PCT | 0.35 (35%) | V3.0 | Account protection |
| MAX_PORTFOLIO_EXPOSURE_PCT | 0.80 (80%) | V3.0 | Concentration limit |
| CORRELATION_CAP_PCT | 0.70 (70%) | V3.0 | Diversification gate |
| MIN_MARGIN_USD | 500 | V3.0 | Per-trade minimum |
| CRYPTO_HIVE_CONSENSUS_MIN | 0.90 (90%) | V3.0 | Hive voting threshold |
| CRYPTO_CONFLUENCE_MIN | 4 (of 5) | V3.0 | Filter convergence |
| CRYPTO_TRADING_START_HOUR | 8 (8am ET) | V3.0 | Time gate |
| CRYPTO_TRADING_END_HOUR | 16 (4pm ET) | V3.0 | Time gate |
| CRYPTO_TRADING_WEEKDAYS_ONLY | TRUE | V3.0 | Calendar gate |
| HIVE_CONSENSUS_MIN_FX | 0.65 (65%) | V3.0 | FX voting threshold |
| ML_WEIGHTED_TALLY_MIN | 0.75 (75%) | V3.0 | ML confidence floor |
| SMART_LOGIC_FILTERS_REQUIRED | 5 (ALL) | V3.0 | Filter convergence |

#### Crypto Volatility Scaling (V3.0)

| REGIME | POSITION_SIZE_MULTIPLIER | APPLICATION |
|--------|--------------------------|--------------|
| LOW volatility | 0.5x | Conservative sizing |
| MID volatility | 1.0x | Normal sizing |
| HIGH volatility | 1.5x | Aggressive sizing |

---

## PART 2: GUARDIAN GATE SYSTEM

**File:** 
- RICK_LIVE_CLEAN/hive/guardian_gates.py
- new_RLC_rebuild/hive/guardian_gates.py

**Class:** `GuardianGates(pin: int = 841921)`

### Gate Architecture
- **Logic:** ALL gates must PASS (AND logic) before order placement
- **PIN Verification:** Required at initialization
- **Return Format:** `(all_passed: bool, results: List[GateResult])`

### The Four Guardian Gates

#### GATE 1: MARGIN UTILIZATION GATE

```
gate_name: "margin"
validation: margin_used / NAV ≤ 35%
rejection_reason: "Margin utilization {mu:.1%} exceeds Charter max {max_mu:.1%}"
parameters:
  - mu: current margin utilization ratio
  - max: 0.35 (35% threshold)
```

**Purpose:** Prevent over-leverage and account ruin  
**Source:** RickCharter.MAX_MARGIN_UTILIZATION_PCT = 0.35

---

#### GATE 2: CONCURRENT POSITIONS GATE

```
gate_name: "concurrent"
validation: open_positions < 3
rejection_reason: "Open positions {open_count} >= Charter max {max_concurrent}"
parameters:
  - open: current open position count
  - max: 3 (hard limit)
```

**Purpose:** Limit concentration and avoid correlation drag  
**Source:** RickCharter.MAX_CONCURRENT_POSITIONS = 3

---

#### GATE 3: CORRELATION EXPOSURE GATE (USD Bucket)

```
gate_name: "correlation"
validation: same_side_USD_exposure = 0
rejection_reason: "Same-side USD exposure detected: {exposure} units"
parameters:
  - exposure: total correlated units
  - side: BUY/SELL direction
```

**Logic:**
1. Scans open positions for USD pairs: [USD, USDT, USDC, BUSD, USDP, TUSD]
2. Checks incoming signal symbol against USD pairs
3. If BOTH involve USD AND same direction (BUY/BUY or SELL/SELL):
   - BLOCKS the order (correlation protection)
4. Otherwise: PASSES

**Purpose:** Prevent basket correlation disaster (all same direction)

---

#### GATE 4: CRYPTO-SPECIFIC GATE (Conditional)

```
gate_name: "crypto"
validation: Only runs if signal.symbol is crypto
checks:
  - hive_consensus ≥ 90% (CRYPTO_AI_HIVE_VOTE_CONSENSUS)
  - Additional time-window and regime checks
rejection_reason: Various (hive vote, time window, regime)
parameters:
  - hive_consensus: voting agreement threshold
```

**Purpose:** Extra protections for volatile crypto assets  
**Trigger:** `_is_crypto(symbol)` - detects BTC, ETH, etc.

---

### GateResult Dataclass

```python
@dataclass
class GateResult:
    gate_name: str          # "margin", "concurrent", "correlation", "crypto"
    passed: bool            # True/False
    reason: str             # Human-readable message
    details: Dict = None    # {"mu": 0.25, "max": 0.35} etc
```

---

## PART 3: QUANT HEDGE RULES SYSTEM

**File:**
- RICK_LIVE_CLEAN/hive/quant_hedge_rules.py
- new_RLC_rebuild/hive/quant_hedge_rules.py

**Class:** `QuantHedgeRules(pin: int = 841921)`

### Architecture
- **PIN Verification:** Required at initialization
- **Regime Detector:** Integrated StochasticRegimeDetector
- **Multi-condition Analysis:** 5 weighted conditions
- **Output:** `QuantHedgeAnalysis` dataclass

### Method: `analyze_market_conditions()`

```python
def analyze_market_conditions(
    prices: np.ndarray,           # OHLC close prices
    volume: np.ndarray,            # Trading volume
    account_nav: float,            # Net asset value
    margin_used: float,            # Current margin $
    open_positions: int,           # Number of open positions
    correlation_matrix: Dict = None,  # Symbol correlations
    lookback_periods: int = 50     # Historical lookback
) -> QuantHedgeAnalysis
```

### The Five Hedge Conditions

#### CONDITION 1: VOLATILITY ANALYSIS (30% weight)

**Thresholds:**
- LOW: 0-1.5% annualized
- MODERATE: 1.5-3.0% annualized
- HIGH: 3.0-5.0% annualized
- EXTREME: 5%+ annualized

**Config Thresholds:**
```python
self.volatility_thresholds = {
    'low': 0.015,           # 1.5%
    'moderate': 0.030,      # 3.0%
    'high': 0.050,          # 5.0%
    'extreme': 0.075        # 7.5%
}
```

**Severity Mapping:**
- EXTREME vol → RED severity
- HIGH vol → YELLOW severity
- MODERATE/LOW → GREEN severity

---

#### CONDITION 2: TREND STRENGTH (25% weight)

**Purpose:** Evaluate momentum and trend quality  
**Input:** Regime detector output  
**Severity:** Based on trend alignment with position

---

#### CONDITION 3: CORRELATION RISK (20% weight)

**Levels:**
- LOW: Different assets move independently
- MODERATE: Some correlation detected
- HIGH: Strong correlation (diversification risk)
- EXTREME: Perfect/near-perfect correlation

**Severity Mapping:**
- HIGH/EXTREME correlation → RED
- MODERATE → YELLOW
- LOW → GREEN

---

#### CONDITION 4: VOLUME ANALYSIS (15% weight)

**Purpose:** Confirm trend with volume bars  
**Severity:** Volume-weighted confirmation

---

#### CONDITION 5: MARGIN UTILIZATION (10% weight)

**Purpose:** Account health check  
**Threshold:** Compare against Charter MAX_MARGIN_UTILIZATION_PCT = 35%

---

### Hedge Actions (Recommendations)

| ACTION | DESCRIPTION | TRIGGER |
|--------|-------------|---------|
| FULL_LONG | Aggressive long positions | All conditions green, high confidence |
| MODERATE_LONG | Conservative long positions | Mixed conditions, moderate confidence |
| REDUCE_EXPOSURE | Cut position size by 50% | Yellow severity signals |
| CLOSE_ALL | Exit all positions immediately | Critical risk level |
| HEDGE_SHORT | Add offsetting short hedge | High correlation/volatility |
| PAUSE_TRADING | Stop new entries temporarily | Elevated risk signals |
| WAIT_FOR_CLARITY | Hold and monitor | Uncertain market regime |

### Risk Level Classification

**Severity Score Range:** 0-100 (higher = more risky)

| RISK_LEVEL | SEVERITY_SCORE | ACTION | CONFIDENCE |
|------------|---|--------|----------|
| SAFE | 0-25 | FULL_LONG | High |
| MODERATE | 25-50 | MODERATE_LONG | Medium |
| ELEVATED | 50-75 | REDUCE_EXPOSURE | Medium-Low |
| CRITICAL | 75-100 | CLOSE_ALL | Low |

### QuantHedgeAnalysis Output

```python
@dataclass
class QuantHedgeAnalysis:
    timestamp: datetime                  # Analysis time (UTC)
    regime: str                          # Market regime (uptrend, downtrend, choppy)
    volatility_level: str                # Classification (low/moderate/high/extreme)
    volatility_value: float              # Actual volatility value
    
    conditions: List[HedgeCondition]     # 5 individual conditions
    
    severity_score: float                # 0-100, weighted severity
    primary_action: str                  # Recommended main action
    secondary_actions: List[str]         # Additional considerations
    
    position_size_multiplier: float      # 0.25 to 1.5x normal
    risk_level: str                      # safe/moderate/elevated/critical
    confidence: float                    # 0-1.0 confidence in recommendation
    
    summary: str                         # Executive summary
    detailed_analysis: Dict              # Full breakdown
```

---

## PART 4: CONFIGURATION FILES

### 4.1 charter.yaml

**File:** RICK_LIVE_CLEAN/config/charter.yaml

```yaml
version: 1
risk: 
  min_rr: 3.2                           # Minimum risk-reward ratio
limits: 
  min_notional_usd: 15000               # Minimum trade size ($15k)
  max_concurrent_positions: 3           # Maximum 3 open positions
order_policy: 
  oco_required: true                    # One-Cancels-Other mandatory
```

**Configuration Source:** This is the authoritative config reference for:
- Risk/reward floor (3.2:1 minimum)
- Position sizing minimum ($15,000)
- Concurrent position limits (3)
- Order structure (OCO required)

---

### 4.2 gates.yaml

**File:** RICK_LIVE_CLEAN/config/gates.yaml

```yaml
version: 1
rick_hive: 
  enabled: true
  quorum: 3                             # 3-advisor consensus
  advisors:                             # Multi-condition analysis
    - news_filter
    - volatility_regime
    - trend_bias
    - mean_reversion
compliance: 
  enforce_oco: true                     # Enforce One-Cancels-Other
connectors: 
  oanda_practice: 
    enabled: true
    paper: true                         # Paper trading mode
```

**Components:**
- **RICK Hive:** 3-quorum consensus from 4 advisors
- **Compliance:** OCO enforcement
- **Connectors:** OANDA practice environment enabled

---

## PART 5: BROKER-SPECIFIC IMPLEMENTATIONS

### 5.1 OANDA Charter Bridge

**File:** RICK_LIVE_CLEAN/bridges/oanda_charter_bridge.py

**Purpose:** Institutional-grade OANDA integration with Charter compliance

**Key Functions:**

#### 1. `get_price(instrument)`
- Fetches bid/ask from OANDA Pricing API (v20)
- Returns: (mid, bid, ask)

#### 2. `get_account_summary()`
- Returns: (NAV, margin_used, daily_pl)
- Used for Gate 1 (margin utilization check)

#### 3. `usd_notional_units(instrument, mid)`
- Calculates units for $15,000 notional minimum
- Formula: `units = ceil(15000.0 / mid)`
- Only supports USD-quoted instruments (e.g., EUR_USD)

#### 4. `bracket_for_requirements(direction, entry, units, rr=3.2, min_profit_usd=100.0)`
- Calculates SL and TP for RR compliance
- Enforces minimum:
  - Risk-reward ratio: 3.2:1
  - Minimum profit: $100 USD
- Returns: (stop_loss, take_profit)

**Example Calculation:**
```
direction = "BUY"
entry = 1.0850
units = 15000
rr = 3.2
min_profit = $100

risk_dist = 20 pips = 0.0020
profit_dist = MAX(3.2 * 0.0020, 100/15000) = MAX(0.0064, 0.0067) = 0.0067

SL = 1.0850 - 0.0020 = 1.0830
TP = 1.0850 + 0.0067 = 1.0917
```

#### 5. `place_oanda_market(instrument, units, tp, sl)`
- Places market order with attached SL/TP
- Uses OANDA v3 API endpoints
- Order structure:
  - Type: MARKET
  - TimeInForce: FOK (Fill-or-Kill)
  - takeProfitOnFill: TP price
  - stopLossOnFill: SL price

---

## PART 6: CONSOLIDATION MATRIX

### Rule Coverage Across Files

| RULE | rick_charter.py | guardian_gates.py | quant_hedge_rules.py | charter.yaml | gates.yaml | oanda_bridge.py |
|------|---|---|---|---|---|---|
| MIN_NOTIONAL_USD (15k) | ✅ | - | - | ✅ | - | ✅ |
| MIN_RISK_REWARD (3.2:1) | ✅ | - | - | ✅ | - | ✅ |
| MAX_CONCURRENT_POS (3) | ✅ | ✅ | - | ✅ | - | - |
| MAX_MARGIN_UTIL (35%) | ✅ | ✅ | ✅ | - | - | - |
| MAX_HOLD_DURATION (6h) | ✅ | - | - | - | - | - |
| DAILY_LOSS_BREAKER (-5%) | ✅ | - | - | - | - | - |
| TIMEFRAME_ALLOWED (M15/M30/H1) | ✅ | - | - | - | - | - |
| SPREAD_GATES (ATR multiplier) | ✅ | - | - | - | - | - |
| STOP_LOSS_REQUIREMENT (ATR) | ✅ | - | - | - | - | - |
| CRYPTO_HIVE_CONSENSUS (90%) | ✅ | ✅ | - | - | ✅ | - |
| CORRELATION_EXPOSURE_GUARD | - | ✅ | ✅ | - | - | - |
| VOLATILITY_ANALYSIS | - | - | ✅ | - | - | - |
| HEDGE_ACTIONS | - | - | ✅ | - | - | - |
| REGIME_DETECTION | - | - | ✅ | - | - | - |
| OCO_REQUIREMENT | - | - | - | ✅ | ✅ | - |

---

## PART 7: CONSOLIDATION OPPORTUNITIES

### 7.1 Redundancy Identified
1. **PIN Verification:** Appears in all Python modules (rick_charter, guardian_gates, quant_hedge_rules)
   - **Consolidation:** Create `pep8_pin_verifier.py` for DRY

2. **Charter Constants:** Duplicated in guardian_gates.py as fallback class
   - **Current:** `try/except` import pattern
   - **Improvement:** Mandatory direct import with clear error

3. **Configuration Format Split:** YAML + Python constants
   - **Current:** charter.yaml has constants, rick_charter.py has constants
   - **Improvement:** Single source of truth (favor YAML with Python overlay)

### 7.2 Platform Variations

#### OANDA-Specific Rules
- Supports USD-quoted pairs only (for $15k notional calculation)
- Uses OANDA v20 API for pricing
- Supports FOK (Fill-or-Kill) execution

#### IBKR-Specific (Referenced but not detailed)
- Would require similar bridge implementation
- Likely different API structure

#### Crypto-Specific Rules
- Higher consensus threshold: 90% vs 65% FX
- Time gating: 8am-4pm ET, weekdays only
- Volatility scaling: 0.5x - 1.5x multiplier
- Confluence minimum: 4 of 5 filters

### 7.3 Recommendation Priority

**HIGH Priority (Do First):**
1. Consolidate all charter constants into single YAML master config
2. Create unified PIN verifier module
3. Document API-specific variations (OANDA, IBKR, Crypto)
4. Add integration tests for all 4 gates

**MEDIUM Priority (Next):**
1. Parameterize hedge condition weights (currently hardcoded 30/25/20/15/10)
2. Create broker config inheritance system
3. Add monitoring/audit logging for each gate pass/fail

**LOW Priority (Optional):**
1. Refactor timeframe validation into separate enum module
2. Create position sizing calculator as utility
3. Add CLI tools for testing charter rules in isolation

---

## PART 8: STRUCTURED RULE INVENTORY

### Master Rule List (Sorted by Impact)

```
RULE_NAME | VALUE | TYPE | LOCATION | PLATFORMS | ENFORCEMENT_POINT
───────────────────────────────────────────────────────────────────────────
MIN_NOTIONAL_USD | 15000 | Floor | rick_charter.py | ALL | Pre-signal validation
MIN_RISK_REWARD_RATIO | 3.2:1 | Floor | rick_charter.py | ALL | Pre-signal validation
MAX_CONCURRENT_POSITIONS | 3 | Ceiling | rick_charter.py | ALL | Gate 2 (guardian_gates.py)
MAX_MARGIN_UTILIZATION_PCT | 0.35 | Ceiling | rick_charter.py | ALL | Gate 1 (guardian_gates.py)
MAX_HOLD_DURATION_HOURS | 6 | Ceiling | rick_charter.py | ALL | Position management
DAILY_LOSS_BREAKER_PCT | -5.0% | Hard Stop | rick_charter.py | ALL | Daily reconciliation
ALLOWED_TIMEFRAMES | M15,M30,H1 | Whitelist | rick_charter.py | ALL | Signal validation
REJECTED_TIMEFRAMES | M1,M5 | Blacklist | rick_charter.py | ALL | Signal validation
FX_MAX_SPREAD_ATR_MULTIPLIER | 0.15x | Gate | rick_charter.py | OANDA/IBKR | Order placement
CRYPTO_MAX_SPREAD_ATR_MULTIPLIER | 0.10x | Gate | rick_charter.py | Crypto | Order placement
FX_STOP_LOSS_ATR_MULTIPLIER | 1.2x | Requirement | rick_charter.py | OANDA/IBKR | TP/SL calculation
CRYPTO_STOP_LOSS_ATR_MULTIPLIER | 1.5x | Requirement | rick_charter.py | Crypto | TP/SL calculation
MIN_EXPECTED_PNL_USD | 100.0 | Floor | rick_charter.py | ALL | TP/SL calculation
CRYPTO_HIVE_CONSENSUS_MIN | 0.90 | Floor | rick_charter.py | Crypto | Gate 4 (guardian_gates.py)
HIVE_CONSENSUS_MIN_FX | 0.65 | Floor | rick_charter.py | FX | Hive voting
CORRELATION_EXPOSURE_GUARD | USD pairs | Logic | guardian_gates.py | ALL | Gate 3 (guardian_gates.py)
MARGIN_UTILIZATION_GATE | 35% | Threshold | guardian_gates.py | ALL | Gate 1
CONCURRENT_POSITIONS_GATE | 3 | Threshold | guardian_gates.py | ALL | Gate 2
VOLATILITY_ANALYSIS | 5 levels | Analysis | quant_hedge_rules.py | ALL | Hedge recommendations
HEDGE_ACTION_RECOMMENDATION | 7 actions | Decision | quant_hedge_rules.py | ALL | Position management
POSITION_SIZE_MULTIPLIER | 0.25-1.5x | Scaling | quant_hedge_rules.py | Crypto | Signal sizing
RISK_LEVEL_CLASSIFICATION | 4 levels | Analysis | quant_hedge_rules.py | ALL | Position management
```

---

## PART 9: VALIDATION CHECKLIST

**Before Deployment, Verify:**

- [ ] PIN 841921 is hardcoded in charter module
- [ ] All 4 gates execute in AND logic (all must pass)
- [ ] Margin utilization check: margin_used / NAV ≤ 35%
- [ ] Concurrent positions check: open_count < 3
- [ ] Correlation guard: no same-side USD bucket exposure
- [ ] Crypto gate: hive_consensus ≥ 90% (if crypto)
- [ ] Min notional: $15,000 per trade
- [ ] Min RR ratio: 3.2:1 enforced
- [ ] Min profit: $100 USD at TP
- [ ] Max hold: 6 hours only
- [ ] Allowed TF: M15, M30, H1 only
- [ ] Daily loss halt: -5% NAV breaker
- [ ] Max placement latency: 300ms
- [ ] OANDA: USD-quoted pairs only
- [ ] Stop loss: 1.2x ATR (FX), 1.5x ATR (Crypto)
- [ ] Spread gate: 0.15x ATR (FX), 0.10x ATR (Crypto)
- [ ] OCO required: All orders
- [ ] Hive quorum: 3 of 3 advisors

---

## PART 10: FILES ANALYZED

### Primary Source Files
1. ✅ `/home/ing/RICK/RICK_LIVE_CLEAN/foundation/rick_charter.py` (179 lines)
2. ✅ `/home/ing/RICK/RICK_LIVE_CLEAN/hive/guardian_gates.py` (226 lines)
3. ✅ `/home/ing/RICK/RICK_LIVE_CLEAN/hive/quant_hedge_rules.py` (621 lines)
4. ✅ `/home/ing/RICK/RICK_LIVE_CLEAN/deploy_institutional_charter.py` (150 lines)
5. ✅ `/home/ing/RICK/RICK_LIVE_CLEAN/config/charter.yaml` (5 lines)
6. ✅ `/home/ing/RICK/RICK_LIVE_CLEAN/config/gates.yaml` (10 lines)
7. ✅ `/home/ing/RICK/RICK_LIVE_CLEAN/bridges/oanda_charter_bridge.py` (100+ lines)
8. ✅ `/home/ing/RICK/RICK_LIVE_CLEAN/rick_clean_live/foundation/rick_charter.py` (institutional version)
9. ✅ `/home/ing/RICK/new_RLC_rebuild/foundation/rick_charter.py` (current version)
10. ✅ `/home/ing/RICK/new_RLC_rebuild/hive/guardian_gates.py` (current version)
11. ✅ `/home/ing/RICK/new_RLC_rebuild/hive/quant_hedge_rules.py` (current version)

### Notes
- **Versions:** 2 major versions found (V2.0 Immutable, V3.0 Institutional)
- **Broker Support:** OANDA fully implemented, IBKR referenced, Crypto specific rules present
- **Current Workspace:** new_RLC_rebuild contains V2.0 (immutable), rick_clean_live contains V3.0 (institutional)

---

## END OF CONSOLIDATION REPORT

**Document Status:** COMPLETE  
**Audit Verification:** PIN 841921 ✅  
**Rule Count:** 20+ rules consolidated  
**Platforms Covered:** FX (OANDA, IBKR), Crypto, Multi-broker  
**Gating Layers:** 4 guardian gates + 5 quant hedge conditions = 9-layer protection
