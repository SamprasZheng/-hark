---
type: research
title: Trading Society — 3-layer competition framework (short-term + 10-year)
as_of_timestamp: 2026-06-14T00:00:00+08:00
author_role: writer
status: draft
tags: [trading-society, framework, allocation, competition, potential, layers]
related:
  - simulation/layer1_allocation.py
  - simulation/competition_2018_2026.py
  - simulation/layer3_potential.py
  - simulation/portfolio_generator.py
---

# Trading Society — 3-layer competition framework

A layered framework that serves both **short-term executable recommendations** and
**long-term potential prediction**. Recommend-only throughout; promotion to capital
use requires human + Risk-Officer gate (CLAUDE.md §10).

| Layer | Goal | Horizon | Output | Status |
|---|---|---|---|---|
| **1** | short-term decision support | 1–3 months | next-quarter allocation (new/hold/trim) | **built** (`layer1_allocation.py`) |
| **2** | mid-term strategy validation | 1–4 quarters | evolving competition leaderboard | **built** (`competition_2018_2026.py`) |
| **3** | long-term potential | 5–10 years | Top-30 potential scorecard | **built** (`layer3_potential.py`) |

## Layer 1 — short-term allocation (top priority)

`layer1_allocation.py` turns the 14-trader vote into a readable next-quarter
allocation:
- **Core growth (large-cap, 80% of growth leg):** new / hold / trim lists (diffed
  vs the prior Layer-1 run). Single-name cap ≤ 12%.
- **Satellite (small-cap high-beta, 20%):** Small Cap Catalyst Hunter picks. Cap ≤ 6%.
- **Defensive leg:** dynamic ratio + the §10 high-valuation floor (≥ 35%), cash +
  defensive basket.
- **Caps:** single-sector ≤ 35% (real Finviz industries). Regime guardrail applied.

## Layer 2 — mid-term evolving competition

`competition_2018_2026.py` — long-horizon, quarter-by-quarter evolution.

**Rigor upgrades (review A + B):**
- **Diversified per-quarter book (A):** each trader holds a **≤10-name** monthly
  book, **80% large-cap / 20% small-cap**, single-name caps **12% / 6%** — no more
  top-3 concentration, so a single moonshot can't carry a trader. (`LARGE_CAP` is a
  curated stable-large-cap set; historical market caps aren't in the lake.)
- **Cross-style fair fitness (B):** a second leaderboard ranks by a risk-adjusted +
  regime-aware composite (40% quarterly Sharpe + 30% normalized cumulative + 30%
  drawdown control), and reports each trader's bull-quarter vs bear-quarter average
  return + hit rate. So a steady defensive trader isn't buried under a momentum
  trader's headline number. The **fair champion** is reported alongside the raw one.
- Long-biased (long-only diversified book); shorts remain gated to HARD_DEFENSE in
  the simple path + live portfolio (CLAUDE §10).

**Out-of-sample validation (`walk_forward_validation.py`):** train 2018-2022 (20q,
evolving, 4 bear quarters) → freeze genomes → validate 2023-2026 (14q, frozen). All
7 traders held their risk-adjusted rank; **LT_BALANCED stayed #1 → #1** (rank
stability = the real positive). **But honest caveat:** the validation window has **0
bear quarters** (vs 4 in training), so the uniformly higher out-of-sample Sharpe is a
**regime-difficulty artifact, not proof of cross-regime robustness**. A genuine bear
out-of-sample isn't available post-2022 in this data; cross-regime/bear robustness can
only be judged from the in-sample bears (where LT_TREND was the only positive-in-bear
trader). Verdict: the mechanism is **rank-stable in a bull**, not yet bear-validated.

Still TODO: real fundamentals (Capex/FCF/ROIC) for selection quality; a bear-
containing OOS window (e.g. when the next drawdown arrives) for true cross-regime proof.

## Layer 3 — 10-year potential scorecard

`layer3_potential.py` — a transparent 0-100 scorecard over 7 dimensions:

| Dimension | Weight | Data source |
|---|---|---|
| Industry trend (10-yr structural growth) | 25% | curated by Finviz industry |
| Moat / competitive advantage | 20% | **real** (`fom.IP_DEFENSIBILITY`) |
| Capital allocation (ROIC, M&A record) | 15% | **proxy (neutral) — TODO real** |
| FCF quality & growth | 15% | **proxy (neutral) — TODO real** |
| Valuation vs growth | 10% | **real** (Finviz P/E) |
| Management & governance | 10% | **proxy (neutral) — TODO** |
| Geopolitical / sovereign immunity | 5% | curated |

Output: Top-30 ranking, each name tagged `core_long_term` vs `high_growth_high_risk`,
with its main driver + risk flag. Honest: 3 of 7 dimensions are neutral proxies until
real financials (polygon FCF/ROIC) + governance data are wired.

## Quarterly run sequence

```
each quarter start:
  Layer 1 -> next-quarter allocation (new/hold/trim) + regime floor
  Layer 2 -> run the evolving competition; update leaderboard + genomes
  Layer 3 -> (yearly) refresh the 10-year potential Top-30; cross-check vs Layer 1
```

## Governance

Recommend-only. Layers never write `outputs/picks-*` / `wiki/05_recommendations/*`.
Real data: FRED macro + real Buffett Indicator, Finviz industries + valuation.
Long-biased; shorts only in HARD_DEFENSE (CLAUDE.md §10).
