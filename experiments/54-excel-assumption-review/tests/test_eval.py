import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _evaluate():
    path = ROOT / "eval" / "evaluate.py"
    spec = importlib.util.spec_from_file_location("exp54_evaluate", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.evaluate


def test_smoke_totals_count_each_case_once():
    report = _evaluate()()
    summary = report["summary"]
    assert report["mode"] == "deterministic"
    assert report["not_a_model_evaluation"] is True
    assert "DETERMINISTIC SMOKE TEST" in report["evaluation_label"]
    assert summary["failed"] == 0
    assert summary["errors"] == 0
    assert summary["passed"] == summary["total_cases"]
    assert summary["passed"] + summary["failed"] + summary["errors"] == summary["total_cases"]
    ids = [case["case_id"] for case in report["cases"]]
    assert len(ids) == len(set(ids)) == summary["total_cases"]
    assert summary["total_cases"] >= 16
    checked_in = json.loads((ROOT / "eval" / "smoke_report.json").read_text(encoding="utf-8"))
    assert checked_in["summary"] == summary
