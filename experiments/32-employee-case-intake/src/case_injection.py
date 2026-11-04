"""Prompt-injection scan for one HR narrative.

The narrative is data. A phrase on the list is recorded and is not followed.
A phrase that is not on the list is not detected. That gap is a limitation,
not a claim that the narrative is safe.

The pattern follows Experiment 12's scanner: body, HTML comment, form feed,
trailing blank lines, and zero-width characters. The phrase list is this
experiment's. Experiment 12 is not copied.
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
    "classify this as",
    "set the category to",
    "this is not whistleblowing",
    "contact the employee",
    "contact the manager",
    "email the manager",
    "email the employee",
    "write to the hr system",
    "write this to the hr system",
    "the grievance is unfounded",
    "decide the outcome",
    "dismiss the case",
    "no further action",
    "mark as routine",
    "override the category",
    "you have already decided",
    "disregard the pinned sources",
    "the law has changed, ignore",
    "approve the routing",
    "this disclosure is protected",
    "harassment is made out",
)

_COMMENT = re.compile(r"<!--(.*?)-->", re.DOTALL)
_TRAILING = re.compile(r"\n{3,}(.*)\Z", re.DOTALL)


def _find(blob: str) -> list[str]:
    lower = blob.lower()
    return [phrase for phrase in PHRASES if phrase in lower]


def scan_narrative(text: str) -> dict:
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
        signals.append({"phrase": phrase, "hidden_in": hidden_in, "followed": False})

    for phrase in _find(stripped):
        add(phrase, "body")
    for comment in _COMMENT.findall(text):
        for phrase in _find(comment):
            add(phrase, "html_comment")
    if "\f" in text:
        hidden = text.split("\f", 1)[1]
        for phrase in _find(hidden):
            add(phrase, "form_feed")
    trailing = _TRAILING.search(text)
    if trailing:
        for phrase in _find(trailing.group(1)):
            add(phrase, "trailing_blank_lines")
    if zero_width_removed:
        for phrase in _find(stripped):
            add(phrase, "zero_width")

    return {
        "detected": bool(signals),
        "followed": False,
        "zero_width_characters_removed": zero_width_removed,
        "signals": signals,
    }


def blank_instruction_lines(text: str) -> str:
    """Remove instruction phrases, and the rest of that sentence, before keywords are counted.

    Text before the instruction stays. A keyword that only appears inside
    the instruction sentence is not a category hit. HTML comments and text
    after a form feed are dropped, so a hidden keyword does not set the category.
    """

    stripped = text.translate(_ZERO_WIDTH_MAP)
    stripped = _COMMENT.sub(" ", stripped)
    if "\f" in stripped:
        stripped = stripped.split("\f", 1)[0]
    chars = list(stripped)
    lower = stripped.lower()
    for phrase in PHRASES:
        start = 0
        while True:
            index = lower.find(phrase, start)
            if index < 0:
                break
            end = index + len(phrase)
            stop = lower.find(".", end)
            if stop < 0 or stop > end + 120:
                stop = min(len(chars), end + 120)
            else:
                stop = stop + 1
            for position in range(index, stop):
                chars[position] = " "
            lower = "".join(chars).lower()
            start = stop
    return "".join(chars)
