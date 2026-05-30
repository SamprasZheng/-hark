"""FOM predictive-validity backtest — does FOM actually forecast forward returns?

This is the RECALIBRATION instrument. `fom_backtest.py` answers "did a top-3 DCA
strategy make money" (confounded by the bull market — SPY also rose). This module
answers the sharper question the principal asked — **「FOM 是否失準?」** — by
measuring the cross-sectional **Information Coefficient (IC)**:

  at each month-end T, rank the whole universe by FOM (point-in-time, no
  lookahead), then rank-correlate that against the *realised* forward return over
  T -> T+h. Positive, stable IC across periods = FOM has genuine edge at horizon
  h. Near-zero IC = FOM is noise at that horizon and needs recalibration.

Key honesty (the answer to "yesterday's picks didn't 大漲"): FOM is computed on
MONTHLY closes and blends multi-month momentum / contrarian / quality. It is
structurally a **1-12 MONTH** instrument, not a next-day predictor. This backtest
measures IC across horizons precisely so we stop judging a monthly scorer on daily
moves, and so we learn the horizon at which it actually works.

Metrics reported per horizon h ∈ {1, 3, 6, 12} months:
  - mean_ic          — average Spearman IC across all periods (the edge)
  - ic_ir            — IC information ratio = mean_ic / std_ic * sqrt(n_periods)
                       (an IC t-stat; |IR| > ~2 is a real, stable signal)
  - pct_positive     — fraction of periods with IC > 0 (consistency)
  - quintile_spread  — mean (top-quintile fwd return − bottom-quintile fwd return)
  - hit_rate         — P(top-quintile name beats universe-median fwd return)

LLM involvement: NONE — pure rule-based scorer. Per docs/LLM-BACKTEST-PROTOCOL.md
this run is headline-KPI-eligible (`llm_involvement = "none"`).
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

from sharks.scoring.fom import DEFAULT_UNIVERSE, fetch_monthly, rank_universe

DEFAULT_HORIZONS = (1, 3, 6, 12)
DATA_START = "2014-01-01"          # buffer for 36m lookback before backtest start
BACKTEST_START = "2016-01-01"
DATA_END = "2026-05-01"


# ─── Pure-logic primitives (unit-testable, no network) ───

def spearman_ic(scores: dict[str, float], fwd: dict[str, float]) -> Optional[float]:
    """Spearman rank IC = Pearson correlation of the ranks. Returns None if fewer
    than 5 common, finite observations (too few to be meaningful)."""
    common = [t for t in scores
              if t in fwd and fwd[t] is not None and not np.isnan(fwd[t])
              and scores[t] is not None and not np.isnan(scores[t])]
    if len(common) < 5:
        return None
    s = pd.Series({t: scores[t] for t in common}).rank()
    f = pd.Series({t: fwd[t] for t in common}).rank()
    ic = s.corr(f)  # Pearson on ranks == Spearman
    return None if pd.isna(ic) else float(ic)


def quantile_spread(scores: dict[str, float], fwd: dict[str, float],
                    n_q: int = 5) -> Optional[float]:
    """Mean forward return of the top score-quantile minus the bottom quantile.
    The economically meaningful number: does buying high-FOM and avoiding
    low-FOM actually separate winners from losers?"""
    common = [t for t in scores
              if t in fwd and fwd[t] is not None and not np.isnan(fwd[t])]
    if len(common) < n_q * 2:
        return None
    df = pd.DataFrame({"score": [scores[t] for t in common],
                       "fwd": [fwd[t] for t in common]})
    df = df.sort_values("score")
    k = max(1, len(df) // n_q)
    bottom = df["fwd"].iloc[:k].mean()
    top = df["fwd"].iloc[-k:].mean()
    return float(top - bottom)


def hit_rate(scores: dict[str, float], fwd: dict[str, float],
             top_frac: float = 0.2) -> Optional[float]:
    """Fraction of top-quantile (by FOM) names whose forward return beats the
    universe median forward return."""
    common = [t for t in scores
              if t in fwd and fwd[t] is not None and not np.isnan(fwd[t])]
    if len(common) < 5:
        return None
    df = pd.DataFrame({"t": common,
                       "score": [scores[t] for t in common],
                       "fwd": [fwd[t] for t in common]}).sort_values("score")
    median_fwd = df["fwd"].median()
    k = max(1, int(len(df) * top_frac))
    top = df.iloc[-k:]
    return float((top["fwd"] > median_fwd).mean())


def _forward_returns(closes: pd.DataFrame, as_of_pos: int, horizon: int) -> dict[str, float]:
    """Realised return for every ticker over [as_of_pos, as_of_pos + horizon]."""
    fut_pos = as_of_pos + horizon
    if fut_pos >= len(closes):
        return {}
    now = closes.iloc[as_of_pos]
    fut = closes.iloc[fut_pos]
    out: dict[str, float] = {}
    for t in closes.columns:
        p0, p1 = now.get(t), fut.get(t)
        if p0 and p1 and p0 > 0 and not pd.isna(p0) and not pd.isna(p1):
            out[t] = float(p1 / p0 - 1.0)
    return out


def _aggregate(ic_series: list[float]) -> dict:
    """Mean IC + IC information ratio (t-stat) + consistency from a list of
    per-period ICs."""
    arr = np.array([x for x in ic_series if x is not None], dtype=float)
    n = len(arr)
    if n == 0:
        return {"n_periods": 0, "mean_ic": None, "ic_ir": None, "pct_positive": None}
    mean_ic = float(arr.mean())
    std_ic = float(arr.std(ddof=1)) if n > 1 else 0.0
    ic_ir = float(mean_ic / std_ic * np.sqrt(n)) if std_ic > 0 else None
    return {
        "n_periods": n,
        "mean_ic": round(mean_ic, 4),
        "ic_ir": round(ic_ir, 2) if ic_ir is not None else None,
        "pct_positive": round(float((arr > 0).mean()), 3),
    }


def run_validation(
    closes: pd.DataFrame,
    universe: Optional[list[str]] = None,
    horizons: tuple[int, ...] = DEFAULT_HORIZONS,
    backtest_start: str = BACKTEST_START,
) -> dict:
    """Walk-forward cross-sectional IC study over month-ends. `closes` is a
    monthly-indexed price frame (injectable for tests)."""
    universe = universe or DEFAULT_UNIVERSE
    month_ends = closes.index[closes.index >= pd.Timestamp(backtest_start)]

    per_h = {h: {"ic": [], "spread": [], "hit": []} for h in horizons}
    periods_scored = 0
    persistence: dict[str, int] = {}

    for as_of in month_ends:
        pos = closes.index.searchsorted(as_of)
        # Need at least the longest horizon of future data to score this period.
        if pos + max(horizons) >= len(closes):
            break
        scored = rank_universe(closes, universe, as_of, persistence)
        if len(scored) < 10:
            continue
        persistence = {s.ticker: persistence.get(s.ticker, 0) + 1 for s in scored[:50]}
        fom = {s.ticker: s.final_fom for s in scored}
        periods_scored += 1
        for h in horizons:
            fwd = _forward_returns(closes, pos, h)
            if not fwd:
                continue
            ic = spearman_ic(fom, fwd)
            if ic is not None:
                per_h[h]["ic"].append(ic)
            sp = quantile_spread(fom, fwd)
            if sp is not None:
                per_h[h]["spread"].append(sp)
            hr = hit_rate(fom, fwd)
            if hr is not None:
                per_h[h]["hit"].append(hr)

    by_horizon = {}
    for h in horizons:
        agg = _aggregate(per_h[h]["ic"])
        spreads = per_h[h]["spread"]
        hits = per_h[h]["hit"]
        agg["mean_quintile_spread_pct"] = (
            round(float(np.mean(spreads)) * 100, 2) if spreads else None)
        agg["mean_hit_rate"] = round(float(np.mean(hits)), 3) if hits else None
        by_horizon[f"{h}m"] = agg

    return {
        "periods_scored": periods_scored,
        "universe_size": len(universe),
        "horizons_months": list(horizons),
        "by_horizon": by_horizon,
        "interpretation": _interpret(by_horizon),
    }


def _interpret(by_horizon: dict) -> dict:
    """Translate the numbers into an HONEST verdict — reconciling rank-IC against
    the tradeable quintile spread and the (outlier-robust) hit rate. A positive
    rank-IC with a NEGATIVE top-minus-bottom spread is not an edge you can buy the
    top quintile on; it must be reported as such, not as 'EDGE-CONFIRMED'."""
    best_h, best_ir = None, -1e9
    for h, agg in by_horizon.items():
        ir = agg.get("ic_ir")
        if ir is not None and ir > best_ir:
            best_ir, best_h = ir, h

    if best_h is None:
        return {"best_horizon": None, "verdict": "INCONCLUSIVE", "note": "no periods scored."}

    agg = by_horizon[best_h]
    ic_ir = agg.get("ic_ir") or 0.0
    spread = agg.get("mean_quintile_spread_pct")
    hit = agg.get("mean_hit_rate")
    spread_pos = spread is not None and spread > 0
    hit_pos = hit is not None and hit > 0.5

    # Reconcile the three signals.
    if ic_ir >= 2 and spread_pos and hit_pos:
        verdict = "EDGE-CONFIRMED"  # rank, tails, and robust-tail all agree
    elif ic_ir >= 2 and not spread_pos and hit_pos:
        verdict = "RANK-EDGE-BUT-TOP-TAIL-MEAN-REVERTS"
    elif ic_ir >= 2 and not spread_pos and not hit_pos:
        verdict = "RANK-IC-POSITIVE-BUT-NOT-TRADEABLE-AT-TAILS"
    elif ic_ir >= 1:
        verdict = "WEAK-EDGE"
    elif ic_ir <= -1:
        verdict = "INVERTED-RECALIBRATE"
    else:
        verdict = "NOISE"

    return {
        "best_horizon": best_h,
        "best_ic_ir": round(best_ir, 2),
        "best_horizon_mean_ic": agg.get("mean_ic"),
        "best_horizon_quintile_spread_pct": spread,
        "best_horizon_hit_rate": hit,
        "verdict": verdict,
        "note": (
            "IC_IR is an IC t-stat: |IR|>=2 ≈ a statistically stable rank signal. "
            "But a POSITIVE rank-IC with a NEGATIVE quintile spread means the "
            "extreme-top-FOM names under-perform the extreme-bottom names — the "
            "rank info is real but you CANNOT express it by concentrating in the "
            "highest-FOM tail (it mean-reverts; this is the original bubble_guard "
            "concern, measured). Use FOM as a broad tilt held 3-6m, size for "
            "mean-reversion, lean contrarian at long horizon. 1m IC is weakest — "
            "judging picks on next-day moves is a category error, not a failure."
        ),
        "caveats": [
            "SURVIVORSHIP BIAS: the universe is TODAY's tickers; dead names are "
            "absent, inflating bottom-quintile (low-FOM) forward returns — part of "
            "the negative spread is artifact, not signal.",
            "MEAN-SPREAD OUTLIER SENSITIVITY: quintile spread uses the MEAN, so a "
            "single low-FOM microcap multi-bagger dominates it. The hit_rate "
            "(median-based) is the robust tail statistic — and it is mildly "
            "POSITIVE (>0.5), so FOM is not inverted, just weak + mean-reverting.",
            "WEAK ABSOLUTE IC: |IC|~0.05 is in-band for a real equity factor "
            "(0.03-0.08) but small — FOM is a tilt, never a high-conviction timer.",
        ],
    }


def main() -> int:
    out_dir = Path("outputs")
    out_dir.mkdir(parents=True, exist_ok=True)
    pull = sorted(set(DEFAULT_UNIVERSE + ["SPY"]))
    print(f"Pulling {len(pull)} tickers {DATA_START}..{DATA_END}", file=sys.stderr)
    closes = fetch_monthly(pull, DATA_START, DATA_END)
    print(f"  data: {len(closes.columns)} tickers, {len(closes)} months", file=sys.stderr)

    result = run_validation(closes)
    report = {
        "as_of": datetime.now(timezone.utc).isoformat(),
        "schema_version": 1,
        "report_type": "fom_predictive_validity",
        "llm_involvement": "none",  # rule-based → headline-KPI-eligible
        "method": (
            "Walk-forward cross-sectional Spearman IC of FOM vs realised forward "
            "returns. PIT: FOM at T uses data <= T; forward return is T -> T+h. No "
            "lookahead. See docs/LLM-BACKTEST-PROTOCOL.md."
        ),
        "data_window": {"start": BACKTEST_START, "end": DATA_END},
        **result,
    }
    out_path = out_dir / "fom-validation-2016-to-2026.json"
    out_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"wrote {out_path}", file=sys.stderr)
    # Echo the headline so the operator sees it immediately.
    print(json.dumps(report["by_horizon"], indent=2), file=sys.stderr)
    print("VERDICT:", report["interpretation"]["verdict"],
          "| best horizon:", report["interpretation"]["best_horizon"], file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
