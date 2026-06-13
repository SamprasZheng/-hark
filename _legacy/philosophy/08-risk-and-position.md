---
type: synthesis
tags: [risk, position-sizing, drawdown, exit-rules, philosophy]
title: Risk Budget + Position Sizing + Exit Rules
author_role: human
---

# 08 · Risk & Position Sizing

Resolves codex review point #2 (the v1 plan named "every day 10 picks" but never defined sizing, exposure caps, or exit logic). This page is non-negotiable: the Risk Officer reads it on every decision and rejects anything that violates.

## Position size caps (per holding)

| Tier | Max single-position size |
|---|---|
| tier1 (Mag 7) | 8% of total portfolio |
| tier2 (supply chain ADR) | 5% |
| tier3 (mid-cap dynamic pool) | 3% |
| short (any tier, via Put or inverse ETF) | 4% notional |

Sizes are **% of total portfolio at the time of entry**, not at peak. The cap is checked again on every `add` action; an existing position that exceeds the cap due to price appreciation is not force-trimmed but cannot be added to.

## Concentration caps (per group)

- **Single sector cap**: 25% of portfolio. (Sector defined per [[04-sector-and-finviz]] sector buckets.)
- **Single catalyst cap**: 15% of portfolio.
  - A catalyst is any shared underlying driver — "AI capex cycle", "Fed pivot", "China stimulus". The Compiler tags positions with catalyst codes in `wiki/positions.md`.
- **Total short notional cap**: 30% of portfolio. (Codifies [[03-long-short-taxonomy]].)
- **Single broker cap**: 50% (in case of broker-specific risk; informational, set by user account structure).

## Correlation downweighting

When two positions correlate `> 0.7` over the last 60 trading days:
- Both positions are downweighted to `original_size × 0.6`.
- The trim is executed at the close of the third consecutive correlation-high day, not immediately.
- If correlation drops back below 0.7 for 10 consecutive days, the trim is restored.
- Mag 7 names are exempt from each other's correlation downweighting (treated as a single concentrated bet; instead use the sector cap above).

## Max drawdown halt

The system has one circuit breaker.

- **Trigger**: portfolio mark-to-market drawdown from rolling high ≤ `-12%`.
- **Action 1**: force trim every open long position by 50% (immediate, at session open). Shorts unaffected.
- **Action 2**: pause new entries (all slots `null` in daily output) for the next **5 trading days**.
- **Recovery**: after 5 days, new entries allowed but at **half the standard tier cap** for an additional 10 days. After 15 days total, return to normal.
- **Logging**: every halt entry and exit logged to `wiki/log.md` with the trigger snapshot. Halts are study fodder, not embarrassments.

## Per-thesis exit specification

Every entry in `outputs/picks-*.json` MUST declare three invalidation conditions:

```json
"invalidation": {
  "price": 432.0,                     // dollar level below which the structural thesis is wrong
  "time_stop_days": 135,              // horizon_days * 1.5; thesis must materialise by here
  "catalyst": "Blackwell launch delay > 1 quarter OR CoWoS capacity downgrade"
}
```

- **`price`**: a number, not a range. The structural thesis is wrong below this level.
- **`time_stop_days`**: 1.5× the named horizon. If the thesis hasn't paid out by this point, evidence is insufficient — exit and re-evaluate fresh.
- **`catalyst`**: a sentence describing the named event whose contradiction kills the thesis.

A position is force-exited when ANY one of the three fires. The exit is mechanical; the Risk Officer does not need to approve.

## Earnings-window position policy

- **No new entries** within ±1 trading day of the ticker's own earnings.
- **No new entries** within ±3 trading days of a tier-1 holding's earnings.
- After earnings: existing position **must be re-rated** within 1 trading day. The Compiler writes a `wiki/positions.md` update with one of:
  - `earnings_confirms` → continue current size, update `as_of_timestamp`
  - `earnings_neutral` → continue at current size, mark for review in 4 trading days
  - `earnings_softens` → trim 25-50% based on severity (Risk Officer rule)
  - `earnings_breaks_thesis` → full exit at next open
- "Hold through earnings without action" is **not an allowed state**.

## Risk-of-ruin guardrails

- **Total active longs notional**: ≤ 100% of portfolio (no leverage in Phase 1-5).
- **Total active shorts notional**: ≤ 30% (above).
- **Per-day new-money deployed**: ≤ 15% of portfolio. Slow scaling beats event-clustering.
- **Per-week new-money deployed**: ≤ 35%. Prevents revenge sizing after a halt-and-recover.

## Hand-off to implementation

Phase 3 will codify this page as `src/sharks/risk/budget.py` + `src/sharks/risk/exit.py`. Every numerical threshold above becomes a constant in a single `risk_config.yaml`. Diff between this page and the config is a P0 bug.

Phase 4 backtest must explicitly simulate the max-DD halt mechanic. A backtest that ignores the halt overstates returns and lies about drawdown discipline.

## What this rules out

- "I'll just risk 20% on this one because I'm sure" — denied by tier cap. Conviction adjusts confidence, not size.
- "All my positions are in semis but they're individually small" — denied by sector cap.
- "The halt is hurting me, let me override" — the halt cannot be overridden by chat; it can only be modified by a deliberate edit to this file and a `wiki/log.md` entry. This is the same friction principle as [[sharks]] principle 4: the trigger is upstream of the click.
