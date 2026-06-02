---
type: concept
tags: [macro-analog, regime-cube, decision-support, history, mechanism-set, non-predictive]
title: Macro-Analog Matching (百年宏觀類比)
author_role: human
source: "Promoted from philosophy/_proposals/ai-quant-us-roadmap-merge-2026-05-30.md §4 (Reviewer-2 middle-path methodology). Implemented in src/sharks/regime/macro_analog.py + data/macro_analog_events/."
---

# Macro-Analog Matching

The premise: today's macro configuration usually *rhymes* with a handful of
episodes from the last hundred years, and the mechanism that broke those episodes
is a better checklist than any single-factor forecast. The purpose of this module
is to surface those rhymes as **hypotheses and checklists** — never as a
probability or a price target. Per [[../../sharks]] (no invented certainty), it is
explicitly **decision-support, not predictive quant**.

This is the deliberate opposite of "throw 200 macro features into a clustering
model and read off the nearest year." That approach fails twice: the
curse-of-dimensionality makes high-dim distances meaningless, and with only ~10
labelled century-scale events any "you are 87% similar to 1973" claim is
over-fitting one sample.

## The 3–4 axis regime cube

`src/sharks/regime/macro_analog.py` collapses all candidate features into a small
**human-defined** cube — `REGIME_CUBE_AXES = ("growth", "inflation", "liquidity",
"credit")`. Each axis is a handful of intuitive sub-indicators:

| Axis | Sub-indicators (illustrative) |
|---|---|
| Growth | real GDP YoY, ISM, ADP |
| Inflation | headline CPI, 5y breakeven |
| Liquidity | M2 YoY, NFCI |
| Credit | HY OAS, IG–HY divergence, SLOOS |

Humans define the axes; the dimension count stays ≤ 4. This sidesteps the
distance-concentration problem entirely — `cube_distance()` is a simple ordinal
distance over four labelled axes, not a Euclidean metric in a learned embedding
space.

## Output as a mechanism set, not a single-year label

`match()` does **not** return "you are closest to 1973." It returns the *set* of
mechanisms simultaneously present today (yield-curve inversion ✓, real-rate
tightening ✓, credit-spread widening ✓, currency-tail strain ✗), and then the
historical episodes where that **same combination** held — via
`mechanism_overlap()`, a set-intersection over the curated event files. The output
is a *distribution* of analogues ("episodes where this mechanism set held: 1929
Q3, 1969 Q4, 2000 Q1; what happened next in each: …"), which a human can
sanity-check, rather than a winner-take-all nearest neighbour.

## The non-prediction guardrail

The module hard-codes `BANNED_OUTPUT_KEYS` (probability, direction, verdict,
forecast, score, target, signal). `_assert_no_banned_keys()` rejects any attempt
to attach one of those keys to its output. This is the structural enforcement of
the decision-support framing: *any* consumer — human or LLM — is forbidden from
converting a mechanism set into a probability. Violating it is a Risk-Officer veto
trigger. It is also the first line of defence against the LLM-in-the-loop
backtest-pollution problem (see [[../09-point-in-time]] and
`docs/LLM-BACKTEST-PROTOCOL.md`): a model that has read every post-mortem of 1929
and 2008 must not be allowed to dress recall up as prediction.

## Storage: one immutable file per episode

`data/macro_analog_events/<year>.json` — one human-curated file per labelled
episode (`load_events()` reads the directory). Each carries:

- the (growth, inflation, liquidity, credit) cube classification,
- the mechanism set that defined the episode,
- the T+1y / T+3y / T+5y outcome,
- a "what was actually visible at the time" notes section (PIT-honest — the
  outcome is never used as a matching feature).

Seed events curated so far: `2000-dotcom.json`, `2008-subprime.json`. The library
grows by human curation, not by scraping.

## The ML-clustering gate

Learned clustering is **forbidden** until the library holds ≥ 50 labelled events
with ≥ 5 per archetype (boom-top / deflation-bust / stagflation / exogenous-shock
/ policy-pivot). Even then it may only act as a *prior* over the human axis
labels, never as a replacement. Until that bar is met, the module is — by design —
a transparent lookup over curated history plus a set-intersection function. No
embeddings, no clustering, no hidden state.

## What this assumes — and where it breaks

- **Curation quality is everything.** A mislabelled cube or a hindsight-polluted
  "what was visible" note silently corrupts every future match. Episode files are
  immutable and human-reviewed for exactly this reason.
- **Mechanism sets can be sparse.** A genuinely novel configuration may match no
  prior episode well; the honest answer is then "no strong analogue", not the
  least-bad neighbour.
- **History rhymes, it does not repeat.** The module produces a checklist ("the
  1973 trigger was X — is X present today?"), and the human still has to decide.

## See also

- [[funding-chain-rupture]] — supplies the credit/liquidity mechanisms episodes are scored on
- [[cycle-resonance]] — the rate-cycle reversal lens that complements analog matching
- [[multi-scale-cycles]] — the nested-cycle framing analogues sit inside
- [[btc-halving-cycle]] — a cycle whose analog may be breaking (see [[institutional-btc-anchor]])
- [[../09-point-in-time]] — outcome data must never leak into the matching features
- [[../02-signal-taxonomy]] — the 4D taxonomy this macro layer feeds
- [[../../wiki/01_macro_state]] — the live macro read the cube is computed from
- [[../../sharks]] — constitution
