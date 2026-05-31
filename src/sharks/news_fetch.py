"""Free multi-source market-news fetcher → fills the daily_brief news slot.

Pulls headlines from several FREE public RSS feeds (no API key) with graceful
per-source fallback, dedupes, and writes outputs/news-headlines-<date>.json, which
daily_brief.load_news reads to populate the event-driven 隔夜頭條 / 速解讀 layer.

RSS is public, low-volume (a handful of GETs once per run) — this respects the
no-aggressive-scraping rule. stdlib only (urllib + ElementTree); zero new deps.
Best-effort: any source can fail without breaking the run. Educational/observe-first.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

# Free public RSS feeds (no key). Order = priority (market-targeted first so the top
# headlines are finance-relevant); "多網站備選" — partial failure is fine.
SOURCES = [
    ("Google News-Markets",
     "https://news.google.com/rss/search?q=stock+market+OR+federal+reserve+OR+nasdaq+OR+nvidia+OR+earnings+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("MarketWatch", "http://feeds.marketwatch.com/marketwatch/topstories/"),
    ("CNBC-Finance", "https://www.cnbc.com/id/10000664/device/rss/rss.html"),
    ("Nasdaq", "https://www.nasdaq.com/feed/rssoutbound?category=Markets"),
    ("Investing.com", "https://www.investing.com/rss/news_25.rss"),
    ("Fed-Press", "https://www.federalreserve.gov/feeds/press_all.xml"),
    ("CNBC", "https://www.cnbc.com/id/100003114/device/rss/rss.html"),
    ("Yahoo Finance", "https://finance.yahoo.com/news/rssindex"),
]
_UA = "Mozilla/5.0 (compatible; sharks-daily-brief RSS reader)"


def _strip_ns(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def parse_rss_xml(data) -> list[tuple]:
    """Parse RSS or Atom bytes/str → [(title, link), ...]. PURE (no network)."""
    import xml.etree.ElementTree as ET
    out: list[tuple] = []
    try:
        root = ET.fromstring(data)
    except Exception:
        return out
    for el in root.iter():
        if _strip_ns(el.tag) not in ("item", "entry"):
            continue
        title, link = None, None
        for ch in el:
            t = _strip_ns(ch.tag)
            if t == "title" and (ch.text or "").strip():
                title = ch.text.strip()
            elif t == "link" and link is None:
                link = ((ch.text or "").strip() or ch.get("href") or "").strip()
        if title:
            out.append((title, link or ""))
    return out


def fetch_rss(url: str, timeout: int = 8) -> list[tuple]:
    """Fetch + parse one RSS feed. Network; raises on failure (caller handles)."""
    import urllib.request
    req = urllib.request.Request(url, headers={"User-Agent": _UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:  # noqa: S310 (public RSS)
        return parse_rss_xml(r.read())


def collect(sources=SOURCES, per_source: int = 4, max_total: int = 10) -> dict:
    """Aggregate headlines across sources with graceful fallback + dedupe."""
    seen, items, ok, failed = set(), [], [], []
    for name, url in sources:
        try:
            rows = fetch_rss(url)[:per_source]
        except Exception:
            failed.append(name)
            continue
        if not rows:
            failed.append(name)
            continue
        ok.append(name)
        for title, link in rows:
            key = title.lower()[:60]
            if key in seen:
                continue
            seen.add(key)
            items.append({"title": title, "link": link, "source": name})
    return {"items": items[:max_total], "sources_ok": ok, "sources_failed": failed}


def fetch_and_write(out_dir: str = "outputs", date: Optional[str] = None) -> dict:
    from datetime import datetime, timedelta, timezone
    tpe = timezone(timedelta(hours=8))
    date = date or datetime.now(tpe).strftime("%Y-%m-%d")
    agg = collect()
    headlines = [f"{it['title']} — {it['source']}" for it in agg["items"]]
    payload = {
        "as_of": datetime.now(timezone.utc).isoformat(), "date": date,
        "headlines": headlines, "items": agg["items"],
        "sources_ok": agg["sources_ok"], "sources_failed": agg["sources_failed"],
        "note": "Free public RSS aggregate (grade C/D — headlines only, not verified). Educational.",
    }
    od = Path(out_dir)
    od.mkdir(parents=True, exist_ok=True)
    (od / f"news-headlines-{date}.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return payload


def main(argv=None) -> int:
    import argparse
    import sys
    ap = argparse.ArgumentParser(prog="news-fetch", description="free multi-source market-news RSS → news slot")
    ap.add_argument("--out-dir", default="outputs")
    args = ap.parse_args(argv)
    p = fetch_and_write(args.out_dir)
    print(f"news: {len(p['headlines'])} headlines | ok={p['sources_ok']} | failed={p['sources_failed']}", file=sys.stderr)
    for h in p["headlines"]:
        print(f"  - {h}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
