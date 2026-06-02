"""Finnhub integration — Insider + 13F + News Sentiment.

Setup:
  1. 註冊 https://finnhub.io/(免費 tier)
  2. 取 API key
  3. 在 .env 加: FINNHUB_API_KEY=your_key_here
  4. 或環境變數設好

Free tier:60 req/min — 夠每日跑 50-100 ticker
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

API_KEY = os.environ.get("FINNHUB_API_KEY")
BASE = "https://finnhub.io/api/v1"


def call(endpoint: str, params: dict = None) -> Optional[dict]:
    """Call Finnhub endpoint with rate limit safety."""
    if not API_KEY:
        return {"error": "FINNHUB_API_KEY not set in env"}
    params = params or {}
    params["token"] = API_KEY
    query = "&".join(f"{k}={v}" for k, v in params.items())
    url = f"{BASE}/{endpoint}?{query}"
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        return {"error": str(e)}


def get_insider_transactions(ticker: str, from_date: str = None, to_date: str = None) -> dict:
    """SEC Form 4 transactions for ticker.

    Returns: { "data": [...transactions...], "symbol": ticker }
    Each transaction has: name, share, change, filingDate, transactionDate, transactionCode, etc.
    """
    params = {"symbol": ticker}
    if from_date:
        params["from"] = from_date
    if to_date:
        params["to"] = to_date
    return call("stock/insider-transactions", params) or {}


def get_insider_sentiment(ticker: str, from_date: str = None, to_date: str = None) -> dict:
    """Insider sentiment score (Finnhub-computed)."""
    params = {"symbol": ticker}
    if from_date:
        params["from"] = from_date
    if to_date:
        params["to"] = to_date
    return call("stock/insider-sentiment", params) or {}


def get_institutional_ownership(ticker: str, limit: int = 20) -> dict:
    """13F filings — institutional holders."""
    return call("stock/institutional-ownership", {"symbol": ticker, "limit": limit}) or {}


def get_company_news(ticker: str, from_date: str, to_date: str) -> list:
    """Company-specific news (each has headline, datetime, url, source, summary)."""
    return call("company-news", {"symbol": ticker, "from": from_date, "to": to_date}) or []


def get_news_sentiment(ticker: str) -> dict:
    """Finnhub-computed news sentiment (-1 to +1)."""
    return call("news-sentiment", {"symbol": ticker}) or {}


def get_earnings_calendar(from_date: str, to_date: str) -> dict:
    """Upcoming earnings calendar."""
    return call("calendar/earnings", {"from": from_date, "to": to_date}) or {}


def get_recommendation_trends(ticker: str) -> list:
    """Analyst recommendation trends (strongBuy/buy/hold/sell/strongSell counts)."""
    return call("stock/recommendation", {"symbol": ticker}) or []


def chip_flow_score(ticker: str) -> dict:
    """Combined Finnhub-driven chip flow score."""
    if not API_KEY:
        return {"error": "FINNHUB_API_KEY not set; run with API key"}

    insider = get_insider_transactions(ticker)
    sentiment = get_insider_sentiment(ticker)
    inst = get_institutional_ownership(ticker, limit=10)
    news_sent = get_news_sentiment(ticker)
    recs = get_recommendation_trends(ticker)

    score = 50
    flags = []

    # Insider net buys past 90 days
    if insider and "data" in insider:
        recent = insider["data"][:20]  # most recent 20
        net_change = sum(t.get("change", 0) for t in recent)
        if net_change > 0:
            score += 15
            flags.append(f"INSIDER_NET_BUY_{net_change}")
        elif net_change < -50000:
            score -= 15
            flags.append("INSIDER_HEAVY_SELLING")

    # Insider sentiment
    if sentiment and "data" in sentiment:
        recent_mspr = [d.get("mspr", 0) for d in sentiment.get("data", [])[-3:]]
        if recent_mspr:
            avg_mspr = sum(recent_mspr) / len(recent_mspr)
            if avg_mspr > 0.5:
                score += 10
                flags.append(f"BULLISH_INSIDER_SENTIMENT_{avg_mspr:.2f}")
            elif avg_mspr < -0.5:
                score -= 10
                flags.append(f"BEARISH_INSIDER_SENTIMENT_{avg_mspr:.2f}")

    # News sentiment
    if news_sent and "companyNewsScore" in news_sent:
        s = news_sent["companyNewsScore"]
        if s > 0.7:
            score += 10
            flags.append("STRONG_POSITIVE_NEWS")
        elif s < 0.3:
            score -= 10
            flags.append("WEAK_NEWS")

    # Analyst trend
    if recs and len(recs) >= 2:
        latest = recs[0]
        prev = recs[1]
        bull_change = (latest.get("strongBuy", 0) + latest.get("buy", 0)) - \
                       (prev.get("strongBuy", 0) + prev.get("buy", 0))
        if bull_change > 0:
            score += 5
            flags.append(f"ANALYST_UPGRADES_+{bull_change}")
        elif bull_change < 0:
            score -= 5
            flags.append(f"ANALYST_DOWNGRADES_{bull_change}")

    return {
        "ticker": ticker,
        "finnhub_chip_score": max(0, min(100, score)),
        "flags": flags,
        "raw": {
            "insider_count": len(insider.get("data", [])) if insider else 0,
            "news_sentiment": news_sent.get("companyNewsScore"),
            "analyst_recs_latest": recs[0] if recs else None,
        },
    }


def main():
    out_dir = Path("outputs")
    out_dir.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")

    if not API_KEY:
        print("⚠️  FINNHUB_API_KEY not set", file=sys.stderr)
        print("    To enable: set FINNHUB_API_KEY in env", file=sys.stderr)
        print("    Free key: https://finnhub.io/", file=sys.stderr)
        report = {
            "as_of": datetime.now(timezone.utc).isoformat(),
            "status": "NO_API_KEY",
            "setup_instructions": [
                "1. Sign up at https://finnhub.io/",
                "2. Get free API key (no credit card)",
                "3. Set FINNHUB_API_KEY env var",
                "4. Re-run this module",
            ],
            "free_tier_limits": "60 req/min, sufficient for daily scan of 50-100 tickers",
            "modules_ready_to_call": [
                "get_insider_transactions(ticker)",
                "get_insider_sentiment(ticker)",
                "get_institutional_ownership(ticker)",
                "get_company_news(ticker, from, to)",
                "get_news_sentiment(ticker)",
                "get_earnings_calendar(from, to)",
                "get_recommendation_trends(ticker)",
                "chip_flow_score(ticker)",
            ],
        }
    else:
        # Run sample call to verify
        test_tickers = ["NVDA", "MSFT", "LMT", "AAPL", "NTLA"]
        print(f"Running Finnhub chip flow on {len(test_tickers)} tickers...", file=sys.stderr)
        results = []
        for t in test_tickers:
            try:
                results.append(chip_flow_score(t))
                time.sleep(1.5)  # rate limit safety
            except Exception as e:
                print(f"  {t} failed: {e}", file=sys.stderr)
        report = {
            "as_of": datetime.now(timezone.utc).isoformat(),
            "status": "OK",
            "sample_results": results,
        }

    out_path = out_dir / f"finnhub-test-{today}.json"
    out_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"wrote {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
