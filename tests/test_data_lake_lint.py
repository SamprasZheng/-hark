"""Tests for the info-snapshot sanity lint(EUR/ADR 衍生欄位汙染)— pure dicts, no disk/network."""

from __future__ import annotations

from sharks.data.data_lake import _apply_info_lint, lint_info_fields


def test_lint_flags_asml_style_adr_corruption():
    # 回歸:ASML.json 實測(2026-06-10)— EUR 計帳 ADR,三個衍生欄位同被 ~55.5x 放大
    bad = {
        "currency": "USD", "financialCurrency": "EUR",
        "marketCap": 685_183_991_808, "enterpriseValue": 38_058_359_521_280,
        "priceToBook": 1586.29, "floatShares": 21_403_831_333,
        "sharesOutstanding": 385_417_665,
    }
    reasons = lint_info_fields(bad)
    assert len(reasons) == 3
    assert any("priceToBook" in r for r in reasons)
    assert any("enterpriseValue" in r for r in reasons)
    assert any("floatShares" in r for r in reasons)


def test_lint_passes_clean_snapshot():
    good = {
        "marketCap": 1.0e12, "enterpriseValue": 1.05e12,
        "priceToBook": 12.3, "floatShares": 9.9e9, "sharesOutstanding": 1.0e10,
    }
    assert lint_info_fields(good) == []


def test_lint_tolerates_missing_and_non_numeric_fields():
    assert lint_info_fields({}) == []
    assert lint_info_fields({"priceToBook": "Infinity", "marketCap": None,
                             "enterpriseValue": "n/a"}) == []


def test_apply_lint_marks_and_clears():
    bad = {"priceToBook": 1586.0}
    _apply_info_lint(bad)
    assert bad["derived_fields_suspect"] is True
    assert bad["derived_fields_suspect_reasons"]
    # 修復後重跑 lint(例如下一次 store_info 抓到乾淨數據)→ 旗標要被清掉
    bad["priceToBook"] = 12.0
    _apply_info_lint(bad)
    assert "derived_fields_suspect" not in bad
    assert "derived_fields_suspect_reasons" not in bad
