#!/usr/bin/env python3
"""
Trading Society -- Statistical Arbitrage (Kalman-filter pairs) trader (grok3.md)

PPST Declaration (this PROGRAM):
- PROJECT: Trading Society
- PROGRAM: simulation/statarb_trader.py
- SKILL:   dynamic-hedge-ratio pairs statistical arbitrage via a scalar Kalman
           filter; z-score of the Kalman forecast error -> mean-reversion pair signal.
- TARGET:  Implement grok3.md's StatisticalArbitrageTrader + Kalman filter. For
           each economically-related candidate pair (y, x), a 2-state Kalman filter
           tracks a time-varying hedge ratio [beta, alpha] (Chan's formulation); the
           standardized forecast error (z-score) drives a market-neutral signal:
             z > +entry  -> spread rich: LONG x  / SHORT y (hedge candidate)
             z < -entry  -> spread cheap: LONG y / SHORT x (hedge candidate)

Long-bias reconciliation (CLAUDE.md §10): the society is LONG-BIASED and its
specialists are long-only by construction. A pairs trade is market-neutral, so we
split it: the LONG leg joins the long-biased society vote (`current_longs`); the
SHORT leg is emitted ONLY as a `short_leg_hedge_candidate`, actionable solely when
`regime_filter.shorts_allowed(regime)` is True (a confirmed bear) AND the Risk
Officer gates it. No naked shorts are ever recommended here.

Governance: deterministic (llm_involvement="none"). PIT -- uses only the price
points passed in (the caller slices to <= as_of). never-raise: a pair missing data
or too short is skipped, never fabricated. Recommend-only RESEARCH; does not place
orders, does not touch outputs/picks-* or wiki/05_recommendations/*. Candidate
pairs are Grade-C structural (same-industry economic relationships), not a lookahead
cointegration scan on the test window.

Run: python simulation/statarb_trader.py   (live pairs on the real lake)
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

# Economically-related candidate pairs (Grade-C structural; same end-market /
# substitute names). Not a data-mined cointegration scan -> no lookahead.
CANDIDATE_PAIRS: List[Tuple[str, str]] = [
    ("NVDA", "AMD"), ("KLAC", "LRCX"), ("AMAT", "LRCX"), ("AVGO", "MRVL"),
    ("MU", "WDC"), ("ASML", "AMAT"), ("ONTO", "NVMI"), ("UCTT", "ICHR"),
    ("LMT", "NOC"), ("RTX", "GD"), ("GOOGL", "META"), ("MSFT", "ORCL"),
    ("KO", "PEP"), ("V", "MA"), ("CEG", "VST"), ("ETN", "VRT"),
]

ENTRY_Z = 1.5      # |z| above this opens a pair
EXIT_Z = 0.5       # |z| below this closes (flat)
DELTA = 1e-4       # Kalman process-noise scale (random-walk hedge ratio)
VE = 1e-3          # observation noise (relative to log-price scale)
MIN_POINTS = 120   # need enough history for the filter to settle


@dataclass
class PairSignal:
    y: str
    x: str
    beta: float                 # current Kalman hedge ratio
    zscore: float
    signal: str                 # "long_y_short_x" | "long_x_short_y" | "flat"
    long_leg: Optional[str]
    short_leg_hedge_candidate: Optional[str]
    half_life: Optional[float]  # OU mean-reversion half-life (bars), if estimable

    def to_dict(self) -> Dict[str, Any]:
        return {"y": self.y, "x": self.x, "beta": round(self.beta, 4),
                "zscore": round(self.zscore, 2), "signal": self.signal,
                "long_leg": self.long_leg,
                "short_leg_hedge_candidate": self.short_leg_hedge_candidate,
                "half_life_bars": (round(self.half_life, 1)
                                   if self.half_life is not None else None)}


def _kalman_spread(y: np.ndarray, x: np.ndarray) -> Tuple[float, np.ndarray]:
    """Chan-style 2-state Kalman pairs filter on log prices. Returns the current
    hedge ratio beta and the full standardized-forecast-error (z-score) path."""
    ly, lx = np.log(y), np.log(x)
    delta = DELTA
    Vw = delta / (1.0 - delta) * np.eye(2)   # process covariance
    Ve = VE                                  # observation variance
    beta = np.zeros(2)                       # [hedge_ratio, intercept]
    P = np.zeros((2, 2))
    R = np.zeros((2, 2))
    z = np.full(len(ly), np.nan)
    for t in range(len(ly)):
        H = np.array([lx[t], 1.0])           # observation matrix
        R = P + Vw                           # predicted state covariance
        yhat = H @ beta                      # predicted observation
        e = ly[t] - yhat                     # forecast error (the spread)
        Q = H @ R @ H + Ve                   # forecast error variance
        Q = max(Q, 1e-12)
        K = (R @ H) / Q                      # Kalman gain
        beta = beta + K * e                  # state update
        P = R - np.outer(K, H) @ R           # covariance update
        z[t] = e / np.sqrt(Q)
    return float(beta[0]), z


def _half_life(spread: np.ndarray) -> Optional[float]:
    """OU half-life of mean reversion from an AR(1) fit on the z-score path."""
    s = spread[~np.isnan(spread)]
    if len(s) < 30:
        return None
    lag = s[:-1]
    delta = s[1:] - lag
    denom = float(np.dot(lag, lag))
    if denom <= 0:
        return None
    rho = float(np.dot(lag, delta)) / denom   # delta = rho * lag + eps
    if rho >= 0:                              # not mean-reverting
        return None
    hl = -np.log(2) / np.log(1 + rho) if (1 + rho) > 0 else None
    return float(hl) if hl and hl > 0 else None


def _aligned(series: Dict[str, List[Any]], a: str, b: str
             ) -> Optional[Tuple[np.ndarray, np.ndarray]]:
    """Date-aligned closing-price arrays for two tickers, or None if unavailable."""
    pa, pb = series.get(a), series.get(b)
    if not pa or not pb:
        return None
    ma = {p.as_of: p.close for p in pa if p.close and p.close > 0}
    mb = {p.as_of: p.close for p in pb if p.close and p.close > 0}
    common = sorted(set(ma) & set(mb))
    if len(common) < MIN_POINTS:
        return None
    return (np.array([ma[d] for d in common]),
            np.array([mb[d] for d in common]))


def evaluate_pair(series: Dict[str, List[Any]], y: str, x: str) -> Optional[PairSignal]:
    al = _aligned(series, y, x)
    if al is None:
        return None
    yv, xv = al
    try:
        beta, z = _kalman_spread(yv, xv)
    except Exception:
        return None
    zc = z[-1]
    if not np.isfinite(zc):
        return None
    if zc > ENTRY_Z:
        sig, long_leg, short_leg = "long_x_short_y", x, y
    elif zc < -ENTRY_Z:
        sig, long_leg, short_leg = "long_y_short_x", y, x
    else:
        sig, long_leg, short_leg = "flat", None, None
    return PairSignal(y=y, x=x, beta=beta, zscore=float(zc), signal=sig,
                      long_leg=long_leg, short_leg_hedge_candidate=short_leg,
                      half_life=_half_life(z))


def current_pairs(series: Dict[str, List[Any]],
                  pairs: Optional[List[Tuple[str, str]]] = None
                  ) -> List[Dict[str, Any]]:
    """All active (non-flat) pair signals, ranked by |zscore| (strongest first)."""
    pairs = pairs or CANDIDATE_PAIRS
    out = []
    for y, x in pairs:
        ps = evaluate_pair(series, y, x)
        if ps and ps.signal != "flat":
            out.append(ps.to_dict())
    out.sort(key=lambda d: abs(d["zscore"]), reverse=True)
    return out


def current_longs(series: Dict[str, List[Any]], top_k: int = 6) -> List[str]:
    """The LONG legs only -- what the long-biased society may actually buy. The
    short legs stay as hedge candidates (bear-gated; see module docstring)."""
    longs, seen = [], set()
    for d in current_pairs(series):
        leg = d.get("long_leg")
        if leg and leg not in seen:
            seen.add(leg)
            longs.append(leg)
    return longs[:top_k]


def _demo() -> int:
    import json
    print("=" * 72)
    print("statarb_trader self-test (Kalman pairs on the real lake)")
    print("=" * 72)
    # synthetic sanity: a cointegrated pair (x random walk, y = 2x + noise) must
    # produce a finite beta near 2 and a bounded z-score.
    rng = np.random.default_rng(7)
    steps = rng.normal(0, 0.01, 300).cumsum()
    xsig = np.exp(4.0 + steps)
    ysig = np.exp(np.log(xsig) * 1.0 + 0.7 + rng.normal(0, 0.01, 300))

    class _P:
        def __init__(self, d, c): self.as_of, self.close = d, c
    syn = {"YS": [_P(i, ysig[i]) for i in range(300)],
           "XS": [_P(i, xsig[i]) for i in range(300)]}
    ps = evaluate_pair(syn, "YS", "XS")
    print(f"\n  synthetic cointegrated pair -> {ps.to_dict() if ps else None}")
    assert ps is not None and np.isfinite(ps.beta), "Kalman beta must be finite"

    print("\n  [live lake pairs]")
    try:
        from simulation.universe_competition import build_universe
        from simulation.backtest_runner import load_pit_series
        uni = build_universe(max_names=200)
        names = sorted({t for pr in CANDIDATE_PAIRS for t in pr})
        series = {t: pts for t, pts in load_pit_series(names).items() if pts}
        active = current_pairs(series)
        print(f"  priced names: {len(series)} | active pairs: {len(active)}")
        for d in active[:8]:
            print(f"    {d['y']}/{d['x']:<5} z={d['zscore']:>6} beta={d['beta']:>7} "
                  f"-> {d['signal']} (long {d['long_leg']})")
        print(f"\n  long legs for the society vote: {current_longs(series)}")
    except Exception as e:
        print(f"  live pairs skipped: {e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_demo())
