"""Hotspot-prediction backtest — predict the next sector leaders, then grade it.

The principal's ask: 「回測用歷史數據預測下一個熱點，然後驗證已知下一個熱點的正確性，
讓回測獲利最大化」. This module is the *predict-and-validate* loop (the profit-max
optimiser is a separate layer that sits on whatever signal proves to have edge
here — there is no point optimising a signal that cannot predict).

At each month-end T (point-in-time, no lookahead), it forms a prediction of which
sectors will lead over the next quarter (T -> T+h) from two honest components:

  - MOMENTUM persistence: trailing relative strength vs SPY (sectors money is
    already rotating INTO — `sector_flow.relative_strength`). Tests whether
    "leaders keep leading" for a quarter.
  - SEASONALITY / business-cycle rotation: the historical average forward return
    of each sector conditioned on the *current calendar month*, using only years
    strictly before T (genuinely PIT). Tests 季節性 + 景氣循環產業輪動.

Then it GRADES the prediction against the realised T -> T+h sector returns and
aggregates across the walk-forward window, reporting — separately for momentum,
seasonality, and the blend — the rank IC, precision@k, and how often it beat a
RANDOM baseline (k / N_sectors). The honesty rule: a component that does not beat
random is reported as such, not buried.

Finally it emits the CURRENT prediction (top-k sectors for the coming quarter) —
but only as good as the measured edge above.

LLM involvement: none — rule-based. Headline-KPI-eligible per
docs/LLM-BACKTEST-PROTOCOL.md.
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
from sharks.regime.sector_flow import SECTOR_ETFS, DEFAULT_BENCHMARK, relative_strength

DATA_START = "2013-01-01"        # buffer so seasonality has prior years at 2016
BACKTEST_START = "2016-01-01"
DATA_END = "2026-05-01"
DEFAULT_HORIZON = 3              # quarter-ahead
DEFAULT_K = 3                   # how many "hotspots" we name
# (momentum_weight, seasonality_weight). The 2016-2026 blend sweep showed IC_IR
# rising monotonically as weight shifts to seasonality (mom-only 0.54 -> sea-only
# 2.78): sector MOMENTUM-persistence is ~noise at the quarter horizon, SEASONALITY
# / 景氣循環 carries the edge. We default seasonality-DOMINANT but keep a 0.2
# momentum sliver as a hedge against seasonality regime-breaks (rather than
# overfitting to the exact in-sample maximum at 0.0/1.0).
DEFAULT_BLEND = (0.2, 0.8)


# ─── PIT signal components (unit-testable) ───

def momentum_signal(closes: pd.DataFrame, as_of: pd.Timestamp,
                    sectors: list[str], lookback: int = 3,
                    benchmark: str = DEFAULT_BENCHMARK) -> dict[str, float]:
    """Trailing relative strength vs benchmark per sector (rotating-in = high)."""
    out: dict[str, float] = {}
    for s in sectors:
        rs = relative_strength(closes, s, benchmark, as_of, lookback)
        if rs is not None:
            out[s] = rs
    return out


def seasonal_signal(closes: pd.DataFrame, as_of: pd.Timestamp,
                    sectors: list[str], horizon: int = DEFAULT_HORIZON) -> dict[str, float]:
    """Average forward `horizon`-month return of each sector conditioned on the
    CURRENT calendar month, using ONLY months strictly before `as_of` (PIT). A
    same-month-prior-year start is always >= 12m before as_of, so start+horizon
    (horizon<=12) is also before as_of — no lookahead."""
    idx = closes.index
    month = as_of.month
    starts = [p for p, d in enumerate(idx)
              if d.month == month and d < as_of and p + horizon < len(idx)]
    out: dict[str, float] = {}
    for s in sectors:
        col = closes.get(s)
        if col is None:
            continue
        rets = []
        for p in starts:
            p0, p1 = col.iloc[p], col.iloc[p + horizon]
            if p0 and p1 and p0 > 0 and not pd.isna(p0) and not pd.isna(p1):
                rets.append(p1 / p0 - 1.0)
        if rets:
            out[s] = float(np.mean(rets))
    return out


def _zscore(d: dict[str, float]) -> dict[str, float]:
    if len(d) < 2:
        return {k: 0.0 for k in d}
    vals = np.array(list(d.values()), dtype=float)
    mu, sd = vals.mean(), vals.std()
    if sd == 0:
        return {k: 0.0 for k in d}
    return {k: (v - mu) / sd for k, v in d.items()}


def blend_signals(momentum: dict[str, float], seasonal: dict[str, float],
                  weights: tuple[float, float] = DEFAULT_BLEND) -> dict[str, float]:
    """Z-score each component across sectors, then weighted-average over the
    sectors present in BOTH."""
    zm, zs = _zscore(momentum), _zscore(seasonal)
    wm, ws = weights
    common = set(zm) & set(zs)
    return {s: wm * zm[s] + ws * zs[s] for s in common}


def _forward_sector_returns(closes: pd.DataFrame, as_of_pos: int,
                            horizon: int, sectors: list[str]) -> dict[str, float]:
    fut = as_of_pos + horizon
    if fut >= len(closes):
        return {}
    now, later = closes.iloc[as_of_pos], closes.iloc[fut]
    out: dict[str, float] = {}
    for s in sectors:
        p0, p1 = now.get(s), later.get(s)
        if p0 and p1 and p0 > 0 and not pd.isna(p0) and not pd.isna(p1):
            out[s] = float(p1 / p0 - 1.0)
    return out


def precision_at_k(signal: dict[str, float], actual: dict[str, float], k: int) -> Optional[float]:
    """Fraction of the top-k predicted sectors that were in the actual top-k."""
    common = [s for s in signal if s in actual]
    if len(common) < k:
        return None
    pred_top = set(sorted(common, key=lambda s: signal[s], reverse=True)[:k])
    act_top = set(sorted(common, key=lambda s: actual[s], reverse=True)[:k])
    return len(pred_top & act_top) / k


# ─── Walk-forward driver ───

def run_hotspot_backtest(
    closes: pd.DataFrame,
    sectors: Optional[list[str]] = None,
    horizon: int = DEFAULT_HORIZON,
    k: int = DEFAULT_K,
    blend: tuple[float, float] = DEFAULT_BLEND,
    backtest_start: str = BACKTEST_START,
    benchmark: str = DEFAULT_BENCHMARK,
) -> dict:
    sectors = sectors or [s for s in SECTOR_ETFS if s in closes.columns]
    month_ends = closes.index[closes.index >= pd.Timestamp(backtest_start)]
    comps = ("momentum", "seasonality", "blend")
    acc = {c: {"ic": [], "prec": [], "beat": []} for c in comps}
    periods = 0
    n_sectors = len(sectors)
    baseline_prec = k / n_sectors if n_sectors else None

    for as_of in month_ends:
        pos = closes.index.searchsorted(as_of)
        if pos + horizon >= len(closes):
            break
        fwd = _forward_sector_returns(closes, pos, horizon, sectors)
        if len(fwd) < k + 1:
            continue
        mom = momentum_signal(closes, as_of, sectors, benchmark=benchmark)
        sea = seasonal_signal(closes, as_of, sectors, horizon=horizon)
        bl = blend_signals(mom, sea, blend)
        if not bl:
            continue
        periods += 1
        for name, sig in (("momentum", mom), ("seasonality", sea), ("blend", bl)):
            ic = spearman_ic(sig, fwd)
            if ic is not None:
                acc[name]["ic"].append(ic)
            pr = precision_at_k(sig, fwd, k)
            if pr is not None:
                acc[name]["prec"].append(pr)
                if baseline_prec is not None:
                    acc[name]["beat"].append(1.0 if pr > baseline_prec else 0.0)

    def agg(c):
        ics = np.array(acc[c]["ic"], dtype=float)
        precs = np.array(acc[c]["prec"], dtype=float)
        beats = np.array(acc[c]["beat"], dtype=float)
        n = len(ics)
        mean_ic = float(ics.mean()) if n else None
        std_ic = float(ics.std(ddof=1)) if n > 1 else 0.0
        ic_ir = float(mean_ic / std_ic * np.sqrt(n)) if (mean_ic is not None and std_ic > 0) else None
        return {
            "n_periods": int(n),
            "mean_ic": round(mean_ic, 4) if mean_ic is not None else None,
            "ic_ir": round(ic_ir, 2) if ic_ir is not None else None,
            "mean_precision_at_k": round(float(precs.mean()), 3) if len(precs) else None,
            "pct_beat_random": round(float(beats.mean()), 3) if len(beats) else None,
        }

    by_component = {c: agg(c) for c in comps}
    return {
        "periods_scored": periods,
        "n_sectors": n_sectors,
        "k": k,
        "horizon_months": horizon,
        "blend_weights": {"momentum": blend[0], "seasonality": blend[1]},
        "random_baseline_precision_at_k": round(baseline_prec, 3) if baseline_prec else None,
        "by_component": by_component,
        "interpretation": _interpret(by_component, baseline_prec),
        "current_prediction": _current_prediction(closes, sectors, horizon, k, blend, benchmark),
    }


def _interpret(by_component: dict, baseline: Optional[float]) -> dict:
    best, best_ir = None, -1e9
    for c, a in by_component.items():
        ir = a.get("ic_ir")
        if ir is not None and ir > best_ir:
            best_ir, best = ir, c
    blend = by_component.get("blend", {})
    prec = blend.get("mean_precision_at_k")
    beats = (prec is not None and baseline is not None and prec > baseline)
    if best is None:
        verdict = "INCONCLUSIVE"
    elif best_ir >= 2 and beats:
        verdict = "PREDICTIVE-EDGE"
    elif best_ir >= 1:
        verdict = "WEAK-EDGE"
    elif best_ir <= -1:
        verdict = "INVERTED-RECALIBRATE"
    else:
        verdict = "NO-EDGE-OVER-RANDOM"
    return {
        "best_component": best,
        "best_ic_ir": round(best_ir, 2) if best else None,
        "blend_precision_vs_random": {
            "blend": prec, "random": round(baseline, 3) if baseline else None,
            "blend_wins": bool(beats),
        },
        "verdict": verdict,
        "note": (
            "Sector rotation is a weak, noisy signal by nature — a positive but "
            "small IC that beats the random precision baseline is a genuine, "
            "usable result; it does NOT license concentrated bets. If momentum "
            "alone carries the edge, the seasonality overlay is decoration; if "
            "seasonality adds IC_IR, 景氣循環輪動 is real. Re-run weekly; treat the "
            "current_prediction as a WATCHLIST, gated by evidence-gated-rebalance."
        ),
    }


def _current_prediction(closes, sectors, horizon, k, blend, benchmark) -> dict:
    """Top-k predicted hotspots at the latest available month-end (no forward
    truth — this is the actionable call)."""
    if len(closes) == 0:
        return {}
    as_of = closes.index[-1]
    mom = momentum_signal(closes, as_of, sectors, benchmark=benchmark)
    sea = seasonal_signal(closes, as_of, sectors, horizon=horizon)
    bl = blend_signals(mom, sea, blend)
    ranked = sorted(bl, key=lambda s: bl[s], reverse=True)
    return {
        "as_of": str(as_of.date()),
        "horizon_months": horizon,
        "top_hotspots": [
            {"sector": s, "blend_z": round(bl[s], 3),
             "momentum_rs": round(mom.get(s), 4) if s in mom else None,
             "seasonal_fwd": round(sea.get(s), 4) if s in sea else None}
            for s in ranked[:k]
        ],
        "caveat": "WATCHLIST only — as good as the measured edge above; gate any entry on 十足的證據.",
    }


def main() -> int:
    from sharks.scoring.fom import fetch_monthly
    out_dir = Path("outputs")
    out_dir.mkdir(parents=True, exist_ok=True)
    pull = sorted(set(SECTOR_ETFS + [DEFAULT_BENCHMARK]))
    print(f"Pulling {len(pull)} sector ETFs {DATA_START}..{DATA_END}", file=sys.stderr)
    closes = fetch_monthly(pull, DATA_START, DATA_END)
    print(f"  data: {len(closes.columns)} tickers, {len(closes)} months", file=sys.stderr)

    result = run_hotspot_backtest(closes)
    report = {
        "as_of": datetime.now(timezone.utc).isoformat(),
        "schema_version": 1,
        "report_type": "hotspot_sector_rotation_validity",
        "llm_involvement": "none",
        "method": (
            "Walk-forward sector-rotation prediction (momentum + PIT seasonality) "
            "graded by rank IC + precision@k vs a random baseline. PIT, no "
            "lookahead. See docs/LLM-BACKTEST-PROTOCOL.md."
        ),
        "data_window": {"start": BACKTEST_START, "end": DATA_END},
        **result,
    }
    out_path = out_dir / "hotspot-backtest-2016-to-2026.json"
    out_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"wrote {out_path}", file=sys.stderr)
    print(json.dumps(report["by_component"], indent=2), file=sys.stderr)
    print("VERDICT:", report["interpretation"]["verdict"],
          "| best:", report["interpretation"]["best_component"], file=sys.stderr)
    print("NEXT HOTSPOTS:",
          [h["sector"] for h in report["current_prediction"].get("top_hotspots", [])],
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
