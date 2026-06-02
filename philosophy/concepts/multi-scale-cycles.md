---
type: concept
status: proposal
tags: [cycles, multi-scale, macro, framework, proposal]
title: Multi-Scale Cycles — proposal
author_role: compiler
proposed_destination: philosophy/concepts/multi-scale-cycles.md
proposed_at: 2026-05-29T03:30:00-04:00
---

# Multi-Scale Cycles (PROPOSAL)

> Draft proposal. Human approval required to move to `philosophy/concepts/multi-scale-cycles.md`.

## Definition

Three structural cycles operate on US equity decisions and must be considered together:

1. **BTC 4-year halving cycle** — global liquidity proxy + risk-on signal
2. **US Presidential 4-year cycle** — political-business cycle (Y1/Y2/Y3/Y4)
3. **Annual seasonality** — calendar effects (best 6m / worst 6m)

A fourth scale — **sector-monthly seasonality** — operates as a modifier on individual ticker sizing once the three macro-scale cycles have set the regime.

## Why this needs its own concept page

The system's existing [[cycle-resonance]] concept only addresses Fed-rate-driven cycles. The principal directive 2026-05-29 ([[../../raw/macro/principal-cycles-2026-05-29]]) demands a broader framework that captures political, crypto, and seasonal cycles independently from Fed regime.

## The aggregation rule

Each ticker carries four cycle-position scores in `[-1, +1]`:

```
btc_cycle_bias   ∈ [-1, +1]   # +1 = early cycle bull, -1 = late cycle bear
political_bias   ∈ [-1, +1]   # +1 = Y3 pre-election, -1 = Y2 midterm
calendar_bias    ∈ [-1, +1]   # +1 = Nov-Apr, -1 = May-Oct (Sep -1)
sector_bias      ∈ [-1, +1]   # ticker-specific monthly seasonal mean
```

`combined_cycle_bias = mean(btc_cycle_bias × w_btc, political_bias × w_pol, calendar_bias × w_cal, sector_bias × w_sec)`

Where weights default to `[0.15, 0.30, 0.30, 0.25]` (political and calendar dominate).

The aggregate bias scales position size in [[../05-decision-rubric]]:

`actual_size = standard_size × (1 + combined_cycle_bias × 0.4)`

Range: 60% to 140% of standard size based on cycle alignment.

## Detailed scale-by-scale

(See full empirical numbers in [[../../wiki/06_cycle_framework]].)

### BTC halving cycle

- Months 0-12 post-halving: `btc_cycle_bias = -0.2` (range-bound staging)
- Months 12-20 post-halving: `+0.8` (cycle uptrend)
- Months 20-30 post-halving: `0.0` (peak window — flag exit, not entry)
- Months 30-42 post-halving: `-0.6` (bear market — staging)
- Months 42+: `+0.4` (pre-halving accumulation)

### Presidential cycle

- Y1: `+0.6` (historical +17% mean)
- Y2 (midterm): `-0.4` until mid-October, then `+0.8` (post-midterm bounce)
- Y3: `+0.7` (historical +16% mean, 80% positive)
- Y4: `+0.2` (mixed; election uncertainty + post-election clarity)

### Calendar seasonality (SPX)

- Nov, Dec, Apr, May, Jul: `+0.5 to +0.7`
- Sep: `-0.6`
- Aug, Oct: `-0.2 to +0.1`
- Other: `0.0 to +0.3`

### Sector seasonality

Per-ETF; some highlights:
- XLK Jul: `+0.8`
- SOXX May: `+0.8`
- XHB Nov: `+0.9` (90% hit rate)
- TAN Jan: `+0.7`
- HERO Nov: `+0.7`
- Most sectors Sep: `-0.4 to -0.6`

## Operational integration

- Phase 3 implementation: `src/sharks/regime/cycle_bias.py`
- `wiki/01_macro_state.md` includes a current-position read for each scale
- Risk Officer reads combined_cycle_bias before approving any signal slot

## Discipline reminder

This is a **bias** modifier, not a trigger. A negative combined_cycle_bias doesn't generate short signals; it scales down long position sizing. Per [[../02-signal-taxonomy]] gating, signal triggers still require the four-dimension framework.

## See also

- [[../../wiki/06_cycle_framework]] — full empirical data + verification
- [[../concepts/cycle-resonance]] — existing rate-cycle detector
- [[../08-risk-and-position]] — sizing rules (target for integration)
