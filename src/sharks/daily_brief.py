"""Daily brief engine — 游庭澔『早晨財經速解讀』style, three editions.

  早報 morning : pre-market macro brief — tape -> 速解讀 -> 類股 -> 台股連結 -> 行事曆
  午報 midday  : intraday check — tape vs open + watch + 行事曆提醒 + 盤中紀律
  晚報 evening : post-close wrap + 🎯 個人進出場建議 (portfolio SELL/TRIM/ADD, discipline-
                 overlaid) + 💡 推薦潛力股 (FOM picks) + 明日行事曆

Macro-first, causation-driven (the WHY). Renders MD + HTML + Discord. Picks REUSE
the existing engine's JSON outputs (fom-alpha / portfolio-audit) — never recomputed
here. News = an optional slot (outputs/news-headlines-<date>.json) so a feed/agent
can fill it; econ calendar = curated rules (NFP/CPI/FOMC) until a live feed is wired.

Data = yfinance (grade C); interpretation = data-driven rules. Observe-first /
educational — NOT buy/sell advice. RSU/portfolio actions route through the existing
discipline (finance/05 schedule), never auto-traded.
"""

from __future__ import annotations

import datetime as _dt
import json
from pathlib import Path
from typing import Optional

# ─── ticker groups (display 名 → yfinance ticker) ──────────────────────────────
MACRO = {
    "道瓊": "^DJI", "S&P 500": "^GSPC", "Nasdaq": "^IXIC", "費半 SOX": "^SOX",
    "VIX 恐慌": "^VIX", "美10Y殖利率": "^TNX", "美元 DXY": "DX-Y.NYB",
    "西德州原油": "CL=F", "黃金": "GC=F", "比特幣": "BTC-USD",
}
SECTORS = {
    "科技 XLK": "XLK", "半導體 SOXX": "SOXX", "通訊 XLC": "XLC", "金融 XLF": "XLF",
    "能源 XLE": "XLE", "醫療 XLV": "XLV", "工業 XLI": "XLI", "必需 XLP": "XLP",
    "公用 XLU": "XLU", "原物料 XLB": "XLB",
}
WATCH = {"NVDA": "NVDA", "台積電ADR TSM": "TSM", "AVGO": "AVGO", "MSFT": "MSFT", "AMD": "AMD"}

NVDA_TRACKER_STATUS = "capex 🟢BULL · ASIC 🔴BEAR-WATCH(~27.8%近門檻) · HBM/人才/毛利 🟢"
EDITIONS = {"morning": "早報", "midday": "午報", "evening": "晚報"}
FOMC_2026 = ["2026-01-28", "2026-03-18", "2026-04-29", "2026-06-17",
             "2026-07-29", "2026-09-16", "2026-10-28", "2026-12-09"]

# Curated IPO catalysts — DATE-CERTAIN only (web-verified 2026-06-10; see
# watchlist/ipo_calendar_2026.md). Confidential filings with no set date
# (OpenAI/Anthropic/Discord/Shein) live in that file, not here. Refresh from it.
IPO_EVENTS_2026 = [
    ("2026-06-11", "SpaceX (SPCX) IPO 定價 (~$135/股, ~$1.77T)", "🔴 高"),
    ("2026-06-12", "SpaceX (SPCX) Nasdaq 首日交易 — 太空鏈催化", "🔴 高"),
]


def _g(moves: dict, t: str, k: str = "d1"):
    return (moves.get(t) or {}).get(k)


# ─── interpretation (PURE) ─────────────────────────────────────────────────────
def interpret_macro(moves: dict, edition: str = "morning") -> list[str]:
    """The 速解讀 logic chain — data-driven causation. PURE."""
    b: list[str] = []
    spx, vix, sox = _g(moves, "^GSPC"), _g(moves, "^VIX"), _g(moves, "^SOX")
    tnx, dxy = _g(moves, "^TNX"), _g(moves, "DX-Y.NYB")
    gold, oil, nvda, btc = _g(moves, "GC=F"), _g(moves, "CL=F"), _g(moves, "NVDA"), _g(moves, "BTC-USD")
    if spx is not None and vix is not None:
        if spx > 0 and vix < 0:
            b.append(f"**風險偏好回升**:S&P {spx:+.1f}%、VIX {vix:+.1f}% → risk-on,買盤願意進場。")
        elif spx < 0 and vix > 0:
            b.append(f"**避險升溫**:S&P {spx:+.1f}%、VIX {vix:+.1f}% → risk-off,資金收傘、慎追高。")
        else:
            b.append(f"**方向分歧**:S&P {spx:+.1f}%、VIX {vix:+.1f}% → 多空拉鋸,觀望為宜。")
    if sox is not None and spx is not None:
        rel = sox - spx
        if rel > 0.3:
            b.append(f"**半導體領漲**(費半 {sox:+.1f}% vs 大盤 {spx:+.1f}%)→ AI 算力敘事仍是主引擎,**台股 AI 鏈(台積電/設備/載板)偏強**。")
        elif rel < -0.3:
            b.append(f"**半導體領跌**(費半 {sox:+.1f}% vs 大盤 {spx:+.1f}%)→ 資金自科技撤,**留意台積電/AI 鏈補跌壓力**。")
    if tnx is not None:
        if tnx > 1.0:
            b.append(f"**美 10 年殖利率走高**({tnx:+.1f}%)→ 壓抑高估值成長股與長天期資產。")
        elif tnx < -1.0:
            b.append(f"**殖利率回落**({tnx:+.1f}%)→ 利多成長股/科技股估值,分母變小。")
    if dxy is not None:
        if dxy > 0.3:
            b.append(f"**美元走強**(DXY {dxy:+.1f}%)→ 不利新興市場、商品與台股外資動能。")
        elif dxy < -0.3:
            b.append(f"**美元走弱**(DXY {dxy:+.1f}%)→ 利多商品與非美資產。")
    if gold is not None and abs(gold) > 0.6:
        b.append(f"黃金 {gold:+.1f}% → {'避險/實質利率下行訊號' if gold > 0 else '避險降溫'}。")
    if oil is not None and abs(oil) > 1.5:
        b.append(f"油價{'急漲' if oil > 0 else '急跌'} {oil:+.1f}% → {'通膨/能源股壓力' if oil > 0 else '通膨壓力緩、運輸消費受惠'}。")
    if nvda is not None:
        b.append(f"**龍頭 NVDA {nvda:+.1f}%** — 全產業風向球;{NVDA_TRACKER_STATUS}。")
    if btc is not None and abs(btc) > 3:
        b.append(f"比特幣 {btc:+.1f}% → 風險情緒高 beta 溫度計,{'樂觀' if btc > 0 else '轉弱'}。")
    return b


def sector_rotation(sector_moves: dict) -> dict:
    """Rank sectors by 1d move → 資金流入/流出. PURE."""
    ranked = sorted(((k, v) for k, v in sector_moves.items() if v is not None), key=lambda x: -x[1])
    return {"ranked": ranked, "inflow": [k for k, v in ranked[:3]], "outflow": [k for k, v in ranked[-3:]]}


def tw_implication(moves: dict) -> str:
    """US overnight → 台股 AI 供應鏈含義 (游庭澔 signature). PURE."""
    sox, nvda = _g(moves, "^SOX"), _g(moves, "NVDA")
    if sox is None:
        return "費半資料不足,台股映射略過。"
    if sox > 0.5:
        return (f"費半 {sox:+.1f}%、NVDA {nvda:+.1f}% → **台積電/AI 設備/載板/散熱 偏多**,"
                f"留意開高能否守住量能;強勢不追高,等回測支撐。")
    if sox < -0.5:
        return (f"費半 {sox:+.1f}%、NVDA {nvda:+.1f}% → **台股 AI 鏈有補跌壓力**,"
                f"台積電權值若弱會拖大盤;看外資期貨與台積電開盤量能。")
    return f"費半 {sox:+.1f}% 持平 → 台股 AI 鏈中性,看台積電個別表現與台幣匯率。"


def econ_calendar(date_str: str) -> list[tuple]:
    """本週/近日總經事件 (游庭澔每日前瞻). v1 curated rules — NFP=當月首個週五,
    CPI≈10–14日,FOMC 為 2026 排程。回 [(date, event, impact)]。標估算,待接 live feed。PURE."""
    y, m, d = map(int, date_str.split("-"))
    today = _dt.date(y, m, d)
    ev: list[tuple] = []
    for f in FOMC_2026:
        fd = _dt.date(*map(int, f.split("-")))
        if 0 <= (fd - today).days <= 12:
            ev.append((f, "FOMC 利率決議 + 點陣圖", "🔴 高"))
    first = _dt.date(y, m, 1)
    nfp = first + _dt.timedelta(days=(4 - first.weekday()) % 7)
    if -1 <= (nfp - today).days <= 7:
        ev.append((nfp.isoformat(), "非農就業 NFP + 失業率", "🔴 高"))
    cpi_hi = _dt.date(y, m, 14)
    if 0 <= (cpi_hi - today).days <= 8:
        ev.append((f"{y}-{m:02d}-10~14(估)", "CPI 消費者物價", "🔴 高"))
    # IPO catalysts — surface from ~3 weeks ahead through the listing day.
    for ds, name, imp in IPO_EVENTS_2026:
        try:
            ed = _dt.date(*map(int, ds.split("-")))
        except ValueError:
            continue
        if -1 <= (ed - today).days <= 21:
            ev.append((ds, name, imp))
    if not ev:
        ev.append(("—", "本週無排程高衝擊數據(估);留意 Fed 官員談話與盤後財報", "🟡 中"))
    return ev


# ─── picks (REUSE existing engine JSONs; never recompute) ──────────────────────
def _latest(out_dir: Path, prefix: str):
    fs = sorted(out_dir.glob(f"{prefix}*.json"), reverse=True)
    if not fs:
        return None
    try:
        return json.loads(fs[0].read_text(encoding="utf-8"))
    except Exception:
        return None


def load_picks(out_dir: Path) -> dict:
    """進出場 + 潛力股, composed from fom-alpha + portfolio-audit (already computed)."""
    fom = _latest(out_dir, "fom-alpha") or {}
    audit = _latest(out_dir, "portfolio-audit") or {}

    def pk(p):
        return {"ticker": p.get("ticker"),
                "fom": p.get("final_fom_alpha", p.get("fom_score")),
                "mom": p.get("momentum"), "contr": p.get("contrarian"),
                "bubble": p.get("bubble_guard"), "moat": p.get("ip_defensibility")}
    potential = [pk(p) for p in (fom.get("top_3_sp500_eligible", []) + fom.get("top_3_r2k_eligible", []))]
    p1 = audit.get("p1_summary", {}) or {}
    p2 = audit.get("p2_summary", {}) or {}
    return {
        "potential": [p for p in potential if p["ticker"]],
        "exit": {"P1_SELL": p1.get("SELL", []), "P1_TRIM": p1.get("TRIM", []), "P2_SELL": p2.get("SELL", [])},
        "enter": {"P2_ADD": p2.get("ADD", [])},
        "held_winners": audit.get("p1_held_winners", []),
        "have_fom": bool(fom), "have_audit": bool(audit),
    }


def load_igv(out_dir: Path):
    """Latest IGV software screen (錯殺軟體 + NVIDIA 合作), or None."""
    igv = _latest(out_dir, "igv-software")
    if not igv:
        return None
    return {
        "screen_date": igv.get("screen_date"), "igv_as_of": igv.get("igv_as_of"),
        "universe_size": igv.get("universe_size"),
        "oversold": (igv.get("oversold") or [])[:6],
        "nvidia_partners": igv.get("nvidia_partners") or [],
    }


def _num(v, fmt="{:.0f}"):
    return fmt.format(v) if isinstance(v, (int, float)) else "—"


def _pct(v):
    return f"{v:+.0%}" if isinstance(v, (int, float)) else "—"


def load_news(out_dir: Path, date: str) -> list[str]:
    """Optional news slot — outputs/news-headlines-<date>.json {"headlines":[...]}.
    Lets a feed/agent fill the event-driven 解讀; empty until wired."""
    p = out_dir / f"news-headlines-{date}.json"
    if p.exists():
        try:
            return (json.loads(p.read_text(encoding="utf-8")) or {}).get("headlines", [])[:6]
        except Exception:
            return []
    return []


def load_postmortems(out_dir: Path, date: str) -> list[dict]:
    """Latest attribution-postmortem aggregate (outputs/postmortem-<date>.json),
    compacted for the evening 收盤閉環 section. Empty list if none — the brief
    degrades. Produced separately by `sharks postmortem`; this only reads."""
    best = None
    for p in sorted(out_dir.glob("postmortem-*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(data, dict) and "postmortems" in data:
            best = data  # sorted() → newest aggregate wins
    if not best:
        return []
    return [
        {"ticker": r.get("ticker"), "exited_reason": r.get("exited_reason"),
         "cause": r.get("cause"), "why": r.get("why")}
        for r in (best.get("postmortems") or [])[:8]
    ]


# ─── data ──────────────────────────────────────────────────────────────────────
def fetch_moves(tickers: list[str]) -> dict:
    """Overnight % moves (1d/5d/1mo) via one yfinance batch. Network."""
    import warnings
    warnings.filterwarnings("ignore")
    import pandas as pd
    import yfinance as yf
    data = yf.download(list(tickers), period="3mo", interval="1d", auto_adjust=True, progress=False)
    if isinstance(data.columns, pd.MultiIndex):
        close = data["Close"]
    else:
        close = data[["Close"]].rename(columns={"Close": tickers[0]}) if "Close" in data.columns else data
    out = {}
    for t in tickers:
        try:
            s = close[t].dropna() if t in close.columns else None
        except Exception:
            s = None
        if s is None or len(s) < 2:
            out[t] = {"price": None, "d1": None, "d5": None, "d1mo": None}
            continue
        px = float(s.iloc[-1])
        out[t] = {"price": round(px, 2),
                  "d1": round((px / float(s.iloc[-2]) - 1) * 100, 2),
                  "d5": round((px / float(s.iloc[-6]) - 1) * 100, 2) if len(s) > 6 else None,
                  "d1mo": round((px / float(s.iloc[-22]) - 1) * 100, 2) if len(s) > 22 else None}
    return out


def _named(moves: dict, group: dict) -> list[tuple]:
    return [(disp, moves.get(t, {}).get("price"), moves.get(t, {}).get("d1"),
             moves.get(t, {}).get("d5"), moves.get(t, {}).get("d1mo")) for disp, t in group.items()]


def _arrow(v: Optional[float]) -> str:
    if v is None:
        return "—"
    return f"🔺{v:+.2f}%" if v > 0 else (f"🔻{v:+.2f}%" if v < 0 else "▪️0.00%")


# ─── renderers (read ctx; edition-aware) ───────────────────────────────────────
def render_md(ctx: dict) -> str:
    ed, lab = ctx["edition"], ctx["edition_label"]
    tape_lab = {"morning": "開盤速覽", "midday": "盤中速覽", "evening": "收盤速覽"}[ed]
    L = [f"# 🌅 早晨財經速解讀 — {ctx['date']} {lab}",
         f"> 仿游庭澔《早晨財經速解讀》結構。**研究/教育用途,非投資建議。**　_(edition: {ed})_", "",
         f"## 1️⃣ {tape_lab}", "", "| 指標 | 收盤 | 日 | 週 | 月 |", "|---|--:|--:|--:|--:|"]
    for dd, p, a, b, c in ctx["macro"]:
        L.append(f"| {dd} | {p if p is not None else '—'} | {_arrow(a)} | {_arrow(b)} | {_arrow(c)} |")
    if ctx.get("news"):
        L += ["", "## 📰 隔夜頭條", ""] + [f"- {h}" for h in ctx["news"]]
    L += ["", "## 2️⃣ 速解讀(為什麼)", ""] + ([f"- {x}" for x in ctx["interp"]] or ["- (資料不足)"])
    if ed != "midday":
        L += ["", "## 3️⃣ 類股與資金流", "",
              f"**資金流入** → {' · '.join(ctx['rot']['inflow'])}　|　**資金流出** → {' · '.join(ctx['rot']['outflow'])}", "",
              "| 類股 | 日% |", "|---|--:|"]
        L += [f"| {k} | {_arrow(v)} |" for k, v in ctx["rot"]["ranked"]]
        L += ["", "## 4️⃣ 台股連結", "", ctx["tw"]]
    L += ["", "## 5️⃣ 個股觀察(風向球)", "", "| 股 | 價 | 日 | 週 | 月 |", "|---|--:|--:|--:|--:|"]
    for dd, p, a, b, c in ctx["watch"]:
        L.append(f"| {dd} | {p if p is not None else '—'} | {_arrow(a)} | {_arrow(b)} | {_arrow(c)} |")
    L += ["", f"- **NVDA 追蹤頁**:{NVDA_TRACKER_STATUS}(`tech/nvda-bull-bear-tracker.md`)"]
    pk = ctx.get("picks")
    if pk:
        L += ["", "## 🎯 個人進出場建議(紀律疊加)", "",
              f"- **出場/減碼**:P1 賣出 → {', '.join(pk['exit']['P1_SELL']) or '—'};P1 減碼 → {', '.join(pk['exit']['P1_TRIM']) or '—'}",
              f"- **進場/加碼候選**:{', '.join(pk['enter']['P2_ADD']) or '—'}"]
        hw = pk.get("held_winners") or []
        if hw:
            L.append("- **🛡️ 抱住的贏家(反饋機制:強勢+支撐完好 → 不換股,改掛移動停利)**:")
            for h in hw:
                ts = h.get("trailing_stop_pct")
                ts_txt = f"{ts:.0%}移動停利" if isinstance(ts, (int, float)) else "移動停利"
                s = h.get("support") or {}
                rr = s.get("recent_return")
                rr_txt = f"{rr:+.0%}" if isinstance(rr, (int, float)) else "n/a"
                L.append(f"    - **{h['ticker']}** → {h.get('reviewed_verdict')}({ts_txt});"
                         f"近3月 {rr_txt}、動能 {s.get('momentum')};翻賣條件:{h.get('flips_to_sell_when')}")
        L += ["- **NVDA 紀律**:照 `finance/05` 排程賣到 50%(機器動作,不看盤);槓桿 ETF 優先出清。",
              "", "## 💡 推薦潛力股(FOM 篩選)", ""]
        def _n(v):
            return f"{v:.0f}" if isinstance(v, (int, float)) else "—"
        if pk["potential"]:
            L += ["| 標的 | FOM | 動能 | 逆勢 | 泡沫防護 | 護城河 |", "|---|--:|--:|--:|--:|--:|"]
            L += [f"| {p['ticker']} | {_n(p['fom'])} | {_n(p['mom'])} | {_n(p['contr'])} | {_n(p['bubble'])} | {_n(p['moat'])} |"
                  for p in pk["potential"]]
            L += ["", "_讀法:逆勢高=抄底型、動能高=趨勢型、泡沫防護低=估值偏貴需留意;非進場價,僅篩選。_"]
        else:
            L.append("- (尚無 fom-alpha 輸出;先跑 FOM 引擎)")
    igv = ctx.get("igv")
    if igv and (igv.get("oversold") or igv.get("nvidia_partners")):
        L += ["", "## 🧬 IGV 軟體 — 錯殺抄底 + NVIDIA 合作",
              f"_全 IGV {igv.get('universe_size')} 檔(成分 {igv.get('igv_as_of')})· 引擎篩選,非建議_"]
        if igv.get("oversold"):
            L += ["", "**錯殺型(逆勢高+護城河完好)**:",
                  "| 標的 | 逆勢 | 動能 | 護城河 | 近3月 | fPE | 分析師升 | NV |",
                  "|---|--:|--:|--:|--:|--:|--:|---|"]
            for r in igv["oversold"]:
                fu = r.get("fundamentals") or {}
                nv = (r.get("nvidia") or {}).get("tier", "")
                L.append(f"| {r['ticker']} | {_num(r.get('contrarian'))} | {_num(r.get('momentum'))} | "
                         f"{_num(r.get('ip_defensibility'))} | {_pct(r.get('ret_3m'))} | "
                         f"{_num(fu.get('fwd_pe'))} | {_pct(fu.get('analyst_upside'))} | {nv} |")
        if igv.get("nvidia_partners"):
            L += ["", "**NVIDIA 合作夥伴(波動催化;tier equity>headline>medium>integration)**:"]
            for r in igv["nvidia_partners"]:
                nv = r.get("nvidia") or {}
                L.append(f"    - **{r['ticker']}** [{nv.get('tier')}] {nv.get('type')} — "
                         f"逆勢{_num(r.get('contrarian'))}/動能{_num(r.get('momentum'))}/近3月{_pct(r.get('ret_3m'))}")
    pms = ctx.get("postmortems")
    if pms:
        L += ["", "## 🔁 收盤閉環 — 失敗歸因(recommend-only)",
              "_止損/未達預期的標的自動歸因:regime_flip / quant_signal_failure / "
              "narrative_shift / execution_timing_", "",
              "| 標的 | 出場 | 歸因 | 說明 |", "|---|---|---|---|"]
        L += [f"| {r.get('ticker')} | {r.get('exited_reason')} | {r.get('cause')} | {r.get('why','')} |"
              for r in pms]
    L += ["", "## 📅 數據行事曆", "", "| 日期 | 事件 | 衝擊 |", "|---|---|---|"]
    L += [f"| {dt} | {e} | {imp} |" for dt, e, imp in ctx["calendar"]]
    L += ["", "## 📌 觀察重點 + 紀律", "",
          f"- **環境(regime)**:{ctx['regime']}",
          "- **紀律**:NVDA 是風向球也是你 ~89% 曝險;此報研究非加碼訊號。RSU 照排程賣到 50%,BEAR 觸發看雲廠 capex / ASIC 推論佔比。",
          "", "---", "*研究/教育用途 — 非買賣建議。資料 yfinance(grade C);解讀為規則化邏輯。*"]
    return "\n".join(L)


def render_discord(ctx: dict) -> str:
    def row(d, p, a):
        return f"{d:<11}{(str(p) if p is not None else '—'):>10}  {_arrow(a)}"
    tape = "\n".join(row(d, p, a) for d, p, a, *_ in ctx["macro"])
    w = "\n".join(row(d, p, a) for d, p, a, *_ in ctx["watch"])
    P = [f"🌅 **早晨財經速解讀 — {ctx['date']} {ctx['edition_label']}**  _(研究非建議)_", "",
         "**📊 速覽**", "```", tape, "```", "**🧠 速解讀**"]
    P += [f"• {x.replace('**','')}" for x in ctx["interp"][:6]]
    if ctx["edition"] != "midday":
        P += ["", f"**🔄 資金** 流入 {' · '.join(ctx['rot']['inflow'])} ｜ 流出 {' · '.join(ctx['rot']['outflow'])}",
              f"**🇹🇼 台股** {ctx['tw'].replace('**','')}"]
    P += ["", "**🎯 風向球**", "```", w, "```"]
    pk = ctx.get("picks")
    if pk:
        P += [f"**🎯 進出場** 出 {', '.join(pk['exit']['P1_SELL'][:5]) or '—'} ｜ 減 {', '.join(pk['exit']['P1_TRIM'][:5]) or '—'} ｜ 加 {', '.join(pk['enter']['P2_ADD'][:5]) or '—'}",
              f"**💡 潛力股** {', '.join(p['ticker'] for p in pk['potential'][:6]) or '—'}"]
    pms = ctx.get("postmortems")
    if pms:
        P += ["**🔁 收盤閉環** " + " ｜ ".join(f"{r.get('ticker')}:{r.get('cause')}" for r in pms[:5])]
    cal = " ｜ ".join(f"{e}({imp.split()[0]})" for _, e, imp in ctx["calendar"][:3])
    P += [f"**📅 行事曆** {cal}",
          f"🧭 {ctx['regime']} ｜ 紀律:NVDA=風向球也是你89%曝險,RSU照排程賣到50%,別追高。"]
    return "\n".join(P)


def render_html(ctx: dict) -> str:
    def cell(v):
        if v is None:
            return '<td class="n">—</td>'
        return f'<td class="{"up" if v>0 else ("dn" if v<0 else "n")}">{v:+.2f}%</td>'
    def trows(rows):
        return "\n".join(f"<tr><td class='nm'>{d}</td><td class='px'>{p if p is not None else '—'}</td>"
                         f"{cell(a)}{cell(b)}{cell(c)}</tr>" for d, p, a, b, c in rows)
    sect = "\n".join(f"<tr><td class='nm'>{k}</td>{cell(v)}</tr>" for k, v in ctx["rot"]["ranked"])
    interp = "".join(f"<li>{x.replace('**','')}</li>" for x in ctx["interp"])
    cal = "\n".join(f"<tr><td class='nm'>{dt}</td><td>{e}</td><td>{imp}</td></tr>" for dt, e, imp in ctx["calendar"])
    news = ("<h2>📰 隔夜頭條</h2><ul>" + "".join(f"<li>{h}</li>" for h in ctx["news"]) + "</ul>") if ctx.get("news") else ""
    rot_block = "" if ctx["edition"] == "midday" else f"""
<h2>3️⃣ 類股與資金流</h2>
<div class="box">資金流入 → <b>{' · '.join(ctx['rot']['inflow'])}</b>　|　流出 → <b>{' · '.join(ctx['rot']['outflow'])}</b></div>
<table><tr><th class='nm'>類股</th><th>日%</th></tr>{sect}</table>
<h2>4️⃣ 台股連結</h2><div class="box tw">{ctx['tw'].replace('**','')}</div>"""
    pk = ctx.get("picks")
    picks_block = ""
    if pk:
        def _n(v):
            return f"{v:.0f}" if isinstance(v, (int, float)) else "—"
        pot = ("".join(f"<tr><td class='nm'>{p['ticker']}</td><td>{_n(p['fom'])}</td><td>{_n(p['mom'])}</td>"
                       f"<td>{_n(p['contr'])}</td><td>{_n(p['bubble'])}</td><td>{_n(p['moat'])}</td></tr>" for p in pk["potential"])
               or "<tr><td colspan=6 class='n'>尚無 fom-alpha 輸出</td></tr>")
        picks_block = f"""
<h2>🎯 個人進出場建議(紀律疊加)</h2>
<div class="box">
<b>出場/減碼</b> — P1 賣出: {', '.join(pk['exit']['P1_SELL']) or '—'} ｜ P1 減碼: {', '.join(pk['exit']['P1_TRIM']) or '—'}<br>
<b>進場/加碼候選</b> — {', '.join(pk['enter']['P2_ADD']) or '—'}<br>
<b>NVDA 紀律</b> — 照 finance/05 排程賣到 50%(機器動作);槓桿 ETF 優先出清。
</div>
<h2>💡 推薦潛力股(FOM 篩選)</h2>
<table><tr><th class='nm'>標的</th><th>FOM</th><th>動能</th><th>逆勢</th><th>泡沫防護</th><th>護城河</th></tr>{pot}</table>
<p class="sub">讀法:逆勢高=抄底型、動能高=趨勢型、泡沫防護低=估值偏貴需留意;非進場價,僅篩選。</p>"""
    pms = ctx.get("postmortems")
    pm_block = ""
    if pms:
        pm_rows = "".join(
            f"<tr><td class='nm'>{r.get('ticker')}</td><td>{r.get('exited_reason')}</td>"
            f"<td>{r.get('cause')}</td><td style='text-align:left'>{r.get('why','')}</td></tr>"
            for r in pms
        )
        pm_block = f"""
<h2>🔁 收盤閉環 — 失敗歸因(recommend-only)</h2>
<table><tr><th class='nm'>標的</th><th>出場</th><th>歸因</th><th>說明</th></tr>{pm_rows}</table>
<p class="sub">止損/未達預期自動歸因 — regime_flip / quant_signal_failure / narrative_shift / execution_timing。非建議。</p>"""
    return f"""<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>速解讀 {ctx['date']} {ctx['edition_label']}</title><style>
:root{{color-scheme:dark}}body{{font:15px/1.6 -apple-system,"Noto Sans TC",system-ui,sans-serif;background:#0d1117;color:#e6edf3;margin:0 auto;padding:24px;max-width:900px}}
h1{{font-size:22px;border-bottom:2px solid #30363d;padding-bottom:10px}}h2{{font-size:17px;margin-top:26px;color:#58a6ff}}
.sub{{color:#8b949e;font-size:13px;margin-top:-6px}}table{{border-collapse:collapse;width:100%;margin:8px 0;font-variant-numeric:tabular-nums}}
td,th{{padding:6px 10px;border-bottom:1px solid #21262d;text-align:right}}.nm{{text-align:left;color:#c9d1d9}}.px{{color:#8b949e}}
td:not(.nm):not(.px){{text-align:left}}.up{{color:#3fb950}}.dn{{color:#f85149}}.n{{color:#8b949e}}ul{{padding-left:20px}}li{{margin:4px 0}}
.box{{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:12px 16px;margin:10px 0}}.tw{{border-left:3px solid #58a6ff}}
.foot{{color:#6e7681;font-size:12px;margin-top:24px;border-top:1px solid #21262d;padding-top:10px}}
.tag{{display:inline-block;background:#1f6feb33;color:#58a6ff;border-radius:4px;padding:1px 8px;font-size:12px}}</style></head><body>
<h1>🌅 早晨財經速解讀 — {ctx['date']} <span class="tag">{ctx['edition_label']}</span></h1>
<p class="sub">仿游庭澔《早晨財經速解讀》:看盤 → 為什麼 → 類股 → 台股連結。研究/教育用途,非投資建議。</p>
<h2>1️⃣ 速覽</h2><table><tr><th class='nm'>指標</th><th>收盤</th><th>日</th><th>週</th><th>月</th></tr>{trows(ctx['macro'])}</table>
{news}<h2>2️⃣ 速解讀(為什麼)</h2><ul>{interp}</ul>{rot_block}
<h2>5️⃣ 個股觀察(風向球)</h2><table><tr><th class='nm'>股</th><th>價</th><th>日</th><th>週</th><th>月</th></tr>{trows(ctx['watch'])}</table>
<div class="box">NVDA 追蹤頁:{NVDA_TRACKER_STATUS}</div>{picks_block}{pm_block}
<h2>📅 數據行事曆</h2><table><tr><th class='nm'>日期</th><th>事件</th><th>衝擊</th></tr>{cal}</table>
<h2>📌 觀察重點 + 紀律</h2><div class="box">環境:<b>{ctx['regime']}</b><br>紀律:NVDA 是風向球也是你 ~89% 曝險;研究非加碼訊號。RSU 照排程賣到 50%,BEAR 觸發看雲廠 capex / ASIC 推論佔比。</div>
<p class="foot">研究/教育用途 — 非買賣建議。資料 yfinance(grade C);解讀為規則化邏輯。Generated by sharks.daily_brief ({ctx['edition']}).</p>
</body></html>"""


def generate(edition: str = "morning", out_dir: str = "outputs") -> dict:
    """Build + render one edition; write 3 files. Returns {paths, discord_len}."""
    edition = edition if edition in EDITIONS else "morning"
    tpe = _dt.timezone(_dt.timedelta(hours=8))
    date = _dt.datetime.now(tpe).strftime("%Y-%m-%d")
    od = Path(out_dir)
    od.mkdir(parents=True, exist_ok=True)

    all_t = list(dict.fromkeys(list(MACRO.values()) + list(SECTORS.values()) + list(WATCH.values())))
    moves = fetch_moves(all_t)
    try:
        from sharks.scoring.valuation import current_environment
        ce = current_environment()
        regime = f"{ce['environment']} ({ce.get('classifier_label') or ce.get('source')})"
    except Exception:
        regime = "中性 (n/a)"

    ctx = {
        "date": date, "edition": edition, "edition_label": EDITIONS[edition],
        "macro": _named(moves, MACRO), "watch": _named(moves, WATCH),
        "interp": interpret_macro(moves, edition),
        "rot": sector_rotation({disp: moves.get(t, {}).get("d1") for disp, t in SECTORS.items()}),
        "tw": tw_implication(moves), "regime": regime,
        "calendar": econ_calendar(date), "news": load_news(od, date),
        "picks": load_picks(od) if edition in ("midday", "evening") else None,
        "igv": load_igv(od) if edition in ("midday", "evening") else None,
        "postmortems": load_postmortems(od, date) if edition == "evening" else None,
    }
    md, html, disc = render_md(ctx), render_html(ctx), render_discord(ctx)
    base = f"daily-brief-{date}-{edition}"
    (od / f"{base}.md").write_text(md, encoding="utf-8")
    (od / f"{base}.html").write_text(html, encoding="utf-8")
    (od / f"{base}-discord.txt").write_text(disc, encoding="utf-8")
    return {"date": date, "edition": edition, "md": str(od / f"{base}.md"),
            "html": str(od / f"{base}.html"), "discord": str(od / f"{base}-discord.txt"),
            "discord_len": len(disc), "discord_text": disc}


def main(argv=None) -> int:
    import argparse
    import sys
    ap = argparse.ArgumentParser(prog="daily-brief", description="游庭澔-style daily brief (早/午/晚)")
    ap.add_argument("--edition", choices=list(EDITIONS), default="morning")
    ap.add_argument("--out-dir", default="outputs")
    args = ap.parse_args(argv)
    r = generate(args.edition, args.out_dir)
    print(f"wrote {r['md']} (+ .html, -discord.txt; {r['discord_len']} discord chars)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
