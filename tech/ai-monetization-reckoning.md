---
type: synthesis
domain: tech-trend
tags: [ai-monetization, roi, regime-shift, inference, falsifiable, capex]
as_of_timestamp: 2026-05-31T08:30:00+08:00
author_role: researcher
status: live
schema_version: 1
confidence: 0.68
verdict: 結構
verdict_by_horizon: {T0: "結構", T1: "結構→質變(條件)", T2: "質變 or 過熱出清"}
rubric: {A1: 2, A2: 1, A3: 2, A4: 1, A5: 2}
sources_grade_summary: "A: 2  B: 5  C: 5  D: 0  E: 0"
sequel_to: "[[ai-eats-software]]"
---

# AI 變現清算 / The AI Monetization Reckoning

## 0. 一句話判決 / Verdict

**結構性轉捩點 (結構), confidence 0.68.** The dominant market question for 2026→2028 is not which AI model wins. It is: does the $650–725B hyperscaler capex being deployed in 2026 alone [[1]] actually convert into software-layer earnings that justify those multiples — or does it strand as infrastructure the way Cisco's routers did in 2000? This regime shift does not require the technology to fail. It requires only that the *translation from capex to software P&L* moves slower than the equity market already priced. Every other regime question (NVDA's multiple, memory supercycle duration, software re-rating) is downstream of this one. A verdict of **結構** means the dynamic is real and is driving capital allocation now, but the equity upside at current multiples depends almost entirely on which path resolves — bull or bear — rather than on the trend existing at all.

---

## 1. 兩個政體的定義 / The Two Regimes

**Regime 1 — AI Capex Buildout (2024–2026 dominant):**
- Who wins: NVDA / AVGO / memory (HBM) / optical (CPO) / power / data center construction.
- Logic: "the railroads are being built; own the shovels." Hardware has durable lead because you cannot run inference you have not built.
- Evidence it is working: hyperscalers committed $650–725B capex in 2026 [1] (cross-confirmed, grade B); NVDA ~90% AI GPU share [1]; [[memory-supercycle]] HBM supply discipline; [[optical-interconnect-cpo]] CPO ramp.

**Regime 2 — AI ROI / Monetization Reckoning (2026→2028, the inflection question):**
- Who wins or who unwinds: software / application layer re-rates if ROI proves; infra de-rates if it does not.
- Logic: ~$100s billions in capex must eventually translate into enterprise software revenue acceleration and margin expansion, or the capex was borrowed from the future and the cycle will correct. As with Cisco in 2000, the technology can be entirely real while the equity is entirely wrong.
- The question is datable: the window is roughly 2026–2028, where most enterprise AI pilots either reach production P&L or are quietly shelved.

**The pivot signal:** when hyperscaler capex guidance first *decelerates* (not even reverses), infrastructure names will face the same multiple compression the Regime 1 narrative bid them up to avoid. That single data point is the dominant trigger for [[nvda-bull-bear-tracker]].

---

## 2. 多空路徑與可證偽訊號 / Bull & Bear Paths

### Bull Path — ROI Shows Up

Software / application layer re-rates meaningfully upward. Infra holds at elevated multiples because the spend continues. The ~5% of pilots that currently reach P&L impact [8] accelerates to 20–30%+ by 2027, validating the "$1T enterprise AI TAM" narrative.

**Investable implication:** the capturers identified in [[ai-eats-software]] (MSFT, CRM, NOW, PLTR) see NRR on AI SKUs climb above 120–130%; AI-attributable revenue becomes a disclosed, growing line rather than a rounding error. Inference cost per token continues its ~40–900×/year collapse [5] WHILE usage-based revenue (RPO + consumption backlog) accelerates — i.e., cheaper inference drives *more* usage, not margin-only arbitrage.

### Bear Path — ROI Does Not Show

The capex is a stranded build-out. Pilots stay stuck in pilot (88–95% failure to reach production, multiple sources [8][9]). Enterprise budgets rotate back to infrastructure debt pay-down rather than AI upsell. The hyperscalers — having spent $650–725B in 2026 alone [1] — face shareholder pressure and trim or defer 2027 capex guidance.

**The Cisco-2000 analogy is structural:** Cisco grew 2× in the bubble years; revenues were real; the routers were used. Yet the stock fell ~86% from peak because the *pace of capex* was pricing in a demand curve that took 15 more years to materialise. NVDA does not need to be wrong about AI to re-rate — it needs the *pace premium* to evaporate. See [[../wiki/07_ai_bubble_audit]] for the late-cycle framework this path maps onto.

**Investable implication:** NVDA / AVGO / memory names de-rate 40–70% from 2026 peaks even in a world where AI is used daily by billions. The application layer offers no refuge if the NRR data also stays stuck (sequential pilots spending with no compound expansion).

---

## 3. 計分板 / Scorecard (as_of 2026-05-31)

| Signal | Bull Threshold | Bear Threshold | Current Read | Source Grade |
|---|---|---|---|---|
| MSFT Copilot paid seats & ARR growth | >250% YoY seat growth + AI revenue >$50B ARR | Seat growth stalls <50% YoY; AI ARR decelerates | 20M paid Copilot seats, +250% YoY; AI ARR surpassed $37B run-rate, +123% YoY — *BULL* [2] | B / cross-confirmed |
| CRM Agentforce NRR on AI SKUs | NRR >120% on AI SKUs; ARR acceleration | ARR stalls <$500M; GRR declines from ~92% | ARR ~$540M [est. early-2026] / $800M [as of Q4 FY26 per [[ai-eats-software]]] — *NEUTRAL/early bull* [3] | B / single-source-pending on NRR figure |
| NOW AI revenue & renewal rate | AI-specific ARR >$1B; NRR 120–125% | Renewal rates <100%; Now Assist deal velocity slows | Targeting $1B AI-specific revenue 2026; NRR 120–125%; 35 deals >$1M for Now Assist — *BULL* [6] | C / single-source-pending on exact NRR |
| PLTR US commercial NRR | US commercial growth >100% YoY sustained | Growth deceleration below 40% YoY | US commercial Q1'26 +133% YoY to $595M — *BULL* per [[ai-eats-software]] | B / cross-confirmed via filings |
| Enterprise pilot→production rate | Conversion >20% of pilots reaching P&L ROI | Stays at 5–12%; IBM puts "expected ROI" orgs at 25% but that is aspirational | ~5–12% of pilots reach production (IDC/Lenovo: 4/33 POCs); ~5% reach rapid P&L impact (MIT NANDA) — *BEAR* [8][9] | B / cross-confirmed multiple secondary sources |
| Inference cost/token trend | Continues 40–900×/year decline AND usage-based revenue grows faster than margin compression | Cost collapse triggers commoditisation; NRR stalls as customers migrate to cheaper providers | >280× collapse in 18 months to Oct 2024 (Stanford AI Index); cost decline continuing — cost trend BULL; usage monetization still inconclusive — *SPLIT* [5] | A / primary (Stanford HAI report) |
| Hyperscaler capex guidance (the trigger) | 2027 capex guidance raised or maintained vs 2026; Google Cloud backlog ~$460B still growing [1] | ANY major hyperscaler trims 2027 capex guidance by >10% | 2026 capex $650–725B [1]; Meta raised guidance mid-year [1]; Google Cloud backlog ~$460B+ — *BULL* for now, but this is the single most-watched bear trigger | B / cross-confirmed |
| AI-attributable gross profit ($) at hypers | Cloud AI GM% stable or expanding as inference scales | GM% compression as inference commodity pricing accelerates | Not yet disclosed as line item by MSFT/GOOGL/AMZN — *UNRESOLVED* | — |

**Scorecard summary as_of 2026-05-31:** 4 signals BULL, 1 BEAR (pilot conversion), 1 SPLIT (inference cost vs monetization), 1 BULL-but-fragile (capex), 1 UNRESOLVED (hyper GM%). The regime is still leaning Regime 1 (capex), but the single most dangerous forward indicator — enterprise ROI conversion — is still stuck in the bear zone.

---

## 4. NVDA への連結 / Linkage to Principal's NVDA Exposure

This reckoning is the *upstream cause* of every NVDA scenario. The principal's ~$130K NVDA RSU exposure (see memory index) is a direct Regime 1 bet. The Regime 2 transition does not require NVDA's technology to fail or a competitor to emerge — it requires only the capex guidance trigger above to flip.

Explicitly: if **any** major hyperscaler (MSFT, GOOGL, META, AMZN) cuts 2027 capex guidance by >10% vs 2026 actuals, the assumption embedded in NVDA's current multiple (~30–35× fwd) unravels faster than fundamentals because the multiple was pricing continued capex acceleration. This is the primary falsifier to track in [[nvda-bull-bear-tracker]].

The **bear path is non-linear**: a single bad quarter of capex guidance can reprice NVDA 20–30% before the next earnings, because the multiple is entirely forward-looking. The *technology risk* to NVDA is minor compared to the *narrative risk* of regime pivot.

---

## 5. 跨主題綜效 / Cross-synergies

- [[ai-eats-software]] — the application capture thesis is the bull path's core mechanism; the ~95% pilot failure rate is the same data point this page calls a bear signal. The two pages should be read together.
- [[memory-supercycle]] — if Regime 2 bear path triggers, capex cuts flow directly to HBM demand; the supercycle ends before the supply build does (exactly the Phase-A finding that "stock is ahead of fundamentals").
- [[bayesian-bottleneck-engine]] — the scorecard above is a qualitative likelihood update. The bear trigger (hyperscaler capex cut) has `LR >> 1` because it is a primary, hard-to-dispute, low-noise signal.
- [[99_cross_synthesis]] §5 master conclusion — "stock prices simultaneously ahead of memory, CPO, model-layer, software-winner fundamentals" is this page's regime-shift risk made explicit across the portfolio.
- [[../wiki/07_ai_bubble_audit]] — the late-cycle bubble framework; the Cisco-2000 analogy lives there.
- [[../wiki/07_ai_bubble_audit]] §6 — platform-tier multiples 25–35× fwd already embed the bull path; this page quantifies what happens if those multiples were wrong.

---

## 6. 同溫層風險 / Echo-chamber risk

The bull path is currently the consensus. Every hyperscaler earnings call in 2025–26 leads with AI capex expansion. Every sell-side model has NRR expansion as the base case. The risk the desk must guard against is not the obvious bear case — it is the **incremental-deterioration bear case**: not a collapse, but a slow stall where NRR stays at 110% instead of going to 130%, where Copilot at 20M seats still converts only 5% of the 400M+ M365 commercial seats, where PLTR growth is real but PLTR at 100× P/S is still the wrong price. The Cisco lesson was not that routers stopped working. It was that the *pace assumption* was wrong by 10–15 years.

**The precise echo-chamber gap:** the market is pricing the bull path's best-case speed. The pilot conversion data (4/33 → production; ~5% P&L impact) is pricing the bear path's current reality. The gap between those two numbers — compressing or widening — is the regime's falsifier.

---

## Sources

1. Hyperscaler capex 2026 $650–725B, NVDA ~90% GPU share, Meta raised guidance, Google Cloud backlog ~$460B — https://finance.yahoo.com/sectors/technology/articles/hyperscalers-hit-700-billion-2026-111243744.html and https://alcapitaladvisory.com/research/intelligence/ai-infrastructure.html — retrieved 2026-05-31 — grade B / cross-confirmed
2. MSFT Copilot 20M paid seats +250% YoY; AI ARR >$37B +123% YoY — https://www.tikr.com/blog/microsoft-37-billion-ai-business-is-just-the-beginning-heres-what-the-market-is-missing — retrieved 2026-05-31 — grade B / cross-confirmed (Satya Nadella IR statement)
3. CRM Agentforce ARR ~$540M (early 2026 est.) — https://www.the-ai-corner.com/p/saas-defense-playbook-ai-era-survival-guide-2026 — retrieved 2026-05-31 — grade C / single-source-pending; $800M Q4 FY26 per [[ai-eats-software]] [14] is grade B
4. SaaS NRR 120–130%+ premium valuation band; public SaaS >120% NRR at ~9.3× EV/rev vs <3.1× below 100% — https://www.m3ter.com/blog/net-revenue-retention — retrieved 2026-05-31 — grade C
5. Stanford AI Index 2025: >280× inference-cost collapse over 18 months; 40–900×/year by task; GPT-4-level cost decline — https://hai.stanford.edu/news/ai-index-2025-state-of-ai-in-10-charts and https://hai.stanford.edu/assets/files/hai_ai-index-report-2025_chapter1_final.pdf — retrieved 2026-05-31 — grade A / primary-fetched
6. ServiceNow targeting $1B AI revenue 2026; NRR 120–125%; Now Assist 35 deals >$1M — https://www.fool.com/investing/2026/02/11/better-ai-software-stock-servicenow-vs-salesforce/ — retrieved 2026-05-31 — grade C / single-source-pending
7. Salesforce GRR ~92% (8% attrition), consistent Q4 FY2026 — https://www.saasletter.com/p/ai-nrr-gross-margin-efficient-frontier-2026-gtm-sales-benchmarks-fullcast-pavilion — retrieved 2026-05-31 — grade C
8. Enterprise AI pilot failure: ~95% fail P&L impact (MIT NANDA, multiple secondary confirmations); IDC/Lenovo: 4/33 POCs reach production (~12%) — https://masterofcode.com/blog/ai-roi and https://www.softwareseni.com/why-88-to-95-percent-of-enterprise-ai-pilots-never-reach-production/ — retrieved 2026-05-31 — grade B / cross-confirmed
9. IBM: 25% of enterprises achieve expected ROI (aspirational framing); Wing VC enterprise state-of-AI — https://www.wing.vc/content/the-state-of-ai-in-the-enterprise — retrieved 2026-05-31 — grade C

---

*Research/educational only — not buy/sell advice. Observe-first.*
