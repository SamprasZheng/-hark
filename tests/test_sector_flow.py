"""Offline tests for the Fix E sector-flow detector. Synthetic prices, no network."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from sharks.regime.sector_flow import (
    detect_rotation,
    rank_sectors,
    relative_strength,
    sector_flow_score,
    ticker_sector_flow_score,
)

AS_OF = pd.Timestamp("2026-05-01")


def _monthly_index(n=24):
    return pd.date_range(end=AS_OF, periods=n, freq="MS")


def _series(start, monthly_growth, n=24):
    """Geometric series at a constant monthly growth rate."""
    idx = _monthly_index(n)
    vals = [start * (1 + monthly_growth) ** i for i in range(n)]
    return pd.Series(vals, index=idx)


def _frame(spec: dict[str, float]) -> pd.DataFrame:
    """spec: ticker -> monthly growth rate. SPY benchmark flat-ish at 1%."""
    data = {t: _series(100.0, g) for t, g in spec.items()}
    if "SPY" not in data:
        data["SPY"] = _series(100.0, 0.01)
    return pd.DataFrame(data)


class TestRelativeStrength:
    def test_outperformer_positive_rs(self):
        closes = _frame({"XLK": 0.05, "SPY": 0.01})
        rs = relative_strength(closes, "XLK", "SPY", AS_OF, months=3)
        assert rs is not None and rs > 0

    def test_underperformer_negative_rs(self):
        closes = _frame({"XLU": -0.02, "SPY": 0.01})
        rs = relative_strength(closes, "XLU", "SPY", AS_OF, months=3)
        assert rs is not None and rs < 0

    def test_missing_ticker_none(self):
        closes = _frame({"XLK": 0.05})
        assert relative_strength(closes, "NOPE", "SPY", AS_OF) is None


class TestRankSectors:
    def test_ranks_by_rs_desc(self):
        closes = _frame({"XLK": 0.06, "XLF": 0.03, "XLU": -0.01, "SPY": 0.01})
        ranked = rank_sectors(closes, AS_OF, sector_etfs=["XLK", "XLF", "XLU"])
        etfs = [r["etf"] for r in ranked]
        assert etfs == ["XLK", "XLF", "XLU"]
        assert ranked[0]["rank"] == 1

    def test_percentile_top_is_highest(self):
        closes = _frame({"XLK": 0.06, "XLF": 0.03, "XLU": -0.01, "SPY": 0.01})
        ranked = rank_sectors(closes, AS_OF, sector_etfs=["XLK", "XLF", "XLU"])
        assert ranked[0]["rs_percentile"] == 100.0
        assert ranked[-1]["rs_percentile"] == 0.0

    def test_drops_missing(self):
        closes = _frame({"XLK": 0.06, "SPY": 0.01})
        ranked = rank_sectors(closes, AS_OF, sector_etfs=["XLK", "GHOST"])
        assert [r["etf"] for r in ranked] == ["XLK"]


class TestDetectRotation:
    def test_leaders_and_laggards(self):
        closes = _frame({"XLK": 0.06, "XLF": 0.04, "XLI": 0.02,
                         "XLU": -0.01, "XLP": -0.03, "SPY": 0.01})
        rot = detect_rotation(closes, AS_OF,
                              sector_etfs=["XLK", "XLF", "XLI", "XLU", "XLP"])
        assert rot["leaders"][0] == "XLK"
        assert "XLP" in rot["laggards"]

    def test_rotating_in_when_short_accelerates(self):
        # Build a sector that was flat for 3m but surged in the last month.
        idx = _monthly_index(24)
        base = [100.0] * 23 + [130.0]      # +30% in the final month only
        spy = [100.0 * (1.01) ** i for i in range(24)]
        closes = pd.DataFrame({"XLE": pd.Series(base, index=idx),
                               "SPY": pd.Series(spy, index=idx)})
        rot = detect_rotation(closes, AS_OF, sector_etfs=["XLE"])
        assert "XLE" in rot["rotating_in"]

    def test_rotating_out_when_short_decelerates(self):
        idx = _monthly_index(24)
        # Was up, then dumped in the final month → short RS negative.
        base = [100.0 * (1.02) ** i for i in range(23)] + [80.0]
        spy = [100.0 * (1.01) ** i for i in range(24)]
        closes = pd.DataFrame({"XLB": pd.Series(base, index=idx),
                               "SPY": pd.Series(spy, index=idx)})
        rot = detect_rotation(closes, AS_OF, sector_etfs=["XLB"])
        assert "XLB" in rot["rotating_out"]


class TestSectorFlowScore:
    def test_leader_scores_high(self):
        closes = _frame({"XLK": 0.06, "XLF": 0.03, "XLU": -0.02, "SPY": 0.01})
        score = sector_flow_score(closes, "XLK", AS_OF)
        assert score > 60

    def test_laggard_scores_low(self):
        closes = _frame({"XLK": 0.06, "XLF": 0.03, "XLU": -0.02, "SPY": 0.01})
        score = sector_flow_score(closes, "XLU", AS_OF)
        assert score < 40

    def test_missing_neutral(self):
        closes = _frame({"XLK": 0.06, "SPY": 0.01})
        assert sector_flow_score(closes, "GHOST", AS_OF) == 50.0

    def test_ticker_resolves_via_mapping(self):
        closes = _frame({"XLK": 0.06, "XLU": -0.02, "SPY": 0.01})
        mapping = {"AAPL": "XLK", "DUK": "XLU"}
        assert ticker_sector_flow_score(closes, "AAPL", AS_OF, mapping) > 55
        assert ticker_sector_flow_score(closes, "AAPL", AS_OF, mapping) > \
               ticker_sector_flow_score(closes, "DUK", AS_OF, mapping)

    def test_unmapped_ticker_neutral(self):
        closes = _frame({"XLK": 0.06, "SPY": 0.01})
        assert ticker_sector_flow_score(closes, "AAPL", AS_OF, {}) == 50.0
