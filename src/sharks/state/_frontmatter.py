"""Zero-dependency frontmatter reader for the state layer.

Splits a ``---``-fenced YAML frontmatter block from the markdown body and parses
the small YAML subset the compiled wiki state pages use (top-level scalars,
indented ``- list`` items such as ``source_paths``, and one level of indented
``key: value`` maps). Mirrors the ethos of ``analysts/persona.py``'s
``_parse_frontmatter`` and ``decision/_yamlite.py`` — no pyyaml, since the core
project stays dependency-free. Unlike the persona reader, this one also returns
the body (the state resolver hands the body back to callers).
"""

from __future__ import annotations

import re
from typing import Any

_FM_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?", re.DOTALL)


def _coerce(v: str) -> Any:
    v = v.strip()
    if v.startswith("[") and v.endswith("]"):
        inner = v[1:-1].strip()
        return (
            [x.strip().strip("\"'") for x in inner.split(",") if x.strip()]
            if inner
            else []
        )
    if v.lower() in ("true", "false"):
        return v.lower() == "true"
    try:
        if re.fullmatch(r"-?\d+", v):
            return int(v)
        return float(v)
    except ValueError:
        return v.strip("\"'")


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Return ``(frontmatter_dict, body)``.

    If the text has no leading ``---`` frontmatter block, returns ``({}, text)``.
    An ISO timestamp like ``2026-05-29T00:00:00-04:00`` is kept as a string
    (``float()`` rejects it), which is what the date helpers expect.
    """
    m = _FM_RE.match(text)
    if not m:
        return {}, text
    body = text[m.end():]
    out: dict = {}
    cur_key: str | None = None
    for raw in m.group(1).splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indented = raw[0] in (" ", "\t")
        line = raw.strip()
        if indented and cur_key is not None:
            if line.startswith("- "):
                if not isinstance(out.get(cur_key), list):
                    out[cur_key] = []
                out[cur_key].append(line[2:].strip().strip("\"'"))
            elif ":" in line:
                k, _, v = line.partition(":")
                if not isinstance(out.get(cur_key), dict):
                    out[cur_key] = {}
                out[cur_key][k.strip()] = _coerce(v.strip())
            continue
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key, val = key.strip(), val.strip()
        if val == "":
            cur_key = key
            out.setdefault(key, None)
        else:
            cur_key = None
            out[key] = _coerce(val)
    return out, body
