"""Wikilink + analyst-model schema validator for the philosophy/ layer.

This is the lint stub referenced in ``philosophy/index.md`` line 98:
> "Lint check (Phase 2): every [[link]] here must resolve to an existing file.
>  CI lint job stub lives in tests/test_philosophy_links.py."

What it enforces:

1.  Every ``[[wikilink]]`` in any ``philosophy/*.md`` (and the constitution
    ``sharks.md``) resolves to an existing markdown file.
2.  Every concept page tagged ``analyst-model`` follows the five-contract
    schema documented in ``philosophy/concepts/chip-flow-single-point-breakout.md``
    (the reference implementation):
      - has a ``source:`` frontmatter field
      - cites the constitution ``[[../../sharks]]``
      - cites the signal taxonomy ``[[../02-signal-taxonomy]]``
      - contains the canonical Module / Integration / Implementation hooks /
        Analyst-Model Interface / See also sections.
3.  ``philosophy/index.md`` cites every existing concept file (per the
    index's own maintenance rule on line 96).

Failures here mean: either the philosophy layer is internally inconsistent,
or a new concept has been added without updating the index. Both are real
problems the human author needs to resolve manually — the tests do not
auto-fix anything.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
PHILOSOPHY_DIR = REPO_ROOT / "philosophy"
CONCEPTS_DIR = PHILOSOPHY_DIR / "concepts"
WIKI_DIR = REPO_ROOT / "wiki"

WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")
FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)

# Strip both fenced code blocks (```...```) and inline code (`...`) before
# scanning for wikilinks. Documentation pages legitimately mention
# ``[[link]]`` as a syntax example inside code spans — those are not real
# wikilinks and must not be linted.
FENCED_CODE_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")

# Sections an analyst-model concept page must contain (matched as substrings —
# order doesn't matter, but the heading text must appear verbatim).
ANALYST_MODEL_REQUIRED_SECTIONS: tuple[str, ...] = (
    "## Module ",                       # at least one Module header
    "## Integration into the Sharks framework",
    "## Implementation hooks",
    "## Analyst-Model Interface",
    "## See also",
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _all_philosophy_md() -> list[Path]:
    """Every markdown file in philosophy/ (recursive) plus the constitution."""
    files = sorted(PHILOSOPHY_DIR.rglob("*.md"))
    constitution = REPO_ROOT / "sharks.md"
    if constitution.exists():
        files.append(constitution)
    return files


def _all_concept_files() -> list[Path]:
    return sorted(CONCEPTS_DIR.glob("*.md")) if CONCEPTS_DIR.exists() else []


def _read_frontmatter(path: Path) -> dict[str, str]:
    """Lightweight top-level YAML reader. Values are kept as raw strings."""
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}
    out: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if not line or line.startswith((" ", "\t", "#", "-")):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        out[key.strip()] = value.strip()
    return out


def _has_tag(frontmatter: dict[str, str], tag: str) -> bool:
    raw = frontmatter.get("tags", "")
    # tags may appear as ``[a, b, c]`` or as ``a, b, c``. We just need substring
    # boundaries — split on commas/brackets and strip.
    tokens = re.split(r"[\[\],\s]+", raw)
    return tag in {t.strip().strip("\"'") for t in tokens if t.strip()}


def _resolve_wikilink(link: str, source_file: Path) -> Path | None:
    """Best-effort resolver matching Obsidian-relative-link semantics.

    Tries, in order:
      1. relative to the source file's parent directory,
      2. relative to philosophy/ root,
      3. as a bare slug inside the concepts/ dir,
      4. relative to the repo root.

    Returns the first existing path, or ``None`` if no candidate exists.
    """
    target = link.strip()
    if not target.endswith(".md"):
        target = target + ".md"

    candidates = (
        source_file.parent / target,        # relative to source
        PHILOSOPHY_DIR / target,            # philosophy/ root
        CONCEPTS_DIR / target,              # bare slug inside concepts/
        WIKI_DIR / target,                  # compiled-state wiki/ slug
        REPO_ROOT / target,                 # repo root (catches sharks.md)
    )
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def _strip_code(text: str) -> str:
    """Remove fenced + inline code spans so wikilinks-in-examples don't lint."""
    text = FENCED_CODE_RE.sub("", text)
    text = INLINE_CODE_RE.sub("", text)
    return text


def _analyst_model_files() -> list[Path]:
    return [p for p in _all_concept_files() if _has_tag(_read_frontmatter(p), "analyst-model")]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestWikilinksResolve:
    """Every [[wikilink]] in philosophy/ must point at an existing file."""

    @pytest.mark.parametrize(
        "md_file",
        _all_philosophy_md(),
        ids=lambda p: p.relative_to(REPO_ROOT).as_posix(),
    )
    def test_all_wikilinks_resolve(self, md_file: Path) -> None:
        text = _strip_code(md_file.read_text(encoding="utf-8"))
        unresolved: list[str] = []
        for raw_link in WIKILINK_RE.findall(text):
            link = raw_link.strip()
            if not link:
                continue
            if _resolve_wikilink(link, md_file) is None:
                unresolved.append(link)
        assert not unresolved, (
            f"{md_file.relative_to(REPO_ROOT)} has unresolved wikilinks: "
            f"{unresolved}"
        )


class TestAnalystModelSchema:
    """Concept pages tagged analyst-model must follow the 5-contract schema."""

    @pytest.mark.parametrize(
        "md_file", _analyst_model_files(), ids=lambda p: p.name
    )
    def test_required_sections_present(self, md_file: Path) -> None:
        text = md_file.read_text(encoding="utf-8")
        missing = [s for s in ANALYST_MODEL_REQUIRED_SECTIONS if s not in text]
        assert not missing, (
            f"{md_file.name} (analyst-model) missing required sections: "
            f"{missing}. See "
            f"philosophy/concepts/chip-flow-single-point-breakout.md "
            f"for the reference structure."
        )

    @pytest.mark.parametrize(
        "md_file", _analyst_model_files(), ids=lambda p: p.name
    )
    def test_source_frontmatter_present(self, md_file: Path) -> None:
        frontmatter = _read_frontmatter(md_file)
        assert "source" in frontmatter, (
            f"{md_file.name} has the analyst-model tag but no 'source:' "
            "field in frontmatter. Every internalised analyst must declare "
            "its origin."
        )

    @pytest.mark.parametrize(
        "md_file", _analyst_model_files(), ids=lambda p: p.name
    )
    def test_cites_constitution(self, md_file: Path) -> None:
        text = md_file.read_text(encoding="utf-8")
        assert "[[../../sharks]]" in text, (
            f"{md_file.name} (analyst-model) does not cite "
            "[[../../sharks]]. Every analyst model must declare its "
            "relationship with Andy's constitution (compatible / overlapping "
            "/ contradicting) — never silently bypass it."
        )

    @pytest.mark.parametrize(
        "md_file", _analyst_model_files(), ids=lambda p: p.name
    )
    def test_cites_signal_taxonomy(self, md_file: Path) -> None:
        text = md_file.read_text(encoding="utf-8")
        assert "[[../02-signal-taxonomy]]" in text, (
            f"{md_file.name} (analyst-model) does not cite "
            "[[../02-signal-taxonomy]]. Every analyst model must map its "
            "signals into the 4-dimension framework so the conflict-arbitration "
            "matrix can resolve cross-model disagreements."
        )


class TestIndexCoverage:
    """philosophy/index.md must cite every concept file.

    Per philosophy/index.md line 96:
    > "This file is the map, not the territory. When you add a page
    >  elsewhere in philosophy/, update this index."

    A failure here means the index is out of date. The fix is a human edit
    to index.md (per its line 97 rule that agents propose, humans edit).
    """

    def test_every_concept_appears_in_index(self) -> None:
        index_path = PHILOSOPHY_DIR / "index.md"
        if not index_path.exists():
            pytest.skip("philosophy/index.md not present")
        index = index_path.read_text(encoding="utf-8")
        missing = [
            p.stem
            for p in _all_concept_files()
            if f"[[concepts/{p.stem}]]" not in index
        ]
        assert not missing, (
            "philosophy/index.md is out of date — missing concepts: "
            f"{missing}. Add each under the appropriate subsection. "
            "For analyst-model concepts, the suggested subsection is "
            "'Analyst Models (externally sourced, internalised into the "
            "framework)' inserted after the 'Behavioural' subsection."
        )
