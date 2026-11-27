"""Hallucinated claims are not support. Precision and recall are both reported."""

from src.claims import labelled_claims
from src.grounding import is_supported, score_claims, supports_claim


def test_labelled_set_has_negative_controls():
    rows = labelled_claims()
    positives = [row for row in rows if row["supported"]]
    negatives = [row for row in rows if not row["supported"]]
    assert len(positives) >= 20
    assert len(negatives) >= 20
    score = score_claims(rows)
    assert score["precision"] == 1.0
    assert score["recall"] == 1.0
    assert score["false_positive"] == 0
    assert score["false_negative"] == 0
    assert score["not_added_to_case_total"] is True


def test_a_denial_is_not_the_positive_claim():
    assert supports_claim("I want to move.", "I do not want to move.") is False
    assert supports_claim("want to move", "I do not want to move.") is False
    assert supports_claim("I do not want to move.", "I do not want to move.") is True


def test_diagnosis_words_are_not_inferred():
    line = "I want to stay in my own home."
    for claim in (
        "The adult is eligible for care.",
        "The person has dementia.",
        "high risk of neglect",
        "The person lacks capacity.",
    ):
        assert supports_claim(claim, line) is False


def test_it_is_not_true_that_a_sentence_includes_a_diagnosis():
    text = "It is not true that the transcript includes a diagnosis of dementia."
    assert supports_claim("diagnosis of dementia", text) is False


def test_inferred_join_needs_real_spans():
    lines = {1: "I want to stay in my own home.", 2: "I observed that the hallway was clear."}
    joined = {
        "inferred": True,
        "source_lines": [1, 2],
        "parts": ["I want to stay", "the hallway was clear"],
        "text": "I want to stay; the hallway was clear",
    }
    invented = {
        "inferred": True,
        "source_lines": [1],
        "parts": ["The adult is eligible for care."],
        "text": "The adult is eligible for care.",
    }
    assert is_supported(joined, lines) is True
    assert is_supported(invented, lines) is False
