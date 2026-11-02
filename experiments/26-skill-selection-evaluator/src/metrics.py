"""Precision, recall, and confusable skill pairs.

Precision and recall are computed on the labelled utterances only.
A pair is confusable when the descriptions overlap, a trigger phrase is
shared, or the labelled set shows a swap. The pair is a finding. It is
not a change to either skill.
"""

from __future__ import annotations

from typing import Any

try:
    from .skill_parse import Skill
    from .tokens import normalise_phrase
except ImportError:  # python src/report.py puts this directory on sys.path
    from skill_parse import Skill
    from tokens import normalise_phrase

JACCARD_THRESHOLD = 0.45
MIN_TOKENS_FOR_OVERLAP = 4

CLASSES_RESERVED = ("none", "human")


def per_class(utterances: list[dict[str, Any]], skill_ids: list[str]) -> list[dict[str, Any]]:
    classes = list(skill_ids) + list(CLASSES_RESERVED)
    rows = []
    for name in classes:
        tp = fp = fn = 0
        for item in utterances:
            expected = item["expected_class"]
            predicted = item["predicted_class"]
            if expected == name and predicted == name:
                tp += 1
            elif predicted == name and expected != name:
                fp += 1
            elif expected == name and predicted != name:
                fn += 1
        support = tp + fn
        predicted_count = tp + fp
        rows.append(
            {
                "class": name,
                "kind": "route" if name in CLASSES_RESERVED else "skill",
                "true_positive": tp,
                "false_positive": fp,
                "false_negative": fn,
                "support": support,
                "precision": _percent(tp, predicted_count),
                "recall": _percent(tp, support),
            }
        )
    return rows


def agreement(utterances: list[dict[str, Any]]) -> dict[str, Any]:
    labelled = [item for item in utterances if item.get("expected")]
    correct = sum(1 for item in labelled if item["predicted"] == item["expected"])
    total = len(labelled)
    return {
        "correct": correct,
        "labelled": total,
        "percent": _percent(correct, total),
    }


def confusable_pairs(skills: list[Skill], utterances: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id = {skill.id: skill for skill in skills}
    found: dict[tuple[str, str], dict[str, Any]] = {}

    def pair(left: str, right: str) -> dict[str, Any]:
        key = tuple(sorted((left, right)))
        if key not in found:
            left_tokens = by_id[key[0]].tokens if key[0] in by_id else set()
            right_tokens = by_id[key[1]].tokens if key[1] in by_id else set()
            found[key] = {
                "skills": list(key),
                "reasons": [],
                "jaccard": _jaccard(left_tokens, right_tokens),
                "shared_triggers": [],
                "swaps": 0,
            }
        return found[key]

    ordered = list(skills)
    for index, left in enumerate(ordered):
        for right in ordered[index + 1 :]:
            shared = _shared_triggers(left, right)
            overlap = _overlaps(left, right)
            if shared or overlap:
                row = pair(left.id, right.id)
                if shared:
                    row["shared_triggers"] = shared
                    row["reasons"].append("shared_trigger")
                if overlap:
                    row["reasons"].append("description_overlap")
    for item in utterances:
        expected = item["expected_class"]
        predicted = item["predicted_class"]
        if expected == predicted:
            continue
        if expected in by_id and predicted in by_id:
            row = pair(expected, predicted)
            row["swaps"] += 1
            if "labelled_swap" not in row["reasons"]:
                row["reasons"].append("labelled_swap")
    rows = list(found.values())
    for row in rows:
        row["reasons"] = sorted(set(row["reasons"]))
        row["shared_triggers"] = sorted(set(row["shared_triggers"]))
        row["jaccard"] = round(row["jaccard"], 3)
    rows.sort(key=lambda row: (row["skills"][0], row["skills"][1]))
    return rows


def _shared_triggers(left: Skill, right: Skill) -> list[str]:
    right_norm = {normalise_phrase(trigger) for trigger in right.triggers}
    shared = []
    for trigger in left.triggers:
        phrase = normalise_phrase(trigger)
        if phrase and phrase in right_norm:
            shared.append(trigger)
    return shared


def _overlaps(left: Skill, right: Skill) -> bool:
    if len(left.tokens) < MIN_TOKENS_FOR_OVERLAP or len(right.tokens) < MIN_TOKENS_FOR_OVERLAP:
        return False
    return _jaccard(left.tokens, right.tokens) >= JACCARD_THRESHOLD


def _jaccard(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    union = left | right
    if not union:
        return 0.0
    return len(left & right) / len(union)


def _percent(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return round(100 * numerator / denominator, 1)
