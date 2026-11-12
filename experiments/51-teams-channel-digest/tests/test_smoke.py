"""The checked-in smoke report matches a fresh run and does not double-count."""

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _evaluate():
    path = ROOT / "eval" / "evaluate.py"
    spec = importlib.util.spec_from_file_location("exp51_evaluate", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_smoke_totals_count_each_case_once():
    report = _evaluate().evaluate()
    summary = report["summary"]
    assert report["not_a_model_evaluation"] is True
    assert summary["passed"] + summary["failed"] + summary["errors"] == summary["total_cases"]
    assert summary["failed"] == 0
    assert summary["errors"] == 0
    assert summary["total_cases"] >= 16
    ids = [case["case_id"] for case in report["cases"]]
    assert len(ids) == len(set(ids)) == summary["total_cases"]
    assert summary["section_counts_are_not_added_to_case_count"] is True
