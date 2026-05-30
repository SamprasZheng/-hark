---
type: concept
tags: [farmer-mindset, contrarian, crowded-trade, andy-principle, behaviour]
title: Farmer Mindset (農民思維) — what we explicitly reject
author_role: human
---

# Farmer Mindset (農民思維)

[[../../sharks]] principle 3 names this as the canonical retail failure mode: farmers plant whichever crop sold for the highest price last season. By harvest, everyone has planted it, supply has overshot demand, and prices collapse.

In equity markets, this is the **crowded-trade trap**.

## What it looks like in practice

- "I'm buying NVDA because it had the best returns last year"
- "Everyone is in the AI trade so it must be right"
- "All my friends are buying small-cap biotech, I should too"
- "The KOL with 500k followers said this is the next 10×"

In each case, the underlying logic is "this performed; therefore it will continue to perform" — a backward-looking pattern match.

## Why it fails structurally

1. **Saturation**: by the time a trade is famous, the marginal buyer is already in. The institutional flow that drove the original returns has decelerated.
2. **Valuation premium**: crowded names trade at compressed forward returns. Even if the thesis is right, the entry price has already priced it in.
3. **Crowded exits**: when the regime shifts, every farmer rushes for the door simultaneously. Liquidity at the exit is far less than at the entry — see [[liquidity-fishbowl]] for the dynamics.

## How Sharks structurally avoids it

### Universe construction
- Tier 1 (Mag 7) is the **only** explicitly crowded bucket. We acknowledge concentration risk by capping it via [[../08-risk-and-position]] sector cap.
- Tier 2 (supply chain) is **upstream of the crowded trade**. NVDA is famous; the specialty-gas supplier that gates TSMC's CoWoS production is not.
- Tier 3 (mid-cap dynamic pool) is **populated by structural form, not by narrative**. The Finviz screener in [[../04-sector-and-finviz]] looks for consolidations, breakouts, sector-rotation winners — independent of how famous they are.

### Sentiment-as-warning
Per [[../03-long-short-taxonomy]] 多頭虛漲 quadrant: when social-volume z-score on a name > 2 (signalling crowding), the system **does not buy** unless fundamentals also independently confirm. Sentiment is a warning, not an endorsement.

### Watershed discipline
[[objective-watershed]] enforces position sizing based on observable price levels, not on "this is the next 10×" stories. A famous stock that trades below its 200MA gets no new long allocation, no matter how popular it is.

## The contrarian opportunity flipside

The farmer mindset rule is **symmetric**: just as crowded longs fail at the peak of farmer enthusiasm, oversold names with structural form thrive when no farmer is paying attention. The cycle-resonance ([[cycle-resonance]]) 6m bucket exists precisely to harvest this asymmetry — entering when [[price-volume-divergence]] shows volume drying up on holds, well before the crowd notices.

## Detection signals — when am I farmer-thinking?

The Risk Officer asks these questions before any position open:

- [ ] Is this name in the top 10 of any social-volume tracker (Twitter, Reddit) over the last 7 days? If yes, escalate scrutiny.
- [ ] Has this name been featured in 3+ tier-1 financial media headlines in the last 14 days? If yes, escalate.
- [ ] Would I be embarrassed to NOT own this name if a friend mentioned it? If yes, that is farmer thinking — pause.
- [ ] Am I about to size this position larger than my own [[../08-risk-and-position]] caps because "this one is different"? If yes, hard pause.

A "yes" to any of these is not an automatic veto, but the Researcher must produce a separate written argument for why the structural form (not the narrative) justifies the entry. The argument is filed in `wiki/log.md` as an `entry_justification` entry.

## Anti-pattern: confusing contrarianism with farmer-thinking-inversion

"Everyone is bullish, so I'll be bearish" is **not** anti-farmer thinking. It's farmer thinking with the sign flipped. The discipline is to look at **structural form** — price-volume, watersheds, supply-chain bottlenecks — independent of crowd direction. A crowded name with confirmed structural form is still a valid long (just with higher scrutiny on exit triggers).
