"""News-sentiment scorer — closes the chip-flow FSM "利空不跌" gap.

The chip-flow concept page (``philosophy/concepts/chip-flow-single-point-breakout.md``
lines 64–65) defines State 1 wash-out as requiring **bearish news headline that
the tape refuses to follow through**, but flags the leg as
"unavailable, treated as neutral until news NLP is wired". This module wires it.

Pipeline per ticker:

  1. Fetch headlines via ``sharks.data.finnhub_integration.get_company_news``
     (or accept an injected list for tests).
  2. Dispatch each headline as a ``news_nlp`` task through
     ``sharks.ai.dispatcher`` — local Nemotron classifies bullish / bearish /
     neutral with a confidence and a one-line rationale.
  3. Aggregate per ticker: counts + average confidence-weighted score.
  4. Compute today's price delta from the EOD OHLCV frame produced by
     ``sharks.scoring.chip_flow.fetch_daily_ohlcv``.
  5. Flag ``bearish_no_price_follow`` when bearish_count ≥ 2 **and** price held
     (delta ≥ −0.5%). This is the boolean ``chip_flow_fsm.is_wash_out`` consumes
     to add its +0.10 confidence bump.

Output: ``outputs/news-sentiment-YYYY-MM-DD.jsonl`` — one JSON object per
ticker per line. Never raises: every error path produces a row with
``status`` set so downstream consumers can branch.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from sharks.ai import dispatcher as dp
from sharks.ai.nemotron_client import NemotronClient

# Module-level so tests can monkeypatch easily.
try:
    from sharks.data import finnhub_integration as finnhub
except Exception:  # pragma: no cover — defensive; data layer optional at import time
    finnhub = None  # type: ignore[assignment]

try:
    from sharks.scoring.chip_flow import fetch_daily_ohlcv
except Exception:  # pragma: no cover
    fetch_daily_ohlcv = None  # type: ignore[assignment]


# Thresholds — provisional Phase-4 backtest deliverable per concept page.
DEFAULT_THRESHOLDS: dict = {
    "lookback_days": 3,                # headline freshness window
    "min_bearish_for_flag": 2,         # ≥ this many bearish to consider 利空不跌
    "price_hold_threshold_pct": -0.5,  # if price >= this %, treated as "held"
    "min_confidence_to_count": 0.50,   # ignore low-conf classifications
}


def fetch_headlines(ticker: str, as_of: str, lookback_days: int) -> list[dict]:
    """Pull headlines from Finnhub. Returns [] on any failure."""
    if finnhub is None:
        return []
    try:
        as_of_dt = datetime.strptime(as_of, "%Y-%m-%d")
    except ValueError:
        return []
    from_d = (as_of_dt - timedelta(days=lookback_days)).strftime("%Y-%m-%d")
    raw = finnhub.get_company_news(ticker, from_d, as_of)
    if not isinstance(raw, list):
        return []
    return raw


def compute_price_delta_pct(ticker: str, as_of: str) -> Optional[float]:
    """Last-bar % change from yfinance EOD. None on insufficient data."""
    if fetch_daily_ohlcv is None:
        return None
    try:
        df = fetch_daily_ohlcv(ticker, days=10)
    except Exception:
        return None
    if df is None or df.empty or len(df) < 2:
        return None
    try:
        last = float(df["Close"].iloc[-1])
        prev = float(df["Close"].iloc[-2])
        if prev <= 0:
            return None
        return round((last / prev - 1) * 100, 3)
    except Exception:
        return None


def classify_headlines(
    ticker: str, headlines: list[dict], as_of: str,
    *, client: Optional[NemotronClient] = None,
    thresholds: Optional[dict] = None,
) -> dict:
    """Run each headline through the dispatcher and aggregate.

    Returns a dict with: ``ticker``, ``count``, ``counts`` (per label),
    ``score`` (confidence-weighted [-1, +1]), ``classifications`` (per-headline
    label + confidence), ``errors`` (count of failed dispatches).
    """
    thr = thresholds or DEFAULT_THRESHOLDS
    cli = client or NemotronClient()
    counts = {"bullish": 0, "bearish": 0, "neutral": 0}
    score_sum = 0.0
    weight_sum = 0.0
    classifications: list[dict] = []
    errors = 0
    for h in headlines:
        headline_text = (h.get("headline") or "").strip()
        if not headline_text:
            continue
        task = {
            "v": 1, "type": "news_nlp", "as_of": as_of,
            "payload": {
                "ticker": ticker,
                "headline": headline_text,
                "summary": (h.get("summary") or "")[:500],
            },
        }
        result = dp.dispatch(task, client=cli)
        if not result.get("ok"):
            errors += 1
            classifications.append({
                "headline": headline_text[:140],
                "error": result.get("error"),
            })
            continue
        content = result["content"]
        sentiment = content.get("sentiment", "neutral")
        confidence = float(content.get("confidence", 0.0))
        if confidence >= thr["min_confidence_to_count"]:
            counts[sentiment] = counts.get(sentiment, 0) + 1
        # Score: bullish=+1, bearish=-1, neutral=0, weighted by confidence.
        sign = {"bullish": 1.0, "bearish": -1.0, "neutral": 0.0}[sentiment]
        score_sum += sign * confidence
        weight_sum += confidence
        classifications.append({
            "headline": headline_text[:140],
            "sentiment": sentiment,
            "confidence": confidence,
            "rationale": content.get("rationale", "")[:200],
            "cache_hit": result.get("cache_hit", False),
        })

    avg_score = round(score_sum / weight_sum, 3) if weight_sum > 0 else 0.0
    return {
        "ticker": ticker,
        "as_of": as_of,
        "count": len(headlines),
        "counts": counts,
        "score": avg_score,
        "errors": errors,
        "classifications": classifications,
    }


def analyse(
    ticker: str, as_of: str,
    *, headlines: Optional[list[dict]] = None,
    client: Optional[NemotronClient] = None,
    thresholds: Optional[dict] = None,
) -> dict:
    """Full per-ticker analysis. Combines classification + price delta + flag."""
    thr = thresholds or DEFAULT_THRESHOLDS
    if headlines is None:
        headlines = fetch_headlines(ticker, as_of, int(thr["lookback_days"]))
    classification = classify_headlines(
        ticker, headlines, as_of, client=client, thresholds=thr,
    )
    price_delta = compute_price_delta_pct(ticker, as_of)
    bearish_count = classification["counts"]["bearish"]
    price_held = (
        price_delta is not None
        and price_delta >= float(thr["price_hold_threshold_pct"])
    )
    bearish_no_price_follow = bool(
        bearish_count >= int(thr["min_bearish_for_flag"]) and price_held
    )
    return {
        **classification,
        "price_delta_pct": price_delta,
        "price_held": price_held,
        "bearish_no_price_follow": bearish_no_price_follow,
        "status": "ok" if (classification["count"] > 0 or price_delta is not None) else "no_data",
    }


def write_jsonl(out_dir: Path, as_of: str, rows: list[dict]) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"news-sentiment-{as_of}.jsonl"
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")
    return path


def run(tickers: list[str], as_of: str, *, client: Optional[NemotronClient] = None) -> list[dict]:
    cli = client or NemotronClient()
    rows: list[dict] = []
    for t in tickers:
        try:
            row = analyse(t, as_of, client=cli)
        except Exception as exc:
            row = {"ticker": t, "as_of": as_of, "status": "error", "error": str(exc)}
        rows.append(row)
        flag = " *FLAG*" if row.get("bearish_no_price_follow") else ""
        print(
            f"  {t}: n={row.get('count', 0)} "
            f"counts={row.get('counts', {})} "
            f"price={row.get('price_delta_pct')}%{flag}",
            file=sys.stderr,
        )
    return rows


def main() -> int:
    # Tiny argv parse — keep deps zero; pattern matches other scoring scripts.
    args = sys.argv[1:]
    as_of = args[0] if args else datetime.now().strftime("%Y-%m-%d")
    tickers: list[str] = []
    if "--tickers" in args:
        i = args.index("--tickers")
        tickers = args[i + 1:]
    if not tickers:
        # Fallback to chip-flow's default ticker list so it lines up with the FSM.
        try:
            from sharks.scoring.chip_flow import DEFAULT_TICKERS
            tickers = list(DEFAULT_TICKERS)
        except Exception:
            tickers = []
    if not tickers:
        print("usage: python -m sharks.scoring.news_sentiment YYYY-MM-DD --tickers AAPL DELL", file=sys.stderr)
        return 1
    print(f"news_sentiment as of {as_of}: {len(tickers)} tickers", file=sys.stderr)
    rows = run(tickers, as_of)
    out_dir = Path("outputs")
    path = write_jsonl(out_dir, as_of, rows)
    flagged = [r["ticker"] for r in rows if r.get("bearish_no_price_follow")]
    print(f"wrote {path} ({len(rows)} rows, {len(flagged)} bearish_no_price_follow)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
