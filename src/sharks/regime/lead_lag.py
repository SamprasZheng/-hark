"""Lead-lag / supply-chain transmission detector (regime-level).

Answers the principal's "從哪個產業開始傳導": given a moving LEADER (e.g. SOXX),
which followers are (a) Granger-style predicted by the leader at a short lag AND
(b) haven't moved yet — the UN-CROWDED transmission targets. Implements the
replicated edges from tech/rotation-spillover-algos.md (lead-lag cross-
predictability — Cohen-Frazzini / Hong-Stein gradual diffusion — and a simplified
Diebold-Yilmaz net-transmitter rank) with ZERO new dependency (numpy OLS only,
no statsmodels/scipy).

Mirrors regime/sector_flow.py: the caller supplies a price/returns frame and an
optional `as_of`; everything slices `.loc[:as_of]` so there is NO lookahead.
Pure + unit-testable.

HONEST SCOPE: the lead score is an IN-SAMPLE Granger-style incremental R² over the
supplied window (association, not an out-of-sample-validated alpha) — it produces
a WATCHLIST of transmission candidates that must still clear the 十足的證據 gate +
Risk Officer. It never auto-trades and is observe-first (not folded into final_fom).
"""

from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd


def to_returns(closes: pd.DataFrame) -> pd.DataFrame:
    """Simple returns frame from a price frame (columns = tickers)."""
    return closes.pct_change().dropna(how="all")


def _ols_r2(y: np.ndarray, X: np.ndarray) -> float:
    """In-sample R^2 of OLS y~X (X already includes an intercept column)."""
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    ss_res = float(resid @ resid)
    yc = y - y.mean()
    ss_tot = float(yc @ yc)
    return 0.0 if ss_tot <= 1e-12 else 1.0 - ss_res / ss_tot


def _design(returns: pd.DataFrame, leader: str, follower: str, max_lag: int):
    """Build (y, X_full, X_restricted) for a Granger-style test: does the LEADER's
    lagged returns add predictive power over the follower's own AR(max_lag)?"""
    if leader == follower or leader not in returns or follower not in returns:
        return None
    df = returns[[leader, follower]].dropna()
    n = len(df)
    if n < max_lag + 12:               # need enough obs for a meaningful fit
        return None
    f = df[follower].to_numpy()
    l = df[leader].to_numpy()
    y = f[max_lag:]
    m = len(y)
    inter = np.ones(m)
    follower_lags = [f[max_lag - k: n - k] for k in range(1, max_lag + 1)]
    leader_lags = [l[max_lag - k: n - k] for k in range(1, max_lag + 1)]
    X_restricted = np.column_stack([inter, *follower_lags])
    X_full = np.column_stack([inter, *follower_lags, *leader_lags])
    return y, X_full, X_restricted


def _incremental_r2(returns: pd.DataFrame, leader: str, follower: str, max_lag: int) -> float:
    """Granger-style incremental R^2 from adding leader lags (>=0; 0 = leader does
    not help predict follower)."""
    d = _design(returns, leader, follower, max_lag)
    if d is None:
        return 0.0
    y, x_full, x_restricted = d
    return max(0.0, _ols_r2(y, x_full) - _ols_r2(y, x_restricted))


def best_lag(returns: pd.DataFrame, leader: str, follower: str, max_lag: int = 6) -> Optional[int]:
    """The single lag k (1..max_lag) at which leader_{t-k} most correlates with
    follower_t (the dominant lead time). None if insufficient data."""
    if leader == follower or leader not in returns or follower not in returns:
        return None
    df = returns[[leader, follower]].dropna()
    if len(df) < max_lag + 12:
        return None
    best_k, best_abs = None, -1.0
    for k in range(1, max_lag + 1):
        c = df[leader].shift(k).corr(df[follower])
        if c is not None and not np.isnan(c) and abs(c) > best_abs:
            best_abs, best_k = abs(c), k
    return best_k


def lead_lag_score(returns: pd.DataFrame, leader: str, follower: str,
                   as_of: Optional[pd.Timestamp] = None, max_lag: int = 3) -> dict:
    """Directional lead-lag score. net > 0 ⇒ leader leads follower (leader's past
    helps predict follower's future more than vice-versa)."""
    r = returns.loc[:as_of] if as_of is not None else returns
    lead_r2 = _incremental_r2(r, leader, follower, max_lag)
    reverse_r2 = _incremental_r2(r, follower, leader, max_lag)
    return {
        "leader": leader, "follower": follower,
        "lead_r2": round(lead_r2, 5),
        "reverse_r2": round(reverse_r2, 5),
        "net": round(lead_r2 - reverse_r2, 5),
        "best_lag": best_lag(r, leader, follower, max_lag * 2),
    }


def net_transmitter_rank(returns: pd.DataFrame, tickers: list[str],
                         as_of: Optional[pd.Timestamp] = None, max_lag: int = 3) -> list[dict]:
    """Simplified Diebold-Yilmaz net-transmitter rank: for each ticker, mean
    out-influence (it leads others) minus mean in-influence (others lead it).
    net > 0 ⇒ a SOURCE/transmitter; net < 0 ⇒ a SINK/receiver."""
    r = returns.loc[:as_of] if as_of is not None else returns
    out: dict[str, list[float]] = {t: [] for t in tickers}
    inn: dict[str, list[float]] = {t: [] for t in tickers}
    for i in tickers:
        for j in tickers:
            if i == j:
                continue
            infl = _incremental_r2(r, i, j, max_lag)   # i → j
            out[i].append(infl)
            inn[j].append(infl)
    rows = []
    for t in tickers:
        o = float(np.mean(out[t])) if out[t] else 0.0
        n = float(np.mean(inn[t])) if inn[t] else 0.0
        rows.append({"ticker": t, "out_influence": round(o, 5),
                     "in_influence": round(n, 5), "net": round(o - n, 5)})
    rows.sort(key=lambda x: x["net"], reverse=True)
    for i, row in enumerate(rows):
        row["rank"] = i + 1
        row["role"] = "transmitter" if row["net"] > 0 else "receiver"
    return rows


def transmission_candidates(returns: pd.DataFrame, leader: str, followers: list[str],
                            as_of: Optional[pd.Timestamp] = None, max_lag: int = 3,
                            recent_window: int = 63) -> list[dict]:
    """THE un-crowded answer to "從哪個產業開始傳導": rank followers that are
    (a) led by the leader (high net lead-lag) AND (b) have NOT moved yet (low
    recent cumulative return). High candidate_score = downstream of a moving
    leader but not yet priced — the place to do DD before the crowd.

    candidate_score = max(0, net_leadership) × (1 − normalised_recent_move).
    WATCHLIST output only — must clear the evidence gate + Risk Officer.
    """
    r = returns.loc[:as_of] if as_of is not None else returns
    rows = []
    for f in followers:
        sc = lead_lag_score(r, leader, f, max_lag=max_lag)
        recent = r[f].tail(recent_window).sum() if f in r else 0.0  # ~cumulative return
        rows.append({"follower": f, "lead_net": sc["net"], "best_lag": sc["best_lag"],
                     "recent_move": round(float(recent), 4)})
    moves = [abs(x["recent_move"]) for x in rows] or [0.0]
    ref = max(moves) or 1.0
    for x in rows:
        not_moved = 1.0 - min(1.0, max(0.0, x["recent_move"]) / ref)   # only positive moves "use up" the discount
        x["candidate_score"] = round(max(0.0, x["lead_net"]) * not_moved, 6)
    rows.sort(key=lambda x: x["candidate_score"], reverse=True)
    return rows


def main() -> int:
    """Live demo: rank sector-ETF net-transmitters + SOXX→sector transmission
    candidates (the principal's semis-spillover question). Network via yfinance."""
    import json
    import sys
    import warnings
    from datetime import datetime, timezone
    from pathlib import Path

    warnings.filterwarnings("ignore")
    import yfinance as yf
    from sharks.regime.sector_flow import SECTOR_ETFS

    pull = sorted(set(SECTOR_ETFS) | {"SPY"})
    raw = yf.download(pull, start="2021-01-01", end="2026-05-29", interval="1mo",
                      auto_adjust=True, progress=False, group_by="ticker", threads=True)
    closes = pd.DataFrame()
    for t in pull:
        try:
            closes[t] = raw[t]["Close"] if isinstance(raw.columns, pd.MultiIndex) else raw["Close"]
        except (KeyError, ValueError):
            pass
    if closes.index.tz is not None:
        closes.index = closes.index.tz_localize(None)
    returns = to_returns(closes.sort_index())

    transmitters = net_transmitter_rank(returns, [t for t in SECTOR_ETFS if t in returns])
    followers = [t for t in SECTOR_ETFS if t in returns and t != "SOXX"]
    candidates = transmission_candidates(returns, "SOXX", followers)

    report = {
        "as_of": datetime.now(timezone.utc).isoformat(),
        "report_type": "lead_lag_transmission",
        "note": ("In-sample Granger-style lead-lag over the window; PIT; observe-first; "
                 "WATCHLIST only — must clear 十足的證據 gate. See tech/alpha-transmission-framework.md."),
        "net_transmitter_rank": transmitters,
        "soxx_transmission_candidates": candidates,
    }
    out = Path("outputs") / "lead-lag-transmission.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"wrote {out}", file=sys.stderr)
    print("net transmitters:", [r["ticker"] for r in transmitters[:5]], file=sys.stderr)
    print("SOXX→ candidates:", [(c["follower"], c["candidate_score"]) for c in candidates[:5]], file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
