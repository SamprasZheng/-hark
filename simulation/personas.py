#!/usr/bin/env python3
"""
Trading Society -- Legendary-investor persona roster (Debate Step 1)

PPST Declaration (this PROGRAM):
- PROJECT: Trading Society
- PROGRAM: simulation/personas.py (+ skills/multi_round_debate/personas/*.md)
- SKILL:   multi_round_debate persona injection + forced-hedge regime rule
- TARGET:  A roster of 5 structured investor personas (Buffett, Burry, Dalio,
           Soros, TailRisk_Hedger) that each emit a unified JSON view, plus the
           orchestration that (a) injects them as debate proposers and (b) in a
           HIGH-VALUATION regime forces the TailRisk hedger + at least one
           risk-off voice and lets the Verifier (Risk Officer) veto any
           risk-adding consensus that lacks an explicit hedge.

Governance (binds; CLAUDE.md sec.10, DEBATE_PROGRAM.md):
- recommend-only: persona outputs go ONLY into the debate transcript. They never
  emit a ticker order; default proposed_actions is empty (stand down) so the safe
  default in a stretched market is "no new risk + hedge".
- The deterministic propose() functions are research stubs -> llm_involvement
  stays "none". Wiring a real LLM uses the matching prompt in
  skills/multi_round_debate/personas/<name>.md and flips the marker (triggering
  the walk-forward gate per docs/LLM-BACKTEST-PROTOCOL.md).
- Human + Risk-Officer veto remain supreme. Personas only provide views.

Run: python simulation/personas.py   (runs a high-valuation persona debate demo)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

try:
    from simulation.debate_engine import DebateEngine, Message, DebateState
except Exception:  # pragma: no cover - path fallback for direct script run
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from simulation.debate_engine import DebateEngine, Message, DebateState

# Unified persona output schema (every persona fills exactly these keys).
PERSONA_SCHEMA_KEYS = [
    "agent_name", "thesis", "key_risks", "macro_linkage",
    "suggested_hedge_or_protection", "position_sizing_view", "confidence",
    "regime_view", "dotcom_parallel", "interaction_note",
]
# Threshold that flips the society into "high valuation" posture.
BUFFETT_INDICATOR_HIGH = 200.0


# ---------------------------------------------------------------------------
# Market context handed to each persona (PIT; supplied by the caller / Step-2
# macro provider once it exists). No lookahead -- caller guarantees as_of-honesty.
# ---------------------------------------------------------------------------
@dataclass
class MarketContext:
    as_of: str
    topic: str = ""
    buffett_indicator: Optional[float] = None  # percent, e.g. 225.0
    dalio_bubble_flag: bool = False
    regime_label: str = "unknown"
    vix: Optional[float] = None
    ten_year_yield: Optional[float] = None     # percent, e.g. 4.5
    extra: Dict[str, Any] = field(default_factory=dict)

    @property
    def high_valuation(self) -> bool:
        bi_hi = (self.buffett_indicator is not None
                 and self.buffett_indicator > BUFFETT_INDICATOR_HIGH)
        return bool(bi_hi or self.dalio_bubble_flag)

    def bi_str(self) -> str:
        return f"{self.buffett_indicator:.0f}%" if self.buffett_indicator else "n/a"


@dataclass
class Persona:
    name: str
    philosophy: str
    model_size: str            # routing hint (small/medium/large)
    risk_off: bool             # is this a defensive / risk-off voice?
    is_hedger: bool            # is this the dedicated tail-risk hedger?
    default_stance: str        # support|oppose|neutral (pre-context)
    propose: Callable[["MarketContext"], Dict[str, Any]]


# ---------------------------------------------------------------------------
# Deterministic persona propose() functions (research stubs; English payloads to
# stay console-safe). Real LLM wiring uses the .md prompt templates.
# ---------------------------------------------------------------------------
def _buffett(ctx: MarketContext) -> Dict[str, Any]:
    hv = ctx.high_valuation
    return {
        "agent_name": "Buffett_Agent",
        "thesis": ("Quality businesses bought with a margin of safety, held for "
                   "compounding. With the Buffett Indicator near record highs, "
                   "cash is a call option; I would rather hold cash than overpay."),
        "key_risks": ["overpaying at record valuations",
                      "permanent capital loss", "leverage / complexity"],
        "macro_linkage": (f"Buffett Indicator ~{ctx.bi_str()} is historically "
                          f"extreme; 10Y ~{ctx.ten_year_yield or 4.5}% raises the "
                          "equity risk-premium bar."),
        "suggested_hedge_or_protection": (
            "Raise cash, trim the richest-valued names, wait for a margin of "
            "safety." if hv else "Hold quality compounders; keep a cash buffer."),
        "position_sizing_view": "conservative / selective" if hv else "neutral",
        "confidence": 72,
        "regime_view": ("High valuation regime; wait for margin of safety"
                        if hv else "Constructive on quality"),
        "dotcom_parallel": ("Yes -- stretched valuations and hype echo 2000; "
                            "discipline over FOMO." if hv else "Limited."),
        "interaction_note": "Challenge any aggressive long that ignores price paid.",
    }


def _burry(ctx: MarketContext) -> Dict[str, Any]:
    hv = ctx.high_valuation
    return {
        "agent_name": "Burry_Agent",
        "thesis": ("Asymmetric downside is mispriced. Hype plus record valuations "
                   "set up a deep repricing; favour defined-risk puts on the most "
                   "crowded AI names rather than chasing."),
        "key_risks": ["being early", "short squeeze / momentum", "timing risk"],
        "macro_linkage": ("Concentrated AI leadership + fiscal-dominance liquidity "
                          "risk make crowded longs fragile."),
        "suggested_hedge_or_protection": (
            "Defined-risk put options (limited premium, convex payoff); never "
            "naked shorts."),
        "position_sizing_view": "small, convex, defined-risk",
        "confidence": 60,
        "regime_view": "Late-cycle bubble; run a recession stress test",
        "dotcom_parallel": ("Strong -- the speculative breadth resembles 1999-2000."
                            if hv else "Watching for it."),
        "interaction_note": "Stress-test any bull thesis against a 30-50% drawdown.",
    }


def _dalio(ctx: MarketContext) -> Dict[str, Any]:
    hv = ctx.high_valuation
    return {
        "agent_name": "Dalio_Agent",
        "thesis": ("The AI boom is in an early-bubble phase. Do not panic-sell, "
                   "but expect low forward returns; diversify across asset classes "
                   "and geographies (all-weather)."),
        "key_risks": ["debt cycle / fiscal dominance",
                      "low forward 10y returns", "US large-cap tech concentration"],
        "macro_linkage": ("End-of-QT liquidity drains + fiscal dominance argue for "
                          "diversification away from concentrated US equity beta."),
        "suggested_hedge_or_protection": (
            "All-weather diversification: gold / non-US assets, balanced duration, "
            "reduce single-theme concentration."),
        "position_sizing_view": "diversify; trim concentration; risk-parity tilt",
        "confidence": 65,
        "regime_view": "Early bubble phase; prepare, do not panic",
        "dotcom_parallel": "Partial -- valuations rich, but breadth differs from 2000.",
        "interaction_note": "Reframe single-name bets as portfolio-level risk.",
    }


def _soros(ctx: MarketContext) -> Dict[str, Any]:
    return {
        "agent_name": "Soros_Agent",
        "thesis": ("Reflexivity can extend the trend beyond fundamentals. "
                   "Participate selectively with tight timing, but be ready to "
                   "flip on a confirmed regime break."),
        "key_risks": ["reflexive reversal", "liquidity withdrawal (QT/TGA)",
                      "crowded positioning"],
        "macro_linkage": ("Liquidity proxies (WALCL/TGA/RRP) and positioning drive "
                          "the reflexive feedback loop more than valuation alone."),
        "suggested_hedge_or_protection": (
            "Selective participation with stops + asymmetric optionality; flip "
            "exposure fast on a regime break."),
        "position_sizing_view": "selective participation, timed; quick to reduce",
        "confidence": 60,
        "regime_view": "Reflexive late-stage trend; watch for the turn",
        "dotcom_parallel": "Possible, but a bubble can overshoot first.",
        "interaction_note": "Time matters as much as direction -- name the trigger.",
    }


def _tailrisk(ctx: MarketContext) -> Dict[str, Any]:
    hv = ctx.high_valuation
    return {
        "agent_name": "TailRisk_Hedger_Agent",
        "thesis": ("Provide insurance, not predictions. In an elevated-risk regime "
                   "the priority is protecting capital and capping max drawdown."),
        "key_risks": ["dot-com style repricing", "liquidity stress",
                      "rate shock", "AI-capex energy / grid bottleneck"],
        "macro_linkage": (f"Buffett Indicator ~{ctx.bi_str()} + tightening net "
                          "liquidity amplify tail risk; protection is cheap relative "
                          "to the convexity it buys."),
        "suggested_hedge_or_protection": (
            "OTM put protection / collar, Treasury ladder, raise cash buffer, "
            "volatility targeting, rebalance on regime shift."),
        "position_sizing_view": "reduce equity beta; raise Treasury + cash",
        "confidence": 75,
        "regime_view": "Elevated tail risk" if hv else "Moderate tail risk",
        "dotcom_parallel": ("Comparable systemic tail risk to 2000." if hv
                            else "Contained for now."),
        "interaction_note": ("Directly challenge any 'upside-only' view that omits "
                             "protection."),
    }


# ---------------------------------------------------------------------------
# Roster
# ---------------------------------------------------------------------------
BUFFETT = Persona("Buffett_Agent", "Margin of safety; cash as a call option",
                  "large", risk_off=True, is_hedger=False,
                  default_stance="oppose", propose=_buffett)
BURRY = Persona("Burry_Agent", "Deep contrarian; asymmetric defined-risk shorts",
                "large", risk_off=True, is_hedger=False,
                default_stance="oppose", propose=_burry)
DALIO = Persona("Dalio_Agent", "Economic machine; debt cycle; all-weather",
                "large", risk_off=True, is_hedger=False,
                default_stance="neutral", propose=_dalio)
SOROS = Persona("Soros_Agent", "Reflexivity; bold but timed participation",
                "large", risk_off=False, is_hedger=False,
                default_stance="support", propose=_soros)
TAILRISK = Persona("TailRisk_Hedger_Agent", "Portfolio insurance; cap MaxDD",
                   "medium", risk_off=True, is_hedger=True,
                   default_stance="oppose", propose=_tailrisk)

ROSTER: Dict[str, Persona] = {p.name: p for p in (BUFFETT, BURRY, DALIO, SOROS, TAILRISK)}


def enforce_roster(ctx: MarketContext, roster: List[Persona]) -> tuple:
    """
    HIGH-VALUATION rule (CLAUDE.md sec.10): force the TailRisk hedger in, and
    ensure at least one risk-off voice is present. Returns (roster, notes).
    """
    notes: List[str] = []
    out = list(roster)
    if ctx.high_valuation:
        if not any(p.is_hedger for p in out):
            out.append(TAILRISK)
            notes.append("high-valuation regime: force-injected TailRisk_Hedger_Agent.")
        if not any(p.risk_off for p in out):
            out.append(BUFFETT)
            notes.append("high-valuation regime: force-injected a risk-off voice "
                         "(Buffett_Agent).")
    return out, notes


# ---------------------------------------------------------------------------
# Build debate proposals from personas
# ---------------------------------------------------------------------------
def build_persona_proposals(ctx: MarketContext, roster: List[Persona]
                            ) -> List[Message]:
    msgs: List[Message] = []
    for p in roster:
        payload = p.propose(ctx)
        # Context can sharpen stance: risk-off voices oppose new risk when stretched.
        stance = p.default_stance
        if ctx.high_valuation and p.risk_off:
            stance = "oppose"
        msgs.append(Message(
            debate_id="", round=0, from_agent=p.name, message_type="proposal",
            as_of_timestamp=ctx.as_of, content=payload["thesis"],
            evidence=[], severity="medium" if p.risk_off else "low",
            confidence=round(payload["confidence"] / 100.0, 3), stance=stance,
            extra={**payload, "risk_off": p.risk_off, "is_hedger": p.is_hedger,
                   "proposed_actions": []},  # recommend-only: no ticker orders
        ))
    return msgs


# ---------------------------------------------------------------------------
# High-valuation Verifier (Risk Officer seat) -- veto power
# ---------------------------------------------------------------------------
def make_persona_verifier(ctx: MarketContext) -> Callable[[DebateState], Message]:
    def verify(st: DebateState) -> Message:
        proposals = st.proposals
        n = max(1, len(proposals))
        hedge_present = any(
            p.extra.get("is_hedger") and p.extra.get("suggested_hedge_or_protection")
            for p in proposals)
        risk_off_present = any(p.extra.get("risk_off") for p in proposals)
        wants_risk = any(p.stance == "support" and p.extra.get("proposed_actions")
                         for p in proposals)

        veto, reason = False, ""
        if ctx.high_valuation:
            if not hedge_present:
                veto, reason = True, ("High-valuation regime requires an explicit "
                                      "hedge (TailRisk) in any consensus.")
            elif wants_risk and not risk_off_present:
                veto, reason = True, ("Risk-adding consensus in a high-valuation "
                                      "regime lacks a risk-off voice.")

        support = sum(1 for p in proposals if p.stance == "support")
        oppose = sum(1 for p in proposals if p.stance == "oppose")
        majority = max(support, oppose) / n
        direction = "act" if support > oppose else "stand_down"
        consensus = (not veto) and majority >= 2 / 3

        return Message(
            debate_id=st.debate_id, round=st.round, from_agent="VERIFIER",
            to_agent=None, message_type="verification", as_of_timestamp=st.as_of,
            content=(reason or
                     (f"PIT + grade gate ok; hedge_present={hedge_present}; "
                      f"leaning '{direction}'. "
                      + ("consensus." if consensus else "no firm consensus."))),
            evidence=[], severity="high" if veto else "low",
            confidence=0.7, stance="neutral",
            extra={"consensus_reached": consensus, "veto": veto,
                   "veto_reason": reason or None, "lean": direction,
                   "hedge_present": hedge_present,
                   "support_fraction": round(support / n, 3)},
        )
    return verify


def make_persona_synthesizer(ctx: MarketContext) -> Callable[[DebateState], Message]:
    def synth(st: DebateState) -> Message:
        proposals = st.proposals
        hedges = [p.extra.get("suggested_hedge_or_protection")
                  for p in proposals if p.extra.get("suggested_hedge_or_protection")]
        regime_views = [p.extra.get("regime_view") for p in proposals
                        if p.extra.get("regime_view")]
        support = sum(1 for p in proposals if p.stance == "support")
        oppose = sum(1 for p in proposals if p.stance == "oppose")
        defensive = oppose >= support
        avg_conf = round(sum(p.confidence for p in proposals) / max(1, len(proposals)), 3)
        final_view = (
            "Defensive consensus: stand down on new risk, carry explicit hedges."
            if defensive else
            "Selective participation, but only with the mandated hedges in place.")
        return Message(
            debate_id=st.debate_id, round=st.round, from_agent="SYNTHESIZER",
            to_agent=None, message_type="synthesis", as_of_timestamp=st.as_of,
            content=final_view, evidence=[], severity="low",
            confidence=avg_conf, stance="neutral",
            extra={
                "final_view": final_view,
                "proposed_actions": [],  # recommend-only
                "no_action_buckets": ["long_new", "short_new"],
                "mandated_hedges": hedges,
                "dominant_regime_views": regime_views,
                "high_valuation_regime": ctx.high_valuation,
                "risk_flags": (["high_valuation", "hedge_mandatory"]
                               if ctx.high_valuation else []),
            },
        )
    return synth


def run_persona_debate(ctx: MarketContext,
                       roster: Optional[List[Persona]] = None,
                       max_rounds: int = 3) -> Dict[str, Any]:
    """
    Full persona debate: enforce roster -> build proposals -> run DebateEngine
    with the high-valuation Verifier + persona Synthesizer. llm_involvement=none.
    """
    roster = roster or list(ROSTER.values())
    roster, roster_notes = enforce_roster(ctx, roster)
    proposals = build_persona_proposals(ctx, roster)

    # Critic = the dedicated hedger pressing the bullish voices (deterministic).
    def critic(st: DebateState) -> Message:
        target = next((p.from_agent for p in st.proposals if p.stance == "support"),
                      st.proposals[0].from_agent if st.proposals else "?")
        return Message(
            debate_id=st.debate_id, round=st.round, from_agent="TailRisk_Hedger_Agent",
            to_agent=target, message_type="challenge", as_of_timestamp=st.as_of,
            content=f"{target}: if the worst case hits, what is our MaxDD and how "
                    f"is it capped? Name the protection.",
            evidence=[], severity="high" if ctx.high_valuation else "medium",
            confidence=0.7, stance="oppose")

    engine = DebateEngine(critic, make_persona_verifier(ctx),
                          make_persona_synthesizer(ctx))
    debate_id = f"persona-debate-{ctx.as_of}"
    result = engine.run(debate_id, topic=ctx.topic or "Posture for the AI-bubble tape?",
                        as_of=ctx.as_of, proposals=proposals, max_rounds=max_rounds,
                        llm_involvement="none")
    result["roster"] = [p.name for p in roster]
    result["roster_notes"] = roster_notes
    result["high_valuation_regime"] = ctx.high_valuation
    return result


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------
def _demo() -> int:
    import json
    print("=" * 72)
    print("personas self-test -- HIGH-VALUATION persona debate (llm=none)")
    print("=" * 72)
    ctx = MarketContext(
        as_of="2026-06-13",
        topic="Participate in the AI rally, or protect capital?",
        buffett_indicator=225.0, dalio_bubble_flag=True,
        regime_label="high_valuation", ten_year_yield=4.5,
    )
    result = run_persona_debate(ctx)
    compact = {k: result[k] for k in ("debate_id", "consensus", "verifier_veto",
                                      "confidence", "roster", "roster_notes",
                                      "high_valuation_regime")}
    compact["mandated_hedges"] = result.get("mandated_hedges")
    compact["final_view"] = result.get("final_view")
    compact["risk_flags"] = result.get("risk_flags")
    compact["transcript"] = [f"{m['round']}:{m['from_agent']}:{m['message_type']}"
                             for m in result["transcript"]]
    print(json.dumps(compact, indent=2, ensure_ascii=False))

    print("\n--- force-injection: high-valuation + a lone-bull roster ---")
    # Caller tries to run only Soros (a bull) in a stretched tape; the rule must
    # force the hedger + a risk-off voice back in.
    inj = run_persona_debate(ctx, roster=[SOROS])
    print(json.dumps({"roster": inj["roster"], "roster_notes": inj["roster_notes"],
                      "consensus": inj["consensus"], "veto": inj["verifier_veto"],
                      "risk_flags": inj.get("risk_flags")},
                     indent=2, ensure_ascii=False))

    print("\n--- contrast: NORMAL regime (no forced hedge) ---")
    ctx2 = MarketContext(as_of="2026-06-13", topic="Normal-tape posture?",
                         buffett_indicator=150.0, dalio_bubble_flag=False)
    r2 = run_persona_debate(ctx2)
    print(json.dumps({"consensus": r2["consensus"], "veto": r2["verifier_veto"],
                      "high_valuation_regime": r2["high_valuation_regime"],
                      "roster_notes": r2["roster_notes"]},
                     indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(_demo())
