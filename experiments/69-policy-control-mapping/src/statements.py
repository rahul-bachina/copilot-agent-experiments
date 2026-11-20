"""Obligation strength, negation, and qualifications.

"should" is not "must". "except …" weakens a statement. "It is not true that
X includes Y" is not an inclusion. A stem that is not in this list is not matched.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from cues import biased
else:
    from .cues import biased

_DENIAL = re.compile(
    r"\bnot true that\b"
    r"|\bnot the case that\b"
    r"|\bnot correct that\b"
    r"|\bnothing in this (?:policy|document) requires\b"
    r"|\bthere is no requirement\b"
    r"|\bdoes not require\b"
    r"|\bdo not require\b"
    r"|\bis not required\b"
    r"|\bare not required\b"
    r"|\bno longer requires\b"
    r"|\bdoes not include\b"
    r"|\bdo not include\b"
    r"|\bdoesn't include\b"
    r"|\bdo not treat this as\b"
    r"|\bwithout any requirement\b"
    r"|\bnever have to\b"
    r"|\bnever requires\b"
    r"|\bis not included\b"
    r"|\bnot included\b"
    r"|\bno\b(?:\s+\w+){0,6}\s+\brequires\b"
    r"|\bit is not required\b",
    re.IGNORECASE,
)
_MUST_NOT = re.compile(r"\b(?:must not|shall not|must never|shall never)\b", re.IGNORECASE)
_SHOULD_NOT = re.compile(r"\b(?:should not|ought not to|ought not)\b", re.IGNORECASE)
_MUST = re.compile(r"\b(?:must|shall|is required to|are required to|is required|are required)\b", re.IGNORECASE)
_SHOULD = re.compile(r"\b(?:should|ought to)\b", re.IGNORECASE)
_MAY = re.compile(r"\b(?:may|can choose to)\b", re.IGNORECASE)
_QUAL = re.compile(
    r"\bexcept\b|\bunless\b|\bother than where\b|\bsave where\b|\bapart from where\b"
    r"|\bexcluding where\b|\bbut not where\b|\bother than in\b|\bsave that\b"
    r"|\bonly if\b|\bprovided that\b",
    re.IGNORECASE,
)
_SENTENCE = re.compile(r"(?<=[.!?])\s+|\n+")

STRENGTHS = frozenset({"must", "must_not", "should", "should_not", "may"})


def split_sentences(text: str) -> list[str]:
    parts = [part.strip() for part in _SENTENCE.split(text or "") if part.strip()]
    return parts


def strength_of(sentence: str) -> str:
    """Return the obligation word. A denied sentence is not an inclusion."""

    if _DENIAL.search(sentence or ""):
        return "denied"
    has_must_not = bool(_MUST_NOT.search(sentence or ""))
    has_should_not = bool(_SHOULD_NOT.search(sentence or ""))
    stripped = _MUST_NOT.sub(" ", sentence or "")
    stripped = _SHOULD_NOT.sub(" ", stripped)
    has_must = bool(_MUST.search(stripped))
    has_should = bool(_SHOULD.search(stripped))
    has_may = bool(_MAY.search(stripped))
    if has_must_not and has_must:
        return "ambiguous"
    if has_must and has_should:
        return "ambiguous"
    if has_must_not:
        return "must_not"
    if has_should_not:
        return "should_not"
    if has_must:
        return "must"
    if has_should:
        return "should"
    if has_may:
        return "may"
    return "unstated"


def qualified(sentence: str) -> bool:
    return bool(_QUAL.search(sentence or ""))


def _group_hit(sentence: str, alternatives: list[str]) -> bool:
    for alt in alternatives:
        if re.search(rf"\b{re.escape(alt)}\w*\b", sentence, re.IGNORECASE):
            return True
    return False


def assess_sentence(sentence: str, control: dict) -> dict:
    """How one sentence stands against one pinned control. Nothing is marked met."""

    groups = control.get("signal_groups") or []
    hits = [_group_hit(sentence, group) for group in groups]
    all_hit = bool(groups) and all(hits)
    strength = strength_of(sentence)
    is_qualified = qualified(sentence)
    is_biased = biased(sentence)
    expected = control.get("expected_strength")
    base = {
        "control_id": control.get("control_id"),
        "strength": strength,
        "qualified": is_qualified,
        "biased": is_biased,
        "signals_all_present": all_hit,
        "support": False,
        "opposes": False,
        "obligation_affirmed": False,
        "confidence": None,
        "included": False,
        "control_met": False,
        "acceptable": False,
        "guessed": False,
    }
    if is_biased:
        base["route_to_human"] = True
        return base
    base["route_to_human"] = False
    if not all_hit or expected not in STRENGTHS:
        return base
    if strength in {"denied", "unstated"}:
        return base
    if strength == "ambiguous":
        base["support"] = True
        base["confidence"] = "low"
        base["rationale_code"] = "ambiguous_strength"
        return base
    opposite = {strength, expected} == {"must", "must_not"} or (
        strength == "should_not" and expected == "must"
    ) or (strength == "must" and expected == "should_not")
    if opposite or (strength == "must_not" and expected == "should") or (
        strength == "should" and expected == "must_not"
    ):
        base["opposes"] = True
        return base
    if strength == "should_not" and expected == "must_not":
        base["support"] = True
        base["confidence"] = "medium"
        base["rationale_code"] = "should_is_not_must"
        return base
    if strength != expected and not (expected == "must" and strength in {"should", "may"}):
        return base
    if is_qualified or strength == "may":
        confidence = "low"
        code = "qualification_weakens" if is_qualified else "may_is_not_must"
    elif strength == expected and strength in {"must", "must_not"}:
        confidence = "high"
        code = "expected_strength"
    elif strength == "should" and expected == "must":
        confidence = "medium"
        code = "should_is_not_must"
    else:
        confidence = "low"
        code = "partial"
    base["support"] = True
    base["confidence"] = confidence
    base["rationale_code"] = code
    base["obligation_affirmed"] = confidence == "high" and not is_qualified
    base["included"] = base["obligation_affirmed"]
    return base
