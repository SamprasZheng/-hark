"""Serenity Scout — find the next AXTI / SIVE / AAOI / SOI.

Filter pipeline:
  1. Market cap heuristic: prefer small ($100M-$3B range)
  2. AI supply chain sector tag (Compiler-curated CHOKEPOINT_DB)
  3. 12m return between -20% and +80% (not parabolic, not crashing — staging zone)
  4. Liquidity adequate (60d avg dollar volume > $5M)
  5. Compiler-assigned "Serenity-fit" score 0-100

Outputs ranked candidates with chokepoint thesis text.

Per [[../../raw/kol_signals/serenity-case-studies-2026-05-29]] — Serenity's playbook.
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

from sharks.scoring.fom import fetch_monthly, INDICES

# ─── CHOKEPOINT_DB: known + candidate names with Serenity-style chokepoint theses ───
CHOKEPOINT_DB = {
    # Confirmed Serenity picks (already moved a lot, but reference)
    "AXTI": {"chokepoint": "InP (indium phosphide) substrate for AI optical modules",
             "stage": "已漲完(6×)— 不再進場",
             "serenity_fit": 95, "approx_mcap_band": "$1-2B"},
    "SIVE": {"chokepoint": "CW laser source for CPO / silicon photonics",
             "stage": "已漲(19×)— Serenity 最高信念但已過時",
             "serenity_fit": 90, "approx_mcap_band": "$1-3B"},
    "AAOI": {"chokepoint": "Optical transceiver vertical supply chain",
             "stage": "已漲(5×)— 接近高點",
             "serenity_fit": 85, "approx_mcap_band": "$1-2B"},
    "POET": {"chokepoint": "Silicon photonics integrated optoelectronics",
             "stage": "已大漲;尚有 thesis 可信",
             "serenity_fit": 75, "approx_mcap_band": "$500M"},

    # Soitec - Serenity-named "safest long-term"
    "SOI": {"chokepoint": "SOI (silicon-on-insulator) substrate monopoly for SiPh + RF",
            "stage": "已漲數百%但 Serenity 視為長期 safest",
            "serenity_fit": 90, "approx_mcap_band": "$3-4B (€2B)"},

    # AI infra
    "NBIS": {"chokepoint": "European AI compute infrastructure (former Yandex)",
             "stage": "Mid-cycle;Serenity 追蹤組合",
             "serenity_fit": 75, "approx_mcap_band": "$5B+"},

    # Compound semi / laser
    "VLN": {"chokepoint": "HSD (high-speed data) chipsets for AI compute interconnect",
            "stage": "Multi-bagger 已啟動",
            "serenity_fit": 80, "approx_mcap_band": "$300M-$500M"},

    # Raspberry Pi
    "RPID": {"chokepoint": "Embedded SBC + IoT compute scaling",
             "stage": "Recent IPO catalyst",
             "serenity_fit": 70, "approx_mcap_band": "$1-2B"},

    # ── Compiler proposed NEW candidates (not yet Serenity-named, fit playbook) ──

    # Power semi specialty (XFAB-style, small-cap, government-backed)
    "NVTS": {"chokepoint": "GaN power semis for AI rack power delivery (XFAB pair)",
             "stage": "Mid-cycle;已漲 89% momentum",
             "serenity_fit": 70, "approx_mcap_band": "$500M-1B"},
    "POWI": {"chokepoint": "Power semis (NVDA-named in PCN-22181)",
             "stage": "Mid-stage rally",
             "serenity_fit": 65, "approx_mcap_band": "$2-3B"},

    # MEMS / specialty
    "AOSL": {"chokepoint": "MOSFET / power discrete for AI server",
             "stage": "Under-radar; not yet ran",
             "serenity_fit": 70, "approx_mcap_band": "$1-2B"},
    "QUIK": {"chokepoint": "Programmable logic for AI edge inference",
             "stage": "Speculative; small-cap",
             "serenity_fit": 50, "approx_mcap_band": "$50-100M"},

    # SiC foundry
    "WOLF": {"chokepoint": "SiC wafer + device for EV + AI power",
             "stage": "Battered; potential turnaround",
             "serenity_fit": 60, "approx_mcap_band": "$2-3B"},

    # Specialty foundry (Trump-positive)
    "GFS": {"chokepoint": "US specialty foundry (Trump-favored reshoring)",
            "stage": "Recent IPO; mid-cap; Trump-positive",
            "serenity_fit": 75, "approx_mcap_band": "$25B (note: too large per strict criteria)"},
    "SKYT": {"chokepoint": "US specialty defense foundry (.5GW)",
             "stage": "Pre-stage; volatile",
             "serenity_fit": 70, "approx_mcap_band": "$300-500M"},

    # Test equipment
    "AEHR": {"chokepoint": "SiC + SiPh device test equipment",
             "stage": "Up 10× already",
             "serenity_fit": 55, "approx_mcap_band": "$500M"},
    "ALAB": {"chokepoint": "I/O connectivity + retimer for AI clusters",
             "stage": "Recent IPO; multi-bagger",
             "serenity_fit": 70, "approx_mcap_band": "$5-10B"},

    # Compound semis (RF)
    "AKTS": {"chokepoint": "MEMS RF filters for 5G/6G",
             "stage": "Pre-stage",
             "serenity_fit": 60, "approx_mcap_band": "$100M-$200M"},

    # LPKF (Compiler can't verify the German ticker)
    "LPKFY": {"chokepoint": "LPKF Laser/SiPh — laser drilling for advanced packaging (Pink Sheet ADR)",
              "stage": "Compiler unable to verify ticker exists on yfinance — Researcher needed",
              "serenity_fit": 75, "approx_mcap_band": "TBD"},

    # CRDO — already in $hark universe
    "CRDO": {"chokepoint": "High-speed connectivity SerDes for AI clusters",
             "stage": "Multi-bagger; mid-cycle",
             "serenity_fit": 65, "approx_mcap_band": "$3-5B"},

    # AXT alternatives
    "IIVI / COHR": {"chokepoint": "Laser + optical components (now COHR)",
                    "stage": "Now large-cap COHR — too big",
                    "serenity_fit": 50, "approx_mcap_band": "$10-15B"},

    # Photonics / Optics ETF-tier
    "LITE": {"chokepoint": "Lumentum — coherent optics primes",
             "stage": "Up 11× — late stage",
             "serenity_fit": 50, "approx_mcap_band": "$5-8B"},

    # Substrate / interposer plays (board / glass)
    "GLW": {"chokepoint": "Corning glass — substrate for advanced packaging glass interposer",
            "stage": "Mid-cycle",
            "serenity_fit": 70, "approx_mcap_band": "$30B (too large strict)"},

    # Crypto chokepoint
    "MSTR": {"chokepoint": "Bitcoin treasury proxy (yield-bearing BTC exposure)",
             "stage": "Outside Serenity strict frame but related",
             "serenity_fit": 40, "approx_mcap_band": "$50B+"},
}


def serenity_fit_score(ticker: str) -> tuple[float, dict]:
    data = CHOKEPOINT_DB.get(ticker)
    if data is None:
        return 0.0, {"note": "not in CHOKEPOINT_DB"}
    return float(data.get("serenity_fit", 0)), data


def technical_stage_check(closes: pd.DataFrame, ticker: str, as_of: pd.Timestamp) -> dict:
    """Check 12m return + dist from 52w high + momentum stage."""
    s = closes.get(ticker)
    if s is None or s.dropna().empty:
        return {"r12": None, "dist_from_52w_high": None, "stage": "no_data"}
    s = s.dropna()
    pre = s.loc[:as_of]
    if len(pre) < 13:
        return {"r12": None, "dist_from_52w_high": None, "stage": "insufficient_data"}
    last = pre.iloc[-1]
    r12 = float(last / pre.iloc[-13] - 1)
    window = s.loc[as_of - pd.Timedelta(days=365):as_of]
    high = window.max() if not window.empty else last
    dist = float((high - last) / high) if high > 0 else 0.0
    # Stage classification
    if r12 > 2.0:
        stage = "extended_above_2x"
    elif r12 > 0.5 and dist < 0.1:
        stage = "late_rally"
    elif -0.2 < r12 < 0.5 and 0.05 < dist < 0.3:
        stage = "staging_zone_ideal"  # Serenity sweet spot
    elif r12 < -0.2:
        stage = "deep_correction"
    else:
        stage = "mid_cycle"
    return {"r12": round(r12, 3), "dist_from_52w_high": round(dist, 3), "stage": stage}


def main(out_dir: Path) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    today = pd.Timestamp("2026-05-29")
    tickers = list(CHOKEPOINT_DB.keys())
    print(f"Serenity Scout: scoring {len(tickers)} chokepoint candidates", file=sys.stderr)
    closes = fetch_monthly(tickers, "2019-12-01", "2026-05-29")

    results = []
    for t in tickers:
        if t.find("/") != -1:  # skip "IIVI / COHR" combined names
            continue
        fit, fit_data = serenity_fit_score(t)
        tech = technical_stage_check(closes, t, today)
        results.append({
            "ticker": t,
            "serenity_fit_score": fit,
            "chokepoint_thesis": fit_data.get("chokepoint", "—"),
            "stage_per_serenity_db": fit_data.get("stage", "—"),
            "approx_mcap_band": fit_data.get("approx_mcap_band", "—"),
            "r12_return": tech.get("r12"),
            "dist_from_52w_high": tech.get("dist_from_52w_high"),
            "technical_stage": tech.get("stage"),
        })

    # Rank: Serenity-fit + staging-zone bonus
    def rank_key(r):
        s = r["serenity_fit_score"] or 0
        if r["technical_stage"] == "staging_zone_ideal":
            s += 20
        elif r["technical_stage"] == "deep_correction":
            s += 10  # might be a recovery candidate
        elif r["technical_stage"] in ("extended_above_2x", "late_rally"):
            s -= 30  # too late
        return s

    results.sort(key=rank_key, reverse=True)

    report = {
        "as_of": datetime.now(timezone.utc).isoformat(),
        "schema_version": 1,
        "method": "Serenity-style chokepoint filter — small-cap supply chain + staging-zone technical + Compiler-curated CHOKEPOINT_DB",
        "candidate_count": len(results),
        "top_15_with_staging_bonus": [
            {**r, "final_rank_score": rank_key(r)}
            for r in results[:15]
        ],
        "all_candidates": results,
    }
    out_path = out_dir / f"serenity-scout-{today.date()}.json"
    out_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"wrote {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(Path("outputs")))
