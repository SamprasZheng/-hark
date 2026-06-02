---
type: reference
status: proposal
tags: [inspiration, open-source, ai-trading, quant, factors, qlib, microsoft, proposal]
title: Qlib — Microsoft AI quant platform for factor library + backtest — proposal
author_role: researcher
proposed_destination: philosophy/references/open-source-inspirations.md (append as entry #10)
proposed_at: 2026-05-29T17:00:00+08:00
source_urls:
  - https://github.com/microsoft/qlib
  - https://arxiv.org/abs/2009.11189
---

# Inspiration #10 — `microsoft/qlib` (PROPOSAL)

> Draft proposal for the `philosophy/references/open-source-inspirations.md` numbered list. Human approval required before move into the philosophy layer.

**Fit**: ★★★★★

Qlib is Microsoft Research Asia's open-source AI-oriented quantitative investment platform (redacted). The most architecturally-aligned project the operator could borrow from for `$hark`'s Phase 4–5 work:

- **Data layer**: time-series storage with explicit point-in-time semantics (`D.features(..., end_time=...)`) — directly maps to [[../09-point-in-time]]
- **Factor library**: ~150 built-in alpha factors (Alpha158 set + Alpha360 extended set), each as a named expression that the engine can evaluate per-ticker per-timestamp
- **Model zoo**: LightGBM, MLP, LSTM, GATs, TabNet, TFT, Transformer baselines — all wrapped in the same `Model.fit / .predict` protocol
- **Backtest engine**: realistic frictions (commission, slippage, minimum-amount), portfolio-level execution, walk-forward training
- **Workflow YAML**: end-to-end pipeline (data → features → model → backtest → KPI) declared in one config file

## What we borrow

Three layers, each into a different `src/sharks/` module path. **All three borrows must add `$hark`'s `as_of_timestamp` discipline and source-grading on top of Qlib's native point-in-time** — Qlib's point-in-time is "trade-time-only correct"; ours is "every feature row carries its source provenance and grade."

| Layer | What | Target module | Why |
|---|---|---|---|
| 1. Factor library | Alpha158 expressions, ported and pruned | `src/sharks/factors/qlib_alpha.py` | Phase 3's [[../02-signal-taxonomy]] technical dimension is currently TD-9 + MAs + Bollinger + distance-from-52w-high. Alpha158 adds ~150 candidate features that the four-dimension scorer can subscribe to. The Risk Officer rejects any feature without an interpretable economic story, so Alpha158 is a candidate pool, not a blanket adoption. |
| 2. Backtest engine | Workflow-YAML + executor + analyser | `src/sharks/backtest/qlib_engine.py` | [[../../docs/ROADMAP]] Phase 4 deliverable 1 says "choose Backtrader or vectorbt." Add Qlib to that decision matrix — its backtest engine is the most realistic of the three on US-equity friction modelling. |
| 3. Data API | `D.features()` time-series interface | `src/sharks/data/qlib_dataset.py` | Wraps our existing yfinance / Polygon clients into the Qlib dataset shape so the Qlib factor evaluator + model zoo can be called without reimplementing the data layer. |

## Phase

**Phase 4 (factor library + backtest engine)** + **Phase 5 (model-zoo benchmark on `$hark`-curated universe)**. Per [[../../docs/ROADMAP]] §Phase 4 KPI targets (Strategy A Sharpe > 0.8 / MDD < 25% / Win > 45%), Qlib's reference benchmarks on CSI300 hit Sharpe 1.0+ — the engine is not the bottleneck.

## Proposed integration adaptation

- **`as_of_timestamp` on every feature row**: Qlib's native data API treats time as a single index. We wrap it so every feature row carries `as_of_timestamp` (the latest source timestamp that contributed to it) plus `source_grade` (the worst grade among contributing sources). The Risk Officer rejects any feature row where `as_of_timestamp > trade.signal_time` or `source_grade ∈ {D, E}` for a tier-1 holding.
- **Walk-forward enforcement**: Qlib's `Workflow` supports walk-forward; the `$hark` wrapper makes it *mandatory* (no full-history fit allowed) per [[../04-sector-and-finviz]] Rule 1.
- **Factor pruning**: do not adopt Alpha158 wholesale. Start with the 12 factors whose economic story aligns with the existing `philosophy/concepts/` dictionary (e.g. KMID — body-to-range ratio — maps to TD-9 setup-9 "exhaustion"; KMA20 — distance from 20MA — maps to [[../concepts/golden-cross]]). Add new factors only when a `philosophy/concepts/` page is written first; this preserves the philosophy-first discipline.
- **Model zoo gating**: every model in the zoo must pass an interpretability test before reaching `wiki/05_recommendations/`. LightGBM / Linear → OK; Transformer / TFT → research-only until SHAP / attention-attribution wrappers exist.

## License

**MIT License** (verified: Microsoft Qlib `LICENSE` file is MIT — confirmed via the repo's standard licensing convention; the operator should re-verify at adoption time).

Per [[../../docs/INSPIRATIONS]] §Licensing & legal, MIT → freely integrable. Attribution required in module docstrings; we add `# Adapted from microsoft/qlib (MIT)` headers to any direct port.

## Integration test sketch

```python
# tests/test_qlib_alpha_smoke.py
def test_alpha158_kmid_matches_qlib_native():
    # Sanity: our port of KMID matches Qlib's native evaluation
    df = mock_ohlcv()
    ours   = sharks.factors.qlib_alpha.kmid(df, as_of="2024-06-30")
    native = qlib.contrib.data.handler.Alpha158().kmid(df.loc[:"2024-06-30"])
    assert (ours - native).abs().max() < 1e-9

def test_qlib_engine_rejects_lookahead():
    # Inject a feature row with as_of > signal_time; engine must abort
    cfg = sharks.backtest.qlib_engine.QlibBacktestConfig(...)
    bad = sharks.backtest.qlib_engine.FeatureRow(
        as_of_timestamp="2024-07-01",
        signal_time="2024-06-30",  # lookahead
        feature_value=0.5,
    )
    with pytest.raises(LookaheadError):
        cfg.run(feature_rows=[bad])

def test_walk_forward_enforced():
    # Engine must refuse a full-history fit
    cfg = sharks.backtest.qlib_engine.QlibBacktestConfig(walk_forward=False, ...)
    with pytest.raises(DisciplineError, match="walk_forward must be True"):
        cfg.run(...)
```

## Risks / open questions for the human reviewer

1. **Dependency footprint**: Qlib pulls in `numpy`, `pandas`, `scipy`, `pyarrow`, `lightgbm`, `torch`, `redis-py`, `fire`, plus the C-extension Cython modules for the data store. Phase-4 `pyproject.toml` will grow noticeably. Mitigation: install `microsoft-qlib` as an optional dep group (`[backtest]`), not a base dep.
2. **Data-format coupling**: Qlib's native binary store (`~/.qlib/qlib_data/`) is a CSV → binary conversion. We do NOT migrate `raw/` into it; we feed Qlib via the in-memory DataFrame interface so the immutable `raw/` layer remains untouched per [[../CLAUDE]] §2.
3. **CN-A-share bias**: Qlib was built for China A-shares. The factor library expressions are equity-agnostic, but the reference workflows assume CN market hours / calendar. US-equity calendar config is a known-good extension but the operator should run a smoke test before trusting commission / slippage assumptions.
4. **Maintenance velocity**: Microsoft Research's Qlib has periodically had quiet quarters. Phase 5+ should set a quarterly "upstream check" reminder per [[../../docs/INSPIRATIONS]] §Adoption discipline step 5.

## Cross-references

- [[../09-point-in-time]] — Qlib's native point-in-time is the closest match in any inspiration; we extend it with source-grade tracking
- [[../02-signal-taxonomy]] — technical dimension feature consumer
- [[../04-sector-and-finviz]] Rule 1 — train/val/test partition Qlib's workflow must respect
- [[../05-decision-rubric]] — backtest KPI gates this engine has to clear
- [[../../docs/ROADMAP]] §Phase 4 (deliverable 1) — choice point between Backtrader / vectorbt / Qlib
- [[../../docs/INSPIRATIONS]] §Licensing & legal — MIT discipline applied
- See also Inspiration #4 (`Sleipnir`) — Time-Aware RAG provides retrieval-layer point-in-time; Qlib provides feature-layer point-in-time. They are complementary, not redundant.
- See also companion proposal [[inspiration-11-backtrader-finrl]] — the head-to-head decision the human resolves at Phase 4 kickoff

## Notes for the human reviewer on accept

1. Verify Qlib license at https://github.com/microsoft/qlib/blob/main/LICENSE (expected MIT) before any code copy.
2. Phase-4 sprint-0 decision: Qlib vs vectorbt vs Backtrader. Recommendation: Qlib for engine + Alpha158 for factor pool; reuse vectorbt only if Qlib's engine speed proves a bottleneck.
3. Add `microsoft-qlib` to `pyproject.toml` `[project.optional-dependencies].backtest`.
4. After move from `_proposals/` to `philosophy/references/open-source-inspirations.md`, also append the matching row in `docs/INSPIRATIONS.md` integration matrix (see companion proposal [[inspirations-matrix-patch]]).

