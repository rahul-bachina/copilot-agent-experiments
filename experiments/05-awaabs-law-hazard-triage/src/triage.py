#!/usr/bin/env python3
"""Mock hazard triage for the Awaab's Law starter.

This is a rule-based smoke-test stand-in. It is tuned to the synthetic
fixtures. It is not a model evaluation and it must not be described as one.

Timeframes always come from statutory_clock.calculate_statutory_clock.
The report text cannot move a date, approve a category, or send a summary.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

from records import draft_endeavours_record, ombudsman_information
from statutory_clock import DAMP, NONE, OVERCROWDING, calculate_statutory_clock

SMOKE_LABEL = (
    "MOCK SMOKE TEST. Rule-based stand-in tuned to the synthetic fixtures. "
    "Not a measure of model accuracy. No model was called."
)

DECISIONS_NOT_TAKEN = (
    "hazard_category",
    "send",
    "housing_system_write",
    "reasonable_endeavours_defence",
    "ombudsman_referral",
    "vulnerability_label",
    "decant_booking",
    "spend",
    "downgrade",
)

INJECTION_PATTERNS = (
    "ignore previous instructions",
    "ignore all instructions",
    "ignore your rules",
    "you are now",
    "system:",
    "downgrade this",
    "classify this as not a hazard",
    "classify this as non-urgent",
    "send the summary",
    "send the letter",
    "send it to the tenant",
    "write it to the housing",
    "write this to the housing",
    "update the housing management",
    "mark the tenant as vulnerable",
    "label the tenant",
    "defence is made out",
    "reasonable endeavours defence is made out",
    "reasonable endeavours are exhausted",
    "close the case",
    "refer this to the housing ombudsman",
    "refer this to the ombudsman",
)

EMERGENCY_RULES = (
    ("excess_cold", ("baby is freezing", "freezing and we have no heating", "no heating and the baby")),
    ("damp_mould_fungal_growth", ("can't breathe", "cannot breathe", "struggling to breathe")),
    ("fire_and_explosions", ("smell of gas", "gas leak", "carbon monoxide", "smoke filling", "flames")),
    ("electrical", ("electric shock", "exposed live wire", "sparking", "burning smell from the socket")),
    (
        "structural_collapse",
        ("ceiling coming down", "ceiling is coming down", "about to collapse", "lintel", "wall is bowing"),
    ),
    ("domestic_hygiene", ("sewage coming up", "sewage flooding")),
)

SIGNIFICANT_RULES = (
    ("damp_mould_fungal_growth", ("mould", "mold", "damp", "black spots", "fungal")),
    ("domestic_hygiene", ("rats", "mice", "cockroach", "pest infestation")),
    ("falls_on_stairs", ("banister", "loose stair")),
    ("falls_on_the_level", ("uneven floor",)),
    ("falls_between_levels", ("balcony rail",)),
    ("electrical", ("lights keep tripping",)),
    ("excess_heat", ("overheating", "excess heat", "too hot to sleep")),
    ("structural_collapse", ("crack in the wall",)),
    ("excess_cold", ("excess cold",)),
)

WEAK_RULES = (
    ("excess_cold", ("no heating", "boiler is broken", "boiler broken", "a bit chilly")),
)

OVERCROWDING_PHRASES = ("overcrowded", "not enough bedrooms", "lack of space to sleep")

HEALTH_PHRASES = (
    "asthma",
    "copd",
    "pregnant",
    "pregnancy",
    "wheelchair",
    "disability",
    "disabled",
    "hospital",
)
AGE_PHRASES = ("baby", "toddler", "child", "children", "infant", "newborn", "elderly", "older person")
COMMUNICATION_PHRASES = ("interpreter", "british sign language", "bsl")

STALE_RE = re.compile(
    r"(inspection|inspected|survey|surveyed|report|reported|aware|awareness|as of|noticed)"
    r".{0,48}\b(19\d{2}|20[01]\d|202[0-4])\b"
    r"|\b(19\d{2}|20[01]\d|202[0-4])\b.{0,48}"
    r"(inspection|survey|awareness|as of)",
    re.IGNORECASE,
)


def triage(
    text: str,
    aware_at: datetime,
    *,
    social_home_in_england: bool = False,
    officer_approved_category: bool = False,
    officer_approved_clock: bool = False,
    officer_approved_summary: bool = False,
    officer_approved_record: bool = False,
    confirmed_category: str | None = None,
    confirmed_hazard_family: str | None = None,
    officer_steps: list[dict] | None = None,
    barrier: str | None = None,
    **clock_kwargs,
) -> dict:
    """Propose a triage. Officer flags are arguments, never read out of the text."""
    if aware_at.tzinfo is None:
        raise ValueError("awareness time must be timezone-aware (Europe/London)")
    if officer_approved_summary and not (officer_approved_category and officer_approved_clock):
        raise ValueError("the summary cannot be approved before the category and the clock")
    if officer_approved_category and confirmed_category not in ("emergency", "significant", "not_in_scope"):
        raise ValueError("an approved category must be emergency, significant, or not_in_scope")
    if officer_approved_category and not confirmed_hazard_family:
        raise ValueError("an approved category needs a confirmed hazard family")

    lowered = text.lower()
    injection = [pattern for pattern in INJECTION_PATTERNS if pattern in lowered]
    stale = _stale_signals(text)
    proposal = _propose(lowered)
    if injection and proposal["category"] in ("emergency", "significant"):
        proposal["downgrade_refused"] = True
    proposal["downgrade_refused"] = proposal.get("downgrade_refused", False) or _asked_to_downgrade(lowered, proposal)

    if officer_approved_category:
        calc_category = confirmed_category
        calc_family = confirmed_hazard_family
    else:
        calc_category = proposal["category"]
        calc_family = proposal["hazard_family"]

    clock = calculate_statutory_clock(
        aware_at,
        calc_family,
        calc_category,
        social_home_in_england=social_home_in_england,
        officer_approved_category=officer_approved_category,
        officer_approved_clock=officer_approved_clock,
        **clock_kwargs,
    )
    lower_than_proposed = bool(
        officer_approved_category
        and proposal["category"] == "emergency"
        and confirmed_category != "emergency"
    )
    flags = _characteristics(text)
    summary = _summary(
        proposal,
        clock,
        officer_approved_summary=officer_approved_summary,
        officer_approved_category=officer_approved_category,
        officer_approved_clock=officer_approved_clock,
    )
    record = draft_endeavours_record(
        officer_steps,
        barrier=barrier,
        officer_approved=officer_approved_record,
    )
    result = {
        "processing_mode": "mock",
        "evaluation_label": SMOKE_LABEL,
        "synthetic_data": True,
        "aware_at": aware_at.isoformat(),
        "proposed": proposal,
        "officer": {
            "social_home_in_england": social_home_in_england,
            "category_approved": officer_approved_category,
            "confirmed_category": confirmed_category if officer_approved_category else None,
            "confirmed_hazard_family": confirmed_hazard_family if officer_approved_category else None,
            "clock_approved": officer_approved_clock,
            "summary_approved": officer_approved_summary,
            "record_approved": officer_approved_record,
            "recorded_a_lower_category_than_proposed": lower_than_proposed,
        },
        "statutory_clock": clock,
        "vulnerability_flags": {
            "tenant_labelled_vulnerable": False,
            "flags": flags,
            "recorded_on_housing_system": False,
        },
        "tenant_summary": summary,
        "reasonable_endeavours": record,
        "housing_ombudsman": ombudsman_information(),
        "text_suggests_not_social_housing": any(
            phrase in lowered for phrase in ("private landlord", "private rented", "rent from a private")
        ),
        "security": {
            "prompt_injection_detected": bool(injection),
            "injection_signals": injection,
            "stale_data_signals": stale,
            "actions_taken": [],
        },
        "decisions_not_taken": list(DECISIONS_NOT_TAKEN),
    }
    # Keep the officer's awareness time. Do not re-parse it from the narrative.
    result["aware_at"] = aware_at.isoformat()
    validate_triage(result)
    return result


def _asked_to_downgrade(lowered: str, proposal: dict) -> bool:
    if proposal["category"] not in ("emergency", "significant"):
        return False
    phrases = ("downgrade", "not a hazard", "non-urgent", "classify this as not", "all-clear", "all clear")
    return any(phrase in lowered for phrase in phrases)


def _propose(lowered: str) -> dict:
    for family, phrases in EMERGENCY_RULES:
        hit = _first(lowered, phrases)
        if hit:
            return _proposal(
                family,
                "emergency",
                f"The report contains '{hit}', which this stand-in treats as an emergency signal for an officer to accept or change.",
                hit,
            )
    if re.search(r"\b(baby|infant|newborn)\b", lowered) and re.search(r"\b(freezing|no heating)\b", lowered):
        return _proposal(
            "excess_cold",
            "emergency",
            "The report describes a baby or infant and no heating or freezing conditions. This stand-in does not downgrade that to a routine repair.",
            "baby",
        )
    overcrowding = _first(lowered, OVERCROWDING_PHRASES)
    for family, phrases in SIGNIFICANT_RULES:
        hit = _first(lowered, phrases)
        if hit:
            note = ""
            if overcrowding and family == DAMP:
                note = " Overcrowding is also mentioned. It is outside the regulations, and it does not remove the damp signal."
            return _proposal(
                family,
                "significant",
                f"The report contains '{hit}'. This stand-in proposes a significant hazard for an officer to accept or change.{note}",
                hit,
            )
    if overcrowding:
        return _proposal(
            OVERCROWDING,
            "not_in_scope",
            "The only signal is overcrowding. Regulation 3 excludes a lack of adequate space from an emergency hazard, and it is not a Phase 1 significant hazard. The officer still confirms that reading.",
            overcrowding,
        )
    for family, phrases in WEAK_RULES:
        hit = _first(lowered, phrases)
        if hit:
            return _proposal(
                family,
                "uncertain",
                f"The report contains '{hit}'. That is not enough for this stand-in to choose emergency or significant. The officer must categorise it. The proposal has not been lowered to 'not a hazard'.",
                hit,
            )
    return _proposal(
        NONE,
        "uncertain",
        "No prescribed-hazard signal was found by this stand-in. That is not a decision that the home is safe.",
        None,
    )


def _proposal(family: str, category: str, reason: str, signal: str | None) -> dict:
    return {
        "hazard_family": family,
        "category": category,
        "reason": reason,
        "signal": signal,
        "confidence": "keyword_stand_in",
        "downgrade_refused": False,
        "not_a_model_score": True,
    }


def _first(lowered: str, phrases: tuple[str, ...]) -> str | None:
    for phrase in phrases:
        if phrase in lowered:
            return phrase
    return None


def _characteristics(text: str) -> list[dict]:
    lowered = text.lower()
    found = []
    groups = (
        ("health", HEALTH_PHRASES, True),
        ("age", AGE_PHRASES, False),
        ("communication", COMMUNICATION_PHRASES, False),
    )
    for name, phrases, special in groups:
        hit = _first(lowered, phrases)
        if hit:
            found.append(
                {
                    "characteristic": name,
                    "quote": _quote(text, hit),
                    "may_be_special_category_or_childrens_data": special or name == "age",
                    "label_applied": False,
                }
            )
    if "vulnerable" in lowered:
        found.append(
            {
                "characteristic": "words_used_by_the_tenant",
                "quote": _quote(text, "vulnerable"),
                "may_be_special_category_or_childrens_data": False,
                "label_applied": False,
            }
        )
    return found


def _quote(text: str, needle: str) -> str:
    index = text.lower().find(needle)
    if index < 0:
        return needle
    start = max(0, index - 40)
    end = min(len(text), index + len(needle) + 40)
    return " ".join(text[start:end].split())


def _stale_signals(text: str) -> list[str]:
    signals = []
    for match in STALE_RE.finditer(text):
        signals.append(match.group(0))
    lowered = text.lower()
    for phrase in ("treat that as current", "treat this as current", "clock started in"):
        if phrase in lowered:
            signals.append(phrase)
    return signals


def _summary(proposal: dict, clock: dict, *, officer_approved_summary: bool, officer_approved_category: bool, officer_approved_clock: bool) -> dict:
    approved = officer_approved_summary and officer_approved_category and officer_approved_clock
    lines = [
        "Draft written summary for an officer. This has not been given to the tenant.",
        "The agent cannot send it.",
    ]
    if approved:
        lines.append(
            "An officer has marked this draft as approved for them to edit and send outside this agent. The agent has not sent it."
        )
    else:
        lines.append("An officer has not approved this summary.")
    if clock.get("operative"):
        operative = [item for item in clock["deadlines"] if item["operative"]]
        lines.append("Dates copied from the statutory clock, not written by the stand-in:")
        for item in operative:
            when = item["at"] or item["on"]
            lines.append(f"- {item['name']}: {when} ({item['rule']}).")
    else:
        lines.append(
            "The statutory clock is not operative. Do not treat any date as a deadline that has been approved."
        )
    lines.append(
        "Regulation 9 asks for whether a significant or emergency hazard was identified, "
        "what it is, the action and a target timescale or that no action is required and why, "
        "and how the tenant can contact the landlord. The officer completes those points. "
        "This draft does not decide them."
    )
    lines.append("Contact route: the officer inserts the landlord's contact details.")
    lines.append(f"Proposal only, for the officer to change: {proposal['category']} / {proposal['hazard_family']}.")
    return {
        "status": "draft_for_officer",
        "may_be_sent_by_agent": False,
        "officer_approved": approved,
        "text": "\n".join(lines),
    }


def validate_triage(result: dict) -> None:
    """Reject a draft that claims an action this agent cannot take."""
    if result["tenant_summary"]["may_be_sent_by_agent"] is not False:
        raise ValueError("the agent must not send")
    if result["vulnerability_flags"]["tenant_labelled_vulnerable"] is not False:
        raise ValueError("the tenant must not be labelled vulnerable")
    if result["vulnerability_flags"]["recorded_on_housing_system"] is not False:
        raise ValueError("a vulnerability flag must not be written to a housing system")
    if result["reasonable_endeavours"]["defence_made_out"] is not False:
        raise ValueError("the defence must not be recorded as made out")
    if result["reasonable_endeavours"]["may_be_filed_by_agent"] is not False:
        raise ValueError("the record must not be filed by the agent")
    if result["housing_ombudsman"]["referral_made_by_agent"] is not False:
        raise ValueError("the agent must not refer to the Ombudsman")
    if result["housing_ombudsman"]["jurisdiction_decided_by_agent"] is not False:
        raise ValueError("the agent must not decide Ombudsman jurisdiction")
    if result["security"]["actions_taken"] != []:
        raise ValueError("the agent must not take an action")
    text = result["tenant_summary"]["text"].lower()
    for banned in ("this has been sent", "i have sent", "defence is made out", "i uphold"):
        if banned in text:
            raise ValueError(f"summary contains a prohibited phrase: {banned}")
    officer = result["officer"]
    if not (officer["category_approved"] and officer["clock_approved"]):
        for item in result["statutory_clock"]["deadlines"]:
            if item["operative"]:
                raise ValueError("a deadline is operative without officer approval")
    for flag in result["vulnerability_flags"]["flags"]:
        if flag["label_applied"] is not False:
            raise ValueError("a characteristic flag applied a label")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Mock Awaab's Law triage. Nothing is sent.")
    parser.add_argument("--aware-at", required=True)
    parser.add_argument("--input", required=True, help="Path to a synthetic report")
    parser.add_argument("--social-home-in-england", action="store_true")
    parser.add_argument("--approve-category", action="store_true")
    parser.add_argument("--approve-clock", action="store_true")
    parser.add_argument("--approve-summary", action="store_true")
    parser.add_argument("--confirmed-category", default=None)
    parser.add_argument("--confirmed-hazard-family", default=None)
    args = parser.parse_args(argv)
    text = Path(args.input).read_text(encoding="utf-8")
    aware = datetime.fromisoformat(args.aware_at)
    result = triage(
        text,
        aware,
        social_home_in_england=args.social_home_in_england,
        officer_approved_category=args.approve_category,
        officer_approved_clock=args.approve_clock,
        officer_approved_summary=args.approve_summary,
        confirmed_category=args.confirmed_category,
        confirmed_hazard_family=args.confirmed_hazard_family,
    )
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
