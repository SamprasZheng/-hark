"""Tests for the DD-tilt IC backtest (pure logic; no network)."""

from __future__ import annotations

from sharks.backtest.tech_dd_validation import _interpret_dd, tilted_fom
from sharks.scoring.fom import FOMScore


def _score(ticker, momentum=50, contrarian=50, cyclic=50, quality=50, bg=0.0):
    return FOMScore(
        ticker=ticker, as_of="2020-01-01", sector_etf=None,
        momentum=momentum, contrarian=contrarian, cyclic=cyclic,
        quality=quality, bubble_guard_val=bg,
    )


class TestTiltedFom:
    def test_uncovered_is_noop(self):
        s = _score("ZZZZ", momentum=90)
        assert tilted_fom(s) == s.final_fom

    def test_guohuo_high_momentum_name_drops(self):
        # AXTI = 過熱 (tilt momentum −0.06). A high-momentum name loses FOM when its
        # momentum weight is cut.
        s = _score("AXTI", momentum=90, contrarian=20, cyclic=20, quality=20, bg=-50)
        assert tilted_fom(s) < s.final_fom

    def test_zhibian_high_quality_name_rises(self):
        # LLY = 質變 (tilt quality +0.03, momentum +0.03). A high-quality name gains.
        s = _score("LLY", momentum=50, contrarian=20, cyclic=20, quality=95, bg=0)
        assert tilted_fom(s) > s.final_fom


class TestInterpret:
    def test_adds(self):
        by_h = {"3m": {"delta_ic_ir": 0.8}, "6m": {"delta_ic_ir": 0.6}, "12m": {"delta_ic_ir": 0.7}}
        assert "ADDS-IC" in _interpret_dd(by_h)["verdict"]

    def test_hurts(self):
        by_h = {"3m": {"delta_ic_ir": -0.7}, "6m": {"delta_ic_ir": -0.9}}
        assert "HURTS-IC" in _interpret_dd(by_h)["verdict"]

    def test_neutral(self):
        by_h = {"3m": {"delta_ic_ir": 0.1}, "6m": {"delta_ic_ir": -0.1}}
        assert "NEUTRAL" in _interpret_dd(by_h)["verdict"]

    def test_inconclusive_when_empty(self):
        by_h = {"3m": {"delta_ic_ir": None}}
        assert _interpret_dd(by_h)["verdict"] == "INCONCLUSIVE"
