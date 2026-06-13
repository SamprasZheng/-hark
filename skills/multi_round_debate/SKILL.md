---
name: multi_round_debate
version: 0.1.0
type: skill
tags: [trading-society, debate, consensus, verifier, ppst]
description: Run a bounded multi-round structured debate (Proposer/Critic/Verifier/Synthesizer) that turns independent role proposals into one reviewed, confidence-scored synthesis or an explicit no-consensus.
---

# multi_round_debate

## Purpose

Reduce single-agent hallucination/bias by forcing N independent proposals
through adversarial critique + an independent verifier before synthesis. Output
is a **research** artifact, never a direct capital recommendation.

## Inputs (beyond standard PPST layers)

- `topic`: the question under debate (one falsifiable decision).
- `as_of`: the simulated decision timestamp (PIT). All evidence must be `<= as_of`.
- `proposals`: list of initial role proposals (from CORE_AGENT_ROLES members),
  each a structured dict with `from_agent`, `content`, `evidence`, `confidence`,
  `stance`.
- `max_rounds` (optional): 3 default, 4 for high-risk; never 5 for capital topics.
- `llm_involvement` (optional): one of {none, narration_only, decision_input,
  decision_output}; default `none`. Non-`none` triggers protocol checks.
- `personas` (optional): use the legendary-investor roster (`simulation/personas.py`,
  prompts in `personas/`) as proposers. In a **high-valuation regime** (Buffett
  Indicator > 200% or Dalio bubble flag) the TailRisk hedger + a risk-off voice
  are force-injected and the Verifier vetoes any hedge-less risk-adding consensus
  (CLAUDE.md sec.10; DEBATE_PROGRAM.md sec.6b). Entry: `run_persona_debate(ctx)`.

## Expected Output

A single structured `synthesis` object plus the full message transcript:

```json
{
  "debate_id": "debate-YYYY-MM-DD-NNN",
  "consensus": "reached | partial | none",
  "final_view": "structured, falsifiable, no marketing language",
  "proposed_actions": [],
  "no_action_buckets": ["long_new", "short_new"],
  "confidence": 0.0,
  "risk_flags": [],
  "verifier_veto": false,
  "rounds_used": 2,
  "llm_involvement": "none",
  "transcript": [ /* all messages, schema in DEBATE_PROGRAM.md sec.4 */ ]
}
```

## Constraints and Invariants

- **PIT**: every message declares `as_of_timestamp`; evidence `<= as_of`.
- **Bounded**: stop on consensus (>= 2/3 proposers concur, no open high-severity
  challenge), max_rounds, Verifier veto, or two no-progress rounds.
- **Verifier = Risk Officer seat**: its veto forces `consensus="none"` and is
  never overridden by majority.
- **No padding**: unfilled action slots are `null` / listed in `no_action_buckets`.
- **Grade D/E** evidence informs a watch bucket only -- never opens/sizes.
- **Backtest path**: obey `docs/LLM-BACKTEST-PROTOCOL.md` -- no banned keys on
  historical periods, carry `llm_involvement`, RAG `before_as_of = as_of`.
- Must NOT write to `outputs/picks-*` or `wiki/05_recommendations/*`. Promotion
  to a signal requires human selection + Risk Officer gate + cross-review.

## Failure Modes

- Insufficient/late evidence -> Verifier marks `TBD`, debate ends `consensus=none`
  with a follow-up note (no fabrication).
- Proposers deadlock -> max_rounds fires; synthesis reports `partial`/`none` with
  the open contradictions, not a forced answer.
- Banned key under a non-`none` run -> the engine raises before synthesis.

## Examples

### Good Invocation

```
[CALL SKILL]
PROJECT: Trading Society
PROGRAM: simulation/debate_engine.py
SKILL: multi_round_debate
TARGET: 3-round debate: "add a long_new today?" PIT as_of=2026-06-13. Output a
        structured synthesis (<=2 actions or no_action), confidence, risk_flags.
```

### Expected Good Output

A `synthesis` with `consensus`, `proposed_actions` (possibly `[]`),
`no_action_buckets`, `confidence`, `verifier_veto`, and the full transcript.

### Bad Invocation (common mistake)

Passing `proposals` whose evidence postdates `as_of` (lookahead), or expecting
the skill to "place" a trade. The skill only produces reviewed research.

## Implementation Notes (for the skill author)

- Reference impl: `simulation/debate_engine.py` (deterministic stubs by default,
  `llm_involvement="none"`; pluggable callables for real role LLMs).
- Default agents are pure rules so the skill is runnable and testable offline.
- Versioning: bump `version` on schema changes; keep `DEBATE_PROGRAM.md` in sync.
