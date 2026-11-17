"""The committed smoke report counts each case once."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_smoke_report_does_not_double_count():
    report = json.loads((ROOT / "eval" / "smoke_report.json").read_text(encoding="utf-8"))
    summary = report["summary"]
    assert report["mode"] == "deterministic"
    assert report["not_a_model_evaluation"] is True
    assert "DETERMINISTIC SMOKE TEST" in report["evaluation_label"]
    assert summary["total_cases"] == 14
    assert summary["passed"] + summary["failed"] + summary["errors"] == summary["total_cases"]
    ids = [row["case_id"] for row in report["cases"]]
    assert len(ids) == len(set(ids)) == summary["total_cases"]
    assert summary["failed"] == 0
    assert summary["errors"] == 0
