"""抄底起漲 dip-buy screener — the H2-2026 頂底互換 rotation thesis.

Principal directive (2026-06-01): 賣弱、抄底「**距 ATH 有一段 + 盈利支持 + 開始起漲**」
的軟體/AI 落後股。預計 2026 下半年頂底互換:半導體撐盤、軟體股暴漲;同時觀察加密/
fintech 類股。This is the BUY side that pairs with feedback.py's rotation throttle
(throttle = WHEN to rotate; this = WHAT to rotate into).

The three criteria map cleanly onto real price metrics:
  * 距 ATH 有一段  → distance below the all-time / 52w high in a sweet spot (beaten,
                    not extended at highs, not a destroyed falling-knife).
  * 開始起漲      → short-term momentum turning up (1m return > 0 and above the
                    50d MA, or 1m clearly leading 3m).
  * 盈利支持      → FOM `quality` dim where the name is in the latest scan; else TBD
                    (flagged honestly — quality needs the fundamentals pass).

Self-contained: closes are fetched via yfinance (injectable as ``fetch`` for
tests). recommend-only — screens a watchlist, never trades.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

from sharks.discord.config import Settings

# Canonical thesis lists (mirrored in watchlist/thesis_dipbuy.yaml for /notebook).
SOFTWARE_AI_DIPBUY = ["ADBE", "MSFT", "NOW", "CRM", "META", "AI", "SOUN", "OUST", "DOCN", "RIVN"]
CRYPTO_FINTECH_OBSERVE = ["HOOD", "SOFI", "RUN", "ENPH", "MSTR", "BTC", "ETH", "SOL", "DOT"]
_CRYPTO = {"BTC", "ETH", "SOL", "DOT", "ADA", "AVAX", "LINK"}   # → -USD on yfinance

FetchFn = Callable[[list[str]], dict[str, list[float]]]


@dataclass
class DipCandidate:
    ticker: str
    last: Optional[float] = None
    dist_ath_pct: Optional[float] = None     # 距歷史高 %
    dist_52w_pct: Optional[float] = None      # 距 52 週高 %
    ret_1m: Optional[float] = None
    ret_3m: Optional[float] = None
    rising: bool = False                      # 起漲?
    quality: Optional[float] = None           # 盈利支持(FOM quality)
    dip_score: float = 0.0
    verdict: str = ""
    note: str = ""


def _yf_symbol(t: str) -> str:
    return f"{t}-USD" if t.upper() in _CRYPTO else t


def default_fetch(tickers: list[str], period: str = "2y") -> dict[str, list[float]]:
    """Per-ticker closes via yfinance. Robust (skips failures). Crypto → -USD."""
    import yfinance as yf

    out: dict[str, list[float]] = {}
    for t in tickers:
        try:
            h = yf.Ticker(_yf_symbol(t)).history(period=period, auto_adjust=True)
            cs = [float(x) for x in h["Close"].dropna().tolist()]
            if len(cs) >= 30:
                out[t] = cs
        except Exception:
            continue
    return out


def _metrics(cs: list[float]) -> dict:
    last, ath = cs[-1], max(cs)
    w52 = cs[-252:] if len(cs) >= 252 else cs
    h52 = max(w52)
    sma50 = sum(cs[-50:]) / min(50, len(cs))

    def ret(n: int) -> float:
        return (last / cs[-n] - 1) * 100 if len(cs) > n else 0.0

    return {
        "last": last,
        "dist_ath": (ath - last) / ath * 100 if ath else 0.0,
        "dist_52w": (h52 - last) / h52 * 100 if h52 else 0.0,
        "ret_1m": ret(21),
        "ret_3m": ret(63),
        "above_sma50": last > sma50,
    }


def _verdict(c: DipCandidate, *, beaten_min: float, beaten_max: float,
             qual_min: float) -> None:
    d = c.dist_ath_pct or 0.0
    has_q = c.quality is not None
    q_ok = (c.quality or 0) >= qual_min
    if d < beaten_min:
        c.verdict, c.note = "近高不抄", f"距高僅 {d:.0f}%,沒回檔空間"
    elif d > beaten_max:
        c.verdict, c.note = "⚠️ 跌太深", f"距高 {d:.0f}%(落刀?需查基本面)"
    elif c.rising and (q_ok or not has_q):
        c.verdict = "🟢 抄底起漲候選" if has_q else "🟡 起漲·盈利待確認"
        c.note = f"距高 {d:.0f}% + 起漲(1m {c.ret_1m:+.0f}%)" + (f" + 盈利 q={c.quality:.0f}" if has_q else "")
    elif c.rising:
        c.verdict, c.note = "🟡 起漲但盈利弱", f"q={c.quality:.0f} < {qual_min:.0f}"
    else:
        c.verdict, c.note = "🔵 抄底待起漲", f"距高 {d:.0f}% 已到位,等動能轉強(1m {c.ret_1m:+.0f}%)"
    # ranking: reward sweet-spot beatenness + rising + quality
    sweet = max(0.0, 1 - abs(d - 40) / 40)        # peak at ~40% off high
    c.dip_score = round(60 * sweet + (25 if c.rising else 0)
                        + 0.15 * (c.quality or 0), 1)


def screen(tickers: list[str], *, fetch: FetchFn = default_fetch,
           quality_by_ticker: Optional[dict[str, float]] = None,
           beaten_min: float = 15.0, beaten_max: float = 70.0,
           qual_min: float = 50.0) -> list[DipCandidate]:
    quality_by_ticker = quality_by_ticker or {}
    closes = fetch(tickers)
    out: list[DipCandidate] = []
    for t in tickers:
        c = DipCandidate(ticker=t, quality=quality_by_ticker.get(t))
        cs = closes.get(t)
        if not cs:
            c.verdict, c.note = "資料不足", "yfinance 無資料 / 待納入"
            out.append(c)
            continue
        m = _metrics(cs)
        c.last, c.dist_ath_pct, c.dist_52w_pct = round(m["last"], 2), round(m["dist_ath"], 1), round(m["dist_52w"], 1)
        c.ret_1m, c.ret_3m = round(m["ret_1m"], 1), round(m["ret_3m"], 1)
        c.rising = (m["ret_1m"] > 0) and (m["above_sma50"] or m["ret_1m"] >= 2.0)
        _verdict(c, beaten_min=beaten_min, beaten_max=beaten_max, qual_min=qual_min)
        out.append(c)
    out.sort(key=lambda x: x.dip_score, reverse=True)
    return out


def quality_from_fom(outputs_dir: Path) -> dict[str, float]:
    """{ticker: FOM quality} from the latest fom-monthly scan (for 盈利支持)."""
    files = sorted(Path(outputs_dir).glob("fom-monthly-*.json"))
    if not files:
        return {}
    try:
        d = json.loads(files[-1].read_text(encoding="utf-8"))
    except Exception:
        return {}
    out: dict[str, float] = {}
    for r in d.get("ranked_full", []) or []:
        q = r.get("quality")
        if r.get("ticker") and q is not None:
            out[r["ticker"]] = float(q)
    return out


def run_dipbuy(which: str = "software", *, settings: Optional[Settings] = None,
               fetch: FetchFn = default_fetch) -> tuple[str, list[DipCandidate]]:
    """Screen a thesis list. which ∈ {software, crypto, all}. Returns (title, rows)."""
    settings = settings or Settings.load()
    lists = {
        "software": ("軟體/AI 抄底名單", SOFTWARE_AI_DIPBUY),
        "crypto": ("加密/fintech 觀察", CRYPTO_FINTECH_OBSERVE),
        "all": ("抄底全名單", SOFTWARE_AI_DIPBUY + CRYPTO_FINTECH_OBSERVE),
    }
    title, tickers = lists.get(which, lists["software"])
    rows = screen(tickers, fetch=fetch, quality_by_ticker=quality_from_fom(settings.outputs_dir))
    return title, rows
