#!/usr/bin/env bash
# scripts/tmux-write-loop.sh
# Multi-agent write-loop scaffold for $hark (tmux variant of zellij/layouts/write-loop.kdl).
#
# Spawns a 3-pane tmux session: Orchestrator | Writer (Aider in an isolated worktree) |
# Risk Officer (RAG + cross-review). Agents are READ-ONLY on philosophy/ except via
# _proposals/; never write raw/; recommendations only (AGENTS.md / CLAUDE.md).
#
# PREREQUISITES (some verified-MISSING as of 2026-06-13 -- install before this is functional):
#   - tmux            sudo apt install tmux
#   - aider           pipx install aider-chat                 [Writer pane]   (MISSING)
#   - ollama serving + a coder model:                          [local Writer/Reviewer]
#       ollama serve &  ;  ollama pull qwen2.5-coder:32b      (model MISSING; ollama not serving)
#   - grok            already installed                        [Risk Officer cloud leg] (OK)
#
# The Risk Officer CLOUD leg (Grok + RAG) works today via scripts/cross-review.ps1 from the
# Windows terminal. This tmux scaffold wires the local Writer loop once the above are present.
# Run:  bash scripts/tmux-write-loop.sh   [optional: path-to-existing-worktree]

set -u
SESSION="shark-write-loop"
REPO_WSL="$(cd "$(dirname "$0")/.." && pwd)"
WORKTREE="${1:-}"   # optional: existing git worktree for the Writer pane

if ! command -v tmux >/dev/null 2>&1; then
  echo "tmux not installed. Install: sudo apt install tmux"
  echo "(Or use the Zellij layout once zellij is installed: zellij --layout zellij/layouts/write-loop.kdl)"
  exit 1
fi

# Isolated worktree so the Writer mutates a branch, never the main checkout.
if [ -z "$WORKTREE" ]; then
  WORKTREE="${REPO_WSL}/../shark-write-$(date +%Y%m%d-%H%M)"
  BRANCH="write-loop/$(date +%Y%m%d-%H%M)"
  echo "[write-loop] creating worktree $WORKTREE on $BRANCH"
  git -C "$REPO_WSL" worktree add "$WORKTREE" -b "$BRANCH" \
    || { echo "worktree create failed; Writer will use main repo"; WORKTREE="$REPO_WSL"; }
fi

tmux kill-session -t "$SESSION" 2>/dev/null

# Pane 0 -- Orchestrator
tmux new-session -d -s "$SESSION" -n loop -c "$REPO_WSL"
tmux send-keys -t "$SESSION":0.0 \
  "clear; echo '=== ORCHESTRATOR (you / Claude) ==='; echo 'First: read AGENTS.md + CLAUDE.md.'; echo 'Drive tasks; pull reports from outputs/cross-review/.'" C-m

# Pane 1 -- Writer (Aider in the isolated worktree)
tmux split-window -h -t "$SESSION":0 -c "$WORKTREE"
tmux send-keys -t "$SESSION":0.1 \
  "clear; echo '=== WRITER (Aider @ $WORKTREE) ==='; echo 'Needs aider + ollama. Run:'; echo '  aider --model ollama/qwen2.5-coder:32b'; echo 'Commit small; Risk Officer reviews each diff.'" C-m

# Pane 2 -- Risk Officer (RAG + cross-review)
tmux split-window -v -t "$SESSION":0.1 -c "$REPO_WSL"
tmux send-keys -t "$SESSION":0.2 \
  "clear; echo '=== RISK OFFICER (RAG + cross-review) ==='; echo 'RAG leg (WSL):  python3 scripts/rag_retriever.py --query \"...\" --k 6'; echo 'Grok leg (Win): powershell.exe -File scripts/cross-review.ps1 <diff> -UseRag -Reviewer grok'; echo 'Gate: nothing merges to main without this review (AGENTS.md S3).'" C-m

tmux select-layout -t "$SESSION":0 tiled
tmux select-pane -t "$SESSION":0.0
tmux attach -t "$SESSION"
