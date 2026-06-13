# Zellij Write-Loop Layout for $hark

This deploys **B** (3-Pane isolation write-loop) after the RAG guardrail (A) was wired into cross-review.

## Layout
- `layouts/write-loop.kdl`: 3 logical panes in one tab:
  - `orchestrator` (top, ~28%): Claude / main coordinator. Loads rules, plans, dispatches, consumes Risk Officer reports.
  - `writer` (bottom-left): Aider + local LLM (ollama). **MUST** operate inside a dedicated git worktree only.
  - `risk-officer` (bottom-right): Pre-loaded with the exact `cross-review.ps1 -UseRag` commands (local or grok). Uses the new RAG to force `rag-data/contracts/disclosures.json` (tail +500% winsor + TD-9 sell hard-disable) + all point-in-time / worktree rules.

## Quick Start (WSL / Linux with Zellij + Ollama)

```bash
# 1. Install / copy the layout (once)
mkdir -p ~/.config/zellij/layouts
cp zellij/layouts/write-loop.kdl ~/.config/zellij/layouts/

# 2. From the main $hark repo, create a fresh isolated worktree for the writer
git worktree add ../$hark-write-$(date +%Y%m%d-%H%M) -b write-loop/2026-06-13

# 3. Launch the layout
zellij --layout write-loop
# or
zellij --layout ~/.config/zellij/layouts/write-loop.kdl
```

## Flow (per AGENTS.md §3 + wiki/25 §3b)
1. **Orchestrator** pane: `cat sharks.md CLAUDE.md AGENTS.md philosophy/09-point-in-time.md`
2. Tell the Writer pane the task + the worktree path you just created.
3. **Writer** cd's into the worktree, runs Aider with local model, makes small commits tagged `[writer]`.
4. When ready, Orchestrator (or directly from Risk pane) runs:
   ```bash
   ./scripts/cross-review.ps1 <the-diff-or-files> -UseRag -Reviewer local -Task "對照 disclosures.json ..."
   # or -Reviewer grok -Effort high for the cloud leg
   ```
5. Risk Officer report appears in `outputs/cross-review/`.
6. Human decides merge or request rewrite. Never merge without clean gate.

## Guardrails baked in
- The layout comments + pre-filled commands explicitly reference the RAG retriever and disclosures.json.
- Writer is reminded "NEVER EDIT ON MAIN".
- Risk Officer command always includes `-UseRag` so the overfitting contracts (tail winsorization, TD-9 sell hard-disable) are surfaced on every review.

## Cleanup
```bash
git worktree remove ../$hark-write-...
git branch -D write-loop/2026-06-13
```

## tmux Alternative (for users who prefer tmux over Zellij)
Create `scripts/tmux-write-loop.sh` (or run the commands manually):

```bash
#!/bin/bash
# scripts/tmux-write-loop.sh
SESSION="shark-multi-agent"
REPO_ROOT="/mnt/d/DOT/\$hark"   # adjust for your mount

tmux new-session -d -s $SESSION -n "orchestrator" \
  "clear; printf '=== ORCHESTRATOR (Claude drive) ===\nLoad rules first. Paste tasks here.\nUse PS1 bridge for Grok Risk reviews.\n'; cd $REPO_ROOT; exec \$SHELL"

tmux split-window -v -t $SESSION:0
tmux send-keys -t $SESSION:0.1 \
  "clear; printf '=== WRITER (Aider + local in worktree) ===\ncd to your worktree first!\nExample: aider --model ollama:qwen2.5-coder:32b\n'; exec \$SHELL" C-m

tmux split-window -h -t $SESSION:0.1
tmux send-keys -t $SESSION:0.2 \
  "clear; printf '=== RISK OFFICER ===\n./scripts/cross-review.ps1 ... -UseRag -Reviewer local\n(or grok)\nRAG will force disclosures (long-short, TD-9 guard, no p-hacking, ccxt).\n'; cd $REPO_ROOT; exec \$SHELL" C-m

tmux select-pane -t $SESSION:0.0
tmux attach -t $SESSION
```

Run: `bash scripts/tmux-write-loop.sh`

Same flow and communication model as Zellij. The PS1 bridge remains the primary way Claude (Windows) summons Grok as Risk Officer with full RAG context.

---

This + the RAG-upgraded cross-review.ps1 + disclosures.json completes the "本地 RAG + 雙軌 + 唯讀審查閘" steel guardrail for safe automated write-loops.

See the master plan: `docs/FULL_CLAUDE_CODEX_GROK_ZELLIJ_TMUX_MULTI_AGENT_EXECUTION_PLAN.md` (the single artifact you can paste to Claude for one-shot iteration + execution ownership transfer).

See also prior handoffs in outputs/cross-review/.