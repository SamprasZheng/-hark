"""Point-in-time snapshots of compiled wiki state pages.

The Compiler overwrites ``wiki/01_macro_state.md`` (and ``02_mag7_bottleneck``,
``03_alpha_library``) in place. For a walk-forward backtest to read the
narrative state *as it stood on the trade date* — not today's overwritten copy —
we capture an immutable dated copy at each compile. This mirrors the existing
``watchlist/history/universe-YYYY-MM-DD.yaml`` precedent (philosophy/09) rather
than relying on git tags (reading a tag from Python needs subprocess/a git lib,
which is fragile and non-stdlib).

The snapshot date comes from the page's own ``as_of_timestamp`` frontmatter,
never wall-clock. Snapshots are immutable: an existing dated file is never
overwritten — the first capture for a given ``as_of`` wins. Zero-dependency.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from sharks.state._frontmatter import parse_frontmatter

# The compiled "live" state pages the Compiler maintains (CLAUDE.md S1.1).
LIVE_PAGES = ("01_macro_state", "02_mag7_bottleneck", "03_alpha_library")

DEFAULT_WIKI_ROOT = Path("wiki")
DEFAULT_SNAPSHOTS_ROOT = Path("wiki/_snapshots")


def as_of_date(frontmatter: dict) -> Optional[str]:
    """The ``YYYY-MM-DD`` date part of the page's ``as_of_timestamp`` (or None)."""
    ts = frontmatter.get("as_of_timestamp")
    if not ts:
        return None
    return str(ts)[:10]


def is_compiled_live(frontmatter: dict) -> bool:
    """True for a Compiler-authored live state page (the only kind we snapshot)."""
    return (
        str(frontmatter.get("status", "")).strip() == "live"
        and str(frontmatter.get("author_role", "")).strip() == "compiler"
    )


def snapshot_page(
    page_path: Path,
    *,
    snapshots_root: Path = DEFAULT_SNAPSHOTS_ROOT,
) -> Optional[Path]:
    """Write a byte-for-byte dated copy of a live compiled page.

    Returns the snapshot path (written or already-present), or ``None`` if the
    page is missing, lacks an ``as_of_timestamp``, or is not a compiled live
    page (``status: live`` + ``author_role: compiler``).
    """
    page_path = Path(page_path)
    if not page_path.exists():
        return None
    text = page_path.read_text(encoding="utf-8")
    fm, _ = parse_frontmatter(text)
    if not is_compiled_live(fm):
        return None
    date = as_of_date(fm)
    if not date:
        return None
    dest_dir = Path(snapshots_root) / page_path.stem
    dest = dest_dir / f"{date}.md"
    if dest.exists():
        return dest  # immutable: keep the first capture for this as_of
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest.write_text(text, encoding="utf-8")
    return dest


def snapshot_all_live_pages(
    *,
    wiki_root: Path = DEFAULT_WIKI_ROOT,
    snapshots_root: Path = DEFAULT_SNAPSHOTS_ROOT,
    pages: tuple[str, ...] = LIVE_PAGES,
) -> list[Path]:
    """Snapshot each known live compiled page. Returns the captured paths."""
    out: list[Path] = []
    for stem in pages:
        snap = snapshot_page(
            Path(wiki_root) / f"{stem}.md", snapshots_root=snapshots_root
        )
        if snap is not None:
            out.append(snap)
    return out
