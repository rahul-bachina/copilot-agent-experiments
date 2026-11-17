#!/usr/bin/env python3
"""Draft a one-to-one prep note from context a line manager has already selected.

Autonomy A0. The selection object is the authorisation. Words inside a note
are not. The note quotes follow-ups, objectives, shared updates, and calendar
items. It does not rate performance, compare people, or recommend a
disciplinary or capability step. Distress and personal circumstances are
flagged for a person. They are not turned into routine agenda items.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from copy import deepcopy
from datetime import date
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from concerns import (
        experiment_15_kind,
        flag_row,
        follow_up_cue,
        is_denial_of_inclusion,
        local_concerns,
        prohibited_requests,
    )
    from injection import injection_codes, redact_untrusted_claims, untrusted_claims
    from marking import (
        CEILING,
        RANK,
        above_ceiling,
        clearance_rank,
        highest,
        hold_indicated,
        labels_in_text,
        readable_marking,
        retention_labels,
        strip_clearance_boasts,
    )
    from mask import mask_text, merge_counts
    from reuse import NeighbourMissing, channel_cues, citation_tools, redact_uk_identifiers, scan_indicators
    from sources import (
        DEFAULT_NOTE_STALE_DAYS,
        SOURCES_PINNED_ON,
        STALE_AFTER_DAYS,
        source_rows,
    )
else:
    from .concerns import (
        experiment_15_kind,
        flag_row,
        follow_up_cue,
        is_denial_of_inclusion,
        local_concerns,
        prohibited_requests,
    )
    from .injection import injection_codes, redact_untrusted_claims, untrusted_claims
    from .marking import (
        CEILING,
        RANK,
        above_ceiling,
        clearance_rank,
        highest,
        hold_indicated,
        labels_in_text,
        readable_marking,
        retention_labels,
        strip_clearance_boasts,
    )
    from .mask import mask_text, merge_counts
    from .reuse import NeighbourMissing, channel_cues, citation_tools, redact_uk_identifiers, scan_indicators
    from .sources import (
        DEFAULT_NOTE_STALE_DAYS,
        SOURCES_PINNED_ON,
        STALE_AFTER_DAYS,
        source_rows,
    )

LABEL = (
    "DRAFT ONE-TO-ONE PREP NOTE. NOT A PERFORMANCE RATING. "
    "NOT A DISCIPLINARY RECOMMENDATION."
)
CATALOGUE_ID = "H003"
AUTONOMY = "A0"
CALLER = "exp-60-manager-one-to-one-prep"
MAX_CHARS = 20_000
MAX_POINTS = 8
MARKING_SCAN_CHARS = 2_000

ALLOWED_KINDS = frozenset(
    {
        "previous_one_to_one_note",
        "agreed_objective",
        "employee_shared_update",
        "team_calendar_item",
    }
)
FORBIDDEN_KINDS = frozenset(
    {
        "mailbox",
        "email",
        "chat",
        "teams_chat",
        "direct_message",
        "performance_rating",
        "peer_comparison",
        "health_record",
        "disciplinary_file",
        "capability_file",
    }
)
IGNORED_PACK_KEYS = (
    "human_approval",
    "performance_rating",
    "comparison",
    "disciplinary_recommendation",
    "capability_recommendation",
    "health_inference",
    "protected_characteristic_inference",
    "personal_circumstances_inference",
    "employee_profile",
    "approved",
    "clearance",
    "actor_role",
)
PROMPTS = {
    "previous_one_to_one_note": (
        "What is the current position on this follow-up from the last one-to-one?"
    ),
    "agreed_objective": "What progress would you like to talk through on this agreed objective?",
    "employee_shared_update": "Is there anything you want to add to this update you shared?",
    "team_calendar_item": "Is this calendar item still the one you want to cover?",
}
_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")


class PrepForbidden(RuntimeError):
    """A rating, a comparison, a sanction, a browse, a send, or a write."""


def rate_performance(*_args: Any, **_kwargs: Any) -> None:
    raise PrepForbidden("The prep note does not rate performance.")


def compare_employees(*_args: Any, **_kwargs: Any) -> None:
    raise PrepForbidden("The prep note does not compare employees.")


def recommend_disciplinary(*_args: Any, **_kwargs: Any) -> None:
    raise PrepForbidden("The prep note does not recommend disciplinary action.")


def recommend_capability(*_args: Any, **_kwargs: Any) -> None:
    raise PrepForbidden("The prep note does not recommend capability action.")


def infer_health(*_args: Any, **_kwargs: Any) -> None:
    raise PrepForbidden("The prep note does not infer health.")


def infer_protected_characteristic(*_args: Any, **_kwargs: Any) -> None:
    raise PrepForbidden("The prep note does not infer a protected characteristic.")


def profile_employee(*_args: Any, **_kwargs: Any) -> None:
    raise PrepForbidden("The prep note does not profile an employee.")


def read_mailbox(*_args: Any, **_kwargs: Any) -> None:
    raise PrepForbidden("The prep note does not read a mailbox.")


def read_chat(*_args: Any, **_kwargs: Any) -> None:
    raise PrepForbidden("The prep note does not read a chat.")


def send_note(*_args: Any, **_kwargs: Any) -> None:
    raise PrepForbidden("The prep note does not send.")


def write_personnel_record(*_args: Any, **_kwargs: Any) -> None:
    raise PrepForbidden("The prep note does not write a personnel record.")


def approve_from_content(*_args: Any, **_kwargs: Any) -> None:
    raise PrepForbidden("Words inside a note are not the manager's selection.")


def parse_date(value: Any) -> date | None:
    if not isinstance(value, str) or not _DATE.fullmatch(value.strip()):
        return None
    try:
        return date.fromisoformat(value.strip())
    except ValueError:
        return None


def parse_positive_int(value: Any) -> int | None:
    """A positive whole number. Zero, a float, and a word are not coerced."""
    if isinstance(value, bool) or isinstance(value, float) or value is None:
        return None
    if isinstance(value, int):
        return value if value > 0 else None
    if isinstance(value, str) and re.fullmatch(r"[1-9]\d*", value.strip()):
        return int(value.strip())
    return None


def _people(directory: Any) -> tuple[dict[str, dict], str | None]:
    if not isinstance(directory, list):
        return {}, "directory_not_a_list"
    people: dict[str, dict] = {}
    for row in directory:
        if not isinstance(row, dict):
            return {}, "directory_row_unreadable"
        person_id = row.get("id")
        role = row.get("role")
        if not isinstance(person_id, str) or not person_id or not isinstance(role, str) or not role:
            return {}, "directory_row_unreadable"
        if person_id in people:
            return {}, "duplicate_directory_id"
        reports = row.get("reports")
        if reports is None:
            report_ids: list[str] = []
        elif isinstance(reports, list) and all(isinstance(item, str) for item in reports):
            report_ids = list(reports)
        else:
            return {}, "directory_reports_unreadable"
        manager_id = row.get("manager_id")
        if manager_id is not None and not isinstance(manager_id, str):
            return {}, "directory_manager_unreadable"
        people[person_id] = {
            "id": person_id,
            "role": role,
            "manager_id": manager_id,
            "reports": report_ids,
            "clearance": row.get("clearance") if isinstance(row.get("clearance"), str) else None,
            "display_name": row.get("display_name") if isinstance(row.get("display_name"), str) else "",
        }
    return people, None


def _lines(source: dict) -> tuple[list[str] | None, str | None]:
    raw = source.get("lines")
    if raw is None:
        return [], None
    if isinstance(raw, str):
        return raw.splitlines(), None
    if isinstance(raw, list) and all(isinstance(item, str) for item in raw):
        return list(raw), None
    return None, "lines_unreadable"


def _body(lines: list[str]) -> str:
    return "\n".join(lines)


def _source_labels(source: dict, lines: list[str]) -> tuple[str | None, bool, list[str], bool]:
    """Marking, whether the marking was readable, hold, retention labels."""
    text = strip_clearance_boasts(_body(lines))
    scan_text = text if len(text) <= MAX_CHARS else text[:MARKING_SCAN_CHARS]
    meta_labels, meta_ok = readable_marking(source.get("protective_marking"))
    if not meta_ok:
        return None, False, hold_indicated(scan_text, source.get("legal_hold") is True), retention_labels(
            scan_text, source.get("retention_label") or source.get("retention_labels")
        )
    content_labels = labels_in_text(scan_text)
    label = highest(meta_labels + content_labels)
    if label is None:
        label = "OFFICIAL"
    hold = hold_indicated(scan_text, source.get("legal_hold") is True)
    labels = retention_labels(scan_text, source.get("retention_label") or source.get("retention_labels"))
    return label, True, hold, labels


def _lock(result: dict) -> dict:
    result["performance_rating"] = None
    result["comparison"] = None
    result["disciplinary_recommendation"] = None
    result["capability_recommendation"] = None
    result["health_inference"] = None
    result["protected_characteristic_inference"] = None
    result["personal_circumstances_inference"] = None
    result["employee_profile"] = None
    result["mailbox_read"] = False
    result["chat_read"] = False
    result["sources_pulled_beyond_selection"] = False
    result["network_called"] = False
    result["injection_followed"] = False
    result["approval_taken_from_content"] = False
    result["flags"] = {
        "sent": False,
        "written": False,
        "rated": False,
        "compared": False,
        "disciplinary_recommended": False,
        "capability_recommended": False,
        "health_inferred": False,
        "protected_characteristic_inferred": False,
        "profiled": False,
        "mailbox_read": False,
        "chat_read": False,
        "graph_called": False,
        "network_called": False,
        "injection_followed": False,
        "approval_taken_from_content": False,
    }
    return result


def _base(pack: dict) -> dict:
    return _lock(
        {
            "label": LABEL,
            "catalogue_id": CATALOGUE_ID,
            "experiment": "60",
            "autonomy": AUTONOMY,
            "caller": CALLER,
            "synthetic_only": True,
            "outcome": "needs_human",
            "may_be_relied_on": False,
            "human_approval": None,
            "meeting_id": pack.get("meeting_id") if isinstance(pack.get("meeting_id"), str) else None,
            "prep_note": {"points": [], "follow_ups": [], "open_questions": []},
            "human_flags": [],
            "source_report": [],
            "not_read": [],
            "omitted": [],
            "prohibited_requests": [],
            "injection": {"detected": False, "followed": False, "items": []},
            "untrusted_claims": [],
            "field_errors": [],
            "ignored_pack_keys": [],
            "masking": merge_counts([]),
            "uk_identifier_types": [],
            "copied_lines": [],
            "points_not_shown_count": 0,
            "reuse": {
                "experiment_15": {"called": False, "text_copied": False},
                "experiment_41": {"called": False, "text_copied": False},
                "experiment_51": {"called": False, "text_copied": False},
                "experiment_08": {"called": False, "values_stored": False},
            },
            "ceiling": CEILING,
            "described_as_anonymised": False,
        }
    )


def _field_error(field: str, reason: str) -> dict:
    return {"field": field, "reason": reason, "coerced_to": None}


def prepare(pack: dict, as_of: str | None = None) -> dict:
    """Return one prep note. The same pack and date produce the same JSON."""
    if not isinstance(pack, dict):
        result = _base({})
        result["outcome"] = "needs_human"
        result["field_errors"].append(_field_error("pack", "not_an_object"))
        return result

    working = deepcopy(pack)
    ignored = [key for key in IGNORED_PACK_KEYS if key in working]
    for key in ignored:
        working.pop(key, None)
    result = _base(working)
    result["ignored_pack_keys"] = ignored
    result["synthetic"] = working.get("synthetic") is True

    if working.get("synthetic") is not True:
        result["outcome"] = "refused"
        result["refusal"] = "not_synthetic"
        result["prep_note"] = {"points": [], "follow_ups": [], "open_questions": []}
        return _lock(result)

    chosen = as_of if as_of is not None else working.get("as_of")
    as_of_date = parse_date(chosen)
    if as_of_date is None:
        result["field_errors"].append(_field_error("as_of", "unparseable"))
        result["as_of"] = None
        return _lock(result)
    result["as_of"] = as_of_date.isoformat()
    if as_of is not None and "as_of" in working and working.get("as_of") != as_of:
        pack_date = parse_date(working.get("as_of"))
        if pack_date is None or pack_date != as_of_date:
            result["field_errors"].append(_field_error("as_of", "pack_and_argument_disagree"))

    scheduled = working.get("scheduled_for")
    if scheduled is not None and parse_date(scheduled) is None:
        result["field_errors"].append(_field_error("scheduled_for", "unparseable"))
        result["scheduled_for"] = None
    else:
        result["scheduled_for"] = parse_date(scheduled).isoformat() if scheduled else None

    if "stale_after_days" in working:
        window = parse_positive_int(working.get("stale_after_days"))
        if window is None:
            result["field_errors"].append(_field_error("stale_after_days", "unparseable"))
            result["stale_after_days"] = None
            result["outcome"] = "needs_human"
            return _lock(result)
    else:
        window = DEFAULT_NOTE_STALE_DAYS
    result["stale_after_days"] = window
    result["stale_window_is_statutory"] = False

    pin_age = (as_of_date - SOURCES_PINNED_ON).days
    rules_current = 0 <= pin_age <= STALE_AFTER_DAYS
    result["statutory_pins_current"] = rules_current
    result["sources"] = source_rows(as_of_date.isoformat(), rules_current=rules_current)

    people, directory_error = _people(working.get("directory"))
    if directory_error:
        result["field_errors"].append(_field_error("directory", directory_error))
        result["outcome"] = "needs_human"
        return _lock(result)
    result["directory_snapshot"] = [
        {
            "id": person["id"],
            "role": person["role"],
            "manager_id": person["manager_id"],
            "reports": list(person["reports"]),
            "clearance": person["clearance"],
        }
        for person in people.values()
    ]

    manager_id = working.get("manager_id")
    employee_id = working.get("employee_id")
    manager = people.get(manager_id) if isinstance(manager_id, str) else None
    employee = people.get(employee_id) if isinstance(employee_id, str) else None
    selection = working.get("selection")
    authorised, auth_reason = _authorised(manager, employee, selection)
    result["manager_id"] = manager["id"] if manager else None
    result["employee_id"] = employee["id"] if employee else None
    result["selection"] = {
        "authorised": authorised,
        "reason": auth_reason,
        "selector_id": selection.get("selector_id") if isinstance(selection, dict) else None,
        "selected_source_ids": (
            list(selection.get("selected_source_ids"))
            if isinstance(selection, dict) and isinstance(selection.get("selected_source_ids"), list)
            else None
        ),
        "approval_reference": (
            selection.get("approval_reference") if isinstance(selection, dict) else None
        ),
    }
    if not authorised:
        result["outcome"] = "refused" if auth_reason != "selection_unreadable" else "needs_human"
        result["refusal"] = auth_reason
        _inventory_without_reading(working, result)
        return _lock(result)

    rank, clearance_ok = clearance_rank(manager.get("clearance") if manager else None)
    if not clearance_ok or rank is None:
        result["field_errors"].append(_field_error("directory_clearance", "unreadable"))
        result["outcome"] = "needs_human"
        return _lock(result)
    result["directory_clearance_rank"] = rank
    result["clearance_taken_from"] = "directory"

    selected_ids = list(selection["selected_source_ids"])
    result["selection"]["item_id"] = _item_id(
        str(working.get("meeting_id") or ""),
        selected_ids,
        str(selection.get("approval_reference") or ""),
    )
    keep_names = {
        name
        for name in (
            (manager or {}).get("display_name", ""),
            (employee or {}).get("display_name", ""),
        )
        if name
    }
    display_name = (employee or {}).get("display_name") or "Employee"

    sources = working.get("sources")
    if not isinstance(sources, list):
        result["field_errors"].append(_field_error("sources", "not_a_list"))
        result["outcome"] = "needs_human"
        return _lock(result)

    seen_ids: dict[str, int] = {}
    for source in sources:
        if isinstance(source, dict) and isinstance(source.get("id"), str):
            seen_ids[source["id"]] = seen_ids.get(source["id"], 0) + 1

    try:
        scan = scan_indicators()
        check_sentence, index_events = citation_tools()
    except NeighbourMissing as exc:
        result["field_errors"].append(_field_error("reuse", f"missing:{exc}"))
        result["outcome"] = "needs_human"
        return _lock(result)

    mask_rows: list[dict] = []
    identifier_types: list[str] = []
    points: list[dict] = []
    request = working.get("request")
    if isinstance(request, str):
        _absorb_line_signals(
            result,
            request,
            source_id=None,
            line_no=None,
        )

    known_ids = set()
    for source in sources:
        if not isinstance(source, dict) or not isinstance(source.get("id"), str) or not source.get("id"):
            result["field_errors"].append(_field_error("sources", "source_id_unreadable"))
            continue
        source_id = source["id"]
        known_ids.add(source_id)
        kind = source.get("kind") if isinstance(source.get("kind"), str) else ""
        selected = source_id in selected_ids
        lines, line_error = _lines(source)
        if line_error or lines is None:
            result["field_errors"].append(_field_error(source_id, "lines_unreadable"))
            result["source_report"].append(
                _report(source_id, kind, selected, marking=None, hold=False, retention=[], reason="lines_unreadable")
            )
            continue
        if seen_ids.get(source_id, 0) > 1:
            label, ok, hold, retention = _source_labels(source, lines)
            result["source_report"].append(
                _report(source_id, kind, selected, label if ok else None, hold, retention, "duplicate_source_id")
            )
            result["field_errors"].append(_field_error(source_id, "duplicate_source_id"))
            continue

        label, marking_ok, hold, retention = _source_labels(source, lines)
        too_long = sum(len(line) for line in lines) > MAX_CHARS
        if not marking_ok:
            result["field_errors"].append(_field_error(source_id, "marking_unreadable"))
            result["source_report"].append(
                _report(source_id, kind, selected, None, hold, retention, "marking_unreadable")
            )
            continue
        if not selected or kind not in ALLOWED_KINDS or too_long or above_ceiling(label) or RANK[label] > rank:
            reason = _skip_reason(
                selected=selected,
                kind=kind,
                too_long=too_long,
                label=label,
                clearance_rank_value=rank,
            )
            result["source_report"].append(_report(source_id, kind, selected, label, hold, retention, reason))
            result["not_read"].append(
                {
                    "source_id": source_id,
                    "kind": kind or None,
                    "reason": reason,
                    "marking": label,
                    "legal_hold": hold,
                    "retention_labels": list(retention),
                    "body_copied": False,
                    "content_used_in_prep_note": False,
                }
            )
            continue

        date_status = _date_status(source, kind, as_of_date, window)
        if date_status in {"unreadable", "future"}:
            result["field_errors"].append(
                _field_error(source_id, "date_unreadable" if date_status == "unreadable" else "date_in_the_future")
            )
            result["source_report"].append(
                _report(source_id, kind, True, label, hold, retention, date_status)
            )
            continue
        stale = date_status == "stale"
        indicator_lines = _indicator_lines(scan, lines, source_id, result)
        copied_numbers: list[int] = []
        omitted_numbers: list[int] = []
        for number, line in enumerate(lines, start=1):
            if not line.strip():
                continue
            codes = injection_codes(line)
            claims = untrusted_claims(line)
            requests = prohibited_requests(line)
            if claims:
                result["untrusted_claims"].append(
                    {"source_id": source_id, "line": number, "claims": claims, "trusted": False}
                )
            for code in requests:
                result["prohibited_requests"].append(
                    {
                        "code": code,
                        "source_id": source_id,
                        "line": number,
                        "followed": False,
                        "sentence_copied": False,
                    }
                )
            if codes:
                result["injection"]["detected"] = True
                result["injection"]["items"].append(
                    {
                        "source_id": source_id,
                        "line": number,
                        "codes": codes,
                        "followed": False,
                        "sentence_copied": False,
                    }
                )
                omitted_numbers.append(number)
                result["omitted"].append(
                    {"source_id": source_id, "line": number, "reason": "injection", "sentence_copied": False}
                )
                continue
            try:
                cues = channel_cues(line, display_name)
                result["reuse"]["experiment_51"]["called"] = True
            except NeighbourMissing:
                cues = {"action": False, "decision": False, "negated": False, "injection": True}
                result["field_errors"].append(_field_error("experiment_51", "missing"))
            if cues.get("injection"):
                result["injection"]["detected"] = True
                result["injection"]["items"].append(
                    {
                        "source_id": source_id,
                        "line": number,
                        "codes": ["experiment_51"],
                        "followed": False,
                        "sentence_copied": False,
                    }
                )
                omitted_numbers.append(number)
                result["omitted"].append(
                    {
                        "source_id": source_id,
                        "line": number,
                        "reason": "injection",
                        "sentence_copied": False,
                    }
                )
                continue
            concerns = list(indicator_lines.get(number, []))
            concerns.extend(local_concerns(line))
            if requests:
                omitted_numbers.append(number)
                result["omitted"].append(
                    {
                        "source_id": source_id,
                        "line": number,
                        "reason": "prohibited_request",
                        "sentence_copied": False,
                    }
                )
                continue
            if concerns:
                _add_flags(result, concerns, source_id, number)
                omitted_numbers.append(number)
                result["omitted"].append(
                    {
                        "source_id": source_id,
                        "line": number,
                        "reason": "human_flag",
                        "sentence_copied": False,
                    }
                )
                continue
            if is_denial_of_inclusion(line):
                omitted_numbers.append(number)
                result["omitted"].append(
                    {
                        "source_id": source_id,
                        "line": number,
                        "reason": "negation_not_an_inclusion",
                        "sentence_copied": False,
                    }
                )
                continue
            if not _work_line(kind, line, cues):
                omitted_numbers.append(number)
                result["omitted"].append(
                    {
                        "source_id": source_id,
                        "line": number,
                        "reason": "not_a_follow_up_or_selected_update",
                        "sentence_copied": False,
                    }
                )
                continue
            if len(points) >= MAX_POINTS:
                result["points_not_shown_count"] += 1
                omitted_numbers.append(number)
                result["omitted"].append(
                    {"source_id": source_id, "line": number, "reason": "cap", "sentence_copied": False}
                )
                continue
            shown, copied = _present_line(
                line,
                keep_names,
                source_id,
                number,
                kind,
                label,
                hold,
                retention,
                stale,
                check_sentence,
                index_events,
                as_of_date.isoformat(),
                result,
                mask_rows,
                identifier_types,
            )
            if copied:
                points.append(shown)
                copied_numbers.append(number)
            else:
                omitted_numbers.append(number)

        non_empty = [number for number, line in enumerate(lines, start=1) if line.strip()]
        result["source_report"].append(
            {
                **_report(source_id, kind, True, label, hold, retention, None if copied_numbers else "nothing_copied"),
                "lines_copied": copied_numbers,
                "lines_not_copied": omitted_numbers,
                "full_body_copied": bool(non_empty) and omitted_numbers == [] and copied_numbers == non_empty,
                "body_copied": bool(copied_numbers),
                "stale": stale,
                "content_used_in_prep_note": bool(copied_numbers),
            }
        )

    for source_id in selected_ids:
        if source_id not in known_ids:
            result["field_errors"].append(_field_error(source_id, "selected_source_missing"))
            result["not_read"].append(
                {
                    "source_id": source_id,
                    "kind": None,
                    "reason": "selected_source_missing",
                    "body_copied": False,
                    "content_used_in_prep_note": False,
                }
            )

    result["prep_note"]["points"] = points
    result["prep_note"]["follow_ups"] = [
        point for point in points if point["kind"] == "previous_one_to_one_note"
    ]
    result["prep_note"]["open_questions"] = [
        {
            "question_id": f"Q{index}",
            "prompt": PROMPTS[point["kind"]],
            "quoted_line": point["text"],
            "citation": point["citation"],
            "performance_rating": None,
        }
        for index, point in enumerate(points, start=1)
    ]
    result["copied_lines"] = [
        {"source_id": point["citation"]["source_id"], "line": point["citation"]["line"], "text": point["text"]}
        for point in points
    ]
    result["masking"] = merge_counts(mask_rows)
    result["uk_identifier_types"] = identifier_types
    result["injection"]["followed"] = False
    if result["field_errors"] or result["human_flags"] or any(point["stale"] for point in points) or not rules_current:
        result["may_be_relied_on"] = False
    else:
        result["may_be_relied_on"] = True
    if result["human_flags"] and not points:
        result["outcome"] = "needs_human"
    elif result["field_errors"] and not points:
        result["outcome"] = "needs_human"
    elif points or result["human_flags"]:
        result["outcome"] = "prep_note"
    else:
        result["outcome"] = "needs_human"
        result["may_be_relied_on"] = False
    return _lock(result)


def _authorised(manager: dict | None, employee: dict | None, selection: Any) -> tuple[bool, str]:
    if not isinstance(selection, dict):
        return False, "selection_unreadable"
    selector = selection.get("selector_id")
    source_ids = selection.get("selected_source_ids")
    reference = selection.get("approval_reference")
    if not isinstance(selector, str) or not selector:
        return False, "selection_unreadable"
    if not isinstance(source_ids, list) or not source_ids or not all(isinstance(item, str) and item for item in source_ids):
        return False, "selection_unreadable"
    if not isinstance(reference, str) or not reference:
        return False, "selection_unreadable"
    if manager is None or manager.get("role") != "line_manager":
        return False, "selector_not_line_manager_in_directory"
    if employee is None or employee.get("role") != "employee":
        return False, "employee_not_in_directory"
    if employee.get("manager_id") != manager.get("id"):
        return False, "not_the_employees_line_manager"
    if employee.get("id") not in (manager.get("reports") or []):
        return False, "employee_not_in_manager_reports"
    if selector != manager.get("id"):
        return False, "selector_is_not_the_manager"
    return True, "directory_line_manager"


def _skip_reason(*, selected: bool, kind: str, too_long: bool, label: str, clearance_rank_value: int) -> str:
    if not selected:
        return "not_selected"
    if kind in FORBIDDEN_KINDS:
        return "source_class_not_permitted"
    if kind not in ALLOWED_KINDS:
        return "source_class_not_permitted"
    if too_long:
        return "too_long"
    if above_ceiling(label):
        return "above_ceiling"
    if RANK[label] > clearance_rank_value:
        return "above_directory_clearance"
    return "not_read"


def _report(source_id, kind, selected, marking, hold, retention, reason) -> dict:
    return {
        "source_id": source_id,
        "kind": kind or None,
        "selected": selected,
        "marking": marking,
        "legal_hold": hold,
        "retention_labels": list(retention),
        "lines_copied": [],
        "lines_not_copied": [],
        "full_body_copied": False,
        "body_copied": False,
        "content_used_in_prep_note": False,
        "reason": reason,
    }


def _date_status(source: dict, kind: str, as_of_date: date, window: int) -> str:
    if kind == "agreed_objective":
        raw = source.get("recorded_on")
        if raw is None:
            return "undated_objective"
        parsed = parse_date(raw)
        if parsed is None:
            return "unreadable"
    elif kind == "team_calendar_item":
        parsed = parse_date(source.get("occurs_on"))
        if parsed is None:
            return "unreadable"
    else:
        parsed = parse_date(source.get("recorded_on"))
        if parsed is None:
            return "unreadable"
    if parsed is None:
        return "undated_objective"
    age = (as_of_date - parsed).days
    if kind == "team_calendar_item":
        if age > window:
            return "stale"
        return "current"
    if age < 0:
        return "future"
    if age > window:
        return "stale"
    return "current"


def _indicator_lines(scan, lines: list[str], source_id: str, result: dict) -> dict[int, list[dict]]:
    text = _body(lines)
    if not text.strip():
        return {}
    scanned = scan(text, synthetic=True)
    result["reuse"]["experiment_15"]["called"] = True
    result["reuse"]["experiment_15"]["text_copied"] = False
    spans = []
    cursor = 0
    for number, line in enumerate(lines, start=1):
        spans.append((number, cursor, cursor + len(line)))
        cursor += len(line) + 1
    found: dict[int, list[dict]] = {}
    for flag in scanned.get("flags") or []:
        pos = flag.get("start")
        if not isinstance(pos, int):
            continue
        for number, start, end in spans:
            if start <= pos < end:
                kind = experiment_15_kind(
                    str(flag.get("category") or ""),
                    str(flag.get("phrase") or ""),
                    lines[number - 1],
                    pos - start,
                )
                if kind is None:
                    break
                row = {
                    "kind": kind,
                    "indicator": str(flag.get("category") or kind),
                    "experiment_15": True,
                    "sentence_copied": False,
                }
                bucket = found.setdefault(number, [])
                if not any(item["indicator"] == row["indicator"] for item in bucket):
                    bucket.append(row)
                break
    return found


def _add_flags(result: dict, concerns: list[dict], source_id: str, number: int) -> None:
    seen = {(row["source_id"], row["line"], row["indicator"]) for row in result["human_flags"]}
    for concern in concerns:
        key = (source_id, number, concern["indicator"])
        if key in seen:
            continue
        seen.add(key)
        result["human_flags"].append(
            flag_row(
                concern["kind"],
                concern["indicator"],
                source_id,
                number,
                experiment_15=bool(concern.get("experiment_15")),
            )
        )


def _work_line(kind: str, line: str, cues: dict) -> bool:
    if kind == "previous_one_to_one_note":
        return follow_up_cue(line) or bool(cues.get("action") or cues.get("decision"))
    return kind in ALLOWED_KINDS


def _present_line(
    line: str,
    keep_names: set[str],
    source_id: str,
    number: int,
    kind: str,
    label: str,
    hold: bool,
    retention: list[str],
    stale: bool,
    check_sentence,
    index_events,
    as_of: str,
    result: dict,
    mask_rows: list[dict],
    identifier_types: list[str],
) -> tuple[dict, bool]:
    quoted = redact_untrusted_claims(line)
    try:
        redacted, types = redact_uk_identifiers(quoted)
        result["reuse"]["experiment_08"]["called"] = True
    except NeighbourMissing:
        result["field_errors"].append(_field_error(source_id, "experiment_08_missing"))
        result["omitted"].append(
            {"source_id": source_id, "line": number, "reason": "identifier_check_failed", "sentence_copied": False}
        )
        return {}, False
    for entity in types:
        if entity not in identifier_types:
            identifier_types.append(entity)
    masked, counts = mask_text(redacted, keep_names)
    mask_rows.append(counts)
    if not masked.strip():
        result["omitted"].append(
            {"source_id": source_id, "line": number, "reason": "empty_after_masking", "sentence_copied": False}
        )
        return {}, False
    event = {
        "event_id": source_id,
        "status": "current",
        "recorded_on": as_of,
        "paragraphs": [{"paragraph": 1, "lines": [{"line": number, "text": masked}]}],
    }
    try:
        events = index_events([event])
        checked = check_sentence(
            {
                "sentence_id": f"{source_id}-{number}",
                "text": masked,
                "citation": {
                    "event_id": source_id,
                    "paragraph": 1,
                    "line_start": number,
                    "line_end": number,
                },
            },
            events,
            as_of=as_of,
            stale_after_days=100000,
            withheld=set(),
            sentence_has_identifier=False,
        )
        result["reuse"]["experiment_41"]["called"] = True
    except (NeighbourMissing, ValueError):
        result["omitted"].append(
            {"source_id": source_id, "line": number, "reason": "citation_check_failed", "sentence_copied": False}
        )
        return {}, False
    if checked.get("verdict") != "supported":
        result["omitted"].append(
            {
                "source_id": source_id,
                "line": number,
                "reason": "citation_not_supported",
                "sentence_copied": False,
            }
        )
        return {}, False
    point = {
        "text": masked,
        "kind": kind,
        "citation": {"source_id": source_id, "line": number, "kind": kind},
        "marking": label,
        "legal_hold": hold,
        "retention_labels": list(retention),
        "stale": stale,
        "masked": bool(counts["any"] or types),
        "mask_counts": counts["counts"],
        "uk_identifier_types": list(types),
        "raw_values_stored": False,
        "citation_verdict": "supported",
    }
    return point, True


def _absorb_line_signals(result: dict, text: str, source_id: str | None, line_no: int | None) -> None:
    codes = injection_codes(text)
    if codes:
        result["injection"]["detected"] = True
        result["injection"]["items"].append(
            {
                "source_id": source_id,
                "line": line_no,
                "codes": codes,
                "followed": False,
                "sentence_copied": False,
            }
        )
    for code in prohibited_requests(text):
        result["prohibited_requests"].append(
            {
                "code": code,
                "source_id": source_id,
                "line": line_no,
                "followed": False,
                "sentence_copied": False,
            }
        )
    for claim in untrusted_claims(text):
        result["untrusted_claims"].append(
            {"source_id": source_id, "line": line_no, "claims": [claim], "trusted": False}
        )


def _inventory_without_reading(working: dict, result: dict) -> None:
    sources = working.get("sources")
    if not isinstance(sources, list):
        return
    for source in sources:
        if not isinstance(source, dict):
            continue
        source_id = source.get("id") if isinstance(source.get("id"), str) else None
        kind = source.get("kind") if isinstance(source.get("kind"), str) else None
        if source_id is None:
            continue
        result["not_read"].append(
            {
                "source_id": source_id,
                "kind": kind,
                "reason": "selection_not_authorised",
                "body_copied": False,
                "content_used_in_prep_note": False,
            }
        )


def _item_id(meeting_id: str, source_ids: list[str], reference: str) -> str:
    return meeting_id + "|" + "\n".join(source_ids) + "|" + reference


def acknowledge(result: dict, approval: dict) -> dict:
    """Record that the directory line manager has seen this exact prep note.

    The approval object is a separate argument. Text inside the prep note,
    or inside the original sources, is not read again and does not count.
    Seeing the note does not rate performance.
    """
    updated = deepcopy(result)
    updated["human_approval"] = None
    updated["acknowledgement"] = {"accepted": False, "reason": "not_accepted"}
    if not isinstance(approval, dict):
        updated["acknowledgement"]["reason"] = "approval_not_an_object"
        return _lock(updated)
    if updated.get("outcome") == "refused" or updated.get("synthetic") is not True:
        updated["acknowledgement"]["reason"] = "nothing_to_acknowledge"
        return _lock(updated)
    snapshot = {row["id"]: row for row in updated.get("directory_snapshot") or [] if isinstance(row, dict)}
    actor_id = approval.get("actor_id")
    person = snapshot.get(actor_id) if isinstance(actor_id, str) else None
    selection = updated.get("selection") or {}
    expected_ids = selection.get("selected_source_ids")
    reasons: list[str] = []
    if person is None or person.get("role") != "line_manager":
        reasons.append("approver_not_line_manager_in_directory")
    elif actor_id != updated.get("manager_id"):
        reasons.append("approver_is_not_the_manager_for_this_meeting")
    if approval.get("meeting_id") != updated.get("meeting_id"):
        reasons.append("meeting_id_mismatch")
    if approval.get("selected_source_ids") != expected_ids:
        reasons.append("source_ids_do_not_match")
    if approval.get("approval_reference") != selection.get("approval_reference"):
        reasons.append("approval_reference_mismatch")
    if approval.get("seen") is not True:
        reasons.append("not_marked_seen")
    if approval.get("item_id") not in (None, selection.get("item_id")):
        reasons.append("item_id_mismatch")
    claimed_role = approval.get("actor_role")
    role_ignored = isinstance(claimed_role, str)
    if reasons or person is None:
        updated["acknowledgement"] = {
            "accepted": False,
            "reason": reasons[0] if reasons else "not_accepted",
            "actor_role_in_request_ignored": role_ignored,
        }
        return _lock(updated)
    updated["human_approval"] = {
        "approver_id": person["id"],
        "approver_role": person["role"],
        "role_taken_from": "directory",
        "actor_role_in_request_ignored": role_ignored,
        "meeting_id": updated.get("meeting_id"),
        "selected_source_ids": list(expected_ids),
        "approval_reference": selection.get("approval_reference"),
        "item_id": selection.get("item_id"),
        "effect": "seen",
        "performance_rating": None,
        "decides_performance": False,
    }
    updated["acknowledgement"] = {
        "accepted": True,
        "reason": "manager_seen_step",
        "actor_role_in_request_ignored": role_ignored,
    }
    return _lock(updated)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Draft a synthetic one-to-one prep note.")
    parser.add_argument("--pack", required=True, type=Path)
    parser.add_argument("--as-of", default=None)
    args = parser.parse_args(argv)
    try:
        pack = json.loads(args.pack.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        print("The pack could not be read.", file=sys.stderr)
        return 2
    if not isinstance(pack, dict):
        print("The pack is not an object.", file=sys.stderr)
        return 2
    json.dump(prepare(pack, args.as_of), sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
