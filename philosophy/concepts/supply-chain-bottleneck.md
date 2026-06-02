---
type: concept
tags: [supply-chain, bottleneck, mag7, cowos, hbm, alpha, framework]
title: Supply-Chain Bottleneck Thinking
author_role: human
---

# Supply-Chain Bottleneck Framework

The **core alpha source** of the Sharks system. While Mag 7 names are the visible end-buyers, the structural alpha lives in the upstream components where capacity is constrained and pricing power is highest.

## The framework

When a Mag 7 demand thesis activates (e.g. "AI inference demand 10× over 18 months"), the analysis chain is:

```
1. Identify the end-buyer Mag 7 capacity ceiling
2. Walk upstream to the immediate supplier (e.g. NVDA → TSMC for fab capacity)
3. Walk further upstream to the bottleneck component (e.g. TSMC → CoWoS packaging, HBM)
4. Identify the bottleneck component supplier(s) with the highest revenue elasticity (e.g. HBM → SK Hynix, Micron, Samsung)
5. Walk one step further to the equipment / specialty input that gates capacity expansion at step 4 (e.g. ASML for EUV, specialty gases, advanced photoresists)
```

The trade is typically at **step 4 or 5**, not at step 1. The end-buyer's stock has the demand thesis priced in earlier and more efficiently. The bottleneck supplier prices in last.

## Current Mag 7 bottleneck map (updated by Compiler in wiki/02_mag7_bottleneck.md)

Phase 1 starting points — the Compiler will expand and verify in Phase 2:

| End-buyer | Capacity ceiling | Bottleneck component | Bottleneck supplier | Capacity gate |
|---|---|---|---|---|
| NVDA (Blackwell) | TSMC N4/N3 wafer + CoWoS-L packaging | CoWoS-L throughput | TSMC (in-house) | ASML EUV + specialty gases |
| MSFT/META/GOOG (data center) | HBM3e supply | HBM stacking yield | SK Hynix > Micron > Samsung | DRAM wafer capacity, advanced photoresist |
| AAPL (M-series) | TSMC N3E | leading-edge node yield | TSMC | ASML EUV |
| TSLA (FSD compute / Optimus) | proprietary Dojo + HBM | HBM allocation | SK Hynix > Samsung | Same as above |
| AMZN (Trainium) | TSMC + own packaging | CoWoS allocation queue | TSMC | Same as NVDA |

## Trading implication

The Strategy A and Strategy 3m bucket entries from [[../01-time-horizon]] should preferentially fund **bottleneck-supplier positions** when the end-buyer's demand thesis is active. The end-buyer position is for tier1 core; the bottleneck supplier is for tier2 alpha.

Specific patterns to watch:
- **Capacity guidance from the bottleneck supplier**: when SK Hynix raises HBM capex guidance, it confirms downstream demand pull through AND extends supplier pricing power.
- **Allocation announcements**: when TSMC announces 2nd-half-of-year CoWoS allocations are full, all CoWoS-dependent designs (NVDA, AMZN Trainium, GOOG TPU) get a soft cap on their unit volumes — bullish for the bottleneck, mixed for the end-buyer.
- **Equipment orders**: ASML's quarterly order book is the leading-leading indicator for the entire chain. A surprise ASML order from a non-TSMC fab (Intel, Samsung) signals capacity normalisation 18-24 months out.

## Validation checklist

Before opening a bottleneck-supplier position, the Compiler / Researcher confirms:

- [ ] End-buyer demand thesis has at least 2 A-grade sources (per [[../../CLAUDE]] grading)
- [ ] Bottleneck supplier captures ≥ 25% of the bottleneck-step value chain (otherwise the position is too diffuse to express the thesis cleanly)
- [ ] No substitute is technically viable within the position horizon ([[../01-time-horizon]])
- [ ] No regulatory risk that could disrupt supply (e.g. export controls on advanced semis to specific geographies)

## Common failure modes

- **Buying the headline, not the bottleneck**: when the news cycle hypes a Mag 7 product launch, the bottleneck supplier may have already priced in the catalyst. The system must verify via [[distance-from-52w-high]] and [[bollinger-bands]] that the bottleneck supplier still has technical room to run.
- **Wrong step in the chain**: e.g. buying SOX (broad semiconductor index) instead of the specific HBM supplier. Index dilution kills the alpha.
- **Substitution risk**: e.g. buying a packaging substrate maker that gets disintermediated by a new packaging technology. Validation checklist item #3 catches this — but only if the Researcher does the substitute analysis.

## Implementation handoff

`wiki/02_mag7_bottleneck.md` is the living map. The Compiler updates it on every earnings cycle and on every supply-chain news ingest. The Researcher's quarterly review re-validates the map against the latest 10-Q disclosures.

This concept is the most-cited page in the system. Every Strategy A entry on a tier2 ticker references it in `evidence_paths`.
