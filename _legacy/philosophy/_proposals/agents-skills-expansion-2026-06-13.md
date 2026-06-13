# Proposal: Agents & Skills Hooks Expansion for Perception/Brain/Risk Layers (per 2026-06-13 spec)

**Source**: User-provided detailed spec for expanding to address supply chain, macro, KOL, personal finance pain points, while fitting three-layer architecture and constitution (recommend-only, no trades).

**Changes proposed**:
- New Perception Hooks: macro_news_ingest.py, supply_chain_graph.py, kol_logic_scraper.py (in src/sharks/data/, using existing clients like fred, polygon, kol signals; output structured for agents).
- New Brain Agents: supply_chain_hunter_agent.py, social_kol_validator_agent.py, macro_regime_shield_agent.py (Pydantic models in src/sharks/decision/, output JSON for Risk_Officer handoff; integrate with existing conflict_resolver, long-short taxonomy, TD-9 guard).
- Personal_Finance_Guardrail_Hook: personal_finance_guardrail.py (hard Alpha sleeve ~0, tax limits, loss harvesting; explicit human balance_data input).
- Update disclosures.json with new contracts (perception hooks, agent outputs, guardrails as enforceable RAG knowledge).
- New Skills: .grok/skills/ for supply-chain-hunter, macro-regime-shield, kol-validator, personal-finance-guardrail (symmetric .claude/skills/ for Claude calls; enable mutual Claude/Grok review via risk-review skill).
- Discord integration: Extend bot with /supply_chain_hunter, /kol_validate, /macro_shield commands; wire new agents into /council for intense multi-persona debates (Grok risk review + local models + new agent personas); /grok_review now can invoke new agents.
- Workflow: New agents feed daily 10-signal (2 long_new genuine bull only, 2 short_new validated, 6 followup); Risk_Officer gate mandatory; Zellij 3-pane for isolation (Writer runs agent logic in worktree, Risk calls review skill).
- No changes to philosophy/ core without this proposal; no raw/ mods; point-in-time on any outputs.

**RAG/Contracts Impact**: disclosures.json updated to surface new guards (e.g., SupplyChain_Hunter only genuine_bull subs; KOL validator + chips/TD-9/exclusions; Macro HIGH forces defensive; Personal guardrail Alpha~0 + tax triggers).

**Verification**: After accept, Writer in worktree implements; Risk Officer (Grok via skill or PS1 -UseRag -Worktree) reviews with full RAG; human merges only on clean gate.

as_of_timestamp: 2026-06-13T20:00:00+08:00
author_role: researcher (tooling expansion per user spec)
source_paths: [user query spec 2026-06-13, existing decision/conflict_resolver.py, disclosures.json, discord/bot.py council, .grok/skills/risk-review]
confidence: 0.9

This enables "skills claude/grok 互相呼叫review" (via the new skills + risk-review bridge) and "大家都在discord 激烈辯論" (council with new agents + grok review outputs).
