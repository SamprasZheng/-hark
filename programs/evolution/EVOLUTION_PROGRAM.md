---
type: research
title: Evolution Program -- selection, mutation, niche protection (Phase 3)
as_of_timestamp: 2026-06-13T22:00:00+08:00
author_role: writer
tags: [trading-society, evolution, mutation, selection, niche, ppst, governance]
status: draft
related:
  - programs/trading_society/PROJECT.md
  - simulation/ranking_system.py
  - simulation/reflection_engine.py
  - simulation/evolution/mutator.py
  - docs/LLM-BACKTEST-PROTOCOL.md
---

# Evolution Program (Phase 3)

**PPST for this PROGRAM**
- PROJECT: Trading Society
- PROGRAM: programs/evolution/ (this doc) + simulation/evolution/* (impl)
- SKILL: agent_mutator + performance_evaluator + regime_detector
- TARGET: A monthly, human-gated evolution cycle: rank -> reflect -> mutate
  (candidate only) -> multi-regime re-backtest -> human selection. Protects
  ecological niches; never auto-promotes a candidate to capital-facing use.

This is the Phase-3 destination. Phase-2 ships the **base** mutator
(`simulation/evolution/mutator.py`) and the reflection/ranking that feed it.

---

## 1. Cycle (monthly cadence, all steps logged)

```
1. RANK       ranking_system -> weekly/monthly/yearly fitness + niche coverage
2. REFLECT    reflection_engine -> bottom-K structured adjustment proposals
3. MUTATE     mutator.apply_reflection -> CANDIDATE configs (active=false)
4. INJECT     mutator.propose_novelty_injection -> fill any empty niche
5. RE-TEST    backtest_runner across MULTIPLE regimes (not one window)
6. SELECT     human chooses what (if anything) graduates; Risk Officer gate
7. LOG        evolution log entry: lineage, deltas, regime results, decision
```

## 2. Selection rules (anti winner-take-all)

- **Niche protection.** Each declared (frequency x edge) niche keeps >= 1 agent.
  A mutation that would empty a niche is rejected; an empty niche triggers
  novelty injection (step 4).
- **Multi-regime gate.** A candidate only graduates if it improves (or holds)
  fitness across risk-on / risk-off / high-vol / transition buckets -- not just
  the recent window. Single-regime winners are curve-fit suspects.
- **Bounded, reversible mutations.** Deltas are clamped (`mutator.PARAM_BOUNDS`,
  `MAX_STEP`); lineage is recorded; any mutation can be rolled back.
- **Human final selector.** No candidate is "active" for capital-facing use
  without explicit human selection + Risk Officer sign-off. Evolution is
  assistive (CLAUDE.md sec.1-2, PROJECT.md success criteria).

## 3. Governance bindings

- **PIT + protocol.** Re-tests obey `docs/LLM-BACKTEST-PROTOCOL.md`; LLM-involved
  candidate runs are exploratory only (never headline KPIs) and declare a
  post-cutoff walk-forward window.
- **No fabrication.** Missing regime coverage -> `TBD` + a `wiki/log.md` note;
  never invent a result to justify a promotion.
- **Function evolution** (new indicators / selection logic) is allowed only after
  strong, multi-regime evidence and human review -- not as a default mutation.

## 4. Implementation status

- DONE (base): `simulation/evolution/mutator.py` -- bounded reversible mutation
  (`apply_reflection` + `mutate_random`) + niche-aware novelty injection,
  human-gated, deterministic.
- DONE (feeders): `simulation/ranking_system.py`, `simulation/reflection_engine.py`.
- DONE (substrate): `simulation/strategy_agent.py` -- parameterized genome so
  mutation changes backtest behavior; `simulation/tournament.py` -- cross-regime
  competition ranked by avg + worst-regime fitness.
- DONE (engine): `simulation/evolution/evolution_engine.py` -- the generational
  cycle (compete -> elites -> reflect-mutate worst -> breed -> novelty-inject ->
  evolution log). Multi-regime mandatory; promotion human-gated; nothing active.
- DONE (real run): `simulation/universe_competition.py` -- traders compete on the
  REAL FOM universe + SpaceX sleeve on lake PIT prices; ranked leaderboard.
- TODO: monthly schedule wiring; transaction-cost / position-sizing realism in the
  scorer; lineage diagrams in `wiki/`; FRED-vintage PIT macro for historical replay.

**End of Evolution Program design. All impl work restates the four PPST layers.**
