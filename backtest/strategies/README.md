# backtest/strategies/

Phase 4 home for per-strategy backtest configuration YAMLs.

## Phase 1 status

Empty placeholder. Phase 4 produces:

- `strategy_a.yaml` — Consolidation-Breakout (per [[../../philosophy/10-strategies]] Strategy A)
- `strategy_b.yaml` — Momentum Breakout
- `strategy_c.yaml` — Whale / Order-Flow Tracking
- `cycle_resonance.yaml` — Cycle-Resonance 6m bucket entries (per [[../../philosophy/concepts/cycle-resonance]])
- `composite.yaml` — Portfolio-level combination of A + B + C + cycle_resonance with caps from [[../../philosophy/08-risk-and-position]]

## YAML schema template

```yaml
schema_version: 1
strategy_id: strategy_a
strategy_name: Consolidation-Breakout
philosophy_ref: philosophy/10-strategies.md#strategy-a
kpi_targets:
  sharpe_min: 0.8
  max_drawdown_max_pct: 25
  win_rate_min_pct: 45
  median_holding_period_days_range: [60, 120]
  worst_single_trade_loss_max_pct: 10
trigger:
  consolidation_band_pct: 0.05         # ±5% of 60MA
  consolidation_min_weeks: 4
  dry_volume_ratio_threshold: 0.8       # 5d/90d avg
  breakout_volume_multiplier: 1.5       # vs 20d avg
  fundamental_filter:
    sales_qoq_min_pct: 10
    margin_not_deteriorating: true
exit:
  price_invalidation:
    method: consolidation_low_minus_n_atr
    n_atr: 1.0
    atr_period: 20
  time_stop_days: 135
  catalyst_invalidation:
    method: negative_fundamental_update_during_holding
universe:
  tier_filter: [tier1_mag7, tier2_supply_chain]
  exclusions_ref: philosophy/06-exclusions.md
sizing:
  default_pct_of_tier_cap: 1.0  # full tier cap
walkforward:
  train_pct: 60
  val_pct: 20
  test_pct: 20
data:
  source: yfinance + polygon_historical
  start_date: 2015-01-01
  end_date: 2025-12-31
```

## Discipline

Every config edit increments a `revision:` field. Every revision is logged with rationale to `wiki/04_backtest_log.md`. A config that has been retuned after its test split was opened is **rejected** by the Phase 4 framework and the revision history records the rejection.

## See also

- [[../../philosophy/10-strategies]] — Strategy A / B / C source of truth
- [[../../philosophy/04-sector-and-finviz]] — anti-data-snooping discipline that constrains config edits
- [[../README]] — parent backtest docs
