#!/usr/bin/env python3
"""Review one employer pack against the pinned Employment Rights Act dates.

The function does not decide compliance, harassment, discipline, or
dismissal. It does not publish a policy, write a record, or send a message.
hr_decision, compliance_conclusion, and disciplinary_decision are null.

No network. No model.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from datetime import date, datetime
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from injection import (
        PROHIBITED_PAYLOAD_KEYS,
        question_refusal_reasons,
        signals_in_text,
    )
    from sources import (
        ACAS_PROMPTS,
        ACAS_UPDATED,
        ACAS_URL,
        ALL_REASONABLE_STEPS_IN_FORCE,
        DEFAULT_POLICY_STALE_AFTER_DAYS,
        DEFAULT_STALE_AFTER_DAYS,
        LAST_VERIFIED,
        NDA_INSTRUMENT_OPENED,
        NDA_TIMETABLE,
        REASONABLE_STEPS_IN_FORCE,
        SCOTLAND_CONTRACT_INSTRUMENT_OPENED,
        SCOTLAND_CONTRACT_TIMELINE_DATE,
        SOURCES,
        SPECIFIED_STEPS_REGULATIONS_MADE,
        SPECIFY_STEPS_POWER_IN_FORCE,
        THIRD_PARTY_IN_FORCE,
        TRIBUNAL_LIMITS_IN_FORCE,
        UNFAIR_DISMISSAL_IN_FORCE,
        WHISTLEBLOWING_IN_FORCE,
    )
else:
    from .injection import (
        PROHIBITED_PAYLOAD_KEYS,
        question_refusal_reasons,
        signals_in_text,
    )
    from .sources import (
        ACAS_PROMPTS,
        ACAS_UPDATED,
        ACAS_URL,
        ALL_REASONABLE_STEPS_IN_FORCE,
        DEFAULT_POLICY_STALE_AFTER_DAYS,
        DEFAULT_STALE_AFTER_DAYS,
        LAST_VERIFIED,
        NDA_INSTRUMENT_OPENED,
        NDA_TIMETABLE,
        REASONABLE_STEPS_IN_FORCE,
        SCOTLAND_CONTRACT_INSTRUMENT_OPENED,
        SCOTLAND_CONTRACT_TIMELINE_DATE,
        SOURCES,
        SPECIFIED_STEPS_REGULATIONS_MADE,
        SPECIFY_STEPS_POWER_IN_FORCE,
        THIRD_PARTY_IN_FORCE,
        TRIBUNAL_LIMITS_IN_FORCE,
        UNFAIR_DISMISSAL_IN_FORCE,
        WHISTLEBLOWING_IN_FORCE,
    )

LABEL = "DRAFT FOR HR REVIEW"
REFUSED = "REFUSED"

GREAT_BRITAIN = {"england", "wales", "england_and_wales", "scotland"}
NORTHERN_IRELAND = {"northern_ireland"}
JURISDICTIONS = GREAT_BRITAIN | NORTHERN_IRELAND

EVIDENCE_STATUSES = {"evidenced", "not_evidenced", "not_supplied"}
EVIDENCE_KEYS = {item["id"] for item in ACAS_PROMPTS} | {
    "third_party_risk_recorded",
    "whistleblowing_policy_mentions_sexual_harassment",
    "probation_wording_reviewed_for_six_month_period",
    "risk_assessment_recorded",
}
EVIDENCE_DATE_KEYS = {"policy_review_date"}

POLICY_HEADINGS = (
    "Purpose",
    "Who is covered",
    "How to report",
    "Training",
    "Third parties",
    "Whistleblowing",
    "Review",
)

SEXUAL_LANGUAGE = ("sexual", "harassment", "appearance", "banter")
THIRD_PARTY_LANGUAGE = ("visitor", "customer", "client", "contractor", "member of the public")


class ReviewError(ValueError):
    """The pack cannot be read. Nothing was decided."""


def _parse_date(value: str, field: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError) as exc:
        raise ReviewError(f"{field} must be YYYY-MM-DD") from exc


def _iso(value: date) -> str:
    return value.isoformat()


def _on_or_after(as_of: date, start: date) -> bool:
    return as_of >= start


def _strip_prohibited(value, path: str, found: list[str]):
    """Return a copy with prohibited keys removed. Lists and dicts are copied."""
    if isinstance(value, dict):
        kept = {}
        for key, item in value.items():
            here = f"{path}.{key}" if path else key
            if key in PROHIBITED_PAYLOAD_KEYS:
                found.append(here)
                continue
            kept[key] = _strip_prohibited(item, here, found)
        return kept
    if isinstance(value, list):
        return [_strip_prohibited(item, f"{path}[{index}]", found) for index, item in enumerate(value)]
    return value


def _scan(value, path: str, hits: list[dict]) -> None:
    if isinstance(value, str):
        signals = signals_in_text(value)
        if signals:
            hits.append({"field": path or "pack", "signals": signals})
        return
    if isinstance(value, dict):
        for key, item in value.items():
            _scan(item, f"{path}.{key}" if path else key, hits)
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _scan(item, f"{path}[{index}]", hits)


def _refusal(reason: str) -> dict:
    return {
        "label": REFUSED,
        "reason": reason,
        "narrative_echoed": False,
        "hr_decision": None,
        "compliance_conclusion": None,
        "disciplinary_decision": None,
        "policy_published": False,
        "records_changed": False,
        "message_sent": False,
        "actions_taken": [],
        "model_called": False,
        "network_called": False,
        "legal_advice": False,
    }


def _source_rows(as_of: date, stale_after_days: int) -> list[dict]:
    rows = []
    for source in SOURCES:
        verified = _parse_date(source["last_verified"], f"sources.{source['id']}.last_verified")
        age = (as_of - verified).days
        stale = age > stale_after_days
        rows.append(
            {
                "id": source["id"],
                "title": source["title"],
                "url": source["url"],
                "page_as_at": source["page_as_at"],
                "last_verified": source["last_verified"],
                "body_opened": source["body_opened"],
                "notes": source["notes"],
                "age_days": age,
                "stale": stale,
                "relied_on": not stale,
            }
        )
    return rows


def _evidence_status(evidence: dict, key: str) -> str:
    if key not in evidence or evidence[key] in (None, ""):
        return "not_supplied"
    value = evidence[key]
    if value not in EVIDENCE_STATUSES:
        raise ReviewError(
            f"evidence.{key} must be evidenced, not_evidenced, or not_supplied"
        )
    return value


def _prompt_row(prompt_id: str, text: str, status: str, *, source: str) -> dict:
    return {
        "id": prompt_id,
        "source": source,
        "source_url": ACAS_URL if source == "acas" else None,
        "source_updated": ACAS_UPDATED if source == "acas" else None,
        "prompt": text,
        "not_a_statutory_step": True,
        "absence_is_not_a_breach": True,
        "legal_breach": False,
        "status": status,
        "evidence_gap": status in {"not_evidenced", "not_supplied"},
    }


def _duty_prompts(evidence: dict, applied: bool, prevent_in_force: bool, third_in_force: bool, whistle_in_force: bool, dismissal_in_force: bool) -> list[dict]:
    rows = []
    for item in ACAS_PROMPTS:
        status = _evidence_status(evidence, item["id"])
        if not applied or not prevent_in_force:
            status = "not_yet_in_force"
        row = _prompt_row(item["id"], item["prompt"], status, source="acas")
        if status == "not_yet_in_force":
            row["evidence_gap"] = False
            row["employer_status"] = _evidence_status(evidence, item["id"])
        rows.append(row)

    third_status = _evidence_status(evidence, "third_party_risk_recorded")
    third = _prompt_row(
        "third_party_risk_recorded",
        "The pack records whether third-party harassment was considered. Section 21 is a date. This row is not a finding that anyone was harassed.",
        third_status if applied and third_in_force else "not_yet_in_force",
        source="employer_record",
    )
    if third["status"] == "not_yet_in_force":
        third["evidence_gap"] = False
        third["employer_status"] = third_status
    rows.append(third)

    whistle_status = _evidence_status(evidence, "whistleblowing_policy_mentions_sexual_harassment")
    whistle = _prompt_row(
        "whistleblowing_policy_mentions_sexual_harassment",
        "The pack records whether the whistleblowing policy mentions sexual harassment. This row does not decide that a disclosure was protected.",
        whistle_status if applied and whistle_in_force else "not_yet_in_force",
        source="employer_record",
    )
    if whistle["status"] == "not_yet_in_force":
        whistle["evidence_gap"] = False
        whistle["employer_status"] = whistle_status
    whistle["protected_disclosure_decided"] = False
    rows.append(whistle)

    probation_status = _evidence_status(evidence, "probation_wording_reviewed_for_six_month_period")
    probation = _prompt_row(
        "probation_wording_reviewed_for_six_month_period",
        "The pack records whether probation wording was reviewed against the six-month qualifying period. This row does not apply that period to a person.",
        probation_status if applied and dismissal_in_force else "not_yet_in_force",
        source="employer_record",
    )
    if probation["status"] == "not_yet_in_force":
        probation["evidence_gap"] = False
        probation["employer_status"] = probation_status
    probation["applied_to_a_person"] = False
    rows.append(probation)
    return rows


def _policy_currency(evidence: dict, as_of: date, policy_stale_after_days: int) -> dict:
    raw = evidence.get("policy_review_date")
    if raw in (None, ""):
        return {
            "policy_review_date": None,
            "policy_review_date_missing": True,
            "policy_review_date_in_future": False,
            "policy_evidence_stale": False,
            "policy_age_days": None,
            "policy_relied_on": False,
        }
    reviewed = _parse_date(raw, "evidence.policy_review_date")
    age = (as_of - reviewed).days
    in_future = age < 0
    stale = age > policy_stale_after_days
    return {
        "policy_review_date": _iso(reviewed),
        "policy_review_date_missing": False,
        "policy_review_date_in_future": in_future,
        "policy_evidence_stale": stale,
        "policy_age_days": age,
        "policy_relied_on": not stale and not in_future,
    }


def _duties(as_of: date, jurisdiction: str, applied: bool, relied: bool) -> list[dict]:
    reasonable = applied and _on_or_after(as_of, REASONABLE_STEPS_IN_FORCE)
    all_steps = applied and _on_or_after(as_of, ALL_REASONABLE_STEPS_IN_FORCE)
    third = applied and _on_or_after(as_of, THIRD_PARTY_IN_FORCE)
    power = applied and _on_or_after(as_of, SPECIFY_STEPS_POWER_IN_FORCE)
    whistle = applied and _on_or_after(as_of, WHISTLEBLOWING_IN_FORCE)
    tribunal = applied and _on_or_after(as_of, TRIBUNAL_LIMITS_IN_FORCE)
    dismissal = applied and _on_or_after(as_of, UNFAIR_DISMISSAL_IN_FORCE)

    if not applied:
        wording = None
    elif all_steps:
        wording = "all reasonable steps"
    elif reasonable:
        wording = "reasonable steps"
    else:
        wording = None

    prevent = {
        "id": "prevent_sexual_harassment",
        "applied": applied,
        "in_force": reasonable,
        "wording": wording,
        "reasonable_steps_in_force_from": _iso(REASONABLE_STEPS_IN_FORCE),
        "all_reasonable_steps_in_force_from": _iso(ALL_REASONABLE_STEPS_IN_FORCE),
        "all_reasonable_steps_in_force": all_steps,
        "provision": (
            "Equality Act 2010 section 40A(1). From 30 October 2026, "
            "Employment Rights Act 2025 section 20 inserts 'all'."
        ),
        "urls": [
            "https://www.legislation.gov.uk/ukpga/2010/15/section/40A",
            "https://www.legislation.gov.uk/ukpga/2025/36/section/20",
            "https://www.legislation.gov.uk/uksi/2026/1065/regulation/3/made",
        ],
        "compliance_conclusion": None,
        "relied_on": relied and reasonable,
        "note": (
            "In force is a date comparison. It is not a finding that this "
            "employer took, or failed to take, the steps."
        ),
    }
    third_row = {
        "id": "third_party_harassment",
        "applied": applied,
        "in_force": third,
        "in_force_from": _iso(THIRD_PARTY_IN_FORCE),
        "provision": "Employment Rights Act 2025 section 21, inserting Equality Act 2010 section 40(1A) to (1C)",
        "url": "https://www.legislation.gov.uk/ukpga/2025/36/section/21",
        "both_limbs_required": True,
        "limbs_decided": False,
        "compliance_conclusion": None,
        "relied_on": relied and third,
        "note": (
            "The inserted subsection (1B) requires both harassment in the "
            "course of employment and a failure to take all reasonable steps. "
            "This core decides neither limb."
        ),
    }
    power_row = {
        "id": "power_to_specify_reasonable_steps",
        "applied": applied,
        "in_force": power,
        "in_force_from": _iso(SPECIFY_STEPS_POWER_IN_FORCE),
        "provision": "Employment Rights Act 2025 section 22, inserting Equality Act 2010 section 40B",
        "url": "https://www.legislation.gov.uk/ukpga/2025/36/section/22",
        "specified_steps_regulations_made": SPECIFIED_STEPS_REGULATIONS_MADE,
        "regulations_applied": False,
        "compliance_conclusion": None,
        "relied_on": relied and power,
        "note": (
            "The power coming into force is not a list of steps. "
            "No specifying regulations were opened on 27 October 2026."
        ),
    }
    whistle_row = {
        "id": "whistleblowing_sexual_harassment",
        "applied": applied,
        "in_force": whistle,
        "in_force_from": _iso(WHISTLEBLOWING_IN_FORCE),
        "provision": "Employment Rights Act 2025 section 23, amending Employment Rights Act 1996 section 43B",
        "url": "https://www.legislation.gov.uk/ukpga/2025/36/section/23",
        "commencement_instrument_page_opened": False,
        "commencement_source": "Commencement line on the section 23 page: SI 2026/323 regulation 3",
        "protected_disclosure_decided": False,
        "compliance_conclusion": None,
        "relied_on": relied and whistle,
    }
    tribunal_row = {
        "id": "tribunal_time_limits",
        "applied": applied,
        "in_force": tribunal,
        "in_force_from": _iso(TRIBUNAL_LIMITS_IN_FORCE),
        "provision": (
            "Employment Rights Act 2025 section 152 and Schedule 12, "
            "by SI 2026/954 regulation 3, subject to regulation 4"
        ),
        "url": "https://www.legislation.gov.uk/ukpga/2025/36/section/152",
        "deadline_calculated": False,
        "relevant_date_identified": False,
        "compensation_figure_stated": False,
        "scotland_contract_claims": {
            "stated_on_govuk_timeline": SCOTLAND_CONTRACT_TIMELINE_DATE,
            "timeline_updated": "2026-10-22",
            "instrument_opened": SCOTLAND_CONTRACT_INSTRUMENT_OPENED,
            "applies_to_this_pack": jurisdiction == "scotland",
            "applied": False,
        },
        "compliance_conclusion": None,
        "relied_on": relied and tribunal,
        "note": "The core does not count three months or six months, and it does not identify the relevant date.",
    }
    if not applied:
        dismissal_note = "Not applied. This starter does not state Northern Ireland law."
    elif dismissal:
        dismissal_note = (
            "Section 25 is in force on this date, subject to SI 2026/559 regulation 4, "
            "which this core does not apply to a person. No compensation figure is stated."
        )
    else:
        dismissal_note = (
            "Section 25 says it substitutes 'six months' for 'two years' in section 108 "
            "of the Employment Rights Act 1996. On this date that substitution is not in force. "
            "It is not applied to a person."
        )
    dismissal_row = {
        "id": "unfair_dismissal_qualifying_period",
        "applied": applied,
        "in_force": dismissal,
        "in_force_from": _iso(UNFAIR_DISMISSAL_IN_FORCE),
        "provision": "Employment Rights Act 2025 section 25, by SI 2026/559 regulation 3, subject to regulation 4",
        "url": "https://www.legislation.gov.uk/ukpga/2025/36/section/25",
        "qualifying_period_words": ("six months" if dismissal else "two years") if applied else None,
        "section_124_omitted": dismissal,
        "applied_to_a_person": False,
        "effective_date_of_termination_decided": False,
        "transitional_provision_applied": False,
        "compensation_figure_stated": False,
        "compliance_conclusion": None,
        "relied_on": relied and dismissal,
        "note": dismissal_note,
    }
    nda_row = {
        "id": "nda_misuse_regulations",
        "applied": False,
        "in_force": False,
        "timetable_only": NDA_TIMETABLE,
        "source": "GOV.UK timeline updated 22 October 2026",
        "url": (
            "https://www.gov.uk/government/publications/"
            "implementing-the-plan-to-make-work-pay-and-employment-rights-act/"
            "plan-to-make-work-pay-and-employment-rights-act-timeline-update"
        ),
        "instrument_opened": NDA_INSTRUMENT_OPENED,
        "scored": False,
        "compliance_conclusion": None,
        "relied_on": False,
        "note": "A timetable sentence. The regulations were not opened and are not scored.",
    }
    return [prevent, third_row, power_row, whistle_row, tribunal_row, dismissal_row, nda_row]


def _excerpt_relied(excerpt: dict, as_of: date, policy_stale_after_days: int) -> tuple[bool, bool]:
    raw = excerpt.get("review_date")
    if raw in (None, ""):
        return False, False
    reviewed = _parse_date(raw, f"policy_excerpts.{excerpt.get('id', 'excerpt')}.review_date")
    age = (as_of - reviewed).days
    stale = age > policy_stale_after_days or age < 0
    return (not stale), stale


def _answer(question, excerpts, as_of: date, policy_stale_after_days: int) -> dict | None:
    if question is None:
        return None
    if isinstance(question, str):
        text = question
        topic = None
    elif isinstance(question, dict):
        text = question.get("text") or ""
        topic = question.get("topic")
    else:
        raise ReviewError("question must be a string or an object")
    if not isinstance(text, str):
        raise ReviewError("question.text must be a string")

    reasons = question_refusal_reasons(text)
    base = {
        "refused": False,
        "refusal_reasons": reasons,
        "answer_status": None,
        "quotations": [],
        "legal_advice": False,
        "sent": False,
    }
    if reasons:
        base["refused"] = True
        base["answer_status"] = "refused_not_legal_advice"
        return base
    if not isinstance(topic, str) or not topic.strip():
        base["answer_status"] = "topic_not_supplied"
        return base

    topic_key = topic.strip().casefold()
    matches = []
    if excerpts is None:
        excerpts = []
    if not isinstance(excerpts, list):
        raise ReviewError("policy_excerpts must be a list")
    for excerpt in excerpts:
        if not isinstance(excerpt, dict):
            raise ReviewError("each policy excerpt must be an object")
        excerpt_topic = excerpt.get("topic")
        if not isinstance(excerpt_topic, str) or excerpt_topic.strip().casefold() != topic_key:
            continue
        if excerpt.get("approved_by_policy_owner") is not True:
            matches.append(
                {
                    "excerpt_id": excerpt.get("id"),
                    "quoted": False,
                    "reason": "excerpt_not_approved",
                    "relied_on": False,
                }
            )
            continue
        text_body = excerpt.get("text")
        if not isinstance(text_body, str) or not text_body.strip():
            raise ReviewError("an approved excerpt needs text")
        if signals_in_text(text_body):
            matches.append(
                {
                    "excerpt_id": excerpt.get("id"),
                    "quoted": False,
                    "reason": "excerpt_quarantined",
                    "relied_on": False,
                }
            )
            continue
        relied, stale = _excerpt_relied(excerpt, as_of, policy_stale_after_days)
        matches.append(
            {
                "excerpt_id": excerpt.get("id"),
                "title": excerpt.get("title"),
                "quoted": True,
                "text": text_body,
                "review_date": excerpt.get("review_date"),
                "stale": stale,
                "relied_on": relied,
                "reason": None if relied else "excerpt_not_current",
            }
        )
    quoted = [item for item in matches if item["quoted"]]
    if not matches:
        base["answer_status"] = "not_in_the_approved_pack"
        return base
    if not quoted:
        quarantined = all(item["reason"] == "excerpt_quarantined" for item in matches)
        base["answer_status"] = "excerpt_quarantined" if quarantined else "excerpt_not_approved"
        base["quotations"] = matches
        return base
    base["answer_status"] = "quoted"
    base["quotations"] = matches
    return base


def _incident(incident: dict | None) -> dict | None:
    if incident is None:
        return None
    if not isinstance(incident, dict):
        raise ReviewError("incident must be an object")
    if incident.get("anonymised") is not True:
        return {
            "status": "refused",
            "reason": "report_not_marked_anonymised",
            "narrative_echoed": False,
            "route": None,
            "closed": False,
            "disciplinary_decision": None,
            "message_sent": False,
            "finding": None,
        }
    reference = incident.get("reference")
    if not isinstance(reference, str) or not reference.strip():
        raise ReviewError("an anonymised incident needs a reference")
    narrative = incident.get("narrative")
    if not isinstance(narrative, str):
        raise ReviewError("incident.narrative must be a string")
    lowered = narrative.casefold()
    sexual = any(word in lowered for word in SEXUAL_LANGUAGE)
    third = any(word in lowered for word in THIRD_PARTY_LANGUAGE)
    return {
        "status": "draft",
        "reference": reference,
        "route": "hr_review",
        "closed": False,
        "disciplinary_decision": None,
        "message_sent": False,
        "finding": None,
        "language_flags": {
            "sexual_harassment_language": sexual,
            "third_party_language": third,
            "not_a_finding": True,
        },
        "special_category_possible": "sexual" in lowered,
        "signpost_for_a_person": (
            "A person may mention the Acas helpline. The agent does not contact Acas."
        ),
        "summary": (
            f"Anonymised report {reference} is for an HR lead to read. "
            "The agent has not decided what happened and has not closed it."
        ),
    }


def _check_evidence(evidence: dict) -> None:
    unknown = set(evidence) - EVIDENCE_KEYS - EVIDENCE_DATE_KEYS
    if unknown:
        names = ", ".join(sorted(unknown))
        raise ReviewError(f"unknown evidence fields: {names}")
    for key in EVIDENCE_KEYS:
        _evidence_status(evidence, key)


def review(
    pack: dict,
    *,
    as_of: date | None = None,
    stale_after_days: int = DEFAULT_STALE_AFTER_DAYS,
    policy_stale_after_days: int = DEFAULT_POLICY_STALE_AFTER_DAYS,
) -> dict:
    """Return a draft review, or a refusal that does not echo the pack."""
    if not isinstance(pack, dict):
        raise ReviewError("pack must be a JSON object")
    if stale_after_days < 0 or policy_stale_after_days < 0:
        raise ReviewError("stale thresholds must not be negative")

    prohibited: list[str] = []
    cleaned = _strip_prohibited(copy.deepcopy(pack), "", prohibited)

    if cleaned.get("synthetic") is not True:
        return _refusal("record_not_marked_synthetic")

    if as_of is None:
        if "as_of" not in cleaned:
            raise ReviewError("as_of is required")
        as_of = _parse_date(cleaned["as_of"], "as_of")
    elif not isinstance(as_of, date):
        raise ReviewError("as_of must be a date")

    employer = cleaned.get("employer")
    if not isinstance(employer, dict):
        raise ReviewError("employer must be an object")
    name = employer.get("name")
    if not isinstance(name, str) or not name.strip():
        raise ReviewError("employer.name is required")
    jurisdiction = employer.get("jurisdiction")
    if jurisdiction not in JURISDICTIONS:
        raise ReviewError(
            "employer.jurisdiction must be england, wales, england_and_wales, scotland, or northern_ireland"
        )
    worker_count = employer.get("worker_count")
    if worker_count is not None and (not isinstance(worker_count, int) or isinstance(worker_count, bool) or worker_count < 0):
        raise ReviewError("employer.worker_count must be a non-negative integer")
    sector = employer.get("sector")
    if sector is not None and not isinstance(sector, str):
        raise ReviewError("employer.sector must be a string")

    evidence = cleaned.get("evidence") or {}
    if not isinstance(evidence, dict):
        raise ReviewError("evidence must be an object")
    _check_evidence(evidence)

    hits: list[dict] = []
    _scan(cleaned, "", hits)
    signal_ids = sorted({signal for hit in hits for signal in hit["signals"]})
    name_quarantined = bool(signals_in_text(name))

    sources = _source_rows(as_of, stale_after_days)
    any_stale = any(row["stale"] for row in sources)
    applied = jurisdiction in GREAT_BRITAIN
    relied = applied and not any_stale
    duties = _duties(as_of, jurisdiction, applied, relied)
    by_id = {duty["id"]: duty for duty in duties}

    prompts = _duty_prompts(
        evidence,
        applied,
        by_id["prevent_sexual_harassment"]["in_force"],
        by_id["third_party_harassment"]["in_force"],
        by_id["whistleblowing_sexual_harassment"]["in_force"],
        by_id["unfair_dismissal_qualifying_period"]["in_force"],
    )
    currency = _policy_currency(evidence, as_of, policy_stale_after_days)
    answer = _answer(
        cleaned.get("question"),
        cleaned.get("policy_excerpts"),
        as_of,
        policy_stale_after_days,
    )
    incident = _incident(cleaned.get("incident"))

    risk_recorded = _evidence_status(evidence, "risk_assessment_recorded")
    if not applied:
        risk_recorded_status = "not_applied"
    else:
        risk_recorded_status = risk_recorded

    return {
        "label": LABEL,
        "catalogue_id": "UK03",
        "autonomy": "A1",
        "reference": cleaned.get("reference"),
        "employer_name": "[quarantined]" if name_quarantined else name.strip(),
        "employer_name_quarantined": name_quarantined,
        "jurisdiction": jurisdiction,
        "jurisdiction_applied": "great_britain" if applied else "not_applied",
        "northern_ireland_law_stated": False,
        "as_of": _iso(as_of),
        "hr_decision": None,
        "compliance_conclusion": None,
        "disciplinary_decision": None,
        "policy_published": False,
        "records_changed": False,
        "message_sent": False,
        "actions_taken": [],
        "model_called": False,
        "network_called": False,
        "legal_advice": False,
        "not_legal_advice": True,
        "any_source_stale": any_stale,
        "rules_current": not any_stale,
        "catalogue_last_verified": LAST_VERIFIED,
        "workforce": {
            "worker_count": worker_count,
            "sector": sector,
            "used_to_lower_a_duty": False,
            "note": (
                "Acas says the steps depend on the organisation. "
                "This core does not decide which steps are reasonable for this size or sector."
            ),
        },
        "sources_and_currency": sources,
        "duties": duties,
        "preparation_prompts": prompts,
        "policy_currency": currency,
        "policy_skeleton": {
            "status": "draft_headings_only",
            "hr_must_write": True,
            "published": False,
            "text_written_by_agent": False,
            "headings": [
                {"heading": heading, "body": None, "text_written_by_agent": False}
                for heading in POLICY_HEADINGS
            ],
        },
        "risk_assessment": {
            "likelihood": None,
            "impact": None,
            "residual_risk": None,
            "hr_must_complete": True,
            "employer_recorded": risk_recorded_status == "evidenced",
            "employer_status": risk_recorded_status,
            "agent_completed": False,
        },
        "employee_qa": answer,
        "incident_summary": incident,
        "prompt_injection": {
            "detected": bool(hits) or bool(prohibited),
            "signals": signal_ids,
            "fields": [hit["field"] for hit in hits],
            "prohibited_keys_ignored": prohibited,
            "followed": False,
        },
        "flags": {
            "policy_published": False,
            "records_changed": False,
            "message_sent": False,
            "disciplinary_decision_made": False,
            "compliance_concluded": False,
            "tribunal_deadline_calculated": False,
            "dismissal_decided": False,
            "acas_contacted": False,
            "regulations_under_section_40b_applied": False,
            "size_used_to_lower_a_duty": False,
            "northern_ireland_law_stated": False,
        },
        "firm_steps_for_a_person": [
            "The HR lead reads the draft and decides whether any evidence gap is accepted.",
            "The HR lead writes any policy change. The skeleton is headings only.",
            "The HR lead completes the risk-assessment ratings.",
            "A person, not the agent, replies to a worker or mentions Acas.",
            "A disciplinary step, a suspension, or a dismissal stays in the employer's own process.",
        ],
        "signpost": "This is not legal advice. A person may mention Acas or a solicitor. The agent contacts neither.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Draft an ERA 2025 HR review. Nothing is decided or sent.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--as-of", dest="as_of", required=True)
    parser.add_argument("--stale-after-days", type=int, default=DEFAULT_STALE_AFTER_DAYS)
    parser.add_argument("--policy-stale-after-days", type=int, default=DEFAULT_POLICY_STALE_AFTER_DAYS)
    args = parser.parse_args(argv)
    try:
        pack = json.loads(args.input.read_text(encoding="utf-8"))
        result = review(
            pack,
            as_of=_parse_date(args.as_of, "as_of"),
            stale_after_days=args.stale_after_days,
            policy_stale_after_days=args.policy_stale_after_days,
        )
    except (OSError, json.JSONDecodeError, ReviewError) as exc:
        sys.stderr.write(f"{exc}\n")
        return 2
    json.dump(result, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    if result["label"] == REFUSED:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
