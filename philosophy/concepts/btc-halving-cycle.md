---
type: concept
status: proposal
tags: [btc, bitcoin, halving, 4-year-cycle, crypto, proposal]
title: BTC 4-Year Halving Cycle — proposal
author_role: compiler
proposed_destination: philosophy/concepts/btc-halving-cycle.md
proposed_at: 2026-05-29T03:30:00-04:00
---

# BTC 4-Year Halving Cycle (PROPOSAL)

> Draft proposal. Human approval required.

## Historical pattern (verified by monthly closes)

| Halving | Date | Cycle peak (months post-halving) | Peak return from halving | Bottom date | Bottom DD from peak |
|---|---|---|---|---|---|
| h2012 | 2012-11-28 | 2014-09 (~22m) | ~10× pre-data; peak ~$1,100 | 2015-01 | ~-85% |
| h2016 | 2016-07-09 | 2017-12 (17m) | +2,360% | 2018-12 | ~-84% |
| h2020 | 2020-05-11 | 2021-10 (17m) | +572% | 2022-11 | ~-77% |
| h2024 | 2024-04-19 | 2025-07 (15m) | +72% (peak so far) | TBD (projected 2026-Q4) | -37% to 2026-05 |
| h2028 | ~2028-04 (est.) | — | — | — | — |

## Diminishing returns

Each cycle's peak multiple has compressed:
- h2016: 24× from entry
- h2020: 6.7× from entry
- h2024 to date: 1.7× from entry

This is consistent with the broader analyst consensus ("4-year cycle weakening, not broken"). ETF flows + institutional adoption dampen amplitude; pattern timing remains but magnitude compresses.

## Phases within the cycle

### Phase A (months 0-12 post-halving): range-bound staging
- Reduced supply not yet biting demand
- Sideways action common
- Bias: neutral to slightly bearish (`-0.2`)

### Phase B (months 12-20 post-halving): cycle uptrend
- Supply constraint meets demand
- Historically the strongest phase
- Bias: strongly positive (`+0.8`)

### Phase C (months 18-24 post-halving): peak window
- Distribution to retail
- Sentiment z-score maxes
- Bias: neutral but **exit-signal sensitive** (`0.0`)
- Action: Strategy B exit triggers per [[td-9-sequential]]

### Phase D (months 24-38 post-halving): bear market
- Drawdowns 70-85% historically (compressing each cycle)
- Bias: bearish; staging for next halving (`-0.6`)
- Action: cash + selective accumulation

### Phase E (months 38-48 post-halving): pre-halving accumulation
- Smart money positioning
- Volatility compression
- Bias: positive (`+0.4`)

## Current cycle (h2024) position

- **+25 months since halving** as of 2026-05
- Peak printed at +15m (2025-07 monthly close $115,758)
- Currently -37% from peak
- **Phase D (bear market)** — bottoming window 2026-Q4 to 2027-Q1
- **NOT yet Phase E** — no accumulation signal until late 2027

## Operational use

### For crypto positions (Strategy C):
- Phase A/E: stage long via `ccxt_client` with strict TD-9 + volume validation
- Phase B: full position; ride trend
- Phase C: trim 30-50% on TD-9 sell + volume contraction
- Phase D: NO new longs; existing positions exit on +30% bounce
- The system is NOT a BTC pure-play; max BTC notional 4% of portfolio per [[../06-exclusions]]

### For equities (risk-on / risk-off proxy):
- BTC cycle bias contributes to `combined_cycle_bias` per [[multi-scale-cycles]]
- Phase D coincides historically with risk-asset volatility — discounts tier 2/3 cap
- Phase B coincides historically with risk-on melt-ups — supports full tier 2/3 caps

## Open question — cycle invalidation

If h2024 fails to print a meaningful bear market (no Phase D drawdown > 50% from peak), the 4-year halving cycle is materially invalidated. The Compiler tracks this as a falsification test:

- **Falsification trigger**: BTC closes above $115,758 (2025-07 peak) within 36 months of h2024 halving (i.e., by 2027-04) — without a prior >50% drawdown
- **If falsified**: deprecate this concept; BTC cycle bias contribution reduced to 0 in the multi-scale framework

## See also

- [[../../wiki/06_cycle_framework]] §1 — full empirical data
- [[multi-scale-cycles]] — broader framework
- [[../03-long-short-taxonomy]] — quadrant routing for crypto positions
- [[../10-strategies]] — Strategy C for crypto whale-tracking
- [[../../raw/macro/principal-cycles-2026-05-29]] — principal directive source
