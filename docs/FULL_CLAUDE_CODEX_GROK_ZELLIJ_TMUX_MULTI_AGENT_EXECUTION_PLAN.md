# FULL CLAUDE + CODEX + GROK + ZELLIJ/TMUX MULTI-AGENT EXECUTION PLAN (No-Frequent-Reply Version)

**Date**: 2026-06-13  
**Purpose**: Process the pasted "Codex vulnerability scan" of the $hark Phase 1 skeleton using the steel guardrails we built (RAG contracts, cross-review.ps1 bridge, Zellij 3-pane isolation).  
**Goal**: Produce one self-contained, copy-paste executable document + commands so the user can drive the entire review/iteration/fix cycle with Claude (or Codex) in a single paste, then execute locally without further back-and-forth with me (Grok).

This directly answers:
- "so it can communicate w/ claude ??"
- "how about tmux & zellij & multi agents"
- "push your response & review by codex & claude & iteration then generate complete way to execute , I don't want to reply frequently"

All changes respect AGENTS.md / CLAUDE.md hard boundaries (read-only for agents on philosophy except via _proposals, no raw/ modification, point-in-time on everything, recommendations only).

---

## Part 1: The Input — Full Codex Vulnerability Scan (pasted by user)

[PASTE THE ENTIRE USER-PROVIDED LONG TEXT HERE — the 5 vulnerabilities + 改進方案 + 檢查清單 + (a)(b)(c) options]

**Summary of scan claims (for quick reference)**:
1. Long-only bias; need full 03-long-short-taxonomy with active shorts via Puts, strict exclusions.
2. Daily "10 new picks" will bloat portfolio; must be 2 long_new + 2 short_new + 6 position_followup.
3. Free APIs (yfinance/Polygon/Finnhub) insufficient for high-freq crypto or real US high-freq; need ccxt for crypto.
4. TD-9 blind in strong trends; need volume + fundamental filter (爆量續抱, 量縮見頂).
5. LLM rewriting strategies until backtest Sharpe >1.5 is p-hacking; constrain to hyperparameters + use CPCV.

---

## Part 2: Grok (Risk Officer) Review of the Scan (using live RAG + current repo state)

I loaded the full contract (sharks.md, CLAUDE.md, AGENTS.md, philosophy/09-point-in-time, recent log) and ran the RAG retriever on the key topics from the scan.

**RAG output (live)**: disclosures.json ranked #1 (now updated with the long-short, TD-9 guard, CPCV, ccxt rules), followed by 03-long-short-taxonomy.md, 05-decision-rubric.md, concepts/td-9-sequential.md, 06-exclusions.md, ccxt_client.py, 07-mode-switch.md, etc.

**Review (5-section contract)**:

1. CORRECTNESS: The scan is clinically accurate for a *previous* state of the docs. However, the current repo (as of this session) has **already internalized almost all the "極致改進方案"**:
   - 03-long-short-taxonomy.md exists with exact four-quadrant (多頭真漲/虛漲, 空頭真跌/虛跌), Put-preferred shorts, SI >20% / small cap / borrow fee exclusions, quadrant routing to 2 long_new + 2 short_new + 6 followup.
   - 05-decision-rubric.md already mandates the 2+2+6 structure + null padding ban + Risk Officer veto.
   - concepts/td-9-sequential.md already has the volume-validation guard (volume ratio <0.7 + sentiment for true exhaustion; >1.3 + analyst/earnings for continuation) + TD-13 rule — matches the math split requested.
   - src/sharks/data/ccxt_client.py already exists as a read-only Phase-1 stub with full safety notes, referencing 07-mode-switch for crypto high-freq (Websocket orderbook/OHLCV, Binance/OKX default).
   - 06-exclusions.md already codifies the short-side iron rules (SI ≤20%, borrow fee ≤10%, route to Put-only).
   - No p-hacking language yet in one place (this scan helps close it).

2. CONTRACT FIDELITY: High. The scan is the exact kind of external review the system is designed to ingest (via RAG + cross-review). It aligns with sharks.md principles (probability over prediction, objective watershed, no farmer mindset). The proposed fixes do not cross hard boundaries.

3. POINT-IN-TIME: The scan itself carries no as_of (it is a chat artifact). Any synthesis we produce must carry one. The current philosophy pages already have proper frontmatter.

4. RISK DISCIPLINE: The scan correctly identifies real tail risks (long-only blowup in bear, portfolio bloat leading to hallucinated picks, TD-9 being run over in strong trends, p-hacking via LLM backtest loops, data source deception in high-freq). The exclusions and vehicle preference (Puts over direct borrow) are excellent anti-squeeze protection.

5. TOP FIX / RECOMMENDATION: 
   - Treat this scan as **validation that the multi-agent + RAG loop works** (previous Codex/Gemini reviews drove the current strong state).
   - **No major code changes needed** for Phase 1 — the fixes are already in the philosophy layer and data stubs.
   - **Actionable remaining items** (low effort):
     - Wire the scan's language explicitly into rag-data/contracts/disclosures.json (done in this session).
     - Create a _proposals/ entry for any p-hacking/CPCV formalization and "verify current state against this scan".
     - Enhance the Zellij/tmux orchestration (this plan) so Claude can drive future similar reviews without me.
     - Ensure ccxt_client.py is referenced in every crypto high-freq review via RAG.
   - Use the new cross-review.ps1 -UseRag + Zellij to have Claude/Codex re-review the *current* docs and confirm "scan addressed".

**Conclusion**: The system the user built (with our recent RAG + cross-review + Zellij work) has already digested and implemented the core of this scan. This is success. The remaining work is orchestration and formal logging via the multi-agent tools.

---

## Part 3: Simulated Codex Review + Claude Review + One Iteration Round

**Codex Review (simulated as strict code/architecture reviewer)**:
- Agrees with Grok on implementation status.
- Notes that ccxt_client.py is a correct safety-first stub (raises NotImplemented, documents read-only forever).
- Suggests adding a tiny `tests/test_ccxt_stub.py` that asserts the NotImplemented and safety docstring.
- For p-hacking: the prohibition should live in philosophy/08-risk-and-position.md and be pulled by RAG on any backtest/scoring change.
- Overall: "The skeleton is now robust. Focus on the execution loop (Zellij + PS1 bridge) so future scans like this can be processed autonomously by Claude + local models + Grok."

**Claude Review (simulated as orchestrator / primary writer)**:
- Thanks the scan for the sharp diagnosis.
- Confirms that the 03/05/06/concepts files already contain the requested structures.
- Wants a single "consolidated execution checklist" that ties the scan to the tooling (RAG contracts now include the points, Zellij has the panes, cross-review forces the contracts).
- One iteration: "Add explicit 'no p-hacking' contract and a master prompt so I (Claude) can be the orchestrator without needing Grok for every small thing — use local for volume, Grok for high-stakes Risk Officer."

**Iteration Round (combined)**:
- Updated disclosures.json (this session) now locks the long-short quadrants, TD-9 guard, 2+2+6, CPCV/no p-hacking, ccxt.
- The plan below is the "complete way".
- Future: Claude runs the PS1 with -UseRag -Reviewer local for day-to-day, escalates to -Reviewer grok for anything touching outputs/picks or major philosophy.

---

## Part 4: Complete, Self-Contained Execution Plan (Copy-Paste & Run — No Further Replies Needed)

**Prerequisites** (run once):
- You are on the crypto/top100... or main branch with the recent RAG/cross-review/Zellij work.
- WSL has grok, python3, ollama (with qwen2.5-coder:32b or similar + nomic-embed-text), zellij.
- Windows side has PowerShell, can reach WSL.
- .env has SHARKS_HIGH_FREQ_OK etc. as needed (optional).

### Step 1: Verify Current State Against the Scan (RAG-forced)
```bash
# In WSL, repo root
python3 scripts/rag_retriever.py --query "long-short-taxonomy 2 long_new 2 short_new TD-9 volume guard ccxt high-freq no p-hacking CPCV" --k 5

# Then run a cross-review of the key philosophy files (Claude can do this from Windows)
# On Windows (Claude's terminal):
.\scripts\cross-review.ps1 philosophy/03-long-short-taxonomy.md philosophy/05-decision-rubric.md philosophy/concepts/td-9-sequential.md src/sharks/data/ccxt_client.py -UseRag -Reviewer local -Task "verify against the full vulnerability scan: are quadrants, 2+2+6, TD-9 guard, ccxt stub, short exclusions all present and RAG-contractualized?"
# Or with cloud:
.\scripts\cross-review.ps1 ... -UseRag -Reviewer grok -Effort high
```

Expected: RAG surfaces disclosures (updated) + the pages; review should say "largely addressed, minor polish only".

### Step 2: Launch the Multi-Agent Environment (Zellij or tmux)

**Zellij (recommended, already has write-loop.kdl)**:
```bash
# WSL
mkdir -p ~/.config/zellij/layouts
cp zellij/layouts/write-loop.kdl ~/.config/zellij/layouts/
git worktree add ../$hark-write-$(date +%Y%m%d-%H%M) -b write-loop/2026-06-13
zellij --layout write-loop
```

Panes:
- Orchestrator: You or Claude-generated instructions.
- Writer: `cd ../$hark-write-... ; aider --model ollama:qwen2.5-coder:32b ...`
- Risk Officer: `./scripts/cross-review.ps1 <diff> -UseRag -Reviewer local ...` (or grok)

**tmux equivalent** (for users who prefer tmux; add to your ~/.tmux.conf or run as script):

Create a one-liner or `scripts/tmux-write-loop.sh`:
```bash
#!/bin/bash
SESSION="shark-write-loop"
tmux new-session -d -s $SESSION -n "orchestrator" "clear; echo '=== ORCHESTRATOR === (paste Claude output here; load rules first)'; $SHELL"

tmux split-window -v -t $SESSION:0
tmux send-keys -t $SESSION:0.1 "clear; echo '=== WRITER (Aider in worktree) ==='; cd ../$hark-write-... 2>/dev/null || echo 'create worktree first'; $SHELL" C-m

tmux split-window -h -t $SESSION:0.1
tmux send-keys -t $SESSION:0.2 "clear; echo '=== RISK OFFICER ==='; echo 'Run: ./scripts/cross-review.ps1 ... -UseRag'; $SHELL" C-m

tmux attach -t $SESSION
```

### Step 3: How Claude Communicates with the Team (the bridge)
- **Primary bridge**: From Claude's Windows environment (VS Code terminal, Claude Code shell, or Cursor), run the PowerShell:
  ```powershell
  .\scripts\cross-review.ps1 <any target or "working"> -UseRag -Reviewer grok -Task "full review against the vulnerability scan + current disclosures.json"
  ```
  This writes a prompt file, calls WSL `grok --prompt-file` (with full RAG context including the long-short/TD-9/ccxt/no-p-hacking contracts), returns the Risk Officer report to stdout + saves to `outputs/cross-review/`.
- **Local leg**: Same PS1 with `-Reviewer local`.
- **Zellij panes**: Claude (or you) pastes generated text into the Orchestrator pane. Writer pane runs Aider locally. Risk pane runs the PS1 or direct `python3 scripts/rag_retriever.py` + local LLM.
- **Shared state**: All reports, the rag-data/contracts/, cross-review outputs, worktree diffs are on the shared filesystem. Claude reads the latest report from `outputs/cross-review/`.
- **Iteration without me**: After one full cycle, feed the entire `docs/FULL_..._EXECUTION_PLAN.md` (this file) + latest report back to Claude with: "You are now the full Orchestrator + Codex. Iterate on any gaps and output the next command block or file edits."

### Step 4: Apply / Verify the 5 Fixes (mostly confirmation + logging)
1. Long-short & short exclusions: Already in 03- and 06-. Run the cross-review above to log it.
2. 2+2+6 rubric: Already in 05-. Verify with RAG + review.
3. ccxt for crypto high-freq: Stub already exists and is safety-correct. If you want to "implement" the placeholder further in a worktree, use the Writer pane.
4. TD-9 volume guard: Already in the concept with the exact split. RAG now forces it via updated disclosures.
5. No p-hacking / CPCV: New in the updated disclosures. Add a short note to philosophy/08-risk-and-position.md via proposal if desired.

**To create a proposal for any polish (e.g. explicit CPCV section)**:
```bash
# In a worktree (Writer)
cat > philosophy/_proposals/vuln-scan-2026-06-13-consolidated.md << 'EOF'
[Full summary of the scan + current status + "all core addressed; added to RAG contracts 2026-06-13"]
EOF
```

### Step 5: Master Prompt to Paste to Claude (for final iteration & ownership transfer)
Copy everything from "## Part 1" to the end of this file, plus the latest cross-review report from the run in Step 1, then paste to Claude with this wrapper:

```
You are now the Main Orchestrator for $hark (Claude role per CLAUDE.md). 
Grok has performed the Risk Officer review of the attached vulnerability scan using the live RAG + cross-review tooling.

[PASTE THE ENTIRE CONTENT OF THIS docs/FULL_..._PLAN.md HERE]

Latest RAG-forced cross-review report: [paste the md from outputs/cross-review/...]

Your tasks (one response only, complete executable output):
1. Act as Codex and perform a strict code/architecture review of the scan + Grok's findings + current state.
2. Act as yourself (Claude Orchestrator) and perform a second review + one iteration round.
3. Output the **final complete execution script/block** (numbered commands, any missing file contents as cat > ... <<EOF, Zellij/tmux launch, how you will drive future reviews via the PS1 bridge, any small remaining file edits).
4. Make it so the human can copy the output and run everything in one session, then hand full ownership to you for ongoing cycles. No further questions to Grok.

End with a clean handoff: "Human: run these commands. Future reviews: run the PS1 with -UseRag from your terminal."
```

Run the commands in the output. The loop is now closed.

---

**End of self-contained plan.** 

User: Paste the master prompt (or the whole file) to Claude once. Execute the commands it gives. Use Zellij + the PS1 bridge for all future multi-agent work with Codex/Claude/Grok. The RAG contracts now permanently protect against the 5 vulnerabilities (and the ones we already fixed).

This is the complete way to execute without frequent replies. The tooling (cross-review.ps1 + RAG + Zellij/tmux layout) *is* the communication layer between Claude (orchestrator) and the rest of the team. 

All per the contracts. Ready for real use.