"""Detect instructions aimed at this checker. Do not follow them.

A sentence that already refuses the action is not treated as an instruction.
Payload keys that would approve a threshold, record a release, or set a score
are removed before scoring. Their values are not kept.
"""

from __future__ import annotations

import re
from typing import Any

PROHIBITED_PAYLOAD_KEYS = frozenset(
    {
        "threshold_approved_by_evaluation_owner",
        "threshold_approved",
        "release_decision",
        "pass_fail_released",
        "pass_fail",
        "groundedness_clearance",
        "draft_bar_met",
        "supported_rate",
        "verdict",
        "verdicts",
        "approved",
        "passed",
        "failed",
        "model_called",
        "network_called",
        "foundry_evaluator_called",
        "a3_recommended",
        "actions_taken",
        "do_not_rely",
        "decision",
    }
)

_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("ignore_instructions", re.compile(r"ignore (all |any |the )?(previous|prior|above|your) instructions", re.I)),
    ("approve_thresholds", re.compile(r"\bapprove (the |these )?(thresholds|threshold)\b", re.I)),
    ("release", re.compile(r"\b(release (this|the) agent|mark the release as pass|record a pass|record a fail)\b", re.I)),
    ("clearance", re.compile(r"\bgroundedness[_ ]clearance\b", re.I)),
    ("force_supported", re.compile(r"\bmark every claim (as )?supported\b", re.I)),
    ("persona_override", re.compile(r"\byou are now\b", re.I)),
)

_REFUSAL = re.compile(
    r"\b(do not|don't|must not|never|cannot|can't|not followed|refuse|refused)\b",
    re.I,
)


def _sentences(text: str) -> list[str]:
    parts = re.split(r"[\n.]+", text)
    return [part.strip() for part in parts if part.strip()]


def signals_in_text(text: str) -> list[str]:
    if not text:
        return []
    found: list[str] = []
    for sentence in _sentences(text):
        if _REFUSAL.search(sentence):
            continue
        for name, pattern in _PATTERNS:
            if pattern.search(sentence) and name not in found:
                found.append(name)
    return found


def strip_prohibited(node: Any, path: str = "") -> tuple[Any, list[str]]:
    """Return a copy with output-shaped keys removed. Values are not kept."""
    ignored: list[str] = []
    if isinstance(node, dict):
        copied: dict[str, Any] = {}
        for key, value in node.items():
            here = f"{path}.{key}" if path else str(key)
            if key in PROHIBITED_PAYLOAD_KEYS:
                ignored.append(here)
                continue
            child, nested = strip_prohibited(value, here)
            copied[key] = child
            ignored.extend(nested)
        return copied, ignored
    if isinstance(node, list):
        copied_list = []
        for index, value in enumerate(node):
            child, nested = strip_prohibited(value, f"{path}[{index}]")
            copied_list.append(child)
            ignored.extend(nested)
        return copied_list, ignored
    return node, ignored


def scan_strings(node: Any, path: str = "") -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    if isinstance(node, str):
        codes = signals_in_text(node)
        if codes:
            found.append({"path": path or "value", "codes": codes})
    elif isinstance(node, dict):
        for key, value in node.items():
            here = f"{path}.{key}" if path else str(key)
            found.extend(scan_strings(value, here))
    elif isinstance(node, list):
        for index, value in enumerate(node):
            found.extend(scan_strings(value, f"{path}[{index}]"))
    return found
