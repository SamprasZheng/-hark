"""Fundamentals fetcher — key earnings numbers + turnaround-inflection flags.

The principal wants to TRACK the fundamentals of his watched names so he does not
miss a turnaround (扭轉條件) — e.g. NKE's gross-margin inflection. This pulls the
key numbers (revenue growth, gross/operating/profit margin, the gross-margin YoY
DELTA, EPS growth, FCF, forward valuation, analyst upside) via yfinance and
derives simple, plain inflection flags.

Network lives in `fetch_*`; the derive/flag logic is PURE + unit-tested. Free data
(yfinance), best-effort: missing fields degrade to None, never raise. Grade-C/D
(yfinance .info is unofficial) — verify a turnaround call against the primary 8-K
before acting. WATCHLIST / monitoring only.
"""

from __future__ import annotations

from typing import Optional


def inflection_flags(f: dict) -> dict:
    """Derive plain turnaround flags from a fundamentals dict. `turnaround_score`
    0-5 = how many fundamental conditions are currently positive."""
    rg = f.get("revenue_growth_yoy")
    eg = f.get("earnings_growth_yoy")
    om = f.get("operating_margin")
    fcf = f.get("fcf")
    gmd = f.get("gross_margin_yoy_delta")
    flags = {
        "revenue_growing": rg is not None and rg > 0,
        "earnings_growing": eg is not None and eg > 0,
        "margin_inflecting_up": gmd is not None and gmd > 0,   # the NKE-style turnaround signal
        "profitable": om is not None and om > 0,
        "fcf_positive": fcf is not None and fcf > 0,
    }
    flags["turnaround_score"] = sum(1 for v in flags.values() if v is True)
    return flags


def gross_margin_yoy_delta(quarterly_income_stmt) -> Optional[float]:
    """Latest-quarter gross margin minus the year-ago quarter (4 quarters back).
    Positive = margin inflecting up (the turnaround tell). None if unavailable."""
    try:
        gp = quarterly_income_stmt.loc["Gross Profit"]
        rev = quarterly_income_stmt.loc["Total Revenue"]
    except (KeyError, AttributeError):
        return None
    gm = (gp / rev).dropna()
    if len(gm) < 5:
        return None
    return round(float(gm.iloc[0] - gm.iloc[4]), 4)


def fetch_fundamentals(ticker: str) -> dict:
    """Pull key fundamentals for one ticker (network, best-effort)."""
    import yfinance as yf
    out: dict = {"ticker": ticker}
    try:
        tk = yf.Ticker(ticker)
        info = tk.info or {}
    except Exception as e:  # pragma: no cover - network
        return {"ticker": ticker, "error": str(e)[:80]}
    out.update({
        "revenue_growth_yoy": info.get("revenueGrowth"),
        "earnings_growth_yoy": info.get("earningsGrowth"),
        "gross_margin": info.get("grossMargins"),
        "operating_margin": info.get("operatingMargins"),
        "profit_margin": info.get("profitMargins"),
        "fwd_pe": info.get("forwardPE"),
        "trailing_pe": info.get("trailingPE"),
        "ps_ttm": info.get("priceToSalesTrailing12Months"),
        "fcf": info.get("freeCashflow"),
        "roe": info.get("returnOnEquity"),
        "forward_eps": info.get("forwardEps"),
        "target_low": info.get("targetLowPrice"),
        "target_mean": info.get("targetMeanPrice"),
        "target_high": info.get("targetHighPrice"),
        "price": info.get("currentPrice"),
        "recommendation": info.get("recommendationKey"),
    })
    if out["target_mean"] and out["price"]:
        out["analyst_upside"] = round(out["target_mean"] / out["price"] - 1, 3)
    try:  # pragma: no cover - network
        out["gross_margin_yoy_delta"] = gross_margin_yoy_delta(tk.quarterly_income_stmt)
    except Exception:
        out["gross_margin_yoy_delta"] = None
    out["flags"] = inflection_flags(out)
    return out


def scan(tickers: list[str]) -> list[dict]:
    """Fetch fundamentals for a list of tickers (network). Sorted by turnaround_score."""
    rows = [fetch_fundamentals(t) for t in tickers]
    rows.sort(key=lambda r: r.get("flags", {}).get("turnaround_score", -1), reverse=True)
    return rows


def main() -> int:
    import json
    import sys
    from datetime import datetime, timezone
    from pathlib import Path
    from sharks.backtest.sleeve_classifier import P1_HOLDINGS_USD
    import sharks.scoring.leveraged_etf as L

    watch = sorted({t for t in P1_HOLDINGS_USD if not L.is_leveraged_etf(t)} | {"NKE", "AMZN"})
    rows = scan(watch)
    report = {
        "as_of": datetime.now(timezone.utc).isoformat(),
        "report_type": "fundamentals_tracker",
        "note": ("Key earnings numbers + turnaround-inflection flags (gross-margin YoY "
                 "delta = the 扭轉 tell). yfinance grade-C/D — verify vs 8-K before acting. "
                 "Monitoring only."),
        "rows": rows,
    }
    out = Path("outputs") / "fundamentals-tracker.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print(f"wrote {out}", file=sys.stderr)
    for r in rows[:12]:
        fl = r.get("flags", {})
        print(f"  {r['ticker']:5} turn={fl.get('turnaround_score')} "
              f"rev%={r.get('revenue_growth_yoy')} gmΔ={r.get('gross_margin_yoy_delta')} "
              f"opM={r.get('operating_margin')} fcf+={fl.get('fcf_positive')}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
