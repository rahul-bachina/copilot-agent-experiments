"""Draft a cited credit memo from one synthetic pack.

Every stated figure and claim is a copy of named lines, with a pinpoint
citation. A closed-list section with no usable current paragraph is
"not stated". Nothing is inferred.

Autonomy is A1. draft_memo() does not approve or decline credit, set a limit,
contact the customer or a bureau, post to a core banking or CRM system, or
file a SAR. The credit officer owns the recommendation and every approval.
The MLRO decides any SAR.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from src.citations import (  # type: ignore
        check_fact,
        document_block_reason,
        empty_verdict_counts,
        index_documents,
        normalise,
    )
    from src.cross_source import compare_pack
    from src.injection import injection_codes, prohibited_codes, scan_documents, strip_prohibited
    from src.intake_call import inventory
    from src.sources import DEFAULT_STALE_AFTER_DAYS, pin_rows, regulatory_notes
    from src.themes import equality_themes, financial_crime_narrative, special_category_themes
else:
    from .citations import (
        check_fact,
        document_block_reason,
        empty_verdict_counts,
        index_documents,
        normalise,
    )
    from .cross_source import compare_pack
    from .injection import injection_codes, prohibited_codes, scan_documents, strip_prohibited
    from .intake_call import inventory
    from .sources import DEFAULT_STALE_AFTER_DAYS, pin_rows, regulatory_notes
    from .themes import equality_themes, financial_crime_narrative, special_category_themes

LABEL = "DRAFT FOR THE CREDIT OFFICER. NOT A CREDIT DECISION AND NOT A LIMIT."
CATALOGUE_ID = "B009"
EXPERIMENT_ID = "exp-39-credit-memo-drafting"
NOT_STATED = "not stated"
CREDIT_OFFICER = "Credit officer"
FIELDS = (
    "company_profile",
    "financial_highlights",
    "limit_request",
    "security",
    "covenants",
    "risk_flags",
    "information_gaps",
)
PRODUCT_LABELS = frozenset({"commercial_non_consumer", "retail", "sme_consumer_facing"})
# Several lines in these sections are a list, not two competing values.
MULTI_VALUE_FIELDS = frozenset({"security", "covenants", "risk_flags", "information_gaps"})
FIELD_INDEX = {name: index for index, name in enumerate(FIELDS)}

DIFFERENCE_FROM_12 = (
    "Experiment 12 inventories text files. It has no credit purpose. This experiment "
    "calls intake() with no purpose, so nothing is routed, and then copies lines from "
    "documents whose file was read. It does not confirm the files and it does not decide credit."
)
DIFFERENCE_FROM_16 = (
    "Experiment 16 drafts a Money Laundering Regulations checklist and can record that "
    "a KYC reviewer confirmed documents. This experiment mirrors the checklist shape: "
    "a status, sufficient false, and decides_the_credit false. It does not import "
    "Experiment 16. That package lives under the module name src. It does not confirm "
    "identity, apply regulation 28, or onboard anyone."
)
DIFFERENCE_FROM_36 = (
    "Experiment 36 classifies the same fact across sources. This experiment calls "
    "compare() when the pack supplies a comparisons object. It does not choose a "
    "source. The comparison counts stay on cross_source and are not added to the "
    "memo's stated-fact count."
)
DIFFERENCE_FROM_37 = (
    "Experiment 37 copies a contiguous span and checks a pinpoint for a broker "
    "submission. This experiment uses that same rule for credit-memo sections. It "
    "does not import Experiment 37, because that package lives under the module name "
    "src. It does not decide coverage or price, and it does not decide credit."
)

LIMITATIONS = (
    "The checker is extractive. A true paraphrase fails. A copied line can still omit the line that changes the credit picture.",
    "The section list is closed. A point outside those seven sections is not extracted.",
    "A missing section is the words not stated. The value is not inferred.",
    "Experiment 16 is not imported. The checklist does not decide that a Money Laundering Regulations duty is met.",
    "Experiment 36 is called only when the pack supplies comparisons. No comparison is not a finding that the sources agree.",
    "Comparison counts are not memo facts. They are not added to stated_fact_count.",
    "The 90-day window is a freshness flag. It is not a statutory period.",
    "Article 22 was shown as omitted on 6 November 2026. This draft does not certify meaningful human involvement under Article 22A.",
    "No Article 9 condition is applied. Schedule 1 to the Data Protection Act 2018 was not opened.",
    "Schedule 3 to the Equality Act 2010 was not opened. No services exception is applied.",
    "PRIN 3 was not opened. The glossary definition of a retail customer was not opened. PRIN 2A.2 did not return rule text.",
    "Section 333A of the Proceeds of Crime Act 2002 was not opened. No customer text is produced.",
    "Regulation 28 was not re-opened. JMLSG guidance was not opened.",
    "Microsoft Foundry and Microsoft Fabric product pages were not opened. Neither is called.",
    "No model was called.",
)


class MemoForbidden(Exception):
    """A prohibited credit action. The draft is not a decision."""


class NotSynthetic(ValueError):
    """The pack was not marked synthetic. The message does not include the body."""


def approve_credit(*_args: Any, **_kwargs: Any) -> None:
    raise MemoForbidden("The agent does not approve credit.")


def decline_credit(*_args: Any, **_kwargs: Any) -> None:
    raise MemoForbidden("The agent does not decline credit.")


def set_limit(*_args: Any, **_kwargs: Any) -> None:
    raise MemoForbidden("The agent does not set a limit.")


def contact_customer(*_args: Any, **_kwargs: Any) -> None:
    raise MemoForbidden("The agent does not contact the customer.")


def contact_bureau(*_args: Any, **_kwargs: Any) -> None:
    raise MemoForbidden("The agent does not contact a bureau.")


def post_core_banking(*_args: Any, **_kwargs: Any) -> None:
    raise MemoForbidden("The agent does not post to a core banking system.")


def post_crm(*_args: Any, **_kwargs: Any) -> None:
    raise MemoForbidden("The agent does not post to a CRM system.")


def file_sar(*_args: Any, **_kwargs: Any) -> None:
    raise MemoForbidden("The agent does not file a SAR. The MLRO decides.")


def recommend_autonomy_a3(*_args: Any, **_kwargs: Any) -> None:
    raise MemoForbidden("The agent does not recommend autonomy A3.")


def release_evaluation(*_args: Any, **_kwargs: Any) -> None:
    raise MemoForbidden("The agent does not release an evaluation as a decision.")


def _parse_day(value: str, label: str) -> date:
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} is not a calendar date.") from exc


def _product_label(value: Any) -> str:
    if value is None or value == "":
        return "not_stated"
    if isinstance(value, str) and value in PRODUCT_LABELS:
        return value
    return "unrecognised"


def _paragraph_lines(paragraph: dict[str, Any]) -> list[dict[str, Any]] | None:
    rows = paragraph.get("lines")
    if not isinstance(rows, list) or not rows:
        return None
    parsed: list[tuple[int, str]] = []
    for row in rows:
        if not isinstance(row, dict):
            return None
        number = row.get("line")
        if isinstance(number, bool) or not isinstance(number, int):
            return None
        parsed.append((number, str(row.get("text") or "")))
    parsed.sort(key=lambda item: item[0])
    numbers = [number for number, _text in parsed]
    if numbers != list(range(numbers[0], numbers[-1] + 1)):
        return None
    return [{"line": number, "text": text} for number, text in parsed]


def _decision_flags() -> dict[str, Any]:
    return {
        "credit_decision": None,
        "recommendation": None,
        "limit_set": None,
        "limit_requested_chosen": None,
        "customer_contacted": False,
        "bureau_contacted": False,
        "core_banking_posted": False,
        "crm_posted": False,
        "sar_filed": False,
        "suspicion_decided": False,
        "discrimination_found": False,
        "consumer_duty_met": None,
        "reading_acknowledged": False,
        "draft_approved_for_use": False,
        "summary_accepted_as_decision": False,
        "solely_automated_decision": False,
        "product_label_decided_by_agent": False,
        "model_called": False,
        "network_called": False,
        "foundry_called": False,
        "fabric_called": False,
        "lakehouse_written": False,
        "a3_recommended": False,
        "actions_taken": [],
        "output_is_anonymised": False,
        "experiment_16_imported": False,
        "experiment_37_imported": False,
        "evaluation_released": False,
    }


def _extract(
    documents: list[dict[str, Any]],
    as_of: str,
    stale_after_days: int,
    intake_files: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    pending: list[dict[str, Any]] = []
    not_used: list[dict[str, Any]] = []
    for document in documents:
        reason = document_block_reason(document, as_of, stale_after_days, intake_files)
        document_id = str(document.get("document_id") or "")
        if reason is not None:
            fields = []
            for page in document.get("pages") or []:
                for paragraph in page.get("paragraphs") or []:
                    field = paragraph.get("fact_key")
                    if field in FIELD_INDEX and field not in fields:
                        fields.append(field)
            if not fields:
                fields = [None]
            for field in fields:
                row = {
                    "document_id": document_id,
                    "file_id": document.get("file_id"),
                    "reason": reason,
                    "quoted": False,
                }
                if field is not None:
                    row["field"] = field
                not_used.append(row)
            continue
        for page in document.get("pages") or []:
            page_no = page.get("page")
            if isinstance(page_no, bool) or not isinstance(page_no, int):
                continue
            for paragraph in page.get("paragraphs") or []:
                field = paragraph.get("fact_key")
                if field not in FIELD_INDEX:
                    continue
                lines = _paragraph_lines(paragraph)
                if lines is None:
                    continue
                text = " ".join(row["text"].strip() for row in lines if row["text"].strip())
                if not text:
                    continue
                if prohibited_codes(text) or injection_codes(text):
                    not_used.append(
                        {
                            "document_id": document_id,
                            "file_id": document.get("file_id"),
                            "reason": "instruction_or_prohibited_wording",
                            "quoted": False,
                            "field": field,
                        }
                    )
                    continue
                pending.append(
                    {
                        "field": field,
                        "text": text,
                        "citation": {
                            "document_id": document_id,
                            "page": page_no,
                            "paragraph": paragraph.get("paragraph"),
                            "line_start": lines[0]["line"],
                            "line_end": lines[-1]["line"],
                        },
                    }
                )
    pending.sort(
        key=lambda item: (
            FIELD_INDEX[item["field"]],
            item["citation"]["document_id"],
            item["citation"]["page"],
            item["citation"]["paragraph"],
            item["citation"]["line_start"],
        )
    )
    rows = []
    for index, item in enumerate(pending, start=1):
        rows.append({"fact_id": f"F{index}", **item})
    return rows, not_used


def _gaps(facts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    present = {fact["field"] for fact in facts}
    gaps = []
    for index, field in enumerate(FIELDS, start=1):
        if field in present:
            continue
        gaps.append(
            {
                "gap_id": f"G{index}",
                "field": field,
                "value": NOT_STATED,
                "status": "not_stated",
                "citation": None,
                "verdict": "not_stated",
                "inferred": False,
            }
        )
    return gaps


def _contradictions(facts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for fact in facts:
        grouped.setdefault(fact["field"], []).append(fact)
    rows = []
    for field in FIELDS:
        items = grouped.get(field, [])
        distinct = []
        for fact in items:
            folded = normalise(fact["text"])
            if folded not in distinct:
                distinct.append(folded)
        if field in MULTI_VALUE_FIELDS or len(distinct) < 2:
            continue
        rows.append(
            {
                "field": field,
                "fact_ids": [fact["fact_id"] for fact in items],
                "chosen_value": None,
                "resolved_by_agent": False,
            }
        )
    return rows


def _sections(facts: list[dict[str, Any]], gaps: list[dict[str, Any]]) -> dict[str, Any]:
    by_field: dict[str, list[dict[str, Any]]] = {field: [] for field in FIELDS}
    for fact in facts:
        by_field[fact["field"]].append(
            {
                "fact_id": fact["fact_id"],
                "value": fact["text"],
                "status": "stated",
                "citation": fact["citation"],
                "verdict": fact["verdict"],
                "other_failures": fact["other_failures"],
                "inferred": False,
            }
        )
    gap_by_field = {gap["field"]: gap for gap in gaps}
    sections = {}
    for field in FIELDS:
        if by_field[field]:
            sections[field] = {"status": "stated", "items": by_field[field]}
        else:
            gap = gap_by_field[field]
            sections[field] = {
                "status": "not_stated",
                "items": [
                    {
                        "gap_id": gap["gap_id"],
                        "value": NOT_STATED,
                        "status": "not_stated",
                        "citation": None,
                        "verdict": "not_stated",
                        "inferred": False,
                    }
                ],
            }
    return sections


def _summary(
    facts: list[dict[str, Any]],
    gaps: list[dict[str, Any]],
    not_used: list[dict[str, Any]],
    contradictions: list[dict[str, Any]],
) -> dict[str, Any]:
    counts = empty_verdict_counts()
    for fact in facts:
        counts[fact["verdict"]] += 1
    stated = len(facts)
    if sum(counts.values()) != stated:
        raise RuntimeError("Verdict totals do not match the stated fact count.")
    return {
        "stated_fact_count": stated,
        "verdict_total": stated,
        "verdicts": counts,
        "failure_count": stated - counts["supported"],
        "gap_count": len(gaps),
        "contradiction_count": len(contradictions),
        "not_used_count": len(not_used),
        "section_count": len(FIELDS),
        "each_stated_fact_has_one_verdict": True,
        "other_failures_are_not_in_the_totals": True,
        "gaps_are_not_verdicts": True,
        "section_count_is_not_added_to_stated_fact_count": True,
        "cross_source_counts_are_not_added": True,
    }


def _checklist(facts: list[dict[str, Any]], not_used: list[dict[str, Any]]) -> dict[str, Any]:
    items = []
    for field in FIELDS:
        matched = [fact for fact in facts if fact["field"] == field]
        stale_only = [
            row
            for row in not_used
            if row.get("field") == field and row.get("reason") in {"stale", "intake_date_not_current"}
        ]
        if matched:
            status = "evidenced"
        elif stale_only:
            status = "evidenced_but_stale"
        else:
            status = "missing"
        items.append(
            {
                "id": field,
                "section": field,
                "requirement_words": (
                    "A current cited line for this section, or the words not stated. "
                    "The status does not decide credit and does not decide a regulatory duty."
                ),
                "status": status,
                "sufficient": False,
                "decides_the_credit": False,
                "decides_the_duty": False,
                "fact_ids": [fact["fact_id"] for fact in matched],
            }
        )
    return {
        "items": items,
        "sufficient": False,
        "decides_the_credit": False,
        "pattern": "Experiment 16 checklist shape, mirrored locally. Experiment 16 is not imported.",
    }


def _do_not_rely(
    *,
    gaps: list[dict[str, Any]],
    contradictions: list[dict[str, Any]],
    facts: list[dict[str, Any]],
    injection_detected: bool,
    intake: dict[str, Any],
    not_used: list[dict[str, Any]],
    pins_stale: bool,
    product_label: str,
    label_differs: bool,
    equality: dict[str, Any],
    special: dict[str, Any],
    crime: dict[str, Any],
    cross: dict[str, Any],
) -> list[str]:
    reasons = []
    if gaps:
        reasons.append("missing_information")
    if contradictions:
        reasons.append("contradiction")
    if any(fact["verdict"] != "supported" for fact in facts):
        reasons.append("stated_fact_failed")
    if injection_detected or intake["prompt_injection_detected"]:
        reasons.append("injection_detected")
    if any(row["reason"] == "withheld_identifier" for row in not_used):
        reasons.append("withheld_identifier")
    if intake["any_document_not_current"] or any(
        row["reason"]
        in {
            "intake_date_not_current",
            "stale",
            "superseded",
            "status_not_current",
            "intake_not_read",
            "not_in_intake",
        }
        for row in not_used
    ):
        reasons.append("intake_or_document_not_current")
    if intake["catalogue_stale"] or intake["gateway_rules_stale"]:
        reasons.append("intake_catalogue_or_rules_stale")
    if pins_stale:
        reasons.append("source_pin_stale")
    if product_label == "unrecognised":
        reasons.append("product_label_unrecognised")
    if product_label == "not_stated":
        reasons.append("product_label_not_stated")
    if label_differs:
        reasons.append("caller_label_differs_from_cited_name")
    if equality["themes"]:
        reasons.append("equality_theme")
    if special["themes"]:
        reasons.append("special_category_theme")
    if crime["narrative_for_human_review"]:
        reasons.append("financial_crime_narrative")
    if cross["material_fact_keys"]:
        reasons.append("material_cross_source_discrepancy")
    return reasons


def _force(draft: dict[str, Any]) -> dict[str, Any]:
    draft.update(_decision_flags())
    draft["reading_acknowledged"] = False
    draft["checklist"]["sufficient"] = False
    draft["checklist"]["decides_the_credit"] = False
    for item in draft["checklist"]["items"]:
        item["sufficient"] = False
        item["decides_the_credit"] = False
        item["decides_the_duty"] = False
    draft["equality"]["discrimination_found"] = False
    draft["special_category"]["article_9_condition_applied"] = False
    draft["special_category"]["used_as_a_credit_factor"] = False
    draft["financial_crime"]["suspicion_decided"] = False
    draft["financial_crime"]["sar_filed"] = False
    draft["financial_crime"]["authorised_disclosure_made"] = False
    draft["financial_crime"]["customer_text_produced"] = False
    draft["cross_source"]["agent_chose_source"] = False
    draft["cross_source"]["register_queried"] = False
    draft["prompt_injection"]["followed"] = False
    for note in draft["regulatory_notes"]:
        note["applied_as_a_finding"] = False
    return draft


def draft_memo(
    pack: dict[str, Any],
    *,
    as_of: str,
    stale_after_days: int = DEFAULT_STALE_AFTER_DAYS,
    proposed_facts: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    if not isinstance(pack, dict):
        raise TypeError("pack must be an object")
    if pack.get("synthetic") is not True:
        raise NotSynthetic("pack is not marked synthetic")
    as_of_date = _parse_day(as_of, "as_of")
    if type(stale_after_days) is not int or stale_after_days < 0:
        raise ValueError("stale_after_days must be a non-negative integer")

    working, stripped = strip_prohibited(pack)
    files = working.get("files")
    documents_in = working.get("documents")
    if not isinstance(files, list) or not files:
        raise ValueError("pack has no files")
    if not isinstance(documents_in, list) or not documents_in:
        raise ValueError("pack has no documents")

    pack_id = working.get("pack_id", "unspecified")
    if not isinstance(pack_id, str) or not pack_id:
        pack_id = "unspecified"
    caller_label = working.get("applicant_name")
    if not isinstance(caller_label, str):
        caller_label = None

    intake = inventory(
        files,
        batch_id=pack_id,
        as_of=as_of_date,
        stale_after_days=stale_after_days,
    )
    intake_files = {row["file_id"]: row for row in intake["files"]}
    documents = index_documents(documents_in)
    document_list = list(documents.values())
    injection = scan_documents(document_list)
    if intake["prompt_injection_detected"]:
        injection = {
            "detected": True,
            "followed": False,
            "signals": injection["signals"]
            + [
                {
                    "document_id": None,
                    "code": "intake_file_signal",
                    "hidden_in": "experiment_12",
                    "followed": False,
                }
            ],
        }

    product_label = _product_label(working.get("product_label"))
    sources, pins_stale = pin_rows(as_of, stale_after_days)
    comparisons = working.get("comparisons")
    cross = (
        compare_pack(comparisons, as_of=as_of, stale_after_days=stale_after_days)
        if proposed_facts is None
        else compare_pack(None, as_of=as_of, stale_after_days=stale_after_days)
    )

    if proposed_facts is None:
        raw_facts, not_used = _extract(document_list, as_of, stale_after_days, intake_files)
    else:
        raw_facts = []
        not_used = []
        for index, item in enumerate(proposed_facts, start=1):
            if not isinstance(item, dict):
                raise ValueError("proposed facts must be objects")
            raw_facts.append(
                {
                    "fact_id": item.get("fact_id") or f"P{index}",
                    "field": item.get("field"),
                    "text": str(item.get("text") or ""),
                    "citation": item.get("citation"),
                }
            )

    checked = [
        check_fact(fact, documents, as_of, stale_after_days, intake_files) for fact in raw_facts
    ]
    gaps = _gaps(checked) if proposed_facts is None else []
    contradictions = _contradictions(checked) if proposed_facts is None else []
    cited_names = [
        normalise(fact["text"])
        for fact in checked
        if fact["field"] == "company_profile" and fact["verdict"] == "supported"
    ]
    label_differs = bool(
        caller_label
        and cited_names
        and all(normalise(caller_label) not in name for name in cited_names)
    )
    shown_text = [fact["text"] for fact in checked]
    risk_text = [fact["text"] for fact in checked if fact["field"] == "risk_flags"]
    equality = equality_themes(shown_text)
    special = special_category_themes(shown_text)
    crime = financial_crime_narrative(risk_text)
    reasons = _do_not_rely(
        gaps=gaps,
        contradictions=contradictions,
        facts=checked,
        injection_detected=injection["detected"],
        intake=intake,
        not_used=not_used,
        pins_stale=pins_stale,
        product_label=product_label,
        label_differs=label_differs,
        equality=equality,
        special=special,
        crime=crime,
        cross=cross,
    )
    summary = _summary(checked, gaps, not_used, contradictions)
    checker_passed = summary["failure_count"] == 0 and all(
        fact["verdict"] == "supported" for fact in checked
    )
    draft = {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment_id": EXPERIMENT_ID,
        "autonomy": "A1",
        "pack_id": pack_id,
        "applicant_name_as_labelled": caller_label,
        "applicant_label_is_not_a_cited_fact": True,
        "caller_label_differs_from_cited_name": label_differs,
        "applicant_is_fictional": True,
        "product_label": product_label,
        "as_of": as_of,
        "stale_after_days": stale_after_days,
        "intake": intake,
        "sections": _sections(checked, gaps) if proposed_facts is None else None,
        "facts": checked,
        "gaps": gaps,
        "contradictions": contradictions,
        "not_used": not_used,
        "summary": summary,
        "checklist": _checklist(checked, not_used) if proposed_facts is None else _checklist(checked, []),
        "cross_source": cross,
        "equality": equality,
        "special_category": special,
        "financial_crime": crime,
        "regulatory_notes": regulatory_notes(product_label),
        "sources": sources,
        "prompt_injection": injection,
        "prohibited_payload_keys": stripped,
        "checker_passed": checker_passed,
        "do_not_rely": bool(reasons),
        "do_not_rely_reasons": reasons,
        "differences": {
            "experiment_12": DIFFERENCE_FROM_12,
            "experiment_16": DIFFERENCE_FROM_16,
            "experiment_36": DIFFERENCE_FROM_36,
            "experiment_37": DIFFERENCE_FROM_37,
        },
        "human_approval": {
            "credit_officer_reviews_every_cited_fact": True,
            "credit_officer_owns_recommendation_and_approval": True,
            "limit_is_outside_this_agent": True,
            "mlro_decides_any_sar": True,
            "customer_or_bureau_contact_is_outside_this_agent": True,
            "core_or_crm_post_is_outside_this_agent": True,
            "dpo_confirms_lawful_basis_before_live_processing": True,
            "agent_marked_any_approval_done": False,
        },
        "limitations": list(LIMITATIONS),
        "experiment_12_called": True,
        "experiment_29_number_check": True,
        "experiment_36_called": cross["called"],
    }
    draft.update(_decision_flags())
    return _force(draft)


def record_credit_officer_review(
    draft: dict[str, Any],
    *,
    role: str,
    fact_ids: list[str],
    gap_ids: list[str],
) -> dict[str, Any]:
    """Record that a credit officer read every cited row and every gap.

    The agent must not call this. The command line does not expose it.
    A matching role does not approve or decline credit, set a limit, contact
    anyone, post a system, or file a SAR. draft_approved_for_use stays false.
    Use of the memo stays outside this agent.
    """

    if role != CREDIT_OFFICER:
        raise ValueError("only a credit officer can record the reading")
    if not isinstance(draft, dict) or draft.get("label") != LABEL:
        raise ValueError("draft is not a credit memo")
    if not isinstance(fact_ids, list) or not isinstance(gap_ids, list):
        raise ValueError("fact_ids and gap_ids must be lists")
    actual_facts = [fact["fact_id"] for fact in draft.get("facts") or []]
    actual_gaps = [gap["gap_id"] for gap in draft.get("gaps") or []]
    if list(fact_ids) != actual_facts or list(gap_ids) != actual_gaps:
        raise ValueError("fact_ids and gap_ids must match the draft, in order")
    updated = json.loads(json.dumps(draft))
    updated["reading_acknowledged"] = True
    updated["human_approval"]["agent_marked_any_approval_done"] = False
    return _force_reading(updated)


def _force_reading(draft: dict[str, Any]) -> dict[str, Any]:
    reading = True
    _force(draft)
    draft["reading_acknowledged"] = reading
    draft["draft_approved_for_use"] = False
    draft["credit_decision"] = None
    draft["recommendation"] = None
    draft["limit_set"] = None
    return draft


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Draft one synthetic credit memo.")
    parser.add_argument("--pack", required=True)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--stale-after-days", type=int, default=DEFAULT_STALE_AFTER_DAYS)
    parser.add_argument("--approve", action="store_true")
    parser.add_argument("--decline", action="store_true")
    parser.add_argument("--set-limit", action="store_true")
    parser.add_argument("--contact-customer", action="store_true")
    parser.add_argument("--contact-bureau", action="store_true")
    parser.add_argument("--post-core", action="store_true")
    parser.add_argument("--post-crm", action="store_true")
    parser.add_argument("--file-sar", action="store_true")
    args = parser.parse_args(argv)
    prohibited = (
        (args.approve, approve_credit),
        (args.decline, decline_credit),
        (args.set_limit, set_limit),
        (args.contact_customer, contact_customer),
        (args.contact_bureau, contact_bureau),
        (args.post_core, post_core_banking),
        (args.post_crm, post_crm),
        (args.file_sar, file_sar),
    )
    for flagged, function in prohibited:
        if flagged:
            try:
                function()
            except MemoForbidden as exc:
                print(str(exc), file=sys.stderr)
                return 2
    path = Path(args.pack)
    payload = json.loads(path.read_text(encoding="utf-8"))
    try:
        draft = draft_memo(payload, as_of=args.as_of, stale_after_days=args.stale_after_days)
    except NotSynthetic as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except (ValueError, TypeError, RuntimeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    json.dump(draft, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
