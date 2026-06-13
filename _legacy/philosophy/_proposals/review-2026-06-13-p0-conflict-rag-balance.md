# Proposal: Address P0/P1 from 2026-06-13 Cross-Review (Momentum Decoupling, Dynamic RAG Worktree, Hard Clipping, Tax Loop Separation)

**Source**: External cross-review provided 2026-06-13 (Huang Jingzhe momentum logic vs TD-9, RAG temporal pollution, balance clipping, tax black-box).

**Status**: Proposal for Compiler to integrate. Author: risk_officer (Grok-assisted).

## Changes

1. **Momentum Decoupling Lock** (P0 conflict between institutional breakout chasing and TD-9 counter-trend shorting):
   - Add `src/sharks/decision/conflict_resolver.py` (pure function).
   - When `institutional_buying_streak >=3 AND volume_breakthrough`, reject any SHORT proposal for that ticker until TD exhaustion confirmed.
   - Integrate into rally_signal, fom, or any signal generator before quadrant routing in 03-long-short-taxonomy.

2. **Dynamic RAG for Worktree** (P0 stale context):
   - Update `scripts/cross-review.ps1` to accept `-Worktree <path>` (or auto-detect from git).
   - When active worktree provided, rag_retriever.py and prompt construction scan from that root (so Writer changes in `../hark-write-xxx` are visible to Risk Officer).
   - Default remains main repo for read-only reviews.

3. **Hard Clipping on Real Available Power** (P1 financial defense):
   - In conflict_resolver (or position_sizing helper), `actual_bet = min(theoretical, available_buying_power * cap)`.
   - `balance_data` is **always passed explicitly** (from human export of broker statement or paper trading log). No live API call or key inside the code.
   - Update 08-risk-and-position.md to reference this as mandatory before any size recommendation.

4. **Tax/Financial Auditing as Separate Low-Freq Task** (P1):
   - Do not embed tax calc (證交稅, overseas 750萬, lending income) in daily signal loop.
   - Add to daily_routine or separate cron-like: weekly task that reads `outputs/realized_pnl.json` (or equivalent), checks thresholds, and writes priority adjustments to a `data/financial_priorities.json` that scorers read (low weight on high-tax events).
   - This keeps daily context clean and respects low vs high freq mode.

## RAG / Disclosures Impact
- These become new enforceable contracts in rag-data/contracts/disclosures.json (see update in this session).
- All future Risk Officer runs (local or Grok) via cross-review.ps1 -UseRag will surface them.

## Verification
- After implementation, run cross-review on the new files + affected philosophy with -UseRag.
- No real execution keys introduced (per CLAUDE §2).

**Next for human/Compiler**: Review proposal, accept or edit, then have Writer implement in worktree, Risk gate via the updated PS1.

as_of_timestamp: 2026-06-13T20:00:00+08:00
author_role: risk_officer
source_paths: [chat input 2026-06-13 review, current philosophy/03-long-short-taxonomy.md, concepts/td-9-sequential.md, 08-risk-and-position.md, src/sharks/data/ccxt_client.py (read-only precedent)]
confidence: 0.85
