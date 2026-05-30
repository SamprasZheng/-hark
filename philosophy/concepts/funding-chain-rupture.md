---
type: concept
tags: [funding-chain, liquidity, credit, systemic-risk, leading-indicator, macro, defensive]
title: Funding-Chain Rupture Detection (資金鏈條斷裂)
author_role: human
source: "Promoted from philosophy/_proposals/ai-quant-us-roadmap-merge-2026-05-30.md §4 (Reviewer-2 fact-corrected). Implemented in src/sharks/regime/funding_chain.py."
---

# Funding-Chain Rupture Detection

Bubbles do not pop because equities are "expensive". They pop because the
**funding chain ruptures** — the short-term credit/liquidity plumbing that lets
leveraged holders roll their positions seizes up, forcing liquidation into a
falling tape. The equity capitulation is the *last* domino, not the first. Per
[[../../sharks]] (read the regime before sizing), this concept is the leading-
indicator layer that tries to see the rupture *before* the index rolls over.

The 2000 dotcom top and the 2008 subprime collapse share this DNA: the stress
showed up first in funding markets (margin-debt unwind + CMBS in 2000; ABCP +
repo + Bear Stearns hedge funds through 2007) months before the broad equity
capitulation. The job of this module is to watch those plumbing indicators on the
**cadence at which they actually lead**, and to refuse to be lulled by lagging
survey data.

## The latency-stratified indicator taxonomy

The single biggest error in a funding-stress monitor is mixing *market-priced*
series (timely, leading) with *survey/aggregate* series (lagging) and treating
them as equivalent. `src/sharks/regime/funding_chain.py` stratifies every
indicator into one of three tiers, and only Tier-1 can fire an entry/exit on its
own.

| Tier | Cadence | Weight | Indicators | Role |
|---|---|---|---|---|
| Tier-1 | daily, market-priced | 1.0 | SOFR-OIS basis, SOFR-IORB spread, cross-currency basis (EUR/JPY-USD), CDX IG financials, HY OAS (`BAMLH0A0HYM2`) | leading — can trigger |
| Tier-2 | weekly | 0.5 | Chicago Fed NFCI, St. Louis Fed FSI, MMF outflows, CP outstanding | baseline confirmation |
| Tier-3 | quarterly | 0.0 | SLOOS bank lending standards | confirmatory only — NEVER trigger alone |

`TIER_WEIGHT = {1: 1.0, 2: 0.5, 3: 0.0}` encodes exactly this: a Tier-3
confirmatory signal carries **zero** trigger weight by construction.

### Why these specific 2026 indicators (the fact-corrections)

- **SOFR-OIS basis REPLACES FRA-OIS.** USD LIBOR ceased mid-2023, so the classic
  3m-LIBOR-FRA vs OIS spread no longer exists. Term-SOFR vs OIS is the successor
  measure of forward bank-funding stress.
- **SOFR-IORB REPLACES raw SOFR-EFFR.** SOFR routinely spikes at month-/quarter-
  end on collateral scarcity and dealer window-dressing — these are *not* systemic
  events. Filtering on persistent (≥5 day) elevation, or using SOFR-IORB, strips
  the seasonal noise.
- **Cross-currency basis** (EUR-USD, JPY-USD 3m) is the canary for *global* USD
  funding stress — the first place offshore dollar shortages show up.
- **CDX IG financials + KBW relative + sub-debt spreads + bank put-skew REPLACE
  single-name bank CDS.** Post-2008 single-name CDS is thinly traded and sits
  behind a Markit/IHS licence inaccessible to an individual project; the index +
  relative-performance proxies measure the same systemic-node risk from cheap
  feeds.
- **HY OAS lives on FRED but is market-priced and timely** (~1 trading-day lag).
  The lazy "FRED is all lagging" framing is wrong: FRED carries both timely
  market mirrors (HY OAS, SOFR, yields, NFCI) and genuinely lagging survey
  aggregates (SLOOS, H.8 deposits). The fix is per-series classification, not
  blanket distrust.

## The stress score

`funding_stress_score(readings)` classifies each supplied indicator into
`normal / elevated / stress` bands (`classify_indicator`), weights the band
severity by its tier, and rolls up to one of four states:

- **CALM** — plumbing is healthy; risk-on sizing permitted.
- **WATCH** — one or two Tier-1 indicators elevated; tighten new-entry discipline.
- **STRESS** — multiple Tier-1 indicators in stress band; begin de-risking,
  consider deploying the bear-hedge menu (see [[../10-strategies]] /
  `src/sharks/scoring/leveraged_etf.py::bear_hedge_menu`).
- **RUPTURE** — broad Tier-1 stress; this is the funding-chain break that precedes
  capitulation. Defensive posture is mandatory, not optional.

The score is deliberately a *transparent weighted band-count*, not a black-box
model — every input and its band are visible in the output so a human can audit
exactly which plumbing indicator drove the state.

## What this assumes — and where it breaks

- **Data access is the hard part, not the math.** `fetch_funding_indicators()` is
  a Phase-2 stub that raises `NotImplementedError`. The taxonomy and scoring are
  done; wiring FRED ALFRED + cheap market feeds (vintage-honest per
  [[../09-point-in-time]]) is the deferred work.
- **No single indicator is sufficient.** Quarter-end SOFR spikes, one-off basis
  widenings, and idiosyncratic CDX moves all produce false positives. The tier
  weighting and the ≥5-day persistence filter exist to suppress exactly these.
- **Tier-3 can confirm but never lead.** A SLOOS tightening print is a quarter
  stale by publication; reacting to it as a trigger is reacting to history.

## Case studies to encode

- **2000** — CMBS stress + dotcom margin-debt unwind.
- **2007–2008** — ABCP freeze + Bear Stearns hedge funds + repo run.
- **2023** — SVB / Silicon Valley Bank deposit run (a Tier-1 cross-currency +
  bank-equity-relative event in real time).
- **2025** — Warsh-era policy-shock sub-cycle per [[../../wiki/01_macro_state]].

## See also

- [[liquidity-fishbowl]] — the broad liquidity-regime intuition this sharpens
- [[cycle-resonance]] — the rate-cycle reversal detector funding-stress front-runs
- [[macro-analog-matching]] — supplies the historical episodes whose mechanisms include funding rupture
- [[../10-strategies]] — where a RUPTURE state routes into defensive strategy
- [[../08-risk-and-position]] — funding stress tightens position caps
- [[../09-point-in-time]] — every indicator reading must be vintage-honest
- [[../02-signal-taxonomy]] — the 4D taxonomy this macro layer feeds
- [[../../wiki/10_defensive_hedging]] — the hedge playbook a STRESS/RUPTURE state activates
- [[../../sharks]] — constitution
