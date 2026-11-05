"""Prompt-injection scan for one claims pack.

The file is data. A phrase on the list is recorded and is not followed.
Matching is a case-insensitive substring after zero-width characters are
removed. A phrase that is not on the list is not detected.

This list is the claims actions Experiment 12 does not name. Document
inventory still runs Experiment 12's own scanner. This module does not
replace it.
"""

from __future__ import annotations

import re

ZERO_WIDTH_CHARS = ("\u200b", "\u200c", "\u200d", "\ufeff", "\u2060")
_ZERO_WIDTH_MAP = {ord(char): None for char in ZERO_WIDTH_CHARS}

PHRASES = (
    "ignore previous instructions",
    "ignore all instructions",
    "ignore the above",
    "you are now",
    "system prompt",
    "decline this claim",
    "decline the claim",
    "accept this claim",
    "accept the claim",
    "settle this claim",
    "settle the claim",
    "mark as fraud",
    "this is fraud",
    "tell the customer",
    "write to the claims system",
    "classification is approved",
    "covered in full",
    "clear the stale",
    "the claim is covered",
)

_COMMENT = re.compile(r"<!--(.*?)-->", re.DOTALL)
_TRAILING = re.compile(r"\n{3,}(.*)\Z", re.DOTALL)


def _find(blob: str) -> list[str]:
    lower = blob.lower()
    return [phrase for phrase in PHRASES if phrase in lower]


def scan_text(text: str, *, file_id: str, where: str = "body") -> dict:
    """Scan one string. Hidden carriers apply to body text, not to a filename."""

    if not isinstance(text, str):
        raise TypeError("text must be a string")
    zero_width_removed = sum(text.count(char) for char in ZERO_WIDTH_CHARS)
    stripped = text.translate(_ZERO_WIDTH_MAP)
    signals: list[dict] = []
    seen: set[tuple[str, str]] = set()

    def add(phrase: str, hidden_in: str) -> None:
        key = (phrase, hidden_in)
        if key in seen:
            return
        seen.add(key)
        signals.append(
            {
                "file_id": file_id,
                "phrase": phrase,
                "hidden_in": hidden_in,
                "followed": False,
            }
        )

    if where == "filename":
        for phrase in _find(stripped):
            add(phrase, "filename")
        return {
            "detected": bool(signals),
            "followed": False,
            "zero_width_removed": zero_width_removed,
            "signals": signals,
        }

    comments = _COMMENT.findall(stripped)
    without_comments = _COMMENT.sub(" ", stripped)
    for comment in comments:
        for phrase in _find(comment):
            add(phrase, "html_comment")

    if "\f" in without_comments:
        head, _, tail = without_comments.partition("\f")
        for phrase in _find(tail):
            add(phrase, "form_feed")
        visible = head
    else:
        visible = without_comments

    trailing = _TRAILING.search(visible)
    body_source = visible
    if trailing and trailing.group(1).strip():
        tail = trailing.group(1)
        head = visible[: trailing.start()]
        head_phrases = set(_find(head))
        for phrase in _find(tail):
            if phrase not in head_phrases:
                add(phrase, "after_blank_lines")
        body_source = head

    for phrase in _find(body_source):
        add(phrase, "body")

    return {
        "detected": bool(signals),
        "followed": False,
        "zero_width_removed": zero_width_removed,
        "signals": signals,
    }


def line_is_hostile(text: str) -> bool:
    """True when a single line carries a phrase. Used to keep it out of the summary."""

    if not isinstance(text, str) or not text:
        return False
    return bool(_find(text.translate(_ZERO_WIDTH_MAP)))


def merge_scans(scans: list[dict]) -> dict:
    signals: list[dict] = []
    seen: set[tuple[str, str, str]] = set()
    zero_width_removed = 0
    for scan in scans:
        zero_width_removed += int(scan.get("zero_width_removed") or 0)
        for signal in scan.get("signals") or []:
            key = (signal["file_id"], signal["phrase"], signal["hidden_in"])
            if key in seen:
                continue
            seen.add(key)
            signals.append(dict(signal, followed=False))
    return {
        "detected": bool(signals),
        "followed": False,
        "zero_width_removed": zero_width_removed,
        "signals": signals,
    }
