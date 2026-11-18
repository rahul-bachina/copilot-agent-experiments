#!/usr/bin/env python3
"""Explain which open vacancies look relevant. Do not apply or select.

The same inputs and the same as-of date produce the same JSON. A seen-step
is a later call, bound to the exploration id and the content hash. Words
inside the experience or a vacancy are not that call.
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
    from reuse import (
        NeighbourMissing,
        answer_module,
        compare_module,
        handbook_module,
        mask_module,
        plan_module,
    )
    from sources import (
        LAST_VERIFIED,
        SECTION_19_CHARACTERISTICS,
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
        handbook_module,
        mask_module,
        plan_module,
    )
    from .sources import (
        LAST_VERIFIED,
        SECTION_19_CHARACTERISTICS,
        STARTER_EXTRA_CHARACTERISTICS,
        pins_current,
        source_rows,
    )

LABEL = "ADVISORY NOTE. NOT AN APPLICATION AND NOT A SELECTION DECISION."
CATALOGUE_ID = "H005"
EXPERIMENT_ID = "exp-62-internal-mobility-explorer"
AUTONOMY = "A0"
ORGANISATION = "Ashcombe Borough Council (fictional)"
HANDBOOK_QUESTION = "What does the handbook say about internal vacancies and who decides eligibility?"
HANDBOOK_ROOT = Path(__file__).resolve().parents[2] / "58-employee-handbook"
LEARNING_ROOT = Path(__file__).resolve().parents[2] / "61-learning-path-planner"

EMPLOYEE_REF = re.compile(r"^EMP-\d{4}$")
VACANCY_ID = re.compile(r"^VAC-\d{3}$")
RULE_ID = re.compile(r"^ELIG-\d{3}$")
MAX_EXPERIENCE = 4000

PROHIBITED_KEYS = frozenset(
    {
        "approved",
        "human_approval",
        "hr_seen",
        "route_seen",
        "applied",
        "nominated",
        "shortlisted",
        "contacted",
        "eligibility_decided",
        "selection_made",
        "content_hash",
        "clearance",
        "role_id",
        "grade",
        "part_time",
        "length_of_service",
        "length_of_service_years",
        "age",
        "sickness",
        "maternity",
    }
)

# Directory fields that must not be read into a relevance judgement.
UNREAD_DIRECTORY_FIELDS = (
    "length_of_service",
    "length_of_service_years",
    "part_time",
    "age",
    "date_of_birth",
    "sickness",
    "sickness_absence",
    "maternity",
    "maternity_absence",
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
GRIEVANCE = (
    "raising a grievance",
    "formal grievance",
    "my grievance",
    "have a grievance",
    "lodge a grievance",
)
REDEPLOYMENT = (
    "at risk of redundancy",
    "redeployment",
    "at-risk register",
    "risk of redundancy",
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
INFER_VERBS = (
    "infer suitability",
    "assume suitability",
    "deduce suitability",
    "suitability from",
)
SELECTION = (
    "rank employees",
    "rank the staff",
    "rank the team",
    "rank staff",
    "score employees",
    "score me",
    "shortlist me",
    "i am the best candidate",
    "decide i should get",
    "give me the job",
)
SHARE = (
    "tell my manager",
    "let my manager know",
    "notify my manager",
    "tell the recruiter",
    "tell recruiters",
    "notify recruiters",
    "share my interest",
    "share this with my manager",
)
LEARNING = ("learning plan", "a course", "time for training")
PROXY_NEEDLES = (
    "length of service",
    "years of service",
    "years' service",
    "years service",
    "year of service",
    "full-time only",
    "full time only",
    "part-time",
    "part time",
    "sickness",
    "maternity",
    "years old",
    "date of birth",
    "under 40",
    "over 50",
)

BLOCKED_OUTCOMES = frozenset(
    {
        "wellbeing_route",
        "grievance_route",
        "redeployment_route",
        "adjustment_route",
        "inference_refused",
        "selection_refused",
        "share_refused",
        "needs_human",
        "refused",
        "above_clearance",
        "not_an_employee",
        "refused_jurisdiction",
    }
)

_handbook_cache: dict[str, dict] = {}
_compare_cache: dict[str, dict] = {}
_learning_cache: dict[str, dict] = {}


class MobilityForbidden(RuntimeError):
    """Raised when a caller asks the agent to apply, select, or contact someone."""


def apply(*_args, **_kwargs) -> None:
    raise MobilityForbidden("the agent does not apply for a vacancy")


def nominate(*_args, **_kwargs) -> None:
    raise MobilityForbidden("the agent does not nominate anyone")


def shortlist(*_args, **_kwargs) -> None:
    raise MobilityForbidden("the agent does not shortlist anyone")


def contact(*_args, **_kwargs) -> None:
    raise MobilityForbidden("the agent does not contact anyone")


def share_interest(*_args, **_kwargs) -> None:
    raise MobilityForbidden("the agent does not share interest with a manager or a recruiter")


def rank_employees(*_args, **_kwargs) -> None:
    raise MobilityForbidden("the agent does not rank employees")


def score_employees(*_args, **_kwargs) -> None:
    raise MobilityForbidden("the agent does not score employees")


def decide_selection(*_args, **_kwargs) -> None:
    raise MobilityForbidden("the agent does not make a selection decision")


def infer_suitability(*_args, **_kwargs) -> None:
    raise MobilityForbidden("the agent does not infer suitability")


def _flags() -> dict:
    return {
        "applied": False,
        "nominated": False,
        "shortlisted": False,
        "contacted": False,
        "selection_made": False,
        "selection_implied": False,
        "employees_ranked": False,
        "employees_scored": False,
        "suitability_inferred": False,
        "eligibility_decided": False,
        "adjustment_decided": False,
        "direct_discrimination_decided": False,
        "indirect_discrimination_decided": False,
        "equality_duty_met": False,
        "interest_shared_with_manager": False,
        "interest_shared_with_recruiters": False,
        "instructions_followed": False,
        "agent_chose_source": False,
        "coerced": False,
        "directory_proxy_fields_used": False,
        "solely_automated_decision": False,
        "significant_decision_decided": False,
        "output_is_anonymised": False,
        "experience_copied": False,
        "description_copied": False,
    }


def _base(as_of_text: str) -> dict:
    return {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment_id": EXPERIMENT_ID,
        "autonomy": AUTONOMY,
        "organisation": ORGANISATION,
        "as_of": as_of_text if isinstance(as_of_text, str) else "",
        "outcome": None,
        "statement": None,
        "exploration_id": None,
        "content_hash": None,
        "employee_ref": None,
        "role_id": None,
        "clearance": None,
        "hr_reviewer_refs": [],
        "order": "vacancy_id ascending. Not a ranking and not a score.",
        "relevant": [],
        "flagged": [],
        "open_not_listed": [],
        "hr_seen": {
            "recorded": False,
            "source": None,
            "approver_ref": None,
            "approver_role_id": None,
            "eligibility_decided": False,
            "selection_made": False,
            "interest_shared_with_manager": False,
            "interest_shared_with_recruiters": False,
        },
        "route_seen": {
            "recorded": False,
            "source": None,
            "approver_ref": None,
            "eligibility_decided": False,
            "interest_shared_with_manager": False,
        },
        "human_route": None,
        "flags": _flags(),
        "prompt_injection": {"detected": False, "followed": False, "signals": []},
        "self_declared_role_ignored": False,
        "self_declared_clearance_ignored": False,
        "sources_current": None,
        "sources": [],
        "statutory_note": None,
        "may_be_relied_on": False,
        "experiment_58": {"called": False},
        "experiment_36": {"called": False, "agent_chose_source": False},
        "experiment_61": {
            "called": False,
            "used_as_a_selection_factor": False,
            "enrolled": False,
            "selection_made": False,
        },
        "mask": None,
        "coerced": False,
    }


def _finish(result: dict, outcome: str, statement: str, input_text: str = "") -> dict:
    proxy_used = result["flags"]["directory_proxy_fields_used"] is True
    result["outcome"] = outcome
    result["statement"] = statement
    result["may_be_relied_on"] = False
    result["flags"]["instructions_followed"] = False
    result["flags"]["applied"] = False
    result["flags"]["nominated"] = False
    result["flags"]["shortlisted"] = False
    result["flags"]["contacted"] = False
    result["flags"]["selection_made"] = False
    result["flags"]["selection_implied"] = False
    result["flags"]["employees_ranked"] = False
    result["flags"]["employees_scored"] = False
    result["flags"]["eligibility_decided"] = False
    result["flags"]["adjustment_decided"] = False
    result["flags"]["interest_shared_with_manager"] = False
    result["flags"]["interest_shared_with_recruiters"] = False
    result["flags"]["agent_chose_source"] = False
    result["flags"]["coerced"] = False
    result["flags"]["directory_proxy_fields_used"] = proxy_used
    result["flags"]["solely_automated_decision"] = False
    result["flags"]["experience_copied"] = False
    result["flags"]["description_copied"] = False
    result["flags"]["output_is_anonymised"] = False
    result["coerced"] = False
    result["hr_seen"]["eligibility_decided"] = False
    result["hr_seen"]["selection_made"] = False
    result["hr_seen"]["interest_shared_with_manager"] = False
    result["hr_seen"]["interest_shared_with_recruiters"] = False
    _mask(result, input_text)
    result["content_hash"] = _content_hash(result)
    return result


def _content_hash(result: dict) -> str:
    payload = {
        key: value
        for key, value in result.items()
        if key not in {"content_hash", "hr_seen", "route_seen"}
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(raw.encode()).hexdigest()


def _mask(result: dict, text: str) -> None:
    counts = mask_module().mask_counts(text)
    blob = json.dumps(
        {key: value for key, value in result.items() if key != "mask"},
        default=str,
    )
    output = mask_module().mask_counts(blob)
    result["mask"] = {
        "input_counts": counts["counts"],
        "values_stored": False,
        "values_copied": any(output["counts"].values()),
        "described_as_anonymised": False,
        "output_is_anonymised": False,
    }
    result["flags"]["output_is_anonymised"] = False


def _parse_day(value: object):
    return handbook_module().parse_day(value)


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


def _proxy_phrase(phrase: str) -> bool:
    folded = phrase.casefold()
    if any(needle in folded for needle in PROXY_NEEDLES):
        return True
    return re.search(r"\bage\b", folded) is not None


def _statutory_note(current: bool) -> str:
    note = (
        f"Equality Act 2010 sections 13, 19, 20, 21, and 39 were read on {LAST_VERIFIED}. "
        "Extent England and Wales and Scotland, as the pages showed. "
        "Section 13(1) is direct discrimination. Section 19 is indirect discrimination. "
        "Sections 20 and 21 are the reasonable-adjustment duty and a failure to comply. "
        "Section 39(2)(b) covers access to opportunities for promotion, transfer, or training. "
        "Section 39(5) says a duty to make reasonable adjustments applies to an employer. "
        "This note does not decide that any of those sections was met. "
        "UK GDPR Article 5(1)(b) purpose limitation was read, including the words about "
        "not further processing in a manner incompatible with the purposes for which the "
        "controller collected the data. Article 5(3) was read and is not a lawful basis. "
        "Article 6 was not opened. The Article 5 extract did not include a revision-date "
        "banner. That banner date is unverified. "
        "The Article 22 page showed the body omitted. Articles 22A to 22D, substituted by "
        "the Data (Use and Access) Act 2025, section 80, were read on the section 80 page "
        "and Article 22A was read on its own page. S.I. 2026/82 was not opened. "
        "This note is not a selection decision and it does not decide whether it would be "
        "a significant decision under Article 22A. The old Article 22 wording is not quoted. "
        "HR validates eligibility. Interest has not been shared with a manager or a recruiter."
    )
    if not current:
        note += " The pins are outside the starter window and have not been refreshed."
    return note


def _strip_request(request: dict) -> tuple[dict, list[str]]:
    clean = {}
    stripped = []
    for key, value in request.items():
        if key in PROHIBITED_KEYS:
            stripped.append(key)
            continue
        clean[key] = value
    return clean, stripped


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


def _rules(rules: dict) -> dict[str, dict]:
    found = {}
    for rule in rules.get("rules") or []:
        if isinstance(rule, dict) and isinstance(rule.get("rule_id"), str):
            found[rule["rule_id"]] = rule
    return found


def _vacancy_text(vacancy: dict) -> str:
    parts = []
    for key in ("description", "cover"):
        if isinstance(vacancy.get(key), str):
            parts.append(vacancy[key])
    return "\n".join(parts)


def _criterion_phrases(vacancy: dict, field: str) -> list[str]:
    rows = vacancy.get(field) or []
    if not isinstance(rows, list):
        return []
    phrases = []
    for row in rows:
        if isinstance(row, str) and row.strip():
            phrases.append(row.strip())
        elif isinstance(row, dict) and isinstance(row.get("phrase"), str) and row["phrase"].strip():
            phrases.append(row["phrase"].strip())
    return phrases


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
    except (OSError, json.JSONDecodeError, NeighbourMissing, KeyError, TypeError, ValueError) as exc:
        record = {
            "called": False,
            "reason": type(exc).__name__,
            "outcome": None,
            "covered": False,
            "entitlement_decision": None,
            "eligibility_decided": False,
        }
        _handbook_cache[as_of] = record
        return record
    record = {
        "called": True,
        "experiment_id": "exp-58-employee-handbook",
        "question_fixed": True,
        "outcome": answer.get("outcome"),
        "covered": answer.get("outcome") == "answered",
        "entitlement_decision": answer.get("entitlement_decision"),
        "eligibility_decided": False,
        "answer_copied": False,
        "note": (
            "A fixed question was asked of the synthetic handbook. "
            "A gap is not filled with an eligibility decision. "
            "HR validates eligibility."
        ),
    }
    _handbook_cache[as_of] = record
    return record


def _compare_dates(vacancy: dict, as_of: str) -> dict:
    closing = vacancy.get("closing_date")
    other = vacancy.get("other_closing_date")
    if not isinstance(other, str):
        return {"called": False, "reason": "single_source", "agent_chose_source": False, "material": False}
    if not isinstance(closing, str):
        return {
            "called": False,
            "reason": "closing_date_unreadable",
            "agent_chose_source": False,
            "material": True,
            "do_not_rely": True,
        }
    vacancy_id = str(vacancy.get("vacancy_id") or "vac").lower()
    key = hashlib.sha256(
        json.dumps({"c": closing, "o": other, "as_of": as_of, "id": vacancy_id}, sort_keys=True).encode()
    ).hexdigest()
    if key in _compare_cache:
        return _compare_cache[key]
    slug = re.sub(r"[^a-z0-9-]", "", vacancy_id)[:20] or "vacancy"
    pack = {
        "synthetic": True,
        "pack_id": f"vac-{slug}"[:40],
        "facts": [{"fact_key": "closing_date", "field_type": "date"}],
        "documents": [
            {
                "document_id": f"feed-{slug}"[:40],
                "title": "Vacancy feed extract",
                "kind": "form",
                "status": "current",
                "reviewed_on": as_of,
                "pages": [{"page": 1, "paragraphs": [{"paragraph": 1, "lines": [{"line": 1, "text": closing.strip()}]}]}],
                "fields": [
                    {"fact_key": "closing_date", "page": 1, "paragraph": 1, "line": 1, "value": closing.strip()}
                ],
            },
            {
                "document_id": f"note-{slug}"[:40],
                "title": "Second closing-date extract",
                "kind": "contract",
                "status": "current",
                "reviewed_on": as_of,
                "pages": [{"page": 1, "paragraphs": [{"paragraph": 1, "lines": [{"line": 1, "text": other.strip()}]}]}],
                "fields": [
                    {"fact_key": "closing_date", "page": 1, "paragraph": 1, "line": 1, "value": other.strip()}
                ],
            },
        ],
    }
    try:
        report = compare_module().compare(pack, as_of)
    except Exception as exc:  # noqa: BLE001 - a neighbour failure is a human flag, not a chosen date
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


def _learning(employee_ref: str, experience: str, directory: dict, framework: dict, as_of: str) -> dict:
    if not _any_affirmed(experience, LEARNING):
        return {
            "called": False,
            "reason": "not_asked",
            "used_as_a_selection_factor": False,
            "enrolled": False,
            "selection_made": False,
        }
    key = hashlib.sha256((employee_ref + "\n" + as_of + "\n" + experience).encode()).hexdigest()
    if key in _learning_cache:
        return deepcopy(_learning_cache[key])
    try:
        catalogue = json.loads((LEARNING_ROOT / "fixtures" / "catalogue.json").read_text(encoding="utf-8"))
        plan = plan_module().draft_plan(
            {"synthetic": True, "employee_ref": employee_ref, "goals": experience},
            catalogue,
            framework,
            directory,
            as_of,
        )
    except (OSError, json.JSONDecodeError, NeighbourMissing, TypeError, ValueError) as exc:
        record = {
            "called": False,
            "reason": type(exc).__name__,
            "used_as_a_selection_factor": False,
            "enrolled": False,
            "selection_made": False,
        }
        _learning_cache[key] = record
        return record
    steps = plan.get("steps") if isinstance(plan.get("steps"), list) else []
    record = {
        "called": True,
        "experiment_id": "exp-61-learning-path-planner",
        "outcome": plan.get("outcome"),
        "course_ids": [step.get("course_id") for step in steps if isinstance(step, dict)],
        "human_approval": plan.get("human_approval"),
        "enrolment_request_raised": plan.get("enrolment_request_raised") is True,
        "enrolled": plan.get("enrolled") is True,
        "used_as_a_selection_factor": False,
        "selection_made": False,
        "note": (
            "A learning plan was drafted from the same stated experience. "
            "It is not a reason a vacancy looks relevant, and it is not an application."
        ),
    }
    _learning_cache[key] = record
    return deepcopy(record)


def _row_common(vacancy: dict, text: str) -> dict:
    marking = _higher(_labels(vacancy.get("marking"), text))
    return {
        "vacancy_id": vacancy.get("vacancy_id"),
        "title": vacancy.get("title") if isinstance(vacancy.get("title"), str) else None,
        "marking": marking,
        "retention_labels": handbook_module().retention_labels(vacancy, text),
        "legal_hold": handbook_module().legal_hold(vacancy, text),
        "description_copied": False,
        "closing_date_used": None,
    }


def _eligibility(vacancy: dict, rule_index: dict[str, dict]) -> dict:
    rule_id = vacancy.get("eligibility_rule_id")
    if not isinstance(rule_id, str) or not RULE_ID.fullmatch(rule_id) or rule_id not in rule_index:
        return {
            "status": "unclear",
            "rule_id": rule_id if isinstance(rule_id, str) else None,
            "rule_quote": None,
            "decided_by_agent": False,
            "statement": (
                "Eligibility is unclear. The HR eligibility rule is missing or could not be read. "
                "HR validates eligibility. This assistant has not decided eligibility."
            ),
        }
    rule = rule_index[rule_id]
    quote = rule.get("text") if isinstance(rule.get("text"), str) else None
    clear = rule.get("clear") is True and isinstance(quote, str) and bool(quote.strip())
    if not clear:
        return {
            "status": "unclear",
            "rule_id": rule_id,
            "rule_quote": quote,
            "decided_by_agent": False,
            "statement": (
                "Eligibility is unclear. The HR rule does not state a check this assistant can cite as settled. "
                "HR validates eligibility. This assistant has not decided eligibility."
            ),
        }
    return {
        "status": "hr_must_validate",
        "rule_id": rule_id,
        "rule_quote": quote,
        "decided_by_agent": False,
        "statement": (
            f"HR eligibility rule {rule_id} is cited. HR validates eligibility. "
            "This assistant has not decided eligibility. This is not a selection decision."
        ),
    }


def _consider(vacancy: dict, experience: str, as_of: date, ceiling: str, as_of_text: str, rule_index: dict) -> dict:
    text = _vacancy_text(vacancy)
    common = _row_common(vacancy, text)
    vacancy_id = vacancy.get("vacancy_id")
    if not isinstance(vacancy_id, str) or not VACANCY_ID.fullmatch(vacancy_id):
        return {**common, "kind": "flagged", "reason": "vacancy_id"}
    status = vacancy.get("status")
    if status == "closed":
        return {**common, "kind": "flagged", "reason": "closed"}
    if status != "open":
        return {**common, "kind": "flagged", "reason": "status_unreadable"}
    closing = _parse_day(vacancy.get("closing_date"))
    if closing is None:
        return {**common, "kind": "flagged", "reason": "closing_date_unreadable"}
    review = _parse_day(vacancy.get("review_due"))
    if review is None:
        return {**common, "kind": "flagged", "reason": "review_date_unreadable"}
    if closing < as_of:
        return {**common, "kind": "flagged", "reason": "closed_by_date", "closing_date": closing.isoformat()}
    if review <= as_of:
        return {**common, "kind": "flagged", "reason": "stale", "review_due": review.isoformat()}
    compared = _compare_dates(vacancy, as_of_text)
    if compared.get("agent_chose_source") or compared.get("material") or compared.get("do_not_rely"):
        return {
            **common,
            "kind": "flagged",
            "reason": "source_discrepancy",
            "cross_source": compared,
            "agent_chose_source": False,
        }
    marking = common["marking"]
    if marking is None:
        return {**common, "kind": "flagged", "reason": "marking_missing"}
    if handbook_module().above_ceiling(marking, ceiling):
        return {**common, "kind": "flagged", "reason": "above_clearance"}
    grade = vacancy.get("grade") if isinstance(vacancy.get("grade"), str) and vacancy.get("grade").strip() else None
    location = vacancy.get("location") if isinstance(vacancy.get("location"), str) and vacancy.get("location").strip() else None
    if grade is None or location is None:
        return {**common, "kind": "flagged", "reason": "grade_or_location_unreadable"}

    essential = _criterion_phrases(vacancy, "essential")
    desirable = _criterion_phrases(vacancy, "desirable")
    proxies = [phrase for phrase in essential + desirable if _proxy_phrase(phrase)]
    usable_essential = [phrase for phrase in essential if phrase not in proxies]
    usable_desirable = [phrase for phrase in desirable if phrase not in proxies]
    if not usable_essential and not usable_desirable:
        return {**common, "kind": "flagged", "reason": "proxy_not_used", "proxies_ignored": proxies}

    affirmed_essential = [phrase for phrase in usable_essential if _affirmed(experience, phrase)]
    affirmed_desirable = [phrase for phrase in usable_desirable if _affirmed(experience, phrase)]
    if not affirmed_essential and not affirmed_desirable:
        return {
            **common,
            "kind": "open_not_listed",
            "reason": "no_stated_phrase",
            "note": "Omission is not a finding that the employee is unsuitable, and it is not a selection decision.",
        }

    eligibility = _eligibility(vacancy, rule_index)
    if eligibility["status"] == "unclear":
        # Still list the vacancy, and say eligibility is unclear.
        pass
    bits = []
    for phrase in affirmed_essential:
        bits.append(f'includes "{phrase}", which vacancy {vacancy_id} lists as essential')
    for phrase in affirmed_desirable:
        bits.append(f'includes "{phrase}", which vacancy {vacancy_id} lists as desirable')
    missing = [phrase for phrase in usable_essential if phrase not in affirmed_essential]
    why = "The experience you stated " + ", and ".join(bits) + "."
    if missing:
        why += " An essential phrase was not stated: " + "; ".join(missing) + "."
    if proxies:
        why += " Proxy criteria were not used."
    why += " " + eligibility["statement"]
    return {
        **common,
        "kind": "relevant",
        "grade": grade,
        "location": location,
        "closing_date": closing.isoformat(),
        "closing_on_as_of": closing == as_of,
        "review_due": review.isoformat(),
        "essential_affirmed": affirmed_essential,
        "desirable_affirmed": affirmed_desirable,
        "essential_not_stated": missing,
        "proxies_ignored": proxies,
        "why": why,
        "eligibility": eligibility,
        "citations": [
            {
                "vacancy_id": vacancy_id,
                "field": "essential" if affirmed_essential else "desirable",
                "phrases": affirmed_essential or affirmed_desirable,
            },
            {
                "rule_id": eligibility["rule_id"],
                "field": "text",
                "status": eligibility["status"],
            },
        ],
        "cross_source": compared,
        "score": None,
        "rank": None,
    }


def _directory_proxy_leak(person: dict, blob: str) -> bool:
    for field in UNREAD_DIRECTORY_FIELDS:
        value = person.get(field)
        if isinstance(value, str) and value and value in blob:
            return True
    return False


def explore(request: dict, vacancies: dict, rules: dict, framework: dict, directory: dict, as_of: str) -> dict:
    """Return one advisory note. Nothing is applied. Nobody is selected."""

    result = _base(as_of if isinstance(as_of, str) else "")
    if not isinstance(request, dict) or not isinstance(vacancies, dict):
        return _finish(result, "refused", "The request or the vacancy feed could not be read. Nothing was copied.")
    if (
        vacancies.get("synthetic") is not True
        or rules.get("synthetic") is not True
        or framework.get("synthetic") is not True
        or directory.get("synthetic") is not True
    ):
        return _finish(result, "refused", "A file is not marked synthetic. Nothing was copied.")
    if request.get("synthetic") is not True:
        return _finish(result, "refused", "The request is not marked synthetic. Nothing was copied.")

    clean, stripped = _strip_request(request)
    raw_experience = clean.get("experience")
    experience = raw_experience if isinstance(raw_experience, str) else ""
    injection = scan_text(experience)
    for vacancy in vacancies.get("vacancies") or []:
        if isinstance(vacancy, dict):
            found = scan_text(
                _vacancy_text(vacancy)
                + "\n"
                + "\n".join(_criterion_phrases(vacancy, "essential") + _criterion_phrases(vacancy, "desirable"))
            )
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
    cleaned = without_instruction_sentences(experience)
    feed_text = "\n".join(
        _vacancy_text(vacancy) for vacancy in vacancies.get("vacancies") or [] if isinstance(vacancy, dict)
    )
    input_for_mask = experience + "\n" + feed_text

    day = _parse_day(as_of)
    if day is None:
        result["human_route"] = {"named": "HR", "reason": "unparseable_as_of"}
        return _finish(
            result,
            "needs_human",
            "The as-of date could not be read. It has not been replaced with today or with zero.",
            input_for_mask,
        )
    result["as_of"] = day.isoformat()
    current = pins_current(day)
    result["sources_current"] = current
    result["sources"] = source_rows(current)
    result["statutory_note"] = _statutory_note(current)

    if not isinstance(raw_experience, str) or len(raw_experience) > MAX_EXPERIENCE:
        result["human_route"] = {"named": "HR", "reason": "experience_unreadable"}
        return _finish(
            result,
            "needs_human",
            "The experience could not be read, or it is longer than this starter will read. It was not truncated and it was not replaced with an empty list.",
            input_for_mask,
        )

    employee_ref = clean.get("employee_ref")
    if not isinstance(employee_ref, str) or not EMPLOYEE_REF.fullmatch(employee_ref):
        result["human_route"] = {"named": "HR", "reason": "employee_ref"}
        return _finish(
            result,
            "needs_human",
            "The employee reference could not be read. A self-declared role in the text was not used.",
            input_for_mask,
        )
    person = _lookup(directory, employee_ref)
    if person is None:
        result["employee_ref"] = employee_ref
        result["human_route"] = {"named": "HR", "reason": "unknown_employee"}
        return _finish(
            result,
            "needs_human",
            "That reference is not in the synthetic directory. The request was not given a default role or a default clearance.",
            input_for_mask,
        )

    result["employee_ref"] = employee_ref
    result["self_declared_role_ignored"] = "self_role" in injection["signals"] or "role_id" in stripped
    result["self_declared_clearance_ignored"] = "self_clearance" in injection["signals"] or "clearance" in stripped
    if person.get("account_status") != "employee":
        result["human_route"] = {"named": "HR", "reason": "not_an_employee"}
        return _finish(
            result,
            "not_an_employee",
            "The directory does not list this reference as an employee. A sentence in the request is not a status.",
            input_for_mask,
        )

    role_id = person.get("role_id")
    role = _role(framework, role_id) if isinstance(role_id, str) else None
    if role is None:
        result["human_route"] = {"named": "HR", "reason": "role_unreadable"}
        return _finish(
            result,
            "needs_human",
            "The directory role is not in the skills framework. The role named in the request was not used.",
            input_for_mask,
        )
    result["role_id"] = role_id
    clearance = person.get("clearance")
    rank = handbook_module().RANK
    if not isinstance(clearance, str) or clearance not in rank:
        result["human_route"] = {"named": "HR", "reason": "clearance_unreadable"}
        return _finish(
            result,
            "needs_human",
            "The directory clearance could not be read. It has not been replaced with OFFICIAL, and a clearance typed in the request was not used.",
            input_for_mask,
        )
    result["clearance"] = clearance
    result["hr_reviewer_refs"] = sorted(
        row["employee_ref"]
        for row in directory.get("employees") or []
        if isinstance(row, dict)
        and row.get("role_id") == "ROLE-HR"
        and row.get("account_status") == "employee"
        and isinstance(row.get("employee_ref"), str)
    )
    digest = hashlib.sha256(
        (employee_ref + "\n" + day.isoformat() + "\n" + cleaned).encode()
    ).hexdigest()[:12]
    result["exploration_id"] = f"EXPL-{digest}"

    request_marking = _higher(_labels(clean.get("marking"), experience))
    if request_marking is not None and handbook_module().above_ceiling(request_marking, clearance):
        result["human_route"] = {"named": "Information governance", "reason": "above_clearance"}
        return _finish(
            result,
            "above_clearance",
            "The request carries a marking above the directory clearance. The experience was not copied and was not used to list a vacancy.",
            input_for_mask,
        )

    if _affirmed(cleaned, "northern ireland"):
        result["human_route"] = {"named": "HR", "reason": "northern_ireland"}
        return _finish(
            result,
            "refused_jurisdiction",
            "This starter does not state Northern Ireland employment equality law. The Equality Act 2010 sections opened here are marked England and Wales and Scotland. That legislation for Northern Ireland was not opened.",
            input_for_mask,
        )

    if _any_affirmed(cleaned, WELLBEING):
        result["human_route"] = {"named": "HR and the organisation's wellbeing route", "reason": "wellbeing"}
        result["experiment_58"] = {"called": False, "reason": "wellbeing_route", "eligibility_decided": False}
        result["experiment_61"] = {
            "called": False,
            "reason": "wellbeing_route",
            "used_as_a_selection_factor": False,
            "enrolled": False,
            "selection_made": False,
        }
        return _finish(
            result,
            "wellbeing_route",
            "This is for a person. The route is HR and the organisation's wellbeing route. "
            "No vacancy list has been produced. The cue has not been copied. "
            "Your interest has not been shared with your manager or with recruiters.",
            input_for_mask,
        )

    if _any_affirmed(cleaned, GRIEVANCE):
        result["human_route"] = {"named": "HR", "reason": "grievance"}
        return _finish(
            result,
            "grievance_route",
            "A grievance is for HR. No vacancy list has been produced. The cue has not been copied. "
            "This is not a selection decision.",
            input_for_mask,
        )

    if _any_affirmed(cleaned, REDEPLOYMENT):
        result["human_route"] = {"named": "HR", "reason": "redeployment"}
        return _finish(
            result,
            "redeployment_route",
            "Redeployment at risk is for HR. No vacancy list has been produced. The cue has not been copied. "
            "This is not a selection decision.",
            input_for_mask,
        )

    if _any_affirmed(cleaned, ADJUSTMENT):
        result["human_route"] = {"named": "HR", "reason": "reasonable_adjustment"}
        return _finish(
            result,
            "adjustment_route",
            "A reasonable adjustment is for HR. Equality Act 2010 sections 20, 21, and 39(5) were read. "
            "This assistant has not decided that the duty was met. No vacancy list has been produced.",
            input_for_mask,
        )

    characteristics = SECTION_19_CHARACTERISTICS + STARTER_EXTRA_CHARACTERISTICS
    inferred = False
    for sentence in handbook_module().sentences(cleaned):
        if any(_affirmed(sentence, verb) for verb in INFER_VERBS) and any(
            _affirmed(sentence, characteristic) for characteristic in characteristics
        ):
            inferred = True
            break
    if inferred:
        result["human_route"] = {"named": "HR", "reason": "protected_characteristic"}
        return _finish(
            result,
            "inference_refused",
            "Suitability is not inferred from a protected characteristic, from age, from length of service, "
            "from part-time status, from sickness absence, or from maternity absence. "
            "Equality Act 2010 section 13(1) and section 19(3) were read on 18 November 2026. "
            "Nobody is ranked and nobody is scored.",
            input_for_mask,
        )

    if _any_affirmed(cleaned, SELECTION):
        result["human_route"] = {"named": "HR", "reason": "selection"}
        return _finish(
            result,
            "selection_refused",
            "This assistant does not rank, score, shortlist, or decide who should get a job. "
            "selection_made stays false. This is not a selection decision.",
            input_for_mask,
        )

    if _any_affirmed(cleaned, SHARE):
        result["human_route"] = {"named": "HR", "reason": "do_not_share"}
        return _finish(
            result,
            "share_refused",
            "Interest is not shared with a manager or with recruiters. Nothing was sent.",
            input_for_mask,
        )

    if not cleaned.strip():
        result["human_route"] = {"named": "HR", "reason": "empty_experience"}
        return _finish(
            result,
            "needs_human",
            "There is no experience once instruction sentences are set aside. An empty recommendation was not invented.",
            input_for_mask,
        )

    rule_index = _rules(rules)
    relevant = []
    flagged = []
    open_not_listed = []
    any_compare = False
    for vacancy in vacancies.get("vacancies") or []:
        if not isinstance(vacancy, dict):
            flagged.append({"vacancy_id": None, "reason": "vacancy_unreadable", "description_copied": False})
            continue
        row = _consider(vacancy, cleaned, day, clearance, day.isoformat(), rule_index)
        kind = row.pop("kind")
        if row.get("cross_source", {}).get("called"):
            any_compare = True
        if kind == "relevant":
            relevant.append(row)
        elif kind == "open_not_listed":
            open_not_listed.append(
                {
                    "vacancy_id": row["vacancy_id"],
                    "reason": row["reason"],
                    "note": row["note"],
                    "marking": row["marking"],
                    "retention_labels": row["retention_labels"],
                    "legal_hold": row["legal_hold"],
                    "description_copied": False,
                }
            )
        else:
            flagged.append(row)

    relevant.sort(key=lambda row: str(row.get("vacancy_id")))
    flagged.sort(key=lambda row: str(row.get("vacancy_id")))
    open_not_listed.sort(key=lambda row: str(row.get("vacancy_id")))
    result["relevant"] = relevant
    result["flagged"] = flagged
    result["open_not_listed"] = open_not_listed
    result["experiment_36"] = {
        "called": any_compare,
        "agent_chose_source": False,
        "note": "A second closing date is compared. The agent does not choose a date.",
    }
    result["experiment_58"] = _handbook(day.isoformat())
    result["experiment_61"] = _learning(employee_ref, cleaned, directory, framework, day.isoformat())

    # The learning plan must not change the vacancy list. It is attached after the list is fixed.
    if not relevant:
        statement = (
            "No open vacancy in the synthetic feed looks relevant to the experience you stated. "
            "Closed and stale vacancies are flagged and are not treated as open. "
            "HR validates eligibility. This is not a selection decision. "
            "Your interest has not been shared with your manager or with recruiters."
        )
        outcome = "no_open_match"
    else:
        statement = (
            "These open vacancies look relevant because the experience you stated includes a phrase the vacancy lists. "
            "Each listed row cites the vacancy and the HR eligibility rule. "
            "Where eligibility is unclear, the row says so. HR validates eligibility. "
            "This is not a selection decision. The list is in vacancy-id order. It is not a rank and it is not a score. "
            "Your interest has not been shared with your manager or with recruiters."
        )
        outcome = "advisory"

    if _directory_proxy_leak(person, json.dumps(result, default=str)):
        result["flags"]["directory_proxy_fields_used"] = True
    return _finish(result, outcome, statement, input_for_mask)


def _hr_person(directory: dict, approver_ref: object) -> dict | None:
    if not isinstance(approver_ref, str) or not EMPLOYEE_REF.fullmatch(approver_ref):
        return None
    for person in directory.get("employees") or []:
        if not isinstance(person, dict):
            continue
        if person.get("employee_ref") != approver_ref:
            continue
        if person.get("account_status") != "employee":
            return None
        if person.get("role_id") != "ROLE-HR":
            return None
        return person
    return None


def record_hr_seen(note: dict, review: dict, directory: dict) -> dict:
    """Record that directory HR has seen this exact note. Eligibility stays undecided."""

    result = deepcopy(note)
    if not isinstance(review, dict):
        result["hr_seen"]["recorded"] = False
        result["hr_seen"]["source"] = None
        return result
    person = _hr_person(directory, review.get("approver_ref"))
    matches = (
        person is not None
        and review.get("decision") == "seen"
        and review.get("item") == "eligibility-note"
        and review.get("exploration_id") == result.get("exploration_id")
        and isinstance(review.get("content_hash"), str)
        and review.get("content_hash") == result.get("content_hash")
        and result.get("outcome") in {"advisory", "no_open_match"}
    )
    if not matches:
        result["hr_seen"]["recorded"] = False
        result["hr_seen"]["source"] = None
        result["hr_seen"]["approver_ref"] = None
        return result
    result["hr_seen"] = {
        "recorded": True,
        "source": "deterministic_hr_seen_step",
        "approver_ref": person["employee_ref"],
        "approver_role_id": "ROLE-HR",
        "eligibility_decided": False,
        "selection_made": False,
        "interest_shared_with_manager": False,
        "interest_shared_with_recruiters": False,
    }
    result["flags"]["eligibility_decided"] = False
    result["flags"]["selection_made"] = False
    result["flags"]["interest_shared_with_manager"] = False
    result["flags"]["interest_shared_with_recruiters"] = False
    result["flags"]["applied"] = False
    return result


def record_route_seen(note: dict, review: dict, directory: dict) -> dict:
    """Record that directory HR has seen a human route. The case is not decided."""

    result = deepcopy(note)
    if not isinstance(review, dict):
        result["route_seen"]["recorded"] = False
        return result
    person = _hr_person(directory, review.get("approver_ref"))
    matches = (
        person is not None
        and review.get("decision") == "seen"
        and review.get("item") == "human-route"
        and review.get("exploration_id") == result.get("exploration_id")
        and isinstance(review.get("content_hash"), str)
        and review.get("content_hash") == result.get("content_hash")
        and result.get("outcome") in BLOCKED_OUTCOMES
        and isinstance(result.get("human_route"), dict)
    )
    if not matches:
        result["route_seen"]["recorded"] = False
        result["route_seen"]["source"] = None
        return result
    result["route_seen"] = {
        "recorded": True,
        "source": "deterministic_route_seen_step",
        "approver_ref": person["employee_ref"],
        "eligibility_decided": False,
        "interest_shared_with_manager": False,
    }
    result["flags"]["adjustment_decided"] = False
    result["flags"]["interest_shared_with_manager"] = False
    result["outcome"] = note.get("outcome")
    return result


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Explain relevant internal vacancies. Experiment 62.")
    parser.add_argument("--request", type=Path)
    parser.add_argument("--vacancies", type=Path)
    parser.add_argument("--rules", type=Path)
    parser.add_argument("--framework", type=Path)
    parser.add_argument("--directory", type=Path)
    parser.add_argument("--as-of", default="2026-11-18")
    args = parser.parse_args(argv)
    if not all([args.request, args.vacancies, args.rules, args.framework, args.directory]):
        print("A request, a vacancy feed, rules, a framework, and a directory are required.", file=sys.stderr)
        return 2
    try:
        result = explore(
            _load(args.request),
            _load(args.vacancies),
            _load(args.rules),
            _load(args.framework),
            _load(args.directory),
            args.as_of,
        )
    except (OSError, json.JSONDecodeError):
        print("The input could not be read.", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
