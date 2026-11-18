"""Explain a synthetic leave policy and the statutory baseline.

The same inputs produce the same JSON. entitlement_decision stays null.
The agent does not book leave, record leave, or calculate pay.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.reuse import (  # noqa: E402
    EXPERIMENTS,
    NeighbourMissing,
    answer_module,
    gateway_module,
    handbook_module,
    injection_module,
    manifest_module,
    mask_module,
)
from src.sources import LAST_VERIFIED, PINNED_ON, PINS, STALE_AFTER_DAYS, TOPIC_PINS, pin  # noqa: E402

LABEL = "POLICY EXPLANATION. NOT AN ENTITLEMENT DECISION."
CATALOGUE_ID = "H006"
CALLER = "exp-63-leave-policy-explainer"
HANDBOOK_QUESTION = "What does the leave policy state for a worker on a five-day week?"
DISTINCTION = (
    "The figure in the policy is the employer's contractual scheme. "
    "The statutory minimum is cited separately. Neither is applied to a person."
)
HUMAN = "HR or the line manager decides entitlement. This explanation does not."
CARE_ANSWER = (
    "This question is routed to HR or the line manager, with care. "
    "It is not treated as a routine policy question. "
    "No entitlement is decided, no leave is booked, and no pay is calculated. "
    "A person is available."
)

PROHIBITED_KEYS = {
    "approved",
    "entitlement_decision",
    "human_approval",
    "leave_booked",
    "leave_recorded",
    "pay_decision",
    "pay_rate",
    "clearance",
    "role",
    "approver_ref",
    "document_ids",
    "explanation_hash",
}

TOPIC_PHRASES: tuple[tuple[str, tuple[str, ...], tuple[str, ...]], ...] = (
    ("neonatal", ("neonatal",), ()),
    ("shared_parental", ("shared parental",), ()),
    ("parental_bereavement", ("parental bereavement",), ()),
    ("parental_leave", ("parental leave", "unpaid parental"), ("shared parental",)),
    ("maternity", ("maternity",), ()),
    ("paternity", ("paternity",), ()),
    ("adoption", ("adoption leave", "adoption"), ()),
    ("carer", ("carer's leave", "carer"), ()),
    ("jury", ("jury service", "jury"), ()),
    ("sickness", ("sickness", "sick pay", "sick leave"), ()),
    ("annual", ("annual leave", "holiday entitlement"), ()),
    ("bereavement", ("bereavement",), ()),
    ("pay", ("payroll rate", "payroll rates"), ()),
)

CARE_PHRASES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("miscarriage", ("miscarriage", "miscarried")),
    ("domestic_abuse", ("domestic abuse", "hurting me", "hits me", "frightened at home", "scared to go home")),
    (
        "distress",
        (
            "can't cope",
            "cannot cope",
            "cannot face work",
            "do not know how i will manage",
            "don't know how i'll manage",
            "i am not okay",
            "i'm not okay",
            "things at home have got frightening",
        ),
    ),
    ("pregnancy", ("i am pregnant", "i'm pregnant", "my pregnancy")),
    (
        "bereavement_personal",
        ("my mother died", "my father died", "my child died", "my baby died", "i am bereaved", "we lost our"),
    ),
    (
        "sickness_personal",
        ("i am off sick", "i am too ill", "i'm too ill", "my sick pay", "how much sick pay will i get"),
    ),
    ("disability", ("my disability", "i am disabled", "i'm disabled", "reasonable adjustment for me")),
    ("pregnancy_loss_personal", ("my pregnancy loss", "i had a pregnancy loss", "i lost the pregnancy")),
)

ENTITLEMENT_ASKS = (
    "am i entitled",
    "do i qualify",
    "how many days do i have",
    "how much will i be paid",
    "calculate my pay",
    "what will i be paid",
)

CLAIM_PHRASES = {
    "annual": ("buying extra leave", "30 days", "25 days"),
    "sickness": ("unpaid leave after the contractual period",),
    "bereavement": ("paid leave for a colleague",),
    "carer": ("two weeks",),
}

_BALANCE = re.compile(r"\bbalance is\s+([^\s.,;]+)", re.IGNORECASE)
_SELF_ROLE = re.compile(
    r"\bi am hr\b|\bmy role is\b|\bi am the line manager\b|\bi am a guest\b",
    re.IGNORECASE,
)
_CLEARANCE = re.compile(
    r"\bmy clearance is\b|\bi have\s+(?:secret|top secret)\s+clearance\b",
    re.IGNORECASE,
)

_handbook_cache: dict[str, dict] = {}
_manifest_cache: dict | None = None

FACTS = [
    "Whether the person is an employee or a worker",
    "The start date and the length of service",
    "Earnings, where a statutory payment depends on them",
    "The dates of the absence and, where relevant, the child's date of birth",
    "Leave already taken",
]


class LeaveForbidden(RuntimeError):
    """A prohibited action. The agent has no path that does it."""


def decide_entitlement(*_args, **_kwargs) -> None:
    raise LeaveForbidden("This agent does not decide entitlement.")


def book_leave(*_args, **_kwargs) -> None:
    raise LeaveForbidden("This agent does not book leave.")


def record_leave(*_args, **_kwargs) -> None:
    raise LeaveForbidden("This agent does not record leave.")


def calculate_pay(*_args, **_kwargs) -> None:
    raise LeaveForbidden("This agent does not calculate pay.")


def approve_policy(*_args, **_kwargs) -> None:
    raise LeaveForbidden("This agent does not approve a policy.")


def _empty_mask() -> dict:
    return {
        "counts": {
            "phone": 0,
            "email": 0,
            "date_of_birth": 0,
            "postal_address": 0,
            "personal_name": 0,
        },
        "any": False,
        "values_stored": False,
        "values_copied": False,
        "described_as_anonymised": False,
    }


def _base(as_of_text: str | None) -> dict:
    return {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment": "63-leave-policy-explainer",
        "autonomy": "A0",
        "synthetic": True,
        "as_of": as_of_text,
        "about_date": None,
        "about_date_source": None,
        "outcome": None,
        "answer": "",
        "entitlement_decision": None,
        "pay_decision": None,
        "pay_rate": None,
        "leave_booked": False,
        "leave_recorded": False,
        "approved": False,
        "human_approval": None,
        "human_route": {
            "to": "HR or the line manager",
            "decides": "entitlement",
            "available": True,
        },
        "care_route": None,
        "depends_on_facts": [],
        "policy": [],
        "statutory": [],
        "distinction": DISTINCTION,
        "claims": [],
        "instructions": {"detected": False, "followed": False, "signals": []},
        "withheld": [],
        "mask": _empty_mask(),
        "gateway": {"called": False, "redacted_text_copied": False, "values_stored": False},
        "copied": {
            "question_text": False,
            "policy_quotes": False,
            "secret_body": False,
            "identifier_values": False,
            "redacted_text": False,
            "described_as_anonymised": False,
        },
        "input_problem": None,
        "coerced": False,
        "applied_balance": None,
        "self_declared_role_trusted": False,
        "clearance_trusted": False,
        "sources_current": None,
        "may_be_relied_on": False,
        "point_in_time_text_verified": False,
        "verification_date": LAST_VERIFIED,
        "snapshot_conflict": False,
        "experiment_58": {"called": False},
        "experiment_03": {"called": False, "approved": False},
        "explanation_hash": None,
        "legal_advice": False,
    }


def _mentioned(text: str, phrase: str, blockers: tuple[str, ...] = ()) -> bool:
    handbook = handbook_module()
    needle = phrase.casefold()
    for sentence in handbook.sentences(text):
        folded = sentence.casefold()
        if needle not in folded:
            continue
        if handbook.phrase_is_denied(sentence, phrase):
            continue
        reduced = folded
        for blocker in blockers:
            reduced = reduced.replace(blocker.casefold(), " ")
        if needle not in reduced:
            continue
        return True
    return False


def _topics(text: str) -> list[str]:
    found: list[str] = []
    for topic, phrases, blockers in TOPIC_PHRASES:
        if any(_mentioned(text, phrase, blockers) for phrase in phrases):
            found.append(topic)
    if "parental_bereavement" in found and "bereavement" not in found:
        found.append("bereavement")
    return found


def _care(text: str) -> list[str]:
    found: list[str] = []
    for name, phrases in CARE_PHRASES:
        if any(_mentioned(text, phrase) for phrase in phrases):
            found.append(name)
    return found


def _asks_entitlement(text: str) -> bool:
    return any(_mentioned(text, phrase) for phrase in ENTITLEMENT_ASKS)


def _balance_problem(question: dict, text: str) -> str | None:
    """A bad balance is flagged. It is not replaced with zero."""

    problems: list[str] = []
    if "stated_balance" in question:
        problems.append(_one_balance(question.get("stated_balance")))
    match = _BALANCE.search(text)
    if match:
        problems.append(_one_balance(match.group(1)))
    for problem in problems:
        if problem in {"unparseable", "out_of_range"}:
            return problem
    if any(problem == "supplied_not_applied" for problem in problems):
        return "supplied_not_applied"
    return None


def _one_balance(value: object) -> str:
    if isinstance(value, bool) or isinstance(value, float):
        return "unparseable"
    if isinstance(value, int):
        if value < 0 or value > 366:
            return "out_of_range"
        return "supplied_not_applied"
    if isinstance(value, str):
        token = value.strip()
        if re.fullmatch(r"-?\d+", token):
            number = int(token)
            if number < 0 or number > 366:
                return "out_of_range"
            return "supplied_not_applied"
        return "unparseable"
    return "unparseable"


def _person(directory: object, ref: object) -> dict | None:
    if not isinstance(directory, dict) or not isinstance(ref, str):
        return None
    for person in directory.get("people") or []:
        if isinstance(person, dict) and person.get("id") == ref:
            return person
    return None


def _scope_ok(scope: object, directory: object) -> str | None:
    if not isinstance(scope, dict):
        return "scope_missing"
    if scope.get("synthetic") is not True:
        return "scope_not_synthetic"
    person = _person(directory, scope.get("approver_ref"))
    if person is None or person.get("active") is not True or person.get("role") != "HR":
        return "scope_approver_not_in_directory"
    if scope.get("approver_role") != person.get("role"):
        return "scope_role_does_not_match_directory"
    if not isinstance(scope.get("document_ids"), list) or not scope["document_ids"]:
        return "scope_has_no_documents"
    ceiling = scope.get("ceiling")
    handbook = handbook_module()
    if ceiling not in handbook.RANK:
        return "ceiling_unreadable"
    return None


def _full_text(document: dict) -> str:
    parts = [document.get("cover") or ""]
    for section in document.get("sections") or []:
        if isinstance(section, dict):
            parts.append(section.get("text") or "")
    return "\n".join(part for part in parts if isinstance(part, str))


def _prepare(document: dict, ceiling: str) -> dict:
    handbook = handbook_module()
    text = _full_text(document)
    labels = handbook.markings_in(document.get("marking"), text)
    marking = handbook.higher_marking(labels)
    return {
        "document": document,
        "text": text,
        "marking": marking,
        "labels": labels,
        "above": handbook.above_ceiling(marking, ceiling),
        "legal_hold": handbook.legal_hold(document, text),
        "retention": handbook.retention_labels(document, text),
    }


def _clean_section(text: str) -> str:
    return injection_module().without_instruction_sentences(text)


def _claims_for(topics: list[str], quoted: str, raw: str) -> list[dict]:
    handbook = handbook_module()
    rows: list[dict] = []
    seen: set[str] = set()
    for topic in topics:
        for phrase in CLAIM_PHRASES.get(topic, ()):
            if phrase in seen:
                continue
            seen.add(phrase)
            rows.append(
                {
                    "phrase": phrase,
                    "included": handbook.source_includes(quoted, phrase),
                    "denied": handbook.source_denies(raw, phrase),
                }
            )
    return rows


def _sources_current(as_of: date) -> bool:
    age = (as_of - PINNED_ON).days
    return 0 <= age <= STALE_AFTER_DAYS


def _statutory(topics: list[str], current: bool) -> list[dict]:
    ids: list[str] = []
    for topic in topics:
        for source_id in TOPIC_PINS.get(topic, []):
            if source_id not in ids:
                ids.append(source_id)
    return [pin(source_id, current=current) for source_id in ids]


def _baseline_conflicts(baseline: object, rows: list[dict]) -> list[dict]:
    if not isinstance(baseline, dict) or baseline.get("synthetic") is not True:
        return [{"id": "*", "problem": "baseline_not_synthetic"}]
    by_id = {
        row.get("id"): row
        for row in baseline.get("rows") or []
        if isinstance(row, dict)
    }
    conflicts = []
    for row in rows:
        snapshot = by_id.get(row["id"])
        if snapshot is None:
            conflicts.append({"id": row["id"], "problem": "missing_from_snapshot"})
            continue
        if snapshot.get("quote") != PINS[row["id"]]["quote"]:
            conflicts.append({"id": row["id"], "problem": "snapshot_disagrees"})
    return conflicts


def _handbook(as_of: str) -> dict:
    if as_of in _handbook_cache:
        return _handbook_cache[as_of]
    folder = EXPERIMENTS / "58-employee-handbook"
    try:
        handbook = json.loads((folder / "fixtures" / "handbook.json").read_text(encoding="utf-8"))
        scope = json.loads((folder / "examples" / "sample_scope.json").read_text(encoding="utf-8"))
        answer = answer_module().answer_handbook(
            {"synthetic": True, "question": HANDBOOK_QUESTION},
            handbook,
            scope,
            as_of,
        )
    except (OSError, json.JSONDecodeError, NeighbourMissing, KeyError, TypeError, ValueError) as exc:
        record = {"called": False, "reason": type(exc).__name__, "answer_copied": False}
        _handbook_cache[as_of] = record
        return record
    record = {
        "called": True,
        "experiment_id": "exp-58-employee-handbook",
        "question_fixed": True,
        "outcome": answer.get("outcome"),
        "entitlement_decision": answer.get("entitlement_decision"),
        "answer_copied": False,
        "note": (
            "A fixed question was asked of the synthetic handbook. "
            "The handbook answer is not copied into this explanation. "
            "It is not an entitlement decision."
        ),
    }
    _handbook_cache[as_of] = record
    return record


def _manifest() -> dict:
    global _manifest_cache
    if _manifest_cache is not None:
        return _manifest_cache
    path = ROOT / "agent-manifest.yaml"
    try:
        module = manifest_module()
    except NeighbourMissing as exc:
        _manifest_cache = {"called": False, "reason": str(exc), "approved": False}
        return _manifest_cache
    refused = False
    try:
        module.generate_manifest({}, LAST_VERIFIED, approve=True)
    except Exception as exc:
        refused = "cannot mark a manifest approved" in str(exc)
    errors: list[str] = []
    try:
        import yaml

        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
        errors = module._validate(loaded)
    except (OSError, Exception) as exc:  # noqa: BLE001
        errors = [type(exc).__name__]
    record = {
        "called": True,
        "experiment_id": "exp-03-agent-inventory-atrs-assurance",
        "manifest_validation_passed": not errors,
        "error_count": len(errors),
        "approved": False,
        "approve_attempt_refused": refused,
        "generator_cannot_approve": True,
    }
    _manifest_cache = record
    return record


def _mask(text: str) -> dict:
    try:
        return mask_module().mask_counts(text)
    except NeighbourMissing:
        return _empty_mask()


def _gateway(text: str) -> dict:
    try:
        proposal = gateway_module().propose(text, caller=CALLER, apply_model_suggestions=False)
    except (NeighbourMissing, TypeError, ValueError):
        return {"called": False, "redacted_text_copied": False, "values_stored": False}
    audit = proposal.get("audit_log") or {}
    types: list[str] = []
    for finding in audit.get("findings") or []:
        entity = finding.get("entity_type")
        if isinstance(entity, str) and entity not in types:
            types.append(entity)
    return {
        "called": True,
        "experiment_id": "exp-08-uk-pii-redaction-gateway",
        "finding_count": len(audit.get("findings") or []),
        "entity_types": types,
        "raw_values_logged": audit.get("raw_values_logged"),
        "redacted_text_copied": False,
        "output_is_anonymised": False,
        "values_stored": False,
    }


def _scan(*texts: str) -> dict:
    module = injection_module()
    signals: list[str] = []
    detected = False
    for text in texts:
        row = module.scan_text(text)
        if row.get("detected"):
            detected = True
        for name in row.get("signals") or []:
            if name not in signals:
                signals.append(name)
    return {"detected": detected, "followed": False, "signals": signals}


def _hash(result: dict) -> str:
    payload = {
        "about_date": result.get("about_date"),
        "outcome": result.get("outcome"),
        "policy_ids": [row.get("section_id") for row in result.get("policy") or []],
        "quotes": [row.get("quote") for row in result.get("policy") or []],
        "statutory_ids": [row.get("id") for row in result.get("statutory") or []],
    }
    encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _finish(result: dict, outcome: str, answer: str, *, rely: bool) -> dict:
    result["outcome"] = outcome
    result["answer"] = answer
    result["entitlement_decision"] = None
    result["pay_decision"] = None
    result["pay_rate"] = None
    result["leave_booked"] = False
    result["leave_recorded"] = False
    result["approved"] = False
    result["may_be_relied_on"] = bool(rely) and outcome == "explained"
    result["explanation_hash"] = _hash(result)
    result["experiment_03"] = _manifest()
    if isinstance(result.get("as_of"), str):
        result["experiment_58"] = _handbook(result["as_of"])
    return result


def _question_text(question: object) -> tuple[str, list[str], dict]:
    if not isinstance(question, dict):
        return "", [], {}
    stripped = [key for key in PROHIBITED_KEYS if key in question]
    text = question.get("text") if isinstance(question.get("text"), str) else ""
    if not text and isinstance(question.get("question"), str):
        text = question["question"]
    return text, stripped, question


def explain(
    question: object,
    policies: object,
    scope: object,
    baseline: object,
    directory: object,
    as_of: str,
    about_date: str | None = None,
) -> dict:
    result = _base(as_of if isinstance(as_of, str) else None)
    handbook = handbook_module()
    as_of_day = handbook.parse_day(as_of)
    if as_of_day is None:
        result["input_problem"] = "as_of_unparseable"
        result["coerced"] = False
        return _finish(
            result,
            "needs_human",
            "The as-of date cannot be read. It has not been replaced with today. HR or the line manager has to look at it.",
            rely=False,
        )
    result["sources_current"] = _sources_current(as_of_day)
    text, stripped, question_dict = _question_text(question)
    result["stripped_keys"] = stripped
    result["mask"] = _mask(text)
    result["gateway"] = _gateway(text)
    result["self_declared_role_trusted"] = False
    result["clearance_trusted"] = False
    if _SELF_ROLE.search(text):
        result["self_declared_role_present"] = True
    if _CLEARANCE.search(text):
        result["clearance_claim_present"] = True

    policy_texts = []
    documents = []
    if isinstance(policies, dict):
        documents = [row for row in policies.get("documents") or [] if isinstance(row, dict)]
        policy_texts = [_full_text(row) for row in documents]
    result["instructions"] = _scan(text, *policy_texts)

    if not isinstance(policies, dict) or policies.get("synthetic") is not True:
        return _finish(
            result,
            "refused",
            "The policy set is not marked synthetic. Nothing was copied.",
            rely=False,
        )

    scope_problem = _scope_ok(scope, directory)
    if scope_problem:
        result["input_problem"] = scope_problem
        return _finish(
            result,
            "needs_human",
            "The scope is not an HR approval on the directory. No policy was quoted. HR or the line manager decides entitlement.",
            rely=False,
        )

    care = _care(text)
    if care:
        result["care_route"] = {
            "to": "HR or the line manager",
            "signals": care,
            "with_care": True,
            "processed_as_routine": False,
        }
        return _finish(result, "routed_to_human", CARE_ANSWER, rely=False)

    raw_about = about_date
    if raw_about is None and isinstance(question_dict, dict):
        raw_about = question_dict.get("about_date")
    if raw_about in (None, ""):
        about = as_of_day
        result["about_date"] = about.isoformat()
        result["about_date_source"] = "as_of"
    else:
        about = handbook.parse_day(raw_about)
        if about is None:
            result["input_problem"] = "about_date_unparseable"
            result["coerced"] = False
            return _finish(
                result,
                "needs_human",
                "The date the question is about cannot be read. It has not been replaced with the as-of date or with today.",
                rely=False,
            )
        result["about_date"] = about.isoformat()
        result["about_date_source"] = "question"
    result["point_in_time_text_verified"] = about == PINNED_ON

    balance = _balance_problem(question_dict if isinstance(question_dict, dict) else {}, text)
    entitlement = _asks_entitlement(text)
    if entitlement:
        result["depends_on_facts"] = list(FACTS)
    if balance in {"unparseable", "out_of_range"}:
        result["input_problem"] = f"balance_{balance}"
        result["coerced"] = False
        result["applied_balance"] = None
        result["depends_on_facts"] = list(FACTS)
        return _finish(
            result,
            "needs_human",
            "A balance was supplied that cannot be used. It has not been replaced with zero. HR or the line manager has to look at it. No pay was calculated.",
            rely=False,
        )
    if balance == "supplied_not_applied":
        result["input_problem"] = "balance_supplied_not_applied"
        result["applied_balance"] = None
        result["depends_on_facts"] = list(dict.fromkeys([*result["depends_on_facts"], "The stated balance was not applied"]))

    topics = _topics(text)
    if not topics:
        return _finish(
            result,
            "not_covered",
            "The approved leave policies do not cover this question. "
            + HUMAN,
            rely=False,
        )

    ceiling = scope["ceiling"]
    allowed = set(scope["document_ids"])
    current = bool(result["sources_current"])
    statutory = _statutory(topics, current)
    conflicts = _baseline_conflicts(baseline, statutory)
    conflict_ids = {row["id"] for row in conflicts}
    if conflicts:
        result["snapshot_conflict"] = True
        for row in statutory:
            if row["id"] in conflict_ids:
                row["quote"] = None
                row["also"] = []
                row["snapshot_conflict"] = True
                row["note"] = (
                    "The curated snapshot does not match the pin. "
                    "No figure from either side is stated."
                )
    result["statutory"] = statutory

    quoted_rows: list[dict] = []
    withheld: list[dict] = []
    raw_parts: list[str] = []
    quoted_parts: list[str] = []
    for document in documents:
        if document.get("id") not in allowed:
            continue
        if document.get("status") == "draft":
            continue
        section_topics = []
        for section in document.get("sections") or []:
            if isinstance(section, dict):
                section_topics.extend(section.get("topics") or [])
        matched = document.get("topic") in topics or bool(set(section_topics) & set(topics))
        if not matched:
            continue
        prepared = _prepare(document, ceiling)
        if prepared["above"]:
            withheld.append(
                {
                    "document_id": document.get("id"),
                    "marking": prepared["marking"],
                    "labels": prepared["labels"],
                    "legal_hold": prepared["legal_hold"],
                    "retention": prepared["retention"],
                    "body_copied": False,
                    "reason": "above_ceiling",
                }
            )
            continue
        in_force = handbook.in_force_on(document, about)
        if in_force is None:
            result["input_problem"] = "policy_date_unparseable"
            result["coerced"] = False
            return _finish(
                result,
                "needs_human",
                "A policy date cannot be read. No version was chosen and no date was replaced with today.",
                rely=False,
            )
        if not in_force:
            continue
        end = handbook.parse_day(document.get("effective_to")) if document.get("effective_to") else None
        review = handbook.parse_day(document.get("review_by"))
        if document.get("review_by") not in (None, "") and review is None:
            result["input_problem"] = "review_date_unparseable"
            result["coerced"] = False
            return _finish(
                result,
                "needs_human",
                "A review date cannot be read. It has not been ignored and it has not been replaced.",
                rely=False,
            )
        superseded = bool(end is not None and as_of_day > end) or document.get("status") == "superseded" and end is not None and as_of_day > end
        review_overdue = bool(review is not None and review < about)
        sections_out = []
        for section in document.get("sections") or []:
            if not isinstance(section, dict):
                continue
            topics_here = section.get("topics") or []
            if document.get("topic") not in topics and not (set(topics_here) & set(topics)):
                continue
            raw = section.get("text") if isinstance(section.get("text"), str) else ""
            clean = _clean_section(raw)
            if not clean:
                continue
            sections_out.append({"section_id": section.get("id"), "quote": clean})
            raw_parts.append(raw)
            quoted_parts.append(clean)
        if not sections_out:
            continue
        quoted_rows.append(
            {
                "document_id": document.get("id"),
                "title": document.get("title"),
                "version": document.get("version"),
                "section_id": sections_out[0]["section_id"],
                "section_ids": [row["section_id"] for row in sections_out],
                "effective_from": document.get("effective_from"),
                "effective_to": document.get("effective_to"),
                "review_by": document.get("review_by"),
                "status": document.get("status"),
                "superseded_on_as_of": superseded,
                "later_version_id": document.get("superseded_by"),
                "review_overdue": review_overdue,
                "marking": prepared["marking"],
                "legal_hold": prepared["legal_hold"],
                "retention": prepared["retention"],
                "quote": " ".join(row["quote"] for row in sections_out),
                "body_copied": True,
            }
        )

    result["withheld"] = withheld
    result["policy"] = quoted_rows
    result["copied"]["policy_quotes"] = bool(quoted_rows)
    result["copied"]["secret_body"] = False
    quoted = "\n".join(quoted_parts)
    raw = "\n".join(raw_parts)
    result["claims"] = _claims_for(topics, quoted, raw)

    if not quoted_rows and withheld:
        return _finish(
            result,
            "needs_human",
            "A matching page is above the ceiling. The body was not copied. "
            "The marking, the legal hold, and the retention labels are kept. "
            + HUMAN,
            rely=False,
        )
    if not quoted_rows:
        return _finish(
            result,
            "not_covered",
            "No approved policy version is in force on the date the question is about. "
            + HUMAN,
            rely=False,
        )

    lines = []
    if entitlement or balance == "supplied_not_applied":
        lines.append(
            "This question depends on facts this explanation does not have, or it asks for a decision. "
            "The scheme is quoted and is not applied to a person."
        )
    for row in quoted_rows:
        version_note = ""
        if row["superseded_on_as_of"]:
            later = row.get("later_version_id") or "a later version"
            version_note = (
                f" This version had ended by the as-of date. It is superseded. "
                f"The later version on the scope is {later}."
            )
        if row["review_overdue"]:
            version_note += (
                f" The review date {row['review_by']} is before the date the question is about. "
                "The version is past review."
            )
        lines.append(
            f"Policy {row['document_id']} section {row['section_id']}, version {row['version']}, "
            f"effective {row['effective_from']}. {row['quote']}{version_note}"
        )
    lines.append(DISTINCTION)
    if any(row["denied"] and not row["included"] for row in result["claims"]):
        lines.append("A denial in the policy is not an inclusion.")
    for row in statutory:
        if row.get("snapshot_conflict"):
            lines.append(
                f"{row['citation']} is not stated, because the snapshot and the pin disagree."
            )
            continue
        if row.get("verified") is not True or row.get("quote") is None:
            lines.append(
                f"{row['citation']} is not verified. No figure and no pay rate are stated. {row['note']}"
            )
            continue
        lines.append(
            f"{row['citation']}, verified {row['verification_date']}: {row['quote']}"
        )
        if row.get("in_force") == "partial":
            lines.append(row["note"])
    if about != PINNED_ON:
        lines.append(
            "The statutory text is the text opened on 18 November 2026. "
            "It is not a point-in-time copy of the law on the date the question is about."
        )
    lines.append(HUMAN)
    if not result["sources_current"]:
        lines.append(
            "The statutory pins are outside the 90-day window. They have not been refreshed from the web."
        )

    unverified = any(row.get("verified") is not True or row.get("quote") is None for row in statutory)
    overdue = any(row["review_overdue"] for row in quoted_rows)
    superseded = any(row["superseded_on_as_of"] for row in quoted_rows)
    rely = (
        not entitlement
        and balance is None
        and not conflicts
        and not unverified
        and not overdue
        and not superseded
        and bool(result["sources_current"])
    )
    outcome = "needs_human" if entitlement or conflicts else "explained"
    return _finish(result, outcome, " ".join(lines), rely=rely)


def record_seen(result: dict, review: object, directory: object) -> dict:
    """Record that HR has seen this exact explanation. It does not approve leave.

    The review has to come from the deterministic approval step. Words in the
    question are not this object. The approver has to be an active HR id on
    the directory, and the hash has to be the hash of this explanation.
    """

    updated = dict(result)
    updated["human_approval"] = None
    updated["approved"] = False
    updated["entitlement_decision"] = None
    updated["leave_booked"] = False
    updated["leave_recorded"] = False
    updated["pay_decision"] = None
    if not isinstance(review, dict):
        updated["blocked_reason"] = "review_missing"
        return updated
    if review.get("source") != "deterministic_approval_step":
        updated["blocked_reason"] = "review_not_from_approval_step"
        return updated
    if review.get("item") != "leave-explanation" or review.get("decision") != "seen":
        updated["blocked_reason"] = "review_is_not_a_seen_step"
        return updated
    if review.get("explanation_hash") != result.get("explanation_hash"):
        updated["blocked_reason"] = "explanation_hash_mismatch"
        return updated
    person = _person(directory, review.get("approver_ref"))
    if person is None or person.get("active") is not True or person.get("role") != "HR":
        updated["blocked_reason"] = "approver_not_in_directory"
        return updated
    if review.get("role") != "HR":
        updated["blocked_reason"] = "role_does_not_match_directory"
        return updated
    updated["human_approval"] = {
        "seen": True,
        "approver_ref": person["id"],
        "role": "HR",
        "item": "leave-explanation",
        "explanation_hash": result.get("explanation_hash"),
        "decides_entitlement": False,
        "books_leave": False,
        "records_leave": False,
        "calculates_pay": False,
    }
    updated["blocked_reason"] = None
    return updated


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Explain a synthetic leave policy.")
    parser.add_argument("--policies", required=True)
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--scope", required=True)
    parser.add_argument("--directory", required=True)
    parser.add_argument("--question", required=True)
    parser.add_argument("--as-of", required=True)
    args = parser.parse_args(argv)
    result = explain(
        json.loads(Path(args.question).read_text(encoding="utf-8")),
        json.loads(Path(args.policies).read_text(encoding="utf-8")),
        json.loads(Path(args.scope).read_text(encoding="utf-8")),
        json.loads(Path(args.baseline).read_text(encoding="utf-8")),
        json.loads(Path(args.directory).read_text(encoding="utf-8")),
        args.as_of,
    )
    json.dump(result, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    if result["outcome"] == "refused":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
