#!/bin/bash
#
# QUICK START GUIDE - OPTIONS A, C, and D
# PIN: 841921
#

cat << 'EOF'

╔════════════════════════════════════════════════════════════════════════════════╗
║                                                                                ║
║               QUICK START - OPTIONS A, C, and D READY TO GO                  ║
║                                                                                ║
║                          PIN: 841921 | Ready Now                              ║
║                                                                                ║
╚════════════════════════════════════════════════════════════════════════════════╝


WHAT'S BEEN COMPLETED
════════════════════════════════════════════════════════════════════════════════

✅ OPTION A: Verified Coinbase and IBKR broker adjustments
   ├─ Coinbase: Paper/live switching, OCO orders, 90% hive consensus
   ├─ IBKR: Port configuration, futures margin, conditional orders
   └─ Both have platform-specific "adjustments that account for things"

✅ OPTION C: Priority 3 components ready for integration
   ├─ Crypto Entry Gate System (23 KB)
   ├─ Portfolio Optimizer (16 KB)
   ├─ Adaptive RICK (18 KB)
   └─ Enhanced OANDA Connector (21 KB)

✅ OPTION D: Documentation copied and organized
   ├─ Core consolidation documents (7 files)
   ├─ Reference guides (9+ files)
   ├─ Configuration file (PAPER_LIVE_CONFIG.json - KEY FILE)
   └─ Integration scripts (4 utilities)

✅ PAPER/LIVE UNIFIED SYSTEM
   ├─ Single config file switches paper ↔ live mode
   ├─ Identical trading logic for BOTH modes
   ├─ NO code changes needed
   └─ Charter, gates, risk rules same for all


CRITICAL FILE - KNOW THIS FIRST
════════════════════════════════════════════════════════════════════════════════

File: config/PAPER_LIVE_CONFIG.json

To Switch Paper → Live:
  1. Open: nano /home/ing/RICK/RICK_LIVE_CLEAN/config/PAPER_LIVE_CONFIG.json
  2. Find: "active_mode": "paper"
  3. Change: "active_mode": "live"
  4. Save: Ctrl+O, Enter, Ctrl+X

That's it. Everything else stays the same.


TRADING LOGIC - IDENTICAL FOR BOTH MODES
═════════════════════════════════════════════════════════════════════════════════

Charter Enforcement:
  ✓ PIN 841921 (hardcoded, immutable)
  ✓ All 14+ universal rules enforced
  ✓ Cannot be overridden

Guardian Gates (All 4 Must Pass):
  ✓ Gate 1: Margin ≤35% NAV
  ✓ Gate 2: Positions <3
  ✓ Gate 3: Correlation (no USD conflicts)
  ✓ Gate 4: Crypto consensus ≥90%

Position Manager:
  ✓ Every 60 seconds: Reassess all positions
  ✓ 9 autonomous actions available
  ✓ No manual approval needed

Risk Management:
  ✓ 2% risk per trade
  ✓ 3.2:1 min risk/reward
  ✓ -5% daily loss breaker

Result: PAPER and LIVE trade identically


PAPER MODE (BEFORE GOING LIVE)
═════════════════════════════════════════════════════════════════════════════════

Steps:
  1. Verify system:
     $ python3 validate_system.py
     (All 9 systems must show ✅ passing)

  2. Start trading:
     $ python3 rick_cli.py
     (Interactive menu)

  3. Monitor in another terminal:
     $ tail -f logs/narration.log
     (Watch real-time events)

  4. Test for 1-2 weeks:
     ✓ Watch position manager 60-second cycles
     ✓ Verify guardian gates rejecting trades
     ✓ Check narration logging
     ✓ Monitor performance

  5. When confident:
     Switch to live (see below)


LIVE MODE (REAL MONEY TRADING)
═════════════════════════════════════════════════════════════════════════════════

Prerequisites:
  [ ] Paper tested for 1-2 weeks minimum
  [ ] All 9 systems passing validation
  [ ] Confident in trading logic
  [ ] Understand guardian gates
  [ ] Understand risk management

How to Switch:
  1. Edit: nano config/PAPER_LIVE_CONFIG.json
  2. Change: "active_mode": "paper" → "active_mode": "live"
  3. Verify: python3 validate_system.py
  4. Start: python3 rick_cli.py
  5. Monitor: tail -f logs/narration.log

Result: Same trading logic, real money execution


IMMEDIATE COMMANDS
═════════════════════════════════════════════════════════════════════════════════

Verify Everything:
  $ python3 validate_system.py

Check PIN is immutable:
  $ python3 -c "from foundation.rick_charter import RickCharter; print(RickCharter.PIN)"
  Expected: 841921

Check Python syntax:
  $ python3 -m py_compile hive/*.py config/*.py

Start CLI (paper mode):
  $ python3 rick_cli.py

Monitor events (new terminal):
  $ tail -f logs/narration.log

Run Priority 3 Integration (optional):
  $ python3 option_c_priority3_integration.py

Copy Documentation (optional):
  $ bash option_d_copy_documentation.sh


WHAT EACH OPTION PROVIDES
═════════════════════════════════════════════════════════════════════════════════

OPTION A - Broker Verification
  What: Confirms Coinbase and IBKR have proper adjustments
  Why: Ensure brokers handle paper/live switching correctly
  Where: OPTION_A_VERIFIED.txt
  Status: ✅ Complete (just for confirmation)

OPTION C - Priority 3 Components
  What: 4 optional enhancements for better trading
  Why: Improve performance with crypto gates, ML selection, portfolio optimization
  How: Run option_c_priority3_integration.py
  Status: ✅ Ready (can be added anytime)

OPTION D - Documentation
  What: Complete knowledge transfer package
  Why: Have all docs available in target location
  How: Run option_d_copy_documentation.sh
  Status: ✅ Ready (run to organize docs)


KEY FILES TO KNOW
═════════════════════════════════════════════════════════════════════════════════

Foundation (NEVER CHANGE):
  foundation/rick_charter.py          (PIN 841921 - immutable)
  hive/guardian_gates.py              (4 cascading gates)

Core Trading:
  position_manager.py                 (60-second autonomous cycle)
  aggressive_money_machine.py         (main trading engine)
  rick_cli.py                         (CLI interface)

THE KEY FILE (CHANGE TO SWITCH MODES):
  config/PAPER_LIVE_CONFIG.json       (paper vs live)

Monitoring:
  logs/narration.log                  (all events logged)


AUTOMATION SCRIPTS
═════════════════════════════════════════════════════════════════════════════════

Master Script (Run All):
  $ bash MASTER_EXECUTION_A_C_D.sh
  (Takes ~5-10 minutes, runs all checks)

Priority 3 Integration:
  $ python3 option_c_priority3_integration.py
  (Adds optional enhanced components)

Documentation Copy:
  $ bash option_d_copy_documentation.sh
  (Organizes all docs in target location)

Quick Reference:
  View: /home/ing/RICK/new_RLC_rebuild/OPTIONS_A_C_D_COMPLETE.txt


DEPLOYMENT TIMELINE
═════════════════════════════════════════════════════════════════════════════════

Day 1: Validation & Setup
  [ ] Read OPTIONS_A_C_D_COMPLETE.txt
  [ ] Run: python3 validate_system.py
  [ ] Verify: All 9 systems passing

Day 1-14: Paper Mode Testing (1-2 weeks)
  [ ] Trade with: python3 rick_cli.py
  [ ] Monitor: tail -f logs/narration.log
  [ ] Test position manager 60-second cycles
  [ ] Verify guardian gates rejecting invalid
  [ ] Check PIN 841921 immutable
  [ ] Confirm narration logging working

Week 2+: Go Live (When ready)
  [ ] Edit: config/PAPER_LIVE_CONFIG.json
  [ ] Change: "active_mode": "paper" → "active_mode": "live"
  [ ] Run: python3 validate_system.py (again)
  [ ] Start: python3 rick_cli.py
  [ ] Monitor closely: tail -f logs/narration.log


BROKER DETAILS
═════════════════════════════════════════════════════════════════════════════════

OANDA
  Paper: Practice API endpoint
  Live: Live API endpoint
  Same logic applies to both

Coinbase
  Paper: Sandbox API
  Live: Production API
  Same logic applies to both
  Special: 90% hive consensus for crypto trades

IBKR (Interactive Brokers)
  Paper: Port 4002, demo account DU6880040
  Live: Port 4001, real account from env
  Same logic applies to both
  Special: Futures margin calculations


CRITICAL REMINDERS
═════════════════════════════════════════════════════════════════════════════════

1. PIN 841921 is IMMUTABLE
   - Hardcoded in rick_charter.py
   - Cannot be changed or overridden
   - Protects system integrity

2. Guardian Gates use AND logic
   - ALL 4 gates must PASS for trade execution
   - If ANY gate fails → trade REJECTED
   - Designed for maximum safety

3. Paper and Live trade IDENTICALLY
   - Same charter rules
   - Same guardian gates
   - Same position manager
   - Only difference: real vs simulated money

4. Position Manager is AUTONOMOUS
   - Every 60 seconds: reassesses positions
   - 9 possible actions available
   - NO manual approval needed

5. All Events are LOGGED
   - Every trade logged
   - Every gate rejection logged
   - Every autonomous action logged
   - Check: logs/narration.log


TROUBLESHOOTING QUICK REFERENCE
═════════════════════════════════════════════════════════════════════════════════

Validation fails?
  $ python3 validate_system.py

Syntax errors?
  $ python3 -m py_compile hive/*.py config/*.py

Can't import modules?
  $ python3 -c "import foundation; import hive"

Position manager not running?
  Check: tail -f logs/narration.log for 60-second cycle events

Guardian gates always rejecting?
  Check: narration logs for specific rejection reason
  (margin too high, positions too many, correlation issue, hive consensus low)

PIN not immutable?
  Test: python3 -c "from foundation.rick_charter import RickCharter; print(RickCharter.PIN)"
  Expected output: 841921

Broker connection issues?
  OANDA: Check .env for API credentials
  Coinbase: Verify sandbox vs live API keys
  IBKR: Ensure TWS/Gateway running on correct port


NEXT ACTIONS (IN ORDER)
═════════════════════════════════════════════════════════════════════════════════

1. READ:
   $ cat OPTIONS_A_C_D_COMPLETE.txt

2. VERIFY:
   $ python3 validate_system.py

3. TEST (Paper Mode):
   $ python3 rick_cli.py

4. MONITOR:
   $ tail -f logs/narration.log

5. WAIT (1-2 weeks):
   Monitor trading performance

6. SWITCH (When ready):
   Edit config/PAPER_LIVE_CONFIG.json

7. VERIFY AGAIN:
   $ python3 validate_system.py

8. TRADE LIVE:
   $ python3 rick_cli.py
   (Now with real money, identical logic)


DONE!
═════════════════════════════════════════════════════════════════════════════════

You now have:
  ✅ Option A: Broker adjustments verified
  ✅ Option C: Priority 3 components ready
  ✅ Option D: Documentation organized
  ✅ Paper/Live system configured
  ✅ Identical trading logic for both modes
  ✅ Ready for immediate deployment

Start with: python3 validate_system.py

Then: python3 rick_cli.py

Good luck trading! 🚀

════════════════════════════════════════════════════════════════════════════════

EOF
