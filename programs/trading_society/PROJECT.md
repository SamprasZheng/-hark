---
type: research
title: Trading Society — PROJECT definition & PPST decomposition
as_of_timestamp: 2026-06-13T18:00:00+08:00
author_role: orchestrator
tags: [trading-society, ppst, multi-agent, debate, evolution, backtest, governance]
status: draft
source_paths:
  - grok.md (debate patterns, multi-round debate guide, PPST application examples, 1980-2026 benchmark list)
  - wiki/25_cross_tool_agent_orchestration.md
  - analysts/README.md + _TEMPLATE.md (existing persona council)
  - docs/LLM-BACKTEST-PROTOCOL.md
  - backtest/README.md
  - CLAUDE.md / AGENTS.md / RISK_OFFICER_SLA.md
---

# Trading Society (矽基交易社會) — PROJECT

**Core Goal** (per user plan digested): Build multiple AI traders/analysts with distinct strategies and time frequencies. They improve via competition, multi-round debate, reflection, and controlled evolution. Final selection of "winners" remains with human. All validation uses historical data under strict point-in-time (PIT) rules. Performance must be measurable and stable across regimes.

**Alignment to $hark governance**:
- Extends the existing analyst-persona council (`analysts/`) and council/debate patterns already sketched in `grok.md`.
- Every artifact carries `as_of_timestamp` and `author_role`.
- **Never** produces or bypasses the canonical 10-signal contract (`outputs/picks-*.json`, `wiki/05_recommendations/*`). Society outputs may inform research or (after human choice + Risk Officer gate + cross-review) feed watchlist-style signals only.
- **No trades**, no keys, recommendations only.
- Raw/ immutable. Any benchmark data used for validation must be dated raw/ or data/lake PIT extracts; the 1980-2026 leading/lagging names list already exists inside `grok.md` (user prior query) — treat as Grade-D research seed, not executable universe without fresh PIT price/volume reconstruction.

## PPST Declaration for this work block
- **PROJECT**: Trading Society (this document)
- **PROGRAM**: programs/trading_society/* (definition + role specs) + initial simulation/ and agents/ skeletons
- **SKILL**: PPST decomposition + multi-round-debate (seeded) + persona/role design (extending analysts/ template)
- **TARGET**: Explicit 4-Program mapping of the 4 user phases + 6-8 core agent role definitions (A + E immediate deliverables). All future work must hand off via [CALL SKILL] with the four layers.

## Phase → PROGRAM Mapping (user plan refined to repo realities)

| User Phase | PROGRAM name                  | Primary artifacts (initial)                  | Key constraints from existing repo |
|------------|-------------------------------|----------------------------------------------|------------------------------------|
| Phase 0 (highest priority) | Backtest / Simulation Program | `simulation/backtest_runner.py` (skeleton), `simulation/performance_tracker.py`, regime-aware harness, explicit LLM-BACKTEST-PROTOCOL compliance | Must obey `docs/LLM-BACKTEST-PROTOCOL.md` (banned keys: probability/direction/verdict/signal/score etc on historical windows; walk-forward post model-cutoff; `llm_involvement` marker; RAG `before_as_of`; only `none`/`narration_only` eligible for headline KPIs). "daily max 10 trades" global limit. Use existing `src/sharks/backtest/*` + `data/lake` where possible instead of duplicating. 1980-2026 benchmark requires PIT reconstruction. |
| Phase 1 | Debate Program               | `programs/debate/DEBATE_PROGRAM.md` (adapt from grok.md sketches), `skills/multi_round_debate/SKILL.md` | 2-4 round max; structured JSON messages; Proposer/Critic/Verifier/Synthesizer roles; terminate on consensus or max rounds or Verifier veto. Ties to existing `src/sharks/discord/council.py` patterns. |
| Phase 2 | Ranking + Reflection Program | `simulation/ranking_system.py`, `simulation/reflection_engine.py` | Multi-horizon (Weekly/Monthly/Yearly); Fitness = multi-dim (risk-adj return, regime stability, turnover penalty, drawdown control). Reflection produces structured "adjustment proposal" (prompt delta or param delta) for later Mutation. |
| Phase 3 | Evolution Program            | `programs/evolution/EVOLUTION_PROGRAM.md`, `simulation/evolution/mutator.py` (base) | Selection + Mutation + occasional random new Agent injection (avoid "大者恆大"). Function evolution (new indicators/logic) only after strong evidence. Multi-regime evaluation mandatory. Human gate on promotion to "active" status for any capital-facing use. Monthly cadence initially. |

**Cross-cutting Society Layer** (not a separate Program):
- Performance tracking & ranking (inside Ranking Program)
- Reflection + controlled mutation (Phase 2/3)
- Niche protection + periodic novelty injection (explicit in roles + evolution)
- Human final selector ("優勝者" adoption)

## Immediate Execution Choice (user query A-E)
**Selected: A + E (primary)**  
Rationale (after digesting grok.md + repo state):
- A (6-8 core Agent roles + prompts + model allocation) is the highest-leverage first deliverable. Roles are prerequisite for any debate, ranking, or backtest. Existing `analysts/` provides a proven persona frontmatter + loading pattern to adapt (or keep separate "trader" vs "analyst" tracks). Roles encode time-frequency specialization and ecological niches from day 1.
- E (overall main flow Python architecture) is delivered here as this PROJECT.md + a minimal runnable `simulation/society_orchestrator.py` stub that demonstrates PPST declaration, role loading, and phase routing without producing any numbers or signals.
- B (full backtest framework + Performance Tracker) is deferred as secondary: the protocol and existing `src/sharks/backtest/` + lake make a naive "let 8 agents trade 1980-2025 history" both polluting and duplicative. First skeleton only after roles + protocol plumbing.
- C (multi-round debate) is ~70% pre-specified in `grok.md` ("多輪辯論機制實作指南", Debate Program / multi_round_debate Skill sections, message schema, state machine, PPST call examples). We adapt rather than duplicate.
- D (Ranking + Reflection) follows A + a data model for agent run logs; cannot be designed in vacuum.

**Next handoff after this TARGET**: Writer (or self) will implement one concrete PROGRAM (likely Debate Program skeleton or the Backtest Program compliance layer) via explicit [CALL SKILL] with full four layers + minimal CONTEXT. No write to `outputs/`, `wiki/05_recommendations/`, or `wiki/positions.md` without Risk Officer gate.

## Global Hard Constraints (P0, never relax)
- Point-in-time everywhere (CLAUDE §2). No as_of-later data in earlier analysis.
- LLM backtest pollution defenses mandatory (see docs/LLM-BACKTEST-PROTOCOL.md full text).
- Max ~10 discrete "actions" per simulated day across the entire society (aligns with canonical 10-signal spirit; prevents over-trading in sim).
- Grade D/E (KOL, social, pure LLM opinion) informs watch/monitor only; never standalone position or sizing.
- All society artifacts start as research (tech/ or programs/ or simulation/); promotion path to production signals requires human sign-off + Risk Officer review + cross-model review (AGENTS §3).
- No fabrication of tickers/prices/dates. Use TBD + follow-up log when needed.
- Ecological niches protected: each core agent owns a distinct (freq × edge) slot. New agents must justify unoccupied niche or retire an underperformer.

## Data & Provenance Note
The user plan references "你提供的歷史 benchmark（1980~2026 領漲領跌股票）". This list (decade-by-decade, large/small-cap separated, leading/lagging exemplars) is already present inside `grok.md` (search for "1980 ~2026 的領漲領跌代表性股票"). It is a prior Grade-D synthesis. Any backtest runner must:
- Reconstruct actual PIT prices/volumes from data/lake or fresh dated raw/ for those names.
- Declare the as_of of the benchmark list itself.
- Never treat the names as a fixed tradable universe without survivorship / delisting handling (repo already has hard lessons on delisted names in 2026-06-12 log entries).

## Success Criteria for the overall PROJECT
- 6-8 roles defined with executable prompt templates and model routing.
- At least one end-to-end (simulated) cycle through Debate → Rank → (optional) Reflect that produces structured, reviewable artifacts.
- All backtest-involved runs carry correct `llm_involvement` + obey protocol.
- Human-readable evolution log showing at least one controlled mutation + niche injection.
- Zero P0 governance violations in any artifact that could later touch capital decisions.

**End of PROJECT declaration. All subsequent work blocks must restate the four layers and stay inside declared PROGRAM.**
