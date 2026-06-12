"""Offline tests for the stdlib FRED CSV client. No network calls.

An injected ``opener`` feeds canned CSV / raises, mirroring
``test_coingecko_client.py``. ``time.sleep`` is a recorder so retry/backoff runs
instantly and is asserted.
"""

from __future__ import annotations

import email.message
import io
import urllib.error

import pytest

from sharks.data import fred_client as fc

WALCL_CSV = (
    "observation_date,WALCL\n"
    "2026-02-01,7000000\n"
    "2026-03-01,7100000\n"
    "2026-04-01,.\n"
    "2026-05-01,7250000\n"
)


def _resp(text: str):
    body = text.encode("utf-8")

    class _Ctx:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            return body

    return _Ctx()


def _hdrs(retry_after=None):
    m = email.message.Message()
    if retry_after is not None:
        m["Retry-After"] = str(retry_after)
    return m


def _http_error(code, retry_after=None, url="https://fred.stlouisfed.org/x"):
    return urllib.error.HTTPError(url, code, "err", _hdrs(retry_after), io.BytesIO(b""))


class TestParseFredCsv:
    def test_header_skipped_and_values_parsed(self):
        rows = fc.parse_fred_csv(WALCL_CSV)
        assert rows[0] == ("2026-02-01", 7000000.0)
        assert len(rows) == 4  # header dropped

    def test_dot_missing_marker_becomes_none(self):
        rows = dict(fc.parse_fred_csv(WALCL_CSV))
        assert rows["2026-04-01"] is None

    def test_legacy_DATE_header_skipped(self):
        rows = fc.parse_fred_csv("DATE,RRPONTSYD\n2026-05-01,500.0\n")
        assert rows == [("2026-05-01", 500.0)]

    def test_blank_and_malformed_lines_tolerated(self):
        rows = fc.parse_fred_csv("observation_date,X\n\n2026-05-01,1.0\ngarbage\n")
        assert rows == [("2026-05-01", 1.0)]


class TestFetchSeries:
    def test_happy_path_builds_query_and_stamps(self):
        seen = {}

        def opener(req, timeout=None):
            seen["url"] = req.full_url
            seen["ua"] = req.get_header("User-agent")
            return _resp(WALCL_CSV)

        rows = fc.fetch_series(
            "WALCL", start="2026-02-01", end="2026-05-01",
            opener=opener, sleep=lambda *_: None,
        )
        assert "id=WALCL" in seen["url"]
        assert "cosd=2026-02-01" in seen["url"]
        assert "coed=2026-05-01" in seen["url"]
        assert seen["ua"]
        assert rows[0]["series_id"] == "WALCL"
        assert rows[0]["as_of_timestamp"] == "2026-02-01"
        # live path: no vintage → source_first_visible_at left None (may be revised)
        assert rows[0]["source_first_visible_at"] is None

    def test_fetch_latest_skips_missing_tail(self):
        def opener(req, timeout=None):
            return _resp("observation_date,X\n2026-05-01,5.0\n2026-05-08,.\n")

        latest = fc.fetch_latest("X", opener=opener, sleep=lambda *_: None)
        assert latest["value"] == 5.0  # the "." tail is skipped

    def test_429_then_success_honours_retry_after(self):
        state = {"i": 0}
        slept = []

        def opener(req, timeout=None):
            i = state["i"]
            state["i"] += 1
            if i < 2:
                raise _http_error(429, retry_after=5)
            return _resp(WALCL_CSV)

        rows = fc.fetch_series("WALCL", opener=opener, sleep=lambda s: slept.append(s))
        assert rows
        assert slept[:2] == [5.0, 5.0]

    def test_persistent_503_exhausts_and_raises(self):
        def opener(req, timeout=None):
            raise _http_error(503)

        with pytest.raises(fc.FREDError):
            fc.fetch_series("WALCL", opener=opener, sleep=lambda *_: None, max_retries=3)

    def test_4xx_other_than_429_is_fatal_immediately(self):
        calls = {"n": 0}

        def opener(req, timeout=None):
            calls["n"] += 1
            raise _http_error(404)

        with pytest.raises(fc.FREDError):
            fc.fetch_series("WALCL", opener=opener, sleep=lambda *_: None, max_retries=4)
        assert calls["n"] == 1

    def test_transport_error_retries_then_raises(self):
        slept = []

        def opener(req, timeout=None):
            raise urllib.error.URLError("conn refused")

        with pytest.raises(fc.FREDError):
            fc.fetch_series("WALCL", opener=opener, sleep=lambda s: slept.append(s), max_retries=3)
        assert len(slept) == 2


class TestVintage:
    def test_vintage_date_in_url_and_stamped(self):
        # The PIT acceptance contract: a vintage request stamps
        # source_first_visible_at to the vintage, not the (possibly later) revision.
        seen = {}

        def opener(req, timeout=None):
            seen["url"] = req.full_url
            return _resp("observation_date,WALCL\n2020-03-13,4000000\n")

        rows = fc.fetch_series(
            "WALCL", vintage_date="2020-03-15", opener=opener, sleep=lambda *_: None
        )
        assert "vintage_date=2020-03-15" in seen["url"]
        assert rows[0]["source_first_visible_at"] == "2020-03-15"
        assert rows[0]["vintage_date"] == "2020-03-15"
        # observation date is on/before the vintage (no lookahead)
        assert rows[0]["as_of_timestamp"] <= "2020-03-15"
