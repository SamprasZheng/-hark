---
type: entity
tags: [entity, mag7, semiconductors, ai, nvidia, tier1]
title: NVIDIA Corporation
ticker: NVDA
exchange: NASDAQ
sector: technology
sub_sector: semiconductors
market_cap_band: trillion
last_earnings_date: TBD
tier: tier1_mag7
author_role: human
---

# NVIDIA (NVDA)

The structural beneficiary of the AI compute capex cycle. Owns the GPU stack (data center + edge), the CUDA software moat, and the leading position in AI training and inference.

## One-line business model

Designs accelerator silicon and sells it via a vertically integrated software / systems stack to hyperscale data center operators, enterprises, and (increasingly) sovereign customers.

## Why it's in the watchlist

- Largest single concentration of upside in the current AI capex cycle (per [[../00-thesis]])
- Owns the most-binding bottleneck in the supply chain (CoWoS-L packaging, see [[../concepts/supply-chain-bottleneck]])
- Highest sensitivity to Fed liquidity regime (per [[../concepts/liquidity-fishbowl]]) of any Mag 7 — both the most-bought and most-cut name in any regime shift

## Three key catalysts to monitor

1. **Blackwell / B200 production ramp**: gating component is TSMC CoWoS-L. Capacity ramp pace determines whether earnings beats accelerate or moderate in next 4 quarters.
2. **Sovereign AI demand**: orders from non-US national governments (UAE, KSA, India, etc.) represent the next leg of revenue. Cluster announcements from these channels are A-grade catalysts.
3. **Networking moat depth**: Mellanox-derived networking (InfiniBand / Spectrum-X) is the harder-to-replicate part of the stack. Competitive erosion would show first in networking attach rates, not in GPU pricing.

## Bottleneck / vulnerability map

- **Upstream**: TSMC N4/N3 wafer + CoWoS-L packaging. NVDA cannot ship more than TSMC can package.
- **Bottleneck supplier exposure** (see [[../concepts/supply-chain-bottleneck]]): SK Hynix (HBM3e supply), ASML (EUV gating future capacity), specialty gas / photoresist suppliers
- **Substitution risk**: AMD MI300 series (catching up but not equal), custom silicon from hyperscalers (TPU, Trainium, MAIA). The substitution thesis is real but 2-3 years away from materially denting NVDA share.
- **Regulatory risk**: US export controls on advanced AI silicon (current; expected to expand). Each round of restrictions is interpreted by the system as a near-term headwind but does not invalidate the structural thesis.

## Current thesis status

`TBD` until Compiler populates `wiki/02_mag7_bottleneck.md` with as-of dated state.

Historical reference: as of plan-writing time (2026-05-28), NVDA has been the leadership name of the AI cycle since Q4 2022. Position-sizing discipline from [[../08-risk-and-position]] tier1 cap (8%) applies regardless of conviction.

## Cross-references

- [[../concepts/supply-chain-bottleneck]] — the chain NVDA sits at the top of
- [[../10-strategies]] — Strategy A consolidation entries on NVDA are the cleanest expression of structural thesis
- [[../03-long-short-taxonomy]] — historical TD-9 sell setups on NVDA (e.g. Jul 2023) are the exemplars of the volume-validation guard preventing false exits
- [[tsmc-adr]] — upstream wafer + packaging
- [[../concepts/cycle-resonance]] — NVDA was the leadership name in the 2022→2023 cycle reversal

## Notes for the Compiler

When updating this page on new sources, prioritise:
1. Quarterly earnings (especially data center segment revenue and CoWoS allocation commentary)
2. CES / GTC keynote summaries
3. Hyperscaler capex guidance (because hyperscaler capex is the demand function for NVDA)
4. Geopolitical: export control updates, sovereign customer announcements
