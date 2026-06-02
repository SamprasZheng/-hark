---
type: synthesis
domain: tech-trend
tags: [protocol, sourcing, verification, 考證, data-integrity]
as_of_timestamp: 2026-05-31T02:30:00+08:00
author_role: researcher
status: live
schema_version: 1
---

# tech/ 資料考證協定 / Data-Source Verification Protocol

The principal flagged **數據來源考證 (source verification)** as the layer's real weak point. Phase A proved it: SEC/EDGAR `403`'d the fetcher, agents fell back to secondaries, and one genuine **Q-vs-FY mislabel** slipped through (Uber Q4 FCF/EBITDA presented as full-year) — caught only on manual spot-check. This file codifies how `tech/` sources a claim so a future reader (or the Risk Officer) can trust the number without re-deriving it. It tightens [[../CLAUDE]] §5.

## §1. Two independent axes: Grade × Verification

These are **orthogonal** — do not conflate them.

- **Grade (A–E)** = source *type* (who said it): A primary/official (filing, IR/PR, regulator, peer-reviewed, standards body) · B reputable second-hand w/ links (Bloomberg/Reuters/FT/Nikkei/IDC) · C analysis w/o primary link · D social/KOL · E rumour/scrape.
- **Verification** = *how we confirmed it*: `primary-fetched` (we read the primary directly) · `cross-confirmed` (≥2 independent secondaries agree **and** the primary URL is cited) · `single-source-pending` (one source only — not yet trustworthy) · `contradicted` (sources disagree — both shown).

> An A-*grade* claim reached only through one secondary is **`A / single-source-pending`** — high-quality *type*, low-confidence *verification*. It is NOT yet citable in a recommendation. This distinction is the core of the protocol.

Tag format on every quantitative claim:
`[<title> — <URL> — retrieved <date> — grade <A-E> — <verification>]`

## §2. The seven rules

1. **Period + Q/FY label on every financial figure.** "Q1-FY2026" or "FY2024" — never a bare number. (The Uber bug rule.)
2. **Never sum quarters into an unstated annual; never present a quarter as a full year.** ARR ≠ revenue; contract-award-ceiling ≠ booked revenue; bookings ≠ GAAP revenue — label which.
3. **A-grade financials need `primary-fetched` OR `cross-confirmed`** (≥2 agreeing secondaries + cited primary URL). One secondary ⇒ `single-source-pending`.
4. **On 403 / paywall:** record the primary URL anyway, mark the verification honestly, and fall back to ≥2 secondaries. (EDGAR 403s WebFetch — use `stockanalysis`/company-IR mirrors + the 8-K URL.)
5. **Conflicting sources → show BOTH + flag `contradicted`.** Never silently pick the convenient number.
6. **Date every figure + apply a staleness discount.** A financial figure older than one reporting quarter must be re-verified before it feeds a recommendation or a milestone tick.
7. **Forward/projection figures carry the source's own dated estimate + a `projection` tag** — never stated as fact, never lookahead past the page's `as_of_timestamp`.

## §3. Weekly re-verification (couples to the tracker)

[[_weekly-watch]] re-checks any claim that feeds a milestone. On the weekly pass:
- Re-run the source for any figure tagged `single-source-pending` or older than one quarter.
- Promote `single-source-pending` → `cross-confirmed` once a second independent source agrees; or downgrade/cut if it cannot be confirmed.
- Log `contradicted` items for human resolution (the [[../CLAUDE]] §3 contradiction rule).

## §4. 打臉自己 — what Phase A taught us (self-refutation)

The anti-echo-chamber mandate must include **anti-own-error**, not just anti-consensus:

- **Uber FY24 mislabel** — Q4 FCF $1.7B / Adj EBITDA $1.8B were presented as full-year (true FY24 = FCF $6.9B / Adj EBITDA ~$6.5B). Root cause: rule 1/2 not enforced at write time. Fix: the Q/FY label is now mandatory in the page template.
- **"HBM margin 5×" myth** — repeated in the narrative; the primary showed ~1.5×, and DDR5 profitability had actually overtaken HBM3e. Caught only by demanding the primary. Lesson: a number "everyone knows" is exactly the one to primary-check.
- **"Permanent AI shortage"** — primary data showed supply *discipline* (capex deliberately +14%), not scarcity. The narrative outran the filing.

The meta-lesson: **the most dangerous claim is the one that confirms the thesis.** Primary-check those first.

## See also

- [[00_framework]] — the rubric this protocol feeds
- [[_weekly-watch]] — the milestone tracker that re-verifies on a weekly cadence
- [[../CLAUDE]] §5 — the base A–E grading this tightens
- [[../philosophy/concepts/evidence-gated-rebalance]] — the 十足的證據 gate (absence of evidence ≠ evidence)
