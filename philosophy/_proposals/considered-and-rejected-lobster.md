---
type: reference
status: proposal
proposed_status: rejected-for-integration
tags: [inspiration, open-source, ai-trading, hft, lob, microstructure, considered-and-rejected, proposal]
title: LOBSTER — considered and rejected for $hark integration — proposal
author_role: researcher
proposed_destination: philosophy/references/considered-and-rejected.md (create new aggregator page)
proposed_at: 2026-05-29T17:00:00+08:00
source_urls:
  - https://lobsterdata.com
  - https://lobsterdata.com/info/WhatIsLOBSTER.php
---

# LOBSTER (REJECTED-FOR-INTEGRATION, PROPOSAL)

> Draft proposal for a NEW page `philosophy/references/considered-and-rejected.md` (aggregator of HFT-class projects evaluated and rejected). Human approval required before move into the philosophy layer.

**Status**: rejected-for-integration / reference-only

**What it is**: LOBSTER (Limit Order Book System — The Efficient Reconstructor) is a NASDAQ ITCH-derived limit order book reconstruction service, originally developed by Huang & Polak at Humboldt-Universität zu Berlin / SFB 649, and operated commercially since the mid-2010s. It outputs **microsecond-resolution** event-by-event LOB state (message file + orderbook file) for every NASDAQ-listed name, used heavily in academic HFT / microstructure research.

**Original source of the operator's interest**: market scan referenced LOBSTER + DeepLOB as a "high-frequency / microstructure" direction the operator was weighing against the LLM-agent direction.

## Why this is rejected for `$hark` integration

Five independently-sufficient reasons, in priority order:

1. **README structural exclusion.** `$hark/README.md` is unambiguous:
   > *"It does NOT do high-frequency trading on US equities."*
   This is not a Phase-deferral; it is a structural scope decision tied to the operator's edge being in 1-month-to-1-year supply-chain analysis, not microsecond reaction time. Integrating LOBSTER data would either be unused or would silently invite scope creep. The constitution ([[../../sharks]]) and [[../00-thesis]] both anchor on swing-horizon edge.

2. **Horizon mismatch.** `$hark`'s [[../01-time-horizon]] anchors on 1m–12m holding periods. LOBSTER's information value decays on millisecond-to-minute horizons. The signal-to-cost ratio at swing horizon is approximately zero — by the time `$hark` would have ingested + compiled an LOB-derived signal, the microstructure information has been arbitraged out by HFT firms with co-located silicon.

3. **Cost / data-access asymmetry.** Free LOBSTER sample data is limited to a handful of trading days for a handful of tickers. Full historical access is paid (academic and commercial tiers, **Unconfirmed: pricing — check lobsterdata.com**) and the licensing typically forbids retransmission. Even if the operator wanted to absorb the cost, the cost-per-marginal-signal at swing horizon does not pencil out.

4. **No interaction with the existing alpha source.** The thesis in [[../00-thesis]] is *Mag-7 supply-chain bottleneck propagation* (see [[../concepts/supply-chain-bottleneck]]). That signal lives in earnings transcripts + supplier announcements + macro releases — none of which are visible in LOBSTER feeds. LOBSTER is the wrong dataset for the wrong alpha.

5. **Tooling and infrastructure burden.** Ingesting LOBSTER into a Compile-first ([[../references/karpathy-llm-wiki]]) architecture requires a parser for the binary message / orderbook format, a time-series store sized for ~10 GB per ticker-day, and stream-processing infra the `$hark` Python `src/sharks/` skeleton does not have ambitions to host (per the no-HFT rule in [[../CLAUDE]] §2 spirit). The infrastructure spend would compete with the Phase 4 backtest engine work.

## What we keep from having considered it

- **Decision-audit value**: this rejection is recorded so a future agent / reviewer does not re-litigate the question. Same pattern as `docs/SAFETY-CHECKLIST.md` recording each of Codex's 10 vulnerability flags so they aren't re-introduced silently.
- **Adjacent valid use**: if the operator ever opens a sub-project (NOT `$hark`) specifically for microstructure research — e.g. a separate `$hark-hft/` repo, with its own constitution that does not inherit the no-HFT rule — LOBSTER would be the obvious dataset to start with. This proposal does not foreclose that future; it scopes the rejection to the existing `$hark` system.
- **Conceptual cross-link**: the *idea* of order-book imbalance as a leading indicator informs [[../concepts/price-volume-divergence]] at swing horizon (where volume profile substitutes for the unavailable per-order microstructure). The macro intuition transfers; the microsecond data does not.

## What would flip this rejection

This is the falsifiability table — explicit conditions under which the operator should re-open the LOBSTER question:

| Condition | Re-open? |
|---|---|
| Operator's edge thesis shifts toward US-equity intraday / day-trading | yes |
| LOBSTER releases a *free* tier covering 2023+ at full ticker coverage | maybe — re-evaluate cost side only |
| Academic research demonstrates LOB-derived features adding alpha *at multi-week horizon* on US equities | maybe — re-evaluate horizon-mismatch claim only |
| `$hark` README is amended to permit HFT on US equities | yes (but that is a constitutional change requiring [[../../sharks]] human edit) |

Until at least one of the above triggers, this stays a no-go.

## Cross-references

- [[../../README]] — the binding scope exclusion
- [[../../sharks]] — the constitutional edge thesis
- [[../00-thesis]] — supply-chain-bottleneck alpha source
- [[../01-time-horizon]] — swing-horizon binding
- [[../CLAUDE]] §2 — hard boundaries the rejection respects
- [[../references/open-source-inspirations]] — the *accepted* inspirations list this proposal complements
- [[../../docs/SAFETY-CHECKLIST]] — discipline-precedent for recording decisions-not-taken
- See also companion proposal [[considered-and-rejected-deeplob]] (sibling rejection)

## Notes for the human reviewer on accept

1. This proposal asks the human to **create** `philosophy/references/considered-and-rejected.md` as a NEW aggregator page (parallel to `open-source-inspirations.md`).
2. The aggregator page should open with a one-paragraph framing: "Projects considered and explicitly rejected for `$hark` integration, recorded so the rejection is auditable and re-evaluation triggers are explicit."
3. The first entry of the new aggregator page is the body of this proposal (LOBSTER); the second is [[considered-and-rejected-deeplob]].
4. After accept, the matrix-patch proposal ([[inspirations-matrix-patch]]) shows the link line to add to `philosophy/references/open-source-inspirations.md` ("See also: considered-and-rejected.md").
