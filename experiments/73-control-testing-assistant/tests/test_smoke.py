"""The smoke scorer counts each case once."""

import json
from pathlib import Path

from eval.evaluate import evaluate

ROOT = Path(__file__).resolve().parents[1]


def test_smoke_totals_do_not_double_count():
    report = evaluate()
    summary = report["summary"]
    assert report["mode"] == "deterministic"
    assert report["not_a_model_evaluation"] is True
    assert "DETERMINISTIC SMOKE TEST" in report["evaluation_label"]
    assert summary["total_cases"] == 20
    assert summary["passed"] + summary["failed"] + summary["errors"] == summary["total_cases"]
    assert summary["failed"] == 0
    assert summary["errors"] == 0
    ids = [case["case_id"] for case in report["cases"]]
    assert len(ids) == len(set(ids)) == summary["total_cases"]
    paraphrase = report["paraphrase_recall"]
    assert paraphrase["not_added_to_case_total"] is True
    for name, row in paraphrase["categories"].items():
        assert row["sentences"] >= 20, name
        assert row["recall"] == 1.0, name
        assert row["precision"] == 1.0, name
        assert row["false_inclusions"] == 0, name
    written = json.loads((ROOT / "eval" / "smoke_report.json").read_text(encoding="utf-8"))
    assert written["summary"]["total_cases"] == 20
    assert written["summary"]["passed"] == 20
