"""Free text is data. An instruction in it is recorded and not followed.

Only the instruction phrase is removed. The rest of the sentence stays, so a
complaint that shares a sentence with an instruction is still coded.
"""

from __future__ import annotations

import re

ZERO_WIDTH = ("\u200b", "\u200c", "\u200d", "\ufeff", "\u2060")
_ZERO_WIDTH_MAP = {ord(char): None for char in ZERO_WIDTH}

PATTERNS: tuple[tuple[str, str], ...] = (
    ("ignore_instructions", r"ignore (?:all |any )?(?:previous |prior |above |your )?instructions"),
    ("ignore_the_above", r"ignore the above"),
    ("disregard_rules", r"disregard (?:the )?(?:rules|limitations|sample|catalogue|catalog)"),
    ("you_are_now", r"you are now"),
    ("system_prompt", r"system prompt"),
    ("mark_all_positive", r"mark (?:all|every) records? positive"),
    ("mark_ready", r"(?:this pack is approved|ready to publish|mark (?:the |this )?pack ready)"),
    ("publish_pack", r"\bpublish (?:the |this )?pack\b"),
    ("contact_customer", r"\bcontact the customer\b"),
    ("duty_was_met", r"\b(?:the )?duty was met\b"),
    ("prin_was_met", r"\bprin 2a\.(?:5|6|8|9) was met\b"),
    ("drop_limitations", r"\bdo not include limitations\b"),
    ("override_sample", r"\boverride the sample\b"),
    ("conclude_customer", r"\bconclude that\b"),
    ("already_confirmed", r"\b(?:sample frame|limitations) (?:is |are |has been |have been )?already confirmed\b"),
)

_COMPILED = tuple((name, re.compile(pattern, re.IGNORECASE)) for name, pattern in PATTERNS)
_COMMENT = re.compile(r"<!--(.*?)-->", re.DOTALL)
_WORD = re.compile(r"[A-Za-z]{3,}")


def _apostrophe(text: str) -> str:
    return text.replace("\u2019", "'").replace("\u2018", "'")


def unwrap(text: str) -> tuple[str, dict]:
    """Make a hidden instruction visible to the matcher, then the excise step removes it."""

    if not isinstance(text, str):
        return "", {"zero_width_removed": 0, "had_html_comment": False, "had_form_feed": False}
    zero_width_removed = sum(text.count(char) for char in ZERO_WIDTH)
    cleaned = _apostrophe(text.translate(_ZERO_WIDTH_MAP))
    had_comment = bool(_COMMENT.search(cleaned))
    cleaned = _COMMENT.sub(lambda match: " " + match.group(1) + " ", cleaned)
    had_form_feed = "\f" in cleaned
    cleaned = cleaned.replace("\f", " ")
    return cleaned, {
        "zero_width_removed": zero_width_removed,
        "had_html_comment": had_comment,
        "had_form_feed": had_form_feed,
    }


def signals_in(text: str) -> list[dict]:
    """Record instruction signals. Do not return the surrounding sentence."""

    if not isinstance(text, str) or not text:
        return []
    raw = _apostrophe(text)
    unwrapped, notes = unwrap(text)
    found: list[dict] = []
    seen: set[str] = set()
    for name, pattern in _COMPILED:
        if name in seen or not pattern.search(unwrapped):
            continue
        seen.add(name)
        if notes["zero_width_removed"] and not pattern.search(raw):
            hidden_in = "zero_width"
        elif notes["had_html_comment"] and not pattern.search(_COMMENT.sub(" ", raw)):
            hidden_in = "html_comment"
        elif notes["had_form_feed"] and not pattern.search(raw.split("\f", 1)[0]):
            hidden_in = "form_feed"
        else:
            hidden_in = "body"
        found.append({"signal": name, "hidden_in": hidden_in, "followed": False})
    return found


def excise(text: str) -> str:
    """Remove instruction phrases. Keep every other word."""

    unwrapped, _notes = unwrap(text)
    parts = re.split(r"(?<=[.!?])\s+", unwrapped.strip())
    kept: list[str] = []
    for part in parts:
        remaining = part
        for _name, pattern in _COMPILED:
            remaining = pattern.sub(" ", remaining)
        remaining = re.sub(r"\s+", " ", remaining).strip(" \t,;:-")
        if _WORD.search(remaining):
            kept.append(remaining)
    return " ".join(kept).strip()
