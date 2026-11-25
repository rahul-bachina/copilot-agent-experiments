"""Recall and precision for reworded cues. Not a model score."""

from src.cues import (
    carve_out_affirmed,
    category_hit,
    distress_hit,
    grievance_hit,
    safeguarding_hit,
    whistleblowing_hit,
)
from src.material import compare_texts
from src.paraphrases import ALIGNMENT_PAIRS, NEGATIVES, OBLIGATION_NEGATIVES, OBLIGATION_PAIRS, POSITIVES
from src.align import score_pairs

_SENSITIVE = {
    "distress": distress_hit,
    "safeguarding": safeguarding_hit,
    "whistleblowing": whistleblowing_hit,
    "grievance": grievance_hit,
}


def _hit(category: str, text: str) -> bool:
    if category in _SENSITIVE:
        return _SENSITIVE[category](text)
    if category == "carve_out_included":
        return carve_out_affirmed(text)
    return category_hit(text, category)


def test_each_risk_category_has_twenty_reworded_sentences():
    for name, rows in POSITIVES.items():
        assert len(rows) >= 20, name
        assert len(NEGATIVES[name]) >= 20, name


def test_reworded_cues_are_recalled_and_negatives_are_not():
    for name, rows in POSITIVES.items():
        matched = sum(1 for text in rows if _hit(name, text))
        recall = matched / len(rows)
        assert recall == 1.0, (name, matched, len(rows))
        false = sum(1 for text in NEGATIVES[name] if _hit(name, text))
        assert false == 0, (name, false)


def test_obligation_rewordings_and_negative_controls():
    assert len(OBLIGATION_PAIRS) >= 20
    assert len(OBLIGATION_NEGATIVES) >= 20
    caught = 0
    for left, right in OBLIGATION_PAIRS:
        diff = compare_texts(left, right, question=None)
        if "obligation_strength" in diff["flags"]:
            caught += 1
    assert caught / len(OBLIGATION_PAIRS) == 1.0
    false = 0
    for left, right in OBLIGATION_NEGATIVES:
        diff = compare_texts(left, right, question=None)
        if "obligation_strength" in diff["flags"]:
            false += 1
    assert false == 0


def test_alignment_precision_and_recall():
    positives = [row for row in ALIGNMENT_PAIRS if row["expect_aligned"]]
    negatives = [row for row in ALIGNMENT_PAIRS if not row["expect_aligned"]]
    assert len(positives) >= 20
    assert len(negatives) >= 20
    score = score_pairs(ALIGNMENT_PAIRS)
    assert score["recall"] == 1.0
    assert score["precision"] == 1.0
    assert score["false_positive"] == 0
    assert score["false_negative"] == 0
