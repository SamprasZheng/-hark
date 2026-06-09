"""Offline tests for the 隱蔽吸籌 (stealth accumulation) detector."""

from __future__ import annotations

from sharks.scoring import stealth_signal as ST


class C:
    def __init__(self, ticker, dist, vs, gc):
        self.ticker, self.dist_ath_pct, self.vol_surge = ticker, dist, vs
        self.golden_cross, self.bottom_zone = gc, gc


def test_money_in_price_flat_and_beaten_is_stealth():
    # 量×2.5 進場、距高 45% 深、月線還沒突破 = 隱蔽吸籌
    r = ST.stealth_score(C("X", 45, 2.5, False))
    assert r.stealth and r.verdict.startswith("🕵️")
    assert r.capital > 60 and not r.broke_out


def test_already_broken_out_is_not_stealth():
    # 同樣量能但月線已金叉突破 = 已表態,不隱蔽
    r = ST.stealth_score(C("X", 45, 2.5, True))
    assert not r.stealth and r.verdict.startswith("🟡") and r.broke_out


def test_no_volume_footprint_is_rejected():
    r = ST.stealth_score(C("X", 45, 1.0, False))   # 量×1 = 沒放大
    assert not r.stealth and "無明顯資金" in r.verdict


def test_near_high_is_not_accumulation():
    r = ST.stealth_score(C("X", 5, 3.0, False))    # 距高僅 5% = 近高
    assert not r.stealth and "近高" in r.verdict


def test_missing_volume_data():
    r = ST.stealth_score(C("X", 40, None, False))
    assert r.capital is None and "無量能資料" in r.verdict


def test_rank_puts_stealth_first():
    rows = ST.stealth_rank([
        C("OBVIOUS", 45, 2.5, True),     # broke out
        C("STEALTH", 45, 2.5, False),    # accumulating
        C("QUIET", 5, 1.0, False),       # nothing
    ])
    assert rows[0].ticker == "STEALTH" and rows[0].stealth


def test_low_attention_boosts_score():
    hi = ST.stealth_score(C("X", 45, 2.0, False), attention=90)
    lo = ST.stealth_score(C("X", 45, 2.0, False), attention=10)
    assert lo.score > hi.score        # 越少人看 → 越隱蔽 → 分數越高
