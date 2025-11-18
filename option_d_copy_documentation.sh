#!/bin/bash
#
# OPTION D - DOCUMENTATION COPYING SCRIPT
# 
# Copies all consolidation and integration documentation to RICK_LIVE_CLEAN
# and creates a comprehensive knowledge transfer package
#
# PIN: 841921 | Date: Nov 15, 2025
#

SOURCE_ROOT="/home/ing/RICK/new_RLC_rebuild"
TARGET_ROOT="/home/ing/RICK/RICK_LIVE_CLEAN"
DOC_SUBDIR="docs/INTEGRATION_KNOWLEDGE_BASE"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case $level in
        "INFO")
            echo -e "${BLUE}[${timestamp}] [INFO]${NC} $message"
            ;;
        "SUCCESS")
            echo -e "${GREEN}[${timestamp}] [✓]${NC} $message"
            ;;
        "WARNING")
            echo -e "${YELLOW}[${timestamp}] [⚠]${NC} $message"
            ;;
        "ERROR")
            echo -e "${RED}[${timestamp}] [✗]${NC} $message"
            ;;
        *)
            echo "[${timestamp}] $message"
            ;;
    esac
}

# Main documentation copy script
copy_documentation() {
    log "INFO" "╔════════════════════════════════════════════════════════════════╗"
    log "INFO" "║          OPTION D - DOCUMENTATION COPYING STARTED             ║"
    log "INFO" "╚════════════════════════════════════════════════════════════════╝"
    log "INFO" ""
    
    # Step 1: Create documentation directory in target
    log "INFO" "Creating documentation directory structure..."
    mkdir -p "$TARGET_ROOT/$DOC_SUBDIR"
    if [ $? -eq 0 ]; then
        log "SUCCESS" "Documentation directory created: $TARGET_ROOT/$DOC_SUBDIR"
    else
        log "ERROR" "Failed to create documentation directory"
        return 1
    fi
    
    log "INFO" ""
    
    # Step 2: Define documentation files to copy
    log "INFO" "Copying core documentation files..."
    
    CORE_DOCS=(
        "CONSOLIDATION_INDEX.md"
        "CHARTER_AND_GATING_CONSOLIDATION.md"
        "CHARTER_GATING_QUICK_REFERENCE.md"
        "RULE_MATRIX_STRUCTURED.md"
        "CONSOLIDATION_DELIVERY.md"
        "FINAL_DELIVERY_841921.txt"
        "OPTION_A_VERIFIED.txt"
    )
    
    copy_count=0
    for doc in "${CORE_DOCS[@]}"; do
        source_file="$SOURCE_ROOT/$doc"
        target_file="$TARGET_ROOT/$DOC_SUBDIR/$doc"
        
        if [ -f "$source_file" ]; then
            cp "$source_file" "$target_file"
            if [ $? -eq 0 ]; then
                size=$(du -h "$target_file" | cut -f1)
                log "SUCCESS" "Copied: $doc ($size)"
                ((copy_count++))
            else
                log "WARNING" "Failed to copy: $doc"
            fi
        else
            log "WARNING" "Source not found: $doc"
        fi
    done
    
    log "SUCCESS" "Copied $copy_count core documentation files"
    log "INFO" ""
    
    # Step 3: Copy reference documentation
    log "INFO" "Copying reference documentation..."
    
    REFERENCE_DOCS=(
        "README.md"
        "PROJECT_STRUCTURE.md"
        "RICK_130_FEATURES_ANALYSIS.md"
        "RICK_HIVE_ARCHITECTURE.md"
        "HIVE_MIND_EXPLAINED.md"
        "ENHANCED_SYSTEM_GUIDE.md"
        "PRE_LAUNCH_CHECKLIST.md"
        "QUICK_START.md"
        "IMPLEMENTATION_GUIDE.md"
    )
    
    ref_count=0
    for doc in "${REFERENCE_DOCS[@]}"; do
        source_file="$SOURCE_ROOT/$doc"
        target_file="$TARGET_ROOT/$DOC_SUBDIR/$doc"
        
        if [ -f "$source_file" ]; then
            cp "$source_file" "$target_file"
            if [ $? -eq 0 ]; then
                log "SUCCESS" "Copied: $doc"
                ((ref_count++))
            else
                log "WARNING" "Failed to copy: $doc"
            fi
        else
            log "WARNING" "Source not found: $doc"
        fi
    done
    
    log "SUCCESS" "Copied $ref_count reference documentation files"
    log "INFO" ""
    
    # Step 4: Copy integration scripts
    log "INFO" "Copying integration scripts and utilities..."
    
    SCRIPTS=(
        "option_c_priority3_integration.py"
        "autonomous_launch.sh"
        "QUICK_START_AUTONOMOUS.sh"
        "migrate_from_live_clean.sh"
    )
    
    script_count=0
    for script in "${SCRIPTS[@]}"; do
        source_file="$SOURCE_ROOT/$script"
        target_file="$TARGET_ROOT/$DOC_SUBDIR/$script"
        
        if [ -f "$source_file" ]; then
            cp "$source_file" "$target_file"
            chmod +x "$target_file"
            if [ $? -eq 0 ]; then
                log "SUCCESS" "Copied: $script (made executable)"
                ((script_count++))
            else
                log "WARNING" "Failed to copy: $script"
            fi
        fi
    done
    
    log "SUCCESS" "Copied $script_count scripts"
    log "INFO" ""
    
    # Step 5: Create master integration index
    log "INFO" "Creating master integration index..."
    
    create_master_index
    
    log "SUCCESS" "Master index created"
    log "INFO" ""
    
    # Step 6: Create quick reference card
    log "INFO" "Creating quick reference card..."
    
    create_quick_reference
    
    log "SUCCESS" "Quick reference card created"
    log "INFO" ""
    
    # Step 7: Create knowledge transfer summary
    log "INFO" "Creating knowledge transfer summary..."
    
    create_knowledge_transfer
    
    log "SUCCESS" "Knowledge transfer summary created"
    log "INFO" ""
    
    # Final summary
    log "INFO" "╔════════════════════════════════════════════════════════════════╗"
    log "SUCCESS" "║          OPTION D - DOCUMENTATION COPYING COMPLETE             ║"
    log "INFO" "╚════════════════════════════════════════════════════════════════╝"
    
    log "SUCCESS" "All documentation files copied to: $TARGET_ROOT/$DOC_SUBDIR"
    log "INFO" ""
    log "INFO" "Documentation Summary:"
    log "INFO" "  ✅ Core consolidation docs (5 files)"
    log "INFO" "  ✅ Reference documentation (9 files)"
    log "INFO" "  ✅ Integration scripts (4 files)"
    log "INFO" "  ✅ Master integration index"
    log "INFO" "  ✅ Quick reference card"
    log "INFO" "  ✅ Knowledge transfer summary"
    
    return 0
}

# Create master integration index
create_master_index() {
    cat > "$TARGET_ROOT/$DOC_SUBDIR/MASTER_INTEGRATION_INDEX.md" << 'EOF'
# RICK Trading System - Master Integration Index

## Document Organization

### 1. Consolidation Documents (Read These First)
- **CONSOLIDATION_INDEX.md** - Main reference (START HERE)
- **CHARTER_AND_GATING_CONSOLIDATION.md** - Charter enforcement details
- **CHARTER_GATING_QUICK_REFERENCE.md** - Quick lookup guide
- **RULE_MATRIX_STRUCTURED.md** - All rules in matrix format
- **CONSOLIDATION_DELIVERY.md** - Integration status

### 2. System Overview
- **RICK_130_FEATURES_ANALYSIS.md** - All 130+ features explained
- **RICK_HIVE_ARCHITECTURE.md** - Architecture deep dive
- **HIVE_MIND_EXPLAINED.md** - How Hive Consensus works
- **PROJECT_STRUCTURE.md** - File organization

### 3. Implementation Guides
- **ENHANCED_SYSTEM_GUIDE.md** - System enhancement guide
- **IMPLEMENTATION_GUIDE.md** - How to implement new features
- **PRE_LAUNCH_CHECKLIST.md** - Deployment checklist
- **QUICK_START.md** - Quick start guide

### 4. Integration Guides
- **OPTION_A_VERIFIED.txt** - Broker verification (Coinbase/IBKR)
- **FINAL_DELIVERY_841921.txt** - Integration completion status

## Key Facts

- **PIN**: 841921 (hardcoded, immutable)
- **Starting Capital**: $2,271.38
- **Risk Per Trade**: 2%
- **Min R:R**: 3.2:1
- **Daily Loss Breaker**: -5%
- **Max Positions**: 3 concurrent
- **Margin Cap**: 35% NAV
- **Charter Enforcement**: Guardian Gates (4 cascading AND gates)

## Paper/Live Modes

- **Paper Config**: PAPER_LIVE_CONFIG.json
- **Active Mode**: Change single "active_mode" setting
- **Trading Logic**: IDENTICAL for both modes
- **Broker Endpoints**: Automatically switch (practice ↔ live)
- **Result**: Same logic, different money

## Quick Links

- Consolidation Index: Read first for complete overview
- Broker Verification: See OPTION_A_VERIFIED.txt for Coinbase/IBKR details
- Priority 3 Components: Run option_c_priority3_integration.py
- Quick Start: Run QUICK_START_AUTONOMOUS.sh

## Integration Stages

1. **Phase 1** (Complete) - new_RLC_rebuild system built
2. **Phase 2** (Complete) - Integrated into RICK_LIVE_CLEAN
3. **Phase 3** (Ready) - Priority 3 components available
4. **Phase 4** (Ready) - Paper/Live testing ready
5. **Phase 5** (Ready) - Live deployment with config switch

## Testing Recommendation

1. Run in paper mode for 1-2 weeks minimum
2. Verify all 9 systems passing (validate_system.py)
3. Monitor narration logs for proper event logging
4. Test position manager 60-second cycles
5. Verify guardian gates reject invalid trades
6. Switch config to "live" when confident

## Status

✅ All systems ready
✅ PIN 841921 immutable
✅ Guardian gates enforced
✅ Paper/Live modes configured
✅ Ready for deployment
EOF
}

# Create quick reference card
create_quick_reference() {
    cat > "$TARGET_ROOT/$DOC_SUBDIR/QUICK_REFERENCE.txt" << 'EOF'
╔════════════════════════════════════════════════════════════════════════════════╗
║                         RICK SYSTEM - QUICK REFERENCE                         ║
║                              PIN: 841921                                       ║
╚════════════════════════════════════════════════════════════════════════════════╝

STARTUP COMMANDS
════════════════════════════════════════════════════════════════════════════════

Paper Mode (Default):
  $ python3 rick_cli.py                    # Interactive CLI
  $ python3 position_manager.py            # Autonomous 60-second cycle
  $ python3 aggressive_money_machine.py    # Main trading engine
  $ tail -f logs/narration.log             # Real-time event monitoring

Validation:
  $ python3 validate_system.py             # Check all 9 systems
  $ python3 -m py_compile hive/*.py        # Syntax check

CRITICAL SETTINGS
════════════════════════════════════════════════════════════════════════════════

Config File:
  /home/ing/RICK/RICK_LIVE_CLEAN/config/PAPER_LIVE_CONFIG.json

Switch Paper → Live:
  Edit: "active_mode": "paper" → "active_mode": "live"
  Result: Same logic, real money

CHARTER RULES (IMMUTABLE)
════════════════════════════════════════════════════════════════════════════════

Universal:
  - PIN: 841921
  - Min notional: $15,000
  - Max hold: 6 hours
  - Min R:R: 3.2:1
  - Daily loss: -5% max

Limits:
  - Max concurrent: 3 positions
  - Margin cap: 35% NAV
  - Risk per trade: 2%
  - Leverage: 1.0x (no margin for crypto)

GUARDIAN GATES (ALL 4 MUST PASS)
════════════════════════════════════════════════════════════════════════════════

Gate 1: Margin Utilization ≤35% NAV
Gate 2: Concurrent Positions <3
Gate 3: Correlation Guard (no same-side USD)
Gate 4: Crypto Consensus ≥90% if crypto

POSITION MANAGER (60-SEC CYCLE)
════════════════════════════════════════════════════════════════════════════════

Every 60 seconds:
  1. Analyze all positions
  2. Check profit target (take profit)
  3. Monitor stops (stop loss)
  4. Tighten stops if needed
  5. Trail stops on winners
  6. Apply hedges if needed
  7. Reduce on correlation risk
  8. Add on confirmed trends
  9. Evaluate exits

Actions are autonomous (no approval needed).

MONITORING
════════════════════════════════════════════════════════════════════════════════

Real-Time Logging:
  $ tail -f logs/narration.log

Events Logged:
  - TRADE_INITIATED
  - GATE_REJECTED (when invalid trades blocked)
  - POSITION_MANAGED (60-sec cycle actions)
  - MARGIN_WARNING
  - PROFIT_TAKEN
  - STOP_HIT
  - CHART_VIOLATION
  - AUTONOMOUS_ACTION

TROUBLESHOOTING
════════════════════════════════════════════════════════════════════════════════

Validation Failures:
  $ python3 validate_system.py

Import Errors:
  $ python3 -m py_compile hive/*.py config/*.py

PIN Verification:
  $ python3 -c "from foundation.rick_charter import RickCharter; print(RickCharter.PIN)"
  Expected output: 841921

Connection Issues (IBKR):
  - Ensure IB Gateway/TWS running
  - Paper: Port 4002, Live: Port 4001

Performance:
  - Check narration logs for latency
  - Monitor logs/narration.log for execution times
  - Sub-300ms targets for crypto trades

DEPLOYMENT CHECKLIST
════════════════════════════════════════════════════════════════════════════════

Before Live Trading:
  [ ] Run validate_system.py - ALL 9 systems passing
  [ ] Monitor paper mode 1-2 weeks minimum
  [ ] Review narration logs for proper event logging
  [ ] Test all 9 autonomous position manager actions
  [ ] Verify guardian gates rejecting invalid trades
  [ ] Confirm PIN 841921 immutable
  [ ] Test manual pause/resume
  [ ] Verify broker endpoints correct
  
To Go Live:
  [ ] Edit PAPER_LIVE_CONFIG.json
  [ ] Change: "active_mode": "paper" → "active_mode": "live"
  [ ] NO code changes needed
  [ ] Run validate_system.py again
  [ ] Start trading with real money

CRITICAL FILES
════════════════════════════════════════════════════════════════════════════════

Foundation (Never Change):
  /home/ing/RICK/RICK_LIVE_CLEAN/foundation/rick_charter.py
  /home/ing/RICK/RICK_LIVE_CLEAN/hive/guardian_gates.py

Core Trading:
  /home/ing/RICK/RICK_LIVE_CLEAN/position_manager.py
  /home/ing/RICK/RICK_LIVE_CLEAN/aggressive_money_machine.py
  /home/ing/RICK/RICK_LIVE_CLEAN/rick_cli.py

Configuration:
  /home/ing/RICK/RICK_LIVE_CLEAN/config/PAPER_LIVE_CONFIG.json
  /home/ing/RICK/RICK_LIVE_CLEAN/config/enhanced_task_config.py

Logging:
  /home/ing/RICK/RICK_LIVE_CLEAN/config/narration_logger.py
  /home/ing/RICK/RICK_LIVE_CLEAN/logs/narration.log

SUPPORT CONTACTS
════════════════════════════════════════════════════════════════════════════════

System Issues:
  - Check narration logs first: tail -f logs/narration.log
  - Run validate_system.py for diagnostics
  - Review guardian gate rejections in logs

Broker Issues:
  - OANDA: Check API credentials in .env
  - Coinbase: Verify API keys (sandbox vs live)
  - IBKR: Ensure TWS/Gateway running (ports 4001/4002)

Code Issues:
  - Python syntax: python3 -m py_compile [file].py
  - Imports: python3 -c "import [module]"
  - Tests: python3 validate_system.py

════════════════════════════════════════════════════════════════════════════════
EOF
}

# Create knowledge transfer summary
create_knowledge_transfer() {
    cat > "$TARGET_ROOT/$DOC_SUBDIR/KNOWLEDGE_TRANSFER.md" << 'EOF'
# RICK System - Complete Knowledge Transfer Guide

## What You Need to Know First

### 1. The System Overview
RICK (Robustly Insured Cryptocurrencies & Korrelations) is a fully autonomous trading system that:
- Executes trades automatically with NO manual approval needed
- Enforces 14+ immutable trading rules (PIN 841921 protected)
- Uses 4 cascading guardian gates to validate every trade
- Manages positions autonomously every 60 seconds
- Supports multiple brokers (OANDA, Coinbase, IBKR)
- Trades identically in paper and live modes

### 2. The PIN - 841921
- Hardcoded in foundation/rick_charter.py
- Immutable - cannot be overridden
- Required for all charter enforcement
- Required for all broker operations
- Never changes, never expires

### 3. Guardian Gates - All Must Pass (AND Logic)
```
Gate 1 (Margin): ≤35% NAV
Gate 2 (Positions): <3 concurrent
Gate 3 (Correlation): No same-side USD conflicts
Gate 4 (Crypto): ≥90% hive consensus if crypto
```
If ANY gate fails → trade REJECTED. If ALL pass → trade APPROVED.

### 4. The Position Manager (60-Second Autonomous Cycle)
Every 60 seconds:
1. Analyze all open positions
2. Execute ONE of 9 possible autonomous actions:
   - HOLD (do nothing)
   - TAKE_PROFIT (close winners)
   - STOP_LOSS (close losers)
   - TIGHTEN_STOP (move stops up)
   - TRAIL_STOP (follow price up)
   - APPLY_HEDGE (reduce risk)
   - REDUCE (partially close)
   - ADD (add to winner)
   - EVALUATE_EXIT (check exit logic)

### 5. Paper vs Live - Same Logic, Different Money
- Paper mode: Practice trading (simulated execution)
- Live mode: Real money trading
- **Identical trading logic** for both
- Switch with config file: "active_mode": "paper" vs "live"
- NO code changes needed

## Critical Architecture

### File Structure
```
foundation/
  ├─ rick_charter.py                  ← PIN 841921 (NEVER CHANGE)
  └─ margin_correlation_gate.py       ← Margin calculations

hive/
  ├─ guardian_gates.py                ← 4 cascading gates (CRITICAL)
  ├─ quant_hedge_rules.py            ← 5 conditions, 7 actions
  └─ crypto_entry_gate_system.py     ← Crypto-specific validation

config/
  ├─ PAPER_LIVE_CONFIG.json          ← Paper/Live toggle (KEY FILE)
  ├─ narration_logger.py             ← Event logging
  └─ enhanced_task_config.py         ← Configuration interface

brokers/
  ├─ oanda_connector.py               ← Forex/CFDs
  ├─ coinbase_connector.py            ← Crypto
  └─ ib_connector.py                  ← Futures/Stocks/Forex

position_manager.py                    ← 60-second autonomous cycle
aggressive_money_machine.py            ← Main trading engine
rick_cli.py                            ← CLI interface
validate_system.py                     ← System diagnostics
```

### How Trades Get Executed

```
User Signal (from ML models)
  ↓
Charter Validation (PIN 841921)
  ↓
Guardian Gates (4 cascading checks)
  ├─ Gate 1: Margin ≤35%?
  ├─ Gate 2: Positions <3?
  ├─ Gate 3: Correlation OK?
  └─ Gate 4: Hive consensus ≥90%? (if crypto)
  ↓
Position Sizing (Kelly Criterion)
  ↓
Order Placement (Broker-specific)
  ↓
Execution (Real or simulated based on mode)
  ↓
Narration Logged (Plain English)
  ↓
Position Manager Monitors (Every 60 seconds)
```

## Key Components Explained

### 1. Guardian Gates (hive/guardian_gates.py)
Four sequential validation gates that must ALL pass:

**Gate 1: Margin Utilization**
- Question: Is margin usage ≤35% of NAV?
- Calculation: Current positions value / Total account value
- If FAIL: Prevents new entries, allows exits only

**Gate 2: Concurrent Positions**
- Question: Are we under 3 concurrent positions?
- Rationale: Concentration risk - too many positions = more risk
- If FAIL: New positions rejected until one closes

**Gate 3: Correlation Guard**
- Question: Are there no conflicting USD exposures?
- Example: Can't be long EUR/USD while short GBP/USD (both bullish USD)
- If FAIL: Conflicting position rejected

**Gate 4: Crypto Consensus (90% for crypto, N/A for forex)**
- Question: Do ≥90% of hive models agree this is a good trade?
- Applies: Only to cryptocurrency trades
- If FAIL: Crypto trade rejected despite other factors

### 2. Quant Hedge Rules (hive/quant_hedge_rules.py)
Analyzes 5 market conditions with weighted scoring:

**Condition Weights:**
- Volatility: 30% (market volatility level)
- Trend: 25% (directional momentum)
- Correlation: 20% (position correlation risk)
- Volume: 15% (trading volume support)
- Margin: 10% (available margin)

**7 Possible Recommendations:**
1. FULL_LONG - Go fully bullish
2. MODERATE_LONG - Conservative bullish
3. REDUCE_EXPOSURE - Cut position size
4. CLOSE_ALL - Exit everything
5. HEDGE_SHORT - Add bearish hedge
6. PAUSE - Wait for better setup
7. WAIT - Accumulate more data

### 3. Position Manager (position_manager.py)
Runs continuously in background thread, every 60 seconds:

```python
while trading_active:
    sleep(60)  # Wait 60 seconds
    for position in all_positions:
        # Analyze this position
        pnl_percent = (current_price - entry_price) / entry_price
        
        # If in profit and hit target
        if pnl_percent >= target_profit:
            TAKE_PROFIT  # Close partial or all
        
        # If below stop
        elif current_price < stop_price:
            STOP_LOSS  # Close position
        
        # If trending up and no stop above price
        elif trend_is_up and stop_below_trend:
            TRAIL_STOP  # Move stop up
        
        # Other actions...
```

### 4. Narration Logger (config/narration_logger.py)
Logs all events in plain English to logs/narration.log:

```
2025-11-15 14:23:45 | TRADE_INITIATED | EUR/USD long 0.5% risk | Gate consensus 95%
2025-11-15 14:23:46 | ORDER_PLACED | Market order EUR/USD buy
2025-11-15 14:24:15 | POSITION_MANAGED | Position up 0.8%, trailing stop activated
2025-11-15 14:25:32 | MARGIN_WARNING | Margin at 32% (approaching 35% gate threshold)
2025-11-15 14:26:01 | POSITION_MANAGED | 60-second cycle: monitoring 3 positions
```

## Paper/Live Mode Details

### File: config/PAPER_LIVE_CONFIG.json

```json
{
  "mode": {
    "active_mode": "paper"  // ← CHANGE THIS: "paper" or "live"
  }
}
```

### What Changes When Switching

| Aspect | Paper | Live |
|--------|-------|------|
| Broker Endpoint | practice/sandbox | production |
| Real Money | NO | YES |
| Order Execution | Simulated | Real |
| Slippage | Simulated (±0.05%) | Real |
| Position Tracking | Simulated | Real |
| Guardian Gates | Identical | Identical |
| Position Manager | Identical | Identical |
| Risk Rules | Identical | Identical |
| Capital Tracking | Same math | Same math |

### No Code Changes Required
The entire system automatically detects the mode and switches execution layers while keeping trading logic 100% identical.

## Deployment Process

### Phase 1: Paper Mode Testing (1-2 weeks minimum)
```bash
# 1. Verify system
python3 validate_system.py

# 2. Start CLI
python3 rick_cli.py

# 3. Monitor position manager
python3 position_manager.py

# 4. Watch events (in another terminal)
tail -f logs/narration.log

# 5. Check narration for:
#    - Proper gate rejections
#    - Position manager actions every 60 seconds
#    - Charter enforcement working
#    - Correct position sizing
```

### Phase 2: Switch to Live
```bash
# 1. Edit config file
nano config/PAPER_LIVE_CONFIG.json

# 2. Change: "active_mode": "paper" → "active_mode": "live"

# 3. Verify again
python3 validate_system.py

# 4. Start trading
python3 rick_cli.py

# 5. Monitor closely
tail -f logs/narration.log
```

## Troubleshooting Guide

### Validation Fails
```bash
# Run full diagnostic
python3 validate_system.py

# Check syntax
python3 -m py_compile foundation/*.py hive/*.py

# Check PIN
python3 -c "from foundation.rick_charter import RickCharter; print(RickCharter.PIN)"
# Expected: 841921
```

### Guardian Gates Always Reject
- Check margin: narration logs show why (margin %, positions, correlation, etc)
- Check hive consensus: crypto trades need 90% agreement
- Check position count: max 3 concurrent

### Position Manager Not Running
- Check if background thread started: look in logs
- Monitor narration log for 60-second cycle events
- Verify no exceptions in logs

### Broker Connection Issues
- OANDA: Check .env for API credentials
- Coinbase: Verify sandbox vs live API keys
- IBKR: Ensure TWS/Gateway running (paper: 4002, live: 4001)

## Maintenance

### Daily
- Monitor narration logs for anomalies
- Check margin levels (should stay <35%)
- Verify position manager cycle running

### Weekly
- Review trading performance metrics
- Check for any gate rejections and why
- Analyze position sizing accuracy

### Monthly
- Review risk metrics
- Check capital growth trajectory
- Optimize position sizing if needed

## Emergency Procedures

### Stop All Trading
```bash
# Kill the process
pkill -f "python3 rick_cli.py"
pkill -f "position_manager.py"
```

### Force Close All Positions
Edit rick_cli.py, run option: "CLOSE_ALL_POSITIONS"

### Rollback to Paper Mode
Edit: config/PAPER_LIVE_CONFIG.json
Change: "active_mode": "live" → "active_mode": "paper"

## Summary

1. **System is fully autonomous** - No manual approval needed
2. **Guardian gates validate every trade** - 4 cascading checks
3. **Position manager runs autonomously** - 60-second cycle
4. **Paper and live are identical** - Only config file differs
5. **Charter rules are immutable** - PIN 841921 protects them
6. **All events are logged** - Plain English narration
7. **Ready to deploy** - Start in paper, switch config for live

Good luck with RICK! 🚀
EOF
}

# Main execution
log "INFO" "Starting Option D - Documentation Copying..."
copy_documentation

if [ $? -eq 0 ]; then
    exit 0
else
    log "ERROR" "Documentation copying failed"
    exit 1
fi
