"""NASDAQ-100 'check the answer key' backtest + train/test FOM calibration.

The principal's test: 「從 2000~2026 NASDAQ100 你選到了哪些 TOP3? 對答案。先抓數據知道
答案，再回去微調 FOM 參數。先校證年，再到月、週、日 top3。不同時間跨度的參數可能不同。」

This module does that HONESTLY — which means it refuses the one move that would
make the numbers a lie. "Look at the answers, then tune params to fit them" is
in-sample curve-fitting / lookahead: it produces a gorgeous backtest that fails
live. Per [[philosophy/09-point-in-time]] and docs/LLM-BACKTEST-PROTOCOL.md, we
instead split time:

  - CALIBRATE FOM weights on a TRAIN window (default 2000-2014) using only that
    window's realised returns as the objective.
  - VALIDATE the winning weights on a HELD-OUT TEST window (2015-2026) the tuner
    never saw. Out-of-sample performance is the only number that counts.
  - Report BOTH the answer key (actual top performers) and FOM's PIT picks, plus
    the canonical-weights baseline, so over-fitting is visible, not hidden.

Horizon note (「不同時間跨度的參數可能不同」 — correct): FOM is computed on MONTHLY
bars, so YEAR and MONTH top-3 are valid here and are calibrated separately. WEEK
and DAY top-3 from a monthly-bar scorer would be a category error — they need
daily bars + re-parameterised lookbacks, flagged as a separate build, not faked.

Survivorship caveat: the universe is a NASDAQ-100 *proxy* of long-history names;
true point-in-time index membership needs a data vendor. Today's list back to 2000
tilts toward survivors — the answer key and any absolute returns are optimistic.
The train/test split still measures whether tuning GENERALISES, which is the point.

LLM involvement: none — rule-based. Headline-eligible per the protocol.
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

from sharks.scoring.fom import fetch_monthly, rank_universe

DATA_START = "1998-01-01"        # buffer for trailing lookbacks at 2000
TRAIN_END_YEAR = 2014
TEST_END_YEAR = 2026
DATA_END = "2026-05-01"

# NASDAQ-100 proxy — long-history large caps (many list mid-window; rank_universe
# skips tickers with no data at a given as_of, so the cross-section grows over
# time). NOT point-in-time index membership — see survivorship caveat above.
NDX_PROXY = [
    "AAPL", "MSFT", "INTC", "CSCO", "ORCL", "QCOM", "AMGN", "GILD", "AMZN", "ADBE",
    "CMCSA", "COST", "PEP", "SBUX", "TXN", "AMAT", "MU", "ADI", "KLAC", "LRCX",
    "ROST", "INTU", "ISRG", "BIIB", "REGN", "VRTX", "EA", "CTAS", "PCAR", "PAYX",
    "FAST", "IDXX", "CTSH", "NVDA", "DLTR", "MNST", "XEL", "EXC", "HON", "GOOGL",
    "BKNG", "MELI", "NFLX", "CSX", "MAR", "ODFL", "CPRT", "ANSS", "CDNS", "SNPS",
    "MCHP", "NXPI", "AVGO", "TMUS", "ASML", "ADP", "AEP", "FTNT", "PANW", "CRWD",
    "DDOG", "ZS", "TEAM", "WDAY", "ABNB", "PYPL", "META", "TSLA", "GOOG", "PDD",
]
BENCHMARK = "QQQ"


def _normalize(w: dict) -> dict:
    s = sum(w.values())
    return {k: v / s for k, v in w.items()} if s else w


def _W(mom, con, cyc, qual, bg) -> dict:
    return _normalize({"momentum": mom, "contrarian": con, "cyclic": cyc,
                       "quality": qual, "bubble_guard": bg})


# Candidate weight archetypes (interpretable, NOT a fine grid — a fine grid is
# itself a form of over-fitting). Each is a hypothesis about what drives forward
# returns. The calibrator picks the best on TRAIN; the test window judges it.
WEIGHT_CANDIDATES: dict[str, dict] = {
    "canonical_neutral":   _W(0.25, 0.25, 0.15, 0.15, 0.20),
    "momentum_heavy":      _W(0.55, 0.05, 0.15, 0.10, 0.15),
    "momentum_quality":    _W(0.40, 0.10, 0.10, 0.30, 0.10),
    "contrarian_heavy":    _W(0.10, 0.45, 0.10, 0.20, 0.15),
    "contrarian_quality":  _W(0.10, 0.35, 0.10, 0.35, 0.10),
    "quality_heavy":       _W(0.15, 0.20, 0.10, 0.45, 0.10),
    "bubble_guard_heavy":  _W(0.20, 0.25, 0.10, 0.15, 0.30),
    "balanced_growth":     _W(0.35, 0.15, 0.15, 0.25, 0.10),
    "defensive_value":     _W(0.10, 0.30, 0.10, 0.30, 0.20),
    "anti_bubble_momentum":_W(0.45, 0.15, 0.10, 0.15, 0.15),
}


def _regime(weights: dict, floor: int = -100) -> dict:
    return {"label": "calib", "weights": dict(weights), "bubble_guard_floor": floor}


def _ret(closes: pd.DataFrame, ticker: str, p0: int, p1: int) -> Optional[float]:
    if p1 >= len(closes):
        return None
    a, b = closes[ticker].iloc[p0], closes[ticker].iloc[p1]
    if a and b and a > 0 and not pd.isna(a) and not pd.isna(b):
        return float(b / a - 1.0)
    return None


def _period_ends(closes: pd.DataFrame, freq: str) -> list[pd.Timestamp]:
    """Year-end or month-end timestamps present in the (monthly) index."""
    if freq == "year":
        seen, out = set(), []
        for d in closes.index:
            if d.year not in seen:
                # take the LAST month of each year as the year-end as_of
                pass
        # last available month per calendar year
        by_year = {}
        for d in closes.index:
            by_year[d.year] = d
        return [by_year[y] for y in sorted(by_year)]
    return list(closes.index)  # monthly


def answer_key(closes: pd.DataFrame, universe: list[str], freq: str,
               start_year: int, end_year: int, k: int = 3) -> dict:
    """For each period, the ACTUAL top-k performers (the answer the principal
    wants to 對答案 against)."""
    ends = _period_ends(closes, freq)
    out = {}
    for i, as_of in enumerate(ends):
        if not (start_year <= as_of.year <= end_year):
            continue
        p0 = closes.index.searchsorted(as_of)
        # forward span: next year-end (≈12 rows) or next month (1 row)
        p1 = (p0 + 12) if freq == "year" else (p0 + 1)
        rets = {t: _ret(closes, t, p0, p1) for t in universe if t in closes.columns}
        rets = {t: r for t, r in rets.items() if r is not None}
        if len(rets) < k:
            continue
        top = sorted(rets, key=lambda t: rets[t], reverse=True)[:k]
        out[str(as_of.date())] = {"top_k": [{"t": t, "ret": round(rets[t], 4)} for t in top],
                                  "n_universe": len(rets)}
    return out


def fom_picks(closes: pd.DataFrame, universe: list[str], weights: dict, freq: str,
              start_year: int, end_year: int, k: int = 3) -> dict:
    """FOM's PIT top-k picks per period + their realised forward return, under a
    given weights table. as_of uses only data <= as_of; forward return is the next
    period. No lookahead."""
    ends = _period_ends(closes, freq)
    regime = _regime(weights)
    periods, pick_rets, bench_rets, overlaps = [], [], [], []
    for as_of in ends:
        if not (start_year <= as_of.year <= end_year):
            continue
        p0 = closes.index.searchsorted(as_of)
        p1 = (p0 + 12) if freq == "year" else (p0 + 1)
        if p1 >= len(closes):
            break
        scored = rank_universe(closes, universe, as_of, regime=regime)
        if len(scored) < k:
            continue
        top = [s.ticker for s in scored[:k]]
        rs = [_ret(closes, t, p0, p1) for t in top]
        rs = [r for r in rs if r is not None]
        if not rs:
            continue
        pick_ret = float(np.mean(rs))
        bench = _ret(closes, BENCHMARK, p0, p1) if BENCHMARK in closes.columns else None
        actual_top = set(sorted(
            (t for t in universe if t in closes.columns and _ret(closes, t, p0, p1) is not None),
            key=lambda t: _ret(closes, t, p0, p1), reverse=True)[:k])
        periods.append({
            "as_of": str(as_of.date()),
            "fom_top_k": top,
            "fom_pick_fwd_ret": round(pick_ret, 4),
            "benchmark_fwd_ret": round(bench, 4) if bench is not None else None,
            "excess_vs_bench": round(pick_ret - bench, 4) if bench is not None else None,
            "overlap_with_actual_topk": len(set(top) & actual_top),
        })
        pick_rets.append(pick_ret)
        if bench is not None:
            bench_rets.append(bench)
        overlaps.append(len(set(top) & actual_top))
    summary = {
        "n_periods": len(pick_rets),
        "mean_pick_fwd_ret": round(float(np.mean(pick_rets)), 4) if pick_rets else None,
        "mean_benchmark_fwd_ret": round(float(np.mean(bench_rets)), 4) if bench_rets else None,
        "mean_excess_vs_bench": (round(float(np.mean(pick_rets)) - float(np.mean(bench_rets)), 4)
                                 if pick_rets and bench_rets else None),
        "mean_overlap_with_actual_topk": round(float(np.mean(overlaps)), 3) if overlaps else None,
    }
    return {"summary": summary, "periods": periods}


def calibrate(closes: pd.DataFrame, universe: list[str], freq: str,
              train_start: int, train_end: int, k: int = 3) -> dict:
    """Pick the weight archetype maximising mean EXCESS-vs-benchmark on TRAIN.
    (Excess, not raw return, so we reward stock selection, not just beta.)"""
    results = []
    for name, w in WEIGHT_CANDIDATES.items():
        out = fom_picks(closes, universe, w, freq, train_start, train_end, k)
        s = out["summary"]
        obj = s["mean_excess_vs_bench"]
        results.append({"name": name, "weights": w, "train_summary": s,
                        "objective_excess": obj})
    ranked = sorted([r for r in results if r["objective_excess"] is not None],
                    key=lambda r: r["objective_excess"], reverse=True)
    return {"ranked_train": ranked, "best": ranked[0] if ranked else None}


def run(closes: pd.DataFrame, universe: list[str], freq: str, k: int = 3) -> dict:
    """Full check-the-answer + train/test calibration for one horizon."""
    ak = answer_key(closes, universe, freq, 2000, TEST_END_YEAR, k)

    calib = calibrate(closes, universe, freq, 2000, TRAIN_END_YEAR, k)
    best = calib["best"]
    canonical = WEIGHT_CANDIDATES["canonical_neutral"]

    # Validate BEST and CANONICAL on the held-out TEST window.
    test = {}
    if best:
        test["best_oos"] = fom_picks(closes, universe, best["weights"], freq,
                                     TRAIN_END_YEAR + 1, TEST_END_YEAR, k)["summary"]
    test["canonical_oos"] = fom_picks(closes, universe, canonical, freq,
                                      TRAIN_END_YEAR + 1, TEST_END_YEAR, k)["summary"]
    # Full-history canonical picks (the 對答案 table the principal asked to see).
    full_canonical = fom_picks(closes, universe, canonical, freq, 2000, TEST_END_YEAR, k)

    overfit_flag = None
    if best:
        tr = best["objective_excess"]
        te = test["best_oos"].get("mean_excess_vs_bench")
        if tr is not None and te is not None:
            # crude over-fit gauge: how much edge survives out-of-sample
            overfit_flag = {
                "train_excess": tr, "test_excess": te,
                "edge_decay": round(tr - te, 4),
                "generalises": bool(te is not None and te > 0 and te >= 0.4 * tr) if tr > 0 else None,
            }

    return {
        "freq": freq, "k": k,
        "train_window": f"2000-{TRAIN_END_YEAR}",
        "test_window": f"{TRAIN_END_YEAR + 1}-{TEST_END_YEAR}",
        "best_weights_name": best["name"] if best else None,
        "best_weights": best["weights"] if best else None,
        "train_ranking": [{"name": r["name"], "excess": r["objective_excess"]}
                          for r in calib["ranked_train"]],
        "oos_validation": test,
        "overfit_check": overfit_flag,
        "answer_key": ak,
        "fom_canonical_full_history": full_canonical,
    }


def main() -> int:
    out_dir = Path("outputs")
    out_dir.mkdir(parents=True, exist_ok=True)
    pull = sorted(set(NDX_PROXY + [BENCHMARK]))
    print(f"Pulling {len(pull)} NDX-proxy tickers {DATA_START}..{DATA_END}", file=sys.stderr)
    closes = fetch_monthly(pull, DATA_START, DATA_END)
    print(f"  data: {len(closes.columns)} tickers, {len(closes)} months", file=sys.stderr)
    universe = [t for t in NDX_PROXY if t in closes.columns]

    report = {
        "as_of": datetime.now(timezone.utc).isoformat(),
        "schema_version": 1,
        "report_type": "nasdaq100_calibration",
        "llm_involvement": "none",
        "universe_size": len(universe),
        "survivorship_caveat": (
            "NDX proxy = today's long-history names; not PIT index membership. "
            "Absolute returns optimistic. Train/test split still measures whether "
            "tuning generalises."
        ),
        "horizons": {},
    }
    for freq in ("year", "month"):
        print(f"--- calibrating {freq} ---", file=sys.stderr)
        report["horizons"][freq] = run(closes, universe, freq, k=3)

    report["week_day_note"] = (
        "WEEK and DAY top-3 intentionally NOT produced: FOM uses monthly bars; "
        "weekly/daily picks need daily data + re-parameterised lookbacks (a "
        "separate build). Producing them from a monthly scorer would be a category "
        "error. 「不同時間跨度的參數可能不同」 — agreed; that is why they are split."
    )

    out_path = out_dir / "nasdaq100-calibration-2000-to-2026.json"
    out_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"wrote {out_path}", file=sys.stderr)

    # Echo the headline.
    for freq in ("year", "month"):
        h = report["horizons"][freq]
        print(f"\n[{freq.upper()}] best train weights: {h['best_weights_name']}", file=sys.stderr)
        print(f"  train ranking (excess vs QQQ): "
              + ", ".join(f"{r['name']}={r['excess']}" for r in h["train_ranking"][:4]), file=sys.stderr)
        oos = h["oos_validation"]
        print(f"  OOS best={oos.get('best_oos', {}).get('mean_excess_vs_bench')}  "
              f"canonical={oos.get('canonical_oos', {}).get('mean_excess_vs_bench')}", file=sys.stderr)
        print(f"  overfit_check: {h['overfit_check']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
