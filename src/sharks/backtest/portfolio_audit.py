"""Portfolio Audit — apply FOM + leveraged-ETF + farmer-mindset filters to user's actual holdings.

Per-ticker verdict: HOLD / TRIM / SELL with rationale.

Hardcoded portfolio = P1 (32 holdings) + P2 (26 holdings) from principal screenshots 2026-05-30.
"""

from __future__ import annotations

import json
import sys
import warnings
from datetime import datetime, timezone
from pathlib import Path

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import pandas as pd

from sharks.scoring.fom import (
    fetch_monthly, momentum_score, contrarian_score, cyclic_score,
    quality_score, bubble_guard, IP_DEFENSIBILITY,
)

# ─── User's actual portfolios (2026-05-30) ───
# Format: ticker -> {percent_of_account, decoded_name, pct_account}
PORTFOLIO_1 = {
    # Leveraged ETFs (forced SELL)
    "TARK": {"name": "Tradr 2X Long ARKK", "pct": 13.04, "leveraged_of": "ARKK"},
    "LABU": {"name": "Direxion 3X Biotech Bull", "pct": 5.05, "leveraged_of": "XBI"},
    "ORCX": {"name": "GraniteShares 2x ORCL Daily", "pct": 4.53, "leveraged_of": "ORCL"},
    "CRSR": {"name": "Corsair Gaming", "pct": 4.46, "leveraged_of": None},
    "SBIT": {"name": "ProShares Short BTC -1x", "pct": 4.11, "leveraged_of": "BTC-USD"},
    "RGTX": {"name": "Rigetti Computing (quantum)", "pct": 3.63, "leveraged_of": None},
    "AAPB": {"name": "GraniteShares 2x AAPL Daily", "pct": 3.54, "leveraged_of": "AAPL"},
    "NOWL": {"name": "Tradr 2x NOW Daily", "pct": 3.23, "leveraged_of": "NOW"},
    "DDD":  {"name": "3D Systems", "pct": 3.11, "leveraged_of": None},
    "ENPH": {"name": "Enphase Energy", "pct": 3.06, "leveraged_of": None},
    "SMCL": {"name": "Direxion 2x SMCI Daily Bull", "pct": 3.02, "leveraged_of": "SMCI"},
    "LULG": {"name": "GraniteShares 2x LULU Daily", "pct": 2.95, "leveraged_of": "LULU"},
    "VSCO": {"name": "Victoria's Secret", "pct": 2.58, "leveraged_of": None},
    "ARRY": {"name": "Array Technologies", "pct": 2.46, "leveraged_of": None},
    "QBTX": {"name": "Defiance 2x Quantum Daily", "pct": 2.22, "leveraged_of": "QTUM"},
    "NOW":  {"name": "ServiceNow (cash)", "pct": 1.91, "leveraged_of": None},
    "QSU":  {"name": "Quantum-related (unverified)", "pct": 1.89, "leveraged_of": None},
    "AMPX": {"name": "Amprius Technologies", "pct": 1.87, "leveraged_of": None},
    "RBLU": {"name": "GraniteShares 2x ROBL Daily", "pct": 1.85, "leveraged_of": "RBLX"},
    "NKE":  {"name": "Nike", "pct": 1.85, "leveraged_of": None},
    "LULU": {"name": "Lululemon (cash)", "pct": 1.84, "leveraged_of": None},
    "TSLA": {"name": "Tesla (cash)", "pct": 1.83, "leveraged_of": None},
    "STZ":  {"name": "Constellation Brands", "pct": 1.82, "leveraged_of": None},
    "CRCT": {"name": "Cricut Inc", "pct": 1.82, "leveraged_of": None},
    "APA":  {"name": "APA Corp (oil)", "pct": 1.82, "leveraged_of": None},
    "SWKS": {"name": "Skyworks Solutions", "pct": 1.80, "leveraged_of": None},
    "PG":   {"name": "Procter & Gamble", "pct": 1.76, "leveraged_of": None},
    "PEP":  {"name": "PepsiCo", "pct": 1.74, "leveraged_of": None},
    "CRM":  {"name": "Salesforce", "pct": 1.73, "leveraged_of": None},
    "QUBX": {"name": "Quantum-related (speculative)", "pct": 1.70, "leveraged_of": None},
    "OKLL": {"name": "GraniteShares 2x OKLO Daily", "pct": 1.64, "leveraged_of": "OKLO"},
    "VFC":  {"name": "VF Corp", "pct": 1.60, "leveraged_of": None},
}

PORTFOLIO_2 = {
    "ZM":   {"name": "Zoom", "pct": None},
    "PEP":  {"name": "PepsiCo", "pct": None},
    "DIS":  {"name": "Disney", "pct": None},
    "LUNR": {"name": "Intuitive Machines", "pct": None},
    "UPS":  {"name": "United Parcel", "pct": None},
    "DOCN": {"name": "DigitalOcean", "pct": None},
    "SHAK": {"name": "Shake Shack", "pct": None},
    "ARRY": {"name": "Array Tech", "pct": None},
    "RRX":  {"name": "Regal Rexnord", "pct": None},
    "IP":   {"name": "International Paper", "pct": None},
    "DELL": {"name": "Dell Technologies", "pct": None},
    "ORCL": {"name": "Oracle Corp", "pct": None},
    "UEC":  {"name": "Uranium Energy", "pct": None},
    "TAC":  {"name": "Transalta", "pct": None},
    "GFS":  {"name": "GlobalFoundries", "pct": None},
    "AAPL": {"name": "Apple Inc", "pct": None},
    "BIRK": {"name": "Birkenstock", "pct": None},
    "PG":   {"name": "Procter & Gamble", "pct": None},
    "ALGM": {"name": "Allegro Microsystems", "pct": None},
    "SKYT": {"name": "SkyWater Technology", "pct": None},
    "RELY": {"name": "Remitly Global", "pct": None},
    "PATH": {"name": "UiPath", "pct": None},
    "APPN": {"name": "Appian Corp", "pct": None},
    "AESI": {"name": "Atlas Energy Solutions", "pct": None},
    "GRPN": {"name": "Groupon", "pct": None},
    "EXTR": {"name": "Extreme Networks", "pct": None},
}

# ─── Concentration context (the elephant the audit does NOT score) ───
# NVDA RSU/ESPP employer-comp exposure dominates total liquid-ish exposure but
# is intentionally OUTSIDE PORTFOLIO_1 / PORTFOLIO_2 (those are the actively
# managed brokerage books). Without surfacing this, an audit verdict like
# "P1 is 100% leveraged-ETF risk" misleads — P1 is only ~8% of true exposure.
# Figures are point-in-time estimates from raw/principal/2026-05-29-snapshot-*.md
# and wiki/12_employee_concentration.md. Update when a fresh snapshot lands.
CONCENTRATION_CONTEXT_USD = {
    "nvda_rsu_espp": 130_000,   # unvested employer comp; next vest 2026-06-17
    "us_broker_p1": 11_374,     # inferred from TARK 13.04% = $1,483.20 snapshot
    "taiwan_9a92_etf": 1_320,   # 台股 domestic ETF satellite
    "complementary_p2": 3_000,  # 複委託 (8840) — small, not fully snapshotted; rough est
}


def build_concentration_context() -> dict:
    """Surface the NVDA-RSU-dominated true exposure alongside the active-book
    audit, so downstream consumers don't mistake P1's internal mix for the
    principal's actual risk profile. Not scored — framed only."""
    c = CONCENTRATION_CONTEXT_USD
    total = sum(c.values())
    shares = {k: round(v / total * 100, 1) for k, v in c.items()} if total else {}
    return {
        "note": (
            "NVDA RSU/ESPP is NOT in portfolio_1_audit / portfolio_2_audit by "
            "design (those are the actively managed brokerage books). It "
            "dominates true exposure, so read the audit verdicts as applying to "
            "the ~10% active sleeve, not the whole book. The concentration lever "
            "is the RSU vest/sale schedule, not active-book rebalancing."
        ),
        "exposure_usd": dict(c),
        "exposure_share_pct": shares,
        "total_liquidish_usd": total,
        "see": "wiki/12_employee_concentration.md",
        "as_of_basis": "raw/principal/2026-05-29-snapshot-p1.md + wiki/12_employee_concentration.md",
        "figures_are_estimates": True,
    }

# Inline Buffett 3M (from earlier)
BUFFETT_3M = {
    "AAPL": 75, "KO": 75, "JNJ": 76, "PG": 73, "WMT": 71,
    "MSFT": 73, "GOOGL": 73, "META": 75, "NFLX": 69,
    "AMZN": 73, "BRK-B": 81, "MA": 69, "V": 69,
    "LMT": 79, "NOC": 78, "RTX": 76, "CAT": 72, "DE": 73,
    "GE": 67, "HON": 71, "LIN": 74, "APD": 73,
    "NVDA": 67, "TSM": 75, "ASML": 73, "AVGO": 66,
    "AMD": 57, "AMAT": 63, "LRCX": 61, "KLAC": 63,
    "ARM": 57, "CRM": 77, "NOW": 74, "ORCL": 63,
    "TSLA": 50, "INTC": 55, "OKLO": 33, "SMCI": 42,
    "VRT": 60, "ETN": 69, "GEV": 62, "EQIX": 73, "DLR": 73,
    "DHI": 68, "LEN": 68, "NEM": 63, "FCX": 65,
    "VRTX": 72, "REGN": 72, "GILD": 72, "PEP": 75, "STZ": 70,
    "NKE": 72, "LULU": 60, "VFC": 35, "APA": 55, "SWKS": 55,
    "DELL": 60, "ENPH": 50,
    "DIS": 70, "UPS": 65, "AESI": 55, "UEC": 40, "GFS": 60,
    "BIRK": 55, "DDD": 30, "RGTX": 25, "AMPX": 30,
    "CRSR": 40, "VSCO": 35, "ARRY": 40, "ALGM": 55, "SKYT": 55,
    "RELY": 50, "PATH": 50, "APPN": 50, "GRPN": 30, "EXTR": 50,
    "LUNR": 35, "TAC": 50, "IP": 55, "RRX": 60, "ZM": 50, "DOCN": 50,
    "SHAK": 45, "CRCT": 35,
}


def verdict_leveraged(ticker, ticker_data, fom_underlying=None):
    """Return verdict for leveraged ETF: forced SELL with rationale."""
    leveraged_of = ticker_data.get("leveraged_of")
    name = ticker_data.get("name")
    rationale = []
    rationale.append(f"槓桿 ETF 結構性 decay 15-50%/年")
    if leveraged_of:
        rationale.append(f"標的: {leveraged_of}")
        if leveraged_of in ["ORCL", "OKLO", "SMCI"]:
            rationale.append(f"🚨 {leveraged_of} 已被 principal 旗為破絕 — 持有其 2x 版本自相矛盾")
        elif leveraged_of in ["AAPL", "NOW"]:
            rationale.append(f"{leveraged_of} 是 Buffett-tier — 但持槓桿版會被 decay 吃光")
        elif leveraged_of in ["ARKK"]:
            rationale.append("ARKK 集合都在 bubble breakdown 邊緣")
        elif leveraged_of in ["XBI"]:
            rationale.append("XBI 6-10 月歷史最弱季 — leverage 加倍 decay")
        elif leveraged_of in ["RBLX", "LULU"]:
            rationale.append(f"{leveraged_of} 高 vol + 槓桿 = 加速燒錢")
        elif leveraged_of in ["QTUM"]:
            rationale.append("量子計算商業營收 < 2030 不會有規模;敘事 + 槓桿 = 1999 dot-com 重演")
        elif leveraged_of == "BTC-USD":
            rationale.append("BTC 反向 -1x: 系統說 BTC 2026 Q4-2027 Q1 才見底 → SBIT 還有空間,**這支可以保留**")
            return ("HOLD", " | ".join(rationale))
    return ("SELL", " | ".join(rationale))


def verdict_quantum_speculative(ticker):
    rationale = [
        "量子計算 IBM/Google/D-Wave roadmap 規模化 < 2030",
        "純敘事 + 0 營收 = 跟 1999 dot-com 同模式",
        "Buffett 能力圈外",
        "principal 自承「因為火紅買」= farmer mindset",
    ]
    return ("SELL", " | ".join(rationale))


def fom_verdict(closes, ticker, as_of):
    """Run FOM dimensions and convert to HOLD/TRIM/SELL."""
    try:
        mom = momentum_score(closes, ticker, as_of)
        con = contrarian_score(closes, ticker, as_of)
        cyc, _ = cyclic_score(ticker, as_of)
        qual = quality_score(closes, ticker, as_of)
        bub = bubble_guard(closes, ticker, as_of)
        buf = BUFFETT_3M.get(ticker, 40)
    except Exception as e:
        return ("HOLD-DATA-GAP", f"data error: {e}", {})

    base = 0.22*mom + 0.22*con + 0.13*cyc + 0.13*qual + 0.15*((bub+100)/2) + 0.15*buf
    breakdown = {"momentum": round(mom, 1), "contrarian": round(con, 1),
                 "cyclic": round(cyc, 1), "quality": round(qual, 1),
                 "bubble_guard": round(bub, 1), "buffett_3m": buf, "final_fom": round(base, 1)}

    # Verdict logic
    if bub <= -50:
        return ("TRIM-25%", f"bubble guard {bub} 極端 — late-cycle 過熱", breakdown)
    if bub <= -30 and mom > 60:
        return ("TRIM-25%", f"高 momentum 但 bubble guard {bub} 警示", breakdown)
    if base >= 55 and bub >= 0:
        return ("HOLD-or-ADD", f"FOM {base:.1f} + healthy bubble guard", breakdown)
    if base >= 45 and buf >= 70:
        return ("HOLD-Buffett-tier", f"Buffett-tier moat,雖然 FOM 中等", breakdown)
    if base < 35 and qual < 40:
        return ("SELL-or-TRIM-50%", f"low FOM {base:.1f} + low quality {qual:.1f}", breakdown)
    if base < 40:
        return ("TRIM-30%", f"low FOM {base:.1f}", breakdown)
    return ("HOLD", f"neutral FOM {base:.1f}", breakdown)


def main():
    out_dir = Path("outputs")
    today = pd.Timestamp("2026-05-30")
    print(f"Portfolio audit as of {today.date()}", file=sys.stderr)

    # Merge tickers
    all_tickers = set(PORTFOLIO_1.keys()) | set(PORTFOLIO_2.keys())
    # Add a few NVDA RSU-related
    all_tickers.add("NVDA")
    # Need data for fom; also need underlying for leveraged
    pull_set = set(all_tickers)
    for t, d in PORTFOLIO_1.items():
        if d.get("leveraged_of"):
            pull_set.add(d["leveraged_of"])
    pull_set.discard("QSU")  # likely no data
    pull_set.discard("QUBX")  # likely no data
    pull_set.discard("LULG")  # likely no data
    pull_set.discard("NOWL")
    pull_set.discard("ORCX")
    pull_set.discard("AAPB")
    pull_set.discard("OKLL")
    pull_set.discard("SMCL")
    pull_set.discard("QBTX")
    pull_set.discard("TARK")
    pull_set.discard("RBLU")
    pull_set.discard("SBIT")
    pull_set.discard("LABU")

    closes = fetch_monthly(list(pull_set), "2019-12-01", "2026-05-30")
    print(f"  pulled data for {len(closes.columns)} tickers", file=sys.stderr)

    # Audit each portfolio
    p1_results = []
    for t, d in PORTFOLIO_1.items():
        if d.get("leveraged_of"):
            verdict, rationale = verdict_leveraged(t, d)
            p1_results.append({"ticker": t, "name": d["name"], "pct": d["pct"],
                               "verdict": verdict, "rationale": rationale,
                               "fom_breakdown": None, "category": "leveraged_etf"})
        elif t in ("RGTX",):
            verdict, rationale = verdict_quantum_speculative(t)
            p1_results.append({"ticker": t, "name": d["name"], "pct": d["pct"],
                               "verdict": verdict, "rationale": rationale,
                               "fom_breakdown": None, "category": "speculative"})
        elif t in ("QSU", "QUBX"):
            verdict = "SELL"
            rationale = "量子敘事 + Compiler 無法驗證 ticker → farmer-mindset 持倉"
            p1_results.append({"ticker": t, "name": d["name"], "pct": d["pct"],
                               "verdict": verdict, "rationale": rationale,
                               "fom_breakdown": None, "category": "speculative"})
        else:
            verdict, rationale, breakdown = fom_verdict(closes, t, today)
            p1_results.append({"ticker": t, "name": d["name"], "pct": d["pct"],
                               "verdict": verdict, "rationale": rationale,
                               "fom_breakdown": breakdown, "category": "cash_equity"})

    p2_results = []
    for t, d in PORTFOLIO_2.items():
        verdict, rationale, breakdown = fom_verdict(closes, t, today)
        p2_results.append({"ticker": t, "name": d["name"],
                           "verdict": verdict, "rationale": rationale,
                           "fom_breakdown": breakdown})

    # Categorize verdicts
    def categorize(results):
        cats = {"SELL": [], "TRIM": [], "HOLD": [], "ADD": []}
        for r in results:
            v = r["verdict"]
            if v.startswith("SELL"):
                cats["SELL"].append(r["ticker"])
            elif "TRIM" in v:
                cats["TRIM"].append(r["ticker"])
            elif "ADD" in v:
                cats["ADD"].append(r["ticker"])
            else:
                cats["HOLD"].append(r["ticker"])
        return cats

    report = {
        "as_of": datetime.now(timezone.utc).isoformat(),
        "schema_version": 2,
        "concentration_context": build_concentration_context(),
        "portfolio_1_audit": p1_results,
        "portfolio_2_audit": p2_results,
        "p1_summary": categorize(p1_results),
        "p2_summary": categorize(p2_results),
    }
    out_path = out_dir / f"portfolio-audit-{today.date()}.json"
    out_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"wrote {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
