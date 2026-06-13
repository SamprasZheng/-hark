# PPST Constitution

**Project-Program-Skill-Target Engineering Framework**  
**Version**: 1.0  
**Date**: 2026-06-14  
**Status**: Ratified (open for extension)

## Preamble

This document defines the immutable high-level principles for the PPST (Project-Program-Skill-Target) multi-agent engineering system. It is designed for open, modular, engineering-first collaboration between human operators and AI agents (Claude, Grok, local models, etc.).

The system exists to enable precise, auditable, and extensible software engineering work through clear decomposition and interoperable skills.

All implementations, skills, harnesses, and agent behaviors must align with these principles. Changes to this constitution require explicit human ratification and version bump.

## Core Principles

1. **Layered Decomposition is Mandatory**  
   Every unit of work must be explicitly mapped to four layers: Project (scope), Program (artifact), Skill (capability), and Target (measurable outcome). Ambiguity in layering is not allowed.

2. **Stateless Boundaries and Explicit Handoffs**  
   Agents operate with minimal shared state. All collaboration happens through explicit, structured handoffs (CALL SKILL format or equivalent). Long context history is secondary to explicit declarations.

3. **Skills are First-Class, Open, and Extensible**  
   Skills are versioned, documented modules that any compliant agent can load and invoke. The system encourages creation of new skills. No skill is privileged except those defined in this constitution for core orchestration.

4. **Interoperability Over Centralization**  
   Agents from different providers (Claude, Grok, local Ollama, etc.) must be able to call each other using standardized protocols. The harness provides bridges, not a single runtime dictator.

5. **Auditability and Traceability**  
   Every action, decision, review, and artifact must be traceable to its originating layers (Project/Program/Skill/Target) and the invoking agent. Reviews (Risk Officer style) are mandatory gates before promotion of artifacts.

6. **Engineering Rigor Over Narrative**  
   Decisions are driven by code, schemas, tests, and measurable targets — not subjective philosophy. All outputs must be structured where possible (JSON, diffs, reports) for machine consumption.

7. **Openness and Forkability**  
   The entire harness, skill registry, and constitution are designed to be forked, extended, and adapted. There are no hidden rules. Extension points (new agents, new skill types, new harness modules) are explicit and encouraged.

8. **Human in the Loop for Constitution and High-Stakes Gates**  
   Humans ratify changes to this constitution and high-level policy. AI agents execute within the defined boundaries and escalate when boundaries are unclear or violated.

## Immutable Elements

- The four-layer PPST model is the primary decomposition primitive.
- The CALL SKILL protocol (or direct equivalent) is the standard for agent-to-agent invocation.
- Review gates (structured 5-section or equivalent) are required before promoting major artifacts.
- All skills must be self-documenting and loadable without side effects on the constitution.

## Governance

- This constitution takes precedence over any harness implementation or skill.
- Updates require a ratified proposal (via chat diff or equivalent) and update to this document with version.
- The harness (separate document) implements these principles but can evolve more rapidly.

## Relationship to Implementations

- `skills/project-program-skill-target/` contains the canonical PPST skill definition and harness entry points.
- The harness (see HARNESS.md or equivalent) provides concrete launchers, bridges (Discord, Zellij, GUI), and runtime for agents.
- New constitutions or major forks should start from this document.

This is an engineering constitution for building better software with AI agents — open, precise, and built to last through iteration.

---

*Ratified for use in clean, philosophy-free multi-agent software engineering environments.*