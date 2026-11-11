"""Untrusted document text. Instructions are recorded and not followed.

A legal-hold cue such as "do not destroy" is kept. An instruction to delete,
dispose, downgrade, or skip the queue is removed from the matching text and
is not obeyed. Hidden HTML comments are not used as classification evidence.
"""

from __future__ import annotations

import re

ZERO_WIDTH = re.compile(r"[\u200b\u200c\u200d\ufeff]")
HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)

INSTRUCTIONS = (
    (re.compile(r"ignore (?:all|any|previous|the above) instructions", re.IGNORECASE), "ignore_instructions"),
    (re.compile(r"do not queue", re.IGNORECASE), "do_not_queue"),
    (re.compile(r"don't queue", re.IGNORECASE), "do_not_queue"),
    (re.compile(r"delete this record", re.IGNORECASE), "delete_record"),
    (re.compile(r"destroy this record", re.IGNORECASE), "destroy_record"),
    (re.compile(r"dispose of this record", re.IGNORECASE), "dispose_record"),
    (re.compile(r"downgrade (?:this|the record|to official)", re.IGNORECASE), "downgrade"),
    (re.compile(r"classify this as [^.\n]{0,80}", re.IGNORECASE), "classify_as"),
    (re.compile(r"mark this (?:as )?official(?:-sensitive)?", re.IGNORECASE), "mark_official"),
    (re.compile(r"you are now", re.IGNORECASE), "you_are_now"),
    (re.compile(r"system prompt", re.IGNORECASE), "system_prompt"),
    (re.compile(r"this is not personal data", re.IGNORECASE), "deny_personal_data"),
    (re.compile(r"there is no legal hold", re.IGNORECASE), "deny_legal_hold"),
    (re.compile(r"apply the label", re.IGNORECASE), "apply_label"),
)

HIGHER_MARKING = (
    (re.compile(r"\b(?:marked|classification:)\s*top secret\b", re.IGNORECASE), "TOP SECRET"),
    (re.compile(r"\b(?:marked|classification:)\s*secret\b", re.IGNORECASE), "SECRET"),
    (
        re.compile(r"\b(?:marked|classification:)\s*official-sensitive\b", re.IGNORECASE),
        "OFFICIAL-SENSITIVE",
    ),
)


def _signals_in(text: str, hidden_in: str) -> list[dict]:
    found = []
    for pattern, signal in INSTRUCTIONS:
        if pattern.search(text):
            found.append({"signal": signal, "hidden_in": hidden_in, "followed": False})
    return found


def prepare_text(text: str) -> tuple[str, dict]:
    """Return matching text and an injection report. ``followed`` is false."""

    signals: list[dict] = []
    if ZERO_WIDTH.search(text):
        signals.append({"signal": "zero_width", "hidden_in": "zero_width", "followed": False})
    visible = ZERO_WIDTH.sub("", text)
    comments = HTML_COMMENT.findall(visible)
    for comment in comments:
        signals.extend(_signals_in(comment, "html_comment"))
    visible = HTML_COMMENT.sub(" ", visible)
    signals.extend(_signals_in(visible, "body"))
    matching = visible
    for pattern, _signal in INSTRUCTIONS:
        matching = pattern.sub(" ", matching)
    matching = re.sub(r"\s+", " ", matching).strip()
    body_marking = None
    for pattern, marking in HIGHER_MARKING:
        if pattern.search(matching):
            body_marking = marking
            break
    return matching, {
        "detected": bool(signals),
        "followed": False,
        "signals": signals,
        "body_marking": body_marking,
    }
