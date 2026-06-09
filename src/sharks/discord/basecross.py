"""月線底部金叉 + 資金介入 screener — the "Intel 領漲 → 補炒 2022 殺下來的票 + AI 錯殺
軟體股" rotation thesis (2026-06).

Principal thesis: Intel 的反彈打開了「**補炒 2022 被殺下來 + AI 錯殺軟體股**」的門。要找的
形態 = **Boeing / Snowflake 那種多年大底翻揚**:
  * 題材        — 屬於 2022 空頭重災 或 被「AI 會取代它」錯殺的軟體股(下面兩張清單)。
  * 月線底部金叉 — 月線級別 MACD 在**低檔**由下往上交叉(底部金叉,不是高檔金叉)。
  * 資金介入     — 近月成交量相對前段明顯放大(量價配合 = 主力進場的痕跡)。
  * 大底形態     — 距歷史高有一段(深跌、長期築底),剛開始翻揚,不是貼著高點、也不是落刀。

這是 dipbuy.py「距高+盈利+起漲」的姊妹篩(日線動能版);本檔是**月線結構版**,專門抓
Boeing/Snowflake 那種「月線剛翻多」的大底。純函式 + fetch 可注入(離線可測);
recommend-only — 只篩研究清單,永不下單,不捏造數字。

月線是用日線重抽樣近似的(每 ~21 個交易日一根),所以不需要日期序列就能算「月線級別」
MACD;fetch 給足 ~5 年日線即可。
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

from sharks.discord.config import Settings

# ── 題材宇宙(候選池,不是部位)─────────────────────────────────────────────────
# 2022 空頭殺下來、之後長期築底的「Boeing/Snowflake 形態」候選。
KILLED_2022 = [
    "INTC", "BA", "SNOW", "PYPL", "ADBE", "CRM", "NKE", "DIS", "ROKU", "TWLO",
    "DDOG", "NET", "OKTA", "ZS", "MDB", "SHOP", "U", "PATH", "RBLX", "PINS",
    "SE", "ABNB", "DOCU", "WDAY", "TEAM", "BILL", "CFLT", "GTLB", "ESTC", "DOCN",
]
# 被「AI 會取代它」恐慌錯殺的軟體股(SaaS / 應用層)。
AI_OVERSOLD_SOFTWARE = [
    "ADBE", "CRM", "NOW", "INTU", "WDAY", "HUBS", "DDOG", "MDB", "SNOW", "TEAM",
    "DOCU", "ESTC", "TWLO", "ZI", "PATH", "AI", "S", "BRZE", "GTLB", "CHGG",
]
# Agentic-commerce 題材:AI 代理(自動比價/下單)利好的電商平台 + 金流/物流基建。
# 富邦媒(8454.TW)/網家(8044.TW)等台股需 Phase-2 suffix,先放 watchlist;這裡列
# US/ADR(yfinance 直接抓得到)。用 /basecross ecommerce 或 tickers:8454.TW 補台股。
ECOMMERCE_AGENTIC = [
    "AMZN", "SHOP", "SE", "MELI", "BABA", "PDD", "CPNG", "ETSY", "EBAY",
    "W", "CHWY", "GLBE", "BIGC", "JD",
]
# 小型 / 長尾電商(更高賠率、也更高風險;含主理人點名的 Jumia/Wayfair/Etsy)。
# 用 /basecross ecommerce 一起篩;盈利分層見 watchlist/thesis_ecommerce_agentic.md。
ECOMMERCE_SMALL = [
    "JMIA", "RVLV", "VIPS", "REAL", "SFIX", "WRBY", "MYTE", "CART", "FIGS", "RENT",
]
# 廣度輪動 / 錯殺的非-AI 民生消費醫療股(行情若擴散、華爾街輪動的隱蔽吸籌池)。
# 刻意放「大家還沒看到」的落後股,給 /stealth 找「資金先進、價未動」的吸籌指紋。
BROADENING_LAGGARDS = [
    # 民生必需 staples
    "KHC", "CAG", "CL", "HSY", "GIS", "K", "KVUE", "CLX", "SJM", "BG",
    # 消費非必需落後 discretionary laggards
    "NKE", "SBUX", "LULU", "EL", "TGT", "DG", "DLTR", "FIVE", "MCD",
    # 醫療錯殺 healthcare beaten
    "PFE", "MRNA", "BMY", "CVS", "HUM", "GILD", "DXCM",
]
# 太空板塊(SpaceX IPO 催化)— 沿價值鏈分層;多為 2021-SPAC 在 2022 被殺的倖存者
# = 錯殺大底。Starlink 競爭使 satcom 名字是雙面刃,持續性看真合約/營收。
SPACE_PUREPLAYS = [
    "RKLB",                          # 發射(SpaceX 最純對標)
    "ASTS", "IRDM", "GSAT", "VSAT",  # 衛星通訊 / direct-to-cell(Starlink 對標)
    "PL", "BKSY", "SPIR",            # 對地觀測 / 數據
    "RDW", "LUNR",                   # 製造 / 月球 / 政府合約
]
# 跨產業分散的「錯殺大底 + 有存活基本面」轉機股(不是只挑科技)。兼顧收益(深跌有空間)
# 與風險(有真生意/現金流/股息當地板)。見 watchlist/thesis_diversified_turnaround.md。
DIVERSIFIED_TURNAROUND = [
    "KVUE", "PFE", "TGT", "NKE", "KHC", "CVS",   # 必需消費 / 醫療 / 零售(防禦、有股息)
    "SBUX", "DIS", "EL", "ALB", "MMM",            # 餐飲 / 媒體 / 美妝 / 材料 / 工業(轉機)
    "PYPL", "RKLB", "F", "WBD",                   # 金融 / 太空 / 汽車 / 媒體(高賠率)
]
# 更多「中風險」轉機股:週期/公司轉機,有真營收/現金流(非殭屍、非 pre-profit),
# 但轉機未證實。跨金融/醫療/工業/材料/通訊/汽車/能源,刻意分散不重押單一產業。
MID_RISK_TURNAROUND = [
    "C", "BIIB", "MDT", "DE", "LYB", "FCX",       # 金融 / 生技 / 醫材 / 農機 / 化工 / 銅
    "CMCSA", "APTV", "GM", "SLB", "DPZ", "GPC",   # 通訊 / 車用零件 / 車廠 / 油服 / 餐飲 / 汽配
]
# 2026 IPO 超級年(~$3.6T)的「上市公司代理 + 受惠板塊」。散戶多半買不到 IPO 本身,
# 改提前佈局每個私有巨頭的**公開代理/持股受惠者**。見 watchlist/thesis_2026_ipo_wave.md。
IPO_PROXIES = [
    "RKLB", "IRDM", "ASTS", "LUNR",                       # SpaceX → 太空
    "MSFT", "NVDA", "AVGO", "ORCL", "AMZN", "GOOGL",      # OpenAI/Anthropic/xAI → 算力+持股者
    "SNOW", "MDB", "PLTR", "CFLT",                        # Databricks → 資料/AI 基建
    "PYPL", "FI", "GPN", "XYZ", "SOFI", "NU", "HOOD", "COIN",  # Stripe/Revolut/Ripple → 金融科技
    "ADBE",                                               # Canva → 設計軟體
    "PDD",                                                # Shein → 電商
]
# Agentic 支付 / 代理人支付題材(機器人/AI 代理自動下單付款 + 一點 crypto)。Stripe 是
# 私有領頭(IPO H1'26);公開可佈局的是卡組織(吃信任/憑證)、支付平台、加密軌。
# 見 watchlist/thesis_agentic_payments.md。
AGENTIC_PAYMENTS = [
    "V", "MA", "AXP",                 # 卡組織/信任憑證層(Visa Intelligent Commerce / MC Agent Pay)
    "PYPL", "XYZ", "FI", "GPN", "FOUR",  # 支付平台 / 收單(Stripe 的公開同業)
    "COIN", "CRCL", "HOOD",           # 加密軌 / 穩定幣(x402/USDC、Stripe+Tempo MPP)
    "SOFI", "NU",                     # neobank
]
# Web3 / 加密週期(2024 減半後的後段循環 + 機器/穩定幣支付)。高 beta、晚週期、看 BTC 循環。
# 含 BTC 代理(MSTR)、礦工(CLSK/MARA/RIOT…)、交易所/穩定幣(COIN/CRCL/HOOD)、現貨 ETF。
WEB3_CRYPTO = [
    "COIN", "MSTR", "HOOD", "CRCL",                       # 交易所 / BTC 代理 / 穩定幣
    "CLSK", "MARA", "RIOT", "HUT", "WULF", "CIFR", "BITF",  # 礦工(後段循環高 beta)
    "IBIT",                                               # 現貨 BTC ETF
]

FetchFn = Callable[[list[str]], dict[str, dict[str, list[float]]]]  # t -> {"close":[],"volume":[]}


@dataclass
class BaseCrossCandidate:
    ticker: str
    last: Optional[float] = None
    dist_ath_pct: Optional[float] = None      # 距歷史高 %(築底深度)
    golden_cross: bool = False                # 月線 MACD 由下往上交叉
    bottom_zone: bool = False                 # 交叉發生在低檔(底部金叉,非高檔)
    rising: bool = False                      # 月線剛翻揚(站上月均)
    vol_surge: Optional[float] = None         # 近月量 / 前段量(資金介入)
    inflow: bool = False                      # 資金介入確認
    quality: Optional[float] = None           # 盈利支持(FOM quality,有就帶)
    theme: str = ""                           # 2022殺 / AI錯殺
    score: float = 0.0
    verdict: str = ""
    note: str = ""


# ── 純數學:EMA / MACD / 月線重抽樣 ─────────────────────────────────────────────

def _ema(xs: list[float], span: int) -> list[float]:
    k = 2.0 / (span + 1)
    e = xs[0]
    out = [e]
    for x in xs[1:]:
        e = x * k + e * (1 - k)
        out.append(e)
    return out


def _macd(closes: list[float], fast: int = 12, slow: int = 26, sig: int = 9
          ) -> tuple[list[float], list[float]]:
    ef, es = _ema(closes, fast), _ema(closes, slow)
    macd = [a - b for a, b in zip(ef, es)]
    signal = _ema(macd, sig)
    return macd, signal


def _to_monthly(daily: list[float], bucket: int = 21, agg: str = "last") -> list[float]:
    """Resample a daily series to ~monthly. last close per bucket, or sum (volume)."""
    out: list[float] = []
    for i in range(0, len(daily), bucket):
        chunk = daily[i:i + bucket]
        if not chunk:
            continue
        out.append(chunk[-1] if agg == "last" else float(sum(chunk)))
    return out


# ── 評分 ───────────────────────────────────────────────────────────────────────

def _classify(c: BaseCrossCandidate, *, beaten_min: float, beaten_max: float,
              inflow_min: float) -> None:
    d = c.dist_ath_pct or 0.0
    gc = c.golden_cross and c.bottom_zone
    if d < beaten_min:
        c.verdict = "〽️ 近高/乖離(非大底)"
        c.note = f"距高僅 {d:.0f}%,不是 2022 大底形態"
    elif d > beaten_max:
        c.verdict = "⚠️ 跌太深(落刀?)"
        c.note = f"距高 {d:.0f}%,需查是否價值陷阱/退市風險"
    elif gc and c.inflow:
        c.verdict = "🟢 月線底部金叉 + 資金進場"
        c.note = (f"距高 {d:.0f}% + 月線金叉(低檔)+ 量能放大 ×{c.vol_surge:.1f}"
                  + (f" + 盈利 q={c.quality:.0f}" if c.quality is not None else " · 盈利TBD"))
    elif gc:
        c.verdict = "🟡 月線金叉 · 量能待確認"
        c.note = f"距高 {d:.0f}% + 月線金叉,但資金未明顯介入(量 ×{(c.vol_surge or 0):.1f} < {inflow_min:.1f})"
    elif c.inflow and c.rising:
        c.verdict = "🟡 量先進場 · 金叉待確認"
        c.note = f"距高 {d:.0f}% + 量放大 ×{c.vol_surge:.1f},月線金叉尚未成形"
    else:
        c.verdict = "🔵 築底中 · 待金叉"
        c.note = f"距高 {d:.0f}% 大底已成,等月線金叉 + 資金介入"
    # 排名:底部金叉最重、資金介入次之、距高甜蜜區(這類深跌名字 ~50% off 最典型)
    sweet = max(0.0, 1 - abs(d - 50) / 50)
    c.score = round(45 * (1 if gc else 0) + 25 * (1 if c.inflow else 0)
                    + 20 * sweet + 10 * (1 if c.rising else 0) + 0.1 * (c.quality or 0), 1)


def screen(tickers: list[str], *, fetch: FetchFn,
           quality_by_ticker: Optional[dict[str, float]] = None,
           theme_by_ticker: Optional[dict[str, str]] = None,
           beaten_min: float = 20.0, beaten_max: float = 85.0,
           inflow_min: float = 1.3, min_months: int = 30
           ) -> list[BaseCrossCandidate]:
    """Screen for 月線底部金叉 + 資金介入. ``fetch(tickers) -> {t: {close:[], volume:[]}}``
    (≥ ~5y daily). Pure given ``fetch`` (tests inject a stub)."""
    quality_by_ticker = quality_by_ticker or {}
    theme_by_ticker = theme_by_ticker or {}
    data = fetch(tickers)
    out: list[BaseCrossCandidate] = []
    for t in tickers:
        c = BaseCrossCandidate(ticker=t, quality=quality_by_ticker.get(t),
                               theme=theme_by_ticker.get(t, ""))
        d = data.get(t) or {}
        closes, vols = d.get("close") or [], d.get("volume") or []
        mc = _to_monthly(closes, agg="last")
        if len(mc) < min_months:
            c.verdict, c.note = "資料不足", "月線樣本不足(需 ~5 年日線)"
            out.append(c)
            continue

        last, ath = mc[-1], max(mc)
        c.last = round(last, 2)
        c.dist_ath_pct = round((ath - last) / ath * 100, 1) if ath else 0.0

        macd, signal = _macd(mc)
        c.golden_cross = (macd[-2] <= signal[-2]) and (macd[-1] > signal[-1])
        recent = macd[-12:]
        lo, hi = min(recent), max(recent)
        mid = (lo + hi) / 2
        c.bottom_zone = macd[-1] <= max(0.0, mid)     # 交叉在零軸下或近期低檔 = 底部金叉
        sma6 = sum(mc[-6:]) / 6
        c.rising = last > mc[-2] and last >= sma6

        mv = _to_monthly(vols, agg="sum") if vols else []
        if len(mv) >= 12:
            base = sum(mv[-12:-2]) / 10 or 1.0
            recent_v = sum(mv[-2:]) / 2
            c.vol_surge = round(recent_v / base, 2) if base else None
            c.inflow = (c.vol_surge or 0) >= inflow_min

        _classify(c, beaten_min=beaten_min, beaten_max=beaten_max, inflow_min=inflow_min)
        out.append(c)
    out.sort(key=lambda x: x.score, reverse=True)
    return out


# ── yfinance fetch (close + volume, ~5y) ───────────────────────────────────────

def default_fetch(tickers: list[str], period: str = "5y") -> dict[str, dict[str, list[float]]]:
    import yfinance as yf
    out: dict[str, dict[str, list[float]]] = {}
    for t in tickers:
        try:
            h = yf.Ticker(t).history(period=period, auto_adjust=True)
            cs = [float(x) for x in h["Close"].dropna().tolist()]
            vs = [float(x) for x in h["Volume"].fillna(0).tolist()]
            if len(cs) >= 30 * 21:
                out[t] = {"close": cs, "volume": vs[:len(cs)]}
        except Exception:
            continue
    return out


def quality_from_fom(outputs_dir: Path) -> dict[str, float]:
    """{ticker: FOM quality} from the latest fom-monthly scan (盈利支持, optional)."""
    files = sorted(Path(outputs_dir).glob("fom-monthly-*.json"))
    if not files:
        return {}
    try:
        d = json.loads(files[-1].read_text(encoding="utf-8"))
    except Exception:
        return {}
    return {r["ticker"]: float(r["quality"]) for r in d.get("ranked_full", []) or []
            if r.get("ticker") and r.get("quality") is not None}


def run_basecross(which: str = "all", *, settings: Optional[Settings] = None,
                  fetch: FetchFn = default_fetch,
                  extra_tickers: Optional[list[str]] = None
                  ) -> tuple[str, list[BaseCrossCandidate]]:
    """Screen a thesis list. which ∈ {killed2022, ai_software, all}; ``extra_tickers``
    lets you throw arbitrary names (e.g. straight from a Finviz/Pelosi screenshot)."""
    settings = settings or Settings.load()
    ecommerce_all = ECOMMERCE_AGENTIC + ECOMMERCE_SMALL
    everything = sorted(set(KILLED_2022) | set(AI_OVERSOLD_SOFTWARE)
                        | set(ecommerce_all) | set(BROADENING_LAGGARDS)
                        | set(SPACE_PUREPLAYS) | set(DIVERSIFIED_TURNAROUND)
                        | set(MID_RISK_TURNAROUND) | set(IPO_PROXIES) | set(AGENTIC_PAYMENTS)
                        | set(WEB3_CRYPTO))
    lists = {
        "killed2022": ("2022 殺下來的大底", KILLED_2022),
        "ai_software": ("AI 錯殺軟體股", AI_OVERSOLD_SOFTWARE),
        "ecommerce": ("電商 · agentic-commerce(含小型)", ecommerce_all),
        "ecommerce_small": ("小型電商(高賠率高風險)", ECOMMERCE_SMALL),
        "broadening": ("廣度輪動 · 錯殺民生/消費/醫療", BROADENING_LAGGARDS),
        "space": ("太空板塊 · SpaceX IPO 催化", SPACE_PUREPLAYS),
        "diversified": ("跨產業分散轉機股", DIVERSIFIED_TURNAROUND),
        "midrisk": ("中風險轉機股(週期/公司轉機)", MID_RISK_TURNAROUND),
        "ipo": ("2026 IPO 超級年 · 上市代理/受惠", IPO_PROXIES),
        "payments": ("Agentic 支付 · 金融科技變革", AGENTIC_PAYMENTS),
        "crypto": ("Web3/加密週期(BTC 後段循環)", WEB3_CRYPTO),
        "all": ("月線大底金叉全名單", everything),
    }
    title, base = lists.get(which, lists["all"])
    theme = {t: "2022殺" for t in KILLED_2022}
    theme.update({t: (theme.get(t, "") + "+AI錯殺").lstrip("+") for t in AI_OVERSOLD_SOFTWARE})
    theme.update({t: (theme.get(t, "") + "+電商").lstrip("+") for t in ecommerce_all})
    theme.update({t: (theme.get(t, "") + "·小型").lstrip("+") for t in ECOMMERCE_SMALL})
    theme.update({t: (theme.get(t, "") + "+廣度").lstrip("+") for t in BROADENING_LAGGARDS})
    theme.update({t: (theme.get(t, "") + "+太空").lstrip("+") for t in SPACE_PUREPLAYS})
    theme.update({t: (theme.get(t, "") + "+分散").lstrip("+") for t in DIVERSIFIED_TURNAROUND})
    theme.update({t: (theme.get(t, "") + "+中風險").lstrip("+") for t in MID_RISK_TURNAROUND})
    theme.update({t: (theme.get(t, "") + "+IPO代理").lstrip("+") for t in IPO_PROXIES})
    theme.update({t: (theme.get(t, "") + "+支付").lstrip("+") for t in AGENTIC_PAYMENTS})
    theme.update({t: (theme.get(t, "") + "+加密").lstrip("+") for t in WEB3_CRYPTO})
    tickers = sorted(set(base) | set(t.upper() for t in (extra_tickers or [])))
    rows = screen(tickers, fetch=fetch,
                  quality_by_ticker=quality_from_fom(settings.outputs_dir),
                  theme_by_ticker=theme)
    if extra_tickers:
        title += f"(+{len(extra_tickers)} 自訂)"
    return title, rows
