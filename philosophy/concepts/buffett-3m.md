---
type: concept
status: proposal
tags: [buffett, value-investing, moat, margin-of-safety, 3m, proposal]
title: Buffett 3M Integration — proposal
author_role: compiler
proposed_destination: philosophy/concepts/buffett-3m.md
proposed_at: 2026-05-29T06:30:00-04:00
---

# Buffett 3M Integration (PROPOSAL)

> Per principal directive 2026-05-29 + `D:\DOT\$hark\buffet.md` source archive.
> Draft proposal; human approval required.

## The 3M law applied to Sharks

Buffett's 3M法則: **Management + Moat + Margin of Safety** — these become the foundation of the new FOM v2 `buffett_value` dimension.

| Buffett "M" | FOM v2 sub-component | Score range | Compiler source |
|---|---|---|---|
| **Moat** | `moat` field in BUFFETT_3M dict | 0-100 | qualitative: brand strength, switching cost, network effect, IP barriers |
| **Management** | `management` field in BUFFETT_3M dict | 0-100 | qualitative: capital allocation history, insider buying patterns, governance |
| **Margin of Safety** | `margin_safety_at_current` field | 0-100 | quantitative-adjacent: forward P/E vs sector + FCF yield + dividend stability |

**Final `buffett_value` = (Moat + Management + MoS) / 3** — equal-weighted at start; tune later.

## 8 Buffett principles integrated into the system

### 1. 內在價值 (Intrinsic Value)
- Already partially captured in `quality_score` (return + low vol)
- v3 enhancement: forward P/E vs intrinsic value calculation via DCF approximation per ticker
- For Phase 2: hardcode intrinsic value estimates from public analyst targets (consensus median)

### 2. 市場先生 (Mr Market)
- Already captured in `contrarian_score` (52w high distance + IP)
- v3 enhancement: add `vix_extreme_bonus` — when VIX > 30, boost contrarian scores of high-IP names by +15
- This formalises Buffett's "be greedy when others fearful"

### 3. 安全邊際 (Margin of Safety)
- New `buffett_value.margin_safety_at_current` sub-score
- Threshold: a stock with MoS > 60 is "safe-margin available", MoS < 30 is "no MoS — overpriced"
- Combined with high IP defensibility = Buffett-tier candidate

### 4. 經濟護城河 (Economic Moat)
- New `buffett_value.moat` sub-score
- Aligned with existing `IP_DEFENSIBILITY` but more specific (Buffett looks for: brand, network, scale, switching cost, regulatory licence)
- v3: explicit moat type tag per ticker (BRAND / NETWORK / SCALE / SWITCH / REGULATORY)

### 5. 能力圈 (Circle of Competence)
- **System-level rule**: any ticker not in `BUFFETT_3M` dict defaults to 40 (neutral-low)
- This penalises names the Compiler doesn't have explicit understanding of — implementing "stay in your circle"
- Adding a ticker to BUFFETT_3M is a deliberate Researcher act per [[../CLAUDE]]

### 6. 棒球理論 (Baseball — wait for sweet spot)
- **Persistence boost** in FOM IS the system's "wait for sweet spot"
- A ticker that's been consistently top-3 for 6+ weeks earns +30% FOM — only THEN is it a clear "sweet spot"
- Single-week appearances are NOT investable — they're observations

### 7. 複利思維 (Compound thinking)
- **Buffett-tier hold permanent flag**: For tickers with Moat ≥ 90 AND Management ≥ 85 AND MoS ≥ 60 at entry, allow 12m bucket position with NO time stop (override the 14-month thesis-re-ratify rule)
- The system's "permanent" categorization is narrow: must satisfy ALL THREE conditions simultaneously

### 8. 逆反人性 (Greed when fearful, fearful when greedy)
- VIX > 30 trigger: boost Buffett-tier candidates' confidence +0.15
- Sentiment z-score > 2 on a Buffett-tier holding: trim 20% (the system is fearful when others are greedy)

## Sizing rules (additions to `08-risk-and-position.md`)

For **Buffett-tier holdings** (Moat ≥ 90 AND Management ≥ 85 AND MoS ≥ 60):

- Standard tier-1 cap: 8%
- **Buffett-tier cap: 15%** (allow more concentration in proven moat + quality + value)
- No time stop (override 14-month rule)
- Trim trigger: only on Moat or Management score downgrade (Researcher quarterly review)
- The 2022 NVDA experience shows even "great" tickers can drawdown 50%+ — Buffett-tier doesn't mean drawdown-immune, it means thesis-immune

## "Don't repeat mistakes" mechanism

Every postmortem in [[../../wiki/09_postmortem_log]] feeds into the Compiler's knowledge base:
- If a name was once a confirmed mistake (false positive), its IP defensibility / moat scores get adjusted down
- If a sector-month combo proved seasonality data wrong (e.g. solar Dec → Jan), the [[sector-seasonality]] gets calibrated
- Phase 2+ NLP could read the postmortem log automatically and propose calibration deltas

## What this DOES NOT do (intentional)

- Does NOT replace momentum dim — Buffett's framework is value-only; the system explicitly blends both
- Does NOT veto Strategy B momentum trades — Buffett would not trade momentum; Sharks does, but separately from Buffett-tier
- Does NOT eliminate market-timing — the multi-scale cycle stays. Buffett doesn't time markets, but the system's macro framework does, as additional risk management

## Verification (Phase 4 backtest)

Compare backtest with vs without Buffett dim:
- Hypothesis: Buffett dim improves Sharpe by ~10% but reduces total return by ~15% (lower concentration in narrative-momentum names)
- Run with `--enable-buffett-dim true|false` flags
- Acceptance: if Buffett dim improves Sharpe-MDD trade-off, integrate live

## See also

- [[../../raw/methodology/buffett-philosophy]] — source archive
- [[../05-decision-rubric]] — daily 10-signal where Buffett-tier candidates earn priority
- [[../08-risk-and-position]] — sizing rules (Buffett-tier cap = 15%)
- [[../09-point-in-time]] — Buffett-tier "permanent" tag still subject to as_of discipline
- [[../../wiki/09_postmortem_log]] — mistakes ledger that feeds calibration
