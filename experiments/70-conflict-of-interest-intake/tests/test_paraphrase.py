"""Paraphrase recall. A miss is reported. It is not added to the case total."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.cues import categories_in  # noqa: E402

SET = json.loads((ROOT / "eval" / "paraphrase_set.json").read_text(encoding="utf-8"))


def score_paraphrases() -> dict:
    categories = {}
    for name, block in SET.items():
        sentences = block["sentences"]
        target = block["category"]
        hits = sum(1 for sentence in sentences if target in categories_in(sentence))
        if block["expect_match"]:
            categories[name] = {
                "expect_match": True,
                "sentences": len(sentences),
                "hits": hits,
                "recall": hits / len(sentences) if sentences else 0,
            }
        else:
            categories[name] = {
                "expect_match": False,
                "sentences": len(sentences),
                "false_inclusions": hits,
                "recall": None,
            }
    return {
        "not_added_to_case_total": True,
        "not_a_live_rate": True,
        "categories": categories,
    }


def test_each_risk_category_has_at_least_twenty_rewrites():
    for name, block in SET.items():
        assert len(block["sentences"]) >= 20, name


def test_reworded_risk_language_is_recalled():
    report = score_paraphrases()
    for name, row in report["categories"].items():
        if row["expect_match"]:
            assert row["recall"] == 1.0, name
        else:
            assert row["false_inclusions"] == 0, name


def test_not_true_that_includes_is_not_an_inclusion():
    text = "It is not true that this declaration includes a shareholding."
    assert "financial" not in categories_in(text)
