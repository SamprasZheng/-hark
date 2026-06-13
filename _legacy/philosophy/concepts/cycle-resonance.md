---
type: concept
tags: [cycle, time-resonance, 6-month, andy-principle, regime]
title: Cycle Resonance (半年調整 / 兩個月上漲)
author_role: human
---

# Cycle Resonance — 6-Month Correction / 2-Month Advance

[[../../sharks]] empirical regularity: equity drawdowns of meaningful depth tend to last around 6 months (~22 weeks), followed by initial advance windows of roughly 2 months. The system uses this as the primary trigger for 6m bucket entries.

## The pattern as defined

The cycle-resonance detector fires when ALL of the following hold simultaneously for the underlying (SPX or NDX or SOX):

- Weekly closing series shows a drawdown of `≥ 22 weeks` from the prior 52-week high
- Drawdown depth ∈ `[10%, 30%]` (rules out both shallow noise and crash-mode resets)
- Current week's low `≥ 5-week trailing low` for 10 consecutive sessions (no new lows being made)
- VIX has retreated from its drawdown peak by ≥ 30% (volatility easing)
- Liquidity score `L` (from [[liquidity-fishbowl]]) has bottomed and started rising (`L_5d > L_30d_low + 0.10`)

When the condition fires, the 6m bucket opens new entries for **14 calendar days**. After 14 days, the window closes regardless of whether positions were taken. Re-entry of the window requires a fresh `as_of` qualifying event — no "extending" the window because you didn't act fast enough.

## Why this works (the proposed mechanism)

The pattern is empirical but the proposed mechanism connects three forces:

1. **Capital reallocation cycle**: institutional rebalancing windows tend to follow quarter-end / half-year boundaries. A drawdown that breaches Q1 and Q2 has likely seen two rebalance flushes.
2. **Sentiment exhaustion**: the [[concepts/separation-mind]] crowd has had ~6 months to capitulate. The marginal seller is gone.
3. **Multiple compression to absorption**: the drawdown brings forward valuations into ranges where buy-and-hold capital flows return on a 6-month forward basis.

The 2-month advance window is the initial mean-reversion impulse before the next macro-driven phase. The bucket is sized to harvest this impulse, NOT to ride a multi-year recovery (that would be the 12m bucket, which requires separate confirmation).

## Historical instances to study

The Compiler should file these to `wiki/03_alpha_library.md` with full `as_of_timestamp` discipline:

- 2020 March → May (Covid; abbreviated to ~3 months by Fed intervention)
- 2022 January → June, then second wave June → October (two consecutive cycles in a single bear)
- 2023 January (post-Q4 2022 drawdown; cleanest example)
- 2024 August (Yen carry unwind, brief; window opened and closed in 3 weeks)
- (the system will track and file each future instance)

Each historical case logs:
- the qualifying event date (window open)
- the 2-month advance return
- the post-advance behaviour (was it a true cycle bottom or a bear-market rally?)

## Trade construction inside the window

When the window is open:

- **6m bucket allocation**: up to 30% of portfolio may be deployed into 6m positions
- **Tier preference**: tier1 Mag 7 first (highest beta to cycle reversal), tier2 supply chain second, tier3 generally avoided in cycle-resonance (mid-caps are noisier in the initial reversal phase)
- **Watershed**: per [[objective-watershed]], the cycle-resonance entry uses **trailing 12-month low + 1 ATR(20)** as the watershed. Crossing below this level invalidates the cycle-resonance thesis.
- **Strategy assignment**: cycle-resonance entries are tagged `strategy: cycle_resonance` in `outputs/picks-*.json` to distinguish from Strategy A/B/C in the backtest.

## What this is NOT

- **NOT a mechanical "buy after 22 weeks down" rule**. The volatility-easing and liquidity-bottoming conditions are mandatory co-confirmations. Drawdowns that continue making new lows without volatility easing do not qualify.
- **NOT a market-bottom predictor**. The system has no ability to predict THE bottom. It predicts WINDOWS where the next 2-month forward return has historically been positively skewed.
- **NOT relevant to short-side decisions**. Cycle-resonance is a long-side framework. Short setups follow [[../03-long-short-taxonomy]] separately.

## Falsification

The cycle-resonance hypothesis is **falsified** if any of the following accumulate:

- 3 consecutive cycle-resonance windows produce 2-month forward returns below SPY's average — the regime that produced the historical pattern has shifted
- A drawdown lasting > 30 weeks with cycle-resonance never firing — the 22-week threshold is no longer calibrated to current regime

Falsification triggers a re-evaluation of the trigger conditions, not a quiet drift in the rules. See [[../00-thesis]] for the broader falsification clauses.

## Implementation handoff

Phase 2: implement detection in `src/sharks/regime/cycle.py`. The function returns `CycleResonanceState` with fields:
- `window_open: bool`
- `window_open_date: Optional[date]`
- `window_close_date: Optional[date]`
- `current_drawdown_weeks: int`
- `current_drawdown_pct: float`
- `qualifying_conditions: Dict[str, bool]` (each of the 5 conditions)

Phase 4 backtest verifies historical instances above match the detector's output with strict point-in-time discipline.
