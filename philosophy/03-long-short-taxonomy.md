---
type: synthesis
tags: [long-short, four-quadrant, short-selling, philosophy]
title: Long/Short Four-Quadrant Taxonomy
author_role: human
---

# 03 · Long / Short Four-Quadrant Taxonomy

Replaces the v1 "sentiment-rally = sell" binary, which the Gemini review correctly identified as a Long-only blind spot. Every signal candidate is mapped to one of four quadrants before sizing.

## The four quadrants

| Quadrant | Necessary conditions | Default action | Bucket(s) |
|---|---|---|---|
| **多頭真漲 (Genuine bull)** | (Fundamental ≥ 2A sources) ∧ (price-volume platform breakout) ∧ (no contradictory news) | **Long / Long Call**, hold 3m+, no inverse hedge | 3m, 6m, 12m |
| **多頭虛漲 (Sentiment bull)** | (Sentiment surge: social volume z-score > 2) ∧ ([[concepts/td-9-sequential]] sell setup) ∧ (price-volume divergence, see [[concepts/price-volume-divergence]]) | **Trim existing longs; open short only via Long Put** (never via direct borrow on retail mid-caps) | tactical only — 1m |
| **空頭真跌 (Genuine bear)** | (Macro break: Fed hawkish / war / antitrust strike) ∧ (supply chain disruption confirmed) ∧ (industry-wide repricing) | **Active short via Mag 7 Put or sector inverse ETF (e.g. SOXS, SQQQ)** | 1m, 3m |
| **空頭虛跌 (Sentiment bear)** | (KOL panic cluster) ∧ (volume contracting without further price decline, see [[sharks]] section on 縮量也不下跌) | **Observe. Stage long entries** for next cycle-resonance window ([[concepts/cycle-resonance]]) | 6m staging |

## Short-selling iron rules

Codex review point #4 + Gemini review point #1 both flag that retail short-selling is structurally biased against the borrower. The rules below are hard:

- **Forbidden direct borrow shorts** on any of:
  - `short_interest_pct_float > 20%`
  - `borrow_fee_apr > 10%`
  - `market_cap < $1B`
  - `60d_avg_volume < $5M / day`
- **Preferred short vehicles** (in order):
  1. Mag 7 long-dated Put options (>= 60 DTE)
  2. Sector inverse ETF (SOXS / SQQQ / FAZ / SDS) with explicit sector tag in `wiki/positions.md`
  3. Index futures (ES / NQ) — Phase 6 only, requires separate authorisation
- **No short on a Mag 7 within ±5 trading days of its earnings.** Earnings-day gamma kills short-Put theta in 24h.
- **Total short notional ≤ 30% of portfolio.** Codified in [[08-risk-and-position]].

## Why no direct borrow on mid-caps

Three structural reasons:

1. **Borrow recall risk**: prime brokers recall mid-cap shares without notice on a squeeze. You get force-closed at the worst price.
2. **Negative carry**: borrow fees on names with high short interest can exceed 50% APR, eating any thesis edge in weeks.
3. **Gamma squeeze asymmetry**: meme-cap shorts go convex against you; the loss tail is unbounded vs. capped Put loss.

Mag 7 Puts avoid all three: deep liquidity, low IV (relative to the short tail), and defined max loss.

## Quadrant routing in the daily 10-signal rubric

The decision rubric ([[05-decision-rubric]]) allocates:

- 2 long_new slots → fill from 多頭真漲 candidates
- 2 short_new slots → fill from 空頭真跌 candidates **or** the short-side action of 多頭虛漲 candidates (with the Put-only constraint above)

If only `多頭虛漲` candidates exist on the short side and the candidate violates the iron rules (e.g. retail meme with short interest > 20%), the slot stays `null`. The Risk Officer veto applies.

## Anti-pattern: "I'll just short the obvious bubble"

Counterexamples that have crushed retail shorts (and would be filtered out by the rules above):

- TSLA 2020 — short interest > 25%, ran 10× before any fundamental break
- GME 2021 — short interest > 100% of float, social squeeze incinerated borrows
- NVDA 2023 — 多頭虛漲 by social volume z-score, but fundamental real growth → not a short candidate

These are not just historical bad luck. They are the **expected failure mode** of "shorting what looks toppy". The four-quadrant taxonomy rules them out by construction.
