"""Finnhub news + earnings + fundamentals client.

Phase 1 stub: all methods raise NotImplementedError. Phase 2 implementation
wires finnhub-python with point-in-time discipline.

Notes for Phase 2 implementer:
- Finnhub free tier: 60 API calls / minute. Reasonable for our daily flow.
- News API returns articles with `datetime` field (publication time). This
  becomes the `source_first_visible_at` for the corresponding raw/macro/* file.
  See philosophy/09-point-in-time.md.
- Earnings calendar API is the canonical source for the [[../philosophy/06-exclusions]]
  earnings-window blackouts (no entries within ±1 day of own earnings, etc.).
- Fundamentals (Income Statement, Balance Sheet, Cash Flow) are available for
  US tickers. They are reported AT FILING TIME — the as_of_timestamp must be
  the SEC EDGAR filing receipt time, not the API call time.
- The `general_news` and `company_news` endpoints are the primary feeds for
  the Compiler's macro and entity-page updates.
"""

from __future__ import annotations

from datetime import date, datetime


class FinnhubClient:
    """Finnhub.io news + earnings + fundamentals client.

    Wired in Phase 2. See docs/ROADMAP.md.
    """

    def __init__(self, api_key: str) -> None:
        """Initialise with API key from .env (FINNHUB_API_KEY)."""
        raise NotImplementedError("wired in Phase 2 (see docs/ROADMAP.md)")

    def get_company_news(self, ticker: str, since: datetime, until: datetime) -> list[dict]:
        """Return company-specific news articles in [since, until].

        Each dict has at minimum:
            - headline: str
            - datetime: ISO 8601 timestamp (becomes source_first_visible_at)
            - url: str (source URL for the article)
            - category: str
            - summary: str
            - source_grade: assigned by the Compiler post-fetch per CLAUDE.md §5

        Raises:
            NotImplementedError: Phase 2.
        """
        raise NotImplementedError("wired in Phase 2 (see docs/ROADMAP.md)")

    def get_general_news(self, category: str = "general") -> list[dict]:
        """Return general market news (Fed, macro, geopolitics).

        Categories: general, forex, crypto, merger.

        Raises:
            NotImplementedError: Phase 2.
        """
        raise NotImplementedError("wired in Phase 2 (see docs/ROADMAP.md)")

    def get_earnings_calendar(self, start: date, end: date, tickers: list[str] | None = None) -> list[dict]:
        """Return scheduled earnings announcements in [start, end].

        For [[../philosophy/06-exclusions]] earnings-window blackouts and
        [[../philosophy/08-risk-and-position]] earnings re-rate trigger.

        Raises:
            NotImplementedError: Phase 2.
        """
        raise NotImplementedError("wired in Phase 2 (see docs/ROADMAP.md)")

    def get_company_basic_financials(self, ticker: str) -> dict:
        """Return latest quarterly + annual basic financials.

        Returns a dict with keys: revenue, eps, gross_margin, operating_margin,
        each split by quarter / annual + as_of (the SEC filing receipt time).

        Raises:
            NotImplementedError: Phase 2.
        """
        raise NotImplementedError("wired in Phase 2 (see docs/ROADMAP.md)")
