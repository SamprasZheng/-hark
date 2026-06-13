---
type: concept
tags: [bollinger, volatility, breakout, technical]
title: Bollinger Bands
author_role: human
---

# Bollinger Bands

20-period moving average ± 2 standard deviations. Used here primarily as a Strategy B momentum trigger and as a volatility-regime tell.

## Standard definition

- `BB_mid = MA20`
- `BB_upper = MA20 + 2 * stdev(close, 20)`
- `BB_lower = MA20 - 2 * stdev(close, 20)`
- `BB_width = BB_upper - BB_lower` (volatility proxy)

## How Sharks uses it

### Strategy B (primary use)
- **Trigger condition**: close > `BB_upper[t]` on volume > 1.3 × prior-20d average
- The Strategy B ([[../10-strategies]]) spec uses Bollinger upper-band touch as one of two parallel technical triggers (the other being distance-from-52w-high). Per [[../04-sector-and-finviz]] Rule 2, only one of them contributes to the score on any given ticker — the Compiler picks whichever fires stronger.

### Mean-reversion entry (Strategy A modifier)
- Inside a Strategy A consolidation, a touch of `BB_lower` on volume contraction (per [[price-volume-divergence]]) suggests the consolidation lower bound is holding. This is a **timing input**, not a separate trade.

### Volatility regime
- `BB_width / BB_mid` (normalised width) is tracked at the index level (SPX) as a regime indicator. Values:
  - **< 5%**: low-vol regime, compression. Strategy A consolidations more common; Strategy B momentum harder.
  - **5–10%**: normal regime.
  - **> 15%**: high-vol regime. Couple with VIX > 25 → [[../07-mode-switch]] force-low-freq.

## The "squeeze" interpretation

When `BB_width` compresses to its 12-month low, a subsequent breakout in either direction is conventionally considered high-conviction. Sharks treats this as a **filter pass**, not a directional signal — direction must come from the news or fundamental dimension.

## Implementation notes

- Phase 2 implementation in `src/sharks/scoring/bollinger.py`
- Inputs: OHLCV daily bars from `yfinance_client` (EOD) or `polygon_client` (historical backtest)
- The standard parameters (20-period, 2σ) are the Phase 1 defaults. Phase 4 may experiment with 14-period 2σ or 20-period 1.5σ for tier-3 mid-caps, but any change must pass the train/val/test discipline of [[../04-sector-and-finviz]] Rule 1.

## Anti-pattern: "price touched the band, so it's overbought / oversold"

Bollinger bands describe distribution percentiles, not exhaustion. In a strong trend, price can ride the upper band for weeks — this is **the** Strategy B setup, not a sell signal. Combine with [[td-9-sequential]] and [[price-volume-divergence]] for the exit timing, not Bollinger touches alone.
