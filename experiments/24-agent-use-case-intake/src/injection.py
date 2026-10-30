"""Detect instructions hidden in a proposal. Do not follow them.

Structured fields are the only input to the classification. Free text is
scanned so the draft can say that an instruction was seen.
"""

from __future__ import annotations

import re
from typing import Any

PROHIBITED_PAYLOAD_KEYS = frozenset(
    {
        "approved",
        "use_case_approved",
        "use_case_rejected",
        "provisioned",
        "governance_decision",
        "governance_changed_classification",
        "suggested_autonomy",
        "a3_recommended",
        "a3_out_of_scope",
        "dpia_required",
        "dpia_likely_needed",
        "atrs_likely_needed",
        "risk_tier",
        "platform_selected",
        "actions_taken",
        "manifest_approved",
        "selected",
    }
)

_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("ignore_instructions", re.compile(r"ignore (all |any )?(previous|prior|above|your) instructions", re.I)),
    ("disregard_rules", re.compile(r"disregard (the )?(catalogue|rules|instructions|policy|governance)", re.I)),
    ("force_a3", re.compile(r"(recommend(ed)? autonomy|set (the )?autonomy( level)? to|classify (this|it) as)\s+a3\b", re.I)),
    ("approve_use_case", re.compile(r"\bapprove (the |this )?use case\b", re.I)),
    ("reject_use_case", re.compile(r"\breject (the |this )?use case\b", re.I)),
    ("mark_approved", re.compile(r"\bmark (the )?classification approved\b", re.I)),
    ("provision", re.compile(r"\b(provision|deploy|publish) (the |this )?(agent|flow|bot)\b", re.I)),
    ("persona_override", re.compile(r"\byou are now\b", re.I)),
    ("system_role", re.compile(r"(?im)^\s*system\s*:")),
    ("developer_role", re.compile(r"(?im)^\s*developer\s*:")),
    ("hide_from_governance", re.compile(r"do not tell the governance", re.I)),
    ("override_classification", re.compile(r"override the (classification|decision|recommendation)", re.I)),
    ("clear_stale", re.compile(r"\b(sources are not stale|ignore the stale|clear the stale flag)\b", re.I)),
    ("skip_dpia", re.compile(r"\b(no dpia is required|dpia is not required|skip the dpia)\b", re.I)),
    ("skip_atrs", re.compile(r"\b(atrs is not needed|do not record atrs|skip the atrs)\b", re.I)),
)


def signals_in_text(text: str) -> list[str]:
    if not text:
        return []
    collapsed = re.sub(r"\s+", " ", text)
    found = []
    for name, pattern in _PATTERNS:
        if pattern.search(text) or pattern.search(collapsed):
            found.append(name)
    return found


def signals_in(value: Any) -> list[str]:
    found: list[str] = []
    if isinstance(value, str):
        found.extend(signals_in_text(value))
    elif isinstance(value, dict):
        for item in value.values():
            found.extend(signals_in(item))
    elif isinstance(value, list):
        for item in value:
            found.extend(signals_in(item))
    return list(dict.fromkeys(found))


def strip_prohibited(node: Any, path: str = "") -> tuple[Any, list[str]]:
    """Return a copy with output-shaped keys removed. Values are not kept."""

    ignored: list[str] = []
    if isinstance(node, dict):
        copied: dict[str, Any] = {}
        for key, value in node.items():
            here = f"{path}.{key}" if path else str(key)
            if key in PROHIBITED_PAYLOAD_KEYS or key == "expect":
                if key != "expect":
                    ignored.append(here)
                continue
            child, child_ignored = strip_prohibited(value, here)
            copied[key] = child
            ignored.extend(child_ignored)
        return copied, ignored
    if isinstance(node, list):
        copied_list = []
        for index, value in enumerate(node):
            child, child_ignored = strip_prohibited(value, f"{path}[{index}]")
            copied_list.append(child)
            ignored.extend(child_ignored)
        return copied_list, ignored
    return node, ignored


def strip_instruction_sentences(text: str) -> str:
    """Drop a sentence that matches an injection pattern. Do not follow it."""

    if not text:
        return ""
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    kept = [part for part in parts if part and not signals_in_text(part)]
    return " ".join(kept).strip()
