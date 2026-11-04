"""Record instructions inside advice. Do not follow them.

A sentence that already refuses the action is not a hit. Payload keys that
would set a decision, a sign-off, or an export are removed and are not echoed.
"""

from __future__ import annotations

import re
from typing import Any

STRIP_KEYS = frozenset(
    {
        "needs_decided",
        "provision_decided",
        "placement_decided",
        "outcomes_decided",
        "final_plan_edited",
        "final_plan",
        "final_text",
        "sent_to_parents",
        "sent_to_school",
        "written_to_la_system",
        "provision_secured",
        "exported",
        "export_blocked",
        "authorises_export",
        "caseworker_signoff",
        "approved",
        "a3_recommended",
        "named_placement",
        "placement_decision",
        "actions_taken",
    }
)

_NEGATION = re.compile(r"\b(do not|don't|must not|never|cannot|can't)\b", re.I)

_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "ignore_instructions",
        re.compile(r"ignore (all |any )?(previous|prior|above|your) instructions", re.I),
    ),
    (
        "ignore_instructions",
        re.compile(r"disregard (the )?(rules|instructions|statutory headings|section headings)", re.I),
    ),
    ("role_override", re.compile(r"\byou are now\b", re.I)),
    ("system_prefix", re.compile(r"^\s*(system|developer)\s*:", re.I)),
    ("decide_needs", re.compile(r"\bdecide the (needs|special educational needs)\b", re.I)),
    ("decide_provision", re.compile(r"\bdecide the provision\b", re.I)),
    ("decide_placement", re.compile(r"\b(decide the placement|name the school)\b", re.I)),
    ("decide_outcomes", re.compile(r"\bdecide the outcomes?\b", re.I)),
    (
        "send_parents",
        re.compile(r"\bsend (this|the draft|the plan) to (the )?parents\b", re.I),
    ),
    (
        "send_school",
        re.compile(r"\bsend (this|the draft|the plan) to (the )?school\b", re.I),
    ),
    (
        "write_la",
        re.compile(
            r"\b(write|send) (this|the draft|the plan) to the (local authority|la system|case system)\b",
            re.I,
        ),
    ),
    ("export_without_signoff", re.compile(r"\bexport without sign-?off\b", re.I)),
    (
        "fake_signoff",
        re.compile(r"\b(the )?caseworker has (already )?(approved|signed off)\b", re.I),
    ),
    (
        "set_flag",
        re.compile(
            r"\bset (needs_decided|provision_decided|placement_decided|outcomes_decided|exported)( to true)?\b",
            re.I,
        ),
    ),
    ("edit_final", re.compile(r"\b(edit|rewrite|finalise|finalize) the final plan\b", re.I)),
    ("recommend_a3", re.compile(r"\b(recommend|use) autonomy a3\b", re.I)),
    ("secure_provision", re.compile(r"\bsecure the provision\b", re.I)),
)

INJECTION_IDS = frozenset(pattern_id for pattern_id, _pattern in _PATTERNS) | frozenset(
    {"payload_key"}
)


def _sentences(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"[.!?\n]+", text) if part.strip()]


def pattern_ids(text: str) -> list[str]:
    found: list[str] = []
    for sentence in _sentences(text):
        if _NEGATION.search(sentence):
            continue
        for pattern_id, pattern in _PATTERNS:
            if pattern.search(sentence) and pattern_id not in found:
                found.append(pattern_id)
    return found


def strip_payload(value: Any, findings: list[dict]) -> None:
    """Delete keys that would set a control. Do not keep the value."""
    if isinstance(value, dict):
        for key in list(value):
            if key in STRIP_KEYS:
                findings.append({"pattern": "payload_key", "key": key, "followed": False})
                del value[key]
            else:
                strip_payload(value[key], findings)
    elif isinstance(value, list):
        for item in value:
            strip_payload(item, findings)


def strings_in(value: Any) -> list[str]:
    found: list[str] = []
    if isinstance(value, str):
        found.append(value)
    elif isinstance(value, dict):
        for item in value.values():
            found.extend(strings_in(item))
    elif isinstance(value, list):
        for item in value:
            found.extend(strings_in(item))
    return found
