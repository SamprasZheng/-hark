---
type: reference
status: proposal
tags: [inspiration, open-source, ai-trading, llm, sentiment, fingpt, proposal]
title: FinGPT — finance-domain LLM sentiment for the Compiler — proposal
author_role: researcher
proposed_destination: philosophy/references/open-source-inspirations.md (append as entry #9)
proposed_at: 2026-05-29T17:00:00+08:00
source_urls:
  - https://github.com/AI4Finance-Foundation/FinGPT
  - https://arxiv.org/abs/2306.06031
  - https://arxiv.org/abs/2310.04793
---

# Inspiration #9 — `AI4Finance-Foundation/FinGPT` (PROPOSAL)

> Draft proposal for the `philosophy/references/open-source-inspirations.md` numbered list. Human approval required before move into the philosophy layer.

**Fit**: ★★★★☆

FinGPT is the AI4Finance Foundation's open-source line of finance-tuned large language models — LoRA adapters on top of base LLMs (Llama / Falcon / ChatGLM families per the 2023 paper), with a published data pipeline that ingests Twitter / Reddit / financial-news streams and emits sentiment / FinRL signal features.

## What we borrow

The Compiler role ([[../CLAUDE]] §1.1) currently has a stubbed sentiment scorer ([[../../docs/ROADMAP]] Phase 3 deliverable 2.4 — `src/sharks/scoring/sentiment.py`). Inspiration #8 (`awoo424/algotrading`) proposes VADER for that scorer. VADER is general-domain — it scores "the company missed earnings" indistinguishably from "the team missed the bus." For Phase 4 we want a sentiment scorer that:

1. Understands finance-specific vocabulary ("guide-down", "ASP compression", "demand pull-in", "channel inventory", "buyback authorisation").
2. Outputs structured sentiment per ticker / per supply-chain entity, not a single bulk score, so the result can attribute to the four-dimension matrix in [[../02-signal-taxonomy]].
3. Runs locally on the operator's RTX 5070 (per memory `project_nemoclaw_local_gpu`) without exfiltrating raw KOL feeds to a third-party API — preserving the source-grading discipline in [[../CLAUDE]] §5.

FinGPT meets all three: it ships LoRA adapters small enough (single-digit GB) to run on consumer GPUs with 4-bit quantisation, and the FinNLP data layer is the upstream sentiment pipeline.

## Phase

**Phase 4** (per [[../../docs/ROADMAP]] §Phase 4) — slots into `src/sharks/scoring/fingpt_sentiment.py` as a parallel scorer to VADER. Phase 4 milestone: FinGPT sentiment score available as a feature in the backtest config files.

**Phase 5** stretch — fine-tune a small LoRA on `wiki/05_recommendations/archive.md` (recommendation + 30-day forward return outcome) to bias the scorer toward our own Mag-7 supply-chain framing rather than general financial news.

## Proposed integration adaptation

- **Module path**: `src/sharks/scoring/fingpt_sentiment.py` — implements the same scorer-protocol as the other four dimensions (`fundamental` / `news` / `technical` / `sentiment`).
- **Point-in-time discipline**: the FinGPT scorer must accept an `as_of` parameter and only score text whose source timestamp is ≤ `as_of`. This is non-negotiable per [[../09-point-in-time]] and is the single most expensive corruption surface the new tool introduces.
- **Source-grade preservation**: the input to the scorer is already source-graded (A/B/C/D/E per [[../CLAUDE]] §5). The scorer's output row carries the *input* grade forward — a D-grade tweet stays a D-grade signal even after FinGPT scores it. Grade D/E never triggers a position open per the existing rule.
- **Model selection**: start with the smallest published FinGPT LoRA that scores acceptably on the AI4Finance benchmark; defer the Llama-70B-base variants until Phase 5 unless local-GPU benchmarks justify them.
- **Determinism for backtest replay**: temperature 0 + fixed seed at scoring time so backtest re-runs are reproducible. Stochastic decoding is forbidden in backtest paths.

## License

**Unconfirmed: license file on the FinGPT repo should be re-verified at adoption time** — AI4Finance umbrella projects (FinRobot, FinRL) have historically been MIT, but the operator must confirm the exact license on the FinGPT repo before any code copy. If MIT or Apache 2.0 → freely integrable per [[../../docs/INSPIRATIONS]] §Licensing & legal. If GPL → "design-inspiration only" treatment (write our own wrapper around HuggingFace `transformers` + `peft` calls; do not copy FinGPT's code).

Base-model licenses (Llama 2 community, Falcon Apache 2.0, ChatGLM 6B research) are a separate layer the operator reviews per chosen LoRA.

## Integration test sketch

```python
# tests/test_fingpt_sentiment_smoke.py
def test_fingpt_respects_as_of():
    # Two sources: one before, one after as_of
    src_before = "NVDA beat earnings (timestamp: 2024-02-21)"
    src_after  = "NVDA cut guidance (timestamp: 2024-08-15)"
    scorer = FinGPTSentimentScorer(model="fingpt-sentiment-lora-llama2-7b")
    out = scorer.score(
        sources=[src_before, src_after],
        as_of="2024-05-01T00:00:00Z",
    )
    assert len(out) == 1  # only src_before is visible
    assert out[0].source_grade == "B"  # grade preserved
    assert out[0].ticker == "NVDA"

def test_fingpt_deterministic():
    text = "ASML guides 2026 wafer demand higher; CoWoS bottleneck eases."
    scorer = FinGPTSentimentScorer(temperature=0.0, seed=42)
    a = scorer.score_one(text)
    b = scorer.score_one(text)
    assert a == b
```

## Risks / open questions for the human reviewer

1. **GPU memory budget**: the operator's RTX 5070 has 12 GB VRAM (per [[../../../memory/project_nemoclaw_local_gpu]] — unverified VRAM exact figure). FinGPT-Llama2-7B-LoRA in 4-bit should fit; 13B variants likely will not without offload.
2. **Model staleness**: published FinGPT LoRAs are trained on pre-2024 corpora. 2025–2026 finance vocabulary (e.g. "vibe trading", "AI bubble audit", "ODC") will not be in their training distribution. The Phase 5 self-fine-tune is the answer; until then, scores on novel terms should be weighted down.
3. **Chinese / Traditional Chinese inputs**: many KOL feeds the operator reads are Chinese. FinGPT-ChatGLM variants handle this; FinGPT-Llama variants do not natively. Choice of base affects sentence-coverage on the actual `raw/kol_signals/` pipeline.
4. **Hallucination on numerical extraction**: FinGPT is sentiment-strong, number-extraction-weak. Do NOT use it to extract earnings figures into `raw/earnings/` — that stays human-curated or rule-based parser-curated.

## Cross-references

- [[../CLAUDE]] §1.1 (Compiler), §1.2 (Researcher), §5 (source grading)
- [[../09-point-in-time]] — `as_of_timestamp` discipline the scorer must respect
- [[../02-signal-taxonomy]] — sentiment dimension this scorer feeds
- [[../05-decision-rubric]] — sentiment never triggers entry alone
- [[../references/open-source-inspirations]] — proposed insertion point (entry #9)
- [[../../docs/ROADMAP]] §Phase 4 — milestone alignment
- [[../../docs/INSPIRATIONS]] §Licensing & legal — license-handling discipline this proposal inherits
- See also Inspiration #8 (`awoo424/algotrading`) — VADER incumbent this proposal complements / replaces for finance text
- See also Inspiration #3 (`FinRobot`) — sibling AI4Finance project already at Phase 3

## Notes for the human reviewer on accept

1. Verify FinGPT repo license at https://github.com/AI4Finance-Foundation/FinGPT/blob/master/LICENSE before any code copy.
2. Decide base-model (Llama / Falcon / ChatGLM) before module scaffold.
3. Update `pyproject.toml` Phase-4 dep block: `torch`, `transformers`, `peft`, `bitsandbytes`, `accelerate`.
4. After move from `_proposals/` to `philosophy/references/open-source-inspirations.md`, also append the matching row in `docs/INSPIRATIONS.md` integration matrix (see companion proposal [[inspirations-matrix-patch]]).
