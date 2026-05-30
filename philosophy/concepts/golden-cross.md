---
type: concept
tags: [golden-cross, ma-crossover, 20-60ma, technical]
title: Golden Cross (黃金交叉)
author_role: human
---

# Golden Cross (黃金交叉)

The 20-day moving average crossing above the 60-day moving average on a daily chart.

## Calculation

- `golden_cross_today = (MA20[t] > MA60[t]) AND (MA20[t-1] <= MA60[t-1])`
- The mirror — `death cross` — is the same condition with inequality flipped, used as exit confirmation for Strategy A and B longs.

## Where Sharks uses it

- **Strategy A** ([[../10-strategies]]): the consolidation-breakout trigger requires the close to clear the consolidation band on volume. Golden cross is a **co-incident confirmation**, not the primary trigger.
- **Strategy B** ([[../10-strategies]]): golden cross within the prior 10 trading days is a momentum-regime input; combined with distance-from-52w-high and sector resonance.
- **Death cross**: triggers a "review for trim" flag on existing Strategy A positions (50% trim consideration), and a "hard exit" rule on Strategy B positions when combined with [[td-9-sequential]] sell.

## The correlated-features rule

Per [[../04-sector-and-finviz]] Rule 2, golden cross is in the **price-derived feature family** along with Bollinger touches, distance from 52w high, and Donchian breakouts. **Only one** member of the family contributes to a single ticker's score.

In practice the Compiler chooses based on the strategy:
- Strategy A → distance-from-platform (which is a derivative of consolidation, not 52w high)
- Strategy B → distance-from-52w-high preferred (cleaner momentum signal); golden cross is a tie-breaker

## Common failure mode

Golden cross alone is a notoriously lagging signal. In a slow-grinding range, it can fire and reverse multiple times in 30 days, generating whipsaws. The system's defence:

- The cross must hold for ≥ 3 trading sessions before counting as confirmed
- Combined with at least one other dimension's signal per [[../02-signal-taxonomy]] gating

## What Andy uses this for (vs. mainstream)

Mainstream usage treats golden cross as a primary entry. Sharks demotes it to a **confirmation overlay**. The thesis comes from fundamentals or news; the moving averages confirm or invalidate the timing.
