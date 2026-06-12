"""Offline tests for attribution telemetry (decision/postmortem.py).

All pure / injected (no network): one assertion class per cause tag plus
detection, serialization, the scan trigger, and the narrative PIT-fallback that
documents the dependency on the state-snapshot feature.
"""

from __future__ import annotations

import json

from sharks.decision import postmortem as pm

# A representative long_new entry (shape of daily_picks.build_long_new output).
ENTRY = {
    "ticker": "DELL",
    "entry_date": "2026-03-01",
    "thesis": "Chip-flow State 2 single-point breakout on 3x volume",
    "confidence": 0.62,
    "entry_zone": {"low": 100.0, "high": 104.0},
    "entry_mid": 102.0,
    "stop_loss": 95.0,
    "invalidation": {"price": 95.0, "time_stop_days": 135, "catalyst": "close below bar low"},
    "time_stop_days": 135,
    "quadrant": "genuine_bull",
    "evidence_paths": ["outputs/state-2026-03-01.jsonl"],
    "final_fom_entry": None,
    "momentum_entry": None,
}


class TestClassifyCause:
    def test_regime_flip(self):
        out = {"exited_reason": "stop", "forward_return": -0.08}
        r = pm.classify_cause(
            ENTRY, out, regime_delta={"entry": "late_bull", "now": "risk_off", "flipped": True}
        )
        assert r["cause"] == "regime_flip"
        assert r["confidence"] == 0.9

    def test_regime_downgrade_lower_confidence(self):
        out = {"exited_reason": "underperform", "forward_return": -0.12}
        r = pm.classify_cause(
            ENTRY, out, regime_delta={"entry": "bull_trend", "now": "neutral", "flipped": True}
        )
        assert r["cause"] == "regime_flip"
        assert r["confidence"] == 0.7

    def test_quant_signal_failure_high_fom(self):
        out = {"exited_reason": "stop", "forward_return": -0.18}
        r = pm.classify_cause(
            ENTRY, out,
            regime_delta={"entry": "late_bull", "now": "late_bull", "flipped": False},
            fom_delta={"final_fom_now": 60.0, "fom_delta": 2.0, "momentum_delta": -5.0},
        )
        assert r["cause"] == "quant_signal_failure"
        assert r["confidence"] == 0.75

    def test_quant_signal_failure_decay(self):
        out = {"exited_reason": "stop", "forward_return": -0.05}
        r = pm.classify_cause(
            ENTRY, out,
            regime_delta={"entry": "late_bull", "now": "late_bull", "flipped": False},
            fom_delta={"final_fom_now": 30.0, "fom_delta": -2.0, "momentum_delta": -30.0},
        )
        assert r["cause"] == "quant_signal_failure"

    def test_narrative_shift(self):
        out = {"exited_reason": "underperform", "forward_return": -0.11}
        r = pm.classify_cause(
            ENTRY, out,
            regime_delta={"entry": "late_bull", "now": "late_bull", "flipped": False},
            narrative_delta={"changed": True, "pages": [{"page": "02_mag7_bottleneck"}],
                             "method": "pit_snapshot"},
        )
        assert r["cause"] == "narrative_shift"
        assert r["confidence"] == 0.7  # pit_snapshot method → higher confidence

    def test_narrative_shift_heuristic_lower_confidence(self):
        out = {"exited_reason": "stop", "forward_return": -0.2}
        r = pm.classify_cause(
            ENTRY, out,
            narrative_delta={"changed": True, "pages": [], "method": "wiki_mtime_heuristic"},
        )
        assert r["cause"] == "narrative_shift"
        assert r["confidence"] == 0.5

    def test_execution_timing_residual(self):
        out = {"exited_reason": "stop", "forward_return": -0.03}
        r = pm.classify_cause(
            ENTRY, out,
            regime_delta={"entry": "late_bull", "now": "late_bull", "flipped": False},
            fom_delta={"final_fom_now": 30.0, "fom_delta": -2.0, "momentum_delta": -5.0},
            narrative_delta={"changed": False, "method": "wiki_mtime_heuristic"},
        )
        assert r["cause"] == "execution_timing"
        assert r["confidence"] < 0.5

    def test_no_adverse_outcome_is_none(self):
        out = {"exited_reason": "open", "forward_return": 0.15}
        r = pm.classify_cause(ENTRY, out)
        assert r["cause"] == "none"


class TestDetection:
    def test_stop_hit(self):
        out = {"exit_close": 94.0, "exit_low": 94.0, "forward_return": -0.08}
        assert pm.detect_exit(ENTRY, out, "2026-04-01") == "stop"

    def test_time_stop(self):
        out = {"exit_close": 101.0, "exit_low": 99.0}  # above stop, but past time-stop
        assert pm.detect_exit(ENTRY, out, "2026-09-01") == "time_stop"

    def test_underperform(self):
        out = {"exit_close": 101.0, "exit_low": 100.0, "forward_return": -0.15}
        assert pm.detect_exit(ENTRY, out, "2026-04-01") == "underperform"

    def test_open(self):
        out = {"exit_close": 110.0, "exit_low": 108.0, "forward_return": 0.08}
        assert pm.detect_exit(ENTRY, out, "2026-04-01") == "open"


class TestRunAndSerialize:
    def test_run_offline_with_injected_outcome(self):
        out = {"exited_reason": "stop", "exit_close": 94.0, "forward_return": -0.08}
        res = pm.run_postmortem(
            ENTRY, as_of_exit="2026-04-01", outcome=out, network=False,
            regime_now="risk_off", regime_label_entry="late_bull",
            narrative_snapshot={"changed": False},
        )
        assert res.cause == "regime_flip"
        assert res.exited_reason == "stop"

    def test_to_dict_is_json_safe_and_recommend_only(self):
        out = {"exited_reason": "stop", "forward_return": -0.08}
        res = pm.run_postmortem(ENTRY, as_of_exit="2026-04-01", outcome=out, network=False,
                                narrative_snapshot={"changed": False})
        d = res.to_dict()
        assert d["recommend_only"] is True
        assert d["report_type"] == "attribution_postmortem"
        json.dumps(d)  # must not raise

    def test_write_output(self, tmp_path):
        out = {"exited_reason": "stop", "forward_return": -0.08}
        res = pm.run_postmortem(ENTRY, as_of_exit="2026-04-01", outcome=out, network=False,
                                narrative_snapshot={"changed": False})
        path = pm.write_output(tmp_path, res)
        assert path.name == "postmortem-DELL-2026-04-01.json"
        back = json.loads(path.read_text(encoding="utf-8"))
        assert back["ticker"] == "DELL"


class TestNarrativeFallback:
    def test_heuristic_method_when_no_snapshot(self, tmp_path):
        wiki = tmp_path / "wiki"
        wiki.mkdir()
        (wiki / "02_mag7_bottleneck.md").write_text(
            "---\nas_of_timestamp: 2026-05-29T00:00:00-04:00\n---\n\n# x\n", encoding="utf-8"
        )
        # entry predates the page's as_of → heuristic says the thesis moved.
        nd = pm.compute_narrative_delta("2026-03-01", wiki_root=wiki, pages=("02_mag7_bottleneck",))
        assert nd["method"] == "wiki_mtime_heuristic"
        assert nd["changed"] is True

    def test_injected_pit_snapshot_method(self):
        nd = pm.compute_narrative_delta(
            "2026-03-01", narrative_snapshot={"changed": True, "pages": ["02"]}
        )
        assert nd["method"] == "pit_snapshot"
        assert nd["changed"] is True


class TestScan:
    def test_scan_extracts_long_new_entries(self, tmp_path):
        picks = {
            "as_of": "2026-03-01T00:00:00+00:00",
            "signals": [
                {"slot": "long_new_1", "ticker": "DELL", "stop_loss": 95.0,
                 "entry_zone": {"low": 100, "high": 104},
                 "invalidation": {"time_stop_days": 135}, "thesis": "x"},
                {"slot": "position_followup_5", "ticker": "NVDA", "action": "hold"},
            ],
        }
        (tmp_path / "picks-2026-03-01.json").write_text(json.dumps(picks), encoding="utf-8")
        entries = pm.scan_closed_positions(tmp_path)
        assert [e["ticker"] for e in entries] == ["DELL"]  # only long_new
        assert entries[0]["entry_mid"] == 102.0
