"""Paraphrase recall and precision. A miss is a failure. Negation is not an inclusion."""

from src.cues import category_hit, safety_hit
from src.paraphrases import NEGATIVES, POSITIVES, SUPPORT_NEGATIVES, SUPPORT_POSITIVES
from src.assistant import answer_question


def _hit(name: str, text: str) -> bool:
    if name in {"distress", "domestic_abuse", "safeguarding"}:
        return safety_hit(text, name)
    return category_hit(text, name)


def test_each_risk_category_has_twenty_reworded_variants_and_full_recall():
    assert set(POSITIVES) == set(NEGATIVES)
    for name, rows in POSITIVES.items():
        assert len(rows) >= 20
        assert len(NEGATIVES[name]) >= 8
        caught = [row for row in rows if _hit(name, row)]
        false = [row for row in NEGATIVES[name] if _hit(name, row)]
        assert caught == rows
        assert false == []
        precision = len(caught) / (len(caught) + len(false))
        assert precision == 1.0


def test_negation_does_not_count_as_an_eligibility_or_a_rate():
    assert category_hit("It is not true that I will get housing benefit.", "eligibility") is False
    assert category_hit("It is not true that the page includes a weekly rate.", "award") is False
    assert category_hit("Nobody said I will get it.", "eligibility") is False
    assert category_hit("Will I get it?", "eligibility") is True


def test_housing_benefit_page_support_reports_recall_and_precision():
    def quoted(question: str) -> list[str]:
        result = answer_question(
            {
                "synthetic": True,
                "enquiry_id": "SYN-BEN-SUP",
                "resident_ref": "RES-1001",
                "question": question,
            },
            as_of="2026-11-24",
        )
        return [row["page_id"] for row in result["citations"] if row["quoted"]]

    assert len(SUPPORT_POSITIVES) >= 20
    assert len(SUPPORT_NEGATIVES) >= 20
    true_positive = sum(1 for question in SUPPORT_POSITIVES if quoted(question) == ["housing-benefit-what"])
    false_positive = sum(1 for question in SUPPORT_NEGATIVES if "housing-benefit-what" in quoted(question))
    assert true_positive == len(SUPPORT_POSITIVES)
    assert false_positive == 0
    assert true_positive / len(SUPPORT_POSITIVES) == 1.0
    assert true_positive / (true_positive + false_positive) == 1.0
