---
type: concept
tags: [last-snow, macro-divergence, capitulation, andy-principle, bottom-pattern]
title: The Last Snow (最後一場雪) — macro-bearishness at the structural bottom
author_role: human
---

# The Last Snow (最後一場雪)

[[../../sharks]] section on bottom identification: "最後一場雪" describes the macro-bearish atmosphere that often peaks **at** the structural bottom, not before it. The press headlines are uniformly negative, Fed officials sound hawkish, economists call for recession — yet the price action begins to refuse new lows.

## What we're trying to formalise

The retail-trader pattern: confidence bottoms at the same moment as price. By the time the macro narrative is unambiguously bearish, the structural buyers (long-horizon institutions, value funds, sovereign wealth) have already begun absorbing supply. The "last snow" is the last gust of bearish sentiment before the regime change.

## The detection signature

The Last Snow regime is suspected when ALL of the following hold over a 4-8 week window:

- Macro-bearish news flow at peak intensity (Fed hawkish + 衰退 talk in mainstream media + earnings guides down across multiple sectors)
- Yet [[price-volume-divergence]] bullish divergence is firing across the index level
- VIX is **falling** despite continued bearish headlines (the most subtle and important tell)
- Credit spreads (HY OAS) have stopped widening despite ongoing macro pessimism
- High-quality companies miss earnings but **don't sell off** (the absorption tell)

## How it interacts with [[cycle-resonance]]

The Last Snow regime is **necessary but not sufficient** for a cycle-resonance trigger. Cycle-resonance can fire without Last Snow conditions (early bear-rally setups). Last Snow without cycle-resonance is a warning sign that we are approaching but not yet at the entry window — staging mode.

When both fire simultaneously, the 6m bucket is given priority allocation:
- Standard cycle-resonance: 6m bucket up to 30% of portfolio
- Cycle-resonance + Last Snow co-occurrence: 6m bucket up to 35% of portfolio (the extra 5% acknowledges the higher historical conviction of co-occurrence setups)

## Historical Last Snow moments

The Compiler logs each instance to `wiki/03_alpha_library.md`:

- 2009 March (peak bearishness coincided with the structural bottom)
- 2020 late March (Fed pivot day printed amid peak Covid panic)
- 2022 October (CPI shock day; SPX low printed within 2 weeks of consensus calling for further drops)
- 2023 January (recession-talk peak; SPX rallied 25% over next 7 months)
- (future instances tracked prospectively)

## What separates Last Snow from a regular bear-market rally

The retail conflation: every counter-trend rally feels like it could be "the bottom". The discipline:

- **Bear-market rallies**: macro headlines flip transiently bullish, price runs hard, then headlines deteriorate again. Failure mode: chasing the rally late.
- **Last Snow**: macro headlines remain bearish, price refuses to make new lows, volume contracts, vol eases. The setup is **invisible** to headline-driven retail because the headlines are still scary.

The four-dimension matrix in [[../02-signal-taxonomy]] is the structural defence: sentiment-bullish-only rallies fail the gating (sentiment alone never opens a position). Last Snow setups, by contrast, are technical + fundamental convergence WITHOUT sentiment support — the cleanest possible entry.

## The "narrative shift" tell

The Compiler tracks media narrative as a dimension (in [[../02-signal-taxonomy]] News). When the dominant narrative remains bearish but the **frequency** of new bearish headlines decreases week-over-week despite no improvement in underlying data, this is the narrative-exhaustion tell. It does not by itself open positions, but it weights the Last Snow detection upward.

## Trading the Last Snow

Position construction:
- **Pre-window**: tier1 Mag 7 only, capped at 50% of standard tier1 cap. Staging entries on the bullish-divergence bars per [[price-volume-divergence]].
- **Window open** (when cycle-resonance fires): scale up to standard cap; add tier2 supply-chain positions
- **Window close**: positions held under standard [[../08-risk-and-position]] invalidation rules; no special treatment

## What this is NOT

- **NOT a permission to be a permabull**. The Last Snow framework explicitly requires bearish macro coupled with structural-form bullishness. If the macro is mildly bearish and the structure is mildly bullish, this is not Last Snow — just market noise.
- **NOT a contrarian indicator on its own**. Without [[cycle-resonance]] co-occurrence, Last Snow is "directional warning" only — staging mode, not full entry.
- **NOT applicable to single tickers**. Last Snow is an index / regime concept. Individual-name entries still follow the four-dimension matrix at the ticker level.

## Implementation handoff

Phase 3: implement Last Snow detection in `src/sharks/regime/last_snow.py`. Returns a `LastSnowState` with confidence score in `[0, 1]` and the qualifying conditions.

The macro-narrative input is the hardest piece — the Compiler ingests headlines from `raw/macro/` and produces a weekly narrative-tone score. Phase 3 will replicate this for backtest using historical news archives (Phase 4 acceptance: at least the 5 historical instances above must score `LastSnow_confidence > 0.6` within ±2 weeks of their canonical date).
