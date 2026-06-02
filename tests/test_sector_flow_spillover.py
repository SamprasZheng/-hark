"""Tests for the sector_flow spillover/broadening extensions (synthetic prices)."""

from __future__ import annotations

import numpy as np
import pandas as pd

from sharks.regime.sector_flow import (
    SECTOR_ETFS,
    broadening_score,
    semis_spillover_flag,
)


def _closes(trends: dict, n=8, start=100.0):
    """Build a monthly close frame: trends maps ticker -> monthly growth rate."""
    idx = pd.date_range("2025-01-31", periods=n, freq="ME")
    data = {}
    for t, g in trends.items():
        data[t] = [start * ((1 + g) ** i) for i in range(n)]
    return pd.DataFrame(data, index=idx)


class TestBroadening:
    def test_broad_market_high_score(self):
        # every sector beats SPY → broadening 100%
        trends = {e: 0.05 for e in SECTOR_ETFS}
        trends["SPY"] = 0.0
        closes = _closes(trends)
        b = broadening_score(closes, closes.index[-1])
        assert b["broadening_score"] == 100.0

    def test_narrow_market_low_score(self):
        # only SOXX beats SPY → low broadening
        trends = {e: -0.02 for e in SECTOR_ETFS}
        trends["SOXX"] = 0.10
        trends["SPY"] = 0.0
        closes = _closes(trends)
        b = broadening_score(closes, closes.index[-1])
        assert b["broadening_score"] is not None and b["broadening_score"] < 30


class TestSemisSpillover:
    def test_spillover_fires_when_soxx_leads_and_downstream_rotating_in(self):
        # SOXX strong long-horizon (leader); XLI accelerating recently (rotating_in)
        n = 8
        trends = {e: 0.0 for e in SECTOR_ETFS}
        trends["SPY"] = 0.0
        trends["SOXX"] = 0.06           # persistent leader
        closes = _closes(trends, n=n)
        # XLI dips then SURGES in the last month → 1m RS (+12.8%) > 3m RS (+9.3%),
        # both > 0 → classified rotating_in (accel > 0).
        closes["XLI"] = [100, 99, 98, 97, 96, 95, 94, 106][:n]
        out = semis_spillover_flag(closes, closes.index[-1])
        assert out["soxx_leader"] is True
        assert "XLI" in out["downstream_rotating_in"]
        assert out["semis_spillover"] is True

    def test_no_spillover_when_soxx_not_leading(self):
        trends = {e: 0.0 for e in SECTOR_ETFS}
        trends["SPY"] = 0.0
        trends["XLV"] = 0.08            # health care leads, not semis
        closes = _closes(trends)
        out = semis_spillover_flag(closes, closes.index[-1])
        assert out["semis_spillover"] is False
