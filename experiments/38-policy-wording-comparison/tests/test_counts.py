"""Smoke totals count cases once. Cell counts stay on the case."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from eval.evaluate import run  # noqa: E402


def test_two_copies_of_the_sample_are_not_added_together():
    report = run()
    summary = report["summary"]
    assert summary["total_cases"] == 12
    assert summary["passed"] == 12
    assert summary["failed"] == 0
    assert "grand_total" not in summary
    assert 30 not in summary.values()
    quotes = [
        case["stated_cell_count"]
        for case in report["cases"]
        if case["id"] in {"northfen-wordings", "northfen-wordings-again"}
    ]
    assert quotes == [15, 15]
    assert report["not_an_llm_judge"] is True
    assert report["not_a_coverage_opinion"] is True
    assert report["experiment_36_imported"] is False
