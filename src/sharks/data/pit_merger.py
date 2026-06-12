"""PIT 合併器 — Polygon(filing_date 錨點)× yfinance 季表(FCF/CapEx 補課).

架構層:Data Layer(v3 藍圖 §1)。Polygon 標準化現金流表沒有 CapEx 細項 →
FCF 從 yfinance 季表回填(僅 ~6 季深度),按 end_date ±10 天對齊;每個值帶
`fcf_source` 標籤(polygon/yfinance/None)— 可審計性優先,缺值誠實留 None。

輸出列 schema(dict;欄位穩定,下游當資料模型用):
    fiscal, end_date, filing_date, revenue, rev_yoy_pct, ocf, capex, fcf,
    fcf_source, fcf_positive, ocf_improving_yoy

CLI:
    python -m sharks.data.pit_merger HUM COHR        # → outputs/pit-merged-<date>.json
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import pandas as pd

MATCH_TOL_DAYS = 10      # Polygon end_date 與 yfinance 欄位日期的對齊容忍


def yf_quarterly_cash(ticker: str) -> dict[str, dict]:
    """yfinance 季現金流 → {end_date_iso: {capex, fcf}}(僅 ~6 季,誠實限制)。"""
    try:
        import yfinance as yf
        cf = yf.Ticker(ticker).quarterly_cashflow
        if cf is None or cf.empty:
            return {}
        out = {}
        for c in cf.columns:
            key = str(pd.Timestamp(c).date())
            row = {}
            for label, k in (("Capital Expenditure", "capex"), ("Free Cash Flow", "fcf")):
                if label in cf.index and pd.notna(cf.loc[label, c]):
                    row[k] = float(cf.loc[label, c])
            if row:
                out[key] = row
        return out
    except Exception:
        return {}


def _nearest(end_date: Optional[str], pool: dict[str, dict]) -> Optional[dict]:
    if not end_date or not pool:
        return None
    target = pd.Timestamp(end_date)
    best, best_d = None, MATCH_TOL_DAYS + 1
    for k, v in pool.items():
        d = abs((pd.Timestamp(k) - target).days)
        if d < best_d:
            best, best_d = v, d
    return best


def merge_rows(polygon_rows: list[dict], yf_cash: dict[str, dict]) -> list[dict]:
    """Polygon 季列(新→舊,with_yoy 後)× yfinance 現金 → 統一 PIT 列。純函式。"""
    out = []
    for r in polygon_rows:
        fcf, fcf_src, capex = r.get("fcf"), None, r.get("capex")
        if fcf is not None:
            fcf_src = "polygon"
        else:
            hit = _nearest(r.get("end_date"), yf_cash)
            if hit:
                fcf = hit.get("fcf", fcf)
                capex = capex if capex is not None else hit.get("capex")
                if fcf is not None:
                    fcf_src = "yfinance"
        prior = None
        for cand in polygon_rows:
            if cand is r:
                continue
            if cand.get("fiscal", "")[:4].isdigit() and r.get("fiscal", "")[:4].isdigit() \
               and cand.get("fiscal", "")[4:] == r.get("fiscal", "")[4:] \
               and int(cand["fiscal"][:4]) == int(r["fiscal"][:4]) - 1:
                prior = cand
                break
        ocf_imp = (None if prior is None or r.get("ocf") is None or prior.get("ocf") is None
                   else bool(r["ocf"] > prior["ocf"]))
        out.append({"fiscal": r.get("fiscal"), "end_date": r.get("end_date"),
                    "filing_date": r.get("filing_date"),
                    "revenue": r.get("revenue"), "rev_yoy_pct": r.get("rev_yoy_pct"),
                    "ocf": r.get("ocf"), "capex": capex, "fcf": fcf, "fcf_source": fcf_src,
                    "fcf_positive": (None if fcf is None else bool(fcf > 0)),
                    "ocf_improving_yoy": ocf_imp})
    return out


def pit_contested(rows: list[dict]) -> Optional[bool]:
    """「PIT 翻案爭議」判定:最新季營收 YoY > 0 且 OCF 同季 YoY 改善 →
    年度面的負面讀數(如 FCF YoY 深負)可能被季節性污染 — 交 human_review。"""
    if not rows:
        return None
    latest = rows[0]
    if latest.get("rev_yoy_pct") is None or latest.get("ocf_improving_yoy") is None:
        return None
    return bool(latest["rev_yoy_pct"] > 0 and latest["ocf_improving_yoy"])


def pit_series(ticker: str) -> list[dict]:
    """單檔完整流程:Polygon 抓 → yfinance 補 → 合併。網路。"""
    from sharks.data.polygon_financials import fetch_quarters, with_yoy
    return merge_rows(with_yoy(fetch_quarters(ticker)), yf_quarterly_cash(ticker))


def main(argv: Optional[list[str]] = None) -> int:
    import time
    args = [a.upper() for a in (sys.argv[1:] if argv is None else argv)] or ["HUM", "COHR"]
    out = {"generated_at": datetime.now(timezone.utc).isoformat(),
           "engine": "pit-merger(polygon filing_date + yfinance cash)", "tickers": {}}
    for n, t in enumerate(args):
        if n:
            time.sleep(13)
        try:
            rows = pit_series(t)
            out["tickers"][t] = {"rows": rows, "pit_fundamental_contested": pit_contested(rows)}
            print(f"  {t}: {len(rows)} quarters, contested={out['tickers'][t]['pit_fundamental_contested']}",
                  file=sys.stderr)
        except Exception as e:
            out["tickers"][t] = {"error": str(e)[:120]}
    p = Path("outputs") / f"pit-merged-{datetime.now().strftime('%Y-%m-%d')}.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {p}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
