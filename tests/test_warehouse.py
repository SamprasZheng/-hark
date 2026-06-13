"""Offline tests for the warehouse monthly-pattern functions (no yfinance/duckdb/pandas)."""

from __future__ import annotations

from sharks.data import warehouse as W


def _daily(monthly, per=21):
    """Expand monthly closes → daily (dates + closes) so monthly_closes recovers them."""
    dates, closes = [], []
    for mi, mc in enumerate(monthly):
        y, m = 2024 + mi // 12, mi % 12 + 1
        for d in range(per):
            dates.append(f"{y:04d}-{m:02d}-{d+1:02d}")
            closes.append(mc)
    return dates, closes


def test_monthly_closes_resamples_last_per_month():
    dates = ["2026-01-05", "2026-01-20", "2026-02-03", "2026-03-10"]
    closes = [10, 12, 14, 16]
    assert W.monthly_closes(dates, closes) == [12, 14, 16]   # last of Jan, Feb, Mar


def test_consecutive_green_months():
    assert W.consecutive_green_months([10, 11, 12, 13]) == 3   # 3 up-moves
    assert W.consecutive_green_months([10, 12, 11, 13]) == 1   # last up only
    assert W.consecutive_green_months([13, 12, 11]) == 0       # falling


def test_dist_ath_pct():
    assert W.dist_ath_pct([100, 80, 50]) == 50.0               # 50% below the 100 ATH
    assert W.dist_ath_pct([10, 20, 20]) == 0.0                 # at high


def test_golden_cross_flat_then_rise():
    # long flat base, then a recent sharp rise → 50SMA crosses above 200SMA within lookback
    closes = [50.0] * 240 + [50 + 2 * i for i in range(1, 41)]
    assert W.golden_cross(closes) is True
    # monotonic rise the whole time → 50>200 always, never "just crossed"
    assert W.golden_cross([float(i) for i in range(1, 400)]) is False


def test_classify_pre_ignition_deep_base_just_crossed():
    # 200→60 decline, long ~60 base (lets 200SMA settle low), then recovery to ~95 (<50% ATH)
    closes = [200 - i * (140 / 150) for i in range(150)]   # 200 → 60 (deep)
    closes += [60.0] * 120                                  # base, 200SMA settles near 60
    closes += [60 + i * (35 / 60) for i in range(1, 61)]   # recovery 60 → 95, crosses 50>200
    dates = [f"{2019 + i // 252:04d}-{i % 12 + 1:02d}-{i % 28 + 1:02d}" for i in range(len(closes))]
    r = W.classify(dates, closes)
    assert r["dist_ath_pct"] >= 50 and r["deep"] is True   # price < 50% ATH
    assert r["golden_cross"] is True
    assert r["stage"].startswith(("🌱", "🚀", "📈", "🌊"))   # a turning stage, not 整理


def test_classify_three_green_months():
    dates, closes = _daily([100, 90, 80, 85, 92, 99])      # last 3 monthly closes rising
    r = W.classify(dates, closes)
    assert r["green_months"] >= 3
    assert "三連陽" in r["stage"] or r["stage"].startswith("🌊")


def test_resolve_tickers_plain_list():
    assert W._resolve_tickers("NVDA,MU, AMD") == ["NVDA", "MU", "AMD"]
