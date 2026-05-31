"""The standardized decision checklist — one gated scorecard per ticker.

Composes the EXISTING real modules (no rewrites) into the ordered gate sequence
documented in philosophy/_proposals/standard-decision-checklist.md:

    1. exclusion gate            policy_lint + risk_config.yaml (06)
    2. regime                    regime.classify_regime               (06-cycle)
    3. FOM tilt + percentile     scoring.fom.score_ticker / rank      (FOM)
    4. valuation + downside      scoring.valuation.industry_pe_valuation
    5. order / demand trajectory scoring.demand_valuation             (the kill-switch)
    6. RF / analog cycle         scoring.rfpm_cycle.run               (variable #15)
    7. 4-dimension arbitration   philosophy/02-signal-taxonomy
    8. 4-quadrant route          philosophy/03-long-short-taxonomy
    9. horizon bucket + size     philosophy/01 + 08 via risk_config
   10. invalidation              price / time-stop / catalyst (08)
   11. confidence                weights.yaml ladder + bounded nudges (05)

RECOMMEND-ONLY / observe-first. Never trades; never changes the caps. Honours
``as_of`` (no lookahead). The pure helpers (arbitration / routing / confidence /
sizing) carry no heavy imports so they unit-test offline; the data fetch is lazy.

Phase-1 honesty: the News and Sentiment dimensions are NOT wired into this path
yet (no live macro/KOL feed here), so they report ``na`` and can never inflate
alignment -- confidence stays deliberately conservative (defense-first).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from sharks.decision import _yamlite, policy_lint

WEIGHTS_PATH = Path(__file__).resolve().parent / "weights.yaml"

# Tier map (mirrors watchlist/universe.yaml tier1/tier2; everything else == tier3).
TIER1 = {"NVDA", "AAPL", "MSFT", "AMZN", "GOOGL", "GOOG", "META", "TSLA"}
TIER2 = {"TSM", "ASML", "AVGO", "AMD", "ARM", "MU", "AMAT", "LRCX"}

HORIZON_DAYS = {"1m": 30, "3m": 90, "6m": 180, "12m": 365}

# Quadrant labels (philosophy/03-long-short-taxonomy.md)
GENUINE_BULL = "多頭真漲"
SENTIMENT_BULL = "多頭虛漲"
GENUINE_BEAR = "空頭真跌"
SENTIMENT_BEAR = "空頭虛跌"
OBSERVE = "觀察/中性"


def tier_of(ticker: str) -> int:
    t = ticker.upper()
    if t in TIER1:
        return 1
    if t in TIER2:
        return 2
    return 3


# ─── Pure helpers (offline, unit-tested) ────────────────────────────────────────
def arbitrate_signals(
    fundamental: Optional[float],
    technical: Optional[float],
    news: Optional[float] = None,
    sentiment: Optional[float] = None,
    *,
    fire_threshold: float = 0.50,
) -> dict:
    """Apply the hard gating rules of philosophy/02-signal-taxonomy to four
    dimension strengths in [0,1] (None == no data for that dimension). Returns
    which dimensions fired, the aligned count, and the structural gating notes.
    """
    dims = {"fundamental": fundamental, "news": news,
            "technical": technical, "sentiment": sentiment}
    fired = {k: (v is not None and v >= fire_threshold) for k, v in dims.items()}
    aligned = sum(1 for v in fired.values() if v)
    notes: list[str] = []
    # sentiment alone never opens
    if fired["sentiment"] and not (fired["fundamental"] or fired["news"] or fired["technical"]):
        notes.append("sentiment-only -> no slot (02: sentiment never opens)")
    # news alone -> watchlist only
    if fired["news"] and not (fired["fundamental"] or fired["technical"]):
        notes.append("news-only -> watchlist, not a fill (02)")
    technical_only = fired["technical"] and not (fired["fundamental"] or fired["news"])
    if technical_only:
        notes.append("technical-only -> cap at 30% of bucket size (02)")
    return {
        "dims": {k: (round(v, 3) if v is not None else None) for k, v in dims.items()},
        "fired": fired,
        "aligned": aligned,
        "technical_only": technical_only,
        "notes": notes,
    }


def route_quadrant(
    *,
    fundamental_strong: bool,
    technical_ok: bool,
    order_decelerating: bool,
    premium_rich: bool,
    regime_label: str,
) -> dict:
    """Map computed signals to one of the four quadrants (philosophy/03)."""
    macro_break = regime_label in ("risk_off", "capitulation")
    if order_decelerating and premium_rich:
        return {"quadrant": SENTIMENT_BULL,
                "action_bias": "trim longs / short via Put only",
                "reason": "order deceleration into a rich multiple (03: 多頭虛漲)"}
    if macro_break and (order_decelerating or not technical_ok):
        return {"quadrant": GENUINE_BEAR,
                "action_bias": "active short via Mag7 Put / sector inverse ETF",
                "reason": f"macro break (regime={regime_label}) + weak tape/orders (03: 空頭真跌)"}
    if fundamental_strong and technical_ok and not order_decelerating:
        return {"quadrant": GENUINE_BULL,
                "action_bias": "long / long call, hold 3m+",
                "reason": "fundamental ≥ confirm + price/volume ok + no order break (03: 多頭真漲)"}
    if macro_break and not order_decelerating:
        return {"quadrant": SENTIMENT_BEAR,
                "action_bias": "observe; stage long for next cycle-resonance window",
                "reason": "weak regime but orders holding (03: 空頭虛跌)"}
    return {"quadrant": OBSERVE,
            "action_bias": "watchlist only",
            "reason": "no quadrant condition fully met"}


def aggregate_confidence(
    aligned: int,
    weights: dict,
    *,
    fom_percentile: Optional[float] = None,
    premium_to_fair: Optional[float] = None,
    order_trajectory: Optional[str] = None,
    cycle_state: Optional[str] = None,
) -> dict:
    """Confidence in [0,1] from the 05-decision-rubric ladder + bounded nudges
    (weights.yaml). Returns the score + the contribution breakdown (transparency)."""
    ladder = weights["confidence_ladder"]
    adj = weights["adjustments"]
    base = {0: ladder["zero"], 1: ladder["one_dimension"],
            2: ladder["two_aligned"], 3: ladder["three_aligned"]}.get(
        aligned, ladder["confluence_four"])
    contributions: list[tuple[str, float]] = [("base_aligned_%d" % aligned, base)]
    c = float(base)

    def bump(label: str, amount: float) -> None:
        nonlocal c
        c += amount
        contributions.append((label, amount))

    if fom_percentile is not None:
        if fom_percentile >= 0.75:
            bump("fom_top_quartile", adj["fom_top_quartile"])
        elif fom_percentile <= 0.25:
            bump("fom_bottom_quartile", adj["fom_bottom_quartile"])
    if premium_to_fair is not None:
        if premium_to_fair <= -0.15:
            bump("valuation_cheap", adj["valuation_cheap_15pct"])
        elif premium_to_fair >= 0.15:
            bump("valuation_rich", adj["valuation_rich_15pct"])
    if order_trajectory == "accelerating":
        bump("order_accelerating", adj["order_accelerating"])
    elif order_trajectory == "decelerating":
        bump("order_decelerating", adj["order_decelerating"])
    if cycle_state in ("ROLLOVER", "反轉", "rollover"):
        bump("cycle_rollover", adj["cycle_rollover"])
    elif cycle_state in ("EXPANSION", "擴張", "RUSH_RESTOCK", "急單/復甦(變數#15 觸發)"):
        bump("cycle_expansion", adj["cycle_expansion"])

    lo, hi = weights["clamp"]["min"], weights["clamp"]["max"]
    return {"confidence": round(max(lo, min(hi, c)), 3),
            "base": base, "contributions": contributions}


# ─── Scorecard data model ───────────────────────────────────────────────────────
@dataclass
class CheckStep:
    name: str
    status: str          # pass | warn | fail | na
    detail: str
    evidence: dict = field(default_factory=dict)


@dataclass
class ChecklistResult:
    ticker: str
    as_of: str
    tier: int
    action: str          # long_new | short_new_put | watch | exclude
    quadrant: str
    horizon: Optional[str]
    size_pct: Optional[float]
    confidence: float
    confidence_provisional: bool
    invalidation: dict
    steps: list = field(default_factory=list)
    evidence_paths: list = field(default_factory=list)
    notes: list = field(default_factory=list)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["schema_version"] = 1
        d["recommend_only"] = True
        return d


def _load_weights(path: Optional[Path] = None) -> dict:
    return _yamlite.load(path or WEIGHTS_PATH)


# ─── Orchestration ──────────────────────────────────────────────────────────────
def run_checklist(
    ticker: str,
    *,
    as_of: Optional[str] = None,
    network: bool = True,
    fundamentals: Optional[dict] = None,
    regime: Optional[dict] = None,
    closes=None,
    peers: Optional[list] = None,
    metrics: Optional[dict] = None,
    orderbook: Optional[dict] = None,
    cycle: Optional[dict] = None,
    cfg: Optional[dict] = None,
    weights: Optional[dict] = None,
) -> ChecklistResult:
    """Run the full gated checklist for one ticker. Every external input can be
    injected (for offline tests); when omitted and ``network`` is True they are
    fetched from the existing modules. Never raises on missing data — a failed
    sub-step degrades to ``status='na'``."""
    ticker = ticker.upper()
    as_of = as_of or datetime.now().strftime("%Y-%m-%d")
    cfg = cfg or policy_lint.load_risk_config()
    weights = weights or _load_weights()
    tier = tier_of(ticker)
    steps: list[CheckStep] = []
    evidence_paths = ["risk_config.yaml", "philosophy/02-signal-taxonomy.md",
                      "philosophy/03-long-short-taxonomy.md",
                      "philosophy/08-risk-and-position.md"]
    notes: list[str] = []

    # ── fundamentals (price/sector/valuation inputs) ───────────────────────────
    if fundamentals is None and network:
        try:
            from sharks.scoring.fundamentals import fetch_fundamentals
            fundamentals = fetch_fundamentals(ticker)
        except Exception as e:  # pragma: no cover - network
            fundamentals = {"ticker": ticker, "error": str(e)[:80]}
    f = fundamentals or {"ticker": ticker}
    price = f.get("price")
    sector = f.get("sector")

    # ── 1. exclusion gate ──────────────────────────────────────────────────────
    pick = {"price": price, "market_cap": f.get("market_cap"), "tier": tier,
            "sector": sector, "side": "long"}
    violations = policy_lint.lint_pick(pick, cfg)
    hard_fail = [v for v in violations if v["rule"] in ("price_floor", "liquidity_floor", "market_cap_floor")]
    steps.append(CheckStep(
        "exclusion_gate",
        "fail" if hard_fail else ("warn" if violations else "pass"),
        ("excluded: " + "; ".join(v["detail"] for v in hard_fail)) if hard_fail
        else ("flags: " + "; ".join(v["detail"] for v in violations)) if violations
        else f"clears 06-exclusions (price=${price}, tier{tier})",
        {"violations": violations},
    ))
    if hard_fail:
        return ChecklistResult(
            ticker, as_of, tier, "exclude", OBSERVE, None, None, 0.0, True,
            {"price": None, "time_stop_days": None, "catalyst": "excluded at the gate"},
            [asdict(s) for s in steps], evidence_paths,
            ["hard exclusion — no further evaluation"])

    # ── 2. regime ──────────────────────────────────────────────────────────────
    if regime is None:
        try:
            from sharks.regime.classifier import classify_regime
            regime = classify_regime()
        except Exception as e:  # pragma: no cover
            regime = {"label": "neutral", "reasons": [f"fallback ({e})"], "weights": {}}
    regime_label = regime.get("label", "neutral")
    steps.append(CheckStep("regime", "pass",
                           f"regime={regime_label} ({', '.join(regime.get('reasons', [])) or 'no reasons'})",
                           {"label": regime_label, "weights": regime.get("weights")}))

    # ── 3. FOM (single-name + percentile vs a peer set) ────────────────────────
    fom_final = fom_percentile = momentum = None
    try:
        import pandas as pd
        from sharks.scoring import fom as fommod
        as_ts = pd.Timestamp(as_of)
        if closes is None and network:
            peers = peers or sorted(TIER1 | TIER2 | {ticker})
            start = (as_ts - pd.Timedelta(days=6 * 365)).strftime("%Y-%m-%d")
            closes = fommod.fetch_monthly(peers, start, as_of)
        if closes is not None and ticker in getattr(closes, "columns", []):
            scored = fommod.rank_universe(closes, list(closes.columns), as_ts, regime=regime)
            me = next((s for s in scored if s.ticker == ticker), None)
            if me is not None:
                fom_final = round(me.final_fom, 2)
                momentum = round(me.momentum, 1)
                below = sum(1 for s in scored if s.final_fom < me.final_fom)
                fom_percentile = round(below / max(len(scored) - 1, 1), 3)
                steps.append(CheckStep("fom", "pass",
                    f"final_FOM={fom_final} (pct={fom_percentile:.0%} of {len(scored)} peers), "
                    f"momentum={momentum}, regime-gated",
                    {"final_fom": fom_final, "percentile": fom_percentile,
                     "momentum": momentum, "horizon_scores": me.horizon_scores}))
        if fom_final is None:
            steps.append(CheckStep("fom", "na", "no price data for FOM (offline or unlisted)"))
    except Exception as e:  # pragma: no cover
        steps.append(CheckStep("fom", "na", f"FOM unavailable: {str(e)[:80]}"))

    # ── 4. valuation + realistic downside ──────────────────────────────────────
    premium = realistic_downside = panic_floor = None
    try:
        from sharks.scoring.valuation import industry_pe_valuation
        v = industry_pe_valuation(f)
        if v:
            premium = v.get("premium_to_industry_fair")
            realistic_downside = v.get("realistic_downside")
            panic_floor = v.get("panic_floor")
            steps.append(CheckStep("valuation", "pass",
                f"premium_to_industry_fair={premium:+.0%} | realistic_downside={realistic_downside:+.0%} | "
                f"fair(ind)=${v.get('fair_value_industry')} panic=${panic_floor}",
                v))
        else:
            steps.append(CheckStep("valuation", "na", "insufficient fundamentals for P/E-anchored valuation"))
    except Exception as e:  # pragma: no cover
        steps.append(CheckStep("valuation", "na", f"valuation unavailable: {str(e)[:80]}"))

    # ── 5. order / demand trajectory (the kill-switch) ─────────────────────────
    order_trajectory = None
    demand_row = None
    try:
        from sharks.scoring.demand_valuation import load_orderbook, demand_valuation_row, fetch_quality_metrics
        ob_all = orderbook if orderbook is not None else load_orderbook()
        if ticker in ob_all:
            m = metrics
            if m is None and network:
                m = fetch_quality_metrics(ticker)
            m = m or {"ticker": ticker, "sector": sector}
            demand_row = demand_valuation_row(ticker, m, ob_all[ticker])
            order_trajectory = demand_row.get("order_trajectory")
            evidence_paths.append("watchlist/demand-orderbook.json")
            steps.append(CheckStep(
                "order_demand",
                "fail" if order_trajectory == "decelerating" else "pass",
                f"order_trajectory={order_trajectory} | prem_to_fair={demand_row.get('premium_to_fair')} | "
                f"{demand_row.get('verdict')}",
                {k: demand_row.get(k) for k in ("order_trajectory", "order_alert",
                                                "premium_to_fair", "adjusted_fair_pe", "verdict")}))
            if premium is None:
                premium = demand_row.get("premium_to_fair")
        else:
            steps.append(CheckStep("order_demand", "na",
                                   "no curated order-book for this name (not an RF/semi tracked node)"))
    except Exception as e:  # pragma: no cover
        steps.append(CheckStep("order_demand", "na", f"demand layer unavailable: {str(e)[:80]}"))

    # ── 6. RF / analog cycle (variable #15) ────────────────────────────────────
    cycle_state = None
    is_rf_name = ticker in (orderbook or {}) or order_trajectory is not None
    if cycle is not None:
        cycle_state = cycle.get("state")
        steps.append(CheckStep("rf_cycle", "pass",
                               f"leading-door state={cycle_state} (injected)", cycle))
    elif is_rf_name and network:
        try:
            from sharks.scoring.rfpm_cycle import run as rf_run
            reading = rf_run(as_of=as_of, network=True)
            cycle_state = reading.leading_door.get("state")
            steps.append(CheckStep("rf_cycle", "pass",
                f"leading-door={cycle_state} lagging={reading.lagging_door.get('state')} "
                f"(evidence L={reading.evidence_score_leading:+.2f})",
                {"leading": reading.leading_door, "lagging": reading.lagging_door}))
            evidence_paths.append("watchlist/rfpm-cycle-evidence.json")
        except Exception as e:  # pragma: no cover
            steps.append(CheckStep("rf_cycle", "na", f"cycle read unavailable: {str(e)[:80]}"))
    else:
        steps.append(CheckStep("rf_cycle", "na", "not an RF/analog name (cycle not applicable)"))

    # ── 7. 4-dimension arbitration (02) ────────────────────────────────────────
    # Fundamental strength: turnaround flags + analyst upside + order trajectory.
    flags = (f.get("flags") or {})
    f_strength = None
    if flags or demand_row is not None or f.get("analyst_upside") is not None:
        s = 0.0
        s += 0.12 * (flags.get("turnaround_score", 0) or 0)        # 0..0.60
        if f.get("analyst_upside") is not None:
            s += max(-0.1, min(0.2, f["analyst_upside"]))          # analyst tilt
        if order_trajectory == "accelerating":
            s += 0.20
        elif order_trajectory == "decelerating":
            s -= 0.30
        f_strength = max(0.0, min(1.0, s))
    # Technical strength: FOM momentum (0..100) -> 0..1.
    t_strength = round(momentum / 100.0, 3) if momentum is not None else None
    arb = arbitrate_signals(f_strength, t_strength)  # news/sentiment = na (Phase 1)
    steps.append(CheckStep("signal_arbitration", "pass",
        f"aligned={arb['aligned']}/2 wired dims (news+sentiment NOT wired in Phase 1) "
        f"fundamental={arb['dims']['fundamental']} technical={arb['dims']['technical']}; "
        + ("; ".join(arb["notes"]) or "no gating flags"),
        arb))
    notes.append("Phase 1: News + Sentiment dimensions not wired -> confidence is conservative by design.")

    # ── 8. 4-quadrant route (03) ───────────────────────────────────────────────
    premium_rich = premium is not None and premium >= 0.15
    quad = route_quadrant(
        fundamental_strong=bool(arb["fired"]["fundamental"]),
        technical_ok=bool(arb["fired"]["technical"]),
        order_decelerating=order_trajectory == "decelerating",
        premium_rich=premium_rich,
        regime_label=regime_label,
    )
    steps.append(CheckStep("quadrant_route", "pass",
                           f"{quad['quadrant']} — {quad['reason']} -> {quad['action_bias']}", quad))

    # ── 9. horizon bucket + position size (01 + 08) ────────────────────────────
    quad_horizon = {GENUINE_BULL: "3m", SENTIMENT_BULL: "1m",
                    GENUINE_BEAR: "1m", SENTIMENT_BEAR: "6m", OBSERVE: None}
    horizon = quad_horizon.get(quad["quadrant"])
    size_pct = policy_lint.size_cap_for(tier, horizon, cfg) if horizon else None
    if size_pct is not None and arb["technical_only"]:
        size_pct = round(size_pct * 0.30, 2)
        notes.append("technical-only -> size capped at 30% of bucket (02).")
    steps.append(CheckStep("position_size", "pass" if size_pct is not None else "na",
        (f"bucket={horizon}, tier{tier} cap={size_pct}% of portfolio"
         if size_pct is not None else "no entry bucket (observe)"),
        {"horizon": horizon, "size_pct": size_pct}))

    # ── 10. invalidation (08) ──────────────────────────────────────────────────
    inval_price = panic_floor if panic_floor is not None else (round(price * 0.90, 2) if price else None)
    hdays = HORIZON_DAYS.get(horizon)
    time_stop = int(hdays * cfg["risk_of_ruin"]["time_stop_multiplier"]) if hdays else None
    catalyst = (demand_row or {}).get("order_alert") or (
        "thesis falsification: order deceleration (B:B<1 / backlog stall) OR regime break OR "
        "structural-thesis price level breached")
    invalidation = {"price": inval_price, "time_stop_days": time_stop, "catalyst": catalyst}
    ts_txt = f"{time_stop}d" if time_stop else "n/a"
    steps.append(CheckStep("invalidation", "pass" if horizon else "na",
        f"price<=${inval_price} | time_stop={ts_txt} | {catalyst[:60]}...", invalidation))

    # ── 11. confidence (weights.yaml ladder + nudges; 05) ──────────────────────
    conf = aggregate_confidence(arb["aligned"], weights,
                                fom_percentile=fom_percentile, premium_to_fair=premium,
                                order_trajectory=order_trajectory, cycle_state=cycle_state)
    confidence = conf["confidence"]
    provisional = weights.get("calibration_status", "").startswith("phase1")
    thr = cfg["confidence"]["slot_threshold"]
    steps.append(CheckStep("confidence", "pass" if confidence >= thr else "warn",
        f"confidence={confidence} (threshold {thr}; {'provisional/uncalibrated' if provisional else 'calibrated'}) "
        f"base={conf['base']}", conf))

    # ── final action ───────────────────────────────────────────────────────────
    if confidence < thr or quad["quadrant"] in (OBSERVE, SENTIMENT_BEAR):
        action = "watch"
    elif quad["quadrant"] == GENUINE_BULL:
        action = "long_new"
    elif quad["quadrant"] in (SENTIMENT_BULL, GENUINE_BEAR):
        action = "short_new_put"
    else:
        action = "watch"
    if action == "watch":
        size_pct, horizon = None, horizon  # keep horizon for context but no size

    return ChecklistResult(
        ticker, as_of, tier, action, quad["quadrant"], horizon, size_pct,
        confidence, provisional, invalidation,
        [asdict(s) for s in steps], evidence_paths, notes)


def write_output(out_dir: Path, result: ChecklistResult) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {"written_at": datetime.now(timezone.utc).isoformat(),
               "report_type": "decision_checklist", **result.to_dict()}
    path = out_dir / f"checklist-{result.ticker}-{result.as_of}.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    return path


def format_scorecard(result: ChecklistResult) -> str:
    """Plain-language readout (explain-don't-just-build)."""
    lines = [f"  {result.ticker}  (tier{result.tier})  as_of {result.as_of}",
             f"  ACTION: {result.action.upper()}   quadrant={result.quadrant}   "
             f"confidence={result.confidence}{' (provisional)' if result.confidence_provisional else ''}"]
    if result.horizon:
        lines.append(f"  bucket={result.horizon}  size_cap={result.size_pct}%  "
                     f"invalidation: price<={result.invalidation['price']} "
                     f"time_stop={result.invalidation['time_stop_days']}d")
    lines.append("  gates:")
    for s in result.steps:
        mark = {"pass": "✓", "warn": "!", "fail": "✗", "na": "·"}.get(s["status"], "?")
        lines.append(f"    [{mark}] {s['name']:18} {s['detail']}")
    if result.notes:
        lines.append("  notes: " + " | ".join(result.notes))
    return "\n".join(lines)
