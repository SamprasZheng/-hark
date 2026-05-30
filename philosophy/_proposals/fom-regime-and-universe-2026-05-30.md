---
type: reference
status: promoted
tags: [fom, regime, universe, scoring, proposal, fix-a, fix-d]
title: FOM regime gating (Fix A) + universe expansion (Fix D) — proposal
author_role: compiler
proposed_destinations:
  - philosophy/concepts/regime-gated-scoring.md
  - watchlist/universe.yaml
  - philosophy/06-cycle_framework.md
proposed_at: 2026-05-30T01:10:00-04:00
promoted_at: 2026-05-30T03:00:00-04:00
source_paths:
  - src/sharks/regime/classifier.py
  - src/sharks/scoring/fom.py
  - outputs/fom-monthly-2026-05-29.json
  - outputs/regime-classification-2026-05-30.json
  - outputs/breadth-indicator-2026-05-30.json
  - outputs/liquidity-signals-2026-05-30.json
---

> **PROMOTED 2026-05-30.** Canonical artifacts now live: the concept page
> `philosophy/concepts/regime-gated-scoring.md` (documenting Fix A), the
> universe-of-record `watchlist/universe.yaml` `tier2b_fom_expansion` group
> (mirroring Fix D), and the `docs/ROADMAP.md` Phase 3 §7 note. Code is in
> `src/sharks/regime/classifier.py` + `src/sharks/scoring/fom.py` with 39
> classifier tests + 13 horizon tests. This file is retained as the design
> rationale + validation record. Still deferred (separate proposals): Fix F
> regime sensitivity report, `leveraged_etf_scorer`, Taiwan ticker suffixes.

# FOM regime gating + universe expansion — PROPOSAL

> Draft proposal for two related scoring layer improvements ("Fix A" regime classifier and "Fix D" universe expansion). The code lives in the working tree and is included in the same commit as this proposal; human approval is required before the proposed destinations below are populated and before the deliverables are promoted to canonical phase status in [[../../docs/ROADMAP]].

## 1. Why

The pre-Fix FOM (`final_fom` in `src/sharks/scoring/fom.py`) systematically under-rated high-momentum ATH-extension supply-chain leaders. Three structural causes:

1. **`contrarian` 25 % weight is mean-reversion-biased**. `contrarian_score` returns `dist_score = 20` whenever the ticker is within 5 % of its 52-week high — a hard penalty applied uniformly across market regimes.
2. **`bubble_guard` 20 % weight stacks late-cycle penalties**. The 6-m and 12-m return triggers (`fom.py:275-285`) deduct up to ~95 points on a sustained breakout, which dominates the 20 % weight allocation and effectively zeros that dimension's contribution to `base_score`.
3. **The two penalties apply identically in every regime**. Whether breadth is healthy or late-cycle, whether liquidity is GREEN or RED, the weights and floors are constants.

Measured on the 2026-05-29 as-of: AMD with `momentum = 82.9` ranked #23 (`final_fom = 53.7`); MU at `momentum = 81.9` ranked #34 (`final_fom = 49.6`, `bubble_guard = -95`); INTC at `momentum = 82.2` ranked #31 (`final_fom = 52.1`). Conversely, META at `momentum = 19.5` ranked #1 (`final_fom = 59.4`). The model preferred mean-revert software over the highest-momentum supply-chain cycle leaders — the inverse of the empirical 2024-2026 regime per [[../../wiki/02_mag7_bottleneck]] and [[../../wiki/03_alpha_library]].

The universe (`DEFAULT_UNIVERSE`, 59 tickers) compounded the issue by **missing 12 of 13 of the principal's 2026-05-29 fills** (only ORCL was covered) and by missing historical飆股 MSTR, QBTS, IONQ, PLTR, COIN, HOOD, DELL entirely. This matches the coverage gap acknowledged in [[../../wiki/16_rally_themes_and_coverage_audit]] §1.

## 2. Fix A — Regime classifier and weight gating

A new module `src/sharks/regime/classifier.py` reads the latest `outputs/breadth-indicator-*.json` and `outputs/liquidity-signals-*.json` and labels the market state into one of five regimes:

| Regime | Trigger | Momentum / Contrarian / Cyclic / Quality / BubbleGuard | BubbleGuard floor |
|---|---|---|---|
| `bull_trend` | breadth NORMAL + liquidity GREEN/YELLOW + SPX > 200dma | 0.40 / 0.15 / 0.15 / 0.15 / 0.15 | -40 |
| `late_bull` | breadth OVERHEATED + liquidity YELLOW + SPX > 200dma | 0.35 / 0.18 / 0.15 / 0.15 / 0.17 | -50 |
| `neutral` | fallback | 0.25 / 0.25 / 0.15 / 0.15 / 0.20 | -100 |
| `risk_off` | breadth OVERHEATED + liquidity ORANGE/RED, OR SPX < 200dma | 0.15 / 0.30 / 0.10 / 0.20 / 0.25 | -100 |
| `capitulation` | breadth CAPITULATION_BOTTOM | 0.15 / 0.40 / 0.10 / 0.20 / 0.15 | -100 |

`FOMScore.base_score` consumes the regime's weights and clamps `bubble_guard_val` at the regime's floor before normalising to 0-100. A `score_ticker` / `rank_universe` call without a regime falls back to `neutral` weights → existing callers behave identically (verified: invoking `rank_universe(closes, universe, as_of)` with `regime=None` reproduces the canonical 25/25/15/15/20 base_score formula bit-exactly).

Each `REGIME_PROFILES` entry's weights are asserted to sum to 1.0 at module-load time so adding a new regime can't silently break the scorer.

## 3. Fix D — Universe expansion (59 → 87)

`DEFAULT_UNIVERSE` is widened across five new groups, with matching `IP_DEFENSIBILITY` entries:

- `HARDWARE_OEM = [DELL, HPE, HPQ]`
- `SPECULATIVE_NARRATIVE = [MSTR, COIN, HOOD, PLTR, APP, CVNA]`
- `QUANTUM = [QBTS, IONQ, RGTI]`
- `THEMATIC_2026_BUYS = [RIVN, NTLA, UEC, BLDP, AOSL, LPL, TBCH, CRWV, ALGM]`
- `WIKI_16_THEMES = [DNN, CCJ, BEAM, NEM, VAL, AESI, GLD]`

The first three groups capture historical飆股 and current-cycle leaders that were structurally invisible to FOM. The fourth captures the principal's actual 2026-05-29 fills so the audit is no longer blind to ~92 % of the principal's same-day trade book. The fifth picks up the explicit forward-looking themes already listed in [[../../wiki/16_rally_themes_and_coverage_audit]] §3.

Taiwan tickers (2454.TW MediaTek, 005930.KS Samsung) are explicitly **deferred** because yfinance suffix handling needs separate testing on Windows + the existing data pipeline.

## 4. Validation (measured 2026-05-30, current regime = `late_bull`)

| Ticker | Pre-Fix rank | Pre-Fix `final_fom` | Post-Fix rank | Post-Fix `final_fom` | Δ rank |
|---|---|---|---|---|---|
| ARM | #9 | 56.2 | #1 | 61.6 | +8 |
| ALAB | (outside top 20) | — | #2 | 61.3 | new top-5 |
| DELL | (not in universe) | — | #3 | 60.8 | new |
| NEM | (not in universe) | — | #4 | 60.7 | new |
| AMD | #23 | 53.7 | #5 | 60.3 | +18 |
| MU | #34 | 49.6 | #7 | 59.4 | +27 |
| INTC | #31 | 52.1 | #10 | 58.3 | +21 |
| META | #1 | 59.4 | #31 | 53.3 | -30 |
| MSFT | #4 | 57.1 | #39 | 50.7 | -35 |

Backtest context per `outputs/fom-backtest-2016-to-2026.json`: pre-Fix FOM caught NVDA in top-3 for 55 months starting at $0.87 (April 2016), and TSLA for 9 months including the 2021 entry month at $189 — so the model historically does catch leaders early. The pre-Fix failure was a different problem: MU appeared in top-3 only twice in the entire 2016-2026 window (2019-05 and 2026-04), missing the 2024-2026 ramp. Fix A is targeted at that specific failure mode, not at replacing the established early-catch behaviour.

Portfolio reconciliation against the principal's own book (per [[../../raw/principal/2026-05-29-snapshot-p1]]):
- P1 tracked positions average `final_fom = 42.6` (n = 4 / 32; the other 28 are leveraged single-stock ETFs outside FOM scope by design).
- P2 2026-05-29 fills average `final_fom = 47.0` (n = 9 / 9 after Fix D).

## 5. Risks and open questions

- **bubble_guard floor -50 in `late_bull` can let a real bubble pass**. Mitigation: regime auto-flips to `risk_off` when liquidity composite escalates to ORANGE / RED or when SPX breaks 200dma; the classifier picks this up on the next `outputs/breadth-indicator-*.json` / `outputs/liquidity-signals-*.json` write.
- **New tickers with limited price history**. CRWV, TBCH, QBTS, IONQ may not have 12-month data; `momentum_score` defaults to 50.0 (neutral) when the lookback window is short. Watch for false-positive top-rankings from this.
- **Leveraged single-stock 2x ETFs (ORCX, QBTX, RGTX, SMCL, …) remain untracked by design** because their structural decay invalidates the price-momentum scorer's assumptions. A separate `leveraged_etf_scorer` proposal is needed to address P1's ~30 % allocation to this bucket.
- **IP_DEFENSIBILITY values for new tickers are author-assigned**, not benchmarked. Human reviewer may rewrite (especially MSTR 20, BLDP 25, CVNA 25, RIVN 35 — all rationally defensible at multiple values).

## 6. Integration test sketch

```python
# tests/test_classifier.py
def test_classify_regime_late_bull():
    breadth = {"verdict": "OVERHEATED",
               "indices_vs_ma": {"SPX": {"vs_200ma": {"above_ma": True}}}}
    liquidity = {"composite_alert": {"level": "YELLOW"}}
    r = classify_regime(breadth, liquidity)
    assert r["label"] == "late_bull"
    assert r["weights"]["momentum"] == 0.35
    assert r["bubble_guard_floor"] == -50

def test_score_ticker_default_neutral_weights():
    # No regime arg → canonical 25/25/15/15/20
    s = score_ticker(closes, "AMD", as_of)
    assert s.weights == {"momentum": 0.25, "contrarian": 0.25,
                         "cyclic": 0.15, "quality": 0.15, "bubble_guard": 0.20}
    assert s.bubble_guard_floor == -100

def test_weights_sum_to_one():
    for label, profile in REGIME_PROFILES.items():
        assert round(sum(profile["weights"].values()), 6) == 1.0
```

These tests are deferred to the next session per [[../../docs/ROADMAP]] Phase 1 + Section 5 of the session plan file at `~/.claude/plans/working-tree-playful-map.md` (outside this repo) (the post-commit execution sequence places the pytest suite as step 1).

## 7. Acceptance checklist for human reviewer

- [ ] `REGIME_PROFILES` weights all sum to 1.0 (already asserted at runtime in `src/sharks/regime/classifier.py`).
- [ ] Five labels are exhaustive for the breadth × liquidity × SPX-vs-200dma space the classifier branches over.
- [ ] `late_bull` bubble_guard floor of -50 is the right number (NOT -40 or -60) — sensitivity analysis welcome.
- [ ] Universe placements correct: DELL/HPE/HPQ → HARDWARE_OEM (cycle leaders), MSTR/COIN/HOOD/PLTR/APP/CVNA → SPECULATIVE_NARRATIVE (narrative tier), QBTS/IONQ/RGTI → QUANTUM (high-narrative-low-IP).
- [ ] [[../../wiki/log]] entry for this proposal is filed.
- [ ] `watchlist/universe.yaml` update is queued (human edits to mirror `DEFAULT_UNIVERSE` additions).
- [ ] Cross-reference added in [[../../wiki/06_cycle_framework]] to point at the regime classifier as the cycle framework's operational hook.

## 8. Out of scope for this proposal

Tracked in the session plan file at `~/.claude/plans/working-tree-playful-map.md` (outside this repo) §4 (deferred follow-ons): Fix B (multi-horizon FOM_3m/12m/36m), Fix E (sector flow via XL* rotation), Fix F (regime sensitivity report), `leveraged_etf_scorer`, Taiwan ticker suffix handling.
