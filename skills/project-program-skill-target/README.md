# Project-Program-Skill-Target (PPST) — Calling Specification and Usage Guide

**Version**: 1.0  
**Status**: Core reference for the PPST engineering framework

This document defines the practical syntax, conventions, and patterns for using the PPST (Project-Program-Skill-Target) decomposition in multi-agent environments.

It is the primary reference for how agents (Orchestrator, Writer/Specialist, Reviewer) declare layers, make handoffs, and collaborate.

## The Four Layers (Must Be Declared Explicitly)

Every task, sub-task, or debate round **must** begin by stating the four layers using these exact tags:

| Layer     | Tag          | Meaning and Constraints                                      | Typical Artifact |
|-----------|--------------|--------------------------------------------------------------|------------------|
| Project   | `PROJECT:`   | Highest-level initiative and its fixed boundaries (scope, compliance, success criteria). Changes rarely. | `project.yaml`, root README, policy docs |
| Program   | `PROGRAM:`   | The concrete code module, service, pipeline, or artifact being created or modified. | Source file(s), script, binary, config |
| Skill     | `SKILL:`     | The specific reusable capability, hook, procedure, or agent behavior being invoked. | `SKILL.md` + implementation |
| Target    | `TARGET:`    | The single, precise, verifiable deliverable required from this step. Must be measurable. | JSON/JSONL, diff, test results, report, file |

**Rule**: If you cannot clearly state all four, you are not ready to start the work or the handoff.

## CALL SKILL Handoff Format (Primary Collaboration Protocol)

Agents communicate using the following explicit block format. It is designed to be both human-readable and easily parseable by tools or other agents.

```
[CALL SKILL]
PROJECT: <project-identifier>
PROGRAM: <specific-program-or-module>
SKILL: <skill-name-or-path>
TARGET: <exact, actionable deliverable description>
CONTEXT: <minimal, relevant context from prior step (optional but strongly recommended)>
```

### Rules for CALL SKILL

- The receiving agent **must** load the named Skill (or fall back to base PPST rules).
- Work is restricted to the declared `PROGRAM`.
- The output must directly satisfy the `TARGET`.
- The response should either deliver the artifact or issue a new `CALL SKILL` for the next step (e.g., review, refinement, or handoff).

### Example 1 — Orchestrator assigns concrete work to Writer

```
[CALL SKILL]
PROJECT: Data Processing CLI Tool v2
PROGRAM: src/data_processor.py
SKILL: robust-csv-parser
TARGET: Implement a CSV reader that correctly handles quoted fields, missing columns, and basic type inference. Deliver the module plus at least 5 passing unit tests and a short usage example.
CONTEXT: Previous exploration showed the input files use RFC 4180 format with occasional empty fields.
```

### Example 2 — Writer requests structured review (intense debate / gate)

```
[CALL SKILL]
PROJECT: Data Processing CLI Tool v2
PROGRAM: src/data_processor.py
SKILL: structured-review
TARGET: Perform a full review of the delivered CSV parser against correctness, edge cases, test coverage, style, and Project constraints. Output a JSON report with overall verdict (PASS / CONDITIONAL / FAIL) plus specific required fixes.
CONTEXT: [paste or reference the module + test results]
```

The Reviewer loads `structured-review` (or equivalent Risk/Review Skill) and returns a structured artifact that the Orchestrator or Writer can act on.

## Multi-Agent Roles in PPST

PPST naturally maps to three primary collaborating roles. These can be humans, different LLM instances, or specialized agents running in separate panes/containers.

- **Orchestrator**: Maintains the overall Project view. Decomposes work into Programs and Targets. Issues `CALL SKILL` assignments. Collects results and decides on next steps or escalation.
- **Writer / Specialist**: Receives a focused `PROGRAM + TARGET`. Uses available Skills to produce the required deliverable. Should work in as much isolation as possible (dedicated worktree, container, or context).
- **Reviewer**: Loads review-oriented Skills. Evaluates outputs against the declared layers, quality criteria, and any active constraints. Produces structured feedback (pass/fail + fixes). Has effective veto power on boundary violations.

These roles can be played by the same model in different "hats", or by completely different backends (Claude, Grok, local Ollama, etc.). The `CALL SKILL` format is the interoperability layer.

## Recommended Environment Harness (for Reliability and Isolation)

For serious use, the following setup is strongly recommended:

- **Zellij or tmux** with at least three labeled panes:
  - Orchestrator (top or side) — tracks state, reads incoming `CALL SKILL` traffic.
  - Writer — works on the current `PROGRAM` in an isolated worktree.
  - Reviewer — loads review Skills and performs gates.

- Start every pane by echoing the current four layers so context is explicit and synchronized.

- Use worktrees (or equivalent isolation) for each significant `PROGRAM` change so that Writer changes do not pollute the main tree until reviewed.

- All important artifacts (Targets, review reports, final deliverables) should be committed or captured in structured form.

## Discord / Chat Council Usage

The same `CALL SKILL` syntax works excellently for intense, recorded multi-agent debate on Discord or similar platforms.

- Any participant can emit a `[CALL SKILL]` block.
- Other agents (or humans) respond in-thread with results or follow-on calls.
- The thread itself becomes an auditable debate log.
- A "council" can be formed by having multiple specialist Skills/agents take turns on the same `TARGET` (e.g., one does implementation, one does security review, one does performance review).

Example flow on Discord:
1. Orchestrator posts a high-level assignment.
2. Writer posts a `[CALL SKILL]` with their proposed implementation.
3. Reviewer posts a review `CALL SKILL` result.
4. Further refinement calls continue until the Target is satisfied or escalated.

## Creating New Skills (Template)

When you discover a repeatable pattern, extract it into a new Skill.

Recommended directory layout for a new Skill:

```
skills/
└── your-skill-name/
    ├── SKILL.md          # Human + agent readable definition (required)
    ├── implementation/   # Code, prompts, hooks, etc. (optional but recommended)
    └── examples/         # Usage examples (strongly recommended)
```

The `SKILL.md` should contain at minimum:
- Purpose and invariants
- Required inputs (beyond the standard four layers)
- Expected output format (prefer structured)
- Constraints and failure modes
- Example invocations (good and bad)

See `skills/_template/SKILL.md` for a ready-to-copy template.

## Structured Outputs and Schemas

Prefer JSON (or JSONL) for machine consumption whenever possible.

Common Target output types in this framework:
- Review reports (verdict + issues + fixes)
- Analysis results
- Generated code diffs or patches (with metadata)
- Test results and coverage
- Configuration or policy updates

A recommended base schema for many review-style Targets is provided alongside this skill (see `schemas/` if present in your harness).

## Openness and Evolution

PPST is deliberately small at the constitutional level so that it remains easy to extend:

- New Skills are the main growth mechanism.
- New agent roles can be introduced by documenting how they participate in layer declarations and `CALL SKILL` exchanges.
- Bridges (Discord, GUI, API, IDE plugins, etc.) are encouraged.
- The four-layer model itself should remain stable; everything else is fair game for improvement.

If you create a generally useful Skill or bridge, consider contributing it back so the ecosystem grows.

---

**Load this document (and the core PPST skill definition) at the start of any relevant session or when onboarding a new agent.**

For the high-level engineering principles and hard boundaries, see `CONSTITUTION.md`.

For the overall system overview, see `PPST.md`.

For how to bootstrap the environment (launchers, Zellij layouts, etc.), see the harness documentation.

This is a living engineering specification. Feedback that increases clarity, verifiability, or openness is welcome.