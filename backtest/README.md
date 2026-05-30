# backtest/

Phase 4 home for the backtest engine configuration and per-strategy specs.

## Phase 1 status

Empty placeholder + the `strategies/` subdirectory README. The Phase 4 implementation lives in `src/sharks/backtest/`.

## Phase 4 deliverables (placeholder summary)

Per [[../docs/ROADMAP]] Phase 4:

1. **Framework choice**: Backtrader or vectorbt (lean vectorbt for speed; finalise on first sprint)
2. **Walk-forward partition**: every backtest enforces train (60%) + val (20%) + test (20%) chronological split
3. **Point-in-time assertion**: every signal evaluation verifies `max(used_source.as_of) <= trade.signal_time`; failure aborts the run
4. **Per-strategy backtest configs**: in `backtest/strategies/`
5. **Composite portfolio backtest**: combines strategies with the [[../philosophy/08-risk-and-position]] caps; explicitly simulates max-DD halt mechanic
6. **KPI reporting**: each run emits a `wiki/04_backtest_log.md` entry following the template there
7. **Filter-family deduplication**: enforces that price-derived features ([[../philosophy/concepts/golden-cross]], [[../philosophy/concepts/bollinger-bands]], [[../philosophy/concepts/distance-from-52w-high]]) contribute only one per ticker

## Anti-data-snooping rules

Per [[../philosophy/04-sector-and-finviz]]:

- **Rule 1**: train/val/test partition (60/20/20 chronological)
- **Rule 2**: price-derived features count as one family — at most one contributes per ticker
- **Rule 3**: NO threshold retuning after the test set is opened. If a strategy fails on test, archive it (don't retune to pass)

CI rejects backtest log entries that violate Rule 3.

## What goes in this directory

- `backtest/strategies/` — per-strategy specs and configs (one YAML per strategy)
- `backtest/results/` — output artefacts of each run (Phase 4 creates this)
- `backtest/historical_data/` — cached point-in-time OHLCV (created by Phase 2 ingest pipeline)

## See also

- [[../philosophy/04-sector-and-finviz]] — anti-data-snooping discipline
- [[../philosophy/09-point-in-time]] — lookahead-bias assertion contract
- [[../philosophy/10-strategies]] — Strategy A / B / C specs (the source-of-truth for what we backtest)
- [[../wiki/04_backtest_log]] — output log
