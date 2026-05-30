---
type: synthesis
domain: tech-trend
tags: [fom, integration, sleeves, milestone-gate, design]
as_of_timestamp: 2026-05-31T02:30:00+08:00
author_role: researcher
status: live
schema_version: 1
---

# tech/ → FOM 整合設計 / Integrating tech/ Verdicts into the FOM System

The principal asked **如何整合到 FOM 交易投資系統**. `tech/` emits *qualitative, multi-horizon* verdicts + falsifiable milestone ladders; FOM (`src/sharks/scoring/fom.py`) is a *quantitative* 5-dimension scorer feeding a 3-sleeve book ([[../philosophy/concepts/return-horizon-structure]]). This is the bridge — **bounded, non-overriding, milestone-gated, observe-first**.

> Governing principle (from [[../philosophy/concepts/analyst-persona-ensemble]]): **the quant/regime DECIDES; DD NUDGES.** A tech/ verdict is a screen + router, never a position; it never overrides the Risk Officer, caps, exclusions, or the 十足的證據 gate.

## §1. What is already wired (observed in `fom.py`, 2026-05-31)

The plumbing exists — only the verdict→action mapping is missing:

- `TECH_DD_NODES` (11 US nodes) merged into `DEFAULT_UNIVERSE`.
- `IP_DEFENSIBILITY` got per-node qualitative scores (LLY 82, NVO 78, UBER 68, DASH 62, SPOT 58, HSAI 45, MBLY 50, RXRX 35, SDGR 38, INTU 78, ADBE 70) — this IS the existing qualitative hook DD can ride.
- `HORIZON_PROFILES` already encodes **3m / 12m / 36m** lenses → the natural home for tech/ `verdict_by_horizon {T0..T3}`.
- §3.1 of [[cross-validation-quant]] already ran the live split (結構-healthy vs 結構-froth).

## §2. The bridge — three coupling points

### 2a. Verdict × `bubble_guard` → sleeve router

Maps each name to a sleeve + posture (sleeves per [[../philosophy/concepts/return-horizon-structure]]):

| tech/ verdict | `bubble_guard` | → sleeve / posture |
|---|---|---|
| 質變 (realized cashflow, e.g. GLP-1) | ≥ 0 | **Core-eligible** (still needs evidence gate + caps) |
| 結構 | ≥ 0 (healthy) | **Core watch** — the better-entry side |
| 結構 | ≤ −40 (froth) | **NOT Core**; Value sleeve *only on a confirmed pullback*, quality-filtered (撿菸頭抽兩口 safely) |
| 過熱 | any | No Core/Value; **Moonshot ring-fence (≤5%)** at most |
| 太早 | any | **Moonshot ring-fence only** (the IONQ/QBTS/RGTI bucket) |

This formalises the §3.1 split + the avoid-list into a deterministic router.

### 2b. DD conviction → bounded FOM tilt (mirrors the analyst-persona ±0.08)

Add a `TECH_DD` table `{ticker: {verdict, horizon:{T0..T3}, milestone_score 0–1, as_of}}` and a **bounded ±0.06/dim** tilt (smaller than regime, like a persona), renormalised:

- 結構-froth → small **negative momentum** tilt (don't chase the −95 names).
- 質變-cashflow → small **quality + momentum** tilt.
- 過熱/太早 → **zero Core weight** (forced to Moonshot via 2a).
- Horizon map: `T0→3m, T1→12m, T2/T3→36m`. A name 太早@T0 but 質變@T2 gets a low `fom_3m` and a higher `fom_36m` → routes to long-horizon watch, not a 短打 breakout. (This is literally what `FOMScore.horizon_scores` already computes — DD just reads it.)

### 2c. Milestone gate → promotion (couples the weekly tracker to FOM)

A name promotes **watch → Core-eligible only when** its milestone ladder ([[_weekly-watch]]) crosses a threshold: **≥1 breakout milestone ✅ AND no falsifier ❌**. Encode as `milestone_score` (fraction of ladder ticked) that gates 2a. This is the principal's *「每周里程碑完成 → 才行動」* link made mechanical.

## §3. Concrete code sketch (PROPOSAL — human applies; do not let an agent edit `src/` unreviewed)

`src/sharks/scoring/tech_dd.py`:

```python
# verdict + horizon + milestone state per DD node, sourced from tech/scoreboard.md
TECH_DD = {
  "LLY": dict(verdict="質變", horizon={"T0":"質變","T1":"質變","T2":"結構","T3":"結構"}, milestone_score=0.6),
  "MU":  dict(verdict="結構", horizon={"T0":"結構","T1":"結構","T2":"過熱","T3":"結構"}, milestone_score=0.4),
  # ... one row per node, refreshed weekly from the scoreboard
}
SLEEVE_RULES = [ ... 2a table as (verdict, bg_lo, bg_hi) -> sleeve ... ]

def dd_sleeve(ticker, fom):        # -> "core" | "value_on_pullback" | "moonshot" | "avoid"
def dd_tilt(ticker):               # -> {dim: ±≤0.06}, renormalised; consumed like a persona
```

Wire as **annotation columns** on `rank_universe` output (`dd_verdict`, `dd_sleeve`, `milestone_score`) — **NOT** folded into `final_fom` yet. **Observe-first**: only blend `dd_tilt` into `final_fom` after a walk-forward shows it adds IC ([[../philosophy/concepts/fom-predictive-validity]]). Folding a narrative into the score before measuring is exactly the fit-to-the-answer error [[../philosophy/concepts/nasdaq100-calibration]] warns against.

## §4. Weekly cadence (wire into `scripts/daily_routine.ps1` WEEKLY pass)

1. Re-verify milestone statuses per [[_weekly-watch]] + [[_sourcing-protocol]] (re-source any `single-source-pending` or >1-quarter-old figure).
2. Re-run FOM on `TECH_DD_NODES`; refresh the 結構-healthy vs 結構-froth split.
3. Update sleeve routing for any name whose `milestone_score` or `bubble_guard` band changed.
4. Emit promotions/demotions to a report for **Risk-Officer review — never auto-act**.

## §5. Guardrails (non-negotiable)

- DD is **observe-first + bounded**; never overrides Risk Officer, position/sector caps, exclusions, or the evidence gate ([[../philosophy/08-risk-and-position]], [[../philosophy/concepts/evidence-gated-rebalance]]).
- **No DD-driven offense** without the 5-dim 十足的證據 quorum (incl. mandatory earnings + a primary catalyst).
- **太早 / 過熱 can only route to the ring-fenced Moonshot sleeve** (≤5% NAV, no leverage) — matches the principal's standing Alpha-sleeve rule.
- **Backtest before trusting** — the tilt stays out of `final_fom` until IC-validated.

## See also

- `src/sharks/scoring/fom.py` — `IP_DEFENSIBILITY`, `TECH_DD_NODES`, `HORIZON_PROFILES`, `bubble_guard`
- [[../philosophy/concepts/return-horizon-structure]] — the 3-sleeve book this routes into
- [[../philosophy/concepts/analyst-persona-ensemble]] — the bounded-nudge pattern DD copies
- [[../philosophy/concepts/fom-predictive-validity]] · [[../philosophy/concepts/nasdaq100-calibration]] — why DD stays observe-first until measured
- [[cross-validation-quant]] — the live split this operationalises · [[_weekly-watch]] · [[_sourcing-protocol]]
