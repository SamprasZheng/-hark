"""API 呼叫記帳 — per-source 用量觀測(DataRouter 提案的採納內核).

2026-06-12 裁決:外部顧問的 DataRouter 大抽象駁回(lake 已是 local-first 層、
各 client 自帶限速/fallback;且 yfinance 對下市票回 0 根已實證 — 路由層救不了
數據存在性的牆)。採納其唯一真內核:**每個受限來源的呼叫記帳**,讓「今天燒了
多少 Polygon 配額」可見、撞牆可診斷。

append-only JSONL(outputs/api-call-log.jsonl),欄位:ts/source/endpoint/ok/
latency_ms。never-raise:記帳失敗絕不影響數據呼叫本身。brief 系統健康區
顯示當日 per-source 計數。
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

LOG_PATH = Path("outputs/api-call-log.jsonl")


def record(source: str, endpoint: str, *, ok: bool = True,
           latency_ms: Optional[int] = None, note: Optional[str] = None,
           log_path: Optional[Path] = None) -> None:
    """記一筆呼叫。never-raise(記帳是觀測,不是依賴)。"""
    try:
        p = log_path or LOG_PATH
        p.parent.mkdir(exist_ok=True)
        row = {"ts": datetime.now(timezone.utc).isoformat(), "source": source,
               "endpoint": endpoint, "ok": bool(ok)}
        if latency_ms is not None:
            row["latency_ms"] = int(latency_ms)
        if note:
            row["note"] = str(note)[:80]
        with p.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    except Exception:
        pass


class timed_call:
    """context manager:with timed_call('polygon', 'aggs') as t: ... 自動計時記帳。
    例外照常傳播(只把 ok=False 記下)。"""

    def __init__(self, source: str, endpoint: str, log_path: Optional[Path] = None):
        self.source, self.endpoint, self.log_path = source, endpoint, log_path

    def __enter__(self):
        self.t0 = time.monotonic()
        return self

    def __exit__(self, exc_type, exc, tb):
        record(self.source, self.endpoint, ok=exc_type is None,
               latency_ms=int((time.monotonic() - self.t0) * 1000),
               note=(str(exc)[:80] if exc else None), log_path=self.log_path)
        return False


def summary(date: Optional[str] = None, log_path: Optional[Path] = None) -> dict:
    """某日(預設今天 UTC)per-source 計數:{source: {calls, errors}}。"""
    date = date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    p = log_path or LOG_PATH
    out: dict = {}
    if not p.exists():
        return out
    for ln in p.read_text(encoding="utf-8").splitlines():
        try:
            r = json.loads(ln)
        except Exception:
            continue
        if not str(r.get("ts", "")).startswith(date):
            continue
        s = out.setdefault(r.get("source", "?"), {"calls": 0, "errors": 0})
        s["calls"] += 1
        if not r.get("ok", True):
            s["errors"] += 1
    return out
