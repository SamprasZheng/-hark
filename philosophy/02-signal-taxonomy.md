---
type: synthesis
tags: [signal, taxonomy, conflict-resolution, philosophy]
title: Four-Dimension Signal Taxonomy + Conflict Arbitration
author_role: human
---

# 02 · Signal Taxonomy

Every actionable signal in Sharks belongs to exactly one of four dimensions. The system aggregates signals across dimensions per ticker, then applies the **conflict arbitration matrix** below before any position is opened. This page resolves codex review point #4 (missing conflict resolution rules).

## The four dimensions

| Dim | Scope | Example primary inputs | Where it lives |
|---|---|---|---|
| **Fundamental (基本面)** | revenue trajectory, margin, capex, supply structure | 10-Q / earnings call / SEC filings | `raw/earnings/`, `wiki/02_mag7_bottleneck.md` |
| **News (消息面)** | Fed, Trump, antitrust, geopolitics, raw-material shock | Reuters / Bloomberg / official releases | `raw/macro/`, `wiki/01_macro_state.md` |
| **Technical (技術面)** | price-volume structure, MA, BB, distance from 52w high, TD-9 | Finviz / yfinance OHLCV | `raw/market_data/`, computed |
| **Sentiment (情緒面)** | social volume, KOL chatter, F&G index, options put/call | X / Telegram / aggregator | `raw/kol_signals/` |

## The hard gating rules

Read these as `if-then` rules applied **before** any size calculation.

- **Sentiment alone never opens or reverses a position.** It can only act as a weighting modifier on signals that originate in another dimension. See [[sharks]] principle 2 (拒絕分別心).
- **A position that is *only* technically supported cannot exceed 30% of its bucket's size cap**, unless it is a Strategy B momentum trade explicitly tagged as such (see [[10-strategies]]).
- **News alone may stage a position but cannot fill it**: a news-only signal earns a slot on the watchlist, not in `outputs/picks-*.json`.
- **Fundamental ≥ 2 A-grade sources** is required to open a 6m or 12m bucket entry. See [[../CLAUDE#5-source-quality-grading]].

## Conflict arbitration matrix

When two dimensions disagree on a ticker, the resolution is:

| Dim A | Dim B | Resolution |
|---|---|---|
| Fundamental ↔ News (opposite) | — | **Hold thesis on fundamental.** Technical may be used only for timing within the existing thesis, not to override it. |
| Fundamental ↔ Technical (opposite) | — | **Max 30% of bucket size cap.** Exception: Strategy B momentum (acknowledges the technical override is part of the strategy). |
| Sentiment ↔ Fundamental (same direction) | — | Multiplicative bonus on confidence score (cap at +0.15). Never converts a `null` signal into a `slotted` one. |
| Sentiment ↔ Fundamental (opposite) | — | **Move to watch-only bucket.** No position. Revisit on next fundamental update. |
| News ↔ Fundamental (same direction) | — | Compound: this is the highest-quality signal class and earns priority slotting in the daily 10. |
| News ↔ Technical (same direction) | — | Standard signal; no special boost. Most Strategy A entries land here. |
| Sentiment ↔ Technical (same direction, no fundamental confirmation) | — | **Strategy B candidate with a hard time stop at 6 weeks.** Sentiment-confirmed momentum decays fast. |
| All four aligned | — | "Confluence" tag; eligible for upper bucket-size cap. Logs flagged for retrospective study because confluence is rare and informative. |

## What this rules out

- "I have a strong gut feeling on AAPL" — sentiment of one, no slot.
- "20MA crossed 60MA so I'm going in" — technical alone, capped at 30% of bucket size.
- "KOL X tweeted bullish on TSM" — sentiment of one, watchlist only.
- "Fed dovish surprise + NVDA broke 52w high + TD-9 not yet" — News + Technical aligned, no fundamental contradiction → standard signal.

## Why these specific rules

The codex review identified that without arbitration, the system devolves into pattern-matching on whichever dimension fired loudest. Empirically the lowest-Sharpe trades in any swing system come from sentiment-driven entries against fundamentals — see [[concepts/separation-mind]] for the cognitive failure mode. The matrix above is calibrated to make those entries structurally impossible without a deliberate override.

## Implementation handoff

Phase 3 ([[../docs/ROADMAP]]) will codify this matrix as `src/sharks/scoring/arbitrate.py`. The matrix is the **specification**; the implementation must round-trip every row above as a unit test. Any agent adding a new dimension or rule must update this page AND add the corresponding test, in that order.
