---
type: concept
tags: [horizon, reversal, momentum, value, term-structure, calibration, sleeves]
title: The Term-Structure of Returns (報酬的時間結構)
author_role: human
source: "Synthesis of 2026-05-31 backtests: daily_horizon_backtest.py (daily reversal), hotspot + IC studies (monthly momentum), nasdaq100_calibration.py (annual value). Principal: 不同時間跨度的參數可能不同."
---

# The Term-Structure of Returns

Across four independent walk-forward backtests this system measured the SAME
underlying structure the academic literature calls the term-structure of returns
— and it is the precise answer to the principal's 「不同時間跨度的參數可能不同」. The
sign of what works **flips** with horizon:

| Horizon | What wins | Measured (IC_IR) | Source |
|---|---|---|---|
| 1-21 trading days | **short-term REVERSAL** (buy recent losers) | +2.4 to +3.5 | `daily_horizon_backtest` |
| (same) | momentum (buy recent winners) | **−1.8 to −2.7 (loses)** | `daily_horizon_backtest` |
| 1-6 months | **MOMENTUM** (FOM's sweet spot) | +2.6 to +3.9, best at 6m | `fom_validation` / `hotspot` |
| 12+ months | **CONTRARIAN + QUALITY** (value) | annual winner; momentum worst tier | `nasdaq100_calibration` |

Reading it as one picture: **fade the very short term, ride the medium term, buy
value for the long term.** Using the wrong sign for the horizon is not a small
miss — at the daily horizon, momentum has a *negative* IC_IR (−2.7), i.e. buying
last month's daily winners actively loses. Per [[../../sharks]], the horizon must
be chosen *before* the signal.

## Why this dictates separate sleeves (not one scorer)

A single weighting cannot serve all three regimes — the optimal sign contradicts
itself across horizons. So the book is **three sleeves with different jobs**, not
one FOM dial:

1. **Core sleeve — FOM, held 3-6 months.** Momentum/quality blend, regime-gated
   ([[regime-gated-scoring]]). Beats the index on average, mean-reverts at tops
   ([[fom-predictive-validity]], [[nasdaq100-calibration]]). This is the engine.
2. **Value sleeve — contrarian + quality, held ~12 months (撿菸頭抽兩口 done safely).**
   The annual-horizon winner in calibration. The KEY discipline: buy beaten-down
   **QUALITY**, never beaten-down junk — the quality filter is the margin of
   safety that separates a cigar-butt from a falling knife. This is the
   *low-risk* way to capture undervaluation, and it is the answer to "how do I buy
   cheap without high-risk".
3. **Moonshot sleeve — ring-fenced, ≤5% NAV, no leverage.** FOM structurally
   cannot pick the moonshots (0.36/3 overlap with actual top-3); chasing them is a
   *different, high-variance* job. Quarantine it so its variance never contaminates
   the core. (Matches the principal's existing Alpha-sleeve rule.)

The daily REVERSAL edge is NOT a fourth sleeve for this book: it is real in IC but
**uncapturable after spread/slippage for a low-frequency investor** — it argues
"don't day-trade, and if you must, don't chase daily winners", nothing more.

## Earnings-season & timing-bias guardrails

- The 1-month IC is the weakest of all horizons — **timing on a 1-day/1-week view
  is noise**. Hold to the sleeve's horizon; do not re-judge on a single print.
- The evidence gate ([[evidence-gated-rebalance]]) already requires earnings
  confirmation before an offensive switch; **do not initiate right before a
  report** — let the volatility resolve, then act on the confirmed number.
- Index seasonality leans *continuation*, not reversion, into late summer (a strong
  May-June has historically RAISED, not lowered, July-August odds — SPX 84% vs 70%
  base, small sample), but earnings dispersion is real: size for the volatility,
  do not lever into prints.

## What this assumes — and where it breaks

- **Daily edges are cost-fragile.** The reversal IC is gross; net of trading costs
  it is likely uncapturable at retail. Reported as research, not a strategy.
- **Survivorship** inflates the annual/value absolute numbers (see
  [[nasdaq100-calibration]]); the *sign structure* is robust to it.
- **Regimes can suspend any layer.** In a funding-chain rupture
  ([[funding-chain-rupture]]) correlations go to 1 and all three sleeves fall
  together — the horizon structure is a normal-market map, not a crisis hedge.

## See also

- [[fom-predictive-validity]] — the medium-horizon momentum edge
- [[nasdaq100-calibration]] — the annual value edge + horizon inversion
- [[hotspot-sector-rotation]] — seasonality at the sector layer
- [[regime-gated-scoring]] — the HORIZON_PROFILES that encode this structure
- [[evidence-gated-rebalance]] — the timing/earnings discipline
- [[farmer-mindset]] — why chasing the short-term winner loses
- [[../01-time-horizon]] — the constitution's horizon doctrine
- [[../02-signal-taxonomy]] — where these signals live
- [[../../sharks]] — constitution
