"""PIT-snapshot validation for ``sharks wiki lint``.

Enforces the compile-first state-snapshot discipline promised in
``philosophy/09-point-in-time.md``:

  * ``error`` — a live compiled page (``status: live`` + ``author_role:
    compiler``) carries no ``as_of_timestamp``;
  * ``warn``  — a live page's current ``as_of`` has no matching snapshot (the
    latest compile was not captured; run ``sharks ingest --snapshot``);
  * ``warn``  — a live page's ``as_of`` is *behind* the newest snapshot, which
    means an edit forgot to bump ``as_of_timestamp`` (two distinct states would
    collide on one snapshot filename).

Returns a list of ``{"severity", "page", "message"}`` findings; the CLI exits
non-zero only on ``error`` findings, so warnings (e.g. a not-yet-seeded repo) do
not break the smoke command.
"""

from __future__ import annotations

from pathlib import Path

from sharks.state._frontmatter import parse_frontmatter
from sharks.state.resolve import _snapshot_dates
from sharks.state.snapshot import (
    DEFAULT_SNAPSHOTS_ROOT,
    DEFAULT_WIKI_ROOT,
    LIVE_PAGES,
    as_of_date,
    is_compiled_live,
)


def lint_state(
    *,
    wiki_root: Path = DEFAULT_WIKI_ROOT,
    snapshots_root: Path = DEFAULT_SNAPSHOTS_ROOT,
    pages: tuple[str, ...] = LIVE_PAGES,
) -> list[dict]:
    """Return state-snapshot findings (empty == clean)."""
    findings: list[dict] = []

    def add(sev: str, page: str, msg: str) -> None:
        findings.append({"severity": sev, "page": page, "message": msg})

    for stem in pages:
        page = Path(wiki_root) / f"{stem}.md"
        if not page.exists():
            continue  # page not present yet — not a state-discipline violation
        fm, _ = parse_frontmatter(page.read_text(encoding="utf-8"))
        if not is_compiled_live(fm):
            continue  # stub / non-compiled page — nothing to snapshot
        date = as_of_date(fm)
        if not date:
            add("error", stem, "live compiled page has no as_of_timestamp")
            continue
        dates = _snapshot_dates(snapshots_root / stem)
        if date not in dates:
            add(
                "warn",
                stem,
                f"live page as_of {date} not snapshotted "
                f"(run `sharks ingest --snapshot`); snapshots={dates or 'none'}",
            )
        if dates and date < max(dates):
            add(
                "warn",
                stem,
                f"live page as_of {date} is BEHIND newest snapshot {max(dates)} "
                f"— bump as_of_timestamp on edit (state-collision risk)",
            )
    return findings
