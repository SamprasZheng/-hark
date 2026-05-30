---
type: synthesis
tags: [mag7, supply-chain, bottleneck, alpha, nvda-5t, ai-breadth]
title: Mag 7 Supply-Chain Bottleneck Map
as_of_timestamp: 2026-05-29T00:00:00-04:00
author_role: compiler
source_paths:
  - raw/macro/principal-narrative-2026-05-29.md
status: live
schema_version: 1
---

# Mag 7 Supply-Chain Bottleneck Map — 2026-05-29

The **living map** of the system's primary alpha source — the upstream chokepoints in the Mag 7 supply chain where pricing power and revenue elasticity are highest.

> **Current regime note**: NVDA has reached ~$5T market cap (world's largest stock) and is consolidating in the $180-220 range. Per [[../philosophy/concepts/supply-chain-bottleneck]], when the leadership name saturates, the **second-derivative trade is the upstream and adjacent supply chain**. This page is the map for that trade. See [[01_macro_state]] §3 and [[03_alpha_library]] §A.6.

## 1. Demand-pull layer (Mag 7 capex)

All four hyperscalers (AMZN, MSFT, GOOGL, META) are confirmed active in the AI capex cycle per principal narrative (2026-05-29). Per-quarter capex guidance is the leading indicator for the supply chain. Phase 2 finnhub ingest will populate exact numbers; current Compiler view is qualitative:

| Hyperscaler | AI capex posture | Custom silicon program |
|---|---|---|
| AMZN | active; AWS Trainium + Inferentia ramps | yes (Trainium 2/3) |
| MSFT | active; Azure AI services + Copilot ARPU expansion | yes (Maia + Cobalt) |
| GOOGL | active; TPU + Gemini stack | yes (TPU v5/v6) |
| META | active; large-scale internal training | yes (MTIA, AVGO partnership) |

## 2. Upstream wafer + packaging (chokepoint)

**TSMC** ([[../philosophy/entities/tsmc-adr]]) remains the binding capacity ceiling for NVDA, Apple M-series, and hyperscaler custom silicon. The CoWoS-L packaging step is the named single most-binding constraint.

Phase 2 ingest priority:
- TSMC monthly revenue reports (most-recent month and prior)
- TSMC CoWoS allocation commentary from earnings transcripts
- N3 → N2 node transition timing

Status: **stub — Phase 2 populates from earnings + Digitimes ingest.**

## 3. Memory bottleneck (HBM)

HBM3e supply remains a binding constraint for AI training workloads. Three suppliers: SK Hynix (leader), Micron, Samsung. The principal narrative did not provide updated allocation numbers; Phase 2 priority research item.

Status: **stub — Phase 2 populates.**

## 4. Equipment + materials

**ASML** ([[../philosophy/entities/asml]]) remains the upstream-most node. Order book disclosures are the leading-leading indicator for the next 18-24 months. Status: **stub — Phase 2 populates.**

## 5. Risk + substitution map

### 5.1 Substitution risk

- AMD MI300/MI325 vs. NVDA — narrowing technical gap; CUDA software moat remains the structural barrier
- Hyperscaler in-sourcing (Trainium, TPU, MAIA) — multi-year structural pressure on NVDA share but currently growing the total pie
- AVGO custom-ASIC partnerships — captures hyperscaler-custom-silicon revenue independent of NVDA allocation

### 5.2 Geopolitical risk

- Per [[01_macro_state]] §7, Trump-policy is now the dominant variance source. Export-control rounds remain a Grade-A near-term catalyst.
- TSMC carries the highest Taiwan-strait risk premium of any tier-2 ADR. Size at 60% of standard cap per `watchlist/universe.yaml` human_overrides when US-China tension is "elevated".

## 6. The supply-chain breadth update (2026-05-29)

**This is the actionable update from the principal narrative.** The AI rally has broadened beyond pure GPU + packaging. The Compiler proposes adding three sub-buckets to the tier 2 universe:

### 6.1 Optical communications

**Thesis**: AI cluster scale requires high-bandwidth, low-latency interconnect. As clusters scale to 100k+ GPUs, optical networking becomes the binding constraint.

**Candidate tickers (Researcher to vet per [[../philosophy/concepts/supply-chain-bottleneck]] validation checklist)**:

- **CIEN** (Ciena) — coherent optics + DCI (data center interconnect)
- **ANET** (Arista) — high-bandwidth networking switches; tier 1 hyperscale customer wins
- **COHR** (Coherent Corp) — optical components, including laser sources for transceivers
- **LITE** (Lumentum) — laser + optical components; capacity for high-end transceivers
- **FN** (Fabrinet) — optical contract manufacturing

**Phase 2 action**: ingest most recent quarterly earnings for each name; Researcher writes entity pages and the Risk Officer approves promotion to `watchlist/universe.yaml` tier 2.

### 6.2 CPU + Agent AI beneficiaries

**Thesis**: Agent AI workloads — long-running, multi-step inference with tool use and reasoning — are CPU-bound to a greater degree than pure training or single-shot inference. This drives a CPU upgrade cycle independent of GPU demand.

**Confirmed beneficiaries** (per principal narrative):

- **AMD** ([[../philosophy/entities/amd]]) — EPYC server CPU share gain + MI series AI GPU
- **Intel** — *not currently in `watchlist/universe.yaml`*. **Compiler proposes adding** to tier 2 with the Agent AI thesis as the supporting framework. Researcher to write `philosophy/entities/intel.md` and Risk Officer to approve.

### 6.3 Mag 7 AI-cloud partnerships (all-in confirmed)

All four hyperscale partners (AMZN, MSFT, GOOGL, META) are confirmed active in the cycle per §1 above. No new entity additions required; the existing entity pages adequately cover them.

## 7. Trade ideas table

Phase 1 status: no trade recommendations yet (Phase 3 produces them).

Once Phase 3 is live, this section becomes a structured list of `[bottleneck → candidate ticker → strategy → horizon]` rows.

## Discipline reminders

- Every claim cites a `raw/` source path (principal narrative is the source for this iteration)
- Section-level `as_of_timestamp` matches `source_first_visible_at` of the source that motivated each section
- Contradictions between sources are flagged on the older claim, not overwritten

## See also

- [[../philosophy/concepts/supply-chain-bottleneck]] — the framework this page implements
- [[../philosophy/00-thesis]] — why this map is the system's alpha source
- [[../philosophy/10-strategies]] — Strategy A entries on tier2 names routinely cite this page
- [[01_macro_state]] — current regime view
- [[03_alpha_library]] §F — supply-chain bottleneck plays historical cases
