"""Prompt-injection scan for a KYC customer file.

The file is data. A phrase on the list is recorded and is not followed.
Matching is a case-insensitive substring. A phrase that is not on the list
is not detected. That gap is a limitation, not a claim that the file is safe.

This list is the KYC actions Experiment 12 does not name. Document inventory
still runs Experiment 12's own scanner. This module does not replace it.
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
    "approve the customer",
    "reject the customer",
    "onboard the customer",
    "onboard this customer",
    "risk rating is",
    "assign a low risk",
    "assign a high risk",
    "final risk rating",
    "do not file a sar",
    "file a sar",
    "have filed a sar",
    "tell the customer we suspect",
    "we suspect money laundering",
    "documents are confirmed",
    "purpose is confirmed",
    "this customer is low risk",
    "this customer is high risk",
    "ignore the money laundering regulations",
    "clear the stale",
    "mark the customer approved",
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
                add(phrase, "trailing_blank_lines")
        body_source = head

    raw_lower = text.lower()
    for phrase in _find(body_source):
        hidden_in = "zero_width" if zero_width_removed and phrase not in raw_lower else "body"
        add(phrase, hidden_in)

    return {
        "detected": bool(signals),
        "followed": False,
        "zero_width_removed": zero_width_removed,
        "signals": signals,
    }


def merge_scans(scans: list[dict]) -> dict:
    signals: list[dict] = []
    seen: set[tuple[str, str, str]] = set()
    zero_width_removed = 0
    for scan in scans:
        zero_width_removed += scan["zero_width_removed"]
        for signal in scan["signals"]:
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
