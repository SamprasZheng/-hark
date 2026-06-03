"""$hark side of the cuFOLIO bridge — GPU Mean-CVaR portfolio optimization.

Fetches point-in-time daily CLOSE prices for a ticker list (yfinance), ships them
to NVIDIA cuFOLIO's Mean-CVaR optimizer running in WSL (cuOpt on the RTX 5070, or
CPU clarabel fallback), and returns suggested long-only weights + expected return
+ CVaR. The "what weights / what risk" layer over $hark's "what to hold".

RECOMMEND-ONLY: weights are a research suggestion over a candidate set; the Risk
Officer + evidence gate still govern, and the system never trades. The optimizer
sees only public prices — never account or holding data.

The heavy lifting (RAPIDS/cuOpt) lives in the cuFOLIO WSL venv; this module just
marshals JSON over `wsl`. If WSL/cuFOLIO isn't deployed it returns a clean error.
"""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

WSL_CUFOLIO_DIR = "~/cuFOLIO"
WSL_BRIDGE = "hark_optimize.py"          # ~/cuFOLIO/hark_optimize.py
WSL_UV = "~/.local/bin/uv"


def _wsl_path(win_path: str) -> str:
    """C:\\Users\\x\\f.json -> /mnt/c/Users/x/f.json"""
    p = Path(win_path)
    drive = p.drive.rstrip(":").lower()
    rest = str(p)[len(p.drive):].replace("\\", "/")
    return f"/mnt/{drive}{rest}"


def fetch_closes(tickers: list[str], period: str = "2y") -> tuple[list[str], list[list[float]]]:
    """Aligned daily close prices for the tickers (drops names without data)."""
    import pandas as pd
    import yfinance as yf

    closes = {}
    for t in tickers:
        try:
            h = yf.Ticker(t).history(period=period, auto_adjust=True)
            cs = h["Close"].dropna()
            if len(cs) >= 60:
                closes[t] = cs
        except Exception:
            continue
    if len(closes) < 2:
        return [], []
    df = pd.DataFrame(closes).dropna()
    return list(df.columns), df.values.tolist()


def optimize(tickers: list[str], *, solver: str = "cuopt", w_max: float = 0.20,
             confidence: float = 0.95, risk_aversion: float = 1.0,
             num_scen: int = 3000, fit_type: str = "gaussian",
             period: str = "2y", timeout: int = 240) -> dict:
    """Mean-CVaR optimize over ``tickers``. solver ∈ {cuopt (GPU), clarabel (CPU)}.
    Returns the bridge result dict (ok/weights/expected_return/CVaR/top/…)."""
    cols, prices = fetch_closes(tickers, period=period)
    if len(cols) < 2:
        return {"ok": False, "error": "需要至少 2 檔有價格資料的標的"}

    cfg = {"tickers": cols, "prices": prices, "solver": solver, "return_type": "LOG",
           "w_min": 0.0, "w_max": float(w_max), "confidence": float(confidence),
           "risk_aversion": float(risk_aversion), "num_scen": int(num_scen),
           "fit_type": fit_type}

    tmp = Path(tempfile.gettempdir())
    inp, outp = tmp / "hark_cufolio_in.json", tmp / "hark_cufolio_out.json"
    inp.write_text(json.dumps(cfg), encoding="utf-8")
    if outp.exists():
        outp.unlink()

    win_in, win_out = _wsl_path(str(inp)), _wsl_path(str(outp))
    bash = (f"cd {WSL_CUFOLIO_DIR} && {WSL_UV} run python {WSL_BRIDGE} "
            f"'{win_in}' '{win_out}'")
    try:
        proc = subprocess.run(["wsl", "bash", "-lc", bash],
                              capture_output=True, text=True, timeout=timeout)
    except FileNotFoundError:
        return {"ok": False, "error": "找不到 wsl(此功能需在有 WSL 的本機跑)"}
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": f"cuFOLIO 逾時({timeout}s);減少 tickers 或用 solver=clarabel"}

    if not outp.exists():
        tail = (proc.stderr or proc.stdout or "")[-500:]
        return {"ok": False, "error": "cuFOLIO 無輸出(WSL 環境未部署?)", "detail": tail}
    try:
        res = json.loads(outp.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"ok": False, "error": f"解析 cuFOLIO 輸出失敗:{exc}"}
    res.setdefault("requested", len(tickers))
    res.setdefault("used", len(cols))
    return res
