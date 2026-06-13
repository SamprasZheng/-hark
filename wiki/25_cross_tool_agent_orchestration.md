---
type: synthesis
tags: [agent-ops, grok, multi-agent, cross-review, mcp, subagents, worktree, tooling]
title: Cross-Tool Agent Orchestration — driving Grok as a headless cross-reviewer
as_of_timestamp: 2026-06-13T11:00:00+08:00
ingested_timestamp: 2026-06-13T11:00:00+08:00
author_role: compiler
confidence: 0.55
source_grade: D
source_paths:
  - wiki/inbox/2026-06-13-grok-agent-integration-conversation.md
---

# Cross-Tool Agent Orchestration

> **Compiler note (read first).** This page is an ingest of a single Grok conversation in which Grok describes *how to wire itself* into a Claude-orchestrated loop. That makes almost every claim below **grade D self-description (opinion / unverified)** — Grok asserting its own capabilities and recommending integration paths. The **verified subset** comes not from the conversation but from the operator's actual 2026-06-13 tests (recorded in the `grok-headless-cross-review` memory). Where the conversation contradicts the tests, **the tests win** and the contradiction is flagged. Treat the speculative rows as a research backlog, not as instructions. This is an ops/tooling page; it does not feed a backtest, but carries point-in-time frontmatter per [[../CLAUDE]] §2 / [[../philosophy/09-point-in-time]] anyway.

The goal under discussion: **Claude as orchestrator + Grok as a headless specialist** (Risk Officer / cross-reviewer), so a different model's read gates merges — the mandate already written into [[../AGENTS]] §3 ("a second model's read is worth more than a second pass by the author").

---

## §1. Verified — what actually works (2026-06-13)

Source: operator hands-on, NOT the Grok conversation.

- **The thin-pointer contract loads.** Grok, run in-repo, executes [[../AGENTS]] §0 on session start and loads `sharks.md` + `CLAUDE.md` + `philosophy/index.md`. The thin-pointer design (§0) is empirically working on a non-Claude tool.
- **Use `--prompt-file`, NOT inline `-p "..."`.** Passing the prompt inline through PowerShell→wsl→bash **truncates it to the first word** (Grok then reports "task underspecified"). A prompt file bypasses all CLI quoting. ⚠ **This directly contradicts the conversation**, which repeatedly recommends `grok -p "..."` (see §4).
- **Bridge:** Grok Build CLI lives in WSL (`~/.local/bin/grok`, user `polkasharks`); Claude runs on Windows. Drive it with `wsl -e bash -lc '...'`, escape the repo path as `/mnt/d/DOT/\$hark`, `cd` into the repo (a bare `/tmp` dir gives permission errors / empty output).
- **Disarm Grok's own discipline.** Grok auto-runs §0 and its caution makes it pause; tell it explicitly *do NOT ask for clarification / do NOT defer to a human* or the loop stalls.
- Keep the loop **read-only by default**; each round spends the operator's Grok credits. A WRITE loop needs worktree isolation + the Risk Officer gate. Full recipe in the `grok-headless-cross-review` memory + [[windows-env-quirks]].

---

## §2. Integration approaches — taxonomy with reality check

The conversation proposed five ways for Claude to call Grok. Reconciled:

| Approach | Conversation's claim | Reality check |
|---|---|---|
| **Shell call** `grok --prompt-file` | "simplest, ★★★★" (as `grok -p`) | **VERIFIED & current method** — but via `--prompt-file`, not inline `-p` |
| **Claude subagent** (`.claude/agents/grok-risk-officer.md`) for role isolation | "★★★★★, cleanest" | Plausible; **not yet built**. Sample uses outdated `claude-3-5-sonnet-20241022` — would need a current model id |
| **Custom MCP server** wrapping Grok | "future-proof, ★★★★" | **Sketch only.** The `server.py` example hard-codes a Linux path (`/home/workdir/...`) and inline `grok -p` (the truncation trap). Conceptually sound, not validated |
| **Agent SDK** programmatic control | "strongest loop, needs code" | Speculative; no work done |
| **`grok agent stdio` + ACP** (JSON-RPC) | "long-term best machine-to-machine" | **Unverified speculation.** Claude Code's support for driving a stdio agent this way is itself uncertain |

**Takeaway:** the verified, lowest-friction path (shell + `--prompt-file`) is good enough for the current cross-review loop. The subagent and MCP routes are real next steps only if/when the loop is run often enough to justify the build cost; ACP/SDK are research backlog.

---

## §3. Orchestration patterns

The conversation's pattern catalogue maps cleanly onto discipline already in [[../AGENTS]] §3 — no new rules, just vocabulary:

- **Hierarchical (orchestrator-worker)** — Claude plans/dispatches, specialists execute. Matches the role split in [[../CLAUDE]] §1.
- **Parallel worktree** — independent agents per git worktree (`research/` / `compile/` / `review/`), exactly the suggested layout in [[../AGENTS]] §3.
- **Peer-review / debate** — ≥2 independent reviews before merge. This *is* the "cross-review mandatory before merge" rule; using a different model (Grok) for the review is the intended instantiation.

All of these remain bound by the non-negotiables: point-in-time discipline survives parallelism, and no `outputs/picks-*` or `wiki/05_recommendations/*` merges to `main` without the Risk Officer gate.

### §3b. Worktree isolation for safe write-loops

The verified loop (§1) is **read-only**. To let Grok (or any agent) *write* without risking point-in-time corruption, the source's most useful contribution is a worktree-isolation recipe that is consistent with [[../AGENTS]] §3 — and worth promoting there if a write-loop is ever built:

- **Flow**: orchestrator opens a dated worktree (`git worktree add ../sharks-compile -b compile/grok-YYYYMMDD-HHMM`) → agent writes only inside it → a *different* model in a standing `../sharks-review` worktree runs `git diff main..compile/...` and reviews against §06/§08/§09 → Risk Officer signs off → human merges. Discard = delete the worktree.
- **Guardrails to consider**: never write directly on `main` or in the review worktree; cap files-per-loop (e.g. 15–30); auto-warn on worktrees unmerged >7 days; branch names must carry date + author.
- **Git hardlink caveat**: `git worktree add` hardlinks unmodified files (copy-on-write on edit), so ordinary read/write is safe — **but attribute changes (`chmod`/`xattr`) propagate across the shared inode until the link breaks**, and aggressive file-watchers can thrash links. For sensitive checkouts use `--no-checkout` + selective `git checkout`, or `git clone --no-hardlinks` for a fully clean (slower) isolate. (WSL↔Windows FS mixing makes hardlink behaviour more fragile — relevant on this setup.)

---

## §4. Flagged contradictions & cautions

- **Inline `-p` truncation** — the single most repeated recommendation in the source is the one method the operator found broken. Do not regress to it.
- **Stale model id** — every subagent/MCP snippet names `claude-3-5-sonnet-20241022`; use a current model id (the latest Claude family) if these are ever built.
- **Environment mismatch** — hard-coded Linux paths and macOS `brew install` assume a *nix host; this setup is Windows + WSL. Paths/commands need translation.
- **Terminal-multiplexer layouts** (Zellij `ai-parallel.kdl` / tmux `tmux-ai-team`) — generic boilerplate with placeholder paths and `claude-code`/`grok-build` command names that don't match this machine. Low durable value; recorded as an option, not adopted.

---

## §5. Cross-references & open items

- Practical runbook: `grok-headless-cross-review` memory · [[windows-env-quirks]] · [[act-now-dont-wait-for-morning-chain]]
- Contract this serves: [[../AGENTS]] §3 (multi-agent / worktree discipline), [[../CLAUDE]] §1 (roles)
- Raw source archived: [[inbox/2026-06-13-grok-agent-integration-conversation]]

**Open items** (research backlog, not commitments): (1) decide whether a persistent `grok-risk-officer` Claude subagent is worth building vs. the current ad-hoc `--prompt-file` loop; (2) if so, validate an MCP wrapper that *forces* `--prompt-file` + in-repo cwd; (3) confirm/deny that `grok agent stdio` ACP is actually drivable from Claude Code before investing in it.
