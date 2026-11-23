"""Recall and precision on reworded sentences. Not added to the case total."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.cues import biased, cue_categories, injection_signals  # noqa: E402
from src.match import addresses, relation, same_duty, theme_reading  # noqa: E402
from tests.paraphrases import (  # noqa: E402
    BIASED,
    CANONICAL,
    CARVE,
    DISTRESS,
    GRIEVANCE,
    INJECTION,
    NEGATION,
    NON_SUPPORT,
    REWORDED,
)

THEMES = ["keep_register", "review_register"]


def _rate(hits: int, total: int) -> float:
    return hits / total if total else 0.0


def score_paraphrases() -> dict:
    categories = {}

    def add(name: str, sentences: list[str], matched: list[bool], *, expect_match: bool) -> None:
        hits = sum(1 for item in matched if item)
        categories[name] = {
            "sentences": len(sentences),
            "matched": hits,
            "recall": _rate(hits, len(sentences)) if expect_match else None,
            "false_inclusions": 0 if expect_match else hits,
            "expect_match": expect_match,
        }

    add("distress", DISTRESS, [ "distress" in cue_categories(text) for text in DISTRESS ], expect_match=True)
    add("grievance", GRIEVANCE, [ "grievance" in cue_categories(text) for text in GRIEVANCE ], expect_match=True)
    add("injection", INJECTION, [ bool(injection_signals(text)) for text in INJECTION ], expect_match=True)
    add(
        "negation_not_inclusion",
        NEGATION,
        [ relation(CANONICAL, text) in {"exact", "near"} or theme_reading(text)["included"] for text in NEGATION ],
        expect_match=False,
    )
    add("reworded_obligation", REWORDED, [ same_duty(CANONICAL, text) for text in REWORDED ], expect_match=True)
    add(
        "carve_out",
        CARVE,
        [
            theme_reading(text)["qualified"]
            and theme_reading(text)["acceptable"] is False
            and addresses(text, THEMES)["supports"] is False
            and relation(CANONICAL, text) == "qualified_near"
            for text in CARVE
        ],
        expect_match=True,
    )
    add(
        "biased",
        BIASED,
        [ biased(text) and addresses(text, THEMES)["supports"] is False for text in BIASED ],
        expect_match=True,
    )
    positive = [addresses(text, THEMES)["supports"] is True for text in REWORDED]
    negative = [addresses(text, THEMES)["supports"] is True for text in NON_SUPPORT]
    true_positive = sum(1 for item in positive if item)
    false_positive = sum(1 for item in negative if item)
    false_negative = len(positive) - true_positive
    precision_denom = true_positive + false_positive
    recall_denom = true_positive + false_negative
    categories["control_support"] = {
        "positive_sentences": len(REWORDED),
        "negative_sentences": len(NON_SUPPORT),
        "true_positive": true_positive,
        "false_positive": false_positive,
        "false_negative": false_negative,
        "precision": _rate(true_positive, precision_denom),
        "recall": _rate(true_positive, recall_denom),
        "expect_match": True,
        "sentences": len(REWORDED),
        "matched": true_positive,
        "false_inclusions": false_positive,
    }
    return {
        "not_added_to_case_total": True,
        "categories": categories,
        "note": "Recall is on these fixture sentences. A wording that uses none of the stems is not claimed.",
    }


def test_each_risk_category_has_at_least_20_reworded_sentences():
    report = score_paraphrases()
    for name, row in report["categories"].items():
        count = row.get("sentences") or row.get("positive_sentences")
        assert count >= 20, name
        if row["expect_match"] and name != "control_support":
            assert row["recall"] == 1.0, name
        if name == "negation_not_inclusion":
            assert row["false_inclusions"] == 0
        if name == "control_support":
            assert row["precision"] == 1.0
            assert row["recall"] == 1.0
            assert row["false_positive"] == 0


def test_negation_phrase_is_not_an_inclusion():
    text = "It is not true that the firm must keep a register of obligations."
    reading = theme_reading(text)
    assert reading["included"] is False
    assert "keep_register" in reading["denied"]
    assert same_duty(CANONICAL, text) is False
