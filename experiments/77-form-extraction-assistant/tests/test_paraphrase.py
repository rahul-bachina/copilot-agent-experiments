"""Reworded distress, safeguarding, and whistleblowing cues."""

from src.cues import category_hit
from src.paraphrases import NEGATIVES, POSITIVES


def _scores(category: str) -> dict:
    positives = POSITIVES[category]
    negatives = NEGATIVES[category]
    true_positives = sum(1 for text in positives if category_hit(text, category))
    false_negatives = len(positives) - true_positives
    false_positives = sum(1 for text in negatives if category_hit(text, category))
    recall = true_positives / len(positives)
    precision = true_positives / (true_positives + false_positives)
    return {
        "sentences": len(positives),
        "negatives": len(negatives),
        "recall": recall,
        "precision": precision,
        "false_inclusions": false_positives,
        "false_negatives": false_negatives,
    }


def test_each_route_category_has_recall_and_precision():
    for category in ("distress", "safeguarding", "whistleblowing"):
        row = _scores(category)
        assert row["sentences"] >= 20
        assert row["negatives"] >= 20
        assert row["recall"] == 1.0
        assert row["precision"] == 1.0
        assert row["false_inclusions"] == 0


def test_negation_does_not_count_as_the_cue():
    assert category_hit("It is not true that this form includes a safeguarding concern.", "safeguarding") is False
    assert category_hit("It is not true that I am suicidal.", "distress") is False
    assert category_hit("A grievance does not appear on this permit.", "whistleblowing") is False
    assert category_hit("I do not feel safe at home.", "safeguarding") is True
    assert category_hit("I am not safe at the site tonight.", "safeguarding") is True
