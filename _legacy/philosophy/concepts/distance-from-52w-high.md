---
type: concept
tags: [52w-high, momentum, distance, technical, regime]
title: Distance from 52-Week High
author_role: human
---

# Distance from 52-Week High

The percentage gap between current close and the trailing 252-trading-day high. Phase 1 Finviz filter set includes this as a primary momentum gate.

## Calculation

```
distance_from_52w_high = (52w_high - close) / 52w_high
```

A close at the 52w high → distance = 0. A close at 50% below the 52w high → distance = 0.5.

## How Sharks uses it

### Strategy B (primary use)
Per [[../10-strategies]]:
- **Trigger**: `distance_from_52w_high ≤ 0.08` (within 8% of the 52w high)
- This identifies stocks in a momentum regime — those near new highs are systematically more likely to extend than mean-revert (the "momentum factor" of academic finance)

### Strategy A (negative-side use)
- A Strategy A consolidation is a **bullish** setup when distance is in `[0.10, 0.30]` — close enough to the high to be in a trend, far enough to have a sustained consolidation phase. Distance > 0.30 suggests a deeper drawdown that needs different framing.

### Regime detection
- Cross-sectional: when `> 40%` of S&P 500 components have `distance_from_52w_high ≤ 0.10`, the broad market is in a momentum regime. The cycle-resonance trigger ([[cycle-resonance]]) is typically NOT in play in this regime.
- When `< 15%` of components are within 10% of the 52w high, the broad market is in a value / bottoming regime. Cycle-resonance more likely activates.

## Why this works as a filter

The empirical pattern is robust across decades and markets: stocks near 52-week highs outperform on a 1-12 month horizon. Two structural reasons:

1. **Reference price anchoring**: institutional portfolio managers are reluctant to sell positions at or near their highs (the "anchor effect"). Selling pressure is lower than at any other technical zone.
2. **Momentum capital flows**: ETFs that track momentum indices (MTUM, etc.) systematically buy stocks near 52w highs, providing flow that is independent of the underlying thesis.

## The correlated-features rule

Per [[../04-sector-and-finviz]] Rule 2, this filter is in the **price-derived feature family**. Only one of `golden-cross / bollinger / distance-from-52w-high / Donchian` may contribute to the score per ticker. The Compiler routes Strategy B selections through distance-from-52w-high preferentially.

## Common failure mode

A stock can be within 8% of the 52w high because it has run from a much higher level — e.g., NVDA in mid-2022 was within 30% of its all-time high but was in a sustained drawdown. The filter must use 52w (252-trading-day) high, NOT all-time high.

Phase 4 backtest must verify the filter using strictly 252-day windows with point-in-time discipline ([[../09-point-in-time]]).

## Implementation

Phase 2 implementation in `src/sharks/scoring/distance.py`:
- `distance_from_52w_high(ticker, as_of) -> float`
- The `as_of` parameter is mandatory and enforced — the high must be the high *as known* at `as_of`, not the high revealed by future data.
