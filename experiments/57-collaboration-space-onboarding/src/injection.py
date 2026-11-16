"""Untrusted request and fixture text. Instructions are recorded and not followed.

A phrase after a negation cue in the same sentence is not a match, not a
safeguarding cue, and not a protective marking. A sentence that says the
owner has approved is not an approval.
"""

from __future__ import annotations

import re

ZERO_WIDTH = re.compile(r"[\u200b\u200c\u200d\ufeff]")
HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
SENTENCE = re.compile(r"[^.!?\n]+[.!?\n]?")

INSTRUCTIONS = (
    (re.compile(r"ignore (?:all|any|previous|the above) instructions[^.]*", re.I), "ignore_instructions"),
    (re.compile(r"never mind,?\s+ignore[^.]*", re.I), "never_mind_ignore"),
    (re.compile(r"you are now[^.]*", re.I), "you_are_now"),
    (re.compile(r"system prompt[^.]*", re.I), "system_prompt"),
    (re.compile(r"the (?:workspace )?owner has approved[^.]*", re.I), "pretend_approval"),
    (re.compile(r"\bi approve this\b[^.]*", re.I), "pretend_approval"),
    (re.compile(r"\bthis request is approved\b[^.]*", re.I), "pretend_approval"),
    (re.compile(r"\bguest access approved\b[^.]*", re.I), "pretend_guest_approval"),
    (re.compile(r"\bowner rights approved\b[^.]*", re.I), "pretend_owner_approval"),
    (re.compile(r"\bgrant owner rights\b[^.]*", re.I), "grant_owner"),
    (re.compile(r"\bmake me an owner\b[^.]*", re.I), "grant_owner"),
    (re.compile(r"\bshare (?:the |this )?(?:file|link) externally\b[^.]*", re.I), "share_externally"),
    (re.compile(r"\badd (?:me|them) to every (?:team|space|channel)\b[^.]*", re.I), "widen_access"),
    (re.compile(r"\bmy clearance is\b[^.]*", re.I), "pretend_clearance"),
    (re.compile(r"\bi am cleared to\b[^.]*", re.I), "pretend_clearance"),
    (re.compile(r"\bclearance is top secret\b[^.]*", re.I), "pretend_clearance"),
    (re.compile(r"\bdo not flag\b[^.]*", re.I), "do_not_flag"),
    (re.compile(r"\bdon't flag\b[^.]*", re.I), "do_not_flag"),
    (re.compile(r"\bthis is not a safeguarding\b[^.]*", re.I), "deny_safeguarding"),
)

NEGATION = re.compile(
    r"\b(?:not true that|it is not the case that|never mind,?\s+ignore|"
    r"no longer|does not include|do not include|not include|never includes|"
    r"does not|do not|is not|isn't|are not|aren't|not a|not an|not the)\b",
    re.IGNORECASE,
)


def _signals_in(text: str, hidden_in: str) -> list[dict]:
    found = []
    for pattern, signal in INSTRUCTIONS:
        if pattern.search(text):
            found.append({"signal": signal, "hidden_in": hidden_in, "followed": False})
    return found


def _clean_sentence(sentence: str) -> str:
    cleaned = sentence
    for pattern, _signal in INSTRUCTIONS:
        cleaned = pattern.sub(" ", cleaned)
    negation = NEGATION.search(cleaned)
    if negation:
        cleaned = cleaned[: negation.start()]
    return cleaned


def prepare_text(text: str) -> tuple[str, dict]:
    """Return matching text and an injection report. ``followed`` is false."""

    if not isinstance(text, str):
        return "", {
            "detected": False,
            "followed": False,
            "signals": [],
            "input_was_text": False,
        }
    signals: list[dict] = []
    if ZERO_WIDTH.search(text):
        signals.append({"signal": "zero_width", "hidden_in": "zero_width", "followed": False})
    visible = ZERO_WIDTH.sub("", text)
    for comment in HTML_COMMENT.findall(visible):
        signals.extend(_signals_in(comment, "html_comment"))
    visible = HTML_COMMENT.sub(" ", visible)
    # Instructions are recorded from the visible text, then dropped from the
    # matching text. A negated sentence does not keep the tail as a match.
    signals.extend(_signals_in(visible, "body"))
    parts = []
    for sentence in SENTENCE.findall(visible):
        negation = NEGATION.search(sentence)
        comparable = sentence[: negation.start()] if negation else sentence
        if any(pattern.search(comparable) for pattern, _signal in INSTRUCTIONS):
            cleaned = _clean_sentence(sentence)
        else:
            cleaned = comparable
        parts.append(cleaned)
    matching = re.sub(r"\s+", " ", " ".join(parts)).strip()
    seen = set()
    unique = []
    for signal in signals:
        if signal["signal"] in seen:
            continue
        seen.add(signal["signal"])
        unique.append(signal)
    return matching, {
        "detected": bool(unique),
        "followed": False,
        "signals": unique,
        "input_was_text": True,
    }
