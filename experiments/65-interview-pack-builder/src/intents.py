"""Requests the agent must not carry out, including paraphrases.

Negation applies. "Do not score the candidates" is not a request to score.
"""

from __future__ import annotations

import re

if __package__ in {None, ""}:
    from negate import denied_at, sentences
else:
    from .negate import denied_at, sentences

_PATTERNS: dict[str, tuple[re.Pattern[str], ...]] = {
    "score": tuple(
        re.compile(pattern, re.I)
        for pattern in (
            r"\bscore (?:the |each |these )?(?:candidates|applicants|interviewees|interviewee|them|people)\b",
            r"\bscore each\b",
            r"\bmark (?:the |each )?(?:candidates|applicants|interviewees)\b",
            r"\bgive (?:them|each candidate|the candidates) a score\b",
        )
    ),
    "rank": tuple(
        re.compile(pattern, re.I)
        for pattern in (
            r"\brank (?:the |these )?(?:candidates|applicants|interviewees|them|people)\b",
            r"\bput them in order\b",
            r"\border of merit\b",
            r"\bmerit order\b",
            r"\bwhich candidate is best\b",
            r"\bpick the best candidate\b",
            r"\bbest person for the job\b",
            r"\bwho (?:should|do) we (?:hire|appoint|prefer)\b",
        )
    ),
    "hire": tuple(
        re.compile(pattern, re.I)
        for pattern in (
            r"\bhiring decision\b",
            r"\bwho gets the job\b",
            r"\boffer them the job\b",
            r"\bmake (?:an|the) offer\b",
            r"\breject this (?:applicant|candidate)\b",
            r"\bsend a rejection\b",
            r"\bdecide who\b",
        )
    ),
    "contact": tuple(
        re.compile(pattern, re.I)
        for pattern in (
            r"\b(?:email|e-mail|call|phone|text|message|contact) the (?:candidate|applicant|interviewee)\b",
            r"\bsend the invitation\b",
            r"\bsend (?:this|the) pack\b",
            r"\bwrite to the (?:candidate|applicant)\b",
        )
    ),
    "schedule": tuple(
        re.compile(pattern, re.I)
        for pattern in (
            r"\bschedule the interview\b",
            r"\bbook the interview\b",
            r"\barrange the interview\b",
            r"\bput (?:it|the interview) in the diary\b",
            r"\bset up the interview\b",
        )
    ),
}


def intents_in(text: str) -> list[str]:
    found: list[str] = []
    for sentence in sentences(text or ""):
        for name, patterns in _PATTERNS.items():
            if name in found:
                continue
            for pattern in patterns:
                match = pattern.search(sentence)
                if match is None:
                    continue
                if denied_at(sentence, match.group(0), match.start()):
                    continue
                found.append(name)
                break
    return found
