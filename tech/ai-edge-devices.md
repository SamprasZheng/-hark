---
type: synthesis
domain: tech-trend
tags: [ai-pc, copilot-plus, apple-intelligence, vision-pro, on-device-slm, edge-ai]
as_of_timestamp: 2026-05-31T01:15:00+08:00
author_role: researcher
confidence: 0.72
verdict: 過熱
rubric: {A1: 1, A2: 1, A3: 2, A4: 2, A5: 1}
sources_grade_summary: "A: 5 B: 7 C: 2 D: 1 E: 0"
---
# AI 端側裝置 — AI PC / NB / iPhone / Vision Pro / On-device AI

## 0. 一句話判決 / Verdict
**過熱 (vendor-pushed narrative), confidence 0.72.** The hardware refresh is real, but it is driven by **Windows 10 end-of-support + an aged installed base + ASP/memory inflation**, NOT by AI features pulling purchases. Sharpest falsifiable claim: *in 2025, AI features were the chief upgrade reason for fewer than ~15% of buyers across PC and phone, while Gartner cut its own 2025 AI-PC forecast from 114M/43% to 77.8M/31% within 11 months* — if 2026 surveys show AI as the #1 stated driver (>30%) or Copilot+ activation/usage breaks out, this flips to 結構.

## 1. 技術底蘊 / Technical moat (A1)
The "AI PC" is defined by an NPU; Microsoft's **Copilot+** bar is **≥40 TOPS** [Gartner — gartner.com/.../2024-09-25 — retrieved 2026-05-31 — A]. Current silicon clears it: AMD Ryzen AI 300 ~50 TOPS, Intel Lunar Lake 48, Qualcomm Snapdragon X Elite 45; Snapdragon X2 Elite Extreme pushes to ~80, Intel Panther Lake (18A, H1-2026) ~50 [Wccftech/PCQuest — wccftech.com/qualcomm-snapdragon-x2... — retrieved 2026-05-31 — C]. But TOPS is a weak moat: real-app tests show architecture/software matter more than raw TOPS, and there is no single killer NPU workload [NewTechGuy — newtechguy.com/ai-pc-buying-guide-2025 — retrieved 2026-05-31 — C]. Moat = 1: the IP is concentrated (ARM/QCOM/AAPL) but the *consumer-facing* differentiation is thin.

## 2. 需求真實性 — 數據 / Demand reality (A2)

| 指標 Metric | 數值 Value | 日期 Date | 來源 (grade) |
|---|---|---|---|
| AI-PC share of shipments 2024 | 17% | 2024 | Gartner (A) |
| Gartner 2025 AI-PC forecast (original) | 114M units / 43% | Sep 2024 | Gartner (A) |
| Gartner 2025 AI-PC forecast (**revised down**) | **77.8M / 31%** | Aug 28 2025 | Gartner (A) |
| Canalys/Counterpoint AI-capable share 2026 | **>50%** | Sep 8 2025 | Counterpoint (B) |
| Win10 install base at EOL | ~646M / ~46% of Windows | Aug 2025 | Omdia/PIRG (B) |
| PCs that *can't* upgrade to Win11 | ~400M | 2025 | PIRG (B) |
| iPhone 2025 shipments | 247.4M (+6.1% YoY) | Dec 2 2025 | IDC (A) |
| iPhone buyers citing AI as chief reason | **14%** (CIRP) / **7.1%** (SellCell) | Sep 2025 | CIRP/SellCell (B) |
| iPhone buyers: "phone needs replacing" | 49% | Sep 2025 | CIRP (B) |
| Vision Pro units 2024 | 390k | 2024 | IDC (A) |
| Vision Pro units, holiday Q 2025 | **45k** | Jan 2 2026 | IDC (A) |

The demand is real in *units* but mis-attributed: refresh, not AI, is doing the work. A2 = 1.

## 3. 資金與權威背書 / Capital & authority (A3)
Full-stack backing: Microsoft (Copilot+ marketing + Win11/Win10-EOL forcing function), Apple (Apple Intelligence + custom silicon), Qualcomm/Intel/AMD silicon roadmaps, and the entire OEM channel (Dell/HP/Lenovo). Win10 commercial ESU starts at $61/device and doubles yearly — a deliberate stick to force migration [Microsoft Support — support.microsoft.com/.../windows-10-support-has-ended — retrieved 2026-05-31 — A]. iPhone fiscal-Q1 revenue +23% YoY (ASP-led; units +5% to 81.3M) [Motley Fool/IDC — fool.com/.../2026/02/03 — retrieved 2026-05-31 — B]. Authority is unambiguous. A3 = 2.

## 4. 供應鏈與可投資節點 / Supply chain & investable nodes (A4)
The investable edge is **silicon IP + memory content uplift**, not the OEM box. NPU/IP: ARM (architecture royalty), QCOM (Snapdragon X / Oryon), AMD (Ryzen AI), INTC (Lunar/Panther Lake), AAPL (A/M-series, in-house). The cleaner chokepoint is **DRAM**: Copilot+ mandates ≥16GB, and DRAM+NAND is rising from 10–18% of laptop BOM toward >20% in 2026 as LPDDR5X prices spike ~90% QoQ [TrendForce/Tom's Hardware — tomshardware.com/.../lpddr5x... — retrieved 2026-05-31 — B]. This is the explicit synergy with [[memory-supercycle]]: every AI PC/phone is a memory-content multiplier, and pricing power sits with the three DRAM makers (Samsung, SK Hynix, Micron) more than with NPU vendors. A4 = 2.

## 5. 大模型 vs 小模型 / Model angle
Edge structurally **favors small models (SLMs)**. Apple's on-device model is **~3B params, quantized to ~2 bits/weight (QAT)**, with a 5:3 block split sharing KV-cache to cut memory 37.5% — engineered for time-to-first-token on-device, with heavy requests escalated to Private Cloud Compute [Apple ML — machinelearning.apple.com/research/apple-foundation-models-2025-updates — retrieved 2026-05-31 — A]. Peers: Microsoft Phi Silica, Google Gemini Nano (1.8B/3.25B in Android AICore), Llama 3.2 1B/3B [arXiv 2505.16508 — arxiv.org/pdf/2505.16508 — retrieved 2026-05-31 — B]. Implication: on-device is a *hybrid* — small local SLM for latency/privacy, large cloud model for hard tasks — so edge devices are a tailwind for SLM tooling and the memory/NPU stack, not a substitute for datacenter compute (cf. [[model-leadership-and-data]]).

## 6. 顛覆 / 取代向量 / Disruption vector (A5)
Datable disruption is **modest and lateral**, not a step-change. (a) Win10 EOL (Oct 14 2025) is a hard, datable catalyst forcing a multi-year corporate refresh — but it disrupts *the upgrade calendar*, not the user experience. (b) Vision Pro's spatial-computing thesis has **failed as a disruption vector**: ~390k (redacted) → 45k (holiday Q 2025), marketing cut >95%, gen-2 paused; Apple is pivoting to cheaper headsets/AI glasses [PYMNTS — pymnts.com/apple/2026/apple-retreats-on-vision-pro — retrieved 2026-05-31 — B]. (c) Smart glasses (Meta) are the live disruption story, outside this hardware-refresh frame. A5 = 1 (refresh timing is datable; product-level disruption is not yet proven).

## 7. 同溫層風險 + 空方論點 / Echo-chamber flags + bear case
**The echo-chamber gap is the headline finding.** The narrative ("AI is driving a hardware super-cycle") is contradicted by hard adoption data:
- **Vendor forecasts are being cut, not raised:** Gartner revised 2025 AI-PC from 114M/43% → 77.8M/31% in <1yr [Gartner — gartner.com/.../2025-08-28 — retrieved 2026-05-31 — A]. The "40%/50%" headlines mostly redefine "AI PC" to mean *any NPU* — most are sub-40-TOPS, not Copilot+.
- **Buyers don't buy for AI:** CIRP 14% / SellCell 7.1% cite AI as chief reason vs 53.2% battery / 49% replacement [SellCell — sellcell.com/blog/iphone-17-pre-launch-survey — retrieved 2026-05-31 — B].
- **AI features rated low-value:** 73% of iPhone and 87% of Samsung users say AI adds little/no value [SellCell — sellcell.com/blog/iphone-vs-samsung-ai-survey — retrieved 2026-05-31 — B].
- **Software pull is absent:** Copilot (web) stuck ~1% share; among triers only 8% keep choosing it [Windows Latest — windowslatest.com/2026/01/09 — retrieved 2026-05-31 — C].
- **Apple's own AI is slipping:** revamped Siri delayed to 2026 [CNBC — cnbc.com/2025/09/19 — retrieved 2026-05-31 — B].
**Bear case:** the unit growth is a one-time pull-forward (Win10 EOL + aged base + ASP/memory inflation). Strip AI out and the cycle still happens; AI is the *marketing wrapper*, and the real margin accrues to **memory**, not NPU storytelling.

## 8. 跨主題綜效 / Cross-synergies
- [[memory-supercycle]] — every AI PC/phone lifts DRAM/NAND BOM; ≥16GB mandate + LPDDR5X spike is the cleanest investable beneficiary.
- [[model-leadership-and-data]] — hybrid edge SLM ↔ cloud LLM split; on-device favors small models but escalates hard tasks to datacenter.
- [[optical-interconnect-cpo]] — indirect: the cloud half of hybrid inference still rides datacenter scale-up.
- [[ai-eats-software]] — Copilot/Apple Intelligence adoption is the demand-side test of whether AI features monetize at the edge.

## Sources
1. Gartner — Worldwide AI PC shipments to account for 43% of all PCs in 2025 (114M; 17%→43%) — https://www.gartner.com/en/newsroom/press-releases/2024-09-25-gartner-forecasts-worldwide-shipments-of-artificial-intelligence-pcs-to-account-for-43-percent-of-all-pcs-in-2025 — retrieved 2026-05-31 — grade A
2. Gartner — AI PCs will represent 31% of worldwide PC market by end of 2025 (77.8M; revised down) — https://www.gartner.com/en/newsroom/press-releases/2025-08-28-gartner-says-artificial-intelligence-pcs-will-represent-31-percent-of-worldwide-pc-market-by-the-end-of-2025 — retrieved 2026-05-31 — grade A
3. Counterpoint Research — AI-advanced PCs to surpass half of global shipments in 2026 — https://counterpointresearch.com/en/reports/ai-advanced-pcs-to-surpass-half-of-global-shipments-in-2026 — retrieved 2026-05-31 — grade B
4. Microsoft Support — Windows 10 support has ended on October 14, 2025 (ESU $61, doubling) — https://support.microsoft.com/en-us/windows/windows-10-support-has-ended-on-october-14-2025-2ca8b313-1946-43d3-b55c-2b95b107f281 — retrieved 2026-05-31 — grade A
5. Omdia — Microsoft has ended support for Windows 10, now what (~646M base; ~400M can't upgrade) — https://omdia.tech.informa.com/blogs/2025/oct/microsoft-has-ended-support-for-windows-10-now-what — retrieved 2026-05-31 — grade B
6. MacRumors/IDC — iPhone 17 demand breaking records (247.4M 2025, +6.1%, China >20%) — https://www.macrumors.com/2025/12/02/apple-2025-iphone-sales-record/ — retrieved 2026-05-31 — grade A
7. Motley Fool/IDC — Apple's surging iPhone sales aren't really about AI (Q1 +23% rev, units +5% to 81.3M; CIRP 49%/14%) — https://www.fool.com/investing/2026/02/03/apples-surging-iphone-sales-arent-really-about-ai/ — retrieved 2026-05-31 — grade B
8. SellCell — iPhone 17 pre-launch survey (68.3% upgrade intent; battery 53.2% vs AI 7.1%) — https://www.sellcell.com/blog/iphone-17-pre-launch-survey/ — retrieved 2026-05-31 — grade B
9. SellCell — iPhone vs Samsung AI survey (73% iPhone / 87% Samsung say AI adds little/no value) — https://www.sellcell.com/blog/iphone-vs-samsung-ai-survey/ — retrieved 2026-05-31 — grade B
10. MacRumors/IDC — Vision Pro still failing to catch on (390k 2024; 45k holiday Q 2025) — https://www.macrumors.com/2026/01/02/vision-pro-still-failing-to-catch-on/ — retrieved 2026-05-31 — grade A
11. PYMNTS — Apple retreats on Vision Pro as demand falls short (marketing -95%, gen-2 paused) — https://www.pymnts.com/apple/2026/apple-retreats-on-vision-pro-as-consumer-demand-falls-short/ — retrieved 2026-05-31 — grade B
12. Apple Machine Learning — Apple foundation models 2025 updates (~3B on-device, 2-bit QAT, KV-cache 5:3) — https://machinelearning.apple.com/research/apple-foundation-models-2025-updates — retrieved 2026-05-31 — grade A
13. Tom's Hardware/TrendForce — LPDDR5X prices to double; DRAM+NAND >20% of laptop BOM in 2026 (~90% QoQ) — https://www.tomshardware.com/pc-components/dram/nvidias-demand-for-lpddr5x-could-double-smartphone-and-server-memory-prices-in-2026 — retrieved 2026-05-31 — grade B
14. arXiv 2505.16508 — Edge-First Language Model Inference (Gemini Nano, Phi, Llama 3.2 1B/3B) — https://arxiv.org/pdf/2505.16508 — retrieved 2026-05-31 — grade B
15. Wccftech/PCQuest — Snapdragon X2 / Lunar Lake / Ryzen AI NPU TOPS comparison — https://wccftech.com/qualcomm-snapdragon-x2-elite-cpu-gpu-npu-performance-versus-intel-amd/ — retrieved 2026-05-31 — grade C
16. Windows Latest — Copilot (web) stuck at ~1% share; only 8% of triers keep it — https://www.windowslatest.com/2026/01/09/is-microsoft-losing-the-ai-race-copilot-web-is-still-stuck-at-1-market-share/ — retrieved 2026-05-31 — grade C
17. CNBC — iPhone 17 launch, China & AI strategy questions (Siri delayed to 2026) — https://www.cnbc.com/2025/09/19/apple-iphone-17-launch-sale-globally-china-market-and-ai-strategy.html — retrieved 2026-05-31 — grade B

