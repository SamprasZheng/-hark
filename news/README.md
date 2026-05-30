# news/

Phase 2+ home for the news ingestion pipeline configuration.

## Phase 1 status

Empty placeholder. The Phase 2 implementation lives in `src/sharks/data/finnhub_client.py` (news API), `src/sharks/agents/macro_intel.py` (Macro SubAgent borrowing from OpenClaw), and `src/sharks/agents/kol_intel.py` (KOL SubAgent).

Outputs from these ingestion modules go to `raw/macro/` and `raw/kol_signals/`.

## What goes here in Phase 2

`news/` holds **configuration**, not data and not code:

- `news/sources.yaml` — list of source URLs, RSS feeds, KOL handles, with source-grade tags (per `CLAUDE.md` §5)
- `news/kol_watchlist.yaml` — tracked KOL accounts on X / Telegram / YouTube + per-account confidence weight (initial weight from track record; updated by the Authentic Market Feedback scoring from Phase 4)
- `news/macro_calendar.yaml` — known event dates (FOMC, CPI, NFP, earnings; populated by Finnhub earnings calendar pull + manual additions for non-scheduled risk events)
- `news/cadence.yaml` — polling cadence per source class (e.g., Fed: hourly during FOMC week, daily otherwise; KOL: every 4 hours during US market hours)

## Cadence design

Per [[../philosophy/07-mode-switch]]:
- **low mode (default)**: news polled hourly, KOL feeds polled every 4 hours
- **high mode**: news polled every 15 min, KOL feeds polled every 30 min (use with caution — high mode has VIX-band and other gates)

## Point-in-time discipline

Per [[../philosophy/09-point-in-time]]:
- Every ingested article is split by claim
- Each claim carries its own `source_first_visible_at` (the publication time)
- Claims that arrive > 2h after their `source_first_visible_at` are flagged `stale: true` and used only as evidence-update, not as fresh-signal trigger

## See also

- [[../CLAUDE]] §5 — source quality grading
- [[../philosophy/09-point-in-time]] — release-time normalisation
- [[../philosophy/02-signal-taxonomy]] — how news scores integrate into the four-dimension framework
- [[../docs/ROADMAP]] — Phase 2 plan
