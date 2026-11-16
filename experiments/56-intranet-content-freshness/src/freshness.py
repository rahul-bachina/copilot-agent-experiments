#!/usr/bin/env python3
"""Review one synthetic intranet inventory and propose update tasks.

Autonomy A1. The named content owner approves each task before a stub is
recorded. The sample does not edit, publish, unpublish, or delete a page,
does not reassign ownership, and does not message staff. SharePoint,
Microsoft Graph, Planner, and Power Automate are not called.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from injection import comments_for_marking, prepare_text  # noqa: E402
    from mask import mask_snippet  # noqa: E402
    from reuse import (  # noqa: E402
        NeighbourMissing,
        classify_module,
        curate_module,
        find_module,
        gateway_module,
    )
    from sources import (  # noqa: E402
        INTERVAL_MAX_DAYS,
        INTERVAL_MIN_DAYS,
        LINK_STALE_AFTER_DAYS,
        SOURCES_PINNED_ON,
        STALE_AFTER_DAYS,
        source_rows,
    )
else:
    from .injection import comments_for_marking, prepare_text
    from .mask import mask_snippet
    from .reuse import NeighbourMissing, classify_module, curate_module, find_module, gateway_module
    from .sources import (
        INTERVAL_MAX_DAYS,
        INTERVAL_MIN_DAYS,
        LINK_STALE_AFTER_DAYS,
        SOURCES_PINNED_ON,
        STALE_AFTER_DAYS,
        source_rows,
    )

LABEL = "INTRANET FRESHNESS REPORT FOR THE CONTENT OWNER"
CATALOGUE_ID = "M008"
EXPERIMENT_ID = "exp-56-intranet-content-freshness"
AUTONOMY = "A1"
ORGANISATION = "Merrowfield Borough Council (fictional)"
MAX_CHARS = 20_000

PAGE_ID = re.compile(r"^SYN-PAGE-\d{4}$")
OWNER_ID = re.compile(r"^SYN-OWNER-[A-Z0-9-]{1,24}$")
POLICY_ID = re.compile(r"\bPOL-[A-Z0-9-]{1,24}\b")
POLICY_KEY = re.compile(r"^POL-[A-Z0-9-]{1,24}$")
PRINCIPAL = re.compile(r"^SYN-PRIN-[A-Z0-9-]{1,24}$")
FILE_ID = re.compile(r"^SYN-OD-\d{4}$")
CONTACT_ID = re.compile(r"^SYN-CONTACT-\d{4}$")
INVENTORY_ID = re.compile(r"^SYN-INV-\d{4}$")
DATE_TEXT = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TASK_ID = re.compile(r"^TASK-\d{4}$")
HREF = re.compile(r"^(?:https://|http://|/).{0,180}$")

OWNER_STATUS = frozenset({"current", "former", "vacant", "missing"})
LINK_STATE = frozenset({"ok", "broken", "stale"})
CONTACT_STATUS = frozenset({"current", "former"})
POLICY_STATUS = frozenset({"current", "superseded", "withdrawn"})
HIGHER_MARKINGS = frozenset({"OFFICIAL-SENSITIVE", "SECRET", "TOP SECRET"})

SAFEGUARDING = (
    "self-harm",
    "self harm",
    "suicide",
    "kill myself",
    "i want to die",
    "safeguarding",
    "domestic abuse",
    "child protection",
)
HOLD_PHRASES = ("legal hold", "do not destroy", "retention hold")
WITHDRAWN_PHRASE = re.compile(
    r"withdrawn guidance|superseded policy|superseded guidance",
    re.IGNORECASE,
)

PROHIBITED_KEYS = frozenset(
    {
        "human_approval",
        "pages_edited",
        "published",
        "unpublished",
        "deleted",
        "ownership_reassigned",
        "messages_sent",
        "approval_request_sent",
        "planner_called",
        "power_automate_called",
        "graph_called",
        "sharepoint_called",
        "executed",
        "confirmed",
        "selection",
        "clearance",
        "task_ids",
        "tasks_created",
        "approved",
        "actions_taken",
    }
)

PROHIBITED_DECISIONS = frozenset(
    {
        "edit_page",
        "publish_page",
        "unpublish_page",
        "delete_page",
        "reassign_owner",
        "message_staff",
        "create_tasks",
        "approve_all",
    }
)


class FreshnessForbidden(RuntimeError):
    """A page change, a reassignment, or a staff message was requested."""


def edit_page(*_args, **_kwargs) -> None:
    raise FreshnessForbidden("edit_page is not a tool of this agent")


def publish_page(*_args, **_kwargs) -> None:
    raise FreshnessForbidden("publish_page is not a tool of this agent")


def unpublish_page(*_args, **_kwargs) -> None:
    raise FreshnessForbidden("unpublish_page is not a tool of this agent")


def delete_page(*_args, **_kwargs) -> None:
    raise FreshnessForbidden("delete_page is not a tool of this agent")


def reassign_owner(*_args, **_kwargs) -> None:
    raise FreshnessForbidden("reassign_owner is not a tool of this agent")


def message_staff(*_args, **_kwargs) -> None:
    raise FreshnessForbidden("message_staff is not a tool of this agent")


def _parse_as_of(value: date | datetime | str) -> date | None:
    """Return a date, or None when the value cannot be read.

    A string is accepted only as YYYY-MM-DD. A longer timestamp is not sliced
    down to a date, and a number is not treated as today.
    """

    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str) and DATE_TEXT.fullmatch(value):
        try:
            return date.fromisoformat(value)
        except ValueError:
            return None
    return None


def _parse_day(value: object) -> tuple[date | None, str]:
    """Return (date, status). Status is ok, absent, or unparseable.

    Only a YYYY-MM-DD string is a date. Null is absent. Anything else is
    unparseable and is not replaced with a default.
    """

    if value is None:
        return None, "absent"
    if isinstance(value, str) and DATE_TEXT.fullmatch(value):
        try:
            return date.fromisoformat(value), "ok"
        except ValueError:
            return None, "unparseable"
    return None, "unparseable"


def _parse_interval(value: object) -> tuple[int | None, str]:
    if value is None:
        return None, "absent"
    if isinstance(value, bool) or not isinstance(value, int):
        return None, "unparseable"
    if value < INTERVAL_MIN_DAYS or value > INTERVAL_MAX_DAYS:
        return None, "out_of_range"
    return value, "ok"


def _parse_views(value: object) -> tuple[int | None, str]:
    if value is None:
        return None, "absent"
    if isinstance(value, bool) or not isinstance(value, int):
        return None, "unparseable"
    if value < 0:
        return None, "out_of_range"
    return value, "ok"


def _strip_prohibited(mapping: dict) -> list[str]:
    removed = [key for key in list(mapping) if key in PROHIBITED_KEYS]
    for key in removed:
        mapping.pop(key, None)
    return removed


def _flags() -> dict:
    return {
        "pages_edited": False,
        "published": False,
        "unpublished": False,
        "deleted": False,
        "ownership_reassigned": False,
        "messages_sent": False,
        "approval_request_sent": False,
        "planner_called": False,
        "power_automate_called": False,
        "graph_called": False,
        "sharepoint_called": False,
    }


def _human_route() -> dict:
    return {
        "offered": True,
        "agent_edits_pages": False,
        "agent_publishes": False,
        "agent_reassigns_ownership": False,
        "agent_messages_staff": False,
    }


def _force(result: dict) -> None:
    result["human_route"] = _human_route()
    result["flags"] = _flags()
    result["model_called"] = False
    result["network_called"] = False
    result["executed"] = False
    result["actions_taken"] = []
    copying = result.get("copying")
    if isinstance(copying, dict):
        copying["page_bodies_copied"] = False
        copying["contacts_raw_copied"] = False
        copying["page_views_coerced_to_zero"] = False
        copying["intervals_defaulted"] = False
        copying["output_is_anonymised"] = False
        copying["values_recorded"] = False
    if result.get("human_approval") is not None and not isinstance(result.get("human_approval"), dict):
        result["human_approval"] = None
    regulatory = result.get("regulatory")
    if isinstance(regulatory, dict):
        regulatory["accuracy_met"] = False
        regulatory["accessibility_scope_decided"] = False


def _scan_marking(text: str) -> tuple[str, int]:
    if not text:
        return "unmarked", 0
    upper = text.upper()
    found: list[tuple[str, int]] = []
    if re.search(r"\bOFFICIAL\b", upper):
        found.append(("OFFICIAL", 1))
    if "OFFICIAL-SENSITIVE" in upper or "OFFICIAL - SENSITIVE" in upper:
        found.append(("OFFICIAL-SENSITIVE", 2))
    if re.search(r"\bSECRET\b", upper):
        found.append(("SECRET", 3))
    if "TOP SECRET" in upper:
        found.append(("TOP SECRET", 4))
    if not found:
        return "unmarked", 0
    found.sort(key=lambda item: item[1])
    return found[-1]


def _meta_marking(raw: object) -> tuple[str, int, bool]:
    if raw is None:
        return "unmarked", 1, False
    if not isinstance(raw, str):
        return "unrecognised", 99, True
    cleaned = " ".join(raw.split())
    if not cleaned or cleaned.upper() in {"NONE", "UNMARKED"}:
        return "unmarked", 1, False
    name, rank = _scan_marking(cleaned)
    if rank == 0:
        return "unrecognised", 99, True
    return name, rank, False


def _combine_marking(meta_name: str, meta_rank: int, meta_bad: bool, content_name: str, content_rank: int, comment_name: str, comment_rank: int) -> dict:
    chosen_name = meta_name
    chosen_rank = meta_rank
    sources = ["metadata"] if not meta_bad else ["metadata_unrecognised"]
    conflict = False
    if content_rank > chosen_rank:
        if content_rank > 0 and meta_rank > 0 and not meta_bad and content_name != meta_name and meta_name != "unmarked":
            conflict = True
        chosen_name, chosen_rank = content_name, content_rank
        sources = ["content"] if not meta_bad else ["metadata_unrecognised", "content"]
    elif content_rank > 0 and content_name != meta_name and meta_name != "unmarked" and not meta_bad:
        conflict = True
        if "content" not in sources:
            sources.append("content")
    if comment_rank > chosen_rank:
        if meta_name not in {"unmarked", "unrecognised"} and comment_name != meta_name:
            conflict = True
        chosen_name, chosen_rank = comment_name, comment_rank
        if "html_comment" not in sources:
            sources.append("html_comment")
    elif comment_rank > 0 and comment_name != chosen_name and chosen_name not in {"unmarked", "unrecognised"}:
        conflict = True
        if "html_comment" not in sources:
            sources.append("html_comment")
    return {
        "marking": chosen_name,
        "rank": chosen_rank,
        "conflict": conflict,
        "sources": sources,
        "unrecognised": meta_bad or chosen_rank >= 99,
    }


def _base(as_of: str, *, outcome: str, statement: str, inventory_id: str = "unspecified") -> dict:
    pinned = date.fromisoformat(as_of) if DATE_TEXT.fullmatch(as_of) else SOURCES_PINNED_ON
    age = (pinned - SOURCES_PINNED_ON).days
    rules_current = 0 <= age <= STALE_AFTER_DAYS
    result = {
        "label": LABEL,
        "experiment_id": EXPERIMENT_ID,
        "catalogue_id": CATALOGUE_ID,
        "autonomy": AUTONOMY,
        "organisation": ORGANISATION,
        "inventory_id": inventory_id,
        "as_of": as_of,
        "outcome": outcome,
        "plain_statement": statement,
        "content_owner_id": None,
        "page_summaries": [],
        "findings": [],
        "human_queue": [],
        "proposed_tasks": [],
        "tasks_created": [],
        "withheld": {
            "not_permitted": 0,
            "unreadable": 0,
            "ids_recorded": False,
            "titles_recorded": False,
            "bodies_recorded": False,
        },
        "copying": {
            "page_bodies_copied": False,
            "titles_copied": 0,
            "snippets_copied": 0,
            "mask_kinds_applied": [],
            "contacts_raw_copied": False,
            "page_views_coerced_to_zero": False,
            "intervals_defaulted": False,
            "output_is_anonymised": False,
            "values_recorded": False,
        },
        "injection": {"detected": False, "followed": False, "signals": []},
        "human_approval": None,
        "regulatory": {
            "accuracy_met": False,
            "accessibility_scope_decided": False,
            "article_5_1_d": "read" if rules_current else "not_quoted",
            "accessibility_regs": "read" if rules_current else "not_quoted",
            "quotes_included": rules_current,
        },
        "stale": {
            "rules_current": rules_current,
            "age_days": age,
            "stale_after_days": STALE_AFTER_DAYS,
            "link_window_days": LINK_STALE_AFTER_DAYS,
            "link_window_is_statutory": False,
            "review_interval_is_statutory": False,
        },
        "sources": source_rows(rules_current),
        "reuse": {
            "sharepoint_curator": {"called": False, "text_recorded": False, "archive_followed": False},
            "onedrive_finder": {"called": False, "text_recorded": False, "snippet_copied": False},
            "records_classification": {"called": False, "text_recorded": False},
            "identifier_gateway": {"called": False, "values_recorded": False, "output_is_anonymised": False},
        },
        "stripped_keys": [],
    }
    _force(result)
    return result


def _call_gateway(text: str) -> dict:
    proposal = gateway_module().propose(
        text,
        caller=EXPERIMENT_ID,
        apply_model_suggestions=False,
        reversible=False,
    )
    if proposal["anonymisation"]["output_is_anonymised"] or proposal["release"]["agent_may_release"]:
        raise FreshnessForbidden("Experiment 08 returned an unexpected release flag")
    types: list[str] = []
    for finding in proposal["audit_log"]["findings"]:
        if finding.get("applied") and finding.get("method") == "deterministic":
            entity = finding.get("entity_type")
            if isinstance(entity, str) and entity not in types:
                types.append(entity)
    return {
        "called": True,
        "entity_types": types,
        "values_recorded": False,
        "output_is_anonymised": False,
    }


def _call_classify(page_id: str, matching: str, as_of: date, reviewed: str | None, marking: str) -> dict:
    document = {
        "synthetic": True,
        "document_id": page_id,
        "filename": f"{page_id}.txt",
        "text": matching,
        "jurisdiction": "england",
        "document_date": reviewed,
    }
    if marking in HIGHER_MARKINGS:
        document["existing_marking"] = marking
    draft = classify_module().classify_record(document, as_of)
    hold = bool((draft.get("legal_hold") or {}).get("indicated"))
    personal = bool((draft.get("proposals") or {}).get("personal_data", {}).get("indicated"))
    return {
        "called": True,
        "legal_hold": hold,
        "personal_data_indicated": personal,
        "text_recorded": False,
        "human_approval": None,
    }


def _curator_pairs(rows: list[dict], principals: list[str], as_of: date) -> dict:
    usable = [row for row in principals if PRINCIPAL.fullmatch(row)]
    items = []
    reverse = {}
    for index, row in enumerate(rows, start=1):
        mapped = f"SYN-SP-{index:04d}"
        reverse[mapped] = row["page_id"]
        items.append(
            {
                "item_id": mapped,
                "kind": "page",
                "title": row["title"] or row["page_id"],
                "text": row["matching"],
                "readers": usable,
                "sensitivity": "OFFICIAL",
                "last_modified": row.get("last_reviewed"),
                "review_date": row.get("last_reviewed"),
                "published": True,
                "url": row["url"] or f"/{row['page_id'].lower()}",
                "content_type": "Guidance",
                "owner": "SYN-OWNER-USER",
                "audience": "staff",
            }
        )
    if len(items) < 2 or not usable:
        return {
            "called": False,
            "reason": "nothing_to_compare" if len(items) < 2 else "principal_pattern",
            "pairs": [],
            "text_recorded": False,
            "archive_followed": False,
            "sharepoint_called": False,
        }
    draft = curate_module().curate_site(
        {
            "synthetic": True,
            "site_id": "SYN-SITE-0056",
            "requesting_user": {"principals": usable},
            "items": items,
        },
        as_of,
    )
    pairs = []
    for proposal in draft.get("proposals") or []:
        if proposal.get("type") not in {"duplicate", "near_duplicate"}:
            continue
        ids = sorted({reverse[item] for item in proposal.get("item_ids") or [] if item in reverse})
        if len(ids) >= 2 and ids not in pairs:
            pairs.append(ids)
    return {
        "called": True,
        "experiment_id": "exp-50-sharepoint-knowledge-curator",
        "catalogue_id": "M001",
        "pairs": pairs,
        "text_recorded": False,
        "archive_followed": False,
        "sharepoint_called": False,
        "graph_called": False,
    }


def _finder(index: dict, selection: dict | None, as_of: date) -> dict:
    empty = {
        "called": False,
        "reason": "no_linked_index",
        "text_recorded": False,
        "snippet_copied": False,
        "sharepoint_called": False,
        "graph_called": False,
        "hits": {},
        "withheld": None,
        "outcome": None,
    }
    if not isinstance(index, dict):
        empty["reason"] = "linked_index_unreadable"
        return empty
    if not isinstance(selection, dict):
        empty["reason"] = "selection_not_supplied"
        return empty
    if selection.get("confirmed") is not True or selection.get("actor_role") != "Requesting user":
        empty["reason"] = "locations_not_confirmed"
        return empty
    query = selection.get("query")
    if not isinstance(query, str) or not query.strip():
        empty["reason"] = "query_not_supplied"
        return empty
    finder_selection = {
        "confirmed": True,
        "actor_role": "Requesting user",
        "location_ids": list(selection.get("location_ids") or []),
        "principals": list(selection.get("principals") or []),
        "clearance": selection.get("clearance"),
    }
    draft = find_module().find_documents(index, {"query": query}, finder_selection, as_of)
    hits = {}
    for match in draft.get("matches") or []:
        file_id = match.get("file_id")
        if not isinstance(file_id, str):
            continue
        hits[file_id] = {
            "file_id": file_id,
            "likely_stale": bool(match.get("likely_stale")),
            "superseded": bool(match.get("superseded")),
            "superseded_by": match.get("superseded_by") if isinstance(match.get("superseded_by"), str) else None,
            "later_version_not_in_view": bool(match.get("later_version_not_in_view")),
            "likely_duplicate": bool(match.get("likely_duplicate")),
            "sensitivity_label": match.get("sensitivity_label") if isinstance(match.get("sensitivity_label"), str) else None,
            "legal_hold": bool(match.get("legal_hold")),
            "retention_label": match.get("retention_label") if isinstance(match.get("retention_label"), str) else None,
            "snippet_copied": False,
        }
    withheld = draft.get("withheld") if isinstance(draft.get("withheld"), dict) else {}
    return {
        "called": True,
        "experiment_id": "exp-55-onedrive-document-finder",
        "catalogue_id": "M007",
        "outcome": draft.get("outcome"),
        "reason": None,
        "text_recorded": False,
        "snippet_copied": False,
        "sharepoint_called": False,
        "graph_called": False,
        "match_count": len(hits),
        "withheld_counts": {
            "outside_selection": withheld.get("outside_selection", 0),
            "not_permitted": withheld.get("not_permitted", 0),
            "above_clearance": withheld.get("above_clearance", 0),
            "unreadable": withheld.get("unreadable", 0),
            "ids_recorded": False,
            "titles_recorded": False,
        },
        "hits": hits,
    }


def _contact_evidence(raw: dict, mask_kinds: set[str]) -> dict | None:
    status = raw.get("status")
    if not isinstance(status, str) or status not in CONTACT_STATUS:
        return None
    contact_id = raw.get("contact_id")
    if not isinstance(contact_id, str) or not CONTACT_ID.fullmatch(contact_id):
        contact_id = None
    fields = {}
    for key in ("name", "email", "phone"):
        value = raw.get(key)
        if not isinstance(value, str) or not value.strip():
            fields[key] = {"present": False, "copied": False}
            continue
        masked, kinds = mask_snippet(value)
        if not kinds or masked == value:
            fields[key] = {"present": True, "copied": False, "reason": "pattern_did_not_match"}
            continue
        for kind in kinds:
            mask_kinds.add(kind)
        fields[key] = {"present": True, "copied": True, "masked": masked}
    return {"contact_id": contact_id, "status": status, "fields": fields, "raw_copied": False}


def _read_policies(raw_policies: object) -> tuple[dict[str, dict], str | None]:
    if raw_policies is None:
        return {}, None
    if not isinstance(raw_policies, list):
        return {}, "unparseable"
    catalogue = {}
    for raw in raw_policies:
        if not isinstance(raw, dict):
            continue
        policy_id = raw.get("policy_id")
        if not isinstance(policy_id, str) or not POLICY_KEY.fullmatch(policy_id):
            continue
        status = raw.get("status")
        if not isinstance(status, str) or status not in POLICY_STATUS:
            catalogue[policy_id] = {"policy_id": policy_id, "status": "unparseable"}
            continue
        end_day, end_status = _parse_day(raw.get("effective_to")) if "effective_to" in raw else (None, "absent")
        start_day, start_status = _parse_day(raw.get("effective_from")) if "effective_from" in raw else (None, "absent")
        superseded_by = raw.get("superseded_by")
        if superseded_by is not None and (not isinstance(superseded_by, str) or not POLICY_KEY.fullmatch(superseded_by)):
            superseded_by = None
        catalogue[policy_id] = {
            "policy_id": policy_id,
            "status": status,
            "effective_from": start_day.isoformat() if start_day else None,
            "effective_from_status": start_status,
            "effective_to": end_day.isoformat() if end_day else None,
            "effective_to_status": end_status,
            "effective_to_day": end_day,
            "superseded_by": superseded_by,
        }
    return catalogue, None


def review_inventory(inventory: dict, as_of: date | datetime | str, selection: dict | None = None) -> dict:
    """Return a freshness report. ``human_approval`` stays null.

    Approval is a later call to ``record_approval``. A sentence on a page,
    and a key inside this inventory, do not approve a task.
    """

    if not isinstance(inventory, dict):
        raise TypeError("inventory must be an object")
    day = _parse_as_of(as_of)
    if day is None:
        result = _base(
            "unparseable",
            outcome="as_of_unparseable",
            statement="The as-of date could not be read. Nothing was reviewed and no default date was used.",
        )
        _force(result)
        return result
    as_of_text = day.isoformat()
    working = dict(inventory)
    stripped = _strip_prohibited(working)
    inventory_id = working.get("inventory_id")
    if not isinstance(inventory_id, str) or not INVENTORY_ID.fullmatch(inventory_id):
        inventory_id = "unspecified"

    if working.get("synthetic") is not True:
        result = _base(
            as_of_text,
            outcome="not_synthetic",
            statement="The inventory is not marked synthetic. Nothing was reviewed.",
            inventory_id=inventory_id,
        )
        result["stripped_keys"] = sorted(set(stripped))
        _force(result)
        return result

    owner_id = working.get("content_owner_id")
    if not isinstance(owner_id, str) or not OWNER_ID.fullmatch(owner_id):
        result = _base(
            as_of_text,
            outcome="content_owner_missing",
            statement="The named content owner is missing or not an owner id. Nothing was reviewed.",
            inventory_id=inventory_id,
        )
        result["stripped_keys"] = sorted(set(stripped))
        _force(result)
        return result

    principals_raw = working.get("requesting_user")
    principals: list[str] = []
    if isinstance(principals_raw, dict):
        for item in principals_raw.get("principals") or []:
            if isinstance(item, str) and PRINCIPAL.fullmatch(item) and item not in principals:
                principals.append(item)
    if not principals:
        result = _base(
            as_of_text,
            outcome="principals_missing",
            statement="No requesting principal was supplied. Pages were not read.",
            inventory_id=inventory_id,
        )
        result["content_owner_id"] = owner_id
        result["stripped_keys"] = sorted(set(stripped))
        _force(result)
        return result

    pages_raw = working.get("pages")
    if not isinstance(pages_raw, list):
        result = _base(
            as_of_text,
            outcome="pages_unparseable",
            statement="The page list could not be read. Nothing was reviewed and no empty list was assumed.",
            inventory_id=inventory_id,
        )
        result["content_owner_id"] = owner_id
        result["stripped_keys"] = sorted(set(stripped))
        _force(result)
        return result

    policies, policy_problem = _read_policies(working.get("policies"))
    withheld = {"not_permitted": 0, "unreadable": 0, "ids_recorded": False, "titles_recorded": False, "bodies_recorded": False}
    admitted = []
    signals: list[dict] = []
    mask_kinds: set[str] = set()

    for raw in pages_raw:
        if not isinstance(raw, dict):
            withheld["unreadable"] += 1
            continue
        page = dict(raw)
        stripped.extend(_strip_prohibited(page))
        page_id = page.get("page_id")
        if not isinstance(page_id, str) or not PAGE_ID.fullmatch(page_id):
            withheld["unreadable"] += 1
            continue
        readers = page.get("readers")
        allowed = set()
        if isinstance(readers, list):
            allowed = {item for item in readers if isinstance(item, str) and PRINCIPAL.fullmatch(item)}
        if not allowed.intersection(principals):
            withheld["not_permitted"] += 1
            continue
        text = page.get("text") if isinstance(page.get("text"), str) else ""
        too_large = len(text) > MAX_CHARS
        matching = ""
        injection = {"detected": False, "followed": False, "signals": []}
        comment_text = ""
        if text and not too_large:
            comment_text = comments_for_marking(text)
            matching, injection = prepare_text(text)
            signals.extend(injection["signals"])
        meta_name, meta_rank, meta_bad = _meta_marking(page.get("sensitivity"))
        content_name, content_rank = _scan_marking(matching)
        comment_name, comment_rank = _scan_marking(comment_text)
        marking = _combine_marking(meta_name, meta_rank, meta_bad, content_name, content_rank, comment_name, comment_rank)
        title = page.get("title") if isinstance(page.get("title"), str) else ""
        title = " ".join(title.split())[:120]
        admitted.append(
            {
                "page_id": page_id,
                "title": title,
                "url": page.get("url") if isinstance(page.get("url"), str) and page.get("url", "").startswith("/") else None,
                "owner_id": page.get("owner_id"),
                "owner_status": page.get("owner_status"),
                "last_reviewed_raw": page.get("last_reviewed"),
                "interval_raw": page.get("review_interval_days"),
                "views_raw": page.get("page_views"),
                "retention_raw": page.get("retention_label"),
                "legal_hold_raw": page.get("legal_hold"),
                "links": page.get("links") if isinstance(page.get("links"), list) else [],
                "contacts": page.get("contacts") if isinstance(page.get("contacts"), list) else [],
                "policy_citations": page.get("policy_citations") if isinstance(page.get("policy_citations"), list) else [],
                "linked_file_ids": page.get("linked_file_ids") if isinstance(page.get("linked_file_ids"), list) else [],
                "text": text,
                "matching": matching,
                "too_large": too_large,
                "injection": injection,
                "marking": marking,
                "last_reviewed": None,
            }
        )

    ordinary = []
    for row in admitted:
        blocking_mark = row["marking"]["rank"] > 1 or row["marking"]["unrecognised"]
        safeguarding = any(cue in row["matching"].lower() for cue in SAFEGUARDING)
        row["safeguarding"] = safeguarding
        if blocking_mark or safeguarding or row["too_large"] or not row["matching"]:
            row["gateway"] = {"called": False, "entity_types": [], "values_recorded": False}
            row["classification"] = {"called": False, "legal_hold": False, "personal_data_indicated": False, "text_recorded": False}
            continue
        ordinary.append(row)

    gateway_types: list[str] = []
    classify_called = 0
    try:
        for row in ordinary:
            gateway = _call_gateway(row["text"])
            reviewed_day, reviewed_status = _parse_day(row["last_reviewed_raw"])
            row["last_reviewed"] = reviewed_day.isoformat() if reviewed_day else None
            marking_name = row["marking"]["marking"] if row["marking"]["marking"] in HIGHER_MARKINGS else ""
            classification = _call_classify(
                row["page_id"],
                row["matching"],
                day,
                row["last_reviewed"] if reviewed_status == "ok" else None,
                marking_name,
            )
            row["gateway"] = gateway
            row["classification"] = classification
            classify_called += 1
            for entity in gateway["entity_types"]:
                if entity not in gateway_types:
                    gateway_types.append(entity)
        curator_rows = [row for row in ordinary if not row["safeguarding"]]
        curator = _curator_pairs(curator_rows, principals, day)
        if isinstance(working.get("linked_index"), dict):
            finder = _finder(working.get("linked_index"), selection if isinstance(selection, dict) else None, day)
        elif "linked_index" in working:
            finder = _finder(working.get("linked_index"), selection if isinstance(selection, dict) else None, day)
        else:
            finder = {
                "called": False,
                "reason": "no_linked_index",
                "text_recorded": False,
                "snippet_copied": False,
                "hits": {},
            }
    except NeighbourMissing as exc:
        raise FreshnessForbidden(
            "A required neighbouring experiment is not beside this folder. "
            "This review does not invent a substitute."
        ) from exc

    for row in admitted:
        if row.get("last_reviewed") is None:
            reviewed_day, _status = _parse_day(row["last_reviewed_raw"])
            row["last_reviewed"] = reviewed_day.isoformat() if reviewed_day else None
            row["reviewed_day"] = reviewed_day
            row["reviewed_status"] = _status
        else:
            row["reviewed_day"], row["reviewed_status"] = _parse_day(row["last_reviewed_raw"])
        row.setdefault("gateway", {"called": False, "entity_types": [], "values_recorded": False})
        row.setdefault("classification", {"called": False, "legal_hold": False, "personal_data_indicated": False})

    pair_map = {}
    for pair in curator.get("pairs") or []:
        for page_id in pair:
            pair_map.setdefault(page_id, [])
            for other in pair:
                if other != page_id and other not in pair_map[page_id]:
                    pair_map[page_id].append(other)

    findings: list[dict] = []
    queues: list[dict] = []
    summaries = []
    seen_pairs = set()
    titles_copied = 0
    snippets_copied = 0

    for row in admitted:
        flags: list[str] = []
        interval, interval_status = _parse_interval(row["interval_raw"])
        views, views_status = _parse_views(row["views_raw"])
        reviewed_day = row["reviewed_day"]
        reviewed_status = row["reviewed_status"]
        if interval_status == "unparseable":
            flags.append("review_interval_unparseable")
        elif interval_status == "out_of_range":
            flags.append("review_interval_out_of_range")
        elif interval_status == "absent":
            flags.append("review_interval_absent")
        if views_status == "unparseable":
            flags.append("page_views_unparseable")
        elif views_status == "out_of_range":
            flags.append("page_views_out_of_range")
        if reviewed_status == "unparseable":
            flags.append("last_reviewed_unparseable")

        hold_raw = row["legal_hold_raw"]
        if hold_raw is True:
            legal_hold = True
            hold_status = "ok"
        elif hold_raw is False or hold_raw is None:
            legal_hold = False
            hold_status = "ok" if hold_raw is False else "absent"
        else:
            legal_hold = None
            hold_status = "unparseable"
            flags.append("legal_hold_unparseable")
        if any(phrase in row["matching"].lower() for phrase in HOLD_PHRASES):
            legal_hold = True
        if row["classification"].get("legal_hold"):
            legal_hold = True

        retention = None
        retention_copied = False
        if isinstance(row["retention_raw"], str) and row["retention_raw"].strip():
            retention = " ".join(row["retention_raw"].split())[:80]
            retention_copied = True
        elif row["retention_raw"] not in (None, ""):
            flags.append("retention_label_unparseable")

        owner_status = row["owner_status"] if isinstance(row["owner_status"], str) else None
        owner_valid = isinstance(row["owner_id"], str) and OWNER_ID.fullmatch(row["owner_id"])
        orphan = False
        if owner_status is None:
            flags.append("owner_status_absent")
        elif owner_status not in OWNER_STATUS:
            flags.append("owner_status_unparseable")
        elif owner_status == "current" and owner_valid:
            orphan = False
        elif owner_status == "current" and not owner_valid:
            flags.append("owner_id_unparseable")
        else:
            orphan = True

        if row["too_large"]:
            flags.append("text_not_scanned")
        if row["safeguarding"]:
            flags.append("safeguarding")
        if row["marking"]["rank"] > 1 or row["marking"]["unrecognised"]:
            flags.append("protective_marking")
        if row["marking"]["conflict"]:
            flags.append("marking_conflict")
        if legal_hold is True:
            flags.append("legal_hold")
        if policy_problem:
            flags.append("policy_catalogue_unreadable")

        sensitive = row["safeguarding"] or row["marking"]["rank"] > 1 or row["marking"]["unrecognised"] or row["too_large"]
        tasks_blocked = sensitive or legal_hold is True or legal_hold is None

        structural: list[dict] = []

        if not tasks_blocked and interval_status == "ok" and reviewed_status == "ok" and reviewed_day is not None:
            due = reviewed_day + timedelta(days=interval)
            if day > due:
                evidence = {
                    "last_reviewed": reviewed_day.isoformat(),
                    "review_interval_days": interval,
                    "due": due.isoformat(),
                    "interval_is_statutory": False,
                }
                if views_status == "ok":
                    evidence["page_views"] = views
                    evidence["page_views_copied"] = True
                elif views_status != "absent":
                    evidence["page_views_copied"] = False
                structural.append({"type": "overdue_review", "evidence": evidence})
        elif not tasks_blocked and reviewed_status == "absent" and interval_status == "ok":
            structural.append(
                {
                    "type": "overdue_review",
                    "evidence": {
                        "last_reviewed": None,
                        "last_reviewed_status": "absent",
                        "review_interval_days": interval,
                        "due": None,
                        "interval_is_statutory": False,
                        "never_reviewed": True,
                    },
                }
            )

        if orphan and not tasks_blocked:
            structural.append(
                {
                    "type": "orphaned_owner",
                    "evidence": {
                        "owner_status": owner_status,
                        "reassigns_ownership": False,
                    },
                }
            )

        cited = set()
        for item in row["policy_citations"]:
            if isinstance(item, str) and POLICY_KEY.fullmatch(item):
                cited.add(item)
        if not sensitive:
            for found in POLICY_ID.findall(row["matching"]):
                cited.add(found)
            if WITHDRAWN_PHRASE.search(row["matching"]) and not any(
                policies.get(item, {}).get("status") in {"superseded", "withdrawn"} for item in cited
            ):
                structural.append(
                    {
                        "type": "withdrawn_guidance_mentioned",
                        "evidence": {"policy_id": None, "catalogue_matched": False},
                    }
                )
        for policy_id in sorted(cited):
            policy = policies.get(policy_id)
            if policy is None:
                if not tasks_blocked:
                    flags.append("policy_not_in_catalogue")
                continue
            if policy["status"] == "unparseable":
                flags.append("policy_status_unparseable")
                continue
            if policy["status"] in {"superseded", "withdrawn"} and not tasks_blocked:
                structural.append(
                    {
                        "type": "withdrawn_policy" if policy["status"] == "withdrawn" else "superseded_policy",
                        "evidence": {
                            "policy_id": policy_id,
                            "status": policy["status"],
                            "superseded_by": policy.get("superseded_by"),
                        },
                    }
                )
            elif (
                policy["status"] == "current"
                and policy.get("effective_to_status") == "ok"
                and policy.get("effective_to_day") is not None
                and policy["effective_to_day"] < day
            ):
                flags.append("policy_date_conflict")
            elif policy.get("effective_to_status") == "unparseable" or policy.get("effective_from_status") == "unparseable":
                flags.append("policy_date_unparseable")

        for link in row["links"]:
            if not isinstance(link, dict):
                flags.append("link_unparseable")
                continue
            state = link.get("state")
            href = link.get("href") if isinstance(link.get("href"), str) else ""
            if not isinstance(state, str) or state not in LINK_STATE or not HREF.fullmatch(href):
                flags.append("link_unparseable")
                continue
            checked_day, checked_status = _parse_day(link.get("last_checked")) if "last_checked" in link else (None, "absent")
            if checked_status == "unparseable":
                flags.append("link_last_checked_unparseable")
                continue
            kind = None
            if state == "broken":
                kind = "broken_link"
            elif state == "stale":
                kind = "stale_link"
            elif state == "ok" and checked_status == "ok" and checked_day is not None and (day - checked_day).days > LINK_STALE_AFTER_DAYS:
                kind = "stale_link"
            if kind and not tasks_blocked and not sensitive:
                structural.append(
                    {
                        "type": kind,
                        "evidence": {
                            "href": href,
                            "state": state,
                            "last_checked": checked_day.isoformat() if checked_day else None,
                            "window_days": LINK_STALE_AFTER_DAYS,
                            "window_is_statutory": False,
                        },
                    }
                )
            elif kind and tasks_blocked:
                flags.append("structural_issue_not_tasked")

        for contact in row["contacts"]:
            if not isinstance(contact, dict):
                flags.append("contact_unparseable")
                continue
            status = contact.get("status")
            if not isinstance(status, str) or status not in CONTACT_STATUS:
                flags.append("contact_status_unparseable")
                continue
            if status == "former" and not tasks_blocked:
                evidence = _contact_evidence(contact, mask_kinds)
                structural.append(
                    {
                        "type": "stale_contact",
                        "evidence": evidence or {"status": "former", "raw_copied": False},
                    }
                )

        linked_ids = []
        for file_id in row["linked_file_ids"]:
            if not isinstance(file_id, str) or not FILE_ID.fullmatch(file_id):
                flags.append("linked_file_id_unparseable")
                continue
            linked_ids.append(file_id)
        if finder.get("called") and not tasks_blocked:
            hits = finder.get("hits") or {}
            for file_id in linked_ids:
                hit = hits.get(file_id)
                if hit is None:
                    flags.append("linked_file_not_in_matches")
                    continue
                if hit["likely_stale"] or hit["superseded"] or hit["likely_duplicate"]:
                    structural.append(
                        {
                            "type": "linked_file",
                            "evidence": {
                                "file_id": file_id,
                                "likely_stale": hit["likely_stale"],
                                "superseded": hit["superseded"],
                                "superseded_by": hit["superseded_by"],
                                "later_version_not_in_view": hit["later_version_not_in_view"],
                                "likely_duplicate": hit["likely_duplicate"],
                                "sensitivity_label": hit["sensitivity_label"],
                                "legal_hold": hit["legal_hold"],
                                "retention_label": hit["retention_label"],
                                "snippet_copied": False,
                            },
                        }
                    )
        duplicates = sorted(pair_map.get(row["page_id"], []))
        if duplicates and not tasks_blocked:
            key = tuple(sorted([row["page_id"], *duplicates]))
            if key not in seen_pairs:
                seen_pairs.add(key)
                structural.append(
                    {
                        "type": "likely_duplicate",
                        "page_ids": list(key),
                        "evidence": {
                            "source": "exp-50-sharepoint-knowledge-curator",
                            "text_recorded": False,
                            "archive_followed": False,
                        },
                    }
                )

        copy_title = not sensitive and not row["safeguarding"] and row["marking"]["rank"] <= 1 and not row["marking"]["unrecognised"]
        title_out = None
        if copy_title and row["title"]:
            masked_title, kinds = mask_snippet(row["title"])
            if kinds:
                for kind in kinds:
                    mask_kinds.add(kind)
                title_out = masked_title
            elif masked_title == row["title"]:
                title_out = row["title"]
            titles_copied += 1
        summary = {
            "page_id": row["page_id"],
            "marking": row["marking"]["marking"],
            "marking_rank": row["marking"]["rank"],
            "marking_sources": row["marking"]["sources"],
            "marking_conflict": row["marking"]["conflict"],
            "title_copied": title_out is not None,
            "title": title_out,
            "body_copied": False,
            "legal_hold": legal_hold is True,
            "legal_hold_unparseable": hold_status == "unparseable",
            "retention_label": retention if retention_copied else None,
            "retention_label_copied": retention_copied,
            "field_flags": sorted(set(flags)),
            "routine": not tasks_blocked and not flags,
        }
        if views_status == "ok":
            summary["page_views"] = views
            summary["page_views_copied"] = True
        else:
            summary["page_views_copied"] = False
            summary["page_views_status"] = views_status
        summaries.append(summary)

        if tasks_blocked or flags:
            queue_evidence = {
                "body_copied": False,
                "title_copied": title_out is not None,
            }
            if not sensitive:
                queue_evidence["field_flags"] = sorted(set(flags))
            else:
                queue_evidence["field_flags"] = [flag for flag in sorted(set(flags)) if flag in {
                    "safeguarding", "protective_marking", "marking_conflict", "legal_hold",
                    "legal_hold_unparseable", "text_not_scanned", "structural_issue_not_tasked",
                }]
            queues.append(
                {
                    "page_id": row["page_id"],
                    "reasons": sorted(set(flags)) if flags else ["needs_a_person"],
                    "marking": row["marking"]["marking"],
                    "marking_sources": row["marking"]["sources"],
                    "retention_label": retention if retention_copied else None,
                    "legal_hold": legal_hold is True,
                    "body_copied": False,
                    "title_copied": False if sensitive else title_out is not None,
                    "routine_task_proposed": False if tasks_blocked else None,
                    "evidence": queue_evidence,
                }
            )

        if tasks_blocked:
            continue
        for item in structural:
            page_ids = item.get("page_ids") or [row["page_id"]]
            findings.append(
                {
                    "type": item["type"],
                    "page_ids": page_ids,
                    "evidence": item["evidence"],
                    "snippet": None,
                    "snippet_copied": False,
                    "body_copied": False,
                    "routine": True,
                }
            )

    findings.sort(key=lambda item: (item["type"], tuple(item["page_ids"]), json.dumps(item["evidence"], sort_keys=True, default=str)))
    deduped = []
    seen_findings = set()
    for item in findings:
        key = (item["type"], tuple(item["page_ids"]), json.dumps(item["evidence"], sort_keys=True, default=str))
        if key in seen_findings:
            continue
        seen_findings.add(key)
        deduped.append(item)
    for index, item in enumerate(deduped, start=1):
        item["finding_id"] = f"F-{index:04d}"

    tasks = []
    for index, item in enumerate(deduped, start=1):
        tasks.append(
            {
                "task_id": f"TASK-{index:04d}",
                "finding_id": item["finding_id"],
                "page_ids": item["page_ids"],
                "type": item["type"],
                "title": f"Review {', '.join(item['page_ids'])}: {item['type'].replace('_', ' ')}",
                "assigned_to_role": "Content owner",
                "assigned_to_id": owner_id,
                "reassigns_ownership": False,
                "created": False,
                "messages_staff": False,
            }
        )
    queues.sort(key=lambda item: item["page_id"])
    tasked_pages = {page_id for task in tasks for page_id in task["page_ids"]}
    blocking_reasons = {
        "safeguarding",
        "protective_marking",
        "legal_hold",
        "legal_hold_unparseable",
        "text_not_scanned",
    }
    for index, item in enumerate(queues, start=1):
        item["queue_id"] = f"HQ-{index:04d}"
        item["routine_task_proposed"] = item["page_id"] in tasked_pages and not any(
            reason in blocking_reasons for reason in item["reasons"]
        )

    if deduped:
        statement = (
            "These findings are proposals. The named content owner approves each task "
            "before a stub is recorded. No page was edited."
        )
        outcome = "report"
    elif queues:
        statement = "Nothing was proposed as a routine task. A person should read the queue. No page was edited."
        outcome = "queue_only"
    else:
        statement = "No freshness finding was produced from the pages that could be read. No page was edited."
        outcome = "no_finding"

    result = _base(as_of_text, outcome=outcome, statement=statement, inventory_id=inventory_id)
    result["content_owner_id"] = owner_id
    result["page_summaries"] = summaries
    result["findings"] = deduped
    result["human_queue"] = queues
    result["proposed_tasks"] = tasks
    result["withheld"] = withheld
    seen = set()
    unique_signals = []
    for signal in signals:
        if signal["signal"] in seen:
            continue
        seen.add(signal["signal"])
        unique_signals.append(signal)
    result["injection"] = {"detected": bool(unique_signals), "followed": False, "signals": unique_signals}
    result["copying"] = {
        "page_bodies_copied": False,
        "titles_copied": titles_copied,
        "snippets_copied": snippets_copied,
        "mask_kinds_applied": sorted(mask_kinds),
        "contacts_raw_copied": False,
        "page_views_coerced_to_zero": False,
        "intervals_defaulted": False,
        "output_is_anonymised": False,
        "values_recorded": False,
    }
    finder_public = {key: value for key, value in finder.items() if key != "hits"}
    finder_public["linked_hit_ids"] = sorted((finder.get("hits") or {}).keys())
    finder_public["text_recorded"] = False
    finder_public["snippet_copied"] = False
    result["reuse"] = {
        "sharepoint_curator": curator,
        "onedrive_finder": finder_public,
        "records_classification": {
            "called": classify_called > 0,
            "experiment_id": "exp-49-records-classification",
            "catalogue_id": "M009",
            "pages_classified": classify_called,
            "text_recorded": False,
            "human_approval": None,
        },
        "identifier_gateway": {
            "called": classify_called > 0,
            "experiment_id": "exp-08-uk-pii-redaction-gateway",
            "entity_types": gateway_types,
            "values_recorded": False,
            "output_is_anonymised": False,
        },
    }
    if policy_problem:
        result["reuse"]["policy_catalogue"] = {"readable": False, "reason": policy_problem}
    result["stripped_keys"] = sorted(set(stripped))
    _force(result)
    return result


def _review_refusal(result: dict, reason: str) -> dict:
    refused = dict(result)
    refused["approval"] = {"recorded": False, "reason": reason, "executed": False}
    refused["human_approval"] = None
    refused["tasks_created"] = []
    _force(refused)
    return refused


def record_approval(draft: dict, review: dict) -> dict:
    """Record the content owner's decision. This does not create a task.

    ``review`` is a separate object. Page text cannot satisfy it.
    """

    if not isinstance(draft, dict) or not isinstance(review, dict):
        raise TypeError("draft and review must be objects")
    result = json.loads(json.dumps(draft))
    if result.get("label") != LABEL or result.get("catalogue_id") != CATALOGUE_ID:
        return _review_refusal(result if result.get("label") == LABEL else _base("unspecified", outcome="not_a_draft", statement="That object is not a freshness report."), "not_a_draft")
    decision = review.get("decision")
    if decision in PROHIBITED_DECISIONS or decision not in {"approve_tasks", "reject_tasks", "defer"}:
        return _review_refusal(result, "prohibited_decision")
    if review.get("actor_role") != "Content owner" or review.get("actor_id") != result.get("content_owner_id"):
        return _review_refusal(result, "actor")
    if review.get("inventory_id") != result.get("inventory_id"):
        return _review_refusal(result, "inventory_id")
    if not result.get("stale", {}).get("rules_current") and review.get("stale_seen") is not True:
        return _review_refusal(result, "stale_pin")
    if result.get("human_queue") and review.get("queue_reviewed") is not True:
        return _review_refusal(result, "queue_unreviewed")
    known = {task["task_id"] for task in result.get("proposed_tasks") or []}
    task_ids = review.get("task_ids")
    if decision == "approve_tasks":
        if not isinstance(task_ids, list) or not task_ids:
            return _review_refusal(result, "task_ids")
        if any(not isinstance(item, str) or item not in known or not TASK_ID.fullmatch(item) for item in task_ids):
            return _review_refusal(result, "task_ids")
        chosen = list(dict.fromkeys(task_ids))
    else:
        chosen = []
    result["human_approval"] = {
        "decision": decision,
        "actor_role": "Content owner",
        "actor_id": result.get("content_owner_id"),
        "task_ids": chosen,
        "via": "record_approval",
        "executed": False,
        "tasks_created_by_this_step": False,
    }
    result["approval"] = {"recorded": True, "reason": None, "executed": False}
    result["tasks_created"] = []
    _force(result)
    result["human_approval"] = {
        "decision": decision,
        "actor_role": "Content owner",
        "actor_id": draft.get("content_owner_id"),
        "task_ids": chosen,
        "via": "record_approval",
        "executed": False,
        "tasks_created_by_this_step": False,
    }
    return result


def create_approved_tasks(draft: dict) -> dict:
    """Record task stubs for task ids the content owner already approved.

    Planner and Power Automate are not called. Pages are not edited.
    """

    if not isinstance(draft, dict):
        raise TypeError("draft must be an object")
    result = json.loads(json.dumps(draft))
    approval = result.get("human_approval")
    if not isinstance(approval, dict) or approval.get("via") != "record_approval":
        return _review_refusal(result, "approval_missing")
    if approval.get("decision") != "approve_tasks":
        return _review_refusal(result, "not_approved")
    if approval.get("actor_role") != "Content owner" or approval.get("actor_id") != result.get("content_owner_id"):
        return _review_refusal(result, "actor")
    known = {task["task_id"]: task for task in result.get("proposed_tasks") or []}
    task_ids = approval.get("task_ids")
    if not isinstance(task_ids, list) or not task_ids:
        return _review_refusal(result, "task_ids")
    if any(not isinstance(item, str) or item not in known for item in task_ids):
        return _review_refusal(result, "task_ids")
    stubs = []
    for number, task_id in enumerate(task_ids, start=1):
        task = known[task_id]
        stubs.append(
            {
                "stub_id": f"STUB-{number:04d}",
                "task_id": task_id,
                "title": task["title"],
                "assigned_to_role": "Content owner",
                "assigned_to_id": result.get("content_owner_id"),
                "reassigns_ownership": False,
                "page_ids": task["page_ids"],
                "planner_request_not_sent": {
                    "method": "POST",
                    "path": "/planner/tasks",
                    "title": task["title"],
                    "planId": None,
                    "called": False,
                },
                "power_automate_approval_not_sent": {
                    "action": "Start and wait for an approval",
                    "approval_type": "Approve/Reject - First to respond",
                    "called": False,
                },
                "created_in_planner": False,
                "body_copied": False,
            }
        )
    result["tasks_created"] = stubs
    result["approval"] = {"recorded": True, "reason": None, "executed": False, "stubs_recorded": True}
    approval = dict(approval)
    approval["tasks_created_by_this_step"] = True
    approval["executed"] = False
    result["human_approval"] = approval
    _force(result)
    result["human_approval"] = approval
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Review a synthetic intranet inventory")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--selection", type=Path)
    parser.add_argument("--as-of", required=True)
    args = parser.parse_args(argv)
    try:
        inventory = json.loads(args.input.read_text(encoding="utf-8"))
        selection = json.loads(args.selection.read_text(encoding="utf-8")) if args.selection else None
    except (OSError, json.JSONDecodeError) as exc:
        sys.stderr.write(f"Could not read input: {exc}\n")
        return 2
    try:
        result = review_inventory(inventory, args.as_of, selection)
    except FreshnessForbidden as exc:
        sys.stderr.write(str(exc) + "\n")
        return 2
    sys.stdout.write(json.dumps(result, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
