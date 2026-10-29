"""Ticket text is data. Instructions inside it are recorded and not followed."""

from __future__ import annotations

import re

# Order is stable so the signal list does not depend on dict ordering.
PATTERNS: tuple[tuple[str, str], ...] = (
    ("ignore_instructions", r"ignore (all |any )?(previous |prior |above |your )?instructions"),
    ("disregard_rules", r"disregard (the )?(rules|catalogue|catalog|knowledge base)"),
    ("you_are_now", r"you are now"),
    ("system_prompt", r"system prompt"),
    ("reveal_prompt", r"reveal (the |your )?prompt"),
    ("role_jailbreak", r"\bDAN\b"),
    ("override_stale", r"override (the )?stale"),
    ("do_not_handover", r"do not (hand ?over|refer)"),
    ("execute_now", r"(reset the password now|grant access now|execute the fix|wipe the device now)"),
    (
        "helpdesk_impersonation",
        r"(this is|i am|i'm) (the )?(it |ict )?(help ?desk|service desk|it support)",
    ),
    (
        "helpdesk_impersonation_call",
        r"(calling|phoning) from (the )?(it |ict )?(help ?desk|service desk|it support|microsoft support)",
    ),
    (
        "request_password",
        r"(tell me|read( me)?|what is|send( me)?) (your |the )?(password|passcode)",
    ),
    (
        "request_mfa_code",
        r"(tell me|read( me)?|send( me)?) (your |the )?(mfa|one[- ]time|otp|authenticator)( code)?",
    ),
    ("skip_verification", r"skip (the )?(identity )?verification"),
    (
        "pretend_verified",
        r"(treat me as verified|identity check (has )?passed|mark (me|the identity) verified)",
    ),
    ("disable_mfa", r"(disable|turn off|remove|bypass) (my |the )?mfa"),
    ("ceo_override", r"(ceo|chief executive).{0,60}(reset|grant|skip|disable)"),
)

# These stop the draft before an article body is quoted.
STOP_SIGNALS = frozenset(
    {
        "helpdesk_impersonation",
        "helpdesk_impersonation_call",
        "request_password",
        "request_mfa_code",
        "skip_verification",
        "pretend_verified",
        "disable_mfa",
        "ceo_override",
        "execute_now",
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
