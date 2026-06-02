"""Offline tests for the RAG example library (rag_library.py + rag_retrieve.py).

Covers the three PIT-honesty guarantees documented in
`data/recommendations_lake/README.md`:

  1. as_of_timestamp immutability after first write.
  2. Embedding derived from prompt_snapshot only — never from outcome.
  3. retrieve(before_as_of=T) honours the temporal filter.

Plus embedding determinism (same input → same vector across runs / machines)
and the cosine ordering correctness needed for the schema to be useful.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from sharks.ai.rag_library import (
    EMBEDDING_DIM,
    EMBEDDING_METHOD,
    embed,
    prompt_text_from_snapshot,
    update_outcome,
    write_recommendation,
)
from sharks.ai.rag_retrieve import (
    load_all,
    retrieve,
)


# ---------------------------------------------------------------------------
# Embedding determinism + math invariants
# ---------------------------------------------------------------------------

class TestEmbedding:
    def test_dim_is_constant(self):
        assert len(embed("hello world")) == EMBEDDING_DIM

    def test_deterministic_across_calls(self):
        v1 = embed("late_bull MU mom 82 bub -95")
        v2 = embed("late_bull MU mom 82 bub -95")
        assert v1 == v2

    def test_empty_text_returns_zero_vector(self):
        v = embed("")
        assert v == [0.0] * EMBEDDING_DIM

    def test_l2_normalised_for_nonempty(self):
        v = embed("foo bar baz quux")
        norm = math.sqrt(sum(x * x for x in v))
        assert math.isclose(norm, 1.0, abs_tol=1e-9)

    def test_different_input_different_vector(self):
        v1 = embed("late_bull AMD")
        v2 = embed("risk_off META")
        assert v1 != v2


class TestPromptTextSnapshot:
    def test_orders_regime_breadth_liquidity_first(self):
        text = prompt_text_from_snapshot({
            "regime_label": "late_bull",
            "breadth_verdict": "OVERHEATED",
            "liquidity_level": "YELLOW",
        })
        assert text.startswith("regime late_bull | breadth OVERHEATED | liquidity YELLOW")

    def test_includes_top_fom_entries(self):
        text = prompt_text_from_snapshot({
            "regime_label": "late_bull",
            "top_n_fom": [{"ticker": "ARM", "fom": 61.6, "momentum": 83.4}],
        })
        assert "top ARM fom 61.6 mom 83.4" in text

    def test_includes_wiki_citations(self):
        text = prompt_text_from_snapshot({
            "regime_label": "neutral",
            "wiki_citations": ["wiki/02_mag7_bottleneck"],
        })
        assert "cite wiki/02_mag7_bottleneck" in text

    def test_empty_snapshot_returns_empty(self):
        assert prompt_text_from_snapshot({}) == ""


# ---------------------------------------------------------------------------
# Write contract — schema + immutability of as_of
# ---------------------------------------------------------------------------

@pytest.fixture
def lake(tmp_path: Path) -> Path:
    return tmp_path / "lake"


def _snapshot(regime: str = "late_bull", ticker_top: str = "ARM") -> dict:
    return {
        "regime_label": regime,
        "breadth_verdict": "OVERHEATED",
        "liquidity_level": "YELLOW",
        "top_n_fom": [{"ticker": ticker_top, "fom": 61.6, "momentum": 83.4}],
        "wiki_citations": ["wiki/02_mag7_bottleneck#supply-chain"],
        "prompt_text": f"thesis for {ticker_top} under {regime}",
    }


def _recommendation(verdict: str = "ADD") -> dict:
    return {
        "verdict": verdict,
        "position_size_pct": 2.0,
        "invalidation_triggers": {
            "price_floor": 80.0,
            "time_stop_days": 60,
            "catalyst_failure": "Q2 ramp delay",
        },
    }


class TestWriteRecommendation:
    def test_creates_file_with_canonical_name(self, lake: Path):
        path = write_recommendation(
            lake, slot_id="01", ticker="MU",
            as_of_timestamp="2026-05-30T01:10:00-04:00",
            prompt_snapshot=_snapshot(),
            recommendation=_recommendation(),
        )
        assert path.name == "2026-05-30-01-MU.json"
        assert path.exists()

    def test_writes_complete_schema(self, lake: Path):
        path = write_recommendation(
            lake, slot_id="01", ticker="mu",  # lowercase ticker → uppercased
            as_of_timestamp="2026-05-30T01:10:00-04:00",
            prompt_snapshot=_snapshot(),
            recommendation=_recommendation(),
        )
        record = json.loads(path.read_text(encoding="utf-8"))
        assert record["schema_version"] == 1
        assert record["ticker"] == "MU"
        assert record["as_of_timestamp"] == "2026-05-30T01:10:00-04:00"
        assert record["embedding"]["method"] == EMBEDDING_METHOD
        assert len(record["embedding"]["vector"]) == EMBEDDING_DIM
        assert record["outcome"] == {
            "return_30d": None, "return_60d": None,
            "return_90d": None, "populated_at": None,
        }

    def test_embedding_is_function_of_snapshot_text_only(self, lake: Path):
        """Critical PIT guarantee: outcome cannot influence embedding."""
        snap = _snapshot()
        path = write_recommendation(
            lake, slot_id="01", ticker="MU",
            as_of_timestamp="2026-05-30T01:10:00-04:00",
            prompt_snapshot=snap, recommendation=_recommendation(),
        )
        record = json.loads(path.read_text(encoding="utf-8"))
        vector_before = record["embedding"]["vector"]
        # Direct re-compute from the canonical text.
        expected = embed(prompt_text_from_snapshot(snap))
        assert vector_before == expected

    def test_as_of_immutable_on_rewrite(self, lake: Path):
        """Filename is date-prefixed (`YYYY-MM-DD-<slot>-<TICKER>.json`), so two
        writes on the same calendar date but different times-of-day collide on
        the same filename and the function must refuse the second write."""
        write_recommendation(
            lake, slot_id="01", ticker="MU",
            as_of_timestamp="2026-05-30T01:10:00-04:00",
            prompt_snapshot=_snapshot(), recommendation=_recommendation(),
        )
        # Same date → same filename; different time-of-day → different as_of
        # in the record body. This is the silent-corruption case the check guards.
        with pytest.raises(ValueError, match="immutable"):
            write_recommendation(
                lake, slot_id="01", ticker="MU",
                as_of_timestamp="2026-05-30T15:30:00-04:00",  # same date, later
                prompt_snapshot=_snapshot(), recommendation=_recommendation(),
            )

    def test_different_dates_create_different_files(self, lake: Path):
        """Two writes for the same slot+ticker on different dates are NOT a
        rewrite — they produce two independent files (per the date-prefix
        filename convention)."""
        p1 = write_recommendation(
            lake, slot_id="01", ticker="MU",
            as_of_timestamp="2026-05-30T01:10:00-04:00",
            prompt_snapshot=_snapshot(), recommendation=_recommendation(),
        )
        p2 = write_recommendation(
            lake, slot_id="01", ticker="MU",
            as_of_timestamp="2026-06-01T01:10:00-04:00",
            prompt_snapshot=_snapshot(), recommendation=_recommendation(),
        )
        assert p1 != p2
        assert p1.exists() and p2.exists()

    def test_idempotent_on_same_as_of(self, lake: Path):
        """Writing twice with the same as_of is fine — does not raise."""
        write_recommendation(
            lake, slot_id="01", ticker="MU",
            as_of_timestamp="2026-05-30T01:10:00-04:00",
            prompt_snapshot=_snapshot(), recommendation=_recommendation(),
        )
        # No exception:
        write_recommendation(
            lake, slot_id="01", ticker="MU",
            as_of_timestamp="2026-05-30T01:10:00-04:00",
            prompt_snapshot=_snapshot(), recommendation=_recommendation(verdict="HOLD"),
        )


class TestUpdateOutcome:
    def test_populates_outcome_only(self, lake: Path):
        path = write_recommendation(
            lake, slot_id="01", ticker="MU",
            as_of_timestamp="2026-05-30T01:10:00-04:00",
            prompt_snapshot=_snapshot(), recommendation=_recommendation(),
        )
        before = json.loads(path.read_text(encoding="utf-8"))
        update_outcome(
            path, return_30d=0.12, return_60d=0.18,
            populated_at="2026-08-30T00:00:00Z",
        )
        after = json.loads(path.read_text(encoding="utf-8"))

        # Outcome populated:
        assert after["outcome"]["return_30d"] == 0.12
        assert after["outcome"]["return_60d"] == 0.18
        assert after["outcome"]["return_90d"] is None
        assert after["outcome"]["populated_at"] == "2026-08-30T00:00:00Z"

        # PIT-critical: embedding bit-identical before/after.
        assert before["embedding"] == after["embedding"]
        # As-of untouched:
        assert before["as_of_timestamp"] == after["as_of_timestamp"]
        # Prompt snapshot untouched:
        assert before["prompt_snapshot"] == after["prompt_snapshot"]


# ---------------------------------------------------------------------------
# Retrieval — PIT filter, ordering, embedding-method gating
# ---------------------------------------------------------------------------

class TestRetrieve:
    def _seed_three(self, lake: Path) -> None:
        # Three records spread across dates + regimes.
        write_recommendation(
            lake, slot_id="01", ticker="MU",
            as_of_timestamp="2026-05-30T01:10:00-04:00",
            prompt_snapshot=_snapshot("late_bull", "ARM"),
            recommendation=_recommendation(),
        )
        write_recommendation(
            lake, slot_id="01", ticker="AMD",
            as_of_timestamp="2026-06-15T01:10:00-04:00",
            prompt_snapshot=_snapshot("late_bull", "AMD"),
            recommendation=_recommendation(),
        )
        write_recommendation(
            lake, slot_id="03", ticker="META",
            as_of_timestamp="2026-07-01T01:10:00-04:00",
            prompt_snapshot=_snapshot("risk_off", "META"),
            recommendation=_recommendation("TRIM"),
        )

    def test_load_all_unfiltered(self, lake: Path):
        self._seed_three(lake)
        records = load_all(lake)
        assert len(records) == 3

    def test_load_all_pit_filter(self, lake: Path):
        self._seed_three(lake)
        records = load_all(lake, before_as_of="2026-06-16T00:00:00-04:00")
        # Excludes the 2026-07-01 META record:
        tickers = {r["ticker"] for r in records}
        assert tickers == {"MU", "AMD"}

    def test_retrieve_orders_by_cosine_descending(self, lake: Path):
        self._seed_three(lake)
        # Query that looks like the late_bull regime → late_bull records score
        # higher than the risk_off META record.
        out = retrieve(
            lake,
            current_prompt_snapshot=_snapshot("late_bull", "ARM"),
            k=3,
        )
        assert out["records_scanned"] == 3
        results = out["results"]
        assert len(results) == 3
        # Sorted descending:
        scores = [r["score"] for r in results]
        assert scores == sorted(scores, reverse=True)
        # First hit should be a late_bull record, not the risk_off META one.
        top_ticker = results[0]["record"]["ticker"]
        assert top_ticker in {"MU", "AMD"}

    def test_retrieve_respects_before_as_of(self, lake: Path):
        self._seed_three(lake)
        out = retrieve(
            lake,
            current_prompt_snapshot=_snapshot("late_bull", "ARM"),
            k=5,
            before_as_of="2026-06-01T00:00:00-04:00",
        )
        # Only the 2026-05-30 MU record qualifies.
        assert out["records_scanned"] == 1
        assert len(out["results"]) == 1
        assert out["results"][0]["record"]["ticker"] == "MU"

    def test_retrieve_skips_wrong_embedding_method(self, lake: Path):
        self._seed_three(lake)
        # Manually corrupt one record's embedding method to simulate an
        # in-progress re-embedding migration.
        path = lake / "2026-06-15-01-AMD.json"
        record = json.loads(path.read_text(encoding="utf-8"))
        record["embedding"]["method"] = "bge-small-en-future-v2"
        path.write_text(json.dumps(record, indent=2), encoding="utf-8")

        out = retrieve(
            lake,
            current_prompt_snapshot=_snapshot("late_bull", "ARM"),
            k=5,
        )
        assert out["records_scanned"] == 3
        assert out["records_skipped_wrong_method"] == 1
        tickers = {r["record"]["ticker"] for r in out["results"]}
        assert "AMD" not in tickers  # the version-mismatched record was skipped

    def test_retrieve_on_empty_lake_is_safe(self, tmp_path: Path):
        out = retrieve(
            tmp_path / "nonexistent_lake",
            current_prompt_snapshot=_snapshot(),
            k=3,
        )
        assert out["records_scanned"] == 0
        assert out["results"] == []
