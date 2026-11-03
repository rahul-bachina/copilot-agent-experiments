"""Strip result-shaped keys and record instructions aimed at this generator.

A sentence that forbids the action is not a hit. Fixture text cannot set
maintainer_approved, merged, pushed, or the case list.
"""

from __future__ import annotations

import re
from typing import Any

PROHIBITED_PAYLOAD_KEYS = frozenset(
    {
        "maintainer_approved",
        "merged",
        "pushed",
        "protected_branch_targeted",
        "agent_under_test_edited",
        "pr_opened",
        "tests_applied",
        "foundry_evaluation_called",
        "foundry_called",
        "a3_recommended",
        "model_called",
        "network_called",
        "approved",
        "score",
        "drafted",
        "cases",
        "actions_taken",
        "do_not_rely",
    }
)

_INJECTION = re.compile(
    r"("
    r"ignore (all |any )?(previous|prior|above|your) instructions"
    r"|disregard (the )?(rules|policy|instructions)"
    r"|you must (now )?(merge|push|approve|edit)"
    r"|merge (the |this )?(pull request|pr)\b"
    r"|push (it |this )?(to )?(main|master|production|release)\b"
    r"|edit the agent under test"
    r"|set maintainer_approved\b"
    r"|mark the tests approved"
    r"|^\s*system\s*:"
    r"|^\s*developer\s*:"
    r")",
    re.I,
)

_NEGATION = re.compile(r"\b(do not|don't|dont|never|must not)\b", re.I)


def split_sentences(text: str) -> list[str]:
    parts = re.split(r"[\n]+|(?<=[.!?])\s+", text.strip())
    return [part.strip() for part in parts if part.strip()]


def strip_prohibited(value: Any, prefix: str = "") -> tuple[Any, list[str]]:
    ignored: list[str] = []
    if isinstance(value, dict):
        kept = {}
        for key, item in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            if key in PROHIBITED_PAYLOAD_KEYS:
                ignored.append(path)
                continue
            cleaned, nested = strip_prohibited(item, path)
            kept[key] = cleaned
            ignored.extend(nested)
        return kept, ignored
    if isinstance(value, list):
        cleaned_list = []
        for index, item in enumerate(value):
            cleaned, nested = strip_prohibited(item, f"{prefix}[{index}]")
            cleaned_list.append(cleaned)
            ignored.extend(nested)
        return cleaned_list, ignored
    return value, ignored


def scan_strings(value: Any, prefix: str = "") -> list[dict[str, str]]:
    hits: list[dict[str, str]] = []
    if isinstance(value, dict):
        for key, item in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            hits.extend(scan_strings(item, path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            hits.extend(scan_strings(item, f"{prefix}[{index}]"))
    elif isinstance(value, str):
        for sentence in split_sentences(value):
            if _NEGATION.search(sentence):
                continue
            if _INJECTION.search(sentence):
                hits.append({"path": prefix or "(root)", "sentence": sentence[:240]})
    return hits
