# Agent Handoff 841921 – RICK Project

This file exists to hand off control to a future coding agent working directly in the canonical project root.

## Canonical Root and Aliases

- Canonical project directory: `/home/ing/RICK/new_RLC_rebuild`
- Symlink alias for tools and scripts: `/home/ing/RICK/RICK_ACTIVE` → `/home/ing/RICK/new_RLC_rebuild`
- Another alias: `/home/ing/RICK/current` → `/home/ing/RICK/new_RLC_rebuild`

The actual code lives under `new_RLC_rebuild`. `RICK_ACTIVE` and `current` are convenience links only.

## Safety and Governance

- PIN: **841921** (immutable – must never be changed).
- Charter (`foundation/rick_charter.py`):
  - All limits and risk rules are hardcoded constants.
  - All charter rules must remain fully enforced.
- Guardian gates (`hive/guardian_gates.py`):
  - 4 gates (Margin, Positions, Correlation, Crypto) with AND logic.
  - If any gate fails, the trade must be rejected.
- Risk / reward:
  - All trades must be designed with **R:R ≥ 3.2:1**.
- Brokers (paper mode):
  - Allowed: **OANDA practice**, **IBKR paper**.
  - Not allowed: **Coinbase paper** in this implementation (no sandbox keys).
- Structural safety:
  - Do **not** weaken any risk controls.
  - Prefer editing existing files for integration.
  - Only create minimal new orchestration/config files when strictly necessary and non-redundant.
  - Do **not** rename or move existing files/folders.

## What the Next Agent Should Do

When a new VS Code agent session is started, the workspace must be opened directly on:

- `/home/ing/RICK/new_RLC_rebuild`

Once that folder is the workspace root, the user will hand the agent the mega prompt (below) and grant approval.

### Mega Prompt to Give the Future Agent

Copy-paste the following text into the agent after opening the `new_RLC_rebuild` folder as the VS Code workspace root:

---

**MEGA PROMPT FOR VS CODE AGENT (RICK_ACTIVE / new_RLC_rebuild IMPLEMENTATION)**

You are the coding agent for my live project at `/home/ing/RICK/new_RLC_rebuild` (also symlinked as `RICK_ACTIVE`). Your job is to implement and wire up everything described below into this specific version of the system, while preserving all safety and governance rules.

The user has explicitly approved structural and integration work with the token **"approved 841921"**, under the following constraints:

- No renaming or moving existing files or folders.
- Prefer integrating by adding to existing files whenever possible and practical.
- Only create new files when strictly necessary, non-redundant, and clearly focused on orchestration/integration.
- Do **not** weaken risk controls, and keep PIN 841921 and all charter/gate rules intact.

### 0. Hard Requirements (Never Break These)

PIN: 841921, immutable.

Charter (RickCharter):
- All constants hardcoded; no runtime editing.
- All charter rules must remain enforced.

Guardian gates:
- 4 gates (Margin, Positions, Correlation, Crypto) with AND logic.
- If any gate fails, trade is rejected.

Risk / R:R:
- All new trades must be designed with reward:risk ≥ 3.2:1.

Brokers for paper trading:
- OANDA practice and IBKR paper only.
- Coinbase must not be used for paper in this implementation (no sandbox keys).

Do not weaken these. Any new feature must respect them.

### 1. Two Trading Modes (Shared Engine After Entry)

Implement two modes of operation that share the same risk engine, gates, position manager and narration:

#### Autonomous mode (closed loop)

System scans for trades and executes them without human input, subject to charter/gates.

Behavior:
- A loop (timer/async/thread) periodically:
  - Runs the existing signal/logic pipeline (hive, hedge rules, regime detector, etc.).
  - Generates candidate trades with:
    - broker in {oanda, ibkr} (paper).
    - symbol, direction, size, TP, SL.
  - Applies:
    - Charter rules,
    - 4 guardian gates,
    - Quant/hedge rules,
    - R:R ≥ 3.2:1 check.
- For each candidate that passes:
  - Calls `place_trade(pin=841921, trade=ManualTrade(...))`.
- Position manager + narration logger:
  - Manage all open trades: TP/SL, trailing stops, partial exits, timeouts.
  - Log all actions.

Implementation note:
- Prefer adding an autonomous controller in an existing orchestration module or, if necessary, a new `orchestration/autonomous_controller.py` file that:
  - Exposes `start_autonomous()`, `stop_autonomous()`, `autonomous_loop()`.
  - Reuses `execution/order_router.py` and `position_manager.py`.

#### Manual-init mode (operator starts a trade)

Human approves an idea once; then the bot manages it fully.

Behavior:
- CLI menu item "Enter manual trade":
  - Prompts for:
    - broker (oanda/ibkr),
    - symbol,
    - direction (buy/sell),
    - quantity,
    - order_type (market/limit).
  - Constructs a `ManualTrade` (or equivalent) object.
  - Calls `place_trade(pin=841921, trade=manual_trade)`.
- After that, the trade is indistinguishable from an autonomous trade:
  - Same position manager,
  - Same TP/SL logic,
  - Same trailing/partial exit rules,
  - Same narration.
- Manual trades must:
  - Pass through charter + gates.
  - Respect R:R design rules.

Autonomous and manual-init trades must share one unified lifecycle engine; only the entry trigger differs.

### 2. Rick as Single Front-Door to the Hive (Design Interface)

We’re not wiring external APIs in this pass, but we must design the interface so future work can plug them in.

Create an internal abstraction (e.g. `orchestration/hive_router.py`) with something like:

```python
def get_best_trade_from_hive(request_text: str) -> dict | None:
    """Given a natural language request, call out to multiple AIs (GPT, Grok, etc.),
    collect trade suggestions, apply charter + gates + R:R constraints,
    and return one best trade spec or None.
    """
    ...
```

Rick (local decision layer) will:
- Receive a single text prompt from the user (or from autonomous mode).
- Use `get_best_trade_from_hive` internally in future.
- For now, this can be a stub or a simple local implementation, but the interface must exist.

From the operator’s perspective:
- They talk only to Rick.
- Rick will eventually call GPT/Grok/etc. via this router behind the scenes.

### 3. Always-On Narration + Health Checks

Narration logger:
- Ensure `config/narration_logger.py` exposes a function like:

```python
def log_event(event_type: str, message: str, **context) -> None:
    ...
```

- Call it from:
  - Autonomous controller (start, stop, trade candidates, gate rejections),
  - Manual trade entry wrapper (success/failure, details),
  - Position manager (entries, exits, stop moves, partials, timeouts),
  - Health checker (HEALTH_OK, HEALTH_WARN, HEALTH_ERROR).
- Output: `logs/narration.log` (or `.jsonl`) in human-readable form.

Health checks:
- Refactor `validate_system.py` (or add a small wrapper) so you can call:

```python
def run_health_check() -> dict:
    """Returns a dict with keys like: 'pin', 'imports', 'router', 'trade', 'narration'.
    Each has { 'ok': bool, 'detail': str }.
    Also logs a summary into narration.
    """
```

- Health check should at minimum:
  - Verify PIN 841921 in `RickCharter`.
  - Smoke-import key modules: charter, gates, connectors, position manager, narration logger, router.
  - Optionally do a dry-run `ManualTrade` through the router without hitting brokers.

Integrate health check in two ways:
- CLI menu item (run on demand).
- Autonomous loop periodic call (e.g. every N iterations).

### 4. Operator Console (CLI Menu + Task Config)

Create a simple task config file and use it to drive an interactive operator menu (if new file creation is allowed). Example: `config/operator_task_config.json`:

```json
{
  "menu_title": "RICK OPERATOR CONSOLE 841921",
  "items": [
    { "id": 1, "label": "Start AUTONOMOUS trading mode", "action": "start_autonomous" },
    { "id": 2, "label": "Pause AUTONOMOUS trading mode", "action": "stop_autonomous" },
    { "id": 3, "label": "Enter MANUAL trade (Oanda/IBKR paper)", "action": "manual_trade_entry" },
    { "id": 4, "label": "Run HEALTH CHECK (PIN + imports + router)", "action": "run_health_check" },
    { "id": 5, "label": "Tail NARRATION log (live view)", "action": "tail_narration" },
    { "id": 6, "label": "Switch ACTIVE BROKER (Oanda / IBKR)", "action": "switch_broker" },
    { "id": 7, "label": "Show OPEN POSITIONS summary", "action": "show_positions" },
    { "id": 8, "label": "Exit OPERATOR console", "action": "exit_console" }
  ]
}
```

Update `rick_cli.py`:
- On startup, read `config/operator_task_config.json`.
- Render the operator menu and map each `action` to a function that:
  - `start_autonomous()` → autonomous controller.
  - `stop_autonomous()` → stop opening new auto trades.
  - `manual_trade_entry()` → prompt user and call `place_trade(pin=841921, ...)`.
  - `run_health_check()` → call the health function and print summary.
  - `tail_narration()` → show latest events from `logs/narration.log`.
  - `switch_broker()` → update a simple config value (e.g. in `AUTONOMOUS_CONFIG.json` or a runtime config).
  - `show_positions()` → call into position manager summary.

The operator must be able to use the system by:

```bash
cd /home/ing/RICK/new_RLC_rebuild
python3 rick_cli.py
```

…and only pressing numbers + answering simple questions.

### 5. Manual vs Autonomous Coexistence

Ensure that:
- Autonomous loop can be running continuously.
- Manual trades can be entered on demand via the CLI without disrupting:
  - The loop,
  - Existing trades,
  - Health checks.

Implementation detail:
- Manual trades become just another entry in whatever structure the position manager uses (e.g. “open positions” list).
- The position manager doesn’t care if a trade was:
  - Created by autonomous scanner, or
  - Created by manual operator; it treats both the same.

### 6. Constraints and Testing

After changes, verify:

```bash
python3 validate_system.py

python3 -c "from foundation.rick_charter import RickCharter; assert RickCharter.PIN == 841921; print('PIN OK')"
```

- A small manual Oanda/IBKR paper test through the CLI:
  - Use very small size.
  - See that:
    - Trade is accepted or rejected with clear reason.
    - Narration logs entry / gate failure.

- Autonomous mode:
  - Can be started/stopped from the CLI.
  - Logs activity in narration.
  - No Coinbase trading path is used for paper until explicitly re-enabled and configured.

### 7. Style and Safety

- Reuse existing modules whenever possible; don’t duplicate charter/gate logic.
- Keep changes minimal and focused on:
  - Mode control,
  - Operator console,
  - Narration + health integration,
  - Clear Rick→Hive router interface.
- Do not change PIN or weaken any risk controls.

Use this prompt as your direct instruction set. Your task is to implement these behaviors into the current `/home/ing/RICK/new_RLC_rebuild` codebase, using the existing architecture (charter, gates, position manager, narration logger, CLI) and verifying the system remains safe, PIN-enforced, and ready for Oanda/IBKR paper trading.

---

## How to Use This File

- Keep this file in the root alongside the existing project docs.
- When starting a new agent session, open the folder `/home/ing/RICK/new_RLC_rebuild` as the VS Code workspace root.
- Then send the Mega Prompt above to the agent to resume and complete the integration.
