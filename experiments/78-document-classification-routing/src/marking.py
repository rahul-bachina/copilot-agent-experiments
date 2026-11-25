"""Protective markings.

Experiment 49's prepare_text body_marking and MARKING_RANK are the reused
derivation. A bare cover line such as SECRET is read here because Experiment
49's pattern requires the word "marked" or "classification:". A compound set
takes the higher rank. "My clearance is" is not a cover page.
"""

from __future__ import annotations

import re

if __package__ in {None, ""}:
    from cues import is_instruction
    from negate import denied_at, sentences
    from reuse import marking_rank, prepare_text
else:
    from .cues import is_instruction
    from .negate import denied_at, sentences
    from .reuse import marking_rank, prepare_text

_ORDER = ("TOP SECRET", "OFFICIAL-SENSITIVE", "SECRET", "OFFICIAL")
_CLEARANCE = re.compile(r"\bmy clearance is\b", re.I)
_LABELLED = re.compile(
    r"\b(?:protective marking|classification)\s*:\s*(top secret|official-sensitive|secret|official)\b",
    re.I,
)


def _labels_in(text: str) -> list[str]:
    found: list[str] = []
    remaining = text or ""
    for label in _ORDER:
        pattern = re.compile(rf"\b{re.escape(label)}\b", re.I)
        if pattern.search(remaining):
            found.append(label)
            remaining = pattern.sub(" ", remaining)
    return found


def _denied(sentence: str, label: str) -> bool:
    folded = sentence.casefold()
    needle = label.casefold()
    index = folded.find(needle)
    if index < 0:
        return False
    return denied_at(sentence, label, index)


def content_markings(text: str) -> list[str]:
    found: list[str] = []
    for line in (text or "").splitlines():
        if _CLEARANCE.search(line):
            continue
        token = line.strip().upper()
        if token in _ORDER and token not in found:
            found.append(token)
    for sentence in sentences(text or ""):
        if _CLEARANCE.search(sentence) or is_instruction(sentence):
            continue
        for match in _LABELLED.finditer(sentence):
            label = match.group(1).upper()
            if label not in found and not _denied(sentence, match.group(1)):
                found.append(label)
        if len(sentence.strip().splitlines()) == 1 and sentence.strip().upper() in _ORDER:
            continue
        for label in _labels_in(sentence):
            if _denied(sentence, label):
                continue
            if label not in found:
                found.append(label)
    return found


def metadata_markings(value: object) -> tuple[list[str], bool]:
    if value is None or value == "" or value == []:
        return [], False
    if isinstance(value, str):
        if _CLEARANCE.search(value):
            return [], False
        return _labels_in(value), False
    if isinstance(value, list):
        found: list[str] = []
        bad = False
        for item in value:
            if isinstance(item, str):
                if _CLEARANCE.search(item):
                    continue
                for label in _labels_in(item):
                    if label not in found:
                        found.append(label)
            elif item not in (None, ""):
                bad = True
        return found, bad
    return [], True


def higher(labels: list[str], rank: dict) -> str | None:
    usable = [label for label in labels if label in rank]
    if not usable:
        return None
    return max(usable, key=lambda label: rank[label])


def above_ceiling(marking: str | None, ceiling: str | None, rank: dict) -> bool:
    if ceiling not in rank:
        return True
    if marking is None:
        return False
    if marking not in rank:
        return True
    return rank[marking] > rank[ceiling]


def derive(metadata_value: object, text: str) -> dict:
    rank = marking_rank()
    _matching, report = prepare_text()(text or "")
    body = report.get("body_marking")
    if body not in rank:
        body = None
    content = content_markings(text or "")
    meta, bad = metadata_markings(metadata_value)
    pool: list[str] = []
    for label in list(meta) + list(content) + ([body] if body else []):
        if label and label not in pool:
            pool.append(label)
    return {
        "applied": higher(pool, rank),
        "from_metadata": meta,
        "from_content": content,
        "from_experiment_49": body,
        "conflict": len(pool) > 1,
        "unparseable": bad,
        "self_declared_clearance_ignored": True,
        "higher_taken": True,
        "rank_source": "exp-49-records-classification MARKING_RANK",
        "coerced": False,
        "experiment_49_file_plan_used": False,
    }
