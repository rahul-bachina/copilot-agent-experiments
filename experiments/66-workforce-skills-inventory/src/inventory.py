#!/usr/bin/env python3
"""Propose skills from evidence the employee supplied for this purpose.

The same inputs and the same as-of date produce the same JSON. Confirmation
is a later call, bound to the inventory hash and the skill hash. Words inside
the evidence are not that call. Nothing is written to an HR system.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from copy import deepcopy
from datetime import date
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from injection import scan_text, without_instruction_sentences
    from marking import (
        above_ceiling,
        content_markings,
        higher_marking,
        legal_hold,
        retention_labels,
    )
    from mask import mask_text
    from reuse import NeighbourMissing, learning_plan, mobility_note, redact_uk_identifiers
    from sources import LAST_VERIFIED, pins_current, source_rows
    from words import (
        EXAMPLE_NOTE,
        PURPOSE_MISUSE,
        affirmed,
        affirmed_sentence,
        family_hit,
        sentence_has_health_or_protected,
    )
else:
    from .injection import scan_text, without_instruction_sentences
    from .marking import (
        above_ceiling,
        content_markings,
        higher_marking,
        legal_hold,
        retention_labels,
    )
    from .mask import mask_text
    from .reuse import NeighbourMissing, learning_plan, mobility_note, redact_uk_identifiers
    from .sources import LAST_VERIFIED, pins_current, source_rows
    from .words import (
        EXAMPLE_NOTE,
        PURPOSE_MISUSE,
        affirmed,
        affirmed_sentence,
        family_hit,
        sentence_has_health_or_protected,
    )

LABEL = "PROPOSAL ONLY. NOT A PERFORMANCE RATING AND NOT AN HR RECORD."
CATALOGUE_ID = "H010"
EXPERIMENT_ID = "exp-66-workforce-skills-inventory"
AUTONOMY = "A0"
ORGANISATION = "Ashcombe Borough Council (fictional)"
FRAMEWORK_NOTE = (
    "Example framework only. The labels follow a SFIA-style skill-and-level shape "
    "so a reader can see the fields. This is not SFIA. SFIA is a licensed framework. "
    "The organisation must license any framework it uses and must review these phrases."
)

EMPLOYEE_REF = re.compile(r"^EMP-\d{4}$")
EVIDENCE_ID = re.compile(r"^EV-\d{3,4}$")
SKILL_ID = re.compile(r"^SKL-[A-Z0-9-]{2,24}$")
DAY = re.compile(r"^\d{4}-\d{2}-\d{2}$")
KINDS = frozenset({"cv_extract", "learning_record", "project_summary"})
CHANNELS = frozenset(
    {"employee_supplied", "monitoring", "mailbox", "absence", "manager_notes", "health_record"}
)

PROHIBITED_KEYS = frozenset(
    {
        "approved",
        "human_approval",
        "employee_confirmed",
        "hr_validated",
        "confirmed",
        "performance_rating",
        "clearance",
        "role",
        "role_id",
        "content_hash",
        "inventory_hash",
        "age",
        "disability",
        "sickness",
        "maternity",
    }
)
DIRECTORY_FIELDS = ("employee_ref", "role", "clearance", "team_id")
TRANSPARENCY_FIELDS = (
    "controller_identity_stated",
    "purpose_stated",
    "lawful_basis_stated_by_controller",
    "rights_access_rectification_erasure_restriction_object_portability_stated",
    "right_to_object_brought_to_attention",
)


class InventoryForbidden(RuntimeError):
    """Raised when a caller asks the agent to write, rate, or decide."""


def write_hr(*_args, **_kwargs) -> None:
    raise InventoryForbidden("the agent does not write to an HR system")


def rate_performance(*_args, **_kwargs) -> None:
    raise InventoryForbidden("the agent does not rate performance")


def set_pay(*_args, **_kwargs) -> None:
    raise InventoryForbidden("the agent does not set pay")


def decide_promotion(*_args, **_kwargs) -> None:
    raise InventoryForbidden("the agent does not decide promotion")


def select_for_redundancy(*_args, **_kwargs) -> None:
    raise InventoryForbidden("the agent does not select anyone for redundancy")


def decide_discipline(*_args, **_kwargs) -> None:
    raise InventoryForbidden("the agent does not make a disciplinary decision")


def infer_from_protected(*_args, **_kwargs) -> None:
    raise InventoryForbidden("the agent does not infer skills from a protected characteristic or from health data")


def profile_unsupplied(*_args, **_kwargs) -> None:
    raise InventoryForbidden("the agent does not profile people from data they did not supply for this purpose")


def _sha(payload: object) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _parse_day(value: object) -> date | None:
    if not isinstance(value, str) or not DAY.fullmatch(value):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _strict_bool(value: object) -> bool | None:
    if isinstance(value, bool):
        return value
    return None


def _flags() -> dict:
    return {
        "wrote_to_hr_system": False,
        "performance_rated": False,
        "pay_decision": False,
        "promotion_decision": False,
        "redundancy_decision": False,
        "disciplinary_decision": False,
        "solely_automated_decision": False,
        "article_6_basis_decided": False,
        "article_13_met": False,
        "article_21_grounds_decided": False,
        "article_22a_significant_decision_decided": False,
        "special_category_condition_decided": False,
        "output_is_anonymised": False,
        "instructions_followed": False,
        "coerced": False,
        "profiled_from_unsupplied_data": False,
        "inferred_from_protected_or_health": False,
        "employee_can_still_reject": True,
    }


def _base(as_of: str) -> dict:
    return {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment_id": EXPERIMENT_ID,
        "autonomy": AUTONOMY,
        "organisation": ORGANISATION,
        "as_of": as_of if isinstance(as_of, str) else "",
        "question_date_respected": True,
        "today_not_used": True,
        "sources_current": False,
        "may_be_relied_on": False,
        "framework_note": FRAMEWORK_NOTE,
        "pattern_note": EXAMPLE_NOTE,
        "proposals": [],
        "team_view": None,
        "skipped": [],
        "human_approval": None,
        "human_route": None,
        "flags": _flags(),
        "coerced": False,
        "copy_report": {
            "raw_evidence_copied": False,
            "identifier_values_copied": False,
            "directory_names_copied": False,
            "directory_protected_fields_read": False,
            "snippets_are_masked_sentences": True,
            "legal_holds_dropped": False,
            "retention_labels_dropped": False,
            "output_described_as_anonymised": False,
        },
        "experiment_08": {"called": False, "output_is_anonymised": False, "values_stored": False},
        "experiment_61": {
            "called": False,
            "enrolled": False,
            "used_as_a_performance_or_promotion_factor": False,
            "reason": "not_requested_or_no_confirmed_skill",
        },
        "experiment_62": {
            "called": False,
            "selection_made": False,
            "used_as_a_selection_factor": False,
            "inferred_skills_passed": False,
            "reason": "not_requested",
        },
    }


def _person(directory: dict, ref: object) -> dict | None:
    if not isinstance(directory, dict):
        return None
    for person in directory.get("employees") or []:
        if isinstance(person, dict) and person.get("employee_ref") == ref:
            return {field: person.get(field) for field in DIRECTORY_FIELDS}
    return None


def _strip(request: dict) -> tuple[dict, list[str]]:
    clean = {}
    stripped = []
    for key, value in request.items():
        if key in PROHIBITED_KEYS:
            stripped.append(key)
            continue
        clean[key] = value
    return clean, stripped


def _finish(result: dict, outcome: str, statement: str) -> dict:
    result["outcome"] = outcome
    result["statement"] = statement
    result["may_be_relied_on"] = False
    result["flags"]["instructions_followed"] = False
    result["flags"]["coerced"] = False
    result["coerced"] = False
    return result


def _skill_hash(row: dict) -> str:
    payload = {
        "skill_id": row.get("skill_id"),
        "confidence_band": row.get("confidence_band"),
        "evidence_ids": [item.get("evidence_id") for item in row.get("evidence") or []],
        "snippets": [item.get("snippet") for item in row.get("evidence") or []],
    }
    return _sha(payload)


def _inventory_hash(result: dict) -> str:
    payload = {
        "employee_ref": result.get("employee_ref"),
        "as_of": result.get("as_of"),
        "skills": [
            {"skill_id": row.get("skill_id"), "skill_hash": row.get("skill_hash")}
            for row in result.get("proposals") or []
        ],
    }
    return _sha(payload)


def _transparency(record: object) -> dict:
    gaps = []
    unreadable = []
    if not isinstance(record, dict):
        return {"gaps": ["record_missing"], "unreadable": [], "article_13_met": False}
    for field in TRANSPARENCY_FIELDS:
        value = _strict_bool(record.get(field))
        if value is None:
            unreadable.append(field)
        elif value is False:
            gaps.append(field)
    return {"gaps": gaps, "unreadable": unreadable, "article_13_met": False}


def _threshold(framework: dict) -> tuple[int | None, bool, bool]:
    if "small_number_threshold" not in framework:
        return 5, True, False
    raw = framework.get("small_number_threshold")
    if isinstance(raw, bool) or not isinstance(raw, int) or raw < 2 or raw > 100:
        return None, False, True
    return raw, False, False


def _band(kinds: list[str]) -> str | None:
    distinct = len(kinds)
    if distinct >= 2:
        return "high"
    if distinct == 1 and kinds[0] in {"learning_record", "project_summary"}:
        return "medium"
    if distinct == 1 and kinds[0] == "cv_extract":
        return "low"
    return None


def _cite(sentence: str, cache: dict) -> tuple[str, dict]:
    masked, local = mask_text(sentence)
    try:
        uk = redact_uk_identifiers(masked)
        shown = uk["text"].strip()
        cache["called"] = True
        cache["count"] = cache.get("count", 0) + uk["count"]
        for kind in uk["types"]:
            if kind not in cache["types"]:
                cache["types"].append(kind)
    except NeighbourMissing:
        shown = masked.strip()
        uk = {"called": False, "output_is_anonymised": False, "values_stored": False, "count": 0, "types": []}
    if len(shown) > 240:
        shown = shown[:240]
    local_counts = local["counts"]
    for key, count in local_counts.items():
        cache["local"][key] = cache["local"].get(key, 0) + count
    return shown, {"local": local, "uk": {"called": uk.get("called", cache["called"]), "output_is_anonymised": False}}


def _item_text(item: dict) -> str:
    return item.get("text") if isinstance(item.get("text"), str) else ""


def _usable_item(item: dict, employee_ref: str, day: date, ceiling: str) -> tuple[bool, dict | None]:
    """Return whether the item may support a skill, and a skip row if not."""

    evidence_id = item.get("evidence_id")
    skip = {
        "evidence_id": evidence_id if isinstance(evidence_id, str) else None,
        "reason": "",
        "legal_hold": False,
        "retention_labels": [],
        "marking": None,
        "body_withheld": False,
        "coerced": False,
    }
    text = _item_text(item)
    labels, bad_retention = retention_labels(item.get("retention_labels"), text)
    skip["retention_labels"] = labels
    skip["retention_unreadable"] = bad_retention
    skip["legal_hold"] = legal_hold(item.get("legal_hold"), text)
    meta_mark = item.get("marking")
    if meta_mark is not None and not isinstance(meta_mark, str):
        skip["reason"] = "marking_unreadable"
        skip["body_withheld"] = True
        return False, skip
    marking = higher_marking(([meta_mark] if isinstance(meta_mark, str) else []) + content_markings(text))
    skip["marking"] = marking
    if above_ceiling(marking, ceiling):
        skip["reason"] = "above_clearance"
        skip["body_withheld"] = True
        return False, skip
    if item.get("employee_ref") != employee_ref and item.get("employee_ref") is not None:
        skip["reason"] = "other_employee"
        return False, skip
    if item.get("supplied_for") != "skills_inventory":
        skip["reason"] = "not_supplied_for_this_purpose"
        return False, skip
    consent = _strict_bool(item.get("consent_for_this_purpose"))
    if consent is None:
        skip["reason"] = "consent_unreadable"
        return False, skip
    if consent is False:
        skip["reason"] = "consent_not_recorded"
        return False, skip
    channel = item.get("source_channel")
    if channel not in CHANNELS:
        skip["reason"] = "channel_unreadable"
        return False, skip
    if channel != "employee_supplied":
        skip["reason"] = "not_supplied_for_this_purpose"
        return False, skip
    if item.get("kind") not in KINDS:
        skip["reason"] = "kind_unreadable"
        return False, skip
    supplied = _parse_day(item.get("supplied_on")) if item.get("supplied_on") is not None else day
    if item.get("supplied_on") is not None and supplied is None:
        skip["reason"] = "date_unreadable"
        return False, skip
    if supplied is not None and supplied > day:
        skip["reason"] = "not_yet_supplied"
        return False, skip
    if item.get("review_due") is not None:
        review = _parse_day(item.get("review_due"))
        if review is None:
            skip["reason"] = "date_unreadable"
            return False, skip
        if review < day:
            skip["reason"] = "stale"
            return False, skip
    return True, None


def _proposals_for(items: list[dict], skills: list[dict], cache: dict) -> list[dict]:
    rows = []
    for skill in skills:
        if not isinstance(skill, dict) or not isinstance(skill.get("skill_id"), str):
            continue
        if not SKILL_ID.fullmatch(skill["skill_id"]):
            continue
        phrases = [phrase for phrase in (skill.get("phrases") or []) if isinstance(phrase, str) and phrase.strip()]
        if not phrases:
            continue
        evidence_rows = []
        kinds = []
        holds = False
        labels: list[str] = []
        markings: list[str] = []
        for item in items:
            cleaned = without_instruction_sentences(_item_text(item))
            sentence = None
            matched = None
            for phrase in phrases:
                found = affirmed_sentence(cleaned, phrase)
                if found is None:
                    continue
                if sentence_has_health_or_protected(found):
                    continue
                sentence = found
                matched = phrase
                break
            if sentence is None or matched is None:
                continue
            snippet, _detail = _cite(sentence, cache)
            if affirmed(snippet, matched) is False and matched.casefold() not in snippet.casefold():
                continue
            evidence_rows.append(
                {
                    "evidence_id": item.get("evidence_id"),
                    "kind": item.get("kind"),
                    "snippet": snippet,
                    "phrase": matched,
                }
            )
            kinds.append(item.get("kind"))
            text = _item_text(item)
            holds = holds or legal_hold(item.get("legal_hold"), text)
            item_labels, _bad = retention_labels(item.get("retention_labels"), text)
            for label in item_labels:
                if label not in labels:
                    labels.append(label)
            meta = item.get("marking") if isinstance(item.get("marking"), str) else None
            marking = higher_marking(([meta] if meta else []) + content_markings(text))
            if marking:
                markings.append(marking)
        band = _band([kind for kind in kinds if isinstance(kind, str)])
        if band is None or not evidence_rows:
            continue
        row = {
            "skill_id": skill["skill_id"],
            "name": skill.get("name") if isinstance(skill.get("name"), str) else skill["skill_id"],
            "state": "needs_employee_confirmation",
            "employee_confirmed": False,
            "employee_rejected": False,
            "hr_validated": False,
            "confidence_band": band,
            "confidence_is_not_a_performance_rating": True,
            "performance_rating": None,
            "evidence": evidence_rows,
            "legal_hold": holds,
            "retention_labels": labels,
            "marking": higher_marking(markings),
            "correction": None,
            "correction_hash": None,
        }
        row["skill_hash"] = _skill_hash(row)
        rows.append(row)
    rows.sort(key=lambda item: item["skill_id"])
    return rows


def _team_view(pack_items: list[dict], skills: list[dict], team_id: str | None, day: date, ceiling: str, threshold: int | None, defaulted: bool, unreadable: bool) -> dict:
    view = {
        "team_id": team_id,
        "threshold": threshold,
        "threshold_is_a_starter_default": defaulted,
        "threshold_unreadable": unreadable,
        "statutory_threshold": False,
        "output_is_anonymised": False,
        "suppression_is_not_anonymisation": True,
        "employee_refs_listed": False,
        "snippets_listed": False,
        "cells": [],
        "coerced": False,
    }
    if unreadable or threshold is None or not team_id:
        view["suppressed_because"] = "threshold_unreadable" if unreadable or threshold is None else "no_team"
        return view
    members: set[str] = set()
    usable_by_person: dict[str, list[dict]] = {}
    for item in pack_items:
        if not isinstance(item, dict):
            continue
        ref = item.get("employee_ref")
        if not isinstance(ref, str) or not EMPLOYEE_REF.fullmatch(ref):
            continue
        if item.get("team_id") != team_id:
            continue
        members.add(ref)
        ok, _skip = _usable_item(item, ref, day, ceiling)
        if ok:
            usable_by_person.setdefault(ref, []).append(item)
    team_size = len(members)
    view["team_size_suppressed"] = team_size < threshold
    if team_size < threshold:
        view["team_size"] = None
        view["suppressed_because"] = "small_team"
        return view
    view["team_size"] = team_size
    for skill in skills:
        if not isinstance(skill, dict):
            continue
        phrases = [phrase for phrase in (skill.get("phrases") or []) if isinstance(phrase, str)]
        holders: set[str] = set()
        for ref, items in usable_by_person.items():
            blob = " ".join(without_instruction_sentences(_item_text(item)) for item in items)
            if any(
                affirmed(blob, phrase)
                and not sentence_has_health_or_protected(affirmed_sentence(blob, phrase) or "")
                for phrase in phrases
            ):
                holders.add(ref)
        count = len(holders)
        complement = team_size - count
        suppressed = count < threshold or complement < threshold
        view["cells"].append(
            {
                "skill_id": skill.get("skill_id"),
                "count": None if suppressed else count,
                "suppressed": suppressed,
                "reason": "small_number" if suppressed else None,
            }
        )
    return view


def propose_inventory(
    request: dict,
    evidence: dict,
    framework: dict,
    directory: dict,
    transparency: dict,
    as_of: str,
) -> dict:
    """Return proposals. Every skill stays needs_employee_confirmation."""

    result = _base(as_of if isinstance(as_of, str) else "")
    if not all(isinstance(item, dict) for item in (request, evidence, framework, directory)):
        return _finish(result, "refused", "The input could not be read. Nothing was copied.")
    for blob, name in (
        (evidence, "evidence"),
        (framework, "framework"),
        (directory, "directory"),
    ):
        if blob.get("synthetic") is not True:
            return _finish(result, "refused", f"The {name} file is not marked synthetic. Nothing was copied.")
    if request.get("synthetic") is not True:
        return _finish(result, "refused", "The request is not marked synthetic. Nothing was copied.")
    if framework.get("example_only") is not True:
        return _finish(
            result,
            "refused",
            "The framework is not marked as an example the organisation must license and review. Nothing was copied.",
        )

    clean, stripped = _strip(request)
    items = [item for item in (evidence.get("items") or []) if isinstance(item, dict)]
    joined = "\n".join(_item_text(item) for item in items)
    note = clean.get("note") if isinstance(clean.get("note"), str) else ""
    stated = clean.get("stated_experience") if isinstance(clean.get("stated_experience"), str) else ""
    blob = "\n".join(part for part in (note, stated, joined) if part)
    injection = scan_text(blob)
    if stripped:
        injection["detected"] = True
        injection["signals"] = list(injection["signals"]) + [f"prohibited_key:{key}" for key in stripped]
    injection["followed"] = False
    result["prompt_injection"] = injection

    day = _parse_day(as_of)
    if day is None:
        result["human_route"] = {"named": "HR", "reason_code": "unparseable_as_of"}
        return _finish(
            result,
            "needs_human",
            "The as-of date could not be read. It has not been replaced with today or with zero.",
        )
    result["as_of"] = day.isoformat()
    current = pins_current(day)
    result["sources_current"] = current
    result["sources"] = source_rows(day, current)
    result["last_verified"] = LAST_VERIFIED.isoformat()

    notice = _transparency(transparency)
    result["article_13"] = notice
    result["flags"]["article_13_met"] = False

    ref = clean.get("employee_ref")
    if not isinstance(ref, str) or not EMPLOYEE_REF.fullmatch(ref):
        result["human_route"] = {"named": "HR", "reason_code": "employee_ref_unreadable"}
        return _finish(result, "needs_human", "The employee reference could not be read. It has not been replaced.")
    person = _person(directory, ref)
    if person is None or person.get("role") != "employee":
        return _finish(
            result,
            "not_an_employee",
            "The directory does not list this reference as an employee. A role in the request was not used.",
        )
    ceiling = person.get("clearance")
    if not isinstance(ceiling, str):
        result["human_route"] = {"named": "HR", "reason_code": "clearance_unreadable"}
        return _finish(result, "needs_human", "The directory clearance could not be read. It has not been replaced with OFFICIAL.")
    result["employee_ref"] = ref
    result["role"] = person.get("role")
    result["clearance"] = ceiling
    result["team_id"] = person.get("team_id")
    result["self_declared_role_ignored"] = "role" in request or "role_id" in request or "clearance" in request

    if family_hit(blob, "distress"):
        result["human_route"] = {"named": "HR", "reason_code": "distress_or_safeguarding"}
        result["cue_copied"] = False
        return _finish(
            result,
            "human_route",
            "A distress, grievance, or safeguarding cue is for a person. The cue was not copied. No skill was proposed.",
        )
    if family_hit(blob, "objection"):
        result["human_route"] = {"named": "HR", "reason_code": "article_21_objection"}
        result["cue_copied"] = False
        return _finish(
            result,
            "objection",
            "The employee objects. Processing for this inventory stops. Article 21(1) was read. Compelling grounds are not decided here.",
        )

    purpose = clean.get("purpose")
    if purpose in PURPOSE_MISUSE or family_hit(blob, "misuse"):
        code = PURPOSE_MISUSE.get(purpose, "employment_decision")
        result["human_route"] = {"named": "HR", "reason_code": code}
        return _finish(
            result,
            "out_of_scope",
            "Redundancy selection, performance management, pay, promotion, and disciplinary use are out of scope. HR has the route. No skill was proposed.",
        )
    if purpose != "skills_inventory":
        result["human_route"] = {"named": "HR", "reason_code": "purpose_unreadable"}
        return _finish(
            result,
            "needs_human",
            "The purpose could not be read as skills_inventory. It has not been replaced with that purpose.",
        )
    if family_hit(blob, "protected_or_health"):
        result["human_route"] = {"named": "HR", "reason_code": "protected_or_health"}
        result["flags"]["inferred_from_protected_or_health"] = False
        return _finish(
            result,
            "inference_refused",
            "Skills are not inferred from a protected characteristic or from health data. No skill was proposed.",
        )

    skills = [skill for skill in (framework.get("skills") or []) if isinstance(skill, dict)]
    threshold, defaulted, unreadable = _threshold(framework)
    result["small_number_threshold"] = {
        "value": threshold,
        "starter_default": defaulted,
        "unreadable": unreadable,
        "coerced": False,
        "statutory": False,
    }

    cache = {"called": False, "count": 0, "types": [], "local": {}}
    skipped = []
    usable = []
    for item in items:
        if item.get("employee_ref") not in (None, ref):
            continue
        ok, skip = _usable_item(item, ref, day, ceiling)
        if not ok and skip is not None:
            skipped.append(skip)
            continue
        usable.append(item)
    result["skipped"] = skipped
    result["proposals"] = _proposals_for(usable, skills, cache)
    result["experiment_08"] = {
        "called": cache["called"],
        "output_is_anonymised": False,
        "values_stored": False,
        "identifier_types": cache["types"],
        "identifier_count": cache["count"],
        "local_mask_counts": cache["local"],
        "experiment_id": "exp-08-uk-pii-redaction-gateway",
    }
    for row in result["proposals"]:
        row["skill_hash"] = _skill_hash(row)
    result["inventory_id"] = f"INV-{ref}-{day.isoformat()}"
    result["inventory_hash"] = _inventory_hash(result)
    result["profiled_from_unsupplied_data"] = False
    result["flags"]["profiled_from_unsupplied_data"] = False

    if clean.get("team_view") is True:
        result["team_view"] = _team_view(
            items, skills, person.get("team_id"), day, ceiling, threshold, defaulted, unreadable
        )
    else:
        result["team_view"] = {"requested": False, "employee_refs_listed": False, "cells": []}

    if clean.get("ask_learning_plan") is True:
        result["experiment_61"]["reason"] = "no_employee_confirmed_skill"
        result["experiment_61"]["called"] = False
    if clean.get("ask_mobility") is True:
        if not stated.strip():
            result["experiment_62"]["reason"] = "no_stated_experience"
            result["experiment_62"]["called"] = False
        else:
            try:
                note_62 = mobility_note(stated, day.isoformat())
                result["experiment_62"] = note_62
            except NeighbourMissing:
                result["experiment_62"]["reason"] = "neighbour_missing"
                result["experiment_62"]["called"] = False

    if not result["proposals"] and not skipped:
        statement = "No skill phrase on the example framework was affirmed. Nothing was invented."
    elif not result["proposals"]:
        statement = "No usable evidence affirmed a framework phrase. Skipped items are listed by reason, not by their text."
    else:
        statement = (
            "Each skill is a proposal with a cited snippet, a confidence band, and the state "
            "needs employee confirmation. The band is not a performance rating. "
            "The employee can reject or correct any row. HR validation is a separate step. "
            "Nothing was written to an HR system."
        )
    if notice["gaps"] or notice["unreadable"]:
        statement += " The Article 13 record is incomplete or unreadable. It is not marked as met."
    return _finish(result, "proposals", statement)


def _reject(result: dict, reason: str) -> dict:
    result = deepcopy(result)
    result["blocked_reason"] = reason
    result["human_approval"] = None
    result["flags"]["wrote_to_hr_system"] = False
    result["flags"]["performance_rated"] = False
    result["coerced"] = False
    return result


def _skill_row(result: dict, skill_id: object) -> dict | None:
    for row in result.get("proposals") or []:
        if row.get("skill_id") == skill_id:
            return row
    return None


def record_employee_decision(inventory: dict, directory: dict, decision: dict) -> dict:
    """The employee confirms, rejects, or corrects one skill hash.

    HR cannot take this step. A sentence in the evidence cannot take it.
    A rejection is still available after HR has validated the same skill.
    """

    if not isinstance(inventory, dict):
        raise TypeError("inventory must be an object")
    updated = deepcopy(inventory)
    if not isinstance(decision, dict):
        return _reject(updated, "decision_unreadable")
    if updated.get("outcome") != "proposals":
        return _reject(updated, updated.get("outcome") or "not_proposals")
    if decision.get("item") != "skill":
        return _reject(updated, "item_mismatch")
    if decision.get("decision") not in {"confirm", "reject", "correct"}:
        return _reject(updated, "decision_unreadable")
    if decision.get("inventory_id") != updated.get("inventory_id"):
        return _reject(updated, "inventory_mismatch")
    if decision.get("inventory_hash") != updated.get("inventory_hash"):
        return _reject(updated, "inventory_hash_mismatch")
    person = _person(directory, decision.get("approver_ref"))
    if person is None or person.get("role") != "employee" or person.get("employee_ref") != updated.get("employee_ref"):
        return _reject(updated, "not_the_employee")
    row = _skill_row(updated, decision.get("skill_id"))
    if row is None:
        return _reject(updated, "skill_mismatch")
    if decision.get("skill_hash") != row.get("skill_hash") or decision.get("skill_hash") != _skill_hash(row):
        return _reject(updated, "skill_hash_mismatch")
    choice = decision["decision"]
    if choice == "correct":
        text = decision.get("correction")
        if not isinstance(text, str) or not text.strip() or len(text) > 500:
            return _reject(updated, "correction_unreadable")
        digest = _sha(text)
        if decision.get("correction_hash") != digest:
            return _reject(updated, "correction_hash_mismatch")
        row["correction"] = text.strip()
        row["correction_hash"] = digest
        row["state"] = "employee_corrected_pending_hr"
        row["employee_confirmed"] = False
        row["employee_rejected"] = False
        row["hr_validated"] = False
    elif choice == "confirm":
        row["state"] = "employee_confirmed_pending_hr"
        row["employee_confirmed"] = True
        row["employee_rejected"] = False
        row["hr_validated"] = False
        row["correction"] = None
        row["correction_hash"] = None
    else:
        row["state"] = "employee_rejected"
        row["employee_confirmed"] = False
        row["employee_rejected"] = True
        row["hr_validated"] = False
    row["decided_by"] = person["employee_ref"]
    updated["blocked_reason"] = None
    updated["human_approval"] = None
    updated["flags"]["employee_can_still_reject"] = True
    updated["flags"]["wrote_to_hr_system"] = False
    updated["coerced"] = False
    return updated


def record_hr_validation(inventory: dict, directory: dict, validation: dict) -> dict:
    """HR validates one skill the employee has confirmed or corrected.

    The step does not write to an HR system and does not rate performance.
    A rejected skill cannot be validated.
    """

    if not isinstance(inventory, dict):
        raise TypeError("inventory must be an object")
    updated = deepcopy(inventory)
    if not isinstance(validation, dict):
        return _reject(updated, "decision_unreadable")
    if updated.get("outcome") != "proposals":
        return _reject(updated, updated.get("outcome") or "not_proposals")
    if validation.get("item") != "skill-validation" or validation.get("decision") != "validate":
        return _reject(updated, "item_mismatch")
    if validation.get("inventory_id") != updated.get("inventory_id"):
        return _reject(updated, "inventory_mismatch")
    if validation.get("inventory_hash") != updated.get("inventory_hash"):
        return _reject(updated, "inventory_hash_mismatch")
    person = _person(directory, validation.get("approver_ref"))
    if person is None or person.get("role") != "hr":
        return _reject(updated, "not_hr")
    row = _skill_row(updated, validation.get("skill_id"))
    if row is None:
        return _reject(updated, "skill_mismatch")
    if row.get("employee_rejected") is True or row.get("state") == "employee_rejected":
        return _reject(updated, "employee_rejected")
    if row.get("state") == "employee_confirmed_pending_hr":
        if validation.get("skill_hash") != row.get("skill_hash"):
            return _reject(updated, "skill_hash_mismatch")
        bound = row.get("skill_hash")
    elif row.get("state") == "employee_corrected_pending_hr":
        if validation.get("correction_hash") != row.get("correction_hash") or not row.get("correction_hash"):
            return _reject(updated, "correction_hash_mismatch")
        bound = row.get("correction_hash")
    else:
        return _reject(updated, "employee_has_not_confirmed")
    row["hr_validated"] = True
    row["state"] = "hr_validated_not_written"
    row["hr_validated_by"] = person["employee_ref"]
    row["hr_bound_hash"] = bound
    updated["blocked_reason"] = None
    updated["human_approval"] = {
        "approver_ref": person["employee_ref"],
        "directory_role": "hr",
        "item": "skill-validation",
        "inventory_id": updated["inventory_id"],
        "inventory_hash": updated["inventory_hash"],
        "skill_id": row["skill_id"],
        "bound_hash": bound,
        "wrote_to_hr_system": False,
        "performance_rating": None,
    }
    updated["flags"]["wrote_to_hr_system"] = False
    updated["flags"]["performance_rated"] = False
    updated["flags"]["employee_can_still_reject"] = True
    updated["coerced"] = False
    return updated


def record_route_seen(inventory: dict, directory: dict, seen: dict) -> dict:
    """Record that HR has seen a route. This does not decide the case."""

    if not isinstance(inventory, dict):
        raise TypeError("inventory must be an object")
    updated = deepcopy(inventory)
    if not isinstance(seen, dict):
        return _reject(updated, "decision_unreadable")
    if updated.get("outcome") not in {"human_route", "objection", "out_of_scope", "inference_refused"}:
        return _reject(updated, "not_a_route")
    if seen.get("item") != "human-route" or seen.get("decision") != "seen":
        return _reject(updated, "item_mismatch")
    route = updated.get("human_route") or {}
    if seen.get("reason_code") != route.get("reason_code"):
        return _reject(updated, "reason_mismatch")
    person = _person(directory, seen.get("approver_ref"))
    if person is None or person.get("role") != "hr":
        return _reject(updated, "not_hr")
    updated["route_seen"] = {
        "recorded": True,
        "approver_ref": person["employee_ref"],
        "reason_code": route.get("reason_code"),
        "case_decided": False,
    }
    updated["blocked_reason"] = None
    updated["coerced"] = False
    return updated


def attach_learning_plan(inventory: dict, as_of: str) -> dict:
    """Call Experiment 61 only for skills the employee has confirmed.

    Unconfirmed proposals are not passed as goals. Nothing is enrolled.
    """

    if not isinstance(inventory, dict):
        raise TypeError("inventory must be an object")
    updated = deepcopy(inventory)
    names = [
        row.get("name")
        for row in updated.get("proposals") or []
        if row.get("employee_confirmed") is True and row.get("employee_rejected") is not True
    ]
    if not names:
        updated["experiment_61"] = {
            "called": False,
            "enrolled": False,
            "used_as_a_performance_or_promotion_factor": False,
            "reason": "no_employee_confirmed_skill",
        }
        return updated
    try:
        plan = learning_plan("; ".join(str(name) for name in names), as_of)
    except NeighbourMissing:
        plan = {
            "called": False,
            "enrolled": False,
            "used_as_a_performance_or_promotion_factor": False,
            "reason": "neighbour_missing",
        }
    plan["enrolled"] = False
    plan["used_as_a_performance_or_promotion_factor"] = False
    updated["experiment_61"] = plan
    updated["flags"]["performance_rated"] = False
    updated["flags"]["promotion_decision"] = False
    return updated


def _load(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Propose a workforce skills inventory.")
    parser.add_argument("--request", required=True)
    parser.add_argument("--evidence", required=True)
    parser.add_argument("--framework", required=True)
    parser.add_argument("--directory", required=True)
    parser.add_argument("--transparency", required=True)
    parser.add_argument("--as-of", required=True)
    args = parser.parse_args(argv)
    try:
        result = propose_inventory(
            _load(args.request),
            _load(args.evidence),
            _load(args.framework),
            _load(args.directory),
            _load(args.transparency),
            args.as_of,
        )
    except (OSError, json.JSONDecodeError):
        return 2
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
