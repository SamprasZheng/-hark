---
type: synthesis
domain: method
tags: [concentration, breadth, sector-rotation, liquidity, fund-flows, spillover, dispersion, semiconductors]
as_of_timestamp: 2026-05-31T06:00:00+08:00
author_role: researcher
confidence: 0.70
verdict: 集中度極端 + 外溢已啟動但未證實 (concentration extreme; spillover begun, not yet confirmed)
sources_grade_summary: "A: 0 B: 14 C: 4 D: 0 E: 0 (A-grade primaries Cboe/SEC/Morningstar/SSGA 403'd on fetch; URLs recorded but verification downgraded to B per _sourcing-protocol §1/§4)"
---
# 流動性集中度與資金外溢 / Liquidity Concentration & Spillover (semis → ?)

Tests the principal's hypothesis — *「大量流動性集中在半導體,是否外溢給其他產業,從哪些產業開始傳導?」* — with measured concentration/flow data, and defines the metrics to track it. Complements (does not duplicate) `regime/breadth_indicator.py` (寬度過熱), `regime/sector_flow.py` (RS rotation), `regime/classifier.py`, [[../philosophy/concepts/hotspot-sector-rotation]] (seasonality > momentum, measured), `regime/funding_chain.py` (funding-stress), and [[../wiki/07_ai_bubble_audit]].

## 0. 一句話判決 / Verdict
**集中度處於 ~50 年極端,且資金外溢「已開始啟動但尚未被確認」, confidence 0.70.** Two facts are simultaneously true and must not be conflated: (a) **structural concentration** is at a multi-decade extreme — top-10 ≈ 40% of S&P 500 cap, semis ≈ 18% (more than double the dot-com peak), Mag-7 ≈ 35% [1][3][4]; (b) **flow + breadth at the margin (Jan–Apr 2026) are rotating OUT of mega-cap growth into cyclicals/value/small-cap** — large-growth ETFs saw their first outflow since Jan-2023 (−$5B Feb) while large-value took +$17B, and RSP (equal-weight) beat SPY by double digits YTD [9][8][6]. The honest read: **concentration is the *stock* (extreme), broadening is the *flow* (early, fragile)**. The spillover is *transmitting in the textbook order* — semis → power/electricals/industrials — but the move is ~4 months old, partly rate-cut/OBBBA-driven not purely AI-capex, and the rotation-clock framework that "predicts" the next sector is, by our own backtest, **mostly folklore at the momentum horizon** ([[../philosophy/concepts/hotspot-sector-rotation]]: momentum IC_IR 0.52 ≈ coin-flip; only *seasonality* carries edge). Treat broadening as a watchlist tilt, not a confirmed regime change, until the falsifiable triggers in §4 fire.

## 1. 集中度 / 分化 指標 + 現值 / Concentration & dispersion (the *stock*)

| 指標 Metric | 現值 Value | 歷史分位 / context | 日期 Date | 來源 (grade) |
|---|---|---|---|---|
| Top-10 % of S&P 500 cap | **~40.7%** (peak Dec-25); ~40% | **highest since ≥1972**; vs ~27% dot-com-2000 peak | 2025-12-31 | [1][4] B / cross-confirmed |
| Top-10 (Goldman framing) | ~33% of index cap | "most concentrated in ≥50yr of readily-available data"; >27% (redacted) | 2026-Q1 | [4] B |
| Mag-7 % of S&P 500 cap | **~35%** (range 35–40% intraday) | vs 12.5% in 2016 → near-record | 2026-05 | [1] B |
| Semiconductors % of S&P 500 | **~18%** | **>2× the dot-com-peak semis weight**; ~2% ten years ago | 2026-05-18 | [3] C / single-source-pending |
| Semis (narrower SOX-member basis) | ~11% (all-time high) | contradiction vs the 18% figure — both shown | 2026-05 | [3] C / contradicted-with-18% |
| NVDA share of 2025 S&P 500 *return* | **15.5%** of the 17.9% total | one stock ≈ 1/6 of the index's whole year | FY2025 | [2] B |
| NVDA+AVGO share of 2025 return | **22.7 ppt of 17.9% total** | two semis drove the index | FY2025 | [2] B |
| SOX 2025 return vs S&P 500 | +34.5% vs +14.3% (to 12-17-25) | semis >2× the index | 2025-12-17 | [2] B |
| % S&P 500 > 200-day MA | **56.4%** | off the 70% Aug-25 high and 65%+ Dec-25/Jan-26 | 2026-05-22 | [5] B |
| RSP (equal-wt) vs SPY YTD | RSP ~+1% to +11% vs SPY −4% | sharp reversal of 2023-24 mega-cap dominance | to 2026-03 | [6] B / cross-confirmed |
| Cboe 1-mo implied correlation (COR1M) | **8.7–9.93** | **lowest in ≥23 years**; <10 = contrarian extreme | 2026-05-28 | [7] B |
| Expected avg single-stock correlation 2026 | ~23% | remarkably low → max dispersion regime | 2026 | [7] B |

**Is concentration at historical extremes? Yes, unambiguously** — by top-10 weight (≥50yr high), by semis weight (>2× dot-com), and by *low* implied correlation (≥23yr low, the mirror image of crowding into a handful of index drivers). The dispersion/correlation reading is the subtle one: record-low correlation means index vol is being held down by a few mega-caps while everything else moves on its own — i.e. the concentration shows up as a **dispersion** extreme, which historically (per Cboe's own note) is a *contrarian* warning that dispersion trades can violently unwind [7].

## 2. 資金流 / Fund flows — "everyone in the same trade?" (the *flow*)
2026 flow data says the crowd is **starting to leave** the same-trade, not pile in:
- **Sector ETFs best-ever start:** +$19B Jan + ~$10–12B Feb 2026 [8][9]. Within Feb: **Technology +$5.8B but Industrials +$3.8–5.0B** — industrials punching far above its index weight [8][9] B.
- **Growth→Value rotation, the headline:** large-**growth** ETFs bled **−$5B (first outflow since Jan-2023)**; large-**value** took **+$17B** [9] B / cross-confirmed (Morningstar + etfdb both report record value inflows [9][10]).
- **Return spread driving it:** cyclical sectors averaged **~+20% YTD through Feb** vs **technology ~−6%** [8] B — a ~26-ppt swing that *pulls* flows mechanically.
- **Defensives mixed:** Utilities are the AI-power proxy (capex story) yet saw episodic big *outflows* even as the theme stayed hot [12] — i.e. flows there are theme-driven, not defensive-driven.

Read: the "everyone in semis" trade is real on the *stock* of positioning, but the **2026 marginal dollar is rotating to cyclicals/value/small-cap**. This is the early-spillover signature — though much of it is plausibly the OBBBA (100% bonus depreciation, Jan-1-26) + three 2025 rate cuts (Fed funds 3.50–3.75%) repricing rate-sensitive small-caps [13], *not* purely AI-capex overflow. Separate the two causes before crediting "semis spilled over."

## 3. 傳導順序 / Transmission order — semis → which next?
Two distinct mechanisms; only one has a defensible *order*.

**(a) AI-capex chain (causal, datable — the strong claim):** hyperscaler capex (>$500B 2026, ~$690B cited [14], ~$3T still ahead [—]) flows along a **physical supply chain** with a real lead-lag:
> **semis (GPU/HBM) → power & electricals (transformers, switchgear, grid) → cooling/datacenter-infra (Vertiv-type) → industrials/EPC → utilities → financing/credit.**

Supported by capital-commitment data, not folklore: US utility capex $1.3T 2026-30, electricity demand +25–32% by 2030 [15]; BlackRock survey — **54% name energy/power providers the top AI exposure for 2026** [16]; industrials (GE Vernova, Vertiv) already the breadth leaders. Same chokepoint logic as [[ai-datacenter-power]] / [[optical-interconnect-cpo]]: money moves to the *next* bottleneck, which in 2025-26 demonstrably moved semis→power→industrials.

**(b) Business-cycle / sector-rotation clock (the WEAK claim — largely folklore):** the classic "early financials/discretionary → mid industrials/materials → late energy → defensives" clock is **not predictive at the momentum horizon** in our own work. [[../philosophy/concepts/hotspot-sector-rotation]] (2016-2026, 121 quarterly PIT predictions): momentum-persistence **IC_IR 0.52, precision@3 0.237, beats random 54.5%** — *noise*; only **seasonality** carries edge (IC_IR 2.78, 65.3%). So "semis hot → buy the next sector in the clock" ≈ a coin-flip. Order (a) is credible because it is a *physical* dependency; the generic clock (b) is not — do not dress (b) in (a)'s authority.

**Ranked transmission (capex-chain, high→low conviction):** 1) power/electrical & grid 2) datacenter cooling/infra 3) broad industrials/EPC 4) utilities (regulated, lagged) 5) financing/credit & real assets 6) small-cap/value (rate-driven, *parallel* not downstream). Memory/storage already moved with semis ([[memory-supercycle]]).

## 4. broadening 訊號 + 證偽觸發 / Broadening signals + falsifiable triggers
**Broadening (redacted):** ~65–69% of S&P 500 members beat the index in Feb (≈2nd-best in 50yr) [13]; Russell 2000 +~8–12% YTD vs S&P ~+1.5% (to late-Mar), strongest small-cap relative run in ~3 decades [13]; RSP>SPY [6]; growth→value flow flip [9]. **Continued narrowness:** top-10 still ~40%, semis ~18%, COR1M ≥23yr low [1][3][7] — the *structure* hasn't de-concentrated, only the *margin* moved, and breadth already faded from 65%+ (Jan) to 56% >200dma (May) [5]: **not yet durable**.

**Falsifiable triggers that would CONFIRM spillover is structural (datable, watch weekly):**
1. **% S&P 500 >200dma holds >60% for ≥3 consecutive months** (not a one-print spike) — sustained participation, not a whipsaw.
2. **RSP/SPY ratio makes a higher high AND rising 50dma for ≥2 quarters** — equal-weight leadership persists past one quarter (clears the momentum-is-noise objection).
3. **COR1M mean-reverts UP off <10 *without* an index drawdown** — dispersion normalises benignly (the healthy unwind) rather than via a crash.
4. **Net sector flows: cyclicals/industrials/financials out-gather Tech for ≥2 consecutive quarters** (`sector_flow` `rotating_in` excludes XLK/SOXX persistently).
5. **AI-capex chain confirms in *fundamentals*, not just price:** power/electrical & industrial order-books (GE Vernova, Vertiv, Eaton-type) print accelerating bookings — the [[00_framework]] A2 demand-reality gate, separating real capex overflow from a rate-cut rotation.
**Triggers that would FALSIFY (spillover stalls / it was a head-fake):** breadth rolls back <50% >200dma; RSP/SPY reverts below its 200dma within a quarter; large-growth flows turn positive and reclaim leadership; COR1M unwind comes *with* a drawdown (concentration de-risks the ugly way). Any one of these = "narrowness re-asserts."

## 5. 整合到 $hark / Integration hooks
The desk has the parts; this page specs the *concentration-regime gate* tying them together:
- **`regime/breadth_indicator.py`** — add three first-class metrics so the verdict isn't only NDX/RUT-ratio-driven: **top-10 (& Mag-7) % of S&P 500 cap** + percentile; **semiconductor weight** of the index (the principal's exact variable); **RSP/SPY ratio** + 200dma slope (`breadth_trend`). Add a `CONCENTRATION_EXTREME` branch (top-10 pctile >90 *and* breadth <60%) distinct from `OVERHEATED`.
- **`regime/sector_flow.py`** — already gives `rotating_in/out`, `leaders/laggards`. Add a **`broadening_score`** (% of the 15 ETFs with RS>0 vs SPY — leadership breadth as a number) and a **`semis_spillover` flag** = SOXX is a `leader` AND ≥1 of {XLI, XLU, GRID-type} is `rotating_in` (encodes the §3 capex-chain order, not the folklore clock).
- **Concentration-regime gate (new, cross-module):** combine `CONCENTRATION_EXTREME` × `broadening_score` × `funding_chain` stress into one regime tag for the daily rubric — *when concentration is extreme AND breadth narrow, down-weight any single-name semis add* ([[../philosophy/concepts/evidence-gated-rebalance]] applied to crowding). Route any "next sector" call through the **seasonality** component of [[../philosophy/concepts/hotspot-sector-rotation]] (momentum is noise), with §3(a) capex-chain as a *fundamental* overlay via [[00_framework]] A2 — not a momentum signal.
- **Weekly:** §4 triggers go into [[_weekly-watch]]; percentile/flow figures re-pulled per [[_sourcing-protocol]] (they decay fast — breadth moved 65%→56% in ~4 months).

## 6. 同溫層風險 / Echo-chamber risk
The trap cuts **both ways**. **Bull-side:** "AI-capex broadens the rally forever" — but the 2026 broadening is ~4 months old, breadth already faded, and much of the small-cap leg is a **rate-cut/OBBBA** story that reverses if the Fed pauses; crediting "semis spillover" for a macro-rate move is the seductive error. **Bear/contrarian-side:** "record concentration = imminent crash" — yet Goldman's century study finds extreme-concentration episodes (redacted) sometimes mark *bottoms*, and low correlation can normalise benignly [4][7]; de-concentration can be *up* (laggards catch up), not only *down*. **The deepest trap is the rotation-clock itself** — it feels like analysis, but our backtest says momentum-rotation ≈ coin-flip. Discipline: separate the **measured** facts (§1–§2, dated) from the **folklore** (§3b), demand the §4 triggers before calling spillover confirmed, and cross-check [[../wiki/07_ai_bubble_audit]] before sizing either direction.

## See also
- [[ai-datacenter-power]] — the power/electrical leg of the capex chain (transmission step 2)
- [[optical-interconnect-cpo]] · [[memory-supercycle]] — semis-internal chokepoints that moved first
- [[../philosophy/concepts/hotspot-sector-rotation]] — momentum=noise, seasonality=edge (the folklore guardrail)
- [[../philosophy/concepts/evidence-gated-rebalance]] — the 十足的證據 gate the concentration regime feeds
- [[00_framework]] — A2 demand-reality gate for confirming capex-chain fundamentals
- [[_weekly-watch]] · [[_sourcing-protocol]] — weekly re-verification of fast-decaying breadth/flow figures
- [[../wiki/07_ai_bubble_audit]] — late-cycle bubble guard for either-direction concentration bets

## Sources
1. The Motley Fool / MacroMicro — Magnificent Seven % of S&P 500 (~35%, up from 12.5% in 2016; top-10 ~40% at 2025-12-31) — https://www.fool.com/research/magnificent-seven-sp-500/ — retrieved 2026-05-31 — grade B — cross-confirmed (MacroMicro series 46223)
2. Statista / Yahoo Finance — Contributors to S&P 500 2025 return (NVDA 15.5%, AVGO 7.2ppt of 17.9% total; SOX +34.5% vs S&P +14.3% to 12-17-25) — https://www.statista.com/chart/32015/contributors-to-the-sp500-return/ — retrieved 2026-05-31 — grade B
3. 24/7 Wall St. — Semiconductor exposure in S&P 500 hits 18%, >2× tech-bubble peak (NVDA >25% of index semi weight); note ~11% on narrower basis — https://247wallst.com/investing/2026/05/18/semiconductor-exposure-in-sp-500-hits-18-thats-more-than-double-the-tech-bubble-peak/ — retrieved 2026-05-31 — grade C — single-source-pending (403'd on fetch; figure from index summary; 18% vs 11% contradiction flagged)
4. Goldman Sachs — Is the S&P too concentrated? (top-10 ~33%, most concentrated in ≥50yr; >27% dot-com 2000; 7 historical extreme episodes incl. 1932 bottom) — https://www.goldmansachs.com/insights/articles/is-the-sp-too-concentrated — retrieved 2026-05-31 — grade B — cross-confirmed (see [17][18])
5. MacroMicro / StreetStats — S&P 500 % above 200-day MA (56.4% at 2026-05-22; 65%+ Dec-25/Jan-26; 70% high Aug-25) — https://en.macromicro.me/series/22718/sp-500-200ma-breadth — retrieved 2026-05-31 — grade B
6. Seeking Alpha / 24-7 Wall St / PortfoliosLab — RSP vs SPY (RSP +1–11% YTD vs SPY −4% to Mar-26; 10yr 11.80 vs 15.44%/yr) — https://seekingalpha.com/article/4849078-2026-market-outlook-the-equal-weight-s-and-p-500-makes-a-comeback — retrieved 2026-05-31 — grade B — cross-confirmed
7. Cboe / Crypto Briefing — Implied correlation record low (COR1M 8.7–9.93, lowest in ≥23yr; 2026 avg single-stock corr ~23%; <10 contrarian) — https://cryptobriefing.com/nasdaq-implied-correlation-record-low/ — retrieved 2026-05-31 — grade B — primary index = Cboe https://www.cboe.com/us/indices/implied/ (403'd)
8. State Street Global Advisors / ETF Express — Sector ETF flows Jan+Feb 2026 (best-ever start +$19B/+$10-12B; Tech +$5.8B, Industrials +$3.8B; cyclicals +~20% YTD vs Tech −6%) — https://etfexpress.com/2026/03/03/us-listed-etfs-heading-for-record-year-in-2026-state-street/ — retrieved 2026-05-31 — grade B (500'd on fetch; figures from SSGA flow summary)
9. Morningstar — Investors ditch growth for value ETFs Feb-2026 (large-growth −$5B first outflow since Jan-2023; large-value +$17B; sector-equity +$12B; industrials +$5B) — https://www.morningstar.com/funds/investors-ditch-growth-value-etfs-february — retrieved 2026-05-31 — grade B — cross-confirmed (403'd on fetch; figures from result summary + [10])
10. ETF Database — Value ETFs see record inflows as investors abandon growth (Mar-2026) — https://etfdb.com/news/2026/03/06/value-etfs-record-inflows/ — retrieved 2026-05-31 — grade C
11. Capital Group — Fresh breadth? Market concentration in 3 charts (NVDA 20% of YTD return to 9-30-25; >200dma 16%→64% intra-month; Mag-7 fwd P/E 31× vs 20× rest) — https://www.capitalgroup.com/pcs/insights/articles/fresh-breadth-market-concentration-3-charts.html — retrieved 2026-05-31 — grade B
12. Nasdaq — State Street Utilities Select Sector SPDR (XLU) big outflow (redacted) — https://www.nasdaq.com/articles/state-street-utilities-select-sector-spdr-etf-experiences-big-outflow — retrieved 2026-05-31 — grade C
13. FinancialContent / Royce — Great Rotation 2026: Russell 2000 +~8–12% YTD vs S&P ~+1.5% (Fed 3.50–3.75%, OBBBA 100% bonus depreciation Jan-1-26, 40% small-caps floating-rate) — https://markets.financialcontent.com/stocks/article/marketminute-2026-3-24-the-great-rotation-russell-2000-outshines-mega-caps-as-domestic-small-caps-take-the-reins-in-2026 — retrieved 2026-05-31 — grade C
14. Futurum Group — AI Capex 2026: ~$690B infrastructure sprint (hyperscaler capex >$500B 2026) — https://futurumgroup.com/insights/ai-capex-2026-the-690b-infrastructure-sprint/ — retrieved 2026-05-31 — grade C
15. S&P Global Market Intelligence — US utility capex ~$1.3T 2026-30; electricity demand +25–32% by 2030 — https://www.spglobal.com/market-intelligence/en/news-insights/research/2026/04/surging-energy-demand-puts-us-utility-capex-forecast-near-1-3t-in-2026-30 — retrieved 2026-05-31 — grade B
16. BlackRock — Investing in AI infrastructure / 2026 survey (54% name energy/power providers top AI exposure; broadening beyond semis to power, cooling, industrials, financing) — https://www.blackrock.com/us/financial-professionals/insights/investing-in-ai-infrastructure — retrieved 2026-05-31 — grade B
17. RBC Wealth Management — The "Great Narrowing": S&P 500 concentration (top-10 ~40.7% in 2025, highest since ≥1972) — https://www.rbcwealthmanagement.com/en-us/insights/the-great-narrowing-sp-500-concentration — retrieved 2026-05-31 — grade B — cross-confirms [4]
18. Lord Abbett — Time for a Conversation About Stock Market Concentration (top-10 40% of S&P 500 at 2025-12-31; Russell-1000-Growth top-10 >60%; Mag-7 earnings contribution Q4'23 225% → Q3'25 31%) — https://www.lordabbett.com/en-us/financial-advisor/insights/markets-and-economy/2026/equities-time-for-a-conversation-about-stock-market-concentration.html — retrieved 2026-05-31 — grade B — primary-fetched

