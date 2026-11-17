#!/usr/bin/env python3
"""Draft a learning plan from a synthetic catalogue. Do not enrol, book, or spend.

The same inputs and the same as-of date produce the same JSON. Approval is
a later call. Words inside a goal or a course description are not that call.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from copy import deepcopy
from datetime import date
from decimal import Decimal
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from injection import scan_text, without_instruction_sentences
    from reuse import (
        NeighbourMissing,
        answer_module,
        compare_module,
        gaps_module,
        handbook_module,
        mask_module,
    )
    from sources import (
        LAST_VERIFIED,
        PINNED_ON,
        SECTION_19_CHARACTERISTICS,
        STALE_AFTER_DAYS,
        STARTER_EXTRA_CHARACTERISTICS,
        pins_current,
        source_rows,
    )
else:
    from .injection import scan_text, without_instruction_sentences
    from .reuse import (
        NeighbourMissing,
        answer_module,
        compare_module,
        gaps_module,
        handbook_module,
        mask_module,
    )
    from .sources import (
        LAST_VERIFIED,
        PINNED_ON,
        SECTION_19_CHARACTERISTICS,
        STALE_AFTER_DAYS,
        STARTER_EXTRA_CHARACTERISTICS,
        pins_current,
        source_rows,
    )

LABEL = "DRAFT LEARNING PLAN. NOT AN ENROLMENT."
CATALOGUE_ID = "H004"
EXPERIMENT_ID = "exp-61-learning-path-planner"
AUTONOMY = "A1"
ORGANISATION = "Ashcombe Borough Council (fictional)"
HANDBOOK_QUESTION = "What does the handbook say about time off for study or training?"
HANDBOOK_ROOT = Path(__file__).resolve().parents[2] / "58-employee-handbook"

EMPLOYEE_REF = re.compile(r"^EMP-\d{4}$")
COURSE_ID = re.compile(r"^CRS-\d{3}$")
MONEY = re.compile(r"\d+\.\d{2}")
HOURS = re.compile(r"\d+")
RANK = {
    "OFFICIAL": 1,
    "OFFICIAL-SENSITIVE": 2,
    "SECRET": 3,
    "TOP SECRET": 4,
}
MAX_MONEY = Decimal("1000000.00")
MAX_HOURS = 400
MAX_GOALS = 4000

PROHIBITED_KEYS = frozenset(
    {
        "approved",
        "employee_approved",
        "manager_approved",
        "human_approval",
        "enrolment_request_raised",
        "enrolled",
        "booked",
        "spent",
        "spent_gbp",
        "stale_seen",
        "budget_unreadable_seen",
        "adjustment_seen",
        "clearance",
        "role_id",
        "rank",
        "performance_rating",
        "promotion_decision",
    }
)

WELLBEING = (
    "can't cope",
    "cannot cope",
    "cannot keep going",
    "can't keep going",
    "end of my tether",
    "don't want to be here",
    "do not want to be here",
    "self-harm",
    "suicidal",
    "kill myself",
    "not safe at home",
    "mental health",
    "wellbeing concern",
    "burnout",
    "struggling to cope",
    "safeguarding",
    "being abused",
)
ADJUSTMENT = (
    "reasonable adjustment",
    "reasonable adjustments",
    "accessible format",
    "screen reader",
    "large print",
    "easy read",
    "wheelchair",
    "disability access",
    "auxiliary aid",
)
INFER = (
    "infer",
    "assume ability",
    "deduce ability",
    "rank staff",
    "rank employees",
    "rank the team",
    "score ability",
    "ability from",
)
USE_FOR = (
    "performance review",
    "performance rating",
    "promotion",
    "promote me",
    "appraisal score",
)
ROLE_COVER = ("skills for my role", "role skills framework")
CHARACTERISTICS = SECTION_19_CHARACTERISTICS + STARTER_EXTRA_CHARACTERISTICS

BLOCKED_OUTCOMES = frozenset(
    {
        "wellbeing_route",
        "inference_refused",
        "use_refused",
        "needs_human",
        "refused",
        "above_clearance",
        "not_an_employee",
        "no_suitable_course",
        "refused_jurisdiction",
    }
)

_handbook_cache: dict[str, dict] = {}
_gap_cache: dict[str, dict] = {}
_compare_cache: dict[str, dict] = {}


class LearningPathForbidden(RuntimeError):
    """Raised when a caller asks the agent to enrol, book, spend, or rank."""


def enrol(*_args, **_kwargs) -> None:
    raise LearningPathForbidden("the agent does not enrol anyone")


def book(*_args, **_kwargs) -> None:
    raise LearningPathForbidden("the agent does not book a course")


def spend(*_args, **_kwargs) -> None:
    raise LearningPathForbidden("the agent does not spend")


def rank_employees(*_args, **_kwargs) -> None:
    raise LearningPathForbidden("the agent does not rank employees")


def decide_performance(*_args, **_kwargs) -> None:
    raise LearningPathForbidden("the agent does not use a plan for performance")


def decide_promotion(*_args, **_kwargs) -> None:
    raise LearningPathForbidden("the agent does not use a plan for promotion")


def infer_ability(*_args, **_kwargs) -> None:
    raise LearningPathForbidden("the agent does not infer ability from a protected characteristic")


def _flags() -> dict:
    return {
        "enrolled": False,
        "booked": False,
        "spend_attempted": False,
        "employees_ranked": False,
        "performance_use": False,
        "promotion_use": False,
        "skills_inferred_from_protected_characteristics": False,
        "adjustment_decided": False,
        "equality_duty_met": False,
        "indirect_discrimination_decided": False,
        "section_63d_application_made": False,
        "qualifying_employee_decided": False,
        "levy_eligibility_decided": False,
        "levy_account_used": False,
        "instructions_followed": False,
        "network_called": False,
        "model_called": False,
        "description_copied": False,
        "goals_copied": False,
        "coerced": False,
        "agent_chose_source": False,
        "legal_hold_dropped": False,
        "retention_dropped": False,
        "output_is_anonymised": False,
    }


def _empty_approvals() -> dict:
    return {
        "employee": {"accepted": False, "approver_ref": None, "source": None, "ignored_role": False},
        "manager": {
            "accepted": False,
            "approver_ref": None,
            "source": None,
            "stale_seen": None,
            "budget_unreadable_seen": None,
            "ignored_role": False,
        },
    }


def _base(as_of_text: str) -> dict:
    return {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment_id": EXPERIMENT_ID,
        "autonomy": AUTONOMY,
        "organisation": ORGANISATION,
        "organisation_is_fictional": True,
        "as_of": as_of_text if isinstance(as_of_text, str) else "",
        "outcome": None,
        "statement": "",
        "plan_id": None,
        "employee_ref": None,
        "manager_ref": None,
        "role_id": None,
        "clearance": None,
        "self_declared_role_ignored": False,
        "self_declared_clearance_ignored": False,
        "steps": [],
        "exclusions": [],
        "affirmed_skill_ids": [],
        "budget": {
            "limit_gbp": None,
            "total_gbp": None,
            "within_budget": None,
            "readable": False,
            "information_only": True,
            "spent_gbp": None,
        },
        "human_approval": None,
        "approvals": _empty_approvals(),
        "adjustment_review": {
            "seen": False,
            "reviewer_ref": None,
            "adjustment_decided": False,
            "equality_duty_met": False,
        },
        "enrolment_request_raised": False,
        "enrolment_request": None,
        "enrolled": False,
        "booked": False,
        "spent_gbp": None,
        "blocked_reason": None,
        "may_be_relied_on": False,
        "sources_current": False,
        "sources": [],
        "statutory_note": "",
        "human_route": None,
        "input_record": {
            "marking": None,
            "retention_labels": [],
            "legal_hold": False,
            "body_copied": False,
        },
        "prompt_injection": {"detected": False, "followed": False, "signals": []},
        "masking": {},
        "experiment_58": {"called": False},
        "experiment_44": {"called": False, "used_as_a_course": False, "gap_confirmed": False},
        "experiment_36": {"called": False, "agent_chose_source": False},
        "people_partner_refs": [],
        "flags": _flags(),
        "legal_advice": False,
        "coerced": False,
    }


def _finish(result: dict, outcome: str, statement: str, input_text: str = "") -> dict:
    result["outcome"] = outcome
    result["statement"] = statement
    result["flags"]["instructions_followed"] = False
    result["flags"]["coerced"] = False
    result["coerced"] = False
    result["enrolled"] = False
    result["booked"] = False
    result["spent_gbp"] = None
    result["enrolment_request_raised"] = False
    result["human_approval"] = None
    result["legal_advice"] = False
    result["flags"]["performance_use"] = False
    result["flags"]["promotion_use"] = False
    result["flags"]["employees_ranked"] = False
    result["flags"]["skills_inferred_from_protected_characteristics"] = False
    result["flags"]["adjustment_decided"] = False
    result["flags"]["section_63d_application_made"] = False
    result["flags"]["goals_copied"] = False
    result["flags"]["description_copied"] = False
    input_text = result.pop("_mask_input", input_text)
    if outcome == "proposed" and result.get("sources_current") is True:
        result["may_be_relied_on"] = True
    else:
        result["may_be_relied_on"] = False
    _stamp_id(result)
    _mask_report(result, input_text)
    return result


def _stamp_id(result: dict) -> None:
    payload = {
        "employee_ref": result.get("employee_ref"),
        "as_of": result.get("as_of"),
        "outcome": result.get("outcome"),
        "steps": [step.get("course_id") for step in result.get("steps") or []],
        "exclusions": [row.get("course_id") for row in result.get("exclusions") or []],
        "total_gbp": (result.get("budget") or {}).get("total_gbp"),
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    result["plan_id"] = "LP-" + hashlib.sha256(raw.encode()).hexdigest()[:12]


def _mask_report(result: dict, input_text: str = "") -> None:
    counts = mask_module().mask_counts
    blob = json.dumps(
        {key: value for key, value in result.items() if key != "masking"},
        sort_keys=True,
        default=str,
    )
    output = counts(blob)
    incoming = counts(input_text)
    result["masking"] = {
        "input_counts": incoming["counts"],
        "output_counts": output["counts"],
        "replacements_made": 0,
        "values_stored": False,
        "values_copied": any(output["counts"].values()),
        "described_as_anonymised": False,
        "output_is_anonymised": False,
    }
    result["flags"]["output_is_anonymised"] = False


def _parse_day(value: object):
    handbook = handbook_module()
    return handbook.parse_day(value)


def _affirmed(text: str, phrase: str) -> bool:
    """A phrase counts only outside a negation.

    "It is not true that X includes Y" is not an inclusion of Y. A short
    "not" or "never" before the phrase is the same.
    """

    if not text or not phrase:
        return False
    handbook = handbook_module()
    needle = re.compile(rf"\b{re.escape(phrase)}\b", re.IGNORECASE)
    negation = re.compile(
        r"\b(not|no|never|without|isn't|aren't|wasn't|weren't|don't|doesn't|cannot|can't)\b",
        re.I,
    )
    for sentence in handbook.sentences(text):
        match = needle.search(sentence)
        if match is None:
            continue
        if handbook.phrase_is_denied(sentence, phrase):
            continue
        window = sentence[: match.start()]
        if negation.search(window[-40:]):
            continue
        return True
    return False


def _any_affirmed(text: str, phrases: tuple[str, ...] | list[str]) -> bool:
    return any(_affirmed(text, phrase) for phrase in phrases)


def _labels(metadata: object, text: str) -> list[str]:
    handbook = handbook_module()
    found: list[str] = []
    if isinstance(metadata, str) and metadata.strip():
        for label in handbook.markings_in(None, metadata):
            if label not in found:
                found.append(label)
    for sentence in handbook.sentences(text or ""):
        if re.search(r"\bmy clearance is\b", sentence, re.IGNORECASE):
            continue
        for label in handbook.markings_in(None, sentence):
            if handbook.phrase_is_denied(sentence, label):
                continue
            if label not in found:
                found.append(label)
    return found


def _higher(labels: list[str]) -> str | None:
    if not labels:
        return None
    return handbook_module().higher_marking(labels)


def _retention(record: dict, text: str) -> list[str]:
    return handbook_module().retention_labels(record, text)


def _hold(record: dict, text: str) -> bool:
    return handbook_module().legal_hold(record, text)


def _above(marking: str | None, ceiling: str) -> bool:
    return handbook_module().above_ceiling(marking, ceiling)


def _parse_money(value: object) -> Decimal | None:
    if isinstance(value, bool) or not isinstance(value, str):
        return None
    text = value.strip().replace("£", "").replace("GBP", "").replace(",", "").strip()
    if not MONEY.fullmatch(text):
        return None
    amount = Decimal(text)
    if amount < 0 or amount > MAX_MONEY:
        return None
    return amount


def _parse_hours(value: object) -> int | None:
    if isinstance(value, bool) or not isinstance(value, str):
        return None
    text = value.strip()
    if not HOURS.fullmatch(text):
        return None
    number = int(text)
    if number < 1 or number > MAX_HOURS:
        return None
    return number


def _money_text(amount: Decimal) -> str:
    return f"{amount:.2f}"


def _strip_request(request: dict) -> tuple[dict, list[str]]:
    clean = {}
    stripped = []
    for key, value in request.items():
        if key in PROHIBITED_KEYS:
            stripped.append(key)
            continue
        clean[key] = value
    return clean, stripped


def _statutory_note(current: bool) -> str:
    note = (
        "Employment Rights Act 1996 Part 6A (study and training, sections 63D to 63K) "
        f"was on legislation.gov.uk on {LAST_VERIFIED} and the page did not show a repeal. "
        "The commencement footnote says 6 April 2010 for certain purposes and otherwise "
        "prospective. S.I. 2010/303 was not opened as its own page. "
        "GOV.UK 'Who can and cannot ask for time off to train' stated a 26-week qualifying "
        "period and an organisation of at least 250 people. This plan does not decide that "
        "anyone qualifies, and it is not a section 63D application. "
        "The HMRC pay-Apprenticeship-Levy page, last updated 6 April 2026 on that page, "
        "states a 0.5% rate, a £3 million pay-bill threshold, and a £15,000 allowance. "
        "The funding-rules document for 2026 to 2027 was not opened. What the levy can buy "
        "is unverified. Nothing here is spent. "
        "Equality Act 2010 sections 19, 20, and 21 were read. This plan does not decide "
        "indirect discrimination or that a step is a reasonable adjustment."
    )
    if not current:
        note += " The pins are outside the starter window and have not been refreshed."
    return note


def _handbook(as_of: str) -> dict:
    if as_of in _handbook_cache:
        return _handbook_cache[as_of]
    try:
        handbook = json.loads((HANDBOOK_ROOT / "fixtures" / "handbook.json").read_text(encoding="utf-8"))
        scope = json.loads((HANDBOOK_ROOT / "examples" / "sample_scope.json").read_text(encoding="utf-8"))
        answer = answer_module().answer_handbook(
            {"synthetic": True, "question": HANDBOOK_QUESTION},
            handbook,
            scope,
            as_of,
        )
    except (OSError, json.JSONDecodeError, NeighbourMissing, KeyError, TypeError) as exc:
        record = {"called": False, "reason": type(exc).__name__, "outcome": None, "covered": False}
        _handbook_cache[as_of] = record
        return record
    covered = answer.get("outcome") == "answered"
    text = answer.get("answer") if answer.get("outcome") in {"answered", "not_covered"} else None
    record = {
        "called": True,
        "experiment_id": "exp-58-employee-handbook",
        "question_fixed": True,
        "outcome": answer.get("outcome"),
        "covered": covered,
        "answer": text,
        "entitlement_decision": answer.get("entitlement_decision"),
        "rules_current": (answer.get("stale") or {}).get("rules_current"),
        "section_63d_application_made": False,
        "note": (
            "A fixed question was asked of the synthetic handbook. "
            "A gap is not filled from the course catalogue. "
            "The answer is not a section 63D application."
        ),
    }
    _handbook_cache[as_of] = record
    return record


def _gaps(cleaned: str, as_of: str) -> dict:
    key = hashlib.sha256((as_of + "\n" + cleaned).encode()).hexdigest()
    if key in _gap_cache:
        return _gap_cache[key]
    pack = {
        "synthetic": True,
        "pack_id": "SYN-PACK-0061",
        "sector": "public_service",
        "queries": [{"id": "SYN-QRY-0061", "text": cleaned}],
    }
    try:
        report = gaps_module().detect_gaps(pack, as_of)
    except (NeighbourMissing, TypeError, ValueError) as exc:
        record = {
            "called": False,
            "reason": type(exc).__name__,
            "used_as_a_course": False,
            "gap_confirmed": False,
            "published": False,
        }
        _gap_cache[key] = record
        return record
    counts = report.get("counts") or {}
    record = {
        "called": True,
        "experiment_id": "exp-44-knowledge-gap-detector",
        "pack_id": "SYN-PACK-0061",
        "outcome": report.get("outcome"),
        "refusal_reason": report.get("refusal_reason"),
        "content_gaps": counts.get("content_gaps"),
        "gap_confirmed": False,
        "published": False,
        "used_as_a_course": False,
        "note": (
            "Experiment 44 reviews a different knowledge base. "
            "A content gap there is not a course and is not confirmed. "
            "Outlines are not copied."
        ),
    }
    _gap_cache[key] = record
    return record


def _compare_course(course: dict, as_of: str) -> dict:
    cost = course.get("cost_gbp")
    other_cost = course.get("provider_cost_gbp")
    hours = course.get("duration_hours")
    other_hours = course.get("provider_duration_hours")
    have_cost = isinstance(cost, str) and isinstance(other_cost, str)
    have_hours = isinstance(hours, str) and isinstance(other_hours, str)
    if not have_cost and not have_hours:
        return {"called": False, "reason": "single_source", "agent_chose_source": False, "material": False}
    course_id = str(course.get("course_id") or "crs").lower()
    key = hashlib.sha256(
        json.dumps(
            {"c": cost, "oc": other_cost, "h": hours, "oh": other_hours, "as_of": as_of, "id": course_id},
            sort_keys=True,
        ).encode()
    ).hexdigest()
    if key in _compare_cache:
        return _compare_cache[key]
    facts = []
    if have_cost:
        facts.append({"fact_key": "course_cost", "field_type": "currency"})
    if have_hours:
        facts.append({"fact_key": "course_hours", "field_type": "figure"})
    left_lines = []
    right_lines = []
    left_fields = []
    right_fields = []
    line_no = 1
    if have_cost:
        left_value = f"GBP {cost.strip()}"
        right_value = f"GBP {other_cost.strip()}"
        left_lines.append({"line": line_no, "text": f"Cost: {left_value}"})
        right_lines.append({"line": line_no, "text": f"Cost: {right_value}"})
        left_fields.append(
            {"fact_key": "course_cost", "page": 1, "paragraph": 1, "line": line_no, "value": left_value}
        )
        right_fields.append(
            {"fact_key": "course_cost", "page": 1, "paragraph": 1, "line": line_no, "value": right_value}
        )
        line_no += 1
    if have_hours:
        left_lines.append({"line": line_no, "text": f"Duration: {hours.strip()}"})
        right_lines.append({"line": line_no, "text": f"Duration: {other_hours.strip()}"})
        left_fields.append(
            {"fact_key": "course_hours", "page": 1, "paragraph": 1, "line": line_no, "value": hours.strip()}
        )
        right_fields.append(
            {"fact_key": "course_hours", "page": 1, "paragraph": 1, "line": line_no, "value": other_hours.strip()}
        )
    slug = re.sub(r"[^a-z0-9-]", "", course_id)[:20] or "course"
    pack = {
        "synthetic": True,
        "pack_id": f"course-{slug}",
        "facts": facts,
        "documents": [
            {
                "document_id": f"cat-{slug}",
                "title": "Catalogue extract",
                "kind": "form",
                "status": "current",
                "reviewed_on": as_of,
                "pages": [{"page": 1, "paragraphs": [{"paragraph": 1, "lines": left_lines}]}],
                "fields": left_fields,
            },
            {
                "document_id": f"prv-{slug}",
                "title": "Provider extract",
                "kind": "contract",
                "status": "current",
                "reviewed_on": as_of,
                "pages": [{"page": 1, "paragraphs": [{"paragraph": 1, "lines": right_lines}]}],
                "fields": right_fields,
            },
        ],
    }
    try:
        report = compare_module().compare(pack, as_of)
    except Exception as exc:  # noqa: BLE001 - a neighbour failure is a human flag, not a zero
        record = {
            "called": False,
            "reason": type(exc).__name__,
            "agent_chose_source": False,
            "material": True,
            "do_not_rely": True,
        }
        _compare_cache[key] = record
        return record
    classes = []
    for fact in report.get("facts") or []:
        classes.append(
            {
                "fact_key": fact.get("fact_key"),
                "classification": fact.get("classification"),
                "agent_chose_source": fact.get("agent_chose_source"),
                "correct_value": fact.get("correct_value"),
            }
        )
    material = any(row["classification"] == "material_discrepancy" for row in classes)
    record = {
        "called": True,
        "experiment_id": "exp-36-cross-source-validation",
        "classifications": classes,
        "material": material,
        "agent_chose_source": report.get("agent_chose_source") is True,
        "do_not_rely": report.get("do_not_rely") is True,
        "correct_value_written": report.get("correct_value_written") is True,
    }
    _compare_cache[key] = record
    return record


def _course_text(course: dict) -> str:
    parts = []
    for key in ("description", "cover"):
        if isinstance(course.get(key), str):
            parts.append(course[key])
    return "\n".join(parts)


def _course_marking(course: dict) -> str | None:
    return _higher(_labels(course.get("marking"), _course_text(course)))


def _exclusion(course: dict, reason: str, extra: dict | None = None) -> dict:
    text = _course_text(course)
    row = {
        "course_id": course.get("course_id"),
        "reason": reason,
        "marking": _course_marking(course),
        "retention_labels": _retention(course, text),
        "legal_hold": _hold(course, text),
        "description_copied": False,
        "cost_used": None,
    }
    if extra:
        row.update(extra)
    return row


def _index_courses(catalogue: dict) -> dict[str, dict]:
    rows = {}
    for course in catalogue.get("courses") or []:
        if isinstance(course, dict) and isinstance(course.get("course_id"), str):
            rows[course["course_id"]] = course
    return rows


def _own_problem(course: dict, as_of: date, ceiling: str) -> str | None:
    if not COURSE_ID.fullmatch(str(course.get("course_id") or "")):
        return "course_id"
    status = course.get("status")
    if status == "withdrawn":
        return "withdrawn"
    if status != "current":
        return "status_unreadable"
    review = _parse_day(course.get("review_due"))
    if review is None:
        return "review_date_unreadable"
    if review <= as_of:
        return "stale"
    marking = _course_marking(course)
    if marking is None:
        return "marking_missing"
    if _above(marking, ceiling):
        return "above_clearance"
    if _parse_money(course.get("cost_gbp")) is None:
        return "cost_unreadable"
    if _parse_hours(course.get("duration_hours")) is None:
        return "duration_unreadable"
    unit = course.get("duration_unit")
    other_unit = course.get("provider_duration_unit")
    if other_unit not in (None, unit):
        return "unit_conflict"
    return None


def _select(courses: dict[str, dict], skill_ids: list[str], as_of: date, ceiling: str, as_of_text: str) -> tuple[list[dict], list[dict], bool]:
    """Return recommended courses, exclusions, and whether a source was chosen. Never."""

    wanted = set(skill_ids)
    considered: dict[str, str] = {}
    recommended: dict[str, dict] = {}
    exclusions: list[dict] = []
    visiting: set[str] = set()

    def consider(course_id: str, because_skill: str | None) -> str:
        if course_id in considered:
            return considered[course_id]
        if course_id in visiting:
            return "cycle"
        course = courses.get(course_id)
        if course is None:
            return "missing"
        visiting.add(course_id)
        problem = _own_problem(course, as_of, ceiling)
        if problem:
            visiting.remove(course_id)
            considered[course_id] = problem
            return problem
        compared = _compare_course(course, as_of_text)
        if compared.get("agent_chose_source"):
            visiting.remove(course_id)
            considered[course_id] = "source_chosen"
            return "source_chosen"
        if compared.get("material"):
            visiting.remove(course_id)
            considered[course_id] = "source_discrepancy"
            return "source_discrepancy"
        prerequisites = course.get("prerequisites") or []
        if not isinstance(prerequisites, list):
            visiting.remove(course_id)
            considered[course_id] = "prerequisite_unreadable"
            return "prerequisite_unreadable"
        for prerequisite in prerequisites:
            if not isinstance(prerequisite, str):
                visiting.remove(course_id)
                considered[course_id] = "prerequisite_unreadable"
                return "prerequisite_unreadable"
            state = consider(prerequisite, None)
            if state == "cycle":
                visiting.remove(course_id)
                considered[course_id] = "cycle"
                return "cycle"
            if state != "ok":
                visiting.remove(course_id)
                considered[course_id] = "prerequisite_unavailable"
                return "prerequisite_unavailable"
        visiting.remove(course_id)
        considered[course_id] = "ok"
        recommended[course_id] = {"course": course, "because_skill": because_skill, "compared": compared}
        return "ok"

    for course in courses.values():
        skills = course.get("skills") or []
        if not isinstance(skills, list):
            continue
        matched = [skill for skill in skills if skill in wanted]
        if not matched:
            continue
        state = consider(course["course_id"], matched[0])
        if state != "ok":
            extra = {}
            if state == "source_discrepancy":
                extra["cross_source"] = _compare_course(course, as_of_text)
                extra["agent_chose_source"] = False
            exclusions.append(_exclusion(course, state, extra))

    ordered = _sequence(recommended)
    if ordered is None:
        for item in recommended.values():
            exclusions.append(_exclusion(item["course"], "cycle"))
        return [], exclusions, False
    steps = []
    for index, course_id in enumerate(ordered, start=1):
        item = recommended[course_id]
        course = item["course"]
        text = _course_text(course)
        cost = _parse_money(course["cost_gbp"])
        hours = _parse_hours(course["duration_hours"])
        skill = item["because_skill"]
        if skill:
            reason = (
                f"The stated goals affirm the role skill {skill}. "
                f"Catalogue entry {course_id} is current on the as-of date."
            )
        else:
            reason = (
                f"Catalogue entry {course_id} is listed as a prerequisite of a later step. "
                "It is not an extra skill inferred about the employee."
            )
        steps.append(
            {
                "sequence": index,
                "course_id": course_id,
                "title": course.get("title") if isinstance(course.get("title"), str) else course_id,
                "skill_id": skill,
                "reason": reason,
                "cost_gbp": _money_text(cost),
                "duration_hours": hours,
                "review_due": course.get("review_due"),
                "status": course.get("status"),
                "prerequisites": list(course.get("prerequisites") or []),
                "marking": _course_marking(course),
                "retention_labels": _retention(course, text),
                "legal_hold": _hold(course, text),
                "citation": {"catalogue_entry": course_id, "field": "course_id"},
                "description_copied": False,
                "cross_source": item["compared"],
            }
        )
    exclusions.sort(key=lambda row: str(row.get("course_id")))
    return steps, exclusions, False


def _sequence(recommended: dict[str, dict]) -> list[str] | None:
    remaining = {
        course_id: [
            item
            for item in (payload["course"].get("prerequisites") or [])
            if item in recommended
        ]
        for course_id, payload in recommended.items()
    }
    ordered = []
    while remaining:
        ready = sorted(course_id for course_id, deps in remaining.items() if not deps)
        if not ready:
            return None
        course_id = ready[0]
        ordered.append(course_id)
        del remaining[course_id]
        for deps in remaining.values():
            if course_id in deps:
                deps.remove(course_id)
    return ordered


def _lookup(directory: dict, employee_ref: str) -> dict | None:
    for person in directory.get("employees") or []:
        if isinstance(person, dict) and person.get("employee_ref") == employee_ref:
            return person
    return None


def _role(framework: dict, role_id: str) -> dict | None:
    for role in framework.get("roles") or []:
        if isinstance(role, dict) and role.get("role_id") == role_id:
            return role
    return None


def draft_plan(request: dict, catalogue: dict, framework: dict, directory: dict, as_of: str) -> dict:
    """Return one plan. ``human_approval`` stays null. Nothing is enrolled."""

    result = _base(as_of if isinstance(as_of, str) else "")
    if not isinstance(request, dict) or not isinstance(catalogue, dict):
        return _finish(result, "refused", "The request or the catalogue could not be read. Nothing was copied.")
    if catalogue.get("synthetic") is not True or framework.get("synthetic") is not True or directory.get("synthetic") is not True:
        return _finish(result, "refused", "A file is not marked synthetic. Nothing was copied.")
    if request.get("synthetic") is not True:
        return _finish(result, "refused", "The request is not marked synthetic. Nothing was copied.")

    clean, stripped = _strip_request(request)
    raw_goals = clean.get("goals")
    goals = raw_goals if isinstance(raw_goals, str) else ""
    injection = scan_text(goals)
    for course in catalogue.get("courses") or []:
        if isinstance(course, dict):
            found = scan_text(_course_text(course))
            if found["detected"]:
                injection["detected"] = True
                for signal in found["signals"]:
                    if signal not in injection["signals"]:
                        injection["signals"].append(signal)
    if stripped:
        injection["detected"] = True
        for key in stripped:
            signal = f"prohibited_key:{key}"
            if signal not in injection["signals"]:
                injection["signals"].append(signal)
    injection["followed"] = False
    result["prompt_injection"] = injection
    cleaned = without_instruction_sentences(goals)
    input_for_mask = goals + "\n" + "\n".join(
        _course_text(course) for course in catalogue.get("courses") or [] if isinstance(course, dict)
    )
    result["_mask_input"] = input_for_mask

    day = _parse_day(as_of)
    if day is None:
        result["human_route"] = {"named": "Line manager", "reason": "unparseable_as_of"}
        return _finish(
            result,
            "needs_human",
            "The as-of date could not be read. It has not been replaced with today or with zero.",
        )
    result["as_of"] = day.isoformat()
    current = pins_current(day)
    result["sources_current"] = current
    result["sources"] = source_rows(current)
    result["statutory_note"] = _statutory_note(current)
    result["may_be_relied_on"] = False

    if not isinstance(raw_goals, str) or len(raw_goals) > MAX_GOALS:
        result["human_route"] = {"named": "Line manager", "reason": "goals_unreadable"}
        return _finish(
            result,
            "needs_human",
            "The goals could not be read, or they are longer than this starter will read. They were not truncated and they were not replaced with an empty plan.",
        )

    employee_ref = clean.get("employee_ref")
    if not isinstance(employee_ref, str) or not EMPLOYEE_REF.fullmatch(employee_ref):
        result["human_route"] = {"named": "Line manager", "reason": "employee_ref"}
        return _finish(
            result,
            "needs_human",
            "The employee reference could not be read. A self-declared role in the text was not used.",
        )
    person = _lookup(directory, employee_ref)
    if person is None:
        result["employee_ref"] = employee_ref
        result["human_route"] = {"named": "Line manager", "reason": "unknown_employee"}
        return _finish(
            result,
            "needs_human",
            "That reference is not in the synthetic directory. The request was not given a default role or a default clearance.",
        )

    result["employee_ref"] = employee_ref
    result["self_declared_role_ignored"] = "self_role" in injection["signals"] or "role_id" in stripped
    result["self_declared_clearance_ignored"] = "self_clearance" in injection["signals"] or "clearance" in stripped
    if person.get("account_status") != "employee":
        result["human_route"] = {"named": "Line manager", "reason": "not_an_employee"}
        return _finish(
            result,
            "not_an_employee",
            "The directory does not list this reference as an employee. A sentence in the request is not a status.",
        )

    role_id = person.get("role_id")
    role = _role(framework, role_id) if isinstance(role_id, str) else None
    if role is None:
        result["human_route"] = {"named": "Line manager", "reason": "role_unreadable"}
        return _finish(
            result,
            "needs_human",
            "The directory role is not in the skills framework. The role named in the request was not used.",
        )
    result["role_id"] = role_id
    clearance = person.get("clearance")
    if not isinstance(clearance, str) or clearance not in RANK:
        result["human_route"] = {"named": "Line manager", "reason": "clearance_unreadable"}
        return _finish(
            result,
            "needs_human",
            "The directory clearance could not be read. It has not been replaced with OFFICIAL, and a clearance typed in the request was not used.",
        )
    result["clearance"] = clearance
    manager_ref = person.get("manager_ref")
    if not isinstance(manager_ref, str) or not EMPLOYEE_REF.fullmatch(manager_ref) or manager_ref == employee_ref:
        result["human_route"] = {"named": "HR", "reason": "no_manager"}
        return _finish(
            result,
            "needs_human",
            "The directory has no other manager for this employee. No plan is issued that could be approved by one person twice.",
        )
    if _lookup(directory, manager_ref) is None:
        result["human_route"] = {"named": "HR", "reason": "manager_unknown"}
        return _finish(result, "needs_human", "The manager reference is not in the synthetic directory.")
    result["manager_ref"] = manager_ref
    result["people_partner_refs"] = sorted(
        row["employee_ref"]
        for row in directory.get("employees") or []
        if isinstance(row, dict) and row.get("role_id") == "ROLE-PEOPLE" and isinstance(row.get("employee_ref"), str)
    )

    request_marking = _higher(_labels(clean.get("marking"), goals))
    result["input_record"] = {
        "marking": request_marking,
        "retention_labels": _retention(clean, goals),
        "legal_hold": _hold(clean, goals),
        "body_copied": False,
    }
    if request_marking is not None and _above(request_marking, clearance):
        result["human_route"] = {"named": "Information governance", "reason": "above_clearance"}
        return _finish(
            result,
            "above_clearance",
            "The request carries a marking above the directory clearance. The goals were not copied and were not used to choose a course.",
        )

    if re.search(r"\bnorthern ireland\b", cleaned, re.I):
        result["human_route"] = {"named": "HR", "reason": "northern_ireland"}
        return _finish(
            result,
            "refused_jurisdiction",
            "This starter does not state Northern Ireland employment law. The Equality Act 2010 sections opened here are marked England and Wales and Scotland.",
        )

    if _any_affirmed(cleaned, USE_FOR):
        result["human_route"] = {"named": "Line manager, outside this assistant", "reason": "performance_or_promotion"}
        return _finish(
            result,
            "use_refused",
            "This assistant does not draft a plan for a performance rating or a promotion. performance_use and promotion_use stay false.",
        )

    handbook = handbook_module()
    inferred = _any_affirmed(cleaned, ("rank staff", "rank employees", "rank the team"))
    if not inferred:
        for sentence in handbook.sentences(cleaned):
            if any(_affirmed(sentence, verb) for verb in INFER) and any(
                _affirmed(sentence, characteristic) for characteristic in CHARACTERISTICS
            ):
                inferred = True
                break
    if inferred:
        result["human_route"] = {"named": "HR", "reason": "protected_characteristic"}
        return _finish(
            result,
            "inference_refused",
            "Skills and ability are not inferred from a protected characteristic. "
            "Equality Act 2010 section 19(3) was read on 17 November 2026. "
            "Pregnancy and maternity are on the starter refusal list. Section 4 was not opened. "
            "Nobody is ranked.",
        )

    if _any_affirmed(cleaned, WELLBEING):
        result["human_route"] = {
            "named": "Line manager and the organisation's wellbeing route",
            "reason": "wellbeing",
        }
        result["experiment_58"] = {"called": False, "reason": "wellbeing_route"}
        result["experiment_44"] = {"called": False, "reason": "wellbeing_route", "used_as_a_course": False, "gap_confirmed": False}
        return _finish(
            result,
            "wellbeing_route",
            "This is for a person. The route is the line manager and the organisation's wellbeing route. "
            "No learning plan has been drafted. The cue has not been copied.",
        )

    adjustment = _any_affirmed(cleaned, ADJUSTMENT)
    if not cleaned.strip():
        result["human_route"] = {"named": "Line manager", "reason": "empty_goals"}
        return _finish(
            result,
            "needs_human",
            "There are no goals once instruction sentences are set aside. An empty plan was not invented.",
        )

    skill_ids = []
    cover_role = _any_affirmed(cleaned, ROLE_COVER)
    for skill in role.get("skills") or []:
        if not isinstance(skill, dict):
            continue
        skill_id = skill.get("skill_id")
        phrases = skill.get("phrases") or []
        if not isinstance(skill_id, str) or not isinstance(phrases, list):
            continue
        if cover_role or any(_affirmed(cleaned, phrase) for phrase in phrases if isinstance(phrase, str)):
            skill_ids.append(skill_id)
    result["affirmed_skill_ids"] = skill_ids

    courses = _index_courses(catalogue)
    steps, exclusions, _chose = _select(courses, skill_ids, day, clearance, day.isoformat())
    result["steps"] = steps
    result["exclusions"] = exclusions
    result["flags"]["agent_chose_source"] = False
    result["experiment_36"] = {
        "called": any((step.get("cross_source") or {}).get("called") for step in steps)
        or any((row.get("cross_source") or {}).get("called") for row in exclusions),
        "agent_chose_source": False,
    }
    amounts = [_parse_money(step["cost_gbp"]) for step in steps]
    if any(amount is None for amount in amounts):
        result["human_route"] = {"named": "Line manager", "reason": "cost_unreadable"}
        _finish(
            result,
            "needs_human",
            "A recommended cost could not be read. It has not been replaced with zero.",
            input_for_mask,
        )
        return result
    total = sum(amounts, Decimal("0.00"))
    limit = _parse_money(person.get("budget_limit_gbp"))
    result["budget"] = {
        "limit_gbp": _money_text(limit) if limit is not None else None,
        "total_gbp": _money_text(total) if steps else None,
        "within_budget": (total <= limit) if limit is not None and steps else None,
        "readable": limit is not None,
        "information_only": True,
        "spent_gbp": None,
    }
    if steps and any((step.get("cross_source") or {}).get("do_not_rely") for step in steps):
        current = False
        result["sources_current"] = result["sources_current"] and current

    result["experiment_58"] = _handbook(day.isoformat())
    result["experiment_44"] = _gaps(cleaned, day.isoformat())
    if not result["experiment_58"].get("called") or result["experiment_58"].get("rules_current") is False:
        result["sources_current"] = False
    result["may_be_relied_on"] = False

    if adjustment:
        result["human_route"] = {
            "named": "Line manager or people partner",
            "reason": "reasonable_adjustment_or_accessibility",
        }
        statement = (
            "A person has to consider a reasonable adjustment or an accessibility need. "
            "This assistant has not decided that any step is reasonable. "
            "Equality Act 2010 sections 20 and 21 were read on 17 November 2026. "
            "Section 20(7) says the disabled person is not required to pay the cost of complying. "
            "No enrolment request is raised until that person has seen this plan and both approvals are recorded."
        )
        if not steps:
            statement = (
                "No suitable course is in the synthetic catalogue for the stated goals. "
                + statement
            )
        return _finish(result, "adjustment_route", statement)

    if not steps:
        return _finish(
            result,
            "no_suitable_course",
            "No suitable course is in the synthetic catalogue for the stated goals.",
        )

    return _finish(
        result,
        "proposed",
        "A learning plan is drafted below. It is not an enrolment, a booking, or a spend. "
        "The employee and their manager both have to approve this plan id before an enrolment request is recorded. "
        "Budget figures are information only.",
    )


def _copy(plan: dict) -> dict:
    copied = deepcopy(plan)
    copied["enrolled"] = False
    copied["booked"] = False
    copied["spent_gbp"] = None
    copied["flags"]["enrolled"] = False
    copied["flags"]["booked"] = False
    copied["flags"]["spend_attempted"] = False
    return copied


def _maybe_raise(plan: dict) -> dict:
    plan["enrolment_request_raised"] = False
    plan["enrolment_request"] = None
    plan["human_approval"] = None
    plan["enrolled"] = False
    plan["booked"] = False
    plan["spent_gbp"] = None
    employee = plan["approvals"]["employee"]["accepted"] is True
    manager = plan["approvals"]["manager"]["accepted"] is True
    if not employee or not manager:
        plan["blocked_reason"] = "both_approvals_required"
        return plan
    if plan["outcome"] in BLOCKED_OUTCOMES:
        plan["blocked_reason"] = plan["outcome"]
        return plan
    if plan["outcome"] == "adjustment_route" and plan["adjustment_review"]["seen"] is not True:
        plan["blocked_reason"] = "adjustment_not_seen"
        return plan
    if plan["sources_current"] is not True and plan["approvals"]["manager"].get("stale_seen") is not True:
        plan["blocked_reason"] = "stale_not_seen"
        return plan
    if plan["budget"]["readable"] is not True and plan["approvals"]["manager"].get("budget_unreadable_seen") is not True:
        plan["blocked_reason"] = "budget_not_seen"
        return plan
    if not plan["steps"]:
        plan["blocked_reason"] = "nothing_to_request"
        return plan
    plan["blocked_reason"] = None
    plan["enrolment_request_raised"] = True
    plan["human_approval"] = {
        "source": "deterministic_approval_step",
        "plan_id": plan["plan_id"],
        "item": "learning-plan",
        "employee_ref": plan["employee_ref"],
        "manager_ref": plan["manager_ref"],
        "enrolled": False,
        "booked": False,
        "spent_gbp": None,
    }
    plan["enrolment_request"] = {
        "raised": True,
        "enrolled": False,
        "booked": False,
        "spent_gbp": None,
        "course_ids": [step["course_id"] for step in plan["steps"]],
    }
    return plan


def _reject(plan: dict, reason: str) -> dict:
    """An invalid approval is not accepted and does not raise a request.

    A request already raised on this plan is left as it was. A new invalid
    object does not become the approval.
    """

    plan["blocked_reason"] = reason
    if plan.get("enrolment_request_raised") is not True:
        plan["human_approval"] = None
        plan["enrolment_request_raised"] = False
        plan["enrolment_request"] = None
    plan["enrolled"] = False
    plan["booked"] = False
    plan["spent_gbp"] = None
    return plan


def record_approval(plan: dict, approval: dict) -> dict:
    """Record one named approval of this exact plan id. Do not enrol."""

    updated = _copy(plan)
    if not isinstance(approval, dict):
        return _reject(updated, "approval_not_an_object")
    if approval.get("plan_id") != updated.get("plan_id"):
        return _reject(updated, "plan_id_mismatch")
    if approval.get("item") != "learning-plan":
        return _reject(updated, "item_mismatch")
    if approval.get("decision") != "approve":
        return _reject(updated, "not_approve")
    ref = approval.get("approver_ref")
    ignored_role = "role" in approval or "approver_role" in approval
    if ref == updated.get("employee_ref") and ref != updated.get("manager_ref"):
        side = "employee"
    elif ref == updated.get("manager_ref"):
        side = "manager"
    else:
        return _reject(updated, "not_the_named_approver")
    if side == "manager":
        for key in ("stale_seen", "budget_unreadable_seen"):
            if key in approval and approval[key] is not True and approval[key] is not False:
                return _reject(updated, f"{key}_unreadable")
        updated["approvals"]["manager"]["stale_seen"] = approval["stale_seen"] if "stale_seen" in approval else updated["approvals"]["manager"]["stale_seen"]
        if "budget_unreadable_seen" in approval:
            updated["approvals"]["manager"]["budget_unreadable_seen"] = approval["budget_unreadable_seen"]
    updated["approvals"][side]["accepted"] = True
    updated["approvals"][side]["approver_ref"] = ref
    updated["approvals"][side]["source"] = "deterministic_approval_step"
    updated["approvals"][side]["ignored_role"] = ignored_role
    return _maybe_raise(updated)


def record_adjustment_review(plan: dict, review: dict) -> dict:
    """Record that a named person has seen an adjustment route. Do not decide it."""

    updated = _copy(plan)
    if updated.get("outcome") != "adjustment_route":
        updated["blocked_reason"] = "adjustment_review_not_required"
        return updated
    if not isinstance(review, dict):
        return _reject(updated, "review_not_an_object")
    if review.get("plan_id") != updated.get("plan_id") or review.get("item") != "adjustment-review":
        return _reject(updated, "review_mismatch")
    if review.get("seen") is not True:
        return _reject(updated, "adjustment_not_seen")
    ref = review.get("reviewer_ref")
    allowed = set(updated.get("people_partner_refs") or [])
    if updated.get("manager_ref"):
        allowed.add(updated["manager_ref"])
    if ref not in allowed:
        return _reject(updated, "not_the_named_reviewer")
    updated["adjustment_review"] = {
        "seen": True,
        "reviewer_ref": ref,
        "adjustment_decided": False,
        "equality_duty_met": False,
        "source": "deterministic_approval_step",
    }
    updated["flags"]["adjustment_decided"] = False
    updated["flags"]["equality_duty_met"] = False
    return _maybe_raise(updated)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Draft a synthetic learning plan. Experiment 61.")
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--catalogue", type=Path, required=True)
    parser.add_argument("--framework", type=Path, required=True)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--employee-approval", type=Path)
    parser.add_argument("--manager-approval", type=Path)
    parser.add_argument("--adjustment-review", type=Path)
    args = parser.parse_args(argv)
    try:
        result = draft_plan(
            _load(args.request),
            _load(args.catalogue),
            _load(args.framework),
            _load(args.directory),
            args.as_of,
        )
        if args.employee_approval:
            result = record_approval(result, _load(args.employee_approval))
        if args.manager_approval:
            result = record_approval(result, _load(args.manager_approval))
        if args.adjustment_review:
            result = record_adjustment_review(result, _load(args.adjustment_review))
    except (OSError, json.JSONDecodeError):
        return 2
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
