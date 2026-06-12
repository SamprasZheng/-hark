"""阿卡西案例庫測試 — 純 numpy 後端,離線、確定性(無網路、無 mock、無隨機)。"""

import json
import math
from pathlib import Path

import pytest

from sharks.memory.case_store import (
    MATCH_FEATS,
    CaseStore,
    _compute_norms,
    _latest_output,
)


def F(dd36=0.0, dist_ma10=0.0, buy9_max=0.0, r3m=0.0, vol_ratio=0.0):
    """5 維特徵 dict 簡寫(預設 0 — 未 sync 時恆等變換,cosine 可手算)。"""
    return {"dd36": dd36, "dist_ma10": dist_ma10, "buy9_max": buy9_max,
            "r3m": r3m, "vol_ratio": vol_ratio}


def make_store(tmp_path) -> CaseStore:
    return CaseStore(persist_dir=tmp_path / "akashic", backend="numpy")


def write_outputs(out_dir: Path, cases: list[dict], failed: list[dict],
                  rally_name="rally-dna-2026-06-12.json",
                  failed_name="failed-analogs-2026-06-12.json") -> Path:
    """合成 outputs/ 目錄(只含 sync 會讀的鍵)。"""
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / rally_name).write_text(json.dumps({
        "as_of": "2026-06-12",
        "case_library": {"cases": cases},
        "dna_match_today": {"top": []},
    }, ensure_ascii=False), encoding="utf-8")
    (out_dir / failed_name).write_text(json.dumps({
        "as_of": "2026-06-12",
        "failed_events": failed,
    }, ensure_ascii=False), encoding="utf-8")
    return out_dir


def case(ticker, trigger="2020-06-01", dd_min18=-0.7, gain=500.0,
         sector="Technology", **feats):
    return {"ticker": ticker, "trough": "2020-03-01", "trigger": trigger,
            "dd_min18": dd_min18, "gain_24m_pct": gain, "sector": sector,
            **F(**feats)}


def fail_event(ticker, trigger="2021-02-01", end_ret=-60.0, outcome="disaster",
               **feats):
    return {"ticker": ticker, "trigger": trigger, "end_ret_pct": end_ret,
            "outcome": outcome, **F(**feats)}


class TestAddQuery:
    def test_cosine_ordering(self, tmp_path):
        """未 sync(恆等變換)時 cosine 相似度與排序可手算驗證。"""
        store = make_store(tmp_path)
        store.add_case("AAA", F(dd36=2.0), {"trigger": "2020-01-01"}, True)
        store.add_case("BBB", F(dd36=1.0, dist_ma10=1.0), {"trigger": "2020-01-01"}, True)
        store.add_case("CCC", F(dd36=-1.0), {"trigger": "2020-01-01"}, True)
        res = store.query_similar(F(dd36=1.0), n=3)
        assert [r["ticker"] for r in res] == ["AAA", "BBB", "CCC"]
        assert res[0]["similarity"] == pytest.approx(1.0)               # 同向
        assert res[1]["similarity"] == pytest.approx(1 / math.sqrt(2), abs=1e-4)  # 45 度
        assert res[2]["similarity"] == pytest.approx(-1.0)              # 反向

    def test_where_filter_kind(self, tmp_path):
        store = make_store(tmp_path)
        store.add_case("WIN1", F(dd36=1.0), {"trigger": "2020-01-01"}, True)
        store.add_case("LOSE1", F(dd36=1.0, dist_ma10=0.1), {"trigger": "2021-01-01"}, False)
        store.add_case("LOSE2", F(dd36=0.9), {"trigger": "2021-02-01"}, False)
        res = store.query_similar(F(dd36=1.0), n=5, where={"kind": "fail"})
        assert len(res) == 2
        assert all(r["metadata"]["kind"] == "fail" for r in res)
        assert {r["ticker"] for r in res} == {"LOSE1", "LOSE2"}

    def test_where_filter_metadata(self, tmp_path):
        """任意 metadata 等值過濾(如 archetype)。"""
        store = make_store(tmp_path)
        store.add_case("DK", F(dd36=1.0),
                       {"trigger": "2020-01-01", "archetype": "deep_kill"}, True)
        store.add_case("SB", F(dd36=1.0),
                       {"trigger": "2020-01-01", "archetype": "shallow_base"}, True)
        res = store.query_similar(F(dd36=1.0), n=5, where={"archetype": "deep_kill"})
        assert [r["ticker"] for r in res] == ["DK"]

    def test_missing_feat_skipped(self, tmp_path):
        """缺特徵 → 不入庫、回傳 None(絕不發明數值)。"""
        store = make_store(tmp_path)
        feats = F(dd36=1.0)
        feats["vol_ratio"] = None
        assert store.add_case("BAD", feats, {"trigger": "2020-01-01"}, True) is None
        del feats["vol_ratio"]
        assert store.add_case("BAD2", feats, {"trigger": "2020-01-01"}, True) is None
        st = store.stats()
        assert st["success_cases"] == 0 and st["failed_analogs"] == 0
        with pytest.raises(ValueError):
            store.query_similar(feats)

    def test_upsert_stable_id(self, tmp_path):
        """同 ticker+trigger 重複加入 = upsert(計數不變,最後一筆為準)。"""
        store = make_store(tmp_path)
        store.add_case("AAA", F(dd36=1.0), {"trigger": "2020-01-01"}, True)
        store.add_case("AAA", F(dd36=2.0), {"trigger": "2020-01-01"}, True)
        assert store.stats()["success_cases"] == 1
        res = store.query_similar(F(dd36=1.0), n=1)
        assert res[0]["metadata"]["dd36"] == 2.0   # 後寫覆蓋

    def test_n_limit(self, tmp_path):
        store = make_store(tmp_path)
        for i in range(4):
            store.add_case(f"T{i}", F(dd36=1.0 + i), {"trigger": "2020-01-01"}, True)
        assert len(store.query_similar(F(dd36=1.0), n=2)) == 2


class TestSync:
    def test_sync_counts_and_stats(self, tmp_path):
        out = write_outputs(tmp_path / "outputs",
                            cases=[case("AAA", dd36=-0.7, r3m=0.4, vol_ratio=0.6),
                                   case("BBB", dd36=-0.3, dd_min18=-0.4, r3m=0.2,
                                        vol_ratio=1.1)],
                            failed=[fail_event("XXX", dd36=-0.8, r3m=0.3, vol_ratio=1.0)])
        store = make_store(tmp_path)
        rep = store.sync_from_outputs(out)
        assert rep["n_success"] == 2 and rep["n_fail"] == 1
        assert rep["n_skipped_missing_feats"] == 0
        assert rep["as_of"] == "2026-06-12" and rep["generated_at"]
        assert rep["counts_after"] == {"success_cases": 2, "failed_analogs": 1}
        st = store.stats()
        assert st == {"backend": "numpy", "persist_dir": str(tmp_path / "akashic"),
                      "success_cases": 2, "failed_analogs": 1,
                      "norms_synced": True, "norms_as_of": "2026-06-12",
                      "norms_n_cases": 3}
        # archetype 同 rally_dna 口徑:dd_min18 <= -0.55 → deep_kill
        dk = store.query_similar(F(dd36=-0.7, r3m=0.4, vol_ratio=0.6), n=1,
                                 where={"archetype": "deep_kill"})
        assert dk[0]["ticker"] == "AAA"

    def test_znorm_persisted_and_correct(self, tmp_path):
        """norms.json 的 mean/sd 與手算一致(ddof=1);查自身特徵 → 自己是 top,sim≈1。"""
        dd_vals = [-0.8, -0.6, -0.4, -0.2]
        out = write_outputs(tmp_path / "outputs",
                            cases=[case("AAA", dd36=dd_vals[0], r3m=0.1),
                                   case("BBB", dd36=dd_vals[1], r3m=0.2)],
                            failed=[fail_event("XXX", dd36=dd_vals[2], r3m=0.3),
                                    fail_event("YYY", dd36=dd_vals[3], r3m=0.4)])
        store = make_store(tmp_path)
        store.sync_from_outputs(out)
        norms = json.loads((tmp_path / "akashic" / "norms.json").read_text(encoding="utf-8"))
        m = sum(dd_vals) / 4
        sd = math.sqrt(sum((v - m) ** 2 for v in dd_vals) / 3)   # 樣本 sd(ddof=1)
        assert norms["mean"]["dd36"] == pytest.approx(m)
        assert norms["sd"]["dd36"] == pytest.approx(sd)
        assert norms["n_cases"] == 4 and norms["as_of"] == "2026-06-12"
        # 退化特徵(全 0)→ sd 退回 1.0(防除零,同 rally_dna)
        assert norms["sd"]["buy9_max"] == 1.0
        # 查 AAA 自身特徵 → AAA 為 top、cosine ≈ 1(同向量)
        res = store.query_similar(F(dd36=dd_vals[0], r3m=0.1), n=1)
        assert res[0]["ticker"] == "AAA"
        assert res[0]["similarity"] == pytest.approx(1.0)

    def test_sync_idempotent(self, tmp_path):
        """重 sync(穩定 id = ticker_trigger)→ 計數不變。"""
        out = write_outputs(tmp_path / "outputs",
                            cases=[case("AAA", dd36=-0.7), case("BBB", dd36=-0.3)],
                            failed=[fail_event("XXX", dd36=-0.8)])
        store = make_store(tmp_path)
        rep1 = store.sync_from_outputs(out)
        rep2 = store.sync_from_outputs(out)
        assert rep1["counts_after"] == rep2["counts_after"] == {
            "success_cases": 2, "failed_analogs": 1}
        assert rep1["norms"] == rep2["norms"]

    def test_sync_skips_missing_feats(self, tmp_path):
        """來源缺特徵(null / 缺鍵)的案例跳過並計數 — 不發明。"""
        bad_case = case("NUL", dd36=-0.5)
        bad_case["vol_ratio"] = None
        bad_fail = fail_event("NOF")
        del bad_fail["r3m"]
        out = write_outputs(tmp_path / "outputs",
                            cases=[case("AAA", dd36=-0.7), bad_case],
                            failed=[fail_event("XXX", dd36=-0.8), bad_fail])
        store = make_store(tmp_path)
        rep = store.sync_from_outputs(out)
        assert rep["n_success"] == 1 and rep["n_fail"] == 1
        assert rep["n_skipped_missing_feats"] == 2
        assert store.stats()["success_cases"] == 1

    def test_latest_output_selected(self, tmp_path):
        """sorted-glob-last:取最新日期檔;'.bak' / 'intraday' 名稱排除。"""
        out = tmp_path / "outputs"
        write_outputs(out, cases=[case("OLD", dd36=-0.5)], failed=[],
                      rally_name="rally-dna-2026-01-01.json")
        write_outputs(out, cases=[case("NEW", dd36=-0.5)],
                      failed=[fail_event("XXX", dd36=-0.8)],
                      rally_name="rally-dna-2026-06-12.json")
        (out / "rally-dna-2026-07-01.json.bak").write_text("{}", encoding="utf-8")
        (out / "rally-dna-intraday-2026-07-02.json").write_text("{}", encoding="utf-8")
        assert _latest_output(out, "rally-dna-*.json").name == "rally-dna-2026-06-12.json"
        store = make_store(tmp_path)
        rep = store.sync_from_outputs(out)
        assert rep["sources"]["rally_dna"]["path"].endswith("rally-dna-2026-06-12.json")
        assert [r["ticker"] for r in store.query_similar(F(dd36=-0.5), n=5,
                                                         where={"kind": "win"})] == ["NEW"]

    def test_sync_empty_outputs(self, tmp_path):
        """無來源檔 → 不爆炸、不寫 norms,回報 note。"""
        out = tmp_path / "outputs"
        out.mkdir()
        store = make_store(tmp_path)
        rep = store.sync_from_outputs(out)
        assert rep["n_success"] == 0 and rep["n_fail"] == 0
        assert "note" in rep
        assert not (tmp_path / "akashic" / "norms.json").exists()


class TestPersistence:
    def test_reload_across_instances(self, tmp_path):
        """numpy 後端落盤 json — 新實例(同 persist_dir)看得到既有資料與 norms。"""
        out = write_outputs(tmp_path / "outputs",
                            cases=[case("AAA", dd36=-0.7, r3m=0.4)],
                            failed=[fail_event("XXX", dd36=-0.8, r3m=0.1)])
        store1 = make_store(tmp_path)
        store1.sync_from_outputs(out)
        store2 = make_store(tmp_path)   # 重開
        st = store2.stats()
        assert st["success_cases"] == 1 and st["failed_analogs"] == 1
        assert st["norms_synced"] is True
        res = store2.query_similar(F(dd36=-0.7, r3m=0.4), n=1)
        assert res[0]["ticker"] == "AAA"
        assert res[0]["similarity"] == pytest.approx(1.0)
        # 結果攜帶 metadata(kind / ret_pct / ingest_as_of)
        meta = res[0]["metadata"]
        assert meta["kind"] == "win" and meta["ret_pct"] == 500.0
        assert meta["ingest_as_of"] == "2026-06-12"
