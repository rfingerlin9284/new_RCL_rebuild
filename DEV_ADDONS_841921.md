# DEV ADD‑ONS – RICK (PIN 841921)

This file is for **developers/agents only**. It collects imperative suggestions and add‑ons that are important for getting the system safely trading (paper) as quickly as possible, while respecting all charter constraints.

Operator assumption: does **not** code; interacts via CLI and dashboards only.

---

## 1. Tonight readiness – minimal safe path

When preparing the system to trade **today**, prioritize the following in THIS project root:

1. **Health check must be green**
   - Ensure `validate_system.py` (or equivalent) exists and covers:
     - Charter & PIN validation.
     - Imports and configuration sanity.
     - Broker credentials presence (but NOT live keys).
     - Logging/narration path writeability.
   - If any checks are missing, implement them with clear, plain‑English error messages.

2. **Broker paper path must be end‑to‑end**
   - OANDA PRACTICE must be fully wired:
     - From `rick_cli.py` → `execution/order_router.py` → `brokers/oanda_connector.py` → OANDA practice.
   - IBKR paper support may be present but must NOT block OANDA if unfinished.
   - Coinbase paper remains disabled per charter.

3. **CLI must offer a simple “start paper trading now” flow**
   - Add/confirm a menu option like: `Start autonomous paper trading (OANDA practice)`.
   - The option should:
     - Run a quick health check.
     - Confirm broker connectivity.
     - Start the autonomous loop.
     - Print what it’s doing in plain English.

4. **Narration/logs must clearly show what is happening**
   - Ensure every trade attempt, gate decision, hedge action, and error is logged.
   - Use consistent, searchable tags (e.g., `GATE_FAILED_MARGIN`, `HEDGE_ON`, `AUTO_TRADE_PLACED`).

5. **Emergency stop must be obvious**
   - Provide a clearly documented way to stop autonomous mode (e.g., CLI option or keyboard interrupt handler with safe shutdown).
   - Log an event like `EMERGENCY_STOP_REQUESTED` so it is auditable.

---

## 2. Non‑negotiable safety add‑ons

These add‑ons MUST be present before scaling up size, even in paper:

1. **Daily loss breaker implementation**
   - Track realized P&L and unrealized drawdown per session/day.
   - When loss exceeds configured limit (from charter), block new trades and optionally close risk.

2. **Max exposure guard**
   - Enforce caps on total notional exposure and per‑symbol exposure.
   - Combine with correlation checks to avoid concentrated risk in a single currency/sector.

3. **Time‑of‑day / session filters (optional but recommended)**
   - Allow disabling trading during low‑liquidity hours or news windows.
   - Expose simple config toggles rather than code edits.

4. **Config snapshotting**
   - On startup and before changing any risk setting, write a config snapshot (JSON or similar) to disk.
   - This allows audit of “what settings were active when this trade was taken.”

---

## 3. Operator experience add‑ons (no‑code UX)

To make the system usable for a non‑coder operator:

1. **Plain‑English CLI summaries**
   - Add a CLI command/menu: `Show current safety & mode summary` that prints:
     - Current regime.
     - Active wolf pack.
     - Margin usage.
     - Open positions count.
     - Current risk per trade.
     - Whether autonomous mode is ON or OFF.

2. **Quick status dashboard**
   - If `dashboard/app.py` exists (Streamlit or similar), ensure:
     - It can be launched with one command.
     - It displays live positions, P&L, regime, gates status, and recent events.

3. **Simple toggle switches (config‑level)**
   - Provide config flags (not code edits) for:
     - Enable/disable micro‑trading or high‑frequency modes.
     - Enable/disable crypto trading.
     - Aggressiveness level (e.g., CONSERVATIVE, NORMAL, AGGRESSIVE) mapped to underlying risk parameters.

---

## 4. Remote access expectations (minimal viable approach)

The operator wants to monitor/control the system from a phone or another desktop with **no coding**.

Suggested minimal viable path:

1. **Dashboard over HTTP**
   - Run the dashboard on a configurable port, bound to localhost by default.
   - Allow tunneling via a secure method (e.g., SSH tunnel or a trusted remote desktop solution) – document steps in `README_REMOTE_ACCESS.md`.

2. **CLI from remote terminal (optional)**
   - Document how to SSH into the box and run `rick_cli.py` from a terminal app, if the operator is comfortable with that.

Agents MUST NOT implement insecure "open to the internet" endpoints without authentication.

---

## 5. Integration discipline for new features

When adding any new "fancy" capability (ML, new wolf packs, new hedges, etc.):

1. **Never weaken charter or guardian gates**
   - New features may provide signals or advisories but must not override:
     - PIN 841921.
     - R:R ≥ 3.2.
     - Margin/positions/correlation/crypto gates.

2. **Log before you leap**
   - Every new automatic behavior must log:
     - Why it triggered.
     - What it did (e.g., hedged, reduced, paused).
     - Which inputs it used (regime, volatility, correlation, etc.).

3. **Start in advisory mode**
   - Default new ML/AI features to "advisory" only (log recommendations, do not execute) until explicitly promoted to "active" in config.

---

## 6. To‑do markers for agents

Agents working in this project should:

- Update this file as you implement the items above.
- Mark sections as `DONE`, `PARTIAL`, or `TODO` with dates and brief notes.
- Keep language non‑technical where possible, so the operator can read it.

This file is NOT a replacement for tests or health checks; it is a focused list of critical add‑ons and UX improvements to make the system safely usable and ready to trade.
