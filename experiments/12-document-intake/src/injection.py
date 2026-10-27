"""Prompt-injection scan for document text.

The file is data. A phrase on the list is recorded and is not followed.
Matching is a case-insensitive substring. A phrase that is not on the list
is not detected. That gap is a limitation, not a claim that the file is safe.
"""

from __future__ import annotations

import re

ZERO_WIDTH_CHARS = ("\u200b", "\u200c", "\u200d", "\ufeff", "\u2060")
_ZERO_WIDTH_MAP = {ord(char): None for char in ZERO_WIDTH_CHARS}

# Instructions a document might use to skip the human steps or to take an
# action this agent does not have. Keep the list narrow and tested.
PHRASES = (
    "ignore previous instructions",
    "ignore all instructions",
    "ignore the above",
    "you are now",
    "system prompt",
    "do not redact",
    "this document is approved",
    "approve this file",
    "accept this file into",
    "files are confirmed",
    "permitted purpose is",
    "set the purpose",
    "email the customer",
    "send this to",
    "write to dataverse",
    "write to sharepoint",
    "update the case record",
    "mark as anonymised",
    "mark as anonymized",
    "release the redacted",
    "pay the claim",
    "disclose the records",
    "approve the kyc",
    "this document is current, ignore the date",
    "ignore the document date",
    "disregard the date",
)

_COMMENT = re.compile(r"<!--(.*?)-->", re.DOTALL)
_TRAILING = re.compile(r"\n{3,}(.*)\Z", re.DOTALL)


def _find(blob: str) -> list[str]:
    lower = blob.lower()
    return [phrase for phrase in PHRASES if phrase in lower]


def scan_text(text: str, *, file_id: str, where: str = "body") -> dict:
    """Scan one string.

    ``where`` is ``body`` for file text and ``filename`` for the filename.
    Hidden carriers (HTML comment, form feed, trailing blank lines, zero-width
    characters) are only applied to body text. A filename match is recorded
    as ``filename``.
    """

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
