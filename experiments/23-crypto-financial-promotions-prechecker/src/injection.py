"""Instructions aimed at the checker inside an untrusted promotion.

A match is recorded and is not used as evidence. It is not a finding
that the promotion may be communicated.
"""

from __future__ import annotations

import re

_RAW_PATTERNS: list[tuple[str, str]] = [
    (
        "ignore_instructions",
        r"ignore\s+(?:all\s+|any\s+)?(?:previous|prior|above)\s+instructions",
    ),
    (
        "disregard_rules",
        r"disregard\s+(?:the\s+|all\s+)?(?:rules|instructions|checklist)",
    ),
    (
        "you_are_approver",
        r"you\s+are\s+(?:now\s+)?(?:the\s+)?s\.?\s*21\s+approver",
    ),
    ("approve_promotion", r"approve\s+this\s+promotion"),
    ("mark_compliant", r"mark\s+(?:this\s+)?(?:promotion\s+)?as\s+compliant"),
    ("no_issues", r"there\s+are\s+no\s+issues"),
    ("do_not_flag", r"do\s+not\s+flag"),
    ("publish_this", r"publish\s+this"),
    (
        "set_decision",
        r"set\s+s21_approver_decision|s21_approver_decision\s*[:=]",
    ),
    ("compliance_opinion", r"compliance\s+opinion\s+is"),
    ("new_instructions", r"new\s+instructions\s*:"),
    ("system_prefix", r"(?:^|\n)\s*system\s*:"),
    ("override_checklist", r"override\s+the\s+checklist"),
]

PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (name, re.compile(expression, re.IGNORECASE | re.MULTILINE))
    for name, expression in _RAW_PATTERNS
]

PROHIBITED_PAYLOAD_KEYS = (
    "promotion_approved",
    "published",
    "compliance_opinion",
    "s21_approver_decision",
    "rewrite",
    "rewrite_drafted",
    "approve",
    "publish",
)


def pattern_ids_in(text: str) -> list[str]:
    """Return pattern ids that match text, in catalogue order."""
    return [name for name, pattern in PATTERNS if pattern.search(text)]


def scan_document(text: str) -> dict:
    """Scan one promotion. Injection is never followed."""
    lines = text.splitlines() or [text]
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
                    "excerpt": line.strip()[:180],
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
                "excerpt": collapsed[:180],
                "scope": "split_across_lines",
            }
        )

    quarantine = bool(split)
    signals: list[str] = []
    for finding in findings:
        for pattern_id in finding["pattern_ids"]:
            if pattern_id not in signals:
                signals.append(pattern_id)
    return {
        "detected": bool(findings),
        "followed": False,
        "quarantine_document": quarantine,
        "signals": signals,
        "findings": findings,
        "usable_text": "" if quarantine else "\n".join(kept),
    }
