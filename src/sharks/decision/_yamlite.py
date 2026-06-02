"""Zero-dependency YAML reader for the decision layer.

pyyaml is NOT a project dependency (pyproject keeps the core dep-free), so this
module reads exactly the YAML subset that risk_config.yaml + weights.yaml use:

  - nested maps (any depth) by 2-space indentation
  - scalar values: int / float / bool / null / quoted-or-bare string
  - full-line ``#`` comments and blank lines (ignored)
  - inline trailing comments only when preceded by TWO spaces (``  #``)

It deliberately does NOT support lists, inline ``{}`` / ``[]`` flow collections,
anchors, or block scalars — the two config files avoid them. This mirrors the
zero-dep ethos of ``analysts/persona.py._parse_frontmatter``. Pure + unit-tested
in tests/test_policy_lint.py::TestYamlite.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

_INT_RE = re.compile(r"-?\d+")
_FLOAT_RE = re.compile(r"-?\d*\.\d+")


def _coerce(v: str) -> Any:
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in ("'", '"'):
        return v[1:-1]
    low = v.lower()
    if low in ("true", "false"):
        return low == "true"
    if low in ("null", "~", "none", ""):
        return None
    if _INT_RE.fullmatch(v):
        return int(v)
    if _FLOAT_RE.fullmatch(v):
        return float(v)
    return v


def loads(text: str) -> dict:
    """Parse the supported YAML subset into nested dicts."""
    root: dict = {}
    stack: list[tuple[int, dict]] = [(-1, root)]  # (key_indent, container)
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        line = raw.split("  #", 1)[0].rstrip() if "  #" in raw else raw.rstrip()
        if not line.strip() or ":" not in line:
            continue
        indent = len(line) - len(line.lstrip(" "))
        key, _, val = line.strip().partition(":")
        key = key.strip().strip("'\"")
        val = val.strip()
        # dedent: pop containers whose keys live at >= this indent
        while len(stack) > 1 and indent <= stack[-1][0]:
            stack.pop()
        container = stack[-1][1]
        if val == "":
            child: dict = {}
            container[key] = child
            stack.append((indent, child))
        else:
            container[key] = _coerce(val)
    return root


def load(path: Path | str) -> dict:
    return loads(Path(path).read_text(encoding="utf-8"))
