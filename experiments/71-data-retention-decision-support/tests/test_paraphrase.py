"""Reworded risk sentences. Recall and precision are reported from this file."""

import json
from pathlib import Path

from src.cues import category_match
from src.match import sentence_supports

ROOT = Path(__file__).resolve().parents[1]
PARAPHRASE = json.loads((ROOT / "eval" / "paraphrase_set.json").read_text(encoding="utf-8"))

MATCH_CATEGORIES = (
    "legal_hold",
    "open_matter",
    "personal_data",
    "distress",
    "injection",
    "legal_hold_negated",
    "open_matter_negated",
    "personal_data_negated",
    "distress_negated",
)


def _category_name(name: str) -> str:
    if name.endswith("_negated"):
        return name[: -len("_negated")]
    return name


def test_reworded_risk_recall_and_negation():
    for name in MATCH_CATEGORIES:
        row = PARAPHRASE[name]
        sentences = row["sentences"]
        assert len(sentences) >= 20, name
        category = _category_name(name)
        hits = [sentence for sentence in sentences if category_match(sentence, category)]
        if row["expect_match"]:
            missed = [sentence for sentence in sentences if sentence not in hits]
            assert not missed, missed
            assert len(hits) / len(sentences) == 1
        else:
            assert hits == [], hits


def test_support_precision_and_recall():
    positives = PARAPHRASE["support_positive"]["sentences"]
    negatives = PARAPHRASE["support_negative"]["sentences"]
    assert len(positives) >= 20
    assert len(negatives) >= 20
    true_positive = sum(1 for sentence in positives if sentence_supports(sentence)["supports"])
    false_positive = sum(1 for sentence in negatives if sentence_supports(sentence)["supports"])
    recall = true_positive / len(positives)
    precision = true_positive / (true_positive + false_positive) if true_positive or false_positive else 0
    assert recall == 1
    assert false_positive == 0
    assert precision == 1
    for sentence in negatives:
        row = sentence_supports(sentence)
        assert row["marked_acceptable"] is False
        assert row["sentence_stored"] is False
