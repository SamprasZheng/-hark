"""yfinance EOD US equity data client.

Phase 1 stub: all methods raise NotImplementedError. Phase 2 implementation wraps
the yfinance library with point-in-time discipline.

Notes for Phase 2 implementer:
- yfinance is free and key-less but rate-limited; throttle to ≤ 1 request / sec
  per ticker to avoid rate-limit-induced 429s.
- yfinance "intraday" data is delayed 15 minutes; not suitable for high-freq
  mode (see philosophy/07-mode-switch.md). Use ccxt for crypto high-freq;
  defer US equity intraday to a paid Polygon / Alpaca tier in Phase 6.
- yfinance data is "current" — the client must stamp `as_of_timestamp` at
  the BAR CLOSE time, not at the time of the API call (per
  philosophy/09-point-in-time.md).
- For backtest historical pulls, the client should batch by year and cache
  to `raw/market_data/yfinance-<ticker>-<year>.parquet`.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime


@dataclass
class OHLCVBar:
    """A single OHLCV bar.

    Attributes:
        ticker: the underlying ticker symbol (uppercase)
        bar_close: the bar's close timestamp (timezone-aware; ET for US equities)
        open, high, low, close: prices
        volume: integer share volume
        as_of_timestamp: alias for bar_close; explicit for point-in-time discipline
    """
    ticker: str
    bar_close: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int

    @property
    def as_of_timestamp(self) -> datetime:
        return self.bar_close


class YFinanceClient:
    """Free, no-key client for US equity OHLCV via yfinance.

    Wired in Phase 2. See docs/ROADMAP.md.
    """

    def get_eod(self, ticker: str, start: date, end: date) -> list[OHLCVBar]:
        """Return daily OHLCV bars for [start, end].

        Returns:
            List of OHLCVBar in chronological order. Empty list if no data.

        Raises:
            NotImplementedError: Phase 2.
        """
        raise NotImplementedError("wired in Phase 2 (see docs/ROADMAP.md)")

    def get_intraday(self, ticker: str, interval: str = "15m") -> list[OHLCVBar]:
        """Return intraday bars (15 min default).

        WARNING: yfinance intraday is delayed 15 minutes. This client is NOT
        appropriate for high-freq US equity intraday decisions. The Phase 3
        mode-switch logic uses this only as a fallback for low-priority polls.

        Raises:
            NotImplementedError: Phase 2.
        """
        raise NotImplementedError("wired in Phase 2 (see docs/ROADMAP.md)")

    def get_actions(self, ticker: str) -> dict:
        """Return dividends + splits history.

        Required for correct historical bar adjustment in backtest.

        Raises:
            NotImplementedError: Phase 2.
        """
        raise NotImplementedError("wired in Phase 2 (see docs/ROADMAP.md)")
