"""Polygon PIT 季度基本面 — filing_date 為真 point-in-time 的財報序列.

主理人指令(2026-06-12):Finviz 是好前端但無 PIT 歷史 — Polygon 補盲區。
本模組抓季度財報(營收 / 營運現金流 / CapEx / FCF / 淨利),每筆帶 **filing_date**
(申報日 = 市場「知道」這數字的日子)→ 回測與案例庫對齊用 filing_date 而非
fiscal end_date,杜絕財報前視(philosophy/09-point-in-time)。

用途:
  - HUM/SLAB/ICHR/COHR 觸發前後 4-8 季 PIT 對比(Type A/B 區分)
  - 案例庫「觸發當時」基本面回填(yfinance 年報只回溯 ~5 年的補課)
CLI:
    python -m sharks.data.polygon_financials HUM COHR SLAB ICHR
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

BASE = "https://api.polygon.io/vX/reference/financials"
TOKEN_ENV = "POLYGON_API_KEY"


def _token() -> str:
    tok = os.environ.get(TOKEN_ENV, "").strip()
    if not tok:
        try:
            from sharks.discord.config import PROJECT_ROOT, _read_dotenv
            _read_dotenv(PROJECT_ROOT / ".env")
            tok = os.environ.get(TOKEN_ENV, "").strip()
        except Exception:
            pass
    if not tok:
        raise RuntimeError(f"{TOKEN_ENV} not set — put your Polygon key in .env")
    return tok


def _val(fin: dict, section: str, *keys: str) -> Optional[float]:
    sec = fin.get(section) or {}
    for k in keys:
        v = (sec.get(k) or {}).get("value")
        if v is not None:
            return float(v)
    return None


def parse_quarter(result: dict) -> dict:
    """單季 result → 標準列(防衛式;Polygon 科目名稱跨公司不齊)。"""
    fin = result.get("financials") or {}
    rev = _val(fin, "income_statement", "revenues")
    ni = _val(fin, "income_statement", "net_income_loss",
              "net_income_loss_attributable_to_parent")
    ocf = _val(fin, "cash_flow_statement", "net_cash_flow_from_operating_activities",
               "net_cash_flow_from_operating_activities_continuing")
    capex = _val(fin, "cash_flow_statement", "payments_to_acquire_property_plant_and_equipment",
                 "capital_expenditure")
    inv = _val(fin, "cash_flow_statement", "net_cash_flow_from_investing_activities")
    fcf = (ocf - abs(capex)) if (ocf is not None and capex is not None) else None
    return {"fiscal": f"{result.get('fiscal_year')}{result.get('fiscal_period')}",
            "end_date": result.get("end_date"),
            "filing_date": result.get("filing_date"),     # ← PIT 錨點
            "revenue": rev, "net_income": ni, "ocf": ocf,
            "capex": capex, "investing_cf": inv, "fcf": fcf}


def fetch_quarters(ticker: str, limit: int = 20, token: Optional[str] = None) -> list[dict]:
    """近 N 季(新→舊)。429 退避一次;Polygon 免費層 5 req/min。"""
    import requests
    tok = token or _token()
    params = {"ticker": ticker, "timeframe": "quarterly", "limit": limit,
              "order": "desc", "apiKey": tok}
    for attempt in (1, 2):
        r = requests.get(BASE, params=params, timeout=30)
        if r.status_code == 429 and attempt == 1:
            time.sleep(15)
            continue
        r.raise_for_status()
        return [parse_quarter(x) for x in r.json().get("results") or []]
    return []


def with_yoy(rows: list[dict]) -> list[dict]:
    """同季 YoY(對 4 季前):rev_yoy / ocf_yoy / fcf 改善方向。rows 為新→舊。"""
    out = []
    for i, r in enumerate(rows):
        prior = rows[i + 4] if i + 4 < len(rows) else None
        def yoy(k):
            if prior is None or r.get(k) is None or not prior.get(k):
                return None
            return round((r[k] / prior[k] - 1) * 100, 1) if prior[k] > 0 else None
        out.append({**r, "rev_yoy_pct": yoy("revenue"),
                    "fcf_positive": (r.get("fcf") is not None and r["fcf"] > 0),
                    "fcf_improving_yoy": (None if prior is None or r.get("fcf") is None
                                          or prior.get("fcf") is None
                                          else bool(r["fcf"] > prior["fcf"]))})
    return out


def main(argv: Optional[list[str]] = None) -> int:
    args = [a.upper() for a in (sys.argv[1:] if argv is None else argv)]
    if not args:
        args = ["HUM", "SLAB", "ICHR", "COHR"]
    out = {"generated_at": datetime.now(timezone.utc).isoformat(),
           "source": "polygon vX financials (PIT via filing_date)", "tickers": {}}
    for n, t in enumerate(args):
        if n:
            time.sleep(13)                       # 免費層限速保險
        try:
            out["tickers"][t] = with_yoy(fetch_quarters(t))
            print(f"  {t}: {len(out['tickers'][t])} quarters", file=sys.stderr)
        except Exception as e:
            out["tickers"][t] = {"error": str(e)[:120]}
            print(f"  {t}: ERROR {e}", file=sys.stderr)
    p = Path("outputs") / f"pit-fundamentals-{datetime.now().strftime('%Y-%m-%d')}.json"
    p.parent.mkdir(exist_ok=True)
    p.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {p}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
