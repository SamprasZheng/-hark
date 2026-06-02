"""Tests for the daily portfolio health-check + evidence-gate discipline."""

from __future__ import annotations

import pytest

from sharks.daily_health_check import (
    EVIDENCE_DIMENSIONS,
    evidence_gate,
    mature_analyst_posture,
    scan_hotspots,
    _position_health,
)


def _full_evidence(grade="A"):
    return {dim: {"confirmed": True, "grade": grade} for dim in EVIDENCE_DIMENSIONS}


class TestEvidenceGateOffense:
    def test_full_evidence_authorises_offense(self):
        out = evidence_gate(_full_evidence(), action="rotate_in")
        assert out["authorised"] is True
        assert out["verdict"] == "AUTHORISED"
        assert out["n_confirmed"] == 5

    def test_no_evidence_blocks_offense(self):
        out = evidence_gate({}, action="add")
        assert out["authorised"] is False
        assert "HOLD" in out["verdict"]

    def test_rumour_grade_does_not_count(self):
        # All five 'confirmed' but only C/D grade → none clear the gate.
        ev = {dim: {"confirmed": True, "grade": "D"} for dim in EVIDENCE_DIMENSIONS}
        out = evidence_gate(ev, action="rotate_in")
        assert out["n_confirmed"] == 0
        assert out["authorised"] is False

    def test_missing_earnings_blocks_offense(self):
        ev = _full_evidence()
        ev["earnings"] = {"confirmed": False}
        out = evidence_gate(ev, action="rotate_in")
        # 4/5 confirmed but earnings is mandatory → blocked.
        assert out["n_confirmed"] == 4
        assert out["authorised"] is False
        assert "earnings" in out["rationale"].lower()

    def test_four_of_five_with_earnings_and_primary_passes(self):
        ev = _full_evidence()
        ev["trade_data"] = {"confirmed": False}  # drop a non-mandatory dim
        out = evidence_gate(ev, action="rotate_in")
        assert out["n_confirmed"] == 4
        assert out["authorised"] is True

    def test_missing_primary_blocks_even_at_four(self):
        # Drop BOTH primaries (news + flow), keep volume/trade/earnings + ... only 3 left.
        ev = _full_evidence()
        ev["catalyst_news"] = {"confirmed": False}
        ev["capital_flow"] = {"confirmed": False}
        out = evidence_gate(ev, action="rotate_in")
        assert out["authorised"] is False


class TestEvidenceGateDefense:
    def test_systemic_fast_path(self):
        out = evidence_gate({}, action="trim", systemic_risk=True)
        assert out["authorised"] is True
        assert "systemic" in out["verdict"].lower()

    def test_two_signals_authorise_defense(self):
        ev = {
            "volume": {"confirmed": True, "grade": "A"},
            "capital_flow": {"confirmed": True, "grade": "B"},
        }
        out = evidence_gate(ev, action="rotate_out")
        assert out["authorised"] is True

    def test_one_signal_is_watch_only(self):
        ev = {"volume": {"confirmed": True, "grade": "A"}}
        out = evidence_gate(ev, action="trim")
        assert out["authorised"] is False
        assert out["verdict"] == "WATCH"

    def test_defense_bar_is_lower_than_offense(self):
        # Same 2-signal evidence: defense clears, offense does not. Asymmetry.
        ev = {
            "volume": {"confirmed": True, "grade": "A"},
            "earnings": {"confirmed": True, "grade": "A"},
        }
        assert evidence_gate(ev, action="rotate_out")["authorised"] is True
        assert evidence_gate(ev, action="rotate_in")["authorised"] is False


class TestEvidenceGateErrors:
    def test_unknown_action_raises(self):
        with pytest.raises(ValueError):
            evidence_gate(_full_evidence(), action="yolo")


class TestPosture:
    def test_rupture_is_max_defensive(self):
        p = mature_analyst_posture("bull_trend", "RUPTURE")
        assert p["posture"] == "MAX_DEFENSIVE"
        assert p["systemic_risk"] is True
        assert p["deploy_bear_hedges"] is True

    def test_capitulation_is_max_defensive(self):
        assert mature_analyst_posture("capitulation", "CALM")["posture"] == "MAX_DEFENSIVE"

    def test_risk_off_is_defensive(self):
        p = mature_analyst_posture("risk_off", "CALM")
        assert p["posture"] == "DEFENSIVE"
        assert p["deploy_bear_hedges"] is True

    def test_late_bull_is_cautious_not_systemic(self):
        p = mature_analyst_posture("late_bull", "CALM")
        assert p["posture"] == "NEUTRAL-CAUTIOUS"
        assert p["systemic_risk"] is False
        assert p["deploy_bear_hedges"] is False

    def test_bull_trend_is_risk_on(self):
        assert mature_analyst_posture("bull_trend", "CALM")["posture"] == "RISK_ON"

    def test_funding_stress_overrides_bull_regime(self):
        # Even a bull regime goes systemic if funding is stressed.
        p = mature_analyst_posture("bull_trend", "STRESS")
        assert p["systemic_risk"] is True


class TestHotspots:
    def test_injected_rotation(self):
        rot = {"rotating_in": ["XLK", "SOXX"], "leaders": ["XLK"],
               "rotating_out": ["XLE"], "laggards": ["XLU"]}
        out = scan_hotspots(rotation=rot)
        assert out["available"] is True
        assert out["rotating_in"] == ["XLK", "SOXX"]
        assert "evidence_gate" in out["note"]

    def test_no_data_degrades_gracefully(self):
        out = scan_hotspots()
        assert out["available"] is False


class TestPositionHealth:
    def test_none_audit_degrades(self):
        assert _position_health(None)["available"] is False

    def test_buckets_and_decay_surface(self):
        audit = {
            "portfolio_1_audit": [
                {"ticker": "LABU", "verdict": "SELL"},
                {"ticker": "TARK", "verdict": "TRIM-25%"},
                {"ticker": "PG", "verdict": "HOLD"},
            ],
            "p1_leveraged_audit": [
                {"ticker": "LABU", "factor": 3, "annual_decay_pct": 60.8, "verdict": "SELL"},
                {"ticker": "TARK", "factor": 2, "annual_decay_pct": 20.2, "verdict": "TRIM"},
            ],
            "concentration_context": {"note": "RSU dominates"},
        }
        h = _position_health(audit)
        assert [r["ticker"] for r in h["sell_candidates"]] == ["LABU"]
        assert [r["ticker"] for r in h["trim_candidates"]] == ["TARK"]
        assert [r["ticker"] for r in h["hold"]] == ["PG"]
        # worst-decay first
        assert h["worst_decay_leveraged"][0]["ticker"] == "LABU"
        # leveraged decay flag merged onto the SELL entry
        assert h["sell_candidates"][0]["decay_pct"] == 60.8
