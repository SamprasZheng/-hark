# Sharks — 雙頻多因子 Wiki 交易系統

> Andy's medium-to-long-term US equity swing trading system + weekend crypto satellite, built on Karpathy's [LLM Wiki](philosophy/references/karpathy-llm-wiki.md) compile-first pattern. **Philosophy first, code second.**

## What this is

A trading decision system targeting **1-month-to-1-year US equity swing positions** (plus optional weekend crypto satellite), driven by a structured knowledge base of:

- **Mag 7 supply-chain bottleneck analysis** (the alpha source — see [philosophy/concepts/supply-chain-bottleneck.md](philosophy/concepts/supply-chain-bottleneck.md))
- **Macro narrative ingest** (Fed, Trump-admin policy, geopolitics)
- **Cycle-resonance and Last Snow regime detection** (half-year correction / two-month advance windows)
- **Finviz-style filter discipline** (with strict walk-forward defence against data-snooping)
- **Four-dimension signal taxonomy** with explicit conflict-arbitration (no sentiment-only entries)

It does **NOT** do high-frequency trading on US equities, **does NOT execute trades** (we emit recommendations; humans execute), and **does NOT custody private keys**.

## Quick start

```bash
cd D:\DOT\$hark
uv sync
uv run sharks pick --mode low   # Phase 1: prints a stub message
```

Phase 1 only ships the scaffold. All data clients return `NotImplementedError`. The signal aggregator, backtest engine, and dashboard arrive in Phase 2-5 per [docs/ROADMAP.md](docs/ROADMAP.md).

## What's in this directory

### Operating rules (start here)

- **[CLAUDE.md](CLAUDE.md)** — the operating rulebook (roles, SAFETY boundaries, source grading, the 10-signal contract). Read first, every session.
- **[skills/project-program-skill-target/](skills/project-program-skill-target/SKILL.md)** — the PPST engineering contract for multi-agent calls + structured artifacts.
- **[_legacy/philosophy/](_legacy/philosophy/)** — archived strategy/philosophy reference (history only; not active governance).

### Philosophy layer (static knowledge base)

- **[philosophy/index.md](philosophy/index.md)** — MOC for the philosophy layer
- **[philosophy/references/karpathy-llm-wiki.md](philosophy/references/karpathy-llm-wiki.md)** — methodology root (Karpathy's 2026-04-04 gist verbatim archive)
- **philosophy/00-thesis.md** through **10-strategies.md** — 11 numbered foundation pages
- **philosophy/concepts/*.md** — 12 concept-dictionary pages (technical + structural + behavioural)
- **philosophy/entities/*.md** — 13 entity pages (Mag 7 + supply-chain ADRs + Fed + Trump-admin)

### Compile-first runtime layer (dynamic — populated in Phase 2+)

- **raw/** — read-only source ingest (`macro/`, `earnings/`, `market_data/`, `kol_signals/`)
- **wiki/** — LLM-compiled state (`01_macro_state.md`, `02_mag7_bottleneck.md`, `03_alpha_library.md`, `04_backtest_log.md`, `positions.md`, `05_recommendations/`)

### Universe configuration

- **watchlist/universe.yaml** — tier1 (Mag 7) + tier2 (supply chain) + tier3 (dynamic mid-cap pool); sector buckets with enabling triggers

### Daily outputs

- **outputs/picks-YYYY-MM-DD.json** — machine-readable signal output (Phase 3+)

### Code

- **src/sharks/** — Python package (`cli.py`, `data/` stubs for 5 clients)
- **tests/** — pytest suite

### Documentation

- **[docs/ROADMAP.md](docs/ROADMAP.md)** — Phase 1-6 plan
- **[docs/SAFETY-CHECKLIST.md](docs/SAFETY-CHECKLIST.md)** — codex review's 10 trading-logic vulnerabilities, with alignment status
- **[docs/INSPIRATIONS.md](docs/INSPIRATIONS.md)** — 8 open-source projects we borrow architecture from

### Critique archives (frozen)

- **gemini.md** — Gemini-side design discussion and v1-plan critique (4 critical points)
- **codex.md** — AI-Codex-side v1-plan critique (10 trading-logic vulnerabilities)
- the original hand-written trading philosophy (`sharks.md`) is archived under `_legacy/` + git history

## Operating modes

Three modes are documented in [philosophy/07-mode-switch.md](philosophy/07-mode-switch.md):

- **`low`** (default, ~80% of usage): EOD price + hourly news + daily compile + daily 10-signal output. Mon-Fri.
- **`high`** (~20%): minute-bar price + near-real-time news. **Triggered by market state**, not by human calendar. Requires `SHARKS_HIGH_FREQ_OK=1` env var.
- **`auto`**: CLI evaluates conditions and selects.

Weekend crypto trading is a special case — see [philosophy/07-mode-switch.md](philosophy/07-mode-switch.md) for the criteria.

## The 10-signal daily contract

Each `outputs/picks-YYYY-MM-DD.json` carries exactly 10 slots:

- 2 `long_new` — new long entries from the 多頭真漲 quadrant
- 2 `short_new` — new short entries (Mag 7 Put / inverse ETF only; never direct borrow on retail mid-caps)
- 6 `position_followup` — adjustments to existing positions

Unfilled slots are `null` — **the system never pads**. See [philosophy/05-decision-rubric.md](philosophy/05-decision-rubric.md).

## Hard SAFETY boundaries

These never cross:

- **Never executes trades.** This system emits recommendations; humans execute.
- **Never holds private keys / wallet secrets.**
- **Never connects to brokerage / exchange APIs for order placement.**
- **Never modifies the operating rulebook (`CLAUDE.md`) without a human-applied diff.**
- **Never references future data in a backtest (`as_of_timestamp` discipline).**
- **Never pads the daily 10-signal output with low-confidence picks.**

Full list in [CLAUDE.md Section 2](CLAUDE.md).

## Why this design

Three reviewers (Gemini, AI-Codex, and the user's own trading philosophy, now archived in `_legacy/`) shaped this:

- The original trading-philosophy layer (`sharks.md` + `philosophy/`) is archived under `_legacy/` — history / reference only, not active governance.
- **Gemini's review** identified 4 architectural gaps in v1 (Long-only blind spot, daily-10 vs. 1-12m horizon contradiction, free-API high-freq misalignment, TD-9 trend-continuation override). All addressed in Phase 1.
- **Codex's review** identified 10 trading-logic vulnerabilities (2 Critical: point-in-time + risk/position; 4 High: sentiment rigidity, conflict resolution, data-snooping, time leakage; 4 Medium). All addressed in Phase 1; enforcement code lands Phase 2+.

The [docs/SAFETY-CHECKLIST.md](docs/SAFETY-CHECKLIST.md) tracks each of those issues against alignment status per phase.

## License

Proprietary. Not for redistribution.

## Author

Sampras Zheng — sampras2117@gmail.com
