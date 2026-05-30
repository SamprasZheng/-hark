"""Polygon.io US equity data client.

Phase 1 stub: all methods raise NotImplementedError. Phase 2 implementation
wires polygon-api-client with point-in-time discipline.

CRITICAL caveats for Phase 2 implementer:

- The Polygon free tier does NOT support same-day intraday data. Intraday data
  is delayed 1-2 days on free tier. Therefore this client is appropriate for
  HISTORICAL backtest data only — do NOT use in the live low-freq daily flow
  during US market hours (yfinance EOD covers that case).
- For high-freq US equity intraday (Phase 6), this client requires a paid
  Polygon tier (Stocks Starter ~$29/mo gives delayed-15min real-time; Stocks
  Developer ~$199/mo gives true real-time). The free tier is for backtest only.
- Polygon historical data goes back ~5 years on free tier; ~25 years on paid.
- Rate limit on free tier: 5 requests / minute. Throttle aggressively.
- Polygon timestamps are in nanoseconds UTC; convert to ET datetime for
  internal use.

For weekend crypto high-freq, use ccxt_client.py, NOT this. Polygon does not
have a free crypto tier worth the effort.

The client must stamp `as_of_timestamp` at bar close, NOT at API call time.
See philosophy/09-point-in-time.md.
"""

from __future__ import annotations

from datetime import date


class PolygonClient:
    """Polygon.io US equity OHLCV client. PHASE 2 — HISTORICAL BACKTEST USE ONLY ON FREE TIER.

    Wired in Phase 2. See docs/ROADMAP.md.
    """

    def __init__(self, api_key: str) -> None:
        """Initialise with API key from .env (POLYGON_API_KEY).

        Args:
            api_key: Polygon.io API key

        Raises:
            NotImplementedError: Phase 2.
        """
        raise NotImplementedError("wired in Phase 2 (see docs/ROADMAP.md)")

    def get_eod_historical(self, ticker: str, start: date, end: date) -> list:
        """Bulk historical EOD bars. Free-tier appropriate; suitable for backtest.

        Returns:
            List of OHLCVBar matching yfinance_client.OHLCVBar schema.

        Raises:
            NotImplementedError: Phase 2.
        """
        raise NotImplementedError("wired in Phase 2 (see docs/ROADMAP.md)")

    def get_intraday(self, ticker: str, interval: str = "5m") -> list:
        """Intraday bars.

        WARNING: Free tier returns delayed 1-2 day data. For live use, paid tier
        is required. See module docstring caveats.

        Raises:
            NotImplementedError: Phase 2.
        """
        raise NotImplementedError("wired in Phase 2 (see docs/ROADMAP.md)")
