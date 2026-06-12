"""Tests for the crypto Top-100 tracker — pure transforms + the stale-fallback
degrade path. No network: the fetch is exercised through an injected opener that
either returns canned markets or raises (mirroring test_daily_health_check's
degrade tests + test_nemotron_client's mock style).
"""

from __future__ import annotations

import json
import urllib.error

import pytest

from sharks.scoring import crypto_top100 as ct


# ── fixtures ──────────────────────────────────────────────────────────────────

def _coins():
    """Normalised-style rows (symbols already upper-cased) with hand-computable caps."""
    return [
        {"symbol": "BTC", "name": "Bitcoin", "market_cap": 600, "market_cap_rank": 1,
         "price_change_pct_24h": 1.0, "price_change_pct_7d": 3.0},
        {"symbol": "ETH", "name": "Ethereum", "market_cap": 200, "market_cap_rank": 2,
         "price_change_pct_24h": -2.0, "price_change_pct_7d": 1.0},
        {"symbol": "USDT", "name": "Tether", "market_cap": 100, "market_cap_rank": 3,
         "price_change_pct_24h": 0.0, "price_change_pct_7d": 0.1},
        {"symbol": "SOL", "name": "Solana", "market_cap": 80, "market_cap_rank": 4,
         "price_change_pct_24h": 5.0, "price_change_pct_7d": 10.0},
        {"symbol": "DOT", "name": "Polkadot", "market_cap": 20, "market_cap_rank": 5,
         "price_change_pct_24h": -4.0, "price_change_pct_7d": -8.0},
        {"symbol": "WTF", "name": "NewThing", "market_cap": 10, "market_cap_rank": 6,
         "price_change_pct_24h": 12.0, "price_change_pct_7d": 20.0},
    ]


_WL = {
    "category_tags": {"l1": ["BTC", "ETH", "SOL", "DOT"], "payments": ["XRP"]},
    "stablecoins": ["USDT"],
    "human_overrides": {
        "DOT": "過去重虧；嚴守 4% 名目上限；不可只憑敘事加碼。",
        "BTC": "核心宏觀資產、Alpha 之外、≤4% 名目硬頂、機械式 DCA。",
    },
}

_WATCHLIST_FIXTURE = '''---
schema_version: 1
as_of: "2026-05-31"
tier1_flagship: [BTC, ETH]
tier3_discovery_pool: []
stablecoins: [USDT, USDC]
category_tags:
  l1: [BTC, ETH, SOL, DOT]
  payments: [XRP, XLM]
human_overrides:
  DOT: "過去重虧；嚴守 4% 名目上限；不可只憑敘事加碼。"
  BTC: "核心宏觀資產、Alpha 之外、≤4% 名目硬頂。"
---

# notes below the fence are ignored by load_watchlist
'''


def _raw_markets():
    """CoinGecko-shaped raw rows for end-to-end (lowercase symbols, *_in_currency pct)."""
    return [
        {"id": "bitcoin", "symbol": "btc", "name": "Bitcoin", "market_cap_rank": 1, "market_cap": 600,
         "price_change_percentage_24h_in_currency": 1.5, "price_change_percentage_7d_in_currency": 3.0},
        {"id": "ethereum", "symbol": "eth", "name": "Ethereum", "market_cap_rank": 2, "market_cap": 200,
         "price_change_percentage_24h_in_currency": -2.0, "price_change_percentage_7d_in_currency": 1.0},
        {"id": "tether", "symbol": "usdt", "name": "Tether", "market_cap_rank": 3, "market_cap": 100,
         "price_change_percentage_24h_in_currency": 0.0, "price_change_percentage_7d_in_currency": 0.1},
        {"id": "solana", "symbol": "sol", "name": "Solana", "market_cap_rank": 4, "market_cap": 80,
         "price_change_percentage_24h_in_currency": 5.0, "price_change_percentage_7d_in_currency": 10.0},
    ]


def _ok_opener(payload):
    def opener(req, timeout=None):
        body = json.dumps(payload).encode("utf-8")

        class _Ctx:
            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

            def read(self):
                return body

        return _Ctx()

    return opener


# ── pure transforms ───────────────────────────────────────────────────────────

class TestCategorize:
    def test_known_unknown_and_stable(self):
        cats = ct.categorize(_coins(), _WL["category_tags"], _WL["stablecoins"])
        assert set(cats["l1"]) == {"BTC", "ETH", "SOL", "DOT"}
        assert cats["stablecoin"] == ["USDT"]
        assert cats["uncategorized"] == ["WTF"]  # in no tag, not stable → surfaced
        assert "USDT" not in cats["uncategorized"]


class TestMarketStructure:
    def test_math_on_hand_fixture(self):
        ms = ct.market_structure(_coins(), _WL["stablecoins"])
        # total = 600+200+100+80+20+10 = 1010
        assert ms["total_market_cap"] == 1010
        assert ms["coin_count"] == 6
        assert ms["btc_dominance_pct"] == round(100 * 600 / 1010, 2)
        assert ms["eth_share_pct"] == round(100 * 200 / 1010, 2)
        assert ms["stablecoin_share_pct"] == round(100 * 100 / 1010, 2)
        assert ms["top10_concentration_pct"] == 100.0  # only 6 coins → all of them

    def test_empty_is_safe(self):
        ms = ct.market_structure([], ["USDT"])
        assert ms["total_market_cap"] == 0
        assert ms["btc_dominance_pct"] is None


class TestMovers:
    def test_sorting(self):
        m = ct.compute_movers(_coins(), "price_change_pct_24h", 2)
        assert [g["symbol"] for g in m["gainers"]] == ["WTF", "SOL"]   # +12, +5
        assert [l["symbol"] for l in m["losers"]] == ["DOT", "ETH"]    # -4, -2
        assert m["window"] == "price_change_pct_24h"

    def test_max_rank_filters_microcaps(self):
        coins = _coins() + [
            {"symbol": "MICRO", "market_cap": 1, "market_cap_rank": 99, "price_change_pct_24h": 999.0},
        ]
        m = ct.compute_movers(coins, "price_change_pct_24h", 3, max_rank=50)
        assert "MICRO" not in [g["symbol"] for g in m["gainers"]]  # rank 99 excluded despite +999%
        assert m["max_rank"] == 50


class TestRankChurn:
    def test_new_dropped_and_moves(self):
        today = {"coins": [
            {"symbol": "BTC", "market_cap_rank": 1},
            {"symbol": "ETH", "market_cap_rank": 2},
            {"symbol": "SOL", "market_cap_rank": 3},  # was 5 → +2
        ]}
        prev = {"coins": [
            {"symbol": "BTC", "market_cap_rank": 1},
            {"symbol": "SOL", "market_cap_rank": 5},
            {"symbol": "XRP", "market_cap_rank": 2},  # dropped out
        ]}
        ch = ct.rank_churn(today, prev)
        assert ch["available"] is True
        assert ch["new_entrants"] == ["ETH"]
        assert ch["dropped_out"] == ["XRP"]
        assert ch["biggest_rank_moves"][0]["symbol"] == "SOL"
        assert ch["biggest_rank_moves"][0]["delta"] == 2

    def test_no_prior_degrades(self):
        assert ct.rank_churn({"coins": []}, None)["available"] is False


class TestLoadWatchlist:
    def test_parses_fenced_yaml_without_pyyaml(self, tmp_path):
        p = tmp_path / "watchlist.yaml"
        p.write_text(_WATCHLIST_FIXTURE, encoding="utf-8")
        wl = ct.load_watchlist(p)
        assert wl["tier1_flagship"] == ["BTC", "ETH"]
        assert wl["tier3_discovery_pool"] == []
        assert wl["stablecoins"] == ["USDT", "USDC"]
        assert wl["category_tags"]["l1"] == ["BTC", "ETH", "SOL", "DOT"]
        assert wl["category_tags"]["payments"] == ["XRP", "XLM"]
        assert "DOT" in wl["human_overrides"]
        assert "4%" in wl["human_overrides"]["DOT"]

    def test_absent_file_is_empty(self, tmp_path):
        assert ct.load_watchlist(tmp_path / "nope.yaml") == {}


class TestSnapshotRoundTrip:
    def test_write_and_read_back(self, tmp_path):
        snap = ct.build_snapshot_envelope(
            _coins(), as_of="2026-05-31T00:00:00+00:00", as_of_date="2026-05-31",
            vs_currency="usd", live_data=True, stale={}, source_per_page=100,
        )
        path = ct.write_snapshot(snap, tmp_path)
        assert path.name == "top100-2026-05-31.json"
        back = json.loads(path.read_text(encoding="utf-8"))
        assert back["count"] == 6
        assert back["live_data"] is True
        assert back["stale_fallback"] is False
        assert back["coins"][0]["symbol"] == "BTC"  # upper-case preserved


class TestRenderMarkdown:
    def test_dot_spotlight_and_sections(self):
        snap = ct.build_snapshot_envelope(
            _coins(), as_of="2026-05-31T00:00:00+00:00", as_of_date="2026-05-31",
            vs_currency="usd", live_data=True, stale={}, source_per_page=100,
        )
        ms = ct.market_structure(_coins(), _WL["stablecoins"])
        cats = ct.categorize(_coins(), _WL["category_tags"], _WL["stablecoins"])
        m24 = ct.compute_movers(_coins(), "price_change_pct_24h", 3)
        m7 = ct.compute_movers(_coins(), "price_change_pct_7d", 3)
        md = ct.render_markdown(snap, ms, m24, m7, cats, ct.rank_churn(snap, None), _WL)
        assert "## Market structure" in md
        assert "DOT — rank #5" in md          # DOT spotlight rendered with its rank
        assert "4%" in md                       # the override text surfaced
        assert "Uncategorized (1)" in md        # WTF flagged as a new-narrative candidate
        assert "RECOMMEND-ONLY" in md           # guardrails banner present


# ── orchestration: happy path + stale fallback ────────────────────────────────

class TestRunHappyPath:
    def test_live_run_writes_all_three_artifacts(self, tmp_path):
        handoff = ct.run_crypto_top100(
            out_dir=tmp_path / "out", data_dir=tmp_path / "data",
            watchlist_path=_write(tmp_path, _WATCHLIST_FIXTURE), analysis_dir=tmp_path / "analysis",
            today="2026-05-31T12:00:00+00:00", opener=_ok_opener(_raw_markets()),
            sleep=lambda *_: None,
        )
        assert handoff["live_data"] is True
        assert handoff["stale_fallback"] is False
        assert handoff["market_structure"]["coin_count"] == 4
        assert (tmp_path / "data" / "top100-2026-05-31.json").exists()
        assert (tmp_path / "analysis" / "top100-2026-05-31.md").exists()
        assert (tmp_path / "out" / "crypto-top100-2026-05-31.json").exists()


class TestStaleFallback:
    def test_fetch_failure_reemits_prior_under_today(self, tmp_path):
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        prior = {
            "schema_version": 1, "as_of": "2026-05-30T00:00:00+00:00", "as_of_date": "2026-05-30",
            "source": "coingecko", "vs_currency": "usd", "count": 2,
            "live_data": True, "stale_fallback": False,
            "coins": [
                {"symbol": "BTC", "market_cap": 600, "market_cap_rank": 1},
                {"symbol": "ETH", "market_cap": 200, "market_cap_rank": 2},
            ],
        }
        (data_dir / "top100-2026-05-30.json").write_text(json.dumps(prior), encoding="utf-8")

        def boom(req, timeout=None):
            raise urllib.error.URLError("no network")

        handoff = ct.run_crypto_top100(
            out_dir=tmp_path / "out", data_dir=data_dir,
            watchlist_path=_write(tmp_path, _WATCHLIST_FIXTURE), analysis_dir=tmp_path / "analysis",
            today="2026-05-31T12:00:00+00:00", opener=boom, sleep=lambda *_: None,
        )
        assert handoff["live_data"] is False
        assert handoff["stale_fallback"] is True

        snap = json.loads((data_dir / "top100-2026-05-31.json").read_text(encoding="utf-8"))
        assert snap["as_of_date"] == "2026-05-31"        # new honest date, not the old one
        assert snap["live_data"] is False
        assert snap["stale_fallback"] is True
        assert snap["stale_source_as_of"] == "2026-05-30T00:00:00+00:00"
        assert snap["count"] == 2                         # prior coins re-emitted
        # analysis still written (degrade, note, never crash)
        assert (tmp_path / "analysis" / "top100-2026-05-31.md").exists()


def _write(tmp_path, text):
    p = tmp_path / "watchlist.yaml"
    p.write_text(text, encoding="utf-8")
    return p


# ── on-chain liquidity proxy (prototype) ──────────────────────────────────────

def _stables_payload():
    return {"peggedAssets": [
        {"name": "Tether", "symbol": "USDT", "circulating": {"peggedUSD": 140e9}},
        {"name": "USD Coin", "symbol": "USDC", "circulating": {"peggedUSD": 60e9}},
        {"name": "Dai", "symbol": "DAI", "circulating": {"peggedUSD": 5e9}},
    ]}  # total = 205e9


class TestStablecoinSupplyTrend:
    def test_trend_math(self):
        tr = ct.stablecoin_supply_trend(
            {"total_circulating_usd": 210.0}, {"total_circulating_usd": 200.0}
        )
        assert tr["available"] is True
        assert tr["delta_usd"] == 10.0
        assert tr["pct_change"] == 5.0
        assert tr["direction"] == "expanding"

    def test_no_prior_reports_level_but_no_trend(self):
        tr = ct.stablecoin_supply_trend({"total_circulating_usd": 210.0}, None)
        assert tr["available"] is True
        assert tr["delta_usd"] is None

    def test_no_current_reading_unavailable(self):
        assert ct.stablecoin_supply_trend(None, {"total_circulating_usd": 200.0})["available"] is False


class TestOnchainHappyPath:
    def test_independent_onchain_feed_populates_block(self, tmp_path):
        handoff = ct.run_crypto_top100(
            out_dir=tmp_path / "out", data_dir=tmp_path / "data",
            watchlist_path=_write(tmp_path, _WATCHLIST_FIXTURE), analysis_dir=tmp_path / "analysis",
            today="2026-05-31T12:00:00+00:00",
            opener=_ok_opener(_raw_markets()),          # price feed
            onchain_opener=_ok_opener(_stables_payload()),  # on-chain feed
            sleep=lambda *_: None,
        )
        assert handoff["live_data"] is True
        oc = handoff["onchain"]
        assert oc["live_data"] is True
        assert oc["stablecoin_supply"]["total_circulating_usd"] == round(205e9, 2)


class TestOnchainStaleFallback:
    def test_onchain_outage_does_not_take_down_price_snapshot(self, tmp_path):
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        prior = {
            "schema_version": 1, "as_of": "2026-05-30T00:00:00+00:00", "as_of_date": "2026-05-30",
            "source": "coingecko", "vs_currency": "usd", "count": 2,
            "live_data": True, "stale_fallback": False,
            "coins": [{"symbol": "BTC", "market_cap": 600, "market_cap_rank": 1}],
            "onchain": {
                "live_data": True, "stale_fallback": False, "source": "defillama",
                "stablecoin_supply": {"total_circulating_usd": 200e9, "asset_count": 3},
            },
        }
        (data_dir / "top100-2026-05-30.json").write_text(json.dumps(prior), encoding="utf-8")

        def boom(req, timeout=None):
            raise urllib.error.URLError("defillama down")

        handoff = ct.run_crypto_top100(
            out_dir=tmp_path / "out", data_dir=data_dir,
            watchlist_path=_write(tmp_path, _WATCHLIST_FIXTURE), analysis_dir=tmp_path / "analysis",
            today="2026-05-31T12:00:00+00:00",
            opener=_ok_opener(_raw_markets()),  # price feed LIVE
            onchain_opener=boom,                # on-chain feed DOWN
            sleep=lambda *_: None,
        )
        # Independent degrade: price snapshot stays live, only the on-chain column is stale.
        assert handoff["live_data"] is True
        assert handoff["stale_fallback"] is False
        oc = handoff["onchain"]
        assert oc["live_data"] is False
        assert oc["stale_fallback"] is True
        assert oc["stablecoin_supply"]["total_circulating_usd"] == 200e9  # prior re-emitted
