---
type: concept
tags: [fom, validation, information-coefficient, backtest, recalibration, accountability]
title: FOM Predictive Validity — does the score actually forecast? (IC 驗證)
author_role: human
source: "Principal challenge 2026-05-31: 昨天建議的股票沒大漲，FOM 是否失準需要校正. Implemented in src/sharks/backtest/fom_validation_backtest.py; first run outputs/fom-validation-2016-to-2026.json."
---

# FOM Predictive Validity

The accountability instrument. When the principal asks "the stocks you flagged
didn't rally — **is FOM mis-calibrated?**", the honest answer is not a defence,
it is a measurement. Per [[../../sharks]] (no invented certainty), this concept
documents how we *measure* whether FOM forecasts forward returns, and what the
first measurement actually found — including the part that confirms a known flaw.

`fom_backtest.py` answers a different, weaker question — "did a top-3 DCA strategy
make money" — which is confounded by the bull market (SPY rose too). The sharper
question needs the **cross-sectional Information Coefficient (IC)**.

## The method

`src/sharks/backtest/fom_validation_backtest.py`: at each month-end T, rank the
whole universe by FOM using **only data ≤ T** (point-in-time, no lookahead), then
rank-correlate that against the *realised* forward return over T → T+h for
h ∈ {1, 3, 6, 12} months. Aggregated across 112 monthly periods (2016-2026):

- **mean IC** — average Spearman rank correlation (the edge per period).
- **IC_IR** — IC information ratio = mean / std × √n (an IC t-stat; |IR| ≳ 2 is a
  statistically stable signal).
- **quintile spread** — top-FOM-quintile minus bottom-quintile forward return
  (the *tradeable* tail spread).
- **hit rate** — P(top-quintile name beats the universe-median forward return) —
  the outlier-robust tail statistic.

LLM involvement is `none` (pure rule-based scorer), so per
`docs/LLM-BACKTEST-PROTOCOL.md` this run is headline-KPI-eligible.

## What the first run found (2016-2026, 106-ticker universe)

| Horizon | mean IC | IC_IR | % periods +ve | quintile spread | hit rate |
|---|---|---|---|---|---|
| 1m | 0.042 | 2.61 | 62.5% | −1.3% | 0.53 |
| 3m | 0.059 | 3.37 | 62.5% | −5.9% | 0.56 |
| **6m** | **0.063** | **3.85** | **68.8%** | −12.3% | 0.56 |
| 12m | 0.053 | 3.30 | 65.2% | −37.8% | 0.59 |

**Verdict: `RANK-EDGE-BUT-TOP-TAIL-MEAN-REVERTS` (best horizon 6m).** Read it
honestly, in three parts:

1. **The rank IC is real and stable.** ~0.05-0.06 with IC_IR ~3-4 over 112
   periods is a genuine, statistically significant signal. |IC| ≈ 0.05 is
   *in-band* for a real equity factor (good factors run 0.03-0.08) — so FOM is
   **not** broken or inverted. It works best at **6 months**.
2. **But the extreme-top tail mean-reverts.** The quintile spread is *negative*
   and widens with horizon (−1.3% → −37.8%). The very highest-FOM names
   under-perform the very lowest-FOM names. This is **exactly the original
   complaint** — momentum/extension over-rewarding names into a top — now
   measured. You cannot express the FOM edge by concentrating in the top tail.
3. **The robust tail statistic is mildly positive.** The hit rate (median-based,
   so outlier-proof) is 0.53-0.59 — top-quintile names beat the median *more
   often than not*. So the negative *mean* spread is partly artifact (see
   caveats), not a true inversion.

## The honest caveats (why the interpreter does not say "EDGE-CONFIRMED")

- **Survivorship bias.** The universe is *today's* tickers; names that died are
  absent, inflating the low-FOM bottom-quintile forward returns. Part of the
  negative spread is artifact.
- **Mean-spread outlier sensitivity.** The quintile spread uses the mean, so a
  single low-FOM microcap multi-bagger dominates it. The hit rate is the robust
  number, and it is positive.
- **Weak absolute edge.** |IC| ≈ 0.05 means FOM is a **tilt**, never a
  high-conviction timer. An earlier interpreter draft over-claimed "EDGE-CONFIRMED"
  off IC_IR alone; it was corrected to reconcile IC against the spread and hit
  rate — accountability includes auditing our own scorer's self-report.

## What this changes (the recalibration)

- **Hold FOM picks ~3-6 months, not days.** The 1m IC is the weakest; judging a
  pick on next-day moves is a category error, not a model failure. This validates
  the **weekly cadence** the principal wants.
- **Do not over-concentrate in the absolute-highest-FOM names** — size for
  mean-reversion; the tail is where extension risk lives.
- **Lean contrarian at long horizon** — already encoded in [[regime-gated-scoring]]
  (Fix B horizon profiles boost contrarian at 36m). The IC study independently
  motivates it.
- **Every persona tilt and weight change must be re-validated here**
  ([[analyst-persona-ensemble]]) — a tilt that does not improve (or at least not
  degrade) the 3-6m IC on its claimed slice is an opinion, not an edge.

## What this assumes — and where it breaks

- **Universe definition is the experiment.** A different universe (broader, or
  point-in-time-reconstructed to kill survivorship) would move the numbers. The
  next upgrade is a survivorship-free historical universe.
- **IC is not P&L.** Positive IC is necessary, not sufficient — transaction costs,
  position sizing, and the mean-reversion tail all sit between IC and realised
  return.
- **Past IC ≠ future IC.** This is a calibration heartbeat to re-run weekly, not a
  one-time certificate.

## See also

- [[regime-gated-scoring]] — the scorer being validated; horizon profiles it motivates
- [[evidence-gated-rebalance]] — the discipline that consumes the 3-6m holding insight
- [[analyst-persona-ensemble]] — persona tilts must be re-validated against IC here
- [[farmer-mindset]] — the chase-avoidance the mean-reversion finding reinforces
- [[../09-point-in-time]] — the PIT discipline the walk-forward depends on
- [[../02-signal-taxonomy]] — the dimensions whose blend is being validated
- [[../../sharks]] — constitution
