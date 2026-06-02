"""Daily-bar horizon calibration — which signal works at 1d / 1w / 1m?

The principal's ladder asked for week + day top-3, and correctly intuited that
「不同時間跨度的參數可能不同」. The monthly FOM scorer cannot answer that — its
lookbacks count months. This module is the DAILY-native counterpart: on daily
bars it builds several signals and measures, walk-forward and PIT, which one has
predictive edge at each forward horizon (1 day / 5 days ≈ week / 21 days ≈ month).

Signals (all computed from data <= day t, no lookahead):
  - mom_60 : 60-trading-day trailing return (intermediate momentum)
  - mom_20 : 20-day trailing return (fast momentum)
  - rev_5  : NEGATIVE of the 5-day return (short-term REVERSAL — buy recent losers)
  - rev_1  : NEGATIVE of the 1-day return (overnight/1-day reversal)

The well-documented prior (Jegadeesh 1990 / Lehmann 1990): at 1-5 day horizons
short-term REVERSAL dominates (winners give back, losers bounce); momentum only
emerges at multi-week+ horizons. If the data shows that here, it both validates
the principal's "params differ by horizon" intuition AND warns that a daily/weekly
top-3 built on momentum would be backwards.

Reuses `spearman_ic` from fom_validation_backtest. llm_involvement: none.
"""

from __future__ import annotations

import json
import sys
import warnings
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import numpy as np
import pandas as pd

from sharks.backtest.fom_validation_backtest import spearman_ic
from sharks.backtest.nasdaq100_calibration import NDX_PROXY

DATA_START = "2015-01-01"
DATA_END = "2026-05-01"
SAMPLE_EVERY = 5                 # sample every 5 trading days (cut compute + autocorr)
HORIZONS = (1, 5, 21)            # day, ~week, ~month
SIGNALS = ("mom_60", "mom_20", "rev_5", "rev_1")


def fetch_daily(tickers: list[str], start: str, end: str) -> pd.DataFrame:
    """Daily close frame (columns = tickers). Network — yfinance."""
    import yfinance as yf
    raw = yf.download(tickers, start=start, end=end, interval="1d",
                      auto_adjust=True, progress=False)
    close = raw["Close"] if isinstance(raw.columns, pd.MultiIndex) else raw[["Close"]]
    if isinstance(close, pd.Series):
        close = close.to_frame(tickers[0])
    return close.dropna(how="all")


def _trailing_return(closes: pd.DataFrame, pos: int, lookback: int) -> dict[str, float]:
    if pos - lookback < 0:
        return {}
    now, past = closes.iloc[pos], closes.iloc[pos - lookback]
    out = {}
    for t in closes.columns:
        a, b = past.get(t), now.get(t)
        if a and b and a > 0 and not pd.isna(a) and not pd.isna(b):
            out[t] = float(b / a - 1.0)
    return out


def signal_values(closes: pd.DataFrame, pos: int, name: str) -> dict[str, float]:
    if name == "mom_60":
        return _trailing_return(closes, pos, 60)
    if name == "mom_20":
        return _trailing_return(closes, pos, 20)
    if name == "rev_5":
        return {t: -v for t, v in _trailing_return(closes, pos, 5).items()}
    if name == "rev_1":
        return {t: -v for t, v in _trailing_return(closes, pos, 1).items()}
    raise ValueError(f"unknown signal {name!r}")


def _forward(closes: pd.DataFrame, pos: int, horizon: int) -> dict[str, float]:
    fut = pos + horizon
    if fut >= len(closes):
        return {}
    now, later = closes.iloc[pos], closes.iloc[fut]
    out = {}
    for t in closes.columns:
        a, b = now.get(t), later.get(t)
        if a and b and a > 0 and not pd.isna(a) and not pd.isna(b):
            out[t] = float(b / a - 1.0)
    return out


def _aggregate(ics: list[float]) -> dict:
    arr = np.array([x for x in ics if x is not None], dtype=float)
    n = len(arr)
    if n == 0:
        return {"n": 0, "mean_ic": None, "ic_ir": None, "pct_positive": None}
    mean_ic = float(arr.mean())
    std = float(arr.std(ddof=1)) if n > 1 else 0.0
    ir = float(mean_ic / std * np.sqrt(n)) if std > 0 else None
    return {"n": n, "mean_ic": round(mean_ic, 4),
            "ic_ir": round(ir, 2) if ir is not None else None,
            "pct_positive": round(float((arr > 0).mean()), 3)}


def run_daily_horizons(closes: pd.DataFrame, signals=SIGNALS, horizons=HORIZONS,
                       sample_every: int = SAMPLE_EVERY, start_pos: int = 60) -> dict:
    acc = {s: {h: [] for h in horizons} for s in signals}
    n = len(closes)
    for pos in range(start_pos, n - max(horizons), sample_every):
        sigs = {s: signal_values(closes, pos, s) for s in signals}
        fwds = {h: _forward(closes, pos, h) for h in horizons}
        for s in signals:
            for h in horizons:
                if sigs[s] and fwds[h]:
                    ic = spearman_ic(sigs[s], fwds[h])
                    if ic is not None:
                        acc[s][h].append(ic)
    by_signal = {s: {f"{h}d": _aggregate(acc[s][h]) for h in horizons} for s in signals}
    # best signal per horizon by IC_IR
    best = {}
    for h in horizons:
        ranked = sorted(
            signals,
            key=lambda s: (by_signal[s][f"{h}d"]["ic_ir"] if by_signal[s][f"{h}d"]["ic_ir"] is not None else -1e9),
            reverse=True)
        best[f"{h}d"] = {"signal": ranked[0],
                         "ic_ir": by_signal[ranked[0]][f"{h}d"]["ic_ir"]}
    return {"by_signal": by_signal, "best_per_horizon": best,
            "interpretation": _interpret(best)}


def _interpret(best: dict) -> dict:
    msgs = []
    for h, b in best.items():
        s = b["signal"]
        kind = "REVERSAL (buy recent losers)" if s.startswith("rev") else "MOMENTUM (buy recent winners)"
        msgs.append(f"{h}: best = {s} → {kind} (IC_IR {b['ic_ir']})")
    return {
        "per_horizon": msgs,
        "note": (
            "If short horizons (1d/5d) favour rev_* and longer (21d) favours mom_*, "
            "the classic short-term-reversal → momentum transition holds: a "
            "weekly/daily top-3 must use REVERSAL, not momentum — the opposite of "
            "the monthly book. This is the daily proof of 不同時間跨度參數不同. Edges "
            "at daily horizon are small and costs (spread/slippage) are large — treat "
            "as research, not a license to day-trade."
        ),
    }


def main() -> int:
    out_dir = Path("outputs")
    out_dir.mkdir(parents=True, exist_ok=True)
    pull = sorted(set(NDX_PROXY))
    print(f"Pulling DAILY {len(pull)} tickers {DATA_START}..{DATA_END}", file=sys.stderr)
    closes = fetch_daily(pull, DATA_START, DATA_END)
    print(f"  data: {len(closes.columns)} tickers, {len(closes)} trading days", file=sys.stderr)
    result = run_daily_horizons(closes)
    report = {
        "as_of": datetime.now(timezone.utc).isoformat(),
        "schema_version": 1,
        "report_type": "daily_horizon_calibration",
        "llm_involvement": "none",
        "data_window": {"start": DATA_START, "end": DATA_END},
        "sample_every_days": SAMPLE_EVERY,
        **result,
    }
    out_path = out_dir / "daily-horizon-2015-to-2026.json"
    out_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"wrote {out_path}", file=sys.stderr)
    for m in result["interpretation"]["per_horizon"]:
        print("  " + m, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
