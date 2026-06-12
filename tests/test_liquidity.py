"""Offline tests for the Liquidity Fishbowl composite (regime/liquidity.py).

Pure-logic coverage of the documented L formula + band thresholds, the
classifier-compat alert adapter, the stale-fallback degrade path (no network),
and the classifier integration contract.
"""

from __future__ import annotations

import json

import pytest

from sharks.regime import liquidity as L
from sharks.regime.classifier import classify_regime, load_latest_fishbowl


class TestNormalize:
    def test_midpoint(self):
        assert L.normalize(0, -200, 200) == 0.5

    def test_clamps_to_unit_interval(self):
        assert L.normalize(300, -200, 200) == 1.0
        assert L.normalize(-300, -200, 200) == 0.0

    def test_invert(self):
        assert L.normalize(400, 400, 700, invert=True) == 1.0
        assert L.normalize(700, 400, 700, invert=True) == 0.0

    def test_none_passthrough(self):
        assert L.normalize(None, 0, 1) is None


class TestComputeL:
    def test_all_terms_max_liquidity(self):
        r = L.compute_L(
            reserves_change_30d=200, rrp_change_30d=-200, hy_oas_bps=400,
            spx_60d_rvol=15, ad_line_60d_slope=1.0,
        )
        assert r["L"] == 1.0
        assert r["regime_band"] == "ample"
        assert r["dragon_eating_dragon"] is False
        assert r["missing"] == []

    def test_drought_and_dragon_flag(self):
        r = L.compute_L(
            reserves_change_30d=-200, rrp_change_30d=200, hy_oas_bps=700,
            spx_60d_rvol=35, ad_line_60d_slope=-1.0,
        )
        assert r["L"] == 0.0
        assert r["regime_band"] == "drought"
        # L < 0.15 AND SPX 60d rvol > 30 → 多殺多
        assert r["dragon_eating_dragon"] is True

    def test_missing_terms_renormalize_keeps_unit_interval(self):
        r = L.compute_L(reserves_change_30d=200)  # only one term present
        assert 0.0 <= r["L"] <= 1.0
        assert r["L"] == 1.0  # single present term renormalised to full weight
        assert set(r["missing"]) == {"rrp", "hy_oas", "spx_rvol", "ad_line"}

    def test_all_missing_returns_none(self):
        r = L.compute_L()
        assert r["L"] is None
        assert r["regime_band"] == "unknown"


class TestAlertLevelAdapter:
    @pytest.mark.parametrize(
        "score,level",
        [(0.8, "GREEN"), (0.5, "YELLOW"), (0.3, "ORANGE"), (0.1, "RED")],
    )
    def test_band_mapping(self, score, level):
        assert L.L_to_alert_level(score) == level

    def test_none_is_unknown(self):
        assert L.L_to_alert_level(None) == "UNKNOWN"

    def test_dragon_forces_red(self):
        assert L.L_to_alert_level(0.9, dragon_eating_dragon=True) == "RED"


def _csv_for(series_id: str) -> str:
    # 30d-change series have an earlier + a later point; level series have a tail.
    data = {
        "WALCL": "observation_date,WALCL\n2026-04-10,7000000\n2026-05-10,7100000\n",
        "RRPONTSYD": "observation_date,RRPONTSYD\n2026-04-10,500.0\n2026-05-10,450.0\n",
        "BAMLH0A0HYM2": "observation_date,BAMLH0A0HYM2\n2026-05-10,3.40\n",
        "T10Y2Y": "observation_date,T10Y2Y\n2026-05-10,0.45\n",
        "WTREGEN": "observation_date,WTREGEN\n2026-05-10,800.0\n",
    }
    return data[series_id]


def _series_opener():
    def opener(req, timeout=None):
        url = req.full_url
        sid = next(s for s in (
            "WALCL", "RRPONTSYD", "BAMLH0A0HYM2", "T10Y2Y", "WTREGEN"
        ) if f"id={s}" in url)
        body = _csv_for(sid).encode("utf-8")

        class _Ctx:
            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

            def read(self):
                return body

        return _Ctx()

    return opener


class TestRunHappyPath:
    def test_live_run_emits_band_and_writes(self, tmp_path):
        out = tmp_path / "outputs"
        data = tmp_path / "hist"
        env = L.run_liquidity(
            out_dir=out, data_dir=data, today="2026-05-10T00:00:00+00:00",
            opener=_series_opener(), sleep=lambda *_: None,
        )
        assert env["live_data"] is True
        assert env["stale_fallback"] is False
        assert env["L"] is not None and 0.0 <= env["L"] <= 1.0
        assert env["composite_alert"]["level"] in {"GREEN", "YELLOW", "ORANGE", "RED"}
        assert (out / "liquidity-fishbowl-2026-05-10.json").exists()
        assert (data / "liquidity-fishbowl-2026-05-10.json").exists()


class TestRunStaleFallback:
    def test_fred_failure_reemits_prior_under_today(self, tmp_path):
        out = tmp_path / "outputs"
        data = tmp_path / "hist"
        data.mkdir(parents=True)
        prior = {
            "as_of": "2026-05-01T00:00:00+00:00",
            "as_of_date": "2026-05-01",
            "series": {
                "reserves_change_30d": 50.0,
                "rrp_change_30d": -20.0,
                "hy_oas_bps": 350.0,
            },
        }
        (data / "liquidity-fishbowl-2026-05-01.json").write_text(
            json.dumps(prior), encoding="utf-8"
        )

        def boom(req, timeout=None):
            import urllib.error
            raise urllib.error.HTTPError(req.full_url, 404, "no", None, None)

        env = L.run_liquidity(
            out_dir=out, data_dir=data, today="2026-06-10T00:00:00+00:00",
            opener=boom, sleep=lambda *_: None,
        )
        assert env["live_data"] is False
        assert env["stale_fallback"] is True
        assert env["as_of_date"] == "2026-06-10"  # today, not the prior date
        assert env["stale_source_as_of"] == "2026-05-01T00:00:00+00:00"
        assert env["L"] is not None  # recomputed from the prior series


class TestClassifierIntegration:
    def test_load_latest_fishbowl_reads_artifact(self, tmp_path):
        (tmp_path / "liquidity-fishbowl-2026-05-10.json").write_text(
            json.dumps({"composite_alert": {"level": "ORANGE"}}), encoding="utf-8"
        )
        got = load_latest_fishbowl(out_dir=tmp_path)
        assert got["composite_alert"]["level"] == "ORANGE"

    def test_orange_band_drives_risk_off(self):
        r = classify_regime(
            breadth={"verdict": "OVERHEATED"},
            liquidity={"composite_alert": {"level": "ORANGE"}},
            spx_above_200dma=True,
        )
        assert r["label"] == "risk_off"
        assert r["inputs"]["liquidity_level"] == "ORANGE"

    def test_yellow_band_keeps_late_bull(self):
        r = classify_regime(
            breadth={"verdict": "OVERHEATED"},
            liquidity={"composite_alert": {"level": "YELLOW"}},
            spx_above_200dma=True,
        )
        assert r["label"] == "late_bull"
