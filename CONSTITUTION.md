---
title: PPST Constitution — Engineering Principles and Hard Boundaries
version: 1.0
date: 2026-06-14
type: engineering-constitution
status: ratified
---

# PPST Constitution

**Project-Program-Skill-Target (PPST) Engineering Framework**

This is the immutable high-level constitution for the PPST system.

It defines the non-negotiable engineering principles and hard boundaries. Everything else (skills, harnesses, agents, bridges, tools) is implementation detail and may evolve rapidly.

All participants — human or AI agent — must align with this constitution. Violations of hard boundaries are treated as system faults.

## Core Principles

### 1. Mandatory Layered Decomposition
Every unit of work **must** be explicitly decomposed into the four PPST layers (Project, Program, Skill, Target) at the point of initiation and at every handoff.

Ambiguity or omission of layers is not permitted. This is the primary mechanism for creating clean, auditable boundaries.

### 2. Stateless Handoffs and Explicit Context
Agents must operate with minimal implicit shared state. Collaboration occurs through explicit, structured handoffs (primarily the `CALL SKILL` protocol or direct equivalent).

Context must be minimal and relevant. Long conversation history is a secondary aid, not the primary coordination mechanism.

### 3. Skills as First-Class, Versioned, Open Modules
A Skill is a self-contained, documented, reusable capability.

- Skills must be versioned.
- Skills must be loadable by any compliant agent without hidden side effects.
- The creation of new Skills is encouraged and is the primary way the system grows.
- No central authority may declare a Skill "core" in a way that prevents community or individual extension.

### 4. Structured, Verifiable Outputs
Every Target must produce at least one primary artifact that is:
- Structured and machine-readable where feasible (JSON, JSONL, diffs, schemas, logs, test results).
- Directly traceable back to the declared layers and the agent(s) that produced it.
- Subject to explicit review gates before being considered complete.

Narrative text alone is insufficient as a Target deliverable.

### 5. Mandatory Review Gates
Before any significant artifact is promoted (merged, deployed, published as final output, or used as input for downstream high-stakes work), it must pass a structured review.

Reviews must be:
- Traceable (who reviewed, against which criteria, outcome).
- Repeatable (preferably via a loaded Skill).
- Able to produce clear pass / conditional / fail with required fixes.

The Reviewer role (human or agent) has veto power on boundary violations.

### 6. Interoperability and Heterogeneity
The system is designed from the ground up to support agents from different providers, runtimes, and model families working together.

Bridges, protocols, and the `CALL SKILL` format must remain open and not favor any single implementation.

### 7. Auditability and Traceability
Every significant action must be attributable to:
- The initiating Project/Program/Skill/Target declaration.
- The agent(s) involved.
- The exact artifacts produced.

This enables post-hoc analysis, debugging, and improvement of the system itself.

### 8. Openness and Forkability
The framework is intentionally minimal at the constitutional level so that it can be freely forked, extended, and specialized.

Extension points (new Skill types, new agent roles, new output schemas, new bridges, new review criteria) must be documented and kept open.

There shall be no "secret" rules that are not visible in the constitution, skills, or harness documentation.

### 9. Human Oversight on High-Level Policy
While day-to-day execution can be heavily automated, changes to this constitution, major policy shifts, or high-level Project boundaries require explicit human ratification.

AI agents may propose changes but cannot unilaterally modify the constitution.

### 10. Engineering Rigor Over Narrative
Decisions and outputs must be driven by code, data, schemas, tests, metrics, and explicit constraints — not by subjective storytelling or unverified philosophy.

When narrative is used (e.g., in comments or explanations), it must be secondary to the structured artifacts.

## Hard Boundaries (Non-Negotiable)

- No work may proceed without explicit four-layer declaration.
- Agents must not cross declared Program boundaries without a new explicit Target.
- Review gates cannot be bypassed for any artifact that will be used as a foundation for further work or external delivery.
- Structured outputs are required; pure free-form text is not a valid primary Target.
- The system must remain forkable and not accumulate hidden central control.
- Human ratification is required for constitutional changes.

## Relationship to Implementation

- The four-layer PPST model and the above principles are invariant.
- All skills, the harness, agents, Discord integrations, Zellij layouts, schemas, and tools are implementations that must respect this constitution.
- The constitution takes precedence in case of conflict.

## Amendment Process

1. Proposed changes must be submitted as a clear diff or structured proposal.
2. They must demonstrate compatibility with the ten principles and hard boundaries.
3. Ratification requires explicit human approval and a version bump of this document.
4. The change is then reflected in all dependent documentation and templates.

---

This constitution exists to enable precise, scalable, auditable, and open multi-agent software engineering.

It deliberately contains no domain philosophy, trading rules, or narrative beyond what is required for rigorous engineering collaboration.

**Ratified for use in clean, engineering-first environments.**