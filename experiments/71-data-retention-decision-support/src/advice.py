#!/usr/bin/env python3
"""Retention advice for one synthetic record series.

The records owner or the legal owner decides retention, disposal, transfer,
and hold. This module does not delete, move, relabel, archive, transfer, or
send. A date is indicative. It is not a disposal decision.

The pinned schedule and the pinned inventory are the sources. A schedule or
an inventory pasted into the request is compared and not used. Instructions
in a title or a note are not followed. Approval words in the note are not
the seen step.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

if __package__ in {None, ""}:
    from cues import (
        biased_criteria,
        category_match,
        distress_flags,
        injection_flags,
        open_matter_flags,
    )
    from dates import add_period, iso, parse_date
    from marking import (
        above_ceiling,
        content_markings,
        higher_marking,
        legal_hold_flag,
        metadata_markings,
        retention_labels,
    )
    from mask import mask_text
    from match import canonical, differs, digest, period_months, sentence_supports
    from reuse import detect_classification, detect_urgency_flags, intake, propose
    from sources import citations
else:
    from .cues import (
        biased_criteria,
        category_match,
        distress_flags,
        injection_flags,
        open_matter_flags,
    )
    from .dates import add_period, iso, parse_date
    from .marking import (
        above_ceiling,
        content_markings,
        higher_marking,
        legal_hold_flag,
        metadata_markings,
        retention_labels,
    )
    from .mask import mask_text
    from .match import canonical, differs, digest, period_months, sentence_supports
    from .reuse import detect_classification, detect_urgency_flags, intake, propose
    from .sources import citations

ROOT = Path(__file__).resolve().parents[1]
LABEL = "RETENTION ADVICE FOR THE RECORDS OWNER"
CATALOGUE_ID = "L007"
SMALL_NUMBER_THRESHOLD = 5

_SEEN: dict[str, dict] = {}
_STRIP = {
    "approved",
    "human_approval",
    "approval",
    "decision",
    "disposal_authorised",
    "role",
    "clearance",
    "advice_hash",
    "seen",
}


class RetentionForbidden(RuntimeError):
    """Delete, move, relabel, archive, transfer, dispose, hold changes, and send are not tools."""


def delete_records() -> None:
    raise RetentionForbidden("delete")


def move_records() -> None:
    raise RetentionForbidden("move")


def relabel_records() -> None:
    raise RetentionForbidden("relabel")


def archive_records() -> None:
    raise RetentionForbidden("archive")


def transfer_records() -> None:
    raise RetentionForbidden("transfer")


def dispose() -> None:
    raise RetentionForbidden("dispose")


def apply_hold() -> None:
    raise RetentionForbidden("apply_hold")


def lift_hold() -> None:
    raise RetentionForbidden("lift_hold")


def send() -> None:
    raise RetentionForbidden("send")


def reset_seen() -> None:
    _SEEN.clear()


def pinned_sources() -> dict:
    folder = ROOT / "fixtures"
    return {
        "schedule": json.loads((folder / "schedule.json").read_text(encoding="utf-8")),
        "inventory": json.loads((folder / "inventory.json").read_text(encoding="utf-8")),
        "directory": json.loads((folder / "directory.json").read_text(encoding="utf-8")),
    }


def summarise_inventory(inventory: dict, threshold: object = SMALL_NUMBER_THRESHOLD) -> dict:
    """Replace counts from 1 up to the threshold with a band. Zero stays zero.

    The raw count is not returned. This is a starter control. It is not anonymisation.
    The ICO anonymisation guidance was not opened.
    """

    if type(threshold) is not int or isinstance(threshold, bool) or threshold < 2 or threshold > 100:
        return {
            "ok": False,
            "coerced": False,
            "reason": "threshold_unparseable",
            "described_as_anonymised": False,
            "raw_stored": False,
        }
    rows = inventory.get("series") if isinstance(inventory, dict) else None
    if not isinstance(rows, list):
        return {
            "ok": False,
            "coerced": False,
            "reason": "inventory_unparseable",
            "described_as_anonymised": False,
            "raw_stored": False,
        }

    def show(count: int) -> int | str:
        if count == 0:
            return 0
        if count < threshold:
            return f"<{threshold}"
        return count

    def count_where(predicate) -> int:
        return sum(1 for row in rows if isinstance(row, dict) and predicate(row))

    return {
        "ok": True,
        "coerced": False,
        "threshold": threshold,
        "series": show(sum(1 for row in rows if isinstance(row, dict))),
        "personal_data_series": show(count_where(lambda row: row.get("personal_data") is True)),
        "legal_hold_series": show(count_where(lambda row: row.get("legal_hold") is True)),
        "described_as_anonymised": False,
        "raw_stored": False,
        "note": "Counts from 1 to one below the threshold are replaced. This is not anonymisation.",
    }


def advise_retention(
    request: dict,
    schedule: dict,
    inventory: dict,
    directory: dict,
    as_of: str,
) -> dict:
    if not isinstance(request, dict):
        raise TypeError("request must be an object")
    working = {key: value for key, value in request.items() if key not in _STRIP}
    if working.get("synthetic") is not True:
        return _refused("not_synthetic", as_of)

    as_of_date, as_of_status = parse_date(as_of)
    series_id = working.get("series_id")
    row = _series(inventory, series_id)
    caller_schedule = working.get("caller_schedule")
    caller_inventory = working.get("caller_inventory")
    caller_directory = working.get("caller_directory")
    schedule_differs = differs(schedule, caller_schedule)
    inventory_differs = differs(inventory, caller_inventory)
    directory_differs = differs(directory, caller_directory)
    schedule_current, schedule_status = _schedule_current(schedule, as_of_date, as_of_status)

    base = _shell(
        as_of=as_of if isinstance(as_of, str) else None,
        as_of_status=as_of_status,
        series_id=series_id if isinstance(series_id, str) else None,
        schedule=schedule,
        schedule_current=schedule_current,
        schedule_status=schedule_status,
        schedule_differs=schedule_differs,
        inventory_differs=inventory_differs,
        directory_differs=directory_differs,
    )
    if row is None:
        base["outcome"] = "refer_to_owner"
        base["rule"] = None
        base["questions"] = [
            "This series id is not on the pinned inventory. The records owner must identify the series. A pasted inventory was not used."
        ]
        base["routes"] = ["records_owner"]
        return _finish(base)

    text = _text(row, working)
    mask = mask_text(text)
    neighbours = _neighbours(text, series_id, as_of_date)
    held, hold_unparseable = legal_hold_flag(row.get("legal_hold"), text)
    labels, labels_unparseable = retention_labels(row.get("retention_labels"), text)
    marking = _marking(row, working, text, directory)
    personal, personal_unparseable = _personal(row, text)
    opens, open_unparseable = _opens(row, text)
    distress = distress_flags(text)
    injection = injection_flags(text)
    rules, rules_bad = _active_rules(schedule, row.get("series_code"))
    conflict = len(rules) > 1
    chosen = rules[0] if len(rules) == 1 else None
    trigger_raw, trigger_problem = (None, "no_rule") if chosen is None else _trigger_raw(row, chosen)
    trigger_date, trigger_status = (None, "not_calculated") if chosen is None else parse_date(trigger_raw)
    if trigger_problem and chosen is not None:
        trigger_status = trigger_problem
        trigger_date = None
    indicative, indicative_status = _indicative(chosen, trigger_date, trigger_status)
    pra = _pra(row, as_of_date, caller_schedule)
    below = _below_schedule(caller_schedule, row.get("series_code"), rules)
    criteria_text = working.get("caller_criteria") if isinstance(working.get("caller_criteria"), str) else ""
    biased = biased_criteria(criteria_text)
    support_rows = []
    supplied_support = working.get("support_sentences")
    if isinstance(supplied_support, list):
        for item in supplied_support:
            if isinstance(item, str):
                support_rows.append(sentence_supports(item))
            else:
                support_rows.append({
                    "line_id": "SCH-FIN-01",
                    "supports": False,
                    "carve_out": False,
                    "denied": False,
                    "marked_acceptable": False,
                    "sentence_stored": False,
                    "unparseable": True,
                })
    carve = any(item.get("carve_out") for item in support_rows) or _carve_in_text(text)

    blocked = _blocked(
        held=held,
        hold_unparseable=hold_unparseable,
        opens=opens,
        open_unparseable=open_unparseable,
        conflict=conflict,
        no_rule=not rules,
        trigger_status=trigger_status if chosen else "no_rule",
        as_of_status=as_of_status,
        distress=distress["flagged"],
        pra_selected=pra["selected_for_permanent_preservation"],
        rules_bad=rules_bad,
    )
    questions = _questions(
        row=row,
        chosen=chosen,
        conflict=conflict,
        rules=rules,
        trigger_status=trigger_status if chosen else "no_rule",
        personal=personal or personal_unparseable,
        held=held or hold_unparseable,
        opens=opens,
        open_unparseable=open_unparseable,
        distress=distress["flagged"],
        pra=pra,
        below=below,
        biased=biased,
        injection=injection["detected"],
        schedule_differs=schedule_differs,
        carve=carve,
    )
    routes = ["records_owner"]
    if held or hold_unparseable or opens["litigation"] or opens["inquiry"] or distress["flagged"] or pra["selected_for_permanent_preservation"]:
        routes.append("legal_owner")

    acknowledgements = ["pins_seen"]
    if not schedule_current:
        acknowledgements.append("schedule_seen")
    if schedule_differs or inventory_differs or directory_differs:
        acknowledgements.append("sources_seen")
    if blocked or personal or personal_unparseable or distress["flagged"]:
        acknowledgements.append("route_seen")

    outcome = "refer_to_owner" if blocked else "single_rule_advice"
    base.update({
        "series_code": row.get("series_code") if isinstance(row.get("series_code"), str) else None,
        "owner_ref": row.get("owner_ref") if isinstance(row.get("owner_ref"), str) else None,
        "outcome": outcome,
        "routine_advice": outcome == "single_rule_advice" and not injection["detected"] and not distress["flagged"],
        "rule": _rule_view(chosen, row) if chosen and not conflict else None,
        "rules_cited": [_rule_view(rule, row) for rule in rules],
        "conflicting_rules": [rule.get("line_id") for rule in rules] if conflict else [],
        "ambiguous": conflict or trigger_status == "ambiguous",
        "trigger_date": iso(trigger_date) if not conflict else None,
        "trigger_date_status": trigger_status if not conflict else "not_chosen",
        "indicative_date": iso(indicative) if not conflict else None,
        "indicative_date_status": indicative_status if not conflict else "not_chosen",
        "indicative_date_is_a_disposal_decision": False,
        "schedule_date_not_a_disposal_recommendation": True,
        "schedule_indicative_action": chosen.get("indicative_action") if chosen and not conflict else None,
        "candidate_dates": [] if not conflict else _candidates(rules, row),
        "date_chosen": False,
        "disposal_suggested": False,
        "transfer_suggested": False,
        "advice_only": True,
        "marked_safe": False,
        "marked_acceptable": False,
        "criteria_applied": False,
        "biased_criteria": biased,
        "carve_out": carve,
        "questions": questions,
        "routes": routes,
        "human_route_available": True,
        "uk_gdpr_storage_limitation_question": bool(personal or personal_unparseable),
        "article_5_met": None,
        "offence_found": None,
        "pra_duty_met": None,
        "open_matters": opens,
        "open_matters_unparseable": open_unparseable,
        "legal_hold": {
            "held": held,
            "unparseable": hold_unparseable,
            "preserved": True,
            "lifted": False,
        },
        "retention_labels": labels,
        "retention_labels_unparseable": labels_unparseable,
        "retention_labels_preserved": True,
        "marking": marking,
        "pra": pra,
        "below_pinned_schedule": below["below"],
        "caller_period_status": below["status"],
        "caller_period_coerced": False,
        "personal_data_from_inventory": row.get("personal_data") is True,
        "personal_data_from_text": personal and row.get("personal_data") is not True,
        "distress": distress,
        "prompt_injection": injection,
        "instructions_followed": False,
        "self_declared_role_ignored": True,
        "self_declared_clearance_ignored": True,
        "mask": mask,
        "neighbours": neighbours,
        "support": support_rows,
        "required_acknowledgements": acknowledgements,
        "coerced": False,
        "text_copied": False,
        "content_recorded": False,
    })
    if neighbours.get("exp12", {}).get("catalogue_stale"):
        base["limitations"].append(
            "Experiment 12's catalogue window is that experiment's rule. It does not change the pinned retention schedule."
        )
    return _finish(base)


def record_advice_seen(advice: dict, directory: dict, seen: dict) -> dict:
    """Record that the directory owner has seen this advice hash. Nothing is deleted."""

    result = dict(advice)
    result["human_approval"] = None
    result["deleted"] = False
    result["moved"] = False
    result["relabelled"] = False
    result["archived"] = False
    result["sent"] = False
    result["records_changed"] = False
    result["disposal_authorised"] = False
    result["transfer_authorised"] = False
    result["advice_only"] = True
    result["may_be_relied_on_as_a_disposal_decision"] = False
    if not isinstance(seen, dict):
        return _reject(result, "seen_object_missing")
    if seen.get("item") != "retention-advice-seen" or seen.get("decision") != "seen":
        return _reject(result, "decision_not_accepted")
    for key in ("dispose", "delete", "archive", "transfer", "relabel", "send", "destroy"):
        if key in seen:
            return _reject(result, "decision_not_accepted")
    recomputed = _hash(advice)
    if advice.get("advice_hash") != recomputed or seen.get("advice_hash") != recomputed:
        return _reject(result, "advice_hash_mismatch")
    person = _person(directory, seen.get("approver_ref"))
    if person is None:
        return _reject(result, "approver_not_in_directory")
    role = person.get("role")
    if role == "legal_owner":
        pass
    elif role == "records_owner" and person.get("ref") == advice.get("owner_ref"):
        pass
    else:
        return _reject(result, "approver_role_rejected")
    required = advice.get("required_acknowledgements") or []
    for name in required:
        if seen.get(name) is not True:
            return _reject(result, f"acknowledgement_missing:{name}")
    stored = {
        "item": "retention-advice-seen",
        "approver_ref": person["ref"],
        "role": role,
        "advice_hash": recomputed,
        "effect": "seen_only",
        "records_changed": False,
    }
    _SEEN[recomputed] = stored
    result["human_approval"] = stored
    result["advice_seen"] = True
    result["may_be_relied_on_as_a_disposal_decision"] = False
    return result


def _refused(reason: str, as_of: object) -> dict:
    base = _shell(
        as_of=as_of if isinstance(as_of, str) else None,
        as_of_status="not_read",
        series_id=None,
        schedule={"schedule_id": None},
        schedule_current=False,
        schedule_status="not_read",
        schedule_differs=False,
        inventory_differs=False,
        directory_differs=False,
    )
    base["outcome"] = "refused"
    base["blocked_reason"] = reason
    base["questions"] = ["The request was not marked synthetic. Nothing was calculated."]
    base["routes"] = ["records_owner"]
    return _finish(base)


def _shell(
    *,
    as_of,
    as_of_status,
    series_id,
    schedule,
    schedule_current,
    schedule_status,
    schedule_differs,
    inventory_differs,
    directory_differs,
) -> dict:
    return {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment": "71-data-retention-decision-support",
        "autonomy": "A0",
        "synthetic": True,
        "as_of": as_of,
        "as_of_status": as_of_status,
        "series_id": series_id,
        "schedule_used": "pinned",
        "schedule_id": schedule.get("schedule_id") if isinstance(schedule, dict) else None,
        "schedule_current": schedule_current,
        "schedule_status": schedule_status,
        "sources_current": schedule_current and as_of_status == "ok",
        "may_be_relied_on_as_a_disposal_decision": False,
        "caller_sources": {
            "schedule_differs": schedule_differs,
            "inventory_differs": inventory_differs,
            "directory_differs": directory_differs,
            "used": "pinned",
        },
        "context_for_records_owner": citations(),
        "disposal_suggested": False,
        "transfer_suggested": False,
        "deleted": False,
        "moved": False,
        "relabelled": False,
        "archived": False,
        "sent": False,
        "records_changed": False,
        "disposal_authorised": False,
        "human_approval": None,
        "advice_seen": False,
        "coerced": False,
        "marked_safe": False,
        "marked_acceptable": False,
        "criteria_applied": False,
        "instructions_followed": False,
        "text_copied": False,
        "questions": [],
        "routes": ["records_owner"],
        "human_route_available": True,
        "limitations": [
            "Phrase lists miss a wording that uses none of the stems.",
            "The section 46 code was not opened. Article 84B was not opened. Transitional orders under the Public Records Act were not opened.",
            "A calculated date is not a decision to dispose, transfer, or hold.",
        ],
    }


def _finish(result: dict) -> dict:
    result["advice_hash"] = _hash(result)
    return result


def _hash(result: dict) -> str:
    body = {key: value for key, value in result.items() if key not in {"advice_hash", "human_approval"}}
    return digest(body)


def _reject(result: dict, reason: str) -> dict:
    result = dict(result)
    result["human_approval"] = None
    result["advice_seen"] = False
    result["blocked_reason"] = reason
    result["deleted"] = False
    result["moved"] = False
    result["relabelled"] = False
    result["archived"] = False
    result["sent"] = False
    result["records_changed"] = False
    result["disposal_authorised"] = False
    result["may_be_relied_on_as_a_disposal_decision"] = False
    return result


def _series(inventory: dict, series_id: object) -> dict | None:
    if not isinstance(series_id, str) or not isinstance(inventory, dict):
        return None
    for row in inventory.get("series", []):
        if isinstance(row, dict) and row.get("series_id") == series_id:
            return row
    return None


def _text(row: dict, request: dict) -> str:
    parts = []
    for value in (row.get("content"), request.get("content"), request.get("title"), row.get("title")):
        if isinstance(value, str) and value:
            parts.append(value)
    return "\n".join(parts)


def _person(directory: dict, ref: object) -> dict | None:
    if not isinstance(ref, str) or not isinstance(directory, dict):
        return None
    for person in directory.get("people", []):
        if isinstance(person, dict) and person.get("ref") == ref:
            return person
    return None


def _schedule_current(schedule: dict, as_of_date: date | None, as_of_status: str) -> tuple[bool, str]:
    if as_of_status != "ok" or as_of_date is None or not isinstance(schedule, dict):
        return False, "question_date_not_usable"
    review, status = parse_date(schedule.get("next_review"))
    if status != "ok" or review is None:
        return False, "review_date_unparseable"
    if as_of_date >= review:
        return False, "stale"
    return True, "current"


def _active_rules(schedule: dict, series_code: object) -> tuple[list[dict], bool]:
    if not isinstance(series_code, str) or not isinstance(schedule, dict):
        return [], True
    found = []
    bad = False
    for rule in schedule.get("rules", []):
        if not isinstance(rule, dict):
            bad = True
            continue
        if rule.get("series_code") != series_code:
            continue
        if rule.get("status") != "active":
            continue
        found.append(rule)
    return found, bad


def _trigger_raw(row: dict, rule: dict) -> tuple[object, str | None]:
    event = rule.get("trigger")
    if row.get("trigger_event") != event:
        return None, "trigger_mismatch"
    raw = row.get("trigger_date")
    field = {"date_closed": "closed", "date_created": "created"}.get(event)
    if field is not None:
        other = row.get(field)
        if other not in (None, "") and raw not in (None, "") and other != raw:
            return None, "trigger_fields_differ"
    return raw, None


def _indicative(rule: dict | None, trigger: date | None, status: str) -> tuple[date | None, str]:
    if rule is None or trigger is None or status != "ok":
        return None, "not_calculated"
    years = rule.get("period_years")
    months = rule.get("period_months")
    value, period_status = add_period(trigger, years, months)
    if period_status != "ok":
        return None, period_status
    return value, "ok"


def _candidates(rules: list[dict], row: dict) -> list[dict]:
    rows = []
    for rule in rules:
        raw, problem = _trigger_raw(row, rule)
        parsed, status = (None, problem) if problem else parse_date(raw)
        if problem:
            status = problem
        when, period_status = _indicative(rule, parsed, "ok" if parsed and not problem else "not_calculated")
        rows.append({
            "line_id": rule.get("line_id"),
            "status": "not_chosen",
            "date": iso(when) if period_status == "ok" else None,
            "date_status": period_status if not problem else status,
            "chosen": False,
        })
    return rows


def _rule_view(rule: dict, row: dict) -> dict:
    return {
        "line_id": rule.get("line_id"),
        "schedule_line": rule.get("line_id"),
        "why": (
            "The pinned inventory series code matches this active line on the pinned schedule. "
            "A withdrawn line was not used. A schedule pasted into the request was not used."
        ),
        "series_code": row.get("series_code"),
        "trigger": rule.get("trigger"),
        "period_years": rule.get("period_years") if type(rule.get("period_years")) is int else None,
        "period_months": rule.get("period_months") if type(rule.get("period_months")) is int else None,
        "indicative_action_on_the_schedule": rule.get("indicative_action"),
        "citation": f"Pinned schedule line {rule.get('line_id')}",
        "statutory_period": False,
    }


def _boolish(value: object) -> tuple[bool, bool]:
    if value is True:
        return True, False
    if value is False:
        return False, False
    if value is None:
        return False, True
    return False, True


def _opens(row: dict, text: str) -> tuple[dict, bool]:
    text_flags = open_matter_flags(text)
    unparseable = False
    flags = {}
    for key, name in (
        ("open_foi", "foi"),
        ("open_sar", "sar"),
        ("open_litigation", "litigation"),
        ("open_inquiry", "inquiry"),
    ):
        affirmed_flag, bad = _boolish(row.get(key))
        unparseable = unparseable or bad
        flags[name] = affirmed_flag or text_flags[name]
    return flags, unparseable


def _personal(row: dict, text: str) -> tuple[bool, bool]:
    inventory_flag, bad = _boolish(row.get("personal_data"))
    from_text = category_match(text, "personal_data")
    return inventory_flag or from_text, bad


def _marking(row: dict, request: dict, text: str, directory: dict) -> dict:
    meta_values = [row.get("protective_marking"), request.get("protective_marking")]
    from_meta, meta_bad = metadata_markings(meta_values)
    from_content = content_markings(text)
    applied = higher_marking(from_meta + from_content)
    caller = _person(directory, request.get("caller_ref"))
    ceiling = caller.get("clearance") if caller else None
    return {
        "applied": applied,
        "from_metadata": from_meta,
        "from_content": from_content,
        "metadata_unparseable": meta_bad,
        "self_declared_clearance_ignored": True,
        "caller_in_directory": caller is not None,
        "caller_clearance": ceiling if isinstance(ceiling, str) else None,
        "above_clearance": above_ceiling(applied, ceiling if isinstance(ceiling, str) else None),
        "content_withheld": True,
        "content_copied": False,
    }


def _pra(row: dict, as_of_date: date | None, caller_schedule: object) -> dict:
    public_record, public_bad = _boolish(row.get("public_record"))
    selected, selected_bad = _boolish(row.get("selected_for_permanent_preservation"))
    created, created_status = parse_date(row.get("created"))
    latest = None
    latest_status = "not_applicable"
    appears_passed = False
    if public_record and selected and created_status == "ok" and created is not None:
        latest_date, latest_status = add_period(created, 20, 0)
        latest = iso(latest_date)
        if latest_date is not None and as_of_date is not None and as_of_date > latest_date:
            appears_passed = True
    conflicts = False
    later = False
    if isinstance(caller_schedule, dict):
        for rule in caller_schedule.get("rules", []):
            if not isinstance(rule, dict) or rule.get("series_code") != row.get("series_code"):
                continue
            action = rule.get("indicative_action")
            if isinstance(action, str) and action.casefold() in {"destroy", "dispose", "disposal", "delete"}:
                conflicts = True
            months, status = period_months(rule.get("period_years"), rule.get("period_months", 0))
            if public_record and selected and status == "ok" and months is not None and months > 20 * 12:
                later = True
    return {
        "applies": bool(public_record and selected),
        "public_record": public_record,
        "selected_for_permanent_preservation": bool(public_record and selected),
        "unparseable": public_bad or selected_bad,
        "section": "3(4)" if public_record and selected else None,
        "transfer_latest": latest,
        "transfer_latest_status": latest_status,
        "s3_4_latest_appears_passed": appears_passed,
        "finding_of_breach": False,
        "transitional_order_checked": False,
        "conflicts_with_s3_4": conflicts and bool(public_record and selected),
        "later_than_s3_4_latest": later,
        "disposal_suggested": False,
        "note": (
            "Section 3(4) is context where the pinned inventory says the series is a public record "
            "selected for permanent preservation. The 20 years is the latest transfer point in the "
            "text that was opened. It is not applied to other series. The proviso and section 3(4A) "
            "were not applied."
        ),
    }


def _below_schedule(caller_schedule: object, series_code: object, rules: list[dict]) -> dict:
    pinned_periods = []
    for rule in rules:
        months, status = period_months(rule.get("period_years"), rule.get("period_months"))
        if status == "ok" and months is not None:
            pinned_periods.append(months)
    if caller_schedule is None:
        return {"below": False, "status": "not_supplied", "coerced": False}
    if not isinstance(caller_schedule, dict):
        return {"below": False, "status": "unparseable", "coerced": False}
    shortest = min(pinned_periods) if pinned_periods else None
    statuses = []
    below = False
    for rule in caller_schedule.get("rules", []):
        if not isinstance(rule, dict) or rule.get("series_code") != series_code:
            continue
        months, status = period_months(rule.get("period_years"), rule.get("period_months", 0) if "period_months" in rule else 0)
        if "period_months" not in rule and type(rule.get("period_years")) is int:
            months, status = period_months(rule.get("period_years"), 0)
        statuses.append(status)
        if status == "ok" and months is not None and shortest is not None and months < shortest:
            below = True
    if not statuses:
        return {"below": False, "status": "no_line_for_series", "coerced": False}
    if any(item != "ok" for item in statuses):
        return {"below": below, "status": "unparseable", "coerced": False}
    return {"below": below, "status": "compared", "coerced": False}


def _blocked(
    *,
    held,
    hold_unparseable,
    opens,
    open_unparseable,
    conflict,
    no_rule,
    trigger_status,
    as_of_status,
    distress,
    pra_selected,
    rules_bad,
) -> bool:
    if held or hold_unparseable or conflict or no_rule or distress or pra_selected or rules_bad:
        return True
    if open_unparseable or any(opens.values()):
        return True
    if as_of_status != "ok":
        return True
    if trigger_status != "ok":
        return True
    return False


def _questions(**flags) -> list[str]:
    questions = [
        "Does this series code still describe the records?",
        "Who will decide retention, disposal, transfer, or hold? This advice does not decide.",
    ]
    if not flags["chosen"] and not flags["conflict"]:
        questions.append("No active pinned line matches this series code. Which line should the records owner consider?")
    if flags["conflict"]:
        questions.append("More than one active pinned line matches. Which line, if either, should be used? Neither date was chosen.")
    if flags["trigger_status"] not in {"ok", "no_rule", "not_chosen"}:
        questions.append(
            "The trigger date is missing, ambiguous, or not a calendar date, or it does not match the rule. It was not replaced with today. What is the trigger date?"
        )
    if flags["personal"]:
        questions.append(
            "Personal data appears on the pinned inventory or in the note. Is continued storage still necessary for the purpose? "
            "UK GDPR Article 5(1)(e) is quoted for the records owner. This is not a finding that the principle was met or broken."
        )
    if flags["held"]:
        questions.append("A legal hold is on the pinned row or the note. Disposal is not suggested. Does the hold still apply?")
    if any(flags["opens"].values()) or flags["open_unparseable"]:
        questions.append(
            "An open FOI, SAR, litigation, or inquiry flag is set, or the flag could not be read. "
            "Disposal is not suggested. Section 77 is context for the records owner, not a finding of an offence."
        )
    if flags["distress"]:
        questions.append("The note has a distress, vulnerability, or safeguarding cue. A person should see it. The cue text is not copied.")
    if flags["pra"]["applies"]:
        questions.append(
            "The pinned inventory says this is a public record selected for permanent preservation. "
            "Section 3(4) is quoted. Disposal is not suggested. The transitional order was not checked."
        )
    if flags["below"]["below"] or flags["below"]["status"] == "unparseable":
        questions.append("A period in the pasted schedule is shorter than the pinned line, or it could not be read. The pinned line was used. It was not marked safe.")
    if flags["biased"]:
        questions.append("The pasted criteria look biased or leading. They were not applied.")
    if flags["injection"]:
        questions.append("The title or the note contained an instruction. It was not followed.")
    if flags["schedule_differs"]:
        questions.append("The pasted schedule or inventory differs from the pinned source. The pinned source was used.")
    if flags["carve"]:
        questions.append("A qualification follows the retention wording. It was not marked acceptable.")
    return questions


def _carve_in_text(text: str) -> bool:
    if not text:
        return False
    row = sentence_supports(text)
    return bool(row["carve_out"])


def _neighbours(text: str, series_id: object, as_of_date: date | None) -> dict:
    classification = detect_classification()(text)
    urgency = detect_urgency_flags()(text)
    proposal = propose()(text, caller="exp-71-data-retention-decision-support", reversible=False)
    findings = proposal.get("audit_log", {}).get("findings", [])
    intake_summary = {
        "called": False,
        "files_confirmed": False,
        "purpose_confirmed": False,
        "content_recorded": False,
        "catalogue_stale": None,
    }
    if as_of_date is not None and isinstance(series_id, str):
        batch = {
            "synthetic": True,
            "batch_id": series_id,
            "files": [{
                "file_id": "series-note",
                "filename": "series-note.txt",
                "media_type": "text/plain",
                "content": text,
            }],
        }
        draft = intake()(batch, as_of=as_of_date)
        intake_summary = {
            "called": True,
            "files_confirmed": draft.get("files_confirmed") is True,
            "purpose_confirmed": draft.get("purpose_confirmed") is True,
            "content_recorded": False,
            "catalogue_stale": draft.get("catalogue_stale") is True,
        }
    return {
        "exp01": {
            "called": True,
            "primary_type": classification.get("primary_type"),
            "urgency_level": urgency.get("urgency_level"),
            "safeguarding_concern": urgency.get("safeguarding_concern") is True,
            "text_copied": False,
            "used_as_a_determination": False,
        },
        "exp08": {
            "called": True,
            "finding_count": len(findings) if isinstance(findings, list) else None,
            "values_stored": False,
            "reversible": False,
            "described_as_anonymised": False,
            "redacted_text_copied": False,
        },
        "exp12": intake_summary,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Retention advice for one synthetic series")
    parser.add_argument("--request", required=True)
    parser.add_argument("--as-of", required=True)
    args = parser.parse_args(argv)
    try:
        request = json.loads(Path(args.request).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return 2
    if not isinstance(request, dict):
        return 2
    pinned = pinned_sources()
    result = advise_retention(
        request,
        pinned["schedule"],
        pinned["inventory"],
        pinned["directory"],
        args.as_of,
    )
    json.dump(result, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
