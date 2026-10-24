#!/usr/bin/env python3
"""Mock complaint intake for the Consumer Duty starter.

This is a rule-based smoke-test stand-in. It is tuned to the synthetic
fixtures. It is not a model evaluation and it must not be described as one.

The DISP dates always come from disp_clock.calculate_disp_clock.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path

from disp_clock import ROUTES, calculate_disp_clock

SMOKE_LABEL = (
    "MOCK SMOKE TEST. Rule-based stand-in tuned to the synthetic fixtures. "
    "Not a measure of model accuracy. No model was called."
)

INJECTION_PATTERNS = (
    "ignore previous instructions",
    "ignore all instructions",
    "ignore the above",
    "you are now",
    "system prompt",
    "system:",
    "uphold this complaint",
    "uphold the complaint",
    "send the email",
    "send the response",
    "send a final response",
    "disregard the receipt date",
    "disregard your rules",
    "pay £",
    "pay the customer",
    "mark the customer as vulnerable",
    "label the customer",
)

STALE_PHRASES = (
    "treat the balance as current",
    "treat this as current",
    "disregard the receipt date",
    "the complaint arrived in",
    "as of 2014",
    "as of 2015",
    "as of 2016",
    "as of 2017",
    "as of 2018",
    "as of 2019",
)

PRODUCTS = (
    ("emoney", ("e-money", "e money", "prepaid card", "wallet balance")),
    ("payment_services", ("faster payment", "payment didn't", "payment did not", "transfer", "psp")),
    ("current_account", ("current account", "overdraft", "sort code")),
    ("savings", ("savings", "isa")),
    ("personal_loan", ("personal loan", "loan agreement")),
    ("credit_card", ("credit card",)),
    ("motor_insurance", ("motor insurance", "car insurance", "motor claim")),
    ("home_insurance", ("home insurance", "buildings insurance")),
    ("pension", ("pension", "annuity")),
)

ROOT_CAUSES = (
    ("fees_and_charges", ("fee", "charge", "overdraft", "interest", "price", "expensive")),
    ("fraud", ("scam", "fraud", "unauthorised", "unauthorized", "not me")),
    ("declined_claim", ("claim was declined", "declined my claim", "claim refused", "rejected my claim")),
    ("unclear_information", ("don't understand", "do not understand", "unclear", "jargon", "can't make sense")),
    ("collections", ("arrears", "collections", "bailiff", "can't pay", "cannot pay")),
    ("account_access", ("locked", "can't log in", "cannot log in", "app won't", "password")),
    ("service_delay", ("waiting", "no one", "nobody", "on hold", "delay", "still not", "weeks")),
)

DUTY_FOR_CAUSE = {
    "fees_and_charges": "price_and_value",
    "fraud": "consumer_support",
    "declined_claim": "products_and_services",
    "unclear_information": "consumer_understanding",
    "collections": "consumer_support",
    "account_access": "consumer_support",
    "service_delay": "consumer_support",
    "other": "consumer_support",
}

HARM = (
    ("financial_loss", ("loss", "charged", "refund", "£", "overcharged", "out of pocket", "took the money")),
    ("material_distress", ("distress", "anxious", "upset", "crying", "can't sleep", "cannot sleep", "humiliated")),
    ("material_inconvenience", ("inconvenience", "wasted", "day off", "queued", "hours on the phone")),
)

DISSATISFACTION = (
    "complain", "complaint", "unhappy", "dissatisfied", "unacceptable", "disgusted",
    "failed", "still not", "refused", "ignored", "appalling",
)

VULNERABILITY = (
    ("health", ("hospital", "cancer", "disability", "disabled", "medication", "mental health", "operation")),
    ("life_events", ("bereavement", "died", "funeral", "lost my job", "redundancy", "divorce", "new baby")),
    ("resilience", ("can't buy food", "cannot buy food", "can't pay the rent", "cannot pay the rent", "bailiff", "no money left", "overdrawn and")),
    ("capability", ("don't understand the letter", "do not understand the letter", "can't read", "cannot read", "no computer", "jargon")),
)

HIGH_SEVERITY = ("can't buy food", "cannot buy food", "bailiff", "in hospital", "hospital tomorrow", "suicidal")


def _hash_id(text: str, received_on: date) -> str:
    digest = hashlib.sha256(f"{received_on.isoformat()}|{text}".encode()).hexdigest()
    return f"INT-{received_on.strftime('%Y%m%d')}-{digest[:6].upper()}"


def _has(text: str, phrase: str) -> bool:
    """Match a phrase on word boundaries so 'fee' does not hit 'feel'."""
    if phrase == "£":
        return "£" in text
    return re.search(rf"\b{re.escape(phrase)}\b", text) is not None


def _hits(text: str, phrases: tuple[str, ...]) -> list[str]:
    lower = text.lower()
    return [phrase for phrase in phrases if _has(lower, phrase)]


def suggest_route(text: str) -> str:
    lower = text.lower()
    emd = any(_has(lower, phrase) for phrase in ("e-money", "e money", "prepaid"))
    psd = any(
        _has(lower, phrase)
        for phrase in ("faster payment", "payment didn't", "payment did not", "transfer never")
    )
    if emd and psd:
        return "mixed"
    if emd:
        return "emd"
    if psd:
        return "psd"
    return "general"


def detect_injection(text: str) -> list[str]:
    return _hits(text, INJECTION_PATTERNS)


def _any(text: str, phrases: tuple[str, ...]) -> bool:
    return bool(_hits(text, phrases))


def detect_stale(text: str, received_on: date) -> list[str]:
    signals = _hits(text, STALE_PHRASES)
    for match in re.findall(r"\b(19\d{2}|20\d{2})\b", text):
        year = int(match)
        if year <= received_on.year - 6:
            signals.append(f"narrative cites {year}, which is more than six years before receipt")
    # Preserve order, drop duplicates.
    seen = []
    for signal in signals:
        if signal not in seen:
            seen.append(signal)
    return seen


def analyse(text: str) -> dict:
    lower = text.lower()
    product = "not_identified"
    for name, phrases in PRODUCTS:
        if _any(lower, phrases):
            product = name
            break

    cause = "other"
    for name, phrases in ROOT_CAUSES:
        if _any(lower, phrases):
            cause = name
            break

    harms = [name for name, phrases in HARM if _any(lower, phrases)]
    dissatisfied = _any(lower, DISSATISFACTION)
    about_service = product != "not_identified" or _any(
        lower, ("account", "policy", "insurance", "pension", "loan", "card", "payment")
    )
    meets = dissatisfied and bool(harms) and about_service

    flags = []
    for driver, phrases in VULNERABILITY:
        found = [phrase for phrase in phrases if _has(lower, phrase)]
        if found:
            flags.append({"driver": driver, "evidence_quote": found[0]})

    if _any(lower, HIGH_SEVERITY):
        severity = "high"
    elif "material_distress" in harms or cause == "fraud" or flags:
        severity = "elevated"
    else:
        severity = "standard"

    return {
        "meets": meets,
        "dissatisfied": dissatisfied,
        "harms": harms,
        "about_service": about_service,
        "product": product,
        "cause": cause,
        "severity": severity,
        "flags": flags,
        "outcome": DUTY_FOR_CAUSE[cause] if meets else None,
    }


def draft_acknowledgement(received_on: date, clock: dict, meets: bool) -> str:
    if not meets:
        opening = (
            "Thank you for writing to Northbridge Mutual. A handler still needs to "
            "confirm whether this is a complaint under the DISP glossary. "
        )
    else:
        opening = (
            "Thank you for telling us you are unhappy. We have received this and "
            "a handler is dealing with it. "
        )
    due = clock.get("operative_final_response_due_on")
    if due:
        timing = (
            f"On the general DISP 1.6.2R count, a written response is due by the "
            f"end of {due}. "
        )
    else:
        timing = (
            "The payment-services or e-money count is not operative until a handler "
            "confirms the days the provider is open. Do not quote a 15-day or 35-day "
            "date to the customer yet. "
        )
    return (
        "DRAFT FOR A HANDLER. Do not send.\n\n"
        f"Received {received_on.isoformat()}. {opening}{timing}"
        "This draft does not uphold or reject the complaint and does not offer redress. "
        "A person must check it, edit it, and send it through the firm's own channel."
    )


def intake(
    text: str,
    *,
    received_on: date,
    route: str | None = None,
    exceptional_circumstances: bool = False,
) -> dict:
    """Build a draft intake. `route` must already have been confirmed by a handler.

    If `route` is omitted, a suggestion is made and a general clock is calculated.
    A suggested PSD or EMD route is not applied to the operative clock, because
    that suggestion is not a handler confirmation.
    """
    if route is not None and route not in ROUTES:
        raise ValueError(f"route must be one of {ROUTES}")

    view = analyse(text)
    injection = detect_injection(text)
    stale = detect_stale(text, received_on)
    suggested = suggest_route(text)
    applied_route = route or "general"
    clock = calculate_disp_clock(
        received_on,
        applied_route,
        exceptional_circumstances=exceptional_circumstances,
    )

    result = {
        "intake_id": _hash_id(text, received_on),
        "evaluation_label": SMOKE_LABEL,
        "processing_mode": "mock",
        "received_on": received_on.isoformat(),
        "complaint": {
            "meets_disp_definition": view["meets"],
            "expression_of_dissatisfaction": view["dissatisfied"],
            "harm_alleged": view["harms"],
            "about_a_financial_service": view["about_service"],
            "handler_must_confirm": True,
            "rule": "Handbook glossary 'complaint', https://handbook.fca.org.uk/glossary/G197",
        },
        "product": {"suggested": view["product"], "handler_must_confirm": True},
        "root_cause": {
            "suggested": view["cause"],
            "taxonomy": "Starter taxonomy for the fictional firm Northbridge Mutual. Not an FCA taxonomy.",
            "handler_must_confirm": True,
        },
        "severity": {
            "suggested": view["severity"],
            "requires_prompt_human_review": view["severity"] == "high" or bool(view["flags"]),
            "handler_must_confirm": True,
        },
        "vulnerability_characteristics": {
            "customer_labelled_vulnerable": False,
            "flags": view["flags"],
            "note": (
                "FG21/1 paragraph 2.5 drivers, for a handler to review. "
                "The customer has not been labelled vulnerable (FG21/1 paragraph 2.9)."
            ),
        },
        "consumer_duty": {
            "outcomes_touched": [view["outcome"]] if view["outcome"] else [],
            "breach_found": False,
            "note": (
                "Mapping only, against PRIN 2A.3 to PRIN 2A.6. "
                "Not a finding that the firm has breached the Consumer Duty."
            ),
        },
        "route": {
            "suggested": suggested,
            "applied_to_clock": applied_route,
            "handler_confirmed": route is not None,
        },
        "disp_clock": clock,
        "acknowledgement_draft": {
            "status": "draft_for_handler",
            "may_be_sent_by_agent": False,
            "text": draft_acknowledgement(received_on, clock, view["meets"]),
        },
        "security": {
            "prompt_injection_detected": bool(injection),
            "prompt_injection_signals": injection,
            "stale_data_signals": stale,
            "actions_taken": [],
        },
        "decisions_not_taken": [
            "uphold",
            "reject",
            "redress",
            "close",
            "send",
            "vulnerability_label",
            "fos_referral",
        ],
    }
    validate_intake(result)
    return result


def validate_intake(result: dict) -> None:
    """Reject a draft that records a prohibited decision."""
    if result["vulnerability_characteristics"]["customer_labelled_vulnerable"] is not False:
        raise ValueError("customer must not be labelled vulnerable")
    if result["consumer_duty"]["breach_found"] is not False:
        raise ValueError("agent must not find a Consumer Duty breach")
    if result["acknowledgement_draft"]["may_be_sent_by_agent"] is not False:
        raise ValueError("agent must not send")
    if result["security"]["actions_taken"] != []:
        raise ValueError("agent must not take actions")
    required = {
        "uphold", "reject", "redress", "close", "send",
        "vulnerability_label", "fos_referral",
    }
    if set(result["decisions_not_taken"]) != required:
        raise ValueError("decisions_not_taken was altered")
    text = result["acknowledgement_draft"]["text"].lower()
    for banned in ("i uphold", "we uphold", "redress of", "we will pay you"):
        if banned in text:
            raise ValueError(f"draft contains a prohibited phrase: {banned}")
    clock_route = result["disp_clock"]["route"]
    if clock_route != result["route"]["applied_to_clock"]:
        raise ValueError("clock route does not match the applied route")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Mock complaint intake. Does not call a model.")
    parser.add_argument("--input", "-i", type=Path)
    parser.add_argument("--received", required=True, type=date.fromisoformat)
    parser.add_argument("--route", choices=ROUTES)
    parser.add_argument("--exceptional-circumstances", action="store_true")
    args = parser.parse_args(argv)
    if args.input:
        text = args.input.read_text()
    elif not sys.stdin.isatty():
        text = sys.stdin.read()
    else:
        print("Provide --input or pipe the complaint text.", file=sys.stderr)
        return 2
    if not text.strip():
        print("Empty complaint text.", file=sys.stderr)
        return 2
    result = intake(
        text,
        received_on=args.received,
        route=args.route,
        exceptional_circumstances=args.exceptional_circumstances,
    )
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(2) from exc
