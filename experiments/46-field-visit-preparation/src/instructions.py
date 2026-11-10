"""Work-order text is data. An instruction in it is recorded and not followed.

A sentence that also states a fact keeps that fact. Only the instruction
clause is removed. "Do not enter the loft" is a site instruction for the
technician. It is not an instruction to this agent. "Do not escalate." is.
"""

from __future__ import annotations

import re

ZERO_WIDTH = ("\u200b", "\u200c", "\u200d", "\ufeff", "\u2060")
_ZERO_WIDTH_MAP = {ord(char): None for char in ZERO_WIDTH}

# Narrow on purpose. A site rule such as "Do not enter the loft" must not match.
PATTERNS: tuple[tuple[str, str], ...] = (
    ("ignore_instructions", r"ignore (?:all |any )?(?:previous |prior |above |your )?instructions"),
    ("ignore_the_above", r"ignore the above"),
    ("disregard_rules", r"disregard (?:the )?(?:rules|safety|catalogue|catalog|brief)"),
    ("you_are_now", r"you are now"),
    ("system_prompt", r"system prompt"),
    ("reveal_prompt", r"reveal (?:the |your )?prompt"),
    ("override_confirmation", r"override (?:the )?(?:technician|confirmation|human|approval|safety)"),
    ("override_stale", r"override (?:the )?stale"),
    ("close_work_order", r"\bclose (?:this |the )?work order\b"),
    ("schedule_or_dispatch", r"\b(?:schedule|dispatch) (?:the |this )?(?:visit|technician)\b"),
    ("mark_complete", r"\bmark (?:the |this )?(?:visit|work order) (?:as )?(?:complete|closed|done)\b"),
    ("skip_confirmation", r"\bskip (?:the )?confirmation\b"),
    ("do_not_escalate", r"\bdo not escalate\b"),
    ("dont_escalate", r"\bdon't escalate\b"),
    ("do_not_flag", r"\bdo not flag\b"),
    ("dont_flag", r"\bdon't flag\b"),
    ("mark_safe", r"\bmark (?:it |this |the (?:visit|site) )?(?:as )?safe\b"),
    ("not_a_hazard", r"\bthis is not a hazard\b"),
    ("already_confirmed", r"\b(?:asset|safety) (?:context )?(?:is |has been )?already confirmed\b"),
    ("clear_the_hold", r"\bclear the (?:safety )?hold\b"),
    ("authorise_entry", r"\b(?:authorise|authorize) entry\b"),
)

_COMPILED = tuple((name, re.compile(pattern, re.IGNORECASE)) for name, pattern in PATTERNS)
_COMMENT = re.compile(r"<!--(.*?)-->", re.DOTALL)
_WORD = re.compile(r"[A-Za-z]{3,}")


def _normalise_apostrophe(text: str) -> str:
    return text.replace("\u2019", "'").replace("\u2018", "'")


def unwrap(text: str) -> tuple[str, dict]:
    """Return text with hidden carriers still readable, plus carrier notes.

    HTML comments are kept as their inner text, so a hazard written only in
    a comment is still available to the keyword lists. Instruction clauses
    are removed later, by excise_clauses, and the rest of the sentence stays.
    """

    if not isinstance(text, str):
        return "", {"zero_width_removed": 0, "had_html_comment": False, "had_form_feed": False}
    zero_width_removed = sum(text.count(char) for char in ZERO_WIDTH)
    cleaned = _normalise_apostrophe(text.translate(_ZERO_WIDTH_MAP))
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

    if not text:
        return []
    raw = _normalise_apostrophe(text)
    unwrapped, notes = unwrap(text)
    found: list[dict] = []
    seen: set[str] = set()
    for name, pattern in _COMPILED:
        if not pattern.search(unwrapped):
            continue
        if name in seen:
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


def excise_clauses(text: str) -> str:
    """Remove instruction clauses. Keep every other word in the sentence.

    A sentence that is only an instruction is dropped. A sentence that also
    names a defect keeps the defect. "Do not enter the loft" is not a clause
    this function removes.
    """

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
