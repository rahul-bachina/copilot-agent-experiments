"""Reworded cues. Recall is the share actually caught. Negation is not a match."""

from src.cues import category_hit, distress_hit, grievance_hit, safeguarding_hit, whistleblowing_hit
from src.paraphrases import CATEGORIES


def _hit(kind: str, text: str) -> bool:
    if kind == "distress":
        return distress_hit(text)
    if kind == "safeguarding":
        return safeguarding_hit(text)
    if kind == "whistleblowing":
        return whistleblowing_hit(text)
    if kind == "grievance":
        return grievance_hit(text)
    if kind == "injection":
        return category_hit(text, "embedded_instruction")
    if kind == "forged_approval":
        return category_hit(text, "forged_approval")
    if kind == "leading_criterion":
        return category_hit(text, "leading_criterion")
    return any(
        (
            distress_hit(text),
            safeguarding_hit(text),
            whistleblowing_hit(text),
            grievance_hit(text),
            category_hit(text, "embedded_instruction"),
            category_hit(text, "forged_approval"),
            category_hit(text, "leading_criterion"),
        )
    )


def test_each_risk_category_has_at_least_twenty_rewordings_and_honest_recall():
    for name, row in CATEGORIES.items():
        sentences = list(row["sentences"])
        assert len(sentences) >= 20, name
        matched = [text for text in sentences if _hit(row["kind"], text)]
        if row["expect_match"]:
            recall = len(matched) / len(sentences)
            assert recall == 1.0, (name, recall, [text for text in sentences if text not in matched])
        else:
            assert matched == [], (name, matched)


def test_a_policy_title_is_not_a_personal_cue_and_negation_is_not_an_instruction():
    assert safeguarding_hit("See the safeguarding policy for the connector.") is False
    assert category_hit(
        "It is not true that the error includes ignore previous instructions.",
        "embedded_instruction",
    ) is False
    assert distress_hit("I am not coping with the failed run.") is True
