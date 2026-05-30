# raw/

Read-only ingest layer. Per Karpathy's [[../philosophy/references/karpathy-llm-wiki]] pattern, this directory holds **immutable source artefacts**. The LLM Compiler ([[../CLAUDE]]) reads from here and writes synthesised state into `wiki/`. The LLM never modifies anything in `raw/`.

## Subdirectories

- `macro/` — Fed releases, Trump-admin announcements, geopolitical news, antitrust filings
- `earnings/` — Mag 7 + supply-chain earnings call transcripts and SEC filings (10-Q, 10-K, 8-K)
- `market_data/` — EOD price/volume CSVs, Finviz screener exports, dark pool snapshots
- `kol_signals/` — KOL feed snapshots from Twitter / Telegram / YouTube transcripts

## Naming convention

Every file follows:

```
<topic-slug>-<YYYY-MM-DD>[-<source-suffix>].md       (or .csv, .json, .txt)
```

Examples:
- `raw/macro/fed-fomc-statement-2026-05-28.md`
- `raw/macro/trump-tariff-announcement-2026-06-03.md`
- `raw/earnings/nvda-2026q1-transcript.md`
- `raw/market_data/finviz-strategy-a-screen-2026-05-28.csv`
- `raw/kol_signals/x-cluster-aimomo-2026-05-28.md`

## Frontmatter (for markdown files)

```yaml
---
type: source
source_class: official_statement | sec_filing | wire_news | call_transcript | screener_export | kol_post
source_grade: A | B | C | D | E       # per CLAUDE.md section 5
source_first_visible_at: 2026-05-28T14:00:00-04:00
source_url: https://...
ingested_at: 2026-05-28T14:42:18-04:00
---
```

The `source_first_visible_at` field is **mandatory** for any file that will be referenced by a backtest or signal calculation. See [[../philosophy/09-point-in-time]].

## Immutability rules

- Files in `raw/` are **never edited** after creation. If a source is later corrected (errata in an SEC filing, a corrected transcript), create a new file with a `.v2` suffix and log the supersession in `wiki/log.md`. The original stays.
- Files may be **deleted** only for legal / takedown reasons (e.g. content removed from source by issuer). Deletion is logged with a `## [date] raw_deletion | <file> | <reason>` entry in `wiki/log.md`.

## Versioning and snapshots

`raw/` is git-tracked. The full history is recoverable via git log. Phase 2+ implementations may add `raw/manifest.csv` (auto-generated) listing all files with their hashes and timestamps for fast point-in-time queries.

## What does NOT live here

- LLM-generated summaries → `wiki/`
- Compiled state, theses, entity pages → `wiki/` or `philosophy/`
- Daily decision outputs → `outputs/`
- Code, tests, scripts → `src/`, `tests/`

## Phase 1 status

All four subdirectories created and empty (`.gitkeep` placeholders). Phase 2 begins populating them.

## Backup discipline

For source-grade A artefacts (SEC filings, Fed releases), the Compiler must also save the immutable copy alongside any markdown summary. Example:
- `raw/earnings/nvda-2026q1-transcript.md` (markdown extraction)
- `raw/earnings/nvda-2026q1-transcript.pdf` (original archived)

This ensures we can re-extract if the markdown version has summarisation artefacts that compromise downstream analysis.
