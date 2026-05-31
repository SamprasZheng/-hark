"""Deterministic, offline tests for the RF/PM/analog cycle tracker (variable #15).

No network: the price tape is either injected or skipped (network=False), and the
hard-evidence layer is the seeded DEFAULT_EVIDENCE / an injected list. Pins the
two-door state machine and the evidence scoring.

Model spec: tech/rf-connectivity.md §0 (the two-door read) + variable #15.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from sharks.scoring import rfpm_cycle as rf

THR = rf.DEFAULT_THRESHOLDS


# ── evidence scoring ──────────────────────────────────────────────────────────
class TestEvidenceScore:
    def test_seeded_leading_is_strongly_positive(self):
        ev = rf.load_evidence("2026-05-31", evidence_path=Path("does-not-exist.json"))
        assert rf.score_evidence(ev, "leading") >= 0.8   # B:B>1 + hikes + lean inventory

    def test_seeded_lagging_is_negative(self):
        ev = rf.load_evidence("2026-05-31", evidence_path=Path("does-not-exist.json"))
        assert rf.score_evidence(ev, "lagging") < 0       # handset memory-shock drag

    def test_point_in_time_filters_future_evidence(self):
        # Nothing dated on/before 2020 → empty → neutral 0.0
        ev = rf.load_evidence("2020-01-01", evidence_path=Path("does-not-exist.json"))
        assert ev == []
        assert rf.score_evidence(ev, "leading") == 0.0

    def test_bounds(self):
        ev = rf.load_evidence("2026-05-31", evidence_path=Path("does-not-exist.json"))
        for door in ("leading", "lagging"):
            s = rf.score_evidence(ev, door)
            assert -1.0 <= s <= 1.0


# ── the two-door state machine ────────────────────────────────────────────────
class TestClassifyDoor:
    def test_rush_restock_fires_on_evidence_before_price(self):
        # The whole point of variable #15: the order book turns before the tape.
        assert rf.classify_door(50.0, 1.0, THR, 10.0) == rf.RUSH_RESTOCK

    def test_expansion_when_price_confirms(self):
        assert rf.classify_door(70.0, 1.0, THR, 10.0) == rf.EXPANSION

    def test_overheat_on_parabolic_extended(self):
        assert rf.classify_door(80.0, 1.0, THR, 40.0) == rf.OVERHEAT

    def test_rollover_on_negative_evidence_weak_price(self):
        assert rf.classify_door(40.0, -0.5, THR, -10.0) == rf.ROLLOVER

    def test_destock_on_mild_negative(self):
        assert rf.classify_door(50.0, -0.25, THR, 0.0) == rf.DESTOCK

    def test_neutral_when_flat(self):
        assert rf.classify_door(50.0, 0.0, THR, 0.0) == rf.NEUTRAL

    def test_none_price_defaults_to_50(self):
        # evidence-only mode (no tape) must still classify on evidence
        assert rf.classify_door(None, 1.0, THR, None) == rf.RUSH_RESTOCK


# ── full reading (evidence-only, no network) ──────────────────────────────────
class TestRunEvidenceOnly:
    def test_two_doors_diverge(self):
        # The signature thesis result: leading door rushing, handset door destocking.
        reading = rf.run(as_of="2026-05-31", network=False, include_auto=False)
        assert reading.leading_door["state"] == rf.RUSH_RESTOCK
        assert reading.lagging_door["state"] == rf.DESTOCK
        assert reading.state == rf.RUSH_RESTOCK            # headline = leading door
        assert reading.evidence_score_leading > 0
        assert reading.evidence_score_lagging < 0

    def test_segments_present_without_prices(self):
        reading = rf.run(as_of="2026-05-31", network=False, include_auto=False)
        assert set(reading.segments) == set(rf.SEGMENTS)
        # no tape → no price score
        assert reading.segments["power_analog"]["score"] is None

    def test_output_roundtrips(self, tmp_path):
        reading = rf.run(as_of="2026-05-31", network=False, include_auto=False)
        path = rf.write_output(tmp_path, reading)
        assert path.exists()
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["schema_version"] == 1
        assert payload["recommend_only"] is True
        assert payload["as_of"] == "2026-05-31"
        assert payload["leading_door"]["state"] == rf.RUSH_RESTOCK


# ── build_reading with an injected price tape ─────────────────────────────────
class TestBuildReadingWithPrices:
    def _seg(self, name, door, score, mom6):
        return rf.SegmentSignal(name, door, 3, 3, None, mom6, None, None, None, score, {})

    def test_strong_leading_tape_gives_expansion(self):
        segs = {
            "power_analog":  self._seg("power_analog", "leading", 72.0, 12.0),
            "connectivity":  self._seg("connectivity", "leading", 68.0, 10.0),
            "picks_shovels": self._seg("picks_shovels", "leading", 80.0, 20.0),
            "distributors":  self._seg("distributors", "leading", 65.0, 8.0),
            "handset_rffe":  self._seg("handset_rffe", "lagging", 40.0, -5.0),
        }
        ev = rf.load_evidence("2026-05-31", evidence_path=Path("nope.json"))
        reading = rf.build_reading(segs, ev, "2026-05-31", THR)
        assert reading.leading_door["state"] == rf.EXPANSION   # evidence+price both strong
        # handset door diverges weak (negative evidence + soft tape)
        assert reading.lagging_door["state"] in (rf.DESTOCK, rf.ROLLOVER, rf.NEUTRAL)


# ── CLI wiring ────────────────────────────────────────────────────────────────
class TestCLIWiring:
    def test_rf_cycle_subcommand_parses(self):
        from sharks.cli import build_parser
        ns = build_parser().parse_args(["rf-cycle", "--no-network", "--dry-run"])
        assert ns.command == "rf-cycle" and ns.no_network is True and ns.dry_run is True

    def test_rf_cycle_dry_run_exits_zero(self):
        from sharks.cli import main
        # --no-network avoids yfinance; --dry-run avoids writing outputs/
        assert main(["rf-cycle", "--no-network", "--dry-run"]) == 0

    def test_rf_evidence_subcommand_parses(self):
        from sharks.cli import build_parser
        ns = build_parser().parse_args(["rf-evidence", "--no-network"])
        assert ns.command == "rf-evidence" and ns.no_network is True


# ── auto-evidence merge (curated always overrides the auto proxy layer) ────────
class TestEvidenceMerge:
    def test_auto_layer_fills_uncovered_keys(self, tmp_path):
        curated = tmp_path / "curated.json"
        auto = tmp_path / "auto.json"
        curated.write_text(json.dumps([
            {"key": "list_price_hikes", "door": "leading", "signal": 1, "weight": 1.0, "as_of": "2026-05-31"},
        ]), encoding="utf-8")
        auto.write_text(json.dumps([
            {"key": "list_price_hikes", "door": "leading", "signal": -1, "weight": 1.0, "as_of": "2026-05-31", "grade": "C"},
            {"key": "auto_only_proxy", "door": "leading", "signal": 1, "weight": 0.5, "as_of": "2026-05-31", "grade": "C"},
        ]), encoding="utf-8")
        ev = rf.load_evidence("2026-05-31", evidence_path=curated, auto_path=auto)
        by_key = {e["key"]: e for e in ev}
        # curated wins the shared key (signal +1, not the auto -1)
        assert by_key["list_price_hikes"]["signal"] == 1
        # auto-only key is merged in
        assert by_key["auto_only_proxy"]["signal"] == 1

    def test_include_auto_false_ignores_auto(self, tmp_path):
        auto = tmp_path / "auto.json"
        auto.write_text(json.dumps([
            {"key": "auto_only_proxy", "door": "leading", "signal": 1, "weight": 1.0, "as_of": "2026-05-31"},
        ]), encoding="utf-8")
        ev = rf.load_evidence("2026-05-31", evidence_path=tmp_path / "nope.json",
                              auto_path=auto, include_auto=False)
        assert all(e["key"] != "auto_only_proxy" for e in ev)


# ── financial-proxy derivation (pure, offline) ────────────────────────────────
class TestEvidenceFetchDerive:
    def test_positive_revenue_yoy_gives_plus_one(self):
        from sharks.scoring import rfpm_evidence_fetch as fe
        fundamentals = {
            "ARW": {"revenue_growth_yoy": 0.08}, "AVT": {"revenue_growth_yoy": 0.04},
        }
        rows = fe.derive_financial_proxies(fundamentals, "2026-05-31")
        btb = next(r for r in rows if r["key"] == "distributor_book_to_bill")
        assert btb["signal"] == 1 and btb["grade"] == "C" and btb["auto"] is True

    def test_negative_margin_delta_gives_minus_one(self):
        from sharks.scoring import rfpm_evidence_fetch as fe
        fundamentals = {
            "TXN": {"gross_margin_yoy_delta": -0.02}, "ADI": {"gross_margin_yoy_delta": -0.01},
            "MCHP": {"gross_margin_yoy_delta": -0.03},
        }
        rows = fe.derive_financial_proxies(fundamentals, "2026-05-31")
        hike = next(r for r in rows if r["key"] == "list_price_hikes")
        assert hike["signal"] == -1

    def test_no_data_drops_the_proxy(self):
        from sharks.scoring import rfpm_evidence_fetch as fe
        # empty fundamentals → no usable tickers → no entries emitted (no fake 0)
        rows = fe.derive_financial_proxies({}, "2026-05-31")
        assert rows == []

    def test_deadband_gives_zero(self):
        from sharks.scoring import rfpm_evidence_fetch as fe
        rows = fe.derive_financial_proxies({"QRVO": {"revenue_growth_yoy": 0.0},
                                            "SWKS": {"revenue_growth_yoy": -0.01}}, "2026-05-31")
        h = next(r for r in rows if r["key"] == "handset_demand")
        assert h["signal"] == 0   # mean -0.005 is within [-0.03, 0.0] deadband edge → 0
