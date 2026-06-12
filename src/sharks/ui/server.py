"""Sharks Web UI — 專屬 Finviz:點選式篩選 + 一鍵調研(本地單機,recommend-only).

不用 Streamlit:Starlette + uvicorn(venv 既有依賴)+ 原生 JS/ECharts 前端
(src/sharks/ui/static/)。設計原則:能點就不打字。

資料層:
  - 離線即時:data/lake → ma_scanner 全訊號掃描(篩選器資料一次下發,前端過濾零延遲)、
    K 線 + 均線 + RSI、info 快照(含 derived_fields_suspect 警示)
  - 點了才上網:yfinance 調研(現金流分布/營收/基本面/籌碼資金面)、湖刷新
  - 主題池掃描:basecross / rally / stealth / ecomrank(與 Discord /screen 同引擎,
    背景 job + 輪詢)

啟動:
    python -m sharks.ui.server [port]     # 預設 http://127.0.0.1:8787

recommend-only:本介面只做研究排序與調研呈現,永不下單(CLAUDE.md §2)。
"""

from __future__ import annotations

import json
import math
import re
import threading
import time
import uuid
import warnings
from dataclasses import asdict, is_dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[3]
STATIC_DIR = Path(__file__).resolve().parent / "static"
RESEARCH_TTL = 900           # 調研快取 15 分鐘(盤中數據本來就是快照)
CHART_BARS_DEFAULT = 260


# ── 序列化(numpy / NaN / dataclass → 瀏覽器可吃的 JSON)─────────────────────────

def jsonable(o):
    """遞迴轉成 json.dumps 安全值;NaN/Inf → None(裸 NaN 會讓瀏覽器 JSON.parse 爆掉)。"""
    if o is None or isinstance(o, (bool, int, str)):
        return o
    if isinstance(o, float):
        return None if (math.isnan(o) or math.isinf(o)) else o
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        v = float(o)
        return None if (math.isnan(v) or math.isinf(v)) else v
    if is_dataclass(o) and not isinstance(o, type):
        return jsonable(asdict(o))
    if isinstance(o, dict):
        return {str(k): jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple, set)):
        return [jsonable(x) for x in o]
    if isinstance(o, (pd.Timestamp, datetime)):
        return o.isoformat()
    if isinstance(o, pd.Series):
        return jsonable(o.tolist())
    return str(o)


# ── 財報抽取(yfinance statement DataFrame → {科目: {期末日: 值}})───────────────

CF_ROWS = {
    "operating": ["Operating Cash Flow", "Total Cash From Operating Activities",
                  "Cash Flow From Continuing Operating Activities"],
    "investing": ["Investing Cash Flow", "Total Cashflows From Investing Activities",
                  "Cash Flow From Continuing Investing Activities"],
    "financing": ["Financing Cash Flow", "Total Cash From Financing Activities",
                  "Cash Flow From Continuing Financing Activities"],
    "free_cash_flow": ["Free Cash Flow"],
    "capex": ["Capital Expenditure", "Capital Expenditures"],
}
IS_ROWS = {
    "revenue": ["Total Revenue", "Operating Revenue"],
    "gross_profit": ["Gross Profit"],
    "operating_income": ["Operating Income", "Total Operating Income As Reported"],
    "net_income": ["Net Income", "Net Income Common Stockholders"],
}


def statement_series(df, row_map: dict) -> dict:
    """yfinance 財報(row=科目, col=期末日)→ {key: {ISO日期: float|None}}。
    科目名稱跨 yfinance 版本不穩,row_map 的每個 key 給一串候選 label,取第一個命中。"""
    out = {k: {} for k in row_map}
    if df is None or getattr(df, "empty", True):
        return out
    for key, labels in row_map.items():
        for lb in labels:
            if lb in df.index:
                row = df.loc[lb]
                if isinstance(row, pd.DataFrame):       # 重複 label 防衛
                    row = row.iloc[0]
                series = {}
                for c, v in row.items():
                    p = str(c.date()) if isinstance(c, (pd.Timestamp, datetime)) else str(c)
                    series[p] = None if pd.isna(v) else float(v)
                out[key] = series
                break
    return out


def us_market_open() -> bool:
    """美股是否盤中(近似:3–10 月當 EDT=UTC-4,其餘 EST=UTC-5;不處理假日)。
    只拿來給「盤中快照,非 EOD」徽章用,不參與任何訊號計算。"""
    now = datetime.now(timezone.utc)
    et = now + timedelta(hours=(-4 if 3 <= now.month <= 10 else -5))
    return et.weekday() < 5 and (9, 30) <= (et.hour, et.minute) < (16, 0)


# ── 掃描快取(573 檔離線掃 ~2s;一次下發,前端過濾零延遲)───────────────────────

_scan_lock = threading.Lock()
_scan_cache: dict = {"report": None, "ts": 0.0}


def get_scan(force: bool = False) -> dict:
    from sharks.scoring import ma_scanner
    with _scan_lock:
        if force or _scan_cache["report"] is None:
            _scan_cache["report"] = ma_scanner.scan_lake()
            _scan_cache["ts"] = time.time()
        return _scan_cache["report"]


_research_cache: dict[str, tuple[float, dict]] = {}


def fetch_research(ticker: str, fresh: bool = False) -> dict:
    """一鍵調研:現金流分布 + 營收 + 基本面 + 資金面(yfinance 即時,lake 退路)。"""
    hit = _research_cache.get(ticker)
    if hit and not fresh and time.time() - hit[0] < RESEARCH_TTL:
        return hit[1]

    from sharks.data.data_lake import lint_info_fields, load_info
    from sharks.scoring.deep_research import (BUFFETT_3M_DETAILED, chip_flow_summary,
                                              fundamental_analysis)
    info, source, stmts = {}, "yfinance-live", {}
    try:
        import yfinance as yf
        tk = yf.Ticker(ticker)
        info = tk.info or {}
        for attr in ("cashflow", "quarterly_cashflow", "income_stmt", "quarterly_income_stmt"):
            try:
                stmts[attr] = getattr(tk, attr)
            except Exception:
                stmts[attr] = None
    except Exception:
        pass
    if not (info.get("symbol") or info.get("shortName")):
        info, source = load_info(ticker), "lake-snapshot"

    suspect = lint_info_fields(info)
    data = jsonable({
        "ticker": ticker,
        "source": source,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "name": info.get("shortName") or info.get("longName"),
        "sector": info.get("sector"), "industry": info.get("industry"),
        "price": info.get("currentPrice") or info.get("regularMarketPrice"),
        "fifty_two_wk_high": info.get("fiftyTwoWeekHigh"),
        "fifty_two_wk_low": info.get("fiftyTwoWeekLow"),
        "derived_fields_suspect_reasons": suspect,   # EUR/ADR 換算汙染警示(data_lake lint)
        "fundamentals": fundamental_analysis(info),
        "chip_flow": chip_flow_summary(info),
        "cashflow": {"annual": statement_series(stmts.get("cashflow"), CF_ROWS),
                     "quarterly": statement_series(stmts.get("quarterly_cashflow"), CF_ROWS)},
        "income": {"annual": statement_series(stmts.get("income_stmt"), IS_ROWS),
                   "quarterly": statement_series(stmts.get("quarterly_income_stmt"), IS_ROWS)},
        "moat": BUFFETT_3M_DETAILED.get(ticker),
        "earnings_date": info.get("earningsTimestamp") and str(
            datetime.fromtimestamp(info["earningsTimestamp"], tz=timezone.utc).date()),
    })
    _research_cache[ticker] = (time.time(), data)
    return data


def chart_payload(ticker: str, bars: int = CHART_BARS_DEFAULT) -> dict | None:
    """lake K 線 + MA5/20/60/200 + RSI(離線、即時)。"""
    from sharks.scoring import ma_scanner
    df = ma_scanner.load_lake_prices(ticker)
    if df is None or df.empty or "Close" not in df:
        return None
    close = df["Close"]
    ind = pd.DataFrame({
        "ma5": close.rolling(5).mean(), "ma20": close.rolling(20).mean(),
        "ma60": close.rolling(60).mean(), "ma200": close.rolling(200).mean(),
        "rsi": ma_scanner.rsi(close),
    })
    tail, it = df.tail(bars), ind.tail(bars)

    def col(s, nd=2):
        return [None if pd.isna(v) else round(float(v), nd) for v in s]

    return {
        "ticker": ticker,
        "dates": [str(i.date()) if hasattr(i, "date") else str(i) for i in tail.index],
        "open": col(tail["Open"]), "high": col(tail["High"]),
        "low": col(tail["Low"]), "close": col(tail["Close"]),
        "volume": [0 if pd.isna(v) else int(v) for v in tail.get("Volume", pd.Series(0, index=tail.index))],
        "ma5": col(it["ma5"]), "ma20": col(it["ma20"]),
        "ma60": col(it["ma60"]), "ma200": col(it["ma200"]),
        "rsi": col(it["rsi"], 1),
    }


def rally_history(ticker: str, n_files: int = 12) -> list[dict]:
    """近 N 份 rally-state-*.jsonl 中該 ticker 的 streak 軌跡(防衛式解析)。"""
    out = []
    for f in sorted((PROJECT_ROOT / "outputs").glob("rally-state-*.jsonl"))[-n_files:]:
        try:
            for ln in f.read_text(encoding="utf-8").splitlines():
                d = json.loads(ln)
                if d.get("ticker") == ticker:
                    out.append({"date": f.stem.replace("rally-state-", ""),
                                **{k: d.get(k) for k in ("streak", "composite", "dna_match",
                                                         "buy_consider", "conviction", "has_fuel")}})
                    break
        except Exception:
            continue
    return out


# ── 持股健檢(audit verdict × 離線技術訊號 × rally streak → 建議動作)──────────────
# recommend-only:輸出是研究建議(續抱/減碼/換股/清倉),執行永遠是人的動作。

def latest_output_json(prefix: str) -> dict:
    files = sorted(p for p in (PROJECT_ROOT / "outputs").glob(f"{prefix}-*.json")
                   if not p.name.endswith(".bak"))
    if not files:
        return {}
    try:
        return json.loads(files[-1].read_text(encoding="utf-8"))
    except Exception:
        return {}


def latest_rally_streaks() -> dict[str, dict]:
    files = sorted((PROJECT_ROOT / "outputs").glob("rally-state-*.jsonl"))
    out: dict[str, dict] = {}
    if not files:
        return out
    try:
        for ln in files[-1].read_text(encoding="utf-8").splitlines():
            d = json.loads(ln)
            if d.get("ticker"):
                out[d["ticker"]] = {"streak": d.get("streak"), "composite": d.get("composite"),
                                    "buy_consider": d.get("buy_consider")}
    except Exception:
        pass
    return out


def swap_candidates(sector: str | None, scan_rows: dict, exclude: set, n: int = 3) -> list[dict]:
    """同板塊換股候選:乾淨趨勢結構(連線+騎線+無拒絕棒+站上MA50),依距 52w 高排序。
    研究排序,非買訊 — 進場仍走燃料閘+連續起漲+regime。"""
    cands = [(t, r) for t, r in scan_rows.items()
             if t not in exclude
             and (sector is None or r.get("sector") == sector)
             and r.get("aligned") and r.get("riding")
             and not r.get("rejection_bar") and r.get("above_ma50")]
    cands.sort(key=lambda kv: kv[1].get("dist_52w_high_pct") if kv[1].get("dist_52w_high_pct") is not None else -999,
               reverse=True)
    return [{"ticker": t, "sector": r.get("sector"),
             "dist_52w_high_pct": r.get("dist_52w_high_pct"), "rsi": r.get("rsi"),
             "why": "連線+騎線+無拒絕棒"} for t, r in cands[:n]]


def health_action(holding: dict, audit_row: dict | None, scan_row: dict | None,
                  rally: dict | None) -> dict:
    """單檔健檢決策(純函式,供測試)。動作 ∈ 待驗證/清倉/換股/減碼/續抱⚠/續抱。"""
    a = audit_row or {}
    verdict = str(a.get("reviewed_verdict") or a.get("verdict") or "")
    lev_of = holding.get("leveraged_of")
    name = holding.get("name", "")
    reasons: list[str] = []
    swap_to_underlying = False

    mv = holding.get("mkt_val")
    if mv is not None and float(mv) <= 1.0 and holding.get("shares"):
        return {"action": "清倉", "swap_to_underlying": False, "reasons":
                ["市值歸零(破產/下市殼)— 稅損收割候選,於 NVDA 大額賣出年度同年實現"
                 "(見 portfolio/04_long_range_tax_plan)"]}
    if "TBD" in name or "待驗證" in name or "待確認" in name:
        action = "待驗證"
        reasons.append("代號/標的未解碼或為截斷列推定 — 先補資訊再談操作")
    elif verdict.startswith("SELL"):
        if lev_of:
            action = "換股"
            swap_to_underlying = True
            lev = (a.get("leveraged_scorer") or {})
            decay = lev.get("annual_decay_pct")
            reasons.append(f"audit SELL:槓桿 ETF 結構性 decay{f' ~{decay}%/年' if decay else ''}"
                           f" → 換現股 {lev_of} 同曝險零 decay")
        else:
            action = "換股"
            reasons.append(f"audit SELL:{str(a.get('rationale') or '')[:80]}")
    elif verdict.startswith("TRIM"):
        action = "減碼"
        reasons.append(f"audit {verdict}:部分去風險、其餘移動停利")
        if a.get("review", {}).get("flips_to_sell_when"):
            reasons.append(f"翻空條件:{a['review']['flips_to_sell_when'][:80]}")
    else:
        action = "續抱"
        if verdict:
            reasons.append(f"audit {verdict}:{str(a.get('rationale') or '')[:60]}")

    # 離線技術訊號 overlay(只升警示,不改硬裁決)
    if scan_row:
        if action == "續抱":
            if scan_row.get("rejection_bar"):
                action = "續抱⚠"
                reasons.append("最後一根為拒絕棒(收盤距日高 >3%)— 移動停利收緊")
            rsi = scan_row.get("rsi")
            if rsi is not None and rsi > 78:
                action = "續抱⚠"
                reasons.append(f"RSI {rsi} 過熱 — 別加碼,守停利")
            if scan_row.get("above_ma50") is False:
                action = "續抱⚠"
                reasons.append("跌破 MA50 — 趨勢結構轉弱")
        if scan_row.get("aligned") and scan_row.get("riding") and not scan_row.get("rejection_bar"):
            reasons.append("技術面:連線+騎線,趨勢結構完好")
    elif action in ("續抱", "續抱⚠"):
        reasons.append("不在 lake(調研頁可按「刷新此檔」補數據)")

    if rally and rally.get("streak"):
        reasons.append(f"rally streak={rally['streak']}" +
                       ("(buy_consider)" if rally.get("buy_consider") else ""))

    return {"action": action, "reasons": reasons, "swap_to_underlying": swap_to_underlying}


def holdings_health(book: str = "all") -> dict:
    """持倉健檢:P1/P2/全部 × 最新 audit × 離線掃描 × rally streak。"""
    from sharks.backtest.portfolio_audit import PORTFOLIO_1, PORTFOLIO_2
    holdings: dict[str, dict] = {}
    if book in ("p1", "all"):
        holdings.update({t: {**h, "book": "P1"} for t, h in PORTFOLIO_1.items()})
    if book in ("p2", "all"):
        for t, h in PORTFOLIO_2.items():
            if t in holdings:   # 同名跨帳本(目前無,防衛)
                holdings[t]["book"] = "P1+P2"
            else:
                holdings[t] = {**h, "book": "P2"}
    audit = latest_output_json("portfolio-audit")
    audit_by_t = {r.get("ticker"): r for r in
                  (audit.get("portfolio_1_audit") or []) + (audit.get("portfolio_2_audit") or [])}
    scan = get_scan()
    rows, streaks = scan.get("rows", {}), latest_rally_streaks()
    held = set(PORTFOLIO_1) | set(PORTFOLIO_2)

    out_rows, total = [], 0.0
    lev_val = 0.0
    for t, h in holdings.items():
        ar, sr = audit_by_t.get(t), rows.get(t)
        res = health_action(h, ar, sr, streaks.get(t))
        swaps = []
        if res["swap_to_underlying"] and h.get("leveraged_of"):
            u = h["leveraged_of"]
            ur = rows.get(u) or {}
            swaps.append({"ticker": u, "sector": ur.get("sector"),
                          "dist_52w_high_pct": ur.get("dist_52w_high_pct"), "rsi": ur.get("rsi"),
                          "why": "去槓桿同曝險(現股)"})
        if res["action"] == "換股":
            sector = (sr or {}).get("sector") or ((rows.get(h.get("leveraged_of") or "") or {}).get("sector"))
            swaps += swap_candidates(sector, rows, held | {s["ticker"] for s in swaps})
        mv = float(h.get("mkt_val") or 0)
        total += mv
        if h.get("leveraged_of"):
            lev_val += mv
        out_rows.append({
            "ticker": t, "book": h.get("book"), "name": h.get("name"),
            "pct": h.get("pct"), "mkt_val": h.get("mkt_val"),
            "leveraged_of": h.get("leveraged_of"),
            "audit_verdict": (ar or {}).get("reviewed_verdict") or (ar or {}).get("verdict"),
            "fom": ((ar or {}).get("fom_breakdown") or {}).get("final_fom"),
            "day_signals": {k: (sr or {}).get(k) for k in
                            ("close", "dist_52w_high_pct", "rsi", "aligned", "riding",
                             "rejection_bar", "above_ma50")} if sr else None,
            "rally": streaks.get(t),
            "action": res["action"], "reasons": res["reasons"], "swaps": swaps,
        })

    order = {"清倉": 0, "換股": 1, "減碼": 2, "待驗證": 3, "續抱⚠": 4, "續抱": 5}
    out_rows.sort(key=lambda r: (order.get(r["action"], 9), -(r.get("mkt_val") or 0)))
    actions: dict[str, int] = {}
    for r in out_rows:
        actions[r["action"]] = actions.get(r["action"], 0) + 1
    return jsonable({
        "book": book,
        "as_of_scan": scan.get("as_of"),
        "as_of_audit": audit.get("as_of"),
        "audit_file_basis": str(audit.get("as_of") or "")[:10] or None,
        "total_visible_usd": round(total, 2),
        "leveraged_pct": round(lev_val / total * 100, 1) if total else None,
        "action_counts": actions,
        "rows": out_rows,
        "disclaimer": "recommend-only 健檢;換股候選是研究排序非買訊 — 進場仍走 燃料閘+連續起漲+regime,永不下單。",
    })


# ── 全球風險面板(world-monitor + ABM 供應鏈 → /api/world)──────────────────────
# recommend-only:事件/指標是篩選與微調輸入,非倉位指令(同 world-monitor 輸出免責)。

WORLD_DISCLAIMER = "recommend-only;事件=篩選/微調輸入,非倉位指令。"

# 展示用閾值錨點 — 與 config/world_events.json 的 _basis 一致(分位數定錨,非擬合):
#   GSCPI 本身即 NY Fed z-score → 尖峰線 1.5σ;GPR 月度 1985+ p95=169;GPRC_TWN p95=0.25。
WORLD_THRESHOLDS = {"gscpi_spike": 1.5, "gpr_p95": 169.0, "gprc_twn_p95": 0.25}


def _latest_json_file(outputs_dir: Path, prefix: str) -> tuple[Path | None, dict | None]:
    """最新 outputs/<prefix>-*.json(sorted-glob-last;排除 .bak 與 -intraday 快照)。
    無檔 → (None, None);壞檔 → (path, None) — 呼叫端一律優雅降級。"""
    files = sorted(p for p in outputs_dir.glob(f"{prefix}-*.json")
                   if not p.name.endswith(".bak") and "intraday" not in p.name)
    if not files:
        return None, None
    try:
        d = json.loads(files[-1].read_text(encoding="utf-8"))
        return files[-1], (d if isinstance(d, dict) else None)
    except Exception:
        return files[-1], None


def _abm_compact(d: dict | None) -> dict | None:
    """ABM 供應鏈輸出 → 面板摘要。引擎由 sibling 任務開發、schema 未定 → 防衛式抽取:
    找含 survival 的數值欄(優先 survival+delta 命名,深至 3 層);抽不到 → None,不發明值。"""
    if not isinstance(d, dict):
        return None

    def _num(v):
        return v if isinstance(v, (int, float)) and not isinstance(v, bool) else None

    def scan(obj, want_delta: bool, depth: int = 0):
        if depth > 3 or not isinstance(obj, dict):
            return None, None
        for k, v in obj.items():
            kl = str(k).lower()
            if "survival" in kl and (("delta" in kl or "diff" in kl) if want_delta else True) \
                    and _num(v) is not None:
                return str(k), v
        for v in obj.values():
            key, val = scan(v, want_delta, depth + 1)
            if key is not None:
                return key, val
        return None, None

    key, val = scan(d, want_delta=True)
    if key is None:
        key, val = scan(d, want_delta=False)
    return {
        "as_of": d.get("as_of"),
        "generated_at": d.get("generated_at") or d.get("retrieved_at"),
        "survival_delta": val,
        "survival_delta_field": key,    # 抽到的欄名(前端 tooltip 用,debug 友善)
        "scenario": d.get("scenario") or d.get("event") or d.get("geopolitical_event"),
    }


def _num_or_none(v):
    """數值守門:bool 不算數(observe-first,缺值→None,永不發明)。"""
    return v if isinstance(v, (int, float)) and not isinstance(v, bool) else None


def _behavioral_compact(wm: dict | None) -> dict | None:
    """world-monitor behavioral 區塊 → 面板摘要(score/mania_note/regime_state)。
    無區塊或形狀不對 → None,面板不渲染該行。"""
    b = (wm or {}).get("behavioral") if isinstance(wm, dict) else None
    if not isinstance(b, dict):
        return None
    return {
        "score": _num_or_none(b.get("score")),
        "mania_note": b.get("mania_note"),
        "regime_state": b.get("regime_state"),
    }


def _outlook_compact(rt: dict | None) -> dict | None:
    """regime-transitions current_outlook → 面板摘要(次月四態機率 + 條件層級 + 樣本數)。
    observe-first:展示用,不 gate KPI、不進 sizing。"""
    o = rt.get("current_outlook") if isinstance(rt, dict) else None
    if not isinstance(o, dict):
        return None
    probs = o.get("next_month_probs")
    return {
        "current_state": o.get("current_state"),
        "used_level": o.get("used_level"),
        "n": _num_or_none(o.get("n")),
        "low_n": o.get("low_n") if isinstance(o.get("low_n"), bool) else None,
        "next_month_probs": ({k: _num_or_none(probs.get(k))
                              for k in ("bull", "mania", "bear", "crisis")}
                             if isinstance(probs, dict) else None),
    }


def _history_lens_compact(bf: dict | None) -> dict | None:
    """world-backfill event_forward_study → 面板一行摘要:
    GSCPI_SPIKE 後 3m/6m 前瞻中位數 vs 全樣本基準率(僅中位數;表格之外不做因果宣稱)。"""
    study = bf.get("event_forward_study") if isinstance(bf, dict) else None
    if not isinstance(study, dict):
        return None

    def med(block, horizon: str):
        fwd = block.get("fwd") if isinstance(block, dict) else None
        cell = fwd.get(horizon) if isinstance(fwd, dict) else None
        return _num_or_none(cell.get("median_pct")) if isinstance(cell, dict) else None

    base = study.get("base_rate")
    spike = (study.get("events") or {}).get("GSCPI_SPIKE") \
        if isinstance(study.get("events"), dict) else None
    out = {
        "event": "GSCPI_SPIKE",
        "event_3m": med(spike, "3m"), "event_6m": med(spike, "6m"),
        "base_3m": med(base, "3m"), "base_6m": med(base, "6m"),
    }
    if all(out[k] is None for k in ("event_3m", "event_6m", "base_3m", "base_6m")):
        return None     # 四格全空 → 整段降級,面板不渲染
    return out


def world_panel(outputs_dir: Path | None = None) -> dict:
    """/api/world 載荷:最新 world-monitor 摘要 + ABM 生存差 + 行為偏差/態轉移展望/
    歷史鏡頭(各來源獨立 sorted-glob-last;任一缺檔 → 該段 null,優雅降級)。"""
    out_dir = outputs_dir if outputs_dir is not None else PROJECT_ROOT / "outputs"
    wm_path, wm = _latest_json_file(out_dir, "world-monitor")
    _, abm = _latest_json_file(out_dir, "abm-supply-chain")
    _, rt = _latest_json_file(out_dir, "regime-transitions")
    _, bf = _latest_json_file(out_dir, "world-backfill")
    extras = {
        "behavioral": _behavioral_compact(wm),
        "outlook": _outlook_compact(rt),
        "history_lens": _history_lens_compact(bf),
    }
    if wm is None:
        return {"available": False, "file": wm_path.name if wm_path else None,
                "abm": _abm_compact(abm), **extras, "disclaimer": WORLD_DISCLAIMER}
    metrics = wm.get("metrics") or {}
    impacts = wm.get("impacts") or {}
    return {
        "available": True,
        "file": wm_path.name,
        "retrieved_at": wm.get("retrieved_at"),
        "as_of": wm.get("as_of"),
        "stale_sources": wm.get("stale_sources") or [],
        "events_triggered": [{"id": e.get("id"), "name": e.get("name"),
                              "category": e.get("category"), "severity": e.get("severity")}
                             for e in (wm.get("events_triggered") or [])
                             if isinstance(e, dict)],
        "metrics": {k: metrics.get(k) for k in ("gscpi", "gpr", "gprc_twn", "gprc_twn_z60")},
        "impacts": {"deepkill_cap_multiplier": impacts.get("deepkill_cap_multiplier"),
                    "exposure_penalty": impacts.get("exposure_penalty"),
                    "review_groups": impacts.get("review_groups") or []},
        "thresholds": WORLD_THRESHOLDS,
        "abm": _abm_compact(abm),
        **extras,
        "disclaimer": wm.get("disclaimer") or WORLD_DISCLAIMER,
    }


# ── 背景 jobs(主題池掃描要打 yfinance,分鐘級 → 不能卡 request)────────────────

JOBS: dict[str, dict] = {}


def submit_job(label: str, fn) -> str:
    jid = uuid.uuid4().hex[:8]
    JOBS[jid] = {"id": jid, "label": label, "status": "running",
                 "started": datetime.now(timezone.utc).isoformat(),
                 "result": None, "error": None, "finished": None}

    def run():
        try:
            JOBS[jid]["result"] = fn()
            JOBS[jid]["status"] = "done"
        except Exception as e:
            JOBS[jid]["error"] = f"{type(e).__name__}: {e}"
            JOBS[jid]["status"] = "error"
        JOBS[jid]["finished"] = datetime.now(timezone.utc).isoformat()

    threading.Thread(target=run, daemon=True, name=f"job-{label}-{jid}").start()
    return jid


def run_screen(kind: str, scope: str, extra: list[str] | None) -> dict:
    """Discord /basecross /rally /stealth /ecomrank 同款流程(recommend-only)。"""
    from sharks.discord import basecross as _bc
    from sharks.discord.config import Settings
    from sharks.scoring import rally_signal as _rally
    from sharks.scoring import stealth_signal as _stealth
    settings = Settings.load()
    title, rows = _bc.run_basecross(scope, settings=settings, extra_tickers=extra or None)
    quality = _bc.quality_from_fom(settings.outputs_dir)
    if kind == "rally":
        prior = _rally.load_prior_streaks(settings.outputs_dir)
        payload = _rally.build_signals(rows, quality_by_ticker=quality, prior_streaks=prior)
        _rally.write_state(settings.outputs_dir, payload)
    elif kind == "stealth":
        payload = _stealth.stealth_rank(rows)
    elif kind == "ecomrank":
        payload = _rally.ecommerce_rank(rows, quality_by_ticker=quality)
    else:
        payload = rows
    return {"kind": kind, "title": f"{kind} · {title}", "rows": jsonable(payload)}


def refresh_lake_and_rescan() -> dict:
    """刷新湖內全部 1d K(8 執行緒,~15s/573 檔)→ 重掃。盤中跑會拿到 partial bar,
    回傳 intraday 旗標讓前端掛「盤中快照,非 EOD」徽章。"""
    from concurrent.futures import ThreadPoolExecutor
    from sharks.data.data_lake import store_prices
    from sharks.scoring import ma_scanner
    tks = ma_scanner.lake_tickers()
    errors = []
    with ThreadPoolExecutor(max_workers=8) as ex:
        for r in ex.map(lambda t: store_prices(t, "5y", "1d"), tks):
            if "error" in r or r.get("status") == "no_data":
                errors.append(r.get("ticker"))
    rep = get_scan(force=True)
    return {"refreshed": len(tks), "errors": errors[:20], "n_errors": len(errors),
            "as_of": rep.get("as_of"), "intraday": us_market_open()}


def refresh_one_ticker(ticker: str) -> dict:
    """單檔刷新:價格 + info → 重算該檔訊號 row,patch 進掃描快取。"""
    from sharks.data.data_lake import store_info, store_prices
    from sharks.scoring import ma_scanner
    store_prices(ticker, "5y", "1d")
    info_res = store_info(ticker)
    _research_cache.pop(ticker, None)
    sig = ma_scanner.scan_one(ma_scanner.load_lake_prices(ticker))
    if sig:
        sig["sector"] = ma_scanner.load_sector(ticker)
        with _scan_lock:
            if _scan_cache["report"]:
                _scan_cache["report"]["rows"][ticker] = sig
    return {"ticker": ticker, "row": jsonable(sig),
            "derived_fields_suspect": info_res.get("derived_fields_suspect"),
            "intraday": us_market_open()}


# ── 今日推薦來源(canonical wiki 日度 10-signal 優先;舊 outputs/daily-reco-* fallback)──

_DAILY_NAME = re.compile(r"\A\d{4}-\d{2}-\d{2}\.md\Z")
_LEGACY_NAME = re.compile(r"\Adaily-reco-(\d{4}-\d{2}-\d{2})\.md\Z")
_FRONTMATTER = re.compile(r"\A---\r?\n.*?\r?\n---\r?\n", re.S)


def latest_reco_file(root: Path = PROJECT_ROOT) -> Path | None:
    """最新日度推薦:wiki/05_recommendations/YYYY-MM-DD.md(canonical 10-signal)與
    outputs/daily-reco-YYYY-MM-DD.md(舊 ad-hoc 家族,無產生器)取日期最大者;
    同日 canonical 優先。非日度命名(README/archive/專題頁)不參賽。"""
    cands: list[tuple[str, int, str, Path]] = []
    for p in (root / "wiki" / "05_recommendations").glob("*.md"):
        if _DAILY_NAME.match(p.name):
            cands.append((p.stem, 1, p.name, p))
    for p in (root / "outputs").glob("daily-reco-*.md"):
        m = _LEGACY_NAME.match(p.name)
        if m:
            cands.append((m.group(1), 0, p.name, p))
    if not cands:
        return None
    return max(cands)[3]


def strip_frontmatter(md: str) -> str:
    """去掉 YAML frontmatter — marked 會把 --- 區塊渲染成水平線+裸文字。"""
    return _FRONTMATTER.sub("", md, count=1)


# ── HTTP 層(async 端點 + run_in_threadpool 包阻塞工作)─────────────────────────

def build_app():
    from starlette.applications import Starlette
    from starlette.concurrency import run_in_threadpool
    from starlette.responses import FileResponse, JSONResponse, PlainTextResponse
    from starlette.routing import Mount, Route
    from starlette.staticfiles import StaticFiles

    async def index(request):
        return FileResponse(STATIC_DIR / "index.html")

    async def api_meta(request):
        from sharks.discord.basecross import SCOPES, scope_universe
        from sharks.scoring import ma_scanner
        tickers = await run_in_threadpool(ma_scanner.lake_tickers)
        scopes = [{"value": s, "name": scope_universe(s)[0]} for s in SCOPES]
        return JSONResponse({"tickers": tickers, "scopes": scopes,
                             "intraday": us_market_open(),
                             "disclaimer": "recommend-only 研究排序;進場仍走 燃料閘+連續起漲+regime,永不下單。"})

    async def api_scan(request):
        force = request.query_params.get("refresh") == "1"
        rep = await run_in_threadpool(get_scan, force)
        return JSONResponse({**jsonable(rep), "intraday": us_market_open()})

    async def api_chart(request):
        t = request.path_params["ticker"].upper()
        bars = int(request.query_params.get("bars", CHART_BARS_DEFAULT))
        data = await run_in_threadpool(chart_payload, t, bars)
        if data is None:
            return JSONResponse({"error": f"{t} 不在 lake(可先在調研頁按「刷新此檔」)"}, status_code=404)
        return JSONResponse(data)

    async def api_research(request):
        t = request.path_params["ticker"].upper()
        fresh = request.query_params.get("fresh") == "1"
        return JSONResponse(await run_in_threadpool(fetch_research, t, fresh))

    async def api_local(request):
        t = request.path_params["ticker"].upper()
        rep = await run_in_threadpool(get_scan, False)
        hist = await run_in_threadpool(rally_history, t)
        return JSONResponse(jsonable({"ticker": t, "scan_row": rep["rows"].get(t),
                                      "as_of": rep.get("as_of"), "rally_history": hist}))

    async def api_ticker_refresh(request):
        t = request.path_params["ticker"].upper()
        return JSONResponse(await run_in_threadpool(refresh_one_ticker, t))

    async def api_job_create(request):
        body = await request.json()
        action = body.get("action", "screen")
        if action == "lake_refresh":
            jid = submit_job("lake_refresh", refresh_lake_and_rescan)
        else:
            kind = body.get("kind", "basecross")
            scope = body.get("scope", "all")
            extra = [s.strip().upper() for s in (body.get("extra") or []) if s.strip()]
            if kind not in ("basecross", "rally", "stealth", "ecomrank"):
                return JSONResponse({"error": f"unknown kind {kind}"}, status_code=400)
            jid = submit_job(f"{kind}:{scope}", lambda: run_screen(kind, scope, extra))
        return JSONResponse({"id": jid})

    async def api_job_get(request):
        job = JOBS.get(request.path_params["job_id"])
        if not job:
            return JSONResponse({"error": "no such job"}, status_code=404)
        return JSONResponse(job)

    async def api_health(request):
        book = request.query_params.get("book", "all")
        if book not in ("p1", "p2", "all"):
            book = "all"
        return JSONResponse(await run_in_threadpool(holdings_health, book))

    async def api_world(request):
        return JSONResponse(jsonable(await run_in_threadpool(world_panel)))

    async def api_reco(request):
        f = latest_reco_file()
        if f is None:
            return PlainTextResponse("(還沒有日度推薦輸出)")
        return PlainTextResponse(strip_frontmatter(f.read_text(encoding="utf-8")))

    return Starlette(routes=[
        Route("/", index),
        Route("/api/meta", api_meta),
        Route("/api/scan", api_scan),
        Route("/api/ticker/{ticker}/chart", api_chart),
        Route("/api/ticker/{ticker}/research", api_research),
        Route("/api/ticker/{ticker}/local", api_local),
        Route("/api/ticker/{ticker}/refresh", api_ticker_refresh, methods=["POST"]),
        Route("/api/jobs", api_job_create, methods=["POST"]),
        Route("/api/jobs/{job_id}", api_job_get),
        Route("/api/holdings/health", api_health),
        Route("/api/world", api_world),
        Route("/api/reco", api_reco),
        Mount("/static", app=StaticFiles(directory=str(STATIC_DIR)), name="static"),
    ])


def main(argv: list[str] | None = None) -> int:
    import os
    import sys
    os.chdir(PROJECT_ROOT)        # lake/outputs 的相對路徑都以 repo root 為基準
    args = sys.argv[1:] if argv is None else argv
    port = int(args[0]) if args else 8787
    import uvicorn
    print(f"Sharks UI -> http://127.0.0.1:{port}  (recommend-only; Ctrl+C to stop)")
    uvicorn.run(build_app(), host="127.0.0.1", port=port, log_level="warning")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
