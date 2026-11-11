"""Visit notes are data. An instruction in them is recorded and not followed.

Completion-specific clauses are removed here. Shared clauses are removed by
Experiment 46. A sentence that also states a fact keeps that fact.
"Do not enter the loft" is a site rule. It is not removed.
"""

from __future__ import annotations

import re

ZERO_WIDTH = ("\u200b", "\u200c", "\u200d", "\ufeff", "\u2060")
_ZERO_WIDTH_MAP = {ord(char): None for char in ZERO_WIDTH}

# Narrow on purpose. A site rule such as "Do not enter the loft" must not match.
PATTERNS: tuple[tuple[str, str], ...] = (
    ("close_the_job", r"\bclose (?:this |the )?job\b"),
    ("raise_a_charge", r"\b(?:raise|add) (?:a |the )?charge\b"),
    ("invoice_the_customer", r"\binvoice the (?:tenant|customer|resident)\b"),
    ("order_the_parts", r"\border (?:the |these )?parts\b"),
    ("contact_the_customer", r"\b(?:text|email|call|contact|ring) the (?:tenant|customer|resident)\b"),
    ("approve_all_fields", r"\b(?:approve|mark) all fields\b"),
    ("skip_approval", r"\bskip (?:the )?approval\b"),
    ("write_the_record", r"\bwrite the (?:record|work order|job)\b"),
    ("already_approved", r"\bfields? (?:are |have been )?already approved\b"),
)

_COMPILED = tuple((name, re.compile(pattern, re.IGNORECASE)) for name, pattern in PATTERNS)
_COMMENT = re.compile(r"<!--(.*?)-->", re.DOTALL)
_WORD = re.compile(r"[A-Za-z]{3,}")


def _normalise_apostrophe(text: str) -> str:
    return text.replace("\u2019", "'").replace("\u2018", "'")


def unwrap(text: str) -> tuple[str, dict]:
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


def local_signals(text: str) -> list[dict]:
    """Record completion-specific instruction signals. Do not return the sentence."""

    if not text:
        return []
    raw = _normalise_apostrophe(text)
    unwrapped, notes = unwrap(text)
    found: list[dict] = []
    seen: set[str] = set()
    for name, pattern in _COMPILED:
        if not pattern.search(unwrapped) or name in seen:
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


def excise_local(text: str) -> str:
    """Remove completion-specific instruction clauses. Keep the rest of the sentence."""

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
