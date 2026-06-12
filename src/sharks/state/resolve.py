"""Point-in-time reader for compiled wiki state snapshots.

The read counterpart to :mod:`sharks.state.snapshot` and
``philosophy/09-point-in-time.md``. ``resolve_state(page, as_of)`` returns the
most recent snapshot dated on or before ``as_of`` — and **never** a future one.
This is the file/date-level analogue of the bar-level ``s.loc[:as_of]`` /
``_slice_as_of`` guards already used in the scoring layer.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from sharks.state._frontmatter import parse_frontmatter
from sharks.state.snapshot import (
    DEFAULT_SNAPSHOTS_ROOT,
    DEFAULT_WIKI_ROOT,
    as_of_date,
)

_DATE_RE = re.compile(r"\A\d{4}-\d{2}-\d{2}\Z")


class StateUnavailable(LookupError):
    """No snapshot exists on or before the requested ``as_of`` (strict mode)."""


@dataclass(frozen=True)
class ResolvedState:
    page: str
    as_of_requested: str
    resolved_date: Optional[str]
    source_path: Optional[str]
    frontmatter: dict
    body: str
    degraded: bool = False


def _snapshot_dates(page_dir: Path) -> list[str]:
    """Sorted ``YYYY-MM-DD`` snapshot dates present for a page (empty if none)."""
    if not page_dir.is_dir():
        return []
    return sorted(p.stem for p in page_dir.glob("*.md") if _DATE_RE.match(p.stem))


def _read(path: Path) -> tuple[dict, str]:
    return parse_frontmatter(path.read_text(encoding="utf-8"))


def resolve_state(
    page: str,
    as_of: str,
    *,
    on_missing: str = "strict",
    snapshots_root: Path = DEFAULT_SNAPSHOTS_ROOT,
    wiki_root: Path = DEFAULT_WIKI_ROOT,
) -> ResolvedState:
    """Resolve compiled wiki ``page`` as it stood on ``as_of`` (``YYYY-MM-DD``).

    Selection (mirrors ``s.loc[:as_of]``): among snapshots dated ``<= as_of``,
    return the most recent. A snapshot dated *after* ``as_of`` is never returned.

    ``on_missing`` controls behaviour when no snapshot is ``<= as_of``:
      * ``"strict"`` (default, for backtests) — raise :class:`StateUnavailable`.
        Refuses to silently substitute the mutable live page.
      * ``"oldest"`` — return the oldest snapshot, ``degraded=True`` (best-effort
        exploratory history).
      * ``"live"`` — return the live ``wiki/<page>.md`` (for callers running
        *today*, e.g. ``daily_picks``); ``degraded`` is set only if the live
        page's own ``as_of`` is *after* the request (a lookahead).
    """
    as_of_d = str(as_of)[:10]
    page_dir = Path(snapshots_root) / page
    dates = _snapshot_dates(page_dir)

    eligible = [d for d in dates if d <= as_of_d]
    if eligible:
        chosen = max(eligible)
        src = page_dir / f"{chosen}.md"
        fm, body = _read(src)
        return ResolvedState(page, as_of_d, chosen, str(src), fm, body, False)

    if on_missing == "oldest" and dates:
        chosen = min(dates)
        src = page_dir / f"{chosen}.md"
        fm, body = _read(src)
        return ResolvedState(page, as_of_d, chosen, str(src), fm, body, True)

    if on_missing == "live":
        live = Path(wiki_root) / f"{page}.md"
        if live.exists():
            fm, body = _read(live)
            live_date = as_of_date(fm)
            degraded = bool(live_date and live_date > as_of_d)
            return ResolvedState(page, as_of_d, live_date, str(live), fm, body, degraded)

    raise StateUnavailable(
        f"no snapshot for page {page!r} on or before {as_of_d} "
        f"(available: {dates or 'none'}); on_missing={on_missing!r}"
    )
