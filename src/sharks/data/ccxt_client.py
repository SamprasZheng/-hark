"""ccxt crypto exchange client (READ-ONLY public market data).

Phase 1 stub: all methods raise NotImplementedError. Phase 2 implementation
wires ccxt for weekend crypto high-freq mode per philosophy/07-mode-switch.md.

CRITICAL SAFETY constraint:
- This client is READ-ONLY. It NEVER:
    * Accepts private keys
    * Authenticates with an API key for trading endpoints
    * Calls order-placement endpoints
- It uses ONLY the public market data endpoints (ticker / OHLCV / orderbook).
- Phase 1, 2, 3, 4, 5, and 6 all hold to this. Order execution is a HUMAN
  action; the system emits recommendations only.

Notes for Phase 2 implementer:
- ccxt covers 100+ exchanges. Default to Binance for breadth, OKX for redundancy.
- Public endpoints have no rate limit issues at single-user request volumes.
- Crypto markets are 24/7 — the as_of_timestamp is just the bar close time
  (UTC). No market-hours conversion needed.
- Order-book depth analysis (for [[../philosophy/10-strategies]] Strategy C)
  uses `fetch_order_book(symbol)`. The structure is public and free.
- On-chain large-transfer cluster detection (also Strategy C) requires
  additional data sources beyond ccxt (Glassnode, Etherscan APIs); deferred
  to Phase 6.

Crypto high-freq is enabled when:
- `SHARKS_HIGH_FREQ_CRYPTO_OK=1` in .env
- BTC 60m realised volatility annualised is in [40%, 100%]
- The user is the actor (no automated triggering)

See philosophy/07-mode-switch.md for the full criteria.
"""

from __future__ import annotations

from datetime import datetime


class CcxtClient:
    """ccxt crypto public-data client. SAFETY: read-only, no keys, no orders.

    Wired in Phase 2. See docs/ROADMAP.md.
    """

    def __init__(self, exchange: str = "binance") -> None:
        """Initialise an exchange instance for public market data.

        Args:
            exchange: ccxt exchange ID; default 'binance'. Others: 'okx', 'kraken', 'coinbase'.

        Raises:
            NotImplementedError: Phase 2.
        """
        raise NotImplementedError("wired in Phase 2 (see docs/ROADMAP.md)")

    def get_ohlcv(self, symbol: str, timeframe: str = "1m", limit: int = 500) -> list:
        """Public OHLCV bars.

        Args:
            symbol: e.g. 'BTC/USDT'
            timeframe: ccxt format, e.g. '1m', '5m', '15m', '1h', '4h', '1d'
            limit: number of bars to return (max varies by exchange, typically 1000)

        Returns:
            List of OHLCVBar with bar_close as as_of_timestamp.

        Raises:
            NotImplementedError: Phase 2.
        """
        raise NotImplementedError("wired in Phase 2 (see docs/ROADMAP.md)")

    def get_orderbook(self, symbol: str, depth: int = 20) -> dict:
        """Public orderbook snapshot.

        Args:
            symbol: e.g. 'BTC/USDT'
            depth: number of levels each side

        Returns:
            {'bids': [[price, amount], ...], 'asks': [...], 'timestamp': int_ms,
             'as_of_timestamp': datetime}

        Used by [[../philosophy/10-strategies]] Strategy C for large-order
        clustering detection.

        Raises:
            NotImplementedError: Phase 2.
        """
        raise NotImplementedError("wired in Phase 2 (see docs/ROADMAP.md)")

    def get_24h_ticker(self, symbol: str) -> dict:
        """24h ticker summary.

        Returns the standard ccxt ticker dict. Used for VIX-equivalent crypto
        volatility check in philosophy/07-mode-switch.md weekend special case.

        Raises:
            NotImplementedError: Phase 2.
        """
        raise NotImplementedError("wired in Phase 2 (see docs/ROADMAP.md)")
