---
type: synthesis
tags: [strategies, A-B-C, breakout, momentum, whale-tracking, philosophy]
title: Three Core Strategies — A / B / C
author_role: human
---

# 10 · Three Core Strategies

Derived from the Gemini blueprint's three-strategy proposal. Each strategy is an end-to-end specification: trigger, sizing, exit, backtest KPI, and where it lives in the architecture.

## Strategy A — Value-Price Consolidation Breakout

### Trigger
- Underlying has traded within `±5%` of its 60MA for ≥ 4 weeks (consolidation phase)
- 5-day average volume during consolidation ≤ 0.8 × prior-90-day average (volume-dry phase)
- Today's bar closes above the consolidation upper band on volume `> 1.5 ×` prior-20-day average
- Fundamental dimension confirms (Sales QoQ growth `> 10%`, gross margin not deteriorating) — no fundamental-contradiction veto from [[02-signal-taxonomy]]

### Sizing & horizon
- Default horizon: **3 months** (3m bucket from [[01-time-horizon]])
- Default size: full tier cap (tier1 6%, tier2 4%, tier3 3%)
- Quadrant: 多頭真漲 from [[03-long-short-taxonomy]]

### Exit
- `price` invalidation: low of the consolidation band minus 1 ATR(20)
- `time_stop_days`: 135 (4.5 months)
- `catalyst` invalidation: any negative fundamental update during the holding window

### Backtest KPI targets
- Sharpe > 0.8 net of execution friction
- Max DD < 25% in any 12-month rolling window
- Win rate > 45%
- Median holding period in range [60, 120] days (mid-band of horizon)
- Worst single-trade loss < `-10%`

### Where it lives
- Implementation hook: `src/sharks/strategies/strategy_a_consolidation.py` (Phase 3)
- Backtest config: `backtest/strategies/strategy_a.yaml` (Phase 4)
- Live signals tagged in `outputs/picks-*.json` with `strategy: A`

---

## Strategy B — Momentum Breakout

### Trigger
- Distance from 52w high ≤ 8% (uptrend regime)
- Bollinger 20-period upper band touched on volume `> 1.3 ×` prior-20-day average
- Sector resonance: target sector in top-3 5-day net inflow rank (from [[04-sector-and-finviz]] Filter 3)
- Per [[02-signal-taxonomy]]: this is the **strategy explicitly allowed to override** the fundamental-vs-technical contradiction at 30% bucket cap

### Sizing & horizon
- Default horizon: **1 month** (1m tactical bucket)
- Default size: 50% of tier cap (because momentum failure is fast and costly)
- Quadrant: 多頭真漲 if fundamentals confirm; otherwise tagged `momentum_only` and held to 30% bucket cap per [[02-signal-taxonomy]] Rule

### Exit
- **Hard exit on [[concepts/td-9-sequential]] sell signal with volume contraction**
- **Hard exit on close below 20MA**
- `time_stop_days`: 45 (6 weeks — momentum decays fast)
- `catalyst` invalidation: sector-rotation flip (target sector falls out of top 5 inflow rank for 5 consecutive sessions)

### Backtest KPI targets
- Sharpe > 1.0 (compensates higher trade frequency)
- Max DD < 18% (tighter discipline)
- Win rate > 50%
- Median holding period in [10, 35] days
- Worst single-trade loss < `-7%`

### Where it lives
- Implementation hook: `src/sharks/strategies/strategy_b_momentum.py`
- This is the strategy most exposed to [[concepts/td-9-sequential]] mis-firing (Gemini review point #4) — the volume-divergence guard is mandatory before signal is fired

---

## Strategy C — Whale / Order-Flow Tracking

### Trigger
- Post-session order flow shows persistent block trading (block size > 10,000 shares, occurring in `> 3` non-consecutive 15-minute windows of the regular session)
- Dark pool printed volume > 30% of total session volume (sourced from Phase 6 data feeds; not available on the free Polygon tier)
- For crypto: on-chain large transfer cluster detected via `ccxt` orderbook depth analysis — no API key needed
- News dimension confirms an emerging catalyst (otherwise this is just noise)

### Sizing & horizon
- Default horizon: **1 month** (1m tactical bucket)
- Default size: **30% of tier cap** — Strategy C is the experimental tier, conviction comes from confirmation, not from pattern alone
- Quadrant: candidate is staged for 多頭真漲 promotion; held in Strategy C bucket until fundamental dimension confirms

### Exit
- `price` invalidation: 1.5 ATR(20) below entry
- `time_stop_days`: 21 (3 weeks — whale signals decay even faster than momentum)
- `catalyst` invalidation: order-flow signature reverses (block selling instead of buying)

### Backtest KPI targets
- Sharpe > 1.2 (highest target because lowest size cap; needs higher unit-risk return to justify)
- Max DD < 15%
- Win rate > 55%
- Median holding period in [5, 15] days
- Worst single-trade loss < `-5%`

### Where it lives
- Implementation hook: `src/sharks/strategies/strategy_c_whale.py`
- The crypto path is enabled in Phase 4 (via `ccxt_client`); the US equity dark-pool path waits for Phase 6 paid data subscriptions
- This strategy is the **primary user** of the high-freq mode from [[07-mode-switch]] — most weekend crypto and most WFH-window US equity sessions

---

## Strategy interaction & total allocation

- A single ticker may carry **at most one** active strategy tag at a time. Switching strategy tags requires an exit and a fresh entry.
- Strategy A + B + C may combine on the portfolio level, but:
  - Combined Strategy B + C ≤ 25% of portfolio (high-velocity capital)
  - Strategy A ≤ 60% of portfolio
  - Remainder is cash buffer for [[08-risk-and-position]] halt recovery
- Cross-strategy correlation > 0.7 between two open positions triggers the [[08-risk-and-position]] downweight regardless of strategy tag

## Adding a fourth strategy

If you find yourself wanting to add Strategy D ("event arbitrage", "pairs", etc.), the gate is:
1. Specification page on this same template, sitting in `philosophy/` (not `wiki/`)
2. Backtest KPI threshold met on train+val+test per [[04-sector-and-finviz]] Rule 1
3. Risk Officer review of overlap with existing A/B/C
4. Human commits the file. Agents may draft, but cannot promote.
