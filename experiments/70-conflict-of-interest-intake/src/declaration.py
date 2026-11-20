"""Draft a conflict-of-interest declaration. Do not decide that one exists.

The declarant confirms the exact draft hash. Only then is a copy written to
the synthetic staging store. The ethics or procurement team records any
disposition. The agent does not clear, exclude, or approve anyone, and it
does not send.
"""

from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from datetime import date
from pathlib import Path

if __package__ in {None, ""}:
    from cues import read_cues
    from marking import (
        above_ceiling,
        content_markings,
        higher_marking,
        legal_hold,
        metadata_markings,
        retention_labels,
    )
    from mask import mask_text
    from match import (
        digest,
        extract_amounts,
        extract_dates,
        mentioned_procurement_ids,
        mentioned_supplier_ids,
        parse_iso,
        procurement_view,
        source_note,
    )
    from reuse import NeighbourMissing, case_categories, case_injection, intake, propose
    from sources import statute_context
else:
    from .cues import read_cues
    from .marking import (
        above_ceiling,
        content_markings,
        higher_marking,
        legal_hold,
        metadata_markings,
        retention_labels,
    )
    from .mask import mask_text
    from .match import (
        digest,
        extract_amounts,
        extract_dates,
        mentioned_procurement_ids,
        mentioned_supplier_ids,
        parse_iso,
        procurement_view,
        source_note,
    )
    from .reuse import NeighbourMissing, case_categories, case_injection, intake, propose
    from .sources import statute_context

LABEL = "DECLARATION DRAFT FOR THE ETHICS TEAM"
CATALOGUE_ID = "L005"
EXPERIMENT_ID = "exp-70-conflict-of-interest-intake"
ROOT = Path(__file__).resolve().parents[1]
MAX_CHARS = 20_000
_STORE: dict[str, dict] = {}
_PROHIBITED = (
    "human_approval",
    "approved",
    "approval",
    "conflict_exists",
    "person_cleared",
    "person_excluded",
    "person_approved",
    "supplier_excluded",
    "sent",
    "role",
    "clearance",
    "marked_acceptable",
    "disposition",
    "staged",
)


class DeclarationForbidden(RuntimeError):
    """The agent does not decide, clear, exclude, approve, or send."""


class NotSynthetic(ValueError):
    """The record is not marked synthetic."""


def decide_conflict(*_args, **_kwargs) -> None:
    raise DeclarationForbidden("The agent does not decide whether a conflict exists.")


def clear_person(*_args, **_kwargs) -> None:
    raise DeclarationForbidden("The agent does not clear a person.")


def exclude_person(*_args, **_kwargs) -> None:
    raise DeclarationForbidden("The agent does not exclude a person.")


def exclude_supplier(*_args, **_kwargs) -> None:
    raise DeclarationForbidden("The agent does not exclude a supplier.")


def approve_person(*_args, **_kwargs) -> None:
    raise DeclarationForbidden("The agent does not approve a person.")


def send(*_args, **_kwargs) -> None:
    raise DeclarationForbidden("The agent does not send.")


def write_production(*_args, **_kwargs) -> None:
    raise DeclarationForbidden("The agent does not write a production record.")


def reset_staging() -> None:
    _STORE.clear()


def _load_json(name: str) -> dict:
    return json.loads((ROOT / "fixtures" / name).read_text(encoding="utf-8"))


def pinned_sources() -> dict:
    return {
        "suppliers": _load_json("suppliers.json"),
        "register": _load_json("register.json"),
        "directory": _load_json("directory.json"),
        "criteria": _load_json("criteria.json"),
    }


def _people(directory: dict) -> list[dict]:
    rows = directory.get("people") if isinstance(directory, dict) else None
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict)]


def _person(directory: dict, ref: object) -> dict | None:
    if not isinstance(ref, str):
        return None
    for row in _people(directory):
        if row.get("employee_ref") == ref:
            return row
    return None


def _review(document: dict, on: date) -> dict:
    raw = document.get("review_due") if isinstance(document, dict) else None
    parsed = parse_iso(raw)
    if not isinstance(raw, str) or parsed is None:
        return {"review_due": None, "stale": None, "unreadable": True, "coerced": False}
    return {
        "review_due": parsed.isoformat(),
        "stale": parsed <= on,
        "unreadable": False,
        "coerced": False,
    }


def _force(result: dict) -> None:
    result["conflict_exists"] = None
    result["person_cleared"] = False
    result["person_excluded"] = False
    result["person_approved"] = False
    result["supplier_excluded"] = False
    result["marked_acceptable"] = False
    result["mitigation_decided_by_agent"] = False
    result["conflicts_assessment_prepared"] = False
    result["sent"] = False
    result["production_written"] = False
    result["coerced"] = False
    result["instructions_followed"] = False
    result["described_as_anonymised"] = False
    result["criteria_applied"] = False
    result["body_copied"] = False
    injection = result.get("prompt_injection")
    if isinstance(injection, dict):
        injection["followed"] = False


def _projection(result: dict) -> dict:
    declaration = result.get("declaration") or {}
    return {
        "declaration_id": result.get("declaration_id"),
        "declarant_ref": result.get("declarant_ref"),
        "as_of": result.get("as_of"),
        "outcome": result.get("outcome"),
        "interest_types": declaration.get("interest_types"),
        "financial_or_non_financial": declaration.get("financial_or_non_financial"),
        "direct_or_indirect": declaration.get("direct_or_indirect"),
        "parties": declaration.get("parties"),
        "dates": declaration.get("dates"),
        "amounts": declaration.get("amounts"),
        "none_declared": declaration.get("none_declared"),
        "potential_links": result.get("potential_links"),
        "missing_question_ids": result.get("missing_question_ids"),
        "minimisation": result.get("minimisation"),
        "marking": result.get("marking"),
        "legal_hold": result.get("legal_hold"),
        "retention_labels": result.get("retention_labels"),
        "carve_out": result.get("carve_out"),
        "criteria_flagged": result.get("criteria_flagged"),
        "instruction_detected": (result.get("prompt_injection") or {}).get("detected"),
        "human_route": result.get("human_route"),
    }


def _hash(result: dict) -> str:
    return digest(_projection(result))


def _blank(outcome: str, *, declaration_id, declarant_ref, as_of, reason: str | None = None) -> dict:
    result = {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment_id": EXPERIMENT_ID,
        "autonomy": "A1",
        "outcome": outcome,
        "blocked_reason": reason,
        "declaration_id": declaration_id if isinstance(declaration_id, str) else None,
        "declarant_ref": declarant_ref if isinstance(declarant_ref, str) else None,
        "as_of": as_of,
        "directory_role": None,
        "self_declared_role_ignored": False,
        "self_declared_clearance_ignored": False,
        "routine_processing": False,
        "declaration": None,
        "missing_questions": [],
        "missing_question_ids": [],
        "potential_links": [],
        "not_live": [],
        "minimisation": {
            "body_copied": False,
            "detail_copied": False,
            "family_link": False,
            "family_is_article_9": False,
            "special_category": [],
            "described_as_anonymised": False,
        },
        "mask": None,
        "marking": None,
        "legal_hold": False,
        "legal_hold_unparseable": False,
        "retention_labels": [],
        "retention_unparseable": False,
        "quotes_withheld": False,
        "carve_out": False,
        "criteria_flagged": False,
        "no_conflict_asserted_by_declarant": False,
        "assertion_adopted": False,
        "human_route": None,
        "prompt_injection": {"detected": False, "followed": False, "signals": []},
        "prohibited_payload_keys": [],
        "caller_sources": {},
        "register_review": None,
        "sources_current": False,
        "may_be_relied_on": False,
        "staged": False,
        "human_approval": None,
        "disposition": None,
        "mitigation": None,
        "model_called": False,
        "network_called": False,
        "statute_context": statute_context(),
        "experiment_08": {"called": False},
        "experiment_12": {"called": False, "files_confirmed": False, "purpose_confirmed": False},
        "experiment_32": {"called": False, "narrative_copied": False},
        "required_acknowledgements": ["pins_seen"],
        "limitations": _limitations(),
    }
    _force(result)
    result["declaration_hash"] = _hash(result)
    return result


def _limitations() -> list[str]:
    return [
        "Cue and interest matching is a stem list. A sentence that uses none of the stems is not flagged.",
        "A 'not' within eight words before an interest phrase can hide a match. That is the negation rule, not a clearance.",
        "Marking denial is narrower, so a SECRET cover is kept when the sentence says not to downgrade it.",
        "Family relationships are minimised. They are not in the Article 9(1) list that was opened.",
        "Section 81, section 82, section 83, Article 5, and Article 9 had no 'up to date on or before' date in the extract opened on 20 November 2026. Currency is unverified.",
        "Treating a register as stale on its review-due date is this starter's rule. It is not a statutory period.",
        "The small-number threshold is a starter control. It is not anonymisation. The ICO anonymisation guidance was not opened.",
        "The marking order is a starter rule. The Government Security Classifications Policy was not re-opened.",
        "Experiment 12's document window is that experiment's rule.",
        "Phone numbers, email addresses, dates of birth, street addresses, postcodes, and 'my name is' or a title plus a surname are counted. The values are not stored.",
        "A name with no title and no 'my name is' or 'my wife is' is not counted by this mask.",
        "This is not a conflicts assessment under section 83, and it is not a decision under section 81 or section 82.",
    ]


def _strip(request: dict) -> list[str]:
    removed = []
    for key in list(request):
        if key in _PROHIBITED:
            removed.append(key)
            request.pop(key, None)
    return removed


def _questions(cues: dict, dates: dict, amounts: dict, parties: list, links: list, named: list) -> list[dict]:
    questions = []

    def add(question_id: str, text: str) -> None:
        questions.append({"question_id": question_id, "question": text})

    if cues["nature_conflict"]:
        add("interest_nature_conflict", "The declaration states both a financial and a non-financial interest. Which should the ethics team read?")
    elif cues["financial_or_non_financial"] is None and not cues["none_declared"]:
        add("interest_nature", "Is the interest financial or non-financial?")
    if not parties and not cues["none_declared"]:
        add("parties", "Who are the parties?")
    if not named and not links:
        add("procurement_or_contract", "Which procurement or contract is affected?")
    elif links and not any(row.get("declarant_named_procurement") for row in links):
        add("confirm_live_link", "A live procurement on the pinned register matches a named supplier. Is that the procurement you mean?")
    if not dates["dates"] and dates["unparseable_count"] == 0 and not cues["none_declared"]:
        add("dates", "What dates apply to the interest?")
    if dates["unparseable_count"]:
        add("dates_unreadable", "A date could not be read. What is the date? It has not been replaced with today.")
    if cues["financial"] and not amounts["amounts"] and amounts["unparseable_count"] == 0:
        add("amount", "What is the financial value?")
    if amounts["unparseable_count"]:
        add("amount_unreadable", "An amount could not be read. It has not been replaced with zero.")
    if cues["direction_conflict"]:
        add("direct_or_indirect_conflict", "The declaration states both a direct and an indirect interest. The starter has not chosen.")
    elif cues["direct_or_indirect"] is None and not cues["none_declared"]:
        add("direct_or_indirect", "Is the interest direct or indirect?")
    return questions


def _route_reason(cues: dict) -> dict | None:
    codes = []
    if cues["distress"]:
        codes.append("distress")
    if cues["whistleblowing"]:
        codes.append("whistleblowing")
    if cues["grievance"]:
        codes.append("grievance")
    if cues["special_category"]:
        codes.append("special_category")
    if not codes:
        return None
    return {
        "reason_code": codes[0],
        "also": codes[1:],
        "cue_text_copied": False,
        "routine": False,
    }


def _mask_report(text: str) -> dict:
    _masked, report = mask_text(text)
    report["masked_text_included"] = False
    return report


def _experiment_08(text: str) -> dict:
    try:
        proposal = propose()(text, caller="exp-70-conflict-of-interest-intake", reversible=False)
    except NeighbourMissing:
        return {"called": False, "reason": "neighbour_missing", "redacted_text_copied": False, "output_is_anonymised": False}
    findings = ((proposal.get("audit_log") or {}).get("findings")) or []
    return {
        "called": True,
        "catalogue_id": "O005",
        "finding_count": len(findings),
        "output_is_anonymised": False,
        "redacted_text_copied": False,
        "values_stored": False,
        "reversible_requested": False,
    }


def _experiment_12(declaration_id: str, text: str, on: date) -> dict:
    try:
        draft = intake()(
            {
                "synthetic": True,
                "batch_id": declaration_id if isinstance(declaration_id, str) else "declaration",
                "files": [{
                    "file_id": "declaration",
                    "filename": "declaration.txt",
                    "media_type": "text/plain",
                    "content": text,
                }],
            },
            as_of=on,
        )
    except NeighbourMissing:
        return {"called": False, "reason": "neighbour_missing", "files_confirmed": False, "purpose_confirmed": False}
    files = draft.get("files") or [{}]
    row = files[0] if files else {}
    return {
        "called": True,
        "catalogue_id": "O001",
        "files_confirmed": False,
        "purpose_confirmed": False,
        "read_status": row.get("read_status"),
        "content_recorded": False,
        "intake_draft_copied": False,
        "injection_followed": False,
        "note": "Experiment 12 does not confirm the file and does not confirm a purpose. Its stale window is that experiment's rule.",
    }


def _experiment_32(text: str) -> dict:
    try:
        categories = case_categories()
        injection = case_injection()
        hits = categories.keyword_hits(text)
        indicators = categories.special_category_indicators(text)
        scan = injection.scan_narrative(text)
    except NeighbourMissing:
        return {"called": False, "reason": "neighbour_missing", "narrative_copied": False}
    if __package__ in {None, ""}:
        from negate import affirmed
    else:
        from .negate import affirmed
    affirmed_categories = []
    for category, words in hits.items():
        if any(affirmed(text, word) for word in words):
            affirmed_categories.append(category)
    not_applied = [label for label in indicators if label not in read_cues(text)["special_category"]]
    return {
        "called": True,
        "catalogue_id": "H009",
        "categories_affirmed": affirmed_categories,
        "special_category_not_applied": not_applied,
        "injection_detected": bool(scan.get("detected")),
        "injection_followed": False,
        "narrative_copied": False,
        "draft_case_called": False,
        "note": "Keyword hits are passed through this starter's negation. A denied phrase is not an inclusion. draft_case() is not called.",
    }


def _callers(request: dict, supplied: dict, pinned: dict) -> dict:
    notes = {
        "suppliers_argument": source_note(
            pinned["suppliers"], supplied.get("suppliers"), row_key="suppliers", id_field="supplier_id",
        ),
        "register_argument": source_note(
            pinned["register"], supplied.get("register"), row_key="procurements", id_field="procurement_id",
        ),
        "directory_argument": source_note(
            pinned["directory"], supplied.get("directory"), row_key="people", id_field="employee_ref",
        ),
        "criteria_argument": source_note(pinned["criteria"], supplied.get("criteria"), row_key=None, id_field=None),
        "suppliers_in_request": source_note(
            pinned["suppliers"], request.get("supplier_list"), row_key="suppliers", id_field="supplier_id",
        ),
        "register_in_request": source_note(
            pinned["register"], request.get("procurement_register"), row_key="procurements", id_field="procurement_id",
        ),
        "directory_in_request": source_note(
            pinned["directory"], request.get("directory"), row_key="people", id_field="employee_ref",
        ),
        "criteria_in_request": source_note(pinned["criteria"], request.get("criteria"), row_key=None, id_field=None),
    }
    differs = any(note["differs"] for note in notes.values())
    return {"differs": differs, "used": "pinned", "parts": notes}


def draft_declaration(request: dict, suppliers: dict, register: dict, directory: dict, criteria: dict, as_of: str) -> dict:
    """Return a draft. human_approval stays null. Nothing is staged."""

    if not isinstance(request, dict):
        raise TypeError("request must be an object")
    working = dict(request)
    removed = _strip(working)
    if working.get("synthetic") is not True:
        raise NotSynthetic("record is not marked synthetic")
    declaration_id = working.get("declaration_id")
    declarant_ref = working.get("declarant_ref")
    on = parse_iso(as_of)
    if on is None:
        result = _blank(
            "as_of_unreadable",
            declaration_id=declaration_id,
            declarant_ref=declarant_ref,
            as_of=None,
            reason="as_of_unreadable",
        )
        result["prohibited_payload_keys"] = removed
        _force(result)
        result["declaration_hash"] = _hash(result)
        return result
    if not isinstance(declaration_id, str) or not declaration_id or len(declaration_id) > 40 or not declaration_id.replace("-", "").isalnum():
        result = _blank("declaration_id_unreadable", declaration_id=None, declarant_ref=declarant_ref, as_of=on.isoformat(), reason="declaration_id_unreadable")
        result["prohibited_payload_keys"] = removed
        _force(result)
        result["declaration_hash"] = _hash(result)
        return result

    pinned = pinned_sources()
    callers = _callers(
        working,
        {"suppliers": suppliers, "register": register, "directory": directory, "criteria": criteria},
        pinned,
    )
    suppliers = pinned["suppliers"]
    register = pinned["register"]
    directory = pinned["directory"]
    criteria = pinned["criteria"]
    text = working.get("text")
    metadata = working.get("metadata") if isinstance(working.get("metadata"), dict) else {}
    meta_marks, meta_bad = metadata_markings(metadata.get("protective_marking"))
    content_marks = content_markings(text if isinstance(text, str) else "")
    marking = higher_marking(meta_marks + content_marks)
    hold, hold_bad = legal_hold(metadata.get("legal_hold"), text if isinstance(text, str) else "")
    retention, retention_bad = retention_labels(metadata.get("retention"), text if isinstance(text, str) else "")
    reviews = {
        "suppliers": _review(suppliers, on),
        "register": _review(register, on),
        "criteria": _review(criteria, on),
    }
    stale = any(item["stale"] is True for item in reviews.values())
    review_unreadable = any(item["unreadable"] for item in reviews.values())

    def finish(result: dict) -> dict:
        result["prohibited_payload_keys"] = removed
        result["caller_sources"] = callers
        result["register_review"] = reviews
        result["sources_current"] = False
        result["may_be_relied_on"] = False
        result["marking"] = {
            "metadata": meta_marks,
            "content": content_marks,
            "applied": marking,
            "metadata_unreadable": meta_bad,
            "order_is_a_starter_rule": True,
        }
        result["legal_hold"] = hold
        result["legal_hold_unparseable"] = hold_bad
        result["retention_labels"] = retention
        result["retention_unparseable"] = retention_bad
        result["staged"] = False
        result["human_approval"] = None
        acks = ["pins_seen"]
        if stale or review_unreadable:
            acks.append("register_seen")
        if callers["differs"]:
            acks.append("sources_seen")
        if result.get("criteria_flagged"):
            acks.append("criteria_seen")
        if result.get("carve_out"):
            acks.append("carve_out_seen")
        result["required_acknowledgements"] = acks
        result["statute_context"] = statute_context()
        _force(result)
        result["declaration_hash"] = _hash(result)
        return result

    person = _person(directory, declarant_ref)
    if person is None:
        return finish(_blank("not_in_directory", declaration_id=declaration_id, declarant_ref=declarant_ref, as_of=on.isoformat(), reason="not_in_directory"))
    role = person.get("role")
    if role == "guest":
        result = _blank("guest_not_a_declarant", declaration_id=declaration_id, declarant_ref=declarant_ref, as_of=on.isoformat(), reason="guest")
        result["directory_role"] = "guest"
        return finish(result)
    if role != "staff":
        result = _blank("not_a_staff_declarant", declaration_id=declaration_id, declarant_ref=declarant_ref, as_of=on.isoformat(), reason="role")
        result["directory_role"] = role if isinstance(role, str) else None
        return finish(result)
    ceiling = person.get("clearance") if isinstance(person.get("clearance"), str) else None
    if not isinstance(text, str):
        result = _blank("text_unreadable", declaration_id=declaration_id, declarant_ref=declarant_ref, as_of=on.isoformat(), reason="text_unreadable")
        result["directory_role"] = "staff"
        return finish(result)
    if text == "":
        result = _blank("text_missing", declaration_id=declaration_id, declarant_ref=declarant_ref, as_of=on.isoformat(), reason="text_missing")
        result["directory_role"] = "staff"
        return finish(result)
    if len(text) > MAX_CHARS:
        result = _blank("text_too_long", declaration_id=declaration_id, declarant_ref=declarant_ref, as_of=on.isoformat(), reason="text_too_long")
        result["directory_role"] = "staff"
        result["body_copied"] = False
        return finish(result)

    cues = read_cues(text)
    route = _route_reason(cues)
    dates = extract_dates(text)
    amounts = extract_amounts(text)
    supplier_ids = mentioned_supplier_ids(text, suppliers)
    named_ids = mentioned_procurement_ids(text)
    view = procurement_view(register, supplier_ids, named_ids, on)
    parties = [
        {"kind": "supplier", "supplier_id": supplier_id, "name_copied": False}
        for supplier_id in supplier_ids
    ]
    questions = _questions(cues, dates, amounts, parties, view["potential_links"], named_ids)
    withheld = above_ceiling(marking, ceiling)
    if withheld:
        view = {"potential_links": [], "not_live": [], "unreadable_rows": view["unreadable_rows"], "unknown_procurement_ids": []}
        parties = []
        dates = {"dates": [], "unparseable_count": dates["unparseable_count"], "raw_stored": False, "coerced": False}
        amounts = {"amounts": [], "unparseable_count": amounts["unparseable_count"], "raw_stored": False, "coerced": False}
        questions = [{"question_id": "withheld", "question": "The marking is above the directory clearance. The ethics team has the original. This draft does not copy it."}]
    declaration = {
        "interest_types": [] if withheld else cues["interest_types"],
        "financial_or_non_financial": None if withheld else cues["financial_or_non_financial"],
        "nature_conflict": False if withheld else cues["nature_conflict"],
        "direct_or_indirect": None if withheld else cues["direct_or_indirect"],
        "direction_conflict": False if withheld else cues["direction_conflict"],
        "parties": parties,
        "procurement_or_contract_named": [] if withheld else named_ids,
        "dates": dates["dates"],
        "date_unparseable_count": dates["unparseable_count"],
        "amounts": amounts["amounts"],
        "amount_unparseable_count": amounts["unparseable_count"],
        "none_declared": False if withheld else cues["none_declared"],
        "raw_stored": False,
    }
    outcome = "human_route" if route and not withheld else "draft"
    if withheld:
        outcome = "withheld"
        also = []
        if route:
            also = [route["reason_code"], *route["also"]]
        route = {
            "reason_code": "above_clearance",
            "also": also,
            "cue_text_copied": False,
            "routine": False,
        }
    result = _blank(outcome, declaration_id=declaration_id, declarant_ref=declarant_ref, as_of=on.isoformat())
    result["directory_role"] = "staff"
    result["directory_clearance"] = ceiling
    result["self_declared_role_ignored"] = cues["self_declared_role"]
    result["self_declared_clearance_ignored"] = cues["self_declared_clearance"]
    result["routine_processing"] = outcome == "draft"
    result["declaration"] = declaration
    result["missing_questions"] = questions
    result["missing_question_ids"] = [item["question_id"] for item in questions]
    result["potential_links"] = view["potential_links"]
    result["not_live"] = view["not_live"]
    result["unreadable_register_rows"] = view["unreadable_rows"]
    result["unknown_procurement_ids"] = view["unknown_procurement_ids"]
    result["minimisation"] = {
        "body_copied": False,
        "detail_copied": False,
        "family_link": bool(cues["family_labels"]) and not withheld,
        "family_labels": [] if withheld else cues["family_labels"],
        "family_is_article_9": False,
        "special_category": [] if withheld else cues["special_category"],
        "special_category_text_copied": False,
        "described_as_anonymised": False,
    }
    result["mask"] = _mask_report(text)
    result["quotes_withheld"] = withheld
    result["carve_out"] = bool(cues["carve_out"]) and not withheld
    result["criteria_flagged"] = bool(cues["biased"]) and not withheld
    result["no_conflict_asserted_by_declarant"] = bool(cues["no_conflict_asserted"])
    result["assertion_adopted"] = False
    result["human_route"] = route
    result["prompt_injection"] = {
        "detected": bool(cues["instructions"]),
        "followed": False,
        "signals": [{"phrase": phrase, "followed": False} for phrase in cues["instructions"]],
    }
    result["experiment_08"] = _experiment_08(text)
    result["experiment_12"] = _experiment_12(declaration_id, text, on)
    result["experiment_32"] = _experiment_32(text)
    if route and any(code in {"whistleblowing", "grievance", "distress"} for code in [route["reason_code"], *route["also"]]):
        extra = result["experiment_32"].get("categories_affirmed") or []
        if "protected_disclosure" in extra and "whistleblowing" not in [route["reason_code"], *route["also"]]:
            route["also"].append("whistleblowing")
    result["pinned_register_sha256"] = digest(register)
    result["threshold_from_criteria"] = criteria.get("small_number_threshold")
    return finish(result)


def _reject(draft: dict, reason: str) -> dict:
    result = deepcopy(draft) if isinstance(draft, dict) else _blank("unreadable", declaration_id=None, declarant_ref=None, as_of=None, reason=reason)
    result["blocked_reason"] = reason
    result["staged"] = False
    result["human_approval"] = None
    result["disposition"] = None
    _force(result)
    return result


def _acks_ok(draft: dict, approval: dict) -> str | None:
    for ack in draft.get("required_acknowledgements") or []:
        if approval.get(ack) is not True:
            return f"{ack}_required"
    return None


def confirm_declaration(draft: dict, directory: dict, approval: dict) -> dict:
    """The declarant confirms this exact hash. The synthetic store then keeps a copy.

    A sentence in the declaration is not this step. A tampered draft is rejected.
    """

    if not isinstance(draft, dict):
        raise TypeError("draft must be an object")
    pinned = pinned_sources()["directory"]
    if digest(directory) != digest(pinned):
        return _reject(draft, "directory_not_pinned")
    if not isinstance(approval, dict):
        return _reject(draft, "approval_unreadable")
    if draft.get("outcome") != "draft":
        return _reject(draft, "not_a_draft")
    if approval.get("item") != "declaration-confirm" or approval.get("decision") != "confirm":
        return _reject(draft, "item_mismatch")
    if approval.get("declaration_id") != draft.get("declaration_id"):
        return _reject(draft, "declaration_mismatch")
    recomputed = _hash(draft)
    if draft.get("declaration_hash") != recomputed:
        return _reject(draft, "content_tampered")
    if approval.get("declaration_hash") != recomputed:
        return _reject(draft, "declaration_hash_mismatch")
    person = _person(pinned, approval.get("approver_ref"))
    if person is None or person.get("role") != "staff" or person.get("employee_ref") != draft.get("declarant_ref"):
        return _reject(draft, "not_the_declarant")
    missing = _acks_ok(draft, approval)
    if missing:
        return _reject(draft, missing)
    existing = _STORE.get(draft["declaration_id"])
    if existing is not None:
        if existing.get("declaration_hash") == recomputed:
            return deepcopy(existing)
        return _reject(draft, "already_staged")
    stored = deepcopy(draft)
    stored["staged"] = True
    stored["blocked_reason"] = None
    stored["human_approval"] = {
        "approver_ref": person["employee_ref"],
        "directory_role": "staff",
        "item": "declaration-confirm",
        "declaration_id": draft["declaration_id"],
        "declaration_hash": recomputed,
        "store": "synthetic_staging",
        "production_written": False,
    }
    stored["staged_hash"] = digest({
        "declaration_hash": recomputed,
        "legal_hold": stored.get("legal_hold"),
        "retention_labels": stored.get("retention_labels"),
        "marking": stored.get("marking"),
    })
    _force(stored)
    stored["staged"] = True
    stored["human_approval"] = {
        "approver_ref": person["employee_ref"],
        "directory_role": "staff",
        "item": "declaration-confirm",
        "declaration_id": draft["declaration_id"],
        "declaration_hash": recomputed,
        "staged_hash": stored["staged_hash"],
        "store": "synthetic_staging",
        "production_written": False,
    }
    _STORE[draft["declaration_id"]] = deepcopy(stored)
    return deepcopy(stored)


def record_disposition(directory: dict, decision: dict) -> dict:
    """Record the ethics or procurement decision. Do not apply it."""

    pinned = pinned_sources()["directory"]
    if not isinstance(decision, dict):
        return _reject({}, "decision_unreadable")
    if digest(directory) != digest(pinned):
        return _reject({}, "directory_not_pinned")
    if decision.get("item") != "disposition" or decision.get("decision") != "record":
        return _reject({}, "item_mismatch")
    stored = _STORE.get(decision.get("declaration_id"))
    if stored is None:
        return _reject({}, "not_staged")
    if decision.get("declaration_hash") != stored.get("declaration_hash"):
        return _reject(stored, "declaration_hash_mismatch")
    if decision.get("staged_hash") != stored.get("staged_hash"):
        return _reject(stored, "staged_hash_mismatch")
    person = _person(pinned, decision.get("approver_ref"))
    if person is None or person.get("role") not in {"ethics", "procurement"}:
        return _reject(stored, "not_ethics_or_procurement")
    text = decision.get("disposition_text")
    if not isinstance(text, str) or not text.strip() or len(text) > 500:
        return _reject(stored, "disposition_unreadable")
    if decision.get("disposition_hash") != digest(text):
        return _reject(stored, "disposition_hash_mismatch")
    mitigation = decision.get("mitigation_text", None)
    mitigation_record = None
    if mitigation is not None:
        if not isinstance(mitigation, str) or not mitigation.strip() or len(mitigation) > 500:
            return _reject(stored, "mitigation_unreadable")
        if decision.get("mitigation_hash") != digest(mitigation):
            return _reject(stored, "mitigation_hash_mismatch")
        mitigation_record = {
            "text": mitigation.strip(),
            "text_hash": digest(mitigation),
            "applied": False,
            "decided_by_agent": False,
        }
    updated = deepcopy(stored)
    updated["disposition"] = {
        "recorded": True,
        "by": person["employee_ref"],
        "directory_role": person["role"],
        "text": text.strip(),
        "text_hash": digest(text),
        "interpreted": False,
        "conflict_exists": None,
        "person_cleared": False,
        "person_excluded": False,
        "person_approved": False,
        "supplier_excluded": False,
    }
    updated["mitigation"] = mitigation_record
    updated["blocked_reason"] = None
    updated["human_approval"] = {
        "approver_ref": person["employee_ref"],
        "directory_role": person["role"],
        "item": "disposition",
        "declaration_id": stored["declaration_id"],
        "declaration_hash": stored["declaration_hash"],
        "staged_hash": stored["staged_hash"],
        "interpreted": False,
    }
    updated["declarant_confirmation"] = stored.get("human_approval")
    _force(updated)
    updated["staged"] = True
    _STORE[stored["declaration_id"]] = deepcopy(updated)
    return deepcopy(updated)


def record_route_seen(draft: dict, directory: dict, seen: dict) -> dict:
    """Record that a person has seen a route. This does not decide the declaration."""

    if not isinstance(draft, dict):
        raise TypeError("draft must be an object")
    pinned = pinned_sources()["directory"]
    if digest(directory) != digest(pinned):
        return _reject(draft, "directory_not_pinned")
    if not isinstance(seen, dict):
        return _reject(draft, "decision_unreadable")
    if draft.get("outcome") != "human_route":
        return _reject(draft, "not_a_route")
    if seen.get("item") != "human-route" or seen.get("decision") != "seen":
        return _reject(draft, "item_mismatch")
    route = draft.get("human_route") or {}
    if seen.get("reason_code") != route.get("reason_code"):
        return _reject(draft, "reason_mismatch")
    if seen.get("declaration_hash") != draft.get("declaration_hash") or draft.get("declaration_hash") != _hash(draft):
        return _reject(draft, "declaration_hash_mismatch")
    person = _person(pinned, seen.get("approver_ref"))
    if person is None or person.get("role") not in {"ethics", "procurement"}:
        return _reject(draft, "not_ethics_or_procurement")
    updated = deepcopy(draft)
    updated["route_seen"] = {
        "recorded": True,
        "approver_ref": person["employee_ref"],
        "directory_role": person["role"],
        "reason_code": route.get("reason_code"),
        "conflict_exists": None,
        "cue_text_copied": False,
    }
    updated["blocked_reason"] = None
    updated["staged"] = False
    _force(updated)
    return updated


def team_counts(directory: dict, requester_ref: str) -> dict:
    """Counts for the ethics or procurement team. Small numbers are suppressed.

    The threshold is the pinned criteria value. A caller-supplied threshold is
    not used. Suppression is not anonymisation.
    """

    pinned = pinned_sources()
    if digest(directory) != digest(pinned["directory"]):
        return {
            "outcome": "directory_not_pinned",
            "rows": [],
            "people_listed": False,
            "declarant_refs_included": False,
            "suppression_is_not_anonymisation": True,
            "coerced": False,
        }
    person = _person(pinned["directory"], requester_ref)
    if person is None or person.get("role") not in {"ethics", "procurement"}:
        return {
            "outcome": "not_authorised",
            "rows": [],
            "people_listed": False,
            "declarant_refs_included": False,
            "suppression_is_not_anonymisation": True,
            "coerced": False,
        }
    raw_threshold = pinned["criteria"].get("small_number_threshold")
    threshold = raw_threshold if type(raw_threshold) is int and raw_threshold >= 2 else None
    by_team: dict[str, list[str]] = {}
    for record in _STORE.values():
        declarant = _person(pinned["directory"], record.get("declarant_ref"))
        team = declarant.get("team") if declarant else None
        if not isinstance(team, str):
            team = "unreadable"
        by_team.setdefault(team, []).append(record.get("declaration_id"))
    rows = []
    for team, ids in sorted(by_team.items()):
        members = [row for row in _people(pinned["directory"]) if row.get("team") == team]
        sizes = {row.get("team_size") for row in members}
        size = next(iter(sizes)) if len(sizes) == 1 and type(next(iter(sizes))) is int else None
        count = len(ids)
        if threshold is None or size is None:
            suppressed = True
            reason = "threshold_unreadable" if threshold is None else "team_size_unreadable"
            shown = None
        else:
            complement = size - count
            suppressed = count < threshold or complement < threshold
            reason = "small_number" if suppressed else None
            shown = None if suppressed else count
        rows.append({
            "team": team,
            "count": shown,
            "suppressed": suppressed,
            "reason": reason,
            "people_listed": False,
        })
    return {
        "outcome": "aggregate",
        "threshold": threshold,
        "threshold_is_statutory": False,
        "suppression_is_not_anonymisation": True,
        "people_listed": False,
        "declarant_refs_included": False,
        "coerced": False,
        "rows": rows,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Draft a synthetic conflict-of-interest declaration.")
    parser.add_argument("--request", required=True)
    parser.add_argument("--as-of", required=True)
    args = parser.parse_args(argv)
    try:
        request = json.loads(Path(args.request).read_text(encoding="utf-8"))
        pinned = pinned_sources()
        result = draft_declaration(
            request,
            pinned["suppliers"],
            pinned["register"],
            pinned["directory"],
            pinned["criteria"],
            args.as_of,
        )
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
        print(json.dumps({"error": exc.__class__.__name__}))
        return 2
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
