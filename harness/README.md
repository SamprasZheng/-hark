# PPST Harness — Engineering Multi-Agent Runtime

**Version**: 1.0  
**Status**: Core implementation for the PPST Constitution

This is the **new, open, engineering-focused harness** for the Project-Program-Skill-Target (PPST) system.

It provides concrete, modular components to:
- Launch and orchestrate agents (Orchestrator, Writer, Reviewer/Risk Officer)
- Load and invoke skills via standardized protocols
- Enable mutual calls between heterogeneous agents (Claude, Grok, local models)
- Support intense debate-style collaboration (Discord, chat, multi-pane terminals)
- Keep everything auditable, extensible, and free of hidden philosophy

The harness is deliberately separate from the constitution. It can evolve faster while remaining compliant.

## Architecture Overview

```
Orchestrator (tracks PROJECT + assigns TARGETs)
    |
    v
[CALL SKILL protocol]
    |
    +-- Writer (implements PROGRAM using Skills)
    |
    +-- Reviewer (gates via review Skills, produces reports)
    |
    +-- External Bridges (Discord bot, Zellij panes, GUI)
```

Core invariants (from constitution):
- Always declare PROJECT / PROGRAM / SKILL / TARGET
- Explicit handoffs only
- Review gates before promotion
- Open for new skills and agent types

## Directory Layout

```
harness/
├── README.md                 # This file
├── constitution.md           # (symlink or copy of PPST_CONSTITUTION.md)
├── core/
│   ├── ppst.py               # Core layer declarations + validation
│   ├── skill_loader.py       # Dynamic skill discovery and loading
│   ├── call_protocol.py      # CALL SKILL message parsing and routing
│   └── review_harness.py     # Standardized review gate (5-section or equivalent)
├── launchers/
│   ├── launch-ppst.ps1       # Windows launcher (creates env + optional Zellij)
│   ├── launch-ppst.sh        # Linux/macOS equivalent
│   └── zellij/
│       └── ppst-layout.kdl   # 3-pane layout (Orchestrator / Writer / Reviewer)
├── bridges/
│   ├── discord/
│   │   ├── bot.py            # Discord bot with [CALL SKILL] detection + council
│   │   └── system_prompt.txt # Prompt for bot to act as router/debater
│   └── gui/
│       └── simple_dashboard.py  # Minimal Streamlit/FastAPI tracker
├── agents/
│   ├── orchestrator.py       # Reference orchestrator (tracks state, assigns targets)
│   ├── writer.py             # Reference writer (Aider-style or direct tool use)
│   └── reviewer.py           # Reference reviewer (loads review skills, gates)
└── examples/
    └── cli-json-validator/   # Small end-to-end PPST example
```

## Key Components

### 1. Core Layer (ppst.py)
- Enforces the four-layer declaration.
- Validates handoff messages.
- Provides helpers for state tracking (lightweight JSON or in-memory).

### 2. Skill Loader
- Discovers skills from `skills/` directory (looks for SKILL.md + optional code).
- Supports loading by name.
- Graceful fallback to base PPST rules.

### 3. CALL SKILL Protocol
- Standardized text/JSON format for inter-agent calls.
- Supports routing to local, remote (API), or simulated agents.
- Context is minimal and explicit (previous TARGET output + constraints).

### 4. Review Harness
- Provides a default structured review (adaptable 5-section: Correctness, Fidelity to layers, Traceability, Risk/Constraints, Top Fix).
- Integrates with any review Skill.
- Produces auditable artifacts (JSON + markdown).

### 5. Launchers & Layouts
- One-command setup of the environment.
- Zellij/tmux layouts with clearly labeled panes that start by echoing current PROJECT + TARGET.
- Easy to extend for tmux users.

### 6. Bridges
- **Discord**: Bot that listens for CALL SKILL blocks, can invoke local skills or forward to other agents, and supports full multi-persona council debates using the protocol.
- **GUI**: Lightweight dashboard for visualizing active projects, targets per agent, and one-click call generation.

## How to Run (Basic)

1. Ensure the PPST skill is present: `skills/project-program-skill-target/`
2. Run the launcher:
   ```bash
   ./harness/launchers/launch-ppst.sh --with-zellij
   ```
   (Windows: `.\harness\launchers\launch-ppst.ps1 -StartZellij`)

3. In the Orchestrator pane, start by declaring:
   ```
   PROJECT: Your Project Name
   PROGRAM: main-artifact.py
   SKILL: base-ppst
   TARGET: First concrete deliverable
   ```

4. When you need another agent (e.g. review), use:
   ```
   [CALL SKILL]
   PROJECT: ...
   PROGRAM: ...
   SKILL: reviewer
   TARGET: ...
   ```

5. The Reviewer pane/agent loads the appropriate skill and responds.

## Extending the Harness (Open by Design)

- Add new skills under `skills/<name>/SKILL.md` + optional Python/JS entrypoint.
- Add new agent types under `harness/agents/`.
- Add new bridges (Slack, VS Code extension, etc.) under `harness/bridges/`.
- Customize the review format in `review_harness.py` (still produces structured output).
- Fork the entire harness — the constitution is the only thing that should stay stable across forks.

## Relationship to the Constitution

The harness implements the PPST Constitution. If a harness feature conflicts with the constitution, the constitution wins.

See `PPST_CONSTITUTION.md` for the immutable principles (layering, explicit handoffs, openness, auditability, engineering rigor).

## Philosophy (Engineering Only)

- Prefer explicit declarations over implicit context.
- Prefer composable skills over monolithic prompts.
- Prefer auditable artifacts (JSON, diffs, reports) over narrative.
- Design for heterogeneity (different models, different runtimes) from day one.
- Make extension trivial — the best harness is one that disappears as users add their own skills and agents.

---

## Current Status (as of this version)

- Core PPST skill and protocol defined and clean.
- Launcher and Zellij layout provided.
- Discord bridge skeleton + system prompt ready for expansion.
- Reference agents and review harness included.
- Example project in `examples/`.

This is a living, open engineering harness. Contributions that increase modularity, auditability, or ease of extension are welcome.

Start here:
- Read `PPST_CONSTITUTION.md`
- Load the skill in `skills/project-program-skill-target/SKILL.md`
- Run the launcher
- Declare your first PROJECT / PROGRAM / SKILL / TARGET

Then build.
