---
type: research
title: Debate Program -- multi-round structured debate for the Trading Society
as_of_timestamp: 2026-06-13T22:00:00+08:00
author_role: writer
tags: [trading-society, debate, consensus, ppst, multi-agent, governance]
status: draft
related:
  - programs/trading_society/PROJECT.md
  - programs/trading_society/CORE_AGENT_ROLES.md
  - skills/multi_round_debate/SKILL.md
  - simulation/debate_engine.py
  - grok.md (multi-round debate guide, lines ~5434-5912)
  - RISK_OFFICER_SLA.md
  - docs/LLM-BACKTEST-PROTOCOL.md
---

# Debate Program (Phase 1)

**PPST for this PROGRAM**
- PROJECT: Trading Society
- PROGRAM: programs/debate/ (this design doc) + simulation/debate_engine.py (impl)
- SKILL: multi_round_debate (skills/multi_round_debate/SKILL.md)
- TARGET: A bounded (2-4 round) structured debate that turns N independent role
  proposals into one reviewed, confidence-scored synthesis -- or an explicit
  "no consensus / no action" -- with a full message transcript. Never emits a
  capital recommendation directly; output is research that still passes through
  human selection + Risk Officer gate before any signal use.

This adapts the multi-round-debate design sketched in `grok.md` to $hark
governance. Where grok.md is generic, the binding rules below win.

---

## 1. Why debate (and its limits)

Multi-round structured debate is the most practical Byzantine-fault-tolerant
pattern for LLM agents: independent proposers + adversarial critics + an
independent verifier reduce single-model hallucination, anchoring, and drift.
It does **not** make the output tradeable. In $hark a debate result is, at best,
a better-reasoned research artifact. It inherits every P0 boundary in
`CLAUDE.md sec.2` and never short-circuits the 10-signal contract.

---

## 2. Roles (map to CORE_AGENT_ROLES + RISK_OFFICER_SLA)

| Debate role | Played by | Mandate | In debate |
|---|---|---|---|
| **Orchestrator** | society_orchestrator / Claude | starts/stops debate, advances rounds, decides termination | limited |
| **Proposer(s)** | tactical/strategic roles (MOMENTUM_SWING, MACRO_REGIME, VALUE_CONTRARIAN, ...) | put forward a position + evidence | primary |
| **Critic** | a different role than the proposer (often MEAN_REVERSION vs MOMENTUM, or OVERLAY_RISK) | attack the weakest link; name the target agent | primary |
| **Verifier** | Risk-Officer-flavored checker | fact/consistency/compliance check; can veto | primary, gatekeeper |
| **Synthesizer** | SYNTHESIZER role | merge the strongest coherent view; produce structured output | final |

The **Verifier carries the Risk Officer's veto** inside the debate: a veto sends
the debate to a forced "no_consensus" synthesis, it is never overridden by a
majority (mirrors `CLAUDE.md sec.1`, `RISK_OFFICER_SLA.md`).

---

## 3. State machine

```
S0 INIT          -> register topic, participants, max_rounds, as_of (PIT)
S1 PROPOSE       -> each Proposer emits a `proposal` message
S2 CHALLENGE     -> Critic emits `challenge` (must name to_agent)
S3 REBUTTAL      -> challenged agent emits `rebuttal`
S4 VERIFY        -> Verifier emits `verification` (consensus_reached?, veto?)
S5 DECIDE        -> consensus OR max_rounds OR veto? -> S6 ; else round++ -> S2
S6 SYNTHESIZE    -> Synthesizer emits `synthesis` (final structured output)
```

Termination (any one fires):
1. **Consensus** -- Verifier reports `consensus_reached: true` (>= 2/3 of
   proposers concur, no open high-severity challenge).
2. **Max rounds** -- general task 3, high-risk task up to 4 (we cap at 4; the
   grok.md "5" is reserved for non-capital research only).
3. **Verifier veto** -- forces a `no_consensus` synthesis with the veto reason.
4. **No-progress** -- two consecutive rounds with no new evidence -> stop.

---

## 4. Message schema (JSON; every message)

```json
{
  "debate_id": "debate-2026-06-13-001",
  "round": 2,
  "from_agent": "MEAN_REVERSION_SWING",
  "to_agent": "MOMENTUM_SWING",
  "message_type": "challenge",
  "as_of_timestamp": "2026-06-13",
  "content": "single, falsifiable point",
  "evidence": ["path or PIT datum <= as_of"],
  "severity": "low|medium|high",
  "confidence": 0.0,
  "stance": "support|oppose|neutral"
}
```

`message_type` in {`proposal`,`challenge`,`rebuttal`,`verification`,`synthesis`}.

The **final `synthesis`** message additionally carries:

```json
{
  "message_type": "synthesis",
  "consensus": "reached|partial|none",
  "final_view": "structured, falsifiable, no marketing language",
  "proposed_actions": [ /* <= society action budget; may be [] */ ],
  "no_action_buckets": ["long_new", "short_new", "..."],
  "confidence": 0.0,
  "risk_flags": [],
  "verifier_veto": false,
  "llm_involvement": "none|narration_only|decision_input|decision_output"
}
```

No padding: unfilled action slots are `null` / listed in `no_action_buckets`
(`CLAUDE.md sec.5`). Padding is a Verifier/Risk-Officer veto trigger.

---

## 5. Governance bindings (these override grok.md)

1. **PIT.** Every message declares `as_of_timestamp`; evidence must be data
   timestamped `<= as_of`. A debate replayed historically inside a backtest path
   obeys `docs/LLM-BACKTEST-PROTOCOL.md` -- agent outputs may not carry
   `probability/direction/verdict/target/forecast/signal/score`, the run carries
   an `llm_involvement` marker, and any RAG uses `before_as_of = as_of`.
2. **No trades / no padding / no fabrication** (`CLAUDE.md sec.2`). Missing data
   -> `TBD` + a `wiki/log.md` follow-up; never invent a ticker/price/date.
3. **Grade D/E** (KOL/social/pure model opinion) may inform a watch bucket only,
   never opens or sizes a position (`CLAUDE.md sec.4`).
4. **Risk Officer veto is supreme** inside the debate (Verifier seat).
5. **Output is research.** Promotion to any capital-facing signal needs human
   winner-selection + Risk Officer gate + cross-model review (`AGENTS.md sec.3`).

---

## 6. PPST handoff example

```
[CALL SKILL]
PROJECT: Trading Society
PROGRAM: programs/debate/ + simulation/debate_engine.py
SKILL: multi_round_debate
TARGET: 3-round debate on "does the society add a long_new today?" Inputs:
        today's role proposals (PIT as_of=2026-06-13). Output: structured
        synthesis with consensus level, <=2 proposed_actions or no_action,
        confidence, risk_flags. Verifier enforces PIT + no-padding + grade gate.
CONTEXT: proposals from MOMENTUM_SWING, MACRO_REGIME, VALUE_CONTRARIAN attached.
         llm_involvement="none" for this run (deterministic role stubs).
```

---

## 6b. Legendary-investor persona roster + forced-hedge rule

A domain layer on top of the generic engine (`simulation/personas.py`, prompts in
`skills/multi_round_debate/personas/`). Five structured investor voices, each
emitting the unified persona JSON schema (thesis, key_risks, macro_linkage,
suggested_hedge_or_protection, position_sizing_view, confidence, regime_view,
dotcom_parallel, interaction_note):

| Persona | Voice | Risk-off? |
|---|---|---|
| Buffett_Agent | margin of safety; cash as a call option | yes |
| Burry_Agent | deep contrarian; asymmetric defined-risk shorts | yes |
| Dalio_Agent | economic machine; debt cycle; all-weather | yes |
| Soros_Agent | reflexivity; bold but timed participation | no |
| TailRisk_Hedger_Agent | portfolio insurance; cap MaxDD | yes (hedger) |

**Forced-hedge rule (binding; CLAUDE.md sec.10).** In a high-valuation regime
(`MarketContext.high_valuation` = Buffett Indicator > 200% OR `dalio_bubble_flag`):

1. `enforce_roster()` force-injects `TailRisk_Hedger_Agent` and ensures at least
   one risk-off voice is present.
2. The Verifier (`make_persona_verifier`) **vetoes** any risk-adding consensus
   that lacks an explicit hedge, and requires a hedge voice for any consensus at
   all. Veto -> `consensus="none"` (never majority-overridden).
3. The Synthesizer surfaces the aggregated `mandated_hedges` and sets
   `risk_flags=["high_valuation","hedge_mandatory"]`.

Personas are **recommend-only**: `proposed_actions` stays empty; outputs are
transcript views, never ticker orders. Deterministic stubs keep
`llm_involvement="none"`; the `.md` prompts are used when a real LLM is wired
(which flips the marker and triggers the walk-forward gate).

Entry point: `personas.run_persona_debate(MarketContext, roster=None, max_rounds=3)`.

## 7. Implementation status

- `simulation/debate_engine.py` -- runnable engine: message schema, 2-4 round
  state machine, pluggable agent callables (default deterministic stubs, no LLM),
  consensus/veto/no-progress termination, structured synthesis + transcript.
- `skills/multi_round_debate/SKILL.md` -- the reusable skill contract.
- `simulation/personas.py` + `skills/multi_round_debate/personas/` -- the 5
  legendary-investor voices + the high-valuation forced-hedge rule (sec.6b).
- Future: wire real role LLMs (flips `llm_involvement`, triggers walk-forward
  gate); Discord council surface (`src/sharks/discord/`) for human-in-the-loop;
  reputation-weighting once the Ranking Program has history.

**End of Debate Program design. All impl work restates the four PPST layers.**
