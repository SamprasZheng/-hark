"""Portfolio Audit — apply FOM + leveraged-ETF + farmer-mindset filters to user's actual holdings.

Per-ticker verdict: HOLD / TRIM / SELL with rationale.

Hardcoded portfolio = P1 (16 visible holdings) + P2 (複委託 8840, 24 holdings full book),
both as of 2026-06-11 close. Sources: raw/principal/2026-06-11-snapshot-p1.md +
raw/principal/2026-06-11-snapshot-8840.md.
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
from sharks.scoring.leveraged_etf import (
    audit_leveraged_holdings, bear_hedge_menu, is_leveraged_etf,
    score_leveraged_etf,
)
from sharks.decision import position_review as pr

# ─── User's actual portfolios ───
# P1 updated 2026-06-11 close (raw/principal/2026-06-11-snapshot-p1.md, 2 截圖).
# pct = mkt_val / 可見部位小計 $6,696(清單在 ~$202 截斷,之下未知;無 % Acct 欄)。
# 舊槓桿 (TARK/LABU/SBIT/NOWL/AAPB/RBLU) 已不在頭部,但新開一批 2x 單股。
PORTFOLIO_1 = {
    "IGV":   {"name": "iShares Expanded Tech-Software ETF", "pct": 19.09, "mkt_val": 1278.56, "leveraged_of": None},
    "SIVEF": {"name": "Sivers Semiconductors(CPO 雷射/ELS 咽喉點)", "pct": 13.31, "mkt_val": 891.00, "leveraged_of": None},
    "HPQ":   {"name": "HP Inc", "pct": 7.51, "mkt_val": 503.03, "leveraged_of": None},
    "ALGM":  {"name": "Allegro MicroSystems", "pct": 7.20, "mkt_val": 482.00, "leveraged_of": None},
    "CRWG":  {"name": "GraniteShares 2x CRWV Daily", "pct": 5.93, "mkt_val": 396.88, "leveraged_of": "CRWV"},
    "ZM":    {"name": "Zoom", "pct": 5.53, "mkt_val": 370.60, "leveraged_of": None},
    "MSFU":  {"name": "Direxion Daily MSFT Bull 2X", "pct": 5.38, "mkt_val": 360.19, "leveraged_of": "MSFT"},
    "PTIR":  {"name": "GraniteShares 2x PLTR Daily", "pct": 4.85, "mkt_val": 324.55, "leveraged_of": "PLTR"},
    "CRMG":  {"name": "GraniteShares 2x CRM Daily", "pct": 4.71, "mkt_val": 315.09, "leveraged_of": "CRM"},
    "DDD":   {"name": "3D Systems", "pct": 4.52, "mkt_val": 302.37, "leveraged_of": None},
    "ENPH":  {"name": "Enphase Energy", "pct": 4.18, "mkt_val": 280.00, "leveraged_of": None},
    "LULG":  {"name": "GraniteShares 2x LULU Daily", "pct": 4.15, "mkt_val": 278.00, "leveraged_of": "LULU"},
    "INTU":  {"name": "Intuit", "pct": 4.15, "mkt_val": 277.75, "leveraged_of": None},
    "ARRY":  {"name": "Array Technologies", "pct": 3.34, "mkt_val": 223.51, "leveraged_of": None},
    "NXPX":  {"name": "TBD — 疑為 2x NXPI,待驗證", "pct": 3.14, "mkt_val": 210.00, "leveraged_of": None},
    "APA":   {"name": "APA Corp (oil) — 截斷列推定,待確認", "pct": 3.02, "mkt_val": 202.55, "leveraged_of": None},
}

# P2 = 複委託 8840(Fubon)。Updated 2026-06-11 close — raw/principal/2026-06-11-snapshot-8840.md
# (3 截圖,字母序 A→Z 完整帳本,24 檔;市值=現價×股數;總計 ≈$9,482)。
# 舊 26 檔清單(ZM/PEP/DIS/DOCN…,05-30 來源)與本帳本幾乎無交集 — 疑為另一容器,
# 已被本快照取代;出處待 principal 釐清(見 wiki/log 2026-06-12)。
PORTFOLIO_2 = {
    "ADBE":  {"name": "Adobe", "pct": 11.54, "mkt_val": 1094.00, "shares": 5, "leveraged_of": None},
    "CPNG":  {"name": "Coupang", "pct": 9.10, "mkt_val": 862.50, "shares": 50, "leveraged_of": None},
    "VST":   {"name": "Vistra(電力;Tier A 埋伏名單)", "pct": 7.72, "mkt_val": 731.90, "shares": 5, "leveraged_of": None},
    "AMAT":  {"name": "Applied Materials", "pct": 5.83, "mkt_val": 552.64, "shares": 1, "leveraged_of": None},
    "RDW":   {"name": "Redwire(太空)", "pct": 5.41, "mkt_val": 512.70, "shares": 30, "leveraged_of": None},
    "APPS":  {"name": "Digital Turbine", "pct": 5.35, "mkt_val": 507.00, "shares": 50, "leveraged_of": None},
    "SMR":   {"name": "NuScale Power(核電 SMR)", "pct": 5.05, "mkt_val": 478.50, "shares": 50, "leveraged_of": None},
    "LAC":   {"name": "Lithium Americas", "pct": 4.65, "mkt_val": 441.00, "shares": 100, "leveraged_of": None},
    "PD":    {"name": "PagerDuty", "pct": 4.62, "mkt_val": 438.50, "shares": 50, "leveraged_of": None},
    "TBCH":  {"name": "Turtle Beach", "pct": 4.24, "mkt_val": 401.70, "shares": 30, "leveraged_of": None},
    "ZETA":  {"name": "Zeta Global", "pct": 4.23, "mkt_val": 401.20, "shares": 20, "leveraged_of": None},
    "ORCL":  {"name": "Oracle", "pct": 3.88, "mkt_val": 368.20, "shares": 2, "leveraged_of": None},
    "ARM":   {"name": "ARM Holdings", "pct": 3.61, "mkt_val": 342.23, "shares": 1, "leveraged_of": None},
    "POET":  {"name": "POET Technologies(光子)", "pct": 3.56, "mkt_val": 337.50, "shares": 30, "leveraged_of": None},
    "UEC":   {"name": "Uranium Energy", "pct": 3.36, "mkt_val": 318.90, "shares": 30, "leveraged_of": None},
    "RIVN":  {"name": "Rivian", "pct": 3.28, "mkt_val": 310.80, "shares": 20, "leveraged_of": None},
    "FSLR":  {"name": "First Solar", "pct": 2.86, "mkt_val": 271.17, "shares": 1, "leveraged_of": None},
    "NTLA":  {"name": "Intellia Therapeutics", "pct": 2.60, "mkt_val": 247.00, "shares": 20, "leveraged_of": None},
    "SAFX":  {"name": "XCF Global", "pct": 2.20, "mkt_val": 208.25, "shares": 500, "leveraged_of": None},
    "NOW":   {"name": "ServiceNow", "pct": 2.17, "mkt_val": 206.16, "shares": 2, "leveraged_of": None},
    "HOOD":  {"name": "Robinhood Markets", "pct": 1.95, "mkt_val": 184.46, "shares": 2, "leveraged_of": None},
    "LPL":   {"name": "LG Display ADR", "pct": 1.43, "mkt_val": 135.90, "shares": 30, "leveraged_of": None},
    "AOSL":  {"name": "Alpha & Omega Semiconductor", "pct": 1.37, "mkt_val": 129.99, "shares": 3, "leveraged_of": None},
    "OPITQ": {"name": "Office Properties Income Trust(破產程序,歸零)", "pct": 0.0, "mkt_val": 0.0, "shares": 1000, "leveraged_of": None},
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
    "us_broker_p1": 6_696,      # 2026-06-11 可見部位小計(清單 ~$202 截斷、現金不可見 → 下限值)
    "taiwan_9a92_etf": 1_320,   # 台股 domestic ETF satellite
    "complementary_p2": 9_482,  # 複委託 8840 — 2026-06-11 全帳本(24 檔,OPITQ 計 0)
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
        "as_of_basis": "raw/principal/2026-06-11-snapshot-p1.md (P1) + wiki/12_employee_concentration.md",
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


def _recent_return(closes, ticker, months: int = 3):
    """Trailing return over the last `months` of monthly closes (a fraction),
    or None when there isn't enough history. The reversal gate's price signal —
    price action leads the (lagging) FOM momentum score."""
    try:
        s = closes[ticker].dropna()
    except Exception:
        return None
    if len(s) < months + 1:
        return None
    try:
        return round(float(s.iloc[-1] / s.iloc[-1 - months] - 1.0), 4)
    except Exception:
        return None


def main():
    out_dir = Path("outputs")
    today = pd.Timestamp.now().normalize()      # as_of = 執行日(輸出檔名隨日期,不覆寫歷史 audit)
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
    pull_set.discard("QSU")   # unverified ticker — likely no data
    pull_set.discard("QUBX")  # unverified ticker — likely no data
    pull_set.discard("LULG")  # unverified ticker — likely no data
    # NOTE: the real leveraged ETFs (NOWL/ORCX/AAPB/OKLL/SMCL/QBTX/TARK/RBLU/SBIT/LABU)
    # are intentionally KEPT in the pull so the hold/rotate review can judge a
    # leveraged winner by its OWN price action (owner choice 2026-06-01), not only
    # by the underlying. They still take the forced-SELL base verdict; the review
    # decides hold-trail vs sell from the trend.

    closes = fetch_monthly(list(pull_set), "2019-12-01", str(today.date()))
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

    # ─── Leveraged-ETF decay audit (wired from sharks.scoring.leveraged_etf) ───
    # Compute a base FOM for each leveraged underlying we have data for, so the
    # decay-aware scorer can produce a decay_adjusted_score. Then audit every
    # leveraged holding in P1 by its structural decay (worst-decay first).
    p1_holdings_pct = {t: (d.get("pct") or 0.0) for t, d in PORTFOLIO_1.items()}
    underlyings = {d["leveraged_of"] for d in PORTFOLIO_1.values() if d.get("leveraged_of")}
    underlying_foms: dict[str, float] = {}
    underlying_breakdowns: dict[str, dict] = {}
    for u in underlyings:
        if u in closes.columns:
            _, _, ubd = fom_verdict(closes, u, today)
            if ubd and ubd.get("final_fom") is not None:
                underlying_foms[u] = ubd["final_fom"]
                underlying_breakdowns[u] = ubd
    p1_leveraged_audit = audit_leveraged_holdings(
        p1_holdings_pct, underlying_foms=underlying_foms
    )
    # Tag each leveraged P1 verdict back onto the per-ticker result for the reader.
    lev_by_ticker = {r["ticker"]: r for r in p1_leveraged_audit}
    for r in p1_results:
        lev = lev_by_ticker.get(r["ticker"])
        if lev:
            r["leveraged_scorer"] = {
                "factor": lev["factor"],
                "annual_decay_pct": lev["annual_decay_pct"],
                "decay_adjusted_score": lev["decay_adjusted_score"],
                "decay_verdict": lev["verdict"],
            }

    # ─── Reversal-gated hold/rotate feedback loop (decision/position_review) ───
    # Re-label EXIT/TRIM verdicts to hold-and-trail for strong-trending winners
    # whose support is intact; keep SELL only on a real reversal. Leverage is
    # de-risked via a trailing/staged exit (mode below), never silently removed.
    # Recommend-only; never changes a cap. See philosophy/03-long-short-taxonomy
    # + 08-risk-and-position. (owner ask 2026-06-01: 績效好就觀察不換股, 真反轉才換)
    cash_foms = [r["fom_breakdown"]["final_fom"] for r in p1_results
                 if r.get("category") == "cash_equity" and r.get("fom_breakdown")
                 and r["fom_breakdown"].get("final_fom") is not None]
    perf_gate = pr.sleeve_performance(cash_foms)
    leveraged_exit_mode = "trailing"   # owner-confirmable; "immediate" = strict no-leverage dump
    leveraged_trend_source = "own"     # owner choice 2026-06-01: judge a leveraged ETF by its
                                       # OWN price action ("underlying" = conservative fallback)
    held_winners: list = []
    for r in p1_results:
        cat = r.get("category")
        if cat == "cash_equity":
            rev = pr.review_position(
                ticker=r["ticker"], base_verdict=r["verdict"], category=cat,
                fom_breakdown=r.get("fom_breakdown"),
                recent_return=_recent_return(closes, r["ticker"]), perf_gate=perf_gate)
        elif cat == "leveraged_etf":
            u = PORTFOLIO_1.get(r["ticker"], {}).get("leveraged_of")
            ubd = underlying_breakdowns.get(u, {})
            # judge by the ETF's OWN price (owner choice), falling back to the
            # underlying when the ETF has no usable history.
            own_mom = own_bub = own_rr = None
            if leveraged_trend_source == "own" and r["ticker"] in closes.columns:
                _, _, ebd = fom_verdict(closes, r["ticker"], today)
                own_rr = _recent_return(closes, r["ticker"])
                if ebd:
                    own_mom, own_bub = ebd.get("momentum"), ebd.get("bubble_guard")
            mom = own_mom if own_mom is not None else ubd.get("momentum")
            bub = own_bub if own_bub is not None else ubd.get("bubble_guard")
            rr = own_rr if own_rr is not None else (_recent_return(closes, u) if u else None)
            rev = pr.review_position(
                ticker=r["ticker"], base_verdict=r["verdict"], category=cat,
                trend_momentum=mom, trend_bubble=bub, recent_return=rr,
                leveraged_of=u, perf_gate=perf_gate, leveraged_exit_mode=leveraged_exit_mode)
        else:
            continue  # speculative / data-gap: no winner override; base verdict stands
        r["reviewed_verdict"] = rev.reviewed_verdict
        r["review"] = {"trend": rev.trend, "changed": rev.changed,
                       "trailing_stop_pct": rev.trailing_stop_pct,
                       "flips_to_sell_when": rev.flips_to_sell_when,
                       "why": rev.why, "support": rev.support}
        if rev.reviewed_verdict in (pr.V_HOLD_TRAIL, pr.V_TRIM_TRAIL):
            held_winners.append({
                "ticker": r["ticker"], "name": r["name"],
                "base_verdict": r["verdict"], "reviewed_verdict": rev.reviewed_verdict,
                "trailing_stop_pct": rev.trailing_stop_pct,
                "why": rev.why, "flips_to_sell_when": rev.flips_to_sell_when,
                "support": rev.support})

    # Categorize verdicts (on the REVIEWED verdict; base kept for transparency)
    def _bucket(results, key):
        cats = {"SELL": [], "TRIM": [], "HOLD": [], "ADD": []}
        for r in results:
            v = (r.get(key) or r["verdict"]).upper()
            if v.startswith("SELL"):
                cats["SELL"].append(r["ticker"])
            elif "TRIM" in v:
                cats["TRIM"].append(r["ticker"])
            elif "ADD" in v:
                cats["ADD"].append(r["ticker"])
            else:
                cats["HOLD"].append(r["ticker"])
        return cats

    def categorize(results):
        return _bucket(results, "reviewed_verdict")

    report = {
        "as_of": datetime.now(timezone.utc).isoformat(),
        "schema_version": 3,
        "concentration_context": build_concentration_context(),
        "portfolio_1_audit": p1_results,
        "portfolio_2_audit": p2_results,
        "p1_summary": categorize(p1_results),
        "p1_summary_base": _bucket(p1_results, "verdict"),
        "p1_held_winners": held_winners,
        "sleeve_performance": perf_gate,
        "leveraged_exit_mode": leveraged_exit_mode,
        "leveraged_trend_source": leveraged_trend_source,
        "p2_summary": categorize(p2_results),
        "p1_leveraged_audit": p1_leveraged_audit,
        "leveraged_underlying_foms": {k: round(v, 1) for k, v in underlying_foms.items()},
        "bear_hedge_menu": bear_hedge_menu(),
    }
    out_path = out_dir / f"portfolio-audit-{today.date()}.json"
    out_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"wrote {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
