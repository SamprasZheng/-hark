"""Earnings-date calendar — free, lake-first, with annual-recurrence prediction.

The earnings date is the most actionable per-ticker catalyst: it gates the
blackout (no new entry within N days) AND anchors the IV / 隱波 plays the playbook
tracks (pre-earnings IV ramp, post-earnings vol crush). Earnings recur ~quarterly
and land in roughly the same calendar weeks each year, so a local history is both
a cache (cuts API calls) and a predictor.

Sources, in priority:
  1. LOCAL lake — ``data/lake/info/<ticker>.json`` already carries yfinance
     ``earningsTimestamp`` + ``isEarningsDateEstimate`` (FREE, already cached).
  2. (optional) Finnhub free earnings calendar, if ``FINNHUB_API_KEY`` is set.
  3. PREDICT from history (most-recent + ~quarterly cadence) when neither gives a
     future date.

Persisted GITIGNORED to ``data/earnings/calendar.jsonl`` (append-only observations)
+ a ``data/earnings/upcoming-<date>.json`` summary. recommend-only; never trades.
Zero new deps (stdlib + reads the lake json).
"""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

LAKE_INFO = Path("data/lake/info")
EARNINGS_DIR = Path("data/earnings")
HISTORY = EARNINGS_DIR / "calendar.jsonl"

# Mirror finviz_elite.EARNINGS_BLACKOUT_DAYS / risk_config earnings_blackout_tier1_days.
EARNINGS_BLACKOUT_DAYS = 3
QUARTER_DAYS = 91          # ~quarterly cadence for prediction
DEFAULT_UPCOMING_WINDOW = 14


# ── pure helpers ────────────────────────────────────────────────────────────────

def _ts_to_date(ts) -> Optional[str]:
    """Unix seconds → 'YYYY-MM-DD' (UTC day), or None."""
    if ts is None:
        return None
    try:
        return datetime.fromtimestamp(float(ts), tz=timezone.utc).strftime("%Y-%m-%d")
    except (ValueError, OverflowError, OSError, TypeError):
        return None


def lake_earnings(info: dict) -> Optional[dict]:
    """Extract the earnings record from a yfinance ``.info`` dict (or None).

    Uses ``earningsTimestamp`` as the headline date, with the estimate window
    (``earningsTimestampStart/End``) and ``isEarningsDateEstimate`` flag."""
    ts = info.get("earningsTimestamp")
    d = _ts_to_date(ts)
    if d is None:
        return None
    return {
        "date": d,
        "start": _ts_to_date(info.get("earningsTimestampStart")),
        "end": _ts_to_date(info.get("earningsTimestampEnd")),
        "is_estimate": bool(info.get("isEarningsDateEstimate", False)),
        "most_recent_quarter": _ts_to_date(info.get("mostRecentQuarter")),
        "source": "lake",
        "snapshot_time": info.get("_snapshot_time"),
    }


def days_to_earnings(earnings_date: str, asof: Optional[str] = None) -> Optional[int]:
    """Calendar days from ``asof`` (default today) to ``earnings_date`` (YYYY-MM-DD)."""
    if not earnings_date:
        return None
    a = date.fromisoformat(asof) if asof else date.today()
    try:
        return (date.fromisoformat(earnings_date[:10]) - a).days
    except ValueError:
        return None


def in_blackout(days_to: Optional[int], window: int = EARNINGS_BLACKOUT_DAYS) -> bool:
    """True if earnings is within the next ``window`` days (no new entry / trim)."""
    return days_to is not None and 0 <= days_to <= window


def predict_next(last_date: str, asof: Optional[str] = None,
                 cadence_days: int = QUARTER_DAYS) -> Optional[str]:
    """Roll a known earnings date forward in ~quarterly steps until it's > asof.

    Earnings recur ~every 91 days in roughly the same season; this projects the
    next likely report when no fresh future date is available."""
    a = date.fromisoformat(asof) if asof else date.today()
    try:
        d = date.fromisoformat(last_date[:10])
    except ValueError:
        return None
    if cadence_days <= 0:
        return None
    while d <= a:
        d = d + timedelta(days=cadence_days)
    return d.isoformat()


# ── history (append-only, gitignored) ────────────────────────────────────────────

def load_history(path: Path = HISTORY) -> dict:
    """{ticker: sorted unique observed earnings dates} from the append-only jsonl."""
    out: dict[str, set] = {}
    p = Path(path)
    if not p.exists():
        return {}
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        t, d = rec.get("ticker"), rec.get("date")
        if t and d:
            out.setdefault(t, set()).add(d[:10])
    return {t: sorted(ds) for t, ds in out.items()}


def append_history(records: list[dict], path: Path = HISTORY) -> int:
    """Append (ticker, date) observations, deduped against existing history.
    Returns the number of NEW rows written."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    seen = {(t, d) for t, ds in load_history(path).items() for d in ds}
    new = []
    for r in records:
        t, d = r.get("ticker"), r.get("date")
        if t and d and (t, d[:10]) not in seen:
            seen.add((t, d[:10]))
            new.append({"ticker": t, "date": d[:10], "is_estimate": r.get("is_estimate"),
                        "source": r.get("source", "lake"),
                        "observed_at": datetime.now(timezone.utc).isoformat()})
    if new:
        with path.open("a", encoding="utf-8") as fh:
            for r in new:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    return len(new)


# ── resolution ────────────────────────────────────────────────────────────────

def read_lake(lake_dir: Path = LAKE_INFO) -> dict:
    """{ticker: lake_earnings record} for every info json that carries an earnings date."""
    d = Path(lake_dir)
    out: dict[str, dict] = {}
    if not d.exists():
        return out
    for f in sorted(d.glob("*.json")):
        try:
            info = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        rec = lake_earnings(info)
        if rec:
            out[f.stem.upper()] = {"ticker": f.stem.upper(), **rec}
    return out


def next_earnings(ticker: str, *, lake: Optional[dict] = None, history: Optional[dict] = None,
                  asof: Optional[str] = None) -> Optional[dict]:
    """Resolve the next FUTURE earnings date for one ticker.

    Prefers the lake's ``earningsTimestamp`` when it's on/after ``asof``; otherwise
    predicts from the most recent known date (lake or history) at quarterly cadence.
    Returns {ticker, date, source, is_estimate, days_to, predicted}."""
    ticker = ticker.upper()
    a = asof or date.today().isoformat()
    rec = (lake or {}).get(ticker)
    candidates: list[str] = []
    if rec and rec.get("date"):
        candidates.append(rec["date"])
    for d in (history or {}).get(ticker, []):
        candidates.append(d)
    if not candidates:
        return None
    # A genuine future date from the lake/history → use it directly.
    future = sorted(d for d in candidates if d >= a)
    if future:
        d = future[0]
        is_est = rec.get("is_estimate") if rec and rec.get("date") == d else None
        return {"ticker": ticker, "date": d, "source": "lake" if rec else "history",
                "is_estimate": is_est, "days_to": days_to_earnings(d, a), "predicted": False}
    # Otherwise predict forward from the most recent known date.
    last = max(candidates)
    pred = predict_next(last, a)
    if pred is None:
        return None
    return {"ticker": ticker, "date": pred, "source": "predicted", "is_estimate": True,
            "days_to": days_to_earnings(pred, a), "predicted": True, "anchored_on": last}


def upcoming_within(lake: dict, *, asof: Optional[str] = None,
                    days: int = DEFAULT_UPCOMING_WINDOW, history: Optional[dict] = None) -> list[dict]:
    """Tickers reporting within the next ``days`` days, sorted soonest-first.
    Powers the playbook / brief 財報季 watch + the blackout list."""
    a = asof or date.today().isoformat()
    out = []
    for t in sorted(set(lake) | set(history or {})):
        ne = next_earnings(t, lake=lake, history=history, asof=a)
        if ne and ne["days_to"] is not None and 0 <= ne["days_to"] <= days:
            ne["blackout"] = in_blackout(ne["days_to"])
            out.append(ne)
    out.sort(key=lambda r: r["days_to"])
    return out


# ── optional Finnhub enrichment (best-effort, gated on key) ───────────────────────

def fetch_finnhub(symbol: str, *, asof: Optional[str] = None, token: Optional[str] = None,
                  opener=None, horizon_days: int = 120) -> Optional[dict]:
    """Finnhub free earnings calendar for one symbol → {date, source:'finnhub'} or None.
    No-op (returns None) when no token. Best-effort: any failure degrades to None —
    never raises, never blocks the lake-first path."""
    import os
    import urllib.parse
    import urllib.request

    token = token or os.environ.get("FINNHUB_API_KEY", "").strip()
    if not token:
        return None
    a = date.fromisoformat(asof) if asof else date.today()
    params = {"symbol": symbol.upper(), "from": a.isoformat(),
              "to": (a + timedelta(days=horizon_days)).isoformat(), "token": token}
    url = "https://finnhub.io/api/v1/calendar/earnings?" + urllib.parse.urlencode(params)
    try:
        opener = opener or urllib.request.urlopen
        req = urllib.request.Request(url, headers={"User-Agent": "sharks-earnings/0.1"})
        with opener(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        rows = data.get("earningsCalendar") or []
        future = sorted(r.get("date") for r in rows if r.get("date") and r["date"] >= a.isoformat())
        if future:
            return {"ticker": symbol.upper(), "date": future[0], "source": "finnhub",
                    "is_estimate": True, "days_to": days_to_earnings(future[0], a.isoformat())}
    except Exception:
        return None
    return None


# ── orchestration ────────────────────────────────────────────────────────────────

def build_calendar(*, lake_dir: Path = LAKE_INFO, out_dir: Path = Path("data/earnings"),
                   asof: Optional[str] = None, window: int = DEFAULT_UPCOMING_WINDOW,
                   history_path: Path = HISTORY, write: bool = True) -> dict:
    """Read the lake → append history → compute upcoming/blackout → write the summary.

    Lake-first + prediction; fully offline. Returns the summary dict."""
    a = asof or date.today().isoformat()
    lake = read_lake(lake_dir)
    # Append every observed (non-predicted) lake date to the append-only history.
    new_rows = append_history(list(lake.values()), history_path) if write else 0
    history = load_history(history_path)
    upcoming = upcoming_within(lake, asof=a, days=window, history=history)
    blackout = [r["ticker"] for r in upcoming if r.get("blackout")]
    summary = {
        "as_of": a,
        "schema_version": 1,
        "recommend_only": True,
        "tickers_with_dates": len(lake),
        "history_rows_added": new_rows,
        "window_days": window,
        "upcoming": upcoming,
        "blackout": sorted(blackout),
        "note": ("Lake-first (yfinance earningsTimestamp, free). predicted=True dates are "
                 "quarterly-cadence projections, not confirmed. Cross-check confirmed dates "
                 "against the official IR / Finviz/Finnhub calendar before acting."),
    }
    if write:
        od = Path(out_dir)
        od.mkdir(parents=True, exist_ok=True)
        (od / f"upcoming-{a}.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


def main() -> int:
    import sys
    s = build_calendar()
    print(f"earnings calendar — {s['tickers_with_dates']} tickers, "
          f"+{s['history_rows_added']} history rows; {len(s['upcoming'])} reporting "
          f"in next {s['window_days']}d, {len(s['blackout'])} in blackout (<= "
          f"{EARNINGS_BLACKOUT_DAYS}d)", file=sys.stderr)
    for r in s["upcoming"][:25]:
        tag = " ⚠️BLACKOUT" if r.get("blackout") else ""
        pred = " (predicted)" if r.get("predicted") else ""
        print(f"  {r['ticker']:<6} {r['date']}  T-{r['days_to']:>3}d{pred}{tag}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
