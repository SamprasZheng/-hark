"""Offline tests for the stdlib CoinGecko markets client. No network calls.

An injected ``opener`` feeds canned responses / raises, mirroring the mock style of
``test_nemotron_client.py``. ``time.sleep`` is replaced by a recorder so retry/backoff
paths run instantly and are asserted.
"""

from __future__ import annotations

import email.message
import io
import json
import urllib.error

import pytest

from sharks.data import coingecko_client as ccg


def _resp(payload):
    """Fake urlopen context manager whose ``read()`` returns the JSON-encoded payload."""
    body = json.dumps(payload).encode("utf-8")

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


def _http_error(code, retry_after=None, url="https://api.coingecko.com/x"):
    return urllib.error.HTTPError(url, code, "err", _hdrs(retry_after), io.BytesIO(b""))


# ── normalize_market_row ──────────────────────────────────────────────────────

class TestNormalize:
    def test_full_row_maps_and_uppercases_symbol(self):
        raw = {
            "id": "bitcoin", "symbol": "btc", "name": "Bitcoin", "market_cap_rank": 1,
            "current_price": 60000, "market_cap": 1.2e12, "fully_diluted_valuation": 1.3e12,
            "total_volume": 3e10, "high_24h": 61000, "low_24h": 59000,
            "circulating_supply": 19.8e6, "total_supply": 21e6, "max_supply": 21e6,
            "ath": 109000, "ath_change_percentage": -45.0, "ath_date": "2025-01-20T00:00:00Z",
            "last_updated": "2026-05-31T00:00:00Z",
            "price_change_percentage_1h_in_currency": 0.2,
            "price_change_percentage_24h_in_currency": -2.5,
            "price_change_percentage_7d_in_currency": 5.0,
            "price_change_percentage_30d_in_currency": -10.0,
            "price_change_percentage_1y_in_currency": 30.0,
        }
        row = ccg.normalize_market_row(raw)
        assert row["symbol"] == "BTC"
        assert row["market_cap_rank"] == 1
        assert row["price_change_pct_1h"] == 0.2
        assert row["price_change_pct_24h"] == -2.5
        assert row["price_change_pct_7d"] == 5.0
        assert row["price_change_pct_30d"] == -10.0
        assert row["price_change_pct_1y"] == 30.0
        assert row["max_supply"] == 21e6

    def test_missing_fields_become_none_not_keyerror(self):
        row = ccg.normalize_market_row({"id": "x", "symbol": "x"})
        assert row["symbol"] == "X"
        assert row["market_cap"] is None
        assert row["price_change_pct_1h"] is None
        assert row["price_change_pct_24h"] is None
        assert row["ath"] is None

    def test_plain_24h_field_is_fallback(self):
        row = ccg.normalize_market_row({"symbol": "eth", "price_change_percentage_24h": -1.1})
        assert row["price_change_pct_24h"] == -1.1


# ── fetch_markets ─────────────────────────────────────────────────────────────

class TestFetchMarkets:
    def test_happy_path_builds_query_and_normalizes(self):
        seen = {}

        def opener(req, timeout=None):
            seen["url"] = req.full_url
            seen["ua"] = req.get_header("User-agent")
            return _resp([{"id": "bitcoin", "symbol": "btc", "name": "Bitcoin", "market_cap_rank": 1}])

        rows = ccg.fetch_markets(opener=opener, sleep=lambda *_: None)
        assert rows[0]["symbol"] == "BTC"
        assert "vs_currency=usd" in seen["url"]
        assert "order=market_cap_desc" in seen["url"]
        assert "per_page=100" in seen["url"]
        assert seen["ua"]  # User-Agent always set

    def test_non_list_payload_raises(self):
        def opener(req, timeout=None):
            return _resp({"error": "nope"})

        with pytest.raises(ccg.CoinGeckoError):
            ccg.fetch_markets(opener=opener, sleep=lambda *_: None)

    def test_429_then_success_honours_retry_after(self):
        state = {"i": 0}
        slept = []

        def opener(req, timeout=None):
            i = state["i"]
            state["i"] += 1
            if i < 2:
                raise _http_error(429, retry_after=7)
            return _resp([{"id": "bitcoin", "symbol": "btc", "name": "Bitcoin", "market_cap_rank": 1}])

        rows = ccg.fetch_markets(opener=opener, sleep=lambda s: slept.append(s))
        assert rows[0]["symbol"] == "BTC"
        assert slept[:2] == [7.0, 7.0]  # Retry-After respected, not exponential backoff

    def test_persistent_503_exhausts_and_raises(self):
        def opener(req, timeout=None):
            raise _http_error(503)

        with pytest.raises(ccg.CoinGeckoError):
            ccg.fetch_markets(opener=opener, sleep=lambda *_: None, max_retries=3)

    def test_4xx_other_than_429_is_fatal_immediately(self):
        calls = {"n": 0}

        def opener(req, timeout=None):
            calls["n"] += 1
            raise _http_error(404)

        with pytest.raises(ccg.CoinGeckoError):
            ccg.fetch_markets(opener=opener, sleep=lambda *_: None, max_retries=4)
        assert calls["n"] == 1  # no retries on a hard 4xx

    def test_transport_error_retries_then_raises(self):
        slept = []

        def opener(req, timeout=None):
            raise urllib.error.URLError("conn refused")

        with pytest.raises(ccg.CoinGeckoError):
            ccg.fetch_markets(opener=opener, sleep=lambda s: slept.append(s), max_retries=3)
        assert len(slept) == 2  # retried before the final raise (no wasted final sleep)


class TestRetryAfterParsing:
    def test_seconds_form(self):
        assert ccg._retry_after_seconds(_http_error(429, retry_after=12)) == 12.0

    def test_absent_is_none(self):
        assert ccg._retry_after_seconds(_http_error(429)) is None
