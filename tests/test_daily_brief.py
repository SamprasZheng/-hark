"""Tests for the morning brief logic (pure interpretation functions)."""

from __future__ import annotations

from sharks.daily_brief import (
    econ_calendar,
    interpret_macro,
    load_picks,
    sector_rotation,
    tw_implication,
)


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


class TestEconCalendar:
    def test_shape(self):
        ev = econ_calendar("2026-06-15")
        assert isinstance(ev, list) and len(ev) >= 1
        assert all(len(t) == 3 for t in ev)

    def test_fomc_surfaces_near_meeting(self):
        # 2026-06-17 FOMC; on 2026-06-10 it is within the 12-day window
        assert any("FOMC" in e for _, e, _ in econ_calendar("2026-06-10"))

    def test_quiet_week_has_fallback(self):
        ev = econ_calendar("2026-06-25")  # no NFP/CPI/FOMC nearby
        assert len(ev) >= 1  # fallback row always present


class TestLoadPicks:
    def test_empty_dir(self, tmp_path):
        pk = load_picks(tmp_path)
        assert pk["have_fom"] is False and pk["have_audit"] is False
        assert pk["potential"] == []
        assert "P1_SELL" in pk["exit"] and "P2_ADD" in pk["enter"]
