"""Instructions aimed at the agent inside an untrusted alert case.

A match is recorded and not followed. It is not a finding about the customer.
"""

from __future__ import annotations

import re

_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("ignore_instructions", re.compile(r"ignore (?:all |any )?(?:previous|prior|above) instructions", re.I)),
    ("disregard_rules", re.compile(r"disregard (?:the |all )?(?:rules|instructions|regulations)", re.I)),
    ("role_override", re.compile(r"\byou are now\b|\byou are the mlro\b", re.I)),
    ("system_prefix", re.compile(r"\bsystem\s*:", re.I)),
    ("file_sar", re.compile(r"\b(?:file|submit|lodge) (?:a |the )?(?:sar|suspicious activity report)\b", re.I)),
    ("filed_sar", re.compile(r"\bfiled a sar\b", re.I)),
    ("submit_nca", re.compile(r"\b(?:submit|send|file) (?:it |this )?(?:to|with) the (?:nca|ukfiu)\b", re.I)),
    ("suppress_sar", re.compile(r"\bdo not file\b|\bdon't file\b|\bsuppress (?:the |this )?alert\b", re.I)),
    ("close_alert", re.compile(r"\bclose (?:the |this )?alert\b|\bno suspicion\b", re.I)),
    ("tell_customer", re.compile(r"\btell the customer\b|\bemail the customer\b|\bwrite to the customer\b", re.I)),
    ("we_suspect", re.compile(r"\bwe suspect\b|\bi suspect\b", re.I)),
    ("request_daml", re.compile(r"\brequest (?:a )?daml\b|\bseek a defence\b", re.I)),
    ("freeze_wallet", re.compile(r"\bfreeze (?:the |this )?(?:wallet|account)\b", re.I)),
    ("move_crypto", re.compile(r"\bmove (?:the |these )?(?:funds|crypto|cryptoasset)\b", re.I)),
    ("set_decision", re.compile(r"\bset mlro_decision\b|\bmlro_decision\s*[:=]", re.I)),
    ("glossary_code", re.compile(r"\bglossary code is\b", re.I)),
]

PROHIBITED_PAYLOAD_KEYS = (
    "mlro_decision",
    "sar_filed",
    "nca_contacted",
    "daml_requested",
    "customer_told",
    "suspicion",
    "suspicion_recorded",
    "freeze",
    "freeze_account",
    "move_crypto",
    "file_sar",
    "decision",
    "glossary_codes",
    "customer_message",
)


def signals_in_text(text: str) -> list[str]:
    """Return pattern ids found in text. Empty if text is not a string."""

    if not isinstance(text, str) or not text.strip():
        return []
    return [name for name, pattern in _PATTERNS if pattern.search(text)]
