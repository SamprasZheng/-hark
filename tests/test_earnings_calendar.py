"""Offline tests for the earnings-date calendar (data/earnings_calendar.py).

Pure / lake-first; no network. Timestamps are built from UTC dates so they are
deterministic regardless of the machine timezone.
"""

from __future__ import annotations

import datetime as dt
import json

from sharks.data import earnings_calendar as ec


def _ts(y, m, d) -> float:
    return dt.datetime(y, m, d, tzinfo=dt.timezone.utc).timestamp()


class TestLakeParse:
    def test_earnings_timestamp_to_date(self):
        info = {"earningsTimestamp": _ts(2026, 8, 27), "isEarningsDateEstimate": False,
                "mostRecentQuarter": _ts(2026, 4, 30), "_snapshot_time": "2026-06-10T00:00:00Z"}
        rec = ec.lake_earnings(info)
        assert rec["date"] == "2026-08-27"
        assert rec["is_estimate"] is False
        assert rec["most_recent_quarter"] == "2026-04-30"
        assert rec["source"] == "lake"

    def test_no_earnings_field_returns_none(self):
        assert ec.lake_earnings({"marketCap": 1}) is None


class TestDaysAndBlackout:
    def test_days_to(self):
        assert ec.days_to_earnings("2026-06-12", "2026-06-09") == 3

    def test_in_blackout_within_window(self):
        assert ec.in_blackout(3) is True
        assert ec.in_blackout(4) is False
        assert ec.in_blackout(-1) is False
        assert ec.in_blackout(None) is False


class TestPredict:
    def test_rolls_quarterly_to_future(self):
        # last 2026-03-01, asof 2026-06-09 → +91 (05-31) still past → +91 = 08-30
        assert ec.predict_next("2026-03-01", "2026-06-09") == "2026-08-30"

    def test_future_anchor_steps_once(self):
        # already future → still steps strictly past asof
        assert ec.predict_next("2026-06-01", "2026-06-09") == "2026-08-31"


class TestNextEarnings:
    def test_prefers_future_lake_date(self):
        lake = {"NVDA": {"ticker": "NVDA", "date": "2026-08-27", "is_estimate": False}}
        ne = ec.next_earnings("NVDA", lake=lake, asof="2026-06-09")
        assert ne["date"] == "2026-08-27"
        assert ne["predicted"] is False
        assert ne["days_to"] == 79

    def test_predicts_when_lake_date_is_past(self):
        lake = {"AMD": {"ticker": "AMD", "date": "2026-03-01", "is_estimate": False}}
        ne = ec.next_earnings("AMD", lake=lake, asof="2026-06-09")
        assert ne["predicted"] is True
        assert ne["source"] == "predicted"
        assert ne["date"] == "2026-08-30"

    def test_none_when_no_data(self):
        assert ec.next_earnings("ZZZ", lake={}, history={}, asof="2026-06-09") is None


class TestHistory:
    def test_append_dedups(self, tmp_path):
        hp = tmp_path / "calendar.jsonl"
        recs = [{"ticker": "NVDA", "date": "2026-08-27", "is_estimate": False}]
        assert ec.append_history(recs, hp) == 1
        assert ec.append_history(recs, hp) == 0  # same (ticker,date) → no dup
        hist = ec.load_history(hp)
        assert hist["NVDA"] == ["2026-08-27"]


class TestUpcoming:
    def test_window_and_blackout_flag(self):
        lake = {
            "AAA": {"ticker": "AAA", "date": "2026-06-19", "is_estimate": True},   # T-10
            "BBB": {"ticker": "BBB", "date": "2026-07-09", "is_estimate": True},   # T-30 (outside 14)
            "CCC": {"ticker": "CCC", "date": "2026-06-11", "is_estimate": False},  # T-2 → blackout
        }
        up = ec.upcoming_within(lake, asof="2026-06-09", days=14)
        tickers = [r["ticker"] for r in up]
        assert tickers == ["CCC", "AAA"]            # soonest first, BBB excluded
        assert up[0]["blackout"] is True            # CCC within 3d
        assert up[1]["blackout"] is False


class TestBuildCalendar:
    def test_reads_lake_and_writes_summary(self, tmp_path):
        lake_dir = tmp_path / "info"
        lake_dir.mkdir()
        (lake_dir / "NVDA.json").write_text(json.dumps({
            "earningsTimestamp": _ts(2026, 6, 12), "isEarningsDateEstimate": False,
            "_snapshot_time": "2026-06-10T00:00:00Z"}), encoding="utf-8")
        out_dir = tmp_path / "earnings"
        hist = tmp_path / "calendar.jsonl"
        s = ec.build_calendar(lake_dir=lake_dir, out_dir=out_dir, asof="2026-06-09",
                              history_path=hist)
        assert s["tickers_with_dates"] == 1
        assert s["history_rows_added"] == 1
        assert any(r["ticker"] == "NVDA" for r in s["upcoming"])
        assert "NVDA" in s["blackout"]              # T-3 → blackout
        assert (out_dir / "upcoming-2026-06-09.json").exists()
