# CLAUDE.md — Operating rulebook

> Operating rules for any LLM agent (Claude / Codex / Grok / Gemini / Cursor / OpenCode) working in `D:\DOT\$hark\`.
> This is an **engineering** rulebook. The execution model is **PPST** — `skills/project-program-skill-target/`.
> No philosophy framing: the legacy strategy/philosophy layer is archived under `_legacy/` for reference only, not active governance.

---

## 0. First read, every session

1. This file (`CLAUDE.md`) — the operating rulebook.
2. `skills/project-program-skill-target/SKILL.md` — the PPST execution model.
3. The last 10 entries of `wiki/log.md` — recent state.
4. §2 point-in-time — before anything that lands in a backtest or in `outputs/`.

---

## 1. Roles (PPST)

Every writeback declares its role (`author_role:` on markdown frontmatter, `role:` in JSON output).

- **Orchestrator** — owns the PROJECT; decomposes it into TARGETs; routes `[CALL SKILL]` handoffs; integrates results. Carries no long chat state — uses the four PPST layers + explicit `CONTEXT`.
- **Writer** — receives one PROGRAM + one TARGET; implements **only** inside that PROGRAM; writes tests; self-reviews before handoff.
- **Risk Officer** — gatekeeper before any capital-impacting artifact (`outputs/picks-*.json`, `wiki/05_recommendations/*`). Veto power. Full mandate, veto triggers, and the mandatory 5-section review format live in `RISK_OFFICER_SLA.md`. On veto the Writer rewrites — it never overrides.

---

## 2. Hard boundaries — P0, never cross

- **No trades.** No brokerage / exchange / wallet keys. The system emits *recommendations*; execution is a human action.
- **No lookahead.** Anything compiled into `wiki/` or consumed by a backtest carries an `as_of_timestamp`; never use `as_of`-later data in an `as_of`-earlier analysis (e.g. today's sector label on an old trade). This is the most expensive class of bug in a quant system — it makes backtests look brilliant and live results bleed. (Detail archived: `_legacy/philosophy/09-point-in-time.md`.)
- **`raw/` is immutable.** Inputs are never edited. Correct a source by adding a dated `.v2` file and logging the supersession in `wiki/log.md`.
- **No fabrication.** No invented tickers, prices, or earnings dates → write `TBD` and log a follow-up in `wiki/log.md`.
- **No padding** the 10-signal output (§5). Unfilled slots are `null` / `no_action`.
- **No ingest-edits to governance.** `CLAUDE.md`, `AGENTS.md`, and `RISK_OFFICER_SLA.md` change only via a reviewed diff with human sign-off — never as a side effect of a run. `_legacy/` is read-only history.

---

## 3. PPST execution contract

Full spec: `skills/project-program-skill-target/SKILL.md`. In short:

- Declare all four layers at the top of any work block:
  `PROJECT:` / `PROGRAM:` / `SKILL:` / `TARGET:`.
- Work **only** inside the declared PROGRAM. **One TARGET at a time.**
- Hand off (or call yourself / another agent) with a `[CALL SKILL]` block + minimal `CONTEXT:`.
- A TARGET is **done** only when: the artifact exists, review passed (self-review or a `CALL SKILL` to the Risk Officer), and the next handoff (if any) is stated with the four layers.
- Outputs are **structured artifacts** — JSON / JSONL wherever a schema exists.

---

## 4. Source grading A–E

| Grade | Description | Example |
|---|---|---|
| `A` | Primary, official, timestamped, archivable | Fed FOMC statement, SEC 10-Q, company press release |
| `B` | Reputable second-hand with source links | Bloomberg piece linking the primary |
| `C` | Reputable second-hand without links | WSJ analysis, tier-1 analyst summary |
| `D` | Social / KOL / opinion | X post, Telegram channel |
| `E` | Unverified rumour / low-confidence scrape | forum thread, sourceless screenshot |

- Tier-1 theses (> 3 months) require **≥ 2 A-grade** sources.
- Grade **D/E may inform a watchlist but never opens a position on its own**.

---

## 5. The 10-signal artifact contract

`outputs/picks-YYYY-MM-DD.json` (+ the `wiki/05_recommendations/YYYY-MM-DD.md` readout) carries exactly:

- **2 `long_new`**, **2 `short_new`**, **6 `position_followup`**.

Unfilled slots → `null`, listed in `no_action_buckets`. **Padding is a Risk-Officer veto trigger.** The producing PROGRAM is `src/sharks/daily_picks.py`.

---

## 6. Frequency modes

`low` (default) / `high` / `auto`, set by **market state**, not the calendar. `high` requires VIX ∈ [12, 18], no earnings within ±3 trading days on a held name, no Fed/CPI/NFP day, the 60-day dollar-volume threshold, and explicit opt-in (`SHARKS_HIGH_FREQ_OK=1`). A volatility spike reverts to `low`. (Detail archived: `_legacy/philosophy/07-mode-switch.md`.)

---

## 7. Artifacts, provenance & layout

- `wiki/` and `outputs/` artifacts carry frontmatter: `type`, `as_of_timestamp`, `author_role`/`role`; compiled pages also `source_paths: [...]` and `confidence: 0..1`.
- Markdown; clinical and falsifiable; no marketing language.
- Data flow: `raw/` (immutable inputs) → compiled `wiki/` state → `outputs/` daily artifacts. Integrate into existing pages before adding new ones.
- `tech/` is the technology due-diligence research layer (recommend-only; `tech/index.md`). `_legacy/` holds the archived strategy/philosophy reference.

---

## 8. Multi-agent discipline

See `AGENTS.md`: worktree isolation, **mandatory cross-review before merge**, and the **Risk-Officer gate** on anything touching `outputs/picks-*` or `wiki/05_recommendations/*`. Local-first (Ollama) for volume; Grok at high-stakes review gates via `scripts/cross-review.ps1`.

---

## 9. Change control

`CLAUDE.md`, `AGENTS.md`, and `RISK_OFFICER_SLA.md` are governance: changed only by a reviewed diff with human sign-off, logged in `wiki/log.md` — not by an unprompted agent ingest. The legacy strategy/philosophy layer is frozen in `_legacy/` (reference only).

---

## 10. Trading Society — silicon trading society (research layer)

A multi-agent **research** layer (矽基交易社會): specialized AI traders/analysts with distinct strategies and time frequencies that improve via competition, multi-round debate, reflection, and **controlled, human-gated** evolution. It is a PROJECT under PPST (`programs/trading_society/PROJECT.md`), not a production signal source. The four user phases map to four PROGRAMs: Backtest/Simulation (Phase 0), Debate (Phase 1), Ranking+Reflection (Phase 2), Evolution (Phase 3).

**It inherits every P0 boundary in §2 and adds these binding rules:**

- **Research, never a shortcut to the §5 contract.** Society outputs are research artifacts. They never produce or bypass `outputs/picks-*.json` / `wiki/05_recommendations/*`. Promotion of any society output to a capital-facing signal requires **human winner-selection + Risk-Officer gate + cross-review** (§8, `AGENTS.md §3`).
- **Human is the final selector.** Evolution is assistive. No mutated/evolved agent becomes "active" for capital-facing use without explicit human selection.
- **LLM-backtest protocol is mandatory.** Any society backtest path obeys `docs/LLM-BACKTEST-PROTOCOL.md`: an `llm_involvement` marker on every output, no banned forecast-shaped keys (`probability/direction/verdict/target/forecast/signal/score`) on historical periods, walk-forward gating for LLM-involved runs, and RAG `before_as_of = as_of`. Only `none`/`narration_only` runs are KPI-eligible.
- **~10 actions per simulated society-day** (mirrors the §5 10-signal spirit; prevents over-trading in sim). No padding — unfilled slots are `null`/`no_action`.
- **Ecological niches protected.** Each core agent owns a distinct (frequency × edge) slot; the Ranking/Evolution layer protects empty niches and injects novelty to prevent winner-take-all (大者恆大).
- **Grade D/E** (KOL/social/pure model opinion) informs watch buckets only — never opens or sizes a society position (§4).
- **High-valuation forced-hedge rule.** In a high-valuation regime (Buffett Indicator > 200% **or** the Dalio bubble flag is set), the multi-round debate must force-include the **TailRisk_Hedger_Agent** plus at least one risk-off voice (Buffett/Burry/Dalio), and **any consensus must carry an explicit hedge / capital-preservation plan — otherwise the Risk Officer (debate Verifier seat) vetoes it.** The legendary-investor persona roster (`simulation/personas.py`, `skills/multi_round_debate/personas/`) is recommend-only: persona outputs enter the debate transcript and never emit a ticker order.

**Regime guardrails (grok2.md, veto-class — `simulation/regime_filter.py`).** A regime classifier gates capital posture. These are hard, falsifiable rules aligned with the Risk-Officer gate:

- **HARD_DEFENSE** (net liquidity draining **and** gold outperforming BTC — 1929/2008/2020/2018Q4/2022 analog): small-cap long **allocation cap = 0**, forced defensive floor (≥60%), strict winsorization.
- **PARADIGM_BREAKTHROUGH** (capex growth > 25% **and** strong risk appetite — 1999/2024-26 AI analog): **Momentum Decoupling Lock ON** — reverse-shorts on the AI leaders (NVDA/SMCI/AVGO/ASML/TSM/ORCL…) are **blocked** until the TD-9 / Sharpe-haircut decays (anti-Gamma-squeeze, account survival). Small-cap momentum stays strictly winsorized.
- **MEAN_REVERSION** (otherwise): standard caps; the valuation floor still applies.

**Long-bias / shorting rule (principal directive).** The society is **long-biased by default**. Short positions are permitted **only in a confirmed bear regime** — `HARD_DEFENSE`, the 2022 / COVID-style liquidity-shock analog (in the historical sim: a month whose trailing-6-month median market return is below −8%, computed point-in-time). In `PARADIGM_BREAKTHROUGH` and `MEAN_REVERSION` the society is long-only. When shorting is enabled, per-name short loss is capped at −100% (a stop). Enforced in `simulation/regime_filter.shorts_allowed()` and the backtest layer; specialist traders are long-only by construction.

**Three Ground-Truth invariants (always on):** (1) small-cap melt-ups are asymmetric **"right-to-zero"** → strict dynamic truncation of small-cap momentum; (2) sovereign-credit / geopolitical paradigm faults (1917 Russia, 1949 China) break all backtests → a sovereign/geopolitical-immunity guardrail overrides technicals; (3) during a tech-paradigm squeeze, mean-reversion shorts on leaders are force-blocked by the Momentum Decoupling Lock. Reference data: century regime matrix `simulation/data/century_regimes.json`, quarterly answer key `simulation/data/quarterly_benchmark_2018_2026.json` (both **Grade-D, grading/reference only — never trader inputs, no lookahead**).

**Point-in-time data discipline (§2 cross-ref).** Society backtests / evolution-fitness / regime-classifier training use **ALFRED vintage data** (`vintage_date = as_of`) wherever a FRED input is consumed — plain "latest" FRED is for live same-day reads only, and is flagged `is_point_in_time: false`. Real data sources wired: **FRED** (macro composite + real Buffett Indicator NCBEILQ027S/GDP), **Finviz Elite** (real industry sectors for the concentration cap + valuation), **Polygon** (prices; capex when the cash-flow line is present). Concentration discipline is binding: single-sector ≤ 35%, single-name ≤ 10%, transaction costs charged in fitness, and the **valuation floor overrides a risk-on macro** (a calm-credit tape does not relax the high-valuation hedge).

**Canonical artifacts:** roles → `programs/trading_society/CORE_AGENT_ROLES.md`; orchestrator → `simulation/society_orchestrator.py`; backtest+fitness → `simulation/backtest_runner.py` + `simulation/performance_tracker.py`; debate → `programs/debate/DEBATE_PROGRAM.md` + `skills/multi_round_debate/SKILL.md` + `simulation/debate_engine.py`; investor personas → `simulation/personas.py` + `skills/multi_round_debate/personas/`; ranking/reflection/mutation → `simulation/ranking_system.py` + `simulation/reflection_engine.py` + `simulation/evolution/mutator.py` + `simulation/evolution/evolution_engine.py` (+ `programs/evolution/EVOLUTION_PROGRAM.md`); competition → `simulation/tournament.py` + `simulation/historical_competition.py` + `simulation/universe_competition.py`; forward portfolio → `simulation/portfolio_generator.py`; real data → `simulation/macro_risk.py` + `simulation/capex_provider.py` + `simulation/finviz_data.py`; regime guardrail → `simulation/regime_filter.py` + `simulation/data/century_regimes.json`. Compiled overview: `wiki/26_trading_society.md`.
