# Legendary-investor persona roster

LLM-facing prompt templates for the multi-round debate. The machine-facing
registry + deterministic research stubs live in `simulation/personas.py`; these
markdown files are the prompts used **when a real LLM is wired** (which flips
`llm_involvement` away from `none` and triggers the walk-forward gate per
`docs/LLM-BACKTEST-PROTOCOL.md`).

| Persona | File | Voice | Risk-off? |
|---|---|---|---|
| Buffett_Agent | `buffett.md` | margin of safety; cash as a call option | yes |
| Burry_Agent | `burry.md` | deep contrarian; asymmetric defined-risk shorts | yes |
| Dalio_Agent | `dalio.md` | economic machine; debt cycle; all-weather | yes |
| Soros_Agent | `soros.md` | reflexivity; bold but timed participation | no |
| TailRisk_Hedger_Agent | `tailrisk_hedger.md` | portfolio insurance; cap MaxDD | yes (hedger) |

## Unified output schema (every persona emits exactly this JSON)

```json
{
  "agent_name": "...",
  "thesis": "2-4 sentences",
  "key_risks": ["..."],
  "macro_linkage": "how the current macro (valuation, rates, liquidity, AI capex) shapes the view",
  "suggested_hedge_or_protection": "concrete protection / capital-preservation step",
  "position_sizing_view": "conservative | neutral | selective | reduce-beta | ...",
  "confidence": 0,
  "regime_view": "the persona's read of the current market regime",
  "dotcom_parallel": "is this like 2000? be specific",
  "interaction_note": "what to challenge/add vs other agents (optional)"
}
```

## Binding rules (CLAUDE.md sec.10, DEBATE_PROGRAM.md sec.5)

- **Recommend-only.** Output goes to the debate transcript only; never a ticker
  order. `proposed_actions` stays empty for personas.
- **High-valuation regime** (Buffett Indicator > 200% OR Dalio bubble flag): the
  TailRisk hedger + at least one risk-off voice are forced into the roster, and
  the Verifier (Risk Officer) vetoes any risk-adding consensus that lacks an
  explicit hedge.
- **PIT.** Cite only evidence timestamped `<= as_of`. No banned forecast-shaped
  keys on historical periods (protocol defense #1).
- **Human + Risk-Officer veto are supreme.** Personas only provide views.
