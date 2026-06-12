"""Deterministic, offline tests for the point-in-time state layer.

These pin the anti-lookahead contract of ``resolve_state`` (the file/date-level
analogue of ``s.loc[:as_of]`` / ``_slice_as_of``), the snapshot writer's
immutability + as_of-not-wallclock discipline, and the ``wiki lint`` findings.
A synthetic ``wiki/_snapshots/`` tree is built under ``tmp_path``; no network.
"""

from __future__ import annotations

import pytest

from sharks.state import resolve as R
from sharks.state import snapshot as S
from sharks.state.lint import lint_state
from sharks.state.resolve import StateUnavailable, resolve_state

PAGE = "01_macro_state"


def _make_snapshot(root, page, date, marker):
    """Write a minimal live-compiled snapshot containing ``marker`` in its body."""
    d = root / page
    d.mkdir(parents=True, exist_ok=True)
    text = (
        "---\n"
        "type: synthesis\n"
        f"as_of_timestamp: {date}T00:00:00-04:00\n"
        "author_role: compiler\n"
        "status: live\n"
        "schema_version: 1\n"
        "---\n\n"
        f"# state {date}\n\n{marker}\n"
    )
    (d / f"{date}.md").write_text(text, encoding="utf-8")


def _make_live_page(wiki_root, page, date, marker="LIVE"):
    wiki_root.mkdir(parents=True, exist_ok=True)
    (wiki_root / f"{page}.md").write_text(
        "---\n"
        "type: synthesis\n"
        f"as_of_timestamp: {date}T00:00:00-04:00\n"
        "author_role: compiler\n"
        "status: live\n"
        "schema_version: 1\n"
        "---\n\n"
        f"# live {page}\n\n{marker}\n",
        encoding="utf-8",
    )


class TestResolveState:
    def test_resolves_snapshot_on_or_before_as_of(self, tmp_path):
        snaps = tmp_path / "_snapshots"
        _make_snapshot(snaps, PAGE, "2026-05-10", "M10")
        _make_snapshot(snaps, PAGE, "2026-05-20", "M20")
        rs = resolve_state(PAGE, "2026-05-25", snapshots_root=snaps)
        assert rs.resolved_date == "2026-05-20"
        assert "M20" in rs.body
        assert rs.degraded is False

    def test_exact_date_match_is_inclusive(self, tmp_path):
        snaps = tmp_path / "_snapshots"
        _make_snapshot(snaps, PAGE, "2026-05-20", "M20")
        rs = resolve_state(PAGE, "2026-05-20", snapshots_root=snaps)
        assert rs.resolved_date == "2026-05-20"

    def test_never_returns_future_snapshot(self, tmp_path):
        # The cardinal anti-lookahead assertion.
        snaps = tmp_path / "_snapshots"
        _make_snapshot(snaps, PAGE, "2026-05-10", "PAST")
        _make_snapshot(snaps, PAGE, "2026-06-01", "FUTURE")
        rs = resolve_state(PAGE, "2026-05-15", snapshots_root=snaps)
        assert rs.resolved_date == "2026-05-10"
        assert "FUTURE" not in rs.body
        assert "PAST" in rs.body

    def test_picks_latest_of_several_past_snapshots(self, tmp_path):
        snaps = tmp_path / "_snapshots"
        for d, m in [("2026-05-01", "A"), ("2026-05-10", "B"), ("2026-05-20", "C")]:
            _make_snapshot(snaps, PAGE, d, m)
        rs = resolve_state(PAGE, "2026-05-31", snapshots_root=snaps)
        assert rs.resolved_date == "2026-05-20"
        assert "C" in rs.body

    def test_missing_early_date_strict_raises(self, tmp_path):
        snaps = tmp_path / "_snapshots"
        _make_snapshot(snaps, PAGE, "2026-06-01", "ONLY")
        with pytest.raises(StateUnavailable):
            resolve_state(PAGE, "2026-05-01", snapshots_root=snaps)

    def test_missing_early_date_lenient_returns_oldest_degraded(self, tmp_path):
        snaps = tmp_path / "_snapshots"
        _make_snapshot(snaps, PAGE, "2026-06-01", "ONLY")
        rs = resolve_state(PAGE, "2026-05-01", on_missing="oldest", snapshots_root=snaps)
        assert rs.resolved_date == "2026-06-01"
        assert rs.degraded is True

    def test_live_fallback_not_degraded_when_live_not_future(self, tmp_path):
        snaps = tmp_path / "_snapshots"  # empty
        wiki = tmp_path / "wiki"
        _make_live_page(wiki, PAGE, "2026-05-01")
        rs = resolve_state(
            PAGE, "2026-05-15", on_missing="live", snapshots_root=snaps, wiki_root=wiki
        )
        assert rs.resolved_date == "2026-05-01"
        assert rs.degraded is False

    def test_live_fallback_degraded_when_live_is_future(self, tmp_path):
        snaps = tmp_path / "_snapshots"
        wiki = tmp_path / "wiki"
        _make_live_page(wiki, PAGE, "2026-06-10")  # newer than the request
        rs = resolve_state(
            PAGE, "2026-05-15", on_missing="live", snapshots_root=snaps, wiki_root=wiki
        )
        assert rs.degraded is True

    def test_provenance_fields(self, tmp_path):
        snaps = tmp_path / "_snapshots"
        _make_snapshot(snaps, PAGE, "2026-05-20", "M20")
        rs = resolve_state(PAGE, "2026-05-25", snapshots_root=snaps)
        assert rs.source_path.endswith("2026-05-20.md")
        assert rs.frontmatter["author_role"] == "compiler"
        assert rs.page == PAGE


class TestSnapshotWrite:
    def test_snapshot_uses_as_of_not_wallclock(self, tmp_path):
        wiki = tmp_path / "wiki"
        _make_live_page(wiki, PAGE, "2026-05-29")
        snaps = tmp_path / "_snapshots"
        out = S.snapshot_page(wiki / f"{PAGE}.md", snapshots_root=snaps)
        assert out is not None
        assert out.name == "2026-05-29.md"
        assert out.parent.name == PAGE

    def test_snapshot_is_immutable(self, tmp_path):
        wiki = tmp_path / "wiki"
        _make_live_page(wiki, PAGE, "2026-05-29", marker="FIRST")
        snaps = tmp_path / "_snapshots"
        first = S.snapshot_page(wiki / f"{PAGE}.md", snapshots_root=snaps)
        # Page edited in place WITHOUT bumping as_of — second capture must not clobber.
        _make_live_page(wiki, PAGE, "2026-05-29", marker="SECOND")
        again = S.snapshot_page(wiki / f"{PAGE}.md", snapshots_root=snaps)
        assert again == first
        assert "FIRST" in first.read_text(encoding="utf-8")
        assert "SECOND" not in first.read_text(encoding="utf-8")

    def test_non_live_page_not_snapshotted(self, tmp_path):
        wiki = tmp_path / "wiki"
        wiki.mkdir(parents=True)
        (wiki / f"{PAGE}.md").write_text(
            "---\ntype: synthesis\nstatus: draft\n---\n\n# stub\n", encoding="utf-8"
        )
        out = S.snapshot_page(wiki / f"{PAGE}.md", snapshots_root=tmp_path / "_snapshots")
        assert out is None

    def test_missing_page_returns_none(self, tmp_path):
        out = S.snapshot_page(tmp_path / "nope.md", snapshots_root=tmp_path / "_s")
        assert out is None

    def test_snapshot_all_live_pages(self, tmp_path):
        wiki = tmp_path / "wiki"
        for stem in S.LIVE_PAGES:
            _make_live_page(wiki, stem, "2026-05-29")
        snaps = tmp_path / "_snapshots"
        out = S.snapshot_all_live_pages(wiki_root=wiki, snapshots_root=snaps)
        assert len(out) == len(S.LIVE_PAGES)


class TestWikiLint:
    def test_flags_live_page_without_snapshot(self, tmp_path):
        wiki = tmp_path / "wiki"
        _make_live_page(wiki, PAGE, "2026-05-29")
        findings = lint_state(
            wiki_root=wiki, snapshots_root=tmp_path / "_snapshots", pages=(PAGE,)
        )
        assert any("not snapshotted" in f["message"] for f in findings)
        assert all(f["severity"] == "warn" for f in findings)

    def test_passes_when_snapshot_matches(self, tmp_path):
        wiki = tmp_path / "wiki"
        _make_live_page(wiki, PAGE, "2026-05-29")
        snaps = tmp_path / "_snapshots"
        _make_snapshot(snaps, PAGE, "2026-05-29", "OK")
        findings = lint_state(wiki_root=wiki, snapshots_root=snaps, pages=(PAGE,))
        assert findings == []

    def test_flags_as_of_behind_newest_snapshot(self, tmp_path):
        # Un-bumped edit: live as_of older than an existing newer snapshot.
        wiki = tmp_path / "wiki"
        _make_live_page(wiki, PAGE, "2026-05-29")
        snaps = tmp_path / "_snapshots"
        _make_snapshot(snaps, PAGE, "2026-05-29", "OK")
        _make_snapshot(snaps, PAGE, "2026-06-05", "NEWER")
        findings = lint_state(wiki_root=wiki, snapshots_root=snaps, pages=(PAGE,))
        assert any("BEHIND newest snapshot" in f["message"] for f in findings)

    def test_error_when_live_page_missing_as_of(self, tmp_path):
        wiki = tmp_path / "wiki"
        wiki.mkdir(parents=True)
        (wiki / f"{PAGE}.md").write_text(
            "---\ntype: synthesis\nauthor_role: compiler\nstatus: live\n---\n\n# x\n",
            encoding="utf-8",
        )
        findings = lint_state(
            wiki_root=wiki, snapshots_root=tmp_path / "_s", pages=(PAGE,)
        )
        assert any(f["severity"] == "error" for f in findings)


def test_snapshot_dates_ignores_non_date_files(tmp_path):
    d = tmp_path / PAGE
    d.mkdir(parents=True)
    (d / "2026-05-10.md").write_text("x", encoding="utf-8")
    (d / "README.md").write_text("x", encoding="utf-8")
    (d / "notes.txt").write_text("x", encoding="utf-8")
    assert R._snapshot_dates(d) == ["2026-05-10"]
