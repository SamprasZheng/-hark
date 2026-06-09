"""Finviz Elite export-API client — the modern ``/export?...&auth=TOKEN`` endpoint.

SECURITY (read me):
- The API token comes **only** from env ``FINVIZ_ELITE_API_KEY`` (``.env`` is
  gitignored). It is **never** hardcoded, never committed, never printed/logged —
  ``redact()`` strips the ``auth=`` param from any URL we surface in errors.
- If a token ever appears in a screenshot/chat, regenerate it on Finviz.

WHAT it does: configure a screen in the Finviz UI, copy the ``f=...`` filter string
from the URL, and this fetches the CSV export → rows / tickers you can pipe into the
``basecross`` / ``rally`` / ``stealth`` screens.

Pure helpers (``build_export_url`` / ``redact`` / ``parse_csv`` / ``tickers_from_rows``)
are unit-tested offline; only ``fetch_screen`` touches the network (urllib follows
the 301 redirect automatically, so no ``curl -L`` needed). recommend-only.

Validate on a networked machine:
    FINVIZ_ELITE_API_KEY=... python -m sharks.data.finviz_elite "ta_alltime_b30h,sh_price_o5"
(or a preset name; prints ticker count + first rows, never the token).
"""

from __future__ import annotations

import csv
import io
import os
import re
import urllib.request
from typing import Optional

EXPORT_BASE = "https://elite.finviz.com/export"

# Convenience presets = the ``f=`` filter string copied from a Finviz screener URL.
# ⚠️ Finviz filter CODES change/vary — treat these as a STARTING POINT and verify by
# copying the f=... from your own configured screener (docs/finviz_screening_recipe.md
# explains the return×risk filter logic). Override freely by passing a raw filter str.
PRESETS: dict[str, str] = {
    # beaten (≥30% below ATH) + liquid + not a penny stock + above the 50d MA
    "dipbuy": "ta_alltime_b30h,sh_avgvol_o500,sh_price_o5,ta_sma50_pa",
    # add survival/quality layer: + current ratio>1.5 + positive sales growth
    "dipbuy_quality": "ta_alltime_b30h,sh_avgvol_o500,sh_price_o5,ta_sma50_pa,fa_curratio_o1.5,fa_sales5years_pos",
}

_TOKEN_ENV = "FINVIZ_ELITE_API_KEY"


def _token(explicit: Optional[str] = None) -> str:
    tok = (explicit or os.environ.get(_TOKEN_ENV, "")).strip()
    if not tok:
        raise RuntimeError(
            f"{_TOKEN_ENV} not set — put your Finviz Elite token in .env "
            f"(gitignored). Never commit it.")
    return tok


def redact(url: str) -> str:
    """Hide the auth token in any URL we print/log/raise."""
    return re.sub(r"(auth=)[^&]+", r"\1***", url)


def build_export_url(filters: str, *, token: str, view: str = "111",
                     columns: Optional[str] = None) -> str:
    """Build the export URL. ``filters`` = the Finviz ``f=`` string;
    ``columns`` = optional ``c=`` column ids."""
    query = f"v={view}&f={filters}"
    if columns:
        query += f"&c={columns}"
    return f"{EXPORT_BASE}?{query}&auth={token}"


def parse_csv(text: str) -> list[dict]:
    """Parse the export CSV text into a list of row dicts."""
    return list(csv.DictReader(io.StringIO(text)))


def tickers_from_rows(rows: list[dict]) -> list[str]:
    """Pull the ticker column (Finviz labels it 'Ticker')."""
    out = []
    for r in rows:
        t = (r.get("Ticker") or r.get("ticker") or "").strip()
        if t:
            out.append(t.upper())
    return out


def resolve_filters(filters_or_preset: str) -> str:
    """A preset name → its filter string; otherwise treat the input as a raw f= str."""
    return PRESETS.get(filters_or_preset, filters_or_preset)


# ── Finviz column → 5-dimension mapping (更精準:用 Finviz 的基本/技術/資金欄位) ──
# Finviz export rows carry far richer per-ticker columns than a bare price feed, so
# we can fuse 資金/技術/基本面 directly from them (no price history needed for the
# snapshot). Tolerant to which columns are present (matched by HEADER NAME).

def _num(row: dict, *names: str) -> Optional[float]:
    """First present column among ``names`` → float (strips %, commas, B/M/K)."""
    for n in names:
        if n in row and str(row[n]).strip() not in ("", "-", "—"):
            s = str(row[n]).strip().replace("%", "").replace(",", "")
            mult = {"B": 1e9, "M": 1e6, "K": 1e3}.get(s[-1:], 1)
            if mult != 1:
                s = s[:-1]
            try:
                return float(s) * mult
            except ValueError:
                continue
    return None


def _clamp(x: float) -> float:
    return max(0.0, min(100.0, x))


def finviz_row_to_dims(row: dict) -> dict:
    """Map one Finviz export row → {capital, technical, fundamental, news, dist_ath_pct}
    (0..100 dims, None when the inputs are absent). Feeds rally_signal.assess."""
    # 技術:月/季動能 + 相對 50/200 日線 + RSI 健康區
    perf_m = _num(row, "Perf Month", "Performance (Month)")
    sma50 = _num(row, "SMA50", "SMA50 (Relative)")
    sma200 = _num(row, "SMA200", "SMA200 (Relative)")
    rsi = _num(row, "RSI", "Relative Strength Index (14)")
    tech = None
    if perf_m is not None or sma50 is not None:
        t = 50.0 + (perf_m or 0) * 1.2
        if sma50 is not None:
            t += 10 if sma50 > 0 else -10
        if sma200 is not None:
            t += 8 if sma200 > 0 else -8
        if rsi is not None and 50 <= rsi <= 72:
            t += 8
        tech = _clamp(t)

    # 資金:相對成交量 + 內部人/法人買盤
    relvol = _num(row, "Rel Volume", "Relative Volume")
    insider = _num(row, "Insider Trans", "Insider Transactions")
    inst = _num(row, "Inst Trans", "Institutional Transactions")
    capital = None
    if relvol is not None or insider is not None or inst is not None:
        c = 30.0 + ((relvol or 1) - 1) * 40
        if insider is not None:
            c += 12 if insider > 0 else -8
        if inst is not None:
            c += 12 if inst > 0 else -8
        capital = _clamp(c)

    # 基本面:ROE / 毛利 / 營收成長 / 獲利率(quality 代理)
    roe = _num(row, "ROE", "Return on Equity")
    gm = _num(row, "Gross Margin")
    sales = _num(row, "Sales growth past 5 years", "Sales Q/Q", "Sales growth quarter over quarter")
    pm = _num(row, "Profit Margin", "Net Profit Margin")
    fund = None
    if any(v is not None for v in (roe, gm, sales, pm)):
        f = 50.0
        if roe is not None:
            f += 12 if roe > 15 else (4 if roe > 0 else -10)
        if gm is not None:
            f += 8 if gm > 40 else (3 if gm > 20 else -5)
        if sales is not None:
            f += 10 if sales > 10 else (3 if sales > 0 else -8)
        if pm is not None:
            f += 6 if pm > 10 else (0 if pm > 0 else -8)
        fund = _clamp(f)

    dist = _num(row, "52W High", "52-Week High (Relative)")   # Finviz: negative % from 52w high
    dist_ath = abs(dist) if dist is not None else None

    # ── 更多維度(估值/成長/風險/分析師)——讓評估更立體 ──
    pe = _num(row, "P/E", "PE")
    ps = _num(row, "P/S", "PS")
    peg = _num(row, "PEG")
    valuation = None                                   # 高分 = 便宜(有上檔空間)
    if any(v is not None for v in (pe, ps, peg)):
        v = 50.0
        if pe is not None:
            v += 15 if pe < 15 else (5 if pe < 25 else (-15 if pe > 40 else 0))
        if ps is not None:
            v += 10 if ps < 2 else (-10 if ps > 10 else 0)
        if peg is not None:
            v += 15 if peg < 1 else (-10 if peg > 3 else 0)
        valuation = _clamp(v)

    eps_next = _num(row, "EPS growth next year", "EPS next Y", "EPS Q/Q")
    sales_g = _num(row, "Sales growth past 5 years", "Sales Q/Q")
    growth = None                                      # 高分 = 成長強
    if eps_next is not None or sales_g is not None:
        g = 50.0 + min(30, (eps_next or 0) * 0.4) + min(20, (sales_g or 0) * 0.4)
        growth = _clamp(g)

    beta = _num(row, "Beta")
    short_f = _num(row, "Short Float", "Float Short")
    volat = _num(row, "Volatility (Week)", "Volatility", "Volatility W")
    risk = None                                        # 高分 = 風險高(波動/擁擠空單)
    if any(v is not None for v in (beta, short_f, volat)):
        r = 40.0
        if beta is not None:
            r += (beta - 1) * 20
        if short_f is not None:
            r += min(25, short_f * 1.2)
        if volat is not None:
            r += min(20, volat * 2)
        risk = _clamp(r)

    recom = _num(row, "Analyst Recom", "Recom")        # 1 強力買進 .. 5 賣出
    analyst = _clamp((5 - recom) / 4 * 100) if recom is not None else None

    return {"technical": tech, "capital": capital, "fundamental": fund,
            "news": None, "dist_ath_pct": dist_ath,
            # 額外維度(供更立體評估;rally 核心仍用上面五維)
            "valuation": valuation, "growth": growth, "risk": risk, "analyst": analyst}


def fetch_screen(filters_or_preset: str, *, token: Optional[str] = None,
                 view: str = "111", columns: Optional[str] = None,
                 timeout: int = 30) -> list[dict]:
    """Fetch a screen's CSV export → row dicts. Network; token from env. Errors are
    redacted so the token never leaks into a traceback/log."""
    filters = resolve_filters(filters_or_preset)
    url = build_export_url(filters, token=_token(token), view=view, columns=columns)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 PolkaSharks"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:   # follows 301
            text = resp.read().decode("utf-8", "replace")
    except Exception as exc:
        raise RuntimeError(f"finviz export failed [{redact(url)}]: {exc}") from None
    if "<html" in text[:200].lower():
        raise RuntimeError("finviz returned HTML, not CSV — token invalid/expired or "
                           "bad filter string (URL redacted).")
    return parse_csv(text)


def fetch_tickers(filters_or_preset: str, **kw) -> list[str]:
    """Convenience: screen → ticker list (to feed basecross/rally/stealth)."""
    return tickers_from_rows(fetch_screen(filters_or_preset, **kw))


def main(argv: Optional[list[str]] = None) -> int:
    import sys
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print("用法: python -m sharks.data.finviz_elite '<f=過濾字串或preset>'\n"
              f"presets: {', '.join(PRESETS)}", file=sys.stderr)
        return 2
    arg = argv[0]
    try:
        rows = fetch_screen(arg)
    except Exception as exc:
        print(f"驗證失敗:{exc}", file=sys.stderr)   # token already redacted
        return 1
    tickers = tickers_from_rows(rows)
    print(f"✅ Finviz API OK — {len(tickers)} 檔(filters={resolve_filters(arg)})")
    print("前 30 檔:", ", ".join(tickers[:30]))
    print("→ 餵進系統:python -m sharks.discord.ecom_screens " + " ".join(tickers[:20]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
