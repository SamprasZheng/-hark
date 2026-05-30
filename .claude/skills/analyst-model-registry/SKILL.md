---
name: analyst-model-registry
description: Maintain and audit the registry of analyst models internalised into $hark philosophy/concepts/. Read-only — reports a table, link graph, dedup candidates, and orphan concepts; never modifies files. Use when the user asks to inventory analyst models, audit cross-links, find duplicates, or sanity-check the philosophy layer. Trigger phrases include "what analyst models do we have", "show registry", "audit cross-links", "check for dedup", "我們有幾個分析師模型", "盤點分析師", "philosophy audit", "concept graph", "find orphans".
---

# Analyst Model Registry

A read-only auditor for the `philosophy/` layer. Never writes. Produces tables and diagnostic reports to chat so the user can decide what to do.

## What this skill reports

### 1. Registry table

For every file under `philosophy/concepts/` tagged `analyst-model`:

| Slug | Title | Analyst / Source | States | First added | Last modified |
|---|---|---|---|---|---|

Columns are extracted from frontmatter:
- `Slug` — filename without `.md`
- `Title` — frontmatter `title:`
- `Analyst / Source` — frontmatter `source:` (or "n/a" if absent — flag this as a quality issue)
- `States` — count of top-level `### State N —` headings (or "n/a" if not a state-machine model)
- `First added` — `git log --diff-filter=A --format=%ci -- <file>` (first add date)
- `Last modified` — file mtime

### 2. Link graph audit

For each `analyst-model`-tagged file, parse `[[wikilinks]]` and report:
- **Outbound links** — what each file cites
- **Inbound links** — which other files cite this one (grep across all of `philosophy/`)
- **Dangling links** — `[[targets]]` that don't resolve to an existing file
- **Orphans** — `analyst-model` files with zero inbound links (suggest where they should be cited)

### 3. Dedup candidates

Surface pairs of `analyst-model` files where:
- Tag overlap is high (≥ 3 shared tags), OR
- Title cosine similarity is high (heuristic: shared trigrams), OR
- They cite the same set of `[[../../sharks]]` principles

Report as:
```
Candidate duplicates (review needed — do not auto-merge):
- [[concepts/A]] vs [[concepts/B]] — shared tags: [...]; common cites: [...]
  Suggested action: review whether one should cite the other, OR add explicit "Contradicted by" flag to the older page per wiki/AGENTS.md convention.
```

### 4. Quality checklist per analyst-model page

For each file, score:
- [ ] Has `source:` frontmatter field
- [ ] Cites `[[../../sharks]]` (constitution awareness)
- [ ] Cites `[[../02-signal-taxonomy]]` (4D mapping)
- [ ] Cites `[[../05-decision-rubric]]` (output contract)
- [ ] Cites `[[../07-mode-switch]]` (frequency declaration)
- [ ] Cites `[[../08-risk-and-position]]` (risk layering)
- [ ] Has `## Analyst-Model Interface` section (5 contracts table)
- [ ] Has `## Anti-patterns` section
- [ ] Has `## See also` block

Files missing 3+ items are flagged for refactor. The reference implementation (`chip-flow-single-point-breakout.md`) MUST pass all 9.

## What to do based on user intent

### 1. Show me the registry

Run the full report (sections 1–4 above). Output to chat. No file changes.

### 2. Audit a single analyst model

`analyst-model-registry <slug>` — show only sections 2 + 4 for that one slug. Useful before editing a specific concept.

### 3. Find what's missing

After running the report, suggest concrete additions:
- Orphans → which other concept should cite them
- Missing checklist items per file
- Tags that appear in only one file (might indicate a singleton waiting for a sibling)

### 4. Propose index updates

After the report, scan `philosophy/index.md` for `analyst-model`-tagged files that are NOT in the index. Output a proposed diff to add them under the "Analyst Models" subsection. Do NOT auto-apply (per the index's own rule).

## Workflow (deterministic)

1. PowerShell `Get-ChildItem 'philosophy/concepts/*.md'` — list all concept files. (Glob may fail on paths containing `$`; PowerShell does not.)
2. For each file: Read frontmatter (first YAML block), extract `tags`, `title`, `source`.
3. Filter to files where `tags` contains `analyst-model`.
4. For each retained file: Grep `\[\[` to extract all wikilinks.
5. Build a forward-edge map: file → cited targets.
6. Build a reverse-edge map: cited target → citing files.
7. Resolve each target to a file path (handle `../` prefixes and bare slugs in `concepts/`).
8. Flag unresolved targets as dangling links.
9. Detect dedup candidates via tag-overlap + title-trigram heuristic.
10. Compute the quality checklist per file.
11. Render markdown tables + bullet lists to chat.

## Boundaries

- **Strict read-only.** Never invokes Edit, Write, NotebookEdit, Bash, or any tool that modifies state.
- Never proposes a deletion. The most aggressive action is "flag for human review".
- Never resolves a contradiction unilaterally — when two analyst models disagree, report both and let the human decide which is canonical.
- Index update proposals are emitted to chat as a diff, never applied directly.
- Does NOT cross-walk into `D:\DOT\yxz` — that's a separate repo with a different schema.

## Output format example

```
# Analyst Model Registry — $hark/philosophy/concepts/

## Registry (1 analyst model)
| Slug | Title | Source | States | First | Modified |
| --- | --- | --- | --- | --- | --- |
| chip-flow-single-point-breakout | Chip-Flow & Single-Point Breakout | External investment advisor — 2026-05-29 | 3 | 2026-05-29 | 2026-05-29 |

## Link graph
- Outbound: 14 wikilinks (10 to numbered philosophy/, 6 to sibling concepts/)
- Inbound: 0 — ORPHAN (suggested: add citation from `philosophy/10-strategies.md` Strategy A section)
- Dangling: 0

## Dedup candidates
None (only 1 analyst-model file currently).

## Quality checklist
- chip-flow-single-point-breakout.md: 9/9 ✓

## Proposed philosophy/index.md additions
After line 50 (end of "Behavioural" subsection), add:

  +Analyst Models (externally sourced, internalised into the framework):
  +- [[concepts/chip-flow-single-point-breakout]] — 籌碼水流 + 單點突破 三狀態 FSM (投顧老師)

Run: human edits the file. Per `philosophy/index.md:97`, agents propose, humans apply.
```
