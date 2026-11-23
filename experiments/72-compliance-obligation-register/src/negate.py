"""Negation and carve-outs for one sentence.

"It is not true that X includes Y" does not count as Y. A carve-out that
follows an otherwise clear sentence keeps that sentence from being acceptable.
"Not" in an earlier clause does not, by itself, cancel a later duty, and a
later "must not" does not cancel an earlier "must".
"""

from __future__ import annotations

import re

_SENTENCE = re.compile(r"(?<=[.!?])\s+|\n+")
_CARVE = re.compile(
    r"\b(?:except|unless|provided that|other than where|save where|save that|"
    r"but not where|but only if|only if|excluding where|other than in|"
    r"apart from where)\b",
    re.IGNORECASE,
)
_AND_NOT = re.compile(
    r"\s+\band\s+(?=must not\b|shall not\b|does not\b|do not\b|don't\b|doesn't\b)",
    re.IGNORECASE,
)
_FRAME = re.compile(
    r"\b(?:it is not true that|it is not the case that|it is not correct that|"
    r"not true that|not the case that|not correct that|"
    r"it is not required that|there is no requirement(?: to)?|"
    r"does not require|do not require|is not required|are not required|"
    r"no longer requires|nothing in this (?:policy|document|extract) requires|"
    r"does not include|do not include|doesn't include|"
    r"is not included|are not included|not included|"
    r"does not cover|doesn't cover|do not cover|"
    r"must not|shall not|never have to|never requires|"
    r"without any requirement(?: to)?|"
    r"no register of obligations is required|"
    r"do not treat this as|"
    r"not of)\b",
    re.IGNORECASE,
)
_AUX = re.compile(
    r"\b(?:must not|shall not|does not|do not|doesn't|don't|never|is not|are not)\b",
    re.IGNORECASE,
)
_MUST_NOT = re.compile(r"\b(?:must not|shall not|must never|shall never)\b", re.IGNORECASE)
_SHOULD_NOT = re.compile(r"\b(?:should not|ought not to|ought not)\b", re.IGNORECASE)
_MUST = re.compile(
    r"\b(?:must|shall|is required to|are required to|is required|are required)\b",
    re.IGNORECASE,
)
_SHOULD = re.compile(r"\b(?:should|ought to)\b", re.IGNORECASE)
_MAY = re.compile(r"\b(?:may|can choose to)\b", re.IGNORECASE)


def sentences(text: str) -> list[str]:
    return [part.strip() for part in _SENTENCE.split(text or "") if part.strip()]


def carve_out(sentence: str) -> tuple[str, str]:
    match = _CARVE.search(sentence or "")
    if match is None:
        return sentence or "", ""
    return sentence[: match.start()].strip(" ,;"), sentence[match.start() :].strip()


def denial_split(clause: str) -> tuple[str, str]:
    """Text before a denial frame, and the denied span. Neither is chosen as true."""

    frame = _FRAME.search(clause or "")
    if frame is not None:
        return clause[: frame.start()], clause[frame.end() :]
    aux = _AUX.search(clause or "")
    if aux is not None:
        return clause[: aux.start()], clause[aux.end() :]
    return clause or "", ""


def clauses(sentence: str) -> list[str]:
    main, _carve = carve_out(sentence or "")
    parts = [part.strip(" ,;") for part in _AND_NOT.split(main) if part.strip(" ,;")]
    return parts or [main]


def strength_of(clause: str) -> str:
    """The modal in the part that is not inside a denial span."""

    scope, _denied = denial_split(clause or "")
    if _FRAME.search(clause or "") and not _MUST.search(scope):
        return "denied"
    has_must_not = bool(_MUST_NOT.search(scope))
    has_should_not = bool(_SHOULD_NOT.search(scope))
    stripped = _MUST_NOT.sub(" ", scope)
    stripped = _SHOULD_NOT.sub(" ", stripped)
    has_must = bool(_MUST.search(stripped))
    has_should = bool(_SHOULD.search(stripped))
    has_may = bool(_MAY.search(stripped))
    if has_must and has_should:
        return "ambiguous"
    if has_must_not and has_must:
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
    if _FRAME.search(clause or "") or _AUX.search(clause or ""):
        return "denied"
    return "unstated"


def qualified(sentence: str) -> bool:
    return bool(_CARVE.search(sentence or ""))
