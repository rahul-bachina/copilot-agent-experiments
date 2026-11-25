"""Align clauses across two versions.

Moved, split, and merged clauses are reported. Renumbering and reformatting
are not substantive. A real difference inside similar wording is not hidden.
A low-confidence alignment is flagged and is not treated as certain.
Duplicate clauses that disagree are both cited. Neither is chosen.

Token folding uses Experiment 33 normalise, which Experiment 38 also uses.
Experiment 38 compare() is not called.
"""

from __future__ import annotations

import re
from typing import Any

if __package__ in {None, ""}:
    from siblings import neighbours
else:
    from .siblings import neighbours

HIGH = 0.84
LOW = 0.42
SPLIT = 0.75


def tokens(text: str) -> list[str]:
    folded = neighbours()["normalise"](text or "")
    return re.findall(r"[a-z0-9]+", folded)


def jaccard(left: list[str], right: list[str]) -> float:
    a = set(left)
    b = set(right)
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def format_key(text: str) -> str:
    folded = neighbours()["normalise"](text or "")
    folded = re.sub(r"^(?:clause\s+)?\d+(?:\.\d+)*\s+", "", folded)
    folded = re.sub(r"[^a-z0-9%£ ]+", " ", folded)
    return re.sub(r"\s+", " ", folded).strip()


def align(baseline: list[dict], other: list[dict]) -> list[dict]:
    """Return one row per alignment. Classes do not overlap."""

    base = [_prepared(clause, index) for index, clause in enumerate(baseline)]
    alt = [_prepared(clause, index) for index, clause in enumerate(other)]
    rows: list[dict] = []
    used_base: set[int] = set()
    used_alt: set[int] = set()

    for side, pool, used in (("baseline", base, used_base), ("other", alt, used_alt)):
        groups: dict[str, list[dict]] = {}
        for clause in pool:
            if not clause["duplicate_key"]:
                continue
            groups.setdefault(clause["duplicate_key"], []).append(clause)
        for key, group in groups.items():
            bodies = {clause["format_key"] for clause in group}
            if len(group) < 2 or len(bodies) < 2:
                continue
            for clause in group:
                used.add(clause["index"])
            rows.append(_duplicate_row(side, key, group))

    for clause in base:
        if clause["index"] in used_base or not clause["clause_id"]:
            continue
        matches = [
            item for item in alt
            if item["index"] not in used_alt and item["clause_id"] == clause["clause_id"]
        ]
        if len(matches) != 1:
            continue
        _link(rows, clause, matches[0], used_base, used_alt, how="clause_id")

    for clause in base:
        if clause["index"] in used_base:
            continue
        exact = [
            item for item in alt
            if item["index"] not in used_alt and item["format_key"] and item["format_key"] == clause["format_key"]
        ]
        if len(exact) != 1:
            continue
        _link(rows, clause, exact[0], used_base, used_alt, how="same_text")

    _overlap(rows, base, alt, used_base, used_alt, minimum=HIGH)
    _splits_and_merges(rows, base, alt, used_base, used_alt)
    _overlap(rows, base, alt, used_base, used_alt, minimum=LOW)

    for clause in base:
        if clause["index"] not in used_base:
            rows.append(_single("deleted", clause, None))
    for clause in alt:
        if clause["index"] not in used_alt:
            rows.append(_single("added", None, clause))

    rows.sort(key=lambda row: (row["order"], row["row_id"]))
    for number, row in enumerate(rows, start=1):
        row["row_id"] = f"r{number}"
    return rows


def score_pairs(pairs: list[dict]) -> dict:
    """Precision and recall for expected alignments. A pair is one case."""

    true_positive = 0
    false_positive = 0
    false_negative = 0
    for pair in pairs:
        aligned = _pair_aligned(pair["left"], pair["right"])
        expect = bool(pair["expect_aligned"])
        if aligned and expect:
            true_positive += 1
        elif aligned and not expect:
            false_positive += 1
        elif expect and not aligned:
            false_negative += 1
    precision = _rate(true_positive, true_positive + false_positive)
    recall = _rate(true_positive, true_positive + false_negative)
    return {
        "true_positive": true_positive,
        "false_positive": false_positive,
        "false_negative": false_negative,
        "precision": precision,
        "recall": recall,
        "positives": sum(1 for pair in pairs if pair["expect_aligned"]),
        "negatives": sum(1 for pair in pairs if not pair["expect_aligned"]),
        "not_a_model_evaluation": True,
    }


def _pair_aligned(left: str, right: str) -> bool:
    rows = align(
        [{"clause_id": "a", "number": "1", "heading": "A", "text": left}],
        [{"clause_id": "b", "number": "1", "heading": "B", "text": right}],
    )
    return any(row["change_class"] not in {"added", "deleted", "duplicate_conflict"} for row in rows)


def _prepared(clause: dict, index: int) -> dict:
    text = clause.get("text") if isinstance(clause.get("text"), str) else ""
    number = clause.get("number") if isinstance(clause.get("number"), str) else ""
    heading = clause.get("heading") if isinstance(clause.get("heading"), str) else ""
    clause_id = clause.get("clause_id") if isinstance(clause.get("clause_id"), str) else ""
    duplicate_key = ""
    if clause.get("duplicate_conflict") and clause_id:
        duplicate_key = f"id:{clause_id}"
    elif clause.get("duplicate_conflict") and number:
        duplicate_key = f"number:{number}"
    return {
        "index": index,
        "clause_id": clause_id,
        "number": number,
        "heading": heading,
        "text": text,
        "tokens": tokens(text),
        "format_key": format_key(text),
        "duplicate_key": duplicate_key,
        "citation": clause.get("citation") or {},
        "unparseable": clause.get("unparseable") is True,
    }


def _link(rows, left, right, used_base, used_alt, *, how: str, score: float | None = None) -> None:
    used_base.add(left["index"])
    used_alt.add(right["index"])
    if score is None:
        score = jaccard(left["tokens"], right["tokens"])
    same = bool(left["format_key"]) and left["format_key"] == right["format_key"]
    low = how == "overlap" and score < HIGH
    if how == "clause_id" and score < 0.35:
        low = True
    if same and left["number"] != right["number"]:
        change = "renumbered"
    elif same and left["index"] != right["index"]:
        change = "moved"
    elif same and left["text"] != right["text"]:
        change = "reformatted"
    elif same:
        change = "unchanged"
    else:
        change = "changed"
    if low and change == "changed":
        change = "low_confidence"
    rows.append(
        {
            "row_id": f"b{left['index']}-o{right['index']}",
            "change_class": change,
            "substantive": change in {"changed", "low_confidence"},
            "low_confidence": low,
            "hidden_inside_reformat": False,
            "also_renumbered": left["number"] != right["number"] and change != "renumbered",
            "how": how,
            "score": round(score, 4),
            "order": left["index"],
            "baseline": _cite(left),
            "other": _cite(right),
            "chosen_text": None,
            "material": [],
        }
    )


def _overlap(rows, base, alt, used_base, used_alt, *, minimum: float) -> None:
    for clause in base:
        if clause["index"] in used_base:
            continue
        best = None
        best_score = 0.0
        for item in alt:
            if item["index"] in used_alt:
                continue
            score = jaccard(clause["tokens"], item["tokens"])
            if score > best_score:
                best = item
                best_score = score
        if best is None or best_score < minimum:
            continue
        if minimum == HIGH and best_score < HIGH:
            continue
        _link(rows, clause, best, used_base, used_alt, how="overlap", score=best_score)


def _splits_and_merges(rows, base, alt, used_base, used_alt) -> None:
    for clause in base:
        if clause["index"] in used_base:
            continue
        window = _best_window(clause, alt, used_alt)
        if window is None:
            continue
        for item in window:
            used_alt.add(item["index"])
        used_base.add(clause["index"])
        score = jaccard(clause["tokens"], _concat(window))
        rows.append(
            {
                "row_id": f"split-{clause['index']}",
                "change_class": "split",
                "substantive": False,
                "low_confidence": score < 0.88,
                "hidden_inside_reformat": False,
                "also_renumbered": False,
                "how": "split",
                "score": round(score, 4),
                "order": clause["index"],
                "baseline": _cite(clause),
                "other": [_cite(item) for item in window],
                "chosen_text": None,
                "material": [],
            }
        )
    for item in alt:
        if item["index"] in used_alt:
            continue
        window = _best_window(item, base, used_base)
        if window is None:
            continue
        for clause in window:
            used_base.add(clause["index"])
        used_alt.add(item["index"])
        score = jaccard(_concat(window), item["tokens"])
        rows.append(
            {
                "row_id": f"merge-{item['index']}",
                "change_class": "merged",
                "substantive": False,
                "low_confidence": score < 0.88,
                "hidden_inside_reformat": False,
                "also_renumbered": False,
                "how": "merged",
                "score": round(score, 4),
                "order": window[0]["index"],
                "baseline": [_cite(clause) for clause in window],
                "other": _cite(item),
                "chosen_text": None,
                "material": [],
            }
        )


def _best_window(clause: dict, pool: list[dict], used: set[int]) -> list[dict] | None:
    free = [item for item in pool if item["index"] not in used]
    best: list[dict] | None = None
    best_score = 0.0
    for size in (2, 3):
        for start in range(0, len(free) - size + 1):
            window = free[start:start + size]
            if not _consecutive(window):
                continue
            if not _parts_belong(clause, window):
                continue
            score = jaccard(clause["tokens"], _concat(window))
            if score > best_score:
                best = window
                best_score = score
    if best is None or best_score < SPLIT:
        return None
    return best


def _consecutive(window: list[dict]) -> bool:
    indexes = [item["index"] for item in window]
    return indexes == list(range(indexes[0], indexes[0] + len(indexes)))


def _parts_belong(clause: dict, window: list[dict]) -> bool:
    for item in window:
        if not item["tokens"]:
            return False
        shared = set(clause["tokens"]) & set(item["tokens"])
        if len(shared) < 3 and jaccard(clause["tokens"], item["tokens"]) < 0.3:
            return False
    return True


def _concat(window: list[dict]) -> list[str]:
    words: list[str] = []
    for item in window:
        words.extend(item["tokens"])
    return words


def _duplicate_row(side: str, key: str, group: list[dict]) -> dict:
    citations = [_cite(clause) for clause in group]
    return {
        "row_id": f"dup-{side}-{key}",
        "change_class": "duplicate_conflict",
        "substantive": True,
        "low_confidence": False,
        "hidden_inside_reformat": False,
        "also_renumbered": False,
        "how": "duplicate",
        "score": None,
        "order": group[0]["index"],
        "baseline": citations if side == "baseline" else None,
        "other": citations if side == "other" else None,
        "side": side,
        "chosen_text": None,
        "material": ["duplicates"],
    }


def _single(change: str, left: dict | None, right: dict | None) -> dict:
    order = left["index"] if left else 1000 + right["index"]
    return {
        "row_id": f"{change}-{order}",
        "change_class": change,
        "substantive": True,
        "low_confidence": False,
        "hidden_inside_reformat": False,
        "also_renumbered": False,
        "how": change,
        "score": None,
        "order": order,
        "baseline": _cite(left) if left else None,
        "other": _cite(right) if right else None,
        "chosen_text": None,
        "material": [],
    }


def _cite(clause: dict | None) -> dict | None:
    if clause is None:
        return None
    citation = dict(clause.get("citation") or {})
    citation["clause_id"] = clause.get("clause_id") or None
    citation["number"] = clause.get("number") or None
    citation["heading"] = clause.get("heading") or None
    citation["index"] = clause.get("index")
    return citation


def _rate(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return round(numerator / denominator, 4)
