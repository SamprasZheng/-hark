"""Finviz screener client.

Phase 1 stub: all methods raise NotImplementedError. Phase 2 implementation
wraps the `finviz` library (mariostoev/finviz) with point-in-time discipline.

CRITICAL caveat for Phase 2 implementer:
- Finviz returns the CURRENT screener result — there is no native point-in-time
  API. The client must:
    1. Stamp the CSV with `as_of_timestamp = NYSE_prior_close_time` (typically
       16:00 ET on the most recent trading day)
    2. Save the CSV to `raw/market_data/finviz-<screen-name>-<YYYY-MM-DD>.csv`
    3. The Phase 4 backtest engine reads from this archive, NOT from a fresh
       Finviz pull, to ensure point-in-time integrity.
- Free tier Finviz limits screener results to the first page. The Elite tier
  (~$25/month) gives the full result set + CSV export.
- The library scrapes the HTML site; expect occasional breakage on Finviz UI
  updates. Phase 2 includes a daily smoke test that fails loud on parser break.

Phase 1 initial filter set (see philosophy/04-sector-and-finviz.md):
- 20/60 MA golden cross within last 3 trading days
- Distance from 52w high ≤ 10%
- Sector 5d net inflow top 3
- Bollinger upper-band touch with volume > 1.3x 20d avg
- Sales QoQ growth > 15% AND gross margin expanding
"""

from __future__ import annotations

from datetime import datetime


class FinvizClient:
    """Finviz.com screener client. PHASE 2 — see module docstring caveats.

    Wired in Phase 2. See docs/ROADMAP.md.
    """

    def __init__(self, elite_api_key: str | None = None) -> None:
        """Initialise; elite_api_key from .env (FINVIZ_ELITE_API_KEY). Optional for free tier."""
        raise NotImplementedError("wired in Phase 2 (see docs/ROADMAP.md)")

    def run_screen(self, filters: dict[str, str], as_of_label: str | None = None) -> tuple[list[dict], datetime]:
        """Execute a Finviz screen with the given filter dict.

        Args:
            filters: dict of Finviz filter param → value. Example:
                {"f_geo": "us", "f_sec": "Technology",
                 "f_sma20_pa": "Cross above SMA60",
                 "f_pe_high": "30"}
            as_of_label: optional label used for the saved CSV filename

        Returns:
            (rows, as_of_timestamp) where:
              - rows: list of dicts (ticker + screener column values)
              - as_of_timestamp: NYSE prior close, NOT API call time

        Raises:
            NotImplementedError: Phase 2.
        """
        raise NotImplementedError("wired in Phase 2 (see docs/ROADMAP.md)")

    def run_phase_1_filter_set(self) -> dict[str, tuple[list[dict], datetime]]:
        """Convenience: run all 5 Phase 1 initial filters in one call.

        Returns:
            Dict keyed by filter name with (rows, as_of_timestamp) tuples.

        Raises:
            NotImplementedError: Phase 2.
        """
        raise NotImplementedError("wired in Phase 2 (see docs/ROADMAP.md)")
