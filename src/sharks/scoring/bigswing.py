"""季線 / 年線 大波段 — long-horizon position-swing crossover.

The principal's horizon (2026-06-10): decades of MONTHLY bars, but the actionable
level is **quarterly / yearly** (季線/年線) BIG-SWING position trades — multi-quarter
to multi-year legs, not short-term. This is the long-timeframe sibling of
``discord/basecross.py`` (which runs monthly 月線).

Signal (interpretable on long timeframes — a clean two-MA golden cross beats MACD
when there are few bars):
  * resample the monthly close series to quarterly (3-month buckets) or yearly
    (12-month buckets);
  * a fast vs slow SMA golden cross (quarterly 4Q/12Q ≈ 1y/3y; yearly 2y/5y);
  * price reclaiming ABOVE the slow MA (the secular trend turned up);
  * distance from all-time-high (大底 vs 近高乖離);
  * a rising confirmation.

Data: decades of monthly bars from the local lake
(``data/lake/prices/<ticker>_1mo.parquet``, populated by ``data_lake.py`` with
``period="max"``), with a yfinance ``period="max"`` fallback. recommend-only;
never trades. Pure given an injected fetch (tests inject monthly closes).
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

# bucket = months per resampled bar (from a MONTHLY input series).
TIMEFRAMES: dict[str, dict] = {
    "quarterly": {"bucket": 3, "fast": 4, "slow": 12, "label": "季線", "min_bars": 16},
    "yearly":    {"bucket": 12, "fast": 2, "slow": 5, "label": "年線", "min_bars": 7},
}

FetchFn = Callable[[list[str]], dict]


@dataclass
class BigSwingCandidate:
    ticker: str
    timeframe: str
    last: Optional[float] = None
    dist_ath_pct: Optional[float] = None
    golden_cross: bool = False
    above_slow: bool = False
    rising: bool = False
    ma_fast: Optional[float] = None
    ma_slow: Optional[float] = None
    bars: int = 0
    theme: str = ""
    verdict: str = ""
    note: str = ""
    score: float = 0.0


# ── pure helpers ────────────────────────────────────────────────────────────────

def resample(series: list[float], bucket: int, agg: str = "last") -> list[float]:
    """Group a series into ``bucket``-sized buckets; last value (or sum) per bucket."""
    out: list[float] = []
    for i in range(0, len(series), bucket):
        chunk = series[i:i + bucket]
        if not chunk:
            continue
        out.append(chunk[-1] if agg == "last" else float(sum(chunk)))
    return out


def sma(xs: list[float], n: int) -> list[Optional[float]]:
    """Trailing simple moving average aligned to ``xs`` (None until ``n`` samples)."""
    out: list[Optional[float]] = []
    for i in range(len(xs)):
        if i + 1 < n:
            out.append(None)
        else:
            out.append(sum(xs[i + 1 - n:i + 1]) / n)
    return out


def _classify(c: BigSwingCandidate, label: str) -> None:
    d = c.dist_ath_pct or 0.0
    if c.golden_cross and c.above_slow and c.rising:
        c.verdict = f"🟢 {label}金叉 + 站上長均 + 趨勢翻揚"
        c.note = f"{label}快慢均黃金交叉、收復長均、距高 {d:.0f}% — 大波段轉折確認"
    elif c.golden_cross and c.above_slow:
        c.verdict = f"🟡 {label}金叉 · 待趨勢確認"
        c.note = f"{label}金叉且站上長均,但動能未明顯翻揚(距高 {d:.0f}%)"
    elif c.above_slow and c.rising:
        c.verdict = f"🔵 {label}多頭續抱 · 未新轉折"
        c.note = f"已在長均之上續揚(距高 {d:.0f}%);非新進場點,續抱觀察"
    elif d > 70:
        c.verdict = "⚠️ 長空/深跌(落刀?)"
        c.note = f"距高 {d:.0f}% 且在長均下,需查價值陷阱/結構衰退"
    elif not c.above_slow:
        c.verdict = f"🔻 {label}長空 · 待築底翻揚"
        c.note = f"仍在長均之下(距高 {d:.0f}%);等收復長均 + 金叉再談大波段"
    else:
        c.verdict = "〽️ 近高/乖離"
        c.note = f"距高僅 {d:.0f}%,非大底起漲"
    # rank: golden cross + trend reclaim weigh most; deep-base sweet spot ~50% off.
    sweet = max(0.0, 1 - abs(d - 50) / 50)
    c.score = round(40 * (1 if (c.golden_cross and c.above_slow) else 0)
                    + 25 * (1 if c.above_slow else 0)
                    + 20 * sweet + 15 * (1 if c.rising else 0), 1)


def assess(ticker: str, monthly_closes: list[float], timeframe: str,
           *, theme: str = "") -> BigSwingCandidate:
    """Score ONE ticker's monthly-close series at the quarterly/yearly level. Pure."""
    cfg = TIMEFRAMES[timeframe]
    c = BigSwingCandidate(ticker=ticker, timeframe=timeframe, theme=theme)
    bars = resample(monthly_closes, cfg["bucket"], agg="last")
    c.bars = len(bars)
    if len(bars) < cfg["min_bars"]:
        c.verdict = "資料不足"
        c.note = f"{cfg['label']}樣本不足(需 ≥{cfg['min_bars']} 根 = ~{cfg['min_bars']*cfg['bucket']} 個月)"
        return c
    last, ath = bars[-1], max(bars)
    c.last = round(last, 2)
    c.dist_ath_pct = round((ath - last) / ath * 100, 1) if ath else 0.0
    f, s = sma(bars, cfg["fast"]), sma(bars, cfg["slow"])
    if f[-1] is not None and f[-2] is not None and s[-1] is not None and s[-2] is not None:
        c.ma_fast, c.ma_slow = round(f[-1], 2), round(s[-1], 2)
        c.golden_cross = f[-2] <= s[-2] and f[-1] > s[-1]
        c.above_slow = last > s[-1]
        c.rising = last > bars[-2] and (f[-1] >= f[-2])
    _classify(c, cfg["label"])
    return c


def screen_bigswing(tickers: list[str], *, fetch: FetchFn, timeframe: str = "quarterly",
                    theme_by_ticker: Optional[dict] = None) -> list[BigSwingCandidate]:
    """Screen a universe at the 季線/年線 level. ``fetch(tickers) -> {t: [monthly closes]}``
    (decades of monthly bars). Pure given ``fetch``."""
    if timeframe not in TIMEFRAMES:
        raise ValueError(f"timeframe must be one of {tuple(TIMEFRAMES)}, got {timeframe!r}")
    theme_by_ticker = theme_by_ticker or {}
    data = fetch(tickers)
    out = [assess(t, (data.get(t) or []), timeframe, theme=theme_by_ticker.get(t, ""))
           for t in tickers]
    out.sort(key=lambda x: x.score, reverse=True)
    return out


# ── data: decades of monthly bars (lake-first, yfinance fallback) ─────────────────

def fetch_monthly_lake(tickers: list[str], *, lake_dir: Path = Path("data/lake/prices"),
                       network_fallback: bool = True) -> dict[str, list[float]]:
    """{ticker: [monthly closes]} — lake parquet first (free, decades), else yfinance
    ``period='max', interval='1mo'``. Skips names with no data (never invents)."""
    out: dict[str, list[float]] = {}
    for t in tickers:
        p = Path(lake_dir) / f"{t}_1mo.parquet"
        if p.exists():
            try:
                import pandas as pd
                df = pd.read_parquet(p)
                closes = [float(x) for x in df["Close"].dropna().tolist()]
                if closes:
                    out[t] = closes
                    continue
            except Exception:
                pass
        if network_fallback:
            try:
                import yfinance as yf
                h = yf.Ticker(t).history(period="max", interval="1mo", auto_adjust=True)
                closes = [float(x) for x in h["Close"].dropna().tolist()]
                if closes:
                    out[t] = closes
            except Exception:
                continue
    return out


def run(scope_or_tickers, *, timeframe: str = "quarterly", out_dir=Path("outputs"),
        write: bool = True, fetch: Optional[FetchFn] = None) -> dict:
    """Resolve a basecross scope (or explicit tickers) → screen → write a recommend-only
    artifact. ``fetch`` injectable for tests; defaults to the lake-first fetch."""
    if isinstance(scope_or_tickers, str):
        try:
            from sharks.discord.basecross import scope_universe
            title, tickers = scope_universe(scope_or_tickers)
        except Exception:
            title, tickers = scope_or_tickers, [scope_or_tickers.upper()]
    else:
        title, tickers = "custom", list(scope_or_tickers)
    fetch = fetch or fetch_monthly_lake
    sigs = screen_bigswing(tickers, fetch=fetch, timeframe=timeframe)
    label = TIMEFRAMES[timeframe]["label"]
    rows = [{"ticker": c.ticker, "timeframe": c.timeframe, "verdict": c.verdict,
             "dist_ath_pct": c.dist_ath_pct, "golden_cross": c.golden_cross,
             "above_slow": c.above_slow, "rising": c.rising, "score": c.score,
             "ma_fast": c.ma_fast, "ma_slow": c.ma_slow, "bars": c.bars, "note": c.note}
            for c in sigs]
    report = {"as_of": _today(), "schema_version": 1, "recommend_only": True,
              "report_type": "bigswing", "timeframe": timeframe, "label": label,
              "scope": title, "n": len(rows), "ranked": rows}
    if write:
        od = Path(out_dir)
        od.mkdir(parents=True, exist_ok=True)
        (od / f"bigswing-{timeframe}-{report['as_of']}.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def _today() -> str:
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d")


def main(argv: Optional[list[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    timeframe = "quarterly"
    pos = []
    for a in argv:
        if a in TIMEFRAMES:
            timeframe = a
        else:
            pos.append(a)
    if not pos:
        print("用法:python -m sharks.scoring.bigswing <scope|TICKER...> [quarterly|yearly]\n"
              "  scope: space ipo payments ai_software broadening power crypto all ...\n"
              "  例:python -m sharks.scoring.bigswing ipo yearly", file=sys.stderr)
        return 2
    scope = pos[0] if len(pos) == 1 else pos
    rep = run(scope, timeframe=timeframe)
    print(f"大波段 {rep['label']}({timeframe})— {rep['scope']} · {rep['n']} 檔")
    for r in rep["ranked"][:30]:
        gc = "金叉" if r["golden_cross"] else ("站均上" if r["above_slow"] else "均下")
        d = f"{r['dist_ath_pct']:.0f}%" if r["dist_ath_pct"] is not None else "–"
        print(f"  {r['ticker']:<6} C{r['score']:>5.0f} 距高{d:>5} [{gc}] · {r['verdict']}")
    print("recommend-only · 季/年線大波段 · 連續起漲+題材+regime 健檢才考慮 · 永不下單")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
