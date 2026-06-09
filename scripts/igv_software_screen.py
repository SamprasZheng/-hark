"""IGV software-sector screen — today's software picks via the $hark FOM engine.

Seed for feature #3 (IGV 錯殺抄底). Reuses the EXISTING FOM dimensions
(scoring.fom_alpha.score_ticker_alpha) on an IGV-representative software universe,
then surfaces three views:
  * overall FOM-alpha rank (the engine's pick),
  * 錯殺型 / oversold-to-bottom-fish: high contrarian (逆勢) + intact moat,
    excluding only the extreme-bubble names,
  * 趨勢型 / momentum.

Recommend-only / research-and-education. Writes nothing. Data: yfinance (grade C).
No trades. The universe LIST is grounded in IGV holdings; the SCORING is the
owner's own FOM engine, not the web.

Run:
  PYTHONPATH=src .venv/Scripts/python.exe scripts/igv_software_screen.py [YYYY-MM-DD]
"""
from __future__ import annotations

import sys

import pandas as pd

from sharks.scoring.fom import fetch_monthly, INDICES, SECTOR_ETFS
from sharks.scoring.fom_alpha import score_ticker_alpha

# IGV (iShares Expanded Tech-Software ETF) representative holdings + owner's software book.
IGV_SOFTWARE = [
    "CRM", "MSFT", "ORCL", "NOW", "ADBE", "PANW", "CRWD", "INTU", "FTNT", "SNPS",
    "CDNS", "ROP", "ADSK", "WDAY", "TEAM", "DDOG", "NET", "ZS", "HUBS", "PLTR",
    "APP", "SNOW", "MDB", "DOCU", "GTLB", "PATH", "ZM", "DOCN", "APPN", "S",
    "OKTA", "TWLO", "DT", "ESTC", "CFLT", "AI",
]
# Owner's current software-ish holdings (P1/P2 + the broker screenshot) — for the ★ tag.
HOLDINGS = {"CRM", "NOW", "ORCL", "WDAY", "MSFT", "DDOG", "ZM", "DOCN", "PATH", "APPN"}


def _fmt(r: dict) -> str:
    own = "*" if r["ticker"] in HOLDINGS else " "
    rr = f"{r['ret_3m']:+.0%}" if r.get("ret_3m") is not None else "  n/a"
    return (f"  {own}{r['ticker']:5} FOMa={r['final_fom_alpha']:6.1f}  mom={r['momentum']:5.1f}  "
            f"contrarian={r['contrarian']:5.1f}  bubble={r['bubble_guard']:6.1f}  "
            f"moat={r['ip_defensibility']:3}  3m={rr}")


def main() -> int:
    as_of = pd.Timestamp(sys.argv[1]) if len(sys.argv) > 1 else pd.Timestamp.today().normalize()
    start = (as_of - pd.Timedelta(days=6 * 365)).strftime("%Y-%m-%d")
    uni = sorted(set(IGV_SOFTWARE) | set(INDICES) | set(SECTOR_ETFS))
    print(f"IGV software screen as of {as_of.date()} — {len(IGV_SOFTWARE)} names", file=sys.stderr)
    closes = fetch_monthly(uni, start, as_of.strftime("%Y-%m-%d"))

    rows: list[dict] = []
    for t in IGV_SOFTWARE:
        if t not in closes.columns or closes[t].dropna().empty:
            continue
        try:
            r = score_ticker_alpha(closes, t, as_of)
        except Exception:
            continue
        s = closes[t].dropna()
        r["ret_3m"] = round(float(s.iloc[-1] / s.iloc[-4] - 1), 3) if len(s) >= 4 else None
        rows.append(r)

    print(f"  scored {len(rows)}/{len(IGV_SOFTWARE)} names\n")

    print("=== Today's software — overall FOM-alpha rank (* = your holding) ===")
    for r in sorted(rows, key=lambda x: x["final_fom_alpha"], reverse=True)[:12]:
        print(_fmt(r))

    print("\n=== 錯殺型 oversold-to-bottom-fish (contrarian-led, moat>=50, not extreme-bubble) ===")
    oversold = [r for r in rows if r["bubble_guard"] > -60 and r["ip_defensibility"] >= 50]
    for r in sorted(oversold, key=lambda x: x["contrarian"], reverse=True)[:8]:
        print(_fmt(r))

    print("\n=== 趨勢型 momentum (mom>=60, not extreme-bubble) ===")
    trend = [r for r in rows if r["momentum"] >= 60 and r["bubble_guard"] > -50]
    for r in sorted(trend, key=lambda x: x["momentum"], reverse=True)[:8]:
        print(_fmt(r))
    return 0


if __name__ == "__main__":
    sys.exit(main())
