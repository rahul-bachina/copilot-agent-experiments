#!/usr/bin/env python3
"""Draft a work-order completion record. The technician approves every field.

The same pack and the same as-of date produce the same JSON. human_approval
is null until a separate review object approves fields one by one. A later
review can stub-write only those fields. The stub is in the returned JSON.
It does not close the job, raise a charge, order parts, or contact the customer.

Notes, photo descriptions, and addresses are not copied out.
"""

from __future__ import annotations

import argparse
import copy
import importlib
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from instructions import excise_local, local_signals
    from sources import NOT_OPENED, source_view
else:
    from .instructions import excise_local, local_signals
    from .sources import NOT_OPENED, source_view

EXPERIMENT_ID = "exp-47-work-order-completion"
CATALOGUE_ID = "C009"
LABEL = "DRAFT WORK ORDER COMPLETION FOR TECHNICIAN APPROVAL"
AUTONOMY = "A1"
VISIT_ID = "exp-46-field-visit-preparation"
VISIT_CATALOGUE = "C008"
SCANNER_ID = "exp-15-vulnerability-urgency-scanner"
CLOCK_ID = "exp-05-awaabs-law-hazard-triage"
NARRATIVE_CAP = 20_000

WORK_ORDER_ID = re.compile(r"^SYN-WO-\d{4}$")
ASSET_ID = re.compile(r"^SYN-ASSET-\d{4}$")
TECH_ID = re.compile(r"^SYN-TECH-\d{3}$")
PART_ID = re.compile(r"^SYN-PART-\d{4}$")
PHOTO_ID = re.compile(r"^SYN-PHOTO-\d{2,4}$")

SECTORS = frozenset({"housing", "utility", "facilities"})
ORGANISATIONS = frozenset(
    {
        "Calderwell Borough Council",
        "Calderwell Heat Network",
        "Calderwell Facilities",
    }
)

FIELD_IDS = (
    "work_done",
    "parts",
    "follow_up_actions",
    "outstanding_hazards",
    "vulnerability_or_access",
    "attended_on",
    "technician_id",
)

WORK_ACTIONS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("wiped", re.compile(r"\b(?:wiped|cleaned|washed)\b", re.IGNORECASE)),
    ("replaced", re.compile(r"\b(?:replaced|fitted a new|fitted new)\b", re.IGNORECASE)),
    ("isolated", re.compile(r"\b(?:isolated|capped off|made safe)\b", re.IGNORECASE)),
    ("investigated", re.compile(r"\b(?:inspected|investigated|checked)\b", re.IGNORECASE)),
    (
        "no_access",
        re.compile(
            r"\b(?:no access|could not gain access|unable to gain access|refused access)\b",
            re.IGNORECASE,
        ),
    ),
)

FOLLOW_UP: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("return_visit", re.compile(r"\b(?:return visit|come back|not finished|left outstanding)\b", re.IGNORECASE)),
    ("specialist", re.compile(r"\b(?:specialist|gas safe|electrician)\b", re.IGNORECASE)),
    (
        "access_retry",
        re.compile(
            r"\b(?:no access|could not gain access|unable to gain access|refused access)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "parts_for_a_person_to_order",
        re.compile(r"\b(?:please order|order a|order the|parts to order|need to order)\b", re.IGNORECASE),
    ),
    (
        "further_investigation_for_a_person",
        re.compile(r"\bfurther investigation\b", re.IGNORECASE),
    ),
)

STILL = re.compile(r"\b(?:still|remains|remaining|visible|left behind|not gone)\b", re.IGNORECASE)
CLEARED = re.compile(
    r"\b(?:no mould left|no mold left|mould cleared|mold cleared|mould resolved|"
    r"no hazard left|no outstanding hazard|hazard cleared|all clear)\b",
    re.IGNORECASE,
)
COMPLETED_LANGUAGE = re.compile(r"\b(?:job done|completed|all done)\b", re.IGNORECASE)
MOBILITY = re.compile(r"\b(?:wheelchair|walking frame|cannot use stairs)\b", re.IGNORECASE)

HOLD_WORDS = {
    "gas": re.compile(r"\b(?:smell of gas|gas leak)\b", re.IGNORECASE),
    "carbon_monoxide": re.compile(r"\b(?:carbon monoxide|co alarm)\b", re.IGNORECASE),
    "electrical": re.compile(r"\b(?:exposed live|electric shock|sparking)\b", re.IGNORECASE),
    "asbestos": re.compile(r"\b(?:asbestos damaged|damaged asbestos|asbestos disturbed)\b", re.IGNORECASE),
    "structural": re.compile(r"\b(?:ceiling coming down|about to collapse)\b", re.IGNORECASE),
    "sewage": re.compile(r"\b(?:sewage flooding|sewage coming up)\b", re.IGNORECASE),
}

WORK_TOKENS = frozenset(name for name, _pattern in WORK_ACTIONS)
FOLLOW_TOKENS = frozenset(name for name, _pattern in FOLLOW_UP)
HAZARD_TOKENS = frozenset({"none_stated", *HOLD_WORDS, "damp_mould", "working_at_height", "confined_space", "lone_working", "sharps", "dog", "rotten_structure"})

APPROVE = "technician_approve_fields"
WRITE = "technician_stub_write"
REJECT = "reject_draft"
ALLOWED_DECISIONS = frozenset({APPROVE, WRITE, REJECT})
PROHIBITED_DECISIONS = frozenset(
    {
        "close",
        "close_job",
        "close_work_order",
        "raise_charge",
        "raise_a_charge",
        "order_parts",
        "order_the_parts",
        "contact_customer",
        "contact_the_customer",
        "send",
        "send_message",
        "label_vulnerable",
        "clear_hazard",
        "approve_all",
        "approve_all_fields",
        "skip_approval",
        "write_without_approval",
        "mark_safe",
    }
)
PROHIBITED_INPUT_KEYS = frozenset(
    {
        "human_approval",
        "job_closed",
        "charges_raised",
        "parts_ordered",
        "customer_contacted",
        "written",
        "executed",
        "actions_taken",
        "hazard_cleared",
        "officer_approved_category",
        "officer_approved_clock",
        "officer_approved_summary",
        "officer_approved_record",
        "production_system_written",
    }
)

_VISIT = None


class CompletionForbidden(RuntimeError):
    """The assistant has no close, charge, order, or contact path."""


def close_job(*_args, **_kwargs) -> None:
    raise CompletionForbidden("the agent does not close a job")


def raise_charge(*_args, **_kwargs) -> None:
    raise CompletionForbidden("the agent does not raise a charge")


def order_parts(*_args, **_kwargs) -> None:
    raise CompletionForbidden("the agent does not order parts")


def contact_customer(*_args, **_kwargs) -> None:
    raise CompletionForbidden("the agent does not contact the customer")


def send_message(*_args, **_kwargs) -> None:
    raise CompletionForbidden("the agent does not send a message")


def label_person_vulnerable(*_args, **_kwargs) -> None:
    raise CompletionForbidden("the agent does not label a person as vulnerable")


def clear_hazard(*_args, **_kwargs) -> None:
    raise CompletionForbidden("the agent does not clear a hazard")


def _load_visit():
    src = Path(__file__).resolve().parents[2] / "46-field-visit-preparation" / "src"
    if not src.is_dir():
        raise CompletionForbidden(
            "Experiment 46 is required at experiments/46-field-visit-preparation. "
            "This assistant does not carry its own pre-visit brief."
        )
    names = ("hazards", "instructions", "sources", "prepare")
    saved = {name: sys.modules.get(name) for name in names}
    sys.path.insert(0, str(src))
    try:
        for name in names:
            sys.modules.pop(name, None)
        hazards = importlib.import_module("hazards")
        instructions = importlib.import_module("instructions")
        prepare = importlib.import_module("prepare")
    finally:
        sys.path.pop(0)
        for name in names:
            sys.modules.pop(name, None)
            if saved[name] is not None:
                sys.modules[name] = saved[name]
    if prepare.EXPERIMENT_ID != VISIT_ID:
        raise CompletionForbidden("the brief module is not Experiment 46")
    return hazards, instructions, prepare


def _visit():
    global _VISIT
    if _VISIT is None:
        _VISIT = _load_visit()
    return _VISIT


def _load_scan():
    scanner_src = Path(__file__).resolve().parents[2] / "15-vulnerability-urgency-scanner" / "src"
    if not scanner_src.is_dir():
        raise CompletionForbidden(
            "Experiment 15 is required at experiments/15-vulnerability-urgency-scanner."
        )
    inserted = str(scanner_src)
    if inserted not in sys.path:
        sys.path.insert(0, inserted)
    import scan as scan_module

    if scan_module.CALLER != SCANNER_ID:
        raise CompletionForbidden("the scanner module is not Experiment 15")
    return scan_module


def _load_triage():
    clock_src = Path(__file__).resolve().parents[2] / "05-awaabs-law-hazard-triage" / "src"
    if not clock_src.is_dir():
        raise CompletionForbidden(
            "Experiment 05 is required at experiments/05-awaabs-law-hazard-triage."
        )
    inserted = str(clock_src)
    if inserted not in sys.path:
        sys.path.insert(0, inserted)
    import triage as triage_module

    return triage_module


def _parse_as_of(value: date | datetime | str) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value[:10])
        except ValueError as exc:
            raise ValueError("as_of must be a calendar date") from exc
    raise TypeError("as_of must be a date")


def _parse_day(value: object) -> date | None:
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _pattern(value: object, rule: re.Pattern[str]) -> str | None:
    if isinstance(value, str) and rule.fullmatch(value):
        return value
    return None


def _hits(text: str, rules) -> list[str]:
    found: list[str] = []
    for name, pattern in rules:
        if pattern.search(text) and name not in found:
            found.append(name)
    return found


def _sentences(text: str) -> list[str]:
    return [part for part in re.split(r"(?<=[.!?])\s+", text.strip()) if part]


def _strip_prohibited(working: dict) -> list[str]:
    stripped = []
    for key in list(working):
        if key in PROHIBITED_INPUT_KEYS:
            working.pop(key, None)
            stripped.append(key)
    return stripped


def _matching(raw: str, visit_instructions) -> tuple[str, list[dict]]:
    shared = visit_instructions.signals_in(raw)
    local = local_signals(raw)
    seen = {row["signal"] for row in shared}
    signals = list(shared)
    for row in local:
        if row["signal"] not in seen:
            signals.append(row)
            seen.add(row["signal"])
    text = excise_local(visit_instructions.excise_clauses(raw))
    return text, signals


def _flags() -> dict:
    return {
        "job_closed": False,
        "charges_raised": False,
        "parts_ordered": False,
        "customer_contacted": False,
        "hazard_cleared": False,
        "person_labelled_vulnerable": False,
        "production_system_written": False,
        "follow_up_job": False,
        "safety_escalation": False,
        "awaabs_follow_up_for_a_person": False,
    }


def _human_route() -> dict:
    return {
        "offered": True,
        "who": "Field technician, or the organisation's own work-order process",
        "agent_closes_the_job": False,
        "agent_writes_production": False,
        "agent_contacts_the_customer": False,
        "telephone_published": False,
    }


def _regulatory() -> dict:
    return {
        "hswa_duty_met": False,
        "risk_assessment_is_this_record": False,
        "awaabs_covenant_decided": False,
        "defence_decided": False,
        "accuracy_principle_decided": False,
        "written_summary_sent": False,
        "regulation_applied": False,
    }


def _stub() -> dict:
    return {
        "executed": False,
        "store": "in_memory_stub",
        "production_system_written": False,
        "fields_written": [],
        "fields_refused": [],
        "job_closed": False,
        "charges_raised": False,
        "parts_ordered": False,
        "customer_contacted": False,
    }


def _field(field_id: str, proposed, *, missing: bool, blocking: list[str]) -> dict:
    return {
        "field_id": field_id,
        "proposed": proposed,
        "missing": missing,
        "blocking": list(blocking),
        "approved": False,
        "disposition": None,
        "approved_value": None,
        "written": False,
    }


def _empty_awaabs(reason: str) -> dict:
    return {
        "called": False,
        "experiment": CLOCK_ID,
        "reason": reason,
        "officer_approved_category_passed": False,
        "officer_approved_clock_passed": False,
        "officer_approved_summary_passed": False,
        "social_home_in_england_passed": False,
        "payload_claimed_officer_approval": False,
        "proposed_category": None,
        "proposed_family": None,
        "signal": None,
        "any_operative_deadline": False,
        "downgrade_refused": False,
        "quotes_copied": False,
        "regulation_applied": False,
        "written_summary_sent": False,
        "defence_decided": False,
        "error": None,
    }


def _scan(text: str) -> dict:
    view = {
        "called": False,
        "experiment": SCANNER_ID,
        "reason": None,
        "categories": [],
        "phrases_copied": False,
        "person_labelled_vulnerable": False,
        "error": None,
    }
    if not text:
        view["reason"] = "no_visit_text"
        return view
    try:
        scanned = _load_scan().scan(text, synthetic=True, model=None)
    except CompletionForbidden as exc:
        view["reason"] = "scanner_missing"
        view["error"] = type(exc).__name__
        return view
    except Exception:
        view["reason"] = "scanner_error"
        view["error"] = "scanner_error"
        return view
    categories: list[str] = []
    for flag in scanned.get("flags") or []:
        category = flag.get("category")
        if isinstance(category, str) and category not in categories:
            categories.append(category)
    view.update({"called": True, "categories": categories})
    return view


def _awaabs(pack: dict, sector: str | None, text: str, claimed: bool) -> dict:
    if sector != "housing":
        view = _empty_awaabs(
            "Section 10A and SI 2025/1042 were read as applying to a relevant social "
            "housing lease in England. This sector is not housing. The regulations were not applied."
        )
        view["payload_claimed_officer_approval"] = claimed
        return view
    aware = pack.get("aware_at")
    if not isinstance(aware, str):
        view = _empty_awaabs("awareness_time_not_supplied")
        view["payload_claimed_officer_approval"] = claimed
        return view
    try:
        aware_at = datetime.fromisoformat(aware)
    except ValueError:
        view = _empty_awaabs("awareness_time_unparseable")
        view["payload_claimed_officer_approval"] = claimed
        return view
    if aware_at.tzinfo is None:
        view = _empty_awaabs("awareness_time_needs_a_timezone")
        view["payload_claimed_officer_approval"] = claimed
        return view
    social = pack.get("social_housing_in_england") is True
    view = _empty_awaabs(None)
    view["payload_claimed_officer_approval"] = claimed
    view["social_home_in_england_passed"] = social
    try:
        result = _load_triage().triage(
            text,
            aware_at,
            social_home_in_england=social,
            officer_approved_category=False,
            officer_approved_clock=False,
            officer_approved_summary=False,
            officer_approved_record=False,
        )
    except CompletionForbidden:
        view["reason"] = "triage_missing"
        view["error"] = "triage_missing"
        return view
    except Exception:
        view["reason"] = "triage_error"
        view["error"] = "triage_error"
        return view
    proposed = result.get("proposed") or {}
    clock = result.get("statutory_clock") or {}
    signal = proposed.get("signal")
    view.update(
        {
            "called": True,
            "reason": None,
            "proposed_category": proposed.get("category"),
            "proposed_family": proposed.get("hazard_family"),
            "signal": signal if isinstance(signal, str) and len(signal) <= 40 else None,
            "any_operative_deadline": clock.get("operative") is True,
            "downgrade_refused": bool(proposed.get("downgrade_refused")),
        }
    )
    return view


def _known_hold(hold: str, hazards) -> str | None:
    if hold in HOLD_WORDS:
        return hold
    prefix = "record_defect:"
    if hold.startswith(prefix):
        kind = hold[len(prefix) :]
        if kind in hazards.HOLD_RECORD_KINDS and kind in HOLD_WORDS:
            return kind
    return None


def _brief_view(brief: dict) -> dict:
    hazards, _instructions, _prepare = _visit()
    holds = []
    unrecognised = 0
    for item in brief.get("safety_holds") or []:
        if not isinstance(item, str):
            unrecognised += 1
            continue
        kind = _known_hold(item, hazards)
        if kind is None:
            unrecognised += 1
            continue
        if item not in holds:
            holds.append(item)
    highlights = []
    names = {name for name, _pattern in hazards.HIGHLIGHTS}
    for item in brief.get("safety_highlights") or []:
        if isinstance(item, str) and item in names and item not in highlights:
            highlights.append(item)
    access = []
    access_names = {name for name, _pattern in hazards.ACCESS_TEXT}
    for item in brief.get("access_flags") or []:
        if isinstance(item, str) and item in access_names and item not in access:
            access.append(item)
    categories = []
    vulnerability = brief.get("vulnerability") if isinstance(brief.get("vulnerability"), dict) else {}
    for item in vulnerability.get("categories") or []:
        if isinstance(item, str) and item not in categories and len(item) <= 80:
            categories.append(item)
    awaabs = brief.get("awaabs") if isinstance(brief.get("awaabs"), dict) else {}
    stale = brief.get("stale") if isinstance(brief.get("stale"), dict) else {}
    asset = brief.get("asset") if isinstance(brief.get("asset"), dict) else {}
    return {
        "source": None,
        "catalogue_id": VISIT_CATALOGUE if brief.get("catalogue_id") == VISIT_CATALOGUE else None,
        "experiment_id": VISIT_ID if brief.get("experiment_id") == VISIT_ID else None,
        "work_order_id": brief.get("work_order_id") if isinstance(brief.get("work_order_id"), str) else None,
        "asset_id": asset.get("asset_id") if isinstance(asset.get("asset_id"), str) else None,
        "outcome": brief.get("outcome") if isinstance(brief.get("outcome"), str) else None,
        "as_of": brief.get("as_of") if isinstance(brief.get("as_of"), str) else None,
        "safety_holds": holds,
        "safety_highlights": highlights,
        "access_flags": access,
        "vulnerability_categories": categories,
        "awaabs_called": awaabs.get("called") is True,
        "any_operative_deadline": awaabs.get("any_operative_deadline") is True,
        "rules_current": stale.get("rules_current") is True,
        "unrecognised_hold_count": unrecognised,
        "brief_copied_in_full": False,
        "human_approval_on_brief_ignored": True,
        "usable": brief.get("catalogue_id") == VISIT_CATALOGUE and brief.get("experiment_id") == VISIT_ID,
    }


def _pre_visit(pack: dict, as_of: date) -> dict:
    _hazards, _instructions, prepare = _visit()
    supplied = pack.get("pre_visit_brief")
    nested = pack.get("pre_visit_pack")
    if isinstance(supplied, dict):
        view = _brief_view(supplied)
        view["source"] = "supplied_brief"
        if not view["usable"]:
            view["source"] = "unusable_brief"
        return view
    if isinstance(nested, dict):
        working = dict(nested)
        _strip_prohibited(working)
        if working.get("synthetic") is not True:
            view = _brief_view({})
            view["source"] = "refused_not_synthetic"
            view["usable"] = False
            return view
        try:
            brief = prepare.prepare_brief(working, as_of)
        except CompletionForbidden:
            view = _brief_view({})
            view["source"] = "prepare_missing"
            view["usable"] = False
            return view
        except Exception:
            view = _brief_view({})
            view["source"] = "prepare_error"
            view["usable"] = False
            return view
        view = _brief_view(brief)
        view["source"] = "prepared_now" if view["usable"] else "prepare_refused"
        view["usable"] = view["usable"] and brief.get("outcome") != "refused_not_synthetic"
        if brief.get("outcome") == "refused_not_synthetic":
            view["source"] = "refused_not_synthetic"
        return view
    view = _brief_view({})
    view["source"] = "missing"
    view["usable"] = False
    return view


def _parts(visit: dict, matching: str) -> tuple[list[dict], list[str], bool]:
    if "parts_used" not in visit:
        return [], ["parts"], True
    raw = visit.get("parts_used")
    if raw is None:
        return [], ["parts"], True
    if not isinstance(raw, list):
        return [], ["parts"], True
    rows = []
    blocking = []
    for index, item in enumerate(raw, start=1):
        if not isinstance(item, dict):
            if "parts_unreadable" not in blocking:
                blocking.append("parts_unreadable")
            continue
        code = _pattern(item.get("part_code"), PART_ID)
        quantity = item.get("quantity")
        description = item.get("description") if isinstance(item.get("description"), str) else ""
        valid_quantity = isinstance(quantity, int) and not isinstance(quantity, bool) and 1 <= quantity <= 20
        if code is None:
            if "part_code_invalid" not in blocking:
                blocking.append("part_code_invalid")
            continue
        row = {"part_code": code, "quantity": quantity if valid_quantity else None, "mentioned_in_notes": False}
        if not valid_quantity:
            if "parts_quantity_invalid" not in blocking:
                blocking.append("parts_quantity_invalid")
        tokens = [token for token in re.findall(r"[A-Za-z]{4,}", description.lower())]
        if description.strip():
            mentioned = description.lower() in matching.lower() or (
                bool(tokens) and all(token in matching.lower() for token in tokens)
            )
        else:
            mentioned = False
            if "part_description_missing" not in blocking:
                blocking.append("part_description_missing")
        row["mentioned_in_notes"] = mentioned
        if description.strip() and not mentioned and "part_not_mentioned" not in blocking:
            blocking.append("part_not_mentioned")
        rows.append(row)
        del index
    missing = False
    return rows, blocking, missing


def _outstanding(notes: str, photos: str, hazards) -> tuple[list[str], bool]:
    found: list[str] = []

    def add(name: str) -> None:
        if name not in found:
            found.append(name)

    for source in (notes, photos):
        for name in hazards.hits(source, hazards.HOLDS):
            add(name)
    for name in hazards.hits(photos, hazards.HIGHLIGHTS):
        add(name)
    for sentence in _sentences(notes):
        if not STILL.search(sentence):
            continue
        for name in hazards.hits(sentence, hazards.HIGHLIGHTS):
            add(name)
        for name in hazards.hits(sentence, hazards.HOLDS):
            add(name)
    cleared = bool(CLEARED.search(notes) or CLEARED.search(photos))
    return found, cleared


def _hold_addressed(hold: str, text: str, hazards) -> bool:
    kind = _known_hold(hold, hazards)
    if kind is None:
        return False
    return bool(HOLD_WORDS[kind].search(text))


def _problem_ids(text: str, hazards) -> list[str]:
    """Hazard and highlight ids only. Asset words are not a second problem list."""

    found = hazards.hits(text, hazards.HOLDS)
    for name in hazards.hits(text, hazards.HIGHLIGHTS):
        if name not in found:
            found.append(name)
    return found


def _propose_fields(pack: dict, matching_notes: str, matching_photos: str, matching_original: str, brief: dict) -> tuple[list[dict], list[str], list[str]]:
    hazards, _instructions, _prepare = _visit()
    visit = pack.get("visit") if isinstance(pack.get("visit"), dict) else {}
    notes_present = isinstance(visit.get("notes"), str) and bool(visit.get("notes").strip())
    photos_present = isinstance(visit.get("photo_descriptions"), list) and any(
        isinstance(row, dict) and isinstance(row.get("description"), str) and row.get("description").strip()
        for row in visit.get("photo_descriptions") or []
    )
    visit_text = (matching_notes + "\n" + matching_photos).strip()
    inconsistencies: list[str] = []
    gaps: list[str] = []

    actions = _hits(matching_notes, WORK_ACTIONS)
    work_blocking: list[str] = []
    if not notes_present:
        gaps.append("work_done")
        work_missing = True
    elif not actions:
        gaps.append("work_done")
        work_missing = True
    else:
        work_missing = False

    parts, part_blocking, parts_missing = _parts(visit, visit_text)
    if parts_missing:
        gaps.append("parts")

    follow = _hits(matching_notes, FOLLOW_UP) if notes_present else []
    follow_missing = not notes_present
    if follow_missing:
        gaps.append("follow_up_actions")

    outstanding, cleared = _outstanding(matching_notes, matching_photos, hazards)
    hazard_blocking: list[str] = []
    if not notes_present and not photos_present:
        gaps.append("outstanding_hazards")
        hazard_missing = True
        hazard_value: list[str] | None = None
    else:
        hazard_missing = False
        if cleared and outstanding:
            inconsistencies.append("photo_contradicts_notes")
            hazard_blocking.append("photo_contradicts_notes")
            work_blocking.append("photo_contradicts_notes")
        if cleared and not outstanding:
            hazard_value = ["none_stated"]
        else:
            hazard_value = outstanding

    if "no_access" in actions and COMPLETED_LANGUAGE.search(matching_notes):
        inconsistencies.append("completed_language_with_no_access")
        work_blocking.append("completed_language_with_no_access")

    problems = _problem_ids(matching_original, hazards)
    addressed = _problem_ids(visit_text, hazards)
    for problem in problems:
        if problem not in addressed:
            if "original_problem_not_addressed" not in inconsistencies:
                inconsistencies.append("original_problem_not_addressed")
            if "original_problem_not_addressed" not in work_blocking:
                work_blocking.append("original_problem_not_addressed")

    for name in part_blocking:
        if name not in inconsistencies:
            inconsistencies.append(name)

    if brief.get("source") == "missing":
        gaps.append("pre_visit_brief_missing")
    elif not brief.get("usable"):
        gaps.append("pre_visit_brief_unusable")
    else:
        if brief.get("work_order_id") != pack.get("work_order_id") or brief.get("asset_id") != pack.get("asset_id"):
            inconsistencies.append("brief_identity_mismatch")
        for hold in brief.get("safety_holds") or []:
            if not _hold_addressed(hold, visit_text, hazards):
                if "pre_visit_hold_not_addressed" not in inconsistencies:
                    inconsistencies.append("pre_visit_hold_not_addressed")
                if "pre_visit_hold_not_addressed" not in hazard_blocking:
                    hazard_blocking.append("pre_visit_hold_not_addressed")
        if brief.get("unrecognised_hold_count"):
            gaps.append("unrecognised_pre_visit_hold")
            if "pre_visit_hold_not_addressed" not in inconsistencies:
                inconsistencies.append("pre_visit_hold_not_addressed")

    attended = _parse_day(visit.get("attended_on"))
    attended_missing = attended is None
    if attended_missing:
        gaps.append("attended_on")

    technician = _pattern(pack.get("technician_id"), TECH_ID)
    technician_missing = technician is None
    if technician_missing:
        gaps.append("technician_id")

    access = hazards.hits(visit_text, hazards.ACCESS_TEXT)
    if MOBILITY.search(visit_text) and "mobility_aid_mentioned" not in access:
        access.append("mobility_aid_mentioned")
    highlights = hazards.hits(visit_text, hazards.HIGHLIGHTS)
    possible_code = bool(hazards.CODE_SHAPE.search(visit_text))

    fields = [
        _field("work_done", None if work_missing else actions, missing=work_missing, blocking=work_blocking),
        _field("parts", None if parts_missing else parts, missing=parts_missing, blocking=part_blocking),
        _field("follow_up_actions", None if follow_missing else follow, missing=follow_missing, blocking=[]),
        _field(
            "outstanding_hazards",
            None if hazard_missing else hazard_value,
            missing=hazard_missing,
            blocking=hazard_blocking,
        ),
        _field(
            "vulnerability_or_access",
            {
                "categories": [],
                "access_flags": access,
                "safety_highlights": highlights,
                "possible_code": possible_code,
                "absence_is_not_a_clearance": True,
                "person_labelled_vulnerable": False,
            },
            missing=False,
            blocking=[],
        ),
        _field("attended_on", None if attended_missing else attended.isoformat(), missing=attended_missing, blocking=[]),
        _field("technician_id", technician, missing=technician_missing, blocking=[]),
    ]
    return fields, inconsistencies, gaps


def _outcome(gaps: list[str], inconsistencies: list[str], flags: dict, *, rules_current: bool) -> str:
    if not rules_current:
        return "stale_sources"
    mandatory = {
        "work_done",
        "parts",
        "follow_up_actions",
        "outstanding_hazards",
        "vulnerability_or_access",
        "attended_on",
        "technician_id",
        "narrative_too_long",
    }
    if any(gap in mandatory or gap.split(":", 1)[0] in mandatory for gap in gaps):
        return "missing_mandatory"
    if inconsistencies or flags["safety_escalation"] or flags["follow_up_job"] or flags["awaabs_follow_up_for_a_person"]:
        return "needs_review"
    if "pre_visit_brief_missing" in gaps or "pre_visit_brief_unusable" in gaps:
        return "needs_review"
    return "ready_for_field_approval"


def _blocks(record_gaps: list[str], inconsistencies: list[str], flags: dict, *, rules_current: bool) -> list[str]:
    blocks = []
    if not rules_current:
        blocks.append("stale_sources")
    if flags["safety_escalation"]:
        blocks.append("safety_escalation")
    for name in (
        "brief_stale",
        "brief_identity_mismatch",
        "attended_in_the_future",
        "narrative_too_long",
    ):
        if name in inconsistencies or name in record_gaps:
            blocks.append(name)
    if "pre_visit_brief_missing" in record_gaps or "pre_visit_brief_unusable" in record_gaps:
        blocks.append("pre_visit_context")
    return blocks


def _force(record: dict) -> None:
    record["label"] = LABEL
    record["catalogue_id"] = record.get("catalogue_id") or CATALOGUE_ID
    record["experiment_id"] = EXPERIMENT_ID
    record["autonomy"] = AUTONOMY
    record["actions_taken"] = []
    record["executed"] = False
    record["model_called"] = False
    record["network_called"] = False
    record["narrative_echoed"] = False
    flags = record.setdefault("flags", _flags())
    for key in (
        "job_closed",
        "charges_raised",
        "parts_ordered",
        "customer_contacted",
        "hazard_cleared",
        "person_labelled_vulnerable",
        "production_system_written",
    ):
        flags[key] = False
    stub = record.setdefault("stub_write", _stub())
    stub["store"] = "in_memory_stub"
    stub["production_system_written"] = False
    stub["job_closed"] = False
    stub["charges_raised"] = False
    stub["parts_ordered"] = False
    stub["customer_contacted"] = False
    regulatory = record.setdefault("regulatory", _regulatory())
    for key in regulatory:
        regulatory[key] = False
    route = record.setdefault("human_route", _human_route())
    route["offered"] = True
    route["agent_closes_the_job"] = False
    route["agent_writes_production"] = False
    route["agent_contacts_the_customer"] = False
    injection = record.setdefault("prompt_injection", {"detected": False, "signals": [], "followed": False})
    injection["followed"] = False
    if record.get("awaabs"):
        record["awaabs"]["officer_approved_category_passed"] = False
        record["awaabs"]["officer_approved_clock_passed"] = False
        record["awaabs"]["officer_approved_summary_passed"] = False
        record["awaabs"]["quotes_copied"] = False
        record["awaabs"]["regulation_applied"] = False
        record["awaabs"]["written_summary_sent"] = False
        record["awaabs"]["defence_decided"] = False
        if record["awaabs"].get("any_operative_deadline") is True:
            record["awaabs"]["any_operative_deadline"] = False


def _refusal(stripped: list[str]) -> dict:
    record = {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment_id": EXPERIMENT_ID,
        "autonomy": AUTONOMY,
        "outcome": "refused_not_synthetic",
        "as_of": None,
        "work_order_id": None,
        "asset_id": None,
        "sector": None,
        "organisation": None,
        "fields": [],
        "inconsistencies": [],
        "gaps": ["not_synthetic"],
        "blocks": ["not_synthetic"],
        "original_problem_ids": [],
        "pre_visit": {"source": "not_read", "brief_copied_in_full": False, "usable": False},
        "vulnerability": {"called": False, "categories": [], "phrases_copied": False, "person_labelled_vulnerable": False},
        "awaabs": _empty_awaabs("refused_not_synthetic"),
        "prompt_injection": {"detected": False, "signals": [], "followed": False},
        "prohibited_payload_keys": stripped,
        "sources": [],
        "sources_not_opened": NOT_OPENED,
        "stale": {"rules_current": None, "quotes_withheld": True},
        "regulatory": _regulatory(),
        "human_approval": None,
        "human_route": _human_route(),
        "review": None,
        "flags": _flags(),
        "stub_write": _stub(),
        "actions_taken": [],
        "executed": False,
        "model_called": False,
        "network_called": False,
        "narrative_echoed": False,
        "photo_count": 0,
        "possible_code_in_notes": False,
    }
    _force(record)
    return record


def draft_completion(pack: dict, as_of: date | datetime | str) -> dict:
    """Return one draft. No field is approved and nothing is written."""

    if not isinstance(pack, dict):
        raise TypeError("pack must be an object")
    working = copy.deepcopy(pack)
    stripped = _strip_prohibited(working)
    if working.get("synthetic") is not True:
        return _refusal(stripped)

    hazards, visit_instructions, _prepare = _visit()
    as_of_date = _parse_as_of(as_of)
    visit = working.get("visit") if isinstance(working.get("visit"), dict) else {}
    notes = visit.get("notes") if isinstance(visit.get("notes"), str) else ""
    photo_bits = []
    photo_count = 0
    valid_photos = 0
    for row in visit.get("photo_descriptions") or []:
        if not isinstance(row, dict):
            continue
        photo_count += 1
        if _pattern(row.get("photo_id"), PHOTO_ID):
            valid_photos += 1
        if isinstance(row.get("description"), str):
            photo_bits.append(row["description"])
    photos = "\n".join(photo_bits)
    original = working.get("original_job") if isinstance(working.get("original_job"), dict) else {}
    original_text = " ".join(
        part for part in (
            original.get("summary") if isinstance(original.get("summary"), str) else "",
            original.get("requested_work") if isinstance(original.get("requested_work"), str) else "",
        )
        if part
    )
    combined = "\n".join(part for part in (notes, photos, original_text) if part)
    fully_scanned = len(combined) <= NARRATIVE_CAP
    signals: list[dict] = []
    if fully_scanned:
        matching_notes, note_signals = _matching(notes, visit_instructions)
        matching_photos, photo_signals = _matching(photos, visit_instructions)
        matching_original, original_signals = _matching(original_text, visit_instructions)
        seen = set()
        for row in note_signals + photo_signals + original_signals:
            if row["signal"] not in seen:
                signals.append(row)
                seen.add(row["signal"])
    else:
        matching_notes = matching_photos = matching_original = ""

    work_order_id = _pattern(working.get("work_order_id"), WORK_ORDER_ID)
    asset_id = _pattern(working.get("asset_id"), ASSET_ID)
    sector = working.get("sector") if working.get("sector") in SECTORS else None
    organisation = working.get("organisation") if working.get("organisation") in ORGANISATIONS else None
    claimed = any(key in pack for key in ("officer_approved_category", "officer_approved_clock", "officer_approved_summary"))

    gaps: list[str] = []
    if work_order_id is None:
        gaps.append("work_order_id")
    if asset_id is None:
        gaps.append("asset_id")
    if sector is None:
        gaps.append("sector")
    if not isinstance(original.get("summary"), str) or not original.get("summary").strip():
        gaps.append("original_summary")
    if not fully_scanned:
        gaps.append("narrative_too_long")

    brief = _pre_visit(working, as_of_date) if fully_scanned else {
        "source": "not_read",
        "usable": False,
        "brief_copied_in_full": False,
        "safety_holds": [],
        "safety_highlights": [],
        "unrecognised_hold_count": 0,
    }
    if fully_scanned:
        fields, inconsistencies, field_gaps = _propose_fields(
            working, matching_notes, matching_photos, matching_original, brief
        )
    else:
        fields, inconsistencies, field_gaps = [], [], ["narrative_too_long"]
    gaps.extend(field_gaps)

    visit_text = (matching_notes + "\n" + matching_photos).strip()
    vulnerability = _scan(visit_text) if fully_scanned else {
        "called": False,
        "experiment": SCANNER_ID,
        "reason": "narrative_too_long",
        "categories": [],
        "phrases_copied": False,
        "person_labelled_vulnerable": False,
        "error": None,
    }
    for field in fields:
        if field["field_id"] == "vulnerability_or_access" and vulnerability["called"]:
            field["proposed"]["categories"] = vulnerability["categories"]
        elif field["field_id"] == "vulnerability_or_access" and not vulnerability["called"]:
            field["missing"] = True
            if "vulnerability_or_access" not in gaps:
                gaps.append("vulnerability_or_access")

    awaabs = _awaabs(working, sector, visit_text, claimed) if fully_scanned else _empty_awaabs("narrative_too_long")
    if sector == "housing" and fully_scanned and awaabs["called"] is not True:
        gaps.append("awaabs_illustration_not_run")

    attended = _parse_day(visit.get("attended_on")) if fully_scanned else None
    if attended is not None and attended > as_of_date:
        inconsistencies.append("attended_in_the_future")
        for field in fields:
            if field["field_id"] == "attended_on" and "attended_in_the_future" not in field["blocking"]:
                field["blocking"].append("attended_in_the_future")

    if brief.get("usable") and isinstance(brief.get("as_of"), str):
        brief_day = _parse_day(brief["as_of"][:10])
        if brief_day is not None and (as_of_date - brief_day).days > 180:
            inconsistencies.append("brief_stale")

    outstanding_values: list[str] = []
    follow_values: list[str] = []
    for field in fields:
        if field["field_id"] == "outstanding_hazards" and isinstance(field["proposed"], list):
            outstanding_values = field["proposed"]
        if field["field_id"] == "follow_up_actions" and isinstance(field["proposed"], list):
            follow_values = field["proposed"]

    safety = any(name in HOLD_WORDS for name in outstanding_values) or "pre_visit_hold_not_addressed" in inconsistencies
    if awaabs.get("proposed_category") == "emergency":
        safety = True
    follow_job = bool(follow_values) or "original_problem_not_addressed" in inconsistencies or any(
        name not in {"none_stated"} for name in outstanding_values
    )
    damp_outstanding = "damp_mould" in outstanding_values or (
        "damp_mould" in _problem_ids(matching_original, hazards) and "original_problem_not_addressed" in inconsistencies
    )
    awaabs_follow = sector == "housing" and damp_outstanding

    sources, stale = source_view(as_of_date)
    flags = _flags()
    flags["safety_escalation"] = safety
    flags["follow_up_job"] = follow_job
    flags["awaabs_follow_up_for_a_person"] = awaabs_follow
    blocks = _blocks(gaps, inconsistencies, flags, rules_current=stale["rules_current"])
    possible_code = any(
        field["field_id"] == "vulnerability_or_access"
        and isinstance(field["proposed"], dict)
        and field["proposed"].get("possible_code")
        for field in fields
    )

    record = {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment_id": EXPERIMENT_ID,
        "autonomy": AUTONOMY,
        "outcome": _outcome(gaps, inconsistencies, flags, rules_current=stale["rules_current"]),
        "as_of": as_of_date.isoformat(),
        "work_order_id": work_order_id,
        "asset_id": asset_id,
        "sector": sector,
        "organisation": organisation,
        "organisation_recognised": organisation is not None,
        "fields": fields,
        "inconsistencies": inconsistencies,
        "gaps": gaps,
        "blocks": blocks,
        "original_problem_ids": _problem_ids(matching_original, hazards) if fully_scanned else [],
        "pre_visit": {
            "source": brief.get("source"),
            "usable": bool(brief.get("usable")),
            "work_order_id": brief.get("work_order_id"),
            "asset_id": brief.get("asset_id"),
            "outcome": brief.get("outcome"),
            "as_of": brief.get("as_of"),
            "safety_holds": brief.get("safety_holds") or [],
            "safety_highlights": brief.get("safety_highlights") or [],
            "access_flags": brief.get("access_flags") or [],
            "vulnerability_categories": brief.get("vulnerability_categories") or [],
            "awaabs_called": brief.get("awaabs_called") is True,
            "any_operative_deadline": False,
            "unrecognised_hold_count": brief.get("unrecognised_hold_count") or 0,
            "brief_copied_in_full": False,
            "human_approval_on_brief_ignored": True,
        },
        "vulnerability": vulnerability,
        "awaabs": awaabs,
        "prompt_injection": {"detected": bool(signals), "signals": signals, "followed": False},
        "prohibited_payload_keys": stripped,
        "sources": sources,
        "sources_not_opened": NOT_OPENED,
        "stale": stale,
        "regulatory": _regulatory(),
        "human_approval": None,
        "human_route": _human_route(),
        "review": None,
        "flags": flags,
        "stub_write": _stub(),
        "actions_taken": [],
        "executed": False,
        "model_called": False,
        "network_called": False,
        "narrative_echoed": False,
        "photo_count": photo_count,
        "valid_photo_ids": valid_photos,
        "possible_code_in_notes": possible_code,
        "approvals": [],
        "draft_rejected": False,
    }
    _force(record)
    return record


def _approval_view(record: dict) -> dict | None:
    approved = [row["field_id"] for row in record.get("approvals") or []]
    written = [field["field_id"] for field in record.get("fields") or [] if field.get("written")]
    if not approved and not written:
        return None
    actor = (record.get("approvals") or [{}])[-1]
    return {
        "approver_role": "Field technician",
        "approver_id": actor.get("actor_id"),
        "approved_fields": approved,
        "written_fields": written,
        "blanket_approval": False,
        "each_field_approved_separately": True,
    }


def _ack_missing(record: dict, review: dict) -> str | None:
    blocks = set(record.get("blocks") or [])
    if "stale_sources" in blocks and review.get("stale_sources_acknowledged") is not True:
        return "stale_sources_not_acknowledged"
    if "safety_escalation" in blocks and review.get("safety_escalation_seen") is not True:
        return "safety_escalation_not_seen"
    if "brief_stale" in blocks and review.get("brief_stale_acknowledged") is not True:
        return "brief_stale_not_acknowledged"
    if "pre_visit_context" in blocks and review.get("pre_visit_missing_acknowledged") is not True:
        return "pre_visit_context_not_acknowledged"
    if "brief_identity_mismatch" in blocks and review.get("inconsistency_acknowledged") is not True:
        return "inconsistency_not_acknowledged"
    if "attended_in_the_future" in blocks and review.get("inconsistency_acknowledged") is not True:
        return "inconsistency_not_acknowledged"
    if "narrative_too_long" in blocks and review.get("inconsistency_acknowledged") is not True:
        return "inconsistency_not_acknowledged"
    return None


def _supplied_value(field_id: str, supplied, as_of: date) -> tuple[object, str | None]:
    if field_id == "work_done":
        if not isinstance(supplied, list) or not supplied or any(item not in WORK_TOKENS for item in supplied):
            return None, "supplied_value_not_in_catalogue"
        return list(dict.fromkeys(supplied)), None
    if field_id == "follow_up_actions":
        if not isinstance(supplied, list) or any(item not in FOLLOW_TOKENS for item in supplied):
            return None, "supplied_value_not_in_catalogue"
        return list(dict.fromkeys(supplied)), None
    if field_id == "outstanding_hazards":
        if not isinstance(supplied, list) or not supplied or any(item not in HAZARD_TOKENS for item in supplied):
            return None, "supplied_value_not_in_catalogue"
        return list(dict.fromkeys(supplied)), None
    if field_id == "parts":
        if not isinstance(supplied, list):
            return None, "supplied_value_not_in_catalogue"
        rows = []
        for item in supplied:
            if not isinstance(item, dict):
                return None, "supplied_value_not_in_catalogue"
            code = _pattern(item.get("part_code"), PART_ID)
            quantity = item.get("quantity")
            if code is None or not isinstance(quantity, int) or isinstance(quantity, bool) or not 1 <= quantity <= 20:
                return None, "supplied_value_not_in_catalogue"
            rows.append({"part_code": code, "quantity": quantity, "mentioned_in_notes": False})
        return rows, None
    if field_id == "attended_on":
        day = _parse_day(supplied)
        if day is None or day > as_of:
            return None, "supplied_value_not_in_catalogue"
        return day.isoformat(), None
    if field_id == "technician_id":
        tech = _pattern(supplied, TECH_ID)
        if tech is None:
            return None, "supplied_value_not_in_catalogue"
        return tech, None
    if field_id == "vulnerability_or_access":
        return None, "supplied_value_not_in_catalogue"
    return None, "supplied_value_not_in_catalogue"


def _same(left, right) -> bool:
    return json.dumps(left, sort_keys=True) == json.dumps(right, sort_keys=True)


def record_review(record: dict, review: dict) -> dict:
    """Approve fields, or stub-write fields that were approved earlier."""

    if not isinstance(record, dict) or not isinstance(review, dict):
        raise TypeError("record and review must be objects")
    updated = copy.deepcopy(record)
    decision = review.get("decision")
    updated["review"] = {
        "decision": decision if isinstance(decision, str) else None,
        "accepted": False,
        "refused": True,
        "reason": None,
        "executed": False,
        "fields_touched": [],
    }
    if updated.get("experiment_id") != EXPERIMENT_ID or updated.get("outcome") == "refused_not_synthetic":
        updated["review"]["reason"] = "not_a_completion_record"
        _force(updated)
        return updated
    if decision in PROHIBITED_DECISIONS or decision not in ALLOWED_DECISIONS:
        updated["review"]["reason"] = "prohibited_decision"
        _force(updated)
        return updated
    if review.get("actor_role") != "Field technician":
        updated["review"]["reason"] = "actor_role"
        _force(updated)
        return updated
    actor_id = _pattern(review.get("actor_id"), TECH_ID)
    if actor_id is None:
        updated["review"]["reason"] = "actor_id"
        _force(updated)
        return updated
    if review.get("work_order_id") != updated.get("work_order_id"):
        updated["review"]["reason"] = "work_order_mismatch"
        _force(updated)
        return updated
    if updated.get("draft_rejected") and decision == WRITE:
        updated["review"]["reason"] = "draft_rejected"
        _force(updated)
        return updated

    if decision == REJECT:
        if any(field.get("written") for field in updated.get("fields") or []):
            updated["review"]["reason"] = "already_written_stub_not_reversed"
            _force(updated)
            return updated
        updated["draft_rejected"] = True
        updated["review"]["accepted"] = True
        updated["review"]["refused"] = False
        updated["review"]["reason"] = "draft_rejected"
        updated["human_approval"] = _approval_view(updated)
        _force(updated)
        return updated

    ack_reason = _ack_missing(updated, review)
    requested = review.get("fields")
    if not isinstance(requested, list) or not requested:
        updated["review"]["reason"] = "no_fields"
        _force(updated)
        return updated

    by_id = {field["field_id"]: field for field in updated.get("fields") or []}
    as_of = _parse_as_of(updated.get("as_of"))
    touched = []
    refused = []

    if decision == APPROVE:
        if ack_reason:
            updated["review"]["reason"] = ack_reason
            _force(updated)
            return updated
        for item in requested:
            if not isinstance(item, dict) or item.get("approved") is not True:
                refused.append({"field_id": None, "reason": "field_not_explicitly_approved"})
                continue
            field_id = item.get("field_id")
            field = by_id.get(field_id)
            if field is None:
                refused.append({"field_id": field_id if isinstance(field_id, str) else None, "reason": "unknown_field"})
                continue
            if field_id in {row["field_id"] for row in updated.get("approvals") or []}:
                refused.append({"field_id": field_id, "reason": "already_approved"})
                continue
            if field["blocking"] and review.get("inconsistency_acknowledged") is not True and item.get("inconsistency_acknowledged") is not True:
                refused.append({"field_id": field_id, "reason": "inconsistency_not_acknowledged"})
                continue
            disposition = item.get("disposition") or "accept_proposed"
            if disposition not in {"accept_proposed", "withhold"}:
                refused.append({"field_id": field_id, "reason": "disposition"})
                continue
            if disposition == "withhold":
                value = None
            elif field["missing"]:
                if "supplied" not in item:
                    refused.append({"field_id": field_id, "reason": "missing_value"})
                    continue
                value, reason = _supplied_value(field_id, item.get("supplied"), as_of)
                if reason:
                    refused.append({"field_id": field_id, "reason": reason})
                    continue
            else:
                if "supplied" in item:
                    refused.append({"field_id": field_id, "reason": "proposed_value_is_fixed"})
                    continue
                value = copy.deepcopy(field["proposed"])
            field["approved"] = True
            field["disposition"] = disposition
            field["approved_value"] = value
            updated.setdefault("approvals", []).append(
                {
                    "field_id": field_id,
                    "actor_id": actor_id,
                    "disposition": disposition,
                    "inconsistency_still_open": bool(field["blocking"]),
                }
            )
            touched.append(field_id)
        updated["review"]["fields_touched"] = touched
        updated["review"]["fields_refused"] = refused
        if touched:
            updated["review"]["accepted"] = True
            updated["review"]["refused"] = False
            updated["review"]["reason"] = "fields_approved"
        else:
            updated["review"]["reason"] = refused[0]["reason"] if refused else "no_fields"
        updated["human_approval"] = _approval_view(updated)
        _force(updated)
        return updated

    # Stub write. A field must already have been approved on an earlier review.
    if ack_reason:
        updated["review"]["reason"] = ack_reason
        _force(updated)
        return updated
    if updated.get("draft_rejected"):
        updated["review"]["reason"] = "draft_rejected"
        _force(updated)
        return updated
    approved_ids = {row["field_id"]: row for row in updated.get("approvals") or []}
    written = []
    for item in requested:
        if not isinstance(item, dict) or item.get("approved") is not True:
            refused.append({"field_id": None, "reason": "field_not_explicitly_approved"})
            continue
        field_id = item.get("field_id")
        field = by_id.get(field_id)
        if field is None or field_id not in approved_ids:
            refused.append({
                "field_id": field_id if isinstance(field_id, str) else None,
                "reason": "approval_required_before_write",
            })
            continue
        if field.get("written"):
            refused.append({"field_id": field_id, "reason": "already_written"})
            continue
        if field.get("disposition") == "withhold":
            refused.append({"field_id": field_id, "reason": "withheld"})
            continue
        field["written"] = True
        written.append(field_id)
    updated["stub_write"]["fields_written"] = [
        field_id for field_id in FIELD_IDS if by_id.get(field_id, {}).get("written")
    ]
    updated["stub_write"]["fields_refused"] = refused
    updated["stub_write"]["executed"] = bool(written)
    updated["review"]["fields_touched"] = written
    updated["review"]["fields_refused"] = refused
    if written:
        updated["review"]["accepted"] = True
        updated["review"]["refused"] = False
        updated["review"]["reason"] = "stub_fields_written"
    else:
        updated["review"]["reason"] = refused[0]["reason"] if refused else "no_fields"
    updated["human_approval"] = _approval_view(updated)
    _force(updated)
    return updated


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Draft a synthetic work-order completion record. Does not close the job."
    )
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--review", type=Path)
    args = parser.parse_args(argv)
    try:
        pack = json.loads(args.input.read_text(encoding="utf-8"))
        record = draft_completion(pack, args.as_of)
        if args.review:
            review = json.loads(args.review.read_text(encoding="utf-8"))
            if isinstance(review, list):
                for item in review:
                    record = record_review(record, item)
            else:
                record = record_review(record, review)
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return 2
    json.dump(record, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
