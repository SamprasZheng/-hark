---
type: concept
tags: [liquidity, fishbowl, andy-principle, position-sizing, regime]
title: Liquidity Fishbowl (魚缸生態)
author_role: human
---

# Liquidity Fishbowl (魚缸生態)

[[../../sharks]] principle 5: the market is a fishbowl. Liquidity is the water. The dragons (Mag 7), tigers (mid-caps), and small fish (micro-caps) all share the same water level. When the water drops, the small fish die first; in extreme drought, even the dragons attack each other (`多殺多`).

## What this concept formalises

The Andy principle is **regime-aware position sizing**: when broad-market liquidity contracts, position sizing across the entire portfolio must shrink, and the smallest fish (tier3) gets cut first.

## Liquidity proxies the system tracks

The Compiler maintains these in `wiki/01_macro_state.md` with `as_of_timestamp`:

| Proxy | Source | Interpretation |
|---|---|---|
| Fed reserve balances | FRED `WALCL` | falling → tightening liquidity |
| Reverse repo (RRP) balance | FRED `RRPONTSYD` | rising → liquidity sitting idle, not entering risk assets |
| TGA (Treasury General Account) | Treasury Daily Statement | rising → Treasury absorbing reserves, tightening |
| 10y / 2y spread | FRED `T10Y2Y` | inverting → late-cycle liquidity stress |
| HY OAS (high-yield credit spread) | FRED `BAMLH0A0HYM2` | rising > 100bps → credit stress, liquidity flight |
| SPX 60d realised vol | computed | rising sharply → forced de-leveraging window |
| NYSE A/D line | yfinance / Finviz | falling fast → narrowing breadth, dragons eating tigers |

## The regime-sizing rule

The portfolio scales total exposure based on a composite liquidity score `L ∈ [0, 1]`:

```
L = 0.25 * normalise(reserve_balances_change_30d, max_down=-200B, max_up=+200B)
  + 0.15 * (1 - normalise(rrp_change_30d, ...))
  + 0.15 * (1 - normalise(hy_oas_level, soft_cap=400bps, hard_cap=700bps))
  + 0.20 * (1 - normalise(spx_60d_rvol, soft=15, hard=35))
  + 0.25 * normalise(ad_line_60d_slope, ...)
```

- `L > 0.7`: ample liquidity. All tiers may run at standard caps from [[../08-risk-and-position]].
- `0.4 < L ≤ 0.7`: normal. Standard caps.
- `0.2 < L ≤ 0.4`: contracting. Tier3 capped at 50% of normal. Tier2 unchanged. Tier1 unchanged.
- `L ≤ 0.2`: drought. Tier3 capped at 0% (no new positions); existing tier3 force-trimmed by 50%. Tier2 at 75% of cap. Tier1 unchanged.

## The "多殺多" warning condition

When `L < 0.15` AND `SPX_60d_rvol > 30`, the system flags `dragon-eating-dragon` regime. The Risk Officer escalates: even tier1 standard caps are halved. The [[../08-risk-and-position]] max-DD halt becomes hair-trigger (`-6%` instead of `-12%`).

This regime appeared in:
- March 2020 (Covid liquidity vacuum)
- October 2022 (Fed hawkish + UK gilt crisis spillover)
- August 2024 (Yen carry unwind, brief)

The Compiler files each instance to `wiki/03_alpha_library.md` for retrospective study.

## Why this is a principle, not just a rule

[[../../sharks]] principle 5 frames the fishbowl in cultural / cognitive terms: humans naturally observe "fish swimming" (price action) while ignoring the water level (liquidity). The discipline is to look at the water first. Most retail blowups happen because the water dropped and the trader was still trading the fish.

## Implementation handoff

Phase 2: implement liquidity proxies in `src/sharks/regime/liquidity.py`. Each proxy is a pure function `(as_of: datetime) -> float`.

Phase 3: the composite `L` score gates the daily-10-signal sizing (slot-level multiplier).

Phase 4: the backtest must reproduce historical `L` values with strict point-in-time discipline. The FRED data has a few-day publication lag that MUST be modelled — Phase 4 acceptance includes a test verifying that backtest `L[2020-03-15]` does not use data first published on `2020-03-17`.
