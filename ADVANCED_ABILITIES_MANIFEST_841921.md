# Advanced Abilities Manifest – RICK (PIN 841921)

This manifest is the SINGLE source of truth for all advanced abilities and features wired into the RICK system under PIN 841921.

It is written for a non‑coding operator. Every entry MUST connect code to concrete, visible behavior.

---

## 1. How to use this file (operator)

- You do NOT need to read code.
- Each section below describes a "cluster" of abilities (gates, wolf packs, hedge logic, crypto gates, portfolio optimizer, swarm, etc.).
- For each cluster you will see:
  - What it is called.
  - Where it lives in the code (file paths).
  - What it DOES in real life (what you would see when trading).
  - How to see it working (CLI options, logs, dashboards).

When this file is filled in by an agent, you can:
- Decide which abilities you want enabled or disabled.
- Verify that they are actually working by following the "How to see it" bullets.

---

## 2. Global safety & charter enforcement

**Cluster name:** Charter & Global Safety

- **Core rules:** PIN 841921, min notional $15,000, min R:R 3.2:1, max 3 positions, margin ≤ 35%, daily loss breaker, allowed timeframes, max latency, etc.
- **Primary files:**
  - `foundation/rick_charter.py`
  - Any `autonomous_charter` or extended charter module
  - `hive/guardian_gates.py`
  - `hive/quant_hedge_rules.py`

**What this enforces (behavior):**
- No trade may bypass the PIN 841921 charter.
- No trade may violate min R:R 3.2:1, margin ≤ 35%, or max positions.
- Daily loss breaker and other global breakers are active when configured.

**How to see this working (no code):**
- From `rick_cli.py`, place a deliberate "bad" test trade (too low R:R or too many positions if a test harness exists).
- Watch narration/logs for events like `CHARTER_REJECTED`, `GATE_FAILED_MARGIN`, `MAX_POSITIONS_BLOCKED`, etc.
- Confirm that the trade is rejected and not sent to the broker.

> TODO (agent): Fill in concrete log event names and exact CLI menu paths once wired.

---

## 3. Guardian gates & crypto entry gates

**Cluster name:** Guardian Gates & Crypto Entry

- **Primary files:**
  - `hive/guardian_gates.py`
  - `foundation/margin_correlation_gate.py`
  - `hive/crypto_entry_gate_system.py`

**What this enforces (behavior):**
- Margin gate: blocks trades when margin usage would exceed configured threshold (e.g., 35%).
- Positions gate: blocks trades that would violate max concurrent positions (e.g., >3).
- Correlation gate: blocks same‑side USD or overly correlated exposure.
- Crypto gate: allows crypto trades only when hive consensus, volatility, and time filters pass (e.g., ≥ 90% consensus).

**How to see this working (no code):**
- Use CLI or test harness to:
  - Attempt a trade that would push margin too high.
  - Attempt to open more than the allowed number of positions.
  - Attempt a correlated trade (e.g., multiple same‑side USD pairs).
- Watch narration/logs for:
  - `GATE_FAILED_MARGIN`, `GATE_FAILED_POSITIONS`, `GATE_FAILED_CORRELATION`, `CRYPTO_GATE_REJECTED` (or similar).
- Confirm rejected trades never reach the broker and are clearly narrated.

> TODO (agent): Document exact thresholds, log event names, and any configuration knobs.

---

## 4. Regime detector & wolf packs

**Cluster name:** Regime & Wolf Packs

- **Primary files:**
  - `logic/regime_detector.py`
  - `wolf_packs/orchestrator.py`
  - `wolf_packs/` strategy modules

**What this does (behavior):**
- Detects current market regime (bull, bear, sideways, triage/crash).
- Selects an appropriate "wolf pack" (strategy bundle) based on regime.
- Applies regime‑dependent multipliers to risk and aggressiveness.

**How to see this working (no code):**
- Start autonomous mode.
- Watch logs for events like `REGIME_CHANGED`, `PACK_ROUTED_BULLISH`, `PACK_ROUTED_TRIAGE`.
- Confirm that:
  - In TRIAGE / conservative regimes, position size and frequency are reduced.
  - In strong bullish/bearish regimes, position sizes align with configured multipliers.

> TODO (agent): List all wolf pack names, regimes, and their multipliers; document how to toggle or disable a pack if needed.

---

## 5. Quant hedge rules & portfolio optimizer

**Cluster name:** Hedging & Portfolio Optimization

- **Primary files:**
  - `hive/quant_hedge_rules.py`
  - `logic/portfolio_optimizer.py` (or equivalent)
  - Any `risk/dynamic_sizing.py` or correlation monitor utilities

**What this does (behavior):**
- Monitors volatility, correlation, win‑rate, loss streaks, and notional exposure.
- Recommends or executes hedging: FULL_LONG, REDUCE_EXPOSURE, CLOSE_ALL, HEDGE_SHORT, PAUSE, etc.
- Adjusts exposure across symbols to keep portfolio within defined risk limits.

**How to see this working (no code):**
- During autonomous trading:
  - Observe narration for `HEDGE_ON`, `HEDGE_OFF`, `REDUCE_EXPOSURE`, `CLOSE_ALL`, `PORTFOLIO_OPTIMIZER_REBALANCED`.
  - Check that when volatility spikes or loss streaks occur, exposure is reduced or hedges are opened.

> TODO (agent): Document thresholds for each hedge mode and show one or two example scenarios.

---

## 6. Broker connectors & OCO / latency protections

**Cluster name:** Broker Execution & Protections

- **Primary files:**
  - `brokers/oanda_connector.py`
  - Any enhanced OANDA connector in `data/brokers/`
  - Any Coinbase or IBKR connector modules (paper mode only as allowed by charter)

**What this does (behavior):**
- Sends orders to allowed paper brokers (OANDA practice, IBKR paper).
- Uses OCO (One‑Cancels‑Other) where supported.
- Enforces max placement latency and retries; logs errors with clear messages.

**How to see this working (no code):**
- Place a small paper trade via CLI.
- Confirm:
  - Order reaches broker.
  - OCO behavior is visible (linked TP/SL).
  - Logs include latency measurements and any error details.

> TODO (agent): Fill in details for each broker, including any unsupported capabilities that are clearly disabled.

---

## 7. Autonomous execution loop & manual integration

**Cluster name:** Autonomous Loop & Manual Trades

- **Primary files:**
  - `aggressive_money_machine.py` or main autonomous orchestrator
  - `orchestration/autonomous_controller.py`
  - `position_manager.py`
  - `rick_cli.py`

**What this does (behavior):**
- Runs the 60‑second (or configured) autonomous cycle: data → regime → hedge → gates → sizing → OCO → monitor → narrate.
- Allows manual trades entered from the CLI to be treated identically to autonomous trades AFTER entry (same gates, hedges, trailing, and logs).

**How to see this working (no code):**
- Start autonomous mode from CLI.
- Observe heartbeats (`AUTONOMOUS_HEARTBEAT` or similar) and candidate evaluations.
- Enter a manual trade and confirm it appears in `position_manager`, gets trailed/hedged according to the same rules, and is narrated.

> TODO (agent): Document menu options, log event names, and any emergency stop or override commands.

---

## 8. Narration, dashboards, and operator visibility

**Cluster name:** Narration & Operator Interfaces

- **Primary files:**
  - `util/narration_logger.py` or `config/narration_logger.py`
  - `dashboard/app.py` (if present)
  - Any status/summary scripts

**What this does (behavior):**
- Writes plain‑English logs of every important decision, gate result, trade, hedge, and error.
- Provides a dashboard or CLI summaries so you can monitor without reading code.

**How to see this working (no code):**
- Tail the narration log.
- Open the dashboard app (if present) and confirm metrics/positions update live.

> TODO (agent): Provide exact commands/URLs/ports and example log lines.

---

## 9. Connection loss detection & alerts

**Cluster name:** Connectivity & Alerts

- **Primary files:**
  - Any heartbeat/monitor modules
  - Broker connector timeout handling

**What this does (behavior):**
- Detects when broker/API connections drop or become unstable.
- Logs alerts and, if implemented, pauses autonomous trading until safe.

**How to see this working (no code):**
- Simulate or detect a connection loss (e.g., by network interruption during testing).
- Confirm logs show clear alerts and that autonomous mode behaves safely (no blind firing of orders).

> TODO (agent): Specify exact behavior on loss (pause, retry schedule, alert format).

---

## 10. Additional clusters / 130+ abilities coverage

Agents MUST add new sections here as they discover and wire additional advanced abilities (swarm, ML models, hive buses, installer patches, etc.). Each new section MUST follow the same pattern:

- Cluster name.
- Primary files.
- What it does (behavior).
- How to see it working (no code).

The goal is that, when this file is complete, it covers all ~130+ advanced abilities in a way that a non‑coder operator can understand and verify.

---

## Narration & Heartbeat (Wired Events)

This section documents the plain-English narration events and heartbeat messages now emitted by the system so an operator can confidently monitor the autonomous "conversation".

- **Heartbeat event**: `AUTONOMOUS_HEARTBEAT`
  - **Where**: `orchestration/autonomous_controller.py` (every loop)
  - **What you see**: A single-line heartbeat like:
    - `SYSTEM_HEARTBEAT: mode=paper_practice, autonomous=True, brokers=['oanda'], Coinbase=DISABLED per charter, open_positions=0`
  - **How to see it**: Tail `logs/narration.log` or use the CLI `VIEW NARRATION LOG` menu.

- **Charter rejection (autonomous)**: `AUTONOMOUS_CHARTER_REJECT`
  - **When**: Candidate failing the shared charter pre-check (min notional / R:R) prior to gate evaluation.
  - **What you see**: A line with the symbol and human reasons, e.g. `R:R 2.50:1 below minimum 3.20:1`.

- **Guardian gate pass/fail**: `AUTONOMOUS_GATE_PASS` / `AUTONOMOUS_GATE_REJECT`
  - **When**: After charter checks, gates either accept or reject the candidate.
  - **What you see**: For pass — `Candidate passed guardian gates`; for reject — specific gate reason like `MARGIN_EXCEEDED`.

- **Autonomous trade events**: `AUTONOMOUS_TRADE_PLACED` / `AUTONOMOUS_TRADE_FAILED`
  - **What you see**: Success/failure of routing through the unified `place_trade` pipeline.

- **Manual trade narration keys** (already wired):
  - `CHARTER_REJECTED_MANUAL_PRECHECK` — pre-approval warning in the manual plan
  - `CHARTER_REJECTED_MANUAL_EXECUTION` — post-approval execution block if charter disallows
  - `MANUAL_TRADE_ROUTING` — when a user-approved manual trade is routed to the broker
  - `MANUAL_TRADE_EXECUTION_FAILED` / `narrate_trade_executed` — final execution outcome

How to verify quickly:
- Start the CLI: `python3 rick_cli.py`
- Start autonomous mode via the menu.
- Tail the narration log:
```bash
tail -f logs/narration.log
```
- You will see `AUTONOMOUS_HEARTBEAT` lines every minute and short English narration for candidate/regime/gate/trade events.
