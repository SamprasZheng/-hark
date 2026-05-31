"""Tests for the morning brief logic (pure interpretation functions)."""

from __future__ import annotations

from sharks.daily_brief import interpret_macro, sector_rotation, tw_implication


class TestInterpretMacro:
    def test_risk_on_and_sox_lead(self):
        moves = {"^GSPC": {"d1": 0.8}, "^VIX": {"d1": -3.0}, "^SOX": {"d1": 1.6}, "NVDA": {"d1": 2.0}}
        b = interpret_macro(moves)
        assert any("風險偏好回升" in x for x in b)
        assert any("半導體領漲" in x for x in b)
        assert any("NVDA" in x for x in b)

    def test_risk_off_and_sox_lag(self):
        moves = {"^GSPC": {"d1": -1.2}, "^VIX": {"d1": 8.0}, "^SOX": {"d1": -2.5}}
        b = interpret_macro(moves)
        assert any("避險升溫" in x for x in b)
        assert any("半導體領跌" in x for x in b)

    def test_rates_up_pressures_growth(self):
        b = interpret_macro({"^TNX": {"d1": 2.5}})
        assert any("殖利率走高" in x for x in b)

    def test_empty_safe(self):
        assert interpret_macro({}) == [] or isinstance(interpret_macro({}), list)


class TestSectorRotation:
    def test_ranked_and_flows(self):
        r = sector_rotation({"A": 2.0, "B": -1.0, "C": 0.5, "D": None})
        assert r["ranked"][0][0] == "A"
        assert "A" in r["inflow"] and "B" in r["outflow"]
        assert all(v is not None for _, v in r["ranked"])  # None dropped


class TestTwImplication:
    def test_bull(self):
        assert "偏多" in tw_implication({"^SOX": {"d1": 1.2}, "NVDA": {"d1": 2.0}})

    def test_bear(self):
        assert "補跌" in tw_implication({"^SOX": {"d1": -1.5}, "NVDA": {"d1": -2.0}})

    def test_neutral(self):
        assert "中性" in tw_implication({"^SOX": {"d1": 0.1}, "NVDA": {"d1": 0.0}})

    def test_no_data(self):
        assert "略過" in tw_implication({})
