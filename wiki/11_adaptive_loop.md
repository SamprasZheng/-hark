---
type: synthesis
tags: [adaptive, feedback-loop, walk-forward, ic-analysis, model-updates]
title: Adaptive Feedback Loop — Make FOM Self-Improving
as_of_timestamp: 2026-05-29T07:45:00-04:00
author_role: compiler
status: design
schema_version: 1
---

# Adaptive Feedback Loop Design

Principal asked 2026-05-29: make model **adaptive** — learn from past mistakes.

## §1. The feedback loop architecture

```
┌──────────────┐
│  Daily FOM   │◀──────────────────────┐
│  scoring     │                       │
└──────┬───────┘                       │
       │                               │
       ▼                               │
┌──────────────┐                       │
│ Picks → JSON │                       │
│ → outputs/   │                       │
└──────┬───────┘                       │
       │                               │
       ▼                               │
┌──────────────┐                       │
│  90-day      │                       │
│  forward     │                       │
│  tracking    │                       │
└──────┬───────┘                       │
       │                               │
       ▼                               │
┌──────────────┐                       │
│ IC (Info     │                       │
│ Coefficient) │                       │
│ per dim      │                       │
└──────┬───────┘                       │
       │                               │
       ▼                               │
┌──────────────┐    ┌─────────────────┐│
│  Postmortem  │    │  weight         ││
│  ledger      │───▶│  adjustment     │┘
└──────┬───────┘    │  proposal       │
       │            └─────────────────┘
       ▼
┌──────────────┐
│  Human       │
│  review +    │
│  approve     │
└──────────────┘
```

## §2. The IC (Information Coefficient) measurement

For each FOM dimension, measure how well it correlates with subsequent 90-day forward return:

```
IC(dim) = corr(dim_score, forward_90d_return)
```

- IC > 0.05: dim is **productively predictive**
- IC ∈ [-0.05, +0.05]: dim is **noise**, consider de-weighting
- IC < -0.05: dim is **counter-productive**, flip sign or remove

Computed monthly on a 12-month rolling window.

## §3. The walk-forward weight adjustment

Every 60 days:

1. For each picked-name from 2 months ago, compute realised 60-day return
2. Group by dimension that contributed most to its FOM
3. For dim with highest IC: increase weight by 1-2%
4. For dim with lowest IC: decrease weight by 1-2%
5. Bounds: no single dim < 5% or > 35% of total weight
6. **Human approval required** for weight changes > 2% absolute

## §4. The mistake-feedback mechanism

Per [[09_postmortem_log]]:

When a postmortem ENTRY is filed:
1. Compiler extracts: (a) which dim was wrong, (b) which dim should have been heavier
2. Proposes: weight delta and IP defensibility delta for affected ticker
3. Human reviews via `philosophy/_proposals/`
4. If approved: applied to next FOM run; logged in `data/calibration_history.json`

## §5. Specific adaptive rules already implemented

| Rule | Trigger | Action |
|---|---|---|
| **Persistence boost** | Ticker appears top-50 N consecutive weeks | +5% per week, cap +30% |
| **Drawdown-acceleration** (FOM v2) | r1 << r3/3 AND r1 < -5% | Negative bubble_guard contribution |
| **Trump policy bias** (FOM-Alpha) | Compiler-tagged sectors | +/-10 to final score |
| **Golden cross** (FOM-Alpha) | 5MA × 12MA crossover within 3m | +10 boost |

## §6. Future adaptive features

Phase 3:
- **Sentiment z-score input** (X / Telegram / Reddit social volume)
- **Insider activity signal** (Finnhub SEC filings)
- **Analyst revision direction** (consensus EPS deltas)

Phase 4:
- **Sector-relative momentum** — detect memory-cycle-style catch-up trades that v1 missed (per [[09_postmortem_log]] ENTRY-002)
- **Survivorship-aware backtest** — exclude tickers from universe pre-IPO (per ENTRY-005)
- **Concentration cap rebalance** — auto-trim winning name when > 25% of portfolio (per ENTRY-006)

Phase 5:
- **LLM-driven postmortem reading**: agent reads `09_postmortem_log.md` and proposes weight changes
- **Online learning**: live IC adjustment without explicit human cycles

## §7. Anti-overfitting discipline

Adaptive ≠ overfitting. To stay disciplined:

- **No look-back > 24 months** for IC calculation (forces relevance)
- **No more than 1 weight change per dim per quarter**
- **Always validate on held-out test set** before deploying
- **Document every change** in `data/calibration_history.json`
- **Periodically reset to v1 baseline** to check if adaptive changes generated alpha vs noise

## See also

- [[09_postmortem_log]] — mistake ledger feeding this loop
- [[05_recommendations/2026-05-29-fom-backtest-validation]] — baseline
- [[../philosophy/04-sector-and-finviz]] §Rule 3 — no threshold retuning after test split
