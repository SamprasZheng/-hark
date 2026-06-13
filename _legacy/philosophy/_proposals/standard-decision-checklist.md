---
type: proposal
tags: [decision, checklist, risk, evaluation-function, proposal]
title: Standard Decision Checklist (一套標準 checklist) — proposal
author_role: agent
source: "Agent-proposed 2026-06-01 — composes the existing 02/03/05/06/08 layers + FOM into one gated scorecard. Proposed for human promotion to a numbered foundation (11) or a concept page."
---

# Standard Decision Checklist (內化成一套標準 checklist)

**Status: PROPOSAL.** This page is the human-readable spec for the executable
`src/sharks/decision/checklist.py`. Per the index rule (agents propose, humans edit
the numbered foundations and `index.md`), it lives in `_proposals/` until you promote
it — either to `philosophy/11-standard-checklist.md` (a new foundation) or to
`philosophy/concepts/standard-decision-checklist.md` (a concept page; then add
`[[concepts/standard-decision-checklist]]` to `index.md`).

It does **not** introduce new rules. It *sequences* the rules you already wrote into
one repeatable gate chain, and states **which concept applies and when** — the
"眾多概念的平衡與使用時間" you asked for. It is RECOMMEND-ONLY and never changes the
caps in `[[08-risk-and-position]]`.

---

## The gate sequence (each ticker, in order)

| # | Gate | Source | What it answers |
|---|------|--------|-----------------|
| 1 | **Exclusion** | `[[06-exclusions]]` via `risk_config.yaml` | Is the name even eligible? (price ≥ $5, liquidity, market-cap floor, halt, IPO blackout) — hard fail stops here |
| 2 | **Regime** | `regime/classifier.py` | Which weight table + bubble_guard floor applies (bull/late_bull/neutral/risk_off/capitulation) |
| 3 | **FOM** | `scoring/fom.py` | Regime-gated 5-dimension rank + percentile vs peers + horizon lens |
| 4 | **Valuation** | `scoring/valuation.py` | P/E-anchored fair value, premium-to-fair, and the *realistic* downside (beta-implied) |
| 5 | **Order / demand** | `scoring/demand_valuation.py` | The kill-switch: are orders accelerating, stable, or **decelerating** (B:B<1 / backlog stall)? |
| 6 | **RF cycle** | `scoring/rfpm_cycle.py` | For RF/analog/power names: leading vs lagging door state (variable #15) |
| 7 | **Arbitration** | `[[02-signal-taxonomy]]` | How many of the 4 dimensions align; hard gating (sentiment never opens; technical-only → 30% cap) |
| 8 | **Quadrant** | `[[03-long-short-taxonomy]]` | 多頭真漲 / 多頭虛漲 / 空頭真跌 / 空頭虛跌 / observe |
| 9 | **Horizon + size** | `[[01-time-horizon]]` + `[[08-risk-and-position]]` | Which bucket (1m/3m/6m/12m) and the tier×horizon size cap |
| 10 | **Invalidation** | `[[08-risk-and-position]]` | The three pre-committed exits: price level, time stop (1.5×), catalyst |
| 11 | **Confidence** | `[[05-decision-rubric]]` + `weights.yaml` | The 0.50 / 0.65 / 0.80 ladder + bounded, *calibrated* nudges → final action |

A `long_new` requires: clears exclusion, lands in 多頭真漲, confidence ≥ the
`slot_threshold` (0.50). Anything short of that is `watch` — empty slots stay empty
(`[[05-decision-rubric]]` empty-slot rule; padding forbidden).

---

## Implementation map

- `src/sharks/decision/checklist.py` — `run_checklist(ticker, as_of=…) -> ChecklistResult`;
  composes the modules above; pure helpers (`arbitrate_signals`, `route_quadrant`,
  `aggregate_confidence`) unit-tested offline. CLI: `sharks checklist <ticker>`.
- `risk_config.yaml` (repo root) — the single source of truth mirroring `[[06-exclusions]]`
  + `[[08-risk-and-position]]`; `policy_lint.py` enforces it; a drift test fails if it
  diverges from the md pages.
- `src/sharks/decision/weights.yaml` + `calibrate.py` — the **evaluation-function
  calibration** (評估函數校正): the confidence ladder is fixed from `[[05-decision-rubric]]`;
  `calibrate.py` folds the measured IC / win-rate from the FOM walk-forward backtest into
  the `observed:` block. Re-weighting the nudges from per-horizon win-rate is the iterative
  next step.

## Honours the constitution
Compatible with `[[sharks]]` principle 1 (model over wish — the score is mechanical),
principle 4 (the trigger is upstream of the click — the gates run before any action),
and the point-in-time discipline of `[[09-point-in-time]]` (`as_of` is threaded through).
It sits **under** `[[08-risk-and-position]]` and the Risk Officer veto, never over them.

## Phase-1 limitations (stated honestly)
- **News + Sentiment dimensions are not wired into this path yet** — only Fundamental
  and Technical contribute, so confidence is conservative by design (max 2 aligned).
  Wiring the macro/KOL feeds raises the ceiling later.
- Confidence is **provisional** until `calibrate.py` has a real validation artifact
  (`calibration_status` in `weights.yaml` shows this).
- FOM needs price history; offline it reports `na` rather than guessing.

## Anti-patterns (what this is NOT)
- Not an autotrader — it emits a recommendation + evidence, never an order.
- Not a new threshold source — every number traces to `risk_config.yaml` ↔ the md pages.
- Not a confidence inflator — missing dimensions reduce confidence; they never fabricate it.

## See also
- `[[sharks]]` — the constitution this checklist sequences, never overrides
- `[[02-signal-taxonomy]]` — the 4-dimension arbitration the checklist applies at gate 7
- `[[03-long-short-taxonomy]]` — the quadrant router at gate 8
- `[[05-decision-rubric]]` — the confidence ladder + the slot/empty-slot contract
- `[[06-exclusions]]` — mirrored into `risk_config.yaml`
- `[[08-risk-and-position]]` — sizing, caps, halt, and the 3-part invalidation
- `[[01-time-horizon]]` — the bucket size caps applied at gate 9
- `[[concepts/chip-flow-single-point-breakout]]` — the reference analyst-model interface this composition reuses
- `[[concepts/supply-chain-bottleneck]]` — the structural-alpha source feeding the Fundamental dimension
