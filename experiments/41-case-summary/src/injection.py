"""Instructions inside a case history are data. They are recorded and not followed.

A sentence that already refuses the action is not treated as an instruction.
Payload keys that would set an outcome, a contact, a record change, or an
accuracy flag are removed. Their values are not kept.
"""

from __future__ import annotations

import re
from typing import Any

PROHIBITED_PAYLOAD_KEYS = frozenset(
    {
        "case_outcome",
        "customer_contacted",
        "record_changed",
        "complaint_closed",
        "redress_offered",
        "customer_labelled_vulnerable",
        "accuracy_checked",
        "summary_accepted",
        "checker_passed",
        "do_not_rely",
        "actions_taken",
        "model_called",
        "network_called",
        "foundry_called",
        "a3_recommended",
        "approved",
        "decision",
        "human_approval",
        "proposed_sentences",
        "summary_is_not_a_customer_contact",
    }
)

# Narrow list. A phrase that is not here is not detected.
_INJECTION: tuple[tuple[str, str], ...] = (
    ("ignore_instructions", "ignore previous instructions"),
    ("ignore_instructions", "ignore all instructions"),
    ("ignore_instructions", "ignore the above"),
    ("persona_override", "you are now"),
    ("persona_override", "you are the service representative"),
    ("contact_customer", "contact the customer now"),
    ("update_record", "update the case now"),
    ("update_record", "change the record now"),
    ("close_complaint", "close the complaint now"),
    ("offer_redress", "offer redress now"),
    ("accept_summary", "summary is accepted"),
    ("accept_summary", "mark the summary accurate"),
    ("force_supported", "mark every sentence supported"),
    ("autonomy_a3", "autonomy a3"),
    ("set_outcome", "set case outcome"),
)

_PROHIBITED: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "customer_contact",
        re.compile(
            r"\b(contact the customer|email the customer|text the customer|"
            r"call the customer|send (?:a |the )?(?:letter|email|sms|message) to the customer)\b",
            re.I,
        ),
    ),
    (
        "record_change",
        re.compile(
            r"\b(update the case record|change the (?:case )?record|write the case|"
            r"close the case record)\b",
            re.I,
        ),
    ),
    (
        "complaint_closed",
        re.compile(
            r"\b(close the complaint|complaint is closed|uphold the complaint|reject the complaint)\b",
            re.I,
        ),
    ),
    (
        "redress",
        re.compile(r"\boffer redress\b", re.I),
    ),
    (
        "outcome",
        re.compile(r"\b(decide the outcome|the outcome is|case outcome is)\b", re.I),
    ),
    (
        "vulnerability_label",
        re.compile(
            r"\b(customer is vulnerable|labelled vulnerable|labeled vulnerable)\b",
            re.I,
        ),
    ),
)

_REFUSAL = re.compile(r"\b(do not|don't|must not|never|cannot|can't)\b", re.I)
_AFFIRMATIVE = re.compile(
    r"\b(contact the customer|email the customer|text the customer|call the customer|"
    r"send (?:a |the )?(?:letter|email|sms|message) to the customer|"
    r"update the case record|change the (?:case )?record|write the case|"
    r"close the complaint|complaint is closed|uphold the complaint|reject the complaint|"
    r"offer redress|decide the outcome|the outcome is|case outcome is|"
    r"customer is vulnerable|labelled vulnerable|labeled vulnerable)\b",
    re.I,
)

ZERO_WIDTH_CHARS = ("\u200b", "\u200c", "\u200d", "\ufeff", "\u2060")
_ZERO_WIDTH_MAP = {ord(char): None for char in ZERO_WIDTH_CHARS}
_COMMENT = re.compile(r"<!--(.*?)-->", re.DOTALL)
_TRAILING = re.compile(r"\n{3,}(.*)\Z", re.DOTALL)


def is_refusal_sentence(sentence: str) -> bool:
    """A refusal of an action is not itself the action.

    The refusal word has to come first, and the sentence must not state the
    action a second time. "Do not contact the customer." is a refusal.
    "Contact the customer and do not stop." is not.
    """
    refusal = _REFUSAL.search(sentence)
    if not refusal:
        return False
    affirmative = _AFFIRMATIVE.search(sentence)
    if not affirmative:
        return True
    if affirmative.start() < refusal.start():
        return False
    return _AFFIRMATIVE.search(sentence, affirmative.end()) is None


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


def _add(signals: list[dict], seen: set[tuple], *, event_id: str, code: str, hidden_in: str) -> None:
    key = (event_id, code, hidden_in)
    if key in seen:
        return
    seen.add(key)
    signals.append(
        {
            "event_id": event_id,
            "code": code,
            "hidden_in": hidden_in,
            "followed": False,
        }
    )


def scan_text(text: str, *, event_id: str) -> tuple[list[dict], int]:
    """Scan one string. The instruction text itself is not copied out."""
    if not isinstance(text, str):
        return [], 0
    zero_width_removed = sum(text.count(char) for char in ZERO_WIDTH_CHARS)
    stripped = text.translate(_ZERO_WIDTH_MAP)
    signals: list[dict] = []
    seen: set[tuple] = set()

    def collect(blob: str, hidden_in: str) -> None:
        for code in injection_codes(blob):
            _add(signals, seen, event_id=event_id, code=code, hidden_in=hidden_in)

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
                _add(signals, seen, event_id=event_id, code=code, hidden_in="zero_width")
    collect(body, "body")
    return signals, zero_width_removed
