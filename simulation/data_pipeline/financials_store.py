#!/usr/bin/env python3
"""
Trading Society -- financials store (read local parquet -> real metrics) (review B/D)

PPST Declaration (this PROGRAM):
- PROJECT: Trading Society
- PROGRAM: simulation/data_pipeline/financials_store.py
- SKILL:   read the local Polygon-financials parquet -> PIT real fundamental metrics
- TARGET:  Serve REAL fundamental metrics (OCF growth + margin, investing-intensity
           1st/2nd derivative as the capex proxy, FCF-from-OCF, ROIC = NI/(equity+
           debt)) from the local parquet. PIT via filing_date. No network at read
           time -- reduces API dependency. Returns {} when no data (caller falls
           back to a flagged proxy).

Honest: Polygon exposes no pure capex line, so "capex" here = INVESTING-CASH-FLOW
INTENSITY (|investing_cf| / revenue). For capital-intensive names that is close to
capex; for cash-rich names (e.g. NVDA buying securities) it overstates capex. The
field is labelled `capex_proxy_source: investing_cf`.
"""

from __future__ import annotations

import glob
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

_ROOT = Path(__file__).resolve().parents[2]
FIN_DIR = _ROOT / "data" / "financials"


def _latest_parquet() -> Optional[Path]:
    files = sorted(glob.glob(str(FIN_DIR / "financials-*.parquet")))
    return Path(files[-1]) if files else None


class FinancialsStore:
    def __init__(self):
        self._df = None
        try:
            import pandas as pd
            p = _latest_parquet()
            if p is not None:
                self._df = pd.read_parquet(p)
        except Exception:
            self._df = None

    @property
    def available(self) -> bool:
        return self._df is not None and not self._df.empty

    def cache_path(self) -> Optional[str]:
        p = _latest_parquet()
        return str(p.relative_to(_ROOT)) if p else None

    def _rows(self, ticker: str, as_of: Optional[str]) -> List[Dict[str, Any]]:
        if not self.available:
            return []
        d = self._df[self._df["ticker"] == ticker].copy()
        d = d[d["filing_date"].notna()]
        if as_of:
            d = d[d["filing_date"] <= as_of]
        if d.empty:
            return []
        d = d.sort_values("end_date")
        return d.to_dict("records")

    @staticmethod
    def _yoy(series: List[Optional[float]], i: int) -> Optional[float]:
        if i - 4 < 0:
            return None
        a, b = series[i], series[i - 4]
        if a is None or b is None or b == 0:
            return None
        return a / abs(b) - 1.0 if b > 0 else None

    def metrics(self, ticker: str, as_of: Optional[str] = None) -> Dict[str, Any]:
        rows = self._rows(ticker, as_of)
        if len(rows) < 5:
            return {}

        def col(k):
            return [r.get(k) for r in rows]
        rev, ni, ocf, inv, eq, dbt = (col("revenue"), col("net_income"), col("ocf"),
                                      col("investing_cf"), col("equity"),
                                      col("long_term_debt"))
        n = len(rows)
        last = n - 1

        # investing-intensity (capex proxy) = |investing_cf| / revenue
        inv_int = [abs(inv[i]) / rev[i] if (inv[i] is not None and rev[i] and rev[i] > 0)
                   else None for i in range(n)]
        cap_g = self._yoy(inv_int, last)
        cap_g_prev = self._yoy(inv_int, last - 1)
        cap_accel = (cap_g - cap_g_prev) if (cap_g is not None and cap_g_prev is not None) else None

        ocf_yoy = self._yoy(ocf, last)
        ocf_margin = (ocf[last] / rev[last]) if (ocf[last] is not None and rev[last] and rev[last] > 0) else None
        rev_yoy = self._yoy(rev, last)
        net_margin = (ni[last] / rev[last]) if (ni[last] is not None and rev[last] and rev[last] > 0) else None

        # TTM ROIC = sum(last 4 NI) / (equity + long_term_debt)
        ni4 = [x for x in ni[-4:] if x is not None]
        ttm_ni = sum(ni4) if len(ni4) == 4 else None
        invested = None
        if eq[last] is not None:
            invested = eq[last] + (dbt[last] or 0.0)
        roic = (ttm_ni / invested) if (ttm_ni is not None and invested and invested > 0) else None
        # ROIC 4q ago for trend
        roic_prev = None
        if n >= 8:
            ni4p = [x for x in ni[-8:-4] if x is not None]
            ttm_ni_p = sum(ni4p) if len(ni4p) == 4 else None
            inv_p = (eq[last - 4] + (dbt[last - 4] or 0.0)) if eq[last - 4] is not None else None
            roic_prev = (ttm_ni_p / inv_p) if (ttm_ni_p is not None and inv_p and inv_p > 0) else None
        roic_trend = (roic - roic_prev) if (roic is not None and roic_prev is not None) else None

        return {
            "source": "polygon_real", "filing_date": rows[last].get("filing_date"),
            "fiscal": rows[last].get("fiscal"), "n_quarters": n,
            "revenue_yoy": _r(rev_yoy), "net_margin": _r(net_margin),
            "ocf_margin": _r(ocf_margin), "ocf_yoy": _r(ocf_yoy),
            "capex_proxy_source": "investing_cf",
            "capex_intensity": _r(inv_int[last]), "capex_growth_yoy": _r(cap_g),
            "capex_acceleration": _r(cap_accel),
            "roic": _r(roic), "roic_trend": _r(roic_trend),
            "fcf_proxy_ocf_margin": _r(ocf_margin),
        }

    def sleeve_capex_score(self, tickers: List[str], as_of: Optional[str] = None
                           ) -> Dict[str, Any]:
        """0-100 capex-momentum from real investing-intensity growth+acceleration."""
        gs, accs = [], []
        for t in tickers:
            m = self.metrics(t, as_of)
            if m and m.get("capex_growth_yoy") is not None:
                gs.append(m["capex_growth_yoy"])
                if m.get("capex_acceleration") is not None:
                    accs.append(m["capex_acceleration"])
        if not gs:
            return {}
        g = sorted(gs)[len(gs) // 2]
        a = sorted(accs)[len(accs) // 2] if accs else 0.0
        score = max(0.0, min(100.0, (g + 0.20) / 0.60 * 100 + a * 75))
        return {"score_0_100": round(score, 1), "median_capex_growth": round(g, 4),
                "median_capex_accel": round(a, 4), "n_names": len(gs),
                "source": "polygon_real(investing_cf intensity)"}


def _r(x, nd: int = 4):
    return round(x, nd) if isinstance(x, (int, float)) else None


# module-level singleton
_STORE: Optional[FinancialsStore] = None


def store() -> FinancialsStore:
    global _STORE
    if _STORE is None:
        _STORE = FinancialsStore()
    return _STORE


def _demo() -> int:
    import json
    s = store()
    print("financials_store:", "available" if s.available else "NO DATA (run pull_financials)",
          "|", s.cache_path())
    if s.available:
        for t in ["NVDA", "KLAC", "LMT", "AAPL", "MSFT"]:
            print(f"\n{t}:", json.dumps(s.metrics(t), ensure_ascii=False))
        print("\nAI-infra sleeve capex score:",
              json.dumps(s.sleeve_capex_score(["NVDA", "AVGO", "AMAT", "LRCX", "KLAC", "AMD"]),
                         ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(_demo())
