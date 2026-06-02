---
type: synthesis
domain: tech-trend
phase: C
tags: [ai-datacenter-power, nuclear, smr, uranium, gas-turbines, transformers, switchgear, liquid-cooling, grid-interconnect, ai-infra]
as_of_timestamp: 2026-05-31T04:30:00+08:00
author_role: researcher
confidence: 0.78
verdict: 結構
verdict_by_horizon: {T0: 結構, T1: 結構, T2: 質變, T3: 太早}
rubric: {A1: 2, A2: 2, A3: 2, A4: 2, A5: 1}
sources_grade_summary: "A: 8 B: 9 C: 4 D: 0 E: 0"
---
# AI 資料中心電力瓶頸 / The AI-Datacenter Power Crunch — generation → T&D → cooling

## 0. 一句話判決 + desk view / Verdict
**結構 (structural), conf 0.78.** Power — not GPUs — is now the binding constraint on the AI build-out, and this is *primary-sourced*, not narrative: Eaton's data-center order backlog hit **228 GW = ~12 years of build at 2025 rates** [S6], GE Vernova's gas-turbine + reservation book reached **~100 GW, sold-out toward 2030** [S5], and grid interconnection now takes **~8 years** in PJM [S9]. The electricals (ETN/VRT/GEV/PWR) and merchant nuclear IPPs (CEG/VST/TLN) have **real, accelerating P&L** — they are the cleanest pick-and-shovel on AI capex. **Desk view:** this is the same first-derivative AI-capex trade as [[memory-supercycle]] and [[optical-interconnect-cpo]] — power is simply the *next* bottleneck after compute and interconnect. Own the order-book (electricals) and the only-uprateable baseload (nuclear IPPs); the froth is concentrated in the **pre-revenue SMR pure-plays (OKLO/SMR/NNE)** whose first commercial COD is ~2028–2030+ and which are priced years ahead of a single delivered kWh. Verdict differs by horizon: **結構 now (T0/T1)** for electricals+IPP, **質變 at T2** as datacenter load reshapes the grid, **太早 at T3** for SMR-at-scale/fusion. Not buy/sell advice.

## 1. 技術底蘊 — why power is the binding constraint (A1=2, ENGINEER)
The physics chain is **generation → transmission & distribution (T&D) → cooling**, and every link is now lead-time-bound, not capital-bound.

**The kW/rack escalation is the root driver.** A general-purpose CPU rack draws ~12 kW; air-cooled H100 racks ~40 kW; **NVIDIA GB200 NVL72 ~120 kW/rack**; and the 2027 **Vera Rubin Ultra "Kyber" rack is specced at 600 kW** (576 GPU dies) [S10][S11]. A 5× density jump in ~3 years means a fixed building footprint now demands an order of magnitude more delivered power *and* forces liquid cooling — air cannot remove 120 kW, let alone 600 kW, from a rack.

- **Generation** is the slow link: a new grid interconnect averages **~8 years** in PJM (vs <2y in 2008) [S9]; SMRs are "7–12 years out" [S17b]. The only fast baseload is *restarting/uprating existing nuclear* (Crane/TMI 837 MW, 2028 [S2]) or *behind-the-meter gas* (simple-cycle in 12–18 months [S17b]).
- **T&D** is the *hardest* bottleneck: large-power-transformer lead times have blown out to **128 weeks (standard) / 144 weeks (generator step-up), up to 4 years**, with prices **+77%** since 2020 [S12]. Wood Mackenzie sees the transformer supply deficit at **~100% in 2025, shrinking to <10% only by 2030** [S12]. Switchgear and copper are co-constrained: each MW of datacenter needs **~6–8 tonnes of copper** [S14].
- **Cooling** has flipped: liquid/direct-to-chip is now the **default** for new AI designs (Vertiv) [S4] — the thermal envelope of Blackwell/Rubin makes it non-optional.

This is a **durable physical/lead-time moat** for incumbents (you cannot conjure a transformer plant or a nuclear license overnight). Score 2.

## 2. 需求數據 / Demand reality (A2=2)
| 指標 | 數值 | period | 來源(grade·verification) |
|---|---|---|---|
| Global DC electricity, 2024→2030 (IEA Base) | ~415 → **~945 TWh** (+15%/yr; ~3% of world) | 2030E | [S1] B · cross-confirmed |
| US DC share of generation by 2030 (EPRI) | 4.4% (redacted) → **9% (up to 17% high)** | 2030E | [S13] A · primary-fetched |
| Goldman US DC power demand 2030 | **47 GW (+176%)** | 2030E | [S14] C · single-source-pending |
| PJM load growth 2025–40, DC portion | **+605 TWh total; 422 TWh = DC** (72% rise) | 2040E | [S9] B · cross-confirmed |
| Eaton DC order backlog | **228 GW = ~12yr** of 2025 build; DC orders **+240% YoY** | Q1-FY2026 | [S6] A · primary-fetched |
| GE Vernova gas backlog + reservations | **~100 GW** (was 83 GW), **+21 GW** signed in Q | Q1-FY2026 | [S5] B · cross-confirmed |
| Vertiv backlog | **$12.45B (+~80% YoY)** | Q1-FY2026 (3/31/26) | [S4] B · cross-confirmed |
| Quanta backlog (grid/DC) | **$48.5B record** | Q1-FY2026 | [S15] A · primary-fetched |

This is **accelerating P&L**, not intent: Eaton Q1-FY2026 revenue **$7.5B** record with electrical backlog +48%; Vertiv Q1-FY2026 revenue **$2.65B (+30%)**, FY26 guide raised to **$13.5–14.0B**; Quanta Q1-FY2026 revenue **$7.87B** (vs $6.23B Q1-FY2025) [S4][S6][S15]. Score 2.

## 3. 資金與權威 / Capital & authority (A3=2)
The hyperscaler PPA wave is the authority signal — real dollars, multi-decade, primary-filed:
- **Microsoft–Constellation (Crane/TMI Unit 1):** 20-year PPA, **837 MW**, online **2028**, ~$1B DOE loan [S2]. Constellation Q1-FY2026 revenue **$11.1B (+64%)** post-**$26.6B Calpine** acquisition (→ ~55 GW fleet); **>5,650 MW** of hyperscaler contracts signed; FY26 EPS guide **$11–12** [S3].
- **Amazon–Talen (Susquehanna):** **1,920 MW** through 2042, restructured front-of-the-meter after FERC rejected the behind-the-meter version (Nov-2024) — an **$18B**-scale IPP-for-AI template [S7].
- **Meta:** signed **1.1 GW Clinton** PPA with Constellation (Jun-2025) for *existing* nuclear, while its 1–4 GW SMR RFP targets only **early-2030s** [S8] — the near-term reality is restarts, not new SMRs.
- **Vistra–AWS (Comanche Peak):** up to **1,200 MW**, 20-year; targeting ~3.2 GW more nuclear contracting; Vistra Q1-FY2026 adj-EBITDA record **$1.494B**, FY26 guide **$6.8–7.6B** [S16].
- **GE Vernova** record backlog **~$150B**; Q1-FY2026 orders **$18.3B (+71% organic)**, Electrification DC orders **$2.4B > all of 2025** [S5b]. **Cameco** Q1-FY2026 adj-EBITDA **$509M (+44%)**, uranium term price ref **~$87/lb**, +$2.6B India contract [S18].

Heavy capital across the whole stack, primary-filed. Score 2.

## 4. 受益 / 受損 / 抄底 / Winners, losers, dip-buys (A4=2)
- **WINNERS (real P&L, structural):** Electricals — **Eaton ETN** (228 GW book), **Vertiv VRT** (power+cooling pure-play), **GE Vernova GEV** (turbine+grid duopoly economics), **Quanta PWR** (grid-build labor), **nVent NVT** (liquid-cooling/enclosures). IPPs — **Constellation CEG**, **Vistra VST**, **Talen TLN** (24/7 baseload the hyperscalers must buy). Uranium fuel — **Cameco CCJ** (+ Westinghouse equity), **UEC** (US enrichment/mining). T&D primary — **Hitachi Energy** (private; $1B+ US transformer capex) [S12].
- **抄底候選 (dip-buy on AI-capex air-pocket):** the IPPs are the cyclical dip-buy — CEG fell **~11.6%** on its own Calpine-fueled beat [S20], and VST/TLN trade on PJM capacity-price + PPA cadence, so a capex pause is the entry. The electricals' multiples (below) make them a *pullback*, not chase.
- **受損 / OVER-HYPED:** **SMR pure-plays OKLO / SMR(NuScale) / NNE(Nano Nuclear)** — **flag pre-revenue.** OKLO reported **$0 revenue** Q1-FY2026, ~**$13B** market cap, $2.5B cash, first Aurora COD targeted **late-2027→2028** [S17][S19]; NuScale's first deployment **slipped to 2030** (analysts say 2033–34), FY26 revenue est cut to **~$76M**, still loss-making [S17a]. These are A-grade *stories*, D-grade *valuations* — narrative priced years ahead of a delivered kWh.
- **Valuation guard:** even quality names are stretched — **GEV forward P/E ~37–69×** depending on source [S5b][S20]; the trade's risk has shifted from demand to **multiple + execution.**

Clear chokepoint with listed pure-plays. Score 2.

## 5. 多時程 / Multi-horizon
- **T0 (0–1y) 結構:** electricals + IPP backlogs already converting to revenue; transformer/turbine scarcity is *here*. Priced-in but real.
- **T1 (1–3y) 結構:** PPA ramp (Crane 2028, Talen→2032), transformer deficit still >50% mid-decade; gas turbines bridge. Electricals compound.
- **T2 (3–5y) 質變:** datacenter load reshapes the grid (PJM DC = 422 TWh of +605 TWh) — a genuine demand 質變 for generation/T&D. First SMR CODs *begin* (Oklo ~2028, NuScale ~2030) but immaterial to P&L.
- **T3 (5–10y) 太早:** SMR-at-scale and fusion — technically advancing, no near-term P&L, datable only past 2030. The narrative's most speculative leg.

## 6. 爆發條件 + 里程碑 / Milestones (falsifiable, datable)
1. **Datacenter % of US generation** crosses ~6% (toward EPRI 9%). verify EPRI/EIA · status: 4.4%→tracking · next: EIA 2026 update.
2. **A major transformer-capacity add comes online** (Hitachi South Boston VA = largest US LPT plant). verify Hitachi PR · status: under construction, 2028 target · next: COD confirmation [S12].
3. **First SMR commercial COD.** verify NRC/company 8-K · status: Oklo late-2027–2028 target, none operating · next: NRC license acceptance + construction milestones [S17].
4. **A new hyperscaler PPA $-value signed** (gas or nuclear). verify 8-K/PR · status: CEG >5,650 MW, Talen 1,920 MW, VST 1,200 MW · next: next quarterly disclosure [S2][S7][S16].
5. **GE Vernova turbine book "sold out through 2030"** confirmed. verify GEV 8-K · status: ~100 GW, on-track · next: FY2026 year-end backlog [S5][S5b].
6. **PJM interconnect wait falls below ~5y** (reform working). verify PJM filings · status: ~8y, reform in transition cycles · next: TC2 completion end-2026 [S9].

## 7. 時代影響與交互 / Era-impact + interactions
Power converts AI capex into a **physical-economy supercycle**: utilities, grid-equipment makers, uranium miners and gas producers become AI-levered. It is also the AI bubble's **hardest reality check** — unlike software multiples, a 144-week transformer lead time and an 8-year interconnect queue are *non-fungible* constraints that cap how fast compute can actually be energized. Cross-interactions: same AI-capex first-derivative as [[memory-supercycle]] (HBM) and [[optical-interconnect-cpo]] (InP/laser) — **compute → interconnect → power** is the bottleneck-migration path; if power binds, GPU/HBM/optical demand *throttles at the rack*. Also touches [[ai-edge-devices]] (inference pushed to edge partly to dodge datacenter power) and [[model-leadership-and-data]] (frontier-cluster size is now power-gated, not just chip-gated).

## 8. 同溫層 + 自我打臉 / Echo-chamber gap + self-refutation
**Echo-chamber gap:** the consensus is "infinite, permanent power shortage → buy everything power." Three 打臉 against my own bull case:
1. **SMR is the narrative, not the cash flow.** The desk instinct ("nuclear renaissance → OKLO/SMR") is ADOPTION-empty: **$0 revenue**, CODs 2028–2034, priced like producers [S17][S19]. The *real* nuclear trade is boring uprates/restarts at CEG/VST/CCJ — and Meta's headline "nuclear" deal was an *existing* plant (Clinton), not an SMR [S8].
2. **Demand forecasts have a wide, self-serving range.** IEA 945 TWh, EPRI 9% *to 17%*, Goldman 47 GW — vendors and the build-out's beneficiaries produce the bullish tail. Hyperscaler capex *discipline* (or an AI-capex air-pocket, as in the HBM "permanent shortage" myth that turned out to be supply discipline — see [[memory-supercycle]]) would hit IPP merchant prices and electrical order rates first. Backlogs are real; the *2030 demand curve* is a projection, not a filing.
3. **Valuation, not demand, is the live risk.** GEV at ~37–69× fwd, VRT/ETN richly bid — the bottleneck is genuine but largely priced; the dip-buy thesis only works on an AI-capex pullback, which is precisely what the bulls deny can happen. Transformer/turbine scarcity *also* eases by 2030 per Wood Mackenzie (deficit 100%→<10%) [S12] — the scarcity premium is cyclical, not permanent.

Bear case, stated plainly: if AI capex pauses, the order-books (12-yr Eaton, sold-out GEV) are the very thing that overshoots into a glut, and the pre-rev SMRs re-rate to cash.

## Sources
1. [IEA Energy & AI — DC electricity to ~945 TWh by 2030 (+15%/yr) — datacenterdynamics.com/en/news/iea-data-center-energy-consumption-set-to-double-by-2030-to-945twh/ + spglobal.com/energy/.../041025 — retrieved 2026-05-31 — grade B — cross-confirmed (IEA primary 403'd; ≥2 secondaries cite it)]
2. [Constellation — Crane Clean Energy Center / TMI Unit 1: 837 MW, 20-yr Microsoft PPA, online 2028 — constellationenergy.com/news/2024/Constellation-to-Launch-Crane-Clean-Energy-Center... — retrieved 2026-05-31 — grade A — primary-fetched]
3. [Constellation CEG Q1-FY2026: rev $11.1B (+64%), $26.6B Calpine, >5,650 MW PPAs, EPS guide $11–12 — stocktitan.net/sec-filings/CEG/8-k... + tikr.com — retrieved 2026-05-31 — grade B — cross-confirmed]
4. [Vertiv VRT Q1-FY2026: rev $2.65B (+30%), backlog $12.45B (+~80%), FY26 guide $13.5–14.0B, liquid-cooling default — techjacksolutions.com + kalkine.com + alphastreet.com — retrieved 2026-05-31 — grade B — cross-confirmed]
5. [GE Vernova gas-turbine backlog ~100 GW (was 83 GW), sold-out toward 2030, +21 GW signed Q1-FY2026 — industrialinfo.com/.../356705 + utilitydive.com/news/ge-vernova-gas-turbine-investor/807662/ — retrieved 2026-05-31 — grade B — cross-confirmed]
5b. [GE Vernova GEV Q1-FY2026 orders $18.3B (+71% organic), backlog ~$150B, Electrification DC orders $2.4B; fwd P/E ~37–69× — 247wallst.com + gurufocus.com/term/forward-pe-ratio/GEV — retrieved 2026-05-31 — grade C — single-source-pending]
6. [Eaton ETN Q1-FY2026 8-K: rev $7.5B record, electrical backlog +48%, DC orders +240%, DC backlog 228 GW (~12yr), book-to-bill 1.2, transformer lead times ~100 wks — sec.gov/Archives/edgar/data/0001551182/000155118226000010/etn03312026exhibit99.htm + alphastreet.com — retrieved 2026-05-31 — grade A — primary-fetched]
7. [Talen–Amazon Susquehanna: 1,920 MW through 2042, FTM restructure post-FERC rejection, ~$18B — powermag.com/talen-amazon-launch-18b-nuclear-ppa... + sec.gov/Archives/edgar/data/0001622536/000162828025030559/ — retrieved 2026-05-31 — grade A — primary-fetched]
8. [Meta 1–4 GW nuclear RFP (early-2030s) + 1.1 GW Clinton PPA w/ Constellation (Jun-2025) — power-eng.com/nuclear/meta-seeks-up-to-4-gw... + utilitydive.com/news/meta-seeks-up-to-4-gw... — retrieved 2026-05-31 — grade B — cross-confirmed]
9. [PJM interconnect ~8yr wait (vs <2y 2008); load +605 TWh 2025–40, DC = 422 TWh — rmi.org/pjms-speed-to-power-problem-and-how-to-fix-it/ + pjm.com fact-sheet — retrieved 2026-05-31 — grade B — cross-confirmed]
10. [NVIDIA GB200 NVL72 ~120 kW/rack (vs CPU 12 kW, H100 air 40 kW) — semianalysis.com/p/gb200-hardware-architecture + nvidia.com/en-us/data-center/gb200-nvl72/ — retrieved 2026-05-31 — grade B — cross-confirmed]
11. [NVIDIA Vera Rubin Ultra "Kyber" rack 600 kW (576 GPU dies), 2H-2027 — datacenterdynamics.com/.../nvidias-rubin-ultra-nvl576-rack-expected-to-be-600kw + tomshardware.com — retrieved 2026-05-31 — grade B — cross-confirmed]
12. [US transformer lead times 128 wk standard / 144 wk GSU / up to 4 yr, +77% price; WoodMac deficit 100%(redacted)→<10%(redacted); Hitachi $1B+ US capex — pv-magazine-usa.com/2026/05/11/u-s-transformer-market... + powermag.com/transformers-in-2026... + datacenterdynamics.com (Hitachi CEO) — retrieved 2026-05-31 — grade B — cross-confirmed]
13. [EPRI: US DC could consume 9% (up to 17%) of US generation by 2030, from 4.4% (redacted) — epri.com/about/media-resources/press-release/q5vu86fr8tkxatfx8ihf1u48vw4r1dzf + prnewswire.com — retrieved 2026-05-31 — grade A — primary-fetched]
14. [Goldman US DC power demand 47 GW by 2030 (+176%); ~6–8 t copper/MW; BHP copper +72% by 2050 — carboncredits.com/data-centers-copper-hunger... + spglobal.com copper-in-the-age-of-ai — retrieved 2026-05-31 — grade C — single-source-pending]
15. [Quanta PWR Q1-FY2026 8-K: rev $7.87B, backlog $48.5B record (grid/DC) — sec.gov/Archives/edgar/data/0001050915/000119312526058069/ + theglobeandmail.com — retrieved 2026-05-31 — grade A — primary-fetched]
16. [Vistra VST Q1-FY2026: adj-EBITDA $1.494B record, AWS Comanche Peak 1,200 MW 20-yr, ~3.2 GW more nuclear contracting, FY26 guide $6.8–7.6B — investing.com/.../vistra-q1-2026-slides + tikr.com — retrieved 2026-05-31 — grade B — cross-confirmed]
17. [Oklo OKLO: first Aurora COD late-2027→early-2028, Kiewit constructor, INL groundbreaking Sep-2025 — world-nuclear-news.org/articles/oklo-selects-constructor-for-first-aurora-powerhouse + utilitydive.com/news/oklo-75-mw-reactor-design-smr-nuclear/743578/ — retrieved 2026-05-31 — grade B — cross-confirmed]
17a. [NuScale SMR: first deployment slipped to 2030 (analysts 2033–34), FY26 rev est ~$76M, loss-making, $1.0B cash — nuscalepower.com/press-releases/2026/nuscale-power-reports-first-quarter-2026-results + simplywall.st — retrieved 2026-05-31 — grade B — cross-confirmed]
17b. [Gas simple-cycle installable 12–18 mo vs SMR "7–12 yr"; BTM 25–33% of incremental DC demand to 2030 (~33 GW) — heatmap.news/energy/natural-gas-data-centers-speed + marketplace.org/.../2026/02/04 — retrieved 2026-05-31 — grade B — cross-confirmed]
18. [Cameco CCJ Q1-FY2026 6-K: adj-EBITDA $509M (+44%), term U price ref ~$87/lb, +$2.6B India contract, Westinghouse equity — sec.gov/Archives/edgar/data/0001009001/000119312526085244/d27416dex991.htm + stocktitan.net — retrieved 2026-05-31 — grade A — primary-fetched]
19. [OKLO $0 revenue Q1-FY2026, ~$13B mkt cap, $2.5B cash; NuScale safer per analysts — finance.yahoo.com/.../nuscale-safer-nuclear-stock-pre + fool.com/investing/2026/05/25/oklo-vs-nuscale-power-in-2026 — retrieved 2026-05-31 — grade C — cross-confirmed]
20. [GEV/VRT stretched valuations now central debate; CEG −11.6% on Q1 beat — techi.com/ge-vernova-vertiv-ai-data-center + simplywall.st (CEG) — retrieved 2026-05-31 — grade C — single-source-pending]

## See also
- [[memory-supercycle]] · [[optical-interconnect-cpo]] — same AI-capex first-derivative; power is the next bottleneck after compute + interconnect
- [[model-leadership-and-data]] — frontier-cluster scale is now power-gated · [[ai-edge-devices]] — edge inference partly dodges datacenter power
- [[00_framework]] · [[scoreboard]] · [[99_cross_synthesis]] · [[_sourcing-protocol]] · [[fom-integration]]
- [[../wiki/07_ai_bubble_audit]] — the late-cycle bubble guard (SMR pre-rev froth)

