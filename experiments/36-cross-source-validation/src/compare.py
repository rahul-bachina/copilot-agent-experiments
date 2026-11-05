#!/usr/bin/env python3
"""Compare one fact across synthetic source documents.

The class is a deterministic rule. A model is not called. The reviewer
resolves every material discrepancy. This module does not choose which
source is right, does not edit a record, does not contact anyone, and
does not query Companies House.

Document intake is Experiment 12. Identifier proposals are Experiment 08.
The pinpoint check is Experiment 33's span resolver. Those modules are
called. Their rules are not copied.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from injection import codes_in
    from normalise import FIELD_TYPES, classify_values, display_fold, normalise_value
    from siblings import CompareForbidden, load
    from sources import source_rows
else:
    from .injection import codes_in
    from .normalise import FIELD_TYPES, classify_values, display_fold, normalise_value
    from .siblings import CompareForbidden, load
    from .sources import source_rows

LABEL = "DRAFT FOR THE REVIEWER. NOT A CORRECTION."
CATALOGUE_ID = "B005"
EXPERIMENT_ID = "exp-36-cross-source-validation"
AUTONOMY = "A0"
DEFAULT_STALE_AFTER_DAYS = 90
REVIEWER_ROLE = "Reviewer"
REVIEWER_REF = re.compile(r"^REV-\d{4}$")
DOCUMENT_ID = re.compile(r"^[a-z0-9][a-z0-9-]{0,39}$")
FACT_KEY = re.compile(r"^[a-z][a-z0-9_]{0,40}$")
KINDS = frozenset({"form", "contract", "invoice", "register_extract"})
MAX_DOCUMENTS = 8
MAX_FACTS = 20
MAX_FIELDS = 30
MAX_LINES = 40
MAX_VALUE = 200
MAX_LINE = 500

WITHHOLD = frozenset({"nino", "nhs_number", "sort_code", "account_number", "iban", "utr"})
EXPECTED_FINDINGS = {
    "company_number": frozenset({"crn"}),
    "postcode": frozenset({"postcode"}),
}
REASON_PRIORITY = (
    "identifier_withheld",
    "pinpoint_failed",
    "fewer_than_two_sources",
    "unparseable",
    "normalised_values_differ",
    "formatting_or_abbreviation",
    "same_unparsed_text",
    "same_display",
)
MATERIAL_REASONS = frozenset(
    {
        "identifier_withheld",
        "pinpoint_failed",
        "fewer_than_two_sources",
        "unparseable",
        "normalised_values_differ",
    }
)
PROHIBITED_KEYS = frozenset(
    {
        "agent_chose_source",
        "records_edited",
        "parties_contacted",
        "register_queried",
        "correct_value",
        "preferred_source",
        "resolved",
        "all_material_resolved",
        "model_called",
        "network_called",
        "foundry_called",
        "a3_recommended",
        "output_is_anonymised",
        "actions_taken",
        "explanation_authored_by_model",
        "approved",
        "choose_source",
        "edit_record",
        "contact",
    }
)

EXPLANATIONS = {
    "match": (
        "The values are the same once case and whitespace are folded, or the "
        "unparsed text is the same. This is not a finding that the value is accurate."
    ),
    "immaterial_difference": (
        "The values differ on the page and are the same after the deterministic "
        "normaliser for this field type. The difference is formatting or an "
        "abbreviation in those rules. This is not a finding that either source is right."
    ),
    "material_discrepancy": (
        "The values are not the same after the deterministic normaliser, or a "
        "citation could not be used. The reviewer resolves this. This tool does "
        "not choose a source, edit a record, or contact anyone."
    ),
}

LIMITATIONS = (
    "The class is a rule in src/normalise.py. It is not a finding that personal data is inaccurate under the Data Protection Act 2018, section 205, and it does not erase or rectify anything under UK GDPR Article 5(1)(d).",
    "The ICO accuracy page was requested on 5 November 2026 and returned HTTP 403. It was not opened and is not quoted.",
    "Company numbers and postcodes use Experiment 08's imported shapes. The 2011 URI guide and the 2015 ILR annex were not re-opened. There is no Companies House lookup. A match is not a finding that the number has been issued.",
    "Numeric company numbers are padded to eight digits. An unknown prefix is left unparsed. A 7-digit form and its zero-padded form are immaterial formatting, and the raw quotes are still shown.",
    "Dates are UK day-first. 01/02/2026 is 1 February 2026, not 2 January. A two-digit year is not accepted.",
    "A street abbreviation is expanded only when it is the last word. A town after the street word is not removed.",
    "A leading title is removed only when the next token is a single letter. Other titles stay.",
    "An unparsed value that is identical on every source is a match of the text, not a finding that the value is valid.",
    "Immaterial rows are shown. The reviewer is not asked to resolve them. They are not a decision that the values are accurate.",
    "A negation in the same line can hide one of this experiment's instruction phrases. Experiment 12's phrase list does not use that skip.",
    "Experiment 08 does not detect an unlabelled NHS number, an unlabelled eight-digit company number, names, or email addresses. output_is_anonymised stays false.",
    "The 90-day window is a stale flag. Article 5(1)(d) says 'without delay'. It does not state 90 days.",
    "Experiment 12's purpose stays unconfirmed. This tool does not call the intake confirmation or routing functions.",
    "No model was called. An explanation in the JSON is a fixed sentence for the class.",
)


class NotSynthetic(ValueError):
    """The pack was not marked synthetic. The message does not include the body."""


def choose_source(*_args, **_kwargs) -> None:
    raise CompareForbidden("The agent does not choose which source is right.")


def edit_record(*_args, **_kwargs) -> None:
    raise CompareForbidden("The agent does not edit a record.")


def contact_party(*_args, **_kwargs) -> None:
    raise CompareForbidden("The agent does not contact anyone.")


def lookup_register(*_args, **_kwargs) -> None:
    raise CompareForbidden("The agent does not query Companies House or any other register.")


def recommend_a3(*_args, **_kwargs) -> None:
    raise CompareForbidden("Autonomy A3 is not a recommendation.")


def _strip(mapping: dict) -> list[str]:
    found = []
    for key in list(mapping):
        if key in PROHIBITED_KEYS:
            found.append(key)
            del mapping[key]
    return found


def _parse_as_of(value: str) -> date:
    if not isinstance(value, str):
        raise TypeError("as_of must be an ISO date")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("as_of must be an ISO date") from exc


def _line_index(document: dict) -> dict[tuple[int, int, int], str]:
    index = {}
    for page in document.get("pages") or []:
        page_no = page.get("page")
        for paragraph in page.get("paragraphs") or []:
            paragraph_no = paragraph.get("paragraph")
            for row in paragraph.get("lines") or []:
                if not isinstance(row, dict):
                    raise ValueError("a line must be an object")
                text = row.get("text")
                if not isinstance(text, str) or len(text) > MAX_LINE:
                    raise ValueError("a line must be a string within the length cap")
                key = (page_no, paragraph_no, row.get("line"))
                if key in index:
                    raise ValueError("a line number is repeated")
                index[key] = text
    if not index:
        raise ValueError("a document has no lines")
    if len(index) > MAX_LINES:
        raise ValueError("a document has more lines than this starter will read")
    return index


def _documents(pack: dict) -> list[dict]:
    documents = pack.get("documents")
    if not isinstance(documents, list) or not documents:
        raise ValueError("pack has no documents")
    if len(documents) > MAX_DOCUMENTS:
        raise ValueError("pack has more documents than this starter will compare")
    seen = set()
    cleaned = []
    for raw in documents:
        if not isinstance(raw, dict):
            raise ValueError("each document must be an object")
        document = dict(raw)
        _strip(document)
        document_id = document.get("document_id")
        if not isinstance(document_id, str) or not DOCUMENT_ID.fullmatch(document_id):
            raise ValueError("document_id is not a permitted id")
        if document_id in seen:
            raise ValueError("duplicate document id")
        seen.add(document_id)
        if document.get("kind") not in KINDS:
            raise ValueError("document kind is not in the closed list")
        title = document.get("title")
        if not isinstance(title, str) or not title or len(title) > 120 or "\n" in title:
            raise ValueError("title must be a single line of at most 120 characters")
        _line_index(document)
        fields = document.get("fields")
        if not isinstance(fields, list):
            raise ValueError("document fields must be a list")
        if len(fields) > MAX_FIELDS:
            raise ValueError("a document has more fields than this starter will read")
        cleaned.append(document)
    return cleaned


def _facts(pack: dict) -> list[dict]:
    facts = pack.get("facts")
    if not isinstance(facts, list) or not facts:
        raise ValueError("pack has no facts")
    if len(facts) > MAX_FACTS:
        raise ValueError("pack has more facts than this starter will compare")
    seen = set()
    cleaned = []
    for raw in facts:
        if not isinstance(raw, dict):
            raise ValueError("each fact must be an object")
        fact = dict(raw)
        _strip(fact)
        fact_key = fact.get("fact_key")
        if not isinstance(fact_key, str) or not FACT_KEY.fullmatch(fact_key):
            raise ValueError("fact_key is not a permitted id")
        if fact_key in seen:
            raise ValueError("duplicate fact_key")
        seen.add(fact_key)
        if fact.get("field_type") not in FIELD_TYPES:
            raise ValueError("field_type is not in the closed list")
        cleaned.append({"fact_key": fact_key, "field_type": fact["field_type"]})
    return cleaned


def _intake_batch(documents: list[dict], pack_id: str) -> dict:
    files = []
    for document in documents:
        lines = []
        for page in document["pages"]:
            for paragraph in page["paragraphs"]:
                for row in paragraph["lines"]:
                    lines.append(row["text"])
        files.append(
            {
                "file_id": document["document_id"],
                "filename": f"{document['document_id']}.txt",
                "media_type": "text/plain",
                "document_date": document.get("reviewed_on"),
                "content": "\n".join(lines),
            }
        )
    return {
        "synthetic": True,
        "batch_id": pack_id if DOCUMENT_ID.fullmatch(pack_id or "") else "unspecified",
        "requested_purpose": "general_records",
        "files": files,
    }


def _slim_intake(draft: dict) -> dict:
    if draft.get("files_confirmed") is not False or draft.get("purpose_confirmed") is not False:
        raise CompareForbidden("Intake confirmation was not requested and must stay false.")
    files = []
    for row in draft["files"]:
        files.append(
            {
                "file_id": row["file_id"],
                "read_status": row["read_status"],
                "date_status": row["date_status"],
                "age_days": row["age_days"],
                "duplicate_of": row["duplicate_of"],
                "content_recorded": False,
                "finding_count": row["pii"]["finding_count"],
                "entity_types": list(row["pii"]["entity_types"]),
                "output_is_anonymised": False,
            }
        )
    return {
        "called": True,
        "experiment_id": draft["experiment_id"],
        "catalogue_id": draft["catalogue_id"],
        "files_confirmed": False,
        "purpose_confirmed": False,
        "reviewer_decision": None,
        "accepted_into_queue": False,
        "content_recorded": False,
        "catalogue_stale": draft["catalogue_stale"],
        "any_document_not_current": draft["any_document_not_current"],
        "output_is_anonymised": False,
        "files": files,
    }


def _unexpected_identifiers(field_type: str, value: str, propose) -> list[str]:
    proposal = propose(
        value,
        caller=EXPERIMENT_ID,
        apply_model_suggestions=False,
        reversible=False,
    )
    if proposal["anonymisation"]["output_is_anonymised"] is not False:
        raise CompareForbidden("Experiment 08 reported anonymised output. This starter will not use it.")
    if proposal["release"]["agent_may_release"] is not False:
        raise CompareForbidden("Experiment 08 reported a release. This starter will not release text.")
    expected = EXPECTED_FINDINGS.get(field_type, frozenset())
    found = []
    for finding in proposal["audit_log"]["findings"]:
        if finding.get("method") != "deterministic" or not finding.get("applied"):
            continue
        entity = finding["entity_type"]
        if entity in expected:
            continue
        if entity in WITHHOLD or entity not in expected:
            if entity not in found:
                found.append(entity)
    return found


def _scan_lines(documents: list[dict], siblings: dict) -> dict:
    scans = []
    own_hits = []
    for document in documents:
        for page in document["pages"]:
            for paragraph in page["paragraphs"]:
                for row in paragraph["lines"]:
                    scans.append(
                        siblings["intake_scan"](row["text"], file_id=document["document_id"], where="body")
                    )
                    codes = codes_in(row["text"])
                    if codes:
                        own_hits.append(
                            {
                                "document_id": document["document_id"],
                                "page": page["page"],
                                "paragraph": paragraph["paragraph"],
                                "line": row["line"],
                                "patterns": codes,
                                "text_recorded": False,
                            }
                        )
    merged = siblings["intake_merge"](scans)
    phrases = []
    for signal in merged["signals"]:
        phrase = signal.get("phrase")
        if phrase and phrase not in phrases:
            phrases.append(phrase)
    return {
        "detected": bool(merged["detected"] or own_hits),
        "followed": False,
        "intake_phrases": phrases,
        "hits": own_hits,
        "zero_width_removed": merged["zero_width_removed"],
    }


def _occurrences(fact: dict, documents: list[dict], siblings: dict, injection: dict) -> list[dict]:
    propose = siblings["propose"]
    rows = []
    for document in documents:
        for field in document["fields"]:
            if not isinstance(field, dict):
                raise ValueError("each field must be an object")
            field = dict(field)
            _strip(field)
            if field.get("fact_key") != fact["fact_key"]:
                continue
            value = field.get("value")
            if not isinstance(value, str) or len(value) > MAX_VALUE:
                raise ValueError("field value must be a string within the length cap")
            for code in codes_in(value):
                injection["hits"].append(
                    {
                        "document_id": document["document_id"],
                        "page": field.get("page"),
                        "paragraph": field.get("paragraph"),
                        "line": field.get("line"),
                        "patterns": [code],
                        "text_recorded": False,
                    }
                )
                injection["detected"] = True
            page = field.get("page")
            paragraph = field.get("paragraph")
            line = field.get("line")
            if type(page) is not int or type(paragraph) is not int or type(line) is not int:
                raise ValueError("page, paragraph, and line must be integers")
            span = siblings["resolve_span"](document, page, paragraph, line, line)
            pinpoint_ok = span is not None and siblings["citation_normalise"](value) in siblings["citation_normalise"](span)
            citation = {
                "document_id": document["document_id"],
                "document_title": document["title"],
                "kind": document["kind"],
                "page": page,
                "paragraph": paragraph,
                "line_start": line,
                "line_end": line,
                "field": fact["fact_key"],
            }
            row = {
                "citation": citation,
                "quote": span if pinpoint_ok else None,
                "pinpoint_ok": pinpoint_ok,
                "withheld": False,
                "withheld_types": [],
                "used": False,
                "accepted": False,
                "canonical": None,
                "display_fold": None,
            }
            if pinpoint_ok:
                unexpected = _unexpected_identifiers(fact["field_type"], value, propose)
                sensitive = [item for item in unexpected if item in WITHHOLD or item not in EXPECTED_FINDINGS.get(fact["field_type"], frozenset())]
                if sensitive:
                    row["withheld"] = True
                    row["withheld_types"] = sensitive
                    row["quote"] = None
                else:
                    canonical, accepted = normalise_value(fact["field_type"], value)
                    row["used"] = True
                    row["accepted"] = accepted
                    row["canonical"] = canonical
                    row["display_fold"] = display_fold(value)
            rows.append(row)
    return rows


def _class_for(rows: list[dict]) -> tuple[str, str, list[str]]:
    reasons = []
    if any(row["withheld"] for row in rows):
        reasons.append("identifier_withheld")
    if any(not row["pinpoint_ok"] for row in rows):
        reasons.append("pinpoint_failed")
    usable = [row for row in rows if row["used"]]
    if len(usable) < 2:
        reasons.append("fewer_than_two_sources")
    else:
        _klass, reason = classify_values(
            [(row["canonical"], row["display_fold"], row["accepted"]) for row in usable]
        )
        reasons.append(reason)
    ordered = [reason for reason in REASON_PRIORITY if reason in reasons]
    primary = ordered[0]
    if primary in ("same_display", "same_unparsed_text"):
        klass = "match"
    elif primary == "formatting_or_abbreviation":
        klass = "immaterial_difference"
    else:
        klass = "material_discrepancy"
    return klass, primary, ordered[1:]


def _groups(rows: list[dict]) -> list[dict]:
    groups: dict[str, dict] = {}
    for row in rows:
        if not row["used"]:
            continue
        key = row["canonical"] if row["accepted"] else f"unparsed:{row['display_fold']}"
        bucket = groups.setdefault(
            key,
            {
                "canonical": row["canonical"],
                "normaliser_accepted": row["accepted"],
                "citations": [],
            },
        )
        bucket["citations"].append(row["citation"])
    return list(groups.values())


def _apply_resolutions(facts: list[dict], resolutions: dict | None, as_of: str) -> dict:
    if resolutions is None:
        return {"supplied": False, "rejected": []}
    if not isinstance(resolutions, dict):
        raise ValueError("resolutions must be an object")
    payload = dict(resolutions)
    _strip(payload)
    if payload.get("role") != REVIEWER_ROLE:
        raise ValueError("only a Reviewer can record a resolution")
    if payload.get("signed_on") != as_of:
        raise ValueError("signed_on must equal the as-of date")
    reviewer_ref = payload.get("reviewer_ref")
    if not isinstance(reviewer_ref, str) or not REVIEWER_REF.fullmatch(reviewer_ref):
        raise ValueError("reviewer_ref is not a permitted reference")
    items = payload.get("items")
    if not isinstance(items, list):
        raise ValueError("resolutions items must be a list")
    by_key = {fact["fact_key"]: fact for fact in facts}
    seen = set()
    rejected = []
    for raw in items:
        if not isinstance(raw, dict):
            raise ValueError("each resolution item must be an object")
        item = dict(raw)
        _strip(item)
        fact_key = item.get("fact_key")
        choice = item.get("choice")
        if fact_key in seen:
            raise ValueError("a fact_key is repeated in the resolutions")
        seen.add(fact_key)
        fact = by_key.get(fact_key)
        if fact is None or not isinstance(choice, str):
            rejected.append({"fact_key": fact_key if isinstance(fact_key, str) else None, "reason": "unknown_fact"})
            continue
        if not fact["resolution_required"]:
            rejected.append({"fact_key": fact_key, "reason": "not_material"})
            continue
        document_ids = [row["citation"]["document_id"] for row in fact["occurrences"]]
        if choice != "neither" and choice not in document_ids:
            rejected.append({"fact_key": fact_key, "reason": "choice_not_in_sources"})
            continue
        fact["resolved"] = True
        fact["resolved_by"] = REVIEWER_ROLE
        fact["reviewer_choice"] = choice
        fact["reviewer_ref"] = reviewer_ref
    return {"supplied": True, "reviewer_ref": reviewer_ref, "rejected": rejected}


def _force(draft: dict) -> dict:
    draft["agent_chose_source"] = False
    draft["records_edited"] = False
    draft["parties_contacted"] = False
    draft["register_queried"] = False
    draft["model_called"] = False
    draft["network_called"] = False
    draft["foundry_called"] = False
    draft["a3_recommended"] = False
    draft["output_is_anonymised"] = False
    draft["explanation_authored_by_model"] = False
    draft["actions_taken"] = []
    draft["correct_value_written"] = False
    draft["prompt_injection"]["followed"] = False
    for fact in draft["facts"]:
        fact["correct_value"] = None
        fact["agent_chose_source"] = False
        fact["records_edited"] = False
    return draft


def compare(
    pack: dict,
    as_of: str,
    stale_after_days: int = DEFAULT_STALE_AFTER_DAYS,
    resolutions: dict | None = None,
) -> dict:
    """Return a discrepancy list. Material rows stay unresolved unless a Reviewer object says so."""
    if not isinstance(pack, dict):
        raise TypeError("pack must be an object")
    if pack.get("synthetic") is not True:
        raise NotSynthetic("record is not marked synthetic")
    if type(stale_after_days) is not int or stale_after_days < 0:
        raise ValueError("stale_after_days must be a non-negative integer")
    as_of_date = _parse_as_of(as_of)
    working = dict(pack)
    stripped = _strip(working)
    siblings = load()
    documents = _documents(working)
    facts_in = _facts(working)
    known_facts = {fact["fact_key"] for fact in facts_in}
    for document in documents:
        for field in document["fields"]:
            if isinstance(field, dict) and field.get("fact_key") not in known_facts:
                raise ValueError("a field names a fact_key that is not in the pack")
    pack_id = working.get("pack_id")
    if not isinstance(pack_id, str) or not DOCUMENT_ID.fullmatch(pack_id):
        pack_id = "unspecified"
    intake = siblings["intake"](_intake_batch(documents, pack_id), as_of=as_of_date, stale_after_days=stale_after_days)
    if intake.get("actions_taken"):
        raise CompareForbidden("Intake reported an action. This starter will not take it.")
    injection = _scan_lines(documents, siblings)
    sources = source_rows(as_of_date, stale_after_days)
    fact_rows = []
    occurrence_count = 0
    for fact in facts_in:
        rows = _occurrences(fact, documents, siblings, injection)
        occurrence_count += len(rows)
        klass, reason, other = _class_for(rows)
        used = [row for row in rows if row["used"]]
        normaliser_accepted = bool(used) and all(row["accepted"] for row in used)
        stale_documents = []
        for document in documents:
            if any(row["citation"]["document_id"] == document["document_id"] for row in rows):
                block = siblings["document_block_reason"](document, as_of, stale_after_days)
                if block:
                    stale_documents.append({"document_id": document["document_id"], "reason": block})
        resolution_required = klass == "material_discrepancy"
        fact_rows.append(
            {
                "fact_key": fact["fact_key"],
                "field_type": fact["field_type"],
                "classification": klass,
                "reason": reason,
                "other_reasons": other,
                "explanation": EXPLANATIONS[klass],
                "explanation_authored_by_model": False,
                "normaliser_accepted": normaliser_accepted,
                "resolution_required": resolution_required,
                "resolved": False,
                "resolved_by": None,
                "reviewer_choice": None,
                "reviewer_ref": None,
                "correct_value": None,
                "agent_chose_source": False,
                "records_edited": False,
                "shown_to_reviewer": True,
                "do_not_rely": bool(stale_documents),
                "stale_documents": stale_documents,
                "groups": _groups(rows),
                "occurrences": rows,
            }
        )
    resolution_record = _apply_resolutions(fact_rows, resolutions, as_of)
    counts = {
        "fact_count": len(fact_rows),
        "match_count": sum(1 for fact in fact_rows if fact["classification"] == "match"),
        "immaterial_count": sum(1 for fact in fact_rows if fact["classification"] == "immaterial_difference"),
        "material_count": sum(1 for fact in fact_rows if fact["classification"] == "material_discrepancy"),
        "occurrence_count": occurrence_count,
    }
    if counts["match_count"] + counts["immaterial_count"] + counts["material_count"] != counts["fact_count"]:
        raise RuntimeError("fact classes do not add up to fact_count")
    material = [fact for fact in fact_rows if fact["resolution_required"]]
    all_material_resolved = all(fact["resolved"] for fact in material) if material else True
    pins_stale = any(row["stale"] for row in sources)
    documents_stale = any(fact["do_not_rely"] for fact in fact_rows)
    intake_view = _slim_intake(intake)
    do_not_rely = pins_stale or documents_stale or intake_view["catalogue_stale"] or intake_view["any_document_not_current"]
    for fact in fact_rows:
        if do_not_rely:
            fact["do_not_rely"] = True
    draft = {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment_id": EXPERIMENT_ID,
        "autonomy": AUTONOMY,
        "pack_id": pack_id,
        "as_of": as_of,
        "stale_after_days": stale_after_days,
        "counts": counts,
        "counts_note": "occurrence_count is not included in fact_count. other_reasons are not extra facts.",
        "awaiting_reviewer": not all_material_resolved,
        "all_material_resolved": all_material_resolved,
        "do_not_rely": do_not_rely,
        "pins_stale": pins_stale,
        "live_register": False,
        "register_queried": False,
        "agent_chose_source": False,
        "records_edited": False,
        "parties_contacted": False,
        "correct_value_written": False,
        "model_called": False,
        "network_called": False,
        "foundry_called": False,
        "a3_recommended": False,
        "output_is_anonymised": False,
        "explanation_authored_by_model": False,
        "actions_taken": [],
        "prohibited_payload_keys": stripped,
        "prompt_injection": injection,
        "intake": intake_view,
        "redaction": {
            "called": True,
            "experiment_id": siblings["gateway_experiment_id"],
            "output_is_anonymised": False,
            "agent_may_release": False,
            "model_suggestions_applied": False,
            "withheld_occurrences": sum(1 for fact in fact_rows for row in fact["occurrences"] if row["withheld"]),
        },
        "pinpoint": {
            "experiment_id": siblings["citation_experiment_id"],
            "span_check": "resolve_span",
            "containment": "citation normalise",
        },
        "resolution": resolution_record,
        "facts": fact_rows,
        "sources": sources,
        "human_approval": {
            "reviewer_resolves_each_material_discrepancy": True,
            "agent_marked_any_approval_done": False,
            "stale_sources_reopened_by_agent": False,
            "records_corrected_by_agent": False,
            "lawful_basis_chosen_by_agent": False,
        },
        "limitations": list(LIMITATIONS),
    }
    return _force(draft)


def _load(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compare synthetic source fields. Experiment 36.")
    parser.add_argument("--pack", type=Path)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--stale-after-days", type=int, default=DEFAULT_STALE_AFTER_DAYS)
    parser.add_argument("--resolutions", type=Path)
    parser.add_argument("--choose-source", action="store_true")
    parser.add_argument("--edit-record", action="store_true")
    parser.add_argument("--contact", action="store_true")
    parser.add_argument("--lookup-register", action="store_true")
    parser.add_argument("--recommend-a3", action="store_true")
    args = parser.parse_args(argv)
    prohibited = (
        (args.choose_source, choose_source),
        (args.edit_record, edit_record),
        (args.contact, contact_party),
        (args.lookup_register, lookup_register),
        (args.recommend_a3, recommend_a3),
    )
    for flagged, function in prohibited:
        if flagged:
            try:
                function()
            except CompareForbidden as exc:
                print(str(exc), file=sys.stderr)
                return 2
    if args.pack is None:
        print("A pack path is required.", file=sys.stderr)
        return 1
    try:
        resolutions = _load(args.resolutions) if args.resolutions else None
        draft = compare(
            _load(args.pack),
            args.as_of,
            args.stale_after_days,
            resolutions=resolutions,
        )
    except (NotSynthetic, CompareForbidden) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    json.dump(draft, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
