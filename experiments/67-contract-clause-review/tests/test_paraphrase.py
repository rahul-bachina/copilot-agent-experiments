"""Recall on reworded sentences. Exact strings are not the matcher."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cues import (  # noqa: E402
    AUTO_RENEW_RES,
    any_pattern_affirmed,
    cue_categories,
    death_pi,
    injection_signals,
)

SET = json.loads((ROOT / "eval" / "paraphrase_set.json").read_text(encoding="utf-8"))


def matched(category: str, sentence: str) -> bool:
    if category.startswith("death_pi"):
        return bool(death_pi(sentence)["affirmed"])
    if category == "distress":
        return cue_categories(sentence)["distress"]
    if category == "grievance_or_disclosure":
        return cue_categories(sentence)["grievance"]
    if category.startswith("injection"):
        return bool(injection_signals(sentence))
    if category.startswith("auto_renewal"):
        return bool(any_pattern_affirmed(sentence, AUTO_RENEW_RES))
    raise KeyError(category)


def score_paraphrases() -> dict:
    categories = {}
    for name, block in SET["categories"].items():
        sentences = block["sentences"]
        expect = block["expect"]
        hits = [sentence for sentence in sentences if matched(name, sentence) is expect]
        if expect:
            recall = len(hits) / len(sentences)
            false_inclusions = None
        else:
            recall = None
            false_inclusions = len(sentences) - len(hits)
        categories[name] = {
            "sentences": len(sentences),
            "expect_match": expect,
            "correct": len(hits),
            "recall": recall,
            "false_inclusions": false_inclusions,
        }
    return {
        "label": "Reworded fixture sentences. Not a live recall rate.",
        "not_added_to_case_total": True,
        "categories": categories,
    }


def test_each_risk_category_has_at_least_20_reworded_sentences():
    for name, block in SET["categories"].items():
        assert len(block["sentences"]) >= 20, name
        assert len(block["sentences"]) == len(set(block["sentences"]))


def test_positive_recall_and_negation_controls():
    report = score_paraphrases()
    for name, row in report["categories"].items():
        if row["expect_match"]:
            assert row["recall"] == 1.0, name
        else:
            assert row["false_inclusions"] == 0, name
