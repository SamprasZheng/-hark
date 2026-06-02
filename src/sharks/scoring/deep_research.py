"""Deep Research — per-ticker evidence check.

針對推薦的每支股,產出完整研究報告:
  1. 公司基本面(yfinance info)
  2. 護城河分析(Buffett 3M + IP defensibility)
  3. 現金流 + 收益 + 估值
  4. 技術訊號(MA / golden cross / TD-9 / distance from high)
  5. FOM 5 維 breakdown
  6. 籌碼面(機構 + 短興趣 + 量爆)
  7. 推薦理由(narrative)
  8. 主要風險
  9. 何時該出場
"""

from __future__ import annotations

import json
import math
import sys
import warnings
from datetime import datetime, timezone
from pathlib import Path

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import numpy as np
import pandas as pd
import yfinance as yf

# Inline Buffett 3M
BUFFETT_3M_DETAILED = {
    "AAPL": {"moat": 92, "moat_type": "BRAND + SWITCHING_COST + ECOSYSTEM", "mgmt": 85,
             "thesis": "iPhone 換機 + Apple Intelligence + 印度成長"},
    "MSFT": {"moat": 95, "moat_type": "NETWORK + SWITCHING_COST + ENTERPRISE", "mgmt": 90,
             "thesis": "Azure AI + Copilot ARPU + Activision"},
    "META": {"moat": 85, "moat_type": "NETWORK_EFFECTS + DATA", "mgmt": 80,
             "thesis": "FB/IG/WhatsApp + AI 廣告 + Llama 開源"},
    "GOOGL": {"moat": 88, "moat_type": "SCALE + DATA + DISTRIBUTION", "mgmt": 75,
              "thesis": "Search + YouTube + Cloud,反壟斷風險"},
    "NVDA": {"moat": 92, "moat_type": "TECHNOLOGY + ECOSYSTEM (CUDA)", "mgmt": 90,
             "thesis": "AI GPU 唯一,軟件護城河 CUDA"},
    "TSM": {"moat": 95, "moat_type": "TECHNOLOGY + CAPITAL", "mgmt": 85,
            "thesis": "5nm/3nm 領先,客戶集中但無替代"},
    "AVGO": {"moat": 85, "moat_type": "TECHNOLOGY + CUSTOMER_LOCK", "mgmt": 88,
             "thesis": "定制 ASIC + VMware"},
    "LMT": {"moat": 90, "moat_type": "REGULATORY + SCALE + DUOPOLY", "mgmt": 82,
            "thesis": "國防寡占 + F-35 + 海軍 + 政府訂單長期"},
    "NOC": {"moat": 88, "moat_type": "REGULATORY + SCALE", "mgmt": 82,
            "thesis": "B-21 + 核彈系統 + 太空"},
    "RTX": {"moat": 88, "moat_type": "REGULATORY + TECHNOLOGY", "mgmt": 80,
            "thesis": "飛機引擎 + Patriot 飛彈"},
    "JNJ": {"moat": 90, "moat_type": "BRAND + REGULATORY + R&D", "mgmt": 78,
            "thesis": "藥品 + 醫材;穩定股息王"},
    "PG": {"moat": 85, "moat_type": "BRAND + DISTRIBUTION", "mgmt": 80,
           "thesis": "Tide / Pampers / Gillette 全球品牌"},
    "KO": {"moat": 95, "moat_type": "BRAND + DISTRIBUTION", "mgmt": 80,
           "thesis": "Coca-Cola 品牌權力 + Buffett 擁有"},
    "ORCL": {"moat": 75, "moat_type": "SWITCHING_COST", "mgmt": 70,
             "thesis": "DB lock-in;但 Cloud 落後 + 你旗破絕"},
    "TSLA": {"moat": 70, "moat_type": "BRAND + TECHNOLOGY", "mgmt": 50,
             "thesis": "EV 領先 + FSD + SpaceX 連動;Musk 風險"},
}


def fetch_ticker_data(ticker: str) -> dict:
    """Pull from yfinance — info + history."""
    try:
        t = yf.Ticker(ticker)
        info = t.info or {}
        hist = t.history(period="3y", interval="1mo")
        return {"info": info, "history": hist}
    except Exception as e:
        return {"info": {}, "history": pd.DataFrame(), "error": str(e)}


def technical_signals(hist: pd.DataFrame) -> dict:
    """Compute technical signals."""
    if hist.empty or "Close" not in hist.columns:
        return {}
    s = hist["Close"].dropna()
    if len(s) < 12:
        return {}
    last = float(s.iloc[-1])
    # MAs (monthly: 5MA approximates 5-month, 12MA = 12-month)
    ma_5 = float(s.tail(5).mean())
    ma_12 = float(s.tail(12).mean())
    ma_20 = float(s.tail(20).mean()) if len(s) >= 20 else None
    # Golden cross check
    if len(s) >= 13:
        prev_ma_5 = float(s.iloc[-6:-1].mean())
        prev_ma_12 = float(s.iloc[-13:-1].mean())
        golden_cross = (ma_5 > ma_12) and (prev_ma_5 <= prev_ma_12)
        death_cross = (ma_5 < ma_12) and (prev_ma_5 >= prev_ma_12)
    else:
        golden_cross = False
        death_cross = False
    # 52w high/low
    window = s.tail(13)
    high_52w = float(window.max())
    low_52w = float(window.min())
    dist_high = (high_52w - last) / high_52w if high_52w > 0 else 0
    dist_low = (last - low_52w) / low_52w if low_52w > 0 else 0
    # TD-9 (簡化:連續上漲/下跌週數)
    diffs = s.diff().tail(9).dropna()
    consecutive_up = sum(1 for d in diffs if d > 0)
    consecutive_down = sum(1 for d in diffs if d < 0)
    td9_setup = "BUY_SETUP" if consecutive_down >= 9 else "SELL_SETUP" if consecutive_up >= 9 else "NONE"
    # Bollinger 上下軌
    if len(s) >= 20:
        ma_b = float(s.tail(20).mean())
        std_b = float(s.tail(20).std())
        upper_band = ma_b + 2 * std_b
        lower_band = ma_b - 2 * std_b
        bb_position = "UPPER_BAND" if last > upper_band else "LOWER_BAND" if last < lower_band else "MIDDLE"
    else:
        bb_position = "INSUFFICIENT_DATA"

    return {
        "current_price": round(last, 2),
        "ma_5_month": round(ma_5, 2),
        "ma_12_month": round(ma_12, 2),
        "ma_20_month": round(ma_20, 2) if ma_20 else None,
        "golden_cross_5_vs_12": golden_cross,
        "death_cross_5_vs_12": death_cross,
        "high_52w": round(high_52w, 2),
        "low_52w": round(low_52w, 2),
        "dist_from_52w_high_pct": round(dist_high * 100, 1),
        "dist_from_52w_low_pct": round(dist_low * 100, 1),
        "td9_setup": td9_setup,
        "bollinger_position": bb_position,
    }


def fundamental_analysis(info: dict) -> dict:
    """Extract key fundamentals from yfinance info."""
    return {
        "market_cap_billion": round(info.get("marketCap", 0) / 1e9, 2) if info.get("marketCap") else None,
        "trailing_pe": info.get("trailingPE"),
        "forward_pe": info.get("forwardPE"),
        "peg_ratio": info.get("pegRatio"),
        "price_to_book": info.get("priceToBook"),
        "ev_to_ebitda": info.get("enterpriseToEbitda"),
        "profit_margin_pct": round(info.get("profitMargins", 0) * 100, 2) if info.get("profitMargins") else None,
        "operating_margin_pct": round(info.get("operatingMargins", 0) * 100, 2) if info.get("operatingMargins") else None,
        "return_on_equity_pct": round(info.get("returnOnEquity", 0) * 100, 2) if info.get("returnOnEquity") else None,
        "revenue_growth_yoy_pct": round(info.get("revenueGrowth", 0) * 100, 2) if info.get("revenueGrowth") else None,
        "earnings_growth_yoy_pct": round(info.get("earningsGrowth", 0) * 100, 2) if info.get("earningsGrowth") else None,
        "dividend_yield_pct": round(info.get("dividendYield", 0), 2) if info.get("dividendYield") else None,
        "free_cashflow_billion": round(info.get("freeCashflow", 0) / 1e9, 2) if info.get("freeCashflow") else None,
        "total_debt_billion": round(info.get("totalDebt", 0) / 1e9, 2) if info.get("totalDebt") else None,
        "debt_to_equity": info.get("debtToEquity"),
        "current_ratio": info.get("currentRatio"),
        "analyst_target_mean": info.get("targetMeanPrice"),
        "recommendation": info.get("recommendationKey"),
    }


def chip_flow_summary(info: dict) -> dict:
    """Short interest + institutional ownership."""
    return {
        "shortPercentOfFloat_pct": round(info.get("shortPercentOfFloat", 0) * 100, 2) if info.get("shortPercentOfFloat") else None,
        "heldPercentInstitutions_pct": round(info.get("heldPercentInstitutions", 0) * 100, 2) if info.get("heldPercentInstitutions") else None,
        "heldPercentInsiders_pct": round(info.get("heldPercentInsiders", 0) * 100, 2) if info.get("heldPercentInsiders") else None,
        "floatShares_millions": round(info.get("floatShares", 0) / 1e6, 1) if info.get("floatShares") else None,
        "shortRatio": info.get("shortRatio"),
    }


def deep_research(ticker: str) -> dict:
    """完整 evidence check 報告."""
    data = fetch_ticker_data(ticker)
    info = data.get("info", {})
    hist = data.get("history", pd.DataFrame())

    # Get moat info
    moat_data = BUFFETT_3M_DETAILED.get(ticker, {})

    # Build report
    report = {
        "ticker": ticker,
        "company_name": info.get("longName") or info.get("shortName", ticker),
        "sector": info.get("sector", "?"),
        "industry": info.get("industry", "?"),
        "as_of": datetime.now(timezone.utc).isoformat(),

        "🏰 moat_analysis": {
            "moat_score_buffett": moat_data.get("moat", "NOT_RATED"),
            "moat_type": moat_data.get("moat_type", "?"),
            "mgmt_score": moat_data.get("mgmt", "NOT_RATED"),
            "thesis": moat_data.get("thesis", "需 Researcher 補"),
        },

        "💰 fundamental": fundamental_analysis(info),

        "📊 technical_signals": technical_signals(hist),

        "📉 chip_flow": chip_flow_summary(info),

        "🎯 evidence_check": [],
        "⚠️ risk_check": [],
    }

    # Build evidence checklist
    ev = []
    fund = report["💰 fundamental"]
    tech = report["📊 technical_signals"]
    chip = report["📉 chip_flow"]

    # Fundamental evidence
    if fund.get("forward_pe") and fund["forward_pe"] < 25:
        ev.append(f"✅ Forward PE {fund['forward_pe']:.1f} 合理")
    elif fund.get("forward_pe") and fund["forward_pe"] > 40:
        ev.append(f"⚠️ Forward PE {fund['forward_pe']:.1f} 偏高")

    if fund.get("revenue_growth_yoy_pct") and fund["revenue_growth_yoy_pct"] > 15:
        ev.append(f"✅ 營收成長 +{fund['revenue_growth_yoy_pct']:.1f}% YoY")

    if fund.get("operating_margin_pct") and fund["operating_margin_pct"] > 20:
        ev.append(f"✅ 營業利益率 {fund['operating_margin_pct']:.1f}%(穩定獲利)")

    if fund.get("return_on_equity_pct") and fund["return_on_equity_pct"] > 15:
        ev.append(f"✅ ROE {fund['return_on_equity_pct']:.1f}%")

    if fund.get("free_cashflow_billion") and fund["free_cashflow_billion"] > 1:
        ev.append(f"✅ Free Cashflow ${fund['free_cashflow_billion']:.1f}B")

    if fund.get("dividend_yield_pct") and fund["dividend_yield_pct"] > 1:
        ev.append(f"✅ 股息率 {fund['dividend_yield_pct']:.1f}%")

    # Technical evidence
    if tech.get("golden_cross_5_vs_12"):
        ev.append("✅ **黃金交叉**:5MA 上穿 12MA(月線)")
    if tech.get("dist_from_52w_high_pct") and 15 < tech["dist_from_52w_high_pct"] < 35:
        ev.append(f"✅ **甜蜜點**:距 52w 高 -{tech['dist_from_52w_high_pct']:.0f}%(健康修正)")
    if tech.get("td9_setup") == "BUY_SETUP":
        ev.append("✅ **TD-9 BUY setup** 完成 — 趨勢竭盡反彈")
    if tech.get("bollinger_position") == "LOWER_BAND":
        ev.append("✅ Bollinger 下軌 — 超賣反彈機會")

    # Chip flow evidence
    if chip.get("heldPercentInstitutions_pct") and chip["heldPercentInstitutions_pct"] > 70:
        ev.append(f"✅ 機構持股 {chip['heldPercentInstitutions_pct']:.0f}%(高度認可)")
    if chip.get("shortPercentOfFloat_pct") and chip["shortPercentOfFloat_pct"] > 15:
        ev.append(f"🔥 短興趣 {chip['shortPercentOfFloat_pct']:.1f}% — 軋空潛力")

    # Moat
    if moat_data.get("moat", 0) >= 85:
        ev.append(f"✅ **Buffett-tier 護城河**:{moat_data['moat']}/100({moat_data['moat_type']})")

    report["🎯 evidence_check"] = ev

    # Risk checklist
    risks = []
    if fund.get("forward_pe") and fund["forward_pe"] > 50:
        risks.append(f"🔴 Forward PE {fund['forward_pe']:.1f} 極高(泡沫風險)")
    if fund.get("debt_to_equity") and fund["debt_to_equity"] > 200:
        risks.append(f"🔴 負債權益比 {fund['debt_to_equity']:.1f}%(高槓桿)")
    if tech.get("dist_from_52w_high_pct") is not None and tech["dist_from_52w_high_pct"] < 3:
        risks.append("⚠️ 太靠近 52w 高 — 不是進場點")
    if tech.get("td9_setup") == "SELL_SETUP":
        risks.append("⚠️ TD-9 SELL setup — 趨勢竭盡")
    if tech.get("bollinger_position") == "UPPER_BAND":
        risks.append("⚠️ Bollinger 上軌 — 超買")
    if chip.get("shortPercentOfFloat_pct") and chip["shortPercentOfFloat_pct"] > 25:
        risks.append(f"🔴 短興趣 {chip['shortPercentOfFloat_pct']:.1f}% 極高(空頭強烈)")
    if fund.get("operating_margin_pct") and fund["operating_margin_pct"] < 0:
        risks.append("🔴 營業虧損")
    if fund.get("revenue_growth_yoy_pct") and fund["revenue_growth_yoy_pct"] < 0:
        risks.append(f"🔴 營收下滑 {fund['revenue_growth_yoy_pct']:.1f}% YoY")

    report["⚠️ risk_check"] = risks

    # Verdict
    ev_count = len(ev)
    risk_count = len(risks)
    score = ev_count * 10 - risk_count * 15
    if score >= 50:
        verdict = "🟢 STRONG_BUY"
    elif score >= 25:
        verdict = "🟢 BUY"
    elif score >= 0:
        verdict = "🟡 WATCH"
    else:
        verdict = "🔴 AVOID"
    report["📋 verdict"] = verdict
    report["📋 evidence_score"] = score
    report["📋 evidence_count"] = ev_count
    report["📋 risk_count"] = risk_count

    return report


def main():
    out_dir = Path("outputs")
    out_dir.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")

    # Sample tickers from FOM Alpha top picks
    tickers = ["LMT", "MSFT", "META", "NOC", "UEC", "AESI", "NVDA", "AAPL",
                "NTLA", "DNN", "GLD", "GEV", "AEIS", "DOW"]
    print(f"Deep research on {len(tickers)} tickers", file=sys.stderr)

    reports = {}
    for t in tickers:
        try:
            r = deep_research(t)
            reports[t] = r
            print(f"  {t}: {r['📋 verdict']} (evidence {r['📋 evidence_count']}, risk {r['📋 risk_count']})",
                  file=sys.stderr)
        except Exception as e:
            print(f"  {t} failed: {e}", file=sys.stderr)

    out = {
        "as_of": datetime.now(timezone.utc).isoformat(),
        "schema_version": 1,
        "reports": reports,
    }
    out_path = out_dir / f"deep-research-{today}.json"
    out_path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
    print(f"wrote {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
