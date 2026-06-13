---
type: patch
status: proposal
tags: [patch, inspirations, matrix, proposal]
title: Inspirations matrix patch — accept 3 new + register 2 rejections — proposal
author_role: researcher
proposed_destination: literal edits to philosophy/references/open-source-inspirations.md and docs/INSPIRATIONS.md (see diffs below)
proposed_at: 2026-05-29T17:00:00+08:00
source_urls: []
---

# Inspirations Matrix Patch (PROPOSAL)

> Companion to the 5 sibling proposals in this batch. Lays out the *exact* edits the human applies after accepting the 3 new inspirations and the 2 rejection records. The goal: accept step = `git apply` or visual cp, not re-authoring.

## Companion proposals (must accept before this patch)

- [[inspiration-09-fingpt]]
- [[inspiration-10-qlib]]
- [[inspiration-11-backtrader-finrl]]
- [[considered-and-rejected-lobster]]
- [[considered-and-rejected-deeplob]]

## Patch 1 — `philosophy/references/open-source-inspirations.md`

### 1a. Append 3 numbered entries

Insert AFTER existing entry 8 (`awoo424/algotrading`), BEFORE the `## Integration map` section:

```markdown

---

## 9. `AI4Finance-Foundation/FinGPT`

**Fit**: ★★★★☆

Finance-tuned LLM line from the AI4Finance Foundation. LoRA adapters on Llama / Falcon / ChatGLM bases plus a FinNLP data pipeline that ingests Twitter / Reddit / news streams.

**What we borrow**: a finance-domain sentiment scorer that runs locally on the operator's GPU, preserves the source-grading discipline from [[../CLAUDE]] §5, and outputs per-ticker structured sentiment that the four-dimension matrix can consume. Replaces VADER (Inspiration #8) for finance text; VADER remains for general-text fallback.

**Phase**: 4 (scorer) + 5 (fine-tune on `wiki/05_recommendations/archive.md`).

---

## 10. `microsoft/qlib`

**Fit**: ★★★★★

Microsoft Research Asia's AI quant platform. Data layer with native point-in-time semantics, ~150 alpha-factor library (Alpha158 / Alpha360), model zoo (LightGBM / TFT / TabNet / Transformer), backtest engine with realistic frictions.

**What we borrow**: (a) Alpha158 expressions as a candidate feature pool for the technical dimension in [[../02-signal-taxonomy]]; (b) the backtest engine for [[../../docs/ROADMAP]] §Phase 4 deliverable 1; (c) the Workflow YAML pattern for declarative train/val/test partition per [[../04-sector-and-finviz]] Rule 1. Every adoption layer extends Qlib's native point-in-time with `as_of_timestamp` + source-grade tracking.

**Phase**: 4 (factor library + backtest engine) + 5 (model-zoo benchmark).

---

## 11. `mementum/backtrader` (design only) + `AI4Finance-Foundation/FinRL` (integrate)

**Fit**: ★★★★☆ (FinRL) / ★★★☆☆ (Backtrader, design-only)

Paired RL-trading inspiration. Backtrader is the canonical Python event-driven backtest design but GPLv3 — adopted as architecture inspiration only per [[../../docs/INSPIRATIONS]] §Licensing & legal. FinRL is the AI4Finance RL library (PPO / DDPG / SAC / A2C / TD3 on stock-trading Gym envs) — adopted as code-integrable.

**What we borrow**: (a) Backtrader's `Strategy / DataFeed / Broker / Analyzer` class boundaries, reimplemented from scratch in `src/sharks/backtest/bt_engine.py`; (b) FinRL's `StockTradingEnv` adapted to our point-in-time-aware feature store; (c) Stable-Baselines3 PPO as a **sizing critic** (not an entry/exit decider — entries stay in the analyst-debate stack per [[../02-signal-taxonomy]] and [[../CLAUDE]] §1.3).

**Phase**: 4 (backtest engine) + 5 (RL sizing critic, dry-run advisory only per [[../CLAUDE]] §2).

```

### 1b. Update Integration map table

In the `## Integration map (the borrow stack)` ASCII block, **append**:

```
9. Finance LLM sentiment           ←──── AI4Finance/FinGPT
10. Factor library + backtest      ←──── microsoft/qlib
   engine + model zoo
11. Backtest design + RL sizing    ←──── Backtrader (design) + FinRL
```

### 1c. Append See-also link

At the very end of the file (after `## See also` section), append:

```markdown
- `philosophy/references/considered-and-rejected.md` — projects evaluated and explicitly rejected for `$hark` integration, with falsifiability triggers for re-evaluation
```

## Patch 2 — `docs/INSPIRATIONS.md`

### 2a. Append 3 rows to the integration matrix

In the `## Borrow integration matrix` table, **append**:

```markdown
| 9  | `AI4Finance-Foundation/FinGPT` | 4 | `src/sharks/scoring/fingpt_sentiment.py` | LoRA finance-LLM scorer; preserves source-grading; deterministic (temp=0+seed) for backtest replay; `as_of` parameter mandatory; tiny GPU footprint via 4-bit | not started |
| 10 | `microsoft/qlib` | 4 (factors+engine) + 5 (zoo) | `src/sharks/factors/qlib_alpha.py`, `src/sharks/backtest/qlib_engine.py`, `src/sharks/data/qlib_dataset.py` | Wrap data API; add `as_of_timestamp` + source-grade per feature row; pruned Alpha158 (12 of 158); walk-forward enforced; model-zoo gated by interpretability | not started |
| 11 | Backtrader (design) + AI4Finance/FinRL | 4 (engine) + 5 (RL critic) | `src/sharks/backtest/bt_engine.py`, `src/sharks/backtest/env_gym.py`, `src/sharks/agents/rl_sizing_critic.py` | Backtrader GPLv3 → design only, from-scratch engine; FinRL env adapted for our feature store; RL agent restricted to **sizing**, never entries; reward includes [[../philosophy/08-risk-and-position]] penalties; dry-run advisory only | not started |
```

### 2b. Append integration notes

Append two subsections under `## Per-project integration notes`:

```markdown
### #9 FinGPT (Phase 4)

The Compiler currently lacks a finance-domain sentiment scorer; VADER (#8) is general-text. FinGPT-LoRA-Llama2-7B at 4-bit fits the operator's RTX 5070; ChatGLM variants cover Traditional Chinese KOL feeds.

Mandatory adaptations:
- `as_of` parameter on every score call (rejects sources timestamped after as_of)
- Source-grade preserved through scoring (D-tweet stays D-grade)
- Determinism (temp=0, fixed seed) for backtest replay
- Never used for numeric extraction (sentiment-only)

Phase 5 fine-tune target: 24 months of `wiki/05_recommendations/archive.md` outcomes to bias the model toward Mag-7-supply-chain framing.

### #10 Qlib (Phase 4-5)

The most-architecturally-aligned upstream. Native point-in-time semantics extend cleanly to our `as_of_timestamp` + source-grade. Alpha158 factor library is *candidate pool*, not blanket adoption — every factor that lands in `src/sharks/factors/` first earns a [[../philosophy/concepts]] page that explains its economic interpretation.

Decision matrix for Phase 4 deliverable 1 (Backtrader vs vectorbt vs Qlib engine vs from-scratch):
- vectorbt — fastest, Apache-2.0, no friction realism
- Qlib — realistic frictions, MIT, CN-A-share calendar bias
- from-scratch Backtrader-design — full control, slow to build
- Backtrader proper — GPLv3, blocked by license discipline

Recommendation: Qlib engine + Alpha158 candidate pool, with vectorbt as escape hatch if engine speed bottlenecks the walk-forward sprint.

### #11 Backtrader + FinRL (Phase 4-5)

License-driven split: Backtrader (GPLv3) → design only, from-scratch implementation; FinRL (expected MIT) → code-integrable with attribution. Architectural constraint: the RL agent is a **sizing critic**, not an entry/exit policy. Entries remain in the analyst-debate four-dimension stack. Reasons: (a) constitutional ([[../sharks.md]] embeds entry rules), (b) sample efficiency (~9000 entry decisions/year is insufficient for end-to-end RL training), (c) Risk Officer interpretability requirement.

Phase 5 baseline before any PPO training: a deterministic [[../philosophy/concepts/cycle-resonance]]-gated Kelly sizer. If Kelly hits Sharpe + MDD targets, RL is not adopted.
```

## Patch 3 — Create `philosophy/references/considered-and-rejected.md`

New file. Body:

```markdown
---
type: reference
tags: [reference, rejection, decision-history]
title: Considered and Rejected for $hark integration
author_role: human
---

# Considered and Rejected

Open-source projects evaluated and explicitly rejected for `$hark` integration. Recorded so the rejection is auditable and the conditions for re-evaluation are explicit. Pattern precedent: `docs/SAFETY-CHECKLIST.md` recording Codex's 10 vulnerability flags so they aren't silently re-introduced.

A rejection here does NOT mean the project is bad. It means the project does not fit `$hark`'s specific scope (swing-horizon US equity + weekend crypto satellite, philosophy-first, no-HFT) — and the reasoning is preserved so a future agent does not re-litigate.

---

## R1. LOBSTER (NASDAQ limit order book reconstruction)

<body of accepted [[../_proposals/considered-and-rejected-lobster]] inserted here on accept>

---

## R2. DeepLOB (CNN+LSTM on LOB data)

<body of accepted [[../_proposals/considered-and-rejected-deeplob]] inserted here on accept>

---

## See also

- [[open-source-inspirations]] — the *accepted* projects, by phase
- [[../../docs/SAFETY-CHECKLIST]] — the discipline precedent for recording decisions-not-taken
```

## Verification checklist (for the human applying the patches)

1. After Patch 1a, the open-source-inspirations.md numbered list reaches 11 entries.
2. After Patch 1b, the Integration map ASCII block has 11 rows.
3. After Patch 2a, the `## Borrow integration matrix` in `docs/INSPIRATIONS.md` has 11 rows.
4. After Patch 2b, `## Per-project integration notes` has 11 sections (#1–#11).
5. After Patch 3, `philosophy/references/considered-and-rejected.md` exists with 2 rejection entries.
6. `git grep -n "FinGPT\|Qlib\|Backtrader\|FinRL\|LOBSTER\|DeepLOB" philosophy/ docs/ wiki/` shows the new references reachable.
7. No edits to `sharks.md`, no edits to existing entries 1–8 in `open-source-inspirations.md`, no edits to `raw/`.
8. After patch acceptance, the corresponding 6 files in `philosophy/_proposals/` can be moved to `philosophy/_proposals/archive/` (per `_proposals/README.md` workflow step 4).

## Notes for the human reviewer

- The diffs above are deliberately copy-pasteable, not `git diff` format, because the existing files are alive (no canonical pre-image to diff against). The human's mental model: "open both files in the editor, paste each block at the marked insertion point."
- If the human disagrees with Qlib's ★★★★★ rating (e.g. prefers vectorbt as primary engine), drop Qlib to ★★★★☆ and add a clarifying sentence in 1a #10 — the rest of the patch still applies.
- If the human disagrees with the LOBSTER/DeepLOB rejection (e.g. wants to bank them as *methodology* references instead of *integration* rejections), drop Patch 3 from this batch and propose a new `philosophy/references/methodology/` directory in a separate session.
