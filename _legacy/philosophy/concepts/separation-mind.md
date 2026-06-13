---
type: concept
tags: [psychology, comparison-envy, andy-principle, behaviour]
title: Separation Mind (分別心) — comparison envy
author_role: human
---

# Separation Mind (分別心)

[[../../sharks]] principle 2: the most expensive emotion in any bull market is **watching someone else's basket outperform yours**. The discipline is to grade decisions by the system's own process, never by relative performance against a different system.

## The mechanism

The 分別心 failure cycle:

1. Open a thesis-driven position (Strategy A, B, or C — doesn't matter)
2. Observe that a different name (or a different trader, or an index) is running harder
3. Feel envy / regret / FOMO
4. Override the original thesis: trim the slow-grinding position to free up capital
5. Buy into the running name late, at a worse entry, with weaker thesis support
6. Watch the late entry fail; observe the original position recover
7. Repeat

The cycle is **predictable** and the cost is enormous because it converts disciplined entries into chased entries at every cycle.

## Where it shows up structurally in the system

### In the daily 10-signal output
Per [[../05-decision-rubric]], `position_followup` slots can include `trim` and `exit` actions. The Risk Officer reviews every such action for `separation-mind` markers:
- Is the trim justified by [[../08-risk-and-position]] catalyst invalidation, OR by "this isn't moving as fast as [other ticker]"?
- The latter is automatic-reject.

### In KOL signal weighting
KOL signals are tagged source-grade D (per [[../../CLAUDE]] grading). Per [[../02-signal-taxonomy]] gating, sentiment-only signals never open or reverse a position. This rule exists primarily to prevent 分別心-via-influencer.

### In the comparison-language detector
The Compiler scans the user's session messages for comparison patterns:
- "Why isn't X running as much as Y?"
- "I should have bought Z instead"
- "Everyone made more on the AI trade"
The Compiler does not block — but appends a `## Separation Mind flag` note to `wiki/log.md` for that session. Pattern accumulation triggers a quarterly review.

## What the discipline actually requires

The honest version: comparison is **automatic and unavoidable**. The discipline is not to suppress the feeling, but to **never let it drive a position decision**. Operationally:

1. Acknowledge the comparison in writing (chat or log).
2. Re-read the relevant `wiki/positions.md` entry. The thesis is there in writing, with `as_of_timestamp`.
3. Check whether the thesis has been **falsified** (per [[../08-risk-and-position]] invalidation conditions). If yes, exit per the mechanical rule. If no, the position holds, regardless of how someone else's position is doing.

This is why every position carries an invalidation specification — to make exit decisions mechanical and to inoculate the system against comparison-driven trims.

## The constitution's framing

[[../../sharks]] makes the deeper point: a mature trader **can lose to luck but never to system**. If a different name with the same structural form ran further, that is luck. Our system identified valid forms; the market chose which form to reward. The cumulative edge is in **always trading valid forms**, not in correctly predicting which valid form gets rewarded each cycle.

## Detection at the meta-level

The Risk Officer maintains a quarterly review of "decisions reversed within 30 days that, in hindsight, would have profited if held". Excessive reversals (> 30% of decisions in a quarter) is a 分別心 indicator at the system level. The intervention is a 2-week trade freeze and a forced re-read of [[../../sharks]].

## Anti-pattern: "process worship"

The flipside risk: refusing to trim a position whose thesis has demonstrably broken, because "I committed to the thesis, I won't be influenced by short-term price action". This is mechanical-rule worship masquerading as discipline. The invalidation specs in [[../08-risk-and-position]] are mechanical for a reason — they bind in **both** directions: hold when comparison tempts you to trim, exit when invalidation fires regardless of personal attachment.
