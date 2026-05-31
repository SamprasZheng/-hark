"""CoinGecko markets client — stdlib, dependency-free cross-sectional crypto data.

Complements ``data/ccxt_client.py`` (single-symbol exchange OHLCV / orderbook for
weekend high-freq, Phase 2). This client pulls the cross-sectional market-cap
ranking + metadata for the top-N coins in ONE request — the breadth snapshot the
crypto Top-100 tracker compiles daily. Free tier, no API key required.

``urllib`` only (no ``requests``), matching ``data/finnhub_integration.py`` and
``scoring/real_universe_fetcher.py``, so $hark stays dependency-free
(``pyproject.toml`` declares ``dependencies = []``). Same discipline as
``ai/nemotron_client.py``: every transport error is handled, retries back off,
and a hard failure raises ``CoinGeckoError`` so the caller
(``scoring/crypto_top100.py``) can fall back to the last good snapshot and flag it
stale — this client NEVER invents prices.

Endpoint (top-100 in a single request, no pagination):
    GET /coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page=1
        &sparkline=false&price_change_percentage=1h,24h,7d,30d,1y&locale=en

Free-tier rate is ~10-30 req/min; one call per day is far under budget.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Optional

COINGECKO_BASE = "https://api.coingecko.com/api/v3"
MARKETS_PATH = "/coins/markets"
DEFAULT_USER_AGENT = "sharks-crypto-tracker/0.1 (+https://github.com/SamprasZheng)"
PRICE_CHANGE_WINDOWS = "1h,24h,7d,30d,1y"

# Raw CoinGecko percentage fields → stable snake_case. When
# price_change_percentage=...,Nd,... is requested, CoinGecko returns the windowed
# value as ``price_change_percentage_<win>_in_currency``.
_PCT_KEYS = {
    "1h": "price_change_pct_1h",
    "24h": "price_change_pct_24h",
    "7d": "price_change_pct_7d",
    "30d": "price_change_pct_30d",
    "1y": "price_change_pct_1y",
}


class CoinGeckoError(RuntimeError):
    """Raised when markets data cannot be fetched after exhausting retries."""


def _retry_after_seconds(exc) -> Optional[float]:
    """Parse a ``Retry-After`` header (seconds form) off an HTTPError; None if absent."""
    hdrs = getattr(exc, "headers", None) or getattr(exc, "hdrs", None)
    if hdrs is None:
        return None
    try:
        val = hdrs.get("Retry-After")
    except Exception:
        return None
    if val is None:
        return None
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def _request_json(
    url: str,
    *,
    opener=None,
    max_retries: int = 4,
    timeout: float = 30.0,
    base_backoff: float = 1.5,
    sleep=time.sleep,
):
    """GET ``url`` → parsed JSON, retrying on 429 / 5xx / transport / non-JSON.

    ``opener`` is injectable (defaults to ``urllib.request.urlopen``) so tests can
    feed canned responses with no network. 429 honours ``Retry-After``; 5xx and
    transport errors use exponential backoff. A 4xx other than 429 is fatal
    immediately. Raises ``CoinGeckoError`` when retries are exhausted.
    """
    opener = opener or urllib.request.urlopen
    last_err = None
    for attempt in range(max_retries):
        req = urllib.request.Request(
            url, headers={"User-Agent": DEFAULT_USER_AGENT, "Accept": "application/json"}
        )
        try:
            with opener(req, timeout=timeout) as resp:
                raw = resp.read().decode("utf-8")
            return json.loads(raw)
        except urllib.error.HTTPError as exc:
            if exc.code == 429:
                last_err = "http 429 (rate limited)"
                delay = _retry_after_seconds(exc)
                if delay is None:
                    delay = base_backoff * (2 ** attempt)
            elif 500 <= exc.code < 600:
                last_err = f"http {exc.code}"
                delay = base_backoff * (2 ** attempt)
            else:
                raise CoinGeckoError(f"CoinGecko HTTP {exc.code} for {url}") from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            last_err = f"transport ({getattr(exc, 'reason', exc)})"
            delay = base_backoff * (2 ** attempt)
        except json.JSONDecodeError as exc:
            last_err = f"non-json response ({exc})"
            delay = base_backoff * (2 ** attempt)
        if attempt < max_retries - 1:
            sleep(delay)
    raise CoinGeckoError(
        f"CoinGecko fetch failed after {max_retries} attempts ({last_err}): {url}"
    )


def normalize_market_row(raw: dict) -> dict:
    """Map one CoinGecko ``/coins/markets`` row to stable snake_case.

    Missing fields degrade to ``None`` (never ``KeyError``). ``symbol`` is upper-cased
    so downstream categorisation / dedup is case-stable.
    """
    g = raw.get
    sym = (g("symbol") or "").upper() or None
    row = {
        "id": g("id"),
        "symbol": sym,
        "name": g("name"),
        "market_cap_rank": g("market_cap_rank"),
        "current_price": g("current_price"),
        "market_cap": g("market_cap"),
        "fully_diluted_valuation": g("fully_diluted_valuation"),
        "total_volume": g("total_volume"),
        "high_24h": g("high_24h"),
        "low_24h": g("low_24h"),
        "circulating_supply": g("circulating_supply"),
        "total_supply": g("total_supply"),
        "max_supply": g("max_supply"),
        "ath": g("ath"),
        "ath_change_percentage": g("ath_change_percentage"),
        "ath_date": g("ath_date"),
        "last_updated": g("last_updated"),
    }
    for win, key in _PCT_KEYS.items():
        row[key] = raw.get(f"price_change_percentage_{win}_in_currency")
    # The plain 24h field is always present even without the windowed request.
    if row["price_change_pct_24h"] is None:
        row["price_change_pct_24h"] = raw.get("price_change_percentage_24h")
    return row


def fetch_markets(
    vs_currency: str = "usd",
    per_page: int = 100,
    page: int = 1,
    *,
    base_url: str = COINGECKO_BASE,
    opener=None,
    sleep=time.sleep,
    max_retries: int = 4,
    timeout: float = 30.0,
) -> list[dict]:
    """Fetch the top ``per_page`` coins by market cap, normalised. Raises
    ``CoinGeckoError`` only when retries are exhausted (caller decides fallback)."""
    params = {
        "vs_currency": vs_currency,
        "order": "market_cap_desc",
        "per_page": per_page,
        "page": page,
        "sparkline": "false",
        "price_change_percentage": PRICE_CHANGE_WINDOWS,
        "locale": "en",
    }
    url = f"{base_url}{MARKETS_PATH}?{urllib.parse.urlencode(params)}"
    data = _request_json(
        url, opener=opener, sleep=sleep, max_retries=max_retries, timeout=timeout
    )
    if not isinstance(data, list):
        raise CoinGeckoError(
            f"unexpected CoinGecko payload (expected list, got {type(data).__name__})"
        )
    return [normalize_market_row(row) for row in data if isinstance(row, dict)]
