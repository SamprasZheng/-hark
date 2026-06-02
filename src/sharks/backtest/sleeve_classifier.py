"""Four-sleeve portfolio classifier — FOM / Value / Moonshot / Hedge.

The principal set a target allocation (2026-05-31): **FOM 40 / Value 30 /
Moonshot 20 / Hedge 10**, derived from the measured term-structure of returns
([[philosophy/concepts/return-horizon-structure]]):

  - FOM_CORE  : quality + momentum names FOM ranks; held 3-6m. The engine.
  - VALUE     : beaten-down QUALITY (撿菸頭抽兩口) held ~12m. The quality filter is
                the margin of safety that separates a cigar-butt from a falling
                knife — a low-quality name that is merely down is a VALUE TRAP, not
                value, and is classed as moonshot/avoid instead.
  - MOONSHOT  : high-variance narrative / spec / LEVERAGED-long names. Ring-fenced;
                FOM structurally cannot pick these. Capped at the target weight.
  - HEDGE     : inverse / vol / short-beta instruments (SBIT, SQQQ, UVXY...).
  - DEAD      : −90/−100% husks — not a sleeve; tax-loss/closeout only.

Classification uses the leveraged-ETF registry + Buffett-tier quality scores +
small curated character sets. Pure logic; the curated sets are the judgment layer
and are meant to be reviewed, not trusted blindly.
"""

from __future__ import annotations

from sharks.scoring.leveraged_etf import LEVERAGED_ETF_REGISTRY, is_leveraged_etf

# Buffett-tier 3-month quality proxy (mirrors portfolio_audit.BUFFETT_3M subset;
# kept local so this module has no import cycle). >=65 = quality-grade.
QUALITY = {
    "AAPL": 75, "MSFT": 73, "NVDA": 67, "CRM": 77, "NOW": 74, "ORCL": 63,
    "PG": 73, "PEP": 75, "KO": 75, "NKE": 72, "LULU": 60, "STZ": 70, "COST": 74,
    "HPQ": 58, "SWKS": 55, "ALGM": 55, "APA": 55, "NOK": 45, "TSLA": 50,
    "VFC": 35, "UAA": 38, "VSCO": 35, "CRCT": 35, "ENPH": 50, "AMPX": 30,
    "CRSR": 45, "ARRY": 40, "RUN": 35, "WOLF": 40, "MRNA": 54, "MARA": 30,
    "DDD": 30, "QSU": 25, "ONDU": 30,
}
QUALITY_GRADE = 60   # >= this counts as "quality" for the value sleeve

TARGET_ALLOCATION = {"FOM_CORE": 0.40, "VALUE": 0.30, "MOONSHOT": 0.20, "HEDGE": 0.10}

# Curated character sets (the judgment layer — review, don't trust blindly).
MOONSHOT_NARRATIVE = {           # high-variance spec / narrative, low quality
    "QSU", "QUBX", "QBTX", "RGTX", "RGTI", "DDD", "AMPX", "ARRY", "ONDU", "RUN",
    "LUNR", "VSCO", "CRCT", "WOLF", "ENPH", "MARA", "IONQ", "RGTI", "BBAI", "SOUN",
}
BEATEN_QUALITY = {"NKE", "LULU", "STZ", "MRNA"}   # 撿菸頭: down hard BUT quality
VALUE_TRAP = {"VFC", "UAA"}                       # down hard, LOW quality → avoid (not value)
DEFENSIVE_QUALITY = {"PG", "PEP", "KO", "COST", "CRM"}   # quality core (FOM)
HEDGE_SET = {"SBIT", "SQQQ", "SOXS", "SPXU", "SDOW", "UVXY", "UVIX", "VXX", "SVIX", "SVXY"}
DEAD = {  # −90/−100% husks (tax-loss only)
    "3333.HK", "EVERGRANDE", "FSRNQ", "FTCHQ", "GGEI", "IMTE", "MMTE", "NRDE",
    "LCDL", "BYND",
}


def classify_sleeve(ticker: str) -> dict:
    """Return {sleeve, reason} for one ticker."""
    t = ticker.upper()
    if t in DEAD:
        return {"sleeve": "DEAD", "reason": "−90/−100% husk — tax-loss/closeout only, not a position"}
    if is_leveraged_etf(t):
        spec = LEVERAGED_ETF_REGISTRY[t]
        if spec.get("vix_futures") or spec["factor"] < 0:
            return {"sleeve": "HEDGE", "reason": f"inverse/vol instrument ({spec['name']})"}
        return {"sleeve": "MOONSHOT", "reason": f"leveraged-long {spec['factor']}x ({spec['name']}) — high variance + decay"}
    if t in HEDGE_SET:
        return {"sleeve": "HEDGE", "reason": "inverse / short-beta hedge"}
    if t in VALUE_TRAP:
        q = QUALITY.get(t, 40)
        return {"sleeve": "MOONSHOT", "reason": f"beaten BUT low quality (q={q}) → value TRAP, not value; treat as spec/avoid"}
    if t in BEATEN_QUALITY:
        q = QUALITY.get(t, 60)
        return {"sleeve": "VALUE", "reason": f"beaten-down quality (q={q}) — 撿菸頭 candidate, margin of safety"}
    if t in MOONSHOT_NARRATIVE:
        return {"sleeve": "MOONSHOT", "reason": "narrative / spec — high variance, FOM can't rank"}
    q = QUALITY.get(t, 50)
    if t in DEFENSIVE_QUALITY or q >= 65:
        return {"sleeve": "FOM_CORE", "reason": f"quality core (q={q})"}
    return {"sleeve": "FOM_CORE", "reason": f"solid mid/large (q={q}) — default core"}


def classify_portfolio(holdings_usd: dict[str, float], target: dict = None) -> dict:
    """Tag every holding, roll up to sleeve weights, compare to target, and emit
    trim (over-cap) + add (under-target) guidance.

    holdings_usd: {ticker: market_value_usd}. DEAD names are excluded from the
    investable base (they are ~$0 and not a real allocation)."""
    target = target or TARGET_ALLOCATION
    rows = []
    for t, v in holdings_usd.items():
        c = classify_sleeve(t)
        rows.append({"ticker": t, "value": v, "sleeve": c["sleeve"], "reason": c["reason"]})

    investable = sum(r["value"] for r in rows if r["sleeve"] != "DEAD")
    by_sleeve: dict[str, float] = {}
    for r in rows:
        if r["sleeve"] == "DEAD":
            continue
        by_sleeve[r["sleeve"]] = by_sleeve.get(r["sleeve"], 0.0) + r["value"]

    sleeve_report = {}
    for s in ("FOM_CORE", "VALUE", "MOONSHOT", "HEDGE"):
        cur = by_sleeve.get(s, 0.0)
        cur_pct = cur / investable if investable else 0.0
        tgt = target[s]
        sleeve_report[s] = {
            "current_usd": round(cur, 2),
            "current_pct": round(cur_pct * 100, 1),
            "target_pct": round(tgt * 100, 1),
            "gap_pct": round((cur_pct - tgt) * 100, 1),
            "gap_usd": round((cur_pct - tgt) * investable, 2),
        }

    # Trim list: moonshot is the over-cap risk — worst names first (leveraged 3x,
    # then 2x, then spec), sorted by value desc within.
    moon = [r for r in rows if r["sleeve"] == "MOONSHOT"]
    def _moon_priority(r):
        t = r["ticker"]
        if is_leveraged_etf(t):
            f = LEVERAGED_ETF_REGISTRY[t]["factor"]
            return (0, -abs(f), -r["value"])   # leveraged first, higher factor first
        return (1, 0, -r["value"])
    moon.sort(key=_moon_priority)

    value_candidates = [r for r in rows if r["sleeve"] == "VALUE"]
    dead = [r for r in rows if r["sleeve"] == "DEAD"]

    return {
        "investable_usd": round(investable, 2),
        "by_sleeve": sleeve_report,
        "holdings": sorted(rows, key=lambda r: (r["sleeve"], -r["value"])),
        "trim_priority_moonshot": [{"ticker": r["ticker"], "value": r["value"], "reason": r["reason"]} for r in moon],
        "value_sleeve_holdings": [r["ticker"] for r in value_candidates],
        "dead_for_taxloss": [r["ticker"] for r in dead],
        "actions": _actions(sleeve_report, moon, investable),
    }


def _actions(sleeve_report: dict, moon: list, investable: float) -> list[str]:
    out = []
    m = sleeve_report["MOONSHOT"]
    if m["gap_pct"] > 0:
        out.append(
            f"MOONSHOT {m['current_pct']}% vs 20% target → OVER by {m['gap_pct']}pp "
            f"(~${abs(m['gap_usd']):.0f}). Trim worst-decay leveraged first: "
            + ", ".join(r["ticker"] for r in moon[:5]) + " …")
    v = sleeve_report["VALUE"]
    if v["gap_pct"] < 0:
        out.append(
            f"VALUE {v['current_pct']}% vs 30% target → UNDER by {abs(v['gap_pct'])}pp "
            f"(~${abs(v['gap_usd']):.0f}). Rotate proceeds into beaten-down QUALITY "
            "(撿菸頭): NKE/LULU/STZ-type, NOT low-quality value traps.")
    h = sleeve_report["HEDGE"]
    if h["gap_pct"] < 0:
        out.append(
            f"HEDGE {h['current_pct']}% vs 10% target → UNDER by {abs(h['gap_pct'])}pp "
            f"(~${abs(h['gap_usd']):.0f}). SBIT is the only hedge; add inverse/vol "
            "(SQQQ/UVXY) only on a systemic trigger, else keep dry powder.")
    f = sleeve_report["FOM_CORE"]
    if f["gap_pct"] < 0:
        out.append(
            f"FOM_CORE {f['current_pct']}% vs 40% target → UNDER by {abs(f['gap_pct'])}pp. "
            "Build the core with quality+momentum names as moonshot is trimmed.")
    return out


# Real P1 book (USD market value) from portfolio/index.md §2 (2026-05-30 snapshot).
# Dust (<$10: CRWD/DDOG/WDAY/XYZ/WDC/NXPI/MSFT) excluded — clear, don't classify.
P1_HOLDINGS_USD = {
    "TARK": 1515, "LABU": 585, "AAPB": 399, "NOWL": 469, "LULG": 336, "RBLU": 214,
    "QSU": 209, "TSLL": 158, "OKLL": 178, "ONDU": 147, "HPQ": 551, "CRSR": 484,
    "ALGM": 476, "SBIT": 476, "ENPH": 340, "STZ": 203, "AMPX": 202, "SWKS": 197,
    "PG": 197, "PEP": 196, "UAA": 179, "VFC": 174, "CRM": 215, "LULU": 209,
    "CRCT": 208, "APA": 207, "NKE": 205, "TSLA": 205, "VSCO": 276, "ARRY": 273,
    "RUN": 101, "WOLF": 59, "MRNA": 54, "NOK": 149,
}


def main() -> int:
    import json
    import sys
    from datetime import datetime, timezone
    from pathlib import Path

    report = classify_portfolio(P1_HOLDINGS_USD)
    report["as_of"] = datetime.now(timezone.utc).isoformat()
    report["target_allocation_pct"] = {k: round(v * 100) for k, v in TARGET_ALLOCATION.items()}
    report["source"] = "portfolio/index.md §2 (P1, 2026-05-30)"
    out = Path("outputs") / "sleeve-classification-p1.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"wrote {out}", file=sys.stderr)
    for a in report["actions"]:
        print("  • " + a, file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
