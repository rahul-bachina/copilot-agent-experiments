"""Detect instructions aimed at the agent inside an untrusted transfer record.

A match is recorded and not followed. It is not a finding about the customer.
"""

from __future__ import annotations

import re

# Each pattern is an instruction to the agent, not a description of a transfer.
_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("ignore_instructions", re.compile(r"ignore (?:all |any )?(?:previous|prior|above) instructions", re.I)),
    ("disregard_rules", re.compile(r"disregard (?:the |all )?(?:rules|instructions|regulations)", re.I)),
    ("role_override", re.compile(r"\byou are now\b", re.I)),
    ("system_prefix", re.compile(r"\bsystem\s*:", re.I)),
    ("release_transfer", re.compile(r"\brelease (?:the |this )?(?:transfer|cryptoasset)", re.I)),
    ("make_available", re.compile(r"\bmake (?:the |this )?(?:cryptoasset|asset)s? available\b", re.I)),
    ("dispose_transfer", re.compile(r"\b(?:hold|return|reject) (?:the |this )?transfer\b", re.I)),
    ("file_sar", re.compile(r"\b(?:file|submit) (?:a |the )?sar\b", re.I)),
    ("suppress_sar", re.compile(r"\bdo not file\b", re.I)),
    ("contact_counterparty", re.compile(r"\bcontact the counterparty\b", re.I)),
    ("mark_compliant", re.compile(r"\bmark (?:this |the )?(?:transfer )?compliant\b", re.I)),
    ("set_threshold", re.compile(r"\bset (?:the )?threshold\b", re.I)),
    ("waive_regulation", re.compile(r"\bwaive regulation\b", re.I)),
]

PROHIBITED_PAYLOAD_KEYS = (
    "analyst_decision",
    "decision",
    "release",
    "hold",
    "return_transfer",
    "reject",
    "file_sar",
    "sar",
    "contact_counterparty",
    "make_available",
)


def signals_in_text(text: str) -> list[str]:
    """Return pattern ids found in text. Empty if text is not a string."""
    if not isinstance(text, str) or not text.strip():
        return []
    return [name for name, pattern in _PATTERNS if pattern.search(text)]


def text_is_injection(text: str) -> bool:
    """True when the string is an instruction aimed at the agent."""
    return bool(signals_in_text(text))
