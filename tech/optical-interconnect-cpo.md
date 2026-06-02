---
type: synthesis
domain: tech-trend
tags: [cpo, silicon-photonics, optical-interconnect, indium-phosphide, abf-substrate, ai-infra]
as_of_timestamp: 2026-05-31T01:15:00+08:00
author_role: researcher
confidence: 0.72
verdict: 結構
rubric: {A1: 2, A2: 1, A3: 2, A4: 2, A5: 1}
sources_grade_summary: "A: 5 B: 9 C: 5 D: 1 E: 0"
---
# 光互連 CPO / 矽光子 vs PCB·載板·銅 (Co-packaged optics) — what it kills vs what it grows

## 0. 一句話判決 / Verdict
**結構 (structural), conf 0.72.** CPO's per-port power and signal-integrity advantage is real and primary-sourced, and capital + authority backing is heavy (NVIDIA $4B into lasers, Broadcom/TSMC shipping). BUT the principal's thesis ("if CPO is faster, ordinary PCB / ABF 載板 cannot compete") is **partly right, mostly wrong**: CPO displaces *pluggable-transceiver DSP/retimers and long in-rack copper*, but ABF substrate and high-layer-count PCB demand is **growing, not dying** — bigger packages + more I/O need *more* substrate. Volume is still 2 years out; pluggables keep growing through 2026.

## 1. 技術底蘊 / Technical moat (A1=2)
CPO moves the optical engine onto the switch-ASIC package, collapsing the electrical trace from tens of cm to tens of mm. Hard numbers vs pluggables:
- **Per-port power**: pluggable ~30 W/interface → CPO **as low as 9 W** [S1]. System-level interconnect power **−30–50%** [S2]; NVIDIA claims **3.5×** efficiency, Broadcom **65–70%** optics-power cut [S1][S5][S6].
- **Energy/bit**: pluggable ~15–20 pJ/bit → CPO **~5 pJ/bit**, roadmap <1 pJ/bit [S2].
- **Signal integrity**: electrical loss **22 dB → ~4 dB** at 200G/lane → NVIDIA "**64× better signal integrity**" [S1].
- **Bandwidth density**: copper ~3 Tbps/mm vs optical interposer ~10 Tbps/mm; CPO ~1 Tbps/mm die-edge [S2].
- **Reach**: copper DAC dies at **1–2 m @ 800G**; optics has no such wall [S6].
- **Reliability**: **10× resiliency** / "5× longer training without interruption"; Meta logged 1M device-hours flap-free on Broadcom Bailly [S6].
This is a **durable physics moat** (loss, reach, energy) — not marketing. Score 2.

## 2. 需求真實性 — 數據 / Demand reality (A2=1)
| 指標 | 數值 | 日期 | 來源(grade) |
|---|---|---|---|
| NVIDIA Quantum-X (InfiniBand) avail. | early-2026 | 2025-03 | [S1] A |
| NVIDIA Spectrum-X Photonics (Ethernet) | H2-2026 | 2025-03 | [S1] A |
| Broadcom TH6-Davisson 102.4T status | **sampling** (no volume date) | 2025-10-08 | [S5] A |
| CPO market size | $46M(24) → ~$3.5B(26) | 2026 | [S12] C |
| CPO ports worldwide | >4.5M by 2026 | 2026 | [S12] C |
| **800G+ pluggable shipments** | 24M(25) → **63M (26, +2.6×)** | 2025-12 | [S9][S13] B |
| Analyst on CPO volume | "another **2 years** before shipping in volumes" | 2026 | [S9] C |

Demand is **early-revenue, not accelerating P&L**: CPO is still <$4B vs a pluggable market growing to 63M units/$9.9B. Real ramp is scale-out 2026 → scale-up 2027. Score 1.

## 3. 資金與權威背書 / Capital & authority (A3=2)
- **NVIDIA $4B** (2026-03-02): **$2B Coherent + $2B Lumentum**, each with multi-year multi-billion purchase commitments + capacity/priority access for CW lasers & CPO — demoed 420 Gb/s PAM4 on Coherent InP CW laser [S7][S8]. This is *hard capital + adoption*, not a slide.
- **TrendForce** (2025-12-08): NVIDIA EML lock-in pushed lead times **beyond 2027** and triggered a worldwide laser shortage; only **5 EML suppliers** exist (Lumentum, Coherent, Mitsubishi, Sumitomo, Broadcom) [S10].
- **TSMC COUPE** is the integration substrate for both NVIDIA and Broadcom Davisson — tier-1 foundry authority [S5][S14].
- Furukawa building a DFB-laser plant (+500% capacity by 2028, ELSFP for CPO) [S11]; Sumitomo +40% EML capacity by 2027 [S11b]. Heavy capital across the stack. Score 2.

## 4. 供應鏈與可投資節點 / Supply chain & investable nodes (A4=2)
**The true chokepoint is below the laser: the InP (indium-phosphide) substrate + the external CW/EML laser.** CPO uses an External Laser Source (ELS/ELSFP) so laser-chip demand grows **exponentially, not linearly** [S15].
- **InP wafers**: 2025 supply 600–700k vs demand 1.5–2M = **>70% deficit**; single-crystal yields only **15–25%**; order books full through 2027 [S15][S16].
- **AXT (AXTI)** controls **60–70%** of merchant InP; raised **$632.5M** for InP capacity [S15][S4] — but Q1-26 rev only **$26.9M** (tiny, parabolic-risk).
- **Sumitomo (8053.T)** = ~**60% InP substrate share** + EML; **Furukawa (5801.T)** = DFB CW; **Lumentum (LITE)/Coherent (COHR)** = dominant high-power CW/EML duopoly [S10][S11b][S15]. **VPEC (2455.TW)** + IntelliEPI = InP epi foundries [S10][S17].
- Packaging persists/grows: TSMC CoWoS scaling to **14-reticle by 2028**, glass-substrate panel line in 2026 for CPO [S14] — i.e. CPO *adds* package complexity.

## 5. 大模型 vs 小模型 / Model angle
N/A directly. Indirect: interconnect is the **scale-up/scale-out bottleneck** that determines how large a single training fabric can grow — see [[model-leadership-and-data]] and [[memory-supercycle]].

## 6. 顛覆 / 取代向量 / Disruption vector (A5=1)
**What CPO kills (principal right):** pluggable-transceiver **DSP/retimers**, expensive signal conditioning, and **long in-rack copper** (>1–2 m optical links) [S6]. NVIDIA: a 128k-GPU cluster cuts transceivers ~500k → ~128k [S6].
**What it does NOT kill (principal wrong):**
1. **ABF substrate / FC-BGA** — market **+10.6% CAGR to $9.55B by 2032**, supply-demand gap to **2027**, Ajinomoto/makers raising prices, **>12-layer** segment fastest-growing; "CPO will *further drive up* supply-chain capacity and prices" [S18][S19]. Bigger packages + more I/O = *more* substrate, not less.
2. **In-rack copper** — GB200 NVL72 uses **5,184 copper cables/rack** precisely to avoid **$2.2M/rack** of optics; Amphenol IT-Datacom **+134% YoY** [S20]. Copper wins inside the rack.
3. **Pluggables on NICs** persist (NVIDIA ConnectX-9); optical-DSP incumbent **Marvell** is pivoting DSPs into NPO/CPO, not vanishing [S6][S21].
Disruption is **partial + slow** (datable to 2026 scale-out, 2027 scale-up). Score 1.

## 7. 同溫層風險 + 空方論點 / Echo-chamber flags + bear case
- **Echo-chamber gap**: the narrative ("CPO ends copper/pluggables") is ADOPTION-thin. CAPITAL is real (NVIDIA $4B) and AUTHORITY is real (TSMC/Broadcom filings), but ADOPTION lags: CPO ≈$3.5B vs **63M pluggable units in 2026** still growing, and a sell-side analyst says **volume is ~2 years out** [S9][S13]. The narrative is 1–2 years ahead of the units.
- **Parabolic / bubble cross-check** ([[../wiki/07_ai_bubble_audit]]): **AXTI** (up ~78× per Serenity; FOM bubble_guard −95), **AAOI** (rvol 1.12), **ALAB** (rvol 0.93, Q1-26 rev $308M +93% but PCIe/connectivity, *not* CPO-pure) are flagged late-stage. AXTI's $26.9M revenue vs its market cap is the clearest froth tell — the InP *story* is A-grade, the *valuation* is D-grade.
- **Bear case**: (1) external-laser/InP is the gate — if InP yield improves or WDM-array CW (Sivers) second-sources the high-power laser, the laser duopoly's pricing power erodes (Serenity invalidation: "second-source breaks the bottleneck"). (2) Copper keeps winning scale-up far longer than bulls think (NVL72 proves it). (3) CPO serviceability problem (lasers fail) is why vendors *kept* lasers external — slows full integration.

## 8. 跨主題綜效 / Cross-synergies
- [[memory-supercycle]] — same AI-cluster capex; HBM + CPO are co-bottlenecks.
- [[model-leadership-and-data]] — interconnect caps frontier-cluster scale.
- [[../wiki/07_ai_bubble_audit]] — AXTI/AAOI/ALAB late-stage froth.
- [[../watchlist/serenity-supply-chain]] — **verification result below**.

### Serenity watchlist reconciliation (verified)
- ✅ **Confirmed**: Sumitomo 8053.T, Furukawa 5801.T, Lumentum LITE, Coherent COHR as CW/EML bottleneck; TSMC 2330.TW as CPO-chip/COUPE bottleneck; timeline (NVIDIA early-2026, Broadcom 2026 production-intent).
- ⚠️ **Correction**: Broadcom Davisson is **sampling Oct-2025, no firm volume date** — "2026 production" is roadmap, not confirmed [S5]. **VPEC 2455.TW** is an InP **epi** foundry (verified [S10][S17]), not a finished-laser maker — Serenity's "CW laser" label is imprecise.
- ➕ **Missing the deepest node**: the Serenity map lists lasers but underweights **InP substrate** (AXTI/Sumitomo) as the >70%-deficit chokepoint *beneath* the lasers [S15][S16].

## Sources
1. [Scaling AI Factories with Co-Packaged Optics — developer.nvidia.com/blog/scaling-ai-factories-with-co-packaged-optics-for-better-power-efficiency/ — retrieved 2026-05-31 — grade A]
2. [Co-Packaged Optics deep dive / interchip optical market — nextmsc.com/report/interchip-optical-interconnects-market — retrieved 2026-05-31 — grade C]
3. [NVIDIA Spectrum-X Photonics press release — nvidianews.nvidia.com/news/nvidia-spectrum-x-co-packaged-optics-networking-switches-ai-factories — retrieved 2026-05-31 — grade A]
4. [AXT Inc Q1-2026 8-K / $632.5M raise — sec.gov/Archives/edgar/data/0001051627/000143774926014204/ex_906119.htm — retrieved 2026-05-31 — grade A]
5. [Broadcom TH6-Davisson 102.4T CPO announcement — globenewswire.com/news-release/2025/10/08/3163429/19933/en — retrieved 2026-05-31 — grade A]
6. [Copackaged optics found their killer app — theregister.com/2025/11/22/cpo_ai_nvidia_broadcom — retrieved 2026-05-31 — grade B]
7. [NVIDIA invests $4B in Lumentum, Coherent — siliconangle.com/2026/03/02/nvidia-invests-4b-co-packaged-optics-suppliers-lumentum-coherent/ — retrieved 2026-05-31 — grade B]
8. [Coherent's $23B opportunity from NVIDIA optics — futurumgroup.com/insights/coherents-23-billion-growth-opportunity-lifted-by-nvidias-optical-ambitions/ — retrieved 2026-05-31 — grade C]
9. [CPO market forecast + bear case (volume 2yrs out) — mordorintelligence.com/industry-reports/co-packaged-optics-market — retrieved 2026-05-31 — grade C]
10. [AI data centers ignite laser shortage; NVIDIA lock-in — trendforce.com/presscenter/news/20251208-12823.html — retrieved 2026-05-31 — grade B]
11. [Furukawa new DFB laser plant (+500% by 2028, ELSFP/CPO) — furukawaelectric.com/en/release/2025/comm_20251217.html — retrieved 2026-05-31 — grade A]
11b. [Sumitomo data-center growth strategy (+40% EML by 2027, 60% InP) — sumitomoelectric.com/sites/default/files/2025-11/.../Growth%20strategy%20for%20data%20center-related%20business_2025.pdf — retrieved 2026-05-31 — grade A]
12. [800G+ shipments + CPO ports 4.5M / $3.5B 2026 — c-light.com/news/details/AI_Demand_Ignites_the_Optical_Transceiver_Module_Market_in_2026.html — retrieved 2026-05-31 — grade C]
13. [800G+ transceiver 63M units 2026 — mordorintelligence.com/industry-reports/optical-interconnect-market — retrieved 2026-05-31 — grade B]
14. [TSMC CoWoS→CoPoS panels + glass substrate for CPO — techpowerup.com/339963/tsmc-prepares-cowos-to-copos-shift-with-750-x-620-mm-panels — retrieved 2026-05-31 — grade B]
15. [Indium Phosphide: the quiet bottleneck (supply/demand, yields, AXT 60-70%) — yiazou.com/indium-phosphide-inp-the-quiet-bottleneck-behind-the-ai-infrastructure-boom-2/ — retrieved 2026-05-31 — grade C]
16. [InP substrate shortage new bottleneck (IntelliEPI) — digitimes.com/news/a20251229PD212/substrate-intelliepi-demand-data-growth.html — retrieved 2026-05-31 — grade B]
17. [Why CPO uses external lasers (ELS architecture) — viksnewsletter.com/p/why-cpo-uses-external-lasers — retrieved 2026-05-31 — grade D]
18. [ABF substrate market +10.6% CAGR to $9.55B 2032 — intelmarketresearch.com/abf-substrate-market-21855 — retrieved 2026-05-31 — grade C]
19. [Ajinomoto/ABF supply-demand gap to 2027, CPO drives demand — wccftech.com/msg-maker-ajinomoto-to-raise-prices-as-abf-substrate-supply-demand-gap-extends-to-2027/ — retrieved 2026-05-31 — grade B]
20. [Amphenol GB200 NVL72 5,184 copper cables/rack, +134% — globaltechresearch.substack.com/p/nvidia-nvda-us-2025-gtc-review-is — retrieved 2026-05-31 — grade B]
21. [Marvell 1.6T/800G optics + NPO/CPO positioning (Form 8-K FY2026) — sec.gov/Archives/edgar/data/0001835632/000183563226000014/q127_8kx522026ex-991.htm — retrieved 2026-05-31 — grade A]
