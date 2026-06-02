"""Data client stubs for Sharks.

Phase 1: every client raises NotImplementedError. Their docstrings define the
expected interface, point-in-time obligations, and rate-limit warnings.
Phase 2+ wires real APIs per docs/ROADMAP.md.

Each client is responsible for stamping `as_of_timestamp` and
`source_first_visible_at` on the data it returns, per
philosophy/09-point-in-time.md.
"""
