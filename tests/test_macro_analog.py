"""Offline tests for the macro-analog mechanism-set matcher.

Verifies the decision-support contract from
`philosophy/concepts/macro-analog-matching.md` (proposed):
  - mechanism-set overlap, not high-dim clustering
  - ranked distribution output, not a single nearest-neighbour label
  - output NEVER carries a prediction-flavoured key (probability/direction/...)
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from sharks.regime.macro_analog import (
    BANNED_OUTPUT_KEYS,
    cube_distance,
    load_events,
    match,
    mechanism_overlap,
)

# Path to the real curated events shipped in the repo.
REPO_EVENTS = Path(__file__).resolve().parent.parent / "data" / "macro_analog_events"


def _write_event(d: Path, event_id: str, mechanisms: list[str], cube: dict | None = None) -> None:
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{event_id}.json").write_text(
        json.dumps({
            "event_id": event_id,
            "label": f"label {event_id}",
            "period": "test",
            "mechanisms": mechanisms,
            "regime_cube": cube or {},
            "trigger": "t",
            "outcomes": {"t_plus_1y": "x"},
        }),
        encoding="utf-8",
    )


class TestLoadRealEvents:
    def test_repo_ships_curated_events(self):
        events = load_events(REPO_EVENTS)
        ids = {e["event_id"] for e in events}
        assert "2000-dotcom" in ids
        assert "2008-subprime" in ids

    def test_each_event_has_mechanisms(self):
        for e in load_events(REPO_EVENTS):
            assert isinstance(e["mechanisms"], list) and e["mechanisms"]

    def test_missing_dir_is_safe(self, tmp_path: Path):
        assert load_events(tmp_path / "nope") == []


class TestMechanismOverlap:
    def test_counts_shared(self):
        event = {"event_id": "x", "mechanisms": ["a", "b", "c"]}
        ov = mechanism_overlap(["b", "c", "d"], event)
        assert ov["overlap_count"] == 2
        assert ov["overlapping_mechanisms"] == ["b", "c"]

    def test_case_insensitive(self):
        event = {"event_id": "x", "mechanisms": ["Fed_Tightening", "X"]}
        ov = mechanism_overlap(["fed_tightening"], event)
        assert ov["overlap_count"] == 1

    def test_jaccard(self):
        event = {"event_id": "x", "mechanisms": ["a", "b"]}
        ov = mechanism_overlap(["a", "b"], event)
        assert ov["jaccard"] == 1.0


class TestCubeDistance:
    def test_identical_is_zero(self):
        c = {"growth": "g", "inflation": "i", "liquidity": "l", "credit": "c"}
        assert cube_distance(c, c) == 0

    def test_all_differ_is_four(self):
        a = {"growth": "1", "inflation": "1", "liquidity": "1", "credit": "1"}
        b = {"growth": "2", "inflation": "2", "liquidity": "2", "credit": "2"}
        assert cube_distance(a, b) == 4


class TestMatch:
    def test_ranks_by_overlap_desc(self, tmp_path: Path):
        _write_event(tmp_path, "high", ["a", "b", "c"])
        _write_event(tmp_path, "low", ["a", "z"])
        out = match(["a", "b", "c"], events_dir=tmp_path, k=5)
        ids = [m["event_id"] for m in out["matches"]]
        assert ids[0] == "high"
        assert ids[1] == "low"

    def test_drops_zero_overlap(self, tmp_path: Path):
        _write_event(tmp_path, "match", ["a"])
        _write_event(tmp_path, "nomatch", ["x", "y"])
        out = match(["a"], events_dir=tmp_path)
        ids = [m["event_id"] for m in out["matches"]]
        assert ids == ["match"]

    def test_k_limits_results(self, tmp_path: Path):
        for i in range(5):
            _write_event(tmp_path, f"e{i}", ["a"])
        out = match(["a"], events_dir=tmp_path, k=2)
        assert len(out["matches"]) == 2

    def test_output_has_no_banned_keys(self, tmp_path: Path):
        _write_event(tmp_path, "e", ["a", "b"])
        out = match(["a", "b"], events_dir=tmp_path)
        # The module asserts internally; double-check at the test boundary too.
        def walk(o):
            if isinstance(o, dict):
                for key, v in o.items():
                    assert key not in BANNED_OUTPUT_KEYS, key
                    walk(v)
            elif isinstance(o, list):
                for v in o:
                    walk(v)
        walk(out)

    def test_real_events_subprime_matches_funding_rupture(self):
        # A present that looks like a credit rupture should surface 2008.
        out = match(
            ["funding_chain_rupture", "credit_spread_widening", "leverage_unwind"],
            events_dir=REPO_EVENTS,
            k=3,
        )
        ids = [m["event_id"] for m in out["matches"]]
        assert "2008-subprime" in ids
        top = out["matches"][0]
        assert top["event_id"] == "2008-subprime"
        assert top["overlap_count"] >= 3

    def test_disclaimer_present(self):
        out = match(["fed_tightening_into_slowdown"], events_dir=REPO_EVENTS)
        assert "DECISION SUPPORT, NOT PREDICTION" in out["disclaimer"]

    def test_dotcom_shares_tightening_mechanism(self):
        # Both 2000 and 2008 carry fed_tightening_into_slowdown → both surface.
        out = match(["fed_tightening_into_slowdown"], events_dir=REPO_EVENTS, k=5)
        ids = {m["event_id"] for m in out["matches"]}
        assert {"2000-dotcom", "2008-subprime"} <= ids
