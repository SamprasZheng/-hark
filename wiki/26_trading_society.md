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
