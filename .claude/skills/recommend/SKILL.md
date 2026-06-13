---
name: recommend
description: Compile today's $hark stock/crypto recommendation from canonical repo sources (finviz/fom/rally/serenity + portfolio), verified — never web-first. Use when the user asks for today's picks / 推薦 / daily recommendation.
---

# /recommend — daily recommendation

Consult **$hark canonical sources first** (never web-first). The repo is the source of truth.

1. Read the freshest outputs: `outputs/finviz-scan-*.json` (`.buy_consider`), `outputs/fom-monthly-*.json` (`.ranked_full`), `outputs/rally-state-*.jsonl` (`.buy_consider`), `outputs/serenity-scout-*.json`, plus current `portfolio/` and `watchlist/`.
2. Apply the 10-signal contract (`philosophy/05-decision-rubric.md`): **2 long_new + 2 short_new + 6 position_followup**; emit `null` over padding; Risk Officer veto on caps/exclusions.
3. Cross-check candidates against the **existing portfolio** (avoid double-counting / over-concentration) and `philosophy/06-exclusions.md`.
4. Grade-D social/KOL signals (`raw/kol_signals/`, `scripts/grok-kol.ps1`) **inform only — never trigger or size a position** (CLAUDE.md §5).
5. Output picks + per-slot rationale. Write the machine JSON (`outputs/picks-*.json`) only if asked. **Recommend-only; never trade.**

This is private finance content — do not publish (privacy gate applies).
