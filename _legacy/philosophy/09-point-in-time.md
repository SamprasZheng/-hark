---
type: synthesis
tags: [point-in-time, as-of, lookahead, backtest-integrity, philosophy]
title: Point-in-Time Discipline + Release-Time Normalisation
author_role: human
---

# 09 · Point-in-Time

Resolves codex review points #1 (no `as_of_timestamp` constraint) and #6 (news/KOL hourly summary time-leak risk). These are **Critical**: a system that fails this discipline produces backtests that look brilliant and live results that bleed.

## The cardinal sin: lookahead bias

If a 2024 backtest references a stock's 2025 sector classification, or applies today's earnings-date calendar to a 2022 trade, the result is fiction. Every wiki page that is later consumed by a backtest, screener, or LLM-driven analysis MUST be **time-stamped at the moment of first availability**, not at the moment of ingest.

## The `as_of_timestamp` contract

Every wiki page that originates from a `raw/` source carries frontmatter:

```yaml
---
type: ...
as_of_timestamp: 2026-05-28T13:30:00-04:00   # when this info first became publicly knowable
ingested_timestamp: 2026-05-28T19:45:00-04:00 # when our system actually read it
source_paths:
  - raw/macro/fed-statement-2026-05-28.md
source_first_visible_at: 2026-05-28T14:00:00-04:00
---
```

Rules:
- `as_of_timestamp` ≤ `source_first_visible_at` ≤ `ingested_timestamp`. Violated → page is invalid.
- A page that aggregates multiple sources uses the **latest** `source_first_visible_at` as its `as_of_timestamp`.
- Any agent writing without these fields commits a P0 violation. The Risk Officer rejects on read.

## Source-type rules

| Source class | `as_of_timestamp` rule |
|---|---|
| SEC filing (10-Q, 10-K, 8-K) | EDGAR filing receipt time (UTC; convert to ET) |
| Earnings call transcript | call end time, NOT transcript-publication time |
| Fed statement | release embargo time (typically 14:00 ET on FOMC days) |
| News (Bloomberg, Reuters) | wire timestamp on the article |
| KOL post (X, Telegram) | post timestamp from the platform API; ignore retweet/republication time |
| Polymarket / prediction market | timestamp of the contract-state snapshot used |
| Finviz screener row | NYSE/Nasdaq prior-session close (since Finviz updates at EOD) |
| yfinance OHLCV bar | bar close time |

## Universe versioning

`watchlist/universe.yaml` carries `as_of:` at the top and is **versioned**. The Phase 2 implementation:

- On every edit, the previous version is snapshotted to `watchlist/history/universe-YYYY-MM-DD.yaml`.
- The Phase 4 backtest engine looks up the universe-as-of-trade-date, not today's universe.
- Sector classification, market cap band, tier assignment, and Mag 7 membership are all part of the snapshot. (Mag 7 has changed historically — e.g. Tesla joined in 2020, Meta's status was debated in early 2022.)

## Trading-session time bands

For backtest, all trades fill on the **next available bar after** the signal's `as_of_timestamp`. Specifically:

| Signal `as_of_timestamp` falls in | Fills at |
|---|---|
| Pre-market (04:00 – 09:30 ET) | regular-hours open (09:30 ET) |
| Regular hours (09:30 – 16:00 ET) | next 1-minute bar open |
| After-hours (16:00 – 20:00 ET) | next regular-hours open |
| Overnight (20:00 ET to next 04:00 ET) | next regular-hours open |

Crypto is 24/7 — fills at the next minute bar regardless. Weekend signals on US equities **queue for Monday open**.

## News and KOL release-time normalisation

The most insidious time-leak: an hourly KOL digest at 19:00 ET that references a 17:30 ET press release where the market has already moved. If the system ingests the digest at 19:00 and times the signal at 19:00, it has implicitly used **post-reaction price information** to inform a "pre-reaction" trade.

The fix:
- The Compiler must split each digest by claim. Each claim carries its own `as_of_timestamp` (the source's first-visible time, not the digest's publication time).
- Claims older than 2 hours from the digest publication time are flagged `stale: true` and are not eligible for fresh-signal generation; they may only update existing thesis evidence.
- The Phase 2 ingest pipeline runs a sanity check: any claim whose `as_of_timestamp` ≥ subsequent market price-move time is rejected with a `time-leak-suspected` error.

## Backtest lint rule

The Phase 4 backtest engine MUST enforce, at every signal-evaluation step:

```
assert max(used_source.as_of for used_source in inputs) <= trade.signal_time
```

If this assertion fails, the backtest aborts and the offending source path is logged. A passing backtest without this assertion enabled is invalid.

## The `wiki/log.md` time-stamp format

Codex named the log discipline explicitly. Every log entry starts with:

```
## [YYYY-MM-DD HH:MM ET] ingest|query|lint|recommendation|halt | <short title>
```

This makes the log greppable (`grep "^## \[" wiki/log.md`) and chronologically reliable.

## Why this is Critical (not just nice-to-have)

Two reasons:

1. **Backtest credibility**: any number this system produces — Sharpe, win rate, max DD — is meaningless if lookahead is possible. A 1.5 Sharpe with lookahead becomes 0.3 without. The gap is the deception.
2. **Live trading parity**: backtest performance can only translate to live performance if backtest inputs match live inputs at the same time. Without point-in-time discipline, the system trades against a different feature distribution in production than in test.

Codex was right to flag this as the top-priority issue. The downstream Phase 4 work is built on top of this contract.
