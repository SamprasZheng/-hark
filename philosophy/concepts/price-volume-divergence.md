---
type: concept
tags: [price-volume, divergence, contraction, technical, andy-principle]
title: Price-Volume Divergence (價量背離 / 縮量也不下跌)
author_role: human
---

# Price-Volume Divergence (價量關係)

The core technical concept derived from [[../../sharks]] principles 5 (魚缸生態) and the bottoming-pattern section on "縮量也不下跌" (volume contracts but price holds).

## The two divergence types we trade

### Bullish divergence — volume dry-up at bottom
- Price has declined for ≥ 4 weeks
- 5d_avg_volume / 60d_avg_volume ratio drops below 0.7 over the last 5 sessions
- Despite the volume drop, daily lows hold within ≤ 2% of a prior swing low
- **Interpretation**: selling pressure exhausted; absent buyers, absent sellers; staging zone for next cycle ([[cycle-resonance]])
- **Action**: stage long entries in the 6m bucket; do NOT yet open positions — wait for first volume-expansion bar that breaks the down-trend line

### Bearish divergence — volume dry-up at top
- Price within 5% of 52w high
- 5d_avg_volume / 60d_avg_volume ratio drops below 0.7
- New incremental highs achieved on lower volume than the prior swing high
- Sentiment z-score remains > 2 (social media chatter still elevated despite waning institutional interest)
- **Interpretation**: late-stage 多頭虛漲 ([[../03-long-short-taxonomy]]); institutional distribution into retail enthusiasm
- **Action**: trim longs; via [[td-9-sequential]] sell + volume contraction, allow Put-only short entry

## The "no decline on contracting volume" tell

The [[../../sharks]] section explicitly: "縮量也不下跌" is a **bottom characteristic**. The market has run out of sellers — not because demand has returned, but because supply is exhausted. The next rally requires fresh demand and is therefore not yet present, but the downside risk has compressed dramatically.

This is the **single most important regime signal** in the system's framework for cycle-resonance ([[cycle-resonance]]) bottoming. The 6m bucket entry trigger requires this specific divergence pattern.

## How it interacts with the four-dimension matrix

Per [[../02-signal-taxonomy]]:
- Price-volume divergence is a **Technical** dimension signal
- Alone, it cannot exceed 30% of bucket cap (Technical-only rule)
- The 6m bucket cycle-resonance trigger gives it primary status only when combined with a macro regime change (News dimension)

## Implementation hooks

Phase 2 implementation in `src/sharks/scoring/price_volume.py`:
- `is_volume_dryup(ticker, lookback_days=5, reference_days=60, threshold=0.7) -> bool`
- `is_bearish_divergence(ticker) -> Optional[float]` returns confidence score
- `is_bullish_divergence(ticker) -> Optional[float]` returns confidence score

The thresholds (0.7 ratio, 5/60 windows, 2% swing-low tolerance) are the Phase 1 defaults. Phase 4 backtest may tighten / loosen via the train/val/test discipline of [[../04-sector-and-finviz]] Rule 1 — never on test alone.

## Anti-pattern: "the volume looks weak, this must be a top"

Volume-only narratives without price-structure context are noise. The divergence concept requires **both** the volume signal AND the price-structure signal (holding at low, OR new high on lower volume) before it counts. Single-side volume opinions are not trades.
