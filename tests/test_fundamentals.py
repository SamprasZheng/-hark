"""Tests for the fundamentals tracker (pure derive logic) + fundamentals prior."""

from __future__ import annotations

import pandas as pd

from sharks.scoring.fundamentals import detect_flips, gross_margin_yoy_delta, inflection_flags
from sharks.scoring.bayesian_update import prior_from_fundamentals


class TestInflectionFlags:
    def test_improving_high_score(self):
        f = {"revenue_growth_yoy": 0.15, "earnings_growth_yoy": 0.30,
             "operating_margin": 0.25, "fcf": 5e9, "gross_margin_yoy_delta": 0.02}
        fl = inflection_flags(f)
        assert fl["turnaround_score"] == 5
        assert fl["margin_inflecting_up"] is True

    def test_declining_low_score(self):
        f = {"revenue_growth_yoy": -0.05, "earnings_growth_yoy": -0.20,
             "operating_margin": -0.02, "fcf": -1e9, "gross_margin_yoy_delta": -0.013}
        fl = inflection_flags(f)
        assert fl["turnaround_score"] == 0
        assert fl["margin_inflecting_up"] is False

    def test_missing_fields_safe(self):
        fl = inflection_flags({})
        assert fl["turnaround_score"] == 0


class TestGrossMarginDelta:
    def test_inflection_up(self):
        # 5 quarters; latest GM 0.42, year-ago 0.40 → +0.02
        cols = pd.date_range("2025-02-28", periods=5, freq="-91D")
        df = pd.DataFrame(
            {c: {"Gross Profit": gp, "Total Revenue": 100.0}
             for c, gp in zip(cols, [42, 41, 40, 40, 40])}
        )
        d = gross_margin_yoy_delta(df)
        assert d is not None and abs(d - 0.02) < 1e-6

    def test_insufficient_quarters(self):
        df = pd.DataFrame({pd.Timestamp("2025-02-28"): {"Gross Profit": 42.0, "Total Revenue": 100.0}})
        assert gross_margin_yoy_delta(df) is None

    def test_missing_rows(self):
        df = pd.DataFrame({pd.Timestamp("2025-02-28"): {"Net Income": 10.0}})
        assert gross_margin_yoy_delta(df) is None


class TestPriorFromFundamentals:
    def test_improving_beats_declining(self):
        good = {"revenue_growth_yoy": 0.25, "gross_margin_yoy_delta": 0.03,
                "operating_margin": 0.25, "fcf": 5e9}
        bad = {"revenue_growth_yoy": -0.10, "gross_margin_yoy_delta": -0.02,
               "operating_margin": -0.05, "fcf": -1e9}
        assert prior_from_fundamentals(good) > prior_from_fundamentals(bad)

    def test_clamped(self):
        extreme = {"revenue_growth_yoy": 5.0, "gross_margin_yoy_delta": 0.5,
                   "operating_margin": 0.9, "fcf": 1e11}
        p = prior_from_fundamentals(extreme)
        assert 0.05 <= p <= 0.95

    def test_margin_inflection_moves_prior(self):
        base = {"revenue_growth_yoy": 0.05, "operating_margin": 0.10, "fcf": 1e9}
        with_inflect = dict(base, gross_margin_yoy_delta=0.03)
        assert prior_from_fundamentals(with_inflect) > prior_from_fundamentals(base)

    def test_empty_is_neutral_ish(self):
        p = prior_from_fundamentals({})
        assert 0.3 <= p <= 0.6


class TestDetectFlips:
    def test_turnaround_and_margin_flip(self):
        prev = [{"ticker": "NKE", "flags": {"turnaround_score": 1, "margin_inflecting_up": False,
                                            "earnings_growing": False, "revenue_growing": True}}]
        curr = [{"ticker": "NKE", "flags": {"turnaround_score": 3, "margin_inflecting_up": True,
                                            "earnings_growing": True, "revenue_growing": True},
                 "gross_margin_yoy_delta": 0.01}]
        flips = detect_flips(prev, curr)
        assert len(flips) == 1 and flips[0]["ticker"] == "NKE"
        assert any("gross-margin" in r for r in flips[0]["flips"])
        assert any("turnaround_score 1→3" in r for r in flips[0]["flips"])

    def test_no_flip_when_unchanged(self):
        rows = [{"ticker": "X", "flags": {"turnaround_score": 3, "margin_inflecting_up": True,
                                          "earnings_growing": True, "revenue_growing": True}}]
        assert detect_flips(rows, rows) == []

    def test_new_ticker_not_a_flip(self):
        # a ticker absent from the prior snapshot is not a flip (no baseline to compare)
        assert detect_flips([], [{"ticker": "Y", "flags": {"turnaround_score": 4}}]) == []

    def test_deterioration_not_a_flip(self):
        prev = [{"ticker": "Z", "flags": {"turnaround_score": 4, "margin_inflecting_up": True}}]
        curr = [{"ticker": "Z", "flags": {"turnaround_score": 2, "margin_inflecting_up": False}}]
        assert detect_flips(prev, curr) == []
