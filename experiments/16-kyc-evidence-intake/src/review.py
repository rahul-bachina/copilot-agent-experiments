#!/usr/bin/env python3
"""Draft a KYC evidence checklist for one synthetic customer file.

``review`` calls Experiment 12 ``intake`` with purpose ``kyc_evidence``.
That intake calls Experiment 08. This module does not re-implement either.

The return value is a draft. It does not confirm the documents, set the
purpose, approve or reject or onboard a customer, assign a risk rating,
file a report, or send the customer note. ``record_reviewer_confirmation``
checks a role. It still does not do those things. The forbid functions
always raise.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from copy import deepcopy
from datetime import date, datetime
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from kyc_injection import merge_scans, scan_text
    from sources import (
        ADDRESS_CLASSES,
        ADDRESS_PHRASES,
        BENEFICIAL_OWNER_PHRASES,
        DEFAULT_STALE_AFTER_DAYS,
        FATF_PHRASES,
        IDENTITY_CLASSES,
        IDENTITY_PHRASES,
        LAST_VERIFIED,
        PEP_PHRASES,
        PURPOSE_PHRASES,
        REGISTRAR_PHRASES,
        SOURCES,
        SOURCES_PINNED_ON,
        UNUSUAL_PHRASES,
        QUOTES,
    )
    from tipping_off import (
        ADDRESS_ASK,
        ADDRESS_REFRESH_ASK,
        IDENTITY_ASK,
        IDENTITY_REFRESH_ASK,
        NONE_ASK,
        OUTRO,
        PURPOSE_ASK,
        guard_customer_text,
        lexicon_hits,
    )
else:
    from .kyc_injection import merge_scans, scan_text
    from .sources import (
        ADDRESS_CLASSES,
        ADDRESS_PHRASES,
        BENEFICIAL_OWNER_PHRASES,
        DEFAULT_STALE_AFTER_DAYS,
        FATF_PHRASES,
        IDENTITY_CLASSES,
        IDENTITY_PHRASES,
        LAST_VERIFIED,
        PEP_PHRASES,
        PURPOSE_PHRASES,
        REGISTRAR_PHRASES,
        SOURCES,
        SOURCES_PINNED_ON,
        UNUSUAL_PHRASES,
        QUOTES,
    )
    from .tipping_off import (
        ADDRESS_ASK,
        ADDRESS_REFRESH_ASK,
        IDENTITY_ASK,
        IDENTITY_REFRESH_ASK,
        NONE_ASK,
        OUTRO,
        PURPOSE_ASK,
        guard_customer_text,
        lexicon_hits,
    )

LABEL = "DRAFT FOR KYC REVIEW"
CATALOGUE_ID = "B004"
EXPERIMENT_ID = "exp-16-kyc-evidence-intake"
INTAKE_EXPERIMENT_ID = "exp-12-document-intake"
PURPOSE_ID = "kyc_evidence"
REVIEWER_ROLE = "KYC reviewer"
FIRM_NAME = re.compile(r"[A-Za-z0-9 '&.,-]{1,80}\Z")
PEP_WORD = re.compile(r"\bpep\b", re.IGNORECASE)
NOT_CURRENT = frozenset({"stale", "missing", "future", "invalid"})
CUSTOMER_TYPES = frozenset({"natural_person", "body_corporate", "legal_person", "trust"})
FILE_ID = re.compile(r"^[A-Za-z0-9_-]{1,40}$")

PROHIBITED_KEYS = frozenset(
    {
        "documents_confirmed",
        "purpose_confirmed",
        "permitted_purpose",
        "final_risk_rating",
        "risk_rating",
        "customer_approved",
        "customer_rejected",
        "customer_onboarded",
        "onboard",
        "approve",
        "reject",
        "sar_filed",
        "file_sar",
        "send",
        "email_customer",
        "hints_at_suspicion",
    }
)

LIMITATIONS = (
    "This draft does not confirm the documents or the purpose.",
    "A phrase in a file is not a finding that a Money Laundering Regulations duty is met.",
    "Verification under regulation 28(2)(b) and 28(18) is not performed.",
    "No final risk rating is assigned. Regulation 33 is not decided.",
    "The FATF call-for-action list was not downloaded.",
    "Regulation 35 was not opened. JMLSG Guidance, Part I, was not opened and is not applied.",
    "The 90-day window is a freshness flag. It is not the regulation 40 period.",
    "The five-year date, where shown, is arithmetic on a date the file states. It is not an instruction to retain or to delete.",
    "Customer-facing text is a fixed template. The lexicon is not a complete tipping-off test.",
    "Document inventory and UK identifier spans come from Experiment 12 and Experiment 08. The body is not copied. The text is not anonymised.",
    "No model was called.",
)


class ReviewForbidden(RuntimeError):
    """The review has no approve, rate, onboard, file, or send path."""


class NotSynthetic(ValueError):
    """The customer file was not marked synthetic. The message does not include the body."""


def _load_intake():
    intake_src = Path(__file__).resolve().parents[2] / "12-document-intake" / "src"
    if not intake_src.is_dir():
        raise ReviewForbidden(
            "Experiment 12 is not beside this experiment. The KYC review will not invent an inventory."
        )
    inserted = str(intake_src)
    if inserted not in sys.path:
        sys.path.insert(0, inserted)
    import intake as intake_module

    if intake_module.EXPERIMENT_ID != INTAKE_EXPERIMENT_ID:
        raise ReviewForbidden("the intake module is not Experiment 12")
    return intake_module


def _strip_prohibited(mapping: dict, prefix: str) -> list[str]:
    found = []
    for key in list(mapping):
        if key in PROHIBITED_KEYS:
            found.append(f"{prefix}{key}" if prefix else key)
            del mapping[key]
    return found


def _parse_iso(raw) -> date | None:
    if not isinstance(raw, str) or not raw:
        return None
    try:
        return date.fromisoformat(raw)
    except ValueError:
        return None


def _add_years(value: date, years: int) -> date:
    try:
        return value.replace(year=value.year + years)
    except ValueError:
        return value.replace(year=value.year + years, day=28)


def _firm_label(firm) -> str:
    name = ""
    if isinstance(firm, dict):
        name = firm.get("name") or ""
    if not isinstance(name, str) or not FIRM_NAME.fullmatch(name):
        return "The firm"
    if lexicon_hits(name):
        return "The firm"
    return name


def _closed_or_none(value, allowed: frozenset[str]):
    if value is None or value == "":
        return None
    if isinstance(value, str) and value in allowed:
        return value
    return "unrecognised"


def _will_read(raw: dict, intake_module) -> bool:
    media = raw.get("media_type", "")
    if not isinstance(media, str):
        return False
    content = raw.get("content", "")
    if not isinstance(content, str) or content == "":
        return False
    return media.strip().lower() in intake_module.ALLOWED_MEDIA and len(content) <= intake_module.MAX_CHARS


def _phrase_hits(text: str, phrases: tuple[str, ...]) -> list[str]:
    lower = text.lower()
    return [phrase for phrase in phrases if phrase in lower]


def _class_ids(file: dict) -> set[str]:
    found = set()
    suggested = file.get("suggested_class")
    if isinstance(suggested, str):
        found.add(suggested)
    for candidate in file.get("candidate_classes") or []:
        if isinstance(candidate, dict) and isinstance(candidate.get("id"), str):
            found.add(candidate["id"])
    return found


def _files_matching(files: list[dict], classes: tuple[str, ...], phrases: tuple[str, ...]) -> list[dict]:
    matched = []
    class_set = set(classes)
    for file in files:
        if file.get("read_status") != "read":
            continue
        markers = file.get("markers_found") or []
        phrase_hit = any(phrase in markers for phrase in phrases)
        if _class_ids(file) & class_set or phrase_hit:
            matched.append(file)
    return matched


def _evidence_status(matched: list[dict]) -> str:
    if not matched:
        return "missing"
    statuses = {file["date_status"] for file in matched}
    if "within_window" in statuses:
        return "evidenced"
    if "stale" in statuses:
        return "evidenced_but_stale"
    return "evidenced_but_not_current"


def _cdd_item(item_id: str, regulation: str, words: str, status: str, files: list[dict]) -> dict:
    return {
        "id": item_id,
        "regulation": regulation,
        "requirement_words": words,
        "status": status,
        "sufficient": False,
        "decides_the_duty": False,
        "file_ids": [file["file_id"] for file in files],
        "stale_file_ids": [file["file_id"] for file in files if file["date_status"] == "stale"],
    }


def _trigger(item_id: str, regulation: str, words: str, status: str, file_ids: list[str], phrases: list[str]) -> dict:
    return {
        "id": item_id,
        "regulation": regulation,
        "requirement_words": words,
        "status": status,
        "sufficient": False,
        "decides_the_duty": False,
        "edd_applied": False,
        "file_ids": file_ids,
        "phrases_found": phrases,
    }


def _question(question_id: str, text: str) -> dict:
    return {
        "id": question_id,
        "audience": "KYC reviewer",
        "not_for_the_customer": True,
        "text": text,
    }


def _record_keeping(customer: dict) -> dict:
    relationship = customer.get("relationship")
    status = customer.get("relationship_status")
    result = {
        "regulation": "40(3)",
        "minimum_period_words": QUOTES["reg40_3"],
        "occasional_transaction_words": QUOTES["reg40_3_a"],
        "relationship_end_words": QUOTES["reg40_3_b"],
        "reg40_4_words": QUOTES["reg40_4"],
        "ten_year_date_calculated": False,
        "deletion_performed": False,
        "instruction_to_delete": False,
        "instruction_to_retain": False,
        "freshness_window_is_this_period": False,
        "period_begun": False,
        "arithmetic_end": None,
        "arithmetic_basis": None,
        "date_used": None,
    }
    if relationship == "occasional_transaction":
        parsed = _parse_iso(customer.get("transaction_completed_on"))
        if parsed:
            result["period_begun"] = True
            result["date_used"] = parsed.isoformat()
            result["arithmetic_end"] = _add_years(parsed, 5).isoformat()
            result["arithmetic_basis"] = (
                "The file states that the occasional transaction is complete on this date. "
                "That is not a finding that the relevant person knows, or has reasonable "
                "grounds to believe, that it is complete."
            )
        else:
            result["arithmetic_basis"] = (
                "The file says this is an occasional transaction and gives no usable completion date. "
                "No five-year date was calculated."
            )
    elif relationship == "business_relationship":
        if status == "ended":
            parsed = _parse_iso(customer.get("relationship_ended_on"))
            if parsed:
                result["period_begun"] = True
                result["date_used"] = parsed.isoformat()
                result["arithmetic_end"] = _add_years(parsed, 5).isoformat()
                result["arithmetic_basis"] = (
                    "The file states that the business relationship ended on this date. "
                    "That is not a finding that the relevant person knows, or has reasonable "
                    "grounds to believe, that it has come to an end."
                )
            else:
                result["arithmetic_basis"] = (
                    "The file says the business relationship has ended and gives no usable date. "
                    "No five-year date was calculated."
                )
        elif status == "ongoing":
            result["arithmetic_basis"] = (
                "The file says the business relationship is ongoing. Regulation 40(3)(b) "
                "begins when the relationship has come to an end. No five-year date was calculated."
            )
        else:
            result["arithmetic_basis"] = (
                "The file does not say whether the business relationship has ended. "
                "No five-year date was calculated."
            )
    else:
        result["arithmetic_basis"] = (
            "The file does not say whether this is a business relationship or an occasional "
            "transaction. No five-year date was calculated."
        )
    return result


def _customer_sentences(identity_status: str, address_status: str, purpose_status: str, firm: str) -> str:
    lines = [f"{firm} has asked for the following so its records can be completed."]
    refresh = {"evidenced_but_stale", "evidenced_but_not_current"}
    if identity_status == "missing":
        lines.append(IDENTITY_ASK)
    elif identity_status in refresh:
        lines.append(IDENTITY_REFRESH_ASK)
    if address_status == "missing":
        lines.append(ADDRESS_ASK)
    elif address_status in refresh:
        lines.append(ADDRESS_REFRESH_ASK)
    if purpose_status == "missing":
        lines.append(PURPOSE_ASK)
    if len(lines) == 1:
        lines.append(NONE_ASK)
    lines.append(OUTRO)
    return " ".join(lines)


def _flags() -> dict:
    return {
        "customer_approved": False,
        "customer_rejected": False,
        "customer_onboarded": False,
        "final_risk_rating_assigned": False,
        "sar_filed": False,
        "external_sent": False,
        "production_record_written": False,
        "customer_text_hints_at_suspicion": False,
        "purpose_taken_from_document": False,
        "documents_confirmed_by_document": False,
    }


def _human_approval() -> dict:
    return {
        "documents_and_purpose": {"required": True, "approver": REVIEWER_ROLE, "recorded": False},
        "rely_on_stale_material": {"required": True, "approver": REVIEWER_ROLE, "recorded": False},
        "send_customer_wording": {
            "required": True,
            "approver": REVIEWER_ROLE,
            "recorded": False,
            "performed_by_this_agent": False,
        },
        "risk_rating": {
            "required": True,
            "approver": REVIEWER_ROLE,
            "recorded": False,
            "performed_by_this_agent": False,
        },
        "sar": {
            "required": True,
            "approver": "Nominated officer",
            "recorded": False,
            "performed_by_this_agent": False,
        },
    }


def _source_rows() -> list[dict]:
    rows = []
    for source in SOURCES:
        rows.append(
            {
                "id": source["id"],
                "title": source["title"],
                "url": source["url"],
                "last_verified": source["last_verified"],
                "body_opened": source["body_opened"],
                "applied_as_a_decision": False,
            }
        )
    return rows


def _force_inert(draft: dict) -> None:
    draft["actions_taken"] = []
    draft["model_called"] = False
    draft["network_called"] = False
    draft["fatf_list_downloaded"] = False
    draft["jmlsg_part_i_opened"] = False
    draft["regulation_35_opened"] = False
    draft["final_risk_rating"] = None
    draft["customer_decision"] = None
    draft["flags"] = _flags()
    draft["prompt_injection"]["followed"] = False
    for signal in draft["prompt_injection"]["signals"]:
        signal["followed"] = False
    intake = draft["document_intake"]
    intake["files_confirmed"] = False
    intake["purpose_confirmed"] = False
    intake["permitted_purpose"] = None
    intake["reviewer_decision"] = None
    intake["actions_taken"] = []
    intake["model_called"] = False
    intake["network_called"] = False
    for key, value in (
        ("accepted_into_queue", False),
        ("production_record_written", False),
        ("external_sent", False),
        ("underlying_matter_approved", False),
        ("underlying_matter_rejected", False),
        ("redacted_text_released", False),
        ("output_is_anonymised", False),
        ("purpose_taken_from_document", False),
        ("files_confirmed_by_document", False),
        ("handed_off", False),
    ):
        intake["flags"][key] = value
    intake["gateway"]["output_is_anonymised"] = False
    intake["gateway"]["agent_may_release"] = False
    intake["prompt_injection"]["followed"] = False
    for signal in intake["prompt_injection"]["signals"]:
        signal["followed"] = False
    if intake.get("checklist_preview") is not None:
        intake["checklist_preview"]["sufficient"] = False
    for file in intake["files"]:
        file["content_recorded"] = False
        file["pii"]["output_is_anonymised"] = False
        file["pii"]["agent_may_release"] = False
    draft["checklist"]["sufficient"] = False
    draft["checklist"]["edd_applied"] = False
    draft["checklist"]["risk_rating"] = None
    for item in draft["checklist"]["cdd"] + draft["checklist"]["edd_triggers"]:
        item["sufficient"] = False
        item["decides_the_duty"] = False
        if "edd_applied" in item:
            item["edd_applied"] = False
    published = guard_customer_text(draft["customer_facing"]["text"])
    draft["customer_facing"] = published
    draft["flags"]["customer_text_hints_at_suspicion"] = published["hints_at_suspicion"]
    draft["record_keeping"]["deletion_performed"] = False
    draft["record_keeping"]["instruction_to_delete"] = False
    draft["record_keeping"]["instruction_to_retain"] = False
    draft["record_keeping"]["ten_year_date_calculated"] = False
    draft["record_keeping"]["freshness_window_is_this_period"] = False
    draft["human_approval"]["send_customer_wording"]["performed_by_this_agent"] = False
    draft["human_approval"]["risk_rating"]["recorded"] = False
    draft["human_approval"]["risk_rating"]["performed_by_this_agent"] = False
    draft["human_approval"]["sar"]["recorded"] = False
    draft["human_approval"]["sar"]["performed_by_this_agent"] = False
    for source in draft["sources"]:
        source["applied_as_a_decision"] = False


def review(
    customer_file: dict,
    *,
    as_of: date,
    stale_after_days: int = DEFAULT_STALE_AFTER_DAYS,
    rules_as_of: date | None = None,
) -> dict:
    """Return a draft checklist. Confirmation flags stay false."""

    if not isinstance(customer_file, dict):
        raise TypeError("customer_file must be an object")
    if not isinstance(as_of, date) or isinstance(as_of, datetime):
        raise TypeError("as_of must be a date")
    if type(stale_after_days) is not int or stale_after_days < 0:
        raise ValueError("stale_after_days must be a non-negative integer")
    if rules_as_of is not None and (not isinstance(rules_as_of, date) or isinstance(rules_as_of, datetime)):
        raise TypeError("rules_as_of must be a date")
    if customer_file.get("synthetic") is not True:
        raise NotSynthetic("record is not marked synthetic")

    intake_module = _load_intake()
    working = dict(customer_file)
    prohibited = _strip_prohibited(working, "")
    files_in = working.get("files")
    if not isinstance(files_in, list) or not files_in:
        raise ValueError("customer file has no files")

    customer_file_id = working.get("customer_file_id", "unspecified")
    if (
        not isinstance(customer_file_id, str)
        or not customer_file_id
        or len(customer_file_id) > 80
        or "\n" in customer_file_id
    ):
        customer_file_id = "unspecified"
    customer_ref = working.get("customer_ref", "")
    if not isinstance(customer_ref, str) or "\n" in customer_ref or len(customer_ref) > 80:
        customer_ref = ""

    purpose_on_file = working.get("requested_purpose")
    purpose_conflict = purpose_on_file not in {None, PURPOSE_ID}
    screening_note = working.get("screening_note", "")
    if not isinstance(screening_note, str):
        screening_note = ""
    country = working.get("stated_establishment_country")
    if not isinstance(country, str) or not country.strip() or "\n" in country or len(country) > 80:
        country = None
    else:
        country = country.strip()

    scans = []
    purpose_files: list[str] = []
    beneficial_files: list[str] = []
    registrar_files: list[str] = []
    pep_files: list[str] = []
    pep_phrases: list[str] = []
    fatf_files: list[str] = []
    fatf_phrases: list[str] = []
    unusual_files: list[str] = []
    unusual_phrases: list[str] = []
    pep_in_note = False
    fatf_in_note = False
    unusual_in_note = False

    cleaned_files = []
    for raw in files_in:
        if not isinstance(raw, dict):
            raise ValueError("each file must be an object")
        file_copy = dict(raw)
        file_id = file_copy.get("file_id", "?")
        prohibited.extend(_strip_prohibited(file_copy, f"file:{file_id}:"))
        content = file_copy.get("content", "")
        if not isinstance(content, str):
            content = ""
        filename = file_copy.get("filename", "")
        if not isinstance(filename, str):
            filename = ""
        label = file_id if isinstance(file_id, str) else "?"
        scans.append(scan_text(filename, file_id=label, where="filename"))
        if content and len(content) <= intake_module.MAX_CHARS:
            scans.append(scan_text(content, file_id=label, where="body"))
        if _will_read(file_copy, intake_module):
            if _phrase_hits(content, PURPOSE_PHRASES):
                purpose_files.append(label)
            if _phrase_hits(content, BENEFICIAL_OWNER_PHRASES):
                beneficial_files.append(label)
            if _phrase_hits(content, REGISTRAR_PHRASES):
                registrar_files.append(label)
            found_pep = _phrase_hits(content, PEP_PHRASES)
            if PEP_WORD.search(content):
                found_pep.append("pep")
            if found_pep:
                pep_files.append(label)
                for phrase in found_pep:
                    if phrase not in pep_phrases:
                        pep_phrases.append(phrase)
            found_fatf = _phrase_hits(content, FATF_PHRASES)
            if found_fatf:
                fatf_files.append(label)
                for phrase in found_fatf:
                    if phrase not in fatf_phrases:
                        fatf_phrases.append(phrase)
            found_unusual = _phrase_hits(content, UNUSUAL_PHRASES)
            if found_unusual:
                unusual_files.append(label)
                for phrase in found_unusual:
                    if phrase not in unusual_phrases:
                        unusual_phrases.append(phrase)
        cleaned_files.append(file_copy)

    if screening_note:
        scans.append(scan_text(screening_note, file_id="screening_note", where="body"))
        if _phrase_hits(screening_note, PEP_PHRASES) or PEP_WORD.search(screening_note):
            pep_in_note = True
        if _phrase_hits(screening_note, FATF_PHRASES):
            fatf_in_note = True
        if _phrase_hits(screening_note, UNUSUAL_PHRASES):
            unusual_in_note = True

    batch = {
        "synthetic": True,
        "batch_id": customer_file_id,
        "requested_purpose": PURPOSE_ID,
        "files": cleaned_files,
    }
    intake_draft = intake_module.intake(
        batch,
        as_of=as_of,
        stale_after_days=stale_after_days,
        rules_as_of=rules_as_of,
    )

    identity_files = _files_matching(intake_draft["files"], IDENTITY_CLASSES, IDENTITY_PHRASES)
    address_files = _files_matching(intake_draft["files"], ADDRESS_CLASSES, ADDRESS_PHRASES)
    identity_status = _evidence_status(identity_files)
    address_status = _evidence_status(address_files)
    purpose_matched = [
        file for file in intake_draft["files"] if file["file_id"] in purpose_files and file["read_status"] == "read"
    ]
    purpose_status = _evidence_status(purpose_matched)
    customer_type = _closed_or_none(working.get("customer_type"), CUSTOMER_TYPES)
    if customer_type == "natural_person":
        beneficial_status = "not_applicable_on_the_file"
        beneficial_matched: list[dict] = []
    elif customer_type in {"body_corporate", "legal_person", "trust"}:
        beneficial_matched = [
            file
            for file in intake_draft["files"]
            if file["file_id"] in beneficial_files and file["read_status"] == "read"
        ]
        beneficial_status = _evidence_status(beneficial_matched)
    else:
        beneficial_status = "missing"
        beneficial_matched = []

    cdd = [
        _cdd_item("reg_28_2_a_identify", "28(2)(a)", QUOTES["reg28_2_a"], identity_status, identity_files),
        _cdd_item(
            "intake_address_marker",
            "28(2)(a)",
            "Experiment 12 looks for a proof-of-address class, or the words proof of address, "
            "council tax, or utility bill, on a file that was read. Regulation 28 does not "
            "contain a separate address sentence. This row is that intake marker.",
            address_status,
            address_files,
        ),
        _cdd_item("reg_28_2_b_verify", "28(2)(b)", QUOTES["reg28_2_b"], "not_determined", []),
        _cdd_item(
            "reg_28_2_c_purpose_and_nature",
            "28(2)(c)",
            QUOTES["reg28_2_c"],
            purpose_status,
            purpose_matched,
        ),
        _cdd_item(
            "reg_28_4_beneficial_owner",
            "28(4)",
            "identify the beneficial owner",
            beneficial_status,
            beneficial_matched,
        ),
        _cdd_item("reg_28_11_ongoing_monitoring", "28(11)", QUOTES["reg28_11"], "question_only", []),
    ]

    def trigger_status(file_ids: list[str], in_note: bool, *, country_stated: bool = False) -> str:
        if file_ids:
            return "phrase_present"
        if in_note:
            return "phrase_in_note"
        if country_stated:
            return "country_stated_in_the_file"
        return "not_in_file"

    edd = [
        _trigger(
            "reg_33_1_b_fatf_call_for_action",
            "33(1)(b)",
            QUOTES["reg33_1_b_person"],
            trigger_status(fatf_files, fatf_in_note, country_stated=country is not None),
            fatf_files,
            fatf_phrases,
        ),
        _trigger(
            "reg_33_1_d_pep",
            "33(1)(d)",
            QUOTES["reg33_1_d"],
            trigger_status(pep_files, pep_in_note),
            pep_files,
            pep_phrases,
        ),
        _trigger(
            "reg_33_1_f_unusual_transaction",
            "33(1)(f)",
            QUOTES["reg33_1_f_i"],
            trigger_status(unusual_files, unusual_in_note),
            unusual_files,
            unusual_phrases,
        ),
    ]

    stale_files = [
        {
            "file_id": file["file_id"],
            "date_status": file["date_status"],
            "document_date": file["document_date"],
            "age_days": file["age_days"],
        }
        for file in intake_draft["files"]
        if file["date_status"] in NOT_CURRENT
    ]
    sources_age = (as_of - SOURCES_PINNED_ON).days
    sources_stale = sources_age > stale_after_days
    # Document age is separate. A stale passport does not make the pinned
    # regulation text stale, and the 90-day window is not regulation 40.
    rules_current = (not sources_stale) and intake_draft["rules_current"] is True

    questions = [
        _question(
            "q_verify_identity",
            "Regulation 28(2)(b) and 28(18) require verification on the basis of documents "
            "or information from a reliable source independent of the person whose identity "
            "is being verified. This draft does not verify anyone. Which document will you "
            "rely on, and why is that source independent?",
        ),
        _question(
            "q_ongoing_monitoring",
            "Regulation 28(11) requires ongoing monitoring of a business relationship, "
            "including scrutiny of transactions and keeping the customer due diligence "
            "records up to date. This draft does not monitor the relationship. What review "
            "will you apply?",
        ),
    ]
    if customer_type == "natural_person":
        questions.append(
            _question(
                "q_beneficial_owner",
                "The file states customer_type natural_person. Regulation 28(4) applies where "
                "the customer is beneficially owned by another person. This draft does not "
                "decide that the customer is a natural person. Do you?",
            )
        )
    elif customer_type in {"body_corporate", "legal_person", "trust"}:
        questions.append(
            _question(
                "q_beneficial_owner",
                "The file states a customer that can be beneficially owned. Regulation 28(4) "
                "requires the beneficial owner to be identified, and reasonable measures to "
                "verify that identity. A phrase in the file is not that verification. "
                "Regulation 28(9) says paragraph (4) is not satisfied by relying solely on "
                "information delivered to the registrar.",
            )
        )
    else:
        questions.append(
            _question(
                "q_beneficial_owner",
                "The file does not state a closed-list customer type, so the beneficial-owner "
                "row cannot be marked not applicable. What is the customer?",
            )
        )
    if registrar_files:
        questions.append(
            _question(
                "q_registrar",
                "A read file contains a closed-list registrar phrase. Regulation 28(9), as "
                "substituted on 18 November 2025, says relevant persons do not satisfy "
                "paragraph (4) by relying solely on information delivered to the registrar. "
                "This draft does not decide whether reliance is sole.",
            )
        )
    pep_trigger = edd[1]["status"]
    questions.append(
        _question(
            "q_pep",
            "Regulation 33(1)(d) applies if a relevant person has determined that a customer "
            "or potential customer is a PEP, or a family member or known close associate of "
            "a PEP, in accordance with regulation 35. "
            + (
                "A closed-list phrase is in a file that was read. "
                if pep_trigger == "phrase_present"
                else "A closed-list phrase is in the screening note only. "
                if pep_trigger == "phrase_in_note"
                else "No closed-list PEP phrase was found. "
            )
            + "This draft does not make that determination. Regulation 35 was not opened.",
        )
    )
    fatf_trigger = edd[0]["status"]
    country_sentence = (
        f'The file states an establishment country of "{country}". '
        if country
        else "The file does not state an establishment country. "
    )
    questions.append(
        _question(
            "q_fatf",
            "Regulation 33(1)(b), as substituted on 30 June 2026, refers to a person "
            "established in a FATF call for action country. Regulation 33(3)(a) defines "
            "that as a country named on the FATF list of High-Risk Jurisdictions subject "
            "to a Call for Action, as that list has effect from time to time. "
            "SI 2026/621 regulation 19 replaced the words high-risk third country. "
            + country_sentence
            + (
                "The old or the new words appear in a file that was read. "
                if fatf_trigger == "phrase_present"
                else "Those words appear in the screening note only. "
                if fatf_trigger == "phrase_in_note"
                else "Those words were not found. "
            )
            + "This starter did not download the list and does not decide that paragraph (1)(b) applies.",
        )
    )
    unusual_trigger = edd[2]["status"]
    questions.append(
        _question(
            "q_unusual",
            "Regulation 33(1)(f), as substituted on 30 June 2026, covers a transaction that "
            "is unusually complex or unusually large given its nature, an unusual pattern of "
            "transactions, or a transaction with no apparent economic or legal purpose. "
            + (
                "A closed-list phrase is in the file. "
                if unusual_trigger in {"phrase_present", "phrase_in_note"}
                else "No closed-list phrase was found. "
            )
            + "Regulation 33(4) tells the relevant person to examine the background and purpose "
            "and to increase monitoring to determine whether the transaction or the relationship "
            "appears suspicious. This draft does not make that determination, and that word is "
            "not put in the customer note.",
        )
    )
    questions.append(
        _question(
            "q_record_keeping",
            "Regulation 40(3) sets a period of five years beginning when the relevant person "
            "knows, or has reasonable grounds to believe, that the occasional transaction is "
            "complete or that the business relationship has come to an end. Regulation 40(4) "
            "says the relevant person is not required to keep the records referred to in "
            "paragraph (3)(b)(i) for more than 10 years. That sentence applies only to those "
            "records. It does not limit every record under regulation 40. "
            "This draft does not calculate a ten-year date and does not delete anything. "
            "The 90-day freshness flag is not this period. "
            + draft_basis_placeholder(working),
        )
    )
    if stale_files or sources_stale or intake_draft["catalogue_stale"] or intake_draft["gateway_rules_stale"]:
        questions.append(
            _question(
                "q_stale",
                "At least one document date is not current, or a pinned source is older than "
                "the freshness window. A sentence in the file does not clear that. Will you "
                "rely on it, and on what basis? Confirming the document list does not answer this.",
            )
        )
    if any(file["read_status"] != "read" for file in intake_draft["files"]):
        questions.append(
            _question(
                "q_not_read",
                "At least one file was not read, was empty, or was over the size cap. "
                "That is a gap, not evidence that the point is absent from a document this starter could not open.",
            )
        )
    if purpose_conflict:
        questions.append(
            _question(
                "q_purpose_conflict",
                "The customer file names a purpose other than kyc_evidence. This agent only "
                "previews that purpose. Confirm kyc_evidence, or stop and use the other intake. "
                "The file text cannot confirm it.",
            )
        )
    injection = merge_scans(scans)
    if injection["detected"] or intake_draft["prompt_injection"]["detected"]:
        questions.append(
            _question(
                "q_injection",
                "The file contains an instruction, which may be hidden. It was not followed. "
                "It cannot confirm the documents, approve the customer, set a rating, file a "
                "report, or dictate the customer note. What will you do with that file?",
            )
        )

    record = _record_keeping(
        {
            "relationship": _closed_or_none(working.get("relationship"), frozenset({"business_relationship", "occasional_transaction"})),
            "relationship_status": _closed_or_none(working.get("relationship_status"), frozenset({"ongoing", "ended"})),
            "relationship_ended_on": working.get("relationship_ended_on"),
            "transaction_completed_on": working.get("transaction_completed_on"),
        }
    )
    # The record-keeping question was built before the arithmetic text existed.
    # Replace the placeholder sentence with the basis the same function returns.
    for question in questions:
        if question["id"] == "q_record_keeping":
            question["text"] = question["text"].replace(
                draft_basis_placeholder(working),
                record["arithmetic_basis"],
            )

    evidenced = [
        item["id"]
        for item in cdd
        if item["status"] in {"evidenced", "evidenced_but_stale"}
    ]
    missing = [item["id"] for item in cdd if item["status"] == "missing"]
    firm = _firm_label(working.get("firm"))
    customer_text = _customer_sentences(identity_status, address_status, purpose_status, firm)

    draft = {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment_id": EXPERIMENT_ID,
        "autonomy": "A1",
        "customer_file_id": customer_file_id,
        "customer_ref": customer_ref,
        "firm_name_in_customer_note": firm,
        "firm_is_fictional": True,
        "customer_type_as_stated": customer_type,
        "stated_establishment_country": country,
        "as_of": as_of.isoformat(),
        "sources_pinned_on": SOURCES_PINNED_ON.isoformat(),
        "sources_last_verified": LAST_VERIFIED,
        "sources_age_days": sources_age,
        "sources_stale": sources_stale,
        "stale_after_days": stale_after_days,
        "any_document_stale": intake_draft["any_document_stale"],
        "any_document_not_current": intake_draft["any_document_not_current"],
        "rules_current": rules_current,
        "model_called": False,
        "network_called": False,
        "fatf_list_downloaded": False,
        "jmlsg_part_i_opened": False,
        "regulation_35_opened": False,
        "documents_confirmed": False,
        "purpose_confirmed": False,
        "permitted_purpose": None,
        "purpose_preview": {
            "id": PURPOSE_ID,
            "confirmed": False,
            "supplied_by": "file" if purpose_on_file == PURPOSE_ID else "exp-16",
            "purpose_on_file": purpose_on_file if isinstance(purpose_on_file, str) else None,
            "conflict": purpose_conflict,
        },
        "confirmation": None,
        "final_risk_rating": None,
        "customer_decision": None,
        "actions_taken": [],
        "flags": _flags(),
        "document_intake": intake_draft,
        "checklist": {
            "cdd": cdd,
            "edd_triggers": edd,
            "sufficient": False,
            "edd_applied": False,
            "risk_rating": None,
        },
        "evidenced": evidenced,
        "missing": missing,
        "stale": stale_files,
        "reviewer_questions": questions,
        "customer_facing": {
            "audience": "customer",
            "may_be_sent_by_agent": False,
            "hints_at_suspicion": False,
            "hints_found": [],
            "replaced_by_guard": False,
            "text": customer_text,
        },
        "record_keeping": record,
        "prompt_injection": injection,
        "prohibited_payload_keys": prohibited,
        "sources": _source_rows(),
        "human_approval": _human_approval(),
        "limitations": list(LIMITATIONS),
    }
    _force_inert(draft)
    return draft


def draft_basis_placeholder(_customer: dict) -> str:
    """Stable token replaced once the arithmetic basis is known."""

    return "RECORD_KEEPING_BASIS"


def _require_draft(draft: dict) -> dict:
    if not isinstance(draft, dict) or draft.get("label") != LABEL:
        raise ValueError("draft is not a KYC review")
    if draft.get("experiment_id") != EXPERIMENT_ID:
        raise ValueError("draft is not a KYC review")
    return deepcopy(draft)


def record_reviewer_confirmation(
    draft: dict,
    *,
    role: str,
    file_ids: list[str],
    purpose: str,
    acknowledge_stale: bool = False,
) -> dict:
    """Record that a KYC reviewer confirmed the documents and the purpose.

    The agent must not call this. A matching role does not approve, reject,
    or onboard the customer, and does not assign a rating or file a report.
    """

    if role != REVIEWER_ROLE:
        raise ValueError("only a KYC reviewer can confirm the documents and the purpose")
    if acknowledge_stale is not True and acknowledge_stale is not False:
        raise TypeError("acknowledge_stale must be a boolean")
    updated = _require_draft(draft)
    if not isinstance(file_ids, list) or not file_ids:
        raise ValueError("file_ids must list every file in the draft, in order")
    actual = [file["file_id"] for file in updated["document_intake"]["files"]]
    if list(file_ids) != actual:
        raise ValueError("file_ids must match the draft, in order")
    if any(file["checksum_matches"] is False for file in updated["document_intake"]["files"]):
        raise ValueError("a file checksum does not match; confirmation is refused")
    if purpose != PURPOSE_ID:
        raise ValueError("purpose must be kyc_evidence")
    updated["documents_confirmed"] = True
    updated["purpose_confirmed"] = True
    updated["permitted_purpose"] = {
        "id": PURPOSE_ID,
        "confirmed_by": REVIEWER_ROLE,
        "does_not_approve_the_customer": True,
    }
    updated["confirmation"] = {
        "role": REVIEWER_ROLE,
        "purpose_id": PURPOSE_ID,
        "file_ids": list(file_ids),
        "stale_acknowledged": bool(acknowledge_stale),
        "does_not_approve_the_customer": True,
        "does_not_assign_a_risk_rating": True,
        "does_not_file_a_sar": True,
        "does_not_send": True,
    }
    updated["human_approval"]["documents_and_purpose"]["recorded"] = True
    if acknowledge_stale:
        updated["human_approval"]["rely_on_stale_material"]["recorded"] = True
    _force_inert(updated)
    updated["documents_confirmed"] = True
    updated["purpose_confirmed"] = True
    return updated


def approve_customer(_draft: dict) -> None:
    """Refuse to approve a customer."""

    raise ReviewForbidden("the agent does not approve a customer")


def reject_customer(_draft: dict) -> None:
    """Refuse to reject a customer."""

    raise ReviewForbidden("the agent does not reject a customer")


def onboard_customer(_draft: dict) -> None:
    """Refuse to onboard a customer."""

    raise ReviewForbidden("the agent does not onboard a customer")


def assign_risk_rating(_draft: dict, _rating: str | None = None) -> None:
    """Refuse to assign a final risk rating."""

    raise ReviewForbidden("the agent does not assign a final risk rating")


def file_sar(_draft: dict) -> None:
    """Refuse to file a suspicious activity report."""

    raise ReviewForbidden("the agent does not file a suspicious activity report")


def send_to_customer(_draft: dict) -> None:
    """Refuse to send the customer note."""

    raise ReviewForbidden("the agent does not send to the customer")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Draft a KYC evidence checklist. Does not approve the customer.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--stale-after-days", type=int, default=DEFAULT_STALE_AFTER_DAYS)
    parser.add_argument("--rules-as-of", default=None)
    args = parser.parse_args(argv)
    customer_file = json.loads(Path(args.input).read_text(encoding="utf-8"))
    rules = date.fromisoformat(args.rules_as_of) if args.rules_as_of else None
    try:
        draft = review(
            customer_file,
            as_of=date.fromisoformat(args.as_of),
            stale_after_days=args.stale_after_days,
            rules_as_of=rules,
        )
    except NotSynthetic:
        sys.stderr.write("REFUSED: record is not marked synthetic\n")
        return 2
    json.dump(draft, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
