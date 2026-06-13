---
type: proposal
tags: [proposal, schema, tech-layer, claude-md]
as_of_timestamp: 2026-05-31T01:45:00+08:00
author_role: researcher
status: proposal
---

# Proposal: register the `tech/` due-diligence layer in the schema

**Context.** On 2026-05-31 a new top-level folder `tech/` was created — the **technology-trend due-diligence layer** (recommend/research-only; upstream of the investment layer). It screens hot tech/culture narratives for **質變 vs 同溫層** on the [[../../tech/00_framework]] rubric. It is not yet referenced in [[../CLAUDE]] or [[index]].

**Boundary respected.** Per [[../CLAUDE]] §9, `CLAUDE.md` is co-evolved and human-edited; **this agent did NOT edit `CLAUDE.md` or `sharks.md`.** Below are copy-paste diffs for the human to apply.

---

## Patch 1 — `CLAUDE.md` §1.2 Researcher "Writes" line

Append `tech/<slug>.md` to the Researcher's writes list so the layer is a sanctioned Researcher output:

```diff
 - **Writes**: `philosophy/entities/*.md` (when adding a new ticker to coverage), new `wiki/` synthesis pages.
+- **Also writes**: `tech/<slug>.md` — technology-trend due-diligence pages (recommend-only; see the `tech/` layer note below).
```

## Patch 2 — `CLAUDE.md` new mini-section (suggest placing after §6 "Writing style")

```markdown
## 6b. The `tech/` due-diligence layer

`tech/` is the technology-trend due-diligence layer — upstream of the investment layer, recommend/research-only. Each page screens ONE hot narrative for 質變 (real qualitative change) vs 同溫層 (echo chamber) on the 5-axis rubric in `tech/00_framework.md` (A1 技術底蘊 / A2 需求真實性 / A3 資金·權威 / A4 供應鏈可投資性 / A5 顛覆向量), emitting a verdict ∈ {質變, 結構, 過熱, 太早}.

- Frontmatter: `type: synthesis`, `domain: tech-trend`, plus `verdict`, `rubric`, `confidence`, the usual `as_of_timestamp` + `author_role`.
- A verdict is a SCREEN OUTPUT, not a recommendation. It does not bypass the Risk Officer (§1.3), the position/concentration caps ([[philosophy/08-risk-and-position]]), or the 十足的證據 gate ([[philosophy/concepts/evidence-gated-rebalance]]).
- Anti-echo-chamber mandate: weight CAPITAL + ADOPTION + AUTHORITY data over narrative; every page names its "echo-chamber gap."
- Navigation hub: `tech/index.md`; scored matrix: `tech/scoreboard.md`; synergies: `tech/99_cross_synthesis.md`.
```

## Patch 3 — `philosophy/index.md` "What lives elsewhere" list

```diff
 - `outputs/` — daily `picks-YYYY-MM-DD.json` machine-readable outputs
+- `tech/` — technology-trend due-diligence (質變-vs-同溫層 screen; recommend-only; hub `tech/index.md`)
 - `src/sharks/` — the Python implementation (Phase 2+)
```

---

## Rationale

- The layer already follows the constitution (point-in-time, A–E grading, clinical tone, `[[wikilink]]`s), so registration is documentation-catch-up, not a new rule.
- Without registration, a fresh agent session will not discover `tech/` from the schema doc alone (it is currently only findable via `wiki/log.md` + the memory pointer).
- No change to any hard boundary: `tech/` is recommend-only and its verdicts remain subject to the Risk Officer and all caps.

## If declined

Leave `tech/` as an un-schema'd working area; it remains functional and logged. Re-propose only if the layer grows a second phase.
