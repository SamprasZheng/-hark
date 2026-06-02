# watchlist/

The structured ticker universe for the Sharks system. The single source of truth that the screener (Phase 2), signal aggregator (Phase 3), and backtest engine (Phase 4) all read.

## Contents

- `universe.yaml` — the active universe (this is what code reads)
- `history/` — versioned snapshots (`universe-YYYY-MM-DD.yaml`), created on every edit to `universe.yaml`. Required by [[../philosophy/09-point-in-time]] for backtest integrity. Phase 1: directory created on first universe edit; not pre-created.

## Universe schema (current: schema_version 1)

```yaml
schema_version: 1
as_of: YYYY-MM-DD
tiers:
  tier1_mag7: {description, tickers: [...]}
  tier2_supply_chain: {description, tickers: [...]}
  tier3_mid_cap_pool: {description, tickers: [...]}
sector_buckets:
  - {name, enabled, weight_cap_pct, enabling_trigger}
price_floor_exceptions: {description, tickers: [...]}
short_blacklist: {description, tickers: [...]}
human_overrides:
  - {ticker, notes}
```

## How to add a ticker

1. Identify the appropriate tier based on market cap and structural role:
   - tier1: Mag 7 only (immovable)
   - tier2: explicit upstream supply-chain ADR with [[../philosophy/concepts/supply-chain-bottleneck]] justification
   - tier3: usually does NOT require manual addition — populated by the Phase 4 screener
2. If adding a tier2 entity, also write the corresponding `philosophy/entities/<ticker>.md` page using the existing entity-page template (see [[../philosophy/entities/nvidia]] for the canonical form)
3. Update `universe.yaml`:
   - Add the ticker to the tier's `tickers` list (alphabetical within tier)
   - Bump the top-level `as_of` to today's date
4. Add a one-line entry to `wiki/log.md`: `## [YYYY-MM-DD HH:MM ET] universe | added <TICKER> to <tier>`
5. The Phase 2 lint job will create the snapshot `history/universe-YYYY-MM-DD.yaml` automatically. Until that's running, the human creates the snapshot manually via `cp universe.yaml history/universe-<old-as_of>.yaml` BEFORE editing.

## How to remove a ticker

The removal path is symmetric but stricter:

1. Verify the ticker has no open position in `wiki/positions.md`. If it does, exit the position before removal.
2. Update `universe.yaml`: remove the ticker; bump `as_of`.
3. Update `wiki/log.md` with a `removed` entry, including the reason (delisted, structurally no longer relevant, etc.).
4. The corresponding `philosophy/entities/<ticker>.md` page is NOT deleted — it stays as a historical reference (mark with `tier: archived` in frontmatter).

## Sector buckets — when do they enable?

Each disabled bucket has an `enabling_trigger` documented in `universe.yaml`. The Phase 3 macro-regime detector (`src/sharks/regime/sectors.py`) reads `wiki/01_macro_state.md` and flips bucket `enabled` state based on the triggers.

The human can also manually flip a bucket by editing `universe.yaml` directly. Manual flips are logged.

## Phase 1 status

- Tier 1: 7 names seeded (Mag 7)
- Tier 2: 8 names seeded (TSM, ASML, AVGO, AMD, ARM, MU, AMAT, LRCX)
- Tier 3: empty (correct for Phase 1)
- Sector buckets: technology + semiconductors enabled; 6 others pre-declared but disabled
- `history/` directory: not yet created (no edits since seed); first edit triggers creation

## See also

- [[../philosophy/06-exclusions]] — numerical exclusion filters applied on top of the universe
- [[../philosophy/04-sector-and-finviz]] — sector rotation logic that enables/disables buckets
- [[../philosophy/09-point-in-time]] — why the history/ snapshots are critical for backtest integrity
