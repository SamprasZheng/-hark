---
type: synthesis
tags: [time-horizon, swing, holding-period, philosophy]
title: Time Horizons — 1m / 3m / 6m / 12m
author_role: human
---

# 01 · Time Horizons

Sharks operates in **four discrete swing buckets**. A position is opened into exactly one bucket and may be promoted (e.g. 3m → 12m) only after thesis re-confirmation.

| Bucket | Typical trigger | Exit dominant | Default size cap |
|---|---|---|---|
| **1m (tactical breakout)** | strategy B + sector resonance | TD-9 + volume divergence, or 20MA break | tier1 4% / tier2 3% / tier3 2% |
| **3m (catalyst swing)** | supply-chain bottleneck + earnings catalyst confirmed | catalyst invalidation, time stop at 4.5m | tier1 6% / tier2 4% / tier3 3% |
| **6m (cycle position)** | cycle-resonance bottom + macro regime shift | trailing 60MA, or regime breakdown | tier1 8% / tier2 5% / tier3 — |
| **12m (core thesis)** | structural narrative (e.g. AI capex cycle) + quarterly fundamentals confirm | thesis falsification only | tier1 8% / tier2 5% / tier3 — |

## The 「半年調整 / 兩個月上漲」 cycle

The constitution ([[sharks]] section on cycle-resonance) names the empirical regularity that drives the 6m bucket: roughly six months of correction followed by two months of advance. This is implemented as a **cycle detector** in [[concepts/cycle-resonance]] and gates 6m bucket entries.

Mechanics:

- The detector reads weekly closes on SPX / NDX / SOX over a rolling 8-month window.
- It looks for `(drawdown duration ≥ 22 trading weeks) ∧ (drawdown depth ∈ [10%, 30%]) ∧ (current week's low ≥ 5d trailing low for 10 consecutive sessions)`.
- When the condition fires, the 6m bucket opens for new entries for **2 weeks**, then closes regardless of fills.
- This explicitly forbids using the cycle signal to chase already-extended setups.

## Cross-bucket promotion rules

- **1m → 3m**: requires (a) the original 1m trigger held for ≥ 20 trading days without invalidation, AND (b) at least one A-grade fundamental source supporting the holding (see [[../CLAUDE#5-source-quality-grading]]).
- **3m → 6m**: requires (a) cycle-resonance still valid, AND (b) the 3m position has appreciated ≥ 1.5× its initial volatility band.
- **6m → 12m**: requires explicit human approval. Risk Officer cannot auto-promote.

## Hard limits

- **No single position older than 14 months** without thesis re-ratification. Stale positions corrupt regime awareness.
- **No bucket may exceed 40% of total exposure** — diversification across horizons is a feature, not an accident.
- **All buckets pause new entries** when [[08-risk-and-position]] max-DD halt fires.

## Anti-pattern: "I'll just hold it longer"

The most common time-horizon drift is promoting a failing 1m breakout to a 3m hold "because I still believe in it". This is `[[concepts/separation-mind]]` masquerading as conviction. The rule: **a bucket promotion requires fresh, dated evidence**, not absence of disconfirmation.
