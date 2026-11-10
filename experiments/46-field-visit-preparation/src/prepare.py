#!/usr/bin/env python3
"""Assemble one pre-visit brief. The technician confirms asset and safety context.

The same pack and the same as-of date produce the same JSON. human_approval
is null until a separate review object is supplied. Confirmation does not
schedule, dispatch, or close the work order, and it does not authorise entry
or clear a hold.

Narrative text is not copied out. A code-shaped phrase is not copied out.
"""

from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from hazards import (
        ACCESS_TEXT,
        CODE_SHAPE,
        HIGHLIGHTS,
        HOLD_RECORD_KINDS,
        HOLDS,
        RECORD_KINDS,
        RECORD_STATUSES,
        description_ids,
        hits,
    )
    from instructions import excise_clauses, signals_in
    from sources import NOT_OPENED, RETRIEVED_ON, SOURCES, STALE_AFTER_DAYS
else:
    from .hazards import (
        ACCESS_TEXT,
        CODE_SHAPE,
        HIGHLIGHTS,
        HOLD_RECORD_KINDS,
        HOLDS,
        RECORD_KINDS,
        RECORD_STATUSES,
        description_ids,
        hits,
    )
    from .instructions import excise_clauses, signals_in
    from .sources import NOT_OPENED, RETRIEVED_ON, SOURCES, STALE_AFTER_DAYS

EXPERIMENT_ID = "exp-46-field-visit-preparation"
CATALOGUE_ID = "C008"
LABEL = "DRAFT FIELD BRIEF FOR TECHNICIAN CONFIRMATION"
AUTONOMY = "A0"
SCANNER_ID = "exp-15-vulnerability-urgency-scanner"
INTAKE_ID = "exp-12-document-intake"
CLOCK_ID = "exp-05-awaabs-law-hazard-triage"
NARRATIVE_CAP = 20_000

WORK_ORDER_ID = re.compile(r"^SYN-WO-\d{4}$")
ASSET_ID = re.compile(r"^SYN-ASSET-\d{4}$")
LOCATION_ID = re.compile(r"^SYN-LOC-\d{4}$")
SAFE_ID = re.compile(r"^SYN-SAFE-\d{2,4}$")
TECH_ID = re.compile(r"^SYN-TECH-\d{3}$")
SUP_ID = re.compile(r"^SYN-SUP-\d{3}$")

SECTORS = frozenset({"housing", "utility", "facilities"})
PRIORITIES = frozenset({"routine", "urgent", "emergency"})
STATUSES = frozenset({"open", "assigned", "closed"})
ENTRY_RULES = frozenset(
    {"tenant_present", "concierge", "appointment_only", "key_safe_not_stored", "unknown"}
)
ORGANISATIONS = frozenset(
    {
        "Calderwell Borough Council",
        "Calderwell Heat Network",
        "Calderwell Facilities",
    }
)

CONFIRM = "technician_confirm_asset_and_safety"
SUPERVISOR = "supervisor_acknowledge_hold"
REJECT = "reject_brief"
ALLOWED_DECISIONS = frozenset({CONFIRM, SUPERVISOR, REJECT})
PROHIBITED_DECISIONS = frozenset(
    {
        "schedule",
        "schedule_visit",
        "dispatch",
        "dispatch_technician",
        "close",
        "close_work_order",
        "update_work_order",
        "send",
        "send_message",
        "clear_hold",
        "clear_hazard",
        "authorise_entry",
        "authorize_entry",
        "label_vulnerable",
        "approve_hazard_category",
        "mark_safe",
    }
)
PROHIBITED_INPUT_KEYS = frozenset(
    {
        "human_approval",
        "scheduled",
        "dispatched",
        "closed",
        "context_confirmed",
        "entry_authorised",
        "hold_cleared",
        "hazard_cleared",
        "executed",
        "actions_taken",
        "safe_to_proceed",
        "officer_approved_category",
        "officer_approved_clock",
        "officer_approved_summary",
    }
)

BLOCKING = frozenset(
    {
        "work_order_id",
        "sector",
        "asset_id",
        "location",
        "summary",
        "no_safety_record",
        "narrative_too_long",
    }
)


class VisitForbidden(RuntimeError):
    """The brief has no schedule, dispatch, close, or entry path."""


class NotSynthetic(ValueError):
    """Raised only by the direct refusal helpers. prepare_brief returns a refusal."""


def schedule_visit(*_args, **_kwargs) -> None:
    raise VisitForbidden("the agent does not schedule a visit")


def dispatch_technician(*_args, **_kwargs) -> None:
    raise VisitForbidden("the agent does not dispatch a technician")


def close_work_order(*_args, **_kwargs) -> None:
    raise VisitForbidden("the agent does not close a work order")


def update_work_order(*_args, **_kwargs) -> None:
    raise VisitForbidden("the agent does not update a work order")


def send_message(*_args, **_kwargs) -> None:
    raise VisitForbidden("the agent does not send a message")


def authorise_entry(*_args, **_kwargs) -> None:
    raise VisitForbidden("the agent does not authorise entry")


def clear_safety_hold(*_args, **_kwargs) -> None:
    raise VisitForbidden("the agent does not clear a safety hold")


def label_person_vulnerable(*_args, **_kwargs) -> None:
    raise VisitForbidden("the agent does not label a person as vulnerable")


def _load_scan():
    scanner_src = (
        Path(__file__).resolve().parents[2] / "15-vulnerability-urgency-scanner" / "src"
    )
    if not scanner_src.is_dir():
        raise VisitForbidden(
            "Experiment 15 is required at experiments/15-vulnerability-urgency-scanner. "
            "This brief does not carry its own vulnerability list."
        )
    inserted = str(scanner_src)
    if inserted not in sys.path:
        sys.path.insert(0, inserted)
    import scan as scan_module

    if scan_module.CALLER != SCANNER_ID:
        raise VisitForbidden("the scanner module is not Experiment 15")
    return scan_module


def _load_intake():
    intake_src = Path(__file__).resolve().parents[2] / "12-document-intake" / "src"
    if not intake_src.is_dir():
        raise VisitForbidden(
            "Experiment 12 is required at experiments/12-document-intake. "
            "This brief does not carry its own document inventory."
        )
    inserted = str(intake_src)
    if inserted not in sys.path:
        sys.path.insert(0, inserted)
    import intake as intake_module

    if intake_module.EXPERIMENT_ID != INTAKE_ID:
        raise VisitForbidden("the intake module is not Experiment 12")
    return intake_module


def _load_triage():
    clock_src = Path(__file__).resolve().parents[2] / "05-awaabs-law-hazard-triage" / "src"
    if not clock_src.is_dir():
        raise VisitForbidden(
            "Experiment 05 is required at experiments/05-awaabs-law-hazard-triage. "
            "This brief does not carry its own statutory clock."
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
            return date.fromisoformat(value)
        except ValueError as exc:
            raise ValueError("as_of must be a calendar date") from exc
    raise TypeError("as_of must be a date")


def _parse_day(value: object) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        try:
            return date.fromisoformat(value)
        except ValueError:
            return None
    return None


def _age(as_of: date, raw: object) -> dict:
    if raw in (None, ""):
        return {"status": "missing", "age_days": None, "stale": True, "current": False}
    parsed = _parse_day(raw)
    if parsed is None:
        return {"status": "unparseable", "age_days": None, "stale": True, "current": False}
    age_days = (as_of - parsed).days
    if age_days < 0:
        return {"status": "future", "age_days": age_days, "stale": True, "current": False}
    stale = age_days > STALE_AFTER_DAYS
    return {
        "status": "stale" if stale else "current",
        "age_days": age_days,
        "stale": stale,
        "current": not stale,
    }


def _pattern(value: object, pattern: re.Pattern[str]) -> str | None:
    if isinstance(value, str) and pattern.fullmatch(value):
        return value
    return None


def _strip_prohibited(mapping: dict) -> list[str]:
    found = []
    for key in list(mapping):
        if key in PROHIBITED_INPUT_KEYS:
            found.append(key)
            del mapping[key]
    return found


def _free_text(pack: dict) -> str:
    parts: list[str] = []

    def add(value: object) -> None:
        if isinstance(value, str) and value.strip():
            parts.append(value)

    work = pack.get("work_order")
    if isinstance(work, dict):
        add(work.get("summary"))
    asset = pack.get("asset")
    if isinstance(asset, dict):
        add(asset.get("description"))
    access = pack.get("site_access")
    if isinstance(access, dict):
        add(access.get("notes"))
    records = pack.get("safety_records")
    if isinstance(records, list):
        for row in records:
            if isinstance(row, dict):
                add(row.get("note"))
    documents = pack.get("documents")
    if isinstance(documents, list):
        for row in documents:
            if isinstance(row, dict):
                add(row.get("content"))
                add(row.get("text"))
    return "\n".join(parts)


def _flags() -> dict:
    return {
        "scheduled": False,
        "dispatched": False,
        "closed": False,
        "work_order_updated": False,
        "entry_authorised": False,
        "hold_cleared": False,
        "hazard_cleared": False,
        "context_confirmed": False,
        "person_labelled_vulnerable": False,
        "code_copied": False,
        "hazard_category_approved": False,
    }


def _force(brief: dict) -> None:
    flags = brief["flags"]
    flags["scheduled"] = False
    flags["dispatched"] = False
    flags["closed"] = False
    flags["work_order_updated"] = False
    flags["entry_authorised"] = False
    flags["hold_cleared"] = False
    flags["hazard_cleared"] = False
    flags["person_labelled_vulnerable"] = False
    flags["code_copied"] = False
    flags["hazard_category_approved"] = False
    brief["actions_taken"] = []
    brief["executed"] = False
    brief["narrative_echoed"] = False
    brief["model_called"] = False
    brief["network_called"] = False
    brief["regulatory"]["hswa_duty_met"] = False
    brief["regulatory"]["risk_assessment_is_this_brief"] = False
    brief["regulatory"]["awaabs_covenant_decided"] = False
    brief["regulatory"]["article_6_basis_asserted"] = False
    brief["regulatory"]["defence_made_out"] = False
    awaabs = brief.get("awaabs") or {}
    awaabs["applied_as_a_visit_clearance"] = False
    awaabs["defence_decided"] = False
    awaabs["officer_approved_category_passed"] = False
    awaabs["officer_approved_clock_passed"] = False
    awaabs["officer_approved_summary_passed"] = False
    awaabs["quotes_copied"] = False
    vulnerability = brief.get("vulnerability") or {}
    vulnerability["person_labelled_vulnerable"] = False
    vulnerability["phrases_copied"] = False
    documents = brief.get("document_intake") or {}
    documents["files_confirmed"] = False
    documents["purpose_confirmed"] = False
    documents["content_copied"] = False
    injection = brief.get("prompt_injection") or {}
    injection["followed"] = False
    if brief.get("human_approval"):
        brief["human_approval"]["executed"] = False
        brief["human_approval"]["scheduled"] = False
        brief["human_approval"]["dispatched"] = False
        brief["human_approval"]["closed"] = False
        brief["human_approval"]["entry_authorised"] = False
        brief["human_approval"]["hold_cleared"] = False


def _human_route() -> dict:
    return {
        "offered": True,
        "phone_published": False,
        "agent_dispatches": False,
        "note": (
            "A supervisor, or the organisation's own scheduler, can take this visit. "
            "This starter does not publish a telephone number and does not dispatch."
        ),
    }


def _source_view(as_of: date) -> tuple[list[dict], dict]:
    age_days = (as_of - RETRIEVED_ON).days
    rules_current = 0 <= age_days <= STALE_AFTER_DAYS
    rows = []
    for source in SOURCES.values():
        rows.append(
            {
                "id": source["id"],
                "title": source["title"],
                "url": source["url"],
                "retrieved": source["retrieved"],
                "banner": source["banner"],
                "stale": not rules_current,
                "quoted": rules_current,
                "taken": source["taken"] if rules_current else None,
            }
        )
    stale = {
        "rules_current": rules_current,
        "window_days": STALE_AFTER_DAYS,
        "retrieved_on": RETRIEVED_ON.isoformat(),
        "age_days": age_days,
        "equal_to_window_is_current": True,
    }
    return rows, stale


def _vulnerability_stub(reason: str) -> dict:
    return {
        "called": False,
        "experiment": SCANNER_ID,
        "reason": reason,
        "categories": [],
        "finding_count": None,
        "input_sha256": None,
        "phrases_copied": False,
        "person_labelled_vulnerable": False,
        "error": None,
    }


def _documents_stub(reason: str) -> dict:
    return {
        "called": False,
        "experiment": INTAKE_ID,
        "reason": reason,
        "file_count": 0,
        "read_statuses": [],
        "date_statuses": [],
        "suggested_classes": [],
        "injection_detected": False,
        "files_confirmed": False,
        "purpose_confirmed": False,
        "content_copied": False,
        "catalogue_stale": None,
        "error": None,
    }


def _awaabs_stub(reason: str) -> dict:
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
        "applied_as_a_visit_clearance": False,
        "defence_decided": False,
        "quotes_copied": False,
        "error": None,
    }


def _scan(text: str) -> dict:
    view = _vulnerability_stub(None)
    if not text:
        view["reason"] = "no_narrative"
        return view
    try:
        scanned = _load_scan().scan(text, synthetic=True, model=None)
    except VisitForbidden as exc:
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
        if category and category not in categories:
            categories.append(category)
    gateway = scanned.get("pii_gateway") or {}
    view.update(
        {
            "called": True,
            "reason": None,
            "categories": categories,
            "finding_count": gateway.get("finding_count"),
            "input_sha256": gateway.get("input_sha256"),
        }
    )
    return view


def _documents(pack: dict, as_of: date, work_order_id: str | None) -> dict:
    documents = pack.get("documents")
    if not isinstance(documents, list) or not documents:
        return _documents_stub("no_documents")
    files = []
    for row in documents:
        if not isinstance(row, dict):
            continue
        copied = {
            "file_id": row.get("file_id"),
            "filename": row.get("filename"),
            "media_type": row.get("media_type", "text/plain"),
            "document_date": row.get("document_date"),
            "content": row.get("content") if isinstance(row.get("content"), str) else row.get("text") or "",
        }
        if isinstance(row.get("sha256"), str):
            copied["sha256"] = row["sha256"]
        files.append(copied)
    batch = {
        "synthetic": True,
        "batch_id": work_order_id or "unspecified",
        "requested_purpose": "general_records",
        "files": files,
    }
    view = _documents_stub(None)
    try:
        draft = _load_intake().intake(batch, as_of=as_of)
    except VisitForbidden:
        view["reason"] = "intake_missing"
        view["error"] = "intake_missing"
        return view
    except Exception:
        view["reason"] = "intake_error"
        view["error"] = "intake_error"
        return view
    rows = draft.get("files") or []
    view.update(
        {
            "called": True,
            "reason": None,
            "file_count": len(rows),
            "read_statuses": [row.get("read_status") for row in rows],
            "date_statuses": [row.get("date_status") for row in rows],
            "suggested_classes": [row.get("suggested_class") for row in rows],
            "injection_detected": bool((draft.get("prompt_injection") or {}).get("detected")),
            "catalogue_stale": draft.get("catalogue_stale"),
        }
    )
    return view


def _awaabs(pack: dict, sector: str | None, claimed: bool) -> dict:
    if sector != "housing":
        view = _awaabs_stub(
            "Section 10A and SI 2025/1042 were read as applying to a relevant social "
            "housing lease of a dwelling in England. This sector is not housing. "
            "The regulations were not applied."
        )
        view["payload_claimed_officer_approval"] = claimed
        return view
    aware = pack.get("aware_at")
    if not isinstance(aware, str):
        view = _awaabs_stub("awareness_time_not_supplied")
        view["payload_claimed_officer_approval"] = claimed
        return view
    try:
        aware_at = datetime.fromisoformat(aware)
    except ValueError:
        view = _awaabs_stub("awareness_time_unparseable")
        view["payload_claimed_officer_approval"] = claimed
        return view
    if aware_at.tzinfo is None:
        view = _awaabs_stub("awareness_time_needs_a_timezone")
        view["payload_claimed_officer_approval"] = claimed
        return view
    social = pack.get("social_housing_in_england") is True
    narrative = _free_text(pack)
    view = _awaabs_stub(None)
    view["payload_claimed_officer_approval"] = claimed
    view["social_home_in_england_passed"] = social
    try:
        result = _load_triage().triage(
            narrative,
            aware_at,
            social_home_in_england=social,
            officer_approved_category=False,
            officer_approved_clock=False,
            officer_approved_summary=False,
            officer_approved_record=False,
        )
    except VisitForbidden:
        view["reason"] = "triage_missing"
        view["error"] = "triage_missing"
        return view
    except Exception:
        view["reason"] = "triage_error"
        view["error"] = "triage_error"
        return view
    proposed = result.get("proposed") or {}
    clock = result.get("statutory_clock") or {}
    view.update(
        {
            "called": True,
            "reason": None,
            "proposed_category": proposed.get("category"),
            "proposed_family": proposed.get("hazard_family"),
            "signal": proposed.get("signal"),
            "any_operative_deadline": clock.get("operative") is True,
            "downgrade_refused": bool(proposed.get("downgrade_refused")),
        }
    )
    return view


def _safety_rows(pack: dict, as_of: date) -> tuple[list[dict], list[str], list[str]]:
    raw_rows = pack.get("safety_records")
    gaps: list[str] = []
    holds: list[str] = []
    if not isinstance(raw_rows, list) or not raw_rows:
        gaps.append("no_safety_record")
        return [], gaps, holds
    rows = []
    for index, raw in enumerate(raw_rows, start=1):
        if not isinstance(raw, dict):
            gaps.append(f"safety_record_unreadable:{index}")
            continue
        record_id = _pattern(raw.get("record_id"), SAFE_ID)
        kind = raw.get("kind") if raw.get("kind") in RECORD_KINDS else None
        status = raw.get("status") if raw.get("status") in RECORD_STATUSES else None
        age = _age(as_of, raw.get("as_of"))
        if record_id is None:
            gaps.append(f"safety_record_id:{index}")
        if kind is None:
            gaps.append(f"safety_record_kind:{record_id or index}")
        if status is None:
            gaps.append(f"safety_record_status:{record_id or index}")
        if age["status"] != "current":
            gaps.append(f"safety_record_{age['status']}:{record_id or index}")
        if status == "survey_missing":
            gaps.append(f"survey_missing:{kind or index}")
        if status == "expired":
            gaps.append(f"safety_record_expired_status:{kind or index}")
        if status == "defect_open" and kind in HOLD_RECORD_KINDS:
            hold = f"record_defect:{kind}"
            if hold not in holds:
                holds.append(hold)
        elif status == "defect_open":
            gaps.append(f"defect_open:{kind or index}")
        rows.append(
            {
                "record_id": record_id,
                "kind": kind,
                "status": status,
                "date_status": age["status"],
                "age_days": age["age_days"],
                "note_copied": False,
            }
        )
    return rows, gaps, holds


def _access(pack: dict, as_of: date, matching_text: str) -> tuple[dict, list[str], list[str]]:
    gaps: list[str] = []
    flags = hits(matching_text, ACCESS_TEXT)
    raw = pack.get("site_access")
    if not isinstance(raw, dict):
        gaps.append("site_access_missing")
        return {"entry_rule": None, "date_status": "missing", "age_days": None}, gaps, flags
    rule = raw.get("entry_rule") if raw.get("entry_rule") in ENTRY_RULES else None
    if rule is None:
        gaps.append("entry_rule_missing")
    elif rule == "unknown":
        flags.append("entry_rule_unknown")
    elif rule == "key_safe_not_stored":
        flags.append("key_safe_not_stored")
    age = _age(as_of, raw.get("as_of"))
    if age["status"] != "current":
        gaps.append(f"site_access_{age['status']}")
    return {"entry_rule": rule, "date_status": age["status"], "age_days": age["age_days"]}, gaps, flags


def _outcome(gaps: list[str], holds: list[str], *, rules_current: bool) -> str:
    if not rules_current:
        return "stale_sources"
    if holds:
        return "safety_hold"
    if any(gap.split(":", 1)[0] in BLOCKING or gap in BLOCKING for gap in gaps):
        return "missing_information"
    return "ready_for_confirmation"


def _refusal(stripped: list[str]) -> dict:
    sources, stale = _source_view(RETRIEVED_ON)
    brief = {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment_id": EXPERIMENT_ID,
        "autonomy": AUTONOMY,
        "outcome": "refused_not_synthetic",
        "as_of": None,
        "work_order_id": None,
        "sector": None,
        "organisation": None,
        "organisation_recognised": False,
        "asset": {
            "asset_id": None,
            "asset_id_valid": False,
            "description_catalogue_ids": [],
            "description_copied": False,
            "location_supplied": False,
            "location_id": None,
            "location_copied": False,
        },
        "record_priority": None,
        "record_status": None,
        "record_priority_is_not_an_agent_decision": True,
        "safety_records": [],
        "safety_holds": [],
        "safety_highlights": [],
        "access": {"entry_rule": None, "date_status": None, "age_days": None},
        "access_flags": [],
        "gaps": ["not_synthetic"],
        "possible_code_in_notes": False,
        "narrative_fully_scanned": False,
        "vulnerability": _vulnerability_stub("refused_not_synthetic"),
        "awaabs": _awaabs_stub("refused_not_synthetic"),
        "document_intake": _documents_stub("refused_not_synthetic"),
        "prompt_injection": {"detected": False, "signals": [], "followed": False},
        "prohibited_payload_keys": stripped,
        "sources": sources,
        "sources_not_opened": NOT_OPENED,
        "stale": stale,
        "regulatory": {},
        "human_approval": None,
        "human_route": _human_route(),
        "review": None,
        "flags": _flags(),
        "actions_taken": [],
        "executed": False,
        "model_called": False,
        "network_called": False,
        "narrative_echoed": False,
    }
    _force(brief)
    return brief


def prepare_brief(pack: dict, as_of: date | datetime | str) -> dict:
    """Return one brief. Confirmation flags stay false."""

    if not isinstance(pack, dict):
        raise TypeError("pack must be an object")
    working = dict(pack)
    stripped = _strip_prohibited(working)
    if working.get("synthetic") is not True:
        return _refusal(stripped)

    as_of_date = _parse_as_of(as_of)
    narrative = _free_text(working)
    fully_scanned = len(narrative) <= NARRATIVE_CAP
    if fully_scanned:
        matching = excise_clauses(narrative)
        instruction_rows = signals_in(narrative)
    else:
        matching = ""
        instruction_rows = []

    work = working.get("work_order") if isinstance(working.get("work_order"), dict) else {}
    asset = working.get("asset") if isinstance(working.get("asset"), dict) else {}
    work_order_id = _pattern(working.get("work_order_id"), WORK_ORDER_ID)
    sector = working.get("sector") if working.get("sector") in SECTORS else None
    organisation = working.get("organisation") if working.get("organisation") in ORGANISATIONS else None
    asset_id = _pattern(asset.get("asset_id"), ASSET_ID)
    location_id = _pattern(asset.get("location_id"), LOCATION_ID)
    location_supplied = bool(location_id) or (
        isinstance(asset.get("location"), str) and bool(asset.get("location").strip())
    )
    description = asset.get("description") if isinstance(asset.get("description"), str) else ""
    catalogue_ids = description_ids(description) if fully_scanned else []
    priority = work.get("priority_on_record") if work.get("priority_on_record") in PRIORITIES else None
    status = work.get("status_on_record") if work.get("status_on_record") in STATUSES else None
    summary = work.get("summary") if isinstance(work.get("summary"), str) else ""

    gaps: list[str] = []
    if work_order_id is None:
        gaps.append("work_order_id")
    if sector is None:
        gaps.append("sector")
    if asset_id is None:
        gaps.append("asset_id")
    if not location_supplied:
        gaps.append("location")
    if not summary.strip():
        gaps.append("summary")
    if not fully_scanned:
        gaps.append("narrative_too_long")
    if status == "closed":
        gaps.append("record_already_says_closed")

    safety_rows, safety_gaps, record_holds = _safety_rows(working, as_of_date)
    gaps.extend(safety_gaps)
    access, access_gaps, access_flags = _access(working, as_of_date, matching)
    gaps.extend(access_gaps)

    holds = list(record_holds)
    for name in hits(matching, HOLDS):
        if name not in holds:
            holds.append(name)
    highlights = hits(matching, HIGHLIGHTS)
    possible_code = bool(CODE_SHAPE.search(matching))

    claimed_approval = any(
        key in pack for key in ("officer_approved_category", "officer_approved_clock", "officer_approved_summary")
    )
    vulnerability = _scan(matching) if fully_scanned else _vulnerability_stub("narrative_too_long")
    documents = _documents(working, as_of_date, work_order_id) if fully_scanned else _documents_stub("narrative_too_long")
    awaabs = _awaabs(working, sector, claimed_approval) if fully_scanned else _awaabs_stub("narrative_too_long")

    if vulnerability["categories"]:
        gaps.append("vulnerability_indicator")
    if documents.get("injection_detected"):
        gaps.append("document_injection")
    if any(item == "stale" for item in documents.get("date_statuses") or []):
        gaps.append("document_stale")
    if sector == "housing" and awaabs["called"] is not True:
        gaps.append("awaabs_illustration_not_run")

    sources, stale = _source_view(as_of_date)
    last_service = _age(as_of_date, asset.get("last_service_on")) if "last_service_on" in asset else None
    if last_service and last_service["status"] != "current":
        gaps.append(f"last_service_{last_service['status']}")

    brief = {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment_id": EXPERIMENT_ID,
        "autonomy": AUTONOMY,
        "outcome": _outcome(gaps, holds, rules_current=stale["rules_current"]),
        "as_of": as_of_date.isoformat(),
        "work_order_id": work_order_id,
        "sector": sector,
        "organisation": organisation,
        "organisation_recognised": organisation is not None,
        "asset": {
            "asset_id": asset_id,
            "asset_id_valid": asset_id is not None,
            "description_catalogue_ids": catalogue_ids,
            "description_copied": False,
            "location_supplied": location_supplied,
            "location_id": location_id,
            "location_copied": False,
            "last_service_status": None if last_service is None else last_service["status"],
        },
        "record_priority": priority,
        "record_status": status,
        "record_priority_is_not_an_agent_decision": True,
        "safety_records": safety_rows,
        "safety_holds": holds,
        "safety_highlights": highlights,
        "access": access,
        "access_flags": access_flags,
        "gaps": gaps,
        "possible_code_in_notes": possible_code,
        "narrative_fully_scanned": fully_scanned,
        "vulnerability": vulnerability,
        "awaabs": awaabs,
        "document_intake": documents,
        "prompt_injection": {
            "detected": bool(instruction_rows),
            "signals": instruction_rows,
            "followed": False,
        },
        "prohibited_payload_keys": stripped,
        "sources": sources,
        "sources_not_opened": NOT_OPENED,
        "stale": stale,
        "regulatory": {},
        "human_approval": None,
        "human_route": _human_route(),
        "review": None,
        "flags": _flags(),
        "actions_taken": [],
        "executed": False,
        "model_called": False,
        "network_called": False,
        "narrative_echoed": False,
    }
    _force(brief)
    return brief


def record_review(brief: dict, review: dict) -> dict:
    """Record a technician confirmation or a supervisor note. Nothing is scheduled."""

    if not isinstance(brief, dict) or brief.get("experiment_id") != EXPERIMENT_ID:
        raise VisitForbidden("review needs a brief from this experiment")
    if not isinstance(review, dict):
        raise ValueError("review must be an object")
    result = copy.deepcopy(brief)
    decision = review.get("decision")

    def refuse(reason: str) -> dict:
        result["review"] = {
            "decision": decision if isinstance(decision, str) else None,
            "accepted": False,
            "refused": True,
            "reason": reason,
            "executed": False,
        }
        result["human_approval"] = None
        result["flags"]["context_confirmed"] = False
        _force(result)
        return result

    if decision in PROHIBITED_DECISIONS:
        return refuse("prohibited_decision")
    if decision not in ALLOWED_DECISIONS:
        return refuse("unknown_decision")
    if str(result.get("outcome", "")).startswith("refused_"):
        return refuse("not_a_brief")

    if decision == REJECT:
        role = review.get("actor_role")
        if role not in {"Field technician", "Supervisor"}:
            return refuse("actor_role")
        result["review"] = {
            "decision": REJECT,
            "accepted": True,
            "refused": False,
            "reason": "rejected_by_person",
            "executed": False,
        }
        result["human_approval"] = None
        result["flags"]["context_confirmed"] = False
        _force(result)
        return result

    if decision == SUPERVISOR:
        if review.get("actor_role") != "Supervisor":
            return refuse("actor_role")
        if not isinstance(review.get("actor_id"), str) or not SUP_ID.fullmatch(review["actor_id"]):
            return refuse("actor_id")
        if not result["safety_holds"]:
            return refuse("no_hold")
        result["review"] = {
            "decision": SUPERVISOR,
            "accepted": True,
            "refused": False,
            "reason": "hold_seen_not_cleared",
            "executed": False,
        }
        result["human_approval"] = None
        result["flags"]["context_confirmed"] = False
        _force(result)
        return result

    if review.get("actor_role") != "Field technician":
        return refuse("actor_role")
    if not isinstance(review.get("actor_id"), str) or not TECH_ID.fullmatch(review["actor_id"]):
        return refuse("actor_id")
    if review.get("asset_id") != result["asset"]["asset_id"] or not result["asset"]["asset_id"]:
        return refuse("asset_mismatch")
    if review.get("safety_context_read") is not True:
        return refuse("safety_context_not_read")
    if result["gaps"] and review.get("acknowledge_gaps") is not True:
        return refuse("gaps_not_acknowledged")
    if result["safety_holds"] and review.get("acknowledge_safety_hold") is not True:
        return refuse("hold_not_acknowledged")
    if result["stale"]["rules_current"] is not True and review.get("acknowledge_stale") is not True:
        return refuse("sources_outside_window")

    result["human_approval"] = {
        "decision": CONFIRM,
        "approver": "Field technician",
        "actor_id": review["actor_id"],
        "asset_id": review["asset_id"],
        "executed": False,
        "scheduled": False,
        "dispatched": False,
        "closed": False,
        "entry_authorised": False,
        "hold_cleared": False,
    }
    result["review"] = {
        "decision": CONFIRM,
        "accepted": True,
        "refused": False,
        "reason": "context_confirmed",
        "executed": False,
    }
    result["flags"]["context_confirmed"] = True
    _force(result)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Assemble a field brief. Does not schedule, dispatch, or close."
    )
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--as-of", required=True)
    args = parser.parse_args(argv)
    try:
        pack = json.loads(args.input.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        print("The input could not be read.", file=sys.stderr)
        return 2
    if not isinstance(pack, dict):
        print("The input must be a JSON object.", file=sys.stderr)
        return 2
    try:
        brief = prepare_brief(pack, args.as_of)
    except (TypeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    json.dump(brief, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
