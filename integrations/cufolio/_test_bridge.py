"""Smoke test: synthetic prices -> Mean-CVaR weights, on CPU (clarabel) and
GPU (cuopt). Run inside ~/cuFOLIO via uv."""
import json

import numpy as np

import hark_optimize

rng = np.random.default_rng(0)
T, N = 500, 5
tickers = ["AAA", "BBB", "CCC", "DDD", "EEE"]
mu = np.array([0.0008, 0.0005, 0.0010, 0.0003, 0.0007])
sig = np.array([0.015, 0.012, 0.020, 0.010, 0.018])
rets = rng.normal(mu, sig, size=(T, N))
prices = 100 * np.cumprod(1 + rets, axis=0)                 # synthetic close prices
base = {"tickers": tickers, "prices": prices.tolist(), "w_max": 0.4, "num_scen": 1500}

for solver in ("clarabel", "cuopt"):
    cfg = dict(base, solver=solver)
    try:
        out = hark_optimize.optimize(cfg)
        keep = {k: out.get(k) for k in
                ("ok", "solver", "expected_return", "CVaR", "solve_time", "top")}
        print(f"=== {solver} ===")
        print(json.dumps(keep, ensure_ascii=False))
    except Exception as exc:
        import traceback
        print(f"=== {solver} === EXC: {type(exc).__name__}: {exc}")
        print(traceback.format_exc()[-700:])
