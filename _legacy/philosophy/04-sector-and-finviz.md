---
type: synthesis
tags: [finviz, sector, screener, data-snooping, philosophy]
title: Finviz Filter Philosophy + Walk-Forward Guard
author_role: human
---

# 04 · Sector Rotation + Finviz Filter Philosophy

Codex review point #5 flagged Finviz-style screening as the system's biggest data-snooping risk. This page is the structural defence.

## The screener is a classifier, not a stock-picker

A Finviz filter pass tells you **what category a stock currently belongs to** — "in the top decile for 5d sector inflow", "within 8% of 52w high", "above 200MA". It does **not** tell you the stock is a good entry. The decision still requires the four-dimension arbitration in [[02-signal-taxonomy]].

In practice this means:
- A filter pass earns a stock a slot in the **candidate pool**, not in `outputs/picks-*.json`.
- The Compiler aggregates filter passes into `wiki/03_alpha_library.md` with the `as_of_timestamp` recorded.
- The Risk Officer cross-references the filter result against the four-quadrant taxonomy ([[03-long-short-taxonomy]]) before approving.

## The three rules against data-snooping

These exist because price-derived features in any swing screener are highly correlated, and naive multi-filter scoring will silently double-count.

### Rule 1 — Walk-forward train/val/test partition
- Every filter that informs a position must be backtested on:
  - **Train**: 60% of available history (chronological, oldest first)
  - **Val**: 20% (used for filter-threshold tuning)
  - **Test**: 20% (held out, used once at promotion-to-production)
- A filter that beats `SPY * 1.05` on train + val + test may be promoted. A filter that beats only train+val is suspect and goes to a 12-month forward-test before promotion.
- Codified in `backtest/README.md` (Phase 4).

### Rule 2 — Correlated price-features count as one
- All of the following are **price-derived** and form a single feature family:
  - 20MA / 60MA / 200MA crossovers
  - Bollinger band touches
  - Distance from 52w high
  - Donchian channel breakouts
  - Daily / weekly RSI
- At most **one** member of this family contributes to the score per ticker. The screener may pre-filter on multiple, but only one enters the final weighted score.

### Rule 3 — No re-derivation of thresholds on the test set
- If a backtest reveals a filter underperforms on the test set, the response is to **archive the filter** (and the hypothesis), not to retune until it passes.
- This is the most violated rule in retail quant. The Risk Officer should reject any submitted filter whose `wiki/04_backtest_log.md` entry shows threshold revisions after the test split was opened.

## Phase 1 initial filter set

For Phase 2 implementation, the system starts with five filters. Each maps to a four-dimension origin so its scoring is unambiguous.

| Filter | Dimension | Threshold (initial) | Source |
|---|---|---|---|
| 20MA × 60MA golden cross (today) | Technical | crossover within ≤ 3 days | yfinance |
| Distance from 52w high | Technical | `≤ 10%` | yfinance |
| Sector 5d net inflow rank | News (sector-flow proxy) | top 3 of 11 sectors | Finviz screener |
| Bollinger upper-band touch with volume | Technical | touch + volume > 1.3× 20d avg | yfinance |
| Sales QoQ growth | Fundamental | `> 15%` AND gross margin expanding | Finnhub fundamentals |

Per Rule 2, only one of `golden cross / distance-from-52w-high / Bollinger touch` contributes to the final score on any given ticker. The Compiler picks the strongest per row.

## Sector buckets — sector rotation hooks

Codex review point #10 (Mag 7 concentration) is addressed in `watchlist/universe.yaml` via the `sector_buckets` block. Sectors that are disabled by default but enabled when [[01_macro_state]] flags a rotation:

- `defensive_staples` — enable when SPX 200MA breaks down with VIX > 25
- `rate_sensitive` (utilities, REITs) — enable when Fed pivot probability > 60% per Polymarket / Fed funds futures
- `energy` — enable on geopolitical disruption signal (Gemini's "supply chain crisis" path)
- `financial` — enable when 10y / 2y spread re-steepens
- `biotech_small` — enable when XBI / IBB outperforms SPX over 60d
- `defense` — enable on persistent geopolitical premium (always-on watch, position only on entry trigger)

Each sector bucket has a `weight_cap` in `universe.yaml` that caps its share of the active portfolio.

## What this does not solve

This page constrains data-snooping at the **filter** level. It does **not** prevent narrative-driven cherry-picking. That cognitive failure is checked by [[sharks]] (the constitution) and the four-quadrant routing in [[03-long-short-taxonomy]]. Filters are necessary but not sufficient.
