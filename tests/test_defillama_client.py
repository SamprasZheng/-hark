"""Offline tests for the stdlib DefiLlama stablecoins client. No network calls.

Mirrors ``test_coingecko_client.py``: an injected ``opener`` feeds canned JSON /
raises, and ``time.sleep`` is a recorder so retry/backoff runs instantly.
"""

from __future__ import annotations

import email.message
import io
import json
import urllib.error

import pytest

from sharks.data import defillama_client as dl


def _resp(payload):
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


def _http_error(code, retry_after=None, url="https://stablecoins.llama.fi/x"):
    return urllib.error.HTTPError(url, code, "err", _hdrs(retry_after), io.BytesIO(b""))


_PAYLOAD = {
    "peggedAssets": [
        {"name": "Tether", "symbol": "USDT", "circulating": {"peggedUSD": 140e9}},
        {"name": "USD Coin", "symbol": "USDC", "circulating": {"peggedUSD": 60e9}},
        {"name": "Dai", "symbol": "DAI", "circulating": {"peggedUSD": 5e9}},
        {"name": "Broken", "symbol": "BAD", "circulating": {}},      # no peggedUSD → skipped
        {"name": "AlsoBroken", "symbol": "BAD2"},                    # no circulating → skipped
    ]
}


class TestNormalize:
    def test_sums_pegged_usd_and_skips_missing(self):
        out = dl.normalize_stablecoins(_PAYLOAD, as_of="2026-05-31T00:00:00+00:00")
        assert out["total_circulating_usd"] == round(205e9, 2)
        assert out["asset_count"] == 3  # two broken assets skipped, not invented
        assert out["by_asset"]["USDT"] == 140e9
        assert out["source"] == "defillama"
        assert out["as_of_timestamp"] == "2026-05-31T00:00:00+00:00"
        assert out["source_first_visible_at"] == "2026-05-31T00:00:00+00:00"

    def test_empty_assets_total_none(self):
        out = dl.normalize_stablecoins({"peggedAssets": []})
        assert out["total_circulating_usd"] is None
        assert out["asset_count"] == 0

    def test_bad_payload_raises(self):
        with pytest.raises(dl.DefiLlamaError):
            dl.normalize_stablecoins({"nope": 1})


class TestFetch:
    def test_happy_path_sets_ua_and_parses(self):
        seen = {}

        def opener(req, timeout=None):
            seen["url"] = req.full_url
            seen["ua"] = req.get_header("User-agent")
            return _resp(_PAYLOAD)

        out = dl.fetch_stablecoin_supply(opener=opener, sleep=lambda *_: None)
        assert out["total_circulating_usd"] == round(205e9, 2)
        assert "stablecoins.llama.fi" in seen["url"]
        assert seen["ua"]

    def test_429_then_success_honours_retry_after(self):
        state = {"i": 0}
        slept = []

        def opener(req, timeout=None):
            i = state["i"]
            state["i"] += 1
            if i < 2:
                raise _http_error(429, retry_after=4)
            return _resp(_PAYLOAD)

        out = dl.fetch_stablecoin_supply(opener=opener, sleep=lambda s: slept.append(s))
        assert out["asset_count"] == 3
        assert slept[:2] == [4.0, 4.0]

    def test_persistent_503_exhausts_and_raises(self):
        def opener(req, timeout=None):
            raise _http_error(503)

        with pytest.raises(dl.DefiLlamaError):
            dl.fetch_stablecoin_supply(opener=opener, sleep=lambda *_: None, max_retries=3)

    def test_4xx_other_than_429_is_fatal_immediately(self):
        calls = {"n": 0}

        def opener(req, timeout=None):
            calls["n"] += 1
            raise _http_error(404)

        with pytest.raises(dl.DefiLlamaError):
            dl.fetch_stablecoin_supply(opener=opener, sleep=lambda *_: None, max_retries=4)
        assert calls["n"] == 1

    def test_transport_error_retries_then_raises(self):
        slept = []

        def opener(req, timeout=None):
            raise urllib.error.URLError("conn refused")

        with pytest.raises(dl.DefiLlamaError):
            dl.fetch_stablecoin_supply(opener=opener, sleep=lambda s: slept.append(s), max_retries=3)
        assert len(slept) == 2
