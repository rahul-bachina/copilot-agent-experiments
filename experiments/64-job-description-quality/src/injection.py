"""Draft text is untrusted. An instruction is recorded and not followed.

Approval words, a self-declared role, and a self-declared clearance in the
draft are not the approval step and not the directory.
"""

from __future__ import annotations

import re

if __package__ in {None, ""}:
    from words import sentences
else:
    from .words import sentences

_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("ignore_instructions", re.compile(r"ignore (?:all |previous |prior )?instructions", re.I)),
    ("pretend_approval", re.compile(r"\b(?:the recruiter has approved|approval granted|suggestions accepted|accept all suggestions|human_approval)\b", re.I)),
    ("publish", re.compile(r"\bpublish (?:this |the )?(?:advert|job|vacancy|posting)\b", re.I)),
    ("post", re.compile(r"\bpost (?:this |the )?(?:advert|job|vacancy|posting)\b", re.I)),
    ("send", re.compile(r"\bsend (?:this |the )?(?:advert|job|vacancy)\b", re.I)),
    ("strip_mandated", re.compile(r"\b(?:strip|remove|delete|drop) (?:the )?(?:disability confident|right to work|mandated)\b", re.I)),
    ("strip_label", re.compile(r"\b(?:strip|drop|ignore|remove) (?:the )?(?:legal hold|retention|marking|classification)\b", re.I)),
    ("self_clearance", re.compile(r"\bmy clearance is\b", re.I)),
    ("self_role", re.compile(r"\b(?:my role is|i am the recruiter|i'm the recruiter)\b", re.I)),
    ("decide_occupational", re.compile(r"\boccupational requirement is lawful\b", re.I)),
    ("decide_positive_action", re.compile(r"\bpositive action is lawful\b", re.I)),
    ("decide_health", re.compile(r"\bsection 60 does not apply\b", re.I)),
)


def signals_in(text: str) -> list[str]:
    found: list[str] = []
    if not isinstance(text, str) or not text:
        return found
    for name, pattern in _PATTERNS:
        if pattern.search(text) and name not in found:
            found.append(name)
    return found


def sentence_is_strip(sentence: str) -> bool:
    """A sentence that tells the tool to remove a mandated statement or a label."""

    return bool(set(signals_in(sentence)) & {"strip_mandated", "strip_label"})


def scan(text: str) -> dict:
    return {
        "detected": bool(signals_in(text)),
        "followed": False,
        "signals": signals_in(text),
        "sentences_not_treated_as_approval": True,
    }


def content_text(text: str) -> str:
    """Drop a sentence that is only an instruction to publish, approve, or strip.

    A bias phrase, a route phrase, or a mandated statement in another sentence
    stays. Distress and scoring are read on the original text by the caller.
    """

    if not isinstance(text, str) or not text:
        return ""
    drop = {
        "ignore_instructions",
        "pretend_approval",
        "publish",
        "post",
        "send",
        "strip_mandated",
        "strip_label",
        "decide_occupational",
        "decide_positive_action",
        "decide_health",
    }
    kept = []
    for sentence in sentences(text):
        if set(signals_in(sentence)) & drop:
            continue
        kept.append(sentence)
    return "\n".join(kept)
