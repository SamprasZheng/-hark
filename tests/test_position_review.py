"""Tests for the hold/rotate feedback loop (decision/position_review).

All pure + offline. Validates the central contract the owner asked for:
  * a strong-trending winner with intact support is HELD, not rotated;
  * a real reversal (rollover / breakdown) still SELLs;
  * leverage discipline is preserved (trailing/staged), never silently removed;
  * the performance gate widens the hold band when the sleeve is strong.
"""

from __future__ import annotations

from sharks.decision.position_review import (
    classify_trend, sleeve_performance, review_position,
    STRONG, INTACT, ROLLOVER, BROKEN,
    V_HOLD_TRAIL, V_TRIM_TRAIL, V_SELL, V_TRIM,
)


class TestClassifyTrend:
    def test_strong_uptrend(self):
        assert classify_trend(75, 10, 0.12) == STRONG

    def test_moderate_dip_on_strong_mom_is_intact_not_winner(self):
        # high momentum but a -15% dip (not past the -20% broken line): NOT a clean
        # winner-hold, but NOT a forced sell either -> intact (softens SELL to TRIM).
        assert classify_trend(75, 10, -0.15) == INTACT

    def test_rollover_on_fading_mom_plus_drawdown(self):
        assert classify_trend(50, 0, -0.11) == ROLLOVER

    def test_broken_on_deep_drawdown(self):
        assert classify_trend(80, 0, -0.25) == BROKEN

    def test_overheated_bubble_is_rollover(self):
        assert classify_trend(70, -60, None) == ROLLOVER

    def test_overheated_and_falling_is_broken(self):
        assert classify_trend(70, -60, -0.05) == BROKEN

    def test_neutral_is_intact(self):
        assert classify_trend(50, 0, 0.01) == INTACT

    def test_recent_runup_holds_even_with_low_mom_score(self):
        # owner choice 2026-06-01: a clear recent up-run (+33%) is a winner-to-hold
        # even when the lagging FOM momentum score (28) is weak.
        assert classify_trend(28, 0, 0.33) == STRONG

    def test_runup_but_breaking_down_is_not_strong(self):
        # a big run that just cratered past the broken line is NOT a hold
        assert classify_trend(28, 0, -0.25) == BROKEN

    def test_missing_momentum_degrades_to_intact(self):
        assert classify_trend(None, None, None) == INTACT


class TestSleevePerformance:
    def test_strong(self):
        assert sleeve_performance([60, 58, 70, 55]) == "strong"

    def test_weak(self):
        assert sleeve_performance([38, 40, 35, 30]) == "weak"

    def test_normal(self):
        assert sleeve_performance([48, 50, 45]) == "normal"

    def test_empty_is_normal(self):
        assert sleeve_performance([]) == "normal"


class TestCashEquityReversalGate:
    def test_winner_with_sell_base_is_held(self):
        # the heart of the ask: a ripping software winner the base logic wanted to cut
        r = review_position(
            ticker="CRM", base_verdict="SELL-or-TRIM-50%", category="cash_equity",
            fom_breakdown={"momentum": 72, "bubble_guard": 5, "final_fom": 58},
            recent_return=0.11,
        )
        assert r.reviewed_verdict == V_HOLD_TRAIL
        assert r.changed is True
        assert r.trailing_stop_pct is not None
        assert r.trend == STRONG
        assert "trailing" in " ".join(r.notes).lower() or r.trailing_stop_pct > 0

    def test_real_reversal_still_sells(self):
        r = review_position(
            ticker="DDD", base_verdict="SELL", category="cash_equity",
            fom_breakdown={"momentum": 35, "bubble_guard": -10, "final_fom": 30},
            recent_return=-0.22,
        )
        assert r.reviewed_verdict == V_SELL
        assert r.trend == BROKEN
        assert r.changed is False

    def test_intact_softens_hard_sell_to_trim(self):
        r = review_position(
            ticker="VFC", base_verdict="SELL-or-TRIM-50%", category="cash_equity",
            fom_breakdown={"momentum": 50, "bubble_guard": 0, "final_fom": 42},
            recent_return=0.0,
        )
        assert r.reviewed_verdict == V_TRIM
        assert r.changed is True

    def test_non_exit_base_passes_through(self):
        r = review_position(
            ticker="MSFT", base_verdict="HOLD-or-ADD", category="cash_equity",
            fom_breakdown={"momentum": 65, "bubble_guard": 10, "final_fom": 60},
            recent_return=0.05,
        )
        assert r.reviewed_verdict == "HOLD-or-ADD"
        assert r.changed is False
        # evidence still attached
        assert r.support["final_fom"] == 60


class TestLeveragePolicy:
    def test_leveraged_winner_trails_not_dumps(self):
        # NOWL = 2x NOW; the underlying NOW is ripping -> de-risk a slice + trail the rest
        r = review_position(
            ticker="NOWL", base_verdict="SELL", category="leveraged_etf",
            leveraged_of="NOW", trend_momentum=70, trend_bubble=5, recent_return=0.18,
            leveraged_exit_mode="trailing",
        )
        assert r.reviewed_verdict == V_TRIM_TRAIL
        assert r.changed is True
        assert r.trailing_stop_pct is not None
        assert "decay" not in r.why  # not the panic-dump rationale

    def test_leveraged_immediate_mode_dumps(self):
        r = review_position(
            ticker="NOWL", base_verdict="SELL", category="leveraged_etf",
            leveraged_of="NOW", trend_momentum=70, trend_bubble=5, recent_return=0.18,
            leveraged_exit_mode="immediate",
        )
        assert r.reviewed_verdict == V_SELL

    def test_leveraged_rolling_over_dumps_even_in_trailing(self):
        r = review_position(
            ticker="LABU", base_verdict="SELL", category="leveraged_etf",
            leveraged_of="XBI", trend_momentum=30, trend_bubble=-20, recent_return=-0.15,
            leveraged_exit_mode="trailing",
        )
        assert r.reviewed_verdict == V_SELL


class TestPerformanceGate:
    def test_strong_sleeve_holds_borderline_winner(self):
        # momentum 52 is below the 60 default, but a strong sleeve relaxes it to 50
        kw = dict(
            ticker="WDAY", base_verdict="TRIM-30%", category="cash_equity",
            fom_breakdown={"momentum": 52, "bubble_guard": 5, "final_fom": 50},
            recent_return=0.04,
        )
        strong = review_position(perf_gate="strong", **kw)
        normal = review_position(perf_gate="normal", **kw)
        assert strong.reviewed_verdict == V_HOLD_TRAIL   # held under a strong sleeve
        assert normal.reviewed_verdict != V_HOLD_TRAIL    # not held at normal
