---
type: concept
tags: [discipline, rebalance, evidence-gate, mature-analyst, defensive, daily-health-check]
title: Evidence-Gated Rebalancing (十足的證據才調倉)
author_role: human
source: "Principal directive 2026-05-30: 每天倉位健檢 + 除非系統性風險 + 請以成熟分析師交易老手角度 + 十足的證據才調倉換股. Implemented in src/sharks/daily_health_check.py."
---

# Evidence-Gated Rebalancing

The discipline a seasoned trader applies to a held book: **you do not touch a
position without a reason, and the bar for adding risk is far higher than the bar
for cutting it.** This is the operating philosophy of the daily health-check
(`src/sharks/daily_health_check.py`), and it exists to protect the principal from
the exact failure mode that built the (speculative sleeve) graveyard — chasing heat without
evidence. Per [[../../sharks]] (no invented certainty, no padding), it makes
"do nothing" the default and forces every switch to clear a quorum of independent
confirmations.

## The four rules

1. **Default to inaction.** A held position stays held unless something *changed*.
   Churn is the enemy of compounding and the friend of the broker. The portfolio
   audit's HOLD is the modal, expected outcome.
2. **Offense needs full evidence (十足的證據).** A *rotate-in / switch / add* call
   is authorised only when ≥ 4 of 5 evidence dimensions are confirmed, with
   earnings mandatory and at least one primary catalyst (news or capital-flow).
3. **Defense is allowed to be fast (the asymmetry).** Cutting risk clears on a
   single systemic trigger, or on ≥ 2 deterioration signals. 老手 sells quickly
   and buys slowly — the gate encodes that asymmetry literally.
4. **Systemic risk overrides everything.** When the regime is risk_off /
   capitulation or funding stress is STRESS / RUPTURE (see
   [[funding-chain-rupture]]), posture flips DEFENSIVE and the bear-hedge menu
   (也怕大空頭) activates regardless of any offense signal.

## The five evidence dimensions

`evidence_gate()` requires confirmation across the dimensions the principal named.
Each defaults to **UNCONFIRMED** — absence of evidence is not evidence — and only
an A/B-grade source (per [[../../sharks]] source grading) clears it; a rumour or
social post (C–E) does not count.

| Dimension | 中文 | What confirms it |
|---|---|---|
| `catalyst_news` | 確實利多消息 | a sourced, A/B-grade catalyst — not a rumour |
| `capital_flow` | 資金流向數據 | ETF / institutional / dark-pool flow into the name or theme |
| `volume` | 交易量支持 | volume confirmation / accumulation footprint |
| `trade_data` | 進出口 / 出貨數據 | import-export, shipment, or channel-check data |
| `earnings` | 營利支持 | earnings, margin, or forward-guidance support |

## The gate logic

- **Offense** (`rotate_in / switch_into / add / initiate`): authorised iff
  `n_confirmed ≥ 4` AND `earnings` confirmed AND (`catalyst_news` OR
  `capital_flow`) confirmed. Otherwise → `INSUFFICIENT-EVIDENCE → HOLD`.
- **Defense** (`trim / rotate_out / switch_out / exit / hedge`): authorised iff
  `systemic_risk` OR `n_confirmed ≥ 2`. Otherwise → `WATCH` (a reason is still
  required; "fast" is not "free").

The same two-signal evidence set therefore clears a *trim* but not an *add* — the
asymmetry is mechanical, not a matter of mood.

## How it composes into the daily health-check

`run_health_check()` assembles, recommend-only:

- **Regime** ([[regime-gated-scoring]]) + **funding stress**
  ([[funding-chain-rupture]]) → **posture** (RISK_ON / NEUTRAL /
  NEUTRAL-CAUTIOUS / DEFENSIVE / MAX_DEFENSIVE) + sizing guidance.
- **Position health** — the latest `portfolio-audit-*.json` bucketed into
  SELL / TRIM / HOLD, with leveraged-decay flags surfaced (worst-decay first).
- **Hotspots** — `sector_flow.detect_rotation` surfaces sectors rotating IN. A
  hotspot is a **WATCH candidate, never an auto-buy** — it must still clear the
  evidence gate. Sector heat is necessary, never sufficient.
- **Recommendations** — default `HOLD`; a `DEFENSIVE-OVERRIDE` when systemic;
  a `STRUCTURAL-DECAY` trim when a leveraged holding's annual decay ≥ 30 %
  (a confirmed structural drag, not market-timing).

## What this assumes — and where it breaks

- **The evidence inputs are honest.** The gate is only as good as the booleans fed
  to it; a falsely-confirmed dimension defeats it. The A/B-grade requirement and
  the "default UNCONFIRMED" stance are the guardrails, but a human still has to not
  lie to themselves.
- **Funding stress needs live data.** Today `fetch_funding_indicators` is a Phase-2
  stub, so the daily run assumes CALM unless readings are injected. A real STRESS /
  RUPTURE is the single most important input and is not yet wired (FRED ALFRED).
- **Defense-fast can whipsaw.** A low defense bar means occasional unnecessary
  trims in choppy tape. The trade is deliberate: surviving the rare rupture is
  worth a few avoidable trims (also fears a big bear — 也怕大空頭).

## See also

- [[regime-gated-scoring]] — the regime input that sets posture
- [[funding-chain-rupture]] — the systemic-risk trigger that overrides to DEFENSIVE
- [[farmer-mindset]] — the crowded-trade rejection this operationalises
- [[separation-mind]] — the 分別心 inoculation against chasing heat
- [[../08-risk-and-position]] — sizing caps the posture tightens
- [[../05-decision-rubric]] — the decision rubric this gate sits inside
- [[../02-signal-taxonomy]] — the 4D taxonomy the evidence dimensions map into
- [[../../wiki/10_defensive_hedging]] — the hedge playbook a DEFENSIVE posture activates
- [[../../sharks]] — constitution

