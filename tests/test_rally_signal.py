"""Offline tests for the 起漲訊號 fusion + 連續起漲 persistence tracker."""

from __future__ import annotations

from sharks.scoring import rally_signal as R


def test_composite_skips_missing_dims_and_renormalises():
    # only technical given → composite == that value (weights renormalise)
    assert R.composite_score({"technical": 80}) == 80.0
    c = R.composite_score({"technical": 80, "capital": 40})
    assert 40 < c < 80                       # weighted between the two


def test_update_streak_counts_and_resets():
    assert R.update_streak(0, True) == 1
    assert R.update_streak(2, True) == 3
    assert R.update_streak(5, False) == 0    # one stall resets


def test_consecutive_rally_with_catalyst_triggers_buy_consideration():
    dims = {"technical": 75, "capital": 70, "fundamental": 65,
            "supply_chain": 80, "news": 60}
    s = R.assess("NVDA", dims, prior_streak=2, evidence_confirmed=True)
    assert s.is_rallying and s.streak == 3
    assert s.buy_consider and "可考慮買入" in s.conviction
    assert s.dna_match > 60


def test_single_green_bar_is_not_a_buy():
    dims = {"technical": 70, "capital": 60, "fundamental": 60, "supply_chain": 55}
    s = R.assess("SNOW", dims, prior_streak=0)
    assert s.is_rallying and s.streak == 1
    assert not s.buy_consider and "起漲中" in s.conviction   # needs persistence


def test_tight_regime_no_fuel_is_downgraded_to_bounce_not_wave():
    # 有點動(蓄勢/起漲)但無真盈利/真題材、技術不過熱(非墓園)→ 缺燃料降級
    dims = {"technical": 64, "capital": 60, "fundamental": 35, "supply_chain": 35, "news": 30}
    s = R.assess("BOUNCE", dims, prior_streak=5, tight_regime=True)
    assert not s.buy_consider and not s.has_fuel and not s.wave_candidate
    assert "缺燃料" in s.conviction and s.warning


def test_fuel_present_allows_wave_buy_in_tight_regime():
    dims = {"technical": 70, "capital": 65, "fundamental": 75, "supply_chain": 50}
    s = R.assess("REAL", dims, prior_streak=3, tight_regime=True)
    assert s.has_fuel and s.wave_candidate and s.buy_consider


def test_loose_regime_relaxes_fuel_requirement():
    # 同樣無強燃料(只有 catalyst 50 級),loose 下不被降級為缺燃料
    dims = {"technical": 60, "capital": 55, "fundamental": 50}
    tight = R.assess("X", dims, prior_streak=5, tight_regime=True)
    loose = R.assess("X", dims, prior_streak=5, tight_regime=False)
    assert "缺燃料" in tight.conviction          # fundamental 50 < 55 fuel bar
    assert "缺燃料" not in loose.conviction       # loose 只要 catalyst(>=50)


def test_pure_hype_no_catalyst_is_graveyard_warned():
    dims = {"technical": 90, "capital": 85, "fundamental": 20,
            "supply_chain": 30, "news": 10}
    s = R.assess("PUMP", dims, prior_streak=9)
    assert not s.buy_consider                 # never buy a graveyard
    assert "墓園" in s.conviction and s.warning
    assert s.dna_match < 70                    # DNA penalised for no catalyst


def test_dims_from_basecross_mapping():
    class C:
        ticker = "AVGO"; rising = True; golden_cross = True
        bottom_zone = True; vol_surge = 2.0
    dims = R.dims_from_basecross(C(), fom_quality=72.0)
    assert dims["technical"] == 100.0         # rising + bottom golden cross
    assert dims["capital"] and dims["capital"] > 70    # ×2 volume surge
    assert dims["supply_chain"] == 80.0       # AVGO is a supply-chain tag
    assert dims["fundamental"] == 72.0
    assert dims["news"] is None               # honestly TBD


def test_persistence_round_trip(tmp_path):
    s = R.assess("ABC", {"technical": 70, "capital": 60, "fundamental": 60}, prior_streak=4)
    R.write_state(tmp_path, [s], as_of="2026-06-08")
    prior = R.load_prior_streaks(tmp_path, before="2026-06-09")
    assert prior["ABC"] == s.streak == 5
    # same-day file is NOT counted as "prior"
    assert R.load_prior_streaks(tmp_path, before="2026-06-08") == {}


def test_build_signals_from_basecross_candidates():
    class C:
        def __init__(self, t, rising, gc, vs):
            self.ticker, self.rising, self.golden_cross = t, rising, gc
            self.bottom_zone, self.vol_surge = gc, vs
    cands = [C("AVGO", True, True, 2.2), C("ZZZ", False, False, None)]
    sigs = R.build_signals(cands, quality_by_ticker={"AVGO": 70.0},
                           prior_streaks={"AVGO": 2})
    by = {s.ticker: s for s in sigs}
    assert by["AVGO"].streak == 3 and by["AVGO"].buy_consider
    assert by["ZZZ"].dims["capital"] is None and not by["ZZZ"].buy_consider


def test_quality_prior_fills_when_fom_missing_and_fom_overrides():
    class C:
        def __init__(self, t):
            self.ticker, self.rising, self.golden_cross = t, True, False
            self.bottom_zone, self.vol_surge = False, 1.5
    # JMIA not in FOM scan → conservative prior (28) fills 基本面
    [jmia] = R.build_signals([C("JMIA")])
    assert jmia.dims["fundamental"] == R.QUALITY_PRIORS["JMIA"] == 28
    # RVLV with a real FOM quality → FOM wins over the prior
    [rvlv] = R.build_signals([C("RVLV")], quality_by_ticker={"RVLV": 75.0})
    assert rvlv.dims["fundamental"] == 75.0


def test_build_signals_from_basecross_candidates_fallback_off():
    class C:
        def __init__(self, t):
            self.ticker, self.rising, self.golden_cross = t, False, False
            self.bottom_zone, self.vol_surge = False, None
    # explicit empty priors → 基本面 stays TBD
    [s] = R.build_signals([C("JMIA")], quality_priors={})
    assert s.dims["fundamental"] is None


def test_provisional_rank_blends_priors_and_folds_in_live_momentum():
    names = ["VIPS", "JMIA", "SHOP"]
    ranked = R.provisional_rank(names)
    assert {r["ticker"] for r in ranked} == set(names)
    assert all(r["momentum_pending"] for r in ranked)        # no live 動能 → TBD
    # VIPS (high 基本面 + high 獲利空間) outranks SHOP (lower 獲利空間)
    order = [r["ticker"] for r in ranked]
    assert order.index("VIPS") < order.index("SHOP")
    # folding in a hot momentum re-weights and clears the pending flag
    live = R.provisional_rank(names, momentum_by_ticker={"SHOP": 95})
    shop = next(r for r in live if r["ticker"] == "SHOP")
    assert not shop["momentum_pending"] and shop["momentum"] == 95


def test_ecommerce_rank_folds_live_momentum_and_fom():
    class C:
        def __init__(self, t, rising, gc, vs):
            self.ticker, self.rising, self.golden_cross = t, rising, gc
            self.bottom_zone, self.vol_surge = gc, vs
    cands = [C("JMIA", True, True, 3.0),      # hot 動能 but weak 基本面 prior (28)
             C("VIPS", False, False, None)]   # strong priors, cold 動能
    ranked = R.ecommerce_rank(cands, quality_by_ticker={"VIPS": 75.0})
    by = {r["ticker"]: r for r in ranked}
    assert not by["JMIA"]["momentum_pending"]       # live 動能 folded in
    assert by["JMIA"]["momentum"] > 80               # rising + bottom cross + ×3 vol
    assert by["VIPS"]["fundamental"] == 75.0         # FOM overrode the prior


def test_rank_orders_buy_considers_first():
    items = [
        {"ticker": "LOW", "dims": {"technical": 30, "capital": 20}},
        {"ticker": "BUY", "dims": {"technical": 75, "capital": 70, "supply_chain": 80,
                                   "fundamental": 65}, "prior_streak": 3},
    ]
    ranked = R.rank(items)
    assert ranked[0].ticker == "BUY" and ranked[0].buy_consider
