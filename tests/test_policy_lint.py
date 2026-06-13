"""Tests for the decision risk layer: the zero-dep YAML reader, the Risk-Officer
pre-screen (policy_lint), and the drift guard that ties risk_config.yaml to the
philosophy/06 + 08 source pages.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from sharks.decision import _yamlite
from sharks.decision import policy_lint
from sharks.decision.policy_lint import load_risk_config, lint_pick, size_cap_for

REPO_ROOT = Path(__file__).resolve().parents[1]


class TestYamlite:
    def test_scalars_coerce(self):
        d = _yamlite.loads(
            "a: 5\nb: 0.7\nc: -12\nd: true\ne: false\nf: null\ng: hello\nh: \"q\"\n"
        )
        assert d == {"a": 5, "b": 0.7, "c": -12, "d": True, "e": False,
                     "f": None, "g": "hello", "h": "q"}

    def test_nested_maps(self):
        text = (
            "top:\n"
            "  one: 1\n"
            "  two: 2\n"
            "deep:\n"
            "  a:\n"
            "    x: 10\n"
            "    y: 20\n"
            "  b:\n"
            "    z: 30\n"
        )
        d = _yamlite.loads(text)
        assert d["top"] == {"one": 1, "two": 2}
        assert d["deep"]["a"] == {"x": 10, "y": 20}
        assert d["deep"]["b"] == {"z": 30}

    def test_comments_and_inline(self):
        d = _yamlite.loads("# header\nk: 1  # trailing comment\n\n  # indented comment\nj: 2\n")
        assert d == {"k": 1, "j": 2}

    def test_numeric_keys_kept_as_strings(self):
        d = _yamlite.loads("caps:\n  1m:\n    tier1: 4\n")
        assert d["caps"]["1m"]["tier1"] == 4


class TestLoadRiskConfig:
    def test_loads_and_has_required_sections(self):
        cfg = load_risk_config()
        for section in ("exclusions", "position_caps_pct", "concentration_caps_pct",
                        "max_drawdown_halt", "horizon_size_caps_pct", "confidence"):
            assert section in cfg
        assert cfg["exclusions"]["price_floor_usd"] == 5
        assert cfg["position_caps_pct"]["tier1"] == 8

    def test_missing_section_raises(self, tmp_path):
        bad = tmp_path / "bad.yaml"
        bad.write_text("exclusions:\n  price_floor_usd: 5\n", encoding="utf-8")
        with pytest.raises(ValueError, match="missing required sections"):
            load_risk_config(bad)


class TestSizeCap:
    def test_horizon_overrides_flat_cap(self):
        cfg = load_risk_config()
        assert size_cap_for(1, "3m", cfg) == 6     # 01-time-horizon 3m tier1
        assert size_cap_for(1, None, cfg) == 8      # flat 08 tier1
        assert size_cap_for(2, "1m", cfg) == 3
        assert size_cap_for(None, "3m", cfg) is None


class TestLintPick:
    def setup_method(self):
        self.cfg = load_risk_config()

    def test_clean_pick(self):
        pick = {"price": 100, "tier": 1, "size_pct": 6, "side": "long"}
        assert lint_pick(pick, self.cfg) == []

    def test_price_floor(self):
        v = lint_pick({"price": 3.0, "tier": 3}, self.cfg)
        assert any(x["rule"] == "price_floor" for x in v)

    def test_position_cap(self):
        v = lint_pick({"price": 100, "tier": 1, "size_pct": 10}, self.cfg)  # > 8% cap
        assert any(x["rule"] == "position_cap" for x in v)

    def test_short_iron_rules(self):
        v = lint_pick({"price": 50, "tier": 2, "side": "short",
                       "short_interest_pct": 0.25, "borrow_fee_apr": 0.15,
                       "days_to_cover": 7}, self.cfg)
        assert sum(1 for x in v if x["rule"] == "short_iron") == 3

    def test_partial_pick_no_false_positive(self):
        # only a tier present — nothing checkable — must not fabricate a violation
        assert lint_pick({"tier": 1}, self.cfg) == []


class TestDriftVsPhilosophy:
    """risk_config.yaml must not drift from the human-authored philosophy pages.

    We assert the canonical numbers appear in BOTH the md source and the config.
    A failure means someone edited one without the other (a P0 per 06/08).
    """

    def setup_method(self):
        self.cfg = load_risk_config()
        # philosophy/ was archived to _legacy/ (2026-06-13 re-orientation); these pages
        # remain the canonical risk-number source the config must not drift from.
        self.ex = (REPO_ROOT / "_legacy" / "philosophy" / "06-exclusions.md").read_text(encoding="utf-8")
        self.rp = (REPO_ROOT / "_legacy" / "philosophy" / "08-risk-and-position.md").read_text(encoding="utf-8")

    def test_price_floor(self):
        assert "$5" in self.ex
        assert self.cfg["exclusions"]["price_floor_usd"] == 5

    def test_short_interest_cap(self):
        assert "20%" in self.ex
        assert self.cfg["exclusions"]["short_interest_pct_max"] == 0.20

    def test_tier1_position_cap(self):
        assert "8%" in self.rp
        assert self.cfg["position_caps_pct"]["tier1"] == 8

    def test_sector_concentration_cap(self):
        assert "25%" in self.rp
        assert self.cfg["concentration_caps_pct"]["sector"] == 25

    def test_max_drawdown_trigger(self):
        assert "-12%" in self.rp
        assert self.cfg["max_drawdown_halt"]["trigger_pct"] == -12

    def test_total_short_notional_cap(self):
        assert "30%" in self.rp
        assert self.cfg["concentration_caps_pct"]["total_short_notional"] == 30
