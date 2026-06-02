"""Auto-refresh the rf-cycle evidence layer from financials (monthly job).

Variable #15's hard signals (book-to-bill, list-price hikes, channel-inventory
days) live in **earnings transcripts and distributor reports, not in any free
API**. What IS auto-fetchable from the financial statements is a set of
**quantitative proxies** that move with the same cycle:

  | curated signal (hand)        | auto proxy (this module)                         |
  |------------------------------|--------------------------------------------------|
  | distributor book-to-bill     | ARW/AVT revenue YoY  (distributors growing ⇒ B:B>1) |
  | list-price hikes             | TXN/ADI/MCHP gross-margin YoY Δ (margins up ⇒ pricing power) |
  | analog broad recovery        | ADI/NXPI/MPWR/DIOD revenue YoY                   |
  | handset demand (lagging)     | QRVO/SWKS revenue YoY                            |

These auto entries are graded **C** (financial proxy) and written to
``outputs/rfpm-cycle-evidence-auto.json``. ``rfpm_cycle.load_evidence`` merges
them UNDER the hand-curated grade-A/B ``watchlist/rfpm-cycle-evidence.json``
(curated always wins by key). So the curated file stays the source of truth;
this just keeps a fresh proxy layer so the signal never silently goes stale.

The derive logic is PURE and unit-tested offline; only ``fetch_*`` touches the
network (reuses ``scoring.fundamentals.fetch_fundamentals`` — yfinance, no key).
RECOMMEND-ONLY; this writes a proxy, not a trade.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# One proxy per curated key. `metric` is a field of scoring.fundamentals output.
PROXY_SPECS: list[dict] = [
    {"key": "distributor_book_to_bill", "door": "leading", "metric": "revenue_growth_yoy",
     "tickers": ["ARW", "AVT"], "weight": 1.0, "pos": 0.0, "neg": -0.05,
     "label": "distributor revenue YoY (ARW/AVT) — book-to-bill proxy"},
    {"key": "list_price_hikes", "door": "leading", "metric": "gross_margin_yoy_delta",
     "tickers": ["TXN", "ADI", "MCHP"], "weight": 1.0, "pos": 0.003, "neg": -0.003,
     "label": "analog gross-margin YoY Δ (TXN/ADI/MCHP) — pricing-power proxy"},
    {"key": "analog_broad_recovery", "door": "leading", "metric": "revenue_growth_yoy",
     "tickers": ["ADI", "NXPI", "MPWR", "DIOD"], "weight": 0.8, "pos": 0.0, "neg": -0.05,
     "label": "analog revenue YoY (ADI/NXPI/MPWR/DIOD) — recovery proxy"},
    {"key": "handset_demand", "door": "lagging", "metric": "revenue_growth_yoy",
     "tickers": ["QRVO", "SWKS"], "weight": 1.0, "pos": 0.0, "neg": -0.03,
     "label": "handset-RF revenue YoY (QRVO/SWKS) — handset demand proxy"},
]


def _mean(vals: list[float]) -> Optional[float]:
    vals = [v for v in vals if isinstance(v, (int, float))]
    return round(sum(vals) / len(vals), 4) if vals else None


def _signal_from_mean(mean: Optional[float], pos: float, neg: float) -> int:
    """Map a proxy mean to a cycle signal in {-1, 0, +1} with a deadband."""
    if mean is None:
        return 0
    if mean > pos:
        return 1
    if mean < neg:
        return -1
    return 0


def derive_financial_proxies(fundamentals_by_ticker: dict[str, dict],
                             as_of: str) -> list[dict]:
    """PURE: turn fetched fundamentals into auto evidence entries (grade C).

    ``fundamentals_by_ticker`` maps ticker -> the dict returned by
    ``scoring.fundamentals.fetch_fundamentals`` (or any dict carrying the
    `metric` fields). Tickers with no data are skipped; a spec with zero usable
    tickers is dropped (so we never emit a fake 0 with no basis)."""
    out: list[dict] = []
    for spec in PROXY_SPECS:
        vals = []
        for t in spec["tickers"]:
            row = fundamentals_by_ticker.get(t) or {}
            v = row.get(spec["metric"])
            if isinstance(v, (int, float)):
                vals.append(float(v))
        mean = _mean(vals)
        if mean is None:
            continue  # no basis → don't emit (curated/seed still covers the key)
        signal = _signal_from_mean(mean, spec["pos"], spec["neg"])
        pct = f"{mean*100:+.1f}%" if abs(mean) < 5 else f"{mean:+.3f}"
        out.append({
            "key": spec["key"],
            "door": spec["door"],
            "signal": signal,
            "weight": spec["weight"],
            "as_of": as_of,
            "grade": "C",
            "auto": True,
            "n": len(vals),
            "proxy_mean": mean,
            "note": f"auto proxy: {spec['label']} = {pct} (n={len(vals)})",
            "source": "auto:financials (yfinance via scoring.fundamentals)",
        })
    return out


def fetch_and_write(as_of: Optional[str] = None, out_dir: Path = Path("outputs"),
                    network: bool = True) -> Path:
    """Fetch fundamentals for all proxy tickers, derive auto evidence, write JSON.
    Network lives here; the derive is pure above."""
    as_of_str = as_of or datetime.now().strftime("%Y-%m-%d")
    tickers = sorted({t for spec in PROXY_SPECS for t in spec["tickers"]})
    fundamentals_by_ticker: dict[str, dict] = {}
    if network:
        from sharks.scoring.fundamentals import fetch_fundamentals
        for t in tickers:
            try:
                fundamentals_by_ticker[t] = fetch_fundamentals(t)
            except Exception as e:  # pragma: no cover - network
                print(f"  warn {t}: {e}", file=sys.stderr)
    entries = derive_financial_proxies(fundamentals_by_ticker, as_of_str)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "rfpm-cycle-evidence-auto.json"
    path.write_text(json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  refreshed {len(entries)} auto-evidence proxies (as_of {as_of_str})",
          file=sys.stderr)
    return path


def main(argv: Optional[list[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    as_of = next((a for a in argv if not a.startswith("-")), None) \
        or datetime.now().strftime("%Y-%m-%d")
    network = "--no-network" not in argv
    print(f"rf-cycle evidence auto-refresh (financial proxies) as of {as_of}",
          file=sys.stderr)
    path = fetch_and_write(as_of=as_of, network=network)
    print(f"wrote {path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
