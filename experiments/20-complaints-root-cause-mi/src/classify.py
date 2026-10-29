"""Assign one theme to one redacted narrative.

Financial services uses Experiment 02. Housing uses a starter lexicon that
the Complaint Handling Code does not publish. Energy uses the category names
in the Ofgem guidance. First matching rule wins. The complaints owner
validates the assignment.
"""

from __future__ import annotations

import re

from reuse import analyse

HOUSING_RULES = (
    ("damp_mould", ("damp", "mould", "mold")),
    ("antisocial_behaviour", ("antisocial", "anti-social", "anti social")),
    (
        "complaint_handling",
        ("stage two", "no acknowledgement", "did not acknowledge", "complaint was ignored"),
    ),
    ("rent_and_service_charges", ("service charge", "rent")),
    ("repairs", ("repair", "leak", "boiler", "heating")),
    ("staff_conduct", ("rude", "shouted")),
)

METER_VALUES = ("classic_credit", "classic_ppm", "smart_credit", "smart_ppm")
PPM = {"classic_ppm", "smart_ppm"}
SMART = {"smart_credit", "smart_ppm"}

# Order is the first-match order. Meter-independent categories come first.
ENERGY_INDEPENDENT = (
    ("B10", ("feed-in tariff", "feed in tariff", "fit payment")),
    ("B8", ("price comparison", "broker", "third-party", "third party")),
    ("B7", ("mis-sold", "missold", "mis-selling", "sales agent")),
    ("B12", ("price increase", "tariff increase", "more expensive tariff")),
    ("B11", ("direct debit", "direct-debit", "payment method")),
    ("B9", ("on hold", "could not get through", "couldn't get through", "customer service", "missed appointment")),
)

DEBT_PHRASES = ("disconnection", "disconnected", "debt", "warrant", "self-disconnection")
BILLING_PHRASES = ("bills", "bill", "meter reading", "estimated reading", "back billing")
SWITCH_PHRASES = ("switch", "switched", "erroneous transfer", "new supplier")
METER_PHRASES = ("meter not working", "installation", "in-home display", "in home display")


def _has(text: str, phrase: str) -> bool:
    return re.search(rf"\b{re.escape(phrase)}\b", text) is not None


def _any(text: str, phrases: tuple[str, ...]) -> bool:
    return any(_has(text, phrase) for phrase in phrases)


def _first(text: str, phrases: tuple[str, ...]) -> str | None:
    for phrase in phrases:
        if _has(text, phrase):
            return phrase
    return None


def _meter_hint(text: str) -> str | None:
    # "not a smart meter" contains the words "smart meter". The negation wins.
    not_smart = _any(text, ("not a smart", "classic meter", "traditional meter"))
    smart = False if not_smart else _any(text, ("smart meter", "smart"))
    ppm = _any(text, ("prepayment", "pre-payment", "pay as you go", "pay-as-you-go", "top up", "top-up", "ppm"))
    if smart and ppm:
        return "smart_ppm"
    if smart:
        return "smart_credit"
    if ppm:
        return "classic_ppm"
    if not_smart:
        return "classic_credit"
    return None


def _resolve_meter(record_meter: object, text: str) -> tuple[str | None, str]:
    if isinstance(record_meter, str) and record_meter in METER_VALUES:
        return record_meter, "record"
    if record_meter not in (None, "", "unknown"):
        return None, "record_not_in_closed_list"
    hint = _meter_hint(text)
    if hint:
        return hint, "narrative_hint"
    return None, "unknown"


def _meter_category(family: str, meter: str | None) -> str | None:
    if meter is None:
        return None
    if family == "debt":
        return "B6" if meter in PPM else "B5"
    if family == "billing":
        return "B14" if meter in SMART else "B13"
    if family == "switching":
        if meter == "smart_ppm":
            return "B17"
        if meter == "smart_credit":
            return "B16"
        return "B15"
    if family == "meter":
        return {
            "classic_credit": "B18",
            "smart_credit": "B19",
            "classic_ppm": "B20",
            "smart_ppm": "B21",
        }[meter]
    return None


def classify_housing(text: str) -> dict:
    lower = text.lower()
    for theme, phrases in HOUSING_RULES:
        phrase = _first(lower, phrases)
        if phrase:
            return {
                "theme": theme,
                "matched_phrase": phrase,
                "source": "housing_starter_lexicon",
                "meter_context": None,
                "meter_context_source": None,
                "assignment_reason": "first_matching_rule",
            }
    return {
        "theme": "unassigned",
        "matched_phrase": None,
        "source": "housing_starter_lexicon",
        "meter_context": None,
        "meter_context_source": None,
        "assignment_reason": "no_lexicon_phrase",
    }


def classify_energy(text: str, meter_context: object) -> dict:
    lower = text.lower()
    meter, meter_source = _resolve_meter(meter_context, lower)
    for theme, phrases in ENERGY_INDEPENDENT:
        phrase = _first(lower, phrases)
        if phrase:
            return _energy(theme, phrase, meter, meter_source, "first_matching_rule")
    for family, phrases in (
        ("debt", DEBT_PHRASES),
        ("billing", BILLING_PHRASES),
        ("switching", SWITCH_PHRASES),
        ("meter", METER_PHRASES),
    ):
        phrase = _first(lower, phrases)
        if not phrase:
            continue
        theme = _meter_category(family, meter)
        if theme is None:
            return _energy("unassigned", phrase, meter, meter_source, "meter_context_required")
        return _energy(theme, phrase, meter, meter_source, "first_matching_rule")
    return _energy("unassigned", None, meter, meter_source, "no_table_1_phrase")


def _energy(theme: str, phrase: str | None, meter, meter_source: str, reason: str) -> dict:
    return {
        "theme": theme,
        "matched_phrase": phrase,
        "source": "ofgem_guidance_table_1",
        "meter_context": meter,
        "meter_context_source": meter_source,
        "assignment_reason": reason,
    }


def classify_financial(text: str, intake: object) -> dict:
    view = analyse()(text)
    suggested = view["cause"]
    base = {
        "product": view["product"],
        "cause_suggested_by_experiment_02": suggested,
        "duty_outcome_touched": view["outcome"],
        "vulnerability_drivers": [flag["driver"] for flag in view["flags"]],
        "customer_labelled_vulnerable": False,
        "breach_found": False,
        "matched_phrase": None,
        "meter_context": None,
        "meter_context_source": None,
    }
    if isinstance(intake, dict):
        supplied = (intake.get("root_cause") or {}).get("suggested")
        if supplied != suggested:
            return {
                **base,
                "theme": "needs_owner",
                "source": "experiment_02_disagreement",
                "assignment_reason": "intake_cause_differs_from_analyse",
                "intake_cause": supplied if isinstance(supplied, str) else None,
            }
        return {
            **base,
            "theme": suggested,
            "source": "experiment_02_intake_agrees_with_analyse",
            "assignment_reason": "intake_and_analyse_agree",
            "intake_cause": supplied,
        }
    return {
        **base,
        "theme": suggested,
        "source": "experiment_02_analyse",
        "assignment_reason": "analyse_only",
        "intake_cause": None,
    }


def classify(sector: str, text: str, record: dict) -> dict:
    if sector == "financial_services":
        return classify_financial(text, record.get("intake"))
    if sector == "social_housing":
        result = classify_housing(text)
        if record.get("intake") is not None:
            result["intake_ignored"] = True
        return result
    if sector == "energy":
        result = classify_energy(text, record.get("meter_context"))
        if record.get("intake") is not None:
            result["intake_ignored"] = True
        return result
    raise ValueError("sector is not supported")
