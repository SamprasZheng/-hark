"""Tests for the tech/ due-diligence → FOM overlay (tech_dd).

Pure logic + registry integrity. No network. Mirrors the bounded-tilt + sleeve
contracts from tech/fom-integration.md.
"""

from __future__ import annotations

import math

import pytest

from sharks.scoring.tech_dd import (
    DD_MAX_TILT,
    DEFAULT_BASE,
    FLAGS,
    TECH_DD,
    TECH_DD_NONUS,
    VERDICTS,
    annotate_ticker,
    build_report,
    dd_sleeve,
    dd_verdict_tilt,
)
from sharks.analysts.persona import DIMENSIONS


class TestRegistryIntegrity:
    def test_broad_coverage(self):
        # principal asked for a broad universe — assert real breadth.
        assert len(TECH_DD) >= 60
        assert len(TECH_DD_NONUS) >= 15

    def test_every_entry_is_well_formed(self):
        known_flags = set(FLAGS)
        for t, dd in TECH_DD.items():
            assert dd.ticker == t
            assert dd.verdict in VERDICTS, f"{t} bad verdict {dd.verdict}"
            assert 0.0 <= dd.milestone_score <= 1.0, f"{t} milestone out of range"
            assert set(dd.flags) <= known_flags, f"{t} unknown flag {set(dd.flags) - known_flags}"
            assert dd.trend, f"{t} missing trend"

    def test_anchor_names_present(self):
        for t in ("LLY", "MU", "IONQ", "PLTR", "NKE", "DIS", "ASTS", "LMT", "NVDA", "CHGG"):
            assert t in TECH_DD


class TestVerdictTilt:
    def test_quality_lift_for_zhibian(self):
        t = dd_verdict_tilt("質變", ())
        assert t["quality"] > 0 and t["momentum"] > 0

    def test_guohuo_dampens_momentum(self):
        assert dd_verdict_tilt("過熱", ())["momentum"] < 0

    def test_shousun_negative_both(self):
        t = dd_verdict_tilt("受損", ("loser",))
        assert t["momentum"] < 0 and t["quality"] < 0

    def test_second_derivative_rewards_contrarian(self):
        base = dd_verdict_tilt("結構", ())
        sd = dd_verdict_tilt("結構", ("second_derivative",))
        assert sd["contrarian"] > base["contrarian"]

    def test_all_dims_within_ceiling(self):
        for v in VERDICTS:
            for fl in ([], ["second_derivative", "bottom_fish"], ["front_run", "froth", "cashflow"]):
                t = dd_verdict_tilt(v, fl)
                assert set(t.keys()) == set(DIMENSIONS)
                for d in DIMENSIONS:
                    assert abs(t[d]) <= DD_MAX_TILT + 1e-9, f"{v}/{fl}/{d} exceeds ceiling"


class TestSleeveRouting:
    def test_taizao_to_moonshot(self):
        assert dd_sleeve("太早")["sleeve"] == "MOONSHOT"

    def test_guohuo_to_moonshot(self):
        assert dd_sleeve("過熱", bubble_guard=10)["sleeve"] == "MOONSHOT"

    def test_front_run_to_moonshot(self):
        r = dd_sleeve("結構", bubble_guard=10, flags=("front_run",))
        assert r["sleeve"] == "MOONSHOT"

    def test_shousun_avoid(self):
        r = dd_sleeve("受損", flags=("loser",))
        assert r["sleeve"] == "MOONSHOT" and r["posture"] == "avoid"

    def test_zhibian_milestone_met_is_core(self):
        r = dd_sleeve("質變", bubble_guard=5, milestone_score=0.6, flags=("cashflow",))
        assert r["sleeve"] == "FOM_CORE" and r["posture"] == "core"

    def test_zhibian_milestone_unmet_is_core_watch(self):
        r = dd_sleeve("質變", bubble_guard=5, milestone_score=0.2)
        assert r["sleeve"] == "FOM_CORE" and r["posture"] == "core_watch"

    def test_jiegou_froth_to_value_on_pullback(self):
        r = dd_sleeve("結構", bubble_guard=-95, flags=("froth",))
        assert r["sleeve"] == "VALUE" and r["posture"] == "value_on_pullback"

    def test_jiegou_bottom_fish_is_value(self):
        r = dd_sleeve("結構", bubble_guard=5, milestone_score=0.2, flags=("bottom_fish",))
        assert r["sleeve"] == "VALUE"

    def test_jiegou_second_derivative_core_watch(self):
        r = dd_sleeve("結構", bubble_guard=0, flags=("second_derivative",))
        assert r["sleeve"] == "FOM_CORE" and r["posture"] == "core_watch"

    def test_jiegou_healthy_bg_core(self):
        r = dd_sleeve("結構", bubble_guard=10, milestone_score=0.6)
        assert r["sleeve"] == "FOM_CORE" and r["posture"] == "core"

    def test_verdict_only_routing_when_bg_none(self):
        # MU is 結構 + froth → even without bubble_guard it must not be plain core
        r = dd_sleeve("結構", bubble_guard=None, flags=("froth",))
        assert r["sleeve"] == "VALUE"


class TestAnnotate:
    def test_uncovered_returns_none(self):
        assert annotate_ticker("ZZZZ") is None

    def test_tilted_base_sums_to_one(self):
        row = annotate_ticker("LLY", bubble_guard=0)
        assert row is not None
        assert math.isclose(sum(row["dd_tilted_base"].values()), 1.0, abs_tol=1e-9)

    def test_lly_routes_core(self):
        row = annotate_ticker("LLY", bubble_guard=0)
        assert row["dd_sleeve"] == "FOM_CORE"

    def test_mu_froth_routes_value(self):
        row = annotate_ticker("MU", bubble_guard=-95)
        assert row["dd_sleeve"] == "VALUE"

    def test_ionq_moonshot(self):
        row = annotate_ticker("IONQ", bubble_guard=None)
        assert row["dd_sleeve"] == "MOONSHOT"

    def test_structural_crosscheck_present(self):
        row = annotate_ticker("NKE", bubble_guard=0)
        # classify_sleeve covers NKE (BEATEN_QUALITY) → cross-check should populate
        assert "structural_sleeve" in row
        assert row["sleeve_agreement"] in (True, False)


class TestReport:
    def test_build_report_observe_first(self):
        rep = build_report(out_dir="this-dir-has-no-fom-json")
        assert rep["observe_first"] is True
        assert rep["fom_report_used"] is False
        # every covered name lands in exactly one sleeve bucket
        total = sum(len(v) for v in rep["buckets"].values())
        assert total == len(TECH_DD)

    def test_quantum_in_moonshot_bucket(self):
        rep = build_report(out_dir="this-dir-has-no-fom-json")
        moon = {r["ticker"] for r in rep["buckets"]["MOONSHOT"]}
        assert {"IONQ", "QBTS", "RGTI"} <= moon


class TestCLIWiring:
    def test_tech_dd_subcommand_parses(self):
        from sharks.cli import build_parser
        ns = build_parser().parse_args(["tech-dd", "--dry-run"])
        assert ns.command == "tech-dd" and ns.dry_run is True

    def test_tech_dd_dry_run_exits_zero(self):
        from sharks.cli import main
        assert main(["tech-dd", "--dry-run"]) == 0
