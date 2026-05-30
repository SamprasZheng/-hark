---
type: reference
status: proposal
proposed_status: rejected-for-integration
tags: [inspiration, open-source, ai-trading, hft, lob, deep-learning, deeplob, considered-and-rejected, proposal]
title: DeepLOB — considered and rejected for $hark integration — proposal
author_role: researcher
proposed_destination: philosophy/references/considered-and-rejected.md (append as second entry)
proposed_at: 2026-05-29T17:00:00+08:00
source_urls:
  - https://arxiv.org/abs/1808.03668
  - https://github.com/zcakhaa/DeepLOB-Deep-Convolutional-Neural-Networks-for-Limit-Order-Books
---

# DeepLOB (REJECTED-FOR-INTEGRATION, PROPOSAL)

> Draft proposal — second entry for the new aggregator page `philosophy/references/considered-and-rejected.md` introduced by [[considered-and-rejected-lobster]]. Human approval required.

**Status**: rejected-for-integration / reference-only

**What it is**: DeepLOB (Zhang, Zohren, Roberts, Oxford-Man Institute of Quantitative Finance, 2018; arxiv 1808.03668) is the canonical academic deep-learning architecture for limit-order-book mid-price-movement prediction. CNN + Inception modules + LSTM, trained on the FI-2010 benchmark dataset and the LOBSTER NASDAQ dataset. Predicts the direction of the next 10 / 20 / 50 / 100 tick mid-price moves; widely-cited (≥ 600 citations as of late 2025 — **Unconfirmed: re-verify on Google Scholar at adoption time**) and replicated in dozens of follow-up papers and GitHub forks.

**Original source of the operator's interest**: same market-scan bucket as [[considered-and-rejected-lobster]] — the "high-frequency LOB direction" being weighed against the LLM-agent direction.

## Why this is rejected for `$hark` integration

The rejection is inherited from [[considered-and-rejected-lobster]] (it consumes LOBSTER data, so a no-LOBSTER decision is also a no-DeepLOB decision), but four DeepLOB-specific reasons reinforce it:

1. **Prediction-horizon mismatch.** DeepLOB's outputs are 10 / 20 / 50 / 100 *ticks* — seconds to a few minutes of wall-clock time on a liquid NASDAQ name. The model has no edge at the day-to-month horizon `$hark`'s decision rubric operates over. Bolting DeepLOB onto a swing-horizon system is a category error.

2. **Information-decay rate vs Compile-first cadence.** `$hark`'s Compile-first runtime ingests EOD price + hourly news ([[../07-mode-switch]] `low` mode default). DeepLOB requires tick-by-tick streaming inference. The two architectures are not compatible without an event-driven runtime that is explicitly out of scope per [[../CLAUDE]] §2 spirit.

3. **No interpretability at the analyst-debate layer.** DeepLOB's hidden-layer attention is opaque relative to the four-dimension matrix in [[../02-signal-taxonomy]]. The Risk Officer cannot adjudicate "the model said long" against the conflict matrix without a learned attribution layer that does not exist for DeepLOB and is research-quality even for the broader Transformer-attention attribution literature.

4. **The legitimate use case is research, not signal.** If the operator wants to *study* deep-learning microstructure as a method-of-thought, the DeepLOB paper and follow-ups are excellent reading. That is a learning activity, not a `$hark` integration. The wiki has [[../references/karpathy-llm-wiki]] as precedent for filing methodology references; DeepLOB could one day file as a methodology-only reference page in `philosophy/references/` if the operator wanted to bank the literature notes. This proposal does not propose that filing yet.

## What we keep from having considered it

- **Confirmation that swing-horizon ≠ deep-learning-on-prices automatically.** A common reflex when "AI trading" is the topic is to reach for end-to-end deep nets on price data. DeepLOB is a legitimate execution of that pattern — it is well-engineered and academically rigorous — and it still doesn't help `$hark` because the *horizon* is wrong, not the technique. This is a useful priors-calibration reminder for future agent sessions tempted by similar architectures.
- **Methodological design ideas worth noting**: the CNN-on-LOB-volume-imbalance and the multi-horizon-classification reward design are clean. If the operator ever experiments with a much-smaller-scale price-image classifier for *daily-bar* setup recognition, the DeepLOB classification-head pattern transfers without the LOB dataset.

## What would flip this rejection

Inherits from [[considered-and-rejected-lobster]]: any condition that flips that rejection also enables a DeepLOB re-evaluation, because DeepLOB needs LOB data to run. Additionally:

| Condition | Re-open? |
|---|---|
| Published replication shows DeepLOB-like architectures at *daily-bar* horizon on Mag-7 names with Sharpe materially above a TD-9 baseline | yes — re-evaluate as a daily-bar technical-dimension scorer |
| `$hark` adds an event-driven streaming runtime for crypto high-freq weekends (Phase 6 stretch per [[../../docs/ROADMAP]]) | maybe — only for crypto, never for US equities |

## Cross-references

- [[considered-and-rejected-lobster]] — the upstream rejection this one inherits
- [[../01-time-horizon]] — the binding horizon mismatch
- [[../02-signal-taxonomy]] — the matrix the model would have to feed, but can't
- [[../CLAUDE]] §1.3 — Risk Officer's interpretability requirement DeepLOB doesn't meet
- [[../05-decision-rubric]] — the cadence DeepLOB doesn't fit
- [[../../docs/ROADMAP]] §Phase 6 — the only future phase that could host event-driven inference, and only for crypto
- [[../references/open-source-inspirations]] — the *accepted* inspirations list
- See also [[inspiration-10-qlib]] §risks — the model-zoo interpretability gating principle that DeepLOB also fails

## Notes for the human reviewer on accept

1. This is the second entry for the new `philosophy/references/considered-and-rejected.md` aggregator introduced by [[considered-and-rejected-lobster]].
2. If the human wants to file DeepLOB-the-paper as a methodology-reading reference (distinct from "considered for integration"), that is a separate `philosophy/references/` page and should be proposed in its own session.
3. No code dependencies introduced.
