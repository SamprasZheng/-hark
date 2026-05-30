"""FOM backtest 2016-2026 with $1000 weekly DCA into top-3 FOM picks.

Simulates: every month-end (proxy for weekly $1000 → $4000/month),
  - Score the universe via FOM
  - Buy top 3 ($1333 each from $4000)
  - Hold; never sell unless ticker drops below a stop (no rebalance for simplicity)
  - Track portfolio value monthly

Outputs:
  - outputs/fom-backtest-{start}-to-{end}.json with returns, picks per month, did-we-catch-leader log
  - Compares vs SPY benchmark DCA same amounts
"""

from __future__ import annotations

import json
import sys
import warnings
from datetime import datetime, timezone
from pathlib import Path

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import numpy as np
import pandas as pd
import yfinance as yf

from sharks.scoring.fom import (
    DEFAULT_UNIVERSE, INDICES, SECTOR_ETFS, CRYPTO, fetch_monthly, rank_universe,
)

START = "2014-01-01"  # 2 years buffer for 36m lookback at 2016 start
BACKTEST_START = "2016-01-01"
END = "2026-05-01"
WEEKLY_DOLLAR = 1000  # but actually deploy monthly = $4000

# Track if FOM caught the famous "did you ride the wave?" tickers
LEADER_WATCHLIST = ["TSLA", "NVDA", "MU", "META", "NFLX", "LMT", "AVGO", "AMD"]


def main() -> int:
    out_dir = Path("outputs")
    out_dir.mkdir(parents=True, exist_ok=True)

    # Build pull universe
    pull = DEFAULT_UNIVERSE + INDICES + SECTOR_ETFS + CRYPTO + ["SPY"]
    pull = sorted(set(pull))
    print(f"Pulling {len(pull)} tickers from {START} to {END}", file=sys.stderr)
    closes = fetch_monthly(pull, START, END)
    print(f"  data: {len(closes.columns)} tickers", file=sys.stderr)

    # Run monthly backtest
    backtest_months = pd.date_range(start=BACKTEST_START, end=END, freq="MS")
    portfolio_history = []
    holdings = {}  # ticker -> shares
    cash = 0.0
    total_invested = 0.0
    spy_shares = 0.0
    spy_invested = 0.0
    picks_log = []
    leader_catch_log = {t: [] for t in LEADER_WATCHLIST}
    persistence = {}

    for month_start in backtest_months:
        # Use end-of-prior-month as as_of (no lookahead)
        as_of = month_start - pd.Timedelta(days=1)
        # Skip months too early for full FOM
        if as_of < pd.Timestamp("2016-01-01"):
            continue
        # Score universe
        scores = rank_universe(closes, DEFAULT_UNIVERSE, as_of, persistence)
        if len(scores) < 3:
            continue
        top3 = scores[:3]
        top50 = scores[:50]
        persistence = {s.ticker: persistence.get(s.ticker, 0) + 1 for s in top50}

        # "Deploy" $4000 monthly = $1333 each into top 3
        # Buy at next month's open ≈ next month's monthly close (use month_start close as fill)
        # Find next price index
        next_idx = closes.index.searchsorted(month_start)
        if next_idx >= len(closes):
            continue
        fill_date = closes.index[next_idx]

        for pick in top3:
            t = pick.ticker
            if t not in closes.columns:
                continue
            price = closes[t].iloc[next_idx]
            if pd.isna(price) or price <= 0:
                continue
            allocation = 4000 / 3
            shares = allocation / price
            holdings[t] = holdings.get(t, 0) + shares
            total_invested += allocation

        # Track SPY benchmark
        if "SPY" in closes.columns:
            spy_price = closes["SPY"].iloc[next_idx]
            if not pd.isna(spy_price) and spy_price > 0:
                spy_shares += 4000 / spy_price
                spy_invested += 4000

        # Compute portfolio MV at this date
        mv = 0.0
        for t, sh in holdings.items():
            if t in closes.columns:
                p = closes[t].iloc[next_idx]
                if not pd.isna(p):
                    mv += sh * p
        spy_mv = spy_shares * closes["SPY"].iloc[next_idx] if "SPY" in closes.columns else 0.0

        portfolio_history.append({
            "month": str(fill_date.date()),
            "invested_total": round(total_invested, 2),
            "portfolio_mv": round(mv, 2),
            "spy_mv": round(spy_mv, 2),
            "portfolio_return_pct": round((mv / total_invested - 1) * 100, 2) if total_invested > 0 else 0,
            "spy_return_pct": round((spy_mv / spy_invested - 1) * 100, 2) if spy_invested > 0 else 0,
            "top3": [t.ticker for t in top3],
        })

        # Track leader catches
        for t in LEADER_WATCHLIST:
            if t in [p.ticker for p in top3]:
                leader_catch_log[t].append({"month": str(fill_date.date()),
                                             "rank": [p.ticker for p in top3].index(t) + 1,
                                             "price": round(float(closes[t].iloc[next_idx]), 2) if t in closes.columns else None})

        picks_log.append({
            "month": str(fill_date.date()),
            "picks": [{"ticker": p.ticker, "fom": round(p.final_fom, 2),
                       "m": round(p.momentum, 1), "c": round(p.contrarian, 1),
                       "bg": round(p.bubble_guard_val, 1)} for p in top3],
        })

    # Final analysis
    if portfolio_history:
        final = portfolio_history[-1]
        final_mv = final["portfolio_mv"]
        final_spy = final["spy_mv"]
        final_invested = final["invested_total"]
        portfolio_total_return = (final_mv / final_invested - 1) * 100 if final_invested > 0 else 0
        spy_total_return = (final_spy / spy_invested - 1) * 100 if spy_invested > 0 else 0
        excess = portfolio_total_return - spy_total_return

        # Compute Sharpe-like + MDD
        ports = pd.Series([h["portfolio_mv"] / h["invested_total"] for h in portfolio_history if h["invested_total"] > 0])
        spys = pd.Series([h["spy_mv"] / max(h["invested_total"], 1) for h in portfolio_history if h["invested_total"] > 0])
        port_drawdown_max = float(((ports / ports.cummax()) - 1).min()) * 100 if len(ports) > 1 else 0
        spy_drawdown_max = float(((spys / spys.cummax()) - 1).min()) * 100 if len(spys) > 1 else 0

        # Final holding breakdown
        final_holdings = []
        for t, sh in holdings.items():
            if t in closes.columns:
                last_price = closes[t].dropna().iloc[-1] if not closes[t].dropna().empty else 0
                final_holdings.append({"ticker": t, "shares": round(sh, 4),
                                       "current_value": round(sh * last_price, 2)})
        final_holdings.sort(key=lambda x: -x["current_value"])

        report = {
            "as_of": datetime.now(timezone.utc).isoformat(),
            "schema_version": 1,
            "backtest_window": {"start": BACKTEST_START, "end": END},
            "monthly_deployment": 4000,
            "months_run": len(portfolio_history),
            "total_invested": round(final_invested, 2),
            "final_portfolio_mv": round(final_mv, 2),
            "final_spy_mv": round(final_spy, 2),
            "portfolio_total_return_pct": round(portfolio_total_return, 2),
            "spy_total_return_pct": round(spy_total_return, 2),
            "excess_return_vs_spy_pct": round(excess, 2),
            "portfolio_max_drawdown_pct": round(port_drawdown_max, 2),
            "spy_max_drawdown_pct": round(spy_drawdown_max, 2),
            "leader_catches": {
                t: {
                    "appearances_in_top3": len(events),
                    "first_appearance": events[0] if events else None,
                    "last_appearance": events[-1] if events else None,
                    "all_events_brief": events[:10],  # first 10
                } for t, events in leader_catch_log.items()
            },
            "final_holdings_top_15": final_holdings[:15],
            "portfolio_history_summary": portfolio_history[::6],  # every 6 months
        }
    else:
        report = {"error": "no portfolio history"}

    out_path = out_dir / f"fom-backtest-2016-to-2026.json"
    out_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"wrote {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
