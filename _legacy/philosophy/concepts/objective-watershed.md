---
type: concept
tags: [watershed, support-resistance, mechanical-rule, andy-principle]
title: Objective Watershed (客觀分水嶺)
author_role: human
---

# Objective Watershed (客觀分水嶺)

[[../../sharks]] principle 6: set a specific price level (a "watershed") and let the side of the line drive the bias. Above the line, lean long. Below, lean short or flat. No prediction; just observation of which side of the line price closes on.

## Why this concept matters

Most retail loss patterns trace back to "I think the bottom is in" or "this can't go any higher" — predictions based on hope, not on price. The watershed rule removes the prediction entirely.

The structure: pick a meaningful level **before** the trade is live. The level becomes the binary observer. Price either holds it or doesn't. Action follows mechanically.

## What counts as a meaningful watershed

The system uses three classes of watersheds, each with specific qualification rules:

### 1. Structural support / resistance
- Prior swing high or swing low of a substantive consolidation (> 4 weeks)
- Round-number psychological levels for large-cap names (NVDA $500, AAPL $200) — only used as a secondary check; not primary
- Sector ETF inflection (e.g. SOXX's 200MA acting as watershed for the chip sector)

### 2. Volume Profile node
- High-volume node within the relevant N-day window where price has spent the most time
- Acts as a magnet on retracements; a clean break with volume confirms direction

### 3. Long moving averages (regime watersheds)
- 200MA at the index level (SPX, NDX) — the regime watershed for entire portfolio bias
- 200MA at the sector-ETF level — regime for the sector bucket
- 60MA at the individual-ticker level — regime for the position within a Strategy A or B trade

## How the watershed gates action

For each position-level decision in `wiki/positions.md`:

- **Above the watershed**: long bias allowed; Strategy A & B entries unblocked
- **Below the watershed**: long bias suspended; no new long entries on the ticker
- **Crossing down**: existing long position triggers a `review for trim` flag (Risk Officer evaluates against [[../08-risk-and-position]] catalyst-invalidation rule)
- **Crossing up**: short positions trigger a `review for cover` flag

The rule is **observation-based, not interpretation-based**. "Price tested the level and held" is observation. "I think the level will hold" is prediction — not allowed.

## Combining watersheds

When the index watershed disagrees with the ticker watershed (e.g. SPX below 200MA but NVDA above its 60MA), the more-restrictive bias wins:
- Index above + ticker above → standard size
- Index above + ticker below → no new ticker longs
- Index below + ticker above → ticker longs allowed only at 50% of standard cap
- Index below + ticker below → no new ticker longs; existing position evaluated for exit

## The interaction with cycle-resonance

When [[cycle-resonance]] activates the 6m bucket entry window, the watershed for that bucket is the **trailing 12-month low + 1 ATR(20)**. Crossing this level downward invalidates the cycle-resonance entry; crossing above it confirms.

## Implementation handoff

Phase 3 will implement watershed evaluation in `src/sharks/scoring/watershed.py`:
- `ticker_60ma_watershed(ticker, as_of) -> WatershedState`
- `sector_200ma_watershed(sector, as_of) -> WatershedState`
- `index_200ma_watershed("SPX" | "NDX", as_of) -> WatershedState`
- The `WatershedState` enum: `above_strong / above_weak / at / below_weak / below_strong`

The Risk Officer reads the composite watershed state on every position-followup slot.

## Anti-pattern: moving the line

The single most common violation: a position is opened with watershed at $X, price closes below $X, and the trader rationalises "$X-1 is the real level". This is `[[separation-mind]]` masquerading as analysis. The rule: watersheds are committed **before** the position, in writing, in `wiki/positions.md`. Adjusting them mid-trade requires a deliberate edit with a `wiki/log.md` entry — and the Risk Officer reviews that entry skeptically.
