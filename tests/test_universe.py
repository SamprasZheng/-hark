"""Tests for the extended universe + OTC handling + buy-warnings."""

from __future__ import annotations

from sharks.scoring.universe import (
    EXTENDED_TICKERS,
    OTC_WATCH,
    is_otc,
    buy_warning,
    full_universe,
)
from sharks.scoring.fom import DEFAULT_UNIVERSE


class TestFullUniverse:
    def test_extended_is_large(self):
        u = full_universe(include_extended=True, include_otc=False)
        assert len(u) >= 300            # meaningfully wider than DEFAULT
        assert set(DEFAULT_UNIVERSE).issubset(set(u))

    def test_default_only_smaller(self):
        small = full_universe(include_extended=False, include_otc=False, include_extra=False)
        big = full_universe(include_extended=True, include_otc=False, include_extra=False)
        assert len(big) > len(small)

    def test_otc_off_by_default(self):
        u = full_universe(include_otc=False, include_extra=False)
        assert not (set(OTC_WATCH) & set(u))

    def test_otc_on_includes_them(self):
        u = full_universe(include_otc=True, include_extra=False)
        assert "TCEHY" in u

    def test_deduped_sorted(self):
        u = full_universe()
        assert u == sorted(set(u))


class TestOTC:
    def test_explicit_otc(self):
        assert is_otc("TCEHY")

    def test_adr_pink_pattern(self):
        assert is_otc("ABCDY")          # 5-letter …Y not on primary
        assert is_otc("WXYZF")

    def test_primary_not_otc(self):
        assert not is_otc("AAPL")
        assert not is_otc("NVDA")


class TestBuyWarning:
    def test_otc_warns(self):
        w = buy_warning("TCEHY")
        assert w and "OTC" in w

    def test_leveraged_long_warns(self):
        w = buy_warning("TQQQ")
        assert w and ("槓桿" in w or "decay" in w)

    def test_inverse_warns(self):
        w = buy_warning("SQQQ")
        assert w and "反向" in w

    def test_vix_warns(self):
        w = buy_warning("UVXY")
        assert w and "VIX" in w

    def test_clean_name_no_warning(self):
        assert buy_warning("AAPL") is None
        assert buy_warning("RSG") is None


class TestExtendedList:
    def test_uppercase_and_nonempty(self):
        assert len(EXTENDED_TICKERS) > 150
        assert all(t == t.upper() for t in EXTENDED_TICKERS)
