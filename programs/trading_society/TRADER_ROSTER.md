---
type: research
title: Trading Society — 14-trader roster + phased rollout + weight architecture
as_of_timestamp: 2026-06-14T00:00:00+08:00
author_role: writer
status: draft
tags: [trading-society, traders, roster, scorecard, weights, regime, grok2]
related:
  - programs/trading_society/CORE_AGENT_ROLES.md
  - simulation/specialist_traders.py
  - simulation/regime_filter.py
  - simulation/portfolio_generator.py
  - grok2.md (14-trader blueprint)
---

# Trading Society — 14-trader roster

The full target roster (grok2.md blueprint), built **phased** to keep weight
allocation, fitness, and regime mapping tractable. Recommend-only; every trader's
picks pass the regime guardrail + concentration caps + Risk-Officer gate.

## Roster (3 layers, 14 traders)

**Layer 1 — sector specialists (6)**
1. Semiconductor & AI Chain Analyst — *covered by the momentum/breakout core*
2. **Power & AI Infrastructure Trader** — **built ✅** (`specialist_traders.py`)
3. **Biotech & Healthcare Specialist** — **built ✅**
4. Energy & Commodity Trader — TODO
5. **Defense & Geopolitical Analyst** — **built ✅**
6. Consumer & Internet Analyst — TODO

**Layer 2 — style specialists (5)**
7. **Small Cap Catalyst Hunter** — **built ✅** (`specialist_traders.py`)
8. Momentum & Breakout Trader — *covered (MOMENTUM_*/BREAKOUT_HUNTER)*
9. **Value & Quality Compounders** — **built ✅**
10. Mean Reversion Trader — *covered (MEAN_REVERSION/REVERSION_FAST)*
11. Event-Driven / Meme Trader — TODO

**Layer 3 — 13F-imitation (3)**
12. **Nancy Pelosi Tracker** — **built ✅** (Grade-D curated holdings + momentum)
13. **Elon Musk Ecosystem** — **built ✅** (Grade-D curated)
14. Berkshire-style Value — *largely covered by Value & Quality Compounders*

**Status: 7 specialists built + 7 core = 14 voting traders.** Remaining TODO
(Energy & Commodity, Consumer & Internet, Event-Driven/Meme) are lower priority.
All specialists are **long-only**; shorting is regime-gated (HARD_DEFENSE only).

## Phased rollout

| Phase | Traders | Goal |
|---|---|---|
| **1 (done)** | Small Cap Catalyst Hunter, Power & AI Infrastructure Trader | fill the two biggest gaps (small-cap, AI power/infra) |
| 2 | Value & Quality Compounders, Nancy Pelosi Tracker | add value + policy-catalyst coverage |
| 3 | remaining 8 | complete the ecology as backtests justify |

## Phase-1 scorecards (implemented, deterministic, 0-100)

**Small Cap Catalyst Hunter** (`small_cap_catalyst_score`) — gate: market cap
< $12B (real Finviz market caps).
- market-cap (smaller better): 0-25 · low-base (off trailing high): 0-25 ·
  breakout (1m momentum): 0-30 · catalyst/acceleration (1m vs 3m): 0-20.
- Position size: ≥85 → 5% · 70-84 → 3% · 55-69 → 2% · else 0.
- Live sample: RDW 90.7, AI (C3.ai) 86.4, SEDG 80.3, SG, MOV — genuine small-caps
  the large-cap momentum traders never surface.

**Power & AI Infrastructure Trader** (`power_ai_infra_score`) — gate: in the AI
power/grid/cooling/advanced-packaging sleeve.
- 3m trend strength: 0-40 · recent relative strength (1m): 0-30 · persistence
  (low 3m drawdown): 0-30.
- Position size: ≥85 → 6% · 70-84 → 4% · 55-69 → 2.5% · else 0.
- Live sample: KLAC 88.3, UCTT 85.6 (+98% 3m), NVMI, ICHR, ONTO, CRDO.

## Weight architecture (multi-layer)

```
final_weight = base_weight                         # per-trader floor
             x regime_tilt[regime][trader]         # regime_filter.REGIME_TRADER_TILT
             x recent_fitness_adjustment           # (core traders; champion boost)
  -> renormalize across all voting traders
  -> concentration caps (single-name <=10%, single-sector <=35%, real Finviz industries)
  -> cap-clipped weight routed to cash
```

- Specialists enter the vote with `base_weight x regime_tilt`; the core 7 also
  carry recent-fitness + champion boost. All renormalize together.
- Regime tilt (specialists): HARD_DEFENSE → SmallCap ×0.2 (right-to-zero), AI-Infra
  ×0.5; PARADIGM_BREAKTHROUGH → SmallCap ×1.6, AI-Infra ×1.7; MEAN_REVERSION →
  ×0.8 / ×1.0.

## Fairness note (cross-style fitness)

Different styles must be compared on **relative strength within their best regime**,
not raw absolute return (a small-cap hunter and a value compounder are not directly
comparable). The tournament's cross-regime score + the regime tilt encode this.

## Governance

Recommend-only. Specialists never emit a ticker order; their picks join the society
vote and are subject to the regime guardrail, concentration caps, and the
Risk-Officer gate (CLAUDE.md §10). Scorecards are deterministic and auditable.
