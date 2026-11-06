"""Instructions inside a wording are data. They are recorded and not followed.

A sentence that already refuses the action is not treated as an instruction,
unless it also states an affirmative favourability, recommendation, draft,
contact, or write. Payload keys that would set those outcomes are removed.
Their values are not kept.
"""

from __future__ import annotations

import re
from typing import Any

PROHIBITED_PAYLOAD_KEYS = frozenset(
    {
        "favourable_to",
        "favoured_party",
        "recommendation",
        "buy_or_sell",
        "renew",
        "endorsement_draft",
        "endorsement_text",
        "broker_contacted",
        "policy_admin_written",
        "coverage_decision",
        "interpretation_acknowledged",
        "checker_passed",
        "do_not_rely",
        "solely_automated_decision",
        "model_called",
        "network_called",
        "foundry_called",
        "document_intelligence_called",
        "a3_recommended",
        "actions_taken",
        "approved",
        "baseline_wording",
        "chosen_wording",
        "preferred_wording",
        "downstream_use_permitted",
    }
)

_INJECTION: tuple[tuple[str, str], ...] = (
    ("ignore_instructions", "ignore previous instructions"),
    ("ignore_instructions", "ignore all instructions"),
    ("ignore_instructions", "ignore the above"),
    ("persona_override", "you are now"),
    ("persona_override", "you are the specialist"),
    ("favourability_instruction", "more favourable to the insured"),
    ("favourability_instruction", "more favourable to the insurer"),
    ("favourability_instruction", "less favourable to the insured"),
    ("favourability_instruction", "better for the insured"),
    ("favourability_instruction", "better for the insurer"),
    ("recommend_instruction", "recommend renewal"),
    ("recommend_instruction", "recommend buying"),
    ("recommend_instruction", "recommend selling"),
    ("endorsement_instruction", "draft an endorsement"),
    ("endorsement_instruction", "draft a binding endorsement"),
    ("contact_instruction", "email the broker"),
    ("contact_instruction", "contact the broker"),
    ("write_instruction", "write to the policy admin"),
    ("write_instruction", "write to the policy administration"),
    ("bind_instruction", "bind cover"),
    ("force_same", "mark every row the same"),
    ("autonomy_a3", "autonomy a3"),
)

_PROHIBITED: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "favourability",
        re.compile(
            r"\b(more favourable to the (?:insured|insurer)|less favourable to the insured|"
            r"better for the (?:insured|insurer))\b",
            re.I,
        ),
    ),
    (
        "recommendation",
        re.compile(
            r"\b(recommend (?:renewal|buying|selling)|buy this (?:policy|wording)|"
            r"sell this (?:policy|wording)|renew this (?:policy|wording))\b",
            re.I,
        ),
    ),
    (
        "endorsement",
        re.compile(r"\b(draft an endorsement|draft a binding endorsement)\b", re.I),
    ),
    (
        "contact_broker",
        re.compile(r"\b(email the broker|contact the broker|write to the broker)\b", re.I),
    ),
    (
        "write_or_bind",
        re.compile(
            r"\b(write to the policy admin(?:istration)? system|bind cover)\b",
            re.I,
        ),
    ),
)

_REFUSAL = re.compile(r"\b(do not|don't|must not|never|cannot|can't)\b", re.I)
_AFFIRMATIVE = re.compile(
    r"\b(more favourable to the|less favourable to the|better for the (?:insured|insurer)|"
    r"recommend (?:renewal|buying|selling)|draft an endorsement|draft a binding endorsement|"
    r"email the broker|contact the broker|write to the policy admin|bind cover)\b",
    re.I,
)

ZERO_WIDTH_CHARS = ("\u200b", "\u200c", "\u200d", "\ufeff", "\u2060")
_ZERO_WIDTH_MAP = {ord(char): None for char in ZERO_WIDTH_CHARS}
_COMMENT = re.compile(r"<!--(.*?)-->", re.DOTALL)
_TRAILING = re.compile(r"\n{3,}(.*)\Z", re.DOTALL)


def is_refusal_sentence(sentence: str) -> bool:
    return bool(_REFUSAL.search(sentence)) and not _AFFIRMATIVE.search(sentence)


def _sentences(text: str) -> list[str]:
    parts = re.split(r"[\n.]+", text)
    return [part.strip() for part in parts if part.strip()]


def _plain(text: str) -> str:
    return text.translate(_ZERO_WIDTH_MAP)


def injection_codes(text: str) -> list[str]:
    found: list[str] = []
    if not text:
        return found
    for sentence in _sentences(_plain(text)):
        if is_refusal_sentence(sentence):
            continue
        lowered = sentence.casefold()
        for code, phrase in _INJECTION:
            if phrase in lowered and code not in found:
                found.append(code)
    return found


def prohibited_codes(text: str) -> list[str]:
    found: list[str] = []
    if not text:
        return found
    for sentence in _sentences(_plain(text)):
        if is_refusal_sentence(sentence):
            continue
        for code, pattern in _PROHIBITED:
            if pattern.search(sentence) and code not in found:
                found.append(code)
    return found


def strip_prohibited(node: Any, path: str = "") -> tuple[Any, list[str]]:
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


def hidden_payloads(text: str) -> list[dict[str, str]]:
    """Comment bodies, a trailing blank-line tail, and zero-width characters.

    The returned text is for the scanner only. It is not copied into a quote.
    """
    found: list[dict[str, str]] = []
    if not isinstance(text, str) or not text:
        return found
    for match in _COMMENT.finditer(text):
        found.append({"hidden_in": "html_comment", "text": match.group(1)})
    trailing = _TRAILING.search(text)
    if trailing:
        found.append({"hidden_in": "trailing_blank_lines", "text": trailing.group(1)})
    if any(char in text for char in ZERO_WIDTH_CHARS):
        found.append({"hidden_in": "zero_width", "text": _plain(text)})
    return found
