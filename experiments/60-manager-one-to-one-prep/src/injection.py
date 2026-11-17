"""Instructions inside notes are data. They are recorded and not followed."""

from __future__ import annotations

import re

_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("ignore_instructions", re.compile(r"\bignore (?:previous|all) instructions\b", re.I)),
    ("ignore_instructions", re.compile(r"\bignore the above\b", re.I)),
    (
        "strip_label",
        re.compile(
            r"\b(?:strip|remove|drop|ignore) the (?:legal hold|retention(?: label)?|marking|protective marking)\b",
            re.I,
        ),
    ),
    ("persona", re.compile(r"\byou are now\b", re.I)),
    ("persona", re.compile(r"\bsystem prompt\b", re.I)),
    ("approve_in_text", re.compile(r"\bhuman_approval\b", re.I)),
    (
        "approve_in_text",
        re.compile(r"\b(?:this (?:note|selection|prep(?:aration)?) is approved|manager approved)\b", re.I),
    ),
    (
        "force_unselected",
        re.compile(
            r"\b(?:read the mailbox|open the inbox|browse (?:their |his |her )?(?:emails?|chats?|messages)|"
            r"include the (?:mailbox|inbox|chat))\b",
            re.I,
        ),
    ),
    ("autonomy_a3", re.compile(r"\bautonomy a3\b", re.I)),
)

_ROLE_CLAIM = re.compile(
    r"\b(?:i am|i'm)\s+(?:the\s+)?(?:line manager|hr|human resources|a guest|not a guest)\b",
    re.I,
)
_CLEARANCE_CLAIM = re.compile(
    r"\b(?:my|our) clearance is\s+(?:top secret|secret|official-sensitive|official)\b",
    re.I,
)


def injection_codes(text: str) -> list[str]:
    if not isinstance(text, str) or not text:
        return []
    found: list[str] = []
    for code, pattern in _PATTERNS:
        if pattern.search(text) and code not in found:
            found.append(code)
    return found


def untrusted_claims(text: str) -> list[str]:
    if not isinstance(text, str) or not text:
        return []
    found: list[str] = []
    if _ROLE_CLAIM.search(text):
        found.append("self_declared_role")
    if _CLEARANCE_CLAIM.search(text):
        found.append("self_declared_clearance")
    return found


def redact_untrusted_claims(text: str) -> str:
    """Replace boasts so a quotation does not repeat them as facts."""
    text = _CLEARANCE_CLAIM.sub("[untrusted clearance claim]", text)
    text = _ROLE_CLAIM.sub("[untrusted role claim]", text)
    return text
