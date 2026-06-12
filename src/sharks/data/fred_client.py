"""FRED / ALFRED CSV client — stdlib, dependency-free macro series data.

Pulls FRED observation series via the KEYLESS CSV endpoint
``https://fred.stlouisfed.org/graph/fredgraph.csv?id=<SERIES>`` — the same
endpoint ``regime/liquidity_signals.py`` already uses for M2SL (no API key,
unlike the JSON ``api.stlouisfed.org`` API which requires one). ``urllib`` only,
no ``requests`` / ``pandas``, so $hark stays dependency-free.

Point-in-time: each row carries ``as_of_timestamp`` (the observation date — what
the value is *for*) and ``source_first_visible_at`` (the vintage / first-print
date — when it became knowable), per ``data/__init__.py`` and
``philosophy/09-point-in-time.md``. For a backtest, pass ``vintage_date`` to
request the value AS FIRST PUBLISHED (ALFRED) rather than the latest revised
print; the client then stamps ``source_first_visible_at = vintage_date``. On the
live path (no vintage) ``source_first_visible_at`` is left ``None`` — the value
may be a later revision and the true first-print date is unknown; callers that
need PIT correctness MUST pass ``vintage_date``.

Same retry/backoff discipline as ``data/coingecko_client.py``: 429 honours
``Retry-After``; 5xx + transport back off exponentially; a non-429 4xx is fatal
immediately; exhaustion raises :class:`FREDError` so the caller can fall back and
flag the result stale. This client NEVER invents values — FRED's ``"."`` missing
marker maps to ``None``.
"""

from __future__ import annotations

import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Optional

FRED_CSV_BASE = "https://fred.stlouisfed.org/graph/fredgraph.csv"
DEFAULT_USER_AGENT = "sharks-liquidity/0.1 (+https://github.com/SamprasZheng)"


class FREDError(RuntimeError):
    """Raised when a FRED series cannot be fetched after exhausting retries."""


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


def _request_text(
    url: str,
    *,
    opener=None,
    max_retries: int = 4,
    timeout: float = 30.0,
    base_backoff: float = 1.5,
    sleep=time.sleep,
) -> str:
    """GET ``url`` → decoded text (CSV), retrying on 429 / 5xx / transport.

    ``opener`` is injectable (defaults to ``urllib.request.urlopen``) so tests
    can feed canned CSV with no network. Raises :class:`FREDError` on exhaustion.
    """
    opener = opener or urllib.request.urlopen
    last_err = None
    for attempt in range(max_retries):
        req = urllib.request.Request(
            url, headers={"User-Agent": DEFAULT_USER_AGENT, "Accept": "text/csv"}
        )
        try:
            with opener(req, timeout=timeout) as resp:
                return resp.read().decode("utf-8")
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
                raise FREDError(f"FRED HTTP {exc.code} for {url}") from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            last_err = f"transport ({getattr(exc, 'reason', exc)})"
            delay = base_backoff * (2 ** attempt)
        if attempt < max_retries - 1:
            sleep(delay)
    raise FREDError(
        f"FRED fetch failed after {max_retries} attempts ({last_err}): {url}"
    )


def parse_fred_csv(text: str) -> list[tuple[str, Optional[float]]]:
    """Parse fredgraph CSV → list of ``(date_str, value_or_None)``. Pure.

    FRED encodes a missing observation as ``"."`` → ``None`` (never invented).
    Header / non-data rows (first field not a 4-digit year) are skipped, so this
    tolerates either the ``observation_date,<ID>`` or legacy ``DATE,<ID>`` header.
    """
    rows: list[tuple[str, Optional[float]]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split(",")
        if len(parts) < 2:
            continue
        date_str, raw = parts[0].strip(), parts[1].strip()
        if not (len(date_str) >= 4 and date_str[:4].isdigit()):
            continue  # header or other non-data row
        if raw in (".", ""):
            rows.append((date_str, None))
            continue
        try:
            rows.append((date_str, float(raw)))
        except ValueError:
            rows.append((date_str, None))
    return rows


def fetch_series(
    series_id: str,
    *,
    start: Optional[str] = None,
    end: Optional[str] = None,
    vintage_date: Optional[str] = None,
    base_url: str = FRED_CSV_BASE,
    opener=None,
    sleep=time.sleep,
    max_retries: int = 4,
    timeout: float = 30.0,
) -> list[dict]:
    """Fetch one FRED series as a list of PIT-stamped row dicts.

    Each row: ``{series_id, date, value (float|None), as_of_timestamp,
    source_first_visible_at, vintage_date}``. ``start``/``end`` map to FRED's
    ``cosd``/``coed`` window params; ``vintage_date`` (ALFRED) requests the value
    as first published on that date. Raises :class:`FREDError` only on exhaustion.
    """
    params = {"id": series_id}
    if start:
        params["cosd"] = start
    if end:
        params["coed"] = end
    if vintage_date:
        params["vintage_date"] = vintage_date
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    text = _request_text(
        url, opener=opener, sleep=sleep, max_retries=max_retries, timeout=timeout
    )
    return [
        {
            "series_id": series_id,
            "date": date_str,
            "value": value,
            "as_of_timestamp": date_str,
            "source_first_visible_at": vintage_date,
            "vintage_date": vintage_date,
        }
        for date_str, value in parse_fred_csv(text)
    ]


def fetch_latest(series_id: str, **kw) -> Optional[dict]:
    """Most recent non-None observation row, or None if empty / all-missing."""
    for row in reversed(fetch_series(series_id, **kw)):
        if row["value"] is not None:
            return row
    return None
