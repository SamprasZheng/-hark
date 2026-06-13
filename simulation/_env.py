"""
Trading Society -- minimal .env loader.

The repo's data clients read os.environ directly (no central dotenv loader), so
a bare subprocess (e.g. a simulation module run on its own) has no API keys.
Importing this module loads KEY=VALUE pairs from the repo-root .env into
os.environ (never overriding an already-set var, never raising). Keys are never
printed. .env is gitignored.
"""

from __future__ import annotations

import os
from pathlib import Path

_LOADED = False


def load_env(force: bool = False) -> int:
    """Load repo-root .env into os.environ. Returns count of vars set."""
    global _LOADED
    if _LOADED and not force:
        return 0
    root = Path(__file__).resolve().parents[1]
    env = root / ".env"
    n = 0
    if env.exists():
        try:
            for line in env.read_text(encoding="utf-8", errors="ignore").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k, v = k.strip(), v.strip().strip('"').strip("'")
                if v and (force or k not in os.environ):
                    os.environ[k] = v
                    n += 1
        except Exception:
            pass
    _LOADED = True
    return n


# Load on import so `import simulation._env` is enough.
load_env()
