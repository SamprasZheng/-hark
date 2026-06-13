---
type: concept
tags: [regime, scoring, fom, momentum, bubble-guard, fix-a]
title: Regime-Gated FOM Scoring (區制調權)
author_role: human
source: "Promoted from philosophy/_proposals/fom-regime-and-universe-2026-05-30.md (Fix A). Implemented in src/sharks/regime/classifier.py + src/sharks/scoring/fom.py."
---

# Regime-Gated FOM Scoring

The Figure-of-Merit blends five dimensions (momentum / contrarian / cyclic /
quality / bubble_guard) into one 0-100 score. A *fixed* weighting is wrong across
market regimes: the mean-reversion-friendly weights that work in a choppy tape
systematically under-rate high-momentum supply-chain leaders during an AI-cycle
bull. Per [[../../sharks]] (read the regime before sizing), this concept makes the
FOM weights a function of the detected market regime instead of a constant.

## The classifier

`src/sharks/regime/classifier.py` reads the latest `outputs/breadth-indicator-*.json`
and `outputs/liquidity-signals-*.json` and labels the state into one of five
regimes from three inputs: breadth verdict, liquidity composite, and SPX-vs-200dma.

| Regime | Trigger | momentum / contrarian / cyclic / quality / bubble_guard | bubble_guard floor |
|---|---|---|---|
| `bull_trend` | breadth NORMAL + liquidity GREEN/YELLOW + SPX > 200dma | 0.40 / 0.15 / 0.15 / 0.15 / 0.15 | -40 |
| `late_bull` | breadth OVERHEATED + liquidity YELLOW + SPX > 200dma | 0.35 / 0.18 / 0.15 / 0.15 / 0.17 | -50 |
| `neutral` | fallback | 0.25 / 0.25 / 0.15 / 0.15 / 0.20 | -100 |
| `risk_off` | breadth OVERHEATED + liquidity ORANGE/RED, OR SPX < 200dma | 0.15 / 0.30 / 0.10 / 0.20 / 0.25 | -100 |
| `capitulation` | breadth CAPITULATION_BOTTOM | 0.15 / 0.40 / 0.10 / 0.20 / 0.15 | -100 |

Every profile's weights are asserted to sum to 1.0 at module load, so adding a
regime cannot silently break the scorer.

## The bubble_guard floor mechanic

`bubble_guard` runs -100..+100; the FOM normalises `(value + 100) / 2` into
0..100. In a bull regime a single late-cycle penalty (a -95 reading on a name that
has run hard) would otherwise drown the momentum signal. Each regime supplies a
**floor**: the bubble_guard reading is clamped up to the floor before
normalisation. In `late_bull` the floor of -50 lets a strong-momentum
supply-chain leader keep most of its score while still carrying *some* extension
penalty. In `risk_off` / `neutral` the floor is -100 (no clamp) so the full
penalty applies when the regime calls for caution.

## How it gates FOM

`score_ticker(..., regime=...)` stamps the regime label, weights, and floor onto
each `FOMScore`. A call with `regime=None` reproduces the canonical
25/25/15/15/20 neutral weights bit-for-bit, so every pre-regime caller is
unaffected. The daily `fom-monthly-*.json` records the active regime in its
`regime` block and `scoring_method` string.

This is orthogonal to, and composes with, the multi-horizon lens (fom_3m / 12m /
36m): regime sets the *primary* `final_fom` weights; horizons are a separate
regime-independent breakdown.

## What this assumes — and where it breaks

- **Assumes the breadth + liquidity outputs are fresh.** A stale
  `outputs/breadth-indicator-*.json` mislabels the regime. The classifier loads
  the most recent file; a daily pipeline must keep it current.
- **Discrete regimes have boundary chatter.** A market oscillating around the
  OVERHEATED / NORMAL line flips `late_bull` ↔ `bull_trend`. Acceptable here
  because their weights are close; a future smoothing (hysteresis) is a Phase 4
  refinement.
- **The floor is a judgement, not a fitted value.** late_bull = -50 is asserted,
  not backtested. Sensitivity analysis is a Phase 4 backtest deliverable.

## See also

- [[cycle-resonance]] — the adjacent rate-cycle reversal detector
- [[supply-chain-bottleneck]] — the alpha source the momentum tilt is meant to capture
- [[liquidity-fishbowl]] — the liquidity-regime intuition the classifier consumes
- [[distance-from-52w-high]] — a dimension input the regime re-weights
- [[../02-signal-taxonomy]] — the 4D taxonomy the five dimensions extend
- [[../08-risk-and-position]] — regime also informs sizing
- [[../09-point-in-time]] — the daily regime snapshot must be as_of-honest
- [[../../sharks]] — constitution
