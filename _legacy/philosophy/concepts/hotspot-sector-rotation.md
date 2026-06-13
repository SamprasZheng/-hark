---
type: concept
tags: [hotspot, sector-rotation, seasonality, business-cycle, prediction, validation, backtest]
title: Hotspot Prediction — seasonality beats momentum (熱點預測)
author_role: human
source: "Principal directive 2026-05-31: 回測預測下一個熱點並驗證 + 觀察季節性與景氣循環產業輪動. Implemented in src/sharks/backtest/hotspot_backtest.py; run outputs/hotspot-backtest-2016-to-2026.json."
---

# Hotspot Prediction — seasonality beats momentum

The predict-and-validate loop for "下一個熱點是哪個板塊?". At each month-end T
(point-in-time), it predicts the next-quarter (T→T+3m) sector leaders from two
components, then **grades its own prediction** against the realised outcome and
reports whether it beats a random baseline. Per [[../../sharks]], the headline is
not a forecast — it is the measured *edge* of each component, honestly reported.

## The two components

`src/sharks/backtest/hotspot_backtest.py` ranks the 15 sector ETFs
(`sector_flow.SECTOR_ETFS`) by:

- **Momentum persistence** — trailing relative strength vs SPY (the "money is
  rotating in" signal). Tests whether leaders keep leading for a quarter.
- **Seasonality / 景氣循環** — each sector's historical average forward return
  conditioned on the *current calendar month*, using only years strictly before T
  (genuinely PIT). Tests calendar + business-cycle rotation.

Both are z-scored and blended; the predictor names the top-k sectors.

## The finding (2016-2026, 121 quarterly predictions) — counter-intuitive

| Component | mean IC | IC_IR | precision@3 | beats random |
|---|---|---|---|---|
| Momentum | 0.016 | **0.52** | 0.237 | 54.5% |
| **Seasonality** | **0.087** | **2.78** | **0.278** | **65.3%** |
| Blend 50/50 | 0.048 | 1.70 | 0.253 | 61.2% |

**Verdict: `PREDICTIVE-EDGE`, best component = seasonality.** The lessons:

1. **Sector momentum-persistence is ~noise at the quarter horizon** (IC_IR 0.52,
   barely beats a coin flip). "Buy whatever sector is hot" does NOT reliably
   predict next-quarter leaders. This is a direct argument *against* chasing
   rotation — it reinforces [[farmer-mindset]].
2. **Seasonality / business-cycle rotation carries a real, stable edge** (IC_IR
   2.78, beats random 65% of the time). The principal's instinct to watch
   季節性與景氣循環產業輪動 is data-validated.
3. **A naive 50/50 blend is diluted by the noisy momentum half.** A blend sweep
   showed IC_IR rising monotonically as weight shifts to seasonality (0.54 →
   2.78). The default blend is therefore **seasonality-dominant (0.2 / 0.8)** —
   keeping a small momentum sliver as a hedge against seasonality regime-breaks,
   rather than overfitting to the exact in-sample maximum at 0.0/1.0.

## Operating use

- The `current_prediction` block names the top-k sectors for the coming quarter
  (e.g. as of 2026-05: SOXX / XLK / XBI). **It is a WATCHLIST, not a buy list** —
  any entry must still clear [[evidence-gated-rebalance]] (十足的證據). Sector heat,
  even seasonally-confirmed, is necessary but not sufficient.
- Feeds the daily/weekly routine: the weekly pass re-runs this so the hotspot list
  and its measured edge stay current.
- Pairs with [[sector-seasonality]] (the per-sector best/worst-month tables) — this
  module is their walk-forward validation, turning the seasonal lore into a graded,
  PIT-honest signal.

## What this assumes — and where it breaks

- **Seasonality is non-stationary.** A 10-year average month-effect can break in a
  regime shift (e.g. a recession overrides the calendar). The 0.2 momentum sliver
  and the modest edge size are the guardrails; never size a hotspot bet as if the
  seasonal mean were a forecast.
- **15 sectors is a small cross-section.** precision@3 of 0.28 vs a 0.20 random
  baseline is a real but *small* margin — enough to tilt a watchlist, not to bet
  big.
- **Survivorship is mild here** (sector ETFs rarely die) — a cleaner setup than the
  single-name [[fom-predictive-validity]] study, which is why the seasonality
  signal is more trustworthy than the single-stock tail spread.

## See also

- [[sector-seasonality]] — the seasonal lore this validates
- [[seasonal-monthly]] — index-level monthly seasonality (the macro analogue)
- [[fom-predictive-validity]] — the single-name IC study; same method, noisier data
- [[evidence-gated-rebalance]] — the gate any hotspot entry must still clear
- [[farmer-mindset]] — reinforced by the momentum-is-noise finding
- [[../02-signal-taxonomy]] — where sector-rotation sits in the 4D taxonomy
- [[../../sharks]] — constitution
