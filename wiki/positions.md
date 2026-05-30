---
type: synthesis
tags: [positions, open, invalidation, stub]
title: Open Positions and Thesis State
status: stub
as_of_timestamp: 2026-05-28T22:00:00-04:00
---

# Open Positions (stub)

Phase 1 placeholder. Phase 3 onward: this page is the live state of all open positions. Updated on every position open / followup / exit.

## Expected entry format per position

```
## NVDA — long_new — 2026-05-28T20:00:00-04:00

**Strategy**: A (consolidation-breakout)
**Tier / Bucket**: tier1_mag7 / 3m
**Quadrant**: 多頭真漲
**Size**: 4.0% of portfolio
**Entry zone**: $458 – $472
**Entry date**: 2026-05-28
**Avg fill price**: TBD (manual entry — system does not execute)

**Thesis**:
One paragraph linking to [[../philosophy/entities/nvidia]] and [[02_mag7_bottleneck]] sections.

**Catalyst**:
- Blackwell ramp
- Specific quarterly earnings expectation

**Invalidation triggers** (any one = exit):
- price: $432 (close below for 2 consecutive sessions)
- time_stop_days: 135 (exit by 2026-10-10 if thesis hasn't paid)
- catalyst: Blackwell delay > 1Q OR CoWoS capacity downgrade

**Evidence paths**:
- raw/earnings/nvda-2026q1.md
- wiki/02_mag7_bottleneck.md#cowos
- philosophy/entities/nvidia.md#three-key-catalysts

**Followup log**:
- (entries added on each followup slot in daily 05_recommendations/*.md)
```

## Phase 1 status

No open positions. Phase 1 is content scaffold only; no trading recommendations issued.

## Discipline reminders

- A position MUST declare all three invalidation triggers
- A position with `catalyst` field empty is **invalid** and rejected by Risk Officer
- "Hold through earnings without action" is not allowed — every earnings event forces a re-rate per [[../philosophy/08-risk-and-position]]
- Comparison-driven trims ("X is running harder, I should switch") trigger a [[../philosophy/concepts/separation-mind]] flag and require Risk Officer review

## See also

- [[../philosophy/05-decision-rubric]] — how daily followup slots interact with this page
- [[../philosophy/08-risk-and-position]] — invalidation contract
- [[../philosophy/concepts/objective-watershed]] — pre-committed price levels for bias gating
