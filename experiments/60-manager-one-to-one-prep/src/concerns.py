"""Distress, wellbeing, safeguarding, and personal-circumstance indicators.

A denial is not an indicator. A paraphrase is still an indicator. The sentence
is not copied into the routine prep note.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from marking import in_negation, negation_spans
else:
    from .marking import in_negation, negation_spans

_PARAPHRASE: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("safeguarding", re.compile(r"\bfrightened to come (?:in|to work)\b", re.I)),
    ("safeguarding", re.compile(r"\bdo not feel safe(?: at work)?\b", re.I)),
    ("safeguarding", re.compile(r"\bdon't feel safe(?: at work)?\b", re.I)),
    ("distress", re.compile(r"\bfinding it hard to keep going\b", re.I)),
    ("distress", re.compile(r"\bstruggling to (?:get through|carry on)\b", re.I)),
    ("wellbeing", re.compile(r"\bnot been sleeping\b", re.I)),
    ("wellbeing", re.compile(r"\bhaven't been sleeping\b", re.I)),
    ("wellbeing", re.compile(r"\bhave not been sleeping\b", re.I)),
    ("wellbeing", re.compile(r"\b(?:not coping|cannot cope|can't cope)\b", re.I)),
    ("wellbeing", re.compile(r"\b(?:burnt out|burned out)\b", re.I)),
    ("wellbeing", re.compile(r"\bmental health\b", re.I)),
    ("wellbeing", re.compile(r"\bpanic attacks?\b", re.I)),
    ("wellbeing", re.compile(r"\breally low\b", re.I)),
)

_PERSONAL: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("pregnancy", re.compile(r"\b(?:i am pregnant|i'm pregnant|pregnancy)\b", re.I)),
    ("disability", re.compile(r"\b(?:my disability|i am disabled|i'm disabled)\b", re.I)),
    (
        "religion_or_belief",
        re.compile(
            r"\b(?:my religion|i am muslim|i'm muslim|i am christian|i am jewish|i am sikh|i am hindu)\b",
            re.I,
        ),
    ),
    (
        "sexual_orientation",
        re.compile(r"\b(?:my sexual orientation|i am gay|i am lesbian|i am bisexual)\b", re.I),
    ),
    (
        "gender_reassignment",
        re.compile(r"\b(?:gender reassignment|i am transgender)\b", re.I),
    ),
)

_PROHIBITED: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "performance_rating",
        re.compile(
            r"\b(?:performance rating|rate (?:their|his|her|this) performance|"
            r"exceeds expectations|mark (?:them|him|her) as (?:outstanding|poor)|"
            r"score (?:them|him|her))\b",
            re.I,
        ),
    ),
    (
        "comparison",
        re.compile(
            r"\b(?:compare (?:them|him|her|this employee)|peer ranking|ranked against|"
            r"better than (?:their|his|her) (?:peers|colleagues))\b",
            re.I,
        ),
    ),
    (
        "disciplinary",
        re.compile(
            r"\b(?:written warning|disciplinary action|start (?:a )?disciplinary|"
            r"dismiss (?:them|him|her))\b",
            re.I,
        ),
    ),
    (
        "capability",
        re.compile(
            r"\b(?:capability procedure|capability action|performance improvement plan|"
            r"put (?:them|him|her) on a pip)\b",
            re.I,
        ),
    ),
    (
        "health_inference",
        re.compile(
            r"\b(?:infer (?:that )?(?:they|he|she).{0,80}(?:ill|depression|disabled|health)|"
            r"(?:they|he|she) (?:must be|are probably|is probably) (?:depressed|ill|disabled))\b",
            re.I,
        ),
    ),
    (
        "profile",
        re.compile(r"\b(?:build a profile|employee profile|profile (?:them|him|her))\b", re.I),
    ),
)

_BUT = re.compile(r"\b(?:but|however)\b", re.I)
_FOLLOW = re.compile(
    r"\b(?:follow[- ]up|agreed to|action:|next time|we will|to complete|by the next one-to-one)\b",
    re.I,
)
_DENIAL_ONLY = re.compile(
    r"^\s*(?:it is not true that|it's not true that|it is not the case that|"
    r"not true that|does not include|did not include)\b",
    re.I,
)

_EXPERIMENT_15_KIND = {
    "possible_safeguarding_risk": "safeguarding",
    "possible_self_harm_risk": "distress",
    "possible_financial_hardship": "wellbeing",
}
_LEGAL_DEADLINE = re.compile(
    r"\b(?:tribunal|court date|court hearing|possession hearing|appeal deadline)\b",
    re.I,
)

_ROUTE = (
    "HR and the employer's employee assistance programme. "
    "Handle this humanely. Do not treat it as a routine agenda item."
)


def follow_up_cue(text: str) -> bool:
    spans = negation_spans(text)
    match = _FOLLOW.search(text)
    if match is None:
        return False
    return not in_negation(match.start(), spans)


def is_denial_of_inclusion(text: str) -> bool:
    """A sentence that only denies an inclusion is not itself the inclusion."""
    if _BUT.search(text):
        return False
    return _DENIAL_ONLY.search(text) is not None


def local_concerns(text: str) -> list[dict]:
    spans = negation_spans(text)
    found: list[dict] = []
    for kind, pattern in _PARAPHRASE:
        for match in pattern.finditer(text):
            if in_negation(match.start(), spans):
                continue
            found.append(
                {
                    "kind": kind,
                    "indicator": "paraphrase_" + kind,
                    "experiment_15": False,
                    "sentence_copied": False,
                }
            )
            break
    for _topic, pattern in _PERSONAL:
        for match in pattern.finditer(text):
            if in_negation(match.start(), spans):
                continue
            found.append(
                {
                    "kind": "personal_circumstance",
                    "indicator": "personal_circumstance",
                    "experiment_15": False,
                    "sentence_copied": False,
                }
            )
            break
    return found


def prohibited_requests(text: str) -> list[str]:
    if not isinstance(text, str):
        return []
    found: list[str] = []
    for code, pattern in _PROHIBITED:
        if pattern.search(text) and code not in found:
            found.append(code)
    return found


def experiment_15_kind(category: str, phrase: str, line: str, offset_in_line: int) -> str | None:
    """Map an Experiment 15 category. A phrase inside a denial does not count."""
    if in_negation(offset_in_line, negation_spans(line)):
        return None
    if category == "possible_deadline_or_time_limit":
        if _LEGAL_DEADLINE.search(phrase or "") or _LEGAL_DEADLINE.search(line or ""):
            return "safeguarding"
        return None
    return _EXPERIMENT_15_KIND.get(category)


def flag_row(kind: str, indicator: str, source_id: str, line: int, *, experiment_15: bool) -> dict:
    return {
        "kind": kind,
        "indicator": indicator,
        "route": _ROUTE,
        "source_id": source_id,
        "line": line,
        "experiment_15": experiment_15,
        "summarised_as_routine": False,
        "sentence_copied": False,
        "person_labelled": False,
        "health_inferred": False,
    }
