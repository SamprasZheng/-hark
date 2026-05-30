# SAFETY-CHECKLIST.md

Codex review's 10 trading-logic vulnerabilities, mapped to alignment status at each Phase. Re-read every session before committing to `wiki/` or `outputs/`.

Source: `D:\DOT\$hark\codex.md` (the AI-Codex-side critique of the Phase 1 plan v1).

Status legend:
- ✅ **Aligned Phase 1**: philosophy / contract / scaffold covers this; implementation enforces at Phase 2+
- 🔧 **Phase 2+ implementation required**: contract exists, code does not yet enforce
- ⏳ **Tracked, not yet addressed**: known issue, scheduled for a specific later phase

---

## 1. [Critical] Point-in-time / lookahead bias absent

**Risk source**: `watchlist/universe.yaml`, `philosophy/entities/*`, `03-long-short-taxonomy.md`, `04-sector-and-finviz.md`

- ✅ **Aligned Phase 1**: dedicated `philosophy/09-point-in-time.md` page documents the `as_of_timestamp` contract; `universe.yaml` has the `as_of:` field; entity pages carry `last_earnings_date: TBD` (not silently filled with today); wiki and raw frontmatter schemas mandate `as_of_timestamp` + `source_first_visible_at`

- 🔧 **Phase 2 enforcement**: `sharks wiki lint` rejects pages missing `as_of_timestamp`; `watchlist/history/` snapshots created on every `universe.yaml` edit

- 🔧 **Phase 4 enforcement**: backtest engine asserts `max(used_source.as_of) <= trade.signal_time` on every signal evaluation; failure aborts run

**Acceptance**: zero lookahead-bias incidents in `wiki/04_backtest_log.md` past Phase 4 launch.

---

## 2. [Critical] Risk and position-sizing logic missing

**Risk source**: `05-decision-rubric.md`, `01-time-horizon.md`, `07-mode-switch.md`

- ✅ **Aligned Phase 1**: dedicated `philosophy/08-risk-and-position.md` page; size caps by tier; sector + catalyst + total-short caps; max-DD halt mechanic with 5-day cooldown + 10-day reduced-size period; per-thesis invalidation (price + time + catalyst) mandatory in `outputs/picks-*.json`; earnings-window policy

- 🔧 **Phase 3 enforcement**: Risk Officer agent rejects any signal that violates the contract; `risk_config.yaml` mirrors the document; diff between page and config is a P0 bug

- 🔧 **Phase 4 enforcement**: backtest simulates max-DD halt mechanic explicitly

**Acceptance**: Risk Officer test suite passes all synthetic-violation cases.

---

## 3. [High] "Sentiment-rally = sell" rule too rigid; kills early trend stocks

**Risk source**: original `03-sentiment-vs-fundamental.md` (renamed)

- ✅ **Aligned Phase 1**: replaced with `philosophy/03-long-short-taxonomy.md` four-quadrant taxonomy; sentiment is a weighting modifier, never a single-dimension trigger; per `02-signal-taxonomy.md` gating, sentiment alone never opens or reverses positions; conflict arbitration matrix handles sentiment / fundamental disagreement explicitly

- 🔧 **Phase 3 enforcement**: `sentiment.py` scorer caps its contribution to confidence at +0.15 multiplicative bonus only when aligned with another dimension

**Acceptance**: zero positions opened on sentiment-only signals in Phase 3+ live runs.

---

## 4. [High] Signal taxonomy missing conflict-resolution rules

**Risk source**: `02-signal-taxonomy.md`, `05-decision-rubric.md`

- ✅ **Aligned Phase 1**: `philosophy/02-signal-taxonomy.md` includes the explicit Conflict Arbitration Matrix (5 row table) with priority rules; `05-decision-rubric.md` specifies that the JSON output's `confidence` field is derived from the matrix output

- 🔧 **Phase 3 enforcement**: `src/sharks/scoring/arbitrate.py` implements the matrix; each row has a unit test (no exceptions)

**Acceptance**: arbitrator test coverage = 100% of matrix rows.

---

## 5. [High] Finviz-style filters create data-snooping risk

**Risk source**: `04-sector-and-finviz.md`, `backtest/README.md`

- ✅ **Aligned Phase 1**: `philosophy/04-sector-and-finviz.md` lists three anti-snooping rules: (1) train/val/test partition, (2) price-derived feature family deduplication (only one of golden-cross / Bollinger / distance-from-52w-high contributes per ticker), (3) no threshold retuning after test set is opened

- 🔧 **Phase 4 enforcement**: backtest framework enforces train/val/test split; CI rejects any backtest log entry where a filter was modified after test split was opened

**Acceptance**: backtest meta-log shows zero "test set tuning" incidents.

---

## 6. [High] Hourly news/KOL summaries leak future information

**Risk source**: `07-mode-switch.md`, future Phase 2 news pipeline

- ✅ **Aligned Phase 1**: `philosophy/09-point-in-time.md` includes the release-time normalisation section; `raw/README.md` mandates `source_first_visible_at` field; `CLAUDE.md` agent rules require split-by-claim with per-claim `as_of_timestamp`

- 🔧 **Phase 2 enforcement**: ingest pipeline runs a `time-leak-suspected` sanity check on every claim; market-reaction-after-claim is detected and rejected

**Acceptance**: zero `time-leak-suspected` incidents in `wiki/log.md` past Phase 2 launch.

---

## 7. [Medium] Mode switching by human calendar is too coarse

**Risk source**: `07-mode-switch.md`

- ✅ **Aligned Phase 1**: `philosophy/07-mode-switch.md` redefines mode triggers as **market state** functions (VIX band, Fed/CPI/NFP, earnings windows, instrument liquidity); the human calendar (weekend, WFH) is one input among many; weekend crypto special case explicit

- 🔧 **Phase 3 enforcement**: `src/sharks/mode/decide.py` implements the pseudo-spec; refusal conditions are P0 hard guards

**Acceptance**: Phase 3 unit tests verify each refusal condition triggers correctly.

---

## 8. [Medium] Exclusion list non-numerical, leaves grey zones

**Risk source**: `06-exclusions.md`

- ✅ **Aligned Phase 1**: `philosophy/06-exclusions.md` numerises every exclusion: penny floor `$5`, liquidity floor `$5M/day`, market cap floor per tier, OTC + SPAC + post-IPO 90d + halt-risk; short-side additional rules (short interest, borrow fee, days-to-cover); macro-state exclusions (Fed day, VIX > 35)

- 🔧 **Phase 2 enforcement**: `src/sharks/screener/exclusions.py` implements as deterministic predicates; `tests/test_exclusions.py` verifies every threshold

**Acceptance**: every threshold in the page has a corresponding unit test.

---

## 9. [Medium] "10 picks every day" is a hard quota; fills with garbage on weak days

**Risk source**: `05-decision-rubric.md`

- ✅ **Aligned Phase 1**: `philosophy/05-decision-rubric.md` allows `null` slots and `no_action_buckets` array; Risk Officer rejects any submission with `confidence < 0.50` candidates padding slots; expected monthly distribution documented

- 🔧 **Phase 3 enforcement**: `sharks pick` emits `null` slots and tracks `no_action_buckets` rate per month; a `no_action_rate` > 8 / month emits a warning in the daily output

**Acceptance**: published daily outputs never carry confidence < 0.50 picks.

---

## 10. [Medium] Mag 7 + supply-chain over-concentrated in tech / semis

**Risk source**: `watchlist/universe.yaml`, `04-sector-and-finviz.md`

- ✅ **Aligned Phase 1**: `watchlist/universe.yaml` declares 8 sector buckets (technology + semiconductors enabled; 6 others — defensive_staples, rate_sensitive, energy, financial, biotech_small, defense — pre-declared with `enabling_trigger` rules); `philosophy/04-sector-and-finviz.md` documents enabling conditions

- 🔧 **Phase 3 enforcement**: macro-regime detector reads `wiki/01_macro_state.md` and flips bucket `enabled` state based on triggers; sector cap of 25% in `08-risk-and-position.md` prevents tech-dominated portfolio in any single regime

**Acceptance**: in any 12-month rolling window, no single sector contributes > 50% of portfolio realised return.

---

## Cross-cutting: Gemini review's 4 critiques

Gemini side review (in `D:\DOT\$hark\gemini.md`) added four critical points that overlap with codex's items:

### G1. Long-only blind spot

→ Resolved by **Item 3** above (four-quadrant taxonomy) + `philosophy/03-long-short-taxonomy.md` iron rules for short-side (Put-only on retail mid-caps).

### G2. Daily-10 vs. 1-12 month horizon contradiction

→ Resolved by **Item 9** above + `philosophy/05-decision-rubric.md` slot allocation (2 long_new + 2 short_new + 6 position_followup, where followups are the longer-horizon discipline).

### G3. Free-tier API high-freq deceptiveness

→ Documented in `pyproject.toml` and `src/sharks/data/polygon_client.py` docstring: Polygon free does not support intraday; explicit `ccxt_client.py` added for crypto high-freq; high-freq US equity intraday deferred to Phase 6 paid tier or Alpaca / Webull.

### G4. TD-9 trend-continuation override

→ Resolved in `philosophy/concepts/td-9-sequential.md` with the volume-validation guard: true top vs. trend-continuation distinction by volume ratio + analyst-revision input. Mandatory before TD-9 contributes to score.

---

## How to update this file

- Each phase's first week: re-read every item, confirm Phase status flags are accurate, update with any new findings
- New review-feedback items are appended as **Items 11+**; this list grows over time
- The codex / gemini review files in the repo root are **frozen**; this file is the working version
