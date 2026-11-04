#!/usr/bin/env python3
"""Assemble a draft EHCP from synthetic advice the reports already tagged.

The same bundle and the same as-of date produce the same JSON. A paragraph
is filed only under the section letter on that paragraph. Section I is not
filled, because a draft must not name a school or a type of school. Nothing
here decides needs, provision, placement, or outcomes. Nothing is sent.

UK identifier spans come from Experiment 08. This module does not copy the
detectors and does not ask for a reversible token map.
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
    from injection import pattern_ids, strip_payload, strings_in
    from prohibited import PROHIBITED_FLAGS, ProhibitedAction
    from sections import (
        ADVICE_LIST_SECTION,
        ADVICE_TYPES,
        EMPTY_IS_GAP,
        PLACEMENT_SECTION,
        SECTION_ORDER,
        SECTIONS,
    )
    from sources import (
        AUTONOMY,
        CATALOGUE_ID,
        DEFAULT_STALE_AFTER_DAYS,
        EXPERIMENT_ID,
        EXPORT_LABEL,
        GATEWAY_CALLER,
        LABEL,
        TWENTY_WEEKS_AS_DAYS,
        source_rows,
    )
else:
    from .injection import pattern_ids, strip_payload, strings_in
    from .prohibited import PROHIBITED_FLAGS, ProhibitedAction
    from .sections import (
        ADVICE_LIST_SECTION,
        ADVICE_TYPES,
        EMPTY_IS_GAP,
        PLACEMENT_SECTION,
        SECTION_ORDER,
        SECTIONS,
    )
    from .sources import (
        AUTONOMY,
        CATALOGUE_ID,
        DEFAULT_STALE_AFTER_DAYS,
        EXPERIMENT_ID,
        EXPORT_LABEL,
        GATEWAY_CALLER,
        LABEL,
        TWENTY_WEEKS_AS_DAYS,
        source_rows,
    )

MAX_REPORTS = 12
MAX_PARAGRAPHS = 40
MAX_CHARS = 4_000
MAX_STATEMENTS = 20
CASE_ID = re.compile(r"^SYN-[A-Z0-9-]{1,24}$")
CHILD_REF = re.compile(r"^Child [A-Z]$")
CASEWORKER_REF = re.compile(r"^CW-[A-Z0-9]{4,12}$")
CLAIM_KEY = re.compile(r"^[a-z][a-z0-9_]{0,40}$")
CLAIM_VALUE = re.compile(r"^[A-Za-z][A-Za-z '-]{0,120}$")
FORBIDDEN_FIELDS = frozenset(
    {
        "child_name",
        "forename",
        "surname",
        "first_name",
        "last_name",
        "date_of_birth",
        "dob",
        "address",
        "postcode",
        "nhs_number",
        "nhs",
        "upn",
        "uln",
        "school_name",
        "parent_name",
        "email",
        "telephone",
        "phone",
        "ni_number",
        "national_insurance",
    }
)

REQUIRED_ADVICE = tuple(
    advice_type for advice_type, meta in ADVICE_TYPES.items() if meta["required"] is True
)

LIMITATIONS = (
    "This draft does not decide needs, provision, placement, or outcomes.",
    "The caseworker authors the final text. This file is not the final plan.",
    "Section I is left blank. Children and Families Act 2014 s.38(5) says a draft must not name a school or other institution, or specify a type.",
    "Regulation 12 and SEND Code paragraph 9.62 set the section letters. Paragraph 9.62 says the format is agreed locally. Check the local authority's own template. Paragraph 9.69 is about shorter-term targets, not the section list.",
    "A missing advice type is a gap in this file. It is not a finding that the local authority failed regulation 6, and regulation 6(4) is not applied.",
    "Twenty weeks is counted here as 140 days. That arithmetic is not in the regulations. Regulation 13(3) exceptions are not applied. A marker is not a finding of breach.",
    "The 90-day window is a freshness flag for this starter. It is not a statutory expiry of advice.",
    "UK identifier handling is Experiment 08. The output is not anonymised. Names written out in words are not detected.",
    "This starter reads the paragraph text supplied in the file. It does not attach appendices for section K.",
    "Experiment 12 inventories documents. It is not called. Experiment 33, where it exists, summarises a case bundle. It is not called.",
    "No model was called. No message was sent.",
)

DIFFERENCES = {
    "experiment_08": (
        "Experiment 08 proposes redaction of UK identifier patterns. "
        "This assembler calls propose and still sets output_is_anonymised to false. "
        "It does not copy the detectors and it does not release text."
    ),
    "experiment_12": (
        "Experiment 12 inventories a document batch and can suggest a purpose. "
        "It does not file SEND advice under sections A to K. This assembler does not call intake."
    ),
    "experiment_33": (
        "Experiment 33 is the case-bundle summariser, catalogue UK09. "
        "A summary narrates a bundle for a reader. This draft does not narrate. "
        "It files advice the report already tagged, withholds section I, and blocks export. "
        "The summariser is not called."
    ),
}


class NotSynthetic(ValueError):
    """The bundle is not a synthetic case. The message does not include the body."""


class AssemblerError(ValueError):
    """The bundle cannot be read. The message does not include the body."""


def _gateway_propose():
    gateway_src = Path(__file__).resolve().parents[2] / "08-uk-pii-redaction-gateway" / "src"
    if not gateway_src.is_dir():
        raise AssemblerError(
            "Experiment 08 is not beside this experiment. The assembler will not invent a redactor."
        )
    inserted = str(gateway_src)
    if inserted not in sys.path:
        sys.path.insert(0, inserted)
    from gateway import propose

    return propose


def _parse_date(value: Any) -> date | None:
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _norm(text: str) -> str:
    return " ".join(text.split())


def _forbidden_field(value: Any) -> bool:
    if isinstance(value, dict):
        for key, item in value.items():
            if str(key).lower() in FORBIDDEN_FIELDS or _forbidden_field(item):
                return True
    elif isinstance(value, list):
        return any(_forbidden_field(item) for item in value)
    return False


def _exp33() -> dict[str, Any]:
    experiments = Path(__file__).resolve().parents[2]
    found = sorted(path.name for path in experiments.glob("33-*") if path.is_dir())
    return {
        "present": bool(found),
        "folders": found,
        "called": False,
        "note": DIFFERENCES["experiment_33"],
    }


def _false_flags() -> dict[str, Any]:
    return {
        "needs_decided": False,
        "provision_decided": False,
        "placement_decided": False,
        "outcomes_decided": False,
        "final_plan_edited": False,
        "sent_to_parents": False,
        "sent_to_school": False,
        "written_to_la_system": False,
        "provision_secured": False,
        "a3_recommended": False,
        "model_called": False,
        "network_called": False,
        "actions_taken": [],
        "output_is_anonymised": False,
        "agent_checked_template": False,
    }


def _refused(reason: str) -> dict[str, Any]:
    result = {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment_id": EXPERIMENT_ID,
        "autonomy": AUTONOMY,
        "refused": True,
        "reason": reason,
        "text_copied": False,
        "exported": False,
        "export_blocked": True,
        "export": None,
    }
    result.update(_false_flags())
    return result


def _section_shell() -> dict[str, dict[str, Any]]:
    shells = {}
    for letter in SECTION_ORDER:
        meta = SECTIONS[letter]
        shells[letter] = {
            "heading": meta["heading"],
            "regulation": meta["regulation"],
            "code_note": meta["code_note"],
            "local_format_must_be_checked": True,
            "lines": [],
            "decided_by_agent": False,
        }
    shells[PLACEMENT_SECTION]["lines_withheld"] = []
    shells[PLACEMENT_SECTION]["left_blank_in_draft"] = True
    shells[PLACEMENT_SECTION]["draft_rule"] = (
        "Children and Families Act 2014 s.38(5). "
        "The quote is not copied. The caseworker leaves section I unnamed in any draft sent to a parent or young person."
    )
    shells[ADVICE_LIST_SECTION]["advice_list"] = []
    shells[ADVICE_LIST_SECTION]["appendices_attached"] = False
    shells["F"]["provision_secured"] = False
    shells["F"]["section_42_note"] = (
        "Section 42 applies where the local authority maintains an EHC plan. "
        "This draft is not a maintained plan."
    )
    shells["E"]["outcomes_decided"] = False
    shells["B"]["needs_decided"] = False
    return shells


def _signoff_gate(signoff: Any, as_of: date, findings: list[dict]) -> tuple[bool, str | None]:
    if signoff is None:
        return False, "no_caseworker_signoff"
    if not isinstance(signoff, dict):
        return False, "signoff_not_an_object"
    for text in strings_in(signoff):
        for pattern in pattern_ids(text):
            findings.append(
                {
                    "pattern": pattern,
                    "where": "signoff",
                    "followed": False,
                }
            )
    if any(row.get("where") == "signoff" for row in findings):
        return False, "signoff_injection"
    if signoff.get("role") != "Caseworker":
        return False, "role"
    ref = signoff.get("caseworker_ref")
    if not isinstance(ref, str) or not CASEWORKER_REF.fullmatch(ref):
        return False, "caseworker_ref"
    for key in (
        "authorises_export",
        "confirms_caseworker_authored_final_text",
        "confirms_la_template_checked",
    ):
        if signoff.get(key) is not True:
            return False, key
    if _parse_date(signoff.get("signed_on")) != as_of:
        return False, "signed_on"
    return True, None


def _identifier_hit(text: str) -> int:
    proposal = _gateway_propose()(
        text,
        caller=GATEWAY_CALLER,
        apply_model_suggestions=False,
        reversible=False,
    )
    return sum(
        1
        for finding in proposal["audit_log"]["findings"]
        if finding.get("applied") and finding.get("method") == "deterministic"
    )


def assemble(
    bundle: dict[str, Any],
    *,
    as_of: str,
    stale_after_days: int = DEFAULT_STALE_AFTER_DAYS,
    signoff: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a draft. Raises NotSynthetic or AssemblerError before copying text."""
    if not isinstance(bundle, dict):
        raise AssemblerError("The bundle is not an object. The body was not copied.")
    if bundle.get("synthetic") is not True:
        raise NotSynthetic("The bundle is not marked synthetic. The text has not been copied.")
    if _forbidden_field(bundle):
        raise NotSynthetic("A field this starter does not read was present. The value was not copied.")
    case_id = bundle.get("case_id")
    if not isinstance(case_id, str) or not CASE_ID.fullmatch(case_id):
        raise NotSynthetic("case_id is not a synthetic id. The value was not copied.")
    child_ref = bundle.get("child_ref")
    if not isinstance(child_ref, str) or not CHILD_REF.fullmatch(child_ref):
        raise NotSynthetic("child_ref is not a synthetic reference. The value was not copied.")
    as_of_date = _parse_date(as_of)
    if as_of_date is None:
        raise AssemblerError("as_of is not a date. Nothing was copied.")
    if not isinstance(stale_after_days, int) or isinstance(stale_after_days, bool):
        raise AssemblerError("stale_after_days is not an integer.")
    if stale_after_days < 0:
        raise AssemblerError("stale_after_days cannot be negative.")

    working = deepcopy(bundle)
    payload_findings: list[dict] = []
    strip_payload(working, payload_findings)

    reports = working.get("reports")
    if not isinstance(reports, list):
        raise AssemblerError("reports is not a list. Nothing was copied.")
    if len(reports) > MAX_REPORTS:
        raise AssemblerError("Too many reports. The limit is 12. Nothing was copied.")

    year_group = working.get("year_group")
    year_known = isinstance(year_group, int) and not isinstance(year_group, bool) and 0 <= year_group <= 14
    request_date = _parse_date(working.get("request_received"))

    sections = _section_shell()
    gaps: list[dict[str, Any]] = []
    unplaced: list[dict[str, Any]] = []
    injection_rows: list[dict[str, Any]] = list(payload_findings)
    stale_reports: list[dict[str, Any]] = []
    dropped_reports: list[str] = []
    claim_rows: list[dict[str, str]] = []
    unsupported_claims: list[dict[str, str]] = []
    identifier_count = 0
    paragraphs_withheld = 0
    gateway_calls = [0]

    def _count_identifiers(text: str) -> int:
        gateway_calls[0] += 1
        return _identifier_hit(text)
    seen_reports: set[str] = set()
    advice_seen: set[str] = set()

    for report in reports:
        if not isinstance(report, dict):
            gaps.append({"id": "report_not_object", "detail": "A report was not an object and was not read."})
            continue
        report_id = report.get("report_id")
        if not isinstance(report_id, str) or not re.fullmatch(r"[A-Za-z0-9-]{1,40}", report_id):
            gaps.append({"id": "report_id_unusable", "detail": "A report id was not usable and the report was not read."})
            continue
        if report_id in seen_reports:
            dropped_reports.append(report_id)
            continue
        seen_reports.add(report_id)

        advice_type = report.get("advice_type")
        if advice_type not in ADVICE_TYPES:
            gaps.append(
                {
                    "id": f"unknown_advice_type:{report_id}",
                    "report_id": report_id,
                    "detail": "The advice type is not in the regulation 6 list used here. It does not satisfy a required category.",
                }
            )
            advice_type_known = None
        else:
            advice_type_known = advice_type
            advice_seen.add(advice_type)

        dated = _parse_date(report.get("dated"))
        date_problem = None
        if dated is None:
            date_problem = "missing"
        elif dated > as_of_date:
            date_problem = "future"
        stale = False
        if dated is not None and date_problem is None:
            stale = (as_of_date - dated).days > stale_after_days
        if date_problem or stale:
            stale_reports.append(
                {
                    "report_id": report_id,
                    "dated": dated.isoformat() if dated else None,
                    "problem": date_problem or "stale",
                    "stale": True,
                }
            )

        role = report.get("author_role")
        if not isinstance(role, str) or len(role) > 80 or pattern_ids(role):
            role_out = "[withheld]"
            if isinstance(role, str) and pattern_ids(role):
                for pattern in pattern_ids(role):
                    injection_rows.append(
                        {"pattern": pattern, "where": "author_role", "report_id": report_id, "followed": False}
                    )
        else:
            role_out = role

        sections[ADVICE_LIST_SECTION]["advice_list"].append(
            {
                "report_id": report_id,
                "advice_type": advice_type_known,
                "author_role": role_out,
                "dated": dated.isoformat() if dated else None,
                "citation": {"report_id": report_id},
                "body_copied_into_section_k": False,
            }
        )

        paragraphs = report.get("paragraphs")
        if not isinstance(paragraphs, list):
            gaps.append({"id": f"no_paragraphs:{report_id}", "report_id": report_id, "detail": "The report had no paragraph list."})
            continue
        if len(paragraphs) > MAX_PARAGRAPHS:
            gaps.append(
                {
                    "id": f"too_many_paragraphs:{report_id}",
                    "report_id": report_id,
                    "detail": "The report has more than 40 paragraphs. None of them were copied.",
                }
            )
            continue

        seen_paragraphs: set[str] = set()
        usable_paragraphs: dict[str, str] = {}
        for paragraph in paragraphs:
            if not isinstance(paragraph, dict):
                continue
            paragraph_id = paragraph.get("paragraph_id")
            text = paragraph.get("text")
            if not isinstance(paragraph_id, str) or not isinstance(text, str):
                continue
            if paragraph_id in seen_paragraphs:
                continue
            seen_paragraphs.add(paragraph_id)
            if len(text) > MAX_CHARS:
                for pattern in pattern_ids(text):
                    injection_rows.append(
                        {
                            "pattern": pattern,
                            "where": "paragraph",
                            "report_id": report_id,
                            "paragraph_id": paragraph_id,
                            "followed": False,
                        }
                    )
                gaps.append(
                    {
                        "id": f"paragraph_too_long:{report_id}:{paragraph_id}",
                        "report_id": report_id,
                        "paragraph_id": paragraph_id,
                        "detail": "The paragraph is over 4,000 characters and was not copied.",
                    }
                )
                paragraphs_withheld += 1
                continue
            found = _count_identifiers(text)
            identifier_count += found
            hits = pattern_ids(text)
            if hits:
                for pattern in hits:
                    injection_rows.append(
                        {
                            "pattern": pattern,
                            "where": "paragraph",
                            "report_id": report_id,
                            "paragraph_id": paragraph_id,
                            "followed": False,
                        }
                    )
            if hits or found:
                paragraphs_withheld += 1
                if found and not hits:
                    gaps.append(
                        {
                            "id": f"identifier_withheld:{report_id}:{paragraph_id}",
                            "report_id": report_id,
                            "paragraph_id": paragraph_id,
                            "detail": "A UK identifier pattern was found. The paragraph was not copied. The output is not anonymised.",
                        }
                    )
                continue
            if date_problem:
                gaps.append(
                    {
                        "id": f"report_date_{date_problem}:{report_id}:{paragraph_id}",
                        "report_id": report_id,
                        "paragraph_id": paragraph_id,
                        "detail": "The report date is missing or after the as-of date. The paragraph was not copied.",
                    }
                )
                continue

            tag = paragraph.get("section_tag")
            letter = tag.strip().upper() if isinstance(tag, str) else ""
            citation = {
                "report_id": report_id,
                "paragraph_id": paragraph_id,
                "advice_type": advice_type_known,
                "dated": dated.isoformat() if dated else None,
            }
            if letter == PLACEMENT_SECTION:
                sections[PLACEMENT_SECTION]["lines_withheld"].append(
                    {
                        "citation": citation,
                        "quote_copied": False,
                        "reason": "s.38(5)",
                    }
                )
            elif letter in SECTIONS and letter != ADVICE_LIST_SECTION:
                sections[letter]["lines"].append(
                    {
                        "quote": text,
                        "citation": citation,
                        "mapping_source": "advice_tag",
                        "decided_by_agent": False,
                        "stale": stale,
                    }
                )
                usable_paragraphs[paragraph_id] = text
            else:
                unplaced.append(
                    {
                        "quote": text,
                        "citation": citation,
                        "reason": "No section tag this assembler recognises. The caseworker places it. A section is not inferred.",
                        "stale": stale,
                    }
                )
                gaps.append(
                    {
                        "id": f"untagged:{report_id}:{paragraph_id}",
                        "report_id": report_id,
                        "paragraph_id": paragraph_id,
                        "detail": "No section tag. The caseworker places this paragraph. A section is not inferred.",
                    }
                )
                usable_paragraphs[paragraph_id] = text

            for claim in paragraph.get("claims") or []:
                if not isinstance(claim, dict):
                    continue
                key = claim.get("key")
                value = claim.get("value")
                if not isinstance(key, str) or not CLAIM_KEY.fullmatch(key):
                    continue
                if not isinstance(value, str) or not CLAIM_VALUE.fullmatch(value):
                    unsupported_claims.append(
                        {"report_id": report_id, "paragraph_id": paragraph_id, "key": key if isinstance(key, str) else ""}
                    )
                    continue
                if _norm(value) not in _norm(text):
                    unsupported_claims.append(
                        {"report_id": report_id, "paragraph_id": paragraph_id, "key": key}
                    )
                    continue
                if paragraph_id not in usable_paragraphs and letter == PLACEMENT_SECTION:
                    continue
                if paragraph_id not in usable_paragraphs:
                    continue
                claim_rows.append(
                    {
                        "key": key,
                        "value": value,
                        "report_id": report_id,
                        "paragraph_id": paragraph_id,
                    }
                )

    for advice_type in REQUIRED_ADVICE:
        if advice_type not in advice_seen:
            meta = ADVICE_TYPES[advice_type]
            gaps.append(
                {
                    "id": f"missing_advice_{advice_type}",
                    "advice_type": advice_type,
                    "regulation": f"SI 2014/1530 reg. {meta['regulation']}",
                    "detail": "No report of this advice type was in the file. This is a gap. It is not a finding that the duty was breached.",
                }
            )
    if not year_known:
        gaps.append(
            {
                "id": "year_group_not_supplied",
                "detail": "Regulation 6(1)(g) and regulation 12(3) were not checked because year_group was not an integer from 0 to 14.",
            }
        )
    elif year_group >= 9 and "preparation_for_adulthood" not in advice_seen:
        gaps.append(
            {
                "id": "missing_advice_preparation_for_adulthood",
                "advice_type": "preparation_for_adulthood",
                "regulation": "SI 2014/1530 reg. 6(1)(g) and reg. 12(3)",
                "detail": "year_group is 9 or above and no preparation-for-adulthood report was supplied. This starter does not write that provision.",
            }
        )
    requested = working.get("requested_further_advice")
    if isinstance(requested, list):
        for item in requested:
            if isinstance(item, str) and item in ADVICE_TYPES and item not in advice_seen:
                gaps.append(
                    {
                        "id": f"requested_advice_missing:{item}",
                        "advice_type": item,
                        "regulation": "SI 2014/1530 reg. 6(1)(h)",
                        "detail": "The bundle lists this as requested. Regulation 6(1)(h) is for a request the local authority accepts as reasonable. This starter does not decide that.",
                    }
                )
    for letter in EMPTY_IS_GAP:
        if not sections[letter]["lines"]:
            detail = "No tagged advice was placed under this heading. The caseworker authors it."
            if letter == "B":
                detail = (
                    "No tagged advice was placed under section B. "
                    "This is a gap in the draft. It is not a finding that there are no special educational needs."
                )
            gaps.append({"id": f"empty_section_{letter}", "section": letter, "detail": detail})
    if not sections[ADVICE_LIST_SECTION]["advice_list"]:
        gaps.append(
            {
                "id": "empty_section_K",
                "section": "K",
                "detail": "No advice report was listed. Regulation 12(4) expects the advice in appendices. None are attached.",
            }
        )

    conflicts: list[dict[str, Any]] = []
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in claim_rows:
        grouped.setdefault(row["key"], []).append(row)
    for key in sorted(grouped):
        values = []
        seen_values: set[str] = set()
        for row in grouped[key]:
            folded = _norm(row["value"]).casefold()
            if folded in seen_values:
                continue
            seen_values.add(folded)
            values.append(
                {
                    "value": row["value"],
                    "report_id": row["report_id"],
                    "paragraph_id": row["paragraph_id"],
                }
            )
        if len(values) > 1:
            conflicts.append(
                {
                    "id": f"conflict:{key}",
                    "key": key,
                    "values": values,
                    "resolved": False,
                    "chosen_value": None,
                }
            )

    supported: list[dict[str, Any]] = []
    unsupported: list[dict[str, Any]] = []
    statements = working.get("candidate_statements")
    if isinstance(statements, list):
        if len(statements) > MAX_STATEMENTS:
            gaps.append(
                {
                    "id": "too_many_candidate_statements",
                    "detail": "More than 20 candidate statements were supplied. None were copied.",
                }
            )
            statements = []
        paragraph_index: dict[tuple[str, str], str] = {}
        for letter in SECTION_ORDER:
            for line in sections[letter]["lines"]:
                citation = line["citation"]
                paragraph_index[(citation["report_id"], citation["paragraph_id"])] = line["quote"]
        for line in unplaced:
            citation = line["citation"]
            paragraph_index[(citation["report_id"], citation["paragraph_id"])] = line["quote"]
        for statement in statements:
            if not isinstance(statement, dict):
                continue
            statement_id = statement.get("statement_id")
            if not isinstance(statement_id, str):
                statement_id = "unlabelled"
            text = statement.get("text")
            citation = statement.get("citation") if isinstance(statement.get("citation"), dict) else {}
            report_id = citation.get("report_id")
            paragraph_id = citation.get("paragraph_id")
            if pattern_ids(text) if isinstance(text, str) else False:
                for pattern in pattern_ids(text):
                    injection_rows.append(
                        {
                            "pattern": pattern,
                            "where": "candidate_statement",
                            "statement_id": statement_id,
                            "followed": False,
                        }
                    )
                unsupported.append(
                    {"statement_id": statement_id, "reason": "instruction_in_statement", "copied": False}
                )
                continue
            if not isinstance(text, str) or not isinstance(report_id, str) or not isinstance(paragraph_id, str):
                unsupported.append({"statement_id": statement_id, "reason": "missing_citation", "copied": False})
                continue
            source = paragraph_index.get((report_id, paragraph_id))
            if source is None:
                unsupported.append({"statement_id": statement_id, "reason": "unknown_or_withheld_paragraph", "copied": False})
                continue
            if _norm(text) not in _norm(source):
                unsupported.append({"statement_id": statement_id, "reason": "not_in_cited_paragraph", "copied": False})
                continue
            supported.append(
                {
                    "statement_id": statement_id,
                    "citation": {"report_id": report_id, "paragraph_id": paragraph_id},
                    "matched": True,
                    "copied_into_sections": False,
                }
            )

    if request_date is None:
        days_since = None
        marker = False
        if working.get("request_received") is not None:
            gaps.append(
                {
                    "id": "request_received_unusable",
                    "detail": "request_received was not a date. Regulation 13(2) was not marked.",
                }
            )
    else:
        days_since = (as_of_date - request_date).days
        if days_since < 0:
            days_since = None
            marker = False
            gaps.append(
                {
                    "id": "request_received_after_as_of",
                    "detail": "The request date is after the as-of date. Regulation 13(2) was not marked.",
                }
            )
        else:
            marker = days_since >= TWENTY_WEEKS_AS_DAYS

    timescale = {
        "request_received": request_date.isoformat() if request_date and days_since is not None else None,
        "days_since_request": days_since,
        "twenty_weeks_as_days": TWENTY_WEEKS_AS_DAYS,
        "twenty_week_marker_passed": marker,
        "breach_found": False,
        "exceptions_applied": False,
        "exceptions_note": (
            "Regulation 13(3) says the local authority need not comply with regulation 13(2) "
            "if it is impractical for a reason in regulation 10(4)(a) to (d). "
            "This starter does not apply those reasons and does not find a breach."
        ),
        "draft_consultation_started": False,
        "regulation_13_1_note": (
            "Regulation 13(1) gives at least 15 days to make representations on a draft that has been sent. "
            "This starter does not send a draft."
        ),
        "counting_rule": (
            "This starter counts 20 weeks as 140 days from request_received. "
            "The regulations do not define that arithmetic. It does not know about section 24."
        ),
    }

    source_list = source_rows(as_of_date, stale_after_days)
    source_stale = any(row["stale"] for row in source_list)
    advice_stale = any(row["problem"] == "stale" for row in stale_reports)
    injection_detected = bool(injection_rows)
    do_not_rely = bool(
        source_stale or advice_stale or injection_detected or paragraphs_withheld or any(
            row["problem"] != "stale" for row in stale_reports
        )
    )

    allowed, block_reason = _signoff_gate(signoff, as_of_date, injection_rows)
    # A sign-off note can add findings after injection_detected was computed.
    if any(row.get("where") == "signoff" for row in injection_rows):
        injection_detected = True
        do_not_rely = True
        allowed = False
        block_reason = "signoff_injection"

    placed = sum(len(sections[letter]["lines"]) for letter in SECTION_ORDER)
    result: dict[str, Any] = {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment_id": EXPERIMENT_ID,
        "autonomy": AUTONOMY,
        "case_id": case_id,
        "child_ref": child_ref,
        "as_of": as_of_date.isoformat(),
        "synthetic": True,
        "refused": False,
        "text_copied": bool(placed or unplaced),
        "placed_quotes": placed,
        "duplicate_reports_dropped": dropped_reports,
        "sections": sections,
        "unplaced": unplaced,
        "gaps": gaps,
        "conflicts": conflicts,
        "unsupported_statements": unsupported,
        "supported_statements": supported,
        "unsupported_claims": unsupported_claims,
        "stale_reports": stale_reports,
        "timescale": timescale,
        "prompt_injection": {
            "detected": injection_detected,
            "followed": False,
            "findings": injection_rows,
        },
        "prohibited_actions": {"taken": False},
        "pii_gateway": {
            "called": gateway_calls[0] > 0,
            "caller": GATEWAY_CALLER,
            "experiment": "08-uk-pii-redaction-gateway",
            "output_is_anonymised": False,
            "agent_may_release": False,
            "finding_count": identifier_count,
            "paragraphs_withheld": paragraphs_withheld,
        },
        "do_not_rely": do_not_rely,
        "exported": False,
        "export_blocked": True,
        "export_block_reason": block_reason,
        "export": None,
        "caseworker_confirmed_la_template": False,
        "sources": source_list,
        "differences": {
            "experiment_08": DIFFERENCES["experiment_08"],
            "experiment_12": DIFFERENCES["experiment_12"],
            "experiment_33": _exp33(),
        },
        "limitations": list(LIMITATIONS),
    }
    result.update(_false_flags())
    if allowed and isinstance(signoff, dict):
        result["exported"] = True
        result["export_blocked"] = False
        result["export_block_reason"] = None
        result["caseworker_confirmed_la_template"] = True
        result["export"] = {
            "label": EXPORT_LABEL,
            "caseworker_ref": signoff["caseworker_ref"],
            "signed_on": as_of_date.isoformat(),
            "sections": deepcopy(sections),
            "final_plan_included": False,
            "sent_to_parents": False,
            "sent_to_school": False,
            "written_to_la_system": False,
        }
    # The sign-off object is not stored. A final_text field on it is not copied.
    result["signoff_stored"] = False
    return result


def evaluate(
    bundle: dict[str, Any],
    *,
    as_of: str,
    stale_after_days: int = DEFAULT_STALE_AFTER_DAYS,
    signoff: dict[str, Any] | None = None,
) -> dict[str, Any]:
    try:
        return assemble(
            bundle,
            as_of=as_of,
            stale_after_days=stale_after_days,
            signoff=signoff,
        )
    except NotSynthetic as exc:
        return _refused(str(exc))


def _refuse_flag(argv: list[str]) -> int | None:
    for flag, function in PROHIBITED_FLAGS.items():
        if flag in argv:
            try:
                function()
            except ProhibitedAction as exc:
                print(str(exc), file=sys.stderr)
                return 2
    return None


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    refused = _refuse_flag(argv)
    if refused is not None:
        return refused
    export_requested = "--export" in argv
    argv = [item for item in argv if item != "--export"]
    parser = argparse.ArgumentParser(description="Assemble a draft EHCP from synthetic advice.")
    parser.add_argument("--bundle", required=True)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--stale-after-days", type=int, default=DEFAULT_STALE_AFTER_DAYS)
    parser.add_argument("--signoff", default="")
    parser.add_argument("--output", default="")
    args = parser.parse_args(argv)
    try:
        bundle = json.loads(Path(args.bundle).read_text(encoding="utf-8"))
        signoff = None
        if export_requested and args.signoff:
            signoff = json.loads(Path(args.signoff).read_text(encoding="utf-8"))
        draft = evaluate(
            bundle,
            as_of=args.as_of,
            stale_after_days=args.stale_after_days,
            signoff=signoff,
        )
    except (OSError, json.JSONDecodeError, AssemblerError, NotSynthetic) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    if draft.get("refused"):
        print(draft["reason"], file=sys.stderr)
        return 1
    if export_requested and draft["export_blocked"]:
        print("Export blocked.", file=sys.stderr)
        return 2
    text = json.dumps(draft, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
