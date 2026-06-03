"""cuFOLIO ↔ $hark bridge (WSL side).

Runs inside the cuFOLIO uv venv (RAPIDS + cuOpt). Reads {tickers, prices, params}
JSON, runs cuFOLIO's Mean-CVaR optimizer via its own data pipeline
(`utils.calculate_returns` → `generate_cvar_data` → `CVaR`), on the CPU
(`cp.CLARABEL`) or GPU (`cp.CUOPT`), and writes {weights, expected_return, CVaR,…}.

Called by $hark (Windows):
    wsl bash -lc "cd ~/cuFOLIO && uv run python hark_optimize.py <in.json> <out.json>"

recommend-only: suggests weights from point-in-time PRICES; never trades, never
sees account/holding data.
"""

from __future__ import annotations

import json
import os
import sys
import traceback

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.expanduser("~/cuFOLIO"))
from cufolio import cvar_utils, utils                       # noqa: E402
from cufolio.cvar_optimizer import CVaR                     # noqa: E402
from cufolio.cvar_parameters import CvarParameters          # noqa: E402
from cufolio.settings import (                              # noqa: E402
    ReturnsComputeSettings,
    ScenarioGenerationSettings,
)
import cvxpy as cp                                          # noqa: E402

_SOLVERS = {"clarabel": cp.CLARABEL, "cuopt": cp.CUOPT}     # CPU / GPU


def optimize(cfg: dict) -> dict:
    tickers = list(cfg["tickers"])
    prices = np.asarray(cfg["prices"], dtype=float)          # (T, N) close prices
    if prices.ndim != 2 or prices.shape[1] != len(tickers):
        raise ValueError(f"prices must be (T, {len(tickers)}); got {prices.shape}")
    price_df = pd.DataFrame(prices, columns=tickers)

    # 1) returns_dict (mean/cov/returns/regime) via cuFOLIO's own pipeline
    rcs = ReturnsComputeSettings(return_type=cfg.get("return_type", "LOG"), freq=1)
    returns_dict = utils.calculate_returns(price_df, {"name": "live", "range": None}, rcs)

    # 2) scenarios
    scen = ScenarioGenerationSettings(
        num_scen=int(cfg.get("num_scen", 3000)),
        fit_type=cfg.get("fit_type", "gaussian"),            # gaussian | kde | no_fit
    )
    returns_dict = cvar_utils.generate_cvar_data(returns_dict, scen)

    # 3) constraints — long-only, fully invested, no leverage by default
    params = CvarParameters(
        w_min=float(cfg.get("w_min", 0.0)),
        w_max=float(cfg.get("w_max", 0.20)),
        c_min=0.0, c_max=float(cfg.get("c_max", 0.0)),
        L_tar=float(cfg.get("L_tar", 1.0)),
        confidence=float(cfg.get("confidence", 0.95)),
        risk_aversion=float(cfg.get("risk_aversion", 1.0)),
    )

    # 4) optimize on CPU (clarabel) or GPU (cuopt)
    opt = CVaR(returns_dict=returns_dict, cvar_params=params)
    solver_key = cfg.get("solver", "clarabel")
    solver = _SOLVERS.get(solver_key, cp.CLARABEL)
    ss = {"solver": solver, "verbose": False}
    if solver is cp.CUOPT:
        ss.update({"solver_method": "PDLP",
                   "time_limit": int(cfg.get("time_limit", 15)), "optimality": 1e-4})
    result_row, portfolio = opt.solve_optimization_problem(solver_settings=ss, print_results=False)

    w = np.asarray(portfolio.weights, dtype=float).ravel()
    weights = {t: round(float(x), 6) for t, x in zip(portfolio.tickers, w)}
    top = sorted(weights.items(), key=lambda kv: kv[1], reverse=True)

    def _num(key):
        try:
            return round(float(result_row[key]), 6)
        except Exception:
            return None

    return {
        "ok": True, "solver": solver_key, "n_assets": len(tickers),
        "num_scen": int(cfg.get("num_scen", 3000)),
        "weights": weights, "top": top[:15],
        "expected_return": _num("return"), "CVaR": _num("CVaR"),
        "obj": _num("obj"), "solve_time": _num("solve time"),
        "cash": round(float(getattr(portfolio, "cash", 0.0) or 0.0), 6),
    }


def main(in_path: str, out_path: str) -> int:
    try:
        out = optimize(json.load(open(in_path, encoding="utf-8")))
    except Exception as exc:
        out = {"ok": False, "error": f"{type(exc).__name__}: {exc}",
               "trace": traceback.format_exc()[-1800:]}
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(json.dumps({k: out[k] for k in ("ok", "error") if k in out}, ensure_ascii=False))
    return 0 if out.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1], sys.argv[2]))
