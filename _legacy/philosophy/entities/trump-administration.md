---
type: entity
tags: [entity, institution, geopolitics, trade-policy, antitrust, trump]
title: Trump Administration (US Executive)
institution_type: executive-branch
author_role: human
---

# Trump Administration

The single most active source of news-dimension catalysts in the current cycle, especially on trade policy (tariffs), antitrust enforcement, export controls, and US-China relations. Tracked as an entity because policy decisions drive Mag 7 supply-chain repricing.

## Why it's in the entity layer

- Trade policy changes (tariff announcements, reciprocal-tariff frameworks) directly reprice Mag 7 supply-chain ADRs (TSM, ASML especially)
- Antitrust posture shifts affect Big Tech monetisation models (Google Search remedies, App Store rulings)
- Export control updates gate AI silicon revenue (Nvidia, ASML)
- Communication style (Truth Social posts) generates intraday volatility independent of formal policy
- US-China rhetoric cycles drive the Taiwan-strait risk premium on TSM and the broader semiconductor sector

## Policy axes the Compiler tracks

| Axis | Affected entities | Catalyst grade |
|---|---|---|
| Tariffs (sector-specific or country-specific) | Apple (China assembly), Tesla (China factory + sales), TSMC (Taiwan), Amazon (cross-border retail) | A |
| Export controls (silicon, EUV) | NVIDIA, ASML, AMD, TSMC | A |
| Antitrust enforcement (Big Tech) | Google, Apple, Amazon, Meta | A |
| Tax policy | All Mag 7 (corporate tax rates, R&D credits, repatriation) | B |
| Immigration / talent visas | All tech (engineering talent supply) | C |
| Energy / climate policy | Tesla (EV subsidies / penalties), oil & gas sector buckets | B |
| US-China geopolitical rhetoric | TSMC most, Mag 7 broadly | B with potential A on specific events |

## Information sources

Per [[../../CLAUDE]] source quality grading:

- **A-grade**: Official White House releases, executive orders, formally published rules
- **B-grade**: Official statements from administration cabinet members (Treasury Secretary, USTR, Commerce Secretary)
- **C-grade**: Official press conferences and prepared remarks
- **D-grade**: Truth Social posts, ad-hoc media interviews

D-grade posts can move markets despite low formal authority. The Compiler files them but applies the [[../02-signal-taxonomy]] gating: D-grade sentiment alone does not open positions, only stages watchlist updates.

## Trade policy translation framework

When a tariff or export-control announcement hits:

1. **First-order affected company**: identify the named or implied target (e.g. "tariffs on Mexican imports" → Tesla's Mexico operations)
2. **Second-order supply-chain effect**: trace through [[../concepts/supply-chain-bottleneck]] for upstream / downstream impact
3. **Substitution path**: are there alternative routes? (e.g. assembly relocation feasibility, alternative supplier capacity)
4. **Time-horizon attribution**: most policy announcements are 1-3 month catalysts (until the implementation details emerge); persistent themes can be 12m catalysts

## Cross-references

- [[tsmc-adr]] — most directly geopolitically exposed
- [[apple]] — China revenue + assembly exposure
- [[tesla]] — China factory + Mexico operations + EV subsidy exposure
- [[nvidia]] — AI silicon export control exposure
- [[googl]] — Search antitrust ruling and remedies path
- [[../06-exclusions]] — geopolitical event day exclusion rule
- [[../07-mode-switch]] — force-low-freq on geopolitical event days

## Notes for the Compiler

When the Compiler updates `wiki/01_macro_state.md` after a Trump-admin policy action:
1. Identify the policy axis (per the table above)
2. List affected tier1 + tier2 entities with one-line impact statement
3. Apply [[../../CLAUDE#5-source-quality-grading]] grade
4. `as_of_timestamp` matches the first-public-visibility time of the announcement (executive order release time, or Truth Social post time, etc. — see [[../09-point-in-time]])
5. Cross-update affected entity pages with a dated `## News (YYYY-MM-DD)` section
