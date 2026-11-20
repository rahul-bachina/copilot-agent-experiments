"""Recall on reworded sentences. This is not a live rate."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from cues import biased, cue_categories, injection_codes  # noqa: E402
from paraphrases import (  # noqa: E402
    BIASED,
    DISTRESS,
    GRIEVANCE,
    INSTRUCTIONS,
    LOG,
    NEGATION,
    POSITIVE_MUST,
    QUALIFIED,
    SHOULD,
)
from statements import assess_sentence  # noqa: E402


def _hit(category: str, sentence: str) -> bool:
    if category == "positive_must":
        row = assess_sentence(sentence, LOG)
        return row["confidence"] == "high" and row["obligation_affirmed"] is True and row["control_met"] is False
    if category == "negation_not_inclusion":
        row = assess_sentence(sentence, LOG)
        return row["included"] is False and row["obligation_affirmed"] is False and (
            row["strength"] == "denied" or row["opposes"] is True
        )
    if category == "should_not_must":
        row = assess_sentence(sentence, LOG)
        return row["strength"] == "should" and row["confidence"] == "medium" and row["obligation_affirmed"] is False
    if category == "qualification_weakens":
        row = assess_sentence(sentence, LOG)
        return row["qualified"] is True and row["confidence"] == "low" and row["obligation_affirmed"] is False
    if category == "distress_route":
        return "distress" in cue_categories(sentence)
    if category == "grievance_route":
        return "grievance" in cue_categories(sentence)
    if category == "embedded_instruction":
        return bool(injection_codes(sentence))
    if category == "biased_criteria":
        row = assess_sentence(sentence, LOG)
        return biased(sentence) and row["obligation_affirmed"] is False and row["acceptable"] is False
    raise KeyError(category)


CATEGORIES = {
    "positive_must": {"sentences": POSITIVE_MUST, "expect_match": True},
    "negation_not_inclusion": {"sentences": NEGATION, "expect_match": True},
    "should_not_must": {"sentences": SHOULD, "expect_match": True},
    "qualification_weakens": {"sentences": QUALIFIED, "expect_match": True},
    "distress_route": {"sentences": DISTRESS, "expect_match": True},
    "grievance_route": {"sentences": GRIEVANCE, "expect_match": True},
    "embedded_instruction": {"sentences": INSTRUCTIONS, "expect_match": True},
    "biased_criteria": {"sentences": BIASED, "expect_match": True},
}


def score_paraphrases() -> dict:
    categories = {}
    for name, spec in CATEGORIES.items():
        sentences = spec["sentences"]
        hits = sum(1 for sentence in sentences if _hit(name, sentence))
        false_inclusions = 0
        if name == "negation_not_inclusion":
            false_inclusions = sum(
                1 for sentence in sentences if assess_sentence(sentence, LOG)["included"] is True
            )
        categories[name] = {
            "sentences": len(sentences),
            "hits": hits,
            "recall": hits / len(sentences) if sentences else 0,
            "expect_match": spec["expect_match"],
            "false_inclusions": false_inclusions,
        }
    return {
        "not_a_live_recall_rate": True,
        "not_added_to_case_total": True,
        "categories": categories,
    }


def test_reworded_recall_is_complete_on_the_fixture():
    report = score_paraphrases()
    assert report["not_added_to_case_total"] is True
    for name, row in report["categories"].items():
        assert row["sentences"] >= 20, name
        assert row["recall"] == 1.0, name
        assert row["false_inclusions"] == 0, name
