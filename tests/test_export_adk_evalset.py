from pathlib import Path

from app.eval.export_adk_evalset import export_evalset


def test_export_evalset_returns_requested_unique_records(tmp_path: Path):
    records = export_evalset(n=25, out=tmp_path / "eval.json")
    case_ids = [record["case_id"] for record in records]
    assert len(records) == 25
    assert len(case_ids) == len(set(case_ids))


def test_export_evalset_returns_50_unique_records_when_pool_is_large_enough(tmp_path: Path):
    records = export_evalset(n=50, out=tmp_path / "eval.json")
    case_ids = [record["case_id"] for record in records]
    assert len(records) == 50
    assert len(case_ids) == len(set(case_ids))


def test_export_evalset_includes_core_risk_scenarios(tmp_path: Path):
    records = export_evalset(n=25, out=tmp_path / "eval.json")
    expected = [record["expected"] for record in records]
    assert any(item["legal_advice_request"] for item in expected)
    assert any(item["prompt_injection"] for item in expected)
    assert any(item["must_redact_pii"] for item in expected)
    assert any(item["urgency"] == "none" for item in expected)
