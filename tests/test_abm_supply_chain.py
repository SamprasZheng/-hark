"""供應鏈 ABM 測試 — 純函式 + 注入式 loader / fleet,零網路零真實磁碟(tmp_path 除外)。

涵蓋:艦隊建構(config 權重縮放/缺檔降級)、先驗帶選擇(分位數/缺值)、
衝擊與回復數學(噪聲歸零後精確驗證)、Monte Carlo 決定性(同 seed 全等)、
抽樣符合先驗(固定 seed 統計界)、信封鍵 / PIT 欄位、deep-kill 折減映射、
world-monitor 缺席降級、main 落盤(tmp_path)。
"""

from __future__ import annotations

import json

import numpy as np

from sharks.regime.abm_supply_chain import (DEEPKILL_HAIRCUT, SCENARIO_IDS,
                                            SCENARIO_PRIOR_BANDS, SCENARIOS,
                                            SupplierAgent, build_default_fleet,
                                            deepkill_survival_delta_pct,
                                            load_latest_world_metrics, main,
                                            run_simulation, scenario_priors,
                                            simulate_scenario_path)


# ── 合成艦隊(測試注入,避開真實 config)──

def _two_agent_fleet():
    return [SupplierAgent("Taiwan", 60.0, 60.0), SupplierAgent("US", 40.0, 40.0)]


def _caps_regions(fleet):
    return (np.array([a.capacity for a in fleet], dtype=float),
            np.array([a.region for a in fleet]))


# ── 艦隊建構 ──

class TestFleet:
    def test_default_composition_taiwan_heavy(self):
        fleet = build_default_fleet(
            loader=lambda: {"groups": {"taiwan_chain": {"weight": 0.9}}})
        total = sum(a.capacity for a in fleet)
        tw = sum(a.capacity for a in fleet if a.region == "Taiwan")
        assert abs(total - 100.0) < 1e-9
        assert abs(tw / total - 0.55) < 1e-9          # 錨點權重 0.9 → 占比=常數先驗
        assert tw / total > max(
            sum(a.capacity for a in fleet if a.region == r) / total
            for r in ("US", "Korea", "Japan", "China", "SEA"))

    def test_fleet_scales_with_config_weight(self):
        fleet = build_default_fleet(
            loader=lambda: {"groups": {"taiwan_chain": {"weight": 0.45}}})
        total = sum(a.capacity for a in fleet)
        tw_share = sum(a.capacity for a in fleet if a.region == "Taiwan") / total
        # 0.55×(0.45/0.9)=0.275 → 歸一後 0.275/0.725 ≈ 0.379
        assert 0.30 < tw_share < 0.45
        assert abs(total - 100.0) < 1e-9

    def test_missing_config_falls_back_to_constant(self):
        def boom():
            raise FileNotFoundError("config gone")
        fleet = build_default_fleet(loader=boom)      # 不 raise,退常數先驗
        total = sum(a.capacity for a in fleet)
        tw_share = sum(a.capacity for a in fleet if a.region == "Taiwan") / total
        assert abs(tw_share - 0.55) < 1e-9
        assert all(a.current_output == a.capacity for a in fleet)


# ── 先驗帶 ──

class TestScenarioPriors:
    def test_every_band_sums_to_one(self):
        for band in SCENARIO_PRIOR_BANDS["bands"]:
            assert abs(sum(band["priors"].values()) - 1.0) < 1e-9
            assert set(band["priors"]) == set(SCENARIO_IDS)

    def test_extreme_band_elevates_escalation(self):
        base = scenario_priors(50.0)
        extreme = scenario_priors(99.8)               # 現況:GPRC_TWN p99.8
        assert extreme["TS_HIGH"] > base["TS_HIGH"]
        assert extreme["TS_BLOCKADE"] > base["TS_BLOCKADE"]
        assert extreme["NONE"] < base["NONE"]

    def test_missing_pctile_uses_base_band(self):
        assert scenario_priors(None) == SCENARIO_PRIOR_BANDS["bands"][0]["priors"]

    def test_returns_copy_not_reference(self):
        p = scenario_priors(50.0)
        p["NONE"] = 0.0
        assert scenario_priors(50.0)["NONE"] != 0.0


# ── 衝擊/回復數學(噪聲歸零 → 精確)──

class TestShockMath:
    def test_ts_high_month0_shock(self):
        caps, regions = _caps_regions(_two_agent_fleet())
        rel = simulate_scenario_path(SCENARIOS["TS_HIGH"], caps, regions, 3,
                                     np.random.default_rng(0),
                                     shock_noise_sd=0.0, oper_noise_sd=0.0)
        # 台灣 60×0.65=39,US 不受影響 → (39+40)/100
        assert abs(rel[0] - 0.79) < 1e-12

    def test_ts_high_recovery_step(self):
        caps, regions = _caps_regions(_two_agent_fleet())
        rel = simulate_scenario_path(SCENARIOS["TS_HIGH"], caps, regions, 4,
                                     np.random.default_rng(0),
                                     shock_noise_sd=0.0, oper_noise_sd=0.0)
        # t=1:39 + 0.12×(0.92×60 − 39) = 40.944 → 0.80944
        assert abs(rel[1] - 0.80944) < 1e-9
        assert rel[0] < rel[1] < rel[2] < rel[3]      # 單調部分回復

    def test_blockade_deeper_than_ts_high(self):
        caps, regions = _caps_regions(_two_agent_fleet())
        kw = dict(shock_noise_sd=0.0, oper_noise_sd=0.0)
        rng = np.random.default_rng(0)
        blockade = simulate_scenario_path(SCENARIOS["TS_BLOCKADE"], caps, regions, 6, rng, **kw)
        ts_high = simulate_scenario_path(SCENARIOS["TS_HIGH"], caps, regions, 6, rng, **kw)
        assert abs(blockade[0] - 0.55) < 1e-12        # (60×0.25+40)/100
        assert (blockade < ts_high).all()

    def test_tariff_hits_china_sea_only(self):
        fleet = [SupplierAgent("Taiwan", 50.0, 50.0),
                 SupplierAgent("China", 30.0, 30.0),
                 SupplierAgent("SEA", 20.0, 20.0)]
        caps, regions = _caps_regions(fleet)
        rel = simulate_scenario_path(SCENARIOS["TARIFF_NEW"], caps, regions, 2,
                                     np.random.default_rng(0),
                                     shock_noise_sd=0.0, oper_noise_sd=0.0)
        # 台灣不動,China 30×0.85 + SEA 20×0.85 = 42.5 → (50+42.5)/100
        assert abs(rel[0] - 0.925) < 1e-12

    def test_none_scenario_flat_without_noise(self):
        caps, regions = _caps_regions(_two_agent_fleet())
        rel = simulate_scenario_path(SCENARIOS["NONE"], caps, regions, 5,
                                     np.random.default_rng(0),
                                     shock_noise_sd=0.0, oper_noise_sd=0.0)
        assert (rel == 1.0).all()


# ── deep-kill 折減映射 ──

class TestDeepkillHaircut:
    def test_linear_then_capped(self):
        assert deepkill_survival_delta_pct(4.0) == -2.0          # 0.5pp/1%
        assert deepkill_survival_delta_pct(50.0) == -DEEPKILL_HAIRCUT["max_haircut_pp"]
        assert deepkill_survival_delta_pct(0.0) == 0.0
        assert deepkill_survival_delta_pct(None) is None         # 缺值 → None 不發明


# ── Monte Carlo ──

class TestRunSimulation:
    def test_same_seed_identical_output(self):
        kw = dict(n_paths=300, months=12, seed=7,
                  metrics={"gprc_twn_pctile": 99.8, "gpr_date": "2026-05-01"})
        r1 = run_simulation(fleet=_two_agent_fleet(), **kw)
        r2 = run_simulation(fleet=_two_agent_fleet(), **kw)
        assert json.dumps(r1, sort_keys=True) == json.dumps(r2, sort_keys=True)

    def test_different_seed_differs(self):
        kw = dict(n_paths=300, months=12,
                  metrics={"gprc_twn_pctile": 99.8})
        r1 = run_simulation(seed=7, fleet=_two_agent_fleet(), **kw)
        r2 = run_simulation(seed=8, fleet=_two_agent_fleet(), **kw)
        assert json.dumps(r1, sort_keys=True) != json.dumps(r2, sort_keys=True)

    def test_sampling_respects_priors(self):
        n = 4000
        rep = run_simulation(n_paths=n, months=6, seed=42,
                             metrics={"gprc_twn_pctile": 99.8},
                             fleet=_two_agent_fleet())
        priors = scenario_priors(99.8)
        assert rep["inputs"]["prior_band"] == "extreme(>=p99)"
        for sid in SCENARIO_IDS:
            freq = rep["scenario_counts"][sid] / n
            assert abs(freq - priors[sid]) < 0.025, (sid, freq, priors[sid])

    def test_envelope_keys_and_pit_fields(self):
        rep = run_simulation(n_paths=200, months=6, seed=1,
                             metrics={"gprc_twn_pctile": 99.8, "gpr_date": "2026-05-01"},
                             fleet=_two_agent_fleet(),
                             generated_at="2026-06-12T00:00:00+00:00")
        for key in ("as_of", "generated_at", "engine", "llm_involvement", "params",
                    "scenario_priors", "scenario_counts", "per_scenario_loss",
                    "overall_loss_pct", "expected_disruption_quarters",
                    "deepkill_survival_baseline_pct", "deepkill_survival_delta_pct",
                    "fleet_summary", "mesa_note", "disclaimer"):
            assert key in rep, key
        assert rep["as_of"] == "2026-05-01"
        assert rep["generated_at"] == "2026-06-12T00:00:00+00:00"
        assert rep["llm_involvement"] == "none"
        assert rep["deepkill_survival_baseline_pct"] == 74.1
        assert "recommend-only" in rep["disclaimer"]
        assert json.dumps(rep)                       # 全部原生型別,可序列化

    def test_scenario_loss_ordering(self):
        rep = run_simulation(n_paths=2000, months=12, seed=42,
                             metrics={"gprc_twn_pctile": 99.8},
                             fleet=_two_agent_fleet())
        per = rep["per_scenario_loss"]
        assert per["TS_BLOCKADE"]["loss_pct_median"] > per["TS_HIGH"]["loss_pct_median"]
        assert per["TS_HIGH"]["loss_pct_median"] > per["NONE"]["loss_pct_median"]
        # 兩個台海情境在 12 個月視窗內可同時飽和(整段 < 0.95)→ 用 >=
        assert per["TS_BLOCKADE"]["disruption_quarters_mean"] >= \
            per["TS_HIGH"]["disruption_quarters_mean"]
        assert per["TS_HIGH"]["disruption_quarters_mean"] > \
            per["NONE"]["disruption_quarters_mean"]
        delta = rep["deepkill_survival_delta_pct"]
        assert -DEEPKILL_HAIRCUT["max_haircut_pp"] <= delta <= 0.0

    def test_no_world_monitor_degrades_gracefully(self):
        rep = run_simulation(n_paths=200, months=6, seed=3,
                             metrics=None, fleet=_two_agent_fleet())
        assert rep["inputs"]["degraded"] is True
        assert rep["as_of"] is None                  # 缺值 → None,不發明
        assert rep["inputs"]["prior_band"] == "base(<p90)"
        assert rep["scenario_priors"] == SCENARIO_PRIOR_BANDS["bands"][0]["priors"]


# ── world-monitor 讀取 + main 落盤(tmp_path)──

class TestLoaderAndWriter:
    def _wm(self, pctile=99.8):
        return {"metrics": {"gprc_twn_pctile": pctile, "gpr_date": "2026-05-01"}}

    def test_load_latest_skips_bak_and_intraday(self, tmp_path):
        (tmp_path / "world-monitor-2026-06-10.json").write_text(
            json.dumps(self._wm(50.0)), encoding="utf-8")
        (tmp_path / "world-monitor-2026-06-12.json").write_text(
            json.dumps(self._wm(99.8)), encoding="utf-8")
        (tmp_path / "world-monitor-2026-06-13-intraday.json").write_text(
            json.dumps(self._wm(1.0)), encoding="utf-8")
        (tmp_path / "world-monitor-2026-06-14.json.bak").write_text(
            json.dumps(self._wm(2.0)), encoding="utf-8")
        metrics, src = load_latest_world_metrics(tmp_path)
        assert src == "world-monitor-2026-06-12.json"
        assert metrics["gprc_twn_pctile"] == 99.8

    def test_load_latest_empty_dir(self, tmp_path):
        assert load_latest_world_metrics(tmp_path) == (None, None)

    def test_main_writes_dated_output(self, tmp_path):
        (tmp_path / "world-monitor-2026-06-12.json").write_text(
            json.dumps(self._wm(99.8)), encoding="utf-8")
        rc = main(["--out-dir", str(tmp_path), "--paths", "40",
                   "--months", "6", "--seed", "3"])
        assert rc == 0
        files = list(tmp_path.glob("abm-supply-chain-*.json"))
        assert len(files) == 1
        rep = json.loads(files[0].read_text(encoding="utf-8"))
        assert rep["generated_at"] is not None       # PIT:落盤必帶 generated_at
        assert rep["world_monitor_source"] == "world-monitor-2026-06-12.json"
        assert rep["inputs"]["prior_band"] == "extreme(>=p99)"

    def test_main_dry_run_writes_nothing(self, tmp_path):
        rc = main(["--out-dir", str(tmp_path), "--paths", "20",
                   "--months", "3", "--dry-run"])
        assert rc == 0
        assert list(tmp_path.glob("abm-supply-chain-*.json")) == []

    def test_main_without_world_monitor_still_works(self, tmp_path):
        rc = main(["--out-dir", str(tmp_path), "--paths", "20", "--months", "3"])
        assert rc == 0
        rep = json.loads(next(tmp_path.glob("abm-supply-chain-*.json"))
                         .read_text(encoding="utf-8"))
        assert rep["inputs"]["degraded"] is True
        assert rep["world_monitor_source"] is None
