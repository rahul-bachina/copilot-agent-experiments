"""The smoke summary must not add the two identical quote counts."""

from pathlib import Path

from eval.evaluate import run


def test_smoke_report_does_not_sum_quote_counts():
    report = run(Path(__file__).resolve().parents[1] / "eval" / "synthetic_dataset.json")
    summary = report["summary"]
    assert report["mode"] == "deterministic"
    assert report["not_a_model_evaluation"] is True
    assert report["not_a_plan"] is True
    assert "DETERMINISTIC SMOKE TEST" in report["evaluation_label"]
    assert summary["quotes_are_not_summed"] is True
    assert summary["total_cases"] == 13
    assert summary["passed"] == 13
    assert summary["agreement_rate"] == 100.0
    assert "grand_total" not in summary
    assert "placed_quotes_sum" not in summary
    pair = [
        case["placed_quotes"]
        for case in report["cases"]
        if case["id"] in {"northfen-child-a", "northfen-child-a-again"}
    ]
    assert pair == [7, 7]
    assert 14 not in summary.values()
    exported = [case for case in report["cases"] if case["exported"] is True]
    assert [case["id"] for case in exported] == ["valid-signoff-local-copy"]
    assert all(case["needs_decided"] is False for case in report["cases"])
    assert all(case["sent_to_parents"] is False for case in report["cases"])
    assert all(case["model_called"] is False for case in report["cases"])
    assert all(case["network_called"] is False for case in report["cases"])
