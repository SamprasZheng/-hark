---
type: research
title: Trading Society — 矽基交易社會 (multi-agent research layer)
as_of_timestamp: 2026-06-13T22:30:00+08:00
author_role: orchestrator
status: live
confidence: 0.6
tags: [trading-society, multi-agent, debate, evolution, backtest, ppst, governance]
source_paths:
  - programs/trading_society/PROJECT.md
  - programs/trading_society/CORE_AGENT_ROLES.md
  - programs/debate/DEBATE_PROGRAM.md
  - programs/evolution/EVOLUTION_PROGRAM.md
  - skills/multi_round_debate/SKILL.md
  - simulation/society_orchestrator.py
  - simulation/backtest_runner.py
  - simulation/performance_tracker.py
  - simulation/debate_engine.py
  - simulation/ranking_system.py
  - simulation/reflection_engine.py
  - simulation/evolution/mutator.py
  - grok.md (debate guide + ABCDE plan; conversation seed)
  - docs/LLM-BACKTEST-PROTOCOL.md
  - CLAUDE.md §10
---

# 26 — Trading Society (矽基交易社會)

> A multi-agent **research** layer. Specialized AI traders/analysts with distinct
> strategies and time frequencies improve via competition → multi-round debate →
> reflection → **controlled, human-gated** evolution. It is governed by
> [[../CLAUDE]] §10 and **never** produces or bypasses the §5 10-signal contract.
> Every output is research until a human selects it and the Risk Officer gates it.

## Why this exists

The owner's plan (digested from `grok.md`) asks for a "society" of trading agents
that compete and evolve, validated on history under strict point-in-time rules,
with the human keeping final selection. This page is the compiled map; the
canonical PPST decomposition is `programs/trading_society/PROJECT.md`.

## PPST decomposition (4 user phases → 4 PROGRAMs)

| Phase | PROGRAM | Status | Key artifacts |
|---|---|---|---|
| 0 (highest) | Backtest / Simulation | **shipped (skeleton)** | `simulation/backtest_runner.py`, `simulation/performance_tracker.py` |
| 1 | Debate | **shipped (skeleton)** | `programs/debate/DEBATE_PROGRAM.md`, `skills/multi_round_debate/SKILL.md`, `simulation/debate_engine.py` |
| 2 | Ranking + Reflection | **shipped (skeleton)** | `simulation/ranking_system.py`, `simulation/reflection_engine.py` |
| 3 | Evolution | **base shipped** | `programs/evolution/EVOLUTION_PROGRAM.md`, `simulation/evolution/mutator.py` |

## The agents (7 specialists + 1 meta)

Full definitions + prompt templates + model routing: `programs/trading_society/CORE_AGENT_ROLES.md`.

| Role | Horizon / freq | Model size | Niche (protected) |
|---|---|---|---|
| HF_SCALPER | minutes–intraday | small/fast | only sub-day tactical slot |
| MOMENTUM_SWING | 1–5 days | medium | daily momentum / trend |
| MEAN_REVERSION_SWING | 2–10 days | medium | counter-trend / fading |
| MACRO_REGIME | weeks–months | large | strategic regime overlay |
| EVENT_CATALYST | event windows | medium-large | catalyst timing (earnings/M&A) |
| VALUE_CONTRARIAN | months–years | large | deep value / long horizon |
| OVERLAY_RISK | continuous | medium | sizing, caps, DD halts, action budget |
| SYNTHESIZER | debate + synthesis | largest | multi-round debate + final readout |

Model routing follows the plan "小模型負責高頻，大模型負責辯論與風險控管".

## How a cycle composes (verified end-to-end, synthetic, `llm_involvement=none`)

```
backtest_runner (B) ──► performance_tracker fitness ──► ranking_system (D)
        │                                                     │
        │                                              bottom-K selection
        ▼                                                     ▼
   debate_engine (C) ◄──── society_orchestrator (E) ──► reflection_engine (D)
        │                                                     │
   structured synthesis                              mutation candidate (D)
   (consensus / no_action)                           ── human gate required ──►
```

`python simulation/society_orchestrator.py` runs the integrated demo:
backtest → rank → reflect → mutation candidate (human-gated) → debate consensus.
All six modules also self-test standalone (`python simulation/<module>.py`).

## Legendary-investor persona roster (debate Step 1)

A domain layer on the debate engine (`simulation/personas.py`; LLM prompts in
`skills/multi_round_debate/personas/`). Five structured voices, one unified JSON
schema (thesis · key_risks · macro_linkage · suggested_hedge_or_protection ·
position_sizing_view · confidence · regime_view · dotcom_parallel · interaction_note):

| Persona | Voice | Risk-off? |
|---|---|---|
| Buffett_Agent | margin of safety; cash as a call option | yes |
| Burry_Agent | deep contrarian; asymmetric defined-risk shorts (no naked shorts) | yes |
| Dalio_Agent | economic machine; debt cycle; all-weather; "don't panic-sell a bubble" | yes |
| Soros_Agent | reflexivity; bold but timed participation | no |
| TailRisk_Hedger_Agent | portfolio insurance; cap MaxDD | yes (hedger) |

**High-valuation forced-hedge rule** ([[../CLAUDE]] §10): when Buffett Indicator
> 200% **or** the Dalio bubble flag is set, the debate force-injects the TailRisk
hedger + a risk-off voice, and the Verifier (Risk Officer seat) **vetoes any
risk-adding consensus that lacks an explicit hedge**. Verified end-to-end: in a
stretched tape (Buffett Indicator 225%, bubble flag on) the roster reaches a
**defensive consensus — stand down on new risk, carry the mandated hedges**,
`risk_flags=[high_valuation, hedge_mandatory]`; a lone-bull roster gets the hedger
force-injected back in. Personas are recommend-only (`proposed_actions` always
empty). Context (Buffett Indicator, bubble flag, yields) will be fed by the
Step-2 Macro Sentinel (TODO); today it is passed in / synthetic.

## Live result — real-universe competition (2026-06-13)

First run on REAL lake prices (not synthetic): `simulation/universe_competition.py`
ran 6 trader genomes over a 130-name FOM-screened universe + the SpaceX sleeve,
window 2026-02-04..2026-06-12 (90 trading days), PIT, `llm_involvement=none`.
Artifact: `outputs/trading-society-competition-2026-06-13.json`.

| # | trader | fitness | return* | Sharpe | maxDD | win |
|---|---|---|---|---|---|---|
| 1 | MEAN_REVERSION | 0.717 | +1.02 | 2.96 | -0.17 | 0.51 |
| 2 | REVERSION_FAST | 0.694 | +0.73 | 2.46 | -0.21 | 0.52 |
| 3 | MOMENTUM_FAST | 0.279 | -0.50 | -2.04 | -0.57 | 0.49 |
| 4 | BREAKOUT_HUNTER | 0.276 | -0.60 | -2.96 | -0.61 | 0.49 |
| 5 | MOMENTUM_SWING | 0.276 | -0.64 | -4.03 | -0.66 | 0.43 |
| 6 | TREND_RIDER | 0.275 | -0.64 | -3.57 | -0.68 | 0.46 |

**Finding:** over this window mean-reversion (fade dips) decisively beat momentum
(chase breakouts); every momentum trader lost. **`*` Magnitudes are NOT realistic
P&L** — no transaction costs, no slippage, no position sizing, naive next-bar
scoring, 267 trades. The numbers **rank** traders relative to each other; they do
not promise returns. Adding costs/sizing is the next refinement.

**Internal tension (the whole point of a society):** the backtest champion is a
dip-buyer whose "today" picks (DXYZ/ASTS/RKLB — beaten-down space names) are
exactly the falling-knife behavior the persona Risk-Officer layer flags as
dangerous in a high-valuation regime (dot-com analog). The human + Risk Officer
adjudicate between the empirical champion and the defensive persona consensus.

### SpaceX handling (private)

SpaceX is **private — no ticker, no price; monitor-only** (honors
`watchlist/spacex_ipo_2026_event.md`). The society trades the SpaceX **theme** via
public proxies in the lake: **DXYZ** (Destiny Tech100 NAV proxy, fetched
2026-06-13), **RKLB** (purest launch comparable), ASTS / PL / LUNR / STRL / IRDM /
GSAT, and LMT / NOC / BA. No SpaceX price is ever fabricated.

## grok2.md integration — real data sources + regime guardrails (溶入憲法)

**Data-source probe (2026-06-14):** which sources can actually fetch?

| source | status | what it gives the society |
|---|---|---|
| **FRED** | ✅ live | macro composite (credit/curve/VIX/M2/liquidity) + **real Buffett Indicator** = NCBEILQ027S / GDP ≈ **218.5%** (`simulation/macro_risk.py`); ALFRED `vintage_date` for true PIT |
| **Finviz Elite** | ✅ live (key OK) | **real industry sectors** for the concentration cap (NVDA→Semiconductors, KLAC→Semiconductor Equipment, LMT→Aerospace & Defense) + valuation (median P/E 25.4) (`simulation/finviz_data.py`) |
| **Polygon** | ✅ prices; ⚠ capex | prices fine; free-tier financials have **no capex line item** for many names → capex stays a flagged proxy (`simulation/capex_provider.py`) |
| **Finnhub** | ❌ | key is an empty placeholder in `.env` |

The portfolio now runs on real data: real Buffett Indicator 218.5, 6 live FRED
series, and the sector cap binds on **real Finviz industries** (Semiconductor
Equipment & Materials capped at exactly 35%, separate from Semiconductors at 9%).

**Regime guardrails** (`simulation/regime_filter.py`, governed by [[../CLAUDE]] §10):
grok2.md's `evaluate_market_regime()` + the Regime_Filter hard cases —

- **HARD_DEFENSE** (liquidity draining + gold > BTC): small-cap allocation cap = 0,
  defensive floor ≥60%, strict winsorization.
- **PARADIGM_BREAKTHROUGH** (capex > 25% + risk appetite): **Momentum Decoupling
  Lock** — reverse-shorts on AI leaders (NVDA/SMCI/AVGO/ASML/TSM/ORCL) blocked
  (anti-Gamma-squeeze).
- **MEAN_REVERSION** otherwise; valuation floor still applies.

Plus the **3 Ground-Truth invariants** (small-cap right-to-zero truncation;
sovereign/geopolitical-immunity guardrail; paradigm-squeeze short-block) and the
**century regime matrix 1900-2026** (`simulation/data/century_regimes.json`,
Grade-D reference). The live regime today classifies **MEAN_REVERSION** (liquidity
not draining, capex strong but BTC/gold neutral).

## Stage 1 — historical competition: Risk Officer as a trader (2018–2026)

`simulation/historical_competition.py` runs 7 traders — including a **RISK_OFFICER
that competes as an equal** (holds cash when breadth is negative, else a defensive
basket; no veto powers here) — over real lake prices. Weekly/monthly champions use
daily data (2021-06→2026-06); quarterly leaders/laggards + accuracy use monthly
data (2018→2026). Answer key = your grok.md quarterly matrix
(`simulation/data/quarterly_benchmark_2018_2026.json`, Grade-D, **post-hoc grading
only — never a trader input**). Artifact: `outputs/trading-society-history-*.json`.

**Champion wins (who won the most periods):**

| trader | weekly (~260) | monthly (~60) | quarterly (34) |
|---|---|---|---|
| MEAN_REVERSION | 56 | **15** | 3 |
| REVERSION_FAST | **58** | 8 | 5 |
| MOMENTUM_FAST | 45 | 13 | 5 |
| MOMENTUM_SWING | 41 | 9 | **9** |
| TREND_RIDER | 32 | 7 | 6 |
| BREAKOUT_HUNTER | 28 | 9 | 6 |
| RISK_OFFICER | 1 | 0 | 0 |

**Accuracy (caught quarter leaders / avoided laggards / hit your answer-key leader):**

| trader | catch | avoid | answer-key | 
|---|---|---|---|
| MOMENTUM_FAST | 0.235 | 0.871 | **0.235** |
| BREAKOUT_HUNTER | 0.235 | 0.871 | **0.235** |
| TREND_RIDER | 0.228 | 0.879 | 0.118 |
| MOMENTUM_SWING | **0.246** | 0.868 | 0.088 |
| MEAN_REVERSION | 0.162 | 0.846 | 0.059 |
| REVERSION_FAST | 0.169 | 0.860 | 0.000 |
| RISK_OFFICER | 0.007 | **0.989** | 0.029 |

**Findings (all honest, all from real prices):**
1. **Horizon split:** reversion wins the most *weeks* (short-horizon edge);
   momentum wins the most *quarters* (long-horizon edge). Different traders own
   different time frames — exactly the niche design.
2. **Momentum catches the legends:** MOMENTUM_FAST / BREAKOUT_HUNTER hit your
   answer-key leader (NVDA/MSFT/AAPL/TSLA...) 23.5% of quarters — best at
   "catching" the big names; reversion barely does.
3. **The Risk Officer did NOT win** (1 week, 0 months, 0 quarters) — because the
   other traders can *short* and profit in downturns, so pure cash/defense rarely
   tops them. But it has by far the **highest laggard-avoidance (0.989)** — it
   almost never holds the losers. So defense's value here is **risk reduction, not
   leaderboard wins** — and now we can *see* that instead of assuming it.
4. **Evolution adjustment (human-gated):** the engine reflects on the weakest
   trader (REVERSION_FAST, weak answer-key hit) and proposes a regime filter.

Caveat unchanged: returns are **relative rankings, not realistic P&L** (no costs /
slippage / sizing). Recommend-only; the canonical 10-signal pipeline + Risk-Officer
gate remain the authority.

## 3-layer competition framework (short-term + 10-year)

Full design: `programs/trading_society/COMPETITION_FRAMEWORK.md`. Three layers, all
recommend-only:

- **Layer 1 — short-term allocation** (`simulation/layer1_allocation.py`): turns the
  14-trader vote into a next-quarter allocation with **NEW / HOLD / TRIM** lists
  (diffed vs the prior run), **core (large-cap, 80%) + satellite (small-cap, 20%)**
  split, position caps (core ≤12%, satellite ≤6%, sector ≤35%), and the §10 hedge
  floor. First run (2026 Q3, MEAN_REVERSION, BI 218.5%, 35% defensive): core ≈
  ROKU/AMKR/ARM/FORM + semicap; satellite = RDW/AI/SEDG/SG (Small Cap Hunter);
  defensive = 19.5% cash + KO/PG/JNJ/LMT/NOC/RTX. Chinese readout →
  `outputs/layer1-allocation-*.md` (UTF-8).
- **Layer 2 — mid-term evolving competition** (`competition_2018_2026.py`): the
  2018-2026 long-horizon competition (above). Optimization TODO: per-quarter reset,
  risk-adjusted fitness, cross-style fairness.
- **Layer 3 — 10-year potential** (`simulation/layer3_potential.py`): a 0-100,
  7-dimension scorecard (industry trend 25% · **moat 20% real via
  `fom.IP_DEFENSIBILITY`** · capital-allocation 15% *proxy* · FCF 15% *proxy* ·
  **valuation 10% real Finviz P/E** · management 10% *proxy* · geopolitical 5%
  curated). Top-30 today: **MSFT 71.8, NOC, NVDA, TSM, ASML, LMT, QCOM, GOOGL,
  RTX, CRM...** (mega-cap tech + defense + semis), each tagged `core_long_term`
  vs `high_growth_high_risk`. Honest: 3 of 7 dimensions are neutral proxies pending
  real financials.

## 2018–2026 evolving competition + 2026 H2 forecast

`simulation/competition_2018_2026.py` runs a **long-horizon, low-frequency** roster
(monthly rebalance, ≤3 names held → well under 3 trades/week) over real monthly lake
prices 2018-2026 (34 quarters, 582 names, 10bps cost, **long-only**). Each quarter the
**two persistently weakest** traders (worst trailing-4Q) **evolve** (genome
lookback/threshold mutation, kept long-horizon: lookback ≥ 2 months). Artifact:
`outputs/trading-society-2018-2026-*.json`.

**Cumulative leaderboard 2018-2026** (relative ranking, NOT real P&L):

| # | trader | cum (×) | qtrs won | final genome |
|---|---|---|---|---|
| 1 | LT_BREAKOUT | +121.4 | 5 | momentum lb3 th0.08 |
| 2 | LT_MOMENTUM | +74.8 | 5 | momentum lb2 th0.16 |
| 3 | LT_BALANCED | +61.9 | 4 | momentum lb4 th0.12 |
| 4 | LT_TREND | +53.4 | **9** | momentum lb10 th0.13 |
| 5 | LT_REVERSION | +14.1 | 6 | reversion lb5 th0.10 |
| 6 | RISK_OFFICER | +0.47 | 5 | defensive |
| 7 | LT_DEEPVALUE | −0.04 | 0 | reversion lb2 th0.36 |

**Findings:** momentum dominates the 2018-2026 (AI-bull) era — top 4 are all
momentum. LT_TREND won the most quarters (9, the steady winner) but compounds 4th;
LT_BREAKOUT compounds highest. **RISK_OFFICER won 5 quarters** (the down quarters:
2018Q4 / 2020Q1 / 2022) but lags cumulatively in a bull regime — defense's value is
crash-quarter survival, not the trophy. Deep-value reversion was worst (era-specific).

**Methodology honesty:** the first run had broken cumulative math (short positions can
lose >100% → negative equity → −587% garbage). Fixed to **long-only** (equity stays
≥0) + long-horizon evolution bounds. Magnitudes are still **relative rankings**, not
achievable P&L (top-3 concentrated, no realistic sizing).

### 2026 H2 forecast (recommend-only)

The evolutionary champion **LT_BREAKOUT** (momentum, lb3) applied to the latest bar →
**KLAC, MXL, ALAB, VSH, VPG, MU, MRVL, CRDO** — a coherent semiconductor/semicap
breakout list. **Live regime = MEAN_REVERSION, high-valuation → the 35% defensive
floor still binds** (CLAUDE §10). The society's internal tension persists: the
momentum champion says "buy the semis," the hedge layer says "these are the crowded
AI names — carry 35% defense." Human + Risk-Officer adjudicate; not a capital order.

## Phase 1 specialists — 14-trader roster (grok2.md)

The two highest-value Phase-1 traders from the grok2.md roster are live
(`simulation/specialist_traders.py`; full roster + weight architecture in
`programs/trading_society/TRADER_ROSTER.md`). Deterministic 0-100 scorecards;
recommend-only; picks join the society vote (base weight × regime tilt) under the
regime guardrail + concentration caps + Risk-Officer gate.

- **Small Cap Catalyst Hunter** — gate: real Finviz market cap < $12B; scores
  market-cap / low-base / breakout / catalyst-acceleration. **Fills the "not only
  large caps" gap** — surfaces names the large-cap momentum traders never would.
  Live: **RDW 90.7** (Redwire, space, $3.6B), **AI (C3.ai) 86.4**, SEDG 80.3, SG,
  MOV. Sizing 5/3/2% by score band.
- **Power & AI Infrastructure Trader** — gate: AI power/grid/cooling/advanced-
  packaging sleeve; scores 3m trend / relative strength / persistence. Live:
  **KLAC 88.3, UCTT 85.6 (+98% 3m)**, NVMI, ICHR, ONTO, CRDO. Sizing 6/4/2.5%.

Regime tilt for specialists: HARD_DEFENSE → SmallCap ×0.2 (right-to-zero), AI-Infra
×0.5; PARADIGM_BREAKTHROUGH → ×1.6 / ×1.7.

**Roster expansion (now 7 specialists + 7 core = 14 voting traders):** added
**Value & Quality Compounders** (cheap large-cap P/E + low drawdown; live FDX/TRGP),
**Defense & Geopolitical** (defense/space sleeve; IRDM/GSAT), **Biotech & Healthcare**
(LLY/HUM 96/GH), **Nancy Pelosi Tracker** (Grade-D curated public-disclosure
holdings + momentum; PANW/CRWD), **Elon Musk Ecosystem** (Grade-D; TSLA + SpaceX
proxies — no picks today, no forcing). Each has a scorecard + regime tilt; all are
**long-only**.

**Long-bias / shorting rule (principal directive, CLAUDE §10).** The society is
long-biased by default; **shorts are permitted only in a confirmed bear regime**
(HARD_DEFENSE — trailing-6m median market return < −8%, PIT; the 2022/COVID analog).
In the 2018-2026 sim, exactly **8 bear months** lit up (2018-12, 2020-03,
2022-04→07) — precisely the 2018Q4 / COVID / 2022 bears. Per-name short loss capped
at −100% (stop). Enabling bear-shorts lifted the momentum champions
(LT_BREAKOUT +231×) without the earlier negative-equity blowups.

## Stage 2 — forward portfolio (society weighted vote + dynamic hedge)

`simulation/portfolio_generator.py` builds a **next-month** and **next-quarter**
portfolio via the principal-chosen flow: whole-society weighted vote (champion-
boosted) → Macro + Capex scores → dynamic defensive leg → Risk-Officer hedge
floor. `llm_involvement=none`; recommend-only; artifact
`outputs/trading-society-portfolio-*.json`.

8-step method: (1) each trader's current longs from lake PIT prices → (2) recent
risk-adjusted fitness → base weights → (3) champion boost (recent top ~30% ×1.40)
→ (4) **Macro Risk Environment Score** (0-100) → (5) **Capex Momentum Score**
(0-100) → (6) Macro+Capex → **dynamic defensive-leg ratio** → (7) Risk-Officer
review (high-valuation floor ≥35%, CLAUDE §10) → (8) core growth leg + defensive leg.

**First run (as_of 2026-06-12):** Macro risk **97.5/100** (BI 225, bubble on) →
posture **risk_off**, defensive **35%** (high-valuation floor enforced) / growth
**65%**. Champion-boosted: BREAKOUT_HUNTER + MOMENTUM_SWING/FAST. Core growth leg
concentrated in semi-cap equipment + ARM/ROKU (KLAC, ONTO, UCTT, ICHR, FORM,
AMKR, backed by 3-4 traders each). Defensive leg: ~17.5% cash + KO/PG/JNJ/LMT/
NOC/RTX. Walk-forward verification is a **periodic health check**, not every run.

### Stage 2 data-quality upgrade (review B/A/C)

After a cross-review flagged the synthetic inputs, the three weakest links were
wired to real data / real controls:

- **B — real PIT Macro** (`simulation/macro_risk.py`): a transparent 0-100
  composite of **live FRED** credit spread (HY OAS), yield curve, VIX, M2 growth,
  net-liquidity, and valuation; per-series never-raise fallback; ALFRED
  `vintage_date` for true PIT. **Finding:** real macro reads **~31/100 (risk_on)** —
  credit spreads are *tight* (HY OAS 2.78%), M2 *expanding*, liquidity growing —
  the opposite of the old synthetic 97.5. Only **valuation** is extreme, so the
  §10 high-valuation floor (35%) is what forces the hedge, not the plumbing. A
  clean demonstration that valuation discipline holds even in a calm-credit tape.
- **A — real Capex 1st/2nd derivative** (`simulation/capex_provider.py`): capex
  growth (YoY) + acceleration from **polygon cash-flow statements**, PIT via
  `filing_date`, cached; falls back to a flagged price-momentum proxy only when no
  cache / `POLYGON_API_KEY`. `--refresh` populates the real sleeve.
- **C — concentration caps + costs** (`portfolio_generator.py`): single-name
  **≤10%**, single-sector **≤35%** (ai_semis was ~50%, now capped at exactly 35%),
  **10bps** round-trip cost charged in the fitness backtests, and cap-clipped
  weight routed to cash (defensive cash 17.5% → ~26%).

Remaining honest flags: valuation (Buffett Indicator) is still an override input
(no clean free FRED source); real capex needs a polygon key (else proxy). Macro
live-series count varies per run (FRED can time out → flagged fallback).
Recommend-only; promotion needs human + Risk-Officer gate + cross-review.

## Evolution + competition (演化 + 競賽)

- `simulation/strategy_agent.py` — parameterized genome (lookback, entry_threshold,
  momentum_tilt, ...) so mutation actually changes backtest behavior.
- `simulation/tournament.py` — cross-regime competition (bull/bear/chop); ranks by
  a blend of average AND **worst-regime** fitness (worst-regime is half the score)
  to penalize curve-fitting.
- `simulation/evolution/evolution_engine.py` — generational loop: compete → select
  elites → reflection-mutate the worst → breed offspring → novelty-inject empty
  niches → next generation → evolution log. Multi-regime mandatory; every promotion
  human-gated. Demo: an offspring lifted the champion 0.630 → 0.683 across 3 gens.
- `simulation/macro_data_provider.py` (Step 2) — Macro Sentinel feeding
  `MarketContext` (Buffett Indicator, bubble flag, yields, net-liquidity proxy,
  TW/US spread); synthetic default, optional FRED (never-raise), PIT-flagged.

## Fitness (multi-dimensional, anti curve-fit)

`performance_tracker.compute_fitness` blends: risk-adjusted return (Calmar/Sortino)
· **regime stability** (penalizes single-regime fitting) · drawdown control · hit
quality (win × payoff) · turnover discipline (action-budget) · niche purity.
Horizon tilts (weekly/monthly/yearly) live in `ranking_system.HORIZON_WEIGHTS`.

## Governance (binds; see [[../CLAUDE]] §10)

- **PIT everywhere.** Backtest slices price history to `<= as_of` before any
  decision call — lookahead is structurally impossible for price inputs.
- **LLM-backtest protocol** (`docs/LLM-BACKTEST-PROTOCOL.md`) enforced in code:
  `llm_involvement` marker, banned-key rejection on LLM-involved historical runs,
  walk-forward gating, RAG `before_as_of`. Only `none`/`narration_only` → KPI.
- **~10 actions / simulated society-day**; no padding (unfilled → `null`/`no_action`).
- **Niche protection + novelty injection** to avoid 大者恆大.
- **Human is the final selector**; Risk-Officer veto is supreme inside debate.
- **Research only** — no writes to `outputs/picks-*` or `wiki/05_recommendations/*`.

## Honest limits / open work

- All numbers to date are **synthetic** self-tests. Real validation needs PIT
  prices from the data lake; the 1980–2026 benchmark list in `grok.md` is a
  Grade-D seed requiring fresh PIT reconstruction + survivorship handling
  (the repo already has hard lessons on delisted-name availability — see
  `wiki/log.md` 2026-06-12).
- Debate/ranking/reflection/mutation are deterministic **skeletons**; wiring real
  role LLMs flips `llm_involvement` and triggers the walk-forward gate.
- Phase-3 `EvolutionEngine` (full monthly cycle + multi-regime re-test) is TODO;
  only the base mutator + feeders are shipped.

## See also

- [[../CLAUDE]] §10 — governance binding for this layer
- [[25_cross_tool_agent_orchestration]] — driving Grok/other tools as reviewers
- [[11_adaptive_loop]] — the FOM self-improvement loop (sibling idea, production side)
- [[03_alpha_library]] — historical case calibration (a PIT-honest data source)
