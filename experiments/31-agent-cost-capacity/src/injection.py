"""Record instructions in telemetry and rate-card text. Do not follow them.

A sentence that already refuses the action is not a hit. Payload keys that
try to set a cost, a validation flag, or a quota change are removed and are
not echoed.
"""

from __future__ import annotations

import re
from typing import Any

STRIP_KEYS = frozenset(
    {
        "rates_validated",
        "forecast_validated",
        "quota_changed",
        "budget_changed",
        "subscription_changed",
        "cost",
        "total",
        "total_cost",
        "unit_cost",
        "unit_cost_per_case",
        "do_not_rely",
        "microsoft_prices_used",
        "builtin_rates_used",
        "added_rollup",
        "actions_taken",
        "a3_recommended",
        "price_override",
        "used_override",
        "approved",
    }
)

# period_rollup.cost is a comparison figure, not a payload to strip.
_KEEP_EVEN_IF_NAMED = frozenset({"period_rollup"})

_NEGATION = re.compile(r"\b(do not|don't|must not|never|cannot|can't)\b", re.I)

_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "ignore_instructions",
        re.compile(r"ignore (all |any )?(previous|prior|above|your) instructions", re.I),
    ),
    (
        "ignore_instructions",
        re.compile(r"disregard (the )?(rules|instructions|rate card)", re.I),
    ),
    ("set_price", re.compile(r"\b(set|override) (the )?(price|rate|cost)\b", re.I)),
    ("set_price", re.compile(r"\bthe (price|rate) is now\b", re.I)),
    ("validate_rates", re.compile(r"\bvalidate the (rates|rate card)\b", re.I)),
    ("validate_forecast", re.compile(r"\bvalidate the forecast\b", re.I)),
    ("validate_forecast", re.compile(r"\bmark the forecast validated\b", re.I)),
    (
        "change_quota",
        re.compile(r"\b(change|raise|lower|increase|decrease|set) the (quota|limit)\b", re.I),
    ),
    (
        "change_budget",
        re.compile(r"\b(change|raise|lower|increase|decrease|set) the budget\b", re.I),
    ),
    (
        "change_subscription",
        re.compile(r"\b(change|cancel|upgrade) the subscription\b", re.I),
    ),
    ("role_override", re.compile(r"\byou are now\b", re.I)),
    ("system_prefix", re.compile(r"^\s*(system|developer)\s*:", re.I)),
)

INJECTION_IDS = frozenset(
    {
        "ignore_instructions",
        "set_price",
        "role_override",
        "system_prefix",
        "payload_key",
        "validate_rates",
        "validate_forecast",
    }
)
PROHIBITED_IDS = frozenset(
    {
        "change_quota",
        "change_budget",
        "change_subscription",
        "validate_rates",
        "validate_forecast",
    }
)


def _sentences(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"[.!?\n]+", text) if part.strip()]


def strip_payload(value: Any, findings: list[dict], parent_key: str | None = None) -> None:
    """Delete keys that would set a control flag. Do not keep the value.

    period_rollup.cost is a comparison figure supplied by the caller. It is
    not a flag, and it is not added into the total.
    """
    if isinstance(value, dict):
        for key in list(value):
            if parent_key == "period_rollup" and key == "cost":
                continue
            if key in STRIP_KEYS:
                findings.append({"pattern": "payload_key", "key": key})
                del value[key]
            else:
                strip_payload(value[key], findings, key)
    elif isinstance(value, list):
        for item in value:
            strip_payload(item, findings, parent_key)


def scan_text(value: Any, findings: list[dict]) -> None:
    if isinstance(value, dict):
        for item in value.values():
            scan_text(item, findings)
    elif isinstance(value, list):
        for item in value:
            scan_text(item, findings)
    elif isinstance(value, str):
        for sentence in _sentences(value):
            if _NEGATION.search(sentence):
                continue
            for pattern_id, pattern in _PATTERNS:
                if pattern.search(sentence):
                    findings.append({"pattern": pattern_id})


def hostile(text: str) -> bool:
    findings: list[dict] = []
    scan_text(text, findings)
    return bool(findings)


def inspect(bundle: dict, rate_card: dict | None) -> dict:
    findings: list[dict] = []
    strip_payload(bundle, findings)
    if rate_card is not None:
        strip_payload(rate_card, findings)
    scan_text(bundle, findings)
    if rate_card is not None:
        scan_text(rate_card, findings)
    patterns = sorted({row["pattern"] for row in findings})
    return {
        "detected": any(pattern in INJECTION_IDS for pattern in patterns),
        "followed": False,
        "patterns": patterns,
        "prohibited_requested": any(pattern in PROHIBITED_IDS for pattern in patterns),
        "note_withheld": any(pattern in INJECTION_IDS for pattern in patterns),
    }
