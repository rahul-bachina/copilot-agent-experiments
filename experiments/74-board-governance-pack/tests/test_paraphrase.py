"""Reworded cues. Recall and precision are reported on the fixture sentences."""

from src.cues import category_hit, distress_hit
from src.paraphrases import NEGATIVES, POSITIVES


def _hit(category: str, text: str) -> bool:
    if category == "distress":
        return distress_hit(text)
    return category_hit(text, category)


def test_each_risk_category_has_at_least_twenty_rewordings():
    for name, sentences in POSITIVES.items():
        assert len(sentences) >= 20, name
        assert len(NEGATIVES[name]) >= 8, name


def test_reworded_recall_and_precision():
    for name, sentences in POSITIVES.items():
        caught = sum(1 for sentence in sentences if _hit(name, sentence))
        false = [sentence for sentence in NEGATIVES[name] if _hit(name, sentence)]
        assert caught == len(sentences), name
        assert false == [], false
        recall = caught / len(sentences)
        precision = caught / (caught + len(false))
        assert recall == 1.0
        assert precision == 1.0


def test_negation_is_not_an_inclusion_except_distress():
    denied_grant = "It is not true that this paper is about community grants."
    denied_interest = "It is not true that I declare an interest in the supplier."
    denied_approval = "It is not true that the company secretary has approved this pack."
    denied_distress = "It is not true that I cannot cope with this meeting."
    assert category_hit(denied_grant, "outside_remit") is False
    assert category_hit(denied_interest, "conflict_declared") is False
    assert category_hit(denied_approval, "approval_marker") is False
    assert distress_hit(denied_distress) is True


def test_a_qualification_after_acceptable_wording_is_not_acceptable():
    from src.cues import carve_out

    assert carve_out("The cover sheet is complete except for the equality implications.") is True
    assert carve_out("The cover sheet is complete.") is False
