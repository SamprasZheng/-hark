# wiki/05_recommendations/

Daily 10-signal output directory. Each trading day produces:

- `YYYY-MM-DD.md` — human-readable Markdown rendering of the daily signals
- (paired) `outputs/picks-YYYY-MM-DD.json` — machine-readable, schema-validated

## Markdown page schema

```yaml
---
type: recommendation
tags: [recommendation, daily]
as_of_timestamp: 2026-05-28T20:00:00-04:00
trading_date: 2026-05-29        # the trading session the signals are for
regime_ref: 01_macro_state.md@2026-05-28
schema_version: 1
author_role: compiler
risk_officer_review: passed
---
```

Section order (mandatory):

1. **Regime snapshot** (1 paragraph): macro / liquidity / mode / cycle-resonance state
2. **long_new** slots 1-2 (with thesis + evidence paths)
3. **short_new** slots 3-4
4. **position_followup** slots 5-10
5. **No-action buckets** (which slots are `null`, why)
6. **Discarded candidates** (screened in, rejected — with reason)

## Per-slot template

```markdown
### slot 1 — long_new — NVDA — strategy A — 多頭真漲

**Tier**: tier1 | **Horizon**: 90 days | **Size**: 4.0% | **Confidence**: 0.72

**Thesis** (1-2 sentences): ...

**Entry zone**: $458 – $472 | **Stop**: $432 | **Time stop**: 135 days

**Catalyst invalidation**: Blackwell delay > 1Q OR CoWoS capacity downgrade

**Evidence**:
- [[../02_mag7_bottleneck#cowos]]
- raw/earnings/nvda-2026q1.md
- [[../../philosophy/entities/nvidia#three-key-catalysts]]
```

## Archive

- `archive.md` — append-only summary of past recommendations and their outcomes; used for system-level performance review

## Phase 1 status

No daily recommendations yet. Phase 3 produces the first live output after `raw/` is populated and the signal aggregator is wired.

## See also

- [[../../philosophy/05-decision-rubric]] — the contract this directory implements
- [[../../philosophy/03-long-short-taxonomy]] — quadrant routing for the slots
- [[../positions]] — the open-position state these recommendations update
