"""Instructions inside a bundle are data. They are recorded and not followed.

A sentence that already refuses the action is not treated as an instruction.
Payload keys that would set an outcome, a disclosure decision, a credibility
finding, or an acceptance flag are removed. Their values are not kept.
"""

from __future__ import annotations

import re
from typing import Any

PROHIBITED_PAYLOAD_KEYS = frozenset(
    {
        "case_outcome",
        "disclosure_decision",
        "credibility_finding",
        "summary_accepted_as_reading_aid",
        "sentences_reviewed_by_decision_maker",
        "checker_passed",
        "outcome_recommended",
        "summary_is_not_a_decision",
        "actions_taken",
        "model_called",
        "network_called",
        "foundry_called",
        "a3_recommended",
        "approved",
        "decision",
        "recommend_outcome",
        "proposed_sentences",
        "do_not_rely",
    }
)

# Narrow list. A phrase that is not here is not detected.
_INJECTION: tuple[tuple[str, str], ...] = (
    ("ignore_instructions", "ignore previous instructions"),
    ("ignore_instructions", "ignore all instructions"),
    ("ignore_instructions", "ignore the above"),
    ("persona_override", "you are now"),
    ("persona_override", "you are the decision-maker"),
    ("recommend_a_charge", "recommend a charge"),
    ("disclosure_instruction", "set the disclosure decision"),
    ("credibility_instruction", "find the witness credible"),
    ("accept_summary", "summary is accepted"),
    ("force_supported", "mark every sentence supported"),
    ("autonomy_a3", "autonomy a3"),
    ("set_outcome", "set case outcome"),
)

_PROHIBITED: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "outcome_recommendation",
        re.compile(
            r"\b(recommend(?:s|ed|ing)? (?:a |an )?(?:charge|outcome)|should be charged|"
            r"should charge|no further action|grant asylum|refuse asylum|refuse the claim|"
            r"bar from regulated activity|should be barred|should not be barred)\b",
            re.I,
        ),
    ),
    (
        "disclosure_decision",
        re.compile(
            r"\b(disclose (?:this|the|all) (?:unused )?material|withhold (?:this|the) material|"
            r"disclosure decision is|must be disclosed|must be withheld|set the disclosure decision)\b",
            re.I,
        ),
    ),
    (
        "credibility_finding",
        re.compile(
            r"\b((?:witness|applicant|referee) is (?:not )?credible|credibility finding is|"
            r"find the (?:witness|applicant|referee) (?:not )?credible)\b",
            re.I,
        ),
    ),
)

_REFUSAL = re.compile(r"\b(do not|don't|must not|never|cannot|can't)\b", re.I)
_AFFIRMATIVE = re.compile(
    r"\b(should be charged|should charge|no further action|grant asylum|refuse asylum|"
    r"refuse the claim|should be barred|should not be barred|bar from regulated activity|"
    r"must be disclosed|must be withheld|disclose (?:this|the|all) (?:unused )?material|"
    r"withhold (?:this|the) material|(?:witness|applicant|referee) is (?:not )?credible|"
    r"find the (?:witness|applicant|referee) (?:not )?credible)\b",
    re.I,
)

ZERO_WIDTH_CHARS = ("\u200b", "\u200c", "\u200d", "\ufeff", "\u2060")
_ZERO_WIDTH_MAP = {ord(char): None for char in ZERO_WIDTH_CHARS}
_COMMENT = re.compile(r"<!--(.*?)-->", re.DOTALL)
_TRAILING = re.compile(r"\n{3,}(.*)\Z", re.DOTALL)


def is_refusal_sentence(sentence: str) -> bool:
    """A refusal of an action is not itself the action, unless it states one."""
    return bool(_REFUSAL.search(sentence)) and not _AFFIRMATIVE.search(sentence)


def _sentences(text: str) -> list[str]:
    parts = re.split(r"[\n.]+", text)
    return [part.strip() for part in parts if part.strip()]


def _plain(text: str) -> str:
    return text.translate(_ZERO_WIDTH_MAP)


def _injection_codes_raw(text: str) -> list[str]:
    if not text:
        return []
    found: list[str] = []
    for sentence in _sentences(text):
        if is_refusal_sentence(sentence):
            continue
        lowered = sentence.casefold()
        for code, phrase in _INJECTION:
            if phrase in lowered and code not in found:
                found.append(code)
    return found


def injection_codes(text: str) -> list[str]:
    return _injection_codes_raw(_plain(text))


def prohibited_codes(text: str) -> list[str]:
    if not text:
        return []
    found: list[str] = []
    for sentence in _sentences(_plain(text)):
        if is_refusal_sentence(sentence):
            continue
        for code, pattern in _PROHIBITED:
            if pattern.search(sentence) and code not in found:
                found.append(code)
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


def _add(signals: list[dict], seen: set[tuple], *, document_id: str, code: str, hidden_in: str) -> None:
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


def scan_text(text: str, *, document_id: str) -> tuple[list[dict], int]:
    """Scan one string. The instruction text itself is not copied out."""
    if not isinstance(text, str):
        return [], 0
    zero_width_removed = sum(text.count(char) for char in ZERO_WIDTH_CHARS)
    stripped = text.translate(_ZERO_WIDTH_MAP)
    signals: list[dict] = []
    seen: set[tuple] = set()

    def collect(blob: str, hidden_in: str) -> None:
        for code in injection_codes(blob):
            _add(signals, seen, document_id=document_id, code=code, hidden_in=hidden_in)

    comments = _COMMENT.findall(stripped)
    without_comments = _COMMENT.sub(" ", stripped)
    for comment in comments:
        collect(comment, "html_comment")
    body = without_comments
    if "\f" in body:
        head, *rest = body.split("\f")
        for part in rest:
            collect(part, "form_feed")
        body = head
    trailing = _TRAILING.search(body)
    if trailing:
        collect(trailing.group(1), "trailing_blank_lines")
        body = body[: trailing.start()]
    if zero_width_removed:
        visible = _injection_codes_raw(text)
        for code in _injection_codes_raw(stripped):
            if code not in visible:
                _add(signals, seen, document_id=document_id, code=code, hidden_in="zero_width")
    collect(body, "body")
    return signals, zero_width_removed


def _walk_strings(node: Any, document_id: str, signals: list[dict], seen: set[tuple]) -> int:
    removed = 0
    if isinstance(node, str):
        found, count = scan_text(node, document_id=document_id)
        removed += count
        for row in found:
            _add(
                signals,
                seen,
                document_id=document_id,
                code=row["code"],
                hidden_in=row["hidden_in"],
            )
        return removed
    if isinstance(node, dict):
        for value in node.values():
            removed += _walk_strings(value, document_id, signals, seen)
        return removed
    if isinstance(node, list):
        for value in node:
            removed += _walk_strings(value, document_id, signals, seen)
    return removed


def scan_documents(documents: list[dict]) -> dict[str, Any]:
    signals: list[dict] = []
    seen: set[tuple] = set()
    removed = 0
    for document in documents:
        document_id = str(document.get("document_id") or "")
        removed += _walk_strings(document, document_id, signals, seen)
    return {
        "detected": bool(signals),
        "followed": False,
        "zero_width_removed": removed,
        "signals": signals,
        "ignored_keys": [],
    }
