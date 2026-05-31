---
type: synthesis
domain: tech-trend
tags: [stablecoins, tokenization, rwa, genius-act, agentic-payments, circle, usdc, tether, echo-chamber]
as_of_timestamp: 2026-05-31T04:30:00+08:00
author_role: researcher
phase: C
confidence: 0.74
verdict: 結構
verdict_by_horizon: {T0: 結構, T1: 結構→質變(條件), T2: 過熱, T3: 太早}
rubric: {A1: 2, A2: 2, A3: 2, A4: 1, A5: 1}
sources_grade_summary: "A: 8 B: 8 C: 2 D: 0 E: 0"
schema_version: 1
---

# 穩定幣 · 代幣化 · 代理支付 / Stablecoins, Tokenization & Agentic Payments

## 0. 一句話判決 + desk view / Verdict
- **穩定幣結算 → 結構 (real infrastructure, NOW, but the equities run ahead of P&L).** Total stablecoin supply crossed **~$321B** (May 2026, ATH; USDT ~$190B / USDC ~$77B = ~83% of float), the **GENIUS Act** became federal law **2025-07-18**, and a *primary-fetched* Circle income statement proves a real cash machine ($694M Q1-FY2026 revenue). This is the most data-backed of the Phase-C theses. [1][3][5]
- **廣義 RWA 代幣化 → 結構→質變(條件) at T1, 過熱 at T2.** On-chain RWA ex-stablecoins ~$32B and tokenized Treasuries ~$11B is real institutional money (BlackRock BUIDL ~$2.5B) but is **<2% of the $321B stablecoin float** and a rounding error vs the ~$28T UST market. [4]
- **"代理支付/tokenize everything" → 太早 (echo chamber).** x402 does ~**$28K/day**, mostly testing/gamed flows, momentum −92% off the Dec-2025 peak. The rail exists; the demand does not yet. [10]
- **Desk view (caveated, not advice):** the *settlement layer* is a genuine 質變 — dollars now move on-chain at near-zero marginal cost, and via GENIUS the US chose to **export the dollar through private issuers + Treasury demand** rather than a CBDC. But the cleanest pure-play (**CRCL**) is a **levered bet on the front of the curve**: ~95% reserve-interest revenue, so a Fed cutting cycle compresses the top line unless USDC float outruns the rate drop. Own the *toll-road economics* (issuers + Coinbase's revenue share + V/MA rails), not the "everything tokenizes" story; the echo chamber confuses **bot/wash volume** with adoption.

## 1. 技術 / 制度底蘊 / Rails, GENIUS Act, custody (A1 = 2)
Stablecoins are real infrastructure for one engineering reason: **final settlement of a dollar liability in seconds, 24/7, for cents, across borders, without a correspondent-bank chain** — a durable architectural step-change over ACH/SWIFT/card rails, not marketing. Hence A1=2.

**The GENIUS Act, signed 2025-07-18** [2], is the institutional moat the bears underweight: **100% cash/short-dated-Treasury reserves + monthly public disclosure**; permitted issuers = insured-depository subs, federally- or state-qualified issuers; **holders rank ahead of all creditors in bankruptcy**; mandatory seize/freeze/burn + Bank Secrecy Act/AML; and compliant coins are **carved out of "security"/"commodity"** (no SEC/CFTC). [1][2] The hidden hinge: **issuers are PROHIBITED from paying interest/yield to holders** [11] — this protects bank deposits *and* is precisely why the reserve yield accrues to **Circle/Coinbase, not the user**; the entire CRCL model is a creature of this clause. Banks (ABA + 40 associations) are lobbying to close the "affiliate loophole" they say still drains deposits. [11] Rails are concentrating, not fragmenting: **Base carries ~62% of stablecoin transactions** [8], with BlackRock/BNY under BUIDL — the investable signal in §4.

## 2. 需求數據 / Supply, volume, issuer revenue (A2 = 2)
Real P&L exists — but headline *volume* is the most over-stated number in crypto.

| 指標 | 數值 | 期間 | 來源(grade · verification) |
|---|---|---|---|
| Total stablecoin supply | **~$321B** (ATH) | May 2026 | [3] B · cross-confirmed |
| USDT supply | **~$189.6B** (58% share) | Apr 2026 | [3] B · cross-confirmed |
| USDC supply | **$77.0B** (+28% YoY) | Q1-FY2026 | [5] A · primary-fetched |
| Circle total rev & reserve income | **$694M** (+20% YoY) | Q1-FY2026 | [5] A · primary-fetched |
| — of which reserve income | **$653M** (~94% of rev) | Q1-FY2026 | [5] A · primary-fetched |
| Circle reserve **return rate** | **3.5%**, **−66bps YoY** (lower SOFR) | Q1-FY2026 | [5][7] A · primary-fetched |
| Circle net income (cont. ops) | **$55M**, **−15% YoY** (post-IPO SBC) | Q1-FY2026 | [5] A · primary-fetched |
| Tether 2025 net profit | **>$10B** (−23% YoY) | FY2025 | [6] B · cross-confirmed |
| Tether UST exposure | **$122B** direct / **$141B** incl. repo (firm's claim) | FY2025 | [6] B · contradicted-flag |
| Raw on-chain stablecoin volume | **~$33T** (2025) | FY2025 | [9] B · cross-confirmed |
| **Real-economy payments only** | **~$350–550B** of $62T gross transfers | 2025 | [9] B · single-source-pending |

**The signal vs the noise:** Circle's $653M *reserve* income is real, audited, recurring cash — A2=2. But the "$33T, rivals Visa" framing is largely **bot/MEV/liquidity-provisioning churn**: ~**71%** of Q3-2025 volume was bot-driven, organic non-bot only ~20%. [9] Net income actually *fell* 15% even as supply rose 28% — proof the model is **rate-driven, not volume-driven**.

## 3. 資金與權威背書 / Capital & authority (A3 = 2)
Authority weight is now **maximal**: a signed federal statute [2], six agencies (OCC, FDIC, NCUA, FinCEN, Treasury, OFAC) issuing proposed rules Dec-2025→May-2026 [12], and the world's largest asset manager on-chain. BlackRock **BUIDL ~$2.5B** anchors a ~$11B tokenized-Treasury / ~$32B total-RWA market [4]. Capital is heavy and institutional, not KOL — A3=2. Tether is **among the largest holders of US Treasuries globally** ($122B+), making stablecoins a genuine instrument of **dollar export + sovereign-debt demand** — the structural reason Washington legislated rather than banned. [6]

## 4. 受益 / 受損 / 抄底 / Winners, losers, bottom-fish (A4 = 1)
A4=1 (diffuse — value split across issuer, exchange and rail, not one clean chokepoint).
- **WINNERS — issuers & toll-roads:** **CRCL** (USDC issuer; reserve-yield toll) and **COIN** (captures ~44% of USDC economics via the Circle revenue-share; **stablecoin rev $305M Q1-FY2026**, ~$19B USDC on-platform = >25% of float; **Base ~62%**). [8] **V / MA** are *quiet winners*, not victims — both bolting stablecoin settlement onto existing rails (Visa Stablecoin Advisory; Mastercard multi-stablecoin across USDC/PYUSD/USDG/FIUSD). **PYPL** (PYUSD/FIUSD; ~$8.2B cross-border stablecoin volume Q1-FY2026). [13]
- **LOSERS:** **cross-border remittance incumbents** (the 3–7% corridor fee is the fattest target) and **deposit-funded banks** exposed to the yield-loophole drain [11]; tokenized-Treasury growth slowly squeezes **prime money-market** spread.
- **抄底 (caveated):** the rate-sensitive **CRCL** is where a *Fed-cut overreaction* could over-discount — but only if USDC float keeps compounding 25%+ to offset the rate drop. **V/MA** are the lower-variance way to own the theme without the front-of-curve beta.

## 5. 多時程 / Multi-horizon
- **T0 (0–1y): 結構.** GENIUS live; supply $321B; issuer P&L proven; rails concentrating on Base/V/MA. Real now, but CRCL multiple prices a rate path that may not hold.
- **T1 (1–3y): 結構→質變(條件).** Conditional on (a) final GENIUS rules (≤Jul-2026) + (b) a major **bank/retailer** stablecoin going live at scale. If both land, settlement crosses into mainstream B2B.
- **T2 (3–5y): 過熱.** "Tokenize equities/credit/real-estate" — real pilots, but liquidity, legal-finality and 24/7 settlement infra are unproven at size; narrative will outrun rails.
- **T3 (5–10y): 太早.** Fully agentic machine-to-machine payment economy + universal tokenization is a credible end-state but undated; today's x402 demand falsifies imminence. [10]

## 6. 爆發條件 + 里程碑 / Milestone ladder
| # | Falsifiable checkpoint | Verify | Status (2026-05-31) | Next |
|---|---|---|---|---|
| M1 | Total stablecoin supply **>$400B** | DefiLlama / RWA.xyz | ~$321B [3] | watch monthly |
| M2 | **Final** GENIUS rules issued (OCC/Treasury) | Federal Register | proposed only; due ≤2026-07-18 [12] | Jul-2026 |
| M3 | A **top-10 bank OR top-5 retailer** launches a live stablecoin at scale | issuer PR / 8-K | pilots only (V/MA/PYPL enabling) [13] | watch H2-2026 |
| M4 | **CRCL** reserve-return-rate decline outpaces USDC float growth (rev declines YoY) | CRCL 10-Q | rate −66bps but rev +20% (float wins, for now) [5] | next print |
| M5 | Tokenized-Treasury TVL **>$25B** | RWA.xyz | ~$11B [4] | quarterly |
| M6 | x402 / agentic real (non-test) volume **>$50M/mo** | Coinbase/x402 dashboards | ~$28K/day, momentum −92% off peak [10] | quarterly |

## 7. 時代影響與交互 / Era-impact & interactions
This is the **monetary plumbing of the AI-agent era**: GENIUS effectively chose *private dollar-stablecoins + Treasury demand* over a Fed CBDC, exporting the dollar onto open networks. It interacts with [[ai-eats-software]] (fintech/payment software margin) and [[youth-culture-shifts]] (a generation defaulting to app-native, borderless money). The agentic-payments layer ([[ai-coding-agents]], [[model-leadership-and-data]]) is where stablecoins *could* become the settlement substrate for machine commerce — but that is T3, not now.

## 8. 同溫層 + 自我打臉 / Echo-chamber & self-refutation
**Echo-chamber gap (large):** the crypto-Twitter framing — "stablecoins already rival Visa ($33T!) and everything is tokenizing" — collides with the data: **only ~$350–550B of $62T gross transfers was real-economy payment** [9], tokenized RWA is <2% of the float [4], and agentic payments are ~$28K/day [10]. Headline *volume* ≠ adoption; **supply, real-payment volume, and issuer revenue are three different numbers** and the narrative quotes the most flattering one.

**打臉 own bull case (bear THEN bull):** Bull = "regulated dollar rails, $321B and compounding, Treasury-backed, GENIUS moat." 打臉: **CRCL is a single-factor bet on the front of the curve dressed as a fintech** — ~95% reserve-interest revenue, net income *down 15%* YoY despite +28% float; a sustained Fed cut + float stall is the real bear, and Congress closing the affiliate yield-loophole would kneecap the distribution that drives that float. **Bull tail back:** if float compounds 25%+ and bank/retailer adoption lands (M3), reserve income still grows into a falling-rate world, and V/MA/COIN capture the theme with less rate beta. Cross-link [[quantum-vs-bitcoin]] (a future CRQC threatens the chains' signature scheme — PQC-migration risk to the rails) and [[youth-culture-shifts]] (demand-side culture shift).

## Sources
1. The GENIUS Act of 2025: Stablecoin Legislation Adopted in the US — https://www.lw.com/en/insights/the-genius-act-of-2025-stablecoin-legislation-adopted-in-the-us — retrieved 2026-05-31 — grade B
2. White House Fact Sheet: President Signs GENIUS Act into Law (2025-07-18) — https://www.whitehouse.gov/fact-sheets/2025/07/fact-sheet-president-donald-j-trump-signs-genius-act-into-law/ — retrieved 2026-05-31 — grade A
3. Stablecoin market cap tops ~$321B (USDT/USDC shares) — https://bitcoinfoundation.org/news/stablecoin-news/stablecoin-market-cap-tops-321b/ — retrieved 2026-05-31 — grade B
4. Tokenized Treasuries / BlackRock BUIDL ~$2.5B; RWA ex-stablecoins ~$32B — https://www.cryptotimes.io/2026/05/23/blackrock-tokenized-treasury-filings-2026-the-rwa-boom-goes-institutional/ — retrieved 2026-05-31 — grade B
5. Circle Reports First Quarter 2026 Results (primary press release) — https://www.circle.com/pressroom/circle-reports-first-quarter-2026-results — retrieved 2026-05-31 — grade A
6. Tether 2025: >$10B profit (−23% YoY), $122B UST direct / $141B incl repo, $186.5B supply — https://finance.yahoo.com/news/tether-profit-falls-23-2025-092248065.html — retrieved 2026-05-31 — grade B
7. Circle (CRCL) Q1 2026 Earnings Transcript (reserve return rate 3.5%, −66bps on lower SOFR) — https://www.fool.com/earnings/call-transcripts/2026/05/11/circle-crcl-q1-2026-earnings-transcript/ — retrieved 2026-05-31 — grade B
8. Coinbase Q1 2026: stablecoin rev $305M, ~$19B USDC on-platform, ~44% of USDC economics, Base ~62% — https://www.tikr.com/blog/coinbase-q1-2026-earnings-revenue-down-21-but-derivatives-and-stablecoins-are-gaining — retrieved 2026-05-31 — grade B
9. Stablecoin volume: raw ~$33T 2025, ~71% bot-driven, real-economy payments only ~$350–550B — https://coinmarketcap.com/academy/article/stablecoin-transfers-hit-dollar156t-in-q3-as-bot-activity-dominates — retrieved 2026-05-31 — grade B
10. Coinbase-backed x402: demand not there yet (~$28K/day, momentum −92% off Dec-2025 peak) — https://www.coindesk.com/markets/2026/03/11/coinbase-backed-ai-payments-protocol-wants-to-fix-micropayment-but-demand-is-just-not-there-yet — retrieved 2026-05-31 — grade B
11. GENIUS Act bans interest/yield to holders; bank-deposit drain & affiliate-loophole debate — https://bpi.com/closing-the-payment-of-interest-loophole-for-stablecoins/ — retrieved 2026-05-31 — grade A
12. OCC Proposed Rulemaking to implement GENIUS Act (rules due ≤2026-07-18; effective ≤2027-01-18) — https://occ.treas.gov/news-issuances/bulletins/2026/bulletin-2026-3.html — retrieved 2026-05-31 — grade A
13. Mastercard/PayPal/Visa stablecoin integration (multi-stablecoin rails; PYUSD ~$8.2B cross-border Q1-FY2026) — https://www.pymnts.com/cryptocurrency/2025/stablecoins-became-useful-in-2025-can-they-become-ubiquitous-in-2026/ — retrieved 2026-05-31 — grade B
14. GENIUS Act — Congress.gov S.1582 (119th) primary bill text — https://www.congress.gov/bill/119th-congress/senate-bill/1582 — retrieved 2026-05-31 — grade A
15. RWA.xyz — Tokenized U.S. Treasuries live dashboard — https://app.rwa.xyz/treasuries — retrieved 2026-05-31 — grade A
16. x402 + Google AP2 agentic-payments protocol (USDC dominant settlement token) — https://www.coinbase.com/developer-platform/discover/launches/google_x402 — retrieved 2026-05-31 — grade B
17. Circle, Coinbase, and the Prohibition on Interest Under the GENIUS Act (CLS Blue Sky) — https://clsbluesky.law.columbia.edu/2025/12/11/circle-coinbase-and-the-prohibition-on-interest-under-the-genius-act/ — retrieved 2026-05-31 — grade C
18. Chainalysis: stablecoin utility & adjusted volume (~$28T 2025) — https://www.chainalysis.com/blog/stablecoin-utility-future-of-payments/ — retrieved 2026-05-31 — grade C
