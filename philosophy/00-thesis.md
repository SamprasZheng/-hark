---
type: synthesis
tags: [thesis, core, philosophy]
title: Core Thesis — Sharks
author_role: human
---

# 00 · Core Thesis

The Sharks system exists to convert **macro narrative + supply-chain bottlenecks + Mag 7 dynamics** into a small set of **1-month-to-1-year US-equity swing positions**, with weekend / WFH crypto as the high-frequency satellite. Below are the six pillars distilled from [[sharks]], one line each, each with a `[[link]]` back to the constitution section it crystallises.

1. **Model over wish.** Decisions are bound to time-cycle + capital-flow models, not personal forecasts. See [[sharks]] principle 1 and the cycle-resonance regularity in [[concepts/cycle-resonance]].

2. **Probability over outcome.** Execute on high-probability setups; whether the trade hits 2× or 5× is luck. Defeat by the model is unacceptable; defeat by luck is acceptable. See [[sharks]] principle 2.

3. **No 分別心 (no comparison envy).** The most expensive emotion in a bull market is watching someone else's basket outperform yours. We never grade ourselves by the green ticker on someone else's screen. See [[concepts/separation-mind]].

4. **No farmer thinking.** Buying what worked last season is the surest way to oversupply. We look for **valuation troughs in structural form**, not crowded narratives. See [[concepts/farmer-mindset]].

5. **Pull the trigger like an assassin.** The decision work is upstream of the trade. When the trigger fires, the click is immediate — no second-guessing the indicator chain. See [[sharks]] principle 4.

6. **Read the fishbowl.** Liquidity is the water. When the water drops, even the dragons eat each other (`多殺多`). See [[concepts/liquidity-fishbowl]] and [[01-time-horizon]] for how this caps position sizing in low-liquidity regimes.

## Operational implications

- Time horizons live in `[[01-time-horizon]]`. **No HFT.** The system never produces sub-day signals for US equities outside the high-freq satellite mode for crypto.
- News (Fed / Trump / antitrust / supply shock) is the **edge**. Without macro narrative ingest, this system reduces to a Finviz screener and loses its alpha. See `[[02-signal-taxonomy]]`.
- The wiki is the **operational interface**. The user reads `wiki/` and `outputs/`; the LLM compiles them from `raw/`. See [[references/karpathy-llm-wiki]] and [[../CLAUDE]].
- Universe coverage is layered: tier1 Mag 7 (always live), tier2 supply-chain ADRs (always live), tier3 mid-cap "腰股" (dynamic, populated by [[04-sector-and-finviz]] screener in Phase 4). Full list in `watchlist/universe.yaml`.

## Falsification clauses

This thesis is **wrong** if any of the following hold for ≥ 3 consecutive months:

- The 6-month / 2-month cycle ([[concepts/cycle-resonance]]) stops appearing in any of SPX / NDX / SOX charts.
- Mag 7 returns dominate the system's basket return by > 90% — meaning the supply-chain second-derivative is no longer additive and we are just an expensive Mag 7 tracker.
- The news-driven supply-chain thesis ([[02_mag7_bottleneck]]) yields zero "腰股" candidates that beat SPY by > 5% in the following 90 days.

Falsification triggers a constitution revision session, not a silent drift.
