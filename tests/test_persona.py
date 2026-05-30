"""Tests for the analyst-persona loader + FOM weight-tilt ensemble."""

from __future__ import annotations

import math
from pathlib import Path

import pytest

from sharks.analysts.persona import (
    DIMENSIONS,
    MAX_TILT,
    _parse_frontmatter,
    _clamp_tilt,
    apply_persona_tilt,
    ensemble_weights,
    load_personas,
)

NEUTRAL = {"momentum": 0.25, "contrarian": 0.25, "cyclic": 0.15,
           "quality": 0.15, "bubble_guard": 0.20}

PERSONA_FM = """---
type: analyst-persona
name: tester
expertise: [a, b]
fom_weight_tilt:
  momentum: 0.05
  contrarian: -0.03
conviction_weight: 0.7
signature_indicators:
  - sig_one
  - sig_two
status: active
---

body text
"""


class TestFrontmatterParser:
    def test_scalars_and_inline_list(self):
        fm = _parse_frontmatter(PERSONA_FM)
        assert fm["type"] == "analyst-persona"
        assert fm["name"] == "tester"
        assert fm["expertise"] == ["a", "b"]
        assert fm["conviction_weight"] == 0.7

    def test_nested_map(self):
        fm = _parse_frontmatter(PERSONA_FM)
        assert fm["fom_weight_tilt"]["momentum"] == 0.05
        assert fm["fom_weight_tilt"]["contrarian"] == -0.03

    def test_indented_list(self):
        fm = _parse_frontmatter(PERSONA_FM)
        assert fm["signature_indicators"] == ["sig_one", "sig_two"]

    def test_no_frontmatter(self):
        assert _parse_frontmatter("just prose, no frontmatter") == {}


class TestClampTilt:
    def test_clamps_to_ceiling(self):
        t = _clamp_tilt({"momentum": 0.5, "quality": -0.9})
        assert t["momentum"] == MAX_TILT
        assert t["quality"] == -MAX_TILT

    def test_missing_dims_zero(self):
        t = _clamp_tilt({"momentum": 0.02})
        assert t["cyclic"] == 0.0
        assert set(t.keys()) == set(DIMENSIONS)


class TestApplyTilt:
    def test_renormalises_to_one(self):
        w = apply_persona_tilt(NEUTRAL, {"momentum": 0.08})
        assert math.isclose(sum(w.values()), 1.0, abs_tol=1e-9)

    def test_momentum_tilt_raises_momentum_share(self):
        w = apply_persona_tilt(NEUTRAL, {"momentum": 0.08})
        assert w["momentum"] > NEUTRAL["momentum"]

    def test_no_negative_weights(self):
        w = apply_persona_tilt(NEUTRAL, {"cyclic": -0.08})
        assert all(v >= 0 for v in w.values())


class TestEnsemble:
    def test_no_personas_returns_base(self):
        out = ensemble_weights(NEUTRAL, personas=[])
        assert out["weights"] == {d: NEUTRAL[d] for d in DIMENSIONS}
        assert out["contributors"] == []

    def test_draft_personas_do_not_vote(self):
        drafts = [{"name": "d", "status": "draft", "conviction_weight": 1.0,
                   "fom_weight_tilt": _clamp_tilt({"momentum": 0.08})}]
        out = ensemble_weights(NEUTRAL, personas=drafts)
        assert out["contributors"] == []

    def test_opposed_personas_partially_cancel(self):
        # one momentum-up, one momentum-down, equal conviction → net tilt ~0
        a = {"name": "a", "status": "active", "conviction_weight": 0.5,
             "fom_weight_tilt": _clamp_tilt({"momentum": 0.06, "contrarian": -0.06})}
        b = {"name": "b", "status": "active", "conviction_weight": 0.5,
             "fom_weight_tilt": _clamp_tilt({"momentum": -0.06, "contrarian": 0.06})}
        out = ensemble_weights(NEUTRAL, personas=[a, b])
        assert math.isclose(out["effective_tilt"]["momentum"], 0.0, abs_tol=1e-9)
        assert math.isclose(sum(out["weights"].values()), 1.0, abs_tol=1e-9)

    def test_conviction_weighted(self):
        # high-conviction momentum-up should dominate low-conviction momentum-down
        a = {"name": "a", "status": "active", "conviction_weight": 0.9,
             "fom_weight_tilt": _clamp_tilt({"momentum": 0.08})}
        b = {"name": "b", "status": "active", "conviction_weight": 0.1,
             "fom_weight_tilt": _clamp_tilt({"momentum": -0.08})}
        out = ensemble_weights(NEUTRAL, personas=[a, b])
        assert out["effective_tilt"]["momentum"] > 0
        assert out["weights"]["momentum"] > NEUTRAL["momentum"]


class TestLoadRealPersonas:
    def test_loads_active_personas_from_repo(self):
        # huang + sam are retrofitted with analyst-persona frontmatter.
        personas = load_personas(Path("analysts"))
        names = {p.get("name") for p in personas}
        assert "huang" in names and "sam" in names
        # every loaded persona's tilt is within the ceiling
        for p in personas:
            for d in DIMENSIONS:
                assert abs(p["fom_weight_tilt"][d]) <= MAX_TILT

    def test_ensemble_of_real_personas_sums_to_one(self):
        personas = load_personas(Path("analysts"))
        out = ensemble_weights(NEUTRAL, personas=personas)
        assert math.isclose(sum(out["weights"].values()), 1.0, abs_tol=1e-9)
