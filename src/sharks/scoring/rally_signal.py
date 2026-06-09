"""起漲訊號追蹤 — Rally-ignition tracker fusing 資金 / 技術 / 消息 / 供應鏈 / 基本面.

The principal's directive (2026-06-08): 把候選都納入宇宙,然後**追蹤起漲訊號**——
五個維度(資金、技術、消息、供應鏈、基本面)——**連續起漲才考慮買入**,並期待複製
2020~2026 代表性暴漲股(INTC / MU / NVDA / TSLA …)的「點火 DNA」。

This is the *fusion + persistence* layer that sits ON TOP of the single-signal
modules already in the repo:

  技術 technical   ← basecross.py(月線底部金叉/起漲)+ dipbuy.py(日線動能)
  資金 capital     ← basecross 量能放大 / chip_flow_fsm(籌碼)/ moonshot volume_surge
  基本面 fundamental ← fom.py quality(盈利支持)
  供應鏈 supply_chain ← 供應鏈 design-win 名單(huang/serenity 題材)
  消息 news        ← news_sentiment(可選;沒有就標 TBD,不亂猜)

Two disciplines, straight from the constitution + moonshot_hunter:
  1. **連續起漲才買** — one green bar is noise; we require the rally to PERSIST
     (streak ≥ MIN_STREAK_BUY) before it is even "可考慮買入". Persistence is the
     repeatable feature of the 2020-26 winners (they trended, not one-day spikes).
  2. **墓園守門** — hot price/資金 with NO 基本面/供應鏈/消息 catalyst = 純炒作,
     the graveyard pattern. We WARN and refuse the buy-consideration, exactly like
     moonshot_hunter's PURE-HYPE-NO-EVIDENCE gate.

Pure stdlib + every dimension is INJECTED (0..100 or None=TBD), so the whole
fusion/persistence is unit-testable offline. recommend-only — never an order.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

# The five dimensions the principal listed, with display labels.
DIMENSIONS = ("capital", "technical", "news", "supply_chain", "fundamental")
DIM_ZH = {"capital": "資金", "technical": "技術", "news": "消息",
          "supply_chain": "供應鏈", "fundamental": "基本面"}

# Default fusion weights — 技術 + 資金 are the ignition (when it MOVES); 基本面 +
# 供應鏈 are the catalyst (whether it DESERVES to); 消息 is confirmation.
DEFAULT_WEIGHTS = {"technical": 0.30, "capital": 0.25, "fundamental": 0.20,
                   "supply_chain": 0.13, "news": 0.12}

# 2020-2026 代表性暴漲股 — the "ignition DNA" we want a candidate to rhyme with:
# a deep base / cycle-bottom turn → accelerating momentum + volume expansion +
# a confirmed catalyst (earnings inflection / supply-chain design-win).
WINNER_EXEMPLARS = ("INTC", "MU", "NVDA", "TSLA", "AMD", "AVGO",
                    "SMCI", "PLTR", "ARM", "APP", "CVNA", "MSTR")

# Supply-chain design-win / bottleneck tags (題材 = 真有卡位), mirrored from the
# huang / serenity universes. In the set → strong 供應鏈 dimension when un-scored.
SUPPLY_CHAIN_TAGS = frozenset({
    "TSM", "ASML", "AVGO", "AMD", "ARM", "MU", "AMAT", "LRCX", "KLAC", "ANET",
    "COHR", "LITE", "CIEN", "CRDO", "ALAB", "AEHR", "MRVL", "VRT", "ETN", "GEV",
    "NVDA", "AMKR", "TER", "ON", "MPWR", "POET", "AAOI", "FN", "GLW",
})

RALLY_MIN = 55.0          # 今天算「起漲」的 composite 門檻
BUY_MIN = 62.0            # 夠強到可考慮(需配合 streak)
HOT_DIM = 65.0            # 單維過熱(技術/資金)
CATALYST_MIN = 50.0       # 基本面/供應鏈/消息 任一達此 = 有題材撐
WAVE_FUEL_MIN = 55.0      # 「真會賺錢 或 真有題材」的燃料門檻(比 catalyst 更嚴)
MIN_STREAK_BUY = 3        # 連續起漲幾「期」才考慮買入

# 規模/廣度的 regime:2021 是大降息瘋牛(loose,雞犬升天、廣度大);現在不是(tight,
# 廣度小)→ 只有「真會賺錢 或 真有題材」的票才撐得起大浪。預設 tight(主理人 2026-06)。
TIGHT_REGIME_DEFAULT = True

# 盈利先驗(0..100,**保守相對分級,非具體財務數字**)— 在 FOM 還沒把這些票重跑出
# quality 之前,給 /rally 的「基本面」維度一個合理起點。FOM 真值一出現就會覆蓋它
# (build_signals 先取 FOM quality,缺了才用這裡)。分級依「獲利/現金流/資產負債」的
# 相對強弱,對齊 watchlist/thesis_ecommerce_agentic.md 的盈利分層。
QUALITY_PRIORS: dict[str, float] = {
    # 電商大/中型 — 已獲利規模平台
    "AMZN": 80, "PDD": 80, "MELI": 78, "BABA": 70, "EBAY": 68, "JD": 65,
    "ETSY": 65, "SHOP": 62, "CPNG": 60, "SE": 58, "CHWY": 55, "GLBE": 50,
    "W": 40, "BIGC": 42,
    # 小型 / 長尾電商(主理人點名)— 依盈利分層保守給分
    "RVLV": 68, "VIPS": 70, "CART": 62,             # 已獲利、有空間
    "FIGS": 55, "WRBY": 52, "MYTE": 50, "REAL": 48, "SFIX": 45,  # 轉盈中
    "JMIA": 28, "RENT": 25,                          # 燒錢 / 高風險
}

# 獲利空間先驗(0..100,**保守相對分級,非估值預測**)— 「上檔空間」= 估值便宜 +
# 距高有段 + 利潤率擴張的跑道。高分 = 還沒噴、便宜、有重評價空間;低分 = 已貴/近高。
# 這是結構性起點;真正的距高/估值用 /basecross(月線距高)即時覆蓋。
UPSIDE_PRIORS: dict[str, float] = {
    # 電商大/中型
    "BABA": 65, "JD": 62, "PDD": 58, "SE": 56, "ETSY": 55, "W": 58,
    "EBAY": 48, "CPNG": 50, "CHWY": 45, "GLBE": 50, "BIGC": 55,
    "AMZN": 45, "MELI": 40, "SHOP": 35,             # 強但已不便宜 → 空間較小
    # 小型 / 長尾(深跌 → 帳面空間大,但風險也大)
    "JMIA": 72, "RENT": 55, "SFIX": 58, "REAL": 60, "MYTE": 55,
    "VIPS": 70, "RVLV": 55, "FIGS": 55, "CART": 50, "WRBY": 40,
}


def provisional_rank(tickers: list[str], *, quality_priors: Optional[dict] = None,
                     upside_priors: Optional[dict] = None,
                     momentum_by_ticker: Optional[dict] = None) -> list[dict]:
    """綜合排名 over 基本面 / 獲利空間 / 炒作動能 from priors (+ live 動能 when given).

    Without a live price feed, 炒作動能 is unknown → the composite is the 50/50 blend
    of the 基本面 + 獲利空間 priors and momentum is flagged TBD; pass
    ``momentum_by_ticker`` (e.g. from /rally's technical+capital) to fold the third
    axis in at 30% and re-rank. Returns dicts sorted by composite desc."""
    qp = QUALITY_PRIORS if quality_priors is None else quality_priors
    up = UPSIDE_PRIORS if upside_priors is None else upside_priors
    mom = momentum_by_ticker or {}
    out = []
    for t in tickers:
        fund, upside, m = qp.get(t), up.get(t), mom.get(t)
        if fund is None and upside is None and m is None:
            continue
        parts = {"fundamental": fund, "upside": upside, "momentum": m}
        w = {"fundamental": 0.35, "upside": 0.35, "momentum": 0.30}
        num = den = 0.0
        for k, v in parts.items():
            if v is not None:
                num += w[k] * float(v); den += w[k]
        out.append({
            "ticker": t, "fundamental": fund, "upside": upside, "momentum": m,
            "composite": round(num / den, 1) if den else 0.0,
            "momentum_pending": m is None,
        })
    out.sort(key=lambda r: r["composite"], reverse=True)
    return out


def ecommerce_rank(candidates, *, quality_by_ticker: Optional[dict] = None) -> list[dict]:
    """綜合排名 for e-commerce, with LIVE 炒作動能 folded in.

    動能 = mean(技術, 資金) from each basecross candidate; 基本面 = FOM quality where
    present else QUALITY_PRIORS; 獲利空間 = UPSIDE_PRIORS. Returns provisional_rank
    output with momentum no longer pending. This is what /ecomrank runs."""
    quality_by_ticker = quality_by_ticker or {}
    merged_quality = dict(QUALITY_PRIORS)
    merged_quality.update({k: v for k, v in quality_by_ticker.items() if v is not None})
    momentum: dict[str, float] = {}
    tickers: list[str] = []
    for c in candidates:
        t = getattr(c, "ticker", "")
        tickers.append(t)
        d = dims_from_basecross(c)
        vals = [x for x in (d["technical"], d["capital"]) if x is not None]
        if vals:
            momentum[t] = round(sum(vals) / len(vals), 1)
    return provisional_rank(tickers, quality_priors=merged_quality,
                            momentum_by_ticker=momentum)


@dataclass
class RallySignal:
    ticker: str
    dims: dict = field(default_factory=dict)     # {dim: 0..100 | None}
    composite: float = 0.0
    rising: bool = False                          # 技術維起漲
    is_rallying: bool = False                     # 今期是否起漲(技術+composite)
    streak: int = 0                               # 連續起漲期數
    catalyst: bool = False                        # 有基本面/供應鏈/消息撐
    price_hot: bool = False                       # 技術+資金過熱
    has_fuel: bool = False                         # 真會賺錢(基本面) 或 真有題材(供應鏈/消息)
    wave_candidate: bool = False                  # 夠格展開「大浪」(有燃料 + 起漲)
    dna_match: float = 0.0                         # 與暴漲股 DNA 的相符度 0..100
    conviction: str = ""
    buy_consider: bool = False
    warning: str = ""
    note: str = ""


# ── pure fusion ────────────────────────────────────────────────────────────────

def composite_score(dims: dict, weights: Optional[dict] = None) -> float:
    """Weighted blend over the AVAILABLE dimensions (None = TBD, skipped and the
    remaining weights renormalised — absence of a signal must not score as zero)."""
    weights = weights or DEFAULT_WEIGHTS
    num = den = 0.0
    for d in DIMENSIONS:
        v = dims.get(d)
        if v is None:
            continue
        w = weights.get(d, 0.0)
        num += w * float(v)
        den += w
    return round(num / den, 1) if den else 0.0


def dna_match(dims: dict) -> float:
    """0..100 — how well the profile rhymes with the 2020-26 winner ignition DNA:
    moving (技術) + money-in (資金) AND a real catalyst (基本面/供應鏈/消息)."""
    tech = float(dims.get("technical") or 0)
    cap = float(dims.get("capital") or 0)
    catal = max(float(dims.get("supply_chain") or 0),
                float(dims.get("fundamental") or 0),
                float(dims.get("news") or 0))
    ignition = 0.5 * tech + 0.5 * cap
    score = 0.6 * ignition + 0.4 * catal
    # a vertical move with no catalyst is NOT the winner DNA — it is the pump DNA.
    if catal < 30 and ignition >= HOT_DIM:
        score *= 0.6
    return round(max(0.0, min(100.0, score)), 1)


def update_streak(prior_streak: int, is_rallying: bool) -> int:
    """連續起漲 counter: +1 while rallying, reset to 0 the moment it stalls."""
    return (max(0, prior_streak) + 1) if is_rallying else 0


def assess(ticker: str, dims: dict, *, prior_streak: int = 0,
           evidence_confirmed: bool = False, weights: Optional[dict] = None,
           tight_regime: bool = TIGHT_REGIME_DEFAULT) -> RallySignal:
    """Fuse the five dimensions + persistence into one 起漲 verdict for a ticker.

    ``tight_regime`` (default True, the 2026 non-2021 reality): 廣度小,只有「真會賺錢
    (基本面)或真有題材(供應鏈/消息)」= **有燃料**的票才撐得起大浪;沒燃料的深跌反彈
    被降級為『反彈非大浪』,且不給買入考慮。loose(2021 式瘋牛)則放寬。"""
    sig = RallySignal(ticker=ticker, dims={d: dims.get(d) for d in DIMENSIONS})
    sig.composite = composite_score(dims, weights)
    tech = dims.get("technical")
    sig.rising = tech is not None and float(tech) >= RALLY_MIN
    sig.is_rallying = sig.rising and sig.composite >= RALLY_MIN
    sig.streak = update_streak(prior_streak, sig.is_rallying)
    sig.catalyst = evidence_confirmed or any(
        (dims.get(d) is not None and float(dims.get(d)) >= CATALYST_MIN)
        for d in ("fundamental", "supply_chain", "news"))
    # 燃料 = 真會賺錢(基本面高)或 真有題材(供應鏈/消息高),比 catalyst 更嚴。
    sig.has_fuel = evidence_confirmed or any(
        (dims.get(d) is not None and float(dims.get(d)) >= WAVE_FUEL_MIN)
        for d in ("fundamental", "supply_chain", "news"))
    sig.wave_candidate = sig.has_fuel and sig.is_rallying
    sig.price_hot = (float(dims.get("technical") or 0) >= HOT_DIM
                     and float(dims.get("capital") or 0) >= HOT_DIM)
    sig.dna_match = dna_match(dims)
    # tight regime 下,買入考慮一定要有燃料;loose 則 catalyst 即可。
    fuel_ok = sig.has_fuel if tight_regime else sig.catalyst

    if sig.price_hot and not sig.catalyst:
        # graveyard pattern: vertical price + 資金, zero catalyst → WARN, never buy.
        sig.conviction = "🚫 純炒作·無實證(墓園型)"
        sig.warning = "技術/資金過熱但無基本面/供應鏈/消息題材;這是追高墓園型,先找題材或站旁邊"
    elif sig.streak >= MIN_STREAK_BUY and sig.composite >= BUY_MIN and fuel_ok:
        sig.conviction = f"🟢 連續起漲 {sig.streak} 期 · 可考慮買入(分批/小倉)"
        sig.buy_consider = True
        sig.note = "有燃料(真賺錢/真題材)+ 連續起漲 → 這個 regime 撐得起大浪,仍 recommend-only"
    elif tight_regime and not sig.has_fuel and (sig.is_rallying or sig.composite >= 45):
        # 非-2021:有點動但沒燃料(無真盈利/真題材)→ 撐不起大浪,降級為反彈。
        sig.conviction = "🪨 缺燃料·反彈非大浪" + (f" 第 {sig.streak} 期" if sig.is_rallying else "")
        sig.warning = "不是 2021 瘋牛:無真盈利/真題材,這個 regime 撐不起大浪,反彈不追"
        sig.note = "要嘛等盈利(基本面)轉強、要嘛等真題材出現,才有機會展開大浪"
    elif sig.is_rallying:
        sig.conviction = f"🟡 起漲中 第 {sig.streak} 期(觀察,未達連續門檻)"
        sig.note = f"等連續 ≥ {MIN_STREAK_BUY} 期 + composite ≥ {BUY_MIN:.0f} + 有燃料才考慮"
    elif sig.composite >= 45:
        sig.conviction = "🔵 蓄勢(尚未起漲)"
    else:
        sig.conviction = "⚪ 觀察(訊號不足)"
    return sig


def build_signals(candidates, *, quality_by_ticker: Optional[dict] = None,
                  prior_streaks: Optional[dict] = None,
                  news_by_ticker: Optional[dict] = None,
                  quality_priors: Optional[dict] = None,
                  tight_regime: bool = TIGHT_REGIME_DEFAULT) -> list["RallySignal"]:
    """Fuse a list of basecross candidates + FOM quality + prior streaks → ranked
    起漲 signals. 基本面 uses FOM quality first; if a name isn't in the latest FOM
    scan yet, fall back to a conservative ``quality_priors`` (defaults to
    QUALITY_PRIORS) so the dimension isn't blank. Pure given its inputs."""
    quality_by_ticker = quality_by_ticker or {}
    prior_streaks = prior_streaks or {}
    news_by_ticker = news_by_ticker or {}
    quality_priors = QUALITY_PRIORS if quality_priors is None else quality_priors
    items = []
    for c in candidates:
        t = getattr(c, "ticker", "")
        q = quality_by_ticker.get(t)
        if q is None:
            q = quality_priors.get(t)
        dims = dims_from_basecross(c, fom_quality=q, news=news_by_ticker.get(t))
        items.append({"ticker": t, "dims": dims, "prior_streak": prior_streaks.get(t, 0)})
    return rank(items, tight_regime=tight_regime)


def rank(items: list[dict], *, weights: Optional[dict] = None,
         tight_regime: bool = TIGHT_REGIME_DEFAULT) -> list[RallySignal]:
    """Assess a batch. Each item = {ticker, dims, prior_streak?, evidence_confirmed?}.
    Sorted: buy-considers first, then composite, then dna_match."""
    out = [assess(it["ticker"], it["dims"], prior_streak=it.get("prior_streak", 0),
                  evidence_confirmed=it.get("evidence_confirmed", False), weights=weights,
                  tight_regime=tight_regime)
           for it in items]
    out.sort(key=lambda s: (s.buy_consider, s.composite, s.dna_match), reverse=True)
    return out


# ── dimension mapping from existing signals (pure helpers) ─────────────────────

def dims_from_basecross(c, *, fom_quality: Optional[float] = None,
                        news: Optional[float] = None) -> dict:
    """Map a basecross.BaseCrossCandidate + optional FOM quality/news → the 5 dims.

    技術 from the monthly cross/rising; 資金 from the volume surge; 基本面 from FOM
    quality; 供應鏈 from the design-win tag set; 消息 injected (else TBD)."""
    tech = 40.0
    if getattr(c, "rising", False):
        tech += 30
    if getattr(c, "golden_cross", False) and getattr(c, "bottom_zone", False):
        tech += 30
    tech = min(100.0, tech)

    vs = getattr(c, "vol_surge", None)
    capital: Optional[float] = None
    if vs is not None:
        # ×1.0→30, ×1.3→~48, ×2→~70, ×3→~88, saturate ~100
        import math
        capital = max(0.0, min(100.0, 30.0 + 55.0 * math.log2(max(vs, 1e-9))))

    supply = 80.0 if (getattr(c, "ticker", "") in SUPPLY_CHAIN_TAGS) else 45.0
    return {
        "technical": round(tech, 1),
        "capital": round(capital, 1) if capital is not None else None,
        "fundamental": round(float(fom_quality), 1) if fom_quality is not None else None,
        "supply_chain": supply,
        "news": round(float(news), 1) if news is not None else None,
    }


# ── persistence (連續起漲 across runs) ──────────────────────────────────────────

def load_prior_streaks(outputs_dir: Path, before: Optional[str] = None) -> dict[str, int]:
    """{ticker: streak} from the most recent rally-state-*.jsonl strictly before
    ``before`` (default today) — so today's streak can continue yesterday's."""
    before = before or datetime.now().strftime("%Y-%m-%d")
    files = sorted(Path(outputs_dir).glob("rally-state-*.jsonl"))
    prior = [f for f in files if f.stem.replace("rally-state-", "") < before]
    if not prior:
        return {}
    out: dict[str, int] = {}
    try:
        for line in prior[-1].read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if r.get("ticker"):
                out[r["ticker"]] = int(r.get("streak", 0))
    except Exception:
        return out
    return out


def write_state(outputs_dir: Path, signals: list[RallySignal],
                as_of: Optional[str] = None) -> Path:
    """Append-free snapshot of today's streaks, so the next run continues them."""
    as_of = as_of or datetime.now().strftime("%Y-%m-%d")
    outputs_dir = Path(outputs_dir)
    outputs_dir.mkdir(parents=True, exist_ok=True)
    path = outputs_dir / f"rally-state-{as_of}.jsonl"
    lines = [json.dumps({
        "ticker": s.ticker, "streak": s.streak, "composite": s.composite,
        "is_rallying": s.is_rallying, "buy_consider": s.buy_consider,
        "conviction": s.conviction, "date": as_of,
    }, ensure_ascii=False) for s in signals]
    path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    return path
