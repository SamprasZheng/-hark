---
name: structured-trading-model
description: Convert an analyst's qualitative trading framework into a structured concept page that fits Sharks ($hark) philosophy/concepts/ schema. Use when the user pastes investment-advisor notes, KOL methodology, trader playbooks, or video/audio transcripts and asks to formalise it, internalise it, or add a new analyst model. Trigger phrases include "formalise this", "make it a model", "add this analyst", "internalise", "結構化", "形式化", "把這個寫成模型", "新增分析師模型", "內化", "把投顧老師寫進來", "add to the framework".
---

# Structured Trading Model Generator

Turns a piece of qualitative trader/analyst material into a `philosophy/concepts/<slug>.md` page that conforms to the Sharks five-contract analyst-model schema (see `[[concepts/chip-flow-single-point-breakout]]` for the reference implementation).

## Files this skill owns

- `philosophy/concepts/<new-slug>.md` — created per invocation
- (proposes, never writes) one new line under an "Analyst Models" subsection of `philosophy/index.md` — reported to the user for human edit per the index's own rule (line 97 of `philosophy/index.md`)

## Files this skill must read before writing

In this exact order — every invocation:

1. `sharks.md` — the constitution. Quote any overlapping principle by number in the new page's intro. If the new model contradicts a principle, the new page MUST flag the contradiction explicitly; never paper it over.
2. `philosophy/02-signal-taxonomy.md` — to map the analyst's signals into Fundamental / News / Technical / Sentiment dimensions and reference the arbitration matrix.
3. `philosophy/05-decision-rubric.md` — to map the analyst's entry / exit / followup to the `picks-YYYY-MM-DD.json` slot contract.
4. `philosophy/07-mode-switch.md` — to declare the analyst's frequency (Low / High / Auto routing).
5. `philosophy/08-risk-and-position.md` — to layer the analyst's stop/exit rules under existing sizing and DD-halt.
6. `philosophy/10-strategies.md` — to declare which existing Strategy (A / B / C) the new model is a sub-case of, refines, or sits orthogonal to.
7. `philosophy/concepts/chip-flow-single-point-breakout.md` — the **reference implementation** of the analyst-model interface; use as the skeleton for the new file.
8. 2 other existing `philosophy/concepts/*.md` chosen by topic overlap — for length and tone calibration.

## What to do based on user intent

### 1. Internalise a new analyst model from pasted notes

1. Read all files in the order above.
2. Ask the user (only if not already provided): analyst name / source URL / time horizon (1m / 3m / 6m / 12m). Skip questions whose answers are obvious from the paste.
3. Extract the analyst's:
   - States and transitions (if state machine) OR scoring rules (if continuous)
   - Entry / exit conditions
   - Risk rules (stops, take-profits, sizing)
   - Universe constraints (which tickers/markets the model applies to)
   - Data inputs (EOD vs intraday, institutional flow, news, sentiment)
4. Pick a slug: lowercase, hyphenated, descriptive (`<core-thesis>.md`). Examples: `event-arbitrage-trump-tariff.md`, `sector-rotation-monthly-momentum.md`.
5. Write `philosophy/concepts/<slug>.md` with:
   - Frontmatter exactly matching the reference implementation's pattern:
     - `type: concept`
     - `tags:` includes `analyst-model` + `advisor-source` + domain tags
     - `title:` English (中文 alt in parens) — match style of `cycle-resonance.md`, `last-snow.md`
     - `author_role: human`
     - `source:` quoted string with origin + ingestion date
   - Sections (use chip-flow page as the template):
     - 1-paragraph intro citing `[[../../sharks]]` principles by number
     - `## Module 1 — Data Ingestion` mapping inputs to existing `src/sharks/data/*.py` clients (and flagging any missing client as Phase 2 gap)
     - `## Module 2 — Universe Selection` mapping to `watchlist/universe.yaml` and `[[../04-sector-and-finviz]]`
     - `## Module 3 — Core Logic` with the state machine OR scoring rule, each state/score cross-linked to existing concepts
     - `## Module 4 — Execution & Risk` mapping to `[[../07-mode-switch]]` and `[[../08-risk-and-position]]`
     - `## Integration into the Sharks framework` with the 4D taxonomy mapping table + conflict arbitration with adjacent strategies + signal contract per `[[../05-decision-rubric]]`
     - `## Implementation hooks` listing the future `src/sharks/scoring/<scorer>.py` functions with `as_of` honouring `[[../09-point-in-time]]`
     - `## What this model assumes — and where it breaks` listing assumptions + degradation paths
     - `## Analyst-Model Interface` table filling all 5 contracts (states, dimensions, entry, risk, mode)
     - `## Anti-patterns` listing common misapplications
     - `## See also` with `[[wikilink]]` to every cited concept / numbered foundation
6. **Never invent thresholds the analyst didn't provide.** Magic numbers (e.g. "20-day MA", "2× volume", "5% support buffer") only appear if the analyst stated them. Otherwise leave them as "Phase 4 backtest deliverable".
7. After writing, propose (do NOT execute) the index addition:
   ```diff
   Analyst Models (externally sourced, internalised into the framework):
   - [[concepts/<existing-analyst-model>]] — ...
   + [[concepts/<new-slug>]] — <one-line description> (<analyst name>)
   ```
   Report to user with the exact diff. Tell them line number in `philosophy/index.md` if known.
8. Report what was written. Do NOT commit, do NOT push, do NOT run wiki lint (no lint exists yet per `philosophy/index.md` line 98).

### 2. Audit a new analyst model against the constitution

Read `sharks.md` + the proposed analyst material. List:
- Which of Andy's 6 principles the new model is compatible with
- Which (if any) it contradicts
- Which bottoming-pattern recognitions (4 of them) overlap

Report as table. Do not write any file.

### 3. Suggest where overlapping content should live

When two analysts describe the same phenomenon (e.g. both Andy and the new model talk about "縮量也不下跌"), do NOT duplicate. Instead:
- Cross-link the new analyst's section to `[[price-volume-divergence]]` (the existing canonical concept)
- Add the new analyst's name to the existing concept's `## See also` block via a proposal to the user (don't auto-edit existing concepts — they're written by the original author/Andy)

## Boundaries

- Do NOT modify `sharks.md` — constitution is human-only per line 10 of that file.
- Do NOT modify any `philosophy/0*-*.md` numbered foundation — those are authored material.
- Do NOT modify `philosophy/index.md` — per its line 97, agents propose, humans edit.
- Do NOT modify any existing `philosophy/concepts/*.md` — only add new siblings.
- Do NOT write into `D:\DOT\yxz` (Sampras's portfolio wiki) — different repo, different schema, different lint rules. Cross-references to yxz, if any, go in chat reports, not file edits.
- Do NOT invent thresholds, ticker filters, or backtest results.
- Do NOT commit or push.

## Reference implementation

`philosophy/concepts/chip-flow-single-point-breakout.md` is the canonical example. Every new file produced by this skill should be structurally isomorphic to it (same section ordering, same Integration table format, same Analyst-Model Interface table).
