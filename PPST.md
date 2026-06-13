# PPST — Project-Program-Skill-Target Framework

**Version**: 1.0  
**Type**: Engineering multi-agent collaboration framework  
**Status**: Core definition

PPST is a clean, engineering-oriented framework for structured collaboration between AI agents (and humans) in software projects.

It replaces vague conversation or narrative-driven workflows with explicit, layered decomposition and verifiable outputs.

## Why PPST?

Traditional agent interactions often suffer from:
- Context pollution and hidden assumptions
- Non-reproducible results
- Difficulty in auditing or debugging
- Poor interoperability between different models or tools

PPST solves this by forcing every piece of work into four orthogonal layers:

1. **Project** — the highest-level scope and constraints (the "city" boundary).
2. **Program** — the concrete executable artifact, module, service, or process being built or modified.
3. **Skill** — a reusable, self-contained capability (tool, procedure, hook, or agent behavior).
4. **Target** — the single, measurable, structured deliverable that must be produced in this step.

All agents must declare these four layers explicitly at the start of any task or handoff. This creates hard, auditable boundaries.

## The Four Layers

| Layer     | Name      | Definition                                      | Engineering Properties              | Typical Output Form          |
|-----------|-----------|-------------------------------------------------|-------------------------------------|------------------------------|
| Project   | Project   | Highest-level initiative and its hard boundaries (scope, compliance, goals). Rarely changes. | Static, strong invariants, versioned at high level | `project.yaml`, README, policy docs |
| Program   | Program   | The actual code artifact, pipeline, service, or runtime component being created/modified. | Executable, testable, version-controlled, schedulable | Source code, scripts, binaries, configs |
| Skill     | Skill     | A reusable, documented capability or procedure that an agent can load and apply. | Modular, composable, testable, versioned | `SKILL.md` + implementation code / prompts / hooks |
| Target    | Target    | The precise, measurable outcome required from the current invocation. Must be verifiable. | Atomic, measurable, produces structured artifact | JSON / JSONL, diff, report, file, test results |

### Hard Rules

- Every task, review, or debate **must** start by declaring all four layers.
- Agents work **only** inside the declared Program for the current Target.
- Skills are the unit of capability reuse. New repeatable patterns should be extracted into new Skills.
- Targets must produce **structured, machine-readable artifacts** whenever possible (JSON, schemas, diffs, logs).
- A Target is complete only when the declared deliverable exists and has passed required gates (e.g., review).

## Multi-Agent Collaboration Model

PPST naturally supports three primary agent roles that can run in parallel or sequentially:

- **Orchestrator**: Owns the Project. Breaks work into Programs and Targets. Assigns work via `[CALL SKILL]` handoffs. Monitors overall state.
- **Writer / Specialist**: Receives a specific Program + Target. Uses available Skills to produce the required artifact. Works in isolation (e.g., dedicated worktree or container).
- **Reviewer / Risk Officer**: Loads review-oriented Skills. Performs structured checks against the four layers, constraints, and quality criteria. Can veto or require adjustments.

### The CALL SKILL Protocol (Core Handoff Mechanism)

Agents communicate using a simple, explicit block:

```
[CALL SKILL]
PROJECT: <project-name>
PROGRAM: <specific-artifact-or-module>
SKILL: <skill-name-or-path>
TARGET: <exact-deliverable-description>
CONTEXT: <minimal relevant prior output or constraints (optional but recommended)>
```

The receiving agent:
1. Loads the requested Skill.
2. Operates only within the declared Program.
3. Produces output that satisfies the Target.
4. Returns either the artifact or a new CALL SKILL for further work / review.

This format is intentionally human- and machine-readable. It works in Discord, terminal, chat, logs, or GUI.

Example (Orchestrator → Writer):

```
[CALL SKILL]
PROJECT: Data Processing CLI Tool
PROGRAM: src/data_processor.py
SKILL: CSV Parser + Validation
TARGET: Implement robust CSV reader handling quoted fields, missing columns, and type coercion. Deliver working module + 5 passing unit tests + usage example in README.
```

Example (Writer → Reviewer for gate):

```
[CALL SKILL]
PROJECT: Data Processing CLI Tool
PROGRAM: src/data_processor.py
SKILL: Structured Review
TARGET: Review the delivered CSV module against Project constraints, code quality, test coverage, and edge cases. Output JSON report with pass/fail + required fixes.
```

## Openness and Extensibility

PPST is deliberately minimal at the core so it can be extended openly:

- Anyone can create new Skills (see template).
- New agent roles or personas can be added by defining how they declare layers and participate in CALL SKILL exchanges.
- Bridges (Discord, Zellij/tmux, GUI, API gateways) are first-class and encouraged.
- The four-layer model itself is the only invariant. Everything else is implementation detail.

Recommended extension areas:
- Domain-specific Skills (ingestion, transformation, review, deployment, etc.)
- Structured schemas for common Target outputs (JSON Schema recommended).
- Review gates with quantifiable criteria (coverage %, lint score, performance benchmarks).
- Persistent state for long-running Programs (while keeping individual Targets stateless where possible).

## Harness and Environment Recommendations (Engineering Focus)

To keep the system reliable and isolated:

- Use worktrees or isolated environments for each major Program change.
- Run Orchestrator, Writer, and Reviewer in separate panes/processes (Zellij, tmux, or containers recommended).
- All structured outputs (Targets, reviews, logs) should be committed or captured.
- Prefer explicit, versioned Skills over ad-hoc prompts.
- Maintain a lightweight project registry (simple YAML/JSON) tracking active Projects, current Programs, open Targets, and available Skills.

## Benefits

- **Verifiability**: Every step produces traceable, reviewable artifacts.
- **Interoperability**: Different agents/models can collaborate without shared hidden state.
- **Reproducibility**: Clear layer declarations + structured handoffs make sessions replayable.
- **Extensibility**: Easy to add new capabilities without breaking the core model.
- **Auditability**: Strong boundaries make it possible to reason about what each agent was responsible for.
- **Scalability**: Works for solo work, small teams, or large multi-agent "councils" (including intense debate flows on Discord or similar).

PPST turns vague "let's build something" into a rigorous, engineering-grade collaboration protocol.

---

**This document is the single source of truth for the PPST model.**

All Skills, harnesses, agents, and tools in the system must align with the four-layer decomposition and the rules above.

For the detailed calling syntax, examples, and Discord/Zellij usage patterns, see:
`skills/project-program-skill-target/README.md`

For the hard engineering constitution and principles, see:
`CONSTITUTION.md`

For how to create new Skills, see the template in `skills/_template/`.