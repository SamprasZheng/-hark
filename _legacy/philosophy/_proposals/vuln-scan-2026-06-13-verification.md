---
type: proposal
tags: [vulnerability-scan, verification, long-short, td-9, ccxt, p-hacking, cpcv, risk-officer]
as_of_timestamp: 2026-06-13T18:12:00+08:00
author_role: risk_officer
source_paths:
  - philosophy/03-long-short-taxonomy.md
  - philosophy/05-decision-rubric.md
  - philosophy/06-exclusions.md
  - philosophy/concepts/td-9-sequential.md
  - src/sharks/data/ccxt_client.py
  - rag-data/contracts/disclosures.json
  - outputs/cross-review/cross-review-2026-06-13-181032.md
confidence: 0.85
---

# Proposal — verification of the Codex "5-vulnerability scan" against current repo

**Status: draft for human ratification.** A Codex review previously flagged 5 vulnerabilities
in the Phase-1 skeleton. This entry records a verification of whether they are addressed in the
*current* repo, run two ways: (a) direct file inspection by the orchestrator (Claude), and
(b) an independent Grok Risk-Officer RAG cross-review
([report](../../outputs/cross-review/cross-review-2026-06-13-181032.md)). Both agree.

## The 5 scan points and verified status

| # | Scan point | Status | Evidence |
|---|---|---|---|
| 1 | Long-only bias → need full long-short taxonomy, Put-preferred shorts, strict short exclusions | **ADDRESSED** | `03-long-short-taxonomy.md:16-19` (4 quadrants 多頭真漲/虛漲, 空頭真跌/虛跌), `:25-35` (Mag7-Put-first vehicle order, SI>20% / borrow_fee>10% / mktcap<$1B forbidden direct borrow), `:51-54` (routing); `06-exclusions.md:42-47` (repeats short-side gate + route-to-Put-only) |
| 2 | Daily "10 new picks" bloat → 2 long_new + 2 short_new + 6 position_followup | **ADDRESSED** | `05-decision-rubric.md:18-20` (exact slot table), `:24` ("**Padding is forbidden**" + Risk Officer rejects <0.50), `:95`; live `wiki/05_recommendations/2026-06-12.md` shows all long_new/short_new `null` with no padding |
| 3 | Free APIs insufficient for crypto high-freq → ccxt | **ADDRESSED** | `src/sharks/data/ccxt_client.py` — READ-ONLY module, every method `raise NotImplementedError("wired in Phase 2")`, references `07-mode-switch` + `SHARKS_HIGH_FREQ_CRYPTO_OK` |
| 4 | TD-9 blind in strong trends → volume + fundamental filter (爆量續抱 / 量縮見頂) | **ADDRESSED** | `concepts/td-9-sequential.md:34` (vol ratio <0.7 = true exhaustion), `:40` (>1.3 = continuation, ignore), `:46` (TD-13 override → mandatory 50% trim); `disclosures.json` `td9-sell-hard-disable-2026-06` (P0 — sell-9 HARD DISABLED, exit only via rejection bar + monthly-MA break); `src/sharks/decision/conflict_resolver.py` blocks TD-9 counter-trend shorts |
| 5 | LLM rewriting strategies to chase Sharpe = p-hacking → constrain to hyperparameters + CPCV | **PARTIAL** | `rag-data/contracts/disclosures.json:48` declares the rule ("LLM constrained to hyperparameter ranges only; never rewrite core quant logic; validation must use CPCV; any backtest-driven rewrite loop is forbidden") and RAG force-surfaces it. **Gap:** no CPCV implementation in code, no dedicated `philosophy/concepts/` page. Current validation is walk-forward (`04-sector-and-finviz.md` Rule 1, `backtest/README.md` chronological splits) — not CPCV. |

## Recommendation

- **Points 1–4: close.** They are present in the ratified philosophy layer + data stubs + the
  RAG contract, and confirmed by both verification passes. No code change needed for Phase 1.
- **Point 5: the one real remaining gap.** The anti-p-hacking rule lives only at the
  contract/RAG layer. To operationalise it:
  1. Add a `philosophy/concepts/cpcv-validation.md` concept page (what CPCV is, why
     single-axis walk-forward overstates Sharpe, the "hyperparameters-only, never rewrite core
     logic" rule), cross-linked from `08-risk-and-position.md` and `04-sector-and-finviz.md`.
  2. Add one line to `08-risk-and-position.md` pointing at the rule (so the Risk Officer reads
     it on every backtest-touching decision).
  3. Implement CPCV folds when the Phase-4 backtest engine is built; until then the
     contract-layer guard + the human-gate on `_proposals/` is the interim mitigation.

## Note

This is a `_proposals/` draft. Per CLAUDE.md §1.1 the philosophy layer is human-curated;
an agent may propose but not commit. Human ratifies (or rejects) the point-5 actions above.
The point-in-time discipline holds: this verification carries an `as_of_timestamp` and cites
its `source_paths`; the cross-review report it relies on is itself timestamped.
