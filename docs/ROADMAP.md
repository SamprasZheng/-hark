# ROADMAP

Phase-by-phase plan for the Sharks system. Phase 1 (this scaffold) is complete on commit; subsequent phases are not started.

## Phase 1 — Constitution + Compile-first Scaffold ✅

**Goal**: establish the philosophy layer, the Compile-first directory architecture, the agent operational rules, and a runnable Python project skeleton with stubbed data clients.

**Delivered**:
- `sharks.md` constitution with frontmatter (original 6 principles + 4 bottoming patterns preserved verbatim)
- `CLAUDE.md` agent operational rules (Compiler / Researcher / Risk Officer roles, hard SAFETY boundaries)
- `philosophy/` — 11 numbered foundation pages, 12 concept-dictionary pages, 13 entity pages, references including Karpathy gist archive
- `raw/` + `wiki/` Compile-first scaffold with stub pages
- `watchlist/universe.yaml` (Mag 7 + 8 supply-chain ADRs)
- `pyproject.toml` + Python `src/sharks/` skeleton with `NotImplementedError` data client stubs
- `docs/SAFETY-CHECKLIST.md` mapping codex review's 10 vulnerabilities to alignment status
- `docs/INSPIRATIONS.md` (this directory) — 8 open-source projects to borrow from

**Out of scope for Phase 1** (deferred to Phase 2+):
- No API connectivity (yfinance, polygon, finnhub, finviz, ccxt all stubbed)
- No live signals, no real `outputs/*.json` files
- No backtest execution
- No TypeScript UI
- No brokerage / exchange / wallet integration

---

## Phase 2 — API Wiring + Raw Ingest

**Goal**: connect the 5 data clients to real APIs and start filling `raw/` with timestamped sources.

**Deliverables**:
1. **yfinance client**: EOD OHLCV pull for tier1 + tier2; weekly batch + on-demand
2. **Polygon free-tier client**: historical OHLCV backfill (US equities); explicit caveat that intraday is not supported on free tier (per `polygon_client.py` docstring)
3. **Finnhub client**: news feed + earnings calendar; rate-limit-aware ingest scheduler
4. **Finviz client**: Phase 1 filter set ([[../philosophy/04-sector-and-finviz]]) executed daily after US close; output → `raw/market_data/finviz-*.csv` with timestamp
5. **ccxt client**: weekend crypto public-market data (Binance, OKX); read-only (no keys); intended for [[../philosophy/07-mode-switch]] crypto high-freq scenarios
6. **`.env` loading** via `python-dotenv`; documented in `.env.example`
7. **Smoke tests**: each client has a `pytest -m smoke` test that hits the real API and verifies basic response structure
8. **Compile-first loop (skeleton)**: `sharks ingest` CLI subcommand reads new files in `raw/`, computes summary, and APPENDS to `wiki/log.md` (does not yet update `wiki/01_macro_state.md` — that's Phase 3)

**Acceptance criteria**:
- `uv run sharks ingest --source raw/macro/fed-fomc-2026-XX-XX.md` produces a log entry
- All 5 clients have green smoke tests in CI
- No `as_of_timestamp` discipline violations introduced (lint passes per [[../philosophy/09-point-in-time]])

**External dependencies to add to pyproject.toml**:
- `yfinance`, `polygon-api-client`, `finnhub-python`, `finviz`, `ccxt`, `python-dotenv`, `pyyaml`

---

## Phase 3 — Compile Engine + Signal Aggregation

**Goal**: populate `wiki/` from `raw/` and produce the first `wiki/05_recommendations/YYYY-MM-DD.md`.

**Deliverables**:
1. **Compiler agent**: reads new `raw/` files, integrates claims into existing wiki pages (NOT just new pages), updates `wiki/01_macro_state.md`, `wiki/02_mag7_bottleneck.md`, `wiki/03_alpha_library.md`
2. **Four-dimension scorers** (per [[../philosophy/02-signal-taxonomy]]):
   - `src/sharks/scoring/fundamental.py` — Sales QoQ, margin trajectory, source-grade weighted
   - `src/sharks/scoring/news.py` — macro-event tagging + supply-chain impact tracing
   - `src/sharks/scoring/technical.py` — TD-9 (with volume validation), MAs, Bollinger, distance-from-52w-high, price-volume divergence
   - `src/sharks/scoring/sentiment.py` — social volume z-score (weighting only — never single-source decision)
3. **Conflict arbitration**: `src/sharks/scoring/arbitrate.py` implements the matrix in [[../philosophy/02-signal-taxonomy]]; every matrix row has a unit test
4. **Daily 10-signal generator**: `sharks pick` CLI command emits `outputs/picks-YYYY-MM-DD.json` (validated against schema) + companion `wiki/05_recommendations/YYYY-MM-DD.md`
5. **Risk Officer agent**: gating pass before write; veto on [[../philosophy/06-exclusions]], [[../philosophy/08-risk-and-position]] violations
6. **Mode switch logic**: `src/sharks/mode/decide.py` per [[../philosophy/07-mode-switch]] decision function spec
7. **Macro regime detector**: `src/sharks/regime/cycle.py` + `src/sharks/regime/last_snow.py` + `src/sharks/regime/liquidity.py`
8. **Wiki lint command**: `sharks wiki lint` verifies frontmatter, link resolution, `as_of_timestamp` presence, log format

**Acceptance criteria**:
- `uv run sharks pick --mode auto` produces a valid JSON file matching the [[../philosophy/05-decision-rubric]] schema
- All 4 dimension scorers have unit tests for the threshold conditions
- The Risk Officer test suite verifies that synthetic violation cases are blocked
- The lint command exits non-zero on synthetic broken-link cases

---

## Phase 4 — Backtest Engine

**Goal**: validate the signal logic against historical data with strict walk-forward discipline.

**Deliverables**:
1. **Backtest framework**: choose Backtrader or vectorbt (lean toward vectorbt for speed; decide on first sprint)
2. **Train/val/test partition**: enforced per [[../philosophy/04-sector-and-finviz]] Rule 1
3. **Point-in-time assertion**: every signal evaluation checks `max(source.as_of) <= trade.signal_time`; assertion failure aborts backtest
4. **Per-strategy backtest configs**: `backtest/strategies/strategy_a.yaml`, `strategy_b.yaml`, `strategy_c.yaml`, `cycle_resonance.yaml`
5. **Composite portfolio backtest**: combine strategies with the [[../philosophy/08-risk-and-position]] caps and max-DD halt simulation
6. **KPI reporting**: each run emits a `wiki/04_backtest_log.md` entry following the template
7. **Filter family deduplication**: enforce that price-derived features ([[../philosophy/concepts/golden-cross]], [[../philosophy/concepts/bollinger-bands]], [[../philosophy/concepts/distance-from-52w-high]]) contribute only one per ticker

**Acceptance criteria**:
- Strategy A backtest on 2015-2025 train + 2020-2025 val passes KPI targets (Sharpe > 0.8, MDD < 25%, Win > 45%)
- Strategy B backtest hits its KPI targets
- Strategy C backtest hits its KPI targets (using crypto data where US dark-pool is unavailable)
- Cycle-resonance detector reproduces all historical instances in [[../philosophy/concepts/cycle-resonance]] within ±2 weeks
- Last Snow detector flags each historical instance in [[../philosophy/concepts/last-snow]] within ±2 weeks

---

## Phase 5 — Lightweight TS UI

**Goal**: human-readable dashboard for daily review.

**Deliverables**:
1. **TS + Vite + React** single-page app; reads `outputs/picks-*.json` + selected `wiki/*.md` rendered as MDX
2. **Dashboard views**:
   - Today's 10 signals (highlighted slot cards)
   - Open positions list (from `wiki/positions.md`)
   - Macro regime snapshot (from `wiki/01_macro_state.md`)
   - Backtest performance summary
3. **No execution capabilities** — viewer only. The system never trades.
4. Optionally a `local` deployment mode (run on user's laptop) and a `private` cloud mode (Cloudflare Pages, password-protected)

**Acceptance criteria**:
- All views render real data from the Phase 3 outputs
- No state mutation from the UI
- Markdown rendering supports Obsidian `[[link]]` style with internal page linking

---

## Phase 6 — High-Freq Mode Activation + Optional Live Marketdata

**Goal**: enable the documented [[../philosophy/07-mode-switch]] high-freq mode for weekend crypto and selected US equity scenarios.

**Deliverables**:
1. **ccxt-based crypto high-freq**: minute-bar pull, order book depth analysis, large-transfer clustering
2. **(Optional) Paid Polygon tier**: subscribe if Phase 5 dashboard usage justifies; then enable intraday US equity in high-freq mode
3. **(Optional) Alpaca / Webull API**: only for the high-freq US equity intraday data feed; explicit no-execution discipline preserved
4. **Mode-state observability**: dashboard panel shows current mode, why, hours spent in each mode per week
5. **High-freq KPI tracking**: separate Sharpe / MDD / Win rate tracking for high-freq sessions (since they should be far smaller share of total exposure)

**Acceptance criteria**:
- High-freq mode activation respects all the refusal conditions in [[../philosophy/07-mode-switch]]
- Total high-freq exposure ≤ 25% of portfolio per [[../philosophy/10-strategies]] combined B+C cap
- No execution capability added in this phase (the no-brokerage rule remains)

---

## Beyond Phase 6 (open questions)

- Should the system grow a paper-trading shadow that consumes its own recommendations and tracks live PnL?
- Should the wiki layer feed a fine-tuned model later, or stay LLM-prompted indefinitely?
- Should the system expand to non-US equities (Taiwan-listed semis: 2330, 2454, 3008)? Decision pending Phase 5 feedback.

These remain open until Phase 4 backtest results validate that the underlying philosophy is profitable. The system's edge has not been earned until Phase 4 KPIs are met on test (not just train + val).
