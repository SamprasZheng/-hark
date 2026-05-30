"""Sharks CLI entry point.

Phase 1: argparse skeleton. All subcommands print stub messages and exit 0.
Phase 2+ wires real implementations per docs/ROADMAP.md.

Usage:
    sharks pick --mode {low,high,auto} [--dry-run]
    sharks ingest --source <path>
    sharks wiki lint
"""

from __future__ import annotations

import argparse
import sys
from typing import Sequence


def _cmd_pick(args: argparse.Namespace) -> int:
    print(
        f"[stub] sharks pick called with mode={args.mode}, dry_run={args.dry_run}. "
        f"Phase 3 will implement signal aggregation, the four-dimension scorers, "
        f"the conflict arbitration matrix, and the daily 10-signal output. "
        f"See docs/ROADMAP.md (Phase 3)."
    )
    return 0


def _cmd_ingest(args: argparse.Namespace) -> int:
    print(
        f"[stub] sharks ingest called with source={args.source!r}. "
        f"Phase 2 will implement the Compile-first runtime that reads raw/ and "
        f"updates wiki/ pages with as_of_timestamp discipline. "
        f"See docs/ROADMAP.md (Phase 2)."
    )
    return 0


def _cmd_wiki_lint(args: argparse.Namespace) -> int:
    print(
        f"[stub] sharks wiki lint called. "
        f"Phase 2 will implement frontmatter validation, [[link]] resolution, "
        f"as_of_timestamp checks, and log.md format verification. "
        f"See wiki/README.md and philosophy/09-point-in-time.md."
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sharks",
        description=(
            "Sharks trading system. "
            "Phase 1: scaffold only. See docs/ROADMAP.md."
        ),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # `sharks pick` — produce the daily 10-signal output
    p_pick = subparsers.add_parser(
        "pick",
        help="produce the daily 10-signal recommendation output (Phase 3 stub)",
    )
    p_pick.add_argument(
        "--mode",
        choices=["low", "high", "auto"],
        default="auto",
        help="frequency mode; see philosophy/07-mode-switch.md",
    )
    p_pick.add_argument(
        "--dry-run",
        action="store_true",
        help="evaluate signals but do not write outputs/ or wiki/05_recommendations/",
    )
    p_pick.set_defaults(func=_cmd_pick)

    # `sharks ingest` — Compile-first runtime entry
    p_ingest = subparsers.add_parser(
        "ingest",
        help="compile a raw/ source into wiki/ pages (Phase 2 stub)",
    )
    p_ingest.add_argument(
        "--source",
        required=True,
        help="path to the raw/ source file to compile",
    )
    p_ingest.set_defaults(func=_cmd_ingest)

    # `sharks wiki` — wiki maintenance commands
    p_wiki = subparsers.add_parser("wiki", help="wiki maintenance commands")
    wiki_subparsers = p_wiki.add_subparsers(dest="wiki_command", required=True)

    p_wiki_lint = wiki_subparsers.add_parser(
        "lint",
        help="validate wiki frontmatter, links, and point-in-time discipline (Phase 2 stub)",
    )
    p_wiki_lint.set_defaults(func=_cmd_wiki_lint)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
