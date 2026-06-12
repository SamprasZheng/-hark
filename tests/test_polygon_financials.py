"""Tests for polygon_financials — synthetic payloads, no network."""

from __future__ import annotations

from sharks.data.polygon_financials import parse_quarter, with_yoy


def _q(fy, fp, end, filing, rev, ocf, capex):
    return {"fiscal_year": fy, "fiscal_period": fp, "end_date": end, "filing_date": filing,
            "financials": {
                "income_statement": {"revenues": {"value": rev},
                                     "net_income_loss": {"value": rev * 0.1}},
                "cash_flow_statement": {
                    "net_cash_flow_from_operating_activities": {"value": ocf},
                    "payments_to_acquire_property_plant_and_equipment": {"value": capex}}}}


def test_parse_quarter_extracts_pit_fields():
    r = parse_quarter(_q("2026", "Q1", "2026-03-31", "2026-05-02", 1000.0, 200.0, -50.0))
    assert r["fiscal"] == "2026Q1"
    assert r["filing_date"] == "2026-05-02"          # PIT 錨點
    assert r["fcf"] == 150.0                          # OCF - |capex|
    assert r["net_income"] == 100.0


def test_parse_quarter_missing_sections():
    r = parse_quarter({"fiscal_year": "2025", "fiscal_period": "Q4", "financials": {}})
    assert r["revenue"] is None and r["fcf"] is None  # 防衛:缺科目不炸


def test_with_yoy_compares_same_quarter_prior_year():
    rows = [_q("2026", "Q1", "2026-03-31", "2026-05-02", 1200.0, 300.0, -50.0),
            _q("2025", "Q4", "2025-12-31", "2026-02-10", 1100.0, 250.0, -50.0),
            _q("2025", "Q3", "2025-09-30", "2025-11-05", 1050.0, 240.0, -50.0),
            _q("2025", "Q2", "2025-06-30", "2025-08-05", 1020.0, 230.0, -50.0),
            _q("2025", "Q1", "2025-03-31", "2025-05-02", 1000.0, 100.0, -50.0)]
    out = with_yoy([parse_quarter(x) for x in rows])
    assert out[0]["rev_yoy_pct"] == 20.0              # 2026Q1 vs 2025Q1
    assert out[0]["fcf_improving_yoy"] is True        # 250 vs 50
    assert out[-1]["rev_yoy_pct"] is None             # 無 4 季前資料
