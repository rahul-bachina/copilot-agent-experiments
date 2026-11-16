#!/usr/bin/env python3
"""Prepare a collaboration-space onboarding pack. Autonomy A1.

The workspace owner approves membership and internal links on a separate
approval object. Text inside the request is not approval. Owner rights and
guest access are not applied unless that object says so explicitly. The
sample can record a simulated Microsoft Graph add. It does not call Graph.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from copy import deepcopy
from datetime import date
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from graph_sim import (  # noqa: E402
        OnboardingForbidden,
        add_guest_without_approval,
        call_live_graph,
        grant_owner_without_approval,
        share_file_external,
        share_link_external,
        simulate_membership,
    )
    from injection import prepare_text  # noqa: E402
    from labels import above, combine, content_marking, parse_metadata_label  # noqa: E402
    from masking import add_replacements, empty_mask_report, mask_text  # noqa: E402
    from reuse import (  # noqa: E402
        NeighbourMissing,
        digest_module,
        finder_module,
        manifest_module,
    )
    from sources import STALE_AFTER_DAYS, source_rows  # noqa: E402
else:
    from .graph_sim import (
        OnboardingForbidden,
        add_guest_without_approval,
        call_live_graph,
        grant_owner_without_approval,
        share_file_external,
        share_link_external,
        simulate_membership,
    )
    from .injection import prepare_text
    from .labels import above, combine, content_marking, parse_metadata_label
    from .masking import add_replacements, empty_mask_report, mask_text
    from .reuse import NeighbourMissing, digest_module, finder_module, manifest_module
    from .sources import STALE_AFTER_DAYS, source_rows

LABEL = (
    "DRAFT COLLABORATION SPACE ONBOARDING. "
    "NOTHING CHANGED UNTIL THE WORKSPACE OWNER APPROVES."
)
CATALOGUE_ID = "M010"
EXPERIMENT_ID = "exp-57-collaboration-space-onboarding"
AUTONOMY = "A1"
OWNER_ROLE = "Workspace owner"
MEMBER_PRINCIPAL = "SYN-PRIN-MEMBER"
FINDER_INDEX_ID = "SYN-IDX-0057"

ROLES = frozenset({"member", "owner"})
ACCOUNTS = frozenset({"internal", "guest", "external"})
GUEST_POLICIES = frozenset({"disabled", "owner_approval"})
APPLY_DECISIONS = frozenset({"approve", "defer", "refuse"})

SPACE_ID = re.compile(r"^SYN-SPACE-\d{4}$")
REQUEST_ID = re.compile(r"^SYN-REQ-\d{4}$")
PERSON_ID = re.compile(r"^SYN-PERSON-\d{4}$")
CHANNEL_ID = re.compile(r"^SYN-CH-[A-Z0-9-]{1,24}$")
FILE_ID = re.compile(r"^SYN-OD-\d{4}$")
LOCATION_ID = re.compile(r"^LOC-[A-Z0-9-]{1,24}$")
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
CLEARANCE_CLAIM = re.compile(
    r"\b(?:my clearance is|i am cleared to|i'm cleared to|clearance is)\b",
    re.IGNORECASE,
)
RETENTION_IN_TEXT = re.compile(
    r"\bretention label:\s*([A-Za-z0-9][A-Za-z0-9 _-]{0,48})",
    re.IGNORECASE,
)
LEGAL_HOLD_IN_TEXT = re.compile(r"\blegal hold\b", re.IGNORECASE)

SAFEGUARDING = (
    "self-harm",
    "self harm",
    "suicide",
    "kill myself",
    "safeguarding",
    "domestic abuse",
    "child protection",
)

SIDE_EFFECT_KEYS = frozenset(
    {
        "human_approval",
        "applied",
        "approved",
        "owner_rights_approved",
        "guest_access_approved",
        "external_share_approved",
        "links_approved",
        "stale_seen",
        "safeguarding_reviewed",
        "clearance",
        "clearance_override",
        "self_declared_clearance",
        "graph_called",
        "live_graph_called",
        "confirmed",
        "executed",
        "owner_granted",
        "guest_granted",
        "access_widened",
        "actions_taken",
    }
)
REQUEST_OVERRIDE_KEYS = SIDE_EFFECT_KEYS | frozenset(
    {
        "principals",
        "location_ids",
        "selected_location_ids",
        "finder_query",
        "channel_digest_confirmation",
        "channel_export",
        "sensitivity_label",
        "guest_policy",
        "documents",
        "channels",
    }
)

__all__ = [
    "LABEL",
    "CATALOGUE_ID",
    "AUTONOMY",
    "OnboardingForbidden",
    "prepare_onboarding",
    "apply_membership",
    "draft_manifest",
    "share_file_external",
    "share_link_external",
    "grant_owner_without_approval",
    "add_guest_without_approval",
    "call_live_graph",
]


def _iso(value) -> date | None:
    if not isinstance(value, str) or not ISO_DATE.fullmatch(value):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _parse_as_of(value) -> date:
    if isinstance(value, date):
        return value
    parsed = _iso(str(value)[:10] if isinstance(value, str) else "")
    if parsed is None:
        raise ValueError("as_of")
    return parsed


def _strip(node: dict, keys: frozenset) -> list[str]:
    removed = []
    if not isinstance(node, dict):
        return removed
    for key in list(node):
        if key in keys:
            node.pop(key, None)
            removed.append(key)
    return removed


def _phrase_in(text: str, phrase: str) -> bool:
    if not isinstance(text, str) or not isinstance(phrase, str) or not phrase.strip():
        return False
    pattern = r"\b" + re.escape(phrase.strip()) + r"\b"
    return re.search(pattern, text, re.IGNORECASE) is not None


def _cue(text: str) -> bool:
    if not isinstance(text, str):
        return False
    lowered = text.lower()
    return any(cue in lowered for cue in SAFEGUARDING)


def _strings(value) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str)]
    return []


def _shell(outcome: str, statement: str, as_of: str) -> dict:
    return {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment_id": EXPERIMENT_ID,
        "autonomy": AUTONOMY,
        "outcome": outcome,
        "statement": statement,
        "as_of": as_of,
        "human_approval": None,
        "applied": False,
        "apply_outcome": None,
        "executed": False,
        "model_called": False,
        "network_called": False,
        "live_graph_called": False,
        "access_widened": False,
        "external_share_applied": False,
        "owner_granted": False,
        "guest_granted": False,
        "released_to_requester": False,
        "data_minimisation_met": False,
        "integrity_and_confidentiality_met": False,
        "clearance_decision": False,
        "self_declared_clearance_used": False,
        "coerced": False,
        "output_is_anonymised": False,
        "routine_processing": outcome == "proposal_ready",
        "justification_recorded": False,
        "document_extracts_copied": False,
        "external_urls_copied": False,
        "actions_taken": [],
        "graph": None,
        "masking": empty_mask_report(),
        "human_route": {
            "offered": True,
            "how": (
                "A person can ask the workspace owner directly. "
                "This agent does not change a team, a group, a file, or a link on its own."
            ),
        },
    }


def _seal(result: dict) -> dict:
    result["external_share_applied"] = False
    result["access_widened"] = False
    result["live_graph_called"] = False
    result["network_called"] = False
    result["model_called"] = False
    result["executed"] = False
    result["data_minimisation_met"] = False
    result["integrity_and_confidentiality_met"] = False
    result["clearance_decision"] = False
    result["self_declared_clearance_used"] = False
    result["coerced"] = False
    result["output_is_anonymised"] = False
    result["released_to_requester"] = False
    result["justification_recorded"] = False
    result["document_extracts_copied"] = False
    result["external_urls_copied"] = False
    result["owner_granted"] = result.get("owner_granted") is True
    result["guest_granted"] = result.get("guest_granted") is True
    result["applied"] = result.get("applied") is True
    injection = result.get("prompt_injection")
    if isinstance(injection, dict):
        injection["followed"] = False
        for signal in injection.get("signals") or []:
            if isinstance(signal, dict):
                signal["followed"] = False
    graph = result.get("graph")
    if isinstance(graph, dict):
        graph["live_graph_called"] = False
        graph["network_called"] = False
        for call in graph.get("calls") or []:
            if isinstance(call, dict):
                call["live_graph_called"] = False
                call["status_received"] = None
    return result


def _regulatory(as_of: str) -> dict:
    rows, current = source_rows(as_of)
    return {
        "sources_current": current,
        "sources": rows,
        "article_5_1_c": (
            "Data minimisation. data_minimisation_met stays false. "
            "This starter does not decide that the principle was met."
        ),
        "article_5_1_f": (
            "Integrity and confidentiality. integrity_and_confidentiality_met "
            "stays false. This starter does not decide that the principle was met."
        ),
        "article_5_2_opened": True,
        "article_6_opened": False,
        "article_9_opened": False,
        "gscp_is_statutory": False,
        "fixture_rank_is_the_policy": False,
        "ncsc_least_privilege_words_on_the_page_opened": False,
        "entra_review_created": False,
        "live_graph_called": False,
    }


def _holds(document: dict) -> dict:
    extract = document.get("extract") if isinstance(document.get("extract"), str) else ""
    labels: list[str] = []
    metadata = document.get("retention_label")
    if isinstance(metadata, str) and metadata.strip():
        labels.append(metadata.strip())
    for match in RETENTION_IN_TEXT.findall(extract):
        label = match.strip()
        if label and label not in labels:
            labels.append(label)
    hold = document.get("legal_hold") is True or bool(LEGAL_HOLD_IN_TEXT.search(extract))
    return {
        "legal_hold": hold,
        "retention_labels": labels,
        "retention_label": labels[0] if labels else None,
    }


def _document_marking(document: dict) -> tuple[str | None, bool]:
    meta, bad = parse_metadata_label(document.get("sensitivity_label"))
    content = content_marking(
        "\n".join(
            _strings(document.get("title"))
            + _strings(document.get("extract"))
            + _strings(document.get("cover_page"))
        )
    )
    return combine(meta, content), bad


def _channel_marking(channel: dict) -> tuple[str | None, bool]:
    meta, bad = parse_metadata_label(channel.get("sensitivity_label"))
    content = content_marking(
        "\n".join(
            _strings(channel.get("name"))
            + _strings(channel.get("purpose"))
            + _strings(channel.get("conventions"))
            + _strings(channel.get("cover_page"))
        )
    )
    return combine(meta, content), bad


def _container(space: dict) -> tuple[str | None, bool, list[str]]:
    markings: list[str] = []
    sources: list[str] = []
    unparseable = False
    meta, bad = parse_metadata_label(space.get("sensitivity_label"))
    unparseable = unparseable or bad
    if meta:
        markings.append(meta)
        sources.append("metadata")
    content_bits = _strings(space.get("cover_page")) + _strings(space.get("purpose"))
    content_bits += _strings(space.get("conventions"))
    for channel in space.get("channels") or []:
        if not isinstance(channel, dict):
            unparseable = True
            continue
        if channel.get("membership") == "private":
            continue
        marking, channel_bad = _channel_marking(channel)
        unparseable = unparseable or channel_bad
        if marking:
            markings.append(marking)
            sources.append("standard_channel")
    for document in space.get("documents") or []:
        if not isinstance(document, dict):
            unparseable = True
            continue
        marking, document_bad = _document_marking(document)
        unparseable = unparseable or document_bad
        if marking:
            markings.append(marking)
            sources.append("document")
    content = content_marking("\n".join(content_bits))
    if content:
        markings.append(content)
        sources.append("content")
    return combine(*markings), unparseable, sorted(set(sources))


def _needs(space: dict, cleaned: str) -> tuple[str | None, list[str], bool]:
    rows = space.get("access_needs")
    if not isinstance(rows, list) or not rows:
        return None, [], True
    matched: list[str] = []
    labels: list[str] = []
    unparseable = False
    for row in rows:
        if not isinstance(row, dict):
            unparseable = True
            continue
        phrase = row.get("phrase")
        label, bad = parse_metadata_label(row.get("label"))
        if not isinstance(phrase, str) or not phrase.strip() or bad or label is None:
            unparseable = True
            continue
        if _phrase_in(cleaned, phrase):
            matched.append(phrase.strip())
            labels.append(label)
    return combine(*labels), matched, unparseable


def _copy(text: str, report: dict) -> str:
    masked, detail = mask_text(text)
    add_replacements(report, detail)
    return masked


def _link_internal(link: dict) -> bool:
    if link.get("audience") != "internal":
        return False
    url = link.get("url")
    if not isinstance(url, str):
        return False
    return url.startswith("https://merrowfield.example.gov.uk/") or url.startswith(
        "https://example.gov.uk/"
    )


def _key_documents(space: dict, justified: str, as_of: str, report: dict) -> dict:
    location = space.get("document_location")
    if not isinstance(location, dict) or not LOCATION_ID.fullmatch(str(location.get("location_id") or "")):
        return {
            "called": False,
            "reason": "document_location_missing",
            "hits": [],
            "withheld_above_label": 0,
            "withheld_on_legal_hold": 0,
        }
    query = space.get("finder_query")
    if not isinstance(query, str) or not query.strip():
        return {
            "called": False,
            "reason": "finder_query_missing",
            "hits": [],
            "withheld_above_label": 0,
            "withheld_on_legal_hold": 0,
        }
    files = []
    withheld = 0
    withheld_hold = 0
    problems = []
    for document in space.get("documents") or []:
        if not isinstance(document, dict):
            problems.append("document_not_an_object")
            continue
        marking, bad = _document_marking(document)
        if bad:
            problems.append("document_label_unparseable")
            continue
        holds = _holds(document)
        if above(marking, justified):
            withheld += 1
            if holds["legal_hold"]:
                withheld_hold += 1
            continue
        file_id = document.get("file_id")
        modified = _iso(document.get("last_modified"))
        readers = document.get("readers")
        if marking is None:
            problems.append("document_label_missing")
            continue
        if not isinstance(file_id, str) or not FILE_ID.fullmatch(file_id) or modified is None:
            problems.append("document_identity_unparseable")
            continue
        if not isinstance(readers, list) or MEMBER_PRINCIPAL not in readers:
            problems.append("document_not_on_member_principal")
            continue
        title = document.get("title") if isinstance(document.get("title"), str) else ""
        files.append(
            {
                "file_id": file_id,
                "location_id": location["location_id"],
                "title": title,
                "last_modified": modified.isoformat(),
                "sensitivity_label": marking,
                "readers": [MEMBER_PRINCIPAL],
                "extract": document.get("extract") if isinstance(document.get("extract"), str) else "",
                "retention_label": holds["retention_label"],
                "legal_hold": holds["legal_hold"],
                "_holds": holds,
                "_title": title,
            }
        )
    if problems and not files:
        return {
            "called": False,
            "reason": "documents_not_usable",
            "problems": sorted(set(problems)),
            "hits": [],
            "withheld_above_label": withheld,
            "withheld_on_legal_hold": withheld_hold,
        }
    index = {
        "synthetic": True,
        "index_id": FINDER_INDEX_ID,
        "locations": [
            {
                "location_id": location["location_id"],
                "name": location.get("name") if isinstance(location.get("name"), str) else "Library",
            }
        ],
        "files": [
            {key: value for key, value in item.items() if not key.startswith("_")}
            for item in files
        ],
    }
    selection = {
        "confirmed": True,
        "actor_role": "Requesting user",
        "location_ids": [location["location_id"]],
        "principals": [MEMBER_PRINCIPAL],
        "clearance": justified,
    }
    by_id = {item["file_id"]: item for item in files}
    try:
        found = finder_module().find_documents(
            index,
            {"query": query},
            selection,
            as_of,
        )
    except NeighbourMissing as exc:
        return {
            "called": False,
            "reason": "neighbour_missing",
            "neighbour": str(exc),
            "hits": [],
            "withheld_above_label": withheld,
            "withheld_on_legal_hold": withheld_hold,
        }
    hits = []
    for hit in found.get("matches") or []:
        if not isinstance(hit, dict):
            continue
        file_id = hit.get("file_id")
        source = by_id.get(file_id)
        if source is None:
            continue
        holds = source["_holds"]
        title = _copy(source["_title"], report)
        hits.append(
            {
                "file_id": file_id,
                "title": title,
                "location_id": location["location_id"],
                "sensitivity_label": source["sensitivity_label"],
                "retention_label": holds["retention_label"],
                "retention_labels": holds["retention_labels"],
                "legal_hold": holds["legal_hold"],
                "extract_copied": False,
            }
        )
    return {
        "called": True,
        "experiment": "55-onedrive-document-finder",
        "outcome": found.get("outcome"),
        "human_approval": None,
        "finder_human_approval_was_null": found.get("human_approval") is None,
        "access_widened_by_finder": False,
        "hits": hits,
        "withheld_above_label": withheld,
        "withheld_on_legal_hold": withheld_hold,
        "statement": found.get("plain_statement") or found.get("statement"),
        "problems": sorted(set(problems)),
    }


def _digest(space: dict, justified: str, as_of: str, report: dict) -> dict:
    export = space.get("channel_export")
    confirmation = space.get("channel_digest_confirmation")
    if not isinstance(export, dict):
        return {"called": False, "reason": "not_in_fixture", "points": [], "approves_membership": False}
    if not isinstance(confirmation, dict):
        return {
            "called": False,
            "reason": "scope_confirmation_not_in_fixture",
            "points": [],
            "approves_membership": False,
        }
    try:
        produced = digest_module().produce_digest(deepcopy(export), deepcopy(confirmation), as_of)
    except NeighbourMissing as exc:
        return {
            "called": False,
            "reason": "neighbour_missing",
            "neighbour": str(exc),
            "points": [],
            "approves_membership": False,
        }
    points = []
    withheld = 0
    safeguarding = False
    digest = produced.get("digest") if isinstance(produced.get("digest"), dict) else {}
    for key in ("decisions", "open_questions", "actions", "attention"):
        for row in digest.get(key) or []:
            if not isinstance(row, dict) or not isinstance(row.get("text"), str):
                continue
            cleaned, _injection = prepare_text(row["text"])
            if _cue(cleaned):
                safeguarding = True
                withheld += 1
                continue
            if above(content_marking(row["text"]), justified):
                withheld += 1
                continue
            points.append(
                {
                    "point_id": row.get("point_id"),
                    "text": _copy(row["text"], report),
                    "kind": key,
                }
            )
    return {
        "called": True,
        "experiment": "51-teams-channel-digest",
        "outcome": produced.get("outcome"),
        "approves_membership": False,
        "approves_a_post": False,
        "points": points,
        "points_withheld": withheld,
        "safeguarding_withheld": safeguarding,
        "human_approval": None,
    }


def draft_manifest(record: dict, as_of: str, approve: bool = False) -> dict:
    """Draft a permissions manifest. ``approve=True`` is refused."""

    if approve:
        raise OnboardingForbidden(
            "The permissions-manifest generator cannot mark a manifest approved."
        )
    try:
        drafted = manifest_module().generate_manifest(record, as_of, approve=False)
    except NeighbourMissing as exc:
        return {
            "called": False,
            "reason": "neighbour_missing",
            "neighbour": str(exc),
            "approved": False,
            "may_be_relied_on": False,
        }
    if drafted.get("approved") is not False:
        raise OnboardingForbidden("Draft control lost the not-approved flag")
    return {
        "called": True,
        "experiment": "03-agent-inventory-atrs-assurance",
        "approved": False,
        "may_be_relied_on": False,
        "document_status": drafted.get("document_status"),
        "validation_passed": drafted.get("validation_passed") is True,
        "error_count": len(drafted.get("errors") or []),
        "yaml_copied": False,
    }


def _manifest_for(space: dict, request_id: str, as_of: str) -> dict:
    organisation = space.get("organisation")
    if not isinstance(organisation, str) or not organisation.strip():
        organisation = "Not recorded in the fixture"
    record = {
        "inventory_id": "exp-57-" + request_id.lower(),
        "name": "Collaboration space membership proposal",
        "sector": "public",
        "lifecycle_status": "proposed",
        "autonomy_level": "A1",
        "organisation_name": organisation[:200],
        "source_reviewed_on": as_of,
        "version": "0.1.0",
        "team": "Workspace owner",
        "contact_email": "workspace.owner@merrowfield.example.gov.uk",
        "experiment_path": "experiments/57-collaboration-space-onboarding",
        "processes_personal_data": "yes",
        "special_category_data": "unknown",
        "meaningful_human_involvement": "yes",
        "processing_regime": "uk_gdpr",
        "significant_effect": "none",
    }
    return draft_manifest(record, as_of, approve=False)


def _channels(space: dict, request: dict, justified: str) -> tuple[dict, bool]:
    raw = request.get("requested_channels", [])
    if raw is None:
        raw = []
    if not isinstance(raw, list):
        return {"unparseable": True}, True
    known = {}
    unparseable = False
    for channel in space.get("channels") or []:
        if not isinstance(channel, dict):
            unparseable = True
            continue
        if channel.get("membership") not in {"team", "private"}:
            unparseable = True
            continue
        channel_id = channel.get("channel_id")
        if not isinstance(channel_id, str) or not CHANNEL_ID.fullmatch(channel_id):
            unparseable = True
            continue
        marking, bad = _channel_marking(channel)
        if bad:
            unparseable = True
            continue
        known[channel_id] = {
            "channel": channel,
            "marking": marking,
        }
    proposed = []
    withheld = []
    unknown = []
    private_recorded = []
    for channel_id in raw:
        if not isinstance(channel_id, str) or not CHANNEL_ID.fullmatch(channel_id):
            unknown.append(str(channel_id)[:40] if isinstance(channel_id, str) else "unparseable")
            continue
        row = known.get(channel_id)
        if row is None:
            unknown.append(channel_id)
            continue
        channel = row["channel"]
        marking = row["marking"]
        if above(marking, justified):
            withheld.append({"channel_id": channel_id, "reason": "above_justified_label"})
            continue
        need = channel.get("need_phrase")
        if channel.get("membership") == "private":
            if not isinstance(need, str) or not _phrase_in(prepare_text(str(request.get("justification") or ""))[0], need):
                withheld.append({"channel_id": channel_id, "reason": "private_channel_not_justified"})
                continue
            private_recorded.append(channel_id)
        proposed.append(
            {
                "channel_id": channel_id,
                "name": channel.get("name") if isinstance(channel.get("name"), str) else "",
                "purpose": channel.get("purpose") if isinstance(channel.get("purpose"), str) else "",
                "conventions": channel.get("conventions") if isinstance(channel.get("conventions"), str) else "",
                "membership": channel.get("membership"),
                "sensitivity_label": marking,
                "retention_label": channel.get("retention_label")
                if isinstance(channel.get("retention_label"), str)
                else None,
                "legal_hold": channel.get("legal_hold") is True,
            }
        )
    return {
        "unparseable": unparseable,
        "proposed": proposed,
        "withheld": withheld,
        "unknown": unknown,
        "private_recorded_only": private_recorded,
        "known": known,
    }, unparseable


def prepare_onboarding(space: dict, request: dict, as_of) -> dict:
    """Draft an explanation and a membership proposal. Nothing is applied."""

    try:
        day = _parse_as_of(as_of)
    except ValueError:
        result = _shell(
            "needs_human",
            "The as-of date could not be read. It was not replaced with a default.",
            "unparseable",
        )
        result["unparseable_fields"] = ["as_of"]
        result["regulatory"] = _regulatory("0001-01-01")
        return _seal(result)
    as_of_text = day.isoformat()
    if not isinstance(space, dict) or not isinstance(request, dict):
        result = _shell(
            "needs_human",
            "The space and the request have to be objects. Nothing was assumed.",
            as_of_text,
        )
        result["unparseable_fields"] = ["space_or_request"]
        result["regulatory"] = _regulatory(as_of_text)
        return _seal(result)

    working_space = deepcopy(space)
    working_request = deepcopy(request)
    stripped = _strip(working_space, SIDE_EFFECT_KEYS)
    stripped.extend(_strip(working_request, REQUEST_OVERRIDE_KEYS))
    for collection in ("documents", "channels"):
        for item in working_space.get(collection) or []:
            if isinstance(item, dict):
                stripped.extend(_strip(item, SIDE_EFFECT_KEYS))

    result = _shell("needs_human", "", as_of_text)
    result["stripped_keys"] = sorted(set(stripped))
    result["regulatory"] = _regulatory(as_of_text)
    result["space_id"] = working_space.get("space_id")
    result["request_id"] = working_request.get("request_id")
    result["prompt_injection"] = {"detected": False, "followed": False, "signals": []}

    if working_space.get("synthetic") is not True:
        result["outcome"] = "not_synthetic"
        result["statement"] = "The space is not marked synthetic. Nothing was prepared."
        result["routine_processing"] = False
        return _seal(result)

    unparseable: list[str] = []
    if not isinstance(working_space.get("space_id"), str) or not SPACE_ID.fullmatch(working_space["space_id"]):
        unparseable.append("space_id")
    if not isinstance(working_request.get("request_id"), str) or not REQUEST_ID.fullmatch(
        working_request["request_id"]
    ):
        unparseable.append("request_id")
    if not isinstance(working_request.get("person_ref"), str) or not PERSON_ID.fullmatch(
        working_request["person_ref"]
    ):
        unparseable.append("person_ref")
    role = working_request.get("requested_role")
    if role not in ROLES:
        unparseable.append("requested_role")
    account = working_request.get("account_type")
    if account not in ACCOUNTS:
        unparseable.append("account_type")
    guest_policy = working_space.get("guest_policy")
    if guest_policy not in GUEST_POLICIES:
        unparseable.append("guest_policy")
    justification = working_request.get("justification")
    if not isinstance(justification, str) or not justification.strip():
        unparseable.append("justification")
        justification = ""
    exported = _iso(working_space.get("exported_on"))
    if exported is None:
        unparseable.append("exported_on")
    if unparseable:
        result["outcome"] = "needs_human"
        result["statement"] = (
            "An input could not be read. It was not replaced with a default, "
            "and no membership was prepared."
        )
        result["unparseable_fields"] = unparseable
        result["role_proposed"] = None
        result["routine_processing"] = False
        return _seal(result)

    cleaned, injection = prepare_text(justification)
    result["prompt_injection"] = injection
    result["clearance_claim_ignored"] = bool(CLEARANCE_CLAIM.search(justification))
    result["role_requested"] = role
    result["account_type"] = account
    result["guest_policy"] = guest_policy
    result["person_ref"] = working_request["person_ref"]
    result["space_id"] = working_space["space_id"]
    result["request_id"] = working_request["request_id"]
    result["organisation"] = working_space.get("organisation")

    if _cue(cleaned):
        result["outcome"] = "safeguarding_review"
        result["statement"] = (
            "A safeguarding or distress cue needs a person. "
            "The request was not handled as routine onboarding."
        )
        result["routine_processing"] = False
        result["safeguarding"] = {"flagged": True, "quote_copied": False, "in_justification": True}
        result["effective_label"] = None
        result["explanation"] = None
        return _seal(result)

    container, container_bad, label_sources = _container(working_space)
    justified, matched, needs_bad = _needs(working_space, cleaned)
    if container_bad or needs_bad or container is None or justified is None:
        result["outcome"] = "needs_human"
        if container_bad or needs_bad:
            result["statement"] = (
                "The space label or an access-need row could not be read. "
                "It was not coerced to OFFICIAL, and nobody was added."
            )
        else:
            result["statement"] = (
                "The justification does not name a configured access need, "
                "or the space has no marking. OFFICIAL was not assumed, "
                "and nobody was added."
            )
        result["unparseable_fields"] = [
            name
            for name, flag in (
                ("space_label", container_bad),
                ("access_need", needs_bad),
            )
            if flag
        ]
        result["effective_label"] = container
        result["justified_label"] = justified
        result["routine_processing"] = False
        return _seal(result)

    result["effective_label"] = container
    result["label_sources"] = label_sources
    result["justified_label"] = justified
    result["justified_by"] = matched
    result["purview_container_label"] = (
        working_space.get("purview_container_label")
        if isinstance(working_space.get("purview_container_label"), str)
        else None
    )
    result["purview_label_is_not_a_gscp_tier"] = True

    exported_on = exported
    stale = (day - exported_on).days > STALE_AFTER_DAYS
    result["stale"] = stale
    result["exported_on"] = exported_on.isoformat()
    result["stale_window_days"] = STALE_AFTER_DAYS
    result["stale_window_is_a_starter_default"] = True

    if above(container, justified):
        result["outcome"] = "above_justified_label"
        result["statement"] = (
            "The space marking is above the label the justification supports. "
            "The person was not added, and titles were not copied."
        )
        result["routine_processing"] = False
        result["explanation"] = None
        result["titles_copied"] = False
        return _seal(result)

    if account in {"guest", "external"} and guest_policy == "disabled":
        result["outcome"] = "guest_refused"
        result["statement"] = (
            "The fixture guest policy does not allow a guest or external account. "
            "The person was not added, and no file or link was shared."
        )
        result["routine_processing"] = False
        result["explanation"] = None
        result["requires_explicit_guest_approval"] = True
        return _seal(result)

    channel_pack, channel_bad = _channels(working_space, working_request, justified)
    if channel_bad:
        result["outcome"] = "needs_human"
        result["statement"] = (
            "A channel could not be read. It was not treated as a team channel, "
            "and nobody was added."
        )
        result["unparseable_fields"] = ["channel"]
        result["routine_processing"] = False
        return _seal(result)

    owner_phrase = working_space.get("owner_need_phrase")
    owner_phrase_ok = isinstance(owner_phrase, str) and bool(owner_phrase.strip())
    if role == "owner" and owner_phrase_ok and _phrase_in(cleaned, owner_phrase):
        role_proposed = "owner"
        least = "owner_requested_and_justified"
    elif role == "owner":
        role_proposed = "member"
        least = "downgraded_owner_lacks_justification"
    else:
        role_proposed = "member"
        least = "member"
    result["role_proposed"] = role_proposed
    result["least_privilege"] = least
    result["requires_explicit_owner_approval"] = role_proposed == "owner"
    result["requires_explicit_guest_approval"] = account in {"guest", "external"}

    report = empty_mask_report()
    proposed_channels = []
    for row in channel_pack["proposed"]:
        proposed_channels.append(
            {
                "channel_id": row["channel_id"],
                "name": _copy(row["name"], report),
                "purpose": _copy(row["purpose"], report),
                "conventions": _copy(row["conventions"], report),
                "membership": row["membership"],
                "sensitivity_label": row["sensitivity_label"],
                "retention_label": row["retention_label"],
                "legal_hold": row["legal_hold"],
                "graph_channel_call": False,
                "private_channel_membership_simulated": False,
            }
        )
    purpose = working_space.get("purpose") if isinstance(working_space.get("purpose"), str) else ""
    conventions = [
        _copy(item, report)
        for item in _strings(working_space.get("conventions"))
        if not above(content_marking(item), justified) and not _cue(prepare_text(item)[0])
    ]
    internal_links = []
    external_withheld = 0
    for link in working_space.get("pinned_links") or []:
        if not isinstance(link, dict):
            external_withheld += 1
            continue
        if _link_internal(link):
            internal_links.append(
                {
                    "link_id": link.get("link_id"),
                    "title": _copy(link.get("title") if isinstance(link.get("title"), str) else "", report),
                    "url": link["url"],
                    "audience": "internal",
                    "shared_externally": False,
                    "approved_for_later_use": False,
                }
            )
        else:
            external_withheld += 1

    documents = _key_documents(working_space, justified, as_of_text, report)
    digest = _digest(working_space, justified, as_of_text, report)
    manifest = _manifest_for(working_space, working_request["request_id"], as_of_text)

    safeguarding_material = bool(digest.get("safeguarding_withheld"))
    for document in working_space.get("documents") or []:
        if isinstance(document, dict) and _cue(prepare_text(str(document.get("extract") or ""))[0]):
            safeguarding_material = True

    result["masking"] = report
    result["explanation"] = {
        "purpose": _copy(purpose, report) if purpose and not above(content_marking(purpose), justified) else None,
        "channels": proposed_channels,
        "channels_withheld": channel_pack["withheld"],
        "unknown_channels": channel_pack["unknown"],
        "conventions": conventions,
        "key_documents": documents.get("hits") or [],
        "pinned_links_internal": internal_links,
        "external_links_withheld": external_withheld,
        "external_urls_copied": False,
    }
    result["masking"] = report
    result["membership_proposal"] = {
        "group_id_recorded": working_space.get("group_id"),
        "team_id_recorded": working_space.get("team_id"),
        "role": role_proposed,
        "account_type": account,
        "channel_ids": [row["channel_id"] for row in proposed_channels],
        "private_channels_recorded_only": channel_pack["private_recorded_only"],
        "private_channel_api_opened": False,
        "unknown_channels": channel_pack["unknown"],
    }
    result["reuse"] = {
        "experiment_55": documents,
        "experiment_51": digest,
        "experiment_03": manifest,
    }
    result["safeguarding"] = {
        "flagged": safeguarding_material,
        "quote_copied": False,
        "in_justification": False,
    }
    if safeguarding_material:
        result["routine_processing"] = False
    result["outcome"] = "proposal_ready"
    result["statement"] = (
        "A membership proposal is ready for the workspace owner. "
        "Nothing has been changed."
    )
    if stale:
        result["statement"] = (
            "A membership proposal is ready, and the space export is older than "
            "the starter window. Nothing has been changed."
        )
    return _seal(result)


def apply_membership(pack: dict, approval: dict | None) -> dict:
    """Apply a proposal only from the workspace owner's approval object."""

    if not isinstance(pack, dict):
        raise TypeError("pack must be an object")
    result = deepcopy(pack)
    result["applied"] = False
    result["owner_granted"] = False
    result["guest_granted"] = False
    result["graph"] = None
    result["actions_taken"] = []
    result["apply_outcome"] = "approval_missing"
    result["human_approval"] = None
    if not isinstance(approval, dict):
        return _seal(result)
    decision = approval.get("decision")
    if approval.get("approver_role") != OWNER_ROLE:
        result["apply_outcome"] = "approval_not_from_owner"
        return _seal(result)
    if decision not in APPLY_DECISIONS:
        result["apply_outcome"] = "approval_unparseable"
        return _seal(result)
    if approval.get("request_id") != pack.get("request_id") or approval.get("space_id") != pack.get("space_id"):
        result["apply_outcome"] = "request_mismatch"
        return _seal(result)
    result["human_approval"] = {
        "decision": decision,
        "approver_role": OWNER_ROLE,
        "approver_ref": approval.get("approver_ref")
        if isinstance(approval.get("approver_ref"), str)
        else None,
        "source": "approval_object",
        "from_request_text": False,
    }
    if decision != "approve":
        result["apply_outcome"] = "approval_not_granted"
        return _seal(result)
    if pack.get("outcome") != "proposal_ready":
        result["apply_outcome"] = "not_applicable"
        return _seal(result)
    if pack.get("stale") is True and approval.get("stale_seen") is not True:
        result["apply_outcome"] = "stale_not_acknowledged"
        return _seal(result)
    if (pack.get("safeguarding") or {}).get("flagged") is True and approval.get("safeguarding_reviewed") is not True:
        result["apply_outcome"] = "safeguarding_not_reviewed"
        return _seal(result)
    role = pack.get("role_proposed")
    account = pack.get("account_type")
    if role == "owner":
        if approval.get("owner_rights_approved") is not True:
            result["apply_outcome"] = "owner_not_explicitly_approved"
            return _seal(result)
    elif role != "member":
        result["apply_outcome"] = "not_applicable"
        return _seal(result)
    guest = account in {"guest", "external"}
    if guest:
        if pack.get("guest_policy") != "owner_approval" or approval.get("guest_access_approved") is not True:
            result["apply_outcome"] = "guest_not_explicitly_approved"
            return _seal(result)
    if role == "member" and approval.get("owner_rights_approved") is True:
        result["owner_upgrade_refused"] = True
    result["owner_granted"] = role == "owner"
    result["guest_granted"] = guest
    result["applied"] = True
    result["apply_outcome"] = "applied"
    result["graph"] = simulate_membership(owner=role == "owner")
    result["actions_taken"] = [call["path"] for call in result["graph"]["calls"]]
    result["external_share_request_ignored"] = approval.get("external_share_approved") is True
    approved_links = approval.get("links_approved") is True
    explanation = result.get("explanation") if isinstance(result.get("explanation"), dict) else None
    if explanation is not None:
        for link in explanation.get("pinned_links_internal") or []:
            if isinstance(link, dict):
                link["approved_for_later_use"] = approved_links
                link["shared_externally"] = False
    result["internal_links_approved_for_later_use"] = approved_links
    return _seal(result)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Draft collaboration-space onboarding.")
    parser.add_argument("--space", required=True)
    parser.add_argument("--request", required=True)
    parser.add_argument("--approval")
    parser.add_argument("--as-of", required=True)
    args = parser.parse_args(argv)
    try:
        space = _load(Path(args.space))
        request = _load(Path(args.request))
        approval = _load(Path(args.approval)) if args.approval else None
    except (OSError, json.JSONDecodeError):
        sys.stderr.write("The input could not be read.\n")
        return 2
    pack = prepare_onboarding(space, request, args.as_of)
    if approval is not None:
        pack = apply_membership(pack, approval)
    json.dump(pack, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
