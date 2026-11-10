"""Question text is data. Instruction spans are recorded and not followed.

Only the instruction span is removed. The rest of the sentence stays, so a
real question is not dropped because an instruction was attached to it.
"Do not escalate." is an instruction. "The plan does not include accidental
damage." is not.
"""

from __future__ import annotations

import re

ZERO_WIDTH = ("\u200b", "\u200c", "\u200d", "\ufeff", "\u2060")
_ZERO_WIDTH_MAP = {ord(char): None for char in ZERO_WIDTH}
_COMMENT = re.compile(r"<!--(.*?)-->", re.DOTALL)

_SPANS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "ignore_instructions",
        re.compile(
            r"ignore\s+(?:all\s+|any\s+)?(?:previous\s+|prior\s+|above\s+|your\s+)?instructions",
            re.IGNORECASE,
        ),
    ),
    ("ignore_instructions", re.compile(r"ignore\s+the\s+above", re.IGNORECASE)),
    (
        "disregard_rules",
        re.compile(r"disregard\s+(?:the\s+)?(?:rules|table|catalogue|catalog)\b", re.IGNORECASE),
    ),
    ("you_are_now", re.compile(r"you\s+are\s+now", re.IGNORECASE)),
    ("system_prompt", re.compile(r"system\s+prompt", re.IGNORECASE)),
    ("reveal_prompt", re.compile(r"reveal\s+(?:the\s+|your\s+)?prompt", re.IGNORECASE)),
    (
        "do_not_escalate",
        re.compile(
            r"\b(?:do\s+not|don't|never)\s+"
            r"(?:escalate|route(?:\s+this)?\s+to\s+a\s+(?:human|person)|"
            r"ask(?:\s+for)?\s+a\s+(?:human|person))\b",
            re.IGNORECASE,
        ),
    ),
    (
        "do_not_escalate",
        re.compile(r"\b(?:skip\s+the\s+human|no\s+human|do\s+not\s+offer\s+a\s+person)\b", re.IGNORECASE),
    ),
    (
        "grant_now",
        re.compile(
            r"\b(?:grant|approve)\s+(?:the\s+|this\s+)?(?:entitlement|cover|coverage)(?:\s+now)?\b",
            re.IGNORECASE,
        ),
    ),
    (
        "refuse_now",
        re.compile(
            r"\b(?:refuse|decline|reject)\s+(?:the\s+|this\s+)?(?:entitlement|cover|coverage)(?:\s+now)?\b",
            re.IGNORECASE,
        ),
    ),
    (
        "change_now",
        re.compile(
            r"\b(?:change|update|amend|waive)\s+(?:the\s+|this\s+)?(?:entitlement|plan|exclusion)(?:\s+now)?\b",
            re.IGNORECASE,
        ),
    ),
    ("mark_covered", re.compile(r"\bmark\s+(?:me|the\s+customer|this)\s+covered\b", re.IGNORECASE)),
    ("override_rules", re.compile(r"\boverride\s+(?:the\s+)?(?:rules|table|stale)\b", re.IGNORECASE)),
    ("autonomy_a3", re.compile(r"\bautonomy\s+a3\b", re.IGNORECASE)),
    ("send_now", re.compile(r"\bsend\s+(?:the\s+)?(?:email|message|letter|decision)\s+now\b", re.IGNORECASE)),
)

_DISPUTE: tuple[tuple[str, str], ...] = (
    ("customer_disputes", "i dispute"),
    ("customer_disputes", "this is wrong"),
    ("customer_disputes", "you refused"),
    ("customer_disputes", "i was told i was covered"),
    ("customer_disputes", "i was told i was not covered"),
    ("customer_disputes", "unfair term"),
    ("customer_disputes", "complaint about my cover"),
    ("customer_disputes", "complaint about cover"),
    ("customer_disputes", "i do not agree"),
)


def plain(text: str) -> str:
    return (text or "").translate(_ZERO_WIDTH_MAP)


def hidden_and_visible(text: str) -> tuple[str, list[str]]:
    """Return visible text and HTML-comment bodies. Comments are not matched."""
    raw = plain(text or "")
    hidden = [match.group(1) for match in _COMMENT.finditer(raw)]
    visible = _COMMENT.sub(" ", raw)
    return visible, hidden


def signals_in(text: str) -> list[str]:
    found: list[str] = []
    if not text:
        return found
    for name, pattern in _SPANS:
        if pattern.search(plain(text)) and name not in found:
            found.append(name)
    return found


def dispute_codes(text: str) -> list[str]:
    folded = re.sub(r"\s+", " ", plain(text)).casefold()
    found: list[str] = []
    for code, phrase in _DISPUTE:
        if phrase in folded and code not in found:
            found.append(code)
    return found


def strip_instruction_spans(text: str) -> str:
    """Remove instruction spans only. Keep the surrounding words."""
    cleaned = plain(text or "")
    cleaned = _COMMENT.sub(" ", cleaned)
    for _name, pattern in _SPANS:
        cleaned = pattern.sub(" ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    cleaned = re.sub(r"\s+([?.!,;:])", r"\1", cleaned)
    cleaned = re.sub(r"(?:^|\s)[?.!,;:]+(?=\s|$)", " ", cleaned)
    return re.sub(r"\s+", " ", cleaned).strip()
