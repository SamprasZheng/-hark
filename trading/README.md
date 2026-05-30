# trading/

Phase 3+ home for the signal aggregation and decision-output pipeline.

## Phase 1 status

Empty placeholder. The Phase 3 implementation lives in `src/sharks/scoring/` (per-dimension scorers) and `src/sharks/decision/` (the daily 10-signal rubric); see `docs/ROADMAP.md` Phase 3.

## What goes here in Phase 3

This directory holds **non-code** artefacts that complement the trading runtime:

- `trading/templates/` — Markdown templates for `wiki/05_recommendations/YYYY-MM-DD.md`
- `trading/risk_config.yaml` — mirror of the numerical thresholds in [[../philosophy/08-risk-and-position]] (sizing, sector caps, max-DD halt). Single source of truth; the Python runtime imports from this YAML.
- `trading/sector_classifications.yaml` — sector → bucket → enabling_trigger map. Mirror of `watchlist/universe.yaml` `sector_buckets` for code consumption.
- `trading/strategy_a_config.yaml`, `strategy_b_config.yaml`, `strategy_c_config.yaml` — per-strategy numerical params (the strategies are documented in `philosophy/10-strategies.md`; this is the runtime configuration that the strategies read)

## Code lives in `src/sharks/`

The Python implementation of the signal aggregator, scoring, and decision logic does NOT live here. It lives in `src/sharks/{scoring,decision,risk,mode}/`.

`trading/` is for the data-driven configuration only.

## See also

- [[../philosophy/05-decision-rubric]] — the 10-signal output contract
- [[../philosophy/08-risk-and-position]] — risk and sizing rules this YAML mirrors
- [[../philosophy/10-strategies]] — Strategy A / B / C specs
- [[../docs/ROADMAP]] — Phase 3 plan
