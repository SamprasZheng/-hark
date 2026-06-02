---
type: synthesis
domain: tech-trend
tags: [ai-software, saas-disruption, code-gen, agents, valuation-compression, winners-losers]
as_of_timestamp: 2026-05-31T01:15:00+08:00
author_role: researcher
confidence: 0.72
verdict: 結構
rubric: {A1: 2, A2: 2, A3: 2, A4: 1, A5: 1}
sources_grade_summary: "A: 5  B: 7  C: 4  D: 2  E: 0"
---
# AI 吃軟體 — SaaS 軟體股會崩嗎? / Is AI Eating Software?

## 0. 一句話判決 / Verdict
**結構性分化 (結構), confidence 0.72.** The principal's thesis is HALF right: AI is a real 質變 for *low-moat, single-feature, seat-based* SaaS (Chegg lost ~99% of a $14B cap; Stack Overflow question volume −90%), but it is FALSE as a blanket "all software collapses" claim — aggregate enterprise software spend is *accelerating* to ~$1.44T in 2026 (+15.1% YoY) and incumbents with data+distribution+workflow moats (MSFT, CRM, NOW, INTU, PLTR) are *capturing* AI revenue, not dying to it. **Sharpest falsifiable claim:** if AI were broadly destroying SaaS, 2026 software spend growth would be *decelerating below* its ~11.5% 2025 rate — instead Gartner *revised it UP* to ~15.1% [8]. The disruption is a knife, not a flood: it cuts specific workflows (homework help, Q&A forums, basic translation, junior dev tooling) while the platform layer levers up. The "software is dead" Twitter narrative is the echo-chamber error.

## 1. 技術底蘊 / Technical moat (A1 = 2)
Does code-gen / agents actually erode SaaS moats? **Yes, for the moat that was just "a UI over a database + a workflow."** Two mechanisms are now empirically live, not theoretical:
1. **Demand-side substitution via answer-engines.** When the *output* a SaaS sold (an answer, a translation, a snippet, a summary) is now produced for free inside ChatGPT or Google AI Overviews, the SaaS's organic-search funnel collapses. Stack Overflow monthly posts fell >90% from the 2020 peak and −64% YoY in April 2025 [3]; Chegg attributes its collapse jointly to ChatGPT *and* Google AI Overviews [4][6].
2. **Supply-side: code-gen compresses the cost of building the SaaS itself.** Cursor/Anysphere hit ~$2B ARR by Feb 2026 — zero-to-$2B in ~3 years, the fastest in B2B software history [1] — and GitHub Copilot crossed ~20M users / ~4.7M paid by Jan 2026 [7]. If a competent feature is now a weekend of agent-assisted coding, *single-feature* SaaS moats (the "we built the integration first" advantage) shrink toward zero.
**Limit:** code-gen does NOT erode moats built on (a) proprietary data, (b) distribution/install base, (c) compliance/system-of-record lock-in, or (d) regulated workflows. That asymmetry is the whole investment thesis (§4).

## 2. 需求真實性 — 數據 / Demand reality (A2 = 2)
| 指標 Metric | 數值 Value | 日期 Date | 來源 Source (grade) |
|---|---|---|---|
| BVP Emerging Cloud fwd rev multiple — peak | ~28× | Q4 2021 | [2] (C) |
| BVP Emerging Cloud fwd rev multiple — now | ~8× (avg co. <10×) | Q1 2026 | [2] (C) |
| Public SaaS fwd-rev multiple range, then→now | 15–30× → 5–8× | 2021→2026 | [2] (C) |
| Chegg market cap destroyed | ~$14B (−99%, to $1.07) | Nov'22→Apr'26 | [4] (B) |
| Chegg revenue Q1'25 | $121M, −30% YoY | Q1 2025 | [5] (A, 8-K) |
| Chegg subscribers Q2'25 | 2.6M, −40% YoY | Q2 2025 | [5] (A, 8-K) |
| Stack Overflow posts vs 2020 peak | −90%+ (−64% YoY) | Apr 2025 | [3] (B, Similarweb/SO data) |
| Cursor (Anysphere) ARR | ~$2B (fastest 0→2B ever) | Feb 2026 | [1] (B) |
| GitHub Copilot paid subs | ~4.7M (+~75% YoY); 20M users | Jan 2026 | [7] (B) |
| Enterprise GenAI spend | $37B (3.2× YoY, from $11.5B'24) | FY2025 | [9] (C, Menlo) |
| — of which application layer | $19B; coding alone $4.0B | FY2025 | [9] (C, Menlo) |
| AI products >$1B ARR / >$100M ARR | ≥10 / 50+ | FY2025 | [9] (C, Menlo) |
**Read:** multiples compressed ~71% from the 2021 mania — but that was a *rates + over-valuation* reset, not proof of AI substitution (the compression started in 2022, before AI revenue mattered). The *AI-substitution* evidence is the per-name canaries (Chegg, Stack Overflow), not the index multiple. Separate the two or you mis-attribute the bear case.

## 3. 資金與權威背書 / Capital & authority (A3 = 2)
Capital is voting massively for the *application/agent* layer: Anysphere reportedly raising ~$2B at ~$50B valuation (Apr 2026) and forecasting >$6B ARR by end-2026 [1]. AI-app revenue run-rates are real and large: Anthropic ~$30B run-rate reported April 2026 (80× growth claim) and OpenAI ~$24B+ April 2026 [10][10b] — though OpenAI disputes Anthropic's *gross* accounting (~$8B overstatement from cloud-partner pass-through), so treat the headline gap as **B-grade with a methodology asterisk** [10]. Enterprise demand authority: Menlo's $37B (3.2× YoY) is the fastest category expansion in enterprise-software history, >6% of the entire software market within 3 years of ChatGPT [9]. Gartner authority on the *counter* side: total software spend ~$1.44T 2026, GenAI model spend +80.8% [8].

## 4. 贏家 vs 輸家 / Winners vs losers (A4 = 1)
**STRUCTURALLY EXPOSED (losers — low moat / single-feature / seat-as-the-product):**
- **CHGG** — terminal case, −99%; the textbook AI-substitution death [4][5].
- **Education/Q&A/content-mill tier** — Course Hero, language-app basics, generic-content SaaS whose output is now a free LLM completion [3][6].
- **Watch-list (not collapsing, but moat-on-notice):** seat-based tools where an agent does the seat's job; any "thin wrapper" SaaS.

**ADAPTERS / CAPTURERS (winners — data + distribution + workflow lock-in):**
- **MSFT** — Copilot bundled across M365 install base; GitHub Copilot ~42% of paid AI-coding share, generating more than all of GitHub did at the 2018 $7.5B acquisition [7]. Distribution moat intact.
- **CRM** — Agentforce ~$800M ARR Q4 FY26 (+169% YoY), 29,000 deals; Agentforce+Data 360 ~$2.9B recurring (+200%) [from Agentforce coverage]. Re-pricing from seat → outcome (see §6) [Salesforce pricing].
- **NOW** — FY2026 subscription guide +19.5–20%, Now Assist driving it; system-of-record + workflow lock-in [ServiceNow coverage].
- **PLTR** — US commercial +133% YoY to $595M, US gov +84% to $687M Q1'26; AIP is the canonical "capture" story [Palantir coverage].
- **INTU** — Q2 FY26 rev $4.7B (+17%), GenOS + proprietary tax/financial data moat [Intuit coverage].
- **ADBE** — AI-first ARR tripled YoY; >1/3 of book AI-influenced exiting FY25 — but Firefly monetization slower than hoped and the stock is a 2026 laggard, so ADBE is the **contested** case: data+distribution moat, uncertain *whether* it captures vs gets disrupted on the creative tail [Adobe coverage]. **The decisive cross-check is CHGG (loser) vs DUOL (winner): same "AI threatens my category" setup, opposite outcome** — Duolingo grew revenue +39% to ~$1.04B FY25 and DAU to 56.5M by capturing AI (Duolingo Max) rather than being eaten [11]. Moat + adaptation = capture; thin product = death.
*Verdict A4=1 not 2:* winners are identifiable but the *price* already embeds much of the capture for the platform tier (per [[../wiki/07_ai_bubble_audit]] §6, Mag-7-adjacent multiples 25–35× fwd), so the equity edge is thinner than the narrative.

## 5. 大模型 vs 小模型 / Model angle
The disruption is *delivered* through frontier models (OpenAI/Anthropic ~$24–30B run-rates [10]), but the enterprise *capture* increasingly routes through whoever owns the **data + workflow**, not the model. Menlo: application layer ($19B) now exceeds raw model/infra spend dynamics in growth, with coding the single largest app category ($4.0B) [9]. Implication: model leadership is necessary upstream fuel, but value accrues to the distribution/data layer — small/fine-tuned models embedded in a workflow can be "good enough," eroding pure-model pricing power over time. (Develop in [[model-leadership-and-data]].)

## 6. 顛覆 / 取代向量 / Disruption vector (A5 = 1)
The cleanest structural signal is the **pricing-model migration: per-seat → usage/outcome.** Salesforce shipped *three* Agentforce pricing models in ~18 months: $2/conversation at launch → Flex Credits at $0.10/action (May 2025) → per-user "digital labor" at $125/user/mo [Salesforce pricing]. This matters because **seat-based SaaS revenue is mechanically threatened when one agent replaces many seats** — outcome pricing is the incumbents *defending* revenue by re-basing it on work-done rather than headcount. The substitution vector for losers: free LLM output → search-funnel collapse → subscriber churn → restructuring (Chegg cut 22% then 45% of staff in 2025 [4]). A5=1 (not 2) because the vector is *proven for a narrow set* and *defended-against* by the majority of incumbents — it is not yet a broad SaaS extinction event.

## 7. 同溫層風險 + 空方論點 / Echo-chamber flags + (counter) bull case
**Echo-chamber gap (the precise mis-pricing):** Twitter/"SaaS is dead" extrapolates the *Chegg tail* onto the *whole sector*. The actual P&L lines say the opposite at the aggregate: software spend +15.1% to $1.44T 2026 — Gartner *revised UP* from 11.5% in 2025, "the slowdown never came" [8]. Net-new software dollars ~$190B in a single year, the biggest ever [8]. **The bear narrative is loud; the P&L is growing.**
**Counter-thesis weighed fairly (the bull/incumbent case):** (1) Incumbents *bundle* AI into an existing install base at near-zero CAC (MSFT Copilot, CRM Agentforce, NOW Now Assist) — distribution moat holds [7]. (2) Aggregate software revenue is *growing, not shrinking* — quantified above [8]. (3) Switching costs / system-of-record lock-in are unbroken for the platform tier.
**But the bull case has a crack (intent vs realized):** MIT NANDA found ~95% of enterprise GenAI pilots delivered **no measurable P&L impact**; only ~5% achieved rapid revenue acceleration [12]. Menlo's $37B is largely *intent/spend*, not realized ROI [9]. So the capture thesis is real but *front-loaded on spend, lagging on returns* — a 2026–27 air-pocket risk if pilots don't convert. **Flag both: losers' damage is realized P&L; winners' upside is still partly intent.**

## 8. 跨主題綜效 / Cross-synergies
- [[model-leadership-and-data]] — value migrates from model → data/workflow; who owns the moat determines capture vs disruption.
- [[ai-edge-devices]] — on-device small models extend the substitution vector to local/offline workflows (translation, assistants).
- [[../wiki/07_ai_bubble_audit]] §6 — platform-tier multiples 25–35× fwd already embed capture; this is the bubble-audit linkage (intent-vs-realized = the same air-pocket the bubble page flags).

## Sources
1. Cursor/Anysphere $2B ARR & funding — https://thenextweb.com/news/cursor-anysphere-2-billion-funding-50-billion-valuation-ai-coding — retrieved 2026-05-31 — grade B
2. SaaS multiple compression / BVP Cloud Index — https://natelind.com/blog/saas-valuation-multiples-2026-bessemer-cloud-index — retrieved 2026-05-31 — grade C
3. Stack Overflow traffic/posts collapse (Similarweb + SO data) — https://www.similarweb.com/blog/insights/ai-news/stack-overflow-chatgpt/ — retrieved 2026-05-31 — grade B
4. Chegg ~$14B / −99% / management attribution — https://europeanbusinessmagazine.com/business/chegg-stock-collapse-chatgpt-ai-disruption-2026/ — retrieved 2026-05-31 — grade B
5. Chegg Q1/Q2 2025 10-Q / 8-K revenue & subs — https://www.sec.gov/Archives/edgar/data/0001364954/000136495425000096/[redacted-acct]0.htm — retrieved 2026-05-31 — grade A
6. Chegg / ChatGPT 50% single-day drop context — https://www.onlineeducation.com/features/chatgpt-crashes-cheggs-stock — retrieved 2026-05-31 — grade C
7. GitHub Copilot 20M users / 4.7M paid / 42% share — https://techcrunch.com/2025/07/30/github-copilot-crosses-20-million-all-time-users/ — retrieved 2026-05-31 — grade B
8. Gartner 2026 software spend $1.44T +15.1% / GenAI +80.8% — https://www.saastr.com/gartner-software-spend-now-1-44-trillion-in-2026-revised-back-up-to-15-1-the-slowdown-never-came-are-you-grabbing-it/ — retrieved 2026-05-31 — grade B
9. Menlo Ventures 2025 State of GenAI in Enterprise ($37B, $19B app, $4B coding) — https://menlovc.com/perspective/2025-the-state-of-generative-ai-in-the-enterprise/ — retrieved 2026-05-31 — grade C
10. Anthropic vs OpenAI run-rates + accounting dispute — https://venturebeat.com/technology/anthropic-says-it-hit-a-30-billion-revenue-run-rate-after-crazy-80x-growth — retrieved 2026-05-31 — grade B
10b. OpenAI/Anthropic revenue crossover (Epoch AI) — https://epoch.ai/data-insights/anthropic-openai-revenue — retrieved 2026-05-31 — grade B
11. Duolingo FY25 +39% rev / 56.5M DAU / Duolingo Max (counter-example) — https://www.sec.gov/Archives/edgar/data/0001562088/000162828026029790/q1fy26duolingo3-31x26share.htm — retrieved 2026-05-31 — grade A
12. MIT NANDA — 95% of GenAI pilots no ROI (intent-vs-realized) — https://fortune.com/2025/08/18/mit-report-95-percent-generative-ai-pilots-at-companies-failing-cfo/ — retrieved 2026-05-31 — grade B
13. Salesforce Agentforce 3 pricing models (seat→outcome) — https://www.saastr.com/salesforce-now-has-3-pricing-models-for-agentforce-and-maybe-right-now-thats-the-way-to-do-it/ — retrieved 2026-05-31 — grade C
14. Salesforce Agentforce $800M ARR / 29k deals — https://completeaitraining.com/news/salesforce-agentforce-hits-800-million-arr-as-enterprise/ — retrieved 2026-05-31 — grade B
15. Palantir Q1'26 US commercial +133% / gov +84% — https://intellectia.ai/news/etf/investment-comparison-palantir-vs-servicenow — retrieved 2026-05-31 — grade C
16. ServiceNow FY26 +19.5–20% guide / Now Assist; Adobe AI-first ARR tripled — https://247wallst.com/investing/2026/04/27/which-software-stock-has-been-the-worst-performer-in-2026-adobe-salesforce-or-servicenow/ — retrieved 2026-05-31 — grade C
17. Intuit Q2 FY26 $4.7B +17% — https://tickeron.com/compare/INTU-vs-NOW/ — retrieved 2026-05-31 — grade D

