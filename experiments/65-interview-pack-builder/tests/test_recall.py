"""Paraphrase recall. Idioms with none of the concept words stay in the denominator."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from distress import distress_present  # noqa: E402
from intents import intents_in  # noqa: E402
from probes import categories_in, occupational_requirement  # noqa: E402
from variants import NEGATIVES, VARIANTS  # noqa: E402

_OTHER = {"sex", "sexual_orientation", "gender_reassignment", "race"}


def caught(category: str, text: str) -> bool:
    if category == "distress":
        return distress_present(text)
    if category == "occupational_requirement":
        return occupational_requirement(text)
    if category == "prohibited_action":
        return bool(intents_in(text))
    if category == "other_protected":
        return bool(set(categories_in(text)) & _OTHER)
    return category in categories_in(text)


def recall_report() -> dict:
    categories = {}
    for category, rows in VARIANTS.items():
        misses = [text for text, _expect in rows if not caught(category, text)]
        hits = len(rows) - len(misses)
        categories[category] = {
            "caught": hits,
            "variants": len(rows),
            "recall": round(hits / len(rows), 3),
            "misses": misses,
        }
    return {
        "label": "PARAPHRASE RECALL. Not a model score. Idioms that miss are listed.",
        "not_a_model_evaluation": True,
        "categories": categories,
    }


def test_each_risk_category_catches_at_least_twenty_reworded_variants():
    report = recall_report()
    for category, row in report["categories"].items():
        assert row["variants"] >= 20, category
        assert row["caught"] >= 20, category
        assert row["recall"] >= 0.8, category
        assert row["misses"], category


def test_negated_and_right_to_work_sentences_are_not_hits():
    for category, rows in NEGATIVES.items():
        for text in rows:
            assert caught(category, text) is False, text


def test_a_denied_distress_cue_is_still_routed():
    assert distress_present("It is not true that I am suicidal.") is True
