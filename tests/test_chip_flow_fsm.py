"""Deterministic, offline tests for the chip-flow FSM + daily-picks compiler.

These pin the State 0 → State 1 → State 2 classification and the picks-JSON
contract (philosophy/05-decision-rubric.md) without any network call —
synthetic OHLCV frames are injected directly into ``classify``.

The model spec is philosophy/concepts/chip-flow-single-point-breakout.md.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from sharks import daily_picks as dp
from sharks.scoring import chip_flow_fsm as fsm

INFO_STUB = {"heldPercentInstitutions": 0.72, "shortPercentOfFloat": 0.05}


def _make_df(scenario: str) -> pd.DataFrame:
    n = 80
    idx = pd.date_range("2026-01-01", periods=n, freq="B")
    rng = np.random.default_rng(7)
    close = 100 + rng.normal(0, 0.8, n)            # tight consolidation ~98–102
    vol = rng.integers(900_000, 1_100_000, n).astype(float)

    if scenario == "breakout":
        close[-15:-1] = 98.5 + rng.normal(0, 0.4, 14)   # recent dip near support
        close[-1] = 112.0                               # clears ~102 range high
        vol[-1] = vol[:-1].mean() * 3.0                 # 3x volume
    elif scenario == "washout":
        close[-1] = 92.0                                # below consolidation low
        vol[-1] = vol[:-1].mean() * 0.8                 # contracting, no panic
    elif scenario == "accum":
        close[-20:] = 100 + rng.normal(0, 0.4, 20)
        close[-1] = 100.1                               # inside range
        vol[-5:] = vol[:-5].mean() * 0.6                # dried up

    high = close + np.abs(rng.normal(0, 0.5, n)) + 0.5
    low = close - np.abs(rng.normal(0, 0.5, n)) - 0.5
    openp = close + rng.normal(0, 0.3, n)
    return pd.DataFrame(
        {"Open": openp, "High": high, "Low": low, "Close": close, "Volume": vol},
        index=idx,
    )


def _classify(scenario: str, prev_state):
    return fsm.classify(
        "TEST", as_of="2026-05-29", prev_state=prev_state,
        df=_make_df(scenario), info=INFO_STUB,
    )


class TestStateClassification:
    def test_breakout_from_washout_fires_buy(self):
        r = _classify("breakout", fsm.WASH_OUT)
        assert r.state == fsm.BREAKOUT
        assert r.signal == fsm.SIG_BUY
        assert r.transition == f"{fsm.WASH_OUT}->{fsm.BREAKOUT}"
        assert r.stop_loss is not None and r.stop_loss < r.features["last_close"]
        assert r.confidence >= 0.50

    def test_breakout_already_held_is_hold_not_buy(self):
        r = _classify("breakout", fsm.BREAKOUT)
        assert r.state == fsm.BREAKOUT
        assert r.signal == fsm.SIG_HOLD  # no re-entry if already in breakout yesterday

    def test_washout_is_watch_no_entry(self):
        r = _classify("washout", fsm.ACCUMULATION)
        assert r.state == fsm.WASH_OUT
        assert r.signal == fsm.SIG_WATCH
        assert r.stop_loss is None

    def test_accumulation_is_watchlist_no_entry(self):
        r = _classify("accum", None)
        assert r.state == fsm.ACCUMULATION
        assert r.signal == fsm.SIG_WATCHLIST
        assert r.stop_loss is None

    def test_insufficient_history_is_none(self):
        df = _make_df("accum").head(10)  # below min_history
        r = fsm.classify("TEST", as_of="2026-05-29", df=df, info=INFO_STUB)
        assert r.state == fsm.NONE
        assert "insufficient_history" in r.notes


class TestNewsSentimentBump:
    """News-NLP integration: bearish_no_price_follow adds +0.10 to State 1."""

    def test_washout_without_news_unchanged(self):
        # Baseline: no news_sentiment passed → original behaviour preserved.
        r = fsm.classify(
            "TEST", as_of="2026-05-29", prev_state=fsm.ACCUMULATION,
            df=_make_df("washout"), info=INFO_STUB, news_sentiment=None,
        )
        baseline_conf = r.confidence
        assert r.state == fsm.WASH_OUT
        assert 0.50 <= baseline_conf <= 0.85
        # Same call again with empty news dict → also unchanged
        r2 = fsm.classify(
            "TEST", as_of="2026-05-29", prev_state=fsm.ACCUMULATION,
            df=_make_df("washout"), info=INFO_STUB,
            news_sentiment={"bearish_no_price_follow": False},
        )
        assert r2.confidence == baseline_conf

    def test_washout_with_bearish_no_price_follow_bumps_010(self):
        r_base = fsm.classify(
            "TEST", as_of="2026-05-29", prev_state=fsm.ACCUMULATION,
            df=_make_df("washout"), info=INFO_STUB, news_sentiment=None,
        )
        r_news = fsm.classify(
            "TEST", as_of="2026-05-29", prev_state=fsm.ACCUMULATION,
            df=_make_df("washout"), info=INFO_STUB,
            news_sentiment={"bearish_no_price_follow": True},
        )
        assert r_news.state == fsm.WASH_OUT
        # +0.10 bump, but never above 0.85 cap
        expected = round(min(r_base.confidence + 0.10, 0.85), 3)
        assert r_news.confidence == expected
        assert r_news.confidence >= r_base.confidence

    def test_breakout_unaffected_by_news_sentiment(self):
        # The bump only applies to State 1, not State 2.
        r = fsm.classify(
            "TEST", as_of="2026-05-29", prev_state=fsm.WASH_OUT,
            df=_make_df("breakout"), info=INFO_STUB,
            news_sentiment={"bearish_no_price_follow": True},
        )
        assert r.state == fsm.BREAKOUT
        assert r.signal == fsm.SIG_BUY
        # confidence comes from is_breakout, not is_wash_out


class TestBreakoutBarLowIsStop:
    def test_stop_equals_breakout_bar_low(self):
        df = _make_df("breakout")
        r = fsm.classify("TEST", as_of="2026-05-29", prev_state=fsm.WASH_OUT, df=df, info=INFO_STUB)
        assert r.stop_loss == pytest.approx(float(df["Low"].iloc[-1]), rel=1e-6)


class TestDailyPicksContract:
    """The compiled picks JSON must obey philosophy/05-decision-rubric.md."""

    def _buy_row(self):
        df = _make_df("breakout")
        c = fsm.classify("TEST", as_of="2026-05-29", prev_state=fsm.WASH_OUT, df=df, info=INFO_STUB)
        return {
            "ticker": "TEST", "signal": c.signal, "confidence": c.confidence,
            "stop_loss": c.stop_loss, "features": c.features, "state": c.state,
        }

    def _regime(self):
        return {"macro_state_ref": "wiki/01_macro_state.md@2026-05-29", "vix": 14.2,
                "cycle_resonance_active": None, "high_freq_mode_eligible": False}

    def test_buy_lands_in_long_new_1(self):
        picks = dp.compile_picks([self._buy_row()], self._regime(), "2026-05-29")
        slots = {s["slot"]: s for s in picks["signals"]}
        assert "long_new_1" in slots
        assert slots["long_new_1"]["ticker"] == "TEST"
        assert slots["long_new_1"]["quadrant"] == "genuine_bull"
        assert slots["long_new_1"]["author_role"] == "compiler"
        # entry zone brackets the close; stop sits below the entry zone
        ez = slots["long_new_1"]["entry_zone"]
        assert ez["low"] < ez["high"]
        assert slots["long_new_1"]["stop_loss"] < ez["low"]

    def test_short_new_always_no_action(self):
        picks = dp.compile_picks([self._buy_row()], self._regime(), "2026-05-29")
        assert "short_new_1" in picks["no_action_buckets"]
        assert "short_new_2" in picks["no_action_buckets"]

    def test_empty_slot_rule_no_padding(self):
        # one BUY only → long_new_2 + all followups must be no-action, never padded
        picks = dp.compile_picks([self._buy_row()], self._regime(), "2026-05-29")
        assert "long_new_2" in picks["no_action_buckets"]
        filled_slots = {s["slot"] for s in picks["signals"]}
        assert filled_slots == {"long_new_1"}
        # total slots accounted for = 10
        assert len(picks["signals"]) + len(picks["no_action_buckets"]) == 10

    def test_sub_threshold_confidence_not_slotted(self):
        weak = self._buy_row()
        weak["confidence"] = 0.40  # below 0.50 floor
        picks = dp.compile_picks([weak], self._regime(), "2026-05-29")
        assert picks["signals"] == []
        assert "long_new_1" in picks["no_action_buckets"]

    def test_washout_and_exit_go_to_followups(self):
        rows = [
            {"ticker": "AAA", "signal": fsm.SIG_WATCH, "confidence": 0.6, "stop_loss": None, "features": {}},
            {"ticker": "BBB", "signal": fsm.SIG_EXIT_FLAG, "confidence": 0.55, "stop_loss": None, "features": {}},
        ]
        picks = dp.compile_picks(rows, self._regime(), "2026-05-29")
        fu = [s for s in picks["signals"] if s["slot"].startswith("position_followup")]
        assert len(fu) == 2
        actions = {s["ticker"]: s["action"] for s in fu}
        assert actions["BBB"] == "exit"        # exit-flag prioritised first
        assert actions["AAA"] == "hold_update"

    def test_schema_top_level_keys(self):
        picks = dp.compile_picks([self._buy_row()], self._regime(), "2026-05-29")
        for key in ("schema_version", "as_of", "regime", "signals", "no_action_buckets", "footer"):
            assert key in picks
        assert picks["schema_version"] == 1


class TestDailyPicksNewsBump:
    """daily_picks._apply_news_bump_to_watch — bumps WATCH rows when news jsonl
    exists alongside an already-written state-*.jsonl."""

    def test_bump_applies_to_watch_with_flag(self):
        rows = [
            {"ticker": "AAA", "signal": fsm.SIG_WATCH, "confidence": 0.65, "stop_loss": None},
            {"ticker": "BBB", "signal": fsm.SIG_WATCH, "confidence": 0.60, "stop_loss": None},
            {"ticker": "CCC", "signal": fsm.SIG_BUY, "confidence": 0.70, "stop_loss": 99.0},
        ]
        ns_map = {
            "AAA": {"bearish_no_price_follow": True},
            "BBB": {"bearish_no_price_follow": False},
            "CCC": {"bearish_no_price_follow": True},  # ignored: not WATCH
        }
        bumped = dp._apply_news_bump_to_watch(rows, ns_map)
        assert bumped == 1
        assert rows[0]["confidence"] == 0.75   # AAA bumped
        assert rows[1]["confidence"] == 0.60   # BBB untouched
        assert rows[2]["confidence"] == 0.70   # CCC (BUY) untouched

    def test_bump_respects_085_cap(self):
        rows = [{"ticker": "X", "signal": fsm.SIG_WATCH, "confidence": 0.82, "stop_loss": None}]
        ns_map = {"X": {"bearish_no_price_follow": True}}
        dp._apply_news_bump_to_watch(rows, ns_map)
        assert rows[0]["confidence"] == 0.85   # capped, not 0.92
