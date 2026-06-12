"""反身性監控 — Soros reflexivity 斷裂偵測(價格創高 vs 資金/基本面背離).

主理人指令(2026-06-12):「不知道下一隻老鼠是誰 = 我就是最後一隻老鼠」的工程解:
不猜頂,監控**正向回饋鏈條是否斷裂**。反身性 = 價格↑ → 敘事/融資能力↑ → 買盤↑;
斷裂訊號 = 價格仍在高位,但鏈條的「資金腿」(機構/內部人交易)與「基本面腿」(FCF 成長)
開始背離。價格自己不會說謊,但它最後一個說。

訊號分層(recommend-only,絕不自動下單):
  斷裂警告  near-high + 機構/內部人淨流出 + FCF YoY 轉負(雙腿齊斷)
  背離觀察  near-high + 資金腿流出(機構 Inst Trans <0 或內部人 ≤-10%)
  回饋健康  near-high + 機構仍淨流入
  數據缺    無 Finviz flows(僅價格面,不下結論)

數據:價格面 = 本地 lake(ma-scan rows);資金腿 = Finviz Elite(Inst Trans/Insider
Trans,現況快照 — 無歷史,所以這是**監控器不是回測**);基本面腿 = yfinance 年報
FCF YoY。CLI:
    python -m sharks.scoring.reflexivity            # 掃 near-high(距 52w 高 <5%)
"""

from __future__ import annotations

import json
import sys
import warnings
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

NEAR_HIGH_PCT = -5.0      # 距 52w 高 > -5% = 反身性末段候選
INSIDER_BREAK = -10.0     # 內部人淨賣 ≤ -10% 視為資金腿警訊
MAX_FCF_FETCH = 40        # FCF 抓取上限(控制網路呼叫)


def reflexivity_state(*, dist_52w_high_pct: Optional[float],
                      inst_trans: Optional[float], insider_trans: Optional[float],
                      fcf_yoy_pct: Optional[float]) -> dict:
    """單檔反身性判讀(純函式,供測試)。"""
    near = dist_52w_high_pct is not None and dist_52w_high_pct > NEAR_HIGH_PCT
    flow_break = ((inst_trans is not None and inst_trans < 0)
                  or (insider_trans is not None and insider_trans <= INSIDER_BREAK))
    fund_break = fcf_yoy_pct is not None and fcf_yoy_pct <= 0
    if not near:
        verdict = "n/a(未近高)"
    elif flow_break and fund_break:
        verdict = "斷裂警告"
    elif flow_break:
        verdict = "背離觀察"
    elif inst_trans is None and insider_trans is None:
        verdict = "數據缺"
    else:
        verdict = "回饋健康"
    return {"verdict": verdict, "near_high": near,
            "flow_break": bool(flow_break), "fund_break": bool(fund_break)}


def _fcf_yoy(ticker: str) -> Optional[float]:
    try:
        import yfinance as yf
        cf = yf.Ticker(ticker).cashflow
        if cf is None or cf.empty or "Free Cash Flow" not in cf.index:
            return None
        row = cf.loc["Free Cash Flow"].dropna()
        if len(row) < 2:
            return None
        vals = row.sort_index()
        v0, v1 = float(vals.iloc[-2]), float(vals.iloc[-1])
        return round((v1 / v0 - 1) * 100, 1) if v0 else None
    except Exception:
        return None


def scan(near_high_pct: float = NEAR_HIGH_PCT, fetch_fcf: bool = True) -> dict:
    """near-high 名單(本地 ma-scan)→ Finviz flows → FCF YoY → 分層。"""
    from sharks.data.finviz_elite import (DIMENSION_COLUMNS, DIMENSION_VIEW, _num,
                                          fetch_universe)
    try:                                              # CLI 直跑時把 .env 的 token 帶進來
        from sharks.discord.config import PROJECT_ROOT, _read_dotenv
        _read_dotenv(PROJECT_ROOT / ".env")
    except Exception:
        pass
    outs = sorted(Path("outputs").glob("ma-scan-*.json"))
    if not outs:
        return {"error": "no ma-scan output — 先跑 python -m sharks.scoring.ma_scanner"}
    rep = json.loads(outs[-1].read_text(encoding="utf-8"))
    rows = rep.get("rows", {})
    cand = {t: r for t, r in rows.items()
            if r.get("dist_52w_high_pct") is not None and r["dist_52w_high_pct"] > near_high_pct}

    flows: dict[str, dict] = {}
    finviz_err = None
    try:
        for fr in fetch_universe(sorted(cand), view=DIMENSION_VIEW, columns=DIMENSION_COLUMNS):
            tk = (fr.get("Ticker") or "").upper()
            if tk:
                flows[tk] = {"inst_trans": _num(fr, "Inst Trans", "Institutional Transactions"),
                             "insider_trans": _num(fr, "Insider Trans", "Insider Transactions")}
    except Exception as e:
        finviz_err = str(e)[:100]

    results = []
    fcf_budget = MAX_FCF_FETCH if fetch_fcf else 0
    for t, r in sorted(cand.items(), key=lambda kv: -(kv[1].get("dist_52w_high_pct") or -99)):
        fl = flows.get(t, {})
        fcf = None
        # FCF 只查資金腿已有警訊的(省呼叫;健康者不需要第二腿確認)
        if fcf_budget > 0 and ((fl.get("inst_trans") is not None and fl["inst_trans"] < 0)
                               or (fl.get("insider_trans") is not None and fl["insider_trans"] <= INSIDER_BREAK)):
            fcf = _fcf_yoy(t)
            fcf_budget -= 1
        st = reflexivity_state(dist_52w_high_pct=r.get("dist_52w_high_pct"),
                               inst_trans=fl.get("inst_trans"),
                               insider_trans=fl.get("insider_trans"), fcf_yoy_pct=fcf)
        results.append({"ticker": t, "sector": r.get("sector"),
                        "dist_52w_high_pct": r.get("dist_52w_high_pct"),
                        "rsi": r.get("rsi"), "rejection_bar": r.get("rejection_bar"),
                        "inst_trans_pct": fl.get("inst_trans"),
                        "insider_trans_pct": fl.get("insider_trans"),
                        "fcf_yoy_pct": fcf, **st})
    order = {"斷裂警告": 0, "背離觀察": 1, "回饋健康": 2, "數據缺": 3}
    results.sort(key=lambda x: (order.get(x["verdict"], 9), -(x["dist_52w_high_pct"] or -99)))
    counts: dict[str, int] = {}
    for x in results:
        counts[x["verdict"]] = counts.get(x["verdict"], 0) + 1
    return {"as_of_scan": rep.get("as_of"),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "engine": "reflexivity-monitor", "n_near_high": len(results),
            "finviz_error": finviz_err, "verdict_counts": counts, "rows": results,
            "disclaimer": "recommend-only 監控;Finviz flows 為現況快照非歷史 — 這是監控器不是回測。"}


def main(argv: Optional[list[str]] = None) -> int:
    rep = scan()
    if rep.get("error"):
        print(rep["error"], file=sys.stderr)
        return 1
    out = Path("outputs") / f"reflexivity-{rep.get('as_of_scan') or datetime.now().strftime('%Y-%m-%d')}.json"
    out.write_text(json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"reflexivity: near-high {rep['n_near_high']} 檔 → {out}", file=sys.stderr)
    for x in rep["rows"]:
        if x["verdict"] in ("斷裂警告", "背離觀察"):
            print(f"  {x['verdict']} {x['ticker']:6} 距高{x['dist_52w_high_pct']}% "
                  f"inst={x['inst_trans_pct']} insider={x['insider_trans_pct']} fcf={x['fcf_yoy_pct']}")
    print(f"  counts: {rep['verdict_counts']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
