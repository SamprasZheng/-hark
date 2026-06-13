---
type: entity
tags: [entity, supply-chain, asic, networking, broadcom, avgo, tier2]
title: Broadcom Inc.
ticker: AVGO
exchange: NASDAQ
sector: technology
sub_sector: custom-asic + networking + infrastructure-software
market_cap_band: trillion
last_earnings_date: TBD
tier: tier2_supply_chain
author_role: human
---

# Broadcom (AVGO)

The dominant custom-ASIC partner for hyperscale customers (Google TPU, Meta MTIA, ByteDance custom silicon) plus the world leader in data center networking silicon (Tomahawk, Jericho) plus a diversified infrastructure-software business (VMware-integrated).

## One-line business model

Designs custom AI accelerators for hyperscale customers (revenue share economics), supplies networking and connectivity silicon to the same customers + carrier-class deployments, and operates a high-margin enterprise infrastructure software business (post-VMware acquisition).

## Why it's in the watchlist

- The only public-market expression of the "hyperscaler custom ASIC" thesis. As hyperscalers build their own silicon (TPU, MTIA, Trainium), AVGO captures revenue independent of NVIDIA's allocation.
- The dominant data-center networking silicon supplier, which becomes more important as AI clusters scale (network bandwidth is the binding constraint at large scale).
- Cash-generative legacy businesses fund the AI-cycle expansion; lower-beta AI exposure than pure-NVDA.

## Three key catalysts to monitor

1. **AI revenue disclosure**: AVGO reports AI revenue separately. Quarterly trajectory and customer mix commentary are A-grade catalysts.
2. **Custom ASIC win announcements**: new hyperscaler customers or new programs with existing customers materially extend the thesis.
3. **Tomahawk 6 / next-generation networking silicon deployment**: as AI clusters scale to 100k+ GPUs, networking bottlenecks tighten and AVGO's pricing power expands.

## Bottleneck / vulnerability map

- **TSMC fab + CoWoS allocation**: AVGO custom ASICs go through TSMC at leading nodes with CoWoS. Shares the same upstream constraints as NVDA.
- **Customer concentration**: AI revenue is concentrated in 3 hyperscale customers. Loss of any one is material.
- **Substitution risk**: hyperscalers could in-source ASIC design more fully (Google has DeepMind / Brain silicon teams; Meta builds in-house). Material multi-year risk.
- **Software-segment execution risk**: VMware integration has been the dominant near-term execution question. Margin and customer-retention trajectory matter.

## Current thesis status

`TBD` until Compiler populates with as-of dated state. Position-sizing per [[../08-risk-and-position]] tier2 cap (5%).

## Cross-references

- [[../concepts/supply-chain-bottleneck]] — AVGO is the hyperscaler-ASIC alternative path
- [[tsmc-adr]] — upstream foundry
- [[googl]], [[amazon]] — primary custom-ASIC customers
- [[../10-strategies]] — AVGO's quarterly cycles are Strategy A consolidation classics

## Notes for the Compiler

When updating this page on new sources, prioritise:
1. Quarterly earnings — AI revenue, semiconductor mix, software mix + retention
2. Custom-ASIC customer announcements (new wins or losses)
3. Networking-silicon roadmap updates (Tomahawk generation cadence)
4. VMware integration progress + customer-retention metrics
