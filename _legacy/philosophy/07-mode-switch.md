---
type: synthesis
tags: [mode, frequency, low-high-auto, market-state, philosophy]
title: Frequency Mode Switch — Market-State Driven
author_role: human
---

# 07 · Frequency Mode Switch

Codex review point #7: mode switching by human calendar ("weekend = high freq") is too coarse and ignores market state. This page makes the trigger explicit and machine-checkable.

## The three modes

| Mode | Cadence | Use case |
|---|---|---|
| `low` (default) | EOD price + hourly news / KOL digest + daily compile + daily 10-signal output | Default for any weekday US session, default for crypto when volatility is normal |
| `high` | 5m bar pull + near-real-time news + continuous compile | Active trading windows when conditions below all hold |
| `auto` | CLI evaluates conditions and picks | The recommended default for `sharks pick` if no `--mode` flag |

## `should_use_high_freq_mode()` decision function

Pseudo-spec (the Phase 3 implementation in `src/sharks/mode/decide.py` must match):

```python
def should_use_high_freq_mode(
    now: datetime,
    market_state: MarketState,
    user_opt_in: bool,
) -> tuple[bool, str]:
    """
    Returns (use_high_freq, reason).
    Reason is a non-empty string explaining the verdict — always.
    """
    # Hard refusals
    if market_state.vix > 35:
        return False, "VIX > 35: force defensive low-freq mode"
    if market_state.is_geopolitical_event_day:
        return False, "geopolitical event day: force low-freq observation"
    if market_state.has_earnings_within_3d(market_state.active_holdings):
        return False, "earnings within 3 trading days for held position"
    if market_state.is_fed_day or market_state.is_cpi_day or market_state.is_nfp_day:
        return False, "macro release day: force low-freq"

    # Opt-in gate
    if not user_opt_in:
        return False, "user has not opted in (SHARKS_HIGH_FREQ_OK != 1)"

    # Eligibility floor
    if not (12 <= market_state.vix <= 18):
        return False, f"VIX {market_state.vix:.1f} outside high-freq band [12, 18]"

    if not market_state.target_instrument_meets_liquidity_floor():
        return False, "target instrument liquidity below high-freq floor"

    return True, "all conditions met"
```

## The conditions, expanded

### Hard refusals — `low` regardless of opt-in

These are non-negotiable. The system refuses to trade high-freq even if the user insists.

- **VIX > 35**: macro volatility regime where intraday move correlation rises and the swing thesis breaks down. Defensive observation only.
- **Geopolitical event day** (war declaration, major sanctions release, etc.): first 24h of any qualifying event. Updated in `wiki/01_macro_state.md` by the Compiler.
- **Earnings within 3 trading days** for any active tier-1 or tier-2 position: event-clustering risk plus the gamma asymmetry on Put hedges.
- **Macro release day**: Fed FOMC, CPI, NFP. The intraday following any of these is dominated by macro re-pricing, not by the structural thesis the system trades.

### Opt-in gate

- Environment variable `SHARKS_HIGH_FREQ_OK=1` must be set, OR
- The CLI run was invoked with `--mode high` explicitly (which sets the env var for that invocation only).

Rationale: high-freq operations have higher API cost, higher decision-error rate, and require the human to be present. Default-off prevents accidental escalation.

### Eligibility floor

- **VIX in [12, 18]**: the ideal swing-friendly volatility band. Below 12 is complacency and signal-to-noise collapses. Above 18 the bucket-size caps in [[08-risk-and-position]] start binding and high-freq adds little.
- **Liquidity floor** for the target instrument: re-uses the [[06-exclusions]] universe-level liquidity rules but with stricter thresholds for high-freq (`60d_avg_dollar_volume > $20M / day`).

## Weekend crypto special case

The user explicitly named weekend crypto trading as the canonical high-freq scenario. Special handling:

- The macro-release-day refusals do not apply to crypto.
- The earnings refusals do not apply to crypto (no earnings concept).
- The VIX gate is replaced by a crypto-volatility proxy: `BTC 60m realised vol annualised in [40%, 100%]`. Outside this band → low-freq.
- The user opt-in is still required (separate env var: `SHARKS_HIGH_FREQ_CRYPTO_OK=1`).

## When modes change mid-session

If a refusal condition fires while a high-freq session is running (e.g. surprise geopolitical event), the system:

1. Immediately switches to `low` for new signal evaluation.
2. Does NOT auto-close existing positions opened in `high` mode. Those continue under their original invalidation triggers.
3. Logs the switch + reason in `wiki/log.md`.
4. Marks the next daily 10-signal output with `regime.mode_change_during_session: true` for retrospective study.

## Anti-pattern: "I'm bored, let me high-freq"

Codex's broader concern: human-calendar triggers ("weekend", "WFH") are correlated with boredom-driven overtrading, not with edge. The market-state gate above breaks that correlation by structurally refusing high-freq when conditions don't support it, regardless of how much free time the human has.

The system also tracks `mode_session_hours_per_week` in `wiki/log.md`. If it climbs above 8h/week, the next daily output appends a warning. Time is the most-spent resource in trading; the system should be honest about how it's being spent.
