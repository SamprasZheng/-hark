"""Tests for the lead-lag / transmission detector (pure logic, synthetic data)."""

from __future__ import annotations

import numpy as np
import pandas as pd

from sharks.regime.lead_lag import (
    best_lag,
    lead_lag_score,
    net_transmitter_rank,
    to_returns,
    transmission_candidates,
)


def _frame(n=240, seed=0):
    """A leads B (B_t ≈ 0.8*A_{t-1}); C is independent; D already moved (drift)."""
    rng = np.random.default_rng(seed)
    a = rng.normal(0, 0.02, n)
    b = np.empty(n)
    b[0] = rng.normal(0, 0.02)
    for t in range(1, n):
        b[t] = 0.8 * a[t - 1] + rng.normal(0, 0.005)   # B follows A with lag 1
    c = rng.normal(0, 0.02, n)                          # independent
    d = rng.normal(0, 0.02, n) + 0.01                   # positive drift (already moved)
    idx = pd.date_range("2020-01-31", periods=n, freq="ME")
    return pd.DataFrame({"A": a, "B": b, "C": c, "D": d}, index=idx)


class TestToReturns:
    def test_shape(self):
        closes = pd.DataFrame({"X": [100, 101, 102, 103]})
        r = to_returns(closes)
        assert len(r) == 3


class TestLeadLagScore:
    def test_leader_leads_follower(self):
        r = _frame()
        s = lead_lag_score(r, "A", "B")
        assert s["net"] > 0           # A leads B
        assert s["lead_r2"] > s["reverse_r2"]

    def test_reverse_is_not_leading(self):
        r = _frame()
        s = lead_lag_score(r, "B", "A")
        assert s["net"] <= 0          # B does not lead A

    def test_independent_pair_near_zero(self):
        r = _frame()
        s = lead_lag_score(r, "A", "C")
        assert abs(s["net"]) < 0.15   # A does not lead independent C much

    def test_best_lag_is_one(self):
        r = _frame()
        assert best_lag(r, "A", "B", max_lag=6) == 1

    def test_self_pair_guarded(self):
        r = _frame()
        s = lead_lag_score(r, "A", "A")
        assert s["net"] == 0.0

    def test_insufficient_data(self):
        r = to_returns(pd.DataFrame({"A": [1, 2, 3], "B": [1, 2, 3]}))
        s = lead_lag_score(r, "A", "B")
        assert s["net"] == 0.0


class TestNetTransmitter:
    def test_A_is_top_transmitter(self):
        r = _frame()
        rank = net_transmitter_rank(r, ["A", "B", "C", "D"])
        assert rank[0]["ticker"] == "A"
        assert rank[0]["role"] == "transmitter"

    def test_B_is_receiver(self):
        r = _frame()
        rank = net_transmitter_rank(r, ["A", "B", "C", "D"])
        b = next(x for x in rank if x["ticker"] == "B")
        assert b["net"] < 0           # B receives (A leads it)


class TestTransmissionCandidates:
    def test_downstream_not_moved_ranks_first(self):
        r = _frame()
        # B is downstream of A and has ~zero drift; D has drift (already moved)
        cands = transmission_candidates(r, "A", ["B", "C", "D"])
        assert cands[0]["follower"] == "B"

    def test_candidate_score_nonnegative(self):
        r = _frame()
        cands = transmission_candidates(r, "A", ["B", "C", "D"])
        assert all(c["candidate_score"] >= 0 for c in cands)

    def test_as_of_slices(self):
        r = _frame()
        mid = r.index[120]
        cands = transmission_candidates(r, "A", ["B", "C"], as_of=mid)
        assert len(cands) == 2
