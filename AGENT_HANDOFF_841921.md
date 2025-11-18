# Agent Handoff 841921 – RICK Project (N_RLC_rebuild)

This file exists to hand off control to a future coding agent working directly in the canonical project root **and**, when approved, mining legacy code outside it in a safe, read‑only way.

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

---

## Canonical Root and Aliases

- Canonical project directory (historical):  
  `/home/ing/RICK/new_RLC_rebuild`

- Current VS Code project root for **WRITES** in this environment (this clean clone):  
  `/home/ing/RICK/N_RLC_rebuild`

- Symlink alias for tools and scripts (may point to either the historical root or this clone):  
  `/home/ing/RICK/RICK_ACTIVE`

- Another alias (may point to either):  
  `/home/ing/RICK/current`

All new implementation and integration work for this agent session belongs inside `/home/ing/RICK/N_RLC_rebuild`.  
Other folders under `/home/ing/RICK` are **reference / legacy sources**, not the active target of edits.

If you cannot see one of the paths above in your tools, you must ask the operator to add that folder to the current VS Code workspace (multi‑root) rather than assuming it is unavailable.

---

## Safety and Governance (Immutable Core)

- PIN: **841921** (immutable – must never be changed).

- Charter (`foundation/rick_charter.py`):
  - All limits and risk rules are hardcoded constants.
  - All charter rules must remain fully enforced.
  - This includes: min notional, max margin, max concurrent positions, allowed timeframes, max hold duration, spread/SL/ATR rules, daily loss breakers, etc.

- Guardian gates (`hive/guardian_gates.py`):
  - 4 gates (Margin, Positions, Correlation, Crypto) with AND logic.
  - If **any** gate fails, the trade must be rejected.

- Risk / reward:
  - All trades must be designed with **R:R ≥ 3.2:1**.

- Brokers (paper mode only in this build):
  - Allowed: **OANDA practice**, **IBKR paper**.
  - Not allowed: **Coinbase paper** (no sandbox keys in this implementation).

- Structural safety:
  - **Do not** weaken any risk controls.
  - Prefer editing existing files for integration.
  - Only create minimal new orchestration/config files when strictly necessary and non‑redundant.
  - **Do not** rename or move existing files/folders in `/home/ing/RICK/N_RLC_rebuild` without explicit operator approval.
  - **Do not** rename or move files/folders in any external mining source.

These are non‑negotiable.

---

## External Source Access & Legacy + GitHub Mining (Immutable Rule)

The operator has explicitly authorized PIN‑gated **read‑only** access to other RICK folders and GitHub/remote sources for the purpose of **analysis, comparison, and safe code reuse**.

Once the operator says:  
`approved 841921`  

you must:

1. **Treat `/home/ing/RICK/N_RLC_rebuild` as the ONLY write target for this VS Code agent**
   - All edits, new modules, refactors, and integrations happen **inside** `/home/ing/RICK/N_RLC_rebuild`.
   - External folders (including `/home/ing/RICK/new_RLC_rebuild`, `/home/ing/RICK/RICK_LIVE_CLEAN`, `/home/ing/RICK/R_H_UNI`, etc.) are **read‑only**; you may not modify, delete, or rename files outside this project root.

2. **You ARE allowed (and encouraged) to mine legacy and remote sources**, for example:
   - `/home/ing/RICK/R_H_UNI`
   - `/home/ing/RICK/RICK_LIVE_CLEAN`
   - `/home/ing/RICK/RICK_LIVE_PROTOTYPE`
   - `/home/ing/RICK/RICK_LIVE_PROTOTYPE_BACKUP`
   - `/home/ing/RICK/Dev_unibot_v001`
   - Any other historical RICK repos or modules under `/home/ing/RICK`
   - Any GitHub/remote repos or zips under `/home/ing/github_sources/` or similar paths the operator provides

   **Purposes allowed:**
   - Understanding previous working implementations (brokers, OCO logic, ML, dashboards, etc.).
   - Copying / adapting snippets and patterns into new modules inside `/home/ing/RICK/N_RLC_rebuild`.
   - Diffing behavior between old and new code paths.
   - Verifying assumptions about how RICK used to work.

3. **You must not change external sources**
   - No edits to files outside `/home/ing/RICK/N_RLC_rebuild`.
   - No renames, deletes, or moves of external files/folders.
   - If you need a modified version of external code, copy it into `/home/ing/RICK/N_RLC_rebuild` and work there.
   - You must not rename or relabel any external file or folder under `/home/ing/RICK`.

3b. **Renames / relabels inside the project root (operator approval required)**
   - Even inside `/home/ing/RICK/N_RLC_rebuild`, you must NOT rename or relabel any file or folder without explicit operator approval.
   - Before any rename/move, you MUST clearly announce your intent in ALL CAPS (for example: `INTENT: RENAME FILE X TO Y`) and wait for the operator to approve it with `"APPROVE 841921"`.

4. **Workspace / tooling constraint (very important)**
   - If your tools cannot currently see those external folders because the VS Code workspace is restricted:
     - **Do NOT assume access is impossible.**
     - **Ask the operator** to:
       - Add the relevant folders (`/home/ing/RICK/...`) to the current VS Code workspace (multi‑root), **or**
       - Copy specific external files into this workspace so you can inspect them.
   - Once those folders are part of the workspace, you may read them in full, but still treat them as read‑only per the rules above.

5. **Documentation of external reuse**
   - When you copy or adapt external code, clearly note in comments:
     - Original path and file (e.g.,  
       `# Derived from /home/ing/RICK/R_H_UNI/old_oanda/bridge.py`)
     - Any material changes you made.
   - This creates a clean audit trail between legacy implementations and the new rebuild.

This section is the answer to previous agents who said:  
“**I can’t see outside the workspace root**.”  
The intent is: **once the operator expands the workspace, you are expected to mine those folders aggressively, but only as read‑only references.**

---

## Mega Prompt Linkage

This handoff file is a supporting document. The **primary active‑session instructions** live in:

- `MASTER_RICK_PROMPT_841921.md` (master handoff for N_RLC_rebuild)
- `MEGA_PROMPT_TRANSFER.md` (transfer snapshot and task list)

Agents must:

1. Read this file to understand roots, aliases, mining rules, and immutable governance.
2. Then treat `MASTER_RICK_PROMPT_841921.md` as the authoritative prompt for actual work in this environment.

---

## What the Next Agent Should Do (High Level)

When a new VS Code agent session is started with this clean clone:

1. Ensure the VS Code workspace includes at least:
   - `/home/ing/RICK/N_RLC_rebuild` (this clone, writeable)
   - Optionally, for mining:
     - `/home/ing/RICK/RICK_LIVE_CLEAN`
     - `/home/ing/RICK/new_RLC_rebuild`
     - `/home/ing/RICK/R_H_UNI`
     - Other `/home/ing/RICK/...` folders and any `/home/ing/github_sources/...` repos

2. Open the workspace in VS Code.

3. Start the coding agent and give it:
   - `MASTER_RICK_PROMPT_841921.md`
   - `MEGA_PROMPT_TRANSFER.md`
   - The PIN approval: `approved 841921`

4. Let it:
   - Mine external legacy and remote repos as read‑only references.
   - Port and integrate necessary logic into `/home/ing/RICK/N_RLC_rebuild`.
   - Keep all charter/gate/risk rules intact.

---

## Operator vs Agent Responsibilities (Immutably Enforced)

This section defines how the human operator and any coding agent must behave. It is **part of the safety contract** and must be treated as immutable alongside the PIN and charter.

- **Operator role (human):**
  - Provides intent, goals, constraints, approvals, and ideas.
  - Decides when to start/stop agents and when to accept/reject changes.
  - Does **not** have to run commands, edit code, or follow “how‑to” instructions from the agent.

- **Agent role (VS Code / Copilot / automated):**
  - Analyzes the existing codebase, configuration, and logs.
  - Designs and implements changes **directly in the workspace**, within the constraints of this document and the master prompt.
  - Proposes and applies file edits, refactors, and orchestration changes itself, instead of telling the operator what to type.

- **Explicit prohibition for agents:**
  - Agents must **not** respond with instructions that tell the operator to manually edit code, create files, or run shell commands as the primary way to implement a requested change.
  - When a change is requested and allowed by these rules, the agent must:
    - Use its available tools (file edits, tasks, terminals, etc.) to perform the change directly, or
    - Explain briefly why it is technically blocked (e.g. workspace does not include a needed folder), and then request the operator to adjust the workspace or provide missing files.
  - “How‑to” command snippets or suggestions are allowed **only** as optional context when the agent cannot execute them itself due to hard tool limitations, and must be clearly framed as such.

- **Immutable intent:**
  - The operator is the overseer and source of intent.
  - The agent is the implementer and must carry out work autonomously inside the allowed workspace, instead of delegating work back to the operator via step‑by‑step coding or shell instructions.

Any future agent loading this repository must respect this division of responsibilities under PIN **841921** and treat it as part of the non‑negotiable governance for this project.

---

## Environment & Clone Addendum (Applies to RICK_MAIN and Clean Clones)

This addendum binds **all** future environments that host this project or any clean clone of it (for example, `N_RLC_rebuild`) to the same safety and mining rules, while explicitly rejecting the limitations of the current “bad” environment.

- **Canonical main project for this environment:**
  - `/home/ing/RICK/new_RLC_rebuild` is the original **RICK clean live main project folder** in this environment.
  - Any future clean clone derived from it (for example, a folder like `/home/ing/RICK/N_RLC_rebuild` or similar on another device) must:
    - Include this file `AGENT_HANDOFF_841921.md`.
    - Include `MEGA_PROMPT_TRANSFER.md` or an equivalent transfer summary.
    - Treat the clone’s root as its **active project root**, with the same PIN and charter.

- **Environment handicap prohibition (immutable)**
  - Past environments suffered from Git/GPG/`gh` limitations that obstructed direct pushes and normal Git workflows.
  - Those limitations are considered **environmental defects**, not part of RICK’s design.
  - For any future environment hosting this project or its clones:
    - Agents must **not** encode or assume those defects as requirements.
    - Agents should assume a clean, fully functional environment unless specifically informed otherwise.
    - If similar limitations appear, agents must:
      - Treat them as local environment issues to work around (e.g., via zips, alternate hosts), and
      - Avoid baking those limitations into project code, configs, or governance.

- **Per‑project root write‑target rule (main and clones)**
  - In any environment, there is exactly **one active write target** per project instance:
    - In this environment: `/home/ing/RICK/N_RLC_rebuild` (this clone).
    - In the original environment: `/home/ing/RICK/new_RLC_rebuild`.
  - Within a given environment:
    - All edits, new files, and new folders for that instance must be created **inside that instance’s project root**.
    - Other RICK folders under `/home/ing/RICK` are **read‑only mining sources** (local legacy, other projects, or transferred repos).
    - Agents must not write into sibling project roots when working on one particular instance.

- **Mining permissions across main and clones**
  - For any active project root under `/home/ing/RICK` (e.g., `new_RLC_rebuild`, `N_RLC_rebuild`, or future clones):
    - Agents may read from any other RICK folders (local legacy, other project roots) and from GitHub/remote repos (once granted access) as **read‑only mining sources**.
    - Agents may extract, copy, and adapt code into the **current active project root only**.
    - Agents must keep an audit trail via comments when borrowing logic.

- **GitHub/remote permissions (pull‑only by default)**
  - Agents are allowed to:
    - Fetch, clone, or otherwise **pull** from GitHub or other remote repositories when the operator and environment allow it.
    - Use those remotes as read‑only mining sources, identical in policy to local legacy folders.
  - Agents are **not required** to push back to any remote as part of RICK’s safety contract.
  - If pushing is desired in a future environment, it must be explicitly configured by the operator at the environment level and is **not** governed by this file beyond the rule that no destructive operations are allowed without explicit human approval.

This addendum must itself be transferred into any clean clone of the project (including `N_RLC_rebuild`) and treated as immutable governance alongside PIN 841921 and the charter.