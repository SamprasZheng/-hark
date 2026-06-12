"""call_log 測試 — tmp_path 注入,零真實磁碟。"""

from __future__ import annotations

import json

from sharks.data.call_log import record, summary, timed_call


class TestCallLog:
    def test_record_and_summary(self, tmp_path):
        p = tmp_path / "log.jsonl"
        record("polygon", "aggs", latency_ms=120, log_path=p)
        record("polygon", "aggs", ok=False, note="429", log_path=p)
        record("nyfed", "gscpi", log_path=p)
        s = summary(log_path=p)
        assert s["polygon"] == {"calls": 2, "errors": 1}
        assert s["nyfed"] == {"calls": 1, "errors": 0}

    def test_timed_call_ok_and_exception(self, tmp_path):
        p = tmp_path / "log.jsonl"
        with timed_call("x", "ep", log_path=p):
            pass
        try:
            with timed_call("x", "ep", log_path=p):
                raise ValueError("boom")
        except ValueError:
            pass
        rows = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines()]
        assert rows[0]["ok"] is True and "latency_ms" in rows[0]
        assert rows[1]["ok"] is False and "boom" in rows[1]["note"]

    def test_summary_date_filter(self, tmp_path):
        p = tmp_path / "log.jsonl"
        p.write_text(json.dumps({"ts": "2020-01-01T00:00:00+00:00",
                                 "source": "old", "ok": True}) + "\n", encoding="utf-8")
        assert summary(log_path=p) == {}                       # 今天無紀錄
        assert summary("2020-01-01", log_path=p) == {"old": {"calls": 1, "errors": 0}}

    def test_missing_file_and_garbage(self, tmp_path):
        assert summary(log_path=tmp_path / "nope.jsonl") == {}
        p = tmp_path / "g.jsonl"
        p.write_text("garbage\n", encoding="utf-8")
        assert summary(log_path=p) == {}

    def test_record_never_raises_on_bad_path(self, tmp_path):
        # 不可寫路徑(目錄當檔案)→ 靜默吞掉,絕不影響呼叫方
        bad = tmp_path / "dir-as-file"
        bad.mkdir()
        record("x", "y", log_path=bad)         # 不應 raise
