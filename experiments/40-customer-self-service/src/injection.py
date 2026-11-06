"""Enquiry text is data. Instructions inside it are recorded and not followed."""

from __future__ import annotations

import re

PATTERNS: tuple[tuple[str, str], ...] = (
    ("ignore_instructions", r"ignore (all |any )?(previous |prior |above |your )?instructions"),
    ("disregard_rules", r"disregard (the )?(rules|catalogue|catalog|knowledge base)"),
    ("you_are_now", r"you are now"),
    ("system_prompt", r"system prompt"),
    ("reveal_prompt", r"reveal (the |your )?prompt"),
    ("role_jailbreak", r"\bDAN\b"),
    ("override_stale", r"override (the )?stale"),
    ("skip_human", r"(skip the human|do not (ask for|offer) a (person|human)|no human)"),
    ("pretend_verified", r"(treat me as verified|identity check (has )?passed|mark (me|the identity) verified)"),
    (
        "impersonation",
        r"(this is|i am|i'm) (from )?(the )?(bank|energy supplier|fraud team|customer service|help ?desk)",
    ),
    (
        "request_secret",
        r"(tell me|read me|what is|send me) (your |the )?(password|passcode|one[- ]time code)",
    ),
    ("reset_password_now", r"reset the password now"),
    ("take_payment_now", r"(take the payment now|charge the card now)"),
    ("close_complaint_now", r"close the complaint now"),
    ("change_tariff_now", r"change the tariff now"),
    ("change_contract_now", r"change the contract now"),
    ("send_now", r"send the (email|message|letter|sms) now"),
)

STOP_SIGNALS = frozenset(
    {
        "impersonation",
        "request_secret",
        "skip_human",
        "pretend_verified",
        "reset_password_now",
        "take_payment_now",
        "close_complaint_now",
        "change_tariff_now",
        "change_contract_now",
        "send_now",
    }
)

_COMPILED = tuple((name, re.compile(pattern, re.IGNORECASE)) for name, pattern in PATTERNS)


def signals_in(text: str) -> list[str]:
    if not text:
        return []
    return [name for name, pattern in _COMPILED if pattern.search(text)]


def stop_signals(signals: list[str]) -> list[str]:
    return [name for name in signals if name in STOP_SIGNALS]


def sentence_is_instruction(sentence: str) -> bool:
    return bool(signals_in(sentence))


def strip_instruction_sentences(text: str) -> str:
    """Drop sentences that are themselves instructions. Leave the rest."""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    kept = [part for part in parts if part and not sentence_is_instruction(part)]
    return " ".join(kept).strip()
