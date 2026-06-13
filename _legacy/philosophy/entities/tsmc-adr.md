---
type: entity
tags: [entity, supply-chain, semiconductors, foundry, tsmc, tier2]
title: TSMC (ADR)
ticker: TSM
exchange: NYSE
sector: technology
sub_sector: semiconductor-foundry
market_cap_band: trillion
last_earnings_date: TBD
tier: tier2_supply_chain
author_role: human
---

# TSMC ADR (TSM)

The world's largest and most advanced semiconductor foundry. Manufactures leading-edge silicon for NVIDIA, AMD, Apple, Qualcomm, MediaTek, and increasingly Intel and Samsung Foundry customers. Owns the only CoWoS-class advanced packaging capacity at scale.

## One-line business model

Pure-play foundry: designs nothing, manufactures everything for fabless customers at the leading edge (currently N3, ramping N2) plus mature-node specialty.

## Why it's in the watchlist

- The single most important upstream node in the AI capex cycle. Per [[../concepts/supply-chain-bottleneck]], TSMC sits at the chokepoint that gates how many Blackwells / TPUs / Trainiums actually ship.
- The cleanest tier-2 ADR for expressing US-AI-cycle exposure with non-US listing diversification
- Highest geopolitical premium of any tier-2 name (Taiwan exposure); the premium itself creates trading windows on US-China rhetoric cycles

## Three key catalysts to monitor

1. **CoWoS-L capacity announcements**: TSMC's advanced packaging capacity is the direct bottleneck for NVDA Blackwell + B200 + downstream hyperscaler custom silicon. Capacity ramp pace announcements drive the entire AI supply-chain trade.
2. **N2 / A16 yield + customer announcements**: future node leadership. Apple typically first; NVDA second.
3. **Geopolitical posture**: US export-control updates, China tension levels, Taiwan strait risk premium. These move TSM independently of fundamentals.

## Bottleneck / vulnerability map

- **Upstream equipment**: ASML EUV (N5 and beyond), AMAT + LRCX + KLA + TEL for adjacent process steps. See [[asml]].
- **Customer concentration**: NVDA + AAPL are top-2 customers; combined > 30% of revenue. Either's slowdown is material.
- **Substitution risk**: Samsung Foundry + Intel Foundry Services + GlobalFoundries (for mature). Currently no substitute at the leading edge.
- **Tax / regulatory risk**: US CHIPS Act subsidies (positive); Taiwan-based tax position (politically variable)
- **Earthquake / supply disruption risk**: Taiwan-specific concentration risk; major event would be a step-function global shortage

## Current thesis status

`TBD` until Compiler populates with as-of dated state. Position-sizing per [[../08-risk-and-position]] tier2 cap (5%).

## Cross-references

- [[nvidia]] — primary customer
- [[apple]] — primary customer
- [[asml]] — primary upstream supplier
- [[avgo]] — significant customer for ASIC manufacturing
- [[amd]] — customer
- [[../concepts/supply-chain-bottleneck]] — TSMC is the canonical example
- [[trump-administration]] — US-China policy interactions material to TSM
- [[federal-reserve]] — global liquidity cycle drives capex cycle, which drives TSM

## Notes for the Compiler

When updating this page on new sources, prioritise:
1. Quarterly earnings + monthly revenue updates (TSMC reports monthly, which is rare and useful)
2. CoWoS / advanced packaging capacity commentary
3. CHIPS Act subsidy disbursements and Arizona / Japan / Germany fab progress
4. Geopolitical: US-China silicon export control updates
5. Major customer wins or losses (e.g. an Intel design win moving to TSMC, or Apple shifting back to Intel-fab — would be a major sign)
