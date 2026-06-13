---
name: commit-scoped
description: Stage and commit ONLY the explicitly intended files — never blanket git add . — with a privacy/scope check first. Use when committing changes in $hark.
---

# /commit-scoped — scoped, safe commit

1. `git status` — show everything changed / untracked.
2. List the EXACT files this commit should include; stage ONLY those: `git add <path1> <path2> ...`. **NEVER `git add .` / `git add -A`** (a prior commit swept up 161 files).
3. **Privacy gate:** confirm no portfolio / KOL / personal-finance data is being committed to anything public; if any, stop and confirm with the user first.
4. `git diff --cached --stat` — verify the staged set matches intent (no surprise files).
5. Commit with a clear message. Do NOT push unless asked. Do NOT remind about `gh auth` (the user handles it).
