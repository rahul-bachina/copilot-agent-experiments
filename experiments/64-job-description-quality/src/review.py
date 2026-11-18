#!/usr/bin/env python3
"""Prompts on a synthetic job description. The recruiter writes the final wording.

The agent does not publish, post, or send an advert. It does not score
candidates or adverts against people. It does not decide an occupational
requirement or positive action. Findings are prompts, not legal advice.

The same inputs and the same question date produce the same JSON. Approval
words inside the draft are not approval. An approval is a separate object,
from a directory recruiter, for this draft hash and this suggestion hash
or this exact wording hash.
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
    from injection import content_text, scan, sentence_is_strip
    from marking import (
        above_ceiling,
        content_markings,
        higher_marking,
        legal_hold,
        markings_in,
        retention_labels,
    )
    from mask import mask_text
    from reuse import NeighbourMissing, compare_module, redact_uk_identifiers
    from sources import statutory_note, pin_rows
    from words import (
        DISTRESS_PHRASES,
        EXAMPLE_NOTE,
        EXAMPLE_TERMS,
        HEALTH_PHRASES,
        OCCUPATIONAL_PHRASES,
        POSITIVE_ACTION_PHRASES,
        SCORING_PHRASES,
        affirmed,
        any_affirmed,
        sentences,
    )
else:
    from .injection import content_text, scan, sentence_is_strip
    from .marking import (
        above_ceiling,
        content_markings,
        higher_marking,
        legal_hold,
        markings_in,
        retention_labels,
    )
    from .mask import mask_text
    from .reuse import NeighbourMissing, compare_module, redact_uk_identifiers
    from .sources import statutory_note, pin_rows
    from .words import (
        DISTRESS_PHRASES,
        EXAMPLE_NOTE,
        EXAMPLE_TERMS,
        HEALTH_PHRASES,
        OCCUPATIONAL_PHRASES,
        POSITIVE_ACTION_PHRASES,
        SCORING_PHRASES,
        affirmed,
        any_affirmed,
        sentences,
    )

LABEL = "PROMPTS FOR A RECRUITER. NOT LEGAL ADVICE. NOT AN ADVERT."
CATALOGUE_ID = "H007"
EXPERIMENT_ID = "exp-64-job-description-quality"
AUTONOMY = "A0"
MAX_MONEY = Decimal("1000000")
MAX_WORDS = 80
_GRADE = re.compile(r"^[A-Z]{1,4}\d{1,2}$")
_GRADE_LINE = re.compile(r"\bgrade\s*:\s*([A-Za-z]{1,4}\d{1,2})\b", re.IGNORECASE)
_RANGE = re.compile(
    r"£\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})?\s+to\s+£\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})?",
    re.IGNORECASE,
)
_SINGLE = re.compile(
    r"£\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})?|\bGBP\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})?",
    re.IGNORECASE,
)
PROHIBITED_KEYS = frozenset(
    {
        "approved",
        "human_approval",
        "published",
        "posted",
        "sent",
        "advert_published",
        "quality_score",
        "candidates_scored",
        "people_scored",
        "final_wording",
        "role",
        "clearance",
        "suggestion_decisions",
    }
)


class JobDescriptionForbidden(RuntimeError):
    """Publish, send, and scoring are not tools of this agent."""


class NotSynthetic(ValueError):
    """The record was not marked synthetic. The message does not include the body."""


def publish(*_args, **_kwargs) -> None:
    raise JobDescriptionForbidden("The agent does not publish an advert.")


def post(*_args, **_kwargs) -> None:
    raise JobDescriptionForbidden("The agent does not post an advert.")


def send(*_args, **_kwargs) -> None:
    raise JobDescriptionForbidden("The agent does not send an advert.")


def score_candidate(*_args, **_kwargs) -> None:
    raise JobDescriptionForbidden("The agent does not score candidates.")


def score_advert_against_people(*_args, **_kwargs) -> None:
    raise JobDescriptionForbidden("The agent does not score an advert against people.")


def rank_applicants(*_args, **_kwargs) -> None:
    raise JobDescriptionForbidden("The agent does not rank applicants.")


def _parse_day(value: object) -> date | None:
    if isinstance(value, date) and not isinstance(value, type(None)):
        if type(value) is date:
            return value
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _canonical(payload: object) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _draft_hash(draft: dict) -> str:
    payload = {key: draft[key] for key in sorted(draft) if key not in PROHIBITED_KEYS}
    return _sha(_canonical(payload))


def _suggestion_hash(finding: dict) -> str:
    payload = {
        "suggestion_id": finding.get("suggestion_id"),
        "category": finding.get("category"),
        "reason": finding.get("reason"),
        "suggested_alternative": finding.get("suggested_alternative"),
        "excerpt_masked": finding.get("excerpt_masked"),
    }
    return _sha(_canonical(payload))


def _string_list(value: object) -> list[str] | None:
    """A list of strings, or None when the value cannot be read. Never a default list."""

    if not isinstance(value, list):
        return None
    rows = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            return None
        rows.append(item.strip())
    return rows


def _parse_money(value: object) -> str | Decimal:
    """A Decimal, 'missing', 'range', or 'unparseable'. Unparseable is not zero."""

    if value is None or value == "":
        return "missing"
    if isinstance(value, bool) or not isinstance(value, str):
        return "unparseable"
    text = value.strip()
    if not text:
        return "missing"
    if re.search(r"\bto\b", text, re.IGNORECASE):
        return "range"
    cleaned = re.sub(r"(?i)\bgbp\b", "", text).replace("£", "").replace(",", "").strip()
    if not re.fullmatch(r"\d+(?:\.\d{2})?", cleaned):
        return "unparseable"
    amount = Decimal(cleaned)
    if amount < 0 or amount > MAX_MONEY:
        return "unparseable"
    return amount


def _money_code(amount: Decimal) -> str:
    if amount == amount.to_integral_value():
        return f"GBP {int(amount)}"
    return f"GBP {amount:.2f}"


def _body_amounts(text: str) -> str | list[str]:
    """Single-figure extracts, 'range' when a range is present, or a list."""

    without_ranges = _RANGE.sub(" ", text or "")
    if _RANGE.search(text or ""):
        return "range"
    found = []
    for match in _SINGLE.finditer(without_ranges):
        parsed = _parse_money(match.group(0))
        if isinstance(parsed, Decimal):
            code = _money_code(parsed)
            if code not in found:
                found.append(code)
    return found


def _grade_token(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    token = value.strip().upper()
    if _GRADE.fullmatch(token):
        return token
    return None


def _body_grades(text: str) -> list[str]:
    found = []
    for match in _GRADE_LINE.finditer(text or ""):
        token = match.group(1).upper()
        if _GRADE.fullmatch(token) and token not in found:
            found.append(token)
    return found


def _excerpt(sentence: str) -> str:
    masked, _counts = mask_text(sentence)
    if len(masked) > 240:
        return masked[:240]
    return masked


def _person(directory: dict, ref: object) -> dict | None:
    if not isinstance(ref, str):
        return None
    people = directory.get("people")
    if not isinstance(people, list):
        return None
    for person in people:
        if isinstance(person, dict) and person.get("ref") == ref:
            return person
    return None


def _blank() -> dict:
    return {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment_id": EXPERIMENT_ID,
        "autonomy": AUTONOMY,
        "legal_advice": False,
        "published": False,
        "posted": False,
        "sent": False,
        "advert_published": False,
        "quality_score": None,
        "candidates_scored": False,
        "people_scored": False,
        "adverts_scored_against_people": False,
        "occupational_requirement_decided": False,
        "positive_action_decided": False,
        "health_question_decided": False,
        "discrimination_decided": False,
        "right_to_work_checked": False,
        "penalty_given": False,
        "human_approval": None,
        "final_wording": None,
        "final_wording_written_by_agent": False,
        "agent_chose_source": False,
        "correct_value": None,
        "coerced": False,
        "output_is_anonymised": False,
        "described_as_anonymised": False,
        "instructions_followed": False,
        "model_called": False,
        "network_called": False,
        "foundry_called": False,
        "actions_taken": [],
        "example_word_list": {
            "label": "example_list",
            "organisation_must_review": True,
            "statistic": None,
            "note": EXAMPLE_NOTE,
            "term_count": len(EXAMPLE_TERMS),
        },
    }


def _force(result: dict) -> dict:
    result["legal_advice"] = False
    result["published"] = False
    result["posted"] = False
    result["sent"] = False
    result["advert_published"] = False
    result["quality_score"] = None
    result["candidates_scored"] = False
    result["people_scored"] = False
    result["adverts_scored_against_people"] = False
    result["occupational_requirement_decided"] = False
    result["positive_action_decided"] = False
    result["health_question_decided"] = False
    result["discrimination_decided"] = False
    result["right_to_work_checked"] = False
    result["penalty_given"] = False
    result["final_wording_written_by_agent"] = False
    result["agent_chose_source"] = False
    result["correct_value"] = None
    result["coerced"] = False
    result["output_is_anonymised"] = False
    result["described_as_anonymised"] = False
    result["instructions_followed"] = False
    result["model_called"] = False
    result["network_called"] = False
    result["foundry_called"] = False
    result["actions_taken"] = []
    injection = result.get("prompt_injection")
    if isinstance(injection, dict):
        injection["followed"] = False
    return result


def _mask_report(result: dict, original: str, uk: dict | None) -> None:
    _incoming_text, incoming = mask_text(original)
    blob = json.dumps({key: value for key, value in result.items() if key != "masking"}, default=str)
    _out_text, outgoing = mask_text(blob)
    uk_on_output = {"types": [], "count": 0, "called": False}
    try:
        uk_on_output = redact_uk_identifiers(blob)
    except (NeighbourMissing, RuntimeError, TypeError, ValueError):
        uk_on_output = {"types": [], "count": 0, "called": False}
    values_copied = bool(outgoing["any"] or uk_on_output["count"])
    result["masking"] = {
        "input_counts": incoming["counts"],
        "output_counts": outgoing["counts"],
        "uk_identifier_types": list((uk or {}).get("types") or []),
        "uk_identifier_count": int((uk or {}).get("count") or 0),
        "experiment_08_called": bool((uk or {}).get("called")),
        "experiment_08_output_is_anonymised": False,
        "values_stored": False,
        "values_copied": values_copied,
        "described_as_anonymised": False,
        "output_is_anonymised": False,
        "body_copied": False,
    }
    result["flags"]["output_is_anonymised"] = False
    result["flags"]["values_copied"] = values_copied


def _compare(fact_key: str, field_type: str, figures: list[tuple[str, str]], as_of: str) -> dict:
    if len(figures) < 2:
        return {
            "called": False,
            "reason": "single_source",
            "agent_chose_source": False,
            "material": False,
            "correct_value": None,
            "classification": None,
            "do_not_rely": False,
        }
    documents = []
    for index, (doc_id, value) in enumerate(figures):
        documents.append(
            {
                "document_id": doc_id,
                "title": "Figure extract",
                "kind": "form" if index == 0 else "contract",
                "status": "current",
                "reviewed_on": as_of,
                "pages": [{"page": 1, "paragraphs": [{"paragraph": 1, "lines": [{"line": 1, "text": value}]}]}],
                "fields": [{"fact_key": fact_key, "page": 1, "paragraph": 1, "line": 1, "value": value}],
            }
        )
    pack = {
        "synthetic": True,
        "pack_id": "jd-salary" if fact_key.startswith("salary") else "jd-grade",
        "facts": [{"fact_key": fact_key, "field_type": field_type}],
        "documents": documents,
    }
    try:
        report = compare_module().compare(pack, as_of)
    except (NeighbourMissing, TypeError, ValueError, RuntimeError):
        return {
            "called": False,
            "reason": "compare_failed",
            "agent_chose_source": False,
            "material": True,
            "correct_value": None,
            "classification": None,
            "do_not_rely": True,
        }
    fact = (report.get("facts") or [{}])[0]
    classification = fact.get("classification")
    return {
        "called": True,
        "experiment_id": "exp-36-cross-source-validation",
        "fact_key": fact_key,
        "classification": classification,
        "agent_chose_source": report.get("agent_chose_source") is True,
        "correct_value": None,
        "material": classification == "material_discrepancy",
        "do_not_rely": report.get("do_not_rely") is True,
        "quotes_copied": False,
    }


def _finding(
    category: str,
    reason: str,
    alternative: str,
    excerpt: str,
    *,
    requires_decision: bool,
    requires_hr: bool,
    example_list: bool,
    route_to: str | None,
) -> dict:
    row = {
        "category": category,
        "reason": reason,
        "suggested_alternative": alternative,
        "excerpt_masked": excerpt,
        "prompt_for_human": True,
        "legal_advice": False,
        "decided": False,
        "decision": None,
        "requires_decision": requires_decision,
        "requires_hr": requires_hr,
        "hr_seen": False,
        "example_list": example_list,
        "organisation_must_review_list": example_list,
        "route_to": route_to,
        "statistic": None,
    }
    return row


def _finish_findings(rows: list[dict]) -> list[dict]:
    rows.sort(key=lambda item: (item["category"], item["reason"], item.get("excerpt_masked") or ""))
    finished = []
    for index, row in enumerate(rows, start=1):
        row["suggestion_id"] = f"F-{index:02d}"
        row["suggestion_hash"] = _suggestion_hash(row)
        finished.append(row)
    return finished


def _prompt(reason: str, alternative: str) -> str:
    return (
        reason
        + " This is a prompt for a person, not a finding that the wording is unlawful, "
        + "and not legal advice. " + alternative
    )


def review_draft(request: dict, guide: dict, directory: dict, as_of: str) -> dict:
    """Return prompts for one draft. human_approval stays null. Nothing is published."""

    if not isinstance(request, dict) or request.get("synthetic") is not True:
        raise NotSynthetic("request is not marked synthetic")
    if not isinstance(guide, dict) or guide.get("synthetic") is not True:
        raise NotSynthetic("guide is not marked synthetic")
    if not isinstance(directory, dict) or directory.get("synthetic") is not True:
        raise NotSynthetic("directory is not marked synthetic")
    question = _parse_day(as_of)
    if question is None or not isinstance(as_of, str):
        raise ValueError("as_of must be YYYY-MM-DD")

    result = _blank()
    result["as_of"] = as_of
    result["question_date"] = as_of
    result["blocked_reason"] = None
    result["flags"] = {
        "output_is_anonymised": False,
        "values_copied": False,
        "body_copied": False,
        "self_declared_role_ignored": False,
        "self_declared_clearance_ignored": False,
        "distress_route": False,
        "scoring_refused": False,
    }
    stripped = [key for key in request if key in PROHIBITED_KEYS]
    result["stripped_request_keys"] = stripped
    draft = request.get("draft")
    if not isinstance(draft, dict):
        result["outcome"] = "unreadable_draft"
        result["may_be_relied_on"] = False
        result["sources_current"] = False
        result["findings"] = []
        result["prompt_count"] = 0
        result["finding_count"] = 0
        _force(result)
        _mask_report(result, "", None)
        return result

    clean_draft = {key: value for key, value in draft.items() if key not in PROHIBITED_KEYS}
    try:
        result["draft_hash"] = _draft_hash(clean_draft)
    except (TypeError, ValueError):
        result["outcome"] = "unreadable_draft"
        result["may_be_relied_on"] = False
        result["sources_current"] = False
        result["findings"] = []
        result["prompt_count"] = 0
        result["finding_count"] = 0
        result["coerced"] = False
        _force(result)
        _mask_report(result, "", None)
        return result
    result["draft_id"] = clean_draft.get("draft_id") if isinstance(clean_draft.get("draft_id"), str) else None

    text = clean_draft.get("text") if isinstance(clean_draft.get("text"), str) else ""
    text_unreadable = not isinstance(clean_draft.get("text"), str)
    injection = scan(text)
    guide_injection = scan(guide.get("notes") if isinstance(guide.get("notes"), str) else "")
    injection["guide_signals"] = guide_injection["signals"]
    injection["guide_followed"] = False
    if guide_injection["detected"]:
        injection["detected"] = True
    if "self_role" in injection["signals"] or "role" in stripped:
        result["flags"]["self_declared_role_ignored"] = True
    if "self_clearance" in injection["signals"] or "clearance" in stripped:
        result["flags"]["self_declared_clearance_ignored"] = True
    result["prompt_injection"] = injection

    recruiter_ref = request.get("recruiter_ref")
    person = _person(directory, recruiter_ref)
    result["recruiter_ref"] = recruiter_ref if isinstance(recruiter_ref, str) else None
    if not isinstance(directory.get("people"), list):
        result["outcome"] = "directory_unreadable"
        result["may_be_relied_on"] = False
        result["sources_current"] = False
        result["findings"] = []
        result["prompt_count"] = 0
        result["finding_count"] = 0
        _force(result)
        _mask_report(result, text, None)
        return result
    if person is None or person.get("role") != "recruiter":
        result["outcome"] = "recruiter_not_in_directory" if person is None else "not_a_recruiter"
        result["directory_role"] = person.get("role") if isinstance(person, dict) else None
        result["may_be_relied_on"] = False
        result["sources_current"] = False
        result["findings"] = []
        result["body_withheld"] = True
        result["prompt_count"] = 0
        result["finding_count"] = 0
        _force(result)
        _mask_report(result, text, None)
        return result
    result["directory_role"] = "recruiter"
    ceiling = person.get("clearance")
    if not isinstance(ceiling, str) or ceiling not in {"OFFICIAL", "OFFICIAL-SENSITIVE", "SECRET", "TOP SECRET"}:
        result["outcome"] = "clearance_unreadable"
        result["clearance"] = None
        result["clearance_coerced"] = False
        result["may_be_relied_on"] = False
        result["sources_current"] = False
        result["findings"] = []
        result["body_withheld"] = True
        result["prompt_count"] = 0
        result["finding_count"] = 0
        _force(result)
        _mask_report(result, text, None)
        return result
    result["clearance"] = ceiling

    meta_raw = clean_draft.get("marking")
    meta_unreadable = False
    meta_labels = []
    if isinstance(meta_raw, str):
        meta_labels = markings_in(meta_raw)
    elif meta_raw not in (None, ""):
        meta_unreadable = True
    page_labels = content_markings(text)
    marking = higher_marking(meta_labels + page_labels)
    labels, retention_bad = retention_labels(clean_draft.get("retention_labels"), text)
    held = legal_hold(clean_draft.get("legal_hold"), text)
    result["marking"] = marking
    result["marking_found"] = marking is not None
    result["marking_unreadable"] = meta_unreadable
    result["retention_labels"] = labels
    result["retention_unreadable"] = retention_bad
    result["legal_hold"] = held
    result["body_withheld"] = False

    uk = None
    try:
        uk = redact_uk_identifiers(text)
    except (NeighbourMissing, RuntimeError, TypeError, ValueError):
        uk = {"text": "", "types": [], "count": 0, "called": False, "output_is_anonymised": False, "values_stored": False}

    if above_ceiling(marking, ceiling) or text_unreadable:
        result["outcome"] = "unreadable_draft" if text_unreadable else "above_clearance"
        result["body_withheld"] = True
        result["distress_detected"] = any_affirmed(text, DISTRESS_PHRASES)
        result["flags"]["distress_route"] = result["distress_detected"]
        result["may_be_relied_on"] = False
        result["sources_current"] = False
        result["findings"] = []
        result["prompt_count"] = 0
        result["finding_count"] = 0
        result["cue_copied"] = False
        _force(result)
        _mask_report(result, text, uk)
        return result

    if any_affirmed(text, DISTRESS_PHRASES):
        result["outcome"] = "human_route"
        result["flags"]["distress_route"] = True
        result["route_to"] = "hr_partner"
        result["cue_copied"] = False
        result["may_be_relied_on"] = False
        result["sources_current"] = False
        result["findings"] = []
        result["prompt_count"] = 0
        result["finding_count"] = 0
        result["statement"] = (
            "A distress, vulnerability, or safeguarding cue is a route to a person. "
            "The cue is not copied. This is not a routine wording review."
        )
        _force(result)
        _mask_report(result, text, uk)
        return result

    if any_affirmed(text, SCORING_PHRASES):
        result["outcome"] = "scoring_refused"
        result["flags"]["scoring_refused"] = True
        result["may_be_relied_on"] = False
        result["sources_current"] = False
        result["findings"] = []
        result["prompt_count"] = 0
        result["finding_count"] = 0
        result["statement"] = "The agent does not score candidates or adverts against people."
        _force(result)
        _mask_report(result, text, uk)
        return result

    cleaned = content_text(text)
    working = uk.get("text") if uk.get("called") else cleaned
    # Matching uses the redacted body when Experiment 08 ran, and still ignores
    # instruction sentences. Identifiers are not required for the phrase checks.
    match_text = content_text(working if isinstance(working, str) else cleaned)

    reviewed = _parse_day(guide.get("reviewed_on"))
    due = _parse_day(guide.get("review_due"))
    dates_unreadable = reviewed is None or due is None
    in_force = reviewed is not None and question >= reviewed
    stale = due is not None and question >= due
    not_yet = reviewed is not None and question < reviewed
    result["guide"] = {
        "guide_id": guide.get("guide_id") if isinstance(guide.get("guide_id"), str) else None,
        "reviewed_on": guide.get("reviewed_on") if isinstance(guide.get("reviewed_on"), str) else None,
        "review_due": guide.get("review_due") if isinstance(guide.get("review_due"), str) else None,
        "dates_unreadable": dates_unreadable,
        "in_force": False if dates_unreadable else in_force and not stale,
        "stale": False if dates_unreadable else stale,
        "not_yet_in_force": False if dates_unreadable else not_yet,
        "coerced": False,
    }
    pins = pin_rows(question)
    result["pins"] = [
        {"id": row["id"], "confirmed_for_question_date": row["confirmed_for_question_date"], "up_to_date_on_or_before": row["up_to_date_on_or_before"]}
        for row in pins
    ]
    result["pins_not_confirmed"] = [row["id"] for row in pins if not row["confirmed_for_question_date"]]
    result["statutory_note"] = statutory_note(question)
    supplied_question = request.get("question_date")
    conflict = False
    question_unreadable = False
    if "question_date" in request:
        parsed_question = _parse_day(supplied_question)
        if parsed_question is None:
            question_unreadable = True
        elif parsed_question.isoformat() != as_of:
            conflict = True
    result["question_date_conflict"] = conflict
    result["question_date_unreadable"] = question_unreadable

    limit = guide.get("sentence_word_limit")
    limit_ok = type(limit) is int and 1 <= limit <= MAX_WORDS
    result["sentence_word_limit"] = limit if limit_ok else None
    result["sentence_word_limit_unreadable"] = not limit_ok
    jargon = _string_list(guide.get("jargon")) if "jargon" in guide else []
    jargon_unreadable = "jargon" in guide and jargon is None
    if jargon is None:
        jargon = []
    requires = _string_list(guide.get("requires"))
    requires_unreadable = requires is None
    if requires is None:
        requires = []

    grades = guide.get("grades")
    grade_index: dict[str, dict] = {}
    grades_unreadable = not isinstance(grades, list)
    if isinstance(grades, list):
        for row in grades:
            if not isinstance(row, dict):
                grades_unreadable = True
                continue
            token = _grade_token(row.get("grade"))
            if token:
                grade_index[token] = row
            else:
                grades_unreadable = True

    findings: list[dict] = []
    if dates_unreadable:
        findings.append(_finding(
            "unparseable_field",
            "The guide review date or the review-due date cannot be read. It has not been replaced with today or with another date.",
            "A person should confirm the guide dates. This tool will not invent them.",
            "",
            requires_decision=True, requires_hr=False, example_list=False, route_to=None,
        ))
    elif stale or not_yet:
        findings.append(_finding(
            "stale_or_not_in_force",
            "On the question date the guide is stale or not yet in force. A review date on the question date is treated as due. That is this starter's rule, not a statutory period.",
            "A person should confirm which guide applies on the question date. This tool does not choose a later guide.",
            "",
            requires_decision=True, requires_hr=False, example_list=False, route_to=None,
        ))
    if not limit_ok:
        findings.append(_finding(
            "unparseable_field",
            "The sentence limit in the guide cannot be read. It has not been replaced with 25 or with zero.",
            "A person should set the organisation's sentence limit. This is not a reading-age measure.",
            "",
            requires_decision=True, requires_hr=False, example_list=False, route_to=None,
        ))
    if jargon_unreadable or requires_unreadable or grades_unreadable or result["marking_unreadable"] or retention_bad:
        findings.append(_finding(
            "unparseable_field",
            "A guide or draft field was not a list or a marking this starter can read. It has not been coerced to an empty list or to OFFICIAL.",
            "A person should correct the field. This tool has not substituted a default.",
            "",
            requires_decision=True, requires_hr=False, example_list=False, route_to=None,
        ))

    field_grade = clean_draft.get("grade")
    field_token = _grade_token(field_grade) if isinstance(field_grade, str) and field_grade.strip() else None
    grade_unreadable = isinstance(field_grade, str) and field_grade.strip() and field_token is None
    grade_missing = field_grade in (None, "") or (isinstance(field_grade, str) and not field_grade.strip())
    if field_grade not in (None, "") and not isinstance(field_grade, str):
        grade_unreadable = True
        grade_missing = False
    body_grades = _body_grades(match_text)
    grade_compare = None
    established: str | None = None
    if field_token and len(body_grades) == 1 and body_grades[0] != field_token:
        grade_compare = _compare("stated_grade", "reference", [("grade-field", field_token), ("grade-text", body_grades[0])], as_of)
    elif field_token and len(body_grades) == 1:
        grade_compare = _compare("stated_grade", "reference", [("grade-field", field_token), ("grade-text", body_grades[0])], as_of)
        established = field_token
    elif field_token and not body_grades:
        established = field_token
        grade_compare = {"called": False, "reason": "single_source", "agent_chose_source": False, "material": False, "correct_value": None, "classification": None, "do_not_rely": False}
    elif not field_token and len(body_grades) == 1:
        established = body_grades[0]
        grade_compare = {"called": False, "reason": "single_source", "agent_chose_source": False, "material": False, "correct_value": None, "classification": None, "do_not_rely": False}
    elif len(body_grades) > 1:
        grade_unreadable = True
    result["grade"] = {
        "token": established,
        "unparseable": grade_unreadable,
        "missing": grade_missing and established is None,
        "coerced": False,
        "cross_source": grade_compare,
    }
    if grade_compare and grade_compare.get("material"):
        established = None
        result["grade"]["token"] = None
        findings.append(_finding(
            "grade_inconsistency",
            "The grade in the draft field and the grade in the text are not the same after Experiment 36. This tool does not choose which grade is right.",
            "A person should decide which grade applies. The duty check waits until then.",
            "",
            requires_decision=True, requires_hr=False, example_list=False, route_to=None,
        ))
    if grade_unreadable:
        findings.append(_finding(
            "unparseable_field",
            "The grade cannot be read. It has not been replaced with a default grade.",
            "A person should write the grade in the form the guide uses.",
            "",
            requires_decision=True, requires_hr=False, example_list=False, route_to=None,
        ))

    profile = grade_index.get(established) if established else None
    if established and profile is None and not grades_unreadable:
        findings.append(_finding(
            "grade_inconsistency",
            f"The grade {established} is not in the synthetic guide. No other grade has been substituted.",
            "A person should confirm the grade. This tool does not pick the nearest band.",
            "",
            requires_decision=True, requires_hr=False, example_list=False, route_to=None,
        ))

    degree_required = profile.get("degree_required") if profile else None
    physical_recorded = profile.get("physical_requirement_recorded") if profile else None
    degree_known = isinstance(degree_required, bool)
    physical_known = isinstance(physical_recorded, bool)
    if profile and (not degree_known or not physical_known):
        findings.append(_finding(
            "unparseable_field",
            "The guide does not say, as a boolean, whether this grade records a degree or a physical requirement. Those flags have not been treated as false.",
            "A person should read the grade profile. This tool has not filled the gap.",
            "",
            requires_decision=True, requires_hr=False, example_list=False, route_to=None,
        ))

    duty_phrases = _string_list(profile.get("duty_phrases")) if profile else []
    if profile and duty_phrases is None:
        duty_phrases = []
        findings.append(_finding(
            "unparseable_field",
            "The duty phrases for this grade cannot be read. They have not been treated as an empty list of duties.",
            "A person should confirm the grade profile.",
            "",
            requires_decision=True, requires_hr=False, example_list=False, route_to=None,
        ))
    not_this = _string_list(profile.get("not_this_grade")) if profile else []
    if profile and not_this is None:
        not_this = []
    duties = _string_list(clean_draft.get("duties"))
    duties_unreadable = "duties" in clean_draft and duties is None
    if duties is None:
        duties = []
    if duties_unreadable:
        findings.append(_finding(
            "unparseable_field",
            "The duties were not a list of strings. They have not been split or dropped.",
            "A person should supply the duties as a list.",
            "",
            requires_decision=True, requires_hr=False, example_list=False, route_to=None,
        ))
    if established and profile and not_this:
        for phrase in not_this:
            if affirmed(match_text, phrase) or any(affirmed(duty, phrase) for duty in duties):
                findings.append(_finding(
                    "grade_inconsistency",
                    f"The draft describes work the guide lists as not this grade ({phrase}). This is not a decision that the grade is wrong.",
                    "A person should compare the duties with the grade profile.",
                    _excerpt(phrase),
                    requires_decision=True, requires_hr=False, example_list=False, route_to=None,
                ))
                break

    salary_raw = clean_draft.get("salary")
    parsed_salary = _parse_money(salary_raw)
    body_salary = _body_amounts(match_text)
    salary_sources: list[tuple[str, str]] = []
    if isinstance(parsed_salary, Decimal):
        salary_sources.append(("salary-field", _money_code(parsed_salary)))
    salary_range = body_salary == "range" or parsed_salary == "range"
    if isinstance(body_salary, list):
        for index, code in enumerate(body_salary):
            salary_sources.append((f"salary-body-{index}", code))
    # De-duplicate identical codes from field and body for the call, but two
    # documents are required when the same figure is stated twice only if the
    # values differ or both places state a figure. Same figure still goes to
    # Experiment 36 when both a field and a body figure exist.
    cross = None
    band_checked = False
    if salary_range:
        findings.append(_finding(
            "unparseable_field",
            "A salary range has not been collapsed to one figure or to zero.",
            "A person should state the figure the guide asks for, if it asks for one.",
            "",
            requires_decision=True, requires_hr=False, example_list=False, route_to=None,
        ))
    elif len(salary_sources) >= 2:
        cross = _compare("salary_gbp", "currency", salary_sources[:2], as_of)
        if cross.get("material") or cross.get("do_not_rely"):
            findings.append(_finding(
                "salary_sources_disagree",
                "Two salary figures were read. Experiment 36 compared them. This tool does not choose a source and does not check the guide band until a person does.",
                "A person should decide which figure to use. Neither figure has been written back as the correct salary.",
                "",
                requires_decision=True, requires_hr=False, example_list=False, route_to=None,
            ))
        elif cross.get("called") and not cross.get("material"):
            band_checked = isinstance(parsed_salary, Decimal)
    elif len(salary_sources) == 1:
        cross = {"called": False, "reason": "single_source", "agent_chose_source": False, "material": False, "correct_value": None, "classification": None, "do_not_rely": False}
        band_checked = isinstance(parsed_salary, Decimal) or (isinstance(body_salary, list) and len(body_salary) == 1)
    else:
        cross = {"called": False, "reason": "single_source" if parsed_salary == "missing" else "unparseable", "agent_chose_source": False, "material": False, "correct_value": None, "classification": None, "do_not_rely": False}
    if parsed_salary == "unparseable":
        findings.append(_finding(
            "unparseable_field",
            "The salary cannot be read. It has not been replaced with zero.",
            "A person should write the salary the guide requires, if it requires one.",
            "",
            requires_decision=True, requires_hr=False, example_list=False, route_to=None,
        ))
    amount_for_band = parsed_salary if isinstance(parsed_salary, Decimal) else None
    if amount_for_band is None and isinstance(body_salary, list) and len(body_salary) == 1 and band_checked:
        amount_for_band = _parse_money(body_salary[0].replace("GBP ", ""))
        if not isinstance(amount_for_band, Decimal):
            amount_for_band = None
            band_checked = False
    if cross and cross.get("material"):
        band_checked = False
        amount_for_band = None
    band_note = None
    if band_checked and amount_for_band is not None and profile:
        low = _parse_money(str(profile.get("salary_min_gbp"))) if profile.get("salary_min_gbp") is not None else "unparseable"
        high = _parse_money(str(profile.get("salary_max_gbp"))) if profile.get("salary_max_gbp") is not None else "unparseable"
        if not isinstance(low, Decimal) or not isinstance(high, Decimal):
            findings.append(_finding(
                "unparseable_field",
                "The guide salary band cannot be read. The draft figure has not been compared with zero.",
                "A person should confirm the band.",
                "",
                requires_decision=True, requires_hr=False, example_list=False, route_to=None,
            ))
            band_checked = False
        elif amount_for_band < low or amount_for_band > high:
            findings.append(_finding(
                "grade_inconsistency",
                "The single salary figure sits outside the band written in the guide for this grade. This is not a decision that either figure is the right salary.",
                "A person should check the figure against the guide. This tool does not set the salary.",
                "",
                requires_decision=True, requires_hr=False, example_list=False, route_to=None,
            ))
            band_note = "outside_guide_band"
        else:
            band_note = "inside_guide_band"
    result["salary"] = {
        "amount": f"{amount_for_band:.2f}" if isinstance(amount_for_band, Decimal) and band_checked else None,
        "status": parsed_salary if isinstance(parsed_salary, str) else "read",
        "coerced": False,
        "band_checked": band_checked,
        "band_note": band_note,
        "cross_source": cross,
    }

    location = clean_draft.get("location")
    location_present = isinstance(location, str) and bool(location.strip())
    location_unreadable = "location" in clean_draft and not isinstance(location, str)
    if "salary" in requires and parsed_salary == "missing" and not (isinstance(body_salary, list) and body_salary):
        findings.append(_finding(
            "missing_required_information",
            "The guide requires a salary and this draft does not state one figure. No salary has been invented.",
            "A person should add the salary, or record why the guide does not apply.",
            "",
            requires_decision=True, requires_hr=False, example_list=False, route_to=None,
        ))
    if "location" in requires and (not location_present or location_unreadable):
        findings.append(_finding(
            "missing_required_information",
            "The guide requires a location and this draft does not state one. No location has been invented.",
            "A person should add the location.",
            "",
            requires_decision=True, requires_hr=False, example_list=False, route_to=None,
        ))
    if "grade" in requires and established is None and (grade_missing or grade_unreadable or (grade_compare and grade_compare.get("material"))):
        if not any(row["category"] == "grade_inconsistency" and "not the same" in row["reason"] for row in findings):
            if grade_missing and not grade_unreadable:
                findings.append(_finding(
                    "missing_required_information",
                    "The guide requires a grade and this draft does not state one. No grade has been invented.",
                    "A person should add the grade.",
                    "",
                    requires_decision=True, requires_hr=False, example_list=False, route_to=None,
                ))

    for phrase in OCCUPATIONAL_PHRASES:
        if affirmed(text, phrase):
            findings.append(_finding(
                "occupational_requirement_route",
                "The draft uses words that may be an occupational requirement under the Equality Act 2010, Schedule 9, paragraph 1. This tool does not decide that paragraph 1(1) is met.",
                "Ask HR. Do not treat this as a wording change a recruiter can close.",
                _excerpt(phrase),
                requires_decision=False, requires_hr=True, example_list=True, route_to="hr_partner",
            ))
            break
    for phrase in POSITIVE_ACTION_PHRASES:
        if affirmed(text, phrase):
            findings.append(_finding(
                "positive_action_route",
                "The draft uses words that may be positive action under the Equality Act 2010, section 159. This tool does not decide that section 159(4) is met.",
                "Ask HR. Do not treat this as a wording change a recruiter can close.",
                _excerpt(phrase),
                requires_decision=False, requires_hr=True, example_list=True, route_to="hr_partner",
            ))
            break
    for phrase in HEALTH_PHRASES:
        if affirmed(text, phrase):
            findings.append(_finding(
                "pre_employment_health",
                "The draft asks about health or disability before a job is offered. Equality Act 2010 section 60(1) was read. This tool does not decide that a section 60(6) purpose applies, and it does not answer the question.",
                "Ask HR. Remove the question only if HR says so.",
                _excerpt(phrase),
                requires_decision=False, requires_hr=True, example_list=True, route_to="hr_partner",
            ))
            break

    for term in EXAMPLE_TERMS:
        group = term["group"]
        if group == "degree" and degree_known and degree_required is True:
            continue
        if group == "physical" and physical_known and physical_recorded is True:
            continue
        if group == "physical" and term["phrase"] == "good health required":
            continue
        if not affirmed(match_text, term["phrase"]):
            continue
        findings.append(_finding(
            "exclusionary_wording",
            _prompt(
                f"The example list includes '{term['phrase']}' ({group}). {EXAMPLE_NOTE}",
                f"A person could consider '{term['alternative']}' instead.",
            ),
            f"A person could consider '{term['alternative']}' instead. The list is an example the organisation must review.",
            _excerpt(term["phrase"]),
            requires_decision=True, requires_hr=False, example_list=True, route_to=None,
        ))

    if limit_ok:
        for sentence in sentences(match_text):
            words = re.findall(r"[A-Za-z0-9]+(?:'[A-Za-z0-9]+)?", sentence)
            if len(words) > limit:
                findings.append(_finding(
                    "inaccessible_language",
                    f"This sentence is longer than the organisation's limit of {limit} words. That limit is the guide's rule. It is not a reading-age score.",
                    "A person could split the sentence. Keep any mandated statement that sits in it.",
                    _excerpt(sentence),
                    requires_decision=True, requires_hr=False, example_list=False, route_to=None,
                ))
                break
    for term in jargon:
        if affirmed(match_text, term):
            findings.append(_finding(
                "inaccessible_language",
                f"The organisation's guide lists '{term}' as jargon. This is not a national reading-age measure.",
                "A person could use a plainer word. The jargon list is the guide's list.",
                _excerpt(term),
                requires_decision=True, requires_hr=False, example_list=False, route_to=None,
            ))

    essential = _string_list(clean_draft.get("essential"))
    if "essential" in clean_draft and essential is None:
        findings.append(_finding(
            "unparseable_field",
            "The essential criteria were not a list of strings. They have not been dropped and they have not been treated as justified.",
            "A person should supply the essential criteria as a list.",
            "",
            requires_decision=True, requires_hr=False, example_list=False, route_to=None,
        ))
        essential = []
    if essential is None:
        essential = []
    link_phrases = list(duty_phrases or []) + list(duties)
    for criterion in essential:
        linked = False
        folded = criterion.casefold()
        for phrase in link_phrases:
            if phrase.casefold() in folded or folded in phrase.casefold():
                linked = True
                break
        if degree_known and degree_required is True and any(affirmed(criterion, term["phrase"]) for term in EXAMPLE_TERMS if term["group"] == "degree"):
            linked = True
        if physical_known and physical_recorded is True and any(affirmed(criterion, term["phrase"]) for term in EXAMPLE_TERMS if term["group"] == "physical"):
            linked = True
        if not linked:
            findings.append(_finding(
                "unjustified_essential",
                "This essential criterion is not linked to a duty in the draft or to a duty phrase on the grade profile. This is not a decision that the criterion is unlawful.",
                "A person should decide whether the criterion is needed, and should write the reason if it stays.",
                _excerpt(criterion),
                requires_decision=True, requires_hr=False, example_list=False, route_to=None,
            ))

    mandated_rows = guide.get("mandated_statements")
    kept = []
    if isinstance(mandated_rows, list):
        for row in mandated_rows:
            if not isinstance(row, dict):
                continue
            phrase = row.get("phrase")
            if not isinstance(phrase, str) or not phrase.strip():
                continue
            present = False
            for sentence in sentences(text):
                if sentence_is_strip(sentence):
                    continue
                if affirmed(sentence, phrase):
                    present = True
                    break
            record = {
                "id": row.get("id"),
                "label": row.get("label"),
                "phrase": phrase,
                "present": present,
                "stripped": False,
            }
            kept.append(record)
            if present:
                findings.append(_finding(
                    "mandated_statement_kept",
                    f"The guide marks '{row.get('label')}' as wording to keep. It has not been removed. Immigration, Asylum and Nationality Act 2006 section 15 is context for a right-to-work statement only. No person's leave is checked.",
                    "Keep this wording. This tool will not suggest that it is deleted.",
                    _excerpt(phrase),
                    requires_decision=False, requires_hr=False, example_list=False, route_to=None,
                ))
            else:
                findings.append(_finding(
                    "missing_required_information",
                    f"The guide lists '{row.get('label')}' and this draft does not contain it outside an instruction to remove it. The tool has not inserted it.",
                    "A person should add the wording if the guide still requires it.",
                    "",
                    requires_decision=True, requires_hr=False, example_list=False, route_to=None,
                ))
    result["mandated_statements"] = kept
    result["findings"] = _finish_findings(findings)
    result["prompt_count"] = sum(1 for row in result["findings"] if row["requires_decision"])
    result["hr_route_count"] = sum(1 for row in result["findings"] if row["requires_hr"])
    result["finding_count"] = len(result["findings"])
    result["outcome"] = "prompts"
    sources_current = (
        not dates_unreadable
        and not stale
        and not not_yet
        and not result["pins_not_confirmed"]
        and not conflict
        and not question_unreadable
    )
    if cross and cross.get("do_not_rely"):
        sources_current = False
    if grade_compare and grade_compare.get("do_not_rely"):
        sources_current = False
    result["sources_current"] = sources_current
    result["may_be_relied_on"] = sources_current
    result["cue_copied"] = False
    result["statement"] = (
        "Each finding is a prompt. The recruiter accepts or rejects each suggestion "
        "and writes the final wording. Nothing here is an advert."
    )
    _force(result)
    _mask_report(result, text, uk)
    return result


def _directory_person(directory: dict, ref: object) -> dict | None:
    if not isinstance(directory, dict) or directory.get("synthetic") is not True:
        return None
    return _person(directory, ref)


def _reject(review: dict, reason: str) -> dict:
    review["blocked_reason"] = reason
    review["human_approval"] = None
    review["final_wording"] = None
    _force(review)
    return review


def record_suggestion_decision(review: dict, directory: dict, decision: dict) -> dict:
    """Record one recruiter decision on one suggestion hash. This does not publish."""

    if not isinstance(review, dict):
        raise TypeError("review must be an object")
    updated = deepcopy(review)
    if not isinstance(decision, dict):
        return _reject(updated, "decision_unreadable")
    if updated.get("outcome") != "prompts":
        return _reject(updated, updated.get("outcome") or "not_prompts")
    if decision.get("item") != "suggestion":
        return _reject(updated, "item_mismatch")
    if decision.get("decision") not in {"accept", "reject"}:
        return _reject(updated, "decision_unreadable")
    if decision.get("draft_hash") != updated.get("draft_hash"):
        return _reject(updated, "draft_hash_mismatch")
    person = _directory_person(directory, decision.get("approver_ref"))
    if person is None or person.get("role") != "recruiter":
        return _reject(updated, "not_a_recruiter")
    finding = None
    for row in updated.get("findings") or []:
        if row.get("suggestion_id") == decision.get("suggestion_id"):
            finding = row
            break
    if finding is None:
        return _reject(updated, "suggestion_mismatch")
    if finding.get("requires_hr"):
        return _reject(updated, "hr_route_not_a_wording_decision")
    if not finding.get("requires_decision"):
        return _reject(updated, "not_a_suggestion")
    recomputed = _suggestion_hash(finding)
    if decision.get("suggestion_hash") != finding.get("suggestion_hash") or decision.get("suggestion_hash") != recomputed:
        return _reject(updated, "suggestion_hash_mismatch")
    finding["decision"] = decision["decision"]
    finding["decided_by"] = person["ref"]
    finding["decided"] = False
    updated["blocked_reason"] = None
    updated["human_approval"] = None
    updated["final_wording"] = None
    _force(updated)
    return updated


def record_hr_seen(review: dict, directory: dict, seen: dict) -> dict:
    """Record that HR has seen a route. This does not decide the legal question."""

    if not isinstance(review, dict):
        raise TypeError("review must be an object")
    updated = deepcopy(review)
    if not isinstance(seen, dict):
        return _reject(updated, "decision_unreadable")
    if updated.get("outcome") != "prompts":
        return _reject(updated, updated.get("outcome") or "not_prompts")
    if seen.get("item") != "hr-route" or seen.get("decision") != "seen":
        return _reject(updated, "item_mismatch")
    if seen.get("draft_hash") != updated.get("draft_hash"):
        return _reject(updated, "draft_hash_mismatch")
    person = _directory_person(directory, seen.get("approver_ref"))
    if person is None or person.get("role") != "hr_partner":
        return _reject(updated, "not_an_hr_partner")
    finding = None
    for row in updated.get("findings") or []:
        if row.get("suggestion_id") == seen.get("suggestion_id"):
            finding = row
            break
    if finding is None:
        return _reject(updated, "suggestion_mismatch")
    if not finding.get("requires_hr"):
        return _reject(updated, "not_an_hr_route")
    recomputed = _suggestion_hash(finding)
    if seen.get("suggestion_hash") != recomputed:
        return _reject(updated, "suggestion_hash_mismatch")
    finding["hr_seen"] = True
    finding["decided"] = False
    finding["decision"] = None
    updated["blocked_reason"] = None
    updated["human_approval"] = None
    _force(updated)
    return updated


def _needs_boolean(updated: dict, approval: dict) -> str | None:
    guide = updated.get("guide") or {}
    if guide.get("dates_unreadable") or guide.get("stale") or guide.get("not_yet_in_force"):
        if approval.get("guide_seen") is not True:
            return "guide_not_seen"
    if updated.get("pins_not_confirmed"):
        if approval.get("pins_seen") is not True:
            return "pins_not_seen"
    if updated.get("question_date_conflict") or updated.get("question_date_unreadable"):
        if approval.get("question_date_seen") is not True:
            return "question_date_not_seen"
    if updated.get("retention_unreadable") or updated.get("marking_unreadable"):
        if approval.get("labels_unreadable_seen") is not True:
            return "labels_not_seen"
    return None


def record_final_wording(review: dict, directory: dict, approval: dict) -> dict:
    """Store the recruiter's wording when it is bound to this draft and this text.

    Mandated statements that were present stay required. A legal hold and every
    retention label are kept. The agent does not publish the wording.
    """

    if not isinstance(review, dict):
        raise TypeError("review must be an object")
    updated = deepcopy(review)
    if not isinstance(approval, dict):
        return _reject(updated, "decision_unreadable")
    if updated.get("outcome") != "prompts":
        return _reject(updated, updated.get("outcome") or "not_prompts")
    if approval.get("item") != "final-wording" or approval.get("decision") != "record":
        return _reject(updated, "item_mismatch")
    if approval.get("draft_hash") != updated.get("draft_hash"):
        return _reject(updated, "draft_hash_mismatch")
    person = _directory_person(directory, approval.get("approver_ref"))
    if person is None or person.get("role") != "recruiter":
        return _reject(updated, "not_a_recruiter")
    wording = approval.get("wording")
    supplied = approval.get("wording_hash")
    if not isinstance(wording, str) or not wording.strip() or len(wording) > 8000:
        return _reject(updated, "wording_unreadable")
    if not isinstance(supplied, str) or _sha(wording) != supplied:
        return _reject(updated, "wording_hash_mismatch")
    for row in updated.get("findings") or []:
        if row.get("requires_decision") and row.get("decision") not in {"accept", "reject"}:
            return _reject(updated, "suggestions_undecided")
        if row.get("requires_hr") and row.get("hr_seen") is not True:
            return _reject(updated, "hr_route_not_seen")
    gate = _needs_boolean(updated, approval)
    if gate:
        return _reject(updated, gate)
    for statement in updated.get("mandated_statements") or []:
        if statement.get("present") and not affirmed(wording, str(statement.get("phrase") or "")):
            updated["mandated_statements"] = review.get("mandated_statements")
            return _reject(updated, "mandated_statement_removed")
    labels = list(updated.get("retention_labels") or [])
    extra, _bad = retention_labels(None, wording)
    for label in extra:
        if label not in labels:
            labels.append(label)
    updated["retention_labels"] = labels
    updated["legal_hold"] = bool(updated.get("legal_hold")) or legal_hold(None, wording)
    page = content_markings(wording)
    updated["marking"] = higher_marking(([updated["marking"]] if updated.get("marking") else []) + page)
    updated["final_wording"] = wording
    updated["final_wording_hash"] = supplied
    updated["final_wording_written_by"] = "recruiter"
    updated["human_approval"] = {
        "approver_ref": person["ref"],
        "directory_role": "recruiter",
        "item": "final-wording",
        "draft_hash": updated["draft_hash"],
        "wording_hash": supplied,
        "suggestions": [
            {
                "suggestion_id": row.get("suggestion_id"),
                "suggestion_hash": row.get("suggestion_hash"),
                "decision": row.get("decision"),
                "hr_seen": row.get("hr_seen"),
            }
            for row in updated.get("findings") or []
            if row.get("requires_decision") or row.get("requires_hr")
        ],
        "performed_by_agent": False,
    }
    updated["blocked_reason"] = None
    updated["published"] = False
    updated["posted"] = False
    updated["sent"] = False
    _force(updated)
    return updated


def _load(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Review one synthetic job description. Experiment 64.")
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--guide", type=Path, required=True)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--as-of", required=True)
    args = parser.parse_args(argv)
    try:
        result = review_draft(_load(args.request), _load(args.guide), _load(args.directory), args.as_of)
    except (OSError, json.JSONDecodeError, NotSynthetic, ValueError, TypeError) as exc:
        sys.stderr.write(f"{type(exc).__name__}\n")
        return 2
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
