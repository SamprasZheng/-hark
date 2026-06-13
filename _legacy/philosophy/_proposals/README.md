# philosophy/_proposals/

Compiler / Researcher / Risk Officer agents may write **DRAFT** philosophy pages here for human review. These are NOT yet committed to the philosophy layer — they are proposals.

## Workflow

1. Agent writes draft here with `status: proposal` in frontmatter
2. Agent logs the proposal in `wiki/log.md` with a `## [date] proposal | <title>` entry
3. Human reads, edits, approves
4. Human moves the file from `_proposals/` to its final philosophy location (`concepts/`, `entities/`, or root)
5. Human updates `status:` to remove the `proposal` flag and adjusts frontmatter

## Current proposals

- `multi-scale-cycles-concept.md` — proposed `philosophy/concepts/multi-scale-cycles.md`
- `election-cycle-year-2.md` — proposed `philosophy/concepts/election-cycle-year-2.md`
- `btc-halving-cycle.md` — proposed `philosophy/concepts/btc-halving-cycle.md`
- `sell-in-may-and-september-weak.md` — proposed `philosophy/concepts/seasonal-monthly.md`
- `sector-seasonality.md` — proposed `philosophy/concepts/sector-seasonality.md`
- `policy-shock-sub-cycle.md` — proposed `philosophy/concepts/policy-shock-sub-cycle.md` (from previous session)
- `leadership-saturation-sizing.md` — proposed addition to `philosophy/08-risk-and-position.md` (from previous session)

## Rules per CLAUDE.md §1

- Compiler proposes but does not commit
- Risk Officer may veto a proposal (writes `## Veto (as_of YYYY-MM-DD) reason: ...` section)
- A proposal that sits here > 30 days without acceptance is auto-archived to `_proposals/archive/`
