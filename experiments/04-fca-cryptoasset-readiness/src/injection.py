"""Detect instructions aimed at the checker inside an uploaded policy.

Policy text is data. A line that matches is recorded and is not used as
evidence. If the instruction only appears once newlines are collapsed, the
whole document is quarantined and none of it is used as evidence.
"""

from __future__ import annotations

import re

# Patterns are aimed at instructions to the checker, not at ordinary
# control language such as "the MLRO files a SAR".
_RAW_PATTERNS: list[tuple[str, str]] = [
    (
        "ignore_instructions",
        r"ignore\s+(?:all\s+|any\s+)?(?:previous|prior|above)\s+instructions",
    ),
    (
        "disregard_instructions",
        r"disregard\s+(?:your|the|all)\s+(?:system\s+)?instructions",
    ),
    (
        "forget_instructions",
        r"forget\s+(?:everything|all)\s+you\s+(?:were|have been)\s+told",
    ),
    ("mark_ready", r"mark\s+(?:the\s+)?firm\s+as\s+ready"),
    ("no_gaps", r"conclude\s+(?:that\s+)?there\s+are\s+no\s+gaps"),
    ("set_readiness", r"set\s+readiness(?:_conclusion)?\s+to"),
    ("suppress_gaps", r"do\s+not\s+report\s+(?:any\s+|the\s+)?gaps"),
    (
        "override_catalogue",
        r"override\s+the\s+(?:checklist|sources|disclaimer|register|catalogue|catalog)",
    ),
    (
        "promote_consultation",
        r"treat\s+(?:the\s+)?consultation(?:-stage|\s+stage)?\s+(?:rules|items|material)\s+as\s+final",
    ),
    ("alter_currency", r"change\s+(?:the\s+)?last[_\s-]?verified"),
    ("new_instructions", r"new\s+instructions\s*:"),
    (
        "role_tag",
        r"(?:^|\n)\s*(?:system|assistant)\s*:\s*(?:ignore|you\b|mark\b|set\b|override|do not|disregard)",
    ),
    ("xml_tag", r"</?(?:system|instructions)\s*>"),
    (
        "you_are_now",
        r"you\s+are\s+now\s+(?:a\s+|an\s+)?(?:compliant|authorised|authorized|ready|unrestricted)",
    ),
]

PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (name, re.compile(expression, re.IGNORECASE | re.MULTILINE))
    for name, expression in _RAW_PATTERNS
]


def pattern_ids_in(text: str) -> list[str]:
    """Return pattern ids that match text, in catalogue order."""
    return [name for name, pattern in PATTERNS if pattern.search(text)]


def scan_document(text: str) -> dict:
    """Scan one document. Injection is never followed."""
    lines = text.splitlines()
    findings: list[dict] = []
    kept: list[str] = []
    line_pattern_ids: set[str] = set()

    for number, line in enumerate(lines, start=1):
        hits = pattern_ids_in(line)
        if hits:
            line_pattern_ids.update(hits)
            findings.append(
                {
                    "line": number,
                    "pattern_ids": hits,
                    "excerpt": line.strip()[:240],
                    "scope": "line",
                }
            )
        else:
            kept.append(line)

    collapsed = re.sub(r"\s+", " ", text).strip()
    split = [name for name in pattern_ids_in(collapsed) if name not in line_pattern_ids]
    if split:
        findings.append(
            {
                "line": None,
                "pattern_ids": split,
                "excerpt": collapsed[:240],
                "scope": "split_across_lines",
            }
        )

    quarantine = bool(split)
    return {
        "detected": bool(findings),
        "quarantine_document": quarantine,
        "followed": False,
        "findings": findings,
        "usable_text": "" if quarantine else "\n".join(kept),
    }
