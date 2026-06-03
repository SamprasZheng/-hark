# cuFOLIO integration — GPU Mean-CVaR portfolio optimization

[NVIDIA cuFOLIO](https://github.com/NVIDIA-AI-Blueprints/cuFOLIO) is a GPU
Mean-CVaR (Conditional Value-at-Risk) portfolio optimizer built on **cuOpt**
(GPU LP/QP via PDLP), **RAPIDS** (cuDF/cuML), and **cvxpy**. $hark uses it as the
*"what weights / what risk"* layer over its *"what to hold"* screens: given a
candidate ticker set, it suggests a long-only allocation that minimizes the
portfolio's tail loss at a chosen confidence.

**Recommend-only, like the rest of $hark.** Weights are a research suggestion over
a candidate set; the Risk Officer and the evidence gate keep final veto, and the
system never trades. The optimizer sees **only public prices** — never account or
holding data.

## Architecture (Windows ↔ WSL)

cuFOLIO needs CUDA 12 + RAPIDS, which run in **WSL2** on this box; $hark runs on
**Windows**. So the integration is a thin JSON bridge over `wsl`:

```
Windows ($hark)                         WSL2 (cuFOLIO uv venv, RTX 5070)
─────────────────────────────          ──────────────────────────────────
src/sharks/scoring/cufolio_optimize.py
  fetch_closes()  yfinance prices
  optimize()  ── JSON {tickers,prices,  ──▶  ~/cuFOLIO/hark_optimize.py
              solver,w_max,…} via temp        utils.calculate_returns()
              file + `wsl bash -lc`           cvar_utils.generate_cvar_data()
                                              CVaR(...).solve_optimization_problem()
              ◀── JSON {ok,weights,        ◀──  solver = cp.CUOPT (GPU) | cp.CLARABEL (CPU)
                  expected_return,CVaR,top}
```

- `integrations/cufolio/hark_optimize.py` — **WSL-side** bridge. Copied into
  `~/cuFOLIO/`. Reads `{tickers, prices, …}`, runs cuFOLIO's own data pipeline
  (`calculate_returns` → `generate_cvar_data` → `CVaR`), writes
  `{weights, expected_return, CVaR, top, solve_time, …}`.
- `src/sharks/scoring/cufolio_optimize.py` — **Windows-side** caller. Fetches
  aligned daily closes (yfinance), marshals JSON over `wsl`, returns the result.
- `integrations/cufolio/_test_bridge.py` — synthetic-price smoke test for both
  solvers (run inside `~/cuFOLIO`).
- `integrations/cufolio/_nbdump.py` — helper to dump cuFOLIO example-notebook cells.

## Deploy (one-time, WSL)

```bash
# in WSL — clone + sync the CUDA-12 RAPIDS/cuOpt env (uv)
git clone https://github.com/NVIDIA-AI-Blueprints/cuFOLIO ~/cuFOLIO
cd ~/cuFOLIO
UV_HTTP_TIMEOUT=900 UV_CONCURRENT_DOWNLOADS=4 ~/.local/bin/uv sync   # ~124 pkgs

# copy the bridge in + smoke-test both solvers
cp '/mnt/d/DOT/$hark/integrations/cufolio/hark_optimize.py'  ~/cuFOLIO/
cp '/mnt/d/DOT/$hark/integrations/cufolio/_test_bridge.py'   ~/cuFOLIO/
~/.local/bin/uv run python _test_bridge.py
# => "clarabel" and "cuopt" each print ok:true + weights
```

After editing `hark_optimize.py` on the Windows side, re-copy it into `~/cuFOLIO/`
(the Windows caller assumes the latest copy is there).

## Use from $hark (Windows)

```python
from sharks.scoring.cufolio_optimize import optimize

res = optimize(["MSFT", "META", "NVDA", "AVGO", "AMD", "GOOGL", "AMZN", "AAPL"],
               solver="cuopt",   # GPU; "clarabel" = CPU fallback
               w_max=0.25)        # per-name cap
# -> {"ok": True, "solver": "cuopt", "expected_return": …, "CVaR": …,
#     "weights": {...}, "top": [["AVGO",0.25], ...], "solve_time": 0.35, ...}
```

### From Discord

```
/optimize                       # software/AI dip-buy basket, GPU, cap 25%
/optimize universe:megacap      # large-cap tech weights
/optimize tickers:AAPL,MSFT,NVDA,AVGO  cap:0.3  solver:cuopt
/optimize universe:crypto       # BTC/ETH/SOL/DOT auto-mapped to -USD
```

Renders the suggested long-only weights (proportional bars), the ≈annualized
expected return, the daily CVaR@95%, the solve device/time, and a recommend-only
footer. Crypto symbols are mapped to yfinance `-USD` pairs automatically; names
without ≥60 trading days of data are dropped.

## Parameters

| field            | default    | meaning                                            |
|------------------|------------|----------------------------------------------------|
| `solver`         | `cuopt`    | `cuopt` = GPU cuOpt (PDLP) · `clarabel` = CPU cvxpy |
| `w_max`          | `0.20`     | per-name weight cap (long-only, `w_min=0`)          |
| `confidence`     | `0.95`     | CVaR tail confidence                                |
| `risk_aversion`  | `1.0`      | mean-vs-CVaR trade-off                              |
| `num_scen`       | `3000`     | Monte-Carlo scenarios for the CVaR estimate         |
| `fit_type`       | `gaussian` | scenario fit: `gaussian` \| `kde` \| `no_fit`        |
| `period`         | `2y`       | yfinance lookback for the price matrix              |

## Verified on this box

RTX 5070 (Blackwell), WSL2, CUDA 12. Both solvers produce valid long-only
Mean-CVaR weights; GPU `cuopt` path solves an 8-name problem in ~0.3 s. If WSL or
cuFOLIO isn't deployed, `optimize()` returns `{"ok": False, "error": …}` rather
than raising.
