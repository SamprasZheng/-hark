---
type: entity
tags: [entity, supply-chain, semiconductors, ai-gpu, amd, tier2]
title: Advanced Micro Devices
ticker: AMD
exchange: NASDAQ
sector: technology
sub_sector: semiconductors
market_cap_band: high-hundreds-of-billions
last_earnings_date: TBD
tier: tier2_supply_chain
author_role: human
---

# AMD (AMD)

The credible #2 AI GPU alternative to NVIDIA (Instinct MI series). Also operates strong server CPU (EPYC) and PC client (Ryzen) businesses. The closest thing to a hedge / convergence trade against NVIDIA dominance.

## One-line business model

Designs CPU + GPU + adaptive computing silicon, sold to PC OEMs, server OEMs, and increasingly directly to hyperscalers (especially AI accelerators).

## Why it's in the watchlist

- The cleanest single-name expression of "AI GPU competitive dynamics" — every catalyst that strengthens NVIDIA's moat hurts AMD; every NVIDIA stumble lifts AMD
- Strong server CPU position provides a non-AI baseline business (EPYC vs. Intel Xeon share trajectory)
- Most-volatile tier2 name in the system — sensitive to both AI-cycle narrative and PC-cycle realities

## Three key catalysts to monitor

1. **MI300 / MI325 / next-gen AI GPU revenue**: customer adoption (MSFT, Meta primary customers); pricing relative to NVDA; software-stack maturity (ROCm vs. CUDA).
2. **Server CPU share**: EPYC vs. Intel Xeon in datacenter and cloud. Quarterly market-share data points.
3. **PC client unit cycle**: Ryzen vs. Intel Core in consumer + commercial. Macro consumer / refresh cycle exposure.

## Bottleneck / vulnerability map

- **TSMC leading-node + CoWoS allocation**: shares the same upstream constraint as NVDA and AVGO. Competition for the same capacity.
- **HBM supply**: AMD's MI300X uses HBM3; supply allocations matter.
- **Substitution risk at AI**: NVDA's CUDA software moat is the dominant barrier. Even MI300 hardware competitive with H100 generates customer adoption only when software stack supports incumbent workloads.
- **Substitution risk at server CPU**: ARM-based servers (Graviton, Cobalt, Ampere) are emerging structural competitors to both AMD EPYC and Intel Xeon.

## Current thesis status

`TBD` until Compiler populates with as-of dated state. Position-sizing per [[../08-risk-and-position]] tier2 cap (5%).

## Cross-references

- [[nvidia]] — primary competitor + AI-cycle correlate
- [[tsmc-adr]] — upstream foundry
- [[../concepts/supply-chain-bottleneck]] — competes with NVDA for the same CoWoS capacity
- [[../10-strategies]] — AMD's volatility makes it a Strategy B momentum candidate when AI narrative is bullish + sector resonance is strong

## Notes for the Compiler

When updating this page on new sources, prioritise:
1. Quarterly earnings — segment breakdown (Data Center / Client / Gaming / Embedded), Instinct AI revenue
2. AI customer wins (e.g. Meta, Microsoft commitments)
3. ROCm software stack maturity updates
4. Server CPU market share data (Mercury Research quarterly)
5. PC unit and consumer-cycle macro indicators
