"""Daily morning brief — 游庭澔『早晨財經速解讀』style/structure/logic.

Macro-first, causation-driven (not just numbers — the WHY). Structure mirrors the
morning-show flow:
  1. 開盤速覽   overnight tape: 四大指數 + 費半 + 債/匯/商品/加密
  2. 速解讀     the logic chain — risk-on/off, 殖利率, 費半領漲/領跌, 美元, 龍頭 NVDA
  3. 類股與資金流  sector ETF rotation (資金流入/流出)
  4. 台股連結   US overnight → 台積電 / 台股 AI 供應鏈隔日含義 (游庭澔 signature angle)
  5. 個股觀察   bellwethers + NVDA tracker status + valuation/exposure discipline
  6. 今日觀察重點  watch items + 紀律提醒

Renders MD + HTML + Discord. Complements daily_signals.py (picks/alerts). Data =
yfinance overnight % moves; interpretation = data-driven logic + the $hark regime
classifier. Observe-first / educational — NOT buy/sell advice.
"""

from __future__ import annotations

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

# NVDA tracker weekly status (refresh from tech/nvda-bull-bear-tracker.md, not daily)
NVDA_TRACKER_STATUS = "capex 🟢BULL · ASIC 🔴BEAR-WATCH(~27.8%近門檻) · HBM/人才/毛利 🟢"


def _g(moves: dict, t: str, k: str = "d1"):
    return (moves.get(t) or {}).get(k)


def interpret_macro(moves: dict) -> list[str]:
    """The 速解讀 logic chain — data-driven causation, 游庭澔 style. PURE."""
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
            b.append(f"**半導體領漲**(費半 {sox:+.1f}% vs 大盤 {spx:+.1f}%)→ AI 算力敘事仍是主引擎,**台股 AI 鏈(台積電/設備/載板)隔日多偏強**。")
        elif rel < -0.3:
            b.append(f"**半導體領跌**(費半 {sox:+.1f}% vs 大盤 {spx:+.1f}%)→ 資金自科技撤,**留意台積電/AI 鏈隔日補跌壓力**。")
    if tnx is not None:
        if tnx > 1.0:
            b.append(f"**美 10 年殖利率走高**({tnx:+.1f}%)→ 壓抑高估值成長股與長天期資產,利率敏感族群承壓。")
        elif tnx < -1.0:
            b.append(f"**殖利率回落**({tnx:+.1f}%)→ 利多成長股/科技股估值,分母變小。")
    if dxy is not None:
        if dxy > 0.3:
            b.append(f"**美元走強**(DXY {dxy:+.1f}%)→ 不利新興市場、商品與台股外資動能。")
        elif dxy < -0.3:
            b.append(f"**美元走弱**(DXY {dxy:+.1f}%)→ 利多商品與非美資產,外資回補有空間。")
    if gold is not None and abs(gold) > 0.6:
        b.append(f"黃金 {gold:+.1f}% → {'避險/實質利率下行訊號' if gold > 0 else '避險降溫'}。")
    if oil is not None and abs(oil) > 1.5:
        b.append(f"油價{'急漲' if oil > 0 else '急跌'} {oil:+.1f}% → {'通膨/能源股壓力' if oil > 0 else '通膨壓力緩、運輸消費受惠'}。")
    if nvda is not None:
        b.append(f"**龍頭 NVDA {nvda:+.1f}%** — 全產業風向球,動向牽動費半與台積電鏈;{NVDA_TRACKER_STATUS}。")
    if btc is not None and abs(btc) > 3:
        b.append(f"比特幣 {btc:+.1f}% → 風險情緒的高 beta 溫度計,{'樂觀' if btc > 0 else '轉弱'}。")
    return b


def sector_rotation(sector_moves: dict) -> dict:
    """Rank sectors by 1d move → 資金流入/流出 read. PURE.
    sector_moves: {display_name: d1_pct}."""
    ranked = sorted(((k, v) for k, v in sector_moves.items() if v is not None), key=lambda x: -x[1])
    return {
        "ranked": ranked,
        "inflow": [k for k, v in ranked[:3]],
        "outflow": [k for k, v in ranked[-3:]],
    }


def tw_implication(moves: dict) -> str:
    """US overnight → 台股 AI 供應鏈隔日含義 (游庭澔 signature). PURE."""
    sox, nvda = _g(moves, "^SOX"), _g(moves, "NVDA")
    if sox is None:
        return "費半資料不足,台股映射略過。"
    if sox > 0.5:
        return (f"費半 {sox:+.1f}%、NVDA {nvda:+.1f}% → **台積電/AI 設備/載板/散熱 隔日偏多**,"
                f"但留意開高後能否守住量能;強勢不追高,等回測支撐。")
    if sox < -0.5:
        return (f"費半 {sox:+.1f}%、NVDA {nvda:+.1f}% → **台股 AI 鏈隔日有補跌壓力**,"
                f"台積電權值若弱會拖大盤;觀察外資期貨與台積電開盤量能。")
    return f"費半 {sox:+.1f}% 持平 → 台股 AI 鏈隔日中性,看台積電個別表現與台幣匯率。"


# ─── data ──────────────────────────────────────────────────────────────────────
def fetch_moves(tickers: list[str]) -> dict:
    """Overnight % moves (1d/5d/1mo) for tickers via one yfinance batch. Network."""
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
        out[t] = {
            "price": round(px, 2),
            "d1": round((px / float(s.iloc[-2]) - 1) * 100, 2),
            "d5": round((px / float(s.iloc[-6]) - 1) * 100, 2) if len(s) > 6 else None,
            "d1mo": round((px / float(s.iloc[-22]) - 1) * 100, 2) if len(s) > 22 else None,
        }
    return out


def _named(moves: dict, group: dict) -> list[tuple]:
    """[(display, price, d1, d5, d1mo), ...] for a {display:ticker} group."""
    rows = []
    for disp, t in group.items():
        m = moves.get(t, {})
        rows.append((disp, m.get("price"), m.get("d1"), m.get("d5"), m.get("d1mo")))
    return rows


def _arrow(v: Optional[float]) -> str:
    if v is None:
        return "—"
    return f"🔺{v:+.2f}%" if v > 0 else (f"🔻{v:+.2f}%" if v < 0 else "▪️0.00%")


# ─── renderers ─────────────────────────────────────────────────────────────────
def render_md(date: str, macro: list, interp: list, rot: dict, tw: str, watch: list, regime: str) -> str:
    L = [f"# 🌅 早晨財經速解讀 — {date}",
         "> 仿游庭澔《早晨財經速解讀》:先看盤 → 解讀為什麼 → 類股 → 台股連結。**研究/教育用途,非投資建議。**", "",
         "## 1️⃣ 開盤速覽", "", "| 指標 | 收盤 | 日 | 週 | 月 |", "|---|--:|--:|--:|--:|"]
    for d, p, a, b, c in macro:
        L.append(f"| {d} | {p if p is not None else '—'} | {_arrow(a)} | {_arrow(b)} | {_arrow(c)} |")
    L += ["", "## 2️⃣ 速解讀(為什麼)", ""]
    L += [f"- {x}" for x in interp] or ["- (資料不足)"]
    L += ["", "## 3️⃣ 類股與資金流", "",
          f"**資金流入** → {' · '.join(rot['inflow'])}　|　**資金流出** → {' · '.join(rot['outflow'])}", "",
          "| 類股 | 日% |", "|---|--:|"]
    for k, v in rot["ranked"]:
        L.append(f"| {k} | {_arrow(v)} |")
    L += ["", "## 4️⃣ 台股連結(隔日含義)", "", tw, "",
          "## 5️⃣ 個股觀察(風向球)", "", "| 股 | 價 | 日 | 週 | 月 |", "|---|--:|--:|--:|--:|"]
    for d, p, a, b, c in watch:
        L.append(f"| {d} | {p if p is not None else '—'} | {_arrow(a)} | {_arrow(b)} | {_arrow(c)} |")
    L += ["", f"- **NVDA 追蹤頁狀態**:{NVDA_TRACKER_STATUS}(詳見 `tech/nvda-bull-bear-tracker.md`)", "",
          "## 6️⃣ 今日觀察重點 + 紀律", "",
          f"- **當前環境(regime)**:{regime}",
          "- **紀律**:NVDA 是風向球,也是你 ~89% 的曝險。這份是研究,不是叫你加碼。RSU 照排程賣到 50%(`finance/05_equity_monetization_schedule`);BEAR 觸發看雲廠 capex / ASIC 推論佔比。",
          "- 早盤先看:台積電開盤量能、外資期貨、台幣匯率;美盤前看殖利率與當日數據/財報。", "",
          "---", "*研究/教育用途 — 非買賣建議。資料 yfinance(grade C),解讀為規則化邏輯。*"]
    return "\n".join(L)


def render_discord(date: str, macro: list, interp: list, rot: dict, tw: str, watch: list, regime: str) -> str:
    def row(d, p, a):
        return f"{d:<11}{(str(p) if p is not None else '—'):>10}  {_arrow(a)}"
    tape = "\n".join(row(d, p, a) for d, p, a, *_ in macro)
    w = "\n".join(row(d, p, a) for d, p, a, *_ in watch)
    parts = [f"🌅 **早晨財經速解讀 — {date}**  _(研究非建議)_", "",
             "**📊 開盤速覽**", "```", tape, "```",
             "**🧠 速解讀**"]
    parts += [f"• {x.replace('**','')}" for x in interp[:6]]
    parts += ["", f"**🔄 資金** 流入 {' · '.join(rot['inflow'])} ｜ 流出 {' · '.join(rot['outflow'])}",
              "", f"**🇹🇼 台股** {tw.replace('**','')}",
              "", "**🎯 風向球**", "```", w, "```",
              f"🧭 環境:{regime} ｜ 紀律:NVDA=風向球也是你89%曝險,RSU照排程賣到50%,別追高。"]
    return "\n".join(parts)


def render_html(date: str, macro: list, interp: list, rot: dict, tw: str, watch: list, regime: str) -> str:
    def cell(v):
        if v is None:
            return '<td class="n">—</td>'
        cls = "up" if v > 0 else ("dn" if v < 0 else "n")
        return f'<td class="{cls}">{v:+.2f}%</td>'
    def trows(rows):
        return "\n".join(
            f"<tr><td class='nm'>{d}</td><td class='px'>{p if p is not None else '—'}</td>"
            f"{cell(a)}{cell(b)}{cell(c)}</tr>" for d, p, a, b, c in rows)
    sect = "\n".join(f"<tr><td class='nm'>{k}</td>{cell(v)}</tr>" for k, v in rot["ranked"])
    interp_html = "".join(f"<li>{x.replace('**','')}</li>" for x in interp)
    return f"""<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>早晨財經速解讀 {date}</title><style>
:root{{color-scheme:dark}}
body{{font:15px/1.6 -apple-system,"Noto Sans TC",system-ui,sans-serif;background:#0d1117;color:#e6edf3;margin:0;padding:24px;max-width:900px;margin:0 auto}}
h1{{font-size:22px;border-bottom:2px solid #30363d;padding-bottom:10px}}
h2{{font-size:17px;margin-top:28px;color:#58a6ff}}
.sub{{color:#8b949e;font-size:13px;margin-top:-6px}}
table{{border-collapse:collapse;width:100%;margin:8px 0;font-variant-numeric:tabular-nums}}
td,th{{padding:6px 10px;border-bottom:1px solid #21262d;text-align:right}}
.nm{{text-align:left;color:#c9d1d9}}.px{{color:#8b949e}}
.up{{color:#3fb950}}.dn{{color:#f85149}}.n{{color:#8b949e}}
ul{{padding-left:20px}}li{{margin:4px 0}}
.box{{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:12px 16px;margin:10px 0}}
.tw{{border-left:3px solid #58a6ff}}
.foot{{color:#6e7681;font-size:12px;margin-top:24px;border-top:1px solid #21262d;padding-top:10px}}
</style></head><body>
<h1>🌅 早晨財經速解讀 — {date}</h1>
<p class="sub">仿游庭澔《早晨財經速解讀》結構:看盤 → 為什麼 → 類股 → 台股連結。研究/教育用途,非投資建議。</p>
<h2>1️⃣ 開盤速覽</h2>
<table><tr><th class='nm'>指標</th><th>收盤</th><th>日</th><th>週</th><th>月</th></tr>{trows(macro)}</table>
<h2>2️⃣ 速解讀(為什麼)</h2><ul>{interp_html}</ul>
<h2>3️⃣ 類股與資金流</h2>
<div class="box">資金流入 → <b>{' · '.join(rot['inflow'])}</b>　|　資金流出 → <b>{' · '.join(rot['outflow'])}</b></div>
<table><tr><th class='nm'>類股</th><th>日%</th></tr>{sect}</table>
<h2>4️⃣ 台股連結(隔日含義)</h2><div class="box tw">{tw.replace('**','')}</div>
<h2>5️⃣ 個股觀察(風向球)</h2>
<table><tr><th class='nm'>股</th><th>價</th><th>日</th><th>週</th><th>月</th></tr>{trows(watch)}</table>
<div class="box">NVDA 追蹤頁:{NVDA_TRACKER_STATUS}</div>
<h2>6️⃣ 今日觀察重點 + 紀律</h2>
<div class="box">環境(regime):<b>{regime}</b><br>紀律:NVDA 是風向球也是你 ~89% 的曝險;研究非加碼訊號。RSU 照排程賣到 50%,BEAR 觸發看雲廠 capex / ASIC 推論佔比。<br>早盤看:台積電量能、外資期貨、台幣匯率、當日數據/財報。</div>
<p class="foot">研究/教育用途 — 非買賣建議。資料 yfinance(grade C);解讀為規則化邏輯,非新聞事件查證。Generated by sharks.daily_brief.</p>
</body></html>"""


def main() -> int:
    import sys
    from datetime import datetime, timedelta, timezone
    from pathlib import Path
    tpe = timezone(timedelta(hours=8))
    date = datetime.now(tpe).strftime("%Y-%m-%d")

    all_t = list(dict.fromkeys(list(MACRO.values()) + list(SECTORS.values()) + list(WATCH.values())))
    moves = fetch_moves(all_t)

    macro = _named(moves, MACRO)
    watch = _named(moves, WATCH)
    interp = interpret_macro(moves)
    sect_moves = {disp: moves.get(t, {}).get("d1") for disp, t in SECTORS.items()}
    rot = sector_rotation(sect_moves)
    tw = tw_implication(moves)
    try:
        from sharks.scoring.valuation import current_environment
        ce = current_environment()
        regime = f"{ce['environment']} ({ce.get('classifier_label') or ce.get('source')})"
    except Exception:
        regime = "中性 (n/a)"

    md = render_md(date, macro, interp, rot, tw, watch, regime)
    html = render_html(date, macro, interp, rot, tw, watch, regime)
    disc = render_discord(date, macro, interp, rot, tw, watch, regime)

    out = Path("outputs")
    out.mkdir(parents=True, exist_ok=True)
    (out / f"daily-brief-{date}.md").write_text(md, encoding="utf-8")
    (out / f"daily-brief-{date}.html").write_text(html, encoding="utf-8")
    (out / f"daily-brief-{date}-discord.txt").write_text(disc, encoding="utf-8")
    print(f"wrote outputs/daily-brief-{date}.{{md,html,discord.txt}}  ({len(disc)} discord chars)", file=sys.stderr)
    print("\n===== MD PREVIEW =====\n" + md, file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

