"""Reworded cues: recall and precision on the fixture sentences."""

from src.cues import carve_out, category_hit, distress_hit
from src.paraphrases import NEGATIVES, POSITIVES


def _hit(category: str, text: str) -> bool:
    if category == "distress":
        return distress_hit(text)
    if category == "carve_out":
        return carve_out(text)
    return category_hit(text, category)


def test_each_risk_category_has_twenty_reworded_sentences():
    assert len(POSITIVES) >= 8
    for category, sentences in POSITIVES.items():
        assert len(sentences) >= 20, category
        assert len(NEGATIVES[category]) >= 8, category


def test_recall_and_precision():
    for category, sentences in POSITIVES.items():
        caught = sum(1 for sentence in sentences if _hit(category, sentence))
        missed = [sentence for sentence in sentences if not _hit(category, sentence)]
        false = [sentence for sentence in NEGATIVES[category] if _hit(category, sentence)]
        recall = caught / len(sentences)
        precision = caught / (caught + len(false))
        assert not missed, missed
        assert not false, false
        assert recall == 1.0
        assert precision == 1.0


def test_not_true_that_is_not_an_inclusion():
    denial = "It is not true that the preparer approved their own request."
    assert category_hit(denial, "self_approval") is False
    assert category_hit("The preparer approved their own request.", "self_approval") is True
