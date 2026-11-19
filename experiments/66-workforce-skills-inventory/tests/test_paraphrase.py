"""Reworded variants. Exact phrases are not the only check.

Recall is caught divided by the variant count. A category at 0 is a failure.
Negated sentences are counted separately and must not be treated as hits.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from words import family_hit  # noqa: E402


def _set() -> dict:
    return json.loads((ROOT / "eval" / "paraphrases.json").read_text(encoding="utf-8"))


def test_each_risk_category_has_at_least_twenty_reworded_variants():
    data = _set()
    assert set(data) == {
        "distress",
        "misuse",
        "protected_or_health",
        "unsupplied",
        "objection",
        "injection",
    }
    for name, block in data.items():
        assert len(block["positive"]) >= 20, name
        missed = [sentence for sentence in block["positive"] if not family_hit(sentence, block["family"])]
        caught = len(block["positive"]) - len(missed)
        recall = caught / len(block["positive"])
        assert recall >= 0.9, f"{name} recall {caught}/{len(block['positive'])} missed {missed}"
        assert caught != 0


def test_negated_variants_are_not_counted_as_hits():
    data = _set()
    for name, block in data.items():
        leaked = [sentence for sentence in block["negative"] if family_hit(sentence, block["family"])]
        assert leaked == [], name
