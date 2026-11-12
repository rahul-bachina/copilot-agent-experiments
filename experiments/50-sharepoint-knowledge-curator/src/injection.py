"""Untrusted page text. Instructions are recorded and not followed.

A phrase that follows a negation is not a positive match. Hidden HTML
comments are not used as content-type evidence.
"""

from __future__ import annotations

import re

ZERO_WIDTH = re.compile(r"[\u200b\u200c\u200d\ufeff]")
HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
SENTENCE = re.compile(r"[^.!?\n]+[.!?\n]?")

# An instruction is removed through the end of its sentence. followed stays false.
INSTRUCTIONS = (
    (re.compile(r"ignore (?:all|any|previous|the above) instructions[^.]*", re.IGNORECASE), "ignore_instructions"),
    (re.compile(r"never mind,?\s+ignore[^.]*", re.IGNORECASE), "never_mind_ignore"),
    (re.compile(r"you are now[^.]*", re.IGNORECASE), "you_are_now"),
    (re.compile(r"system prompt[^.]*", re.IGNORECASE), "system_prompt"),
    (re.compile(r"the site owner has approved[^.]*", re.IGNORECASE), "pretend_approval"),
    (re.compile(r"approve this (?:metadata|page|change|proposal)[^.]*", re.IGNORECASE), "approve_this"),
    (re.compile(r"delete this page[^.]*", re.IGNORECASE), "delete_page"),
    (re.compile(r"unpublish this[^.]*", re.IGNORECASE), "unpublish"),
    (re.compile(r"change the permissions[^.]*", re.IGNORECASE), "change_permissions"),
    (re.compile(r"grant access[^.]*", re.IGNORECASE), "grant_access"),
    (re.compile(r"move this page[^.]*", re.IGNORECASE), "move_page"),
    (re.compile(r"do not queue[^.]*", re.IGNORECASE), "do_not_queue"),
    (re.compile(r"don't queue[^.]*", re.IGNORECASE), "do_not_queue"),
    (re.compile(r"skip the queue[^.]*", re.IGNORECASE), "skip_queue"),
    (re.compile(r"this is not personal data[^.]*", re.IGNORECASE), "deny_personal_data"),
    (re.compile(r"this is not official-sensitive[^.]*", re.IGNORECASE), "deny_marking"),
)

# Leftmost alternative wins. A phrase after this cue, in the same sentence, is not evidence.
NEGATION = re.compile(
    r"\b(?:not true that|it is not the case that|never mind,?\s+ignore|"
    r"no longer|is not|isn't|are not|aren't|not a|not an|not the)\b",
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

    signals: list[dict] = []
    if ZERO_WIDTH.search(text):
        signals.append({"signal": "zero_width", "hidden_in": "zero_width", "followed": False})
    visible = ZERO_WIDTH.sub("", text)
    for comment in HTML_COMMENT.findall(visible):
        signals.extend(_signals_in(comment, "html_comment"))
    visible = HTML_COMMENT.sub(" ", visible)
    signals.extend(_signals_in(visible, "body"))
    parts = [_clean_sentence(sentence) for sentence in SENTENCE.findall(visible)]
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
    }
