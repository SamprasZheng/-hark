# Philosophy Log

Chronological record of changes to the `philosophy/` layer. Append-only.

Format: `## [YYYY-MM-DD HH:MM ET] <action> | <short title>`

---

## [2026-05-28 22:00 ET] initialise | Phase 1 constitution + philosophy scaffold

- Created `philosophy/` directory structure: `references/`, `concepts/`, `entities/`
- Filed [[references/karpathy-llm-wiki]] — verbatim archive of Karpathy's 2026-04-04 LLM Wiki gist (11,985 bytes), source-grade A
- Wrote 11 numbered foundation pages: [[00-thesis]] through [[10-strategies]]
- Wrote 12 concept-dictionary pages: 5 technical + 4 structural + 3 behavioural
- Wrote 13 entity pages: Mag 7 (NVDA / AAPL / TSLA / AMZN / GOOGL / MSFT / META) + supply chain (TSM / ASML / AVGO / AMD) + institutions (Fed / Trump-admin)
- Wrote [[index]] (this layer's MOC) and [[../CLAUDE]] (agent operational rules)
- The constitution at [[../sharks]] was preserved verbatim — only frontmatter and a 3-line preamble were added

Notes:
- The four-dimension signal taxonomy ([[02-signal-taxonomy]]) integrates the codex review's conflict-arbitration rules and the gemini review's long-short symmetry
- Risk and point-in-time pages ([[08-risk-and-position]], [[09-point-in-time]]) are codex review's two Critical items, treated as non-negotiable in Phase 2+
- All entity pages carry `last_earnings_date: TBD` — Compiler will populate in Phase 2 first run

Next session expectations:
- The `wiki/` layer remains stub. Phase 2 implementation will start populating `wiki/01_macro_state.md` from real `raw/macro/` ingest
- The `watchlist/universe.yaml` is seeded with the 11 tier1+tier2 tickers above; tier3 mid-cap pool stays empty until Phase 4 screener is live
