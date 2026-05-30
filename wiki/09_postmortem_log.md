---
type: synthesis
tags: [postmortem, mistakes, lessons-learned, calibration]
title: Postmortem Log — "Don't repeat the same mistake"
as_of_timestamp: 2026-05-29T06:00:00-04:00
author_role: human + compiler
status: live
schema_version: 1
---

# Postmortem Log

Per Buffett ([[../raw/methodology/buffett-philosophy]]): the cost of repeating a mistake is much higher than the cost of avoiding it. This page is the **append-only ledger** of mistakes — both system-level (FOM/Compiler errors) and human-level (rule violations).

Every entry includes:
1. **What happened** — observation
2. **Why** — root cause analysis
3. **Rule update** — what the system or human will do differently
4. **Verification** — how to check the fix worked

---

## ENTRY-001 — ORCL Compiler-Principal disagreement (2026-05-29)

### What happened
FOM v1 ranked ORCL as top-3 pick (rank #3) with contrarian score 81 and bubble_guard +30. The Principal flagged ORCL as "已經開始下跌" — early-stage bubble breakdown — and the Compiler deferred to human judgment, substituting MSFT in slot #3.

### Why
- FOM v1's `bubble_guard` looked at parabolic patterns and at-the-top conditions
- It did NOT capture **drawdown acceleration** — the moment when a stock transitions from healthy correction to active breakdown
- ORCL's correction was in the "sweet spot" 15-30% from 52w high which triggered max contrarian score (85), but the recent **monthly decline was accelerating**, suggesting structural break rather than buyable correction

### Rule update
**v2 fix already applied** in `src/sharks/scoring/fom.py`:
- Added `drawdown_acceleration()` function
- Compares 1m return rate vs 3m monthly-average rate
- If r1 << r3/3 AND r1 < -5%, generates negative score that subtracts from bubble_guard
- Half-weighted to avoid dominance

### Verification
- Re-run FOM v2 on 2026-05-29 — check that ORCL's bubble_guard score lowers vs v1's +30
- Long-term: track ORCL's actual performance over next 90 days; if it continues to break down, the principal was right and v2 catches it. If it recovers, v1 was right and the v2 fix may be too aggressive.

---

## ENTRY-002 — MU sparse detection (back-test discovery 2026-05-29)

### What happened
FOM 2016-2026 backtest caught MU only TWICE in top 3 (2019-05 and 2026-04). MU had **multiple multi-bagger cycles** during that period (notably 2024-2025 +214%). The system missed most entry windows.

### Why
- MU is highly cyclical (memory commodity cycle)
- Quality dimension penalises MU's high realised volatility
- Cyclic dimension didn't fire because MU's biggest move (2025) was NOT during SOXX-May (which is the biggest cyclic boost)
- Momentum dim wasn't enough to overcome the quality drag

### Rule update
**Proposed for FOM v3**:
- Add **sector-relative momentum**: when XME (memory sub-sector) outperforms SOXX by >15% over 3 months, boost memory-sub-sector candidates' cyclic score
- Apply to: MU, WDC, STX, SIMO
- Track via `wiki/02_mag7_bottleneck.md` HBM allocation tightness section

### Verification
- Re-run backtest with proposed v3 changes; verify MU detection rate increases from 2 to ~5-8 events

---

## ENTRY-003 — TSLA 2020 ramp missed (back-test discovery 2026-05-29)

### What happened
FOM didn't catch TSLA until 2020-11 @ $189. By then TSLA had already 10×'d from 2019 lows. The system missed the bottom of TSLA's biggest single-year run.

### Why
- 2019 TSLA had VERY high realised vol (>1.0 annualised) — quality dim near 0
- IP defensibility 70 wasn't enough to overcome quality drag
- Bubble_guard correctly flagged TSLA at the 2019 low as "not at a bottom" since 2019 was just the end of a multi-year sideways
- TSLA's 2020 ramp was momentum-narrative driven, not value-driven

### Rule update
**Acknowledge**: FOM is structurally a **quality-momentum-value** system. Pure narrative-momentum names like 2020 TSLA are not in the addressable signal universe.
- This is an **acceptable miss** — system reflects its philosophy
- Do not retrofit the system to catch this kind of move (would break the calibration for everything else)

### Verification
- Periodically (annually) review: are we missing structurally-similar narrative moves? If yes, the system is consistent. If we start catching them via some other mechanism (say cyclic boost gets too big), recalibrate.

---

## ENTRY-004 — 2022 drawdown not avoided (back-test discovery)

### What happened
Backtest portfolio max drawdown was -52.9% vs SPY's -27.0% during 2022. System was heavily concentrated in tech (NVDA, AVGO, AMD) and didn't rotate to defensives.

### Why
- No cycle-resonance trigger fired (SPX max DD was ~-25%, NDX was -33%)
- Cycle_bias didn't exist in v1 (added in v2)
- No 2022-specific exit rule
- TD-9 + volume-validation guard wasn't implemented as automatic action

### Rule update
**Already in v2**:
- `cycle_bias` provides -0.4 to -0.6 score during Y2 (midterm + tightening)
- Reduces sizing on candidates whose `cyclic` < 35
- Future v3: add explicit `exit_rule_TD9` that triggers 50% trim when TD-9 + volume contraction confirmed

### Verification
- Re-run 2022 backtest with v2 weights — verify drawdown improves from -52.9% to closer to SPY -27%
- Live test: monitor 2026-Q4 if cycle-resonance fires, watch how positions react

---

## ENTRY-005 — Survivorship bias in backtest universe (back-test discovery)

### What happened
`DEFAULT_UNIVERSE` in `fom.py` includes tickers that didn't exist or trade in 2016 (e.g. OKLO which IPO'd 2024 via SPAC). When backtesting from 2016, these names should be excluded until their actual first-trade date.

The backtest noticed OKLO appearing in 2016-08 top 3, which is clearly bogus.

### Why
- yfinance returns NaN for pre-IPO data, but my scorers default to 50 (neutral) when data is missing — not 0
- The contrarian score defaults to neutral + buffett_value scores defaults — gave OKLO a non-zero FOM

### Rule update
**Proposed v3 fix**: hard-exclude tickers from `DEFAULT_UNIVERSE` at any `as_of` where `closes[ticker].dropna().index[0] > as_of`. Implement in `score_ticker` as the first check.

### Verification
- Re-run backtest with fix — verify OKLO doesn't appear before 2024
- Spot-check other recent IPOs: ARM (2023-09), RKLB (2021-08), ALAB (2024-03)

---

## ENTRY-006 — FOM concentration risk: 55% in NVDA (back-test discovery)

### What happened
After 10 years of DCA, the backtest portfolio is **55% NVDA**. This violates [[../philosophy/08-risk-and-position]] single-ticker 8% cap. Any catastrophic NVDA-specific event (accounting fraud discovery, sudden technological obsolescence by competitor) would devastate the portfolio.

### Why
- Backtest used pure-DCA-into-top-3 without rebalancing
- NVDA appeared top-3 for 55 of 123 months (45%) — system kept buying
- Long horizon (10 years) magnified the concentration drift

### Rule update
**Live system v2+ already has** [[../philosophy/08-risk-and-position]] 8% tier-1 cap. **For live mode**: when adding to a position at the cap, the system instead allocates the slot to next-highest-FOM candidate. This rebalances away from concentration.

**For backtest realism**: future runs should apply the same rule. Expected outcome: ~30% lower final return (NVDA contribution capped) but ~40% lower MDD.

### Verification
- Run two backtests in parallel:
  - With cap: target $3.5M final + -30% MDD
  - Without cap (current): $5.3M final + -53% MDD
- Compare Sharpe — capped version should be higher

---

## ENTRY-007 — "Story stocks": ORCL/OKLO/SMCI Principal-flagged warning

### What happened (early ledger of an ONGOING situation)
Principal warned 2026-05-29 that ORCL, OKLO, SMCI are early-bubble-breakdown candidates. FOM v1 partially confirmed (OKLO + SMCI in low FOM ranks; ORCL false-positive at #3).

### Why this is a learning case
The principal's qualitative reading detected a pattern (accounting/narrative-fade in story stocks) that the FOM system did not yet have explicit detection for. This is the **canonical case** for `human override > system` and motivates the FOM v2 `drawdown_acceleration` fix.

### Rule update (in progress)
- Monitor ORCL/OKLO/SMCI 90-day forward returns
- If principal's call validates (all three are in deeper drawdown by 2026-08), confirm v2 fix as correct
- If FOM v1 contrarian was right (these recover from "錯殺"), update IP defensibility scores down for these specific names

### Verification — pending live data through 2026-Q3

---

## ENTRY-008 — "Sell in May" partially wrong (cycle research 2026-05-29)

### What happened
Principal's intuition "五窮六絕七翻身" partially right but **May is actually positive** on average. The system's monthly seasonality data shows May +1.45% mean, 79% positive.

### Why
- Chinese-market wisdom (Asia tax season cash crunch) doesn't fully transfer to SPX
- US-specific Sell-in-May refers to the 6-month period not the May month
- The actual SPX weak month is **September** (-0.90% mean, 46% positive)

### Rule update
- Compiler updated [[../philosophy/concepts/seasonal-monthly]] with actual data
- Principal's intuition validated for: 七翻身 (Jul), 十一月 (Nov), 秋絕 (Sep), 11-12 消費季
- Calibrated against: 五窮 (May actually strong), 年初爆跌 (Jan actually mid)

### Verification
- Phase 2 ingest of monthly data continues; track if patterns hold forward (2026-2030)

---

## ENTRY-009 — TAN solar "December rally" claim WRONG (cycle research)

### What happened
Principal said panel/solar up in December. Data shows TAN's best month is **January** (+3.85%, 72% positive). December is mediocre (+0.76%, 56% positive).

### Why
- Probable explanation: end-of-year solar installations push (cash for clunkers, year-end policy push)
- But the market doesn't reflect this until January (when next-year guidance is set)

### Rule update
- Add TAN/Solar candidate stage to **December → January** rather than November-December
- Recorded in [[../philosophy/concepts/sector-seasonality]]

### Verification
- Watch TAN performance December 2026 vs January 2027

---

## ENTRY-010 — HERO Gaming "summer rally" WRONG (cycle research)

### What happened
Principal said gaming up in summer (Jul-Aug). Data shows HERO best month is **November** (+4.6%, 71% positive). July and August are mediocre.

### Why
- Gaming consumer doesn't strongly index on summer break (kids gaming during summer is offset by adults out + lower work hours)
- Year-end holiday is the biggest gaming spend window (Christmas + Black Friday)
- Esports tournament finals concentrate in late autumn

### Rule update
- Stage HERO entries for **October → November** rather than June → August
- [[../philosophy/concepts/sector-seasonality]] updated

### Verification
- HERO performance Oct-Nov 2026

---

## Discipline reminder

Per Buffett: **「我會諒解你讓公司賠錢,但聲譽受損我不諒解」**. The analogue for the system: **mistakes happen; failure to log them and learn is the unforgivable sin**.

This page is the canonical record. Every Risk Officer review of a position decision MUST cross-reference this log to ensure no past lesson is being re-violated.

## See also

- [[../raw/methodology/buffett-philosophy]] — value-investing reference
- [[../philosophy/concepts/separation-mind]] — 分別心 (don't compare against past hindsight)
- [[../philosophy/concepts/farmer-mindset]] — don't repeat what worked last year mindlessly
- [[../philosophy/08-risk-and-position]] — sizing rules with override clauses
- [[05_recommendations/2026-05-29-fom-backtest-validation]] — backtest discoveries that created ENTRY 002-006
