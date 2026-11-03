"""Smoke totals count cases once. Claim verdicts are not added to that total."""

from eval.evaluate import evaluate
from src.report import report
from tests.support import ROOT, load_json


def test_smoke_totals_count_cases_once():
    result = evaluate()
    summary = result["summary"]
    assert summary["total_cases"] == 23
    assert summary["passed"] == 23
    assert summary["failed"] == 0
    assert summary["passed"] + summary["failed"] == summary["total_cases"]
    assert summary["total_cases"] == len(result["cases"])
    assert "errors" not in summary
    assert result["claims_added_to_total_cases"] is False
    assert result["not_a_foundry_score"] is True
    claim_sum = sum(row["claim_count"] or 0 for row in result["cases"])
    assert claim_sum != summary["total_cases"]
    for row in result["cases"]:
        if row["claim_count"] is None:
            continue
        assert row["verdict_total"] == row["claim_count"]


def test_sample_output_matches_the_checker():
    bundle = load_json(ROOT / "examples" / "sample_bundle.json")
    saved = load_json(ROOT / "examples" / "sample_output.json")
    assert report(bundle, "2026-11-03") == saved
