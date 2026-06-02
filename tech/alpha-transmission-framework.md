---
type: synthesis
domain: method
tags: [alpha, transmission, lead-lag, rotation, concentration, supply-chain, un-crowded]
as_of_timestamp: 2026-05-31T06:30:00+08:00
author_role: researcher
status: live
schema_version: 1
---

# 流動性傳導與未發現 alpha 框架 / Alpha-Transmission & Rotation Framework

The principal's question: *liquidity is concentrated in semis — will it spill over, from which sector does the transmission start, and how do I find the alpha that is NOT yet priced?* This page integrates four research inputs ([[software-stack-taxonomy]], [[rotation-spillover-algos]], [[social-attention-alpha]], [[liquidity-concentration-flows]]) with the existing `$hark` engine into one method. **Research/educational only.**

## §0. 一句話 / The thesis

> **Undiscovered alpha lives in the LEAD-LAG transmission and the EARLY-attention radar — NOT in chasing whatever sector is already hot.** Your own [[../philosophy/concepts/hotspot-sector-rotation]] backtest proved sector-momentum-chasing is ≈ noise (IC_IR 0.52); the replicated edges are supply-chain lead-lag (Cohen-Frazzini ~150bp/mo), seasonality (IC_IR 2.78), and attention used *before* the crowd arrives. The supply chain is the **map**; concentration→flow→lead-lag→attention is the **detection stack**.

## §1. 供應鏈傳導地圖 / The transmission map (HW + SW)

**Hardware** (your decomposition, extended into the AI-capex chain — three independent agents converged on this order):

```
hyperscaler capex → 晶片(SOXX) → 記憶體(HBM/DRAM) → 光通訊(CPO/InP) → 電力/電氣(power) → 工業/EPC → breadth
   instant pay         leader        moved-with         moved-with        ← NOW spilling      lagged       last
```
SOX leads IT/Nasdaq-100 by **~1–2 quarters**; memory/optical already moved *with* semis; the live spill is into **power/electrical** (the Phase-C [[ai-datacenter-power]] finding — compute→interconnect→電力).

**Software** ([[software-stack-taxonomy]], the layer you didn't have): L0 silicon → L1 cloud → **L2 data/infra (hidden sweet spot)** → L3 model → L4 orchestration → L5 horizontal SaaS → **L6 vertical SaaS (most AI-proof)**. The "smile curve": margin at both ends, **the middle (L1 cloud / L3 models) is squeezed**. Software's lead-lag: **capex committed top-down fast, revenue backfills bottom-up over 2–3 yr → capex revision LEADS revenue revision** (the "capex-fatigue air-pocket").

The unifying insight: **the edge is in the next link that hasn't moved yet, and especially in the under-covered second-tier supplier of that link** — link-momentum is strongest where analyst coverage is thin, NOT in the mega-cap leader.

## §2. 偵測棧 / The detection stack (wired to existing modules)

| 層 | 問題 | 既有/新模組 | 訊號 |
|---|---|---|---|
| **集中度** | regime 是否過度集中 (stock) | [[../philosophy/concepts/regime-gated-scoring]] / `breadth_indicator.py` (+top-10%, semis%, RSP/SPY, COR1M) | top-10 40.7% (50yr 極值)、corr <10 |
| **資金流** | 錢往哪 (flow) | `chip_flow.py` (per-name 籌碼) + `sector_flow.py` (`detect_rotation`) + ETF flows | growth −$5B / value +$17B / industrials↑ |
| **lead-lag** | 哪個 sector 是下游但還沒動 | **NEW `regime/lead_lag.py`** (Granger-like + net-transmitter) | SOXX→X 顯著且 X 未動 |
| **attention** | 在被擁擠前的早期雷達 | `social-attention-alpha` (abnormal-z + acceleration; 反向用於極端) | 加速但未廣泛持有 |
| **seasonality** | 唯一驗證過的輪動 edge | `hotspot-sector-rotation` (IC_IR 2.78) | 季節性favored window |

## §3. 尋找未發現 alpha 的方法 / The un-crowded-alpha funnel

A name/sector is a candidate only when it clears the funnel — each filter removes the crowded:

1. **Downstream** — `lead_lag.py` says it's predicted by a *moving* leader (e.g. SOXX) at a 1–2-quarter lag.
2. **Not-yet-moved** — its recent relative strength is still low (the move hasn't happened → not yet priced).
3. **Attention accelerating, not peaked** — abnormal-attention z rising but not at a crowding extreme (peak attention ≈ peak crowding ≈ reversal).
4. **Seasonally + fundamentally confirmed** — in a seasonally-favoured window AND the capex chain confirms in *order-books*, not just price.
5. → **human DD via `tech/`** + the 5-dim 十足的證據 gate. The funnel SURFACES; it never auto-buys.

Where the edge actually is: **second-tier suppliers of the next link** (power/electrical T&D metrology, cooling, optical metrology — [[optical-supply-chain-deep]]), not the leader; and **L2 data-infra / L6 vertical SaaS** in software.

## §4. 半導體外溢的具體答案 / The concrete semis-spillover answer

- **Over-concentrated?** Yes — ~50-year extreme (top-10 40.7%, semis ~18%, corr <10).
- **Spillover starting?** Yes but **marginal/early/fragile** (~4 months); part is rate-cut + OBBBA bonus-depreciation, **not** pure AI-capex overflow — don't over-credit "semis spillover."
- **Order (capex-chain conviction high→low):** semis → **① power/電氣/grid → ② datacenter cooling/infra (Vertiv-type) → ③ broad industrials/EPC → ④ utilities (lagged) → ⑤ financing/credit/real assets**; small-cap/value is **parallel (rate-driven), not downstream**.
- **Confirm-spillover triggers (falsifiable, in [[_weekly-watch]]):** %S&P >200dma holds >60% for ≥3 mo; RSP/SPY higher-high + rising 50dma ≥2Q; COR1M mean-reverts up off <10 *without* a drawdown; cyclicals out-gather Tech in flows ≥2Q; AI-capex chain confirms in fundamentals. **Falsifiers:** breadth <50%, RSP/SPY back below 200dma within a quarter, growth reclaims flow leadership.

## §5. 演算法參考 / Algorithm reference (real vs decayed — [[rotation-spillover-algos]])

- ✅ **Lead-lag / economic-link** (Cohen-Frazzini, Menzly-Ozbas, Lee tech-links, Hong-Stein diffusion, Diebold-Yilmaz networks) — the core, implemented in `lead_lag.py`.
- ✅ **Graph/network propagation** (Li-Ferreira 2025) — the right abstraction; future `spillover_graph.py`.
- ✅ **Factor momentum** (Ehsani-Linnainmaa); ✅ **regime-switching as a GATE** (not standalone).
- ⚠️ **Flow / attention** — real ~days–2wk then **reverse**; use *inversely* to find un-crowded names.
- ❌ **Sector-momentum chasing / distance-pairs** — decayed/crowded; confirmation only, never the edge.

## §6. 整合到 $hark / Integration + guardrails

- **NEW `regime/lead_lag.py`** — Granger-like lead score + net-transmitter rank + `transmission_candidates(leader, followers)` (zero-dep, PIT). This is the actionable answer to "從哪個產業開始傳導."
- **Extend `breadth_indicator.py`** — top-10/Mag-7 % + percentile, semiconductor weight, RSP/SPY ratio + 200dma slope, a `CONCENTRATION_EXTREME` verdict distinct from `OVERHEATED`.
- **Extend `sector_flow.py`** — `broadening_score` (% of the 15 ETFs with RS>0) + a `semis_spillover` flag (SOXX leader AND power/industrials `rotating_in`).
- **Route "next sector" through SEASONALITY, not momentum** ([[../philosophy/concepts/hotspot-sector-rotation]]), with the capex-chain as a *fundamental* overlay; gate offense on `funding_chain` health + the 十足的證據 quorum. **Observe-first**: like the DD tilt, none of this enters `final_fom` until walk-forward IC-validated.

## §7. 同溫層風險 / Echo-chamber flags

- **The rotation-clock is the deepest trap** — it *feels* like analysis but is ≈ a coin-flip; only seasonality + lead-lag have measured edge.
- **Concentration extreme cuts both ways** — Goldman's century study shows extreme concentration can mark *bottoms* (redacted), and de-concentration can resolve *up* (laggards catch up), not only down.
- **Attention IS the crowd** — trading with it at the extreme joins the losing herd; default contrarian.
- **Sourcing**: the concentration/flow primaries (Cboe/SEC/SSGA/S&P) 403'd the fetcher → all grade-B; the semis-weight 18% vs 11% is `contradicted`, not resolved. These breadth/flow numbers decay weekly — re-pull on the [[_weekly-watch]] cadence.

## See also
- [[software-stack-taxonomy]] · [[rotation-spillover-algos]] · [[social-attention-alpha]] · [[liquidity-concentration-flows]] — the four inputs
- [[../philosophy/concepts/hotspot-sector-rotation]] (seasonality>momentum) · [[../philosophy/concepts/supply-chain-bottleneck]] · [[../philosophy/concepts/chip-flow-single-point-breakout]]
- [[scoreboard]] · [[fom-integration]] · [[_weekly-watch]] · [[_sourcing-protocol]]

