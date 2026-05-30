# data/recommendations_lake/

> **PIT-honest example library for the RAG approach in
> [[../../philosophy/_proposals/ai-quant-us-roadmap-merge-2026-05-30]] §5 #11.**
> Replaces the original Project AI-Quant-US QLoRA fine-tuning loop at this data
> scale (per the reviewer audit that demoted QLoRA to defer-until-≥500-pairs).

Each file in this directory is a single past recommendation slot, immutable after
its **as_of_timestamp** is set. Files are read at decision time by
`src/sharks/ai/rag_retrieve.py` to inject the k most similar past recommendations
into the current prompt as few-shot context.

## File naming

```
<YYYY-MM-DD>-<slot_id>-<TICKER>.json
```

Examples:
- `2026-05-30-01-MU.json` — recommendation slot #1 on 2026-05-30, ticker MU
- `2026-05-30-06-followup-NVDA.json` — followup slot #6 on the same date

Slot ids should match the 10-signal contract in
[[../../philosophy/05-decision-rubric]] (slots 1-2 long_new, 3-4 short_new,
5-10 position_followup).

## Schema (v1)

```json
{
  "schema_version": 1,
  "slot_id": "2026-05-30-01-MU",
  "ticker": "MU",
  "as_of_timestamp": "2026-05-30T01:10:00-04:00",
  "prompt_snapshot": {
    "regime_label": "late_bull",
    "regime_weights": {"momentum": 0.35, "contrarian": 0.18, "...": "..."},
    "breadth_verdict": "OVERHEATED",
    "liquidity_level": "YELLOW",
    "top_n_fom": [
      {"rank": 1, "ticker": "ARM", "fom": 61.6, "momentum": 83.4}
    ],
    "wiki_citations": [
      "wiki/02_mag7_bottleneck#supply-chain",
      "wiki/01_macro_state#warsh-regime"
    ],
    "prompt_text": "Late-bull regime; MU mom 81.9, bub -95 (floored -50); HBM cycle ramp Q2..."
  },
  "recommendation": {
    "verdict": "ADD",
    "position_size_pct": 2.0,
    "invalidation_triggers": {
      "price_floor": 80.0,
      "time_stop_days": 60,
      "catalyst_failure": "Q2 HBM ramp delay > 1 quarter"
    }
  },
  "embedding": {
    "method": "bow-hash-128-v1",
    "vector": [0.0, 0.123, "..."]
  },
  "outcome": {
    "return_30d": null,
    "return_60d": null,
    "return_90d": null,
    "populated_at": null
  }
}
```

## PIT discipline

Three hard rules enforced by `rag_library.py` + `rag_retrieve.py`:

1. **`as_of_timestamp` is immutable after first write.** A second call to
   `write_recommendation()` with the same `slot_id` raises if the existing file
   has a different `as_of`. This prevents silent backdating that would corrupt
   PIT lookups.
2. **Embedding is computed from `prompt_snapshot` only.** Never from `outcome`.
   This is the load-bearing guarantee that makes retrieval lookahead-safe:
   even after outcome data is populated, the similarity score that drives
   retrieval is unchanged because the embedding never saw the future.
3. **`retrieve(before_as_of=T)` returns only records with
   `as_of_timestamp <= T`.** A backtest at simulated time T sees only what was
   actually visible at T — no leakage from later recommendations.

Outcomes are populated post-hoc via `update_outcome()` which writes only to the
`outcome` block. The rest of the record is frozen.

## Embedding method (`bow-hash-128-v1`)

Bag-of-words hash trick over lowercase whitespace tokens, hashed to 128 buckets
with `hashlib.sha256(token).digest()[0:4]` reduced to `int % 128`, counts L2-
normalised. No external model dependency; deterministic across machines.

This is a **stand-in** until the recommendation lake grows past a few hundred
records, at which point swap in a real sentence encoder (BGE-small-en or similar
local model). Bump `embedding.method` to `"bge-small-en-v1.5"` and re-embed
historical records in a one-shot migration script. The retrieval interface stays
identical; only the `embed()` function body changes.

## What this directory does NOT do

- Does not produce recommendations — that's the role of
  [[../../src/sharks/decision]] (Phase 3 of [[../../docs/ROADMAP]]).
- Does not execute trades — see [[../../CLAUDE]] §2.
- Does not retrain a model — RAG explicitly replaces the QLoRA loop per the
  reviewer audit documented in the parent proposal §5 #11.

## When to graduate to fine-tuning

Per the parent proposal §5 #11, fine-tuning becomes a worth-considering option
only when ALL of the following hold:

1. The lake has accumulated **≥ 500 PIT-honest records** with populated outcomes.
2. The LLM-in-the-loop backtest pollution isolation protocol
   (`docs/LLM-BACKTEST-PROTOCOL.md`, see parent proposal §11) is documented and
   in active use.
3. RAG retrieval has been benchmarked against few-shot baselines for at least
   one Strategy A backtest window, and demonstrably under-performs what a LoRA
   adapter trained on the same data could deliver.

Until all three hold, this directory is the **primary** mechanism for the system
to "learn from past recommendations". Do not add a `lora_adapters/` sibling
directory without revisiting the parent proposal.
