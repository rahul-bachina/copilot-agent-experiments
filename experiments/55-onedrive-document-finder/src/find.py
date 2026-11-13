#!/usr/bin/env python3
"""Find files in the locations the user has confirmed.

Autonomy A0. The search reads a synthetic index. It does not call Microsoft
Graph, Work IQ, or Purview. It does not move, delete, share, or change
permissions. A file outside the confirmed locations, a file the user cannot
read, and a file above the user's clearance are counted and not copied out.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from copy import deepcopy
from datetime import date, datetime
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from injection import prepare_text  # noqa: E402
    from mask import mask_snippet  # noqa: E402
    from reuse import (  # noqa: E402
        NeighbourMissing,
        classify_module,
        curate_module,
        gateway_module,
    )
    from sources import (  # noqa: E402
        FILE_STALE_AFTER_DAYS,
        SOURCES_PINNED_ON,
        STALE_AFTER_DAYS,
        source_rows,
    )
else:
    from .injection import prepare_text
    from .mask import mask_snippet
    from .reuse import NeighbourMissing, classify_module, curate_module, gateway_module
    from .sources import (
        FILE_STALE_AFTER_DAYS,
        SOURCES_PINNED_ON,
        STALE_AFTER_DAYS,
        source_rows,
    )

LABEL = "READ-ONLY ONEDRIVE FINDING FOR THE REQUESTING USER"
CATALOGUE_ID = "M007"
EXPERIMENT_ID = "exp-55-onedrive-document-finder"
AUTONOMY = "A0"
ORGANISATION = "Merrowfield Borough Council (fictional)"
MAX_CHARS = 20_000
DUPLICATE_JACCARD = 0.85
SNIPPET_CHARS = 160

FILE_ID = re.compile(r"^SYN-OD-\d{4}$")
LOCATION_ID = re.compile(r"^LOC-[A-Z0-9-]{1,24}$")
PRINCIPAL = re.compile(r"^SYN-PRIN-[A-Z0-9-]{1,24}$")
RETENTION = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 _-]{0,48}$")
WORD = re.compile(r"[a-z0-9]+")

CLEARANCE_RANK = {
    "OFFICIAL": 1,
    "OFFICIAL-SENSITIVE": 2,
    "SECRET": 3,
    "TOP SECRET": 4,
}
HIGHER_MARKINGS = frozenset({"OFFICIAL-SENSITIVE", "SECRET", "TOP SECRET"})

STOPWORDS = frozenset(
    {
        "a", "an", "the", "of", "for", "and", "or", "in", "to", "on", "my",
        "find", "document", "documents", "file", "files", "please", "show",
        "me", "with", "from", "that", "this", "what", "where", "which",
        "about", "into", "your", "you", "is", "are", "was", "be", "it",
    }
)

SAFEGUARDING = (
    "self-harm",
    "self harm",
    "suicide",
    "kill myself",
    "safeguarding",
    "domestic abuse",
    "child protection",
)

PROHIBITED_KEYS = frozenset(
    {
        "human_approval",
        "deleted",
        "moved",
        "shared",
        "permissions_changed",
        "graph_called",
        "search_api_called",
        "work_iq_called",
        "purview_called",
        "access_widened",
        "clearance_override",
        "actions_taken",
        "executed",
        "selected_location_ids",
        "confirmed",
    }
)

PROHIBITED_DECISIONS = frozenset(
    {
        "move_file",
        "delete_file",
        "share_file",
        "change_permissions",
        "search_all",
        "widen_access",
        "reveal_above_clearance",
    }
)


class FinderForbidden(RuntimeError):
    """A file change, a share, or a widened search was requested."""


def move_file(*_args, **_kwargs) -> None:
    raise FinderForbidden("move_file is not a tool of this agent")


def delete_file(*_args, **_kwargs) -> None:
    raise FinderForbidden("delete_file is not a tool of this agent")


def share_file(*_args, **_kwargs) -> None:
    raise FinderForbidden("share_file is not a tool of this agent")


def change_permissions(*_args, **_kwargs) -> None:
    raise FinderForbidden("change_permissions is not a tool of this agent")


def _parse_as_of(value: date | datetime | str) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        return date.fromisoformat(value[:10])
    raise TypeError("as_of must be a date")


def _parse_day(value: object) -> date | None:
    if not isinstance(value, str) or len(value) < 10:
        return None
    try:
        return date.fromisoformat(value[:10])
    except ValueError:
        return None


def _strip_prohibited(mapping: dict) -> list[str]:
    removed = [key for key in list(mapping) if key in PROHIBITED_KEYS]
    for key in removed:
        mapping.pop(key, None)
    return removed


def _flags() -> dict:
    return {
        "moved": False,
        "deleted": False,
        "shared": False,
        "permissions_changed": False,
        "graph_called": False,
        "search_api_called": False,
        "work_iq_called": False,
        "purview_called": False,
        "access_widened": False,
        "full_extract_recorded": False,
    }


def _human_route() -> dict:
    return {
        "offered": True,
        "agent_searches_outside_selection": False,
        "agent_widens_access": False,
        "agent_changes_files": False,
    }


def _force(result: dict) -> None:
    result["human_route"] = _human_route()
    result["flags"] = _flags()
    result["model_called"] = False
    result["network_called"] = False
    result["executed"] = False
    result["actions_taken"] = []
    result["text_recorded"] = False
    if result.get("human_approval") is not None and not isinstance(result.get("human_approval"), dict):
        result["human_approval"] = None


def _label_rank(raw: object) -> tuple[str, int]:
    if raw is None or (isinstance(raw, str) and not raw.strip()):
        return "unmarked", 1
    if not isinstance(raw, str):
        return "unrecognised", 99
    text = " ".join(raw.split())
    upper = text.upper()
    if upper in {"NONE", "UNMARKED"}:
        return "unmarked", 1
    if "TOP SECRET" in upper:
        return text, 4
    if re.search(r"\bSECRET\b", upper) and "OFFICIAL-SENSITIVE" not in upper:
        return text, 3
    if "OFFICIAL-SENSITIVE" in upper or "OFFICIAL - SENSITIVE" in upper:
        return text, 2
    if upper == "OFFICIAL":
        return text, 1
    return text, 99


def _terms(text: str) -> list[str]:
    matching, _report = prepare_text(text)
    found = []
    for word in WORD.findall(matching.lower()):
        if word in STOPWORDS or word in found:
            continue
        found.append(word)
    return found


def _tokens(text: str) -> set[str]:
    return {word for word in WORD.findall(text.lower()) if word not in STOPWORDS and len(word) > 2}


def _jaccard(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def _base(as_of: str, *, outcome: str, statement: str, index_id: str = "unspecified") -> dict:
    age = (date.fromisoformat(as_of) - SOURCES_PINNED_ON).days
    rules_current = 0 <= age <= STALE_AFTER_DAYS
    result = {
        "label": LABEL,
        "experiment_id": EXPERIMENT_ID,
        "catalogue_id": CATALOGUE_ID,
        "autonomy": AUTONOMY,
        "organisation": ORGANISATION,
        "index_id": index_id,
        "as_of": as_of,
        "outcome": outcome,
        "plain_statement": statement,
        "query_terms": [],
        "selected_location_ids": [],
        "clearance": None,
        "matches": [],
        "withheld": {
            "outside_selection": 0,
            "not_permitted": 0,
            "above_clearance": 0,
            "unreadable": 0,
            "ids_recorded": False,
            "titles_recorded": False,
            "extracts_recorded": False,
        },
        "injection": {"detected": False, "followed": False, "signals": []},
        "human_approval": None,
        "regulatory": {
            "data_minimisation_met": False,
            "foi_duty_decided": False,
            "article_5_1_c": "read" if rules_current else "not_quoted",
            "quotes_included": rules_current,
        },
        "stale": {
            "rules_current": rules_current,
            "age_days": age,
            "stale_after_days": STALE_AFTER_DAYS,
            "file_window_days": FILE_STALE_AFTER_DAYS,
            "file_window_is_statutory": False,
        },
        "sources": source_rows(rules_current),
        "reuse": {
            "records_classification": {"called": False, "text_recorded": False},
            "sharepoint_curator": {"called": False, "text_recorded": False, "archive_followed": False},
            "identifier_gateway": {"called": False, "values_recorded": False},
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
        raise FinderForbidden("Experiment 08 returned an unexpected release flag")
    types: list[str] = []
    redacted = proposal.get("redacted_text")
    if not isinstance(redacted, str):
        redacted = ""
    for finding in proposal["audit_log"]["findings"]:
        if finding.get("applied") and finding.get("method") == "deterministic":
            entity = finding.get("entity_type")
            if isinstance(entity, str) and entity not in types:
                types.append(entity)
    return {
        "called": True,
        "experiment_id": "exp-08-uk-pii-redaction-gateway",
        "entity_types": types,
        "redacted_text": redacted,
        "output_is_anonymised": False,
        "values_recorded": False,
    }


def _call_classify(file_id: str, matching: str, as_of: date, modified: str | None, marking: str) -> dict:
    document = {
        "synthetic": True,
        "document_id": file_id,
        "filename": f"{file_id}.txt",
        "text": matching,
        "jurisdiction": "england",
        "document_date": modified,
    }
    if marking in HIGHER_MARKINGS:
        document["existing_marking"] = marking
    draft = classify_module().classify_record(document, as_of)
    hold = bool((draft.get("legal_hold") or {}).get("indicated"))
    personal = bool((draft.get("proposals") or {}).get("personal_data", {}).get("indicated"))
    suggestion = (draft.get("proposals") or {}).get("gsc", {}).get("suggestion")
    return {
        "called": True,
        "experiment_id": "exp-49-records-classification",
        "catalogue_id": "M009",
        "legal_hold": hold,
        "personal_data_indicated": personal,
        "marking_suggestion": suggestion if isinstance(suggestion, str) else None,
        "downgrade_proposed": False,
        "human_approval": None,
        "text_recorded": False,
    }


def _curator_pairs(rows: list[dict], principals: list[str], as_of: date) -> dict:
    usable = [row for row in principals if PRINCIPAL.fullmatch(row)]
    items = []
    reverse = {}
    for index, row in enumerate(rows, start=1):
        mapped = f"SYN-SP-{index:04d}"
        reverse[mapped] = row["file_id"]
        items.append(
            {
                "item_id": mapped,
                "kind": "document",
                "title": row["title"] or row["file_id"],
                "text": row["matching"],
                "readers": usable or ["SYN-PRIN-USER"],
                "sensitivity": "OFFICIAL" if row["label_rank"] == 1 else row["sensitivity_label"],
                "last_modified": row["last_modified"],
                "review_date": row["last_modified"],
                "published": True,
                "url": f"/{row['file_id'].lower()}",
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
            "site_id": "SYN-SITE-0055",
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


def _family_key(raw: dict) -> tuple[str, int] | None:
    family = raw.get("family_id")
    version = raw.get("version")
    if isinstance(family, str) and re.fullmatch(r"FAM-[A-Z0-9-]{1,24}", family) and isinstance(version, int):
        return family, version
    return None


def find_documents(
    index: dict,
    request: dict,
    selection: dict,
    as_of: date | datetime | str,
) -> dict:
    """Return a ranked list. ``human_approval`` stays null.

    ``selection`` is a separate object. A sentence in a file does not confirm
    locations, does not raise clearance, and does not approve a file change.
    """

    if not isinstance(index, dict) or not isinstance(request, dict) or not isinstance(selection, dict):
        raise TypeError("index, request, and selection must be objects")
    day = _parse_as_of(as_of)
    as_of_text = day.isoformat()
    working_index = dict(index)
    working_request = dict(request)
    working_selection = dict(selection)
    stripped = _strip_prohibited(working_index)
    stripped.extend(_strip_prohibited(working_request))
    index_id = working_index.get("index_id")
    if not isinstance(index_id, str) or not re.fullmatch(r"SYN-IDX-\d{4}", index_id):
        index_id = "unspecified"

    if working_index.get("synthetic") is not True:
        result = _base(
            as_of_text,
            outcome="not_synthetic",
            statement="The index is not marked synthetic. Nothing was searched.",
            index_id=index_id,
        )
        result["stripped_keys"] = sorted(set(stripped))
        _force(result)
        return result

    if working_selection.get("confirmed") is not True or working_selection.get("actor_role") != "Requesting user":
        result = _base(
            as_of_text,
            outcome="locations_not_confirmed",
            statement="No locations were confirmed. Nothing was searched.",
            index_id=index_id,
        )
        result["stripped_keys"] = sorted(set(stripped))
        _force(result)
        return result

    known = {}
    for location in working_index.get("locations") or []:
        if not isinstance(location, dict):
            continue
        location_id = location.get("location_id")
        name = location.get("name") if isinstance(location.get("name"), str) else ""
        if isinstance(location_id, str) and LOCATION_ID.fullmatch(location_id):
            known[location_id] = " ".join(name.split())[:80]

    chosen = []
    for location_id in working_selection.get("location_ids") or []:
        if isinstance(location_id, str) and location_id in known and location_id not in chosen:
            chosen.append(location_id)
    clearance_name = working_selection.get("clearance")
    if clearance_name not in CLEARANCE_RANK:
        clearance_name = None
    principals = [
        item
        for item in (working_selection.get("principals") or [])
        if isinstance(item, str) and PRINCIPAL.fullmatch(item)
    ]
    if not chosen or clearance_name is None or not principals:
        result = _base(
            as_of_text,
            outcome="no_locations_selected",
            statement="The confirmed selection has no location in this index that this user can be scoped to. Nothing was searched.",
            index_id=index_id,
        )
        result["selected_location_ids"] = chosen
        result["clearance"] = clearance_name
        result["stripped_keys"] = sorted(set(stripped))
        _force(result)
        return result

    query = working_request.get("query") if isinstance(working_request.get("query"), str) else ""
    query_matching, query_injection = prepare_text(query)
    terms = _terms(query_matching)
    if not terms:
        result = _base(
            as_of_text,
            outcome="empty_query",
            statement="The request has no search terms. Nothing was searched.",
            index_id=index_id,
        )
        result["selected_location_ids"] = chosen
        result["clearance"] = clearance_name
        result["injection"] = query_injection
        result["stripped_keys"] = sorted(set(stripped))
        _force(result)
        return result

    clearance_rank = CLEARANCE_RANK[clearance_name]
    chosen_set = set(chosen)
    withheld = {"outside_selection": 0, "not_permitted": 0, "above_clearance": 0, "unreadable": 0}
    admitted = []
    hidden_versions: dict[str, int] = {}
    visible_versions: dict[str, list[tuple[int, str]]] = {}
    signals = list(query_injection["signals"])

    for raw in working_index.get("files") or []:
        if not isinstance(raw, dict):
            withheld["unreadable"] += 1
            continue
        file_id = raw.get("file_id")
        location_id = raw.get("location_id")
        family = _family_key(raw)
        if not isinstance(file_id, str) or not FILE_ID.fullmatch(file_id):
            withheld["unreadable"] += 1
            continue
        if not isinstance(location_id, str) or location_id not in chosen_set:
            withheld["outside_selection"] += 1
            if family and (family[0] not in hidden_versions or family[1] > hidden_versions[family[0]]):
                hidden_versions[family[0]] = family[1]
            continue
        readers = raw.get("readers")
        allowed = set()
        if isinstance(readers, list):
            allowed = {item for item in readers if isinstance(item, str) and PRINCIPAL.fullmatch(item)}
        if not allowed.intersection(principals):
            withheld["not_permitted"] += 1
            if family and (family[0] not in hidden_versions or family[1] > hidden_versions[family[0]]):
                hidden_versions[family[0]] = family[1]
            continue
        sensitivity_label, rank = _label_rank(raw.get("sensitivity_label", raw.get("sensitivity")))
        if rank > clearance_rank:
            withheld["above_clearance"] += 1
            if family and (family[0] not in hidden_versions or family[1] > hidden_versions[family[0]]):
                hidden_versions[family[0]] = family[1]
            continue
        title = raw.get("title") if isinstance(raw.get("title"), str) else ""
        title = " ".join(title.split())[:120]
        extract = raw.get("extract") if isinstance(raw.get("extract"), str) else ""
        too_large = len(extract) > MAX_CHARS
        matching = ""
        injection = {"detected": False, "followed": False, "signals": []}
        if extract and not too_large:
            matching, injection = prepare_text(extract)
            signals.extend(injection["signals"])
        modified = raw.get("last_modified") if isinstance(raw.get("last_modified"), str) else None
        modified_day = _parse_day(modified)
        retention = raw.get("retention_label")
        if not isinstance(retention, str) or not RETENTION.fullmatch(retention.strip()):
            retention = "present" if retention else None
        else:
            retention = retention.strip()
        admitted.append(
            {
                "file_id": file_id,
                "title": title,
                "location_id": location_id,
                "location_name": known.get(location_id, ""),
                "last_modified": modified_day.isoformat() if modified_day else None,
                "modified_day": modified_day,
                "sensitivity_label": sensitivity_label,
                "label_rank": rank,
                "retention_label": retention,
                "legal_hold_fixture": raw.get("legal_hold") is True,
                "matching": matching,
                "extract": "" if too_large else extract,
                "too_large": too_large,
                "family": family,
                "injection": injection,
            }
        )
        if family:
            visible_versions.setdefault(family[0], []).append((family[1], file_id))

    gateway_types: list[str] = []
    classify_called = 0
    try:
        for row in admitted:
            original = row.pop("extract")
            if row["too_large"] or original == "":
                row["gateway"] = {"called": False, "entity_types": [], "redacted_text": "", "values_recorded": False}
                row["classification"] = {"called": False, "legal_hold": False, "personal_data_indicated": False}
                continue
            gateway = _call_gateway(original)
            marking = row["sensitivity_label"] if row["sensitivity_label"] in HIGHER_MARKINGS else ""
            classification = _call_classify(
                row["file_id"],
                row["matching"],
                day,
                row["last_modified"],
                marking,
            )
            row["gateway"] = gateway
            row["classification"] = classification
            classify_called += 1
            for entity in gateway["entity_types"]:
                if entity not in gateway_types:
                    gateway_types.append(entity)
        curator = _curator_pairs(admitted, principals, day)
    except NeighbourMissing as exc:
        raise FinderForbidden(
            "A required neighbouring experiment is not beside this folder. "
            "This finder does not invent a substitute."
        ) from exc

    curator_pairs = {tuple(pair) for pair in curator.get("pairs") or []}
    hashes: dict[str, list[str]] = {}
    for row in admitted:
        digest = hashlib.sha256(row["matching"].encode("utf-8")).hexdigest() if row["matching"] else ""
        row["digest"] = digest
        row["tokens"] = _tokens(row["matching"]) if row["matching"] else set()
        if digest:
            hashes.setdefault(digest, []).append(row["file_id"])

    matches = []
    for row in admitted:
        title_hits = [term for term in terms if term in row["title"].lower()]
        location_hits = [term for term in terms if term in row["location_name"].lower()]
        extract_hits = [term for term in terms if term in row["matching"].lower()]
        covered = set(title_hits) | set(location_hits) | set(extract_hits)
        if any(term not in covered for term in terms):
            continue
        score = 3 * len(title_hits) + 2 * len(extract_hits) + len(location_hits)
        reasons = []
        if title_hits:
            reasons.append("title matched: " + ", ".join(title_hits))
        if extract_hits:
            reasons.append("extract matched: " + ", ".join(extract_hits))
        if location_hits:
            reasons.append("location matched: " + ", ".join(location_hits))
        safeguarding = any(cue in row["matching"].lower() for cue in SAFEGUARDING)
        legal_hold = row["legal_hold_fixture"] or bool(row["classification"].get("legal_hold"))
        if legal_hold:
            reasons.append("legal hold kept")
        if row["retention_label"]:
            reasons.append(f"retention label kept: {row['retention_label']}")
        reasons.append("sensitivity label kept")
        stale = False
        if row["modified_day"] is not None and (day - row["modified_day"]).days > FILE_STALE_AFTER_DAYS:
            stale = True
            reasons.append(
                "likely stale: last modified more than 365 days before the as-of date. "
                "The window is configuration, not a statutory period."
            )
        superseded = False
        superseded_by = None
        later_hidden = False
        if row["family"]:
            family_id, version = row["family"]
            higher = [item for item in visible_versions.get(family_id, []) if item[0] > version]
            if higher:
                superseded = True
                superseded_by = sorted(higher, key=lambda item: (-item[0], item[1]))[0][1]
                reasons.append(f"superseded by {superseded_by} in the permitted view")
            hidden_version = hidden_versions.get(family_id)
            if hidden_version is not None and hidden_version > version and not higher:
                later_hidden = True
                reasons.append("a later version is in the index and is not in this view. Its name was not copied.")
        duplicate_of = []
        for other in hashes.get(row["digest"], []):
            if other != row["file_id"] and other not in duplicate_of:
                duplicate_of.append(other)
        for pair in curator_pairs:
            if row["file_id"] in pair:
                for other in pair:
                    if other != row["file_id"] and other not in duplicate_of:
                        duplicate_of.append(other)
        if not duplicate_of and row["tokens"]:
            for other in admitted:
                if other["file_id"] == row["file_id"] or not other["tokens"]:
                    continue
                if _jaccard(row["tokens"], other["tokens"]) >= DUPLICATE_JACCARD:
                    duplicate_of.append(other["file_id"])
        duplicate_of = sorted(duplicate_of)
        if duplicate_of:
            reasons.append("likely duplicate of " + ", ".join(duplicate_of))
        snippet = None
        if safeguarding:
            reasons.append("safeguarding cue. A person should read the file. The extract was not copied.")
        elif extract_hits and row["matching"]:
            redacted = row["gateway"].get("redacted_text") or row["matching"]
            masked = mask_snippet(redacted)
            snippet = _window(masked, extract_hits)
        personal = bool(row["classification"].get("personal_data_indicated")) or bool(row["gateway"].get("entity_types"))
        matches.append(
            {
                "file_id": row["file_id"],
                "title": mask_snippet(row["title"]) if row["title"] else row["file_id"],
                "location_id": row["location_id"],
                "location_name": row["location_name"],
                "last_modified": row["last_modified"],
                "sensitivity_label": row["sensitivity_label"],
                "retention_label": row["retention_label"],
                "legal_hold": legal_hold,
                "protective_marking_kept": True,
                "score": score,
                "reasons": reasons,
                "snippet": snippet,
                "likely_stale": stale,
                "superseded": superseded,
                "superseded_by": superseded_by,
                "later_version_not_in_view": later_hidden,
                "likely_duplicate": bool(duplicate_of),
                "duplicate_of": duplicate_of,
                "routine": not safeguarding,
                "human_flag": "safeguarding" if safeguarding else None,
                "identifier_types": list(row["gateway"].get("entity_types") or []),
                "personal_data_indicated": personal,
                "values_recorded": False,
                "output_is_anonymised": False,
            }
        )

    matches.sort(key=lambda item: (-item["score"], item["last_modified"] or "", item["file_id"]))
    for rank, item in enumerate(matches, start=1):
        item["rank"] = rank

    if matches:
        outcome = "matches"
        statement = "These files are in the locations you confirmed. Nothing outside those locations is listed."
    else:
        outcome = "no_match"
        statement = "Nothing in the permitted locations matches this request."
    result = _base(as_of_text, outcome=outcome, statement=statement, index_id=index_id)
    result["query_terms"] = terms
    result["selected_location_ids"] = chosen
    result["clearance"] = clearance_name
    result["matches"] = matches
    result["withheld"] = {
        **withheld,
        "ids_recorded": False,
        "titles_recorded": False,
        "extracts_recorded": False,
    }
    seen = set()
    unique_signals = []
    for signal in signals:
        if signal["signal"] in seen:
            continue
        seen.add(signal["signal"])
        unique_signals.append(signal)
    result["injection"] = {
        "detected": bool(unique_signals),
        "followed": False,
        "signals": unique_signals,
    }
    result["reuse"] = {
        "records_classification": {
            "called": classify_called > 0,
            "experiment_id": "exp-49-records-classification",
            "catalogue_id": "M009",
            "files_classified": classify_called,
            "text_recorded": False,
            "human_approval": None,
        },
        "sharepoint_curator": curator,
        "identifier_gateway": {
            "called": classify_called > 0,
            "experiment_id": "exp-08-uk-pii-redaction-gateway",
            "entity_types": gateway_types,
            "values_recorded": False,
            "output_is_anonymised": False,
        },
    }
    result["stripped_keys"] = sorted(set(stripped))
    _force(result)
    return result


def _window(masked: str, terms: list[str]) -> str | None:
    lower = masked.lower()
    positions = [lower.find(term) for term in terms]
    positions = [item for item in positions if item >= 0]
    if not positions:
        return None
    start = max(0, min(positions) - 40)
    return masked[start : start + SNIPPET_CHARS]


def acknowledge_results(result: dict, review: dict) -> dict:
    """Record that the user saw the list. This does not change a file."""

    if not isinstance(result, dict) or not isinstance(review, dict):
        raise TypeError("result and review must be objects")
    updated = deepcopy(result)
    _force(updated)
    updated["human_approval"] = None

    def refuse(reason: str) -> dict:
        updated["acknowledgement"] = {"recorded": False, "reason": reason, "executed": False}
        _force(updated)
        return updated

    if review.get("decision") in PROHIBITED_DECISIONS:
        return refuse("prohibited_decision")
    if review.get("actor_role") != "Requesting user":
        return refuse("actor_role")
    if review.get("index_id") != updated.get("index_id"):
        return refuse("index_id")
    if updated.get("outcome") not in {"matches", "no_match"}:
        return refuse("outcome")
    flagged = any(item.get("human_flag") for item in updated.get("matches") or [])
    if flagged and review.get("queue_reviewed") is not True:
        return refuse("queue_not_reviewed")
    if review.get("decision") not in {"acknowledge", "defer"}:
        return refuse("decision")
    if not updated.get("stale", {}).get("rules_current") and review.get("stale_seen") is not True:
        return refuse("stale_not_acknowledged")
    updated["acknowledgement"] = {
        "recorded": True,
        "decision": review["decision"],
        "actor_role": "Requesting user",
        "executed": False,
        "files_changed": False,
    }
    updated["human_approval"] = {
        "decision": review["decision"],
        "actor_role": "Requesting user",
        "executed": False,
        "files_changed": False,
    }
    _force(updated)
    updated["human_approval"] = {
        "decision": review["decision"],
        "actor_role": "Requesting user",
        "executed": False,
        "files_changed": False,
    }
    return updated


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Find files in confirmed locations")
    parser.add_argument("--index", required=True)
    parser.add_argument("--request", required=True)
    parser.add_argument("--selection", required=True)
    parser.add_argument("--as-of", required=True)
    args = parser.parse_args(argv)
    try:
        index = json.loads(Path(args.index).read_text(encoding="utf-8"))
        request = json.loads(Path(args.request).read_text(encoding="utf-8"))
        selection = json.loads(Path(args.selection).read_text(encoding="utf-8"))
        result = find_documents(index, request, selection, args.as_of)
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    json.dump(result, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
