"""Order/demand-anchored valuation — the RIGHT lens for earnings-inflecting names.

WHY THIS EXISTS (the lesson from the static-P/E mistake): a flat "price ÷ current
EPS × 30× industry P/E" screen systematically PENALISES names whose earnings are
inflecting up on a surging order book — exactly the memory-supercycle pattern
(those ran multiples BECAUSE orders/earnings exploded; P/E alone never said "sell").
The principal's correction: judge these on REAL order/demand/profit data, on a
FORWARD basis, not a static multiple.

So fair value here is built from THREE layers (see also the value-input menu the
desk uses):
  1. ORDER / DEMAND  (curated, grade A/B — the leading signal): book-to-bill,
     backlog $ + growth, contracted revenue + prepayments, key-segment YoY. These
     are NOT in any free API (they live in releases/transcripts) → curated in
     `watchlist/demand-orderbook.json`, seeded below from cross-confirmed filings.
  2. EARNINGS QUALITY / DURABILITY (auto, yfinance): gross-margin level+trend,
     operating margin, FCF margin + FCF→NI conversion, ROE, net cash, revenue
     growth, beta. The "is the E real and durable" layer beyond the multiple.
  3. INTANGIBLE / 不可估量 (curated 0–2 scorecard): moat, switching cost,
     optionality, capital allocation, customer concentration (a penalty). DCF
     can't see these → they drive a fair-P/E PREMIUM/DISCOUNT, not a fake number.

forward_fair_value = forward_eps × adjusted_fair_pe, where
  adjusted_fair_pe = PEG(order-validated growth) × moat × quality × order-traj
                     × (1 − concentration_penalty) + optionality_addon.

Plus an ORDER-TRAJECTORY ALERT (the kill-switch): the whole bull case rests on
orders CONTINUING to accelerate — flag B:B<1 / backlog stalling / contracted-rev
push-outs / segment-YoY decelerating. (MPWR's 2024 Blackwell-socket loss is the
cautionary tale: even huge demand can be lost to competition → order data must be
per-name, not just sector.)

PURE logic is unit-tested offline; only fetch_* touches network. yfinance grade-C;
order/intangible layer grade A/B (curated). OBSERVE-FIRST, watchlist-only, NOT
buy/sell advice.
"""

from __future__ import annotations

import json
import sys
import warnings
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

warnings.filterwarnings("ignore")

from sharks.scoring.valuation import INDUSTRY_PE

# ─── Layer 1+3: curated order-book + intangible scorecard (seed; override via JSON) ──
# Fields: book_to_bill, backlog_growth_yoy, contracted_rev_usd, prepayments_usd,
#   key_segment, key_segment_yoy (fraction), design_wins (note);
#   moat/switching/optionality/capital_allocation ∈ {0,1,2} (higher=better),
#   concentration_risk ∈ {0,1,2} (higher=worse → discount); grade, source, as_of.
DEMAND_ORDERBOOK: dict[str, dict] = {
    # ── the six "expensive" names, re-examined on order data ──
    "TSEM": {"book_to_bill": None, "backlog_growth_yoy": None, "contracted_rev_usd": 1.3e9,
             "prepayments_usd": 290e6, "key_segment": "SiPho (AI optical)", "key_segment_yoy": 2.00,
             "design_wins": ">50 SiPho customers; capacity 5x by end-2026; 2028 model $2.8B/$750M NI",
             "moat": 2, "switching": 2, "optionality": 2, "capital_allocation": 1, "concentration_risk": 1,
             "grade": "A/B", "as_of": "2026-05-31", "source": "TSEM Q1'26 6-K + IR PR"},
    "VICR": {"book_to_bill": 2.0, "backlog_growth_yoy": 0.70, "contracted_rev_usd": None,
             "prepayments_usd": None, "key_segment": "48V->PoL vertical power (AI)", "key_segment_yoy": None,
             "design_wins": "Gen-2 VPD; backlog $300.6M; ITC litigation pending (architecture-war risk)",
             "moat": 1, "switching": 1, "optionality": 1, "capital_allocation": 1, "concentration_risk": 1,
             "grade": "A/B", "as_of": "2026-05-31", "source": "VICR Q1'26 transcript"},
    "MTSI": {"book_to_bill": 1.5, "backlog_growth_yoy": None, "contracted_rev_usd": None,
             "prepayments_usd": None, "key_segment": "data-center optical + defense GaN", "key_segment_yoy": 0.22,
             "design_wins": "record bookings; owns Wolfspeed RF; DC-optical growth engine",
             "moat": 1, "switching": 1, "optionality": 1, "capital_allocation": 1, "concentration_risk": 1,
             "grade": "A/B", "as_of": "2026-05-31", "source": "MTSI FQ2'26 8-K + transcript"},
    "MPWR": {"book_to_bill": None, "backlog_growth_yoy": None, "contracted_rev_usd": None,
             "prepayments_usd": None, "key_segment": "AI Enterprise Data power", "key_segment_yoy": 0.977,
             "design_wins": "AI server power; BUT 2024 lost ~half Blackwell socket to Infineon/Renesas",
             "moat": 1, "switching": 1, "optionality": 1, "capital_allocation": 1, "concentration_risk": 2,
             "grade": "A/B", "as_of": "2026-05-31", "source": "MPWR Q1'26 8-K"},
    "POWI": {"book_to_bill": None, "backlog_growth_yoy": None, "contracted_rev_usd": None,
             "prepayments_usd": None, "key_segment": "PowiGaN", "key_segment_yoy": 0.40,
             "design_wins": "PowiGaN +40% but small base; total rev only +3% (consumer weak)",
             "moat": 1, "switching": 1, "optionality": 1, "capital_allocation": 1, "concentration_risk": 1,
             "grade": "A/B", "as_of": "2026-05-31", "source": "POWI Q1'26 8-K"},
    "CEVA": {"book_to_bill": None, "backlog_growth_yoy": None, "contracted_rev_usd": None,
             "prepayments_usd": None, "key_segment": "Wi-Fi/UWB IP royalty", "key_segment_yoy": 0.11,
             "design_wins": "record 91M Wi-Fi units, 14 deals/qtr; small absolute base; royalty leverage",
             "moat": 1, "switching": 1, "optionality": 2, "capital_allocation": 1, "concentration_risk": 1,
             "grade": "A/B", "as_of": "2026-05-31", "source": "CEVA Q1'26 IR"},
    # ── the cheap/quality side, for comparison ──
    "KEYS": {"book_to_bill": None, "backlog_growth_yoy": 0.56, "contracted_rev_usd": None, "prepayments_usd": None,
             "key_segment": "6G/NTN/AI test", "key_segment_yoy": 0.35, "design_wins": "orders +56%; the test tollbooth",
             "moat": 2, "switching": 2, "optionality": 1, "capital_allocation": 2, "concentration_risk": 0,
             "grade": "A/B", "as_of": "2026-05-31", "source": "KEYS FQ2'26 8-K"},
    "GFS":  {"book_to_bill": None, "backlog_growth_yoy": None, "contracted_rev_usd": None, "prepayments_usd": None,
             "key_segment": "Comms/DC + SiPho", "key_segment_yoy": 0.32, "design_wins": "RF-SOI/FDX chokepoint; SiPho doubling",
             "moat": 2, "switching": 2, "optionality": 1, "capital_allocation": 1, "concentration_risk": 1,
             "grade": "A/B", "as_of": "2026-05-31", "source": "GFS Q1'26 6-K"},
    "ADI":  {"book_to_bill": 1.0, "backlog_growth_yoy": None, "contracted_rev_usd": None, "prepayments_usd": None,
             "key_segment": "broad analog recovery", "key_segment_yoy": 0.30, "design_wins": "B:B>1 industrial; Empower vertical-power M&A",
             "moat": 2, "switching": 2, "optionality": 1, "capital_allocation": 2, "concentration_risk": 0,
             "grade": "A", "as_of": "2026-05-31", "source": "ADI FQ1'26 8-K"},
    "NXPI": {"book_to_bill": None, "backlog_growth_yoy": None, "contracted_rev_usd": None, "prepayments_usd": None,
             "key_segment": "Ind&IoT + UWB auto", "key_segment_yoy": 0.24, "design_wins": "UWB leader; auto digital-key design-in",
             "moat": 2, "switching": 2, "optionality": 1, "capital_allocation": 1, "concentration_risk": 0,
             "grade": "A", "as_of": "2026-05-31", "source": "NXPI Q1'26 8-K"},
    "QRVO": {"book_to_bill": None, "backlog_growth_yoy": None, "contracted_rev_usd": None, "prepayments_usd": None,
             "key_segment": "cellular RFFE", "key_segment_yoy": -0.07, "design_wins": "BAW duopoly; ~half Apple; in-housing risk; SWKS merger",
             "moat": 2, "switching": 2, "optionality": 0, "capital_allocation": 1, "concentration_risk": 2,
             "grade": "A", "as_of": "2026-05-31", "source": "QRVO FQ4'26 8-K"},
    "SWKS": {"book_to_bill": 1.05, "backlog_growth_yoy": None, "contracted_rev_usd": None, "prepayments_usd": None,
             "key_segment": "RFFE + Broad Markets", "key_segment_yoy": 0.0, "design_wins": "B:B>1, lean channel; $1B Android win; ~60% Apple",
             "moat": 2, "switching": 2, "optionality": 0, "capital_allocation": 1, "concentration_risk": 2,
             "grade": "A/B", "as_of": "2026-05-31", "source": "SWKS FQ2'26 transcript"},
    "MCHP": {"book_to_bill": 1.1, "backlog_growth_yoy": None, "contracted_rev_usd": None, "prepayments_usd": None,
             "key_segment": "MCU+analog recovery", "key_segment_yoy": None, "design_wins": "cycle bottom confirmed; dist inventory 26d low, restocking",
             "moat": 1, "switching": 2, "optionality": 1, "capital_allocation": 1, "concentration_risk": 0,
             "grade": "A", "as_of": "2026-05-31", "source": "MCHP FQ4'26 8-K"},
    "ON":   {"book_to_bill": None, "backlog_growth_yoy": None, "contracted_rev_usd": None, "prepayments_usd": None,
             "key_segment": "auto SiC", "key_segment_yoy": 0.05, "design_wins": "auto +5% first growth in 8 qtrs; SiC still soft",
             "moat": 1, "switching": 1, "optionality": 1, "capital_allocation": 1, "concentration_risk": 1,
             "grade": "A", "as_of": "2026-05-31", "source": "ON Q1'26 8-K"},
    "CRUS": {"book_to_bill": None, "backlog_growth_yoy": None, "contracted_rev_usd": None, "prepayments_usd": None,
             "key_segment": "audio + HPMS", "key_segment_yoy": 0.05, "design_wins": "content growth offsets flat units; ~91% Apple",
             "moat": 1, "switching": 1, "optionality": 0, "capital_allocation": 1, "concentration_risk": 2,
             "grade": "A", "as_of": "2026-05-31", "source": "CRUS FY26 8-K"},
    "NVTS": {"book_to_bill": None, "backlog_growth_yoy": None, "contracted_rev_usd": None, "prepayments_usd": None,
             "key_segment": "GaN high-power", "key_segment_yoy": 0.35, "design_wins": "AI 800V demos (not revenue); legacy collapsed -38.6%; cash burn",
             "moat": 1, "switching": 0, "optionality": 2, "capital_allocation": 0, "concentration_risk": 1,
             "grade": "A/B", "as_of": "2026-05-31", "source": "NVTS Q1'26 release"},
}

CURATED_ORDERBOOK_PATH = Path("watchlist/demand-orderbook.json")

# Intangible → multiplier maps
_MOAT_MULT = {0: 0.88, 1: 1.00, 2: 1.18}
_OPTIONALITY_ADDON = {0: 0.0, 1: 0.05, 2: 0.12}   # absolute fraction of industry P/E added
_CONC_PENALTY = {0: 0.0, 1: 0.06, 2: 0.14}
_PE_LO_MULT, _PE_HI_MULT = 0.7, 2.0               # fair-PE clamp around industry P/E


# ─── data load ────────────────────────────────────────────────────────────────
def load_orderbook(path: Optional[Path] = None) -> dict:
    """Curated order-book + intangibles. External JSON overrides the seed per ticker."""
    ob = {k: dict(v) for k, v in DEMAND_ORDERBOOK.items()}
    p = path or CURATED_ORDERBOOK_PATH
    if p and p.exists():
        try:
            ext = json.loads(p.read_text(encoding="utf-8"))
            if isinstance(ext, dict):
                for k, v in ext.items():
                    ob[k] = {**ob.get(k, {}), **v}   # external wins field-by-field
        except Exception as e:  # pragma: no cover
            print(f"  warn: bad orderbook {p}: {e}", file=sys.stderr)
    return ob


def fetch_quality_metrics(ticker: str) -> dict:
    """Layer-2 earnings-quality metrics from yfinance .info (network, best-effort)."""
    import yfinance as yf
    out = {"ticker": ticker}
    try:
        info = yf.Ticker(ticker).info or {}
    except Exception as e:  # pragma: no cover
        return {"ticker": ticker, "error": str(e)[:80]}
    rev = info.get("totalRevenue")
    ni = info.get("netIncomeToCommon")
    fcf = info.get("freeCashflow")
    cash = info.get("totalCash")
    debt = info.get("totalDebt")
    mc = info.get("marketCap")
    out.update({
        "price": info.get("currentPrice"), "market_cap": mc, "sector": info.get("sector"),
        "forward_eps": info.get("forwardEps"), "fwd_pe": info.get("forwardPE"),
        "gross_margin": info.get("grossMargins"), "operating_margin": info.get("operatingMargins"),
        "revenue_growth_yoy": info.get("revenueGrowth"), "roe": info.get("returnOnEquity"),
        "beta": info.get("beta"),
        "fcf_margin": (round(fcf / rev, 4) if (fcf and rev) else None),
        "fcf_conversion": (round(fcf / ni, 4) if (fcf and ni and ni > 0) else None),
        "net_cash": (round((cash or 0) - (debt or 0), 0) if (cash is not None or debt is not None) else None),
        "net_cash_to_mktcap": (round(((cash or 0) - (debt or 0)) / mc, 4) if mc else None),
    })
    return out


# ─── PURE scoring ───────────────────────────────────────────────────────────────
def quality_score(m: dict) -> float:
    """0-1 earnings-quality/durability score from gross margin, operating margin,
    FCF margin + conversion, ROE, net-cash. Each sub-signal contributes; missing
    fields just don't add (no penalty for absent data)."""
    pts, maxp = 0.0, 0.0
    def add(val, good, weight):
        nonlocal pts, maxp
        if val is None:
            return
        maxp += weight
        pts += weight * max(0.0, min(1.0, val / good)) if good > 0 else 0.0
    add(m.get("gross_margin"), 0.60, 1.0)        # 60%+ GM = top score
    add(m.get("operating_margin"), 0.30, 1.0)    # 30%+ OM
    add(m.get("fcf_margin"), 0.25, 1.0)          # 25%+ FCF margin
    add(m.get("fcf_conversion"), 1.0, 0.8)       # FCF≈NI
    add(m.get("roe"), 0.25, 0.8)                 # 25%+ ROE
    ncm = m.get("net_cash_to_mktcap")
    if ncm is not None:
        maxp += 0.6
        pts += 0.6 * max(0.0, min(1.0, 0.5 + ncm * 2.0))   # net cash positive lifts, net debt drags
    return round(pts / maxp, 3) if maxp > 0 else 0.5


def order_validated_growth(ob: dict, m: dict) -> Optional[float]:
    """The growth rate to feed PEG — VALIDATED by the order book, not yfinance's
    noisy earningsGrowth. Prefers curated key-segment YoY when the order book is
    strong; else revenue growth; haircut if orders are decelerating. Clamped."""
    seg = ob.get("key_segment_yoy")
    rev = m.get("revenue_growth_yoy")
    btb = ob.get("book_to_bill")
    backlog = ob.get("backlog_growth_yoy")
    strong = (btb is not None and btb >= 1.1) or (backlog is not None and backlog >= 0.2) \
        or (ob.get("contracted_rev_usd") is not None) or (seg is not None and seg >= 0.30)
    g = None
    if seg is not None and strong:
        g = seg                                   # trust the segment surge the order book backs
    elif seg is not None and rev is not None:
        g = min(seg, max(rev, 0.0))               # un-backed → haircut toward revenue
    elif rev is not None:
        g = rev
    elif seg is not None:
        g = seg
    if g is None:
        return None
    # decel haircut
    if (btb is not None and btb < 1.0) or (backlog is not None and backlog < 0) or (rev is not None and rev < 0):
        g = min(g, 0.0) if g is not None else g
    return round(max(-0.30, min(0.60, float(g))), 4)


def order_trajectory(ob: dict, m: dict) -> dict:
    """Accelerating / stable / decelerating / unknown + the kill-switch alert."""
    btb = ob.get("book_to_bill")
    backlog = ob.get("backlog_growth_yoy")
    seg = ob.get("key_segment_yoy")
    rev = m.get("revenue_growth_yoy")
    contracted = ob.get("contracted_rev_usd")
    reasons = []
    accel = stable = decel = False
    if (btb is not None and btb >= 1.1) or (backlog is not None and backlog >= 0.2) or \
       (contracted is not None) or (seg is not None and seg >= 0.30):
        accel = True
        if btb is not None: reasons.append(f"B:B {btb}")
        if backlog is not None: reasons.append(f"backlog +{backlog:.0%}")
        if contracted is not None: reasons.append(f"contracted ${contracted/1e9:.1f}B")
        if seg is not None and seg >= 0.30: reasons.append(f"{ob.get('key_segment','seg')} +{seg:.0%}")
    if (btb is not None and btb < 1.0) or (backlog is not None and backlog < 0) or (rev is not None and rev < 0):
        decel = True
        if btb is not None and btb < 1.0: reasons.append(f"B:B<1 ({btb})")
        if rev is not None and rev < 0: reasons.append(f"rev {rev:.0%}")
    if decel:
        state, alert = "decelerating", "⚠️ ORDER DECELERATION — kill-switch (re-underwrite the multiple)"
    elif accel:
        state, alert = "accelerating", None
    elif seg is not None or rev is not None:
        state, alert = "stable", None
    else:
        state, alert = "unknown", "no order data — multiple unvalidated"
    return {"state": state, "alert": alert, "reasons": reasons}


def intangible_multiplier(ob: dict) -> dict:
    """Layer-3: the 不可估量 scorecard → fair-PE premium/discount components."""
    moat = _MOAT_MULT.get(int(ob.get("moat", 1)), 1.0)
    switching = 1.0 + 0.05 * (int(ob.get("switching", 1)) - 1)     # ±5% per step
    cap = 1.0 + 0.04 * (int(ob.get("capital_allocation", 1)) - 1)  # ±4% per step
    conc_pen = _CONC_PENALTY.get(int(ob.get("concentration_risk", 0)), 0.0)
    opt_addon = _OPTIONALITY_ADDON.get(int(ob.get("optionality", 0)), 0.0)
    return {"moat_mult": round(moat * switching * cap, 4),
            "concentration_penalty": conc_pen, "optionality_addon": opt_addon}


def adjusted_fair_pe(growth: Optional[float], qscore: float, traj: dict,
                     intang: dict, industry_pe: float) -> Optional[float]:
    """PEG(order-validated growth) × moat/quality/order-trajectory × (1−conc) + optionality."""
    if growth is None:
        base = industry_pe
    else:
        base = max(industry_pe * _PE_LO_MULT, min(industry_pe * _PE_HI_MULT, max(growth, 0.0) * 100.0))
        if growth <= 0:
            base = industry_pe * _PE_LO_MULT
    qmult = 0.90 + 0.25 * qscore                          # 0.90–1.15
    tmult = {"accelerating": 1.10, "stable": 1.0, "decelerating": 0.82, "unknown": 0.95}[traj["state"]]
    pe = base * intang["moat_mult"] * qmult * tmult * (1.0 - intang["concentration_penalty"])
    pe += intang["optionality_addon"] * industry_pe
    return round(pe, 1)


def demand_valuation_row(ticker: str, m: dict, ob: dict) -> dict:
    industry_pe = INDUSTRY_PE.get(m.get("sector"), 25.0)
    qs = quality_score(m)
    g = order_validated_growth(ob, m)
    traj = order_trajectory(ob, m)
    intang = intangible_multiplier(ob)
    fair_pe = adjusted_fair_pe(g, qs, traj, intang, industry_pe)
    feps, price = m.get("forward_eps"), m.get("price")
    fair_value = round(feps * fair_pe, 2) if (feps and feps > 0 and fair_pe) else None
    premium = round(price / fair_value - 1, 3) if (fair_value and price) else None
    if fair_value is None:
        verdict = "無估值錨(虧損/缺料)— 只能當選擇權看" if (feps is None or (feps or 0) <= 0) else "資料不足"
    elif premium is None:
        verdict = "資料不足"
    elif premium <= -0.15:
        verdict = "訂單撐得起、且仍便宜"
    elif premium <= 0.10:
        verdict = "訂單撐得起估值(合理)"
    elif traj["state"] == "accelerating":
        verdict = "貴但訂單在加速(記憶體 pattern — 看訂單軌跡不是 P/E)"
    else:
        verdict = "估值超前訂單(這個才是真該謹慎)"
    return {
        "ticker": ticker, "price": price, "fwd_pe_current": m.get("fwd_pe"),
        "order_validated_growth": g, "quality_score": qs,
        "order_trajectory": traj["state"], "order_alert": traj["alert"], "order_reasons": traj["reasons"],
        "intangible": {"moat": ob.get("moat"), "switching": ob.get("switching"),
                       "optionality": ob.get("optionality"), "concentration_risk": ob.get("concentration_risk"),
                       "capital_allocation": ob.get("capital_allocation"), **intang},
        "adjusted_fair_pe": fair_pe, "forward_fair_value": fair_value,
        "premium_to_fair": premium, "verdict": verdict,
        "quality_metrics": {k: m.get(k) for k in ("gross_margin", "operating_margin", "fcf_margin",
                                                  "fcf_conversion", "roe", "net_cash_to_mktcap", "revenue_growth_yoy")},
        "key_segment": ob.get("key_segment"), "design_wins": ob.get("design_wins"),
        "grade": ob.get("grade"), "source": ob.get("source"),
    }


def run(tickers: Optional[list[str]] = None, *, network: bool = True,
        orderbook_path: Optional[Path] = None,
        metrics_by_ticker: Optional[dict[str, dict]] = None) -> list[dict]:
    ob_all = load_orderbook(orderbook_path)
    tickers = tickers or list(ob_all.keys())
    rows = []
    for t in tickers:
        m = (metrics_by_ticker or {}).get(t)
        if m is None and network:
            m = fetch_quality_metrics(t)
        m = m or {"ticker": t}
        rows.append(demand_valuation_row(t, m, ob_all.get(t, {})))
    return rows


def write_output(out_dir: Path, rows: list[dict], as_of: str) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {"schema_version": 1, "written_at": datetime.now(timezone.utc).isoformat(),
               "as_of": as_of, "report_type": "demand_valuation", "observe_first": True,
               "note": ("order/demand-anchored forward fair value (3 layers: curated order-book + "
                        "yfinance quality + curated intangible scorecard). WATCHLIST only; not advice."),
               "rows": rows}
    path = out_dir / f"demand-valuation-{as_of}.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    return path


def main(argv: Optional[list[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    as_of = next((a for a in argv if not a.startswith("-")), None) or datetime.now().strftime("%Y-%m-%d")
    network = "--no-network" not in argv
    rows = run(network=network)
    path = write_output(Path("outputs"), rows, as_of)
    print(f"wrote {path}", file=sys.stderr)
    print(f"\n{'TKR':6}{'curPE':>7}{'g~':>7}{'Q':>5}{'fairPE':>8}{'fairVal':>9}{'prem%':>7}  traj  verdict", file=sys.stderr)
    for r in sorted(rows, key=lambda x: (x["premium_to_fair"] is None, x["premium_to_fair"] or 0)):
        prem = r["premium_to_fair"]
        g = r["order_validated_growth"]
        print(f"{r['ticker']:6}{(r['fwd_pe_current'] or 0):>7.1f}"
              f"{(f'{g*100:+.0f}' if g is not None else 'n/a'):>7}{r['quality_score']:>5.2f}"
              f"{(r['adjusted_fair_pe'] or 0):>8.1f}{(r['forward_fair_value'] or 0):>9.2f}"
              f"{(f'{prem*100:+.0f}' if prem is not None else 'n/a'):>7}  {r['order_trajectory'][:5]:5} {r['verdict']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
