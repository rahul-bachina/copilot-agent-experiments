"""Negation is not a match. Unrelated sentences are not evidence."""

from src.cues import category_hit, load_taxonomy, match_classes
from src.paraphrases import NEGATIVES, POSITIVES


NEGATIVES_FOR_CLASS = [
    "The committee minutes were agreed on Tuesday.",
    "It is not true that this is a freedom of information request.",
    "This is not a formal complaint.",
    "Nobody has made a subject access request.",
    "The safeguarding policy was reviewed in March.",
    "It is not true that this includes a subject access request.",
    "This is not an foi request.",
    "Please update the public notice board.",
    "The freedom of information publication scheme was updated in May.",
    "Do not log an article 15 request.",
]


def test_negation_does_not_count_as_inclusion():
    classes = load_taxonomy()["classes"]
    for sentence in (
        "It is not true that this includes a subject access request.",
        "This is not a freedom of information request.",
        "Nobody has made a formal complaint.",
        "It is not the case that a right of access to my personal data is enclosed.",
    ):
        assert match_classes(sentence, classes) == []


def test_unrelated_sentences_are_not_class_evidence():
    classes = load_taxonomy()["classes"]
    false = 0
    for sentence in NEGATIVES_FOR_CLASS:
        if match_classes(sentence, classes):
            false += 1
    assert false == 0
    caught = 0
    for sentence in POSITIVES["foi"] + POSITIVES["sar"]:
        rows = match_classes(sentence, classes)
        assert rows
        caught += 1
    precision = caught / (caught + false)
    assert precision == 1.0
    assert category_hit("foi", "It is not true that this is a freedom of information request.") is False
    assert category_hit("distress", "I am not safe tonight.") is True
