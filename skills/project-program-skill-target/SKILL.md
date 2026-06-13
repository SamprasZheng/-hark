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
- **Target** — the single, measurable deliverable for the current step

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
TARGET: Perform bias and constraint check. Return structured review JSON with pass/fail + recommended adjustments.

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
- **GUI / web frontend**: Dashboard shows active Projects, current Targets per agent, available Skills, and "Assign Target" buttons that generate ready-to-paste `[CALL SKILL]` text.
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
