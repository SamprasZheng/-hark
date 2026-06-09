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
    FINVIZ_ELITE_API_KEY=... python -m sharks.data.finviz_elite rally dipbuy   # 端到端 9維→rally
(prints ticker count / a ranked rally table; never the token).

The ``rally`` mode powers rally_signal directly from Finviz's own columns (a daily
snapshot → 連續起漲 persisted in outputs/rally-state-*.jsonl). Finviz does NOT give the
monthly price history that basecross (月線金叉) / stealth need — those stay on yfinance.
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
    # 起漲點火:早期上升(站上 20/50 日線)+ 量能放大(買盤)+ 不追高 + 有盈利底(嚴格,tight regime)
    "rally_ignition": ("ta_sma20_pa,ta_sma50_pa,ta_perf_4wup,sh_relvol_o1.5,"
                       "sh_avgvol_o500,sh_price_o5,fa_grossmargin_pos,fa_epsyoyttm_pos"),
    # 2022 錯殺反轉:深跌離高(≥30%)+ 月線翻揚 + 量能進場 + 有營收/盈利支撐
    "mis_killed_2022": ("ta_highlow52w_b30h,ta_sma50_pa,sh_relvol_o1.5,sh_avgvol_o500,"
                        "sh_price_o5,fa_sales5years_pos,fa_grossmargin_pos"),
}

# 趨勢階段過濾(LOCAL,不靠 Finviz screener 碼)— 抓精選池 → 用 trend_stage 在本地篩。
# Finviz 的 f= 過濾碼格式易錯(錯碼會被忽略、回傳整個市場),所以這類「型態」一律本地過濾。
STAGE_FILTERS: dict[str, tuple[str, ...]] = {
    "supercycle": ("🌊",),              # 只要 supercycle候選(站上50&200+月/季/半年漲+年漲≥30%)
    "uptrend_3mo": ("🌊", "📈"),        # 月線三連陽級別(多頭排列+持續)
    "monthly3": ("🌊", "📈"),
    "pre_ignition": ("🌱",),            # **預測**:醞釀/底部翻揚,深跌有空間、剛站回 50 線、即將起漲
    "predict": ("🌱",),
    "rally_stage": ("🌊", "📈", "🚀", "🌱"),  # 含起漲/醞釀
}


def _liquid(row: dict, *, min_price: float = 5.0, min_avgvol: float = 500_000,
            min_mktcap: float = 300e6, require_fundamental: bool = True) -> bool:
    """中高 beta、可交易、真公司:價格 + 均量 + 市值門檻 + 要有基本面欄位(濾掉 KEEX/MMA
    那種『基–』的微型垃圾與墓園型)。"""
    price = _num(row, "Price")
    if price is not None and price < min_price:
        return False
    avgvol = _num(row, "Avg Volume", "Average Volume")
    if avgvol is not None and avgvol < min_avgvol:
        return False
    mktcap = _num(row, "Market Cap")
    if mktcap is not None and mktcap < min_mktcap:
        return False
    if require_fundamental:                     # 真公司:至少有一個基本面欄位(墓園型多為 基–)
        if all(_num(row, c) is None for c in ("ROE", "Gross Margin", "P/E", "Profit Margin")):
            return False
    return True


# Finviz Index filter codes (best-effort; verify in the Finviz UI). src=sp500 / src=r2k
# restrict the whole-market scan to those indices = quality, near S&P500/Russell-2000.
_INDEX_FILTER = {"sp500": "idx_sp500", "r2k": "idx_rut", "russell2000": "idx_rut",
                 "midcap": "idx_sp400"}

_TOKEN_ENV = "FINVIZ_ELITE_API_KEY"

# To get the 9 dimensions, the export must include the technical/fundamental/ownership
# columns — the default Overview view (111) does NOT. Use the Custom view (152) with a
# column-id set. Finviz column ids follow a (fairly stable) canonical order; this is a
# best-effort set covering valuation/growth/ownership/fundamentals/technical/risk.
# ⚠️ ids can vary by account — finviz_row_to_dims matches by HEADER NAME, so any
# superset works. If the rally dims come back mostly None, open your Finviz Custom
# view, pick those columns, and pass the URL's v=/c= via `view=`/`cols=` overrides.
DIMENSION_VIEW = "152"
# Request ALL columns (0..70) so every dim's source column is present — robust to the
# exact id↔column mapping (finviz_row_to_dims matches by HEADER NAME). Fixes the
# growth / 52W-High coverage gaps from narrow id guesses.
DIMENSION_COLUMNS = ",".join(str(i) for i in range(71))
# The 9 evaluation dims finviz_row_to_dims produces (for coverage reporting).
DIMS9 = ("technical", "capital", "fundamental", "valuation", "growth",
         "risk", "analyst", "dist_ath_pct", "news")


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


def build_export_url(filters: str = "", *, token: str, view: str = "111",
                     columns: Optional[str] = None, tickers: Optional[str] = None) -> str:
    """Build the export URL. ``filters`` = the Finviz ``f=`` string; ``tickers`` = a
    comma list for the ``t=`` param (fetch specific names — used for theme scopes).
    ``columns`` = optional ``c=`` column ids."""
    query = f"v={view}"
    if tickers:
        query += f"&t={tickers}"
    if filters:
        query += f"&f={filters}"
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
    sales = _num(row, "Sales growth past 5 years", "Sales past 5Y", "Sales Q/Q",
                 "Sales growth quarter over quarter")
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
    sales_g = _num(row, "Sales growth past 5 years", "Sales past 5Y", "Sales Q/Q")
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


def trend_stage(row: dict) -> str:
    """Classify long-term uptrend stage from Finviz multi-period perf + MA stack
    (snapshot proxy for 月線三連陽 / 大浪; true monthly-candle counting needs price
    history). Returns 🌊 supercycle候選 / 📈 月線三連陽(多頭排列)/ 🚀 起漲 / 〰️ 震盪."""
    pm = _num(row, "Perf Month", "Performance (Month)")
    pq = _num(row, "Perf Quart", "Perf Quarter", "Performance (Quarter)")
    ph = _num(row, "Perf Half Y", "Perf Half", "Performance (Half Year)")
    py = _num(row, "Perf Year", "Performance (Year)")
    s50 = _num(row, "SMA50", "SMA50 (Relative)")
    s200 = _num(row, "SMA200", "SMA200 (Relative)")
    if pm is None and pq is None:
        return ""
    stack = (s50 is not None and s50 > 0) and (s200 is not None and s200 > 0)  # 站上 50 & 200
    sustained = (pm or 0) > 0 and (pq or 0) > 0 and (ph is None or ph > 0)      # 多月持續
    if stack and sustained and (py or 0) >= 30:
        return "🌊 supercycle候選"
    if stack and sustained:
        return "📈 月線三連陽(多頭排列)"
    # 醞釀/底部翻揚:站回 50 線、但仍在 200 線下(深跌有空間)、月線剛轉 → 預測「即將三連陽」
    if (s50 is not None and s50 > 0) and (s200 is not None and s200 < 0) and (pm or 0) >= -2:
        return "🌱 醞釀(底部翻揚·即將起漲)"
    if (pm or 0) > 0 and (s50 or -1) > 0:
        return "🚀 起漲"
    return "〰️ 震盪/整理"


def write_scan_recommendation(outputs_dir, signals, *, source: str = "finviz",
                              stages: Optional[dict] = None):
    """Write the data-driven re-recommendation to outputs/finviz-scan-<date>.json
    (ranked, with the buy-consider shortlist) — the Finviz analog of FOM's output."""
    import json
    from datetime import datetime
    from pathlib import Path
    outputs_dir = Path(outputs_dir)
    outputs_dir.mkdir(parents=True, exist_ok=True)
    date = datetime.now().strftime("%Y-%m-%d")
    stages = stages or {}
    def row(s):
        return {"ticker": s.ticker, "composite": s.composite, "dna_match": s.dna_match,
                "streak": s.streak, "conviction": s.conviction,
                "buy_consider": s.buy_consider, "has_fuel": s.has_fuel,
                "trend_stage": stages.get(s.ticker, ""), "dims": s.dims}
    rec = {"as_of": date, "source": source, "engine": "finviz-rally", "n": len(signals),
           "buy_consider": [s.ticker for s in signals if s.buy_consider],
           "ranked": [row(s) for s in signals]}
    path = outputs_dir / f"finviz-scan-{date}.json"
    path.write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def resolve_target(arg: str) -> tuple[str, Optional[str], Optional[str]]:
    """Decide what ``arg`` means → (kind, filters, tickers).

    - a basecross theme scope (space/ipo/payments/…) → fetch those tickers via ``t=``
      (Finviz-native, no yfinance);
    - a PRESETS name or a raw ``f=`` filter string → fetch via ``f=``.
    """
    try:
        from sharks.discord import basecross as _bc
        if arg in _bc.SCOPES:
            _, tickers = _bc.scope_universe(arg)
            return "scope", None, ",".join(tickers)
    except Exception:
        pass
    if arg in ("universe", "fom", "fomuniverse", "全宇宙"):
        return "universe", None, None
    if arg in STAGE_FILTERS:
        return "stage", arg, None            # local trend-stage filter over the universe
    return "filters", resolve_filters(arg), None


def fetch_screen(filters_or_preset: str = "", *, token: Optional[str] = None,
                 view: str = "111", columns: Optional[str] = None,
                 tickers: Optional[str] = None, timeout: int = 30) -> list[dict]:
    """Fetch a screen's CSV export → row dicts. Network; token from env. Errors are
    redacted so the token never leaks into a traceback/log. Pass ``tickers`` to fetch
    specific names (t=) instead of a filter (f=)."""
    filters = "" if tickers else resolve_filters(filters_or_preset)
    url = build_export_url(filters, token=_token(token), view=view,
                           columns=columns, tickers=tickers)
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


def fetch_universe(tickers: list[str], *, token: Optional[str] = None,
                   view: str = "152", columns: Optional[str] = None,
                   batch: int = 80, timeout: int = 30) -> list[dict]:
    """Bulk Finviz export for MANY tickers (the whole FOM universe), batched to stay
    under URL limits. Dedupes by ticker. Real fundamentals/technicals, no yfinance."""
    out: list[dict] = []
    seen: set[str] = set()
    for i in range(0, len(tickers), batch):
        chunk = [t for t in tickers[i:i + batch] if t]
        if not chunk:
            continue
        rows = fetch_screen(token=token, view=view, columns=columns,
                            tickers=",".join(chunk), timeout=timeout)
        for r in rows:
            t = (r.get("Ticker") or r.get("ticker") or "").strip().upper()
            if t and t not in seen:
                seen.add(t)
                out.append(r)
    return out


def fom_universe() -> list[str]:
    """Full scan universe = all theme pools (pure-Python) + the FOM core (only if it
    imports). Deliberately does NOT hard-depend on fom.py (pandas/numpy/yfinance), so
    the Finviz path stays lightweight and keeps working even when those deps are
    broken/missing. Drops indices (^…) and crypto pairs (…-USD) Finviz won't price."""
    tickers: set[str] = set()
    try:
        from sharks.discord import basecross as _bc
        tickers.update(_bc.scope_universe("all")[1])   # 錯殺/payments/ecommerce/crypto/space…
    except Exception:
        pass
    try:
        from sharks.scoring import fom                  # core FOM names (skip if pandas/numpy broken)
        tickers.update(fom.DEFAULT_UNIVERSE)
    except Exception:
        pass
    return sorted(t for t in tickers if t and not t.startswith("^") and "-USD" not in t)


def signals_from_finviz(rows: list[dict], *, prior_streaks: Optional[dict] = None,
                        tight_regime: bool = True) -> list:
    """End-to-end: Finviz rows → 9-dim mapping → rally_signal.assess → ranked signals.

    Uses Finviz's OWN columns for 資金/技術/基本面 (no price history needed for the
    snapshot); 連續起漲 accumulates across daily runs via ``prior_streaks``. Pure given
    its inputs (tests inject rows). ``rally_signal`` imported lazily to keep data→scoring
    layering clean and the import optional for the plain ticker-list mode."""
    from sharks.scoring import rally_signal as RS
    prior_streaks = prior_streaks or {}
    out = []
    for r in rows:
        t = (r.get("Ticker") or r.get("ticker") or "").strip().upper()
        if not t:
            continue
        dims = finviz_row_to_dims(r)
        out.append(RS.assess(t, dims, prior_streak=prior_streaks.get(t, 0),
                             tight_regime=tight_regime))
    out.sort(key=lambda s: (s.buy_consider, s.composite, s.dna_match), reverse=True)
    return out


def main(argv: Optional[list[str]] = None) -> int:
    import sys
    # Load .env so FINVIZ_ELITE_API_KEY is available to the CLI (the bot loads it via
    # Settings; the standalone CLI must do it itself, BEFORE _token reads os.environ).
    try:
        from sharks.discord.config import _read_dotenv, PROJECT_ROOT
        _read_dotenv(PROJECT_ROOT / ".env")
    except Exception:
        pass
    argv = list(sys.argv[1:] if argv is None else argv)
    # overrides: view=152  cols=1,2,3,...  src=market|universe  (src=market = 全市場掃 + 本地濾)
    view_override = cols_override = None
    src = "universe"
    pos: list[str] = []
    for a in argv:
        if a.startswith("view="):
            view_override = a.split("=", 1)[1]
        elif a.startswith(("cols=", "columns=")):
            cols_override = a.split("=", 1)[1]
        elif a.startswith("src="):
            src = a.split("=", 1)[1].strip().lower()
        else:
            pos.append(a)
    mode = "tickers"
    if pos and pos[0] == "rally":
        mode, pos = "rally", pos[1:]
    if not pos:
        print("用法(全程 Finviz,不用 yfinance):\n"
              "  python -m sharks.data.finviz_elite rally universe   # 重掃 FOM 全宇宙→9維→排名+推薦JSON\n"
              "  python -m sharks.data.finviz_elite rally pre_ignition src=sp500  # **預測** 即將起漲(限 S&P500,已砍墓園)\n"
              "  python -m sharks.data.finviz_elite rally pre_ignition src=r2k    # 限 Russell 2000\n"
              "  python -m sharks.data.finviz_elite rally supercycle src=sp500    # S&P500 🌊supercycle候選\n"
              "  python -m sharks.data.finviz_elite rally uptrend_3mo # 池內篩 月線三連陽(加 src=market 擴全市場)\n"
              "  python -m sharks.data.finviz_elite rally space      # 題材池→Finviz t= 抓→9維→rally\n"
              "  python -m sharks.data.finviz_elite rally dipbuy      # preset(f= 過濾)\n"
              "  python -m sharks.data.finviz_elite '<scope|preset|f=>'   # 只驗證+代號清單\n"
              "  (可加 view=152 cols=1,2,... 從你的 Finviz Custom URL 覆蓋欄位)\n"
              "  scope: space ipo payments crypto ecommerce ai_software broadening "
              "diversified midrisk killed2022 all\n"
              f"  presets: {', '.join(PRESETS)}", file=sys.stderr)
        return 2
    arg = pos[0]

    if mode == "rally":
        view = view_override or DIMENSION_VIEW
        columns = cols_override or DIMENSION_COLUMNS
        kind, flt, tks = resolve_target(arg)
        try:
            if kind in ("universe", "stage"):
                if src in ("market", "sp500", "r2k", "russell2000", "midcap"):
                    idxf = _INDEX_FILTER.get(src, "")     # sp500/r2k → Finviz index filter
                    label = src if idxf else "全市場"
                    print(f"{label} 掃描(Finviz → 本地濾流動性/真公司/型態)…", file=sys.stderr)
                    rows = [r for r in fetch_screen(idxf, view=view, columns=columns) if _liquid(r)]
                else:
                    uni = fom_universe()
                    print(f"精選池掃描:{len(uni)} 檔(無 yfinance)…", file=sys.stderr)
                    rows = fetch_universe(uni, view=view, columns=columns)
                if kind == "stage":                      # keep only rows in the target stage(s)
                    keep = STAGE_FILTERS[arg]
                    rows = [r for r in rows if trend_stage(r).startswith(keep)]
                    print(f"型態過濾後:{len(rows)} 檔({arg} = {''.join(keep)})", file=sys.stderr)
            else:
                rows = fetch_screen(flt or "", view=view, columns=columns, tickers=tks)
        except Exception as exc:
            print(f"驗證失敗:{exc}", file=sys.stderr)
            return 1
        from sharks.scoring import rally_signal as RS
        from sharks.discord.config import Settings
        outdir = Settings.load().outputs_dir
        prior = RS.load_prior_streaks(outdir)
        sigs = signals_from_finviz(rows, prior_streaks=prior)
        if kind in ("universe", "stage") or src != "universe":   # 大範圍掃 → 砍墓園型,留有料的
            sigs = [s for s in sigs if not s.conviction.startswith("🚫")]
        stages = {(r.get("Ticker") or r.get("ticker") or "").strip().upper(): trend_stage(r)
                  for r in rows}
        scan_path = write_scan_recommendation(outdir, sigs, source=arg, stages=stages)
        # dims coverage — so you can tell if the export is missing columns
        dims_list = [finviz_row_to_dims(r) for r in rows]
        n = len(rows) or 1
        cov = {k: sum(1 for d in dims_list if d.get(k) is not None) for k in DIMS9}
        RS.write_state(outdir, sigs)
        print(f"✅ Finviz→rally — {len(sigs)} 檔(filters={resolve_filters(arg)}, view={view})")
        print("維度覆蓋:", " ".join(f"{k}={cov[k]}/{n}" for k in DIMS9))
        if cov["technical"] == 0 and cov["fundamental"] == 0:
            print("⚠️ 技術/基本面欄位全空 → 此 view 沒帶到欄位;用 view=/cols= 從你的 "
                  "Finviz Custom URL 覆蓋(見 docs/finviz_screening_recipe.md)。")
        for s in sigs[:30]:
            d = s.dims
            dstr = " ".join(f"{lbl}{int(d[k])}" if d.get(k) is not None else f"{lbl}–"
                            for k, lbl in (("technical", "技"), ("capital", "資"),
                                           ("fundamental", "基")))
            st = stages.get(s.ticker, "")
            print(f"  {s.ticker:<6} C{s.composite:>4.0f} 連{s.streak} {dstr} {st} · {s.conviction}")
        # supercycle / 月線三連陽 shortlist (the 大浪 candidates)
        wave = [s.ticker for s in sigs if stages.get(s.ticker, "").startswith(("🌊", "📈"))]
        if wave:
            print(f"🌊 大浪/月線三連陽候選({len(wave)}):" + ", ".join(wave[:25]))
        print(f"📄 推薦清單已寫入:{scan_path}")
        print("recommend-only · 連續起漲跨日累計(rally-state)· 永不下單")
        return 0

    # default: validate + ticker list (fast Overview view)
    _, flt, tks = resolve_target(arg)
    try:
        rows = fetch_screen(flt or "", view=view_override or "111",
                            columns=cols_override, tickers=tks)
    except Exception as exc:
        print(f"驗證失敗:{exc}", file=sys.stderr)   # token already redacted
        return 1
    tickers = tickers_from_rows(rows)
    print(f"✅ Finviz API OK — {len(tickers)} 檔(filters={resolve_filters(arg)})")
    print("前 30 檔:", ", ".join(tickers[:30]))
    print("→ 端到端評分:python -m sharks.data.finviz_elite rally " + arg)
    print("→ 或餵價量screens:python -m sharks.discord.ecom_screens " + " ".join(tickers[:20]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
