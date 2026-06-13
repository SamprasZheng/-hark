# launch-ppst.ps1
# One-click launcher for PPST (Project-Program-Skill-Target) environment
# Creates the skill directory, writes the latest SKILL.md and README.md
# Optionally starts Zellij with 3-pane layout (Orchestrator / Writer / Reviewer)

param(
    [switch]$StartZellij
)

$skillDir = "skills/project-program-skill-target"
New-Item -ItemType Directory -Force -Path $skillDir | Out-Null

# Write SKILL.md (core definition)
$skillContent = @'
# Project-Program-Skill-Target (PPST) Skill

**Version**: 1.0  
**Standalone** — general-purpose framework for AI-assisted software engineering and multi-agent collaboration.  
**No philosophy, no domain-specific rules, no legacy context.**

---

## Purpose

This skill enforces a strict four-layer decomposition for any software task:

- **Project** — the overall initiative and its hard boundaries
- **Program** — the concrete code artifact(s) being created or modified
- **Skill** — the reusable capability or procedure being applied right now
- **Target** — the single, measurable, deliverable for the current step

Every action, handoff, or debate must be explicitly tagged with all four layers. This creates clean, stateless boundaries between agents (Claude, Grok, local models, etc.).

---

## The Four Layers (Mandatory Declaration)

When starting work or making a handoff, always state:

```
PROJECT: <overall initiative name and scope>
PROGRAM: <specific file, module, class, or executable artifact>
SKILL: <the capability or procedure being used right now>
TARGET: <exact, verifiable outcome for this step>
```

**Examples**

- PROJECT: Build a new CLI data processing tool
- PROGRAM: src/data_processor.py + accompanying tests
- SKILL: CSV/JSON parser + error-handling pattern
- TARGET: Implement robust CSV reader that handles quoted fields and missing columns; produce working code + 4 passing unit tests

---

## Collaboration & Mutual Agent Calls

Agents can call each other (or themselves) using the standardized handoff format. This works in Discord, Zellij panes, terminals, or any chat interface.

### CALL SKILL Format

```
[CALL SKILL]
PROJECT: <name>
PROGRAM: <specific artifact>
SKILL: <skill name or procedure>
TARGET: <what must be produced>
CONTEXT: <minimal relevant previous output or constraints>
```

The receiving agent must:
1. Load the requested SKILL (or fall back to basic PPST rules).
2. Work only inside the declared PROGRAM.
3. Produce output that directly fulfills the TARGET.
4. Return a structured response (report, diff, JSON artifact, or next CALL SKILL).

### Example — Orchestrator assigns ingestion work

```
[CALL SKILL]
PROJECT: Build a new CLI data processing tool
PROGRAM: src/data_ingest
SKILL: Macro_News_Ingest_Hook -> fetch_latest_sentiment()
TARGET: Parse the latest macro announcement and return a sentiment score in [-1.0, +1.0] as clean JSON.
```

### Example — Writer + Reviewer debate on Discord

```
[AGENT: Writer]
I have added two low-base breakout candidates to the shortlist based on volume and price action.

[CALL SKILL]
PROJECT: Build a new CLI data processing tool
PROGRAM: Discord-Council-Bus
SKILL: Risk-Review procedure
TARGET: Perform bias check and constraint check. Return structured review with pass/fail + recommended adjustments.

[AGENT: Reviewer]
🚨 Review result: Market regime is high-volatility. Candidates meet technical criteria but violate current volatility target.
Recommendation: Reduce suggested weight on both to 0.5%. Add cash-flow constraint note.
Status: CONDITIONAL PASS with adjustments.
```

---

## Operating Rules (Hard)

1. **Always declare the four layers** at the start of any response or work block.
2. **Work only inside the declared PROGRAM.** Do not touch other files unless a new TARGET explicitly adds them.
3. **One Target at a time.** Complete or clearly hand off before opening a new one.
4. **Review before claiming done.** Self-review or mutual CALL SKILL to a review procedure is required.
5. **Create new Skills explicitly.** When you discover a repeatable pattern, document it as a new `skills/<name>/SKILL.md`.
6. **Stateful only where necessary.** Use the four layers + explicit CONTEXT instead of relying on long chat history.
7. **No padding.** If a slot or Target cannot be meaningfully filled, output `null` or "no_action" with reason.

---

## Session Start Template

At the beginning of any new session or major task:

```
Loading PPST skill.
PROJECT: <name>
PROGRAM: <main artifact(s)>
SKILLS: PPST (this), <other skills in use>
TARGET: <first concrete deliverable>
```

Then proceed.

---

## Multi-Agent & Debate Usage

- **Orchestrator** pane / agent: Tracks overall PROJECT, assigns TARGETs, receives results.
- **Writer** pane / agent: Receives a single TARGET + PROGRAM, implements using tools and other Skills.
- **Reviewer** pane / agent: Loads review Skills, runs `CALL SKILL` against Writer output, returns structured gate decision.
- **Discord / chat council**: Agents post using the `[CALL SKILL]` format. Other agents respond in-thread. The conversation itself becomes a live debate log.

For intense parallel debate, each participant can maintain its own view of the current four layers.

---

## Integration Points

- **Zellij / tmux**: One pane per role (Orchestrator / Writer / Reviewer). All panes start by echoing the same PROJECT + current TARGET.
- **Discord bot**: Bot can detect `[CALL SKILL]` blocks and route to the appropriate backend (local model, Grok, Claude via API) or simply post the block for human + agent discussion.
- **GUI / web frontend**: Dashboard shows active Projects, current Targets per agent, available Skills, and "Assign Target to Agent" buttons that generate ready-to-paste `[CALL SKILL]` text.
- **Editor (Cursor, VS Code, etc.)**: Add this skill to custom instructions so the agent always starts responses with the four-layer declaration.

---

## Creating New Skills

Any repeatable capability should become its own skill:

```
skills/
└── your-new-skill/
    └── SKILL.md
```

The `SKILL.md` should contain:
- Clear purpose
- Required inputs (the four layers + any extra parameters)
- Expected output format
- Constraints and safety rules
- Example invocations

Then other agents can `CALL SKILL: your-new-skill` with appropriate TARGET.

---

## Completion Criteria

A Target is complete only when:
- The declared PROGRAM change (or artifact) has been produced.
- Review (self or via another agent) has passed or explicit conditions recorded.
- Updated state / summary is provided.
- Next action or handoff (if any) is clearly stated with the four layers.

---

This is a pure engineering collaboration and task-decomposition skill. Load it at the start of any relevant coding or multi-agent session.

**End of PPST Skill Definition.**
'@

Set-Content -Path "$skillDir/SKILL.md" -Value $skillContent -Encoding UTF8

# Write README.md (this file)
$readmeContent = @'
# Project-Program-Skill-Target (PPST) Skill — Complete Companion Guide

## 🚀 Core Overview

This Skill module provides a clean, engineering-focused framework for AI-assisted software development and multi-agent collaboration (Orchestrator, Writer, Reviewer).

Its core value is **enforcing stateless engineering boundaries**. It turns every task, execution, or agent debate into concrete, verifiable artifacts.

The framework is designed for:
- Structured task decomposition using four clear layers
- Cross-agent mutual calls (Claude ↔ Grok, local models, etc.)
- Intense multi-agent debate (e.g. on Discord or in chat)
- Physical isolation in terminal multiplexers (Zellij, tmux)
- Easy GUI / web frontend integration for tracking progress

This is a pure operational engineering skill with zero domain-specific philosophy or legacy context.

---

## 🛠️ PPST Four-Layer Architecture

When assigning or working on tasks (in Zellij, GUI, Discord, or any interface), you **must** explicitly declare all four layers using these tags:

| Layer     | Declaration Tag | Definition & Constraints                                      | Example |
|-----------|-----------------|---------------------------------------------------------------|---------|
| **Project**  | `PROJECT:`     | Highest-level container / initiative. Defines overall scope and success criteria. | "Build a new CLI data processing tool" |
| **Program**  | `PROGRAM:`     | The specific code artifact, module, or system being modified or created. | `src/data_processor.py` or `Discord-Council-Bus` |
| **Skill**    | `SKILL:`       | The concrete capability, hook, procedure, or tool being invoked right now. | `Macro_News_Ingest_Hook` or `cross-review procedure` |
| **Target**   | `TARGET:`      | The single, measurable, verifiable deliverable for this step (usually a concrete artifact like JSON, code diff, or report). | "Produce `analysis.json` containing 5 validated items with confidence scores" |

**Hard Rule**: Never start work or make a handoff without declaring all four layers clearly.

---

## 💬 Cross-Agent Mutual Calls & Intense Debate Syntax

Agents use the standardized `[CALL SKILL]` block for handoffs, reviews, and collaboration. This format works in Discord channels, chat, terminals, or any shared interface.

### Example 1: Orchestrator assigning a data task

```
[CALL SKILL]
PROJECT: Build a new CLI data processing tool
PROGRAM: src/data.perception
SKILL: Macro_News_Ingest_Hook -> fetch_fed_dot_plot()
TARGET: Parse the latest macro announcement and return a sentiment score in the range [-1.0, 1.0] as clean JSON.
```

### Example 2: Writer + Reviewer intense debate (Discord-style council)

```
[AGENT: Writer]
Based on volume and price action analysis, I have added two low-base candidates to the shortlist.

[CALL SKILL]
PROJECT: Build a new CLI data processing tool
PROGRAM: Discord-Council-Bus
SKILL: Reviewer -> cross-review procedure
TARGET: Perform bias check and constraint validation. Return structured review with pass/fail and recommended adjustments.

[AGENT: Reviewer]
🚨 Review complete. Current regime shows high volatility. Candidates meet technical criteria but violate active volatility target.
Action: Reduce suggested weight on both to 0.5%. Add note on cash-flow constraints.
Status: CONDITIONAL PASS — adjustments required.
```

The receiving agent loads the requested Skill (or falls back to basic PPST rules) and responds with structured output that directly addresses the TARGET.

---

## 🎛️ Zellij / tmux Multi-Pane Setup (Recommended for Isolation)

For best results with physical separation:

1. **Orchestrator Pane** (top or dedicated): Monitors incoming `CALL SKILL` messages, tracks overall Project state, assigns new Targets.
2. **Writer Pane** (bottom-left): Runs in an isolated worktree or clean context. Receives one TARGET at a time and only touches the declared PROGRAM.
3. **Reviewer Pane** (bottom-right): Loads review Skills, executes `CALL SKILL` against Writer output, enforces gates, and returns structured feedback.

All panes should start by declaring the same current PROJECT and active TARGET.

---

## 💡 Next Steps (Pick One or More)

**1. One-click environment launcher**  
A small script (PowerShell or Bash) that:
- Creates the `skills/project-program-skill-target/` directory structure
- Writes the latest `SKILL.md` and this `README.md`
- Optionally launches a pre-configured Zellij layout with the three panes labeled

**2. Discord bot integration prompt**  
A ready-to-use System Prompt for a Discord bot that:
- Detects `[CALL SKILL]` messages automatically
- Routes them to the right backend (local model, Grok, Claude via API, etc.)
- Posts clean results back to the channel
- Supports chaining into full council-style debates

**3. Minimal GUI / dashboard starter**  
A small Streamlit or FastAPI + HTMX example that:
- Lists active Projects and current Targets
- Shows available Skills
- Has a "Create CALL SKILL" form that outputs ready-to-paste blocks
- Tracks state across agents

**4. End-to-end worked example**  
A complete miniature project (e.g. "CLI JSON validator") fully broken down into PPST layers, with sample CALL SKILL traces, expected artifacts, and debate logs.

---

Reply with the number (1, 2, 3, or 4) or describe exactly what you need next (e.g. "give me the full Discord bot prompt" or "give me the launcher script"), and I will deliver the complete, ready-to-use code or prompt immediately.

This version is deliberately kept 100% clean and general-purpose.
'@

Set-Content -Path "$skillDir/README.md" -Value $readmeContent -Encoding UTF8

Write-Host "PPST skill environment created at $skillDir"

if ($StartZellij) {
    Write-Host "Starting Zellij with PPST layout (Orchestrator / Writer / Reviewer)..."
    # Assumes zellij is installed and a layout file exists or falls back to default
    zellij --layout default  # User can customize layout for 3 panes
}
