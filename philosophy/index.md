---
type: index
tags: [index, moc, map-of-content]
title: Philosophy Index
updated: 2026-05-28
---

# Philosophy Index — Map of Content

The static `philosophy/` layer of the Sharks system. This is the **constitution + concept dictionary + entity sketches** — the human-curated, slow-changing knowledge base that `wiki/` (the dynamic compiled state) and `outputs/` (the daily decisions) refer back to.

## Where to start

- [[../sharks]] — **the constitution** (read this first, every session)
- [[../CLAUDE]] — operational rules for LLM agents
- [[references/karpathy-llm-wiki]] — the methodology root (Karpathy's LLM Wiki gist)

## Numbered foundations (read in order)

- [[00-thesis]] — core thesis distilled from the constitution
- [[01-time-horizon]] — 1m / 3m / 6m / 12m buckets and the cycle-resonance window
- [[02-signal-taxonomy]] — four-dimension framework + conflict arbitration matrix
- [[03-long-short-taxonomy]] — long/short four-quadrant routing (replaces v1 binary)
- [[04-sector-and-finviz]] — Finviz filter philosophy + walk-forward data-snooping defence
- [[05-decision-rubric]] — daily 10-signal contract (2 long_new + 2 short_new + 6 followup)
- [[06-exclusions]] — numerical hard filters
- [[07-mode-switch]] — low/high/auto frequency mode by market state
- [[08-risk-and-position]] — sizing, concentration caps, max-DD halt, exit rules
- [[09-point-in-time]] — as_of_timestamp discipline + release-time normalisation
- [[10-strategies]] — Strategy A / B / C specifications

## Concept dictionary

Technical:
- [[concepts/td-9-sequential]] — Demark TD-9 + volume-validation guard
- [[concepts/golden-cross]] — 20MA × 60MA crossover
- [[concepts/bollinger-bands]] — volatility-band breakouts
- [[concepts/distance-from-52w-high]] — momentum-regime gate
- [[concepts/price-volume-divergence]] — 縮量也不下跌 bottoming, top distribution

Structural:
- [[concepts/supply-chain-bottleneck]] — the alpha source framework
- [[concepts/liquidity-fishbowl]] — regime-aware sizing
- [[concepts/cycle-resonance]] — 半年調整 / 兩個月上漲 6m bucket trigger
- [[concepts/last-snow]] — peak macro bearishness + structural bottom co-occurrence
- [[concepts/regime-gated-scoring]] — FOM weights as a function of the detected market regime (Fix A)
- [[concepts/buffett-3m]] — 3-month Buffett-tier quality screen

Behavioural (Andy's constitution principles, formalised):
- [[concepts/objective-watershed]] — pre-committed price levels driving bias
- [[concepts/farmer-mindset]] — explicit rejection of crowded-trade thinking
- [[concepts/separation-mind]] — 分別心 detection and inoculation
- [[concepts/evidence-gated-rebalance]] — 十足的證據 discipline: default-hold, offense needs full evidence, defense may move fast (added 2026-05-31)

Cyclical (added 2026-05-29):
- [[concepts/multi-scale-cycles]] — aggregator: BTC halving + Presidential + Calendar + Sector
- [[concepts/btc-halving-cycle]] — 4-year cycle phases
- [[concepts/institutional-btc-anchor]] — counter-thesis: institutional float-locking may compress the 4-year cycle (added 2026-05-30)
- [[concepts/election-cycle-year-2]] — Y2 midterm + post-Nov 100% rule
- [[concepts/seasonal-monthly]] — SPX monthly seasonality + September weakness
- [[concepts/sector-seasonality]] — per-sector best/worst month tables

Macro / systemic (added 2026-05-30):
- [[concepts/funding-chain-rupture]] — latency-stratified funding-stress leading indicators (why bubbles pop)
- [[concepts/macro-analog-matching]] — 100-year regime-cube analog matching, decision-support not prediction

Validation & ensemble (added 2026-05-31):
- [[concepts/fom-predictive-validity]] — IC study: does FOM actually forecast? (recalibration heartbeat)
- [[concepts/analyst-persona-ensemble]] — analysts/ council → bounded FOM weight tilts, conviction-blended
- [[concepts/hotspot-sector-rotation]] — predict next-quarter sector leaders; seasonality beats momentum (measured)
- [[concepts/nasdaq100-calibration]] — 對答案 2000-2026 + train/test split; optimal weights invert with horizon

Analyst Models (externally sourced, internalised into the framework):
- [[concepts/chip-flow-single-point-breakout]] — single-point chip-flow breakout (reference analyst-model implementation)
- [[concepts/serenity-supply-chain-bottleneck]] — supply-chain bottleneck pick-and-shovel (Serenity @aleabitoreddit)

## Entity coverage

Tier 1 — Magnificent 7:
- [[entities/nvidia]] — NVDA, AI cycle leadership
- [[entities/apple]] — AAPL, consumer cycle + China exposure
- [[entities/tesla]] — TSLA, narrative cycle + EV + AI/robotics optionality
- [[entities/amazon]] — AMZN, AWS + retail + advertising
- [[entities/googl]] — GOOGL, Search + cloud + AI; narrative whiplash
- [[entities/microsoft]] — MSFT, most diversified AI exposure
- [[entities/meta]] — META, advertising + AI + Reality Labs

Tier 2 — Supply chain (ADR):
- [[entities/tsmc-adr]] — TSM, the upstream chokepoint
- [[entities/asml]] — ASML, EUV monopoly
- [[entities/avgo]] — AVGO, hyperscaler custom ASIC
- [[entities/amd]] — AMD, AI GPU competitive dynamics

Institutional:
- [[entities/federal-reserve]] — FOMC, liquidity regime driver
- [[entities/trump-administration]] — US Executive, news-dimension catalyst source

## References (external)

- [[references/karpathy-llm-wiki]] — Karpathy 2026-04-04 LLM Wiki gist (methodology root)
- [[references/open-source-inspirations]] — the 8 open-source projects we draw architecture from

## What lives elsewhere

- `wiki/` — LLM-compiled dynamic state (macro state, Mag 7 bottleneck map, alpha library, daily recommendations)
- `raw/` — read-only ingest of external sources (Fed releases, earnings transcripts, KOL feeds, Finviz CSVs)
- `watchlist/universe.yaml` — the structured ticker universe
- `outputs/` — daily `picks-YYYY-MM-DD.json` machine-readable outputs
- `src/sharks/` — the Python implementation (Phase 2+)
- `docs/` — roadmap, safety checklist, open-source inspirations

## Maintenance notes

- This file is the **map**, not the territory. When you add a page elsewhere in `philosophy/`, update this index.
- Agents may propose additions (via chat message); the human edits this file.
- Lint check (Phase 2): every `[[link]]` here must resolve to an existing file. CI lint job stub lives in `tests/test_philosophy_links.py`.
