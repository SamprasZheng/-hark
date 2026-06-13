---
type: concept
tags: [nasdaq100, calibration, train-test, overfitting, horizon, fom, validation, accountability]
title: NASDAQ-100 對答案 — train/test FOM calibration (參數隨時間跨度而變)
author_role: human
source: "Principal test 2026-05-31: 2000-2026 NDX TOP3 對答案 + 先校年再月，不同時間跨度參數可能不同. Implemented in src/sharks/backtest/nasdaq100_calibration.py; run outputs/nasdaq100-calibration-2000-to-2026.json."
---

# NASDAQ-100 對答案 — train/test FOM calibration

The principal asked to *check the answer key*: from 2000-2026, which NASDAQ-100
TOP-3 did FOM pick, and could we tune FOM to the known winners? This page records
what the data said — and why we refused the one move that would have made the
numbers a lie. Per [[../../sharks]] and [[../09-point-in-time]], "look at the
answers, then tune params to fit them" is in-sample curve-fitting; the only honest
calibration splits time: tune on TRAIN (2000-2014), prove on held-out TEST
(2015-2026).

## Finding 1 — FOM does NOT pick the moonshots (對答案, honestly)

Mean overlap between FOM's annual top-3 (canonical weights, PIT) and the *actual*
top-3 performers: **0.36 / 3**. FOM almost never calls the single biggest winner in
advance — it did not foresee BKNG +343% (2000), TSLA +743% (2019), or MU +240%
(2024). Any robust momentum/quality scorer behaves this way; if you expected it to
nail the moonshot, it doesn't, and a system that claimed to would be over-fit.

What FOM *does*: pick solid large-caps that **beat QQQ on average** (NVDA 2023 +171%
captured, AMZN 2009 +101%, AMZN/ASML/NVDA 2020 +64%). Mean annual excess vs QQQ
+17% — **but that figure is survivorship-inflated** (the universe is today's NDX
survivors) and is a 3-stock concentrated, high-variance average. It is not a claim
of real tradeable alpha.

What FOM *fails at*: it gets **crushed at cycle tops**, buying momentum right before
a regime flip — 2000 −46%, 2001 −54%, 2007 −58%, 2021 −52%. This is the
extreme-top-tail mean-reversion that [[fom-predictive-validity]] measured, now seen
year by year. It is the reason concentration in FOM top-3 is dangerous and why the
regime gate ([[regime-gated-scoring]]) + evidence gate ([[evidence-gated-rebalance]])
+ leverage discipline exist.

## Finding 2 — the optimal weighting INVERTS with horizon (你的核心洞察，證實)

Calibrating weight archetypes by mean excess-vs-QQQ on the 2000-2014 TRAIN window:

| Rank | ANNUAL horizon | MONTHLY horizon |
|---|---|---|
| 1 | **defensive_value** (con+qual) | **momentum_heavy** |
| 2 | bubble_guard_heavy | momentum_quality |
| 3 | contrarian_heavy | anti_bubble_momentum |
| … | … | … |
| last-ish | momentum_heavy (worst tier) | canonical (mid) |

**At the ANNUAL horizon, contrarian/defensive wins and momentum is the worst tier;
at the MONTHLY horizon, momentum wins.** The principal's hypothesis —
「不同時間跨度的參數可能不同」 — is directly confirmed. This is *why* the existing
`HORIZON_PROFILES` in `fom.py` already tilt 3m → momentum 0.55 and 36m →
contrarian 0.30 + quality 0.30: the calibration independently validates that
design. No retune was applied (see Finding 3).

## Finding 3 — tuning helped at one horizon, HURT at the other (why we did not overfit)

Out-of-sample (2015-2026), tuned-best vs untuned canonical weights:

| Horizon | TRAIN best | OOS (tuned best) | OOS (canonical) | Did tuning win OOS? |
|---|---|---|---|---|
| Annual | defensive_value | +12.2% excess | **+15.1% excess** | **NO — tuning LOST to baseline** |
| Monthly | momentum_heavy | **+2.25%/mo** | +0.90%/mo | YES — tuning generalised |

This is the whole point of the train/test split. At the **annual** horizon, the
in-sample-optimal config **under-performed the untuned canonical weights
out-of-sample** — had we "fit to the answer" we would have shipped a *worse*
system. At the **monthly** horizon, the momentum tilt did generalise. So:

- **Do not retune the annual/36m profile** — canonical/existing is robust OOS;
  chasing the in-sample winner there is over-fitting (proven).
- **The monthly/3m momentum tilt is supported** — and already present in
  `HORIZON_PROFILES`.
- **Tuning is horizon-specific and must always be OOS-validated**, never trusted
  in-sample. The `overfit_check` flag in the output is deliberately conservative;
  the sharper test is tuned-OOS vs canonical-OOS, reported above.

## Week / Day — withheld on purpose

FOM is computed on **monthly bars**, so weekly/daily top-3 from this scorer would
be a category error (the lookback windows count months). Producing them would be a
fudge. They need daily bars + re-parameterised lookbacks — a separate build. The
horizon split is itself the principal's insight applied honestly.

## What this assumes — and where it breaks

- **Survivorship bias** dominates the absolute numbers. The NDX proxy is today's
  long-history survivors; a PIT-membership universe (data vendor) would lower every
  excess figure. The *relative* findings (horizon inversion, tuning-generalisation)
  share the bias on both sides and survive it.
- **3-stock concentration = high variance.** Top-3 means small-n; the means are
  noisy. The structural pattern is the signal, not any single year.
- **Calibration is a heartbeat, not a certificate.** Re-run; do not freeze a tuned
  weight set and trust it forever.

## See also

- [[fom-predictive-validity]] — the IC study whose top-tail-mean-reversion this confirms year by year
- [[regime-gated-scoring]] — the HORIZON_PROFILES this validates (3m momentum / 36m contrarian)
- [[evidence-gated-rebalance]] — why FOM top-3 is a tilt, not a concentrated bet
- [[hotspot-sector-rotation]] — the sibling predict-and-validate study (sectors)
- [[../09-point-in-time]] — the train/test discipline that makes this honest
- [[../02-signal-taxonomy]] — the dimensions whose weighting is being calibrated
- [[../../sharks]] — constitution
