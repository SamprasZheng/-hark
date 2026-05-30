---
type: synthesis
tags: [exclusions, hard-rules, risk, philosophy]
title: Numerical Exclusion List
author_role: human
---

# 06 · Exclusions — Hard Numerical Filters

Codex review point #8: every exclusion in v1 was qualitative ("avoid penny stocks", "no illiquid names"), leaving grey zones that would be inconsistently applied in production. This page numerises them so the screener and the Risk Officer apply identical logic.

## Universe-level exclusions

A ticker is **immediately removed from any candidate pool** if any of the following hold:

### Price floors
- `last_close < $5` (penny exclusion)
  - **Exception list**: explicit ADRs from primary exchanges (TSM if it ever drops here, etc.). Exception list lives in `watchlist/universe.yaml` under `price_floor_exceptions`.

### Liquidity floors
- `60d_avg_dollar_volume < $5,000,000` per day
- `30d_avg_share_volume < 200,000` shares per day
- Either condition triggers exclusion; both are independent guards.

### Market cap floors
- Tier 1 (Mag 7): no floor (these are all multi-trillion)
- Tier 2 (supply chain): `market_cap < $50B`
- Tier 3 (mid-cap): `market_cap < $1B`

### Structural exclusions
- **Leveraged / inverse ETFs**: excluded by default. Allowed only when an explicit Strategy B short trade names the inverse ETF (SQQQ, SOXS, etc.) in [[10-strategies]].
- **OTC-only listings** (no primary exchange listing): excluded.
- **SPAC pre-merger** vehicles: excluded.
- **Post-IPO 90-day blackout**: excluded for the first 90 trading days after IPO.
- **Halt risk**: `halt_count_last_30_days > 1` → excluded for next 30 days.

### Optionability (for short candidates)
- A short candidate that cannot be hedged via listed options is rejected. Options must satisfy: `weekly_or_monthly_chain_present ∧ avg_daily_option_volume > 500 contracts`.

## Short-side additional exclusions

On top of the universe-level filters, a short candidate (entering via direct borrow, NOT via Put) must clear:

- `short_interest_pct_of_float ≤ 20%`
- `borrow_fee_apr ≤ 10%`
- `days_to_cover ≤ 5`
- Any of these violated → **route to Put-only**. If Put chain insufficient (above), the position is denied.

This is the iron rule from [[03-long-short-taxonomy]]. Repeated here because the Risk Officer reads this page on every decision.

## Earnings-window exclusions

Read with [[08-risk-and-position]]:

- **No new entries** within ±1 trading day of the ticker's earnings.
- **No new entries** within ±3 trading days of a tier-1 portfolio holding's earnings (because event clustering raises correlation).
- **No short via Put** within ±5 trading days of earnings on the same ticker (gamma risk).

## Macro-state exclusions

These are dynamic and resolve from [[wiki/01_macro_state]]:

- **Fed day** (FOMC release): no new entries from 1h pre-release to next session open.
- **CPI day** (8:30 ET release): no new entries until 11:00 ET same day.
- **NFP day** (first Friday): no new entries until 11:00 ET same day.
- **VIX > 35**: enter "defensive only" mode; no new long entries except tier-1 defensives (when sector bucket enabled, see [[04-sector-and-finviz]]).

## Geographic and listing-quality filters

- **PFIC**: excluded unless explicitly authorised (tax treatment is punishing).
- **Variable Interest Entity (VIE) structures** (mostly Chinese ADRs): allowed for tier-2/tier-3 only with the user's explicit per-ticker approval recorded in `wiki/log.md`. Default exclude.
- **Closed-end funds, BDCs, MLPs**: excluded from tier-1/tier-2 universe; tier-3 case-by-case.

## Verification

The screener in `src/sharks/screener/` (Phase 2) must implement this list as deterministic predicates with a single shared config file. Any drift between the screener and this page is a P1 bug.

A Phase 2 acceptance test runs the screener against `watchlist/universe.yaml` and asserts that every exclusion in this page eliminates the expected set of synthetic tickers. The test names live in `tests/test_exclusions.py`.

## Why "no penny" matters even though it's obvious

Codex's broader point: every "obvious" exclusion that isn't numerised will get violated in a moment of conviction. The numerical floor exists to make conviction-overrides require an explicit edit to this file (and a `wiki/log.md` entry explaining why), rather than a quiet typo.
