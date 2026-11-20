"""Smoke totals are one row per case. Paraphrase recall is not added in."""

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_smoke_totals_do_not_double_count():
    spec = importlib.util.spec_from_file_location("eval70", ROOT / "eval" / "evaluate.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["eval70"] = module
    spec.loader.exec_module(module)
    report = module.evaluate()
    summary = report["summary"]
    assert report["mode"] == "deterministic"
    assert report["not_a_model_evaluation"] is True
    assert summary["total_cases"] == 20
    assert summary["passed"] == 20
    assert summary["passed"] + summary["failed"] + summary["errors"] == summary["total_cases"]
    ids = [row["case_id"] for row in report["cases"]]
    assert len(ids) == len(set(ids)) == summary["total_cases"]
    paraphrase = report["paraphrase_recall"]
    assert paraphrase["not_added_to_case_total"] is True
    for name, row in paraphrase["categories"].items():
        assert row["sentences"] >= 20, name
        if row["expect_match"]:
            assert row["recall"] == 1.0, name
        else:
            assert row["false_inclusions"] == 0, name
