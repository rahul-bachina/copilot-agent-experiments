"""Instructions inside a submission are data. They are recorded and not followed.

A sentence that already refuses the action is not treated as an instruction,
unless it also states an affirmative accept, decline, price, contact, or write.
Payload keys that would set a decision are removed. Their values are not kept.
"""

from __future__ import annotations

import re
from typing import Any

PROHIBITED_PAYLOAD_KEYS = frozenset(
    {
        "coverage_decision",
        "accept_or_decline",
        "price_suggested",
        "terms_suggested",
        "premium_suggested",
        "broker_contacted",
        "underwriting_system_written",
        "bound",
        "checker_passed",
        "do_not_rely",
        "summary_accepted_as_decision",
        "reading_acknowledged",
        "proposed_facts",
        "actions_taken",
        "model_called",
        "network_called",
        "foundry_called",
        "a3_recommended",
        "approved",
        "decision",
        "solely_automated_decision",
    }
)

_INJECTION: tuple[tuple[str, str], ...] = (
    ("ignore_instructions", "ignore previous instructions"),
    ("ignore_instructions", "ignore all instructions"),
    ("ignore_instructions", "ignore the above"),
    ("persona_override", "you are now"),
    ("persona_override", "you are the underwriter"),
    ("accept_instruction", "accept this risk"),
    ("decline_instruction", "decline this risk"),
    ("price_instruction", "suggest a premium"),
    ("price_instruction", "set the price"),
    ("contact_instruction", "email the broker"),
    ("contact_instruction", "contact the broker"),
    ("write_instruction", "write to the underwriting system"),
    ("bind_instruction", "bind the risk"),
    ("bind_instruction", "bind cover"),
    ("force_supported", "mark every fact supported"),
    ("autonomy_a3", "autonomy a3"),
)

_PROHIBITED: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "accept_or_decline",
        re.compile(
            r"\b(accept(?:s|ed)? (?:this |the )?risk|decline(?:s|d)? (?:this |the )?risk|"
            r"recommendation is (?:to )?(?:accept|decline)|should be (?:accepted|declined)|"
            r"refer the risk)\b",
            re.I,
        ),
    ),
    (
        "price_or_terms",
        re.compile(
            r"\b(suggest(?:s|ed)? a (?:premium|price|rate)|recommended premium|"
            r"price this at|terms should be|set the (?:price|premium|rate|terms))\b",
            re.I,
        ),
    ),
    (
        "contact_broker",
        re.compile(r"\b(email the broker|contact the broker|write to the broker)\b", re.I),
    ),
    (
        "write_or_bind",
        re.compile(
            r"\b(write to the underwriting system|bind the risk|bind cover)\b",
            re.I,
        ),
    ),
)

_REFUSAL = re.compile(r"\b(do not|don't|must not|never|cannot|can't)\b", re.I)
_AFFIRMATIVE = re.compile(
    r"\b(should be (?:accepted|declined)|recommendation is (?:to )?(?:accept|decline)|"
    r"suggest(?:s|ed)? a (?:premium|price|rate)|price this at|terms should be|"
    r"email the broker|contact the broker|write to the underwriting system|"
    r"bind the risk|bind cover)\b",
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

    The returned text is for the scanner only. It is not copied into a fact.
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
