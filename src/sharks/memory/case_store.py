"""阿卡西案例庫 — 上漲 DNA 案例的向量持久化與相似檢索層(QLIB-VECTORDB-PLAN v3a).

進入條件已達成(2026-06-12):rally-dna 成功案例 60 + failed-analogs 172 = 232 > 150。
本模組是「持久化 + 檢索」層;rally_dna 既有的 Top3 暴力最近鄰(已測試)維持不動 —
未來接線時 dna_match_today 才考慮改由本庫查詢取代每次全池重算。

llm_involvement: none — 全 rule-based(特徵 z-score + cosine 最近鄰,無學習權重、
無嵌入模型;向量 = 數值特徵本身)。

設計:
  * 雙後端同一 API:
      - ChromaBackend:chromadb PersistentClient(lazy import),cosine space,
        collections 'success_cases' / 'failed_analogs'。
      - NumpyJsonBackend:純 numpy + json 檔(persist_dir 下每 collection 一檔)。
        <1k 案例的精確 cosine 是平凡計算 — 測試/離線後端。
    chromadb 可匯入則自動選用,backend= 參數可強制("chroma"|"numpy")。
  * 向量 = rally_dna.MATCH_FEATS 五維('dd36','dist_ma10','buy9_max','r3m','vol_ratio'),
    以 sync 時的全庫(成功∪失敗)mean/sd 做 z-score;統計量持久化於 norms.json,
    查詢時用同一份統計(同一把尺,不因查詢時點漂移)。
  * 缺任一特徵的案例一律跳過 — 絕不發明數值(PIT 紀律);原始特徵同時存進
    metadata,未來可重標準化。
  * 冪等:id = f"{ticker}_{trigger}",重 sync 為 upsert。
  * 注意:sync 重算 norms 後只重寫「本次 sync 的案例」向量;sync 之外以 add_case
    手動加入且不在 outputs 內的案例,其向量停留在加入當時的標準化 — 原始特徵
    在 metadata 內,需要時可全量重建。

CLI:
    python -m sharks.memory.case_store sync                      # outputs/ 最新 rally-dna + failed-analogs → 入庫
    python -m sharks.memory.case_store query --ticker SMCI [--n 5] [--kind fail]
    python -m sharks.memory.case_store stats

recommend-only:本庫輸出僅供研究/旁證,非倉位指令;不下單、不連券商。
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import numpy as np

# 單一事實來源:特徵口徑與 deep_kill 門檻都沿用 rally_dna(同一把尺)
from sharks.backtest.rally_dna import DEEP_KILL_DD, MATCH_FEATS

COLLECTIONS = ("success_cases", "failed_analogs")
NORMS_FILE = "norms.json"
# sd 不可算或為 0 時退回 1.0 — 同 rally_dna dna_match_today 的防除零(float(col.std()) or 1.0)
SD_FALLBACK = 1.0
# cosine 零向量防護:範數低於此值視為零向量,相似度記 0.0(不可比就不比,不發明)
ZERO_NORM_EPS = 1e-12


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _feat_vector(feats: dict) -> Optional[list[float]]:
    """5 維原始特徵向量;任一缺(None / 缺鍵 / 非有限數)→ None(整筆跳過,不發明)。"""
    vals: list[float] = []
    for k in MATCH_FEATS:
        v = (feats or {}).get(k)
        if v is None or isinstance(v, bool) or not isinstance(v, (int, float)):
            return None
        v = float(v)
        if not np.isfinite(v):
            return None
        vals.append(v)
    return vals


def _sanitize_meta(meta: dict) -> dict:
    """僅保留標量且非 None/NaN 的 metadata(chroma 限制;numpy 後端同規則保持一致)。"""
    out = {}
    for k, v in (meta or {}).items():
        if v is None:
            continue
        if isinstance(v, float) and not np.isfinite(v):
            continue
        if isinstance(v, (str, int, float, bool)):
            out[k] = v
    return out


def _compute_norms(raw_vectors: list[list[float]], as_of, generated_at: str) -> dict:
    """全庫 z-score 統計(sync 時計算、持久化於 norms.json)。"""
    arr = np.asarray(raw_vectors, dtype=float)
    mean, sd = {}, {}
    for j, k in enumerate(MATCH_FEATS):
        col = arr[:, j]
        m = float(col.mean())
        # 樣本標準差 ddof=1 — 同 rally_dna 用 pandas .std() 的口徑;單筆/退化 → SD_FALLBACK
        s = float(col.std(ddof=1)) if len(col) > 1 else 0.0
        if not np.isfinite(s) or s == 0.0:
            s = SD_FALLBACK
        mean[k], sd[k] = m, s
    return {"as_of": as_of, "generated_at": generated_at,
            "feats": list(MATCH_FEATS), "n_cases": int(len(arr)),
            "mean": mean, "sd": sd,
            "_doc": ("全庫(成功∪失敗)z-score 統計;sd=樣本標準差(ddof=1,同 rally_dna "
                     "pandas .std() 口徑),不可算或 0 → 1.0(同 rally_dna 防除零);"
                     "查詢時讀同一份 norms.json — 同一把尺。")}


def _latest_output(out_dir: Path, pattern: str) -> Optional[Path]:
    """sorted-glob-last 探索;名稱含 'intraday' 或 '.bak' 結尾者排除(repo 規約)。"""
    cands = sorted(p for p in Path(out_dir).glob(pattern)
                   if "intraday" not in p.name and not p.name.endswith(".bak"))
    return cands[-1] if cands else None


# ── 後端(同一最小介面:upsert / query / count)──


class NumpyJsonBackend:
    """純 numpy + json 後端 — persist_dir 下每 collection 一個 json 檔,精確 cosine 全掃描."""

    name = "numpy"

    def __init__(self, persist_dir: Path):
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self._data: dict[str, dict] = {}
        for coll in COLLECTIONS:
            p = self._path(coll)
            self._data[coll] = (json.loads(p.read_text(encoding="utf-8"))
                                if p.exists() else {})

    def _path(self, coll: str) -> Path:
        return self.persist_dir / f"{coll}.json"

    def upsert(self, coll: str, ids: list[str], vectors: list[list[float]],
               metadatas: list[dict], documents: list[str]) -> None:
        store = self._data[coll]
        for cid, vec, meta, doc in zip(ids, vectors, metadatas, documents):
            store[cid] = {"vector": [float(x) for x in vec],
                          "metadata": meta, "document": doc}
        self._path(coll).write_text(json.dumps(store, ensure_ascii=False, indent=2),
                                    encoding="utf-8")

    def count(self, coll: str) -> int:
        return len(self._data[coll])

    def query(self, coll: str, vector: list[float], n: int,
              where: Optional[dict]) -> list[tuple[str, float, dict]]:
        store = self._data[coll]
        if not store:
            return []
        q = np.asarray(vector, dtype=float)
        qn = float(np.linalg.norm(q))
        out: list[tuple[str, float, dict]] = []
        for cid, rec in store.items():
            meta = rec.get("metadata") or {}
            if where and any(meta.get(k) != v for k, v in where.items()):
                continue
            v = np.asarray(rec["vector"], dtype=float)
            vn = float(np.linalg.norm(v))
            sim = (0.0 if qn < ZERO_NORM_EPS or vn < ZERO_NORM_EPS
                   else float(np.dot(q, v) / (qn * vn)))
            out.append((cid, sim, meta))
        out.sort(key=lambda t: (-t[1], t[0]))   # 同分以 id 排序 — 確定性
        return out[:n]


class ChromaBackend:
    """chromadb PersistentClient 後端(cosine space)。lazy import — 未安裝時不可用."""

    name = "chroma"

    def __init__(self, persist_dir: Path):
        import chromadb  # lazy — pip install 可能還在跑;numpy 後端不受影響
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(path=str(self.persist_dir))
        self._colls = {coll: self._client.get_or_create_collection(
            name=coll, metadata={"hnsw:space": "cosine"}) for coll in COLLECTIONS}

    def upsert(self, coll: str, ids: list[str], vectors: list[list[float]],
               metadatas: list[dict], documents: list[str]) -> None:
        if not ids:
            return
        self._colls[coll].upsert(ids=list(ids),
                                 embeddings=[[float(x) for x in v] for v in vectors],
                                 metadatas=list(metadatas), documents=list(documents))

    def count(self, coll: str) -> int:
        return self._colls[coll].count()

    @staticmethod
    def _where(where: Optional[dict]) -> Optional[dict]:
        if not where:
            return None
        if len(where) == 1:
            return dict(where)
        return {"$and": [{k: v} for k, v in where.items()]}

    def query(self, coll: str, vector: list[float], n: int,
              where: Optional[dict]) -> list[tuple[str, float, dict]]:
        c = self._colls[coll]
        total = c.count()
        if total == 0:
            return []
        res = c.query(query_embeddings=[[float(x) for x in vector]],
                      n_results=min(n, total), where=self._where(where),
                      include=["metadatas", "distances"])
        ids = res["ids"][0]
        dists = res["distances"][0]
        metas = res["metadatas"][0]
        # chroma cosine distance = 1 - cosine similarity
        return [(cid, 1.0 - float(d), dict(m) if m else {})
                for cid, d, m in zip(ids, dists, metas)]


# ── CaseStore ──


class CaseStore:
    """雙後端統一 API:add_case / query_similar / stats / sync_from_outputs."""

    def __init__(self, persist_dir: Path = Path("data/akashic"),
                 backend: Optional[str] = None):
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        if backend is None:
            try:
                import chromadb  # noqa: F401 — 自動偵測
                backend = "chroma"
            except ImportError:
                backend = "numpy"
        if backend == "chroma":
            self.backend = ChromaBackend(self.persist_dir)
        elif backend == "numpy":
            self.backend = NumpyJsonBackend(self.persist_dir)
        else:
            raise ValueError(f"unknown backend: {backend!r}(可用 'chroma'|'numpy')")

    # ── 標準化(查詢與入庫共用 norms.json — 同一把尺)──

    @property
    def _norms_path(self) -> Path:
        return self.persist_dir / NORMS_FILE

    def _load_norms(self) -> dict:
        if self._norms_path.exists():
            return json.loads(self._norms_path.read_text(encoding="utf-8"))
        # 尚未 sync:恆等變換(mean 0 / sd 1)— 不發明統計量
        return {"mean": {k: 0.0 for k in MATCH_FEATS},
                "sd": {k: 1.0 for k in MATCH_FEATS}}

    def _zscore(self, raw: list[float], norms: Optional[dict] = None) -> list[float]:
        nz = norms or self._load_norms()
        return [(v - float(nz["mean"][k])) / (float(nz["sd"][k]) or SD_FALLBACK)
                for k, v in zip(MATCH_FEATS, raw)]

    @staticmethod
    def _case_id(ticker, trigger) -> str:
        return f"{ticker}_{trigger or 'na'}"

    # ── API ──

    def add_case(self, ticker: str, feats: dict, metadata: dict,
                 is_success: bool) -> Optional[str]:
        """加入單一案例;缺特徵 → 跳過並回傳 None。id = ticker_trigger(冪等 upsert)。"""
        raw = _feat_vector(feats)
        if raw is None:
            print(f"case_store: skip {ticker}(missing feat)", file=sys.stderr)
            return None
        kind = "win" if is_success else "fail"
        meta = _sanitize_meta({**(metadata or {}), "ticker": ticker, "kind": kind,
                               **dict(zip(MATCH_FEATS, raw))})
        cid = self._case_id(ticker, (metadata or {}).get("trigger"))
        doc = f"{ticker} {kind} trigger={meta.get('trigger', 'na')}"
        coll = "success_cases" if is_success else "failed_analogs"
        self.backend.upsert(coll, [cid], [self._zscore(raw)], [meta], [doc])
        return cid

    def query_similar(self, feats: dict, n: int = 5,
                      where: Optional[dict] = None) -> list[dict]:
        """cosine 最近鄰(成功∪失敗兩 collection 合併排序)。
        where = metadata 等值過濾,如 {'kind': 'fail'} 或 {'archetype': 'deep_kill'}。"""
        raw = _feat_vector(feats)
        if raw is None:
            raise ValueError(f"query feats 缺值 — 需要全部 {MATCH_FEATS}(缺值不發明)")
        vec = self._zscore(raw)
        hits: list[tuple[str, float, dict]] = []
        for coll in COLLECTIONS:
            hits.extend(self.backend.query(coll, vec, n,
                                           dict(where) if where else None))
        hits.sort(key=lambda t: (-t[1], t[0]))
        return [{"ticker": meta.get("ticker"), "similarity": round(sim, 4),
                 "metadata": meta} for _cid, sim, meta in hits[:n]]

    def stats(self) -> dict:
        norms = (json.loads(self._norms_path.read_text(encoding="utf-8"))
                 if self._norms_path.exists() else None)
        return {"backend": self.backend.name,
                "persist_dir": str(self.persist_dir),
                "success_cases": self.backend.count("success_cases"),
                "failed_analogs": self.backend.count("failed_analogs"),
                "norms_synced": norms is not None,
                "norms_as_of": (norms or {}).get("as_of"),
                "norms_n_cases": (norms or {}).get("n_cases")}

    # ── sync ──

    def sync_from_outputs(self, out_dir: Path = Path("outputs")) -> dict:
        """讀 outputs/ 最新 rally-dna-*.json(case_library.cases)+ failed-analogs-*.json
        (failed_events),全量 upsert(冪等:id = ticker_trigger);同時重算並持久化
        全庫 z-score 統計(norms.json)。"""
        out_dir = Path(out_dir)
        generated_at = _utc_now_iso()
        rally_p = _latest_output(out_dir, "rally-dna-*.json")
        failed_p = _latest_output(out_dir, "failed-analogs-*.json")
        prepped: dict[str, list[tuple[str, list[float], dict, str]]] = {
            c: [] for c in COLLECTIONS}
        n_skipped = 0
        sources: dict[str, dict] = {}

        if rally_p is not None:
            data = json.loads(rally_p.read_text(encoding="utf-8"))
            sources["rally_dna"] = {"path": str(rally_p), "as_of": data.get("as_of")}
            for c in ((data.get("case_library") or {}).get("cases") or []):
                raw = _feat_vector(c)
                if raw is None:
                    n_skipped += 1
                    continue
                dd18 = c.get("dd_min18")
                meta = _sanitize_meta({
                    "ticker": c.get("ticker"), "kind": "win",
                    "sector": c.get("sector"), "era": c.get("era"),
                    "size_bucket": c.get("size_bucket"),
                    "trough": c.get("trough"), "trigger": c.get("trigger"),
                    "ret_pct": c.get("gain_24m_pct"),
                    # archetype 同 rally_dna 口徑:dd_min18 <= DEEP_KILL_DD → deep_kill
                    "archetype": (None if dd18 is None else
                                  ("deep_kill" if float(dd18) <= DEEP_KILL_DD
                                   else "shallow_base")),
                    "ingest_as_of": data.get("as_of"),
                    **dict(zip(MATCH_FEATS, raw))})
                cid = self._case_id(c.get("ticker"), c.get("trigger"))
                doc = (f"{c.get('ticker')} win trigger={c.get('trigger')} "
                       f"sector={c.get('sector')}")
                prepped["success_cases"].append((cid, raw, meta, doc))

        if failed_p is not None:
            data = json.loads(failed_p.read_text(encoding="utf-8"))
            sources["failed_analogs"] = {"path": str(failed_p),
                                         "as_of": data.get("as_of")}
            for c in (data.get("failed_events") or []):
                raw = _feat_vector(c)
                if raw is None:
                    n_skipped += 1
                    continue
                meta = _sanitize_meta({
                    "ticker": c.get("ticker"), "kind": "fail",
                    "trigger": c.get("trigger"), "outcome": c.get("outcome"),
                    "ret_pct": c.get("end_ret_pct"),
                    "ingest_as_of": data.get("as_of"),
                    **dict(zip(MATCH_FEATS, raw))})
                cid = self._case_id(c.get("ticker"), c.get("trigger"))
                doc = (f"{c.get('ticker')} fail trigger={c.get('trigger')} "
                       f"outcome={c.get('outcome')}")
                prepped["failed_analogs"].append((cid, raw, meta, doc))

        as_of_vals = [s.get("as_of") for s in sources.values() if s.get("as_of")]
        report = {"as_of": max(as_of_vals) if as_of_vals else None,
                  "generated_at": generated_at,
                  "backend": self.backend.name, "sources": sources,
                  "n_success": len(prepped["success_cases"]),
                  "n_fail": len(prepped["failed_analogs"]),
                  "n_skipped_missing_feats": n_skipped}
        all_raw = [raw for rows in prepped.values() for (_c, raw, _m, _d) in rows]
        if not all_raw:
            report["note"] = "無可入庫案例 — norms.json 未更新"
            return report

        norms = _compute_norms(all_raw, as_of=report["as_of"],
                               generated_at=generated_at)
        self._norms_path.write_text(json.dumps(norms, ensure_ascii=False, indent=2),
                                    encoding="utf-8")
        for coll, rows in prepped.items():
            if not rows:
                continue
            self.backend.upsert(coll,
                                [r[0] for r in rows],
                                [self._zscore(r[1], norms) for r in rows],
                                [r[2] for r in rows],
                                [r[3] for r in rows])
            print(f"case_store: upsert {len(rows)} -> {coll}", file=sys.stderr)
        report["counts_after"] = {c: self.backend.count(c) for c in COLLECTIONS}
        report["norms"] = {"mean": norms["mean"], "sd": norms["sd"],
                           "n_cases": norms["n_cases"]}
        return report


# ── CLI ──


def _ticker_feats_from_outputs(out_dir: Path, ticker: str) -> Optional[dict]:
    """從最新 rally-dna 輸出找 ticker 的最近特徵:先 dna_match_today.top(今日掃描列),
    再 case_library.cases(歷史案例)。找不到或特徵不全 → None(不發明)。"""
    p = _latest_output(out_dir, "rally-dna-*.json")
    if p is None:
        return None
    data = json.loads(p.read_text(encoding="utf-8"))
    pools = [((data.get("dna_match_today") or {}).get("top") or []),
             ((data.get("case_library") or {}).get("cases") or [])]
    for pool in pools:
        for row in pool:
            if row.get("ticker") == ticker:
                feats = {k: row.get(k) for k in MATCH_FEATS}
                if _feat_vector(feats) is not None:
                    return feats
    return None


def main(argv: Optional[list[str]] = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")    # cp950 console 防護
    except Exception:
        pass
    ap = argparse.ArgumentParser(
        description="akashic case store — 案例向量庫(recommend-only,不下單)")
    ap.add_argument("--persist-dir", default="data/akashic")
    ap.add_argument("--backend", choices=["chroma", "numpy"], default=None,
                    help="預設自動:chromadb 可匯入用 chroma,否則 numpy")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sp_sync = sub.add_parser("sync", help="outputs/ 最新 rally-dna + failed-analogs → 入庫")
    sp_sync.add_argument("--out-dir", default="outputs")
    sp_q = sub.add_parser("query", help="以 ticker 最新特徵查相似案例")
    sp_q.add_argument("--ticker", required=True)
    sp_q.add_argument("--n", type=int, default=5)
    sp_q.add_argument("--kind", choices=["win", "fail"], default=None,
                      help="只看成功或失敗案例")
    sp_q.add_argument("--out-dir", default="outputs")
    sub.add_parser("stats", help="各 collection 計數 + 後端")
    args = ap.parse_args(argv)

    store = CaseStore(Path(args.persist_dir), backend=args.backend)
    if args.cmd == "sync":
        rep = store.sync_from_outputs(Path(args.out_dir))
        print(json.dumps(rep, ensure_ascii=False, indent=2))
    elif args.cmd == "query":
        feats = _ticker_feats_from_outputs(Path(args.out_dir), args.ticker)
        if feats is None:
            print(f"case_store: {args.ticker} 不在最新 rally-dna 輸出"
                  f"(dna_match_today.top / case_library.cases)或特徵不全", file=sys.stderr)
            return 1
        where = {"kind": args.kind} if args.kind else None
        res = store.query_similar(feats, n=args.n, where=where)
        print(json.dumps({"ticker": args.ticker, "feats": feats, "where": where,
                          "generated_at": _utc_now_iso(),
                          "backend": store.backend.name, "similar": res,
                          "disclaimer": "recommend-only;相似案例僅供研究旁證,非倉位指令。"},
                         ensure_ascii=False, indent=2))
    else:   # stats
        print(json.dumps(store.stats(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
