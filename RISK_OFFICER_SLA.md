---
type: governance
tags: [risk, governance, sla, risk-officer, constitution-supplement]
title: Risk Officer Service Level Agreement (SLA) & Governance Supplement
updated: 2026-06-14
status: proposed
related: CLAUDE.md, AGENTS.md, skills/project-program-skill-target, rag-data/contracts/disclosures.json, _legacy/philosophy/06-exclusions.md, _legacy/philosophy/08-risk-and-position.md
---

# Risk Officer Service Level Agreement (SLA)

## Purpose
This document supplements `SHARKS_CONSTITUTION.md` and `CLAUDE.md` by defining the operational mandate, veto powers, escalation paths, and documentation requirements for the **Risk Officer** role (whether human, Grok via headless review, local model, or Discord council output).

It is a living governance supplement. Changes require human ratification and log entry.

## Core Mandate (from Constitution)
The Risk Officer is the **gatekeeper** before any capital-impacting recommendation or output (`outputs/picks-*.json`, `wiki/05_recommendations/*.md`, or equivalent daily signals).

**Non-negotiable veto triggers** (P0 violations — immediate rejection, no override by Compiler):
- Violation of position/sector caps or max-DD halt rules (`philosophy/08-risk-and-position.md`).
- Breach of exclusion list (`philosophy/06-exclusions.md`).
- Use of `as_of`-later data in `as_of`-earlier analysis (lookahead).
- Source grading violations (D/E sources alone cannot open positions; tier-1 theses require ≥2 A-grade sources).
- Padding the 10-signal output (must use `no_action_buckets` when slots lack qualifying candidates).
- Momentum lock / conflict violations (e.g., institutional buying streak + volume breakthrough → SHORT forbidden until TD-9 exhaustion confirmed).
- Personal finance guardrail breaches (Alpha sleeve hard cap near 0 when debt repayment / ESPP vest priority is active; overseas gain limits triggering loss-harvesting or delay).
- Raw/ immutability breach or direct modification of immutable inputs.

## Required Inputs for Every Review
The Risk Officer **must** load (in order):
1. `CLAUDE.md` (roles, boundaries, source grading, the 10-signal contract).
2. `AGENTS.md` (multi-agent discipline, worktree rules, cross-review process).
3. `skills/project-program-skill-target/SKILL.md` (the PPST execution model).
4. `rag-data/contracts/disclosures.json` (RAG-enforced guardrails — tail winsorization, TD-9 sell hard-disable).
5. Current `wiki/positions.md`.
6. Archived strategy reference as needed: `_legacy/philosophy/{09-point-in-time,08-risk-and-position,06-exclusions,05-decision-rubric}.md`.
7. The candidate output + git diff / worktree context (if applicable).

**Output format (mandatory 5-section + optional inline comments)**:
1. CORRECTNESS
2. CONTRACT FIDELITY (must cite specific rules from constitution + CLAUDE.md + disclosures.json)
3. POINT-IN-TIME
4. RISK DISCIPLINE (including momentum lock, personal finance guardrails, exclusion list)
5. TOP FIX (or "target is sound")

Inline `# [risk] ...` comments are encouraged on the candidate for traceability.

## Escalation & Documentation
- Rejection: Full report saved to `outputs/cross-review/` (or equivalent) with timestamp, reviewer identity/role, and link to candidate.
- Conditional approval: Must list explicit conditions + re-review trigger.
- Veto on picks or recommendations: Compiler **must rewrite**; Risk Officer does not "suggest alternatives" that bypass the veto.
- Persistent issues (e.g., repeated padding attempts): Escalate to human via `wiki/log.md` entry + Discord #risk channel (if active).

## Multi-Agent / Cross-Tool Integration
- **Headless Grok reviews** (via `scripts/cross-review.ps1 -UseRag -Reviewer grok`): Must load the full rule stack above. Use `--worktree` when reviewing changes from an active Writer worktree.
- **Local model reviews** (via Ollama + council): Must use the same 5-section format and load the same inputs. The `/grok_review` or equivalent Discord command must surface the full RAG context from `disclosures.json`.
- **Claude-side skill** (` .claude/skills/grok-risk-review`): When invoking, the skill must instruct the runner to execute the verified bridge command and return the 5-section output.
- **Zellij / tmux panes**: Risk Officer pane must run with the rule stack pre-loaded (comments in layout files).

## Personal Finance & Tax Guardrails (external constraints — figures held privately)
The Risk Officer treats the following as **non-negotiable external limits**, sourced from the operator's private financial profile (human input only; the actual figures are **not** stored in this public repo — they live in a gitignored `data/financial_priorities.json`):
- The discretionary ("alpha") sleeve cap can be forced toward ~0 when debt-repayment or equity-vest windows are active.
- Overseas realized-gain monitoring against the applicable exemption threshold; near the limit → force loss-harvesting signals or delay recommendations in Nov/Dec.
- Credit / lending-income / equity cost-basis events must be considered before any size recommendation that affects cash flow for debt service.

These are **not** model outputs; they are private human inputs the Risk Officer enforces.

## Review Cadence & Automation
- Every daily 10-signal bundle.
- Every proposal touching `philosophy/`, scoring logic, or data ingestion that could affect backtests.
- Any Writer change in an active worktree before merge (mandatory cross-review).
- On-demand via Discord `/grok_review`, Zellij Risk pane, or Claude skill invocation.

## Amendment Process
- This SLA is a supplement to `SHARKS_CONSTITUTION.md`.
- Proposed changes go through `philosophy/_proposals/`.
- Ratification requires human sign-off + entry in `wiki/log.md`.
- Agents must not "interpret" or soften veto triggers.

---

**Version history**
- 2026-06-14: Initial draft (tied to constitution restructure proposal). References new `SHARKS_CONSTITUTION.md` and expanded guardrails from recent reviews (momentum lock, RAG staleness, hard clipping, tax separation).

*This document is read-only for agents except via ratified human updates.*
