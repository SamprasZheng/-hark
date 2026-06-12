"""Offline tests for the 季線/年線 big-swing screen (scoring/bigswing.py).

Synthetic monthly-close series (a flat base then a final up-leg) are constructed
so a fast/slow SMA golden cross lands exactly on the last resampled bar. Pure; no
network (fetch is injected).
"""

from __future__ import annotations

from sharks.scoring import bigswing as bs


def _monthly_from(resampled: list[float], bucket: int) -> list[float]:
    """Expand a target resampled series to monthly by repeating each value `bucket`x,
    so resample(monthly, bucket, 'last') reproduces it exactly."""
    out = []
    for v in resampled:
        out.extend([v] * bucket)
    return out


class TestPureHelpers:
    def test_resample_last(self):
        assert bs.resample([1, 2, 3, 4, 5, 6], 3) == [3, 6]

    def test_resample_sum(self):
        assert bs.resample([1, 2, 3, 4], 2, agg="sum") == [3.0, 7.0]

    def test_sma_none_until_window(self):
        out = bs.sma([2, 4, 6], 2)
        assert out[0] is None
        assert out[1] == 3.0
        assert out[2] == 5.0


class TestAssessQuarterly:
    def test_golden_cross_on_last_bar(self):
        q = [50.0] * 15 + [200.0]            # 16 quarterly bars; final up-leg
        monthly = _monthly_from(q, 3)         # 48 monthly bars
        c = bs.assess("TEST", monthly, "quarterly")
        assert c.bars == 16
        assert c.golden_cross is True
        assert c.above_slow is True
        assert c.rising is True
        assert c.verdict.startswith("🟢")
        assert c.score >= 70

    def test_below_long_ma_is_bearish_base(self):
        q = [100.0, 96, 92, 88, 84, 80, 76, 72, 68, 64, 60, 56, 52, 48, 44, 40]  # strict decline
        c = bs.assess("DOWN", _monthly_from(q, 3), "quarterly")
        assert c.above_slow is False                        # last < declining long MA
        assert c.golden_cross is False
        assert c.verdict.startswith("🔻") or c.verdict.startswith("⚠️")

    def test_insufficient_history(self):
        c = bs.assess("SHORT", [10.0] * 12, "quarterly")  # 4 quarterly bars < 16
        assert c.verdict == "資料不足"


class TestAssessYearly:
    def test_yearly_golden_cross(self):
        y = [50.0] * 6 + [200.0]              # 7 yearly bars
        monthly = _monthly_from(y, 12)        # 84 monthly bars
        c = bs.assess("TEST", monthly, "yearly")
        assert c.bars == 7
        assert c.golden_cross is True
        assert c.above_slow is True
        assert c.verdict.startswith("🟢")


class TestScreen:
    def test_ranks_golden_cross_above_laggard(self):
        winner = _monthly_from([50.0] * 15 + [200.0], 3)
        laggard = _monthly_from([100.0, 95, 90, 85, 80, 70, 60, 55, 50, 48, 47, 46, 45, 44, 43, 42], 3)

        def fetch(tickers):
            return {"WIN": winner, "LAG": laggard}

        out = bs.screen_bigswing(["WIN", "LAG"], fetch=fetch, timeframe="quarterly")
        assert out[0].ticker == "WIN"
        assert out[0].score > out[1].score

    def test_bad_timeframe_raises(self):
        import pytest
        with pytest.raises(ValueError):
            bs.screen_bigswing(["X"], fetch=lambda t: {}, timeframe="weekly")


class TestRun:
    def test_run_writes_artifact(self, tmp_path):
        winner = _monthly_from([50.0] * 15 + [200.0], 3)
        rep = bs.run(["WIN"], timeframe="quarterly", out_dir=tmp_path,
                     fetch=lambda t: {"WIN": winner})
        assert rep["report_type"] == "bigswing"
        assert rep["timeframe"] == "quarterly"
        assert rep["ranked"][0]["ticker"] == "WIN"
        assert list(tmp_path.glob("bigswing-quarterly-*.json"))
