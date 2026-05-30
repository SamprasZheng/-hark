---
type: synthesis
tags: [architecture, llm, dispatch, cloud-local, ollama, nemotron, philosophy]
title: Cloud / Local LLM Split — Collector + Dispatcher / Executor
author_role: human
---

# 11 · Cloud / Local LLM Split

> **大模型向外蒐集 + 高階決策派發;小模型作執行。**
> Cloud Claude is the *Collector* and the *Dispatcher*. Local Nemotron-3-Nano
> on the RTX 5070 is the *Executor*. This page formalises the contract so the
> two halves stay decoupled and the seam between them is observable, cacheable,
> and replayable.

## Why this contract exists

Until now `outputs/picks-*.json` declared `compiled_by: "Claude Opus 4.7 + Risk Officer review"` (see [[05-decision-rubric]] line 76) without saying what *else* is allowed to run on the cloud side and what is supposed to run locally. That gap let any LLM call drift to whichever side was convenient at the moment, which:

1. Burned cloud tokens on per-headline NLP that a 4 GB local model handles fine.
2. Leaked the day's portfolio composition into more cloud requests than necessary.
3. Made backtests non-reproducible — re-running a 6-month window would re-issue thousands of stochastic LLM calls.

The split below fixes all three. It also follows [[../sharks]] principle 4 (執行扣扳機,化繁為簡) — once the contract fires, execution is a mechanical local call, not another round of cloud reasoning.

## Roles

### Cloud (Claude Opus / Sonnet — the Collector + Dispatcher)

Responsibilities:

- **External collection** — `WebSearch`, `WebFetch`, multi-source synthesis of news, macro releases, earnings transcripts, KOL feeds.
- **Daily compilation** — produce `outputs/picks-YYYY-MM-DD.json` per the [[05-decision-rubric]] 10-signal contract.
- **Risk Officer review** — score conflict-arbitration outputs against [[02-signal-taxonomy]]; correct confidence downward for unsupported claims.
- **Discarded-candidate justification** — write the `## Discarded candidates` block in the daily Markdown companion.
- **Dispatch** — emit versioned JSON tasks targeted at the local Executor (contract below) and consume the returned `TaskResult`.

What cloud must NOT do:

- Per-ticker thesis paragraphs (Executor handles these).
- Per-headline sentiment classification (Executor handles these).
- Anything that should be deterministic across a backtest replay (run it through the local cache instead).

### Local (Ollama Nemotron-3-Nano on RTX 5070 — the Executor)

Default model: `nemotron-3-nano:4b` (Q4 ≈ 2.8 GB), reasoning OFF for speed.
Optional planner role: same model with reasoning ON, for ambiguous-case adjudication (Phase 5).

Responsibilities (v1):

- **`thesis`** — per-ticker 100-150 word write-up from a deep-research report dict. Used by [[concepts/chip-flow-single-point-breakout]] State 2 picks and any Strategy-A consolidation breakout.
- **`news_nlp`** — classify one headline into `bullish | bearish | neutral` + confidence + one-line rationale. The aggregate feeds the chip-flow FSM's 利空不跌 leg (`is_wash_out` adds +0.10 when `bearish_no_price_follow=True`).

What local must NOT do:

- Hit the network for fresh data — every input must arrive as part of the task payload (cloud collected it).
- Vary its output across reruns of the same task — every successful call lands in the cache; replays must hit it.

## The task envelope (versioned)

```json
{
  "v": 1,
  "type": "thesis" | "news_nlp",
  "as_of": "YYYY-MM-DD",
  "payload": { ... }
}
```

- `v: 1` is required. The dispatcher rejects any other version, so we can evolve the schema without breaking historical callers.
- `as_of` is part of the cache key — running yesterday's tasks today does not poison today's cache.
- `payload` is type-specific; see `src/sharks/ai/dispatcher.py` `_HANDLERS` for the per-type shape.

Result shape (returned to the cloud caller):

```json
{
  "ok": bool,
  "content": str | dict,
  "model": "nemotron-3-nano:4b",
  "backend": "local" | "nim" | "disabled",
  "latency_ms": int,
  "cache_hit": bool,
  "error": null | "..."
}
```

The result is a plain dict (no Pydantic dependency) so cloud Claude can round-trip it through any tool boundary without a custom encoder.

## Cache discipline — the backtest non-negotiable

Every successful dispatch is persisted under `outputs/llm-cache/<sha256>.json`, keyed by

```
sha256(task_type | model | as_of | canonical_json(payload))
```

- Same payload + model + as_of → identical key → identical cache file → identical result on replay.
- Failures are **not** cached (so a transient transport error doesn't pin a bad result).
- Backtests run with `SHARKS_LLM_CACHE_ONLY=1`. In that mode, a cache miss is a hard error — the backtest stops rather than silently asking the live Executor for a number that won't match next time.

This is the only way a strategy that uses LLM-derived features can be honestly backtested. Any module that adds a new task type must respect the same key derivation.

## Disabled mode — CI and emergency degrade

Setting `SHARKS_NEMOTRON_BACKEND=disabled` short-circuits every call. The client returns a `NemotronCall` with `error="backend disabled (...)"` and zero latency. Pipelines that consume LLM outputs already handle the `error` case (see `evidence_card.maybe_generate_thesis` at line 215 for the canonical graceful-degrade pattern). The daily picks compiler in that mode still produces a valid `picks-*.json` — the only thing missing is the +0.10 wash-out bump from [[concepts/chip-flow-single-point-breakout]] §State 1.

## PII / portfolio boundary — by design

Cloud Claude sees ticker lists, position sizes, and the day's regime. This is a deliberate feature of the role split — cloud is the *Collector*, it needs context to know what to research and what to dispatch. The local Executor sees only the per-task payload (one ticker's report, one headline) and never the full picks file.

If a future task involves credentials, account numbers, or anything outside the ticker/news domain, it does **not** become a new task type — it stays inside the local data layer (`src/sharks/data/*`) and never crosses the dispatcher seam.

## Failure modes + degrade order

| Symptom | Behaviour |
|---|---|
| Ollama daemon down | Client returns transport error → dispatcher returns `ok: false` → consumer (e.g. news_sentiment.classify_headlines) counts it under `errors` and continues. FSM falls back to pre-news three-condition wash-out. |
| Cache miss in replay mode | Hard error — backtest must stop and either pre-warm the cache or accept the gap explicitly. |
| Nemotron output not JSON-parseable for `news_nlp` | Treated as non-classifiable; counted under `errors`; not cached. |
| Unknown task type | Rejected at dispatcher entry; never reaches the network. |

## Implementation surface

- `src/sharks/ai/nemotron_client.py` — stdlib `urllib.request` port of the yxz `NemotronClient` pattern.
- `src/sharks/ai/dispatcher.py` — envelope validation + cache + GPU semaphore + handlers.
- `src/sharks/scoring/news_sentiment.py` — the first downstream consumer (closes the [[concepts/chip-flow-single-point-breakout]] 利空不跌 gap).
- `src/sharks/scoring/chip_flow_fsm.py` `is_wash_out(news_sentiment=...)` — the FSM seam that ingests the news output.
- `src/sharks/daily_picks.py` `load_news_sentiment` + `_apply_news_bump_to_watch` — orchestration glue.
- Pre-existing `src/sharks/ai/local_llm.py` + `evidence_card.maybe_generate_thesis` — legacy thesis path, untouched, still works.

## See also

- [[../sharks]] — constitution; this split honours principle 4 (執行扣扳機,化繁為簡)
- [[02-signal-taxonomy]] — the four-dimension framework into which news classifications feed
- [[05-decision-rubric]] — the 10-signal contract the cloud Compiler produces
- [[07-mode-switch]] — Low/High mode gating; cloud dispatch is mode-agnostic, the Executor is too
- [[09-point-in-time]] — `as_of` discipline; the cache key inherits it directly
- [[concepts/chip-flow-single-point-breakout]] — the analyst model that first consumes a local-LLM-derived signal
