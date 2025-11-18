# Phase 2 Integration Plan: new_RLC_rebuild -> RICK_LIVE_CLEAN

PIN: 841921 (immutable)
Date: 2025-11-16

## 1. Assessment Summary
Target repo already contains updated versions of key files (multiple backups present):
- foundation/rick_charter.py (current size ~6.9 KB) plus autonomous_charter.py (15 KB) also exists inside target. Need merge of expanded constants & documentation from autonomous_charter.py into active rick_charter.py if differences remain.
- hive/guardian_gates.py (11.3 KB) present; matches structure referencing 4 gates with documentation blocks.
- hive/quant_hedge_rules.py (29.6 KB) present; includes 5 weighted conditions and 7 actions.
- foundation/margin_correlation_gate.py (16.7 KB) present; includes margin + correlation guard logic.

Target ALREADY has some of Priority 2 components:
- position_manager.py exists (13.8 KB) – check parity with source version (new one ~14 KB) before deciding replace/merge.
- config/narration_logger.py exists (8.3 KB) – likely identical or slightly diverged; confirm diff before replacement.
- config/enhanced_task_config.py exists (15.6 KB) – already integrated.
- rick_cli.py exists (10.3 KB) – present; may differ from source (source had web launcher updates). Need diff & selective merge (add order router invocation if absent).

Broker connectors in target:
- brokers/oanda_connector.py (39.6 KB) + oanda_connector_enhanced.py present.
- brokers/coinbase_connector.py (32.3 KB) + coinbase_advanced_connector.py.
- brokers/ib_connector.py (19.2 KB).

Configuration & validation:
- AUTONOMOUS_CONFIG.json present.
- narration.jsonl log file exists (large) – logging active.
- requirements.txt minimal (255 bytes) – review for FastAPI/Uvicorn additions if web UI desired.
- validate_system.py exists (3.9 KB) – used for system checks.

Missing (from original priority list): None of Priority 1 & 2; already present. Optional features (crypto_entry_gate_system.py, portfolio_optimizer.py, adaptive_rick.py) are also present (crypto_entry_gate_system.py, adaptive_rick.py). Portfolio optimizer may be in logic/ – need later diff.

## 2. Differences & Conflict Notes (Initial High-Level)
Because autonomous_charter.py and rick_charter.py both exist in target, there is potential duplication. Backups show past merges; need a fresh diff to ensure all immutable constants from autonomous version are retained. Guardian gates & quant hedge rules already integrated – reduce risk of conflicts.
Potential conflicts:
- Divergent implementations of position_manager.py (source vs target) – ensure new order routing hooks and narration alignment.
- rick_cli.py might lack new web UI launcher and order router usage for manual trade path.
- coinbase_connector.py in target does not yet include market_order method we added in source environment (added here in rebuild). Integration should port that method if absent to standardize routing.

## 3. Proposed Integration Order
Priority A (Verification / Merge Review):
1. Diff autonomous_charter.py vs active rick_charter.py (confirm constants, PIN, rule completeness). Apply additive merge if any missing documentation or rules.
2. Diff position_manager.py (source vs target) – adopt newer autonomous action hooks if target lacks features (trail, tighten, hedge sequence).
3. Diff coinbase_connector.py – add market_order + OCO parameter alignment if missing.
4. Diff rick_cli.py – merge web UI launcher and order router invocation for manual trades.

Priority B (Adapters & Routing):
5. Introduce/verify execution/order_router.py into target (if not present) for unified manual execution.
6. Ensure narration_logger consistency (field names / event types). Merge if required.
7. Confirm enhanced_task_config.py affords broker selection and paper/live parity (skip if identical).

Priority C (Optional Enhancements):
8. Portfolio sizing (logic/portfolio_optimizer.py) – verify presence and integrate if missing.
9. Crypto entry gate improvements – ensure references wired to guardian flow.
10. Add FastAPI web UI (ui/hive_web.py + dependencies) if desired in target project (not currently in listing) – optional.

## 4. Rollback Strategy
- Full directory snapshot: cp -r RICK_LIVE_CLEAN RICK_LIVE_CLEAN.backup_$(date +%s)
- Per-file backups before each change: cp path/file.py path/file.py.backup_$(date +%s)
- Record applied diffs to integration_logs/diff_<filename>_$(date +%s).patch
- Maintain untouched backup of original charter & gates (already present).

## 5. Detailed Steps (Execution Phase Post-Approval)
1. Generate diffs for: rick_charter.py, position_manager.py, coinbase_connector.py, rick_cli.py.
2. Prepare patch sets (apply_patch) confined to missing methods / constants only.
3. Add order_router.py file (new) if absent.
4. Add market_order method to coinbase_connector.py (if absent) to support unified routing.
5. Insert web UI launcher option & PIN enforcement path in rick_cli.py (ensure numbering stable).
6. Run py_compile on modified modules; run validate_system.py.
7. Test manual trade (sandbox) via order_router standalone.
8. Confirm narration log entry (tail logs/narration.log).
9. Document changes in INTEGRATION_CHANGELOG.md.

## 6. Testing & Verification Checklist (Post-Integration)
- Charter PIN remains 841921; validation returns True.
- guardian_gates pass sequence unchanged; failure reasons intact.
- position_manager executes cycle (simulate add_position + tick function).
- order_router market trade (Coinbase sandbox) returns success + order_id.
- narration_logger writes OCO_PLACED / MARKET_TRADE events.
- rick_cli menu operates; selecting web UI launches server (if added).
- validate_system.py returns no errors.

## 7. Impact Estimate
Adds: order_router.py (+ ~250 lines). Potential minor additions to coinbase_connector.py and rick_cli.py (<100 lines combined). Low risk; contained changes.
Testing time: ~20 minutes end-to-end (diff review, patches, compile, functional smoke tests).
Rollback cost: <5 minutes (restore backups).

## 8. Open Questions (Need Confirmation Before Proceed)
- Should FastAPI web interface be integrated into target (currently absent)?
- Maintain both autonomous_charter.py and rick_charter.py or consolidate into single rick_charter.py? Recommendation: consolidate.
- Is existing position_manager.py functionally equivalent (need diff)?

## 9. Next Actions Pending Approval
Await go/no-go to:
- Produce precise diffs for the four primary files.
- Patch coinbase_connector & rick_cli.
- Introduce order_router.

## 10. Safety Notes
All modifications will preserve PIN usage and immutable constants. No removal of gating logic. Order router only augments manual execution pathway; autonomous logic untouched.

---
Prepared by: Integration Assistant
Ready for: Review & Approval
