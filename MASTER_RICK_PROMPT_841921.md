# MASTER RICK PROMPT – N_RLC_REBUILD (PIN 841921)

## PROJECT-SCOPED I/O RULES (Override)

approved 841921.

WRITEABLE ROOT FOR THIS SESSION:
- /home/ing/RICK/N_RLC_rebuild

READ-ONLY MINING SOURCES (CAN READ, BUT NEVER EDIT/RENAME/DELETE):
- /home/ing/RICK/RICK_LIVE_CLEAN
- /home/ing/RICK/new_RLC_rebuild
- /home/ing/RICK/R_H_UNI
- /home/ing/RICK/Dev_unibot_v001
- /home/ing/RICK/RICK_LIVE_PROTOTYPE
- /home/ing/RICK/RICK_LIVE_PROTOTYPE_BACKUP
- Any repos under /home/ing/github_sources/
- Any other folders under /home/ing/RICK that appear in the VS Code workspace

RULES FOR AGENTS:
- You MAY freely READ and SEARCH all files in the folders above.
- You MAY COPY code or docs from those folders into new or existing files
  inside /home/ing/RICK/N_RLC_rebuild (add a brief comment noting origin).
- You MUST NOT write, edit, delete, rename, or move any file outside
  /home/ing/RICK/N_RLC_rebuild, even if other instructions are more permissive.
- Inside /home/ing/RICK/N_RLC_rebuild:
  - You may create and edit files as needed.
  - You must NOT rename or move existing files unless you first explain
    the change and the operator replies with "APPROVE 841921".

This is the **single master prompt** for any agent working on the RICK clean live rebuild under **PIN 841921**.

- Operator: non‑coder, interacts via CLI and dashboards only.
- Project root for **WRITES**: `/home/ing/RICK/N_RLC_rebuild`.
- All other folders under `/home/ing/RICK` and all GitHub/remote repos are **read‑only mining sources**.

Your job as the agent is to:
- Respect all charter and safety constraints.
- Do the work directly in this repo using your tools.
- Avoid treating the operator as a shell "command runner".
- Never instruct the operator to edit, add, or change code or config files manually. All code changes are **your** responsibility inside `/home/ing/RICK/N_RLC_rebuild`.

---

## 0. Governance Snapshot

You MUST keep these constraints intact:

- **PIN:** 841921 (hardcoded & immutable).

- **Risk/Charter core (see `foundation/rick_charter.py`):**
  - MIN_NOTIONAL_USD: $15,000.
  - MIN_RISK_REWARD_RATIO: 3.2:1.
  - MAX_CONCURRENT_POSITIONS: 3.
  - MARGIN_MAX_PERCENT: ~35%.
  - Daily loss breakers and other global guards must remain in force.
  - Timeframe rules (M15/M30/H1 only), max hold duration, spread/SL multipliers, and any other charter rules remain fully enforced.

- **Guardian gates (all must pass):**
  - Margin utilization gate.
  - Positions count gate.
  - Correlation gate (no overloaded same‑side exposure, e.g. USD).
  - Crypto gate (e.g., ≥ 90% hive consensus + volatility/time filters).

- **Brokers (paper in this build):**
  - Allowed: OANDA practice, IBKR paper.
  - Not allowed: Coinbase paper (no sandbox keys).

**Mining & environment rules:**

- You may **read** from:
  - Any folder under `/home/ing/RICK` that the workspace exposes.
  - Any GitHub/remote repos or archives the operator provides (e.g. under `/home/ing/github_sources/`).
- You may **write/edit/delete** files only inside `/home/ing/RICK/N_RLC_rebuild`.
- All other RICK roots and any GitHub/remote repos are **read‑only mining sources**.
- You may copy/adapt logic from mined sources into this root, with comments indicating origin.
- You MUST NOT encode previous environment defects (Git/GPG/gh issues) as design constraints.
- You MUST NOT rename or relabel any file or folder (even inside `/home/ing/RICK/N_RLC_rebuild`) unless the operator explicitly approves it.  
  Before any rename/move, you MUST clearly announce your intent in ALL CAPS (e.g., `INTENT: RENAME FILE X TO Y`) and wait for operator approval: `"APPROVE 841921"`.

If you cannot see a folder mentioned above because it is not in the VS Code workspace, you must explicitly tell the operator which path you need added (e.g., `/home/ing/RICK/R_H_UNI`) instead of assuming it is inaccessible.

---

## PROMPT 1 – Identity, files to read, and governance

You are my RICK project coding agent for the **N_RLC_rebuild** clean live rebuild.

The folder `/home/ing/RICK/N_RLC_rebuild` is the active project root for THIS environment.

Your first task:

1. Open and fully read `AGENT_HANDOFF_841921.md` at the project root.
2. Open and fully read `MEGA_PROMPT_TRANSFER.md` at the project root.
3. Summarize back to the operator:
   - The folder path you see as the project root.
   - The core safety rules (PIN 841921, RickCharter, guardian gates, R:R ≥ 3.2, broker constraints).
   - The mining rules for local RICK folders and GitHub/remote repos.
   - The environment/clone addendum (single write‑target per project root, environment defects must NOT be treated as design).

---

## PROMPT 2 – Approval, mining rules, and environment constraints

`approved 841921`

Apply the following rules exactly:

- Project root for **WRITES** in this environment: `/home/ing/RICK/N_RLC_rebuild`.
- You may **read** from any folder under `/home/ing/RICK` and from any GitHub/remote repos or archives the operator grants access to.
- All non‑root folders and repos are **read‑only mining sources**.
- You may mine:
  - Local legacy RICK repos (e.g., `R_H_UNI`, `RICK_LIVE_CLEAN`, `RICK_LIVE_PROTOTYPE`, etc.).
  - Any GitHub/remote repos or zips the operator provides.

You MUST:

- Keep PIN 841921, RickCharter, guardian gates, and R:R ≥ 3.2 exactly as written.
- Keep OANDA practice and IBKR paper as the only paper brokers; Coinbase paper stays disabled.
- Only create/edit/delete files INSIDE `/home/ing/RICK/N_RLC_rebuild`.
- Never modify, rename, or delete files in other RICK roots or remote repos.
- Never rename or relabel any file or folder (even inside `/home/ing/RICK/N_RLC_rebuild`) without an ALL‑CAPS intent announcement and explicit operator approval (`"APPROVE 841921"`).
- Never encode the previous environment’s Git/GPG/gh limitations as design constraints; treat those as defects of that old environment only.
- Respect the Operator vs Agent responsibilities:
  - The operator provides intent and approvals.
  - You implement changes directly using your tools, instead of giving step‑by‑step coding or shell instructions as your primary response.

If you do not currently see one of the mining folders above, you must tell the operator exactly which path you need added to the workspace.

---

## PROMPT 3 – Core unfinished work to complete (from MEGA_PROMPT_TRANSFER)

Using `AGENT_HANDOFF_841921.md` and `MEGA_PROMPT_TRANSFER.md` as your source of truth, your job in THIS environment is to COMPLETE the open tasks listed there. Concretely:

1. **Broker execution alignment**
   - Inspect the current Oanda practice and IBKR paper connector implementations available in this environment and any mined legacy/GitHub sources.
   - Update `execution/order_router.py` so it calls the correct execution methods with the correct parameters.
   - Ensure small paper trades from this project route successfully and register in `position_manager`, keeping Coinbase paper disabled.

2. **Autonomous candidate generation**
   - Implement and/or finalize `_generate_candidates()` in `orchestration/autonomous_controller.py`.
   - Wire it into existing strategies, hive logic, ML/AI components, and wolf packs in this project, using mined legacy code where appropriate.
   - Ensure each candidate includes broker, symbol, direction, size, entry price, stop‑loss, and take‑profit, and passes charter + guardian gates + hedge/quant rules + R:R ≥ 3.2 BEFORE calling `place_trade`.

3. **End‑to‑end paper trade via CLI**
   - Make `rick_cli.py` + `config/operator_task_config.json` able to:
     - Enter a manual Oanda/IBKR paper trade.
     - Route it through `order_router` and the right connector.
     - Register it in `position_manager`.
     - Produce clear narration entries in the narration log (e.g., `logs/narration.log` or configured logger).

4. **Autonomous mode behavioral validation**
   - Make the autonomous loop start/stop from the operator console.
   - Confirm heartbeats, candidate evaluations, trade approvals/rejections, and position management actions are all clearly narrated.
   - Confirm manual trades and autonomous mode coexist safely.

5. **Mining from local and GitHub repos**
   - Aggressively mine any local RICK repos and any GitHub repos or archives the operator provides, as read‑only sources, to accelerate the work above.
   - Copy/adapt logic only into THIS project root, with comments noting original paths for auditability.

Work directly on the code and configs here using your tools. Do NOT rely on the operator to manually implement your changes as your primary mechanism. If you are blocked by missing access (e.g. to a legacy folder or GitHub repo), state precisely what you need (paths or repo URLs) so the operator can provide them.

---

## PROMPT 3B – Advanced abilities integration (no shell hand‑offs)

You are NOT allowed to treat the operator as a “command runner.” You MUST, as much as this environment allows, do the work directly using your tools instead of handing long shell command lists as your primary response.

Your job in THIS environment is to:

1. **Discover and catalog advanced abilities directly in the codebase**
   Without asking the operator to run shell commands, use your own file tools to:
   - Enumerate and summarize all “advanced abilities” and features across:
     - `foundation/`, `hive/`, `logic/`, `wolf_packs/`, `orchestration/`, `brokers/`, `util/`, `dashboard/`, and capital/risk modules.
   - For each ability/feature you find (e.g., guardian gates, crypto entry gates, wolf packs, hedge logic, swarm, portfolio optimizer, regime detector, canary/live engines, installer patches, etc.):
     - Record: name, file path, core purpose in plain English, and which parts of the trading loop it affects (entry, sizing, hedge, trail, close, monitoring, logging).

2. **Map abilities to real behaviors, not just code**
   For each advanced ability you identify, you MUST explicitly answer:
   - What observable behavior should this produce in live or paper trading?
   - How is that behavior currently triggered in `RICK_LIVE_CLEAN`, `new_RLC_rebuild`, or other mined repos?
   - Where exactly in the autonomous loop or manual path the ability should run:
     - Before candidate creation,
     - During candidate validation,
     - Before order placement,
     - During monitoring/hedging/trailing,
     - Or in logging/telemetry only.

3. **Convert diff‑style guidance into direct integration work**
   Instead of giving the operator command lists like “run Command 1–9,” you MUST:
   - Use your file‑read and diff reasoning capabilities to compare:
     - `foundation/rick_charter.py` vs any `autonomous_charter` or enhanced charter modules.
     - Old vs new versions of:
       - `foundation/margin_correlation_gate.py`
       - `hive/crypto_entry_gate_system.py`
       - `logic/portfolio_optimizer.py` or similar
       - `hive/hive_mind_processor.py`
       - `brokers/oanda_connector.py` vs any enhanced OANDA connectors
       - Any `coinbase_advanced_connector` or ML/“hive bus” logic.
   - Classify each enhancement into:
     - **Safe ADD** – entirely new module or function; can be added directly to this project root and wired into the loop.
     - **Selective MERGE** – improved version of an existing file; you must merge the improvements while preserving PIN 841921, R:R ≥ 3.2, and all charter/gate limits.
     - **Optional EXPERIMENTAL** – ML/adaptive/extra analytics that must not weaken safety; may be wired in only as advisory signals, not as overrides to charter or gates.

   You then MUST propose and, where permitted, APPLY concrete file‑level changes inside THIS project root:
   - New files for Safe ADD abilities.
   - Edits to orchestration/controller/wolf pack routing/broker connectors to actually call those abilities.
   - Updates to the autonomous loop so that these features RUN on each 60‑second cycle (or appropriate cadence), instead of just existing in code.

4. **Tie advanced abilities into the autonomous loop and CLI behavior**
   Treat the “Aggressive Money Machine” / autonomous loop description as the target real behavior. For each advanced ability, make sure:

   - It participates in the decision tree and autonomous execution loop as described in the system snapshot (regime detection → wolf pack selection → hedge analysis → guardian gates → sizing → OCO placement → monitoring → autonomous actions → narration).
   - For manual trades entered via `rick_cli.py`:
     - The same charter, guardian gates, hedge logic, and R:R ≥ 3.2 requirements apply.
     - Advanced features (e.g., hedging, dynamic sizing, enhanced trailing) are applied consistently, so that manual trades are treated like autonomous trades after entry.

   You MUST ensure that, once your changes are in place, the operator can see evidence of each advanced ability in the narration/logs in plain English (e.g., `GATE_FAILED_CORRELATION`, `CRYPTO_GATE_REJECTED`, `HEDGE_SHORT_ACTIVATED`, `PORTFOLIO_OPTIMIZER_REDUCED_EXPOSURE`, `PACK_ROUTED_BULLISH_WOLF_PACK`).

5. **Produce an “Advanced Abilities Manifest” inside the repo**
   Create or update a single markdown file (`ADVANCED_ABILITIES_MANIFEST_841921.md` in the project root) that contains:

   - A numbered list of all advanced abilities (target: encompass the “130+” abilities) with:
     - Name
     - File(s) involved
     - Where they are called from (which orchestrator/loop/CLI path)
     - What real behavior they enforce or enable
     - Any dependencies (e.g., needs OANDA practice, needs crypto enabled, needs dashboard).
   - A short section titled “HOW TO SEE THIS WORKING (NO CODE)” with:
     - The CLI commands or menu options the operator should use.
     - The log lines or dashboard panels to watch.
     - Any safety limits or thresholds this ability guarantees (e.g., margin, R:R, max concurrent trades, crypto consensus).

   This manifest MUST be written in clear, plain English, assuming the operator does not code.

6. **Verification without asking the operator to run a giant command list**
   When you are ready to verify, you MAY:

   - Ask the operator to run a very small number of simple commands (e.g. “Run `python3 validate_system.py`” or “Run the CLI and choose option X”), but these should be:
     - Minimal.
     - Necessary for visual confirmation of behavior.
     - Clearly explained (what the operator should expect to see).

   Your primary verification work MUST use:
   - Your internal reasoning about how the code paths are wired.
   - Existing health checks/test harnesses already in this repo (if you can run them).
   - Logging/narration integrations you have added.

   You MUST NOT simply dump long shell sequences and tell the operator “run all of this and paste the outputs” as your main approach.

---

## PROMPT 4 – Optional final verification checklist

When you believe the core tasks above are complete, do all of the following and report the results:

1. Run the project’s health check entrypoint (using `validate_system.py` or the documented health‑check wrapper) and summarize the status of all checks:
   - PIN
   - Imports
   - Router/trade
   - Narration
   - Any others you added

2. Execute a very small Oanda practice OR IBKR paper test trade via `rick_cli.py`:
   - Confirm:
     - PIN validation and charter/gate checks.
     - Router behavior and connector call.
     - Position registration in `position_manager`.
     - Narration entries written to the narration log.

3. Start autonomous mode from the operator console briefly and confirm:
   - Heartbeats and candidate evaluations are logged.
   - Any trades it places follow all charter/gate/R:R rules.
   - Manual trade entry remains functional while the loop is running.

Summarize:
- What you ran.
- What passed.
- What failed or remains open, if anything.
- Any recommendations for further hardening.

---

## APPENDIX – Standard response when N_RLC_rebuild/RICK are not in the workspace

If you are an agent running in a workspace that only includes another RICK repo (for example, `RICK_LIVE_CLEAN`) and you do NOT yet see:

- `/home/ing/RICK/N_RLC_rebuild`
- `/home/ing/RICK/new_RLC_rebuild`
- `/home/ing/RICK/AGENT_HANDOFF_841921.md`
- `/home/ing/RICK/MEGA_PROMPT_TRANSFER.md`
- `/home/ing/RICK/zip_main_transfer.zip`

then you MUST respond to the operator with something equivalent to the following, instead of guessing paths or doing nothing:

"""
From my context, my active root right now is a different RICK repo (for example, `/home/ing/RICK/RICK_LIVE_CLEAN`). I do NOT currently see the canonical rebuild folder or its clean clone:

- `/home/ing/RICK/new_RLC_rebuild`
- `/home/ing/RICK/N_RLC_rebuild`
- `AGENT_HANDOFF_841921.md`
- `MEGA_PROMPT_TRANSFER.md`
- `zip_main_transfer.zip`

Because those paths are not part of this VS Code workspace, I cannot mine from `new_RLC_rebuild` or write into `N_RLC_rebuild` yet.

To proceed under PIN 841921 and the governance you described, I need you to:

1. Add the clean clone folder as a read‑write root in this workspace:
   - `/home/ing/RICK/N_RLC_rebuild`

2. Add the main `RICK` folder as a read‑only mining root so I can see the rebuild, the transfer zip, and handoff docs:
   - `/home/ing/RICK`

Once those roots are added, please tell me:

"N_RLC_rebuild and RICK are now in the workspace; continue."

After that, I will:

- Open and fully read `AGENT_HANDOFF_841921.md` and `MEGA_PROMPT_TRANSFER.md` from their real locations.
- Confirm that I am treating `/home/ing/RICK/N_RLC_rebuild` as the active project root.
- Confirm my understanding of PIN 841921, the charter, guardian gates, R:R ≥ 3.2, and read‑only mining rules.
- Then begin wiring the order router, autonomous controller, CLI, and position manager exactly as specified in those documents.
"""

This appendix must be preserved so that any agent who finds itself in the wrong root (e.g. only seeing `RICK_LIVE_CLEAN`) will ask the operator to add `N_RLC_rebuild` and the main `RICK` folder to the workspace before proceeding.

---

## SUPPORT FILES

Agents MUST be aware of and use these support files:

- `AGENT_HANDOFF_841921.md` – canonical handoff and governance details.
- `MEGA_PROMPT_TRANSFER.md` – transfer prompt and project state snapshot.
- `ADVANCED_ABILITIES_MANIFEST_841921.md` – operator‑facing catalog of advanced abilities and how to see them working.
- `DEV_ADDONS_841921.md` – developer/agent add‑ons focused on tonight readiness, safety, UX, and remote access expectations.

These files, together with this master prompt, describe how to take the existing RICK intelligence and rebuild it into a safe, fully autonomous, and operator‑friendly trading engine in this clean environment.