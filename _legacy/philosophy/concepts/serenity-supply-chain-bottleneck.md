---
type: concept
tags: [analyst-model, advisor-source, supply-chain, cpo, photonics, hbm, bottleneck, small-cap]
title: Serenity Supply-Chain Bottleneck (供應鏈瓶頸選股法)
author_role: human
source: "Serenity (@aleabitoreddit) public X posts Apr-May 2026 + Goldman Sachs CPO ecosystem map; reverse-engineered framework ingested 2026-05-30. Raw: raw/kol_signals/serenity-framework-2026-05-30.md, raw/kol_signals/serenity-aleabitoreddit-profile-2026-05-29.md. Watchlist: watchlist/serenity-supply-chain.yaml. Research/educational only — not financial advice."
---

# Serenity Supply-Chain Bottleneck

"Buy the shovels, not the gold." When an AI-hardware theme heats up, the obvious
large-cap endpoint (the GPU, the switch vendor) is already priced; the asymmetric
edge is in the **bottleneck** suppliers everyone needs and few can make. This is a
fundamentals + supply-chain-structure model, not a price-action model — it sits
under [[../../sharks]] principle of finding mispriced supply-chain depth (the same
intuition behind [[supply-chain-bottleneck]]) and explicitly defers entry-timing to
the price/volume concepts ([[golden-cross]], [[price-volume-divergence]]) rather
than re-inventing them.

## Module 1 — Data Ingestion

The model is **fundamental + structural**, so its primary inputs are not OHLCV:

- **Theme inflection** (a node transition / capacity wall / qual cycle) — sourced
  from news + earnings calls. Maps to `src/sharks/data/finnhub_client.py` (news +
  earnings calendar). The "why now" gate is a hard requirement.
- **Supply-chain map** — the layered value chain. Stored as structured data in
  `watchlist/serenity-supply-chain.yaml` (CPO / HBM / passives-PCB themes, one
  entry per listed equity per layer with `ecosystem`, `bottleneck`, `tier`).
- **Qualification / backlog / gross-margin trajectory** — from filings + IR. No
  dedicated client yet → **Phase 2 gap** (fundamentals client `src/sharks/data`).
- **EOD price** only for relative-strength sanity checks (e.g. "Himax +75% while
  FOCI +2.6% — laggard") via `src/sharks/data/yfinance_client.py`.

Cross-border tickers (`.TW` / `.TWO` / `.T` / `.SZ` / `.SS` / `.HK` / KOSPI-KOSDAQ
6-digit) are first-class here. The current FOM universe (`src/sharks/scoring/fom.py`)
handles only US-listed names; non-US suffix handling is a **Phase 2 gap** flagged in
`watchlist/serenity-supply-chain.yaml`.

## Module 2 — Universe Selection

Universe is the union of named equities across all layers of an active theme, per
`watchlist/serenity-supply-chain.yaml`, intersected with [[../04-sector-and-finviz]]
sector buckets (semis, optical, materials). The US-listed subset that overlaps the
FOM universe today: NVDA, AMD, INTC, AVGO, LITE, COHR, FN, GLW, AAOI, POET, AXTI,
CRDO, AEHR, NVTS, POWI, MRVL, TSEM, VPG. The bulk of the bottleneck pure plays are
Taiwan / Japan / Korea / China small caps awaiting Phase 2 cross-listing support.

## Module 3 — Core Logic

A 9-step scoring procedure (no magic thresholds — those are deferred to backtest):

1. **Pin the theme + inflection** — demand cliff, not a vibe; answer "why now".
2. **Decompose the value chain into layers** — Compute → Switch → Optics/CPO →
   Components (optical engine, FAU, connector, CW laser, ELS, fiber, thermal) →
   Equipment → Assembly.
3. **Name listed equities at every layer** — concrete tickers across all exchanges.
4. **Hunt the bottleneck** — critical-path + hard-to-second-source +
   capacity-constrained = pricing power. Bottleneck = thesis. (e.g. CW laser / ELS,
   glass core, PCB micro-drill bits, HBM hybrid-bond metrology.)
5. **Prefer 2nd/3rd-order pure plays** — smaller TAM but more torque to the theme.
6. **Map ecosystem exposure** — single-customer (higher beta) vs dual-ecosystem
   (Nvidia + Broadcom, de-risked).
7. **Rank conviction tiers** — T1 bottleneck pure play / T2 quality exposure /
   T3 basket-only.
8. **Confirm forward pipeline** — gross margin, volume ramp, qual status; not last
   quarter's historicals (this is the model's loudest discipline).
9. **Cross-check the un-listed names** — the "hidden gems" an analyst report omits
   often carry the highest return.

Conviction tier and `bottleneck: true` are the two load-bearing fields; everything
else is exposure context.

## Module 4 — Execution & Risk

- **Mode** — strictly low-frequency / long-horizon per [[../07-mode-switch]]: theses
  play out over scale-out (H2 2026) → scale-up (H2 2027) windows. No intraday.
- **Sizing** — small-cap, high-vol names; per [[../08-risk-and-position]] these are
  tier-2/tier-3 positions with tighter caps. A single-customer pure play is sized
  smaller than a dual-ecosystem name at the same conviction tier.
- **Invalidation** — qual-cycle slip, a second-source emerging (bottleneck breaks),
  or the forward pipeline (gross margin / volume ramp) failing to confirm.

## Integration into the Sharks framework

| Serenity step | 4D taxonomy ([[../02-signal-taxonomy]]) | Sharks home |
|---|---|---|
| Theme inflection / "why now" | News + Fundamental | `src/sharks/scoring/news.py` (Phase 3) |
| Bottleneck identification | Fundamental (structural) | this concept + watchlist yaml |
| Forward pipeline (margin/ramp/qual) | Fundamental | `src/sharks/scoring/fundamental.py` (Phase 3) |
| Relative-strength laggard check | Technical | [[price-volume-divergence]] |
| Ecosystem / oligopoly structure | Fundamental | watchlist `ecosystem` field |

**Conflict arbitration with adjacent strategies**: this model is orthogonal to the
momentum-led FOM scoring and its regime gating (the Fix A regime classifier in
`src/sharks/regime/classifier.py`; see also [[cycle-resonance]]). When FOM momentum
and Serenity bottleneck disagree (a bottleneck name with weak price momentum), the
Risk Officer treats Serenity as a *watchlist-builder* and FOM as the *timing gate* —
Serenity names a candidate, FOM/price concepts time the entry. Per
[[../05-decision-rubric]] a Serenity-sourced candidate enters the daily slate only
with at least one A/B-grade fundamental source per [[../../CLAUDE]] §5.

## Implementation hooks

Future `src/sharks/scoring/serenity_supply_chain.py` (Phase 3+), each `as_of`-honest
per [[../09-point-in-time]]:

- `load_supply_chain(theme)` — parse `watchlist/serenity-supply-chain.yaml`.
- `bottleneck_score(ticker, theme)` — +weight for `bottleneck: true`, tier, and
  dual-ecosystem; threshold values are a **Phase 4 backtest deliverable**, not set
  here.
- `forward_pipeline_gate(ticker)` — requires gross-margin + volume-ramp + qual
  confirmation; blocks any name failing the gate.
- Non-US suffix resolution is a **Phase 2 gap** that this scorer depends on.

## What this model assumes — and where it breaks

- **Assumes the theme's demand cliff is real** — if the inflection is a vibe, the
  whole chain re-rates down together; the bottleneck offers no protection.
- **Assumes bottleneck durability** — a successful second-source (or a redesign that
  routes around the component) destroys the pricing power that *is* the thesis.
- **Assumes pipeline > history** — degrades badly if applied to trailing financials;
  the names are pre-revenue-inflection by construction.
- **Small-cap liquidity** — many names fail the [[../06-exclusions]] dollar-volume
  floor and can only inform a watchlist, never trigger a sized position alone.
- **KOL-source risk** — Serenity himself notes "some tickers are wrong"; codes are
  leads to verify, not facts. Grade-D source per [[../../CLAUDE]] §5 until verified.

## Analyst-Model Interface

| Contract | Value |
|---|---|
| **States / score** | 9-step procedure → conviction tier (T1/T2/T3) + `bottleneck` boolean per name |
| **Dimensions** | Fundamental (primary: structure, margin, qual) + News (inflection) + Technical (laggard relative-strength only) |
| **Entry** | Theme inflection confirmed + bottleneck identified + forward pipeline gate passed + price timing deferred to FOM/[[golden-cross]] |
| **Risk** | Tier-2/3 sizing per [[../08-risk-and-position]]; invalidation = qual slip / second-source / pipeline miss |
| **Mode** | Low-frequency / long-horizon per [[../07-mode-switch]] (scale-out 2026 → scale-up 2027) |

## Anti-patterns

- **Chasing the headline endpoint** (the GPU / the switch vendor) — already priced;
  the model exists precisely to avoid this.
- **Treating a code as fact** — verify every ticker; the watchlist marks unverified
  ones `verify: true`.
- **Sizing a single-customer pre-revenue small cap like a Buffett-tier compounder.**
- **Reading last quarter's financials as the thesis** — the model is forward-pipeline.
- **Letting the LLM narrate "this is the next AAOI"** as a probability — supply-chain
  storytelling is decision-support, not a directional signal (the same
  decision-support-not-prediction boundary the macro-analog and LLM-pollution
  protocols enforce; see `docs/LLM-BACKTEST-PROTOCOL.md`).

## See also

- [[supply-chain-bottleneck]] — the canonical concept this model operationalises
- [[cycle-resonance]] — the supply-chain timing context Serenity candidates pass through
- [[price-volume-divergence]] — laggard relative-strength check
- [[cycle-resonance]] — adjacent supply-chain timing concept
- [[../02-signal-taxonomy]] — 4D mapping
- [[../04-sector-and-finviz]] — sector bucket intersection
- [[../05-decision-rubric]] — daily slate contract
- [[../06-exclusions]] — small-cap liquidity floor
- [[../07-mode-switch]] — low-frequency routing
- [[../08-risk-and-position]] — tier sizing
- [[../09-point-in-time]] — as_of honesty for the future scorer
- [[../../sharks]] — constitution
