"""Instructions inside a credit pack are data. They are recorded and not followed.

A sentence that already refuses the action is not treated as an instruction,
unless it also states an affirmative approve, decline, limit, contact, post,
or SAR. Payload keys that would set a decision are removed. Their values are
not kept.
"""

from __future__ import annotations

import re
from typing import Any

PROHIBITED_PAYLOAD_KEYS = frozenset(
    {
        "credit_decision",
        "recommendation",
        "limit_set",
        "limit_approved",
        "approved_limit",
        "customer_contacted",
        "bureau_contacted",
        "core_banking_posted",
        "crm_posted",
        "sar_filed",
        "suspicion_decided",
        "discrimination_found",
        "consumer_duty_met",
        "reading_acknowledged",
        "draft_approved_for_use",
        "summary_accepted_as_decision",
        "checker_passed",
        "do_not_rely",
        "proposed_facts",
        "resolutions",
        "actions_taken",
        "model_called",
        "network_called",
        "foundry_called",
        "fabric_called",
        "lakehouse_written",
        "a3_recommended",
        "approved",
        "declined",
        "decision",
        "solely_automated_decision",
    }
)

_INJECTION: tuple[tuple[str, str], ...] = (
    ("ignore_instructions", "ignore previous instructions"),
    ("ignore_instructions", "ignore all instructions"),
    ("ignore_instructions", "ignore the above"),
    ("persona_override", "you are now"),
    ("persona_override", "you are the credit officer"),
    ("approve_instruction", "approve the facility"),
    ("approve_instruction", "approve this credit"),
    ("decline_instruction", "decline this credit"),
    ("decline_instruction", "decline the facility"),
    ("limit_instruction", "set the limit"),
    ("contact_customer", "contact the customer"),
    ("contact_customer", "email the customer"),
    ("contact_bureau", "contact the bureau"),
    ("post_core", "post to the core"),
    ("post_crm", "post to the crm"),
    ("file_sar", "file a sar"),
    ("file_sar", "submit a sar"),
    ("force_supported", "mark every fact supported"),
    ("autonomy_a3", "autonomy a3"),
)

_PROHIBITED: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "approve_or_decline",
        re.compile(
            r"\b(approve(?:s|d)? (?:the |this )?(?:facility|credit|application|limit)|"
            r"decline(?:s|d)? (?:the |this )?(?:facility|credit|application)|"
            r"recommendation is (?:to )?(?:approve|decline))\b",
            re.I,
        ),
    ),
    (
        "set_limit",
        re.compile(
            r"\b(set the limit|approved limit is|recommended limit is|limit should be)\b",
            re.I,
        ),
    ),
    (
        "contact",
        re.compile(
            r"\b(contact the customer|email the customer|contact the bureau|"
            r"query the bureau|call the bureau)\b",
            re.I,
        ),
    ),
    (
        "post_or_file",
        re.compile(
            r"\b(post to the core|post to the crm|write to the core banking|"
            r"write to the crm|file a sar|submit a sar)\b",
            re.I,
        ),
    ),
)

_REFUSAL = re.compile(r"\b(do not|don't|must not|never|cannot|can't)\b", re.I)
_AFFIRMATIVE = re.compile(
    r"\b(recommendation is (?:to )?(?:approve|decline)|set the limit|"
    r"approved limit is|recommended limit is|limit should be|"
    r"contact the customer|email the customer|contact the bureau|"
    r"post to the core|post to the crm|file a sar|submit a sar)\b",
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
    if "\f" in text:
        found.append({"hidden_in": "form_feed", "text": text.replace("\f", " ")})
    return found


def scan_documents(documents: list[dict[str, Any]]) -> dict[str, Any]:
    signals: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()

    def add(document_id: str, code: str, hidden_in: str) -> None:
        key = (document_id, code, hidden_in)
        if key in seen:
            return
        seen.add(key)
        signals.append(
            {
                "document_id": document_id,
                "code": code,
                "hidden_in": hidden_in,
                "followed": False,
            }
        )

    for document in documents:
        document_id = str(document.get("document_id") or "")
        for page in document.get("pages") or []:
            for paragraph in page.get("paragraphs") or []:
                lines = paragraph.get("lines") or []
                blob = " ".join(
                    str(row.get("text") or "") for row in lines if isinstance(row, dict)
                )
                chunks = [{"hidden_in": "line", "text": blob}]
                chunks.extend(hidden_payloads(blob))
                for chunk in chunks:
                    for code in injection_codes(chunk["text"]):
                        add(document_id, code, chunk["hidden_in"])
                    for code in prohibited_codes(chunk["text"]):
                        add(document_id, code, chunk["hidden_in"])
    return {"detected": bool(signals), "followed": False, "signals": signals}
