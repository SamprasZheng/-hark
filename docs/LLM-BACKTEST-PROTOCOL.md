# LLM-in-the-loop Backtest Pollution Protocol

> **Status: active runbook.** No LLM-involved historical backtest result is
> publishable (i.e. eligible for a headline KPI) without conforming to this
> document. Sourced from `philosophy/_proposals/ai-quant-us-roadmap-merge-2026-05-30.md`
> §11, which flagged this as the highest-priority foundational issue in the
> AI-Quant-US merge.

## The problem

Any LLM trained on data through 2024-2026 has read the post-mortems of 1929,
1937, 1973, 1987, 2000 (dotcom), 2008 (subprime), 2020 (covid). A backtest that
asks *"would the model have correctly classified the 1973 regime?"* is poisoned
by training-set lookahead: **the model is recalling, not predicting.**

This collides head-on with the macro-analog matching concept
(`philosophy/concepts/macro-analog-matching.md`, proposed): "the current state
most resembles 1973" may be true only because 1973's outcome is baked into the
model's weights, not because the model independently detected a 1973-like
pattern from point-in-time-honest inputs.

Why this matters more than any other ML detail: an unsolved pollution problem
makes every backtest *run-able but uninterpretable*. Sharpe and MDD will look
great because the model is silently leaking outcome information. The temptation
to ship on those numbers is exactly the failure this protocol exists to prevent.

## The five defenses (all mandatory)

### 1. Role restriction

The LLM may **generate hypotheses, build checklists, summarise mechanisms**. The
LLM may **NOT output probability or direction** on historical periods.

Enforcement: any LLM call invoked from a backtest path must return a structured
object whose schema **excludes** the keys `probability`, `direction`, `verdict`,
`target`, `forecast`, `signal`, `score`. The Risk Officer rejects any backtest
run whose LLM outputs contain a banned key.

```python
BANNED_LLM_BACKTEST_KEYS = {
    "probability", "direction", "verdict", "target", "forecast", "signal", "score",
}
# Raise if any banned key appears (recursively) in an LLM response used in a
# backtest path.
```

### 2. Walk-forward gating

An LLM-involved backtest is valid **only** on the time window strictly *after the
base model's training cutoff* AND on prompts not subsequently fine-tuned.

For DeepSeek-R1-Distill / Llama-3 / Qwen-7B this yields a usable window of months
to ~2 years — small, but honest. The backtest module README must declare:

- the base model + its training cutoff date,
- the resulting valid window,
- which runs fall outside it.

Runs outside the valid window are marked `cutoff_polluted: true` in the output
JSON and excluded from all headline KPI aggregation.

### 3. Non-LLM pre-cutoff baselines

For the 1929-2024 portion of any historical study the system uses **only**
deterministic, rule-based components:

- the FOM scorer (`src/sharks/scoring/fom.py`, Fix A + Fix D),
- the regime classifier (`src/sharks/regime/classifier.py`),
- the (to-be-built) funding-chain (`src/sharks/regime/funding_chain.py`) and
  macro-analog (`src/sharks/regime/macro_analog.py`) modules — which are
  themselves human-curated lookup tables, NOT learned LLM functions.

The LLM may *narrate* what these rule-based outputs imply, but the headline
numbers come from the deterministic scorers. Narration is never a number.

### 4. RAG isolation

The RAG library (`src/sharks/ai/rag_library.py` / `rag_retrieve.py`) is exempt
from the pollution concern because retrieval at simulated time T returns only
records with `as_of_timestamp <= T`, which is *enforceable* (see
`rag_retrieve.retrieve(before_as_of=T)`). Vintage-honest storage (FRED ALFRED +
content-hash manifests, proposal §3 Phase 2) makes the temporal filter auditable.

RAG retrieval is therefore allowed inside a backtest path **provided** the
`before_as_of` filter is set to the simulated decision time — never to None.

### 5. `llm_involvement` output marker

Every backtest JSON output gains a top-level field:

```json
{ "llm_involvement": "none" }
```

with domain `{ "none", "narration_only", "decision_input", "decision_output" }`:

| value | meaning | KPI-eligible? |
|---|---|---|
| `none` | no LLM anywhere in the run | ✅ yes |
| `narration_only` | LLM only described rule-based outputs; no LLM value entered a decision | ✅ yes |
| `decision_input` | an LLM output was one of several inputs to a decision | ❌ exploratory only |
| `decision_output` | an LLM directly produced a decision | ❌ exploratory only |

Only `none` and `narration_only` runs may be quoted as headline KPIs. The other
two are exploratory and must carry that label wherever their numbers appear.

## Acceptance criteria (CI / review gate)

A backtest output is **publishable** iff:

1. It declares `llm_involvement` ∈ {`none`, `narration_only`}, OR it declares a
   walk-forward window strictly post-cutoff with `cutoff_polluted: false`.
2. If any LLM call occurred in the path, the role-restriction schema check passed
   (no banned keys).
3. Any RAG retrieval used `before_as_of` = the simulated decision time.
4. The output references this runbook by path.

A reviewer rejecting a backtest for pollution cites the specific failing clause
above.

## Relationship to other docs

- `philosophy/_proposals/ai-quant-us-roadmap-merge-2026-05-30.md` §11 — the
  origin and full rationale.
- `philosophy/concepts/macro-analog-matching.md` (proposed) — the concept most
  exposed to this risk; its decision-support-not-prediction framing is the
  conceptual counterpart to defense #1 here.
- `philosophy/09-point-in-time.md` — the broader PIT discipline this protocol
  specialises for the LLM case.
- `src/sharks/ai/rag_retrieve.py` — the `before_as_of` filter that makes defense
  #4 enforceable.

## Status of enforcement

As of 2026-05-30 this is a **documentation-stage runbook**. The schema-check
helper (defense #1), the `llm_involvement` field plumbing (defense #5), and the
walk-forward window declaration (defense #2) are to be implemented when the first
LLM-involved backtest path is built (Phase 3-4). Until then, the system has no
LLM in any backtest path, so every existing backtest is trivially `none` and
compliant. This runbook exists so that the FIRST time an LLM touches a backtest,
the guardrails are already written down.
