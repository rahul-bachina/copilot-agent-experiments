"""Reworded cues. Recall is the share actually caught. Negation is not a match."""

from src.cues import (
    affordability_hit,
    age_hit,
    bereavement_hit,
    complaint_hit,
    debt_hit,
    disability_hit,
    disconnection_hit,
    distress_hit,
    foi_hit,
    forged_confirmation_hit,
    grievance_hit,
    hardship_hit,
    human_request_hit,
    injection_hit,
    language_hit,
    leading_hit,
    medical_hit,
    mental_health_hit,
    prepayment_hit,
    safeguarding_hit,
    sar_hit,
    whistleblowing_hit,
)
from src.paraphrases import CATEGORIES

_FNS = {
    "medical": medical_hit,
    "age": age_hit,
    "disability": disability_hit,
    "financial_hardship": hardship_hit,
    "bereavement": bereavement_hit,
    "mental_health": mental_health_hit,
    "language": language_hit,
    "distress": distress_hit,
    "safeguarding": safeguarding_hit,
    "complaint": complaint_hit,
    "human_request": human_request_hit,
    "affordability": affordability_hit,
    "debt": debt_hit,
    "disconnection": disconnection_hit,
    "prepayment": prepayment_hit,
    "injection": injection_hit,
    "forged_confirmation": forged_confirmation_hit,
    "whistleblowing": whistleblowing_hit,
    "grievance": grievance_hit,
    "sar": sar_hit,
    "foi": foi_hit,
    "leading_criterion": leading_hit,
}


def _policy(text: str) -> bool:
    return any((
        safeguarding_hit(text),
        whistleblowing_hit(text),
        grievance_hit(text),
        mental_health_hit(text),
        disability_hit(text),
        prepayment_hit(text),
        complaint_hit(text),
    ))


def _unrelated(text: str) -> bool:
    return any(fn(text) for fn in _FNS.values())


def _hit(kind: str, text: str) -> bool:
    if kind == "policy_title":
        return _policy(text)
    if kind == "unrelated":
        return _unrelated(text)
    return _FNS[kind](text)


def test_each_risk_category_has_at_least_twenty_rewordings_and_honest_recall():
    assert len([name for name, row in CATEGORIES.items() if row["expect_match"]]) >= 20
    for name, row in CATEGORIES.items():
        sentences = list(row["sentences"])
        assert len(sentences) >= 20, name
        matched = [text for text in sentences if _hit(row["kind"], text)]
        if row["expect_match"]:
            recall = len(matched) / len(sentences)
            assert recall == 1.0, (name, recall, [text for text in sentences if text not in matched])
        else:
            assert matched == [], (name, matched)


def test_negation_is_not_an_instruction_and_a_policy_title_is_not_a_personal_cue():
    assert injection_hit("It is not true that the message includes ignore previous instructions.") is False
    assert complaint_hit("It is not true that this is a complaint.") is False
    assert distress_hit("I am not coping with the letters.") is True
    assert safeguarding_hit("Please read the safeguarding policy.") is False
    assert prepayment_hit("The prepayment policy is a document.") is False
