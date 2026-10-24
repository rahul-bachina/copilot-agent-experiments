#!/usr/bin/env python3
"""Deterministic Awaab's Law timeframe calculator. England only.

Dates are computed here, in code. A language model must not supply them.
The text was read on 24 October 2026.

In force that day: the Hazards in Social Housing (Prescribed Requirements)
(England) Regulations 2025 (SI 2025/1042), from 27 October 2025.
Not in force: the draft 2026 amendment (Phase 2, stated commencement
30 November 2026, not yet made) and Phase 3 (no instrument found).

This is a calculation aid for a housing officer. It is not a decision,
and it is not legal advice.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timedelta
from typing import Iterable
from zoneinfo import ZoneInfo

from working_days import closed_days_covering, inclusive_week_period_end, working_period_end

LONDON = ZoneInfo("Europe/London")
RETRIEVED_ON = date(2026, 10, 24)
PHASE_1_FROM = date(2025, 10, 27)
PHASE_2_INTENDED = date(2026, 11, 30)

SI_URL = "https://www.legislation.gov.uk/uksi/2025/1042"
DRAFT_AMENDMENT_URL = "https://www.legislation.gov.uk/ukdsi/2026/9780348285611"
SECTION_10A_URL = "https://www.legislation.gov.uk/ukpga/1985/70/section/10A"
GUIDANCE_URL = (
    "https://www.gov.uk/government/publications/"
    "awaabs-law-phase-2-guidance-for-social-housing-landlords/"
    "awaabs-law-phase-2-guidance-for-social-landlords"
)
HHSRS_SCHEDULE_URL = "https://www.legislation.gov.uk/uksi/2005/3208/schedule/1"

DAMP = "damp_mould_fungal_growth"
OVERCROWDING = "overcrowding"
OTHER = "other_prescribed"
NONE = "none"

# Paragraph numbers are Schedule 1 to the HHSRS (England) Regulations 2005
# as amended by SI 2026/571 from 23 June 2026. The draft Awaab's Law
# amendment cites these paragraphs. That amendment was not made on the
# retrieval date, so they are not an operative significant-hazard list.
PHASE_2_FAMILIES: dict[str, dict[str, str]] = {
    "excess_cold": {"paragraph": "2", "title": "Excess cold"},
    "excess_heat": {"paragraph": "3", "title": "Excess heat"},
    "domestic_hygiene": {"paragraph": "14A", "title": "Domestic hygiene"},
    "falls_on_the_level": {"paragraph": "18A", "title": "Falls on the level"},
    "falls_on_stairs": {"paragraph": "21", "title": "Falls on stairs"},
    "falls_between_levels": {"paragraph": "22", "title": "Falls between levels"},
    "electrical": {"paragraph": "23", "title": "Electrical hazards"},
    "fire_and_explosions": {"paragraph": "23A", "title": "Fire and explosions"},
    "structural_collapse": {"paragraph": "29", "title": "Structural collapse and falling elements"},
}

FAMILY_TITLES = {
    DAMP: "Damp, mould or fungal growth",
    OVERCROWDING: "Lack of adequate space for living and sleeping",
    OTHER: "Other prescribed hazard (Phase 3, not in force as a significant hazard)",
    NONE: "No hazard family selected",
    **{key: value["title"] for key, value in PHASE_2_FAMILIES.items()},
}

CATEGORIES = ("emergency", "significant", "not_in_scope", "uncertain")
HAZARD_FAMILIES = frozenset(FAMILY_TITLES)


def _iso_date(value: date | None) -> str | None:
    return value.isoformat() if value else None


def _iso_dt(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.astimezone(LONDON).isoformat()


def london_date(value: datetime) -> date:
    if value.tzinfo is None:
        raise ValueError("awareness time must be timezone-aware (Europe/London)")
    return value.astimezone(LONDON).date()


def _deadline(
    identifier: str,
    name: str,
    rule: str,
    *,
    on: date | None = None,
    at: datetime | None = None,
    operative: bool,
    in_force: bool,
    note: str,
) -> dict:
    return {
        "id": identifier,
        "name": name,
        "rule": rule,
        "on": _iso_date(on if on is not None else (at.astimezone(LONDON).date() if at else None)),
        "at": _iso_dt(at),
        "operative": operative,
        "in_force": in_force,
        "note": note,
    }


def _phase_2_record(in_force: bool) -> dict:
    return {
        "id": "phase_2",
        "name": "Wider significant hazards, and a changed significant-risk test",
        "in_force": in_force,
        "intended_in_force_from": PHASE_2_INTENDED.isoformat(),
        "instrument": (
            "Draft Hazards in Social Housing (Prescribed Requirements) "
            "(England) (Amendment) Regulations 2026"
        ),
        "instrument_url": DRAFT_AMENDMENT_URL,
        "status_on_retrieval": (
            "Not made. The legislation.gov.uk page retrieved on 24 October 2026 "
            "said this was a draft and had not yet been made as a UK statutory instrument. "
            "The draft says it comes into force on 30 November 2026."
        ),
    }


def _phase_3_record() -> dict:
    return {
        "id": "phase_3",
        "name": "Remaining HHSRS hazards except overcrowding, as significant hazards",
        "in_force": False,
        "intended_in_force_from": None,
        "instrument": None,
        "status_on_retrieval": (
            "Not in force. MHCLG guidance retrieved on 24 October 2026 describes Phase 3 "
            "and does not give a commencement date. A GOV.UK news story says the third "
            "phase will be introduced in 2027. No statutory instrument was found. "
            "A date in a local timeline was not treated as a commencement date."
        ),
    }


def scope_status(
    hazard_family: str,
    category: str,
    *,
    as_of: date,
    caller_asserts_phase_2_instrument_in_force: bool,
) -> dict:
    """Whether this category and family are inside the made regulations."""
    if hazard_family not in HAZARD_FAMILIES:
        raise ValueError(f"unknown hazard family: {hazard_family}")
    if category not in CATEGORIES:
        raise ValueError(f"unknown category: {category}")

    warnings: list[str] = []
    if caller_asserts_phase_2_instrument_in_force:
        warnings.append(
            "The caller asserted that the Phase 2 amendment is in force. "
            "On 24 October 2026 legislation.gov.uk still showed it as a draft "
            "that had not been made. An assertion does not make that draft law."
        )

    phase_2_started = (
        caller_asserts_phase_2_instrument_in_force and as_of >= PHASE_2_INTENDED
    )
    phase_1_started = as_of >= PHASE_1_FROM

    def pack(in_force: bool, phase_id: str, reason: str) -> dict:
        phases_not = []
        if not phase_2_started:
            phases_not.append(_phase_2_record(False))
        phases_not.append(_phase_3_record())
        return {
            "in_force": in_force,
            "phase_id": phase_id,
            "reason": reason,
            "warnings": warnings,
            "phases_not_in_force": phases_not,
            "significant_risk_test_encoded": (
                "regulation 3(1)(b) as made: a reasonable lessor with the relevant "
                "knowledge would take steps to make safe as a matter of urgency "
                "(but not within 24 hours). The draft amendment's substitute, "
                "'make safe within 15 working days', is not encoded."
            ),
        }

    if hazard_family == OVERCROWDING or category == "not_in_scope":
        return pack(
            False,
            "out_of_scope",
            "No Awaab's Law clock. Regulation 3 excludes a lack of adequate space "
            "for living and sleeping from an emergency hazard. Significant hazards "
            "in force on the retrieval date are damp, mould or fungal growth only. "
            "MHCLG guidance says Phase 3 will still exclude overcrowding. "
            "Other housing duties are outside this module.",
        )

    if category == "uncertain":
        return pack(
            False,
            "undecided",
            "No category has been chosen, so no timeframe is operative. "
            "Illustrations, if present, are not deadlines.",
        )

    if not phase_1_started:
        return pack(
            False,
            "phase_1",
            "SI 2025/1042 comes into force on 27 October 2025. "
            f"The as-of date {as_of.isoformat()} is before that.",
        )

    if category == "emergency":
        reason = (
            "Phase 1, in force from 27 October 2025: an emergency hazard is a "
            "relevant hazard other than one associated with a lack of adequate "
            "space for living and sleeping (regulation 3). The officer's "
            "confirmation is still required before the clock is operative."
        )
        if hazard_family == "fire_and_explosions":
            warnings.append(
                "The draft Phase 2 amendment would exclude some fire hazards "
                "that arise from a deficiency in a part of a building regulated "
                "by the Fire Safety Order. That exclusion was not law on "
                "24 October 2026 and is not applied."
            )
        if hazard_family in PHASE_2_FAMILIES:
            warnings.append(
                "This family is on the draft Phase 2 list of significant hazards. "
                "That list is not in force. An emergency hazard in the same family "
                "can already fall under Phase 1 if the officer confirms it."
            )
        return pack(True, "phase_1", reason)

    # significant
    if hazard_family == DAMP:
        return pack(
            True,
            "phase_1",
            "Phase 1 significant hazard: risk of harm associated with exposure "
            "to damp, mould or fungal growth (regulation 3(2)). In force from "
            "27 October 2025.",
        )
    if hazard_family in PHASE_2_FAMILIES:
        detail = PHASE_2_FAMILIES[hazard_family]
        if phase_2_started:
            warnings.append(
                "Phase 2 is operative in this result only because the caller "
                "asserted that the amendment has been made and the as-of date "
                "is on or after 30 November 2026. Confirm the made instrument "
                "on legislation.gov.uk before relying on it."
            )
            return pack(
                True,
                "phase_2",
                f"Caller-asserted Phase 2 significant hazard: {detail['title']} "
                f"(HHSRS Schedule 1 paragraph {detail['paragraph']}).",
            )
        why = (
            "The draft amendment had not been made on 24 October 2026."
            if not caller_asserts_phase_2_instrument_in_force
            else "The stated commencement of 30 November 2026 has not been reached."
        )
        return pack(
            False,
            "phase_2",
            f"{detail['title']} (HHSRS Schedule 1 paragraph {detail['paragraph']}) "
            f"is a Phase 2 significant hazard and is not in force. {why} "
            "The dates below are a reference, not a statutory deadline.",
        )
    return pack(
        False,
        "phase_3",
        "A significant hazard in this family is Phase 3. No commencement "
        "date was verified on 24 October 2026. There is no flag that turns "
        "a Phase 3 significant-hazard clock on. An emergency category, if "
        "the officer confirms one, is a separate Phase 1 question.",
    )


def calculate_statutory_clock(
    aware_at: datetime,
    hazard_family: str,
    category: str,
    *,
    social_home_in_england: bool = False,
    officer_approved_category: bool = False,
    officer_approved_clock: bool = False,
    investigation_completed_on: date | None = None,
    investigation_completed_at: datetime | None = None,
    physical_inspection_requested_on: date | None = None,
    investigation_kind: str = "standard",
    emergency_condition: str | None = None,
    part_6_complied: bool | None = None,
    supplementary_preventative_work_identified: bool | None = None,
    further_investigation_completed_on: date | None = None,
    not_reasonably_practicable_to_begin: bool | None = None,
    caller_asserts_phase_2_instrument_in_force: bool = False,
    as_of: date = RETRIEVED_ON,
    extra_non_working_days: Iterable[date] = (),
    cancelled_bank_holidays: Iterable[date] = (),
) -> dict:
    """Return the timeframes. Operative only with officer approval and an in-force phase."""
    if investigation_kind not in ("standard", "renewed"):
        raise ValueError("investigation_kind must be 'standard' or 'renewed'")
    if emergency_condition not in (None, "1", "2"):
        raise ValueError("emergency_condition must be None, '1', or '2'")
    if aware_at.tzinfo is None:
        raise ValueError("awareness time must be timezone-aware (Europe/London)")
    if investigation_completed_at is not None and investigation_completed_at.tzinfo is None:
        raise ValueError("investigation completion time must be timezone-aware")

    if category == "uncertain":
        shared = dict(
            social_home_in_england=social_home_in_england,
            officer_approved_category=False,
            officer_approved_clock=False,
            investigation_completed_on=investigation_completed_on,
            investigation_completed_at=investigation_completed_at,
            physical_inspection_requested_on=physical_inspection_requested_on,
            investigation_kind=investigation_kind,
            emergency_condition=emergency_condition,
            part_6_complied=part_6_complied,
            supplementary_preventative_work_identified=supplementary_preventative_work_identified,
            further_investigation_completed_on=further_investigation_completed_on,
            not_reasonably_practicable_to_begin=not_reasonably_practicable_to_begin,
            caller_asserts_phase_2_instrument_in_force=caller_asserts_phase_2_instrument_in_force,
            as_of=as_of,
            extra_non_working_days=extra_non_working_days,
            cancelled_bank_holidays=cancelled_bank_holidays,
        )
        emergency_view = calculate_statutory_clock(
            aware_at, hazard_family, "emergency", **shared
        )
        significant_view = calculate_statutory_clock(
            aware_at, hazard_family, "significant", **shared
        )
        scope = scope_status(
            hazard_family,
            "uncertain",
            as_of=as_of,
            caller_asserts_phase_2_instrument_in_force=caller_asserts_phase_2_instrument_in_force,
        )
        return _envelope(
            aware_at=aware_at,
            hazard_family=hazard_family,
            category="uncertain",
            social_home_in_england=social_home_in_england,
            officer_approved_category=False,
            officer_approved_clock=False,
            scope=scope,
            scope_as_of=as_of,
            deadlines=[],
            operative_block_reason=(
                "No category has been approved. The illustrations are not deadlines."
            ),
            illustrations={
                "if_officer_confirms_emergency": emergency_view,
                "if_officer_confirms_significant": significant_view,
            },
        )

    scope = scope_status(
        hazard_family,
        category,
        as_of=as_of,
        caller_asserts_phase_2_instrument_in_force=caller_asserts_phase_2_instrument_in_force,
    )
    blocks: list[str] = []
    if not social_home_in_england:
        blocks.append("The officer has not confirmed that this is a social home in England.")
    if not officer_approved_category:
        blocks.append("The officer has not approved the hazard category.")
    if not officer_approved_clock:
        blocks.append("The officer has not approved the clock.")
    if not scope["in_force"]:
        blocks.append(scope["reason"])
    approved = not blocks
    in_force = scope["in_force"]

    anchor_dates = [london_date(aware_at), as_of]
    for value in (
        investigation_completed_on,
        physical_inspection_requested_on,
        further_investigation_completed_on,
    ):
        if value is not None:
            anchor_dates.append(value)
    if investigation_completed_at is not None:
        anchor_dates.append(investigation_completed_at.astimezone(LONDON).date())
    closed = closed_days_covering(
        anchor_dates,
        extra_non_working_days=extra_non_working_days,
        cancelled_bank_holidays=cancelled_bank_holidays,
    )

    deadlines: list[dict] = []
    if category == "emergency":
        deadlines.extend(
            _emergency_deadlines(
                aware_at,
                closed,
                approved=approved,
                in_force=in_force,
                emergency_condition=emergency_condition,
                part_6_complied=part_6_complied,
                investigation_completed_at=investigation_completed_at,
            )
        )
    elif category == "significant":
        deadlines.extend(
            _investigation_deadlines(
                london_date(aware_at),
                closed,
                approved=approved,
                in_force=in_force,
                physical_inspection_requested_on=physical_inspection_requested_on,
                investigation_kind=investigation_kind,
            )
        )

    if category in ("emergency", "significant") and investigation_completed_on is not None:
        deadlines.append(
            _summary_deadline(investigation_completed_on, closed, approved=approved, in_force=in_force)
        )
        if category == "significant":
            deadlines.append(
                _significant_safety_deadline(
                    investigation_completed_on,
                    closed,
                    approved=approved,
                    in_force=in_force,
                    part_6_complied=part_6_complied,
                )
            )
        deadlines.extend(
            _preventative_deadlines(
                investigation_completed_on,
                closed,
                approved=approved,
                in_force=in_force,
                identified=supplementary_preventative_work_identified,
                further_investigation_completed_on=further_investigation_completed_on,
                not_reasonably_practicable_to_begin=not_reasonably_practicable_to_begin,
            )
        )
    elif category in ("emergency", "significant"):
        deadlines.append(
            _deadline(
                "awaiting_investigation_completion",
                "Deadlines that run from investigation completion",
                "SI 2025/1042 regulations 9, 11 and 13",
                operative=False,
                in_force=in_force,
                note=(
                    "Not calculated. The written summary, significant-hazard safety "
                    "work, and supplementary preventative work run from the day the "
                    "investigation is completed. The officer has not recorded that day."
                ),
            )
        )

    return _envelope(
        aware_at=aware_at,
        hazard_family=hazard_family,
        category=category,
        social_home_in_england=social_home_in_england,
        officer_approved_category=officer_approved_category,
        officer_approved_clock=officer_approved_clock,
        scope=scope,
        scope_as_of=as_of,
        deadlines=deadlines,
        operative_block_reason=" ".join(blocks),
        illustrations=None,
    )


def _envelope(
    *,
    aware_at: datetime,
    hazard_family: str,
    category: str,
    social_home_in_england: bool,
    officer_approved_category: bool,
    officer_approved_clock: bool,
    scope: dict,
    scope_as_of: date,
    deadlines: list[dict],
    operative_block_reason: str,
    illustrations: dict | None,
) -> dict:
    operative = any(item["operative"] for item in deadlines)
    result = {
        "as_of": RETRIEVED_ON.isoformat() if "as_of" not in scope else None,
        "sources_retrieved_on": RETRIEVED_ON.isoformat(),
        "scope_as_of": scope_as_of.isoformat(),
        "timezone": "Europe/London",
        "aware_at": _iso_dt(aware_at),
        "hazard_family": hazard_family,
        "hazard_family_title": FAMILY_TITLES[hazard_family],
        "category": category,
        "social_home_in_england": social_home_in_england,
        "officer_approved_category": officer_approved_category,
        "officer_approved_clock": officer_approved_clock,
        "in_force": scope["in_force"],
        "operative": operative,
        "operative_block_reason": None if operative else operative_block_reason,
        "phase_id": scope["phase_id"],
        "scope_reason": scope["reason"],
        "significant_risk_test_encoded": scope["significant_risk_test_encoded"],
        "warnings": scope["warnings"],
        "phases_not_in_force": scope["phases_not_in_force"],
        "deadlines": deadlines,
        "reasonable_endeavours": {
            "defence_made_out": False,
            "decided_by_this_module": False,
            "statute": "Landlord and Tenant Act 1985, section 10A(5)",
            "statute_url": SECTION_10A_URL,
            "note": (
                "Section 10A(5) is a defence the lessor must prove: that they used "
                "all reasonable endeavours to avoid the breach. Regulations 5, 11 and 13 "
                "also stop particular duties once all reasonable endeavours to obtain "
                "a necessary consent are exhausted. This module does not decide either question."
            ),
        },
        "counting": {
            "working_day": (
                "Regulation 2: any day other than a Saturday, a Sunday, Christmas Day, "
                "Good Friday, or a bank holiday under the Banking and Financial Dealings "
                "Act 1971 in England and Wales."
            ),
            "day_one": (
                "For working-day periods, day 1 is the day after the trigger when that "
                "day is a working day, otherwise the next working day. The emergency "
                "period is 24 hours and does not skip weekends."
            ),
            "twelve_weeks": (
                "A period of 12 weeks beginning with the day after the determination "
                "is 84 days beginning with that day, inclusive. The last day is 83 days later."
            ),
        },
        "sources": {
            "regulations": SI_URL,
            "draft_amendment": DRAFT_AMENDMENT_URL,
            "section_10A": SECTION_10A_URL,
            "guidance": GUIDANCE_URL,
            "hhsrs_schedule_1": HHSRS_SCHEDULE_URL,
        },
    }
    # as_of on the envelope is the retrieval date of the legal text, not the
    # caller's hypothetical as_of. The scope reason carries the caller's date.
    result["as_of"] = RETRIEVED_ON.isoformat()
    if illustrations is not None:
        result["illustrations"] = illustrations
    return result


def _emergency_deadlines(
    aware_at: datetime,
    closed: set[date],
    *,
    approved: bool,
    in_force: bool,
    emergency_condition: str | None,
    part_6_complied: bool | None,
    investigation_completed_at: datetime | None,
) -> list[dict]:
    del closed  # the 24-hour period is elapsed time
    deadlines = []
    condition_1_end = aware_at.astimezone(LONDON) + timedelta(hours=24)
    use_condition_1 = emergency_condition in (None, "1")
    hard_stop = part_6_complied is not True
    note = (
        "Regulation 5(8)(a): the emergency action period is 24 hours beginning "
        "when Condition 1 applies. Weekends and bank holidays are not skipped."
    )
    if part_6_complied is True:
        note += (
            " The officer has recorded that Part 6 was complied with. Regulation 5(5) "
            "then omits the 24-hour hard stop. The duty is to act as soon as reasonably "
            "practicable. This module does not decide that Part 6 was complied with, "
            "and it does not invent that date."
        )
    if emergency_condition == "2":
        note += " The officer selected Condition 2, so this Condition 1 period is a reference only."
    deadlines.append(
        _deadline(
            "emergency_action_condition_1",
            "Emergency investigation and relevant safety work (Condition 1)",
            "SI 2025/1042 regulation 5(4) and 5(8)(a)",
            at=condition_1_end,
            operative=approved and in_force and use_condition_1 and hard_stop,
            in_force=in_force,
            note=note,
        )
    )
    if investigation_completed_at is not None or emergency_condition == "2":
        if investigation_completed_at is None:
            deadlines.append(
                _deadline(
                    "emergency_action_condition_2",
                    "Relevant safety work (Condition 2)",
                    "SI 2025/1042 regulation 5(8)(b)",
                    operative=False,
                    in_force=in_force,
                    note=(
                        "Condition 2 runs for 24 hours from the time the investigation "
                        "that identifies the relevant safety work is completed. "
                        "That time has not been recorded, so no date is invented."
                    ),
                )
            )
        else:
            condition_2_end = investigation_completed_at.astimezone(LONDON) + timedelta(hours=24)
            selected = emergency_condition == "2"
            note_2 = (
                "Regulation 5(8)(b): 24 hours beginning when the investigation that "
                "identifies the relevant safety work is completed."
            )
            if not selected:
                note_2 += " The officer has not selected Condition 2, so this is a reference."
            if part_6_complied is True:
                note_2 += " Part 6 has been recorded, so the hard stop is disapplied."
            deadlines.append(
                _deadline(
                    "emergency_action_condition_2",
                    "Relevant safety work (Condition 2)",
                    "SI 2025/1042 regulation 5(4)(b) and 5(8)(b)",
                    at=condition_2_end,
                    operative=approved and in_force and selected and hard_stop,
                    in_force=in_force,
                    note=note_2,
                )
            )
    return deadlines


def _investigation_deadlines(
    aware_day: date,
    closed: set[date],
    *,
    approved: bool,
    in_force: bool,
    physical_inspection_requested_on: date | None,
    investigation_kind: str,
) -> list[dict]:
    deadlines = []
    standard_end = working_period_end(aware_day + timedelta(days=1), 10, closed)
    standard_is_the_period = (
        investigation_kind == "standard" and physical_inspection_requested_on is None
    )
    deadlines.append(
        _deadline(
            "standard_investigation",
            "Standard investigation completed",
            "SI 2025/1042 regulation 6(4), standard investigation period",
            on=standard_end,
            operative=approved and in_force and standard_is_the_period,
            in_force=in_force,
            note=(
                "Ten working days beginning on the day after the day the lessor "
                "becomes aware of the issue of concern. Regulation 6 does not apply "
                "where regulation 5 Condition 1 applies, so this period is used for "
                "a significant hazard and not for an emergency."
                + (
                    ""
                    if standard_is_the_period
                    else " A physical inspection request or a renewed investigation is recorded, so this period is a reference."
                )
            ),
        )
    )
    if physical_inspection_requested_on is not None and investigation_kind == "standard":
        extended_end = working_period_end(physical_inspection_requested_on + timedelta(days=1), 10, closed)
        deadlines.append(
            _deadline(
                "extended_investigation",
                "Investigation completed after a physical-inspection request",
                "SI 2025/1042 regulation 6(4), extended investigation period",
                on=extended_end,
                operative=approved and in_force,
                in_force=in_force,
                note=(
                    "Ten working days beginning on the day after the day the lessee "
                    "requests a physical inspection, where that request is made before "
                    "the investigation is completed. The officer recorded the request. "
                    "This module does not decide that the request was made in time."
                ),
            )
        )
    if investigation_kind == "renewed":
        if physical_inspection_requested_on is None:
            deadlines.append(
                _deadline(
                    "renewed_investigation",
                    "Renewed investigation completed",
                    "SI 2025/1042 regulation 7(2)",
                    operative=False,
                    in_force=in_force,
                    note="A renewed investigation needs the date the lessee requested the physical inspection. None was recorded.",
                )
            )
        else:
            renewed_end = working_period_end(physical_inspection_requested_on + timedelta(days=1), 10, closed)
            deadlines.append(
                _deadline(
                    "renewed_investigation",
                    "Renewed investigation completed",
                    "SI 2025/1042 regulation 7(2)",
                    on=renewed_end,
                    operative=approved and in_force,
                    in_force=in_force,
                    note=(
                        "Ten working days beginning on the day after the request, where "
                        "an earlier investigation had no physical inspection and preventative "
                        "work has not been begun. The officer selected this kind of investigation. "
                        "This module does not decide that regulation 7 applies."
                    ),
                )
            )
    return deadlines


def _summary_deadline(completed_on: date, closed: set[date], *, approved: bool, in_force: bool) -> dict:
    end = working_period_end(completed_on + timedelta(days=1), 3, closed)
    return _deadline(
        "written_summary",
        "Written summary given to the lessee",
        "SI 2025/1042 regulation 9(4)",
        on=end,
        operative=approved and in_force,
        in_force=in_force,
        note=(
            "Three working days beginning on the day after the day the relevant "
            "investigation is completed. Regulation 9(1) says the duty does not apply "
            "if the investigation identifies required work and that work is completed "
            "before the end of this period. This module does not decide that the "
            "exception applies. Regulation 10 describes how the document may be given. "
            "This module does not give it."
        ),
    )


def _significant_safety_deadline(
    completed_on: date,
    closed: set[date],
    *,
    approved: bool,
    in_force: bool,
    part_6_complied: bool | None,
) -> dict:
    end = working_period_end(completed_on + timedelta(days=1), 5, closed)
    hard_stop = part_6_complied is not True
    note = (
        "Five working days beginning on the day after the day the relevant "
        "investigation is completed (regulation 11(2)(a))."
    )
    if part_6_complied is True:
        note += (
            " The officer has recorded Part 6 compliance, so regulation 11(2)(b) "
            "applies instead: as soon as reasonably practicable. No substitute day is invented."
        )
    return _deadline(
        "significant_safety_work",
        "Relevant safety work for a significant hazard completed",
        "SI 2025/1042 regulation 11(2)",
        on=end,
        operative=approved and in_force and hard_stop,
        in_force=in_force,
        note=note,
    )


def _preventative_deadlines(
    determined_on: date,
    closed: set[date],
    *,
    approved: bool,
    in_force: bool,
    identified: bool | None,
    further_investigation_completed_on: date | None,
    not_reasonably_practicable_to_begin: bool | None,
) -> list[dict]:
    if further_investigation_completed_on is not None:
        relevant_day = further_investigation_completed_on + timedelta(days=1)
        relevant_note = "The officer recorded a further investigation, so the relevant day is the day after that investigation was completed (regulation 13(6))."
    else:
        relevant_day = determined_on + timedelta(days=1)
        relevant_note = "The relevant day is the day after the investigation that identified the work (regulation 13(6))."
    begin_end = working_period_end(relevant_day, 5, closed)
    long_stop = inclusive_week_period_end(determined_on + timedelta(days=1), 12)
    identified_yes = identified is True
    base = (
        "Calculated because an investigation completion date is recorded. "
        "Operative only if the officer has also recorded that relevant supplementary "
        "preventative work was identified. This module does not decide that it was. "
    )
    deadlines = [
        _deadline(
            "preventative_begin_or_steps",
            "Begin supplementary preventative work, or take steps to begin it",
            "SI 2025/1042 regulation 13(2)",
            on=begin_end,
            operative=approved and in_force and identified_yes,
            in_force=in_force,
            note=base + relevant_note + " Within five working days beginning with the relevant day the lessor must begin the work, or, where that is not reasonably practicable, take steps so that it begins as soon as reasonably practicable and within the 12-week long-stop.",
        )
    ]
    long_stop_operative = (
        approved and in_force and identified_yes and not_reasonably_practicable_to_begin is True
    )
    if not_reasonably_practicable_to_begin is True:
        long_note = (
            "The officer recorded that it is not reasonably practicable to begin "
            "within five working days. The work must still begin before the end of "
            "12 weeks beginning with the day after the investigation that determined "
            "the hazard (regulation 13(3)). The five-working-day duty to take steps remains."
        )
    elif not_reasonably_practicable_to_begin is False:
        long_note = (
            "The officer recorded that it is reasonably practicable to begin within "
            "five working days, so the 12-week long-stop is not the begin deadline."
        )
    else:
        long_note = (
            "The 12-week date is not an alternative the agent can choose. "
            "It applies only where it is not reasonably practicable to begin within "
            "five working days. The officer has not recorded that."
        )
    deadlines.append(
        _deadline(
            "preventative_begin_long_stop",
            "Long-stop to begin supplementary preventative work",
            "SI 2025/1042 regulation 13(3)",
            on=long_stop,
            operative=long_stop_operative,
            in_force=in_force,
            note=base + long_note,
        )
    )
    deadlines.append(
        _deadline(
            "preventative_completion",
            "Supplementary preventative work completed",
            "SI 2025/1042 regulation 13(4)",
            operative=False,
            in_force=in_force,
            note=(
                "The work must be completed within a reasonable period. "
                "The regulations do not fix a day, and this module will not invent one."
            ),
        )
    )
    return deadlines


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value)


def _parse_datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise ValueError("pass a timezone, for example 2026-01-08T09:00:00+00:00")
    return parsed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Calculate Awaab's Law timeframes. Nothing is sent.")
    parser.add_argument("--aware-at", required=True, help="ISO-8601 awareness time with a timezone")
    parser.add_argument("--category", required=True, choices=CATEGORIES)
    parser.add_argument("--hazard-family", required=True, choices=sorted(HAZARD_FAMILIES))
    parser.add_argument("--social-home-in-england", action="store_true")
    parser.add_argument("--approve-category", action="store_true")
    parser.add_argument("--approve-clock", action="store_true")
    parser.add_argument("--investigation-completed-on", default=None)
    parser.add_argument("--investigation-completed-at", default=None)
    parser.add_argument("--physical-inspection-requested-on", default=None)
    parser.add_argument("--investigation-kind", default="standard", choices=("standard", "renewed"))
    parser.add_argument("--emergency-condition", default=None, choices=("1", "2"))
    parser.add_argument("--part-6-complied", action="store_true")
    parser.add_argument("--preventative-identified", action="store_true")
    parser.add_argument("--further-investigation-completed-on", default=None)
    parser.add_argument("--not-reasonably-practicable-to-begin", action="store_true")
    parser.add_argument("--assert-phase-2-in-force", action="store_true")
    parser.add_argument("--as-of", default=None, help="Hypothetical as-of date. Does not change the retrieval warning.")
    parser.add_argument("--extra-closed", action="append", default=[])
    parser.add_argument("--cancel-bank-holiday", action="append", default=[])
    args = parser.parse_args(argv)
    result = calculate_statutory_clock(
        _parse_datetime(args.aware_at),
        args.hazard_family,
        args.category,
        social_home_in_england=args.social_home_in_england,
        officer_approved_category=args.approve_category,
        officer_approved_clock=args.approve_clock,
        investigation_completed_on=_parse_date(args.investigation_completed_on),
        investigation_completed_at=_parse_datetime(args.investigation_completed_at) if args.investigation_completed_at else None,
        physical_inspection_requested_on=_parse_date(args.physical_inspection_requested_on),
        investigation_kind=args.investigation_kind,
        emergency_condition=args.emergency_condition,
        part_6_complied=True if args.part_6_complied else None,
        supplementary_preventative_work_identified=True if args.preventative_identified else None,
        further_investigation_completed_on=_parse_date(args.further_investigation_completed_on),
        not_reasonably_practicable_to_begin=True if args.not_reasonably_practicable_to_begin else None,
        caller_asserts_phase_2_instrument_in_force=args.assert_phase_2_in_force,
        as_of=_parse_date(args.as_of) or RETRIEVED_ON,
        extra_non_working_days=[date.fromisoformat(value) for value in args.extra_closed],
        cancelled_bank_holidays=[date.fromisoformat(value) for value in args.cancel_bank_holiday],
    )
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
