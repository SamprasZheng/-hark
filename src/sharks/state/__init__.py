"""Point-in-time state layer.

The read/write counterpart to ``philosophy/09-point-in-time.md`` for the
compiled wiki state pages (``wiki/01_macro_state.md`` and friends). The Compiler
overwrites those pages in place; this package captures an immutable dated copy
at each compile (:mod:`sharks.state.snapshot`) and resolves "state as of date D"
without lookahead (:mod:`sharks.state.resolve`). Zero-dependency, stdlib only.
"""

from sharks.state.resolve import ResolvedState, StateUnavailable, resolve_state
from sharks.state.snapshot import (
    LIVE_PAGES,
    snapshot_all_live_pages,
    snapshot_page,
)

__all__ = [
    "ResolvedState",
    "StateUnavailable",
    "resolve_state",
    "LIVE_PAGES",
    "snapshot_all_live_pages",
    "snapshot_page",
]
