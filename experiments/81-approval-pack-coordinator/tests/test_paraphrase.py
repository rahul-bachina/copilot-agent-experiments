"""Recall and precision for reworded cues and for evidence support."""

from src.cues import category_hit
from src.negate import affirmed
from src.paraphrases import NEGATIVES, POSITIVES, SUPPORT_NEGATIVES, SUPPORT_PHRASE, SUPPORT_POSITIVES


def test_each_risk_category_recalls_at_least_twenty_rewordings():
    for name, rows in POSITIVES.items():
        assert len(rows) >= 20, name
        hits = sum(1 for row in rows if category_hit(row, name))
        recall = hits / len(rows)
        assert recall == 1.0, (name, hits, len(rows))
        false = sum(1 for row in NEGATIVES if category_hit(row, name))
        assert false == 0, name
        precision = hits / (hits + false)
        assert precision == 1.0


def test_support_does_not_count_a_negation_or_an_unrelated_sentence():
    assert len(SUPPORT_POSITIVES) >= 20
    assert len(SUPPORT_NEGATIVES) >= 20
    true_positives = sum(1 for row in SUPPORT_POSITIVES if affirmed(row, SUPPORT_PHRASE))
    false_positives = sum(1 for row in SUPPORT_NEGATIVES if affirmed(row, SUPPORT_PHRASE))
    assert true_positives == len(SUPPORT_POSITIVES)
    assert false_positives == 0
    recall = true_positives / len(SUPPORT_POSITIVES)
    precision = true_positives / (true_positives + false_positives)
    assert recall == 1.0
    assert precision == 1.0
    assert affirmed("It is not true that the quote includes Northfold Supplies.", SUPPORT_PHRASE) is False
    assert affirmed("The quote includes Northfold Supplies.", SUPPORT_PHRASE) is True
