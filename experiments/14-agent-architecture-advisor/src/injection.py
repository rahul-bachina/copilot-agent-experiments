"""Detect instructions hidden in a use case. Do not follow them.

Structured fields are the only input to the rules. Free text is scanned
so the draft can say that an instruction was seen and was not followed.
"""

from __future__ import annotations

import re
from typing import Any

PROHIBITED_PAYLOAD_KEYS = frozenset(
    {
        "selected_platform",
        "platform_selected",
        "architect_decision",
        "architect_confirmed",
        "decision",
        "deployed",
        "deploy",
        "approved",
        "manifest_approved",
        "recommended_autonomy",
        "a3_recommended",
        "select_platform",
        "autonomy_level",
    }
)

_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("ignore_instructions", re.compile(r"ignore (all |any )?(previous|prior|above|your) instructions", re.I)),
    ("disregard_rules", re.compile(r"disregard (the )?(catalogue|rules|instructions|policy)", re.I)),
    ("force_a3", re.compile(r"(recommend(ed)? autonomy|set (the )?autonomy( level)? to)\s+a3", re.I)),
    ("persona_override", re.compile(r"\byou are now\b", re.I)),
    ("deploy", re.compile(r"\bdeploy (the |this )?agent\b", re.I)),
    ("select_platform", re.compile(r"\bselect (the )?platform\b", re.I)),
    ("approve_manifest", re.compile(r"\bapprove the manifest\b", re.I)),
    ("system_role", re.compile(r"(?im)^\s*system\s*:")),
    ("developer_role", re.compile(r"(?im)^\s*developer\s*:")),
    ("hide_from_architect", re.compile(r"do not tell the architect", re.I)),
    ("override", re.compile(r"override the (decision|recommendation)", re.I)),
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


def scan_strings(node: Any) -> list[str]:
    found: list[str] = []
    if isinstance(node, str):
        for name in signals_in_text(node):
            if name not in found:
                found.append(name)
        return found
    if isinstance(node, dict):
        for value in node.values():
            for name in scan_strings(value):
                if name not in found:
                    found.append(name)
        return found
    if isinstance(node, list):
        for value in node:
            for name in scan_strings(value):
                if name not in found:
                    found.append(name)
    return found
