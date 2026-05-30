---
type: synthesis
tags: [defense, tail-risk, hedge, uvxy, uvix, vix, trump-black-swan]
title: Defensive Hedging Playbook — Trump Black Swan + AI Bubble Tail Risk
as_of_timestamp: 2026-05-29T07:30:00-04:00
author_role: compiler
status: live
schema_version: 1
---

# Defensive Hedging Playbook

Principal asked 2026-05-29: do we buy UVXY / UVIX for Trump black swan defense?

**Short answer**: UVXY / UVIX are **NOT suitable** for long hold. They decay 50-80% per year. Better options below.

## §1. The UVXY / UVIX problem

Per WebSearch (Seeking Alpha, Volatility Box, CI Volatility, Fool 2026):

- **UVXY**: 1.5× daily VIX short-term futures (commodity pool)
- **UVIX**: 2× daily VIX long-term futures

### Three structural decay forces

1. **Contango roll cost**: VIX futures curve is typically upward-sloping (VIX-1m < VIX-2m < VIX-3m). Daily futures rolling sells cheaper near-month for more expensive next-month → bleeds value
2. **Daily leverage reset**: 1.5×/2× resets every day, creating volatility drag on choppy markets
3. **Percentage asymmetry**: -50% then +50% does NOT recover (=-25% net); compounds against you

**Combined effect**: 60-75% of annual losses come from contango + reset; management fees < 1%.

### Decade-long history

- UVXY since 2011: down >99.99% (reverse splits required to keep listed)
- UVIX since 2022: down ~85% in 3 years
- Only useful: tactical positions of **hours to days** during specific volatility spikes

### Verdict

- ❌ **DO NOT buy-and-hold UVXY/UVIX as a black-swan hedge**
- ✅ **TACTICAL USE ONLY** when VIX is already spiking AND volatility expansion is anticipated
- Even then, **monetise within 1-2 weeks** before contango re-asserts

## §2. Better tail-risk hedges (ranked by structural integrity)

### Tier 1 — Defined risk + capital efficient

#### VIX call options (60-90 DTE)
- Strike: VIX +20% above current (~ if VIX 14 → strike 17)
- Premium: typically 1-3% of notional hedged
- Payoff: defined max loss (premium), unlimited upside on volatility spike
- **Best instrument** for principal's Trump-black-swan ask
- Sizing: 0.5-1.5% of portfolio in premium per 6m hedge cycle

#### Mag 7 Put options (90-180 DTE)
- Long-dated Puts on names with policy exposure: NVDA (export controls), TSM (Taiwan), AAPL (China)
- Strike: 10-15% OTM
- Defined risk; capital efficient
- Replaces direct-borrow short (which is banned per [[../philosophy/03-long-short-taxonomy]])

### Tier 2 — Inverse ETFs (sustainable for medium-term)

#### SH (ProShares Short S&P 500 -1×)
- No leverage reset (1× inverse)
- Decay manageable for weeks-to-months hold
- Use case: directional bearish bet without leverage
- Sizing: 5-10% of portfolio for short-term tactical

#### SDS (ProShares UltraShort S&P 500 -2×)
- 2× inverse; daily reset
- Decay material; hold weeks max
- Use case: stronger tactical bearish

#### SQQQ (ProShares UltraPro Short QQQ -3×)
- 3× inverse tech-heavy NDX
- Aggressive decay
- Use case: TECH-SPECIFIC bear catalyst (AI bubble break)
- Sizing: ≤ 3% of portfolio; days-to-weeks hold

### Tier 3 — Safety assets

#### TLT (20+ year US Treasuries)
- Long-duration Treasury — gains on flight-to-quality during equity sell-offs
- 2022 was a notable exception (TLT also crashed during Fed hike cycle)
- Use case: macro-uncertainty hedge in non-Fed-stress regimes
- Sizing: 5-15% of portfolio as strategic allocation

#### GLD / IAU (Gold ETFs)
- Inflation + macro uncertainty hedge
- Decoupled from equity correlations during stress
- 2025-2026 gold rally already partially priced in
- Sizing: 3-8% of portfolio as strategic allocation

#### Cash (Money Market / SGOV)
- **Buffett's preferred hedge**: he holds ~30% cash at Berkshire
- Optionality value during drawdowns — buy when others fearful
- SGOV (0-3 month T-bills) yields ~4-5% (2026 rates)
- Sizing: principal currently in DCA mode; **target 15-25% cash buffer** entering Sep 2026

## §3. The recommended hedge stack for Sharks

Given current macro state ([[01_macro_state]] §4a) + Y2 midterm + Aug-Oct seasonal weakness + AI bubble proximity:

### Strategic core (always on)
| Component | Size | Purpose |
|---|---|---|
| Cash (SGOV) | 15-25% | Dry powder + Buffett-style optionality |
| Long Mag 7 quality (MSFT, GOOGL, META) | per FOM | Quality core |
| Defensive sectors (XLP, XLU) | 5-10% | Sep weakness hedge |

### Tactical overlay (Aug-Oct 2026 specifically)
| Component | Size | Trigger |
|---|---|---|
| VIX 60-90 DTE calls (strike +20%) | 0.5-1% premium | VIX < 16 + entering Aug |
| TLT or TLT calls | 5-8% | If Fed dovish surprise possible |
| Mag 7 Puts (NVDA / TSM 10% OTM) | 1-2% premium | If tier1 sizing > 30% |
| SH (1× inverse SPY) | up to 5% | If SPX -5% drawdown forms |

### Trump-specific black swan triggers
| Trigger | Action |
|---|---|
| **Truth Social: major tariff escalation announcement** | Buy 60 DTE VIX calls + SH within 1 hour |
| **Iran war escalation** | XLE long + defense long + Mag 7 Puts |
| **Taiwan strait kinetic event** | Exit TSM immediately; defense pile-in; cash buffer to 30% |
| **AI export ban expansion** | Trim NVDA/AMD/AVGO 30%; long TSM Puts |
| **Antitrust hammer on Mag 7** | Sell affected name 50% on the announcement |

## §4. Position-level Trump black swan response

For each existing tier 1/2 holding, pre-define:

| Holding type | Black-swan action |
|---|---|
| Mag 7 long | If sentiment shock > 2σ: trim 30% + buy ATM Put for remainder |
| Tier 2 supply chain | If Taiwan/China escalation: full exit on TSM, 50% trim on others |
| Defense long | INCREASE 50% on escalation news |
| Bubble watchlist (ORCL/OKLO/SMCI) | No defensive action — already short via not-owning |

## §5. When to UN-hedge

Hedges are expensive (decay/premium). They should be removed when:

- VIX returns to baseline (< 18) for 5 consecutive days
- Triggering catalyst has resolved (e.g. Trump tariff is delayed/withdrawn)
- 30 days have elapsed without crystallisation (time-decay = no longer paying for unused insurance)

## §6. Annual hedging budget

Recommended: **3-5% of portfolio per year** spent on hedges (decay + premium + opportunity cost).

This is the price of insurance. Expected payoff: 5-10× the spent budget IF a black swan crystallises. Most years: it expires worthless. **That's the deal.**

## §7. UVXY / UVIX specifically

If principal wants to use these despite warnings:

### Acceptable use
- Hold for **48 hours max** during specific volatility expansion event
- Buy AT the news (Trump announcement / Fed shock) — NOT before
- Pre-set exit at +25% or T+48hrs whichever comes first
- Max position: 2% of portfolio

### Forbidden use
- Buy-and-hold beyond 1 week
- Use as "long-term insurance"
- Size > 3% of portfolio
- Bought when VIX < 14 (just decay, no signal)

## §8. The principle's Buffett angle

Per [[../raw/methodology/buffett-philosophy]]: "別人恐懼時貪婪". Hedges are the OPPOSITE — they pay you when others are fearful, but they DON'T LET YOU buy cheap.

**The system's preferred approach**: 
- 15-25% **cash buffer** as Buffett's "perpetual hedge"
- Cash gives optionality to **buy** during the crisis (not just collect insurance)
- During calm periods, cash earns SGOV ~4-5%
- During crisis: deploy cash into cycle-resonance Long candidates

This is structurally better than UVXY because:
1. No decay
2. Earns yield
3. Generates buy-power when prices are low (compounding bigger)
4. Aligned with Buffett's documented approach

**Recommended**: 80% of "hedge budget" goes to cash buffer; 20% to tactical VIX calls during specific event windows.

## See also

- [[01_macro_state]] §4a — current cycle position
- [[07_ai_bubble_audit]] — bubble breakdown indicators
- [[../philosophy/03-long-short-taxonomy]] — Put-only short rules
- [[../philosophy/concepts/last-snow]] — when fear peaks = bottom
- [[../raw/methodology/buffett-philosophy]] — Buffett cash-as-hedge philosophy

## Sources

- [UVXY Explained: Why It Always Goes Down](https://volatilitybox.com/research/uvxy-explained-why-it-always-goes-down-and-how-to-trade-it/)
- [UVXY: Good Things Do Not Last](https://seekingalpha.com/article/4880235-uvxy-good-things-do-not-last)
- [CI Volatility: UVXY Explained](https://www.civolatility.com/p/uvxy-explained)
- [Best VIX ETFs for 2026 - Motley Fool](https://www.fool.com/investing/how-to-invest/etfs/vix-etfs/)
- [UVIX 2x Long VIX Futures Analysis - Tickeron](https://tickeron.com/ticker/UVIX/)
