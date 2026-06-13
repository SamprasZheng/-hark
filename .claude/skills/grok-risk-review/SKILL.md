# Grok Risk Review Skill (Claude calls Grok for Risk Officer review)

## Purpose
This skill lets Claude (as Orchestrator) request a high-quality, contract-enforced **Risk Officer cross-review** from Grok (headless in WSL).

It uses the established bridge:
- scripts/cross-review.ps1 (with -UseRag -Worktree support)
- RAG retriever pulling latest disclosures.json (Momentum Decoupling Lock, worktree-aware RAG, hard balance clipping, TD-9 guards, no p-hacking, etc.)
- Full AGENTS.md / CLAUDE.md / sharks.md loading

**Safety**: Always read-only. Grok never writes to the repo except reports in outputs/cross-review/. Use worktrees for any Writer changes.

## Invocation (from Claude Code / Cursor / you)
When you need a review (e.g., after Writer makes changes in a worktree, or to gate a proposal):

```
Use the grok-risk-review skill.

Target: <file path, "working", "staged", commit sha, or "main..HEAD">
Task: <focus, e.g. "檢查 conflict_resolver.py 是否正確實作 Momentum Decoupling Lock 並符合 disclosures.json">
Worktree: <optional, e.g. "../hark-write-20260613" if reviewing Writer's changes>
Effort: high (recommended for P0)
```

The skill will:
1. Translate to the correct PowerShell / WSL command.
2. Ensure RAG context (disclosures + PIT + long-short taxonomy) is injected.
3. Execute the review (Grok as Risk Officer).
4. Return the full 5-section report + RAG excerpts + recommendations for next action.

Example output format: The standard
1. CORRECTNESS
2. CONTRACT FIDELITY (cites specific rules from disclosures / 03 / 09-point-in-time)
3. POINT-IN-TIME
4. RISK DISCIPLINE
5. TOP FIX

Plus any inline `# [risk]` comments.

## How it calls Grok
Under the hood it runs (example):

```powershell
.\scripts\cross-review.ps1 <Target> -UseRag -Worktree "<worktree>" -Reviewer grok -Effort high -Task "<Task>"
```

This is the verified bridge (no inline -p truncation, prompt file, in-repo cwd so contracts load).

## Integration with multi-agent flow
- Orchestrator (you/Claude) plans.
- Writer works in dated worktree.
- You invoke this skill to get Grok's Risk Officer gate.
- If clean → merge. If issues → feed report back to Writer for fixes.
- Can be combined with Zellij 3-pane (Orchestrator pane pastes the skill call result).

## For intense Discord debates
Once the report is back, you can paste key excerpts into Discord #分析師議會 or use `/council` with the report as context so local personas + "grok-risk" can debate it.

See also:
- .grok/skills/risk-review/SKILL.md (the symmetric Grok-side skill)
- scripts/cross-review.ps1
- docs/QUICKSTART_USAGE_zh.md
- rag-data/contracts/disclosures.json (all P0 guards are auto-surfaced)
