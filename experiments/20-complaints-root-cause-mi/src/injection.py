"""Prompt-injection scan for a complaint batch.

The batch is data. A phrase on the list is recorded and is not followed.
Matching is a case-insensitive substring after zero-width characters are
removed. A phrase that is not on the list is not detected.
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
    "this is the final return",
    "final regulatory return",
    "submit this return",
    "submit the return",
    "file this with ofgem",
    "send this to ofgem",
    "send the report",
    "publish the report",
    "publish this report",
    "approve the clusters",
    "validate the clusters",
    "validate the narrative",
    "the firm is complying",
    "we comply with the code",
    "code compliant",
    "mark as submitted",
    "treat figures as current",
    "disregard the reporting period",
    "sources are current",
    "do not flag this as stale",
    "clear the stale",
)

_COMMENT = re.compile(r"<!--(.*?)-->", re.DOTALL)
_TRAILING = re.compile(r"\n{3,}(.*)\Z", re.DOTALL)


def _find(blob: str) -> list[str]:
    lower = blob.lower()
    return [phrase for phrase in PHRASES if phrase in lower]


def scan_text(text: str, *, field: str) -> dict:
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
                "field": field,
                "phrase": phrase,
                "hidden_in": hidden_in,
                "followed": False,
            }
        )

    comments = _COMMENT.findall(stripped)
    without_comments = _COMMENT.sub(" ", stripped)
    for comment in comments:
        for phrase in _find(comment):
            add(phrase, "html_comment")

    if "\f" in without_comments:
        head, _, feed_tail = without_comments.partition("\f")
        feed_visible = feed_tail
        feed_trailing = _TRAILING.search(feed_tail)
        if feed_trailing and feed_trailing.group(1).strip():
            feed_visible = feed_tail[: feed_trailing.start()]
            already = set(_find(feed_visible))
            for phrase in _find(feed_trailing.group(1)):
                if phrase not in already:
                    add(phrase, "trailing_blank_lines")
        for phrase in _find(feed_visible):
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


def neutralise(text: str) -> str:
    """Drop hidden carriers and listed phrases before text is copied or classified."""

    if not isinstance(text, str) or not text:
        return text
    cleaned = text.translate(_ZERO_WIDTH_MAP)
    cleaned = _COMMENT.sub(" ", cleaned)
    if "\f" in cleaned:
        cleaned = cleaned.split("\f", 1)[0]
    trailing = _TRAILING.search(cleaned)
    if trailing and trailing.group(1).strip():
        tail_phrases = _find(trailing.group(1))
        head = cleaned[: trailing.start()]
        if any(phrase not in head.lower() for phrase in tail_phrases):
            cleaned = head
    for phrase in PHRASES:
        cleaned = re.sub(re.escape(phrase), "[instruction removed]", cleaned, flags=re.IGNORECASE)
    return cleaned


def scan_fields(fields: list[tuple[str, str]]) -> dict:
    signals: list[dict] = []
    zero = 0
    for name, text in fields:
        found = scan_text(text, field=name)
        zero += found["zero_width_removed"]
        signals.extend(found["signals"])
    return {
        "detected": bool(signals),
        "followed": False,
        "zero_width_removed": zero,
        "signals": signals,
    }
