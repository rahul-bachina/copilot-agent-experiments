#!/usr/bin/env python3
"""Draft an evidence-pack index for one synthetic request.

``build_pack`` returns a draft. It does not approve an export, apply an
exemption, disclose personal data, write a record, or send. ``record_export_approval``
checks a role and a name the caller passes. It still does not send.
``produce_export`` returns an index with no document bodies, and only after
that approval. The forbid functions always raise.

In-scope items are inventoried by Experiment 12, which calls Experiment 08.
This module does not copy either implementation and does not call ``release``.
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
    from catalogue import (
        APPROVER_ROLE,
        CATALOGUE_ID,
        CITATIONS,
        EXPERIMENT_ID,
        GATEWAY_CATALOGUE_ID,
        GATEWAY_EXPERIMENT_ID,
        INTAKE_CATALOGUE_ID,
        INTAKE_EXPERIMENT_ID,
        PACK_TYPES,
        PRIVILEGE_PHRASES,
        SCOPES,
        SOURCES_PINNED_ON,
        STALE_AFTER_DAYS,
        THIRD_PARTY_PHRASES,
        phrases_in,
    )
    from injection import merge_scans, scan_text
else:
    from .catalogue import (
        APPROVER_ROLE,
        CATALOGUE_ID,
        CITATIONS,
        EXPERIMENT_ID,
        GATEWAY_CATALOGUE_ID,
        GATEWAY_EXPERIMENT_ID,
        INTAKE_CATALOGUE_ID,
        INTAKE_EXPERIMENT_ID,
        PACK_TYPES,
        PRIVILEGE_PHRASES,
        SCOPES,
        SOURCES_PINNED_ON,
        STALE_AFTER_DAYS,
        THIRD_PARTY_PHRASES,
        phrases_in,
    )
    from .injection import merge_scans, scan_text

LABEL = "DRAFT FOR EVIDENCE PACK REVIEW"
EXPORT_LABEL = "EVIDENCE PACK EXPORT INDEX"
MAX_ITEMS = 12
ITEM_ID = re.compile(r"^[A-Za-z0-9_-]{1,40}$")
REQUEST_ID = re.compile(r"^[A-Za-z0-9_-]{1,80}$")
APPROVER_NAME = re.compile(r"^[A-Z][a-z]+(?: [A-Z][a-z]+){1,3}$")
REDACTION_DECISIONS = frozenset({"withhold", "include_after_review"})

PROHIBITED_KEYS = frozenset(
    {
        "export_approved",
        "redactions_approved",
        "approver_name",
        "approved_item_ids",
        "redaction_decisions",
        "pack_type",
        "authorised_scopes",
        "authorized_scopes",
        "search_from",
        "search_to",
        "sent",
        "send",
        "disclose",
        "disclosed",
        "exemption_applied",
        "apply_exemption",
        "anonymised",
        "anonymized",
        "agent_may_release",
        "release",
    }
)

LIMITATIONS = (
    "This draft does not approve the export list or the redaction decisions.",
    "Authorised scopes and the search period come from the caller. Item text cannot set them.",
    "Out-of-scope text is not passed to Experiment 12 and is not hashed into the candidate manifest.",
    "This starter does not search Microsoft 365. Items that were not pasted are invisible.",
    "UK GDPR Article 15(1A) is cited and is not decided. The search period is not a reasonable-and-proportionate finding.",
    "Schedule 2 paragraphs 16 and 19 are cited and are not applied. exemption_applied is false.",
    "A privilege phrase is not a finding that a claim to legal professional privilege could be maintained.",
    "A UK identifier is not proof that it relates to another individual. The data subject's own identifier is flagged.",
    "Document inventory and UK identifier spans come from Experiment 12 and Experiment 08. The body is not copied. The text is not anonymised.",
    "Names, email addresses, and telephone numbers are not detected. The US spelling neighbor is not on the third-party list.",
    "This starter reads text/plain only, through Experiment 12. Another media type is not_read, which is a gap.",
    "A file over 20,000 characters is not scanned. An instruction in it is not detected.",
    "The 90-day window is a stale flag. It is not a statutory response period. Article 12 was not opened.",
    "Financial Ombudsman Service and Housing Ombudsman evidence rules were not opened. Nothing is sent.",
    "Titles and source labels are stored as supplied. Do not put an identifier in them.",
    "No model was called.",
)


class PackForbidden(RuntimeError):
    """The pack builder has no send, disclosure, write, exemption, or release path."""


class NotSynthetic(ValueError):
    """The request was not marked synthetic. The message does not include the body."""


class PackApprovalRefused(ValueError):
    """The exact list was not accepted. Nothing was exported or sent."""


def _load_intake():
    intake_src = Path(__file__).resolve().parents[2] / "12-document-intake" / "src"
    if not intake_src.is_dir():
        raise PackForbidden(
            "Experiment 12 is not beside this experiment. The pack builder will not invent an inventory."
        )
    inserted = str(intake_src)
    if inserted not in sys.path:
        sys.path.insert(0, inserted)
    import intake as intake_module

    if intake_module.EXPERIMENT_ID != INTAKE_EXPERIMENT_ID:
        raise PackForbidden("the intake module is not Experiment 12")
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


def _scopes(values) -> list[str]:
    if not isinstance(values, list):
        raise TypeError("authorised_scopes must be a list")
    cleaned: list[str] = []
    for value in values:
        if not isinstance(value, str) or value not in SCOPES:
            raise ValueError("authorised scope is not in the closed list")
        if value not in cleaned:
            cleaned.append(value)
    return cleaned


def _period(search_from: date | None, search_to: date | None) -> dict:
    if search_from is None and search_to is None:
        return {"set": False, "from": None, "to": None}
    if search_from is None or search_to is None:
        raise ValueError("search_from and search_to must both be set, or both omitted")
    if not isinstance(search_from, date) or isinstance(search_from, datetime):
        raise TypeError("search_from must be a date")
    if not isinstance(search_to, date) or isinstance(search_to, datetime):
        raise TypeError("search_to must be a date")
    if search_from > search_to:
        raise ValueError("search_from is after search_to")
    return {"set": True, "from": search_from.isoformat(), "to": search_to.isoformat()}


def _date_position(raw, *, as_of: date, period: dict) -> tuple[str, str | None]:
    if raw is None or raw == "":
        return "missing", None
    if not isinstance(raw, str):
        return "invalid", None
    parsed = _parse_iso(raw)
    if parsed is None:
        return "invalid", None
    if parsed > as_of:
        return "future", parsed.isoformat()
    if not period["set"]:
        return "period_unset", parsed.isoformat()
    start = date.fromisoformat(period["from"])
    end = date.fromisoformat(period["to"])
    if parsed < start or parsed > end:
        return "outside_period", parsed.isoformat()
    return "within_period", parsed.isoformat()


def _empty_intake() -> dict:
    return {
        "called": False,
        "reason": "no item was inside an authorised scope",
        "experiment_id": INTAKE_EXPERIMENT_ID,
        "catalogue_id": INTAKE_CATALOGUE_ID,
        "purpose_preview": None,
        "files_confirmed": False,
        "purpose_confirmed": False,
        "reviewer_decision": None,
        "catalogue_pinned_on": None,
        "catalogue_stale": False,
        "gateway_rules_stale": False,
        "gateway_output_is_anonymised": False,
        "gateway_agent_may_release": False,
        "routing_handed_off": False,
        "checklist_sufficient": None,
        "actions_taken": [],
    }


def _intake_summary(result: dict, purpose_id: str) -> dict:
    checklist = result.get("checklist_preview")
    sufficient = None if checklist is None else False
    return {
        "called": True,
        "reason": None,
        "experiment_id": result["experiment_id"],
        "catalogue_id": result["catalogue_id"],
        "purpose_preview": purpose_id,
        "files_confirmed": False,
        "purpose_confirmed": False,
        "reviewer_decision": None,
        "catalogue_pinned_on": result["catalogue_pinned_on"],
        "catalogue_stale": bool(result["catalogue_stale"]),
        "gateway_rules_stale": bool(result["gateway_rules_stale"]),
        "gateway_output_is_anonymised": False,
        "gateway_agent_may_release": False,
        "routing_handed_off": False,
        "checklist_sufficient": sufficient,
        "actions_taken": [],
    }


def _flags() -> dict:
    return {
        "export_produced": False,
        "external_sent": False,
        "disclosed_to_requester": False,
        "production_record_written": False,
        "exemption_applied": False,
        "redacted_text_released": False,
        "output_is_anonymised": False,
        "scopes_widened_by_item": False,
        "search_period_taken_from_item": False,
    }


def _law() -> dict:
    return {
        "pinned_on": SOURCES_PINNED_ON.isoformat(),
        "exemption_applied": False,
        "reasonable_and_proportionate_search_decided": False,
        "paragraph_17_applied": False,
        "citations": [dict(row) for row in CITATIONS],
        "note": (
            "The citations were read on 28 October 2026. This draft does not "
            "decide that a search was reasonable and proportionate, and it does "
            "not apply Schedule 2."
        ),
    }


def _human_approval() -> dict:
    return {
        "exact_export_list": {
            "required": True,
            "approver": APPROVER_ROLE,
            "recorded": False,
        },
        "redactions": {
            "required": True,
            "approver": APPROVER_ROLE,
            "recorded": False,
        },
        "stale_material": {
            "required": True,
            "approver": APPROVER_ROLE,
            "recorded": False,
        },
        "release_or_send": {
            "required": True,
            "approver": APPROVER_ROLE,
            "recorded": False,
            "performed_by_this_agent": False,
        },
    }


def _force_inert(draft: dict) -> None:
    draft["actions_taken"] = []
    draft["model_called"] = False
    draft["network_called"] = False
    draft["flags"] = _flags()
    draft["law"]["exemption_applied"] = False
    draft["law"]["reasonable_and_proportionate_search_decided"] = False
    draft["law"]["paragraph_17_applied"] = False
    draft["prompt_injection"]["followed"] = False
    draft["export_approved"] = False
    draft["redactions_approved"] = False
    draft["approver_name"] = None
    draft["approved_item_ids"] = None
    for signal in draft["prompt_injection"]["signals"]:
        signal["followed"] = False
    for row in draft["items"]:
        row["content_recorded"] = False
        row["exemption_applied"] = False
    draft["intake"]["files_confirmed"] = False
    draft["intake"]["purpose_confirmed"] = False
    draft["intake"]["reviewer_decision"] = None
    draft["intake"]["gateway_output_is_anonymised"] = False
    draft["intake"]["gateway_agent_may_release"] = False
    draft["intake"]["routing_handed_off"] = False
    draft["intake"]["actions_taken"] = []
    if draft["intake"]["checklist_sufficient"] is not None:
        draft["intake"]["checklist_sufficient"] = False
    draft["human_approval"]["release_or_send"]["recorded"] = False
    draft["human_approval"]["release_or_send"]["performed_by_this_agent"] = False


def _normalise_item(raw: dict) -> tuple[dict, list[str]]:
    if not isinstance(raw, dict):
        raise ValueError("each item must be an object")
    working = dict(raw)
    stripped = _strip_prohibited(working, f"item:{working.get('item_id', '?')}:")
    item_id = working.get("item_id")
    if not isinstance(item_id, str) or not ITEM_ID.fullmatch(item_id):
        raise ValueError("item_id must be 1 to 40 letters, digits, hyphens, or underscores")
    title = working.get("title", "")
    if title == "":
        title = f"{item_id}.txt"
    if not isinstance(title, str) or "\n" in title or len(title) > 120:
        raise ValueError("title must be a single line of at most 120 characters")
    source = working.get("source", "unspecified")
    if not isinstance(source, str) or "\n" in source or not source or len(source) > 200:
        raise ValueError("source must be a single line of at most 200 characters")
    scope = working.get("source_scope", "")
    if not isinstance(scope, str):
        scope = ""
    content = working.get("content", "")
    if not isinstance(content, str):
        raise ValueError("content must be a string")
    media = working.get("media_type", "")
    if not isinstance(media, str):
        media = ""
    return {
        "item_id": item_id,
        "title": title,
        "source": source,
        "source_scope": scope.strip(),
        "document_date": working.get("document_date"),
        "media_type": media.strip().lower(),
        "content": content,
        "sha256": working.get("sha256"),
    }, stripped


def _call_intake(files: list[dict], *, purpose_id: str, as_of: date, rules_as_of: date | None) -> dict:
    intake_module = _load_intake()
    batch = {
        "synthetic": True,
        "batch_id": "exp-18-in-scope",
        "requested_purpose": purpose_id,
        "files": files,
    }
    return intake_module.intake(
        batch,
        as_of=as_of,
        stale_after_days=STALE_AFTER_DAYS,
        rules_as_of=rules_as_of,
    )


def _intake_file(item: dict) -> dict:
    file_row = {
        "file_id": item["item_id"],
        "filename": item["title"],
        "media_type": item["media_type"],
        "document_date": item["document_date"] if isinstance(item["document_date"], str) else None,
        "content": item["content"],
    }
    if isinstance(item["sha256"], str):
        file_row["sha256"] = item["sha256"]
    return file_row


def build_pack(
    request: dict,
    *,
    as_of: date,
    pack_type: str,
    authorised_scopes: list[str],
    search_from: date | None = None,
    search_to: date | None = None,
    rules_as_of: date | None = None,
) -> dict:
    """Return a draft index. Approval flags stay false."""

    if not isinstance(request, dict):
        raise TypeError("request must be an object")
    if not isinstance(as_of, date) or isinstance(as_of, datetime):
        raise TypeError("as_of must be a date")
    if rules_as_of is not None and (not isinstance(rules_as_of, date) or isinstance(rules_as_of, datetime)):
        raise TypeError("rules_as_of must be a date")
    if request.get("synthetic") is not True:
        raise NotSynthetic("record is not marked synthetic")
    if pack_type not in PACK_TYPES:
        raise ValueError("pack_type is not in the closed list")
    scopes = _scopes(authorised_scopes)
    period = _period(search_from, search_to)

    working = dict(request)
    prohibited = _strip_prohibited(working, "")
    items_in = working.get("items")
    if not isinstance(items_in, list) or not items_in:
        raise ValueError("request has no items")
    if len(items_in) > MAX_ITEMS:
        raise ValueError("request has more items than the starter will index")

    request_id = working.get("request_id", "unspecified")
    if not isinstance(request_id, str) or not REQUEST_ID.fullmatch(request_id):
        request_id = "unspecified"

    items: list[dict] = []
    seen_ids: set[str] = set()
    for raw in items_in:
        item, stripped = _normalise_item(raw)
        prohibited.extend(stripped)
        if item["item_id"] in seen_ids:
            raise ValueError("duplicate item_id")
        seen_ids.add(item["item_id"])
        items.append(item)

    scans = []
    for item in items:
        scans.append(scan_text(item["title"], item_id=item["item_id"], where="title"))
        if item["content"] and len(item["content"]) <= 20_000:
            scans.append(scan_text(item["content"], item_id=item["item_id"], where="body"))

    in_scope = [item for item in items if item["source_scope"] in scopes]
    purpose = PACK_TYPES[pack_type]
    intake_result = None
    if in_scope:
        intake_result = _call_intake(
            [_intake_file(item) for item in in_scope],
            purpose_id=purpose["intake_purpose"],
            as_of=as_of,
            rules_as_of=rules_as_of,
        )
        intake = _intake_summary(intake_result, purpose["intake_purpose"])
        by_id = {row["file_id"]: row for row in intake_result["files"]}
        for signal in intake_result["prompt_injection"]["signals"]:
            scans.append(
                {
                    "signals": [
                        {
                            "item_id": signal["file_id"],
                            "phrase": signal["phrase"],
                            "hidden_in": signal["hidden_in"],
                            "followed": False,
                            "source": "experiment_12",
                        }
                    ]
                }
            )
    else:
        intake = _empty_intake()
        by_id = {}

    local_injection = merge_scans(scans)
    signals_by_item: dict[str, list[dict]] = {}
    for signal in local_injection["signals"]:
        signals_by_item.setdefault(signal["item_id"], []).append(signal)

    rows = []
    for item in items:
        intake_row = by_id.get(item["item_id"])
        in_authorised = item["source_scope"] in scopes
        position, document_date = _date_position(item["document_date"], as_of=as_of, period=period)
        item_signals = signals_by_item.get(item["item_id"], [])
        injection_hit = bool(item_signals)
        read_status = None if intake_row is None else intake_row["read_status"]
        entity_types: list[str] = []
        finding_count = 0
        pii_called = False
        checksum_matches = None
        duplicate_of = None
        suggested_class = None
        intake_date_status = None
        sha256 = None
        if intake_row is not None:
            sha256 = intake_row["sha256"]
            checksum_matches = intake_row["checksum_matches"]
            duplicate_of = intake_row["duplicate_of"]
            suggested_class = intake_row["suggested_class"]
            intake_date_status = intake_row["date_status"]
            pii_called = bool(intake_row["pii"]["called"])
            entity_types = list(intake_row["pii"]["entity_types"])
            finding_count = intake_row["pii"]["finding_count"]

        privilege = []
        third_party_phrases = []
        if read_status == "read":
            privilege = phrases_in(item["content"], PRIVILEGE_PHRASES)
            third_party_phrases = phrases_in(item["content"], THIRD_PARTY_PHRASES)
        possible_privilege = bool(privilege)
        possible_third_party = bool(third_party_phrases) or bool(entity_types)

        reasons = []
        if not in_authorised:
            reasons.append("out_of_scope")
        elif read_status != "read":
            reasons.append(read_status or "not_read")
        elif checksum_matches is False:
            reasons.append("checksum_mismatch")
        elif duplicate_of:
            reasons.append("duplicate")
        elif position != "within_period":
            reasons.append(position)
        if injection_hit:
            reasons.append("prompt_injection")
        if possible_privilege:
            reasons.append("possible_privilege")
        if possible_third_party:
            reasons.append("possible_third_party_personal_data")

        structurally_ok = (
            in_authorised
            and read_status == "read"
            and checksum_matches is not False
            and not duplicate_of
            and position == "within_period"
            and not injection_hit
        )
        eligible = structurally_ok
        proposed = structurally_ok and not possible_privilege and not possible_third_party
        held = (
            in_authorised
            and read_status == "read"
            and checksum_matches is not False
            and not duplicate_of
            and position == "within_period"
            and (possible_privilege or possible_third_party or injection_hit)
            and not proposed
        )

        rows.append(
            {
                "item_id": item["item_id"],
                "title": item["title"],
                "source": item["source"],
                "source_scope": item["source_scope"],
                "in_authorised_scope": in_authorised,
                "document_date": document_date,
                "date_position": position,
                "sha256": sha256,
                "read_status": read_status,
                "checksum_matches": checksum_matches,
                "duplicate_of": duplicate_of,
                "suggested_class": suggested_class,
                "intake_date_status": intake_date_status,
                "pii_called": pii_called,
                "entity_types": entity_types,
                "finding_count": finding_count,
                "privilege_phrases": privilege,
                "possible_privilege": possible_privilege,
                "third_party_phrases": third_party_phrases,
                "possible_third_party_personal_data": possible_third_party,
                "prompt_injection": injection_hit,
                "exemption_applied": False,
                "content_recorded": False,
                "eligible_for_approval": eligible,
                "proposed_for_export": proposed,
                "held_for_review": held,
                "reasons": reasons,
            }
        )

    proposed_rows = [row for row in rows if row["proposed_for_export"]]
    proposed_rows.sort(key=lambda row: (row["document_date"] or "", row["item_id"]))
    proposed_index = []
    for page, row in enumerate(proposed_rows, start=1):
        proposed_index.append(
            {
                "page": page,
                "item_id": row["item_id"],
                "source": row["source"],
                "document_date": row["document_date"],
                "sha256": row["sha256"],
                "source_scope": row["source_scope"],
                "status": "proposed",
            }
        )
        row["proposed_page"] = page
    for row in rows:
        row.setdefault("proposed_page", None)

    held = [
        {
            "item_id": row["item_id"],
            "source": row["source"],
            "document_date": row["document_date"],
            "sha256": row["sha256"],
            "possible_privilege": row["possible_privilege"],
            "possible_third_party_personal_data": row["possible_third_party_personal_data"],
            "prompt_injection": row["prompt_injection"],
            "eligible_for_approval": row["eligible_for_approval"],
            "exemption_applied": False,
        }
        for row in rows
        if row["held_for_review"]
    ]
    excluded = [
        {
            "item_id": row["item_id"],
            "source_scope": row["source_scope"],
            "reasons": [reason for reason in row["reasons"] if reason not in {"possible_privilege", "possible_third_party_personal_data"}],
            "sha256": row["sha256"] if row["in_authorised_scope"] else None,
            "content_recorded": False,
        }
        for row in rows
        if not row["proposed_for_export"] and not row["held_for_review"]
    ]

    sources_stale = (as_of - SOURCES_PINNED_ON).days > STALE_AFTER_DAYS
    if rules_as_of is not None and rules_as_of < SOURCES_PINNED_ON:
        sources_stale = True

    draft = {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment_id": EXPERIMENT_ID,
        "autonomy": "A1",
        "request_id": request_id,
        "as_of": as_of.isoformat(),
        "pack_type": pack_type,
        "pack_type_label": purpose["label"],
        "pack_type_note": purpose["downstream_note"],
        "authorised_scopes": scopes,
        "search_period": period,
        "sources_pinned_on": SOURCES_PINNED_ON.isoformat(),
        "sources_stale": sources_stale,
        "rules_as_of": None if rules_as_of is None else rules_as_of.isoformat(),
        "model_called": False,
        "network_called": False,
        "export_approved": False,
        "redactions_approved": False,
        "approver_name": None,
        "approved_item_ids": None,
        "actions_taken": [],
        "flags": _flags(),
        "law": _law(),
        "intake": intake,
        "gateway": {
            "experiment_id": GATEWAY_EXPERIMENT_ID,
            "catalogue_id": GATEWAY_CATALOGUE_ID,
            "called_via": INTAKE_EXPERIMENT_ID,
            "output_is_anonymised": False,
            "agent_may_release": False,
        },
        "prompt_injection": local_injection,
        "prohibited_payload_keys": prohibited,
        "items": rows,
        "proposed_index": proposed_index,
        "held_for_review": held,
        "excluded": excluded,
        "pagination": {
            "proposed_page_count": len(proposed_index),
            "order": "document_date then item_id",
            "note": "A proposal. It is not the approved export order.",
        },
        "human_approval": _human_approval(),
        "limitations": list(LIMITATIONS),
    }
    _force_inert(draft)
    return draft


def _require_draft(draft: dict) -> dict:
    if not isinstance(draft, dict) or draft.get("label") != LABEL:
        raise ValueError("draft is not an evidence pack")
    if draft.get("experiment_id") != EXPERIMENT_ID:
        raise ValueError("draft is not an evidence pack")
    return deepcopy(draft)


def _by_id(draft: dict) -> dict[str, dict]:
    return {row["item_id"]: row for row in draft["items"]}


def record_export_approval(
    draft: dict,
    *,
    role: str,
    approver_name: str,
    approved_item_ids: list[str],
    redaction_decisions: dict | None = None,
    acknowledge_stale: bool = False,
) -> dict:
    """Record that a named approver accepted an exact item list.

    The agent must not call this. A matching role does not send the pack,
    apply an exemption, or release text. ``build_pack`` output cannot be
    passed back through this function by the agent: the skills forbid the call,
    and the tool schema marks it as not callable by the agent.
    """

    if role != APPROVER_ROLE:
        raise PackApprovalRefused("only an Evidence pack approver can record the exact list")
    if not isinstance(approver_name, str) or not APPROVER_NAME.fullmatch(approver_name):
        raise PackApprovalRefused("approver_name must be a personal name passed by the caller")
    if acknowledge_stale is not True and acknowledge_stale is not False:
        raise TypeError("acknowledge_stale must be a boolean")
    if not isinstance(approved_item_ids, list) or any(not isinstance(item_id, str) for item_id in approved_item_ids):
        raise PackApprovalRefused("approved_item_ids must be a list of item ids")
    if len(approved_item_ids) != len(set(approved_item_ids)):
        raise PackApprovalRefused("approved_item_ids contains a duplicate")
    decisions = redaction_decisions or {}
    if not isinstance(decisions, dict):
        raise PackApprovalRefused("redaction_decisions must be an object")

    updated = _require_draft(draft)
    if not updated["search_period"]["set"]:
        raise PackApprovalRefused("search period is not set")
    known = _by_id(updated)
    if approver_name in known:
        raise PackApprovalRefused("approver_name must not be an item id")

    for item_id in approved_item_ids:
        row = known.get(item_id)
        if row is None or not row["eligible_for_approval"]:
            raise PackApprovalRefused("an item id is not eligible for the exact list")
        if row["possible_privilege"] or row["possible_third_party_personal_data"]:
            decision = decisions.get(item_id)
            if decision != "include_after_review":
                raise PackApprovalRefused("a flagged item needs the decision include_after_review")

    for item_id, decision in decisions.items():
        if decision not in REDACTION_DECISIONS:
            raise PackApprovalRefused("redaction decision is not withhold or include_after_review")
        row = known.get(item_id)
        if row is None:
            raise PackApprovalRefused("redaction decision names an unknown item")
        if not row["possible_privilege"] and not row["possible_third_party_personal_data"]:
            raise PackApprovalRefused("redaction decision names an item that was not flagged")
        if decision == "withhold" and item_id in approved_item_ids:
            raise PackApprovalRefused("withhold contradicts the exact list")
        if decision == "include_after_review" and item_id not in approved_item_ids:
            raise PackApprovalRefused("include_after_review is not on the exact list")

    needs_stale = updated["sources_stale"] or updated["intake"]["catalogue_stale"] or updated["intake"]["gateway_rules_stale"]
    if any(known[item_id]["intake_date_status"] == "stale" for item_id in approved_item_ids):
        needs_stale = True
    if needs_stale and not acknowledge_stale:
        raise PackApprovalRefused("stale material must be acknowledged by the evidence pack approver")

    updated["export_approved"] = True
    updated["redactions_approved"] = True
    updated["approver_name"] = approver_name
    updated["approved_item_ids"] = list(approved_item_ids)
    updated["redaction_decisions"] = {key: decisions[key] for key in decisions}
    updated["approval"] = {
        "role": APPROVER_ROLE,
        "approver_name": approver_name,
        "approved_item_ids": list(approved_item_ids),
        "acknowledge_stale": acknowledge_stale,
        "does_not_send": True,
        "does_not_apply_an_exemption": True,
        "does_not_release_text": True,
    }
    updated["human_approval"]["exact_export_list"]["recorded"] = True
    updated["human_approval"]["redactions"]["recorded"] = True
    updated["human_approval"]["stale_material"]["recorded"] = needs_stale and acknowledge_stale
    updated["model_called"] = False
    updated["network_called"] = False
    updated["flags"]["export_produced"] = False
    updated["flags"]["external_sent"] = False
    updated["flags"]["disclosed_to_requester"] = False
    updated["flags"]["exemption_applied"] = False
    updated["flags"]["redacted_text_released"] = False
    updated["law"]["exemption_applied"] = False
    return updated


def produce_export(draft: dict) -> dict:
    """Return an index of the approved ids. No bodies. Nothing is sent.

    The agent must not call this. The caller has to have recorded an approval
    first. The page order is the order of that exact list, not the proposal.
    """

    if not isinstance(draft, dict) or draft.get("label") != LABEL:
        raise PackForbidden("draft is not an evidence pack")
    if draft.get("export_approved") is not True or draft.get("redactions_approved") is not True:
        raise PackForbidden("export index is refused until the exact list and the redactions are approved")
    if not isinstance(draft.get("approver_name"), str) or not draft["approver_name"]:
        raise PackForbidden("export index is refused until the exact list and the redactions are approved")
    if not isinstance(draft.get("approved_item_ids"), list):
        raise PackForbidden("export index is refused until the exact list and the redactions are approved")
    known = _by_id(draft)
    pages = []
    for page, item_id in enumerate(draft["approved_item_ids"], start=1):
        row = known[item_id]
        decision = None
        if isinstance(draft.get("redaction_decisions"), dict):
            decision = draft["redaction_decisions"].get(item_id)
        pages.append(
            {
                "page": page,
                "item_id": row["item_id"],
                "source": row["source"],
                "document_date": row["document_date"],
                "sha256": row["sha256"],
                "source_scope": row["source_scope"],
                "possible_privilege": row["possible_privilege"],
                "possible_third_party_personal_data": row["possible_third_party_personal_data"],
                "redaction_decision": decision,
                "entity_types": list(row["entity_types"]),
                "exemption_applied": False,
                "content_recorded": False,
            }
        )
    return {
        "label": EXPORT_LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment_id": EXPERIMENT_ID,
        "request_id": draft["request_id"],
        "pack_type": draft["pack_type"],
        "approver_role": APPROVER_ROLE,
        "approver_name": draft["approver_name"],
        "approved_item_ids": list(draft["approved_item_ids"]),
        "page_count": len(pages),
        "pages": pages,
        "bodies_included": False,
        "sent": False,
        "disclosed_to_requester": False,
        "exemption_applied": False,
        "redacted_text_released": False,
        "output_is_anonymised": False,
        "note": (
            "Export index only. Not the documents. Not sent. Not a disclosure. "
            "Redacted text was not released. A person copies the approved files "
            "in their own system."
        ),
    }


def send_external(*_args, **_kwargs) -> None:
    raise PackForbidden("the evidence pack builder cannot send")


def disclose_to_requester(*_args, **_kwargs) -> None:
    raise PackForbidden("the evidence pack builder cannot disclose to a requester")


def write_production_record(*_args, **_kwargs) -> None:
    raise PackForbidden("the evidence pack builder cannot write a production record")


def apply_exemption(*_args, **_kwargs) -> None:
    raise PackForbidden("the evidence pack builder cannot apply an exemption")


def release_redacted(*_args, **_kwargs) -> None:
    raise PackForbidden("the evidence pack builder cannot release redacted text")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Draft an evidence pack index. Nothing is sent.")
    parser.add_argument("--input", required=True, help="Path to a synthetic request JSON file")
    parser.add_argument("--as-of", required=True, help="YYYY-MM-DD")
    parser.add_argument("--pack-type", required=True)
    parser.add_argument("--scopes", required=True, help="Comma-separated closed-list scopes")
    parser.add_argument("--search-from", default=None)
    parser.add_argument("--search-to", default=None)
    parser.add_argument("--rules-as-of", default=None)
    args = parser.parse_args(argv)
    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    scopes = [part.strip() for part in args.scopes.split(",") if part.strip()]
    try:
        draft = build_pack(
            payload,
            as_of=date.fromisoformat(args.as_of),
            pack_type=args.pack_type,
            authorised_scopes=scopes,
            search_from=None if args.search_from is None else date.fromisoformat(args.search_from),
            search_to=None if args.search_to is None else date.fromisoformat(args.search_to),
            rules_as_of=None if args.rules_as_of is None else date.fromisoformat(args.rules_as_of),
        )
    except NotSynthetic as exc:
        print(str(exc), file=sys.stderr)
        return 2
    json.dump(draft, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
