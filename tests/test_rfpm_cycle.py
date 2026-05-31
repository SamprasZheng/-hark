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
        reading = rf.run(as_of="2026-05-31", network=False)
        assert reading.leading_door["state"] == rf.RUSH_RESTOCK
        assert reading.lagging_door["state"] == rf.DESTOCK
        assert reading.state == rf.RUSH_RESTOCK            # headline = leading door
        assert reading.evidence_score_leading > 0
        assert reading.evidence_score_lagging < 0

    def test_segments_present_without_prices(self):
        reading = rf.run(as_of="2026-05-31", network=False)
        assert set(reading.segments) == set(rf.SEGMENTS)
        # no tape → no price score
        assert reading.segments["power_analog"]["score"] is None

    def test_output_roundtrips(self, tmp_path):
        reading = rf.run(as_of="2026-05-31", network=False)
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
