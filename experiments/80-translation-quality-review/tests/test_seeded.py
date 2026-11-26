"""Seeded errors, risk paraphrases, and negation."""

from src.risk import risk_categories, sensitive_categories
from src.seeded import alignment_report, paraphrase_report, seeded_report


def test_seeded_error_precision_and_recall():
    report = seeded_report()
    assert report["not_added_to_case_total"] is True
    assert report["not_a_model_evaluation"] is True
    for name, row in report["categories"].items():
        assert row["positives"] >= 20, name
        assert row["negatives"] >= 20, name
        assert row["recall"] == 1.0, name
        assert row["precision"] == 1.0, name
        assert row["false_positive"] == 0, name
        assert row["false_negative"] == 0, name


def test_risk_paraphrases_and_negation():
    report = paraphrase_report()
    assert report["not_added_to_case_total"] is True
    for name, row in report["risk"].items():
        assert row["sentences"] >= 20, name
        assert row["recall"] == 1.0, name
        assert row["false_inclusions"] == 0, name
    denied = "It is not true that this letter sets out the deadline is Tuesday."
    assert risk_categories(denied) == []
    assert "deadlines" in risk_categories("Please note that the deadline is Tuesday.")


def test_sensitive_paraphrases_are_routed_even_when_denied():
    report = paraphrase_report()
    for name, row in report["sensitive"].items():
        assert row["sentences"] >= 20, name
        assert row["recall"] == 1.0, name
        assert row["denied_recall"] == 1.0, name
        assert row["title_is_not_a_cue"] is True, name
    assert sensitive_categories("Please read the safeguarding policy.") == []
    assert "safeguarding" in sensitive_categories("I am not saying that my child is not safe.")


def test_alignment_reuses_experiment_79_and_reports_both_rates():
    report = alignment_report()
    assert report["not_added_to_case_total"] is True
    assert report["positives"] >= 20
    assert report["negatives"] >= 20
    assert report["precision"] == 1.0
    assert report["recall"] == 1.0
    assert "79-document-comparison" in report["reused"]
