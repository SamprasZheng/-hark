---
type: synthesis
tags: [backtest, results, walk-forward, kpi, stub]
title: Backtest Log
status: stub
as_of_timestamp: 2026-05-28T22:00:00-04:00
---

# Backtest Log (stub)

Phase 1 placeholder. The Phase 4 backtest engine writes here on every run.

## Expected entry format

Each backtest run logged as:

```
## [YYYY-MM-DD HH:MM TZ] strategy=<A|B|C|cycle_resonance|composite> | window=<train|val|test|live-shadow>

**Inputs**
- universe_snapshot: watchlist/history/universe-YYYY-MM-DD.yaml
- date_range: YYYY-MM-DD .. YYYY-MM-DD
- universe_size: N tickers
- config: backtest/strategies/strategy_X.yaml@<sha>

**Outputs**
- total_return_pct
- sharpe_ratio
- max_drawdown_pct
- win_rate_pct
- median_holding_period_days
- worst_single_trade_pct
- num_trades

**Compliance checks**
- [ ] point-in-time assertion passed (per [[../philosophy/09-point-in-time]])
- [ ] walk-forward partition respected (per [[../philosophy/04-sector-and-finviz]] Rule 1)
- [ ] max-DD halt mechanic simulated
- [ ] correlation downweight applied per [[../philosophy/08-risk-and-position]]

**KPI verdict**
- [ ] meets target Sharpe (Strategy A > 0.8, B > 1.0, C > 1.2)
- [ ] meets target Max DD (Strategy A < 25%, B < 18%, C < 15%)
- [ ] meets target Win Rate (Strategy A > 45%, B > 50%, C > 55%)

**Findings / next actions**
...
```

## Discipline reminders

- A backtest that did NOT pass the point-in-time assertion is **invalid** and must NOT be entered as a passing run. Re-run with fixes; only log the corrected run.
- Threshold tuning on the test set is **forbidden**. If a strategy fails on test, archive it; do not retune.
- Live-shadow results (paper trading the strategy on out-of-sample live data) are logged with `window=live-shadow` for transparency.

## See also

- [[../philosophy/04-sector-and-finviz]] — walk-forward + train/val/test discipline
- [[../philosophy/09-point-in-time]] — lookahead assertion contract
- [[../philosophy/10-strategies]] — KPI targets per strategy
- [[../docs/ROADMAP]] — Phase 4 plan
