---
type: synthesis
domain: tech-trend
tags: [china-ai, deepseek, qwen, smic, huawei-ascend, export-controls, hbm, bifurcation, nvidia-china]
as_of_timestamp: 2026-05-31T04:30:00+08:00
author_role: researcher
phase: C
confidence: 0.78
verdict: 結構
verdict_by_horizon: {T0: 結構, T1: 結構, T2: 質變-or-stuck, T3: 質變}
rubric: {A1: 2, A2: 2, A3: 2, A4: 1, A5: 2}
sources_grade_summary: "A: 6 B: 9 C: 3 D: 0 E: 0"
us_tickers: "NVDA, BABA, PDD, BIDU, JD, TCEHY"
---
# 中國 AI 技術堆疊與美中科技分流 / China's AI Stack & the US-China Tech Bifurcation

## 0. 一句話判決 + 桌面觀點 / Verdict + Desk View
**結構 (structural, conf 0.78).** The bifurcation is **already a fact, not a forecast** — two parallel AI stacks now exist, and that is the era-defining change (T0 結構). At the *model* layer China has genuinely closed to within 3–6 months of the US frontier and **won the open-weight world outright** (Qwen >1B downloads, >50% of global open-source share, Chinese bases = 63% of new HF fine-tunes Sep-2025) [Pandaily — grade B][the-decoder/Stanford — grade B]. At the *compute* layer the story is the opposite: China can fab and ship in volume **only because of a finite TSMC die-bank plus foreign HBM**, both of which run out ~late-2026; the domestic substitutes (SMIC enhanced-7nm, CXMT HBM3) exist but at yields/capacity that cap, not close, the gap. **The single falsifiable claim that flips 結構→質變 (T2):** CXMT ships HBM at volume sufficient to feed >1M Ascend packages/yr *and* SMIC holds >50% 5nm yield — proving self-sufficiency without EUV. The claim that flips toward 受損/stuck: the die-bank empties in 2026 and Ascend output *falls* YoY. **Desk view (caveated, not advice):** the cheap-multiple China ADRs (BABA fwd P/E ~19.6x, PDD ~9–11.6x [Yahoo/Intellectia — grade C]) are a *barbell* — real AI-capex beneficiaries trading at a structural policy-risk discount that "is unlikely to fully close" [heygotrade — grade C]. This is a value-on-pullback / Moonshot sleeve question, never a Core conviction, because the binding risk is political, not fundamental.

## 1. 技術底蘊 / Technical moat (A1 = 2)
**Models — real, replicable, frontier-adjacent.** DeepSeek shipped V4 (Pro/Flash) on 2026-04-24, claiming a 3–6-month lag to closed frontier at a fraction of the cost [DataCamp/MindStudio — grade C]. The harder evidence is structural: by Aug-2025 Chinese models **overtook US models in total Hugging Face downloads** (17.1% vs 15.8%, Aug-24→Aug-25) and Qwen replaced Llama as the most-downloaded family [the-decoder/Stanford HAI — grade B]. This is a durable *distribution* moat (the open-weight default), even though no single Chinese model holds a capability *lead* over GPT/Gemini/Claude.
**Domestic compute — replicable-but-bottlenecked.** SMIC reached volume on enhanced-7nm (N+2) with yields improved to ~60–70% and an N+3 "5nm-class" node in production *without EUV*, but at ~33% yield and ~50% higher cost via DUV multi-patterning [design-reuse — grade B][wccftech — grade C]. The Ascend 910C is ~60% of an H100 on inference [Tom's Hardware/CFR — grade B]; CloudMatrix 384 brute-forces past a GB200 NVL72 at the system level (~300 vs 180 PFLOPs, 3.6× memory) but at **4.1× the power** and ~$8.2M vs ~$3M [SemiAnalysis — grade B]. So A1=2: a real, physical, hard-won stack — but its moat is *scale-out engineering around a node/HBM handicap*, not parity at the transistor.

## 2. 需求數據 / Demand reality (A2 = 2)
Adoption, revenue and capex are all hard, not narrative:
| Metric | Figure | Period | Source (grade) |
|---|---|---|---|
| Qwen cumulative downloads | >1B, >200k derivatives | Mar-2026 | Pandaily/SCMP (B) |
| Chinese share of global open-source DLs | >50% (Alibaba alone) | Mar-2026 | SCMP (B) |
| New HF fine-tunes on Chinese bases | 63% | Sep-2025 | the-decoder/Stanford (B) |
| Cambricon FY2025 revenue | ¥6.5B (from ¥1.2B) | FY2025 | Bloomberg/CNBC (B) |
| Cambricon FY2025 net income | ¥2.1B (first-ever profit; vs -¥452M FY24) | FY2025 | Bloomberg (B) |
| SMIC FY2025 revenue | $9.33B, +16.2% YoY; util 95.7% | FY2025 | SemiWiki/futunn (B) |
| Alibaba AI+cloud capex | ¥38.6B record | Q1-FY2026 | taibo/AliCloud (B) |
| Ascend 910C output target | ~600k units 2026 (2× 2025) | 2026 (proj) | Bloomberg/RCR (B) |

Cambricon (688256.SS) is the cleanest demand tell: revenue **quintupled and turned its first annual profit**, driven by ByteDance and Beijing's Nvidia-substitution push [CNBC — grade B]. The echo-chamber correction (§8) is that the *open-weight win has not converted to enterprise API revenue* the way Western desks fear.

## 3. 資金·權威 / Capital & authority (A3 = 2)
Two authorities now write this market. **Beijing** funds substitution (Cambricon/Huawei demand is policy-pulled). **Washington** sets the ceiling via BIS. The hard 資金 number is the impairment: NVDA took a **$4.5B charge** in Q1-FY2026 on H20, lost **$2.5B unshippable** that quarter plus a guided **~$8.0B Q2 loss** — ~$13.5B cumulative against a **$17.1B FY-China base** [NVIDIA 8-K q1fy26 — grade A — primary-fetched]. The 2026 pivot: on 2026-01-13 BIS moved to **case-by-case** licensing for H200/MI325X, and ~10 Chinese firms (Alibaba, Tencent, ByteDance) were cleared to buy H200 at **≤75,000 units each** under a 25% export duty + US third-party security testing [BIS/Federal Register — grade A][Bloomberg — grade B]. Authority is unambiguous and bilateral — hence A3=2.

## 4. 受益 / 受損 / 抄底 / Winners, losers, value-trap (A4 = 1)
**受益 (winners):** Cambricon (688256.SS) and Huawei (private) are the policy-pull beneficiaries; SMIC (0981.HK) runs at 95.7% utilization. Among US-listed: **BABA** (Qwen + ¥380B/$53B 3-yr AI-cloud capex [Bloomberg — grade B]), **TCEHY**/ByteDance (H200-cleared buyers), **PDD/JD/BIDU** as cheap-multiple optionality.
**受損 (losers / impaired):** **NVDA** China DC revenue is materially impaired but **routed around, not destroyed** — the H200 license partially reopens a $17.1B market at a 25% tax. Net: dented, not severed.
**抄底 (value or policy-trap):** China ADRs trade at a *wider-than-average* discount to US peers [heygotrade — grade C]; some of that gap "is structural and unlikely to fully close." That is the trap: cheap *because* of VIE/delisting/sanction tail-risk, not mispricing. A4=1 — investability is **diffuse and policy-gated**, the purest pure-plays (Huawei, CXMT) are unlisted or HK/A-share only, not clean US exposure.

## 5. 多時程 / Multi-horizon
- **T0 (0–1y) 結構:** bifurcation is live; open-weight already won; NVDA China impaired-but-routed.
- **T1 (1–3y) 結構:** die-bank empties (~late-2026), forcing the domestic stack to stand alone; HBM is the binding constraint.
- **T2 (3–5y) 質變-or-stuck:** decided by CXMT HBM3/HBM3E ramp + SMIC 5nm yield. Self-sufficiency proven → 質變; die-bank/HBM wall bites → stuck/受損.
- **T3 (5–10y) 質變:** the *decoupling itself* is the era-impact — two non-interoperable AI stacks, regardless of who leads.

## 6. 爆發條件 + 里程碑 / Triggers + milestones (falsifiable, datable)
1. **SMIC advanced-node yield/capacity** — verify: SMIC IR / TechInsights teardown. Status: 7nm 60–70%, 5nm ~33%; capacity ~45k→60k wspm 2025→2026. Next: 5nm yield >50% by 2027.
2. **Huawei Ascend cluster deployments + die-bank** — verify: SemiAnalysis/Bloomberg shipment counts. Status: ~600k 910C target 2026; TSMC die-bank ~9-mo runway from Feb-2026. Next: does 2027 output rely on domestic-only logic?
3. **CXMT HBM volume** — verify: DigiTimes/Tom's. Status: HBM3 samples to Huawei; ~2.2M stacks 2026 ≈ only 250–400k Ascend packages — **insufficient**. Next: HBM3E in 2027.
4. **DeepSeek/Qwen enterprise share** — verify: Menlo/HF derivative counts. Status: open-weight #1; enterprise-paid share still low. Next: a paid-API share datapoint.
5. **NVDA China revenue trajectory** — verify: NVDA 8-K. Status: ~$13.5B cumulative loss; H200 partially reopened. Next: a China-DC line re-appearing in guidance.
6. **A new export-control round** — verify: Federal Register/BIS. Status: Jan-2026 loosened to case-by-case. Next: B30A decision (tighten or open).

## 7. 時代影響與交互 / Era-impact & interactions
The decoupling forces a permanent **dual supply chain**: foreign HBM/EUV-node access vs domestic CXMT/SMIC. Ties: [[memory-supercycle]] (CXMT is the binding constraint on *both* the China stack and global HBM pricing — China low-spec HBM threatens Korean margins), [[model-leadership-and-data]] (Chinese open-weight vs US frontier — the same three-leaderboard split, here a *national* one), [[autonomous-driving]] (BYD/Huawei ADAS run on this domestic compute), [[humanoid-robotics]] (China humanoid demand pulls the same Ascend/Cambricon silicon), [[ai-edge-devices]] (Qwen/Gemma SLMs on-device).

## 8. 同溫層 + 自我打臉 / Echo-chamber & self-refutation
- **Bull case I must 打臉:** "China closed the gap, self-sufficiency is here." **Refute:** the volume only exists on a *finite TSMC die-bank* (~2.9M dies, ~9-mo runway) and *foreign HBM* (13M stacks); domestic CXMT covers only ~250–400k of the ~1.6M packages needed [SemiAnalysis/Tom's — grade B]. Self-sufficiency is **claimed, not yet demonstrated at the binding input (HBM).**
- **Bear case I must 打臉:** "Export controls killed NVDA China." **Refute:** the Jan-2026 BIS loosening + 75k-unit H200 licenses *reopened* the channel at a 25% tax — impaired, not dead [BIS — grade A].
- **The most dangerous comforting claim (both sides):** US bulls say "China can't make leading-edge"; China bulls say "EUV doesn't matter." Both overshoot — DUV 5nm *works* but at 33% yield/+50% cost, an economic handicap, not an impossibility.
- **Conflict flagged:** Cambricon's own initial FY25 guide (¥60–70B) vs actual ¥6.5B — a likely currency/units error in one secondary; the audited Bloomberg/CNBC ¥6.5B figure is used. CXMT mass-production timing is `contradicted` (Tom's "end-2026" vs DigiTimes "slips past 2026").

## Sources
1. NVIDIA Q1 FY2026 results (8-K) — https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-first-quarter-fiscal-2026 — retrieved 2026-05-31 — grade A — primary-fetched
2. NVIDIA Q1 FY26 8-K (SEC) — https://www.sec.gov/Archives/edgar/data/1045810/000104581025000115/q1fy26pr.htm — retrieved 2026-05-31 — grade A — cross-confirmed
3. BIS revises license review policy for semiconductors to China — https://www.bis.gov/press-release/department-commerce-revises-license-review-policy-semiconductors-exported-china — retrieved 2026-05-31 — grade A — primary-fetched
4. Federal Register: Revision to License Review Policy (2026-01-15) — https://www.federalregister.gov/documents/2026/01/15/2026-00789/revision-to-license-review-policy-for-advanced-computing-commodities — retrieved 2026-05-31 — grade A — cross-confirmed
5. Nvidia gets US license for H200 to China (75k/customer) — https://www.bloomberg.com/news/articles/2026-02-26/nvidia-gets-us-license-for-small-amount-of-h200-exports-to-china — retrieved 2026-05-31 — grade B — single-source-pending
6. China captured open-weight lead 2025 (Stanford/The Decoder) — https://the-decoder.com/china-captured-the-global-lead-in-open-weight-ai-development-during-2025-stanford-analysis-shows/ — retrieved 2026-05-31 — grade B — cross-confirmed
7. Qwen >1B downloads, 200k derivatives (Pandaily) — https://pandaily.com/alibaba-s-qwen-open-source-models-surpass-1-billion-downloads-ranking-first-globally — retrieved 2026-05-31 — grade B — cross-confirmed
8. Qwen >50% global open-source share (SCMP) — https://www.scmp.com/tech/big-tech/article/3349552/ — retrieved 2026-05-31 — grade B — cross-confirmed
9. SMIC 5nm N+3 without EUV (Design&Reuse) — https://www.design-reuse.com/news/202529830-chinese-smic-achieves-5-nm-production-on-n-3-node-without-euv-tools/ — retrieved 2026-05-31 — grade B — cross-confirmed
10. SMIC 5nm ~33% yield, +50% cost (wccftech) — https://wccftech.com/smic-5nm-development-completed-in-2025/ — retrieved 2026-05-31 — grade C — single-source-pending
11. SMIC Q4/FY2025 revenue $9.33B, util 95.7% (futunn) — https://news.futunn.com/en/post/68691141/ — retrieved 2026-05-31 — grade B — cross-confirmed
12. Huawei CloudMatrix 384 vs GB200 (SemiAnalysis) — https://newsletter.semianalysis.com/p/huawei-ai-cloudmatrix-384-chinas-answer-to-nvidia-gb200-nvl72 — retrieved 2026-05-31 — grade B — cross-confirmed
13. Ascend 910C ~60% of H100 (Tom's Hardware/CFR) — https://www.tomshardware.com/tech-industry/semiconductors/huawei-still-cant-match-nvidia-on-ai-chips-says-cfr-report — retrieved 2026-05-31 — grade B — cross-confirmed
14. Huawei Ascend production ramp, die-bank, HBM bottleneck (SemiAnalysis) — https://newsletter.semianalysis.com/p/huawei-ascend-production-ramp — retrieved 2026-05-31 — grade B — single-source-pending
15. Cambricon first annual profit, ¥6.5B rev (CNBC) — https://www.cnbc.com/2025/08/27/china-nvidia-rival-cambricon-posts-record-profit-4000percent-revenue-jump.html — retrieved 2026-05-31 — grade B — cross-confirmed
16. CXMT HBM3 timeline + 2.2M stacks (Tom's Hardware) — https://www.tomshardware.com/pc-components/dram/chinese-semiconductor-industry-gears-up-for-domestic-hbm3-production-by-the-end-of-2026 — retrieved 2026-05-31 — grade B — contradicted
17. CXMT HBM3 mass-production slips (DigiTimes) — https://www.digitimes.com/news/a20260421PD230/cxmt-hbm3-dram-production-2026.html — retrieved 2026-05-31 — grade B — contradicted
18. Alibaba ¥380B/$53B 3-yr AI capex (Bloomberg) — https://www.bloomberg.com/news/articles/2025-02-24/alibaba-to-spend-53-billion-on-ai-infrastructure-in-big-pivot — retrieved 2026-05-31 — grade B — cross-confirmed
19. China ADR risk premium BABA/PDD/JD (heygotrade) — https://www.heygotrade.com/en/blog/china-adr-risk-premium-baba-pdd-jd-2026/ — retrieved 2026-05-31 — grade C — single-source-pending
