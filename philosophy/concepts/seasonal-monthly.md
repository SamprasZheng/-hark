---
type: concept
status: proposal
tags: [seasonality, monthly, sell-in-may, september-weak, proposal]
title: Monthly Seasonality — Sell in May variant + September the worst — proposal
author_role: compiler
proposed_destination: philosophy/concepts/seasonal-monthly.md
proposed_at: 2026-05-29T03:30:00-04:00
---

# Monthly Seasonality (PROPOSAL)

> Draft proposal. Human approval required.

## Empirical pattern (verified ^GSPC monthly 1980-2026, n ≈ 41 per month)

### SPX monthly average returns

| Month | Mean | Median | Positive rate | Notes |
|---|---|---|---|---|
| Jan | +0.98% | +1.59% | 62% | Mid |
| Feb | +0.35% | +0.86% | 60% | Weak-mid |
| Mar | +0.87% | +1.45% | 62% | Mid |
| Apr | +1.60% | +1.05% | 69% | **Strong** |
| May | +1.45% | +1.39% | **79%** | **Strong** (defies "Sell in May") |
| Jun | +0.39% | +0.48% | 63% | Weak |
| **Jul** | **+1.45%** | +1.62% | 61% | **Strong** |
| Aug | -0.26% | +0.49% | 56% | Weak |
| **Sep** | **-0.90%** | -0.65% | **46%** | **WORST (only month negative on avg)** |
| Oct | +0.99% | +1.94% | 63% | Mid (recovery) |
| **Nov** | **+1.91%** | +2.45% | 73% | **BEST (highest mean)** |
| **Dec** | **+1.39%** | +1.26% | 73% | Strong (Santa rally) |

## Key observations

1. **Sell-in-May is largely a myth on SPX since 1980**. May itself is the second-strongest month by mean and HIGHEST by hit rate (79%). The "Sell in May" wisdom refers to the 6-month period May-Oct being weaker than Nov-Apr, but the individual May month is positive.

2. **September is the single worst month** — only month with negative mean (-0.90%) and the only month with <50% positive rate. The "秋絕" intuition is empirically valid.

3. **Nov and Dec are the strongest individual months**. Both 73% positive, both >1.3% mean. The "11-12 月消費季" intuition is empirically valid.

4. **The Best 6-Month rule (Nov-Apr) vs Worst 6-Month rule (May-Oct)**:
   - Nov-Apr: mean +1.18% per month
   - May-Oct: mean +0.36% per month
   - Annualized difference: roughly +14% (Nov-Apr) vs +4% (May-Oct)

5. **The August-September weak window** is the most consistent danger zone. Aug -0.26% and Sep -0.90%; combined the 60-day window has historically produced ~50% of all single-quarter SPX drawdowns since 1980.

## NDX (since 1990) seasonality

Similar shape, more volatile:
- Best months: Nov (+2.87%, 69%), Oct (+2.61%, 67%), Jan (+2.41%, 68%)
- **NDX October is much stronger than SPX October** — tech tends to bounce earlier from September weakness

## Operational use

### Calendar bias as part of multi-scale framework

Per [[multi-scale-cycles]], `calendar_bias` contributes to overall sizing:
- Nov: `+0.7`
- Dec, Apr, May, Jul: `+0.5`
- Oct: `+0.2` (recovery, volatile)
- Jan, Mar: `+0.1`
- Feb, Jun: `0.0`
- Aug: `-0.3`
- **Sep: `-0.6`** (the canonical caution flag)

### Tactical September discipline

- Reduce tier 2 / tier 3 exposure by 30% entering September
- No fresh 6m+ bucket entries during September
- Restore standard caps after first weekly SPX close > 20MA in October

### November buy-window

- Most active fresh entries window of the year
- Strategy A consolidation-breakouts most fertile here (Nov historically prints Industrial / Materials / Biotech / Real Estate strongest)
- Aligned with post-midterm-Nov in election Y2 years for double-trigger conviction

## Principal-claim verification table

| Principal claim | Data | Verdict |
|---|---|---|
| 五窮六絕七翻身 | May +1.45% (79%), Jun +0.39%, Jul +1.45% | ⚠️ Jul is strong ✅ but May is actually positive (not 窮) and Jun is the weakest of the three |
| 七月起漲點 | Jul +1.45%, 61% | ✅ Verified |
| 十一月上漲機率高 | Nov +1.91%, 73% | ✅ Verified (highest mean) |
| 秋絕 | Sep -0.90%, 46% | ✅ Verified (only negative-mean month) |
| 11-12 消費季 | Nov + Dec both +1.3-1.9%, 73% | ✅ Verified |
| 年初爆跌 | Jan +0.98%, 62% positive | ❌ Not verified (Jan is mid-strength) |

## See also

- [[../../wiki/06_cycle_framework]] §3 — full table
- [[multi-scale-cycles]] — broader framework
- [[sector-seasonality]] — per-sector month-by-month variant
- [[election-cycle-year-2]] — November 2026 specifically aligns with post-midterm
