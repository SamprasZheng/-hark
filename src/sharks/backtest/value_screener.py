"""Value-sleeve screener — beaten-down QUALITY (撿菸頭抽兩口, done safely).

Finds candidates for the VALUE sleeve ([[philosophy/concepts/return-horizon-structure]]):
stocks that are BOTH deeply off their highs AND quality, so a cigar-butt has
margin of safety rather than being a falling knife. The quality filter is the
whole point — a low-quality name that is merely down is a VALUE TRAP and is
rejected, not surfaced.

Universe note (honest): a true full S&P-500 + Russell-2000 sweep needs a data
vendor (this env lacks lxml for the Wikipedia list; the iShares IWM endpoint is
anti-bot). But scanning 2,000 random micro-caps is the WRONG tool for a
beaten-down-QUALITY screen — most fail the quality gate. So the universe is a
CURATED quality compounder set (mega → small) + the existing $hark universe. The
screen's job is to find which of the *quality* names are on sale, not to trawl junk.

Metrics (monthly, PIT — `closes.loc[:as_of]`):
  - dd_52w     : drawdown from the trailing-12-month high (beaten = −25%..−70%)
  - trend_5y   : 60-month total return (survivor filter — a quality compounder in
                 a drawdown is still up over 5y; a structural collapse is not →
                 this is the falling-knife / value-trap filter)
  - vol_ann    : annualised monthly-return vol (lower = higher quality/stability)
  - ret_3m     : last-3-month return (stabilising filter — not in freefall)

Rank by a value_score that rewards quality (low vol + intact long-term trend +
stabilising) among the beaten-down set. Output is a WATCHLIST — every name must
still clear the 十足的證據 gate before any buy.
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

import numpy as np
import pandas as pd

from sharks.scoring.fom import DEFAULT_UNIVERSE, IP_DEFENSIBILITY, fetch_monthly

# Curated quality-compounder universe (mega → small). These are names that, WHEN
# BEATEN DOWN, are genuine cigar-butts (durable franchises, not structural
# decliners). Spans S&P-500 quality + select quality mid/small-caps as a
# Russell-2000 stand-in. Deduped against DEFAULT_UNIVERSE at assembly.
QUALITY_COMPOUNDERS = [
    # staples / consumer quality
    "KO", "PEP", "PG", "CL", "KMB", "MDLZ", "GIS", "K", "HSY", "MO", "PM", "EL",
    "CLX", "CHD", "MKC", "SJM", "HRL", "KHC",
    # healthcare quality
    "JNJ", "UNH", "MRK", "PFE", "ABBV", "TMO", "DHR", "ABT", "MDT", "ISRG",
    "SYK", "BDX", "ELV", "CI", "HUM", "CVS", "GILD", "BIIB", "VRTX", "REGN",
    "AMGN", "BMY", "ZTS", "DXCM", "IDXX", "RMD", "WST", "A",
    # consumer discretionary quality
    "COST", "WMT", "TGT", "HD", "LOW", "NKE", "SBUX", "MCD", "DIS", "BKNG",
    "MAR", "CMG", "ULTA", "LULU", "TJX", "ROST", "ORLY", "AZO", "YUM", "DPZ",
    "DECK", "CROX", "WING", "TXRH", "FND", "POOL", "WSM", "RH",
    # financials quality
    "V", "MA", "AXP", "JPM", "BAC", "GS", "MS", "BLK", "SPGI", "MCO", "ICE",
    "CME", "BX", "KKR", "BRK-B", "FDS", "MSCI", "TROW", "NDAQ",
    # industrials quality
    "HON", "CAT", "DE", "GE", "RTX", "LMT", "NOC", "GD", "UNP", "UPS", "FDX",
    "ETN", "EMR", "ITW", "PH", "ROP", "DOV", "AME", "FTV", "XYL", "CSL", "WM",
    "RSG", "URI", "PWR", "FAST", "GWW", "PAYX", "ADP", "VRSK", "CTAS",
    # tech / software quality (not already in DEFAULT_UNIVERSE)
    "ORCL", "CSCO", "IBM", "TXN", "ADI", "MCHP", "AMAT", "LRCX", "KLAC", "ACN",
    "NOW", "SNPS", "CDNS", "ANSS", "FICO", "ANET", "KEYS", "TER", "GRMN",
    # comms / media quality
    "CMCSA", "TMUS", "VZ", "T", "NFLX", "EA", "TTWO",
    # real assets / utilities quality
    "AMT", "PLD", "EQIX", "O", "CCI", "DLR", "NEE", "DUK", "SO", "LIN", "SHW",
    "ECL", "APD", "NUE", "VMC", "MLM",
    # quality mid/small (Russell-2000 stand-ins)
    "WD", "EXPO", "SAIA", "MEDP", "HALO", "LNTH", "ENSG", "CSWI", "AAON",
    "RBC", "ATI", "MLI", "WIRE", "CASY", "BJ",
]


def _metric(closes: pd.DataFrame, t: str, as_of: pd.Timestamp) -> Optional[dict]:
    s = closes.get(t)
    if s is None:
        return None
    s = s.dropna().loc[:as_of]
    if len(s) < 15:                       # need enough history
        return None
    price = float(s.iloc[-1])
    if price < 5:                         # liquidity / penny filter
        return None
    win12 = s.iloc[-13:] if len(s) >= 13 else s
    high12 = float(win12.max())
    dd_52w = price / high12 - 1.0 if high12 > 0 else 0.0
    trend_5y = (price / float(s.iloc[-61]) - 1.0) if len(s) >= 61 else (
        price / float(s.iloc[0]) - 1.0)
    rets = s.pct_change().dropna()
    vol_ann = float(rets.iloc[-36:].std() * np.sqrt(12)) if len(rets) >= 12 else float(rets.std() * np.sqrt(12))
    ret_3m = (price / float(s.iloc[-4]) - 1.0) if len(s) >= 4 else 0.0
    return {"price": round(price, 2), "dd_52w": round(dd_52w, 3),
            "trend_5y": round(trend_5y, 3), "vol_ann": round(vol_ann, 3),
            "ret_3m": round(ret_3m, 3)}


def screen(closes: pd.DataFrame, universe: list[str], as_of: pd.Timestamp,
           dd_min: float = -0.70, dd_max: float = -0.20,
           trend_floor: float = -0.25, trend_ceiling: float = 2.5,
           freefall_floor: float = -0.20, vol_max: float = 0.55,
           top_n: int = 25) -> list[dict]:
    """Return ranked beaten-down-QUALITY candidates for the VALUE sleeve.

    A VALUE candidate must be LOW-RISK cheap quality, not a momentum monster in a
    shallow pullback. So beyond the beaten-down band we require:
      - trend_5y in [trend_floor, trend_ceiling]: above floor = survivor (not a
        collapse → value-trap filter); BELOW CEILING = not a +300% momentum name
        merely −20% off its high (that is FOM/moonshot, not value).
      - vol_ann <= vol_max: a value cigar-butt is STABLE; a 100%+ vol name is a
        moonshot regardless of how 'cheap' it looks.
    """
    out = []
    for t in universe:
        m = _metric(closes, t, as_of)
        if m is None:
            continue
        if not (dd_min <= m["dd_52w"] <= dd_max):
            continue
        if not (trend_floor <= m["trend_5y"] <= trend_ceiling):  # survivor, NOT momentum
            continue
        if m["ret_3m"] < freefall_floor:                          # not in freefall
            continue
        if m["vol_ann"] > vol_max:                                # value = stable, not a moonshot
            continue
        ip = IP_DEFENSIBILITY.get(t, 50)
        # value_score rewards quality (IP + low vol + stabilising) with modest
        # credit for cheapness. Trend bonus is small + capped so momentum can't win.
        quality = 0.6 * ip + 20 * min(max(m["trend_5y"], 0) / 1.0, 1.0)  # IP-led, small trend credit
        stability = 100 * (1 - min(m["vol_ann"], vol_max) / vol_max)     # low vol → high
        cheap = 40 * min(abs(m["dd_52w"]) / 0.6, 1.0)                    # deeper dd → cheaper, capped
        stabilising = 20 * (1 if m["ret_3m"] > 0 else 0.3)
        value_score = round(0.40 * quality + 0.30 * stability + 0.20 * cheap + 0.10 * stabilising, 1)
        out.append({"ticker": t, "value_score": value_score, "ip_defensibility": ip, **m})
    out.sort(key=lambda r: r["value_score"], reverse=True)
    return out[:top_n]


def main() -> int:
    out_dir = Path("outputs")
    out_dir.mkdir(parents=True, exist_ok=True)
    universe = sorted(set(DEFAULT_UNIVERSE + QUALITY_COMPOUNDERS))
    print(f"Value screen: {len(universe)} names (DEFAULT_UNIVERSE + quality compounders)", file=sys.stderr)
    closes = fetch_monthly(universe, "2018-01-01", "2026-05-29")
    as_of = pd.Timestamp("2026-05-29")
    cands = screen(closes, [t for t in universe if t in closes.columns], as_of)
    report = {
        "as_of": datetime.now(timezone.utc).isoformat(),
        "schema_version": 1,
        "report_type": "value_sleeve_screen",
        "llm_involvement": "none",
        "universe_size": len([t for t in universe if t in closes.columns]),
        "method": "beaten-down (dd −20..−70%) + survivor (5y>−25%) + stabilising (3m>−20%), ranked by quality-weighted value_score. WATCHLIST only — clear 十足的證據 before buy.",
        "candidates": cands,
    }
    out_path = out_dir / "value-screen.json"
    out_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"wrote {out_path} ({len(cands)} candidates)", file=sys.stderr)
    for c in cands:
        print(f"  {c['ticker']:6} score {c['value_score']:>5}  dd {c['dd_52w']:>6.0%}  "
              f"5y {c['trend_5y']:>+6.0%}  vol {c['vol_ann']:>4.0%}  3m {c['ret_3m']:>+5.0%}  ip {c['ip_defensibility']}",
              file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
