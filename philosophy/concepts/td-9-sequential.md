---
type: concept
tags: [td-9, demark, exhaustion, sequential, technical]
title: TD-9 Sequential (神奇九轉) + Volume-Validation Guard
author_role: human
---

# TD-9 Sequential (神奇九轉)

Tom DeMark's TD Sequential exhaustion indicator, with the volume-validation guard that Gemini review point #4 flagged as missing in v1.

## The standard TD-9 setup

On a daily / weekly / monthly bar series:

- **Buy Setup** completes when bar `C[i].close < C[i-4].close` for 9 consecutive bars.
- **Sell Setup** completes when bar `C[i].close > C[i-4].close` for 9 consecutive bars.

A completed setup is interpreted as a near-term trend-exhaustion signal — "see 9, rest is normal" in [[../../sharks]] (see the "九休息很正常" reference under principle 4 / 5).

## How Sharks uses TD-9

- The Strategy B momentum trade ([[../10-strategies]]) uses TD-9 **sell setup completion as the primary exit trigger** for long positions.
- The 多頭虛漲 quadrant ([[../03-long-short-taxonomy]]) cites TD-9 as part of the "sentiment-bull" identification (alongside social-volume z-score > 2).

## The volume-validation guard

Naive TD-9 misfires badly in strong-fundamental rallies. NVDA 2023, MSFT 2024 H1, and most large secular bull moves printed TD-9 sell setups that would have force-exited longs into the highest-return windows. The Gemini review correctly identified this as a critical blind spot.

The guard distinguishes **true exhaustion** from **trend continuation rejection** of the indicator:

### True top (执行 sell / short)
TD-9 sell setup + ALL of:
- Volume ratio: `5d_avg_volume / 60d_avg_volume < 0.7` (volume drying up)
- Social volume z-score on the ticker > 2.0 in the prior 5 days (sentiment peak — see [[../03-long-short-taxonomy]])
- No analyst upgrades in the prior 14 days (institutional flow not validating)

### Trend continuation (ignore TD-9, keep holding)
TD-9 sell setup BUT any of:
- Volume ratio `> 1.3` (volume expanding — institutional buying through the exhaustion signal)
- Analyst upgrade cluster: ≥ 2 broker upgrades in the prior 14 days
- Earnings surprise > +5% reported within 30 days (fundamental ratchet)

## The 13 extension

Per DeMark methodology, a Sell Setup completion can extend into a Sell Countdown (TD-13). If Countdown completes without the volume-validation guard triggering, that is a **stronger** exhaustion signal and overrides the trend-continuation override above — partial exit is mandatory (50% trim minimum).

## Implementation notes

- Phase 2: implement the bar-comparison check in `src/sharks/scoring/td_sequential.py`
- Phase 3: feed TD-9 status into the four-dimension scorer; the **technical dimension** carries it, but the volume-validation guard is mandatory before it contributes a score
- Phase 4: backtest the volume-validation guard separately to quantify the false-exit prevention rate vs. true-exit catch rate

## Historical study queue (Phase 2+)

The Compiler should file these specific historical cases to `wiki/03_alpha_library.md` to train future judgments:

- NVDA Jul 2023 TD-9 sell — guard ignores → continue holding (correct)
- AAPL Jan 2022 TD-9 sell — guard fires → exit (correct, ahead of 2022 drawdown)
- TSLA Nov 2021 TD-9 sell — guard fires → exit (correct)
- SOXL Mar 2024 TD-9 sell — guard fires (volume contracting) → exit (correct, before April pullback)

These cases anchor the threshold calibration.
