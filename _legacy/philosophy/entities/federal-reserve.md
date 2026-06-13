---
type: entity
tags: [entity, institution, macro, fed, monetary-policy]
title: Federal Reserve (FOMC)
institution_type: central-bank
author_role: human
---

# Federal Reserve / FOMC

The single most important external institutional driver of US equity multiples and global liquidity. Fed policy decisions and communication shape the regime states in [[../concepts/liquidity-fishbowl]] and [[../concepts/cycle-resonance]].

## Why it's in the entity layer

While not a tradable ticker, the Fed is treated as an entity because:

- Its actions are the dominant input to [[../07-mode-switch]] mode triggers
- Its calendar drives [[../06-exclusions]] macro-day exclusions (FOMC days, no new entries)
- Its policy regime defines the [[../concepts/liquidity-fishbowl]] water level
- Its communication style (dot plot, post-meeting press conference, individual member speeches) drives multi-day positioning

## Calendar discipline

The Fed's scheduled cadence (FOMC meetings ~8x/year) is a known unknown — exact timing is calendar-bound but content is event-driven. The system's response:

- **Pre-meeting blackout** (T-1 trading day): no new entries on any ticker
- **Meeting day**: positions hold or trim based on existing thesis, never open
- **Post-meeting T+0 through T+2**: heightened scrutiny; reduced position size on entries opened in this window
- **Inter-meeting Fed speeches** (members): tagged source-grade B (per [[../../CLAUDE]] grading); Powell speeches A

## Key inputs the Compiler tracks

- **Dot plot revisions**: each new SEP (Summary of Economic Projections) shifts the rate-path consensus. Compare to OIS / Fed funds futures market-implied path.
- **Statement language deltas**: the FOMC statement is updated word-by-word from the prior. The deltas are the policy signal.
- **Powell press conference tone**: subjective but consequential. The Compiler files a brief tone summary post-meeting.
- **Balance sheet decisions**: QT pace announcements have larger market impact than rate decisions when liquidity is the binding constraint.

## How Fed regime translates to portfolio actions

| Fed regime | Implication for [[../concepts/liquidity-fishbowl]] L score | Portfolio action |
|---|---|---|
| Easing (rate cuts + QE) | L score rises | All tiers unrestricted; cycle-resonance bias favourable |
| Hold (neutral, balanced) | L stable | Standard sizing per [[../08-risk-and-position]] |
| Tightening (rate hikes + QT) | L falls | Tier3 capped at 50%; defensive sector buckets eligible |
| Shock-tightening (emergency response, accelerated QT) | L < 0.2 | Drought regime; max-DD halt becomes hair-trigger |

## Cross-references

- [[../concepts/liquidity-fishbowl]] — the framework Fed actions translate into
- [[../concepts/cycle-resonance]] — Fed pivot is often the catalyst that triggers the 2-month advance after a 6-month correction
- [[../concepts/last-snow]] — peak Fed hawkishness often coincides with structural market bottoms
- [[../06-exclusions]] — Fed day exclusion rule
- [[../07-mode-switch]] — Fed day force-low-freq

## Notes for the Compiler

When the Compiler updates `wiki/01_macro_state.md` after a Fed action, the page must include:
1. The FOMC statement delta vs. prior
2. The SEP / dot plot snapshot if released
3. Market-implied rate path before vs. after (OIS / FF futures)
4. Tone summary
5. Any updates to the [[../concepts/liquidity-fishbowl]] composite L score
6. `as_of_timestamp` aligned to the release embargo time (typically 14:00 ET)
