"""Recall on reworded sentences. Exact strings are not the matcher."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from match import (  # noqa: E402
    cue_categories,
    injection_signals,
    leading_criteria,
    phrase_relation,
    plain_inclusion,
    superseded_affirmed,
    withdrawn_affirmed,
)

SET = json.loads((ROOT / "eval" / "paraphrase_set.json").read_text(encoding="utf-8"))


def matched(category: str, sentence: str) -> bool:
    if category == "distress":
        return cue_categories(sentence)["distress"]
    if category == "grievance":
        return cue_categories(sentence)["grievance"]
    if category == "withdrawn":
        return withdrawn_affirmed(sentence)
    if category == "superseded":
        return superseded_affirmed(sentence)
    if category == "injection":
        return bool(injection_signals(sentence))
    if category == "negation":
        return plain_inclusion(sentence, "consumer credit")
    if category == "leading":
        row = leading_criteria(sentence)
        return row["flagged"] is True and row["applied"] is False
    if category == "carve_out":
        return (
            plain_inclusion(sentence, "payment accounts") is False
            and plain_inclusion(sentence, "consumer credit") is False
            and phrase_relation(sentence, "payment accounts") in {"qualified", "denied"}
        )
    raise KeyError(category)


def score_paraphrases() -> dict:
    categories = {}
    for name, block in SET["categories"].items():
        sentences = block["sentences"]
        expect = block["expect"]
        hits = [sentence for sentence in sentences if matched(name, sentence) is expect]
        denial_recall = None
        if name == "negation":
            denied = [
                sentence
                for sentence in sentences
                if phrase_relation(sentence, "consumer credit") == "denied"
            ]
            denial_recall = len(denied) / len(sentences)
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
            "denial_recall": denial_recall,
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
        if row["denial_recall"] is not None:
            assert row["denial_recall"] == 1.0, name
