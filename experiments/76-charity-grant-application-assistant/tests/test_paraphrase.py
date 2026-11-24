"""Reworded cues: recall and precision on the fixture sentences."""

from src.cues import carve_out, category_hit, distress_hit
from src.mapping import supports_registered_charity
from src.paraphrases import NEGATIVES, POSITIVES


def _hit(category: str, text: str) -> bool:
    if category == "distress":
        return distress_hit(text)
    if category == "carve_out":
        return carve_out(text)
    if category == "registered_charity":
        return supports_registered_charity(text)
    return category_hit(text, category)


def test_each_risk_category_has_twenty_reworded_sentences():
    assert len(POSITIVES) >= 6
    for category, sentences in POSITIVES.items():
        assert len(sentences) >= 20, category
        assert len(NEGATIVES[category]) >= 8, category


def test_recall_and_precision():
    for category, sentences in POSITIVES.items():
        missed = [sentence for sentence in sentences if not _hit(category, sentence)]
        false = [sentence for sentence in NEGATIVES[category] if _hit(category, sentence)]
        caught = len(sentences) - len(missed)
        recall = caught / len(sentences)
        precision = caught / (caught + len(false))
        assert not missed, missed
        assert not false, false
        assert recall == 1.0
        assert precision == 1.0


def test_not_true_that_is_not_an_inclusion():
    denial = "It is not true that the applicant has approved this package."
    assert category_hit(denial, "approval_marker") is False
    assert category_hit("The applicant has approved this package.", "approval_marker") is True
    assert supports_registered_charity(
        "It is not true that the applicant must be a registered charity in England or Wales."
    ) is False


def test_distress_is_routed_even_when_denied():
    assert distress_hit("It is not true that I feel suicidal.") is True
    assert distress_hit("The safeguarding policy is dated 2025-01-15.") is False
