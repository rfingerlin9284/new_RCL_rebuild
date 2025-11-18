# Transfer Mega Prompt 841921 – new_RLC_rebuild

This file is for a **new agent** working on a copied version of this project (for example, in `N_RLC_rebuild`), after unpacking `zip_main_transfer.zip`. It summarizes what exists, what has been done up to now (from 6am to the latest session), and what still needs to be completed.

---

## 0. Identity and Safety (Must Remain Intact)

- PIN: **841921** (immutable – do not change).
- This project is a rebuild of the RICK clean live system with strict safety:
  - Charter in `foundation/rick_charter.py` defines hardcoded limits and rules.
  - Guardian gates in `hive/guardian_gates.py` (Margin, Positions, Correlation, Crypto) must all pass; any failure rejects a trade.
- All trades must be designed with **R:R ≥ 3.2:1**.
- Brokers for paper trading:
  - Allowed: **OANDA practice**, **IBKR paper**.
  - Not allowed: **Coinbase paper** (no sandbox keys in this implementation).

You must read and obey `AGENT_HANDOFF_841921.md` as the authoritative governance document. Do **not** weaken risk controls or modify PIN 841921.

---

## 1. What the Transfer Zip Contains

The archive `zip_main_transfer.zip` was created from `/home/ing/RICK/new_RLC_rebuild` and includes:

- All project code and configs under `new_RLC_rebuild`.
- All documentation (`*.md`, `*.txt`) and plans.
- No virtual environments or obvious build artifacts (venv, `__pycache__`, `.pyc`, logs, existing archive files).

Key top-level items you should see in the copied folder (e.g., `N_RLC_rebuild`):

- `AGENT_HANDOFF_841921.md` – main handoff and mega prompt.
- `AGENT_HANDOFF_841921_README.md`, `IMPLEMENTATION_GUIDE.md`, `PROJECT_STRUCTURE.md`, `MIGRATION_PLAN.md`, `INTEGRATION_PLAN_PHASE2.md`, `QUICK_START.md` – docs and plans.
- `foundation/` – charter, progress files, autonomous charter, margin/correlation gate, multi-timeframe utilities.
- `hive/` and `rick_hive/` – local AI logic, hive mind, browser connector, learning DB, guardian gates, quant/hedge rules, crypto entry gates.
- `execution/` – `order_router.py` for unified trade routing.
- `position_manager.py` – real-time position management.
- `orchestration/` – `autonomous_controller.py`, `hive_router.py`.
- `config/` – task configs, operator task config, narration logger, broker and environment configs, strategy configs.
- `ml_ai/`, `advanced/`, `strategies/`, `wolf_packs/` – ML, strategies, orchestrators, extracted Oanda logic.
- Shell helpers: `run_autonomous.sh`, `autonomous_launch.sh`, `migrate_from_live_clean.sh`, etc.
- Status markers: `FINAL_DELIVERY_841921.txt`, `SESSION_COMPLETE.md`, `OPTION_A_VERIFIED.txt`, `AGENT_HANDOFF_COMPLETE.txt`, `DOCUMENTATION_INTEGRATION_COMPLETE.txt`.

---

## 2. Work Completed So Far

From the 6am session through the latest work, the following is already implemented:

1. **Governance & roles**
   - `AGENT_HANDOFF_841921.md` defines:
     - Canonical root and alias expectations.
     - Safety rules (PIN, charter, gates, R:R, broker constraints).
     - External source mining rules (read-only legacy mining, when available).
     - Operator vs Agent responsibilities (operator supplies intent; agent implements directly; no “how-to” back to the operator as primary solution).

2. **Shared engine for autonomous and manual trades (skeleton in place)**
   - `position_manager.py` manages open positions, reevaluating them periodically and taking actions (TP/SL, trailing stops, partial exits, timeouts), with narration logging.
   - `execution/order_router.py`:
     - Defines `ManualTrade` and a `place_trade(pin, trade)` function.
     - Validates PIN via the charter.
     - Selects connector based on broker/mode.
     - Attempts to call several order methods on the connector.
     - Registers successful trades with the position manager.

3. **Autonomous controller wired to the engine (candidate generation stubbed)**
   - `orchestration/autonomous_controller.py`:
     - Provides `start_autonomous()` / `stop_autonomous()`.
     - Runs a loop that logs heartbeats and processes candidate trades.
     - For each candidate, applies guardian gates and calls `place_trade(pin=841921, trade=ManualTrade(...))`.
     - `_generate_candidates()` currently returns an empty list – this is deliberate and is to be filled in later.

4. **Manual-init trades through CLI**
   - `rick_cli.py` and config wiring support manual trade entry:
     - The operator can choose “Enter manual trade” from the menu.
     - CLI prompts for broker, symbol, direction, size, order type, etc.
     - Builds a `ManualTrade` and routes it via `place_trade(pin=841921, trade=manual_trade)`.
   - Once entered, manual trades are managed by the same position manager and narration engine as autonomous trades.

5. **Operator console (RICK OPERATOR CONSOLE 841921)**
   - `config/operator_task_config.json` provides a menu:
     - Start/stop autonomous trading mode.
     - Enter manual trade (Oanda/IBKR paper).
     - Run health check.
     - Tail narration log.
     - Switch active broker (placeholder behavior).
     - Show open positions summary.
     - Exit operator console.
   - `rick_cli.py` loads this config and maps menu choices to concrete methods that:
     - Control the autonomous controller.
     - Invoke manual trade entry.
     - Call `validate_system.run_health_check()`.
     - Tail `logs/narration.log`.
     - Query `position_manager` for summary.

6. **Health checks and narration integration**
   - `validate_system.py`:
     - Exposes `run_health_check()` returning a dict of checks (pin, imports, trade, narration, etc.).
     - Confirms PIN 841921 in `RickCharter`.
     - Smoke-imports key modules.
     - Performs a dry-run router call without hitting real brokers.
     - Confirms narration logging works.
   - `config/narration_logger.py`:
     - Writes narration events (trades, errors, health) to disk.
   - `rick_cli.py` includes an operator action that runs health checks and prints a readable summary.

7. **Documentation and planning artifacts**
   - Multiple `.md` and `.txt` files record:
     - Migration plans from prior live systems.
     - Implementation guides and integration phases.
     - Session completion markers and options.

---

## 3. Known Issues / Open Tasks (For the New Agent)

You should treat the following tasks as **open** and prioritize them:

1. **Broker execution alignment**
   - `execution/order_router.py` currently does not perfectly match the method signatures/arguments of the actual Oanda/IBKR connectors available in the environment.
   - Observed previously:
     - Oanda: `place_trade` imported a connector but reported `"No known execution method on connector"`.
     - Coinbase (disabled for paper) had an `unexpected keyword argument 'symbol'` error.
   - Your job:
     - Inspect the current broker connector modules (and any ported legacy code) to learn their real method signatures.
     - Update `order_router.py` so it calls the appropriate execution methods with correct argument shapes.
     - Ensure successful responses are correctly normalized and registered with `position_manager`.
     - Keep paper-only: Oanda practice and IBKR paper – no Coinbase paper.

2. **Implement autonomous candidate generation**
   - `_generate_candidates()` in `AutonomousController` is stubbed.
   - Your job:
     - Integrate it with available signal logic from modules under `hive/`, `rick_hive/`, `strategies/`, `ml_ai/`, `wolf_packs/`, etc.
     - Produce candidate trade specs including: broker, symbol, direction, quantity, entry price, stop-loss, take-profit.
     - Apply charter + gates + hedge/quant rules + R:R ≥ 3.2:1 **before** calling `place_trade`.

3. **End-to-end paper trade test from CLI**
   - Goal: A tiny paper trade (Oanda/IBKR) entered via `rick_cli.py` should:
     - Validate PIN and pass charter + gates.
     - Route through `order_router` and hit the correct broker connector.
     - Create a position in `position_manager`.
     - Generate clear narration entries in `logs/narration.log`.
   - Your job:
     - After aligning broker routing, run controlled tests.
     - Confirm failure modes are safe and clearly narrated.

4. **Autonomous mode behavioral validation**
   - Once `_generate_candidates()` is live and routing is correct:
     - Start autonomous mode from the operator console.
     - Confirm heartbeats and candidate evaluations are narrated.
     - Confirm real passing candidates become trades, positions, and narration entries.
     - Confirm manual trades can be entered and managed while autonomous mode is running.

5. **Legacy mining (if legacy code has been copied into this environment)**
   - If code from older RICK repos (R_H_UNI, RICK_LIVE_CLEAN, etc.) is present:
     - Locate proven working Oanda/IBKR/OCO logic.
     - Port/adapt that logic into the current connectors/router.
     - Keep original legacy copies read-only if they are treated as reference.
     - Add comments noting original paths for auditability.

6. **Environment-specific Git/Deployment**
   - In the original WSL environment, Git commit/push was blocked by GPG and lack of `gh`.
   - In this new location, ensure Git is configured correctly **if** remote pushes are needed.
   - This is environment-level work and not part of Python code; follow your platform’s best practices.

---

## 4. How to Use This Transfer in a New Folder (e.g., N_RLC_rebuild)

1. Unzip `zip_main_transfer.zip` so that you have a folder containing `new_RLC_rebuild` (or its contents copied into a new project folder such as `N_RLC_rebuild`).
2. Open that folder in your environment (VS Code, Codespace, etc.) as the workspace root.
3. Ensure `AGENT_HANDOFF_841921.md` is present at the root and read it fully.
4. As the new agent, treat this `MEGA_PROMPT_TRANSFER.md` as your **session summary** and to-do list:
   - Respect PIN, charter, and gates.
   - Build on the existing autonomous/manual architecture.
   - Fix broker routing.
   - Implement candidate generation.
   - Validate end-to-end behavior and narration.

Throughout, remember the operator vs agent responsibilities:

- The operator provides intent and approvals; you implement changes using your tools.
- Do not rely on the operator to perform manual coding or shell steps as your primary mechanism for change.
- When blocked by environment limits (e.g., missing folders, no Git auth), state clearly what you need, but keep implementation on your side.

**End of Transfer Mega Prompt 841921.**
