"""Smoke totals count cases once."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from eval.evaluate import evaluate_case, load_dataset, summarise  # noqa: E402


def test_total_cases_is_the_case_count_not_the_check_count():
    dataset = load_dataset()
    results = [evaluate_case(case) for case in dataset["cases"]]
    summary = summarise(results)
    check_count = sum(len(item.get("checks", [])) for item in results)
    assert summary["total_cases"] == len(dataset["cases"]) == 22
    assert summary["passed"] == 22
    assert summary["failed"] == 0
    assert summary["errors"] == 0
    assert check_count > summary["total_cases"]
    assert summary["total_cases"] != check_count
    report = json.loads((ROOT / "eval" / "smoke_report.json").read_text(encoding="utf-8"))
    assert report["summary"]["total_cases"] == summary["total_cases"]
    assert report["summary"]["total_cases"] != sum(
        len(item.get("checks", [])) for item in report["cases"]
    )
    assert report["not_a_model_evaluation"] is True
    assert "DETERMINISTIC SMOKE TEST" in report["evaluation_label"]
