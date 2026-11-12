#!/usr/bin/env python3
"""Propose curation actions for one synthetic SharePoint snapshot.

The site owner approves every metadata change and every publishing action.
``apply_approved_action`` records a stub only after that approval. The stub
does not call SharePoint or Microsoft Graph. Nothing in this module deletes,
unpublishes, moves, or changes permissions, and nothing reads the network.

Items the requesting user cannot already see are counted and not read.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from copy import deepcopy
from datetime import date, datetime, timedelta
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from injection import prepare_text  # noqa: E402
    from reuse import (  # noqa: E402
        NeighbourMissing,
        classify_module,
        gaps_module,
        gateway_module,
        intake_module,
    )
    from sources import SOURCES_PINNED_ON, STALE_AFTER_DAYS, source_rows  # noqa: E402
else:
    from .injection import prepare_text
    from .reuse import (
        NeighbourMissing,
        classify_module,
        gaps_module,
        gateway_module,
        intake_module,
    )
    from .sources import SOURCES_PINNED_ON, STALE_AFTER_DAYS, source_rows

LABEL = "DRAFT SHAREPOINT CURATION FOR SITE OWNER APPROVAL"
CATALOGUE_ID = "M001"
EXPERIMENT_ID = "exp-50-sharepoint-knowledge-curator"
AUTONOMY = "A1"
ORGANISATION = "Merrowfield Borough Council (fictional)"
REVIEW_WINDOW_DAYS = 365
MAX_ITEMS = 30
MAX_CHARS = 20_000
NEAR_DUPLICATE = 0.72
DUPLICATE = 0.85

SITE_ID = re.compile(r"^SYN-SITE-\d{4}$")
ITEM_ID = re.compile(r"^SYN-SP-\d{4}$")
USER_ID = re.compile(r"^SYN-USER-\d{3}$")
ACTOR_ID = re.compile(r"^SYN-SO-\d{3}$")
PRINCIPAL = re.compile(r"^SYN-PRIN-[A-Z0-9-]{1,24}$")
PAGE_OWNER = re.compile(r"^SYN-OWNER-[A-Z0-9-]{1,24}$")
PACK_ID = re.compile(r"^SYN-PACK-\d{4}$")
QUERY_ID = re.compile(r"^SYN-QRY-\d{4}$")
SHORT_MARKING = re.compile(r"^[A-Za-z][A-Za-z0-9-]{0,40}$")
BANNER = re.compile(r"[A-Z][A-Z0-9 /-]{2,}")
NINO_SHAPE = re.compile(
    r"\b[A-Za-z]{2}[ \t]{0,2}\d{2}[ \t]{0,2}\d{2}[ \t]{0,2}\d{2}[ \t]{0,2}[A-Da-d]\b"
)

ORDINARY_SENSITIVITY = frozenset({"", "official", "none", "unmarked"})
CONTENT_TYPES = frozenset({"Policy", "Guidance", "News", "How-to", "Form", "Record"})
AUDIENCES = frozenset({"staff", "managers", "public", "residents"})
MARKINGS = frozenset({"OFFICIAL", "OFFICIAL-SENSITIVE", "SECRET", "TOP SECRET"})
SENSITIVE_CLASSIFICATION = frozenset(
    {"personal_data", "official_sensitive", "existing_higher_marking", "legal_hold"}
)
JURISDICTIONS = frozenset({"england", "wales", "scotland", "northern_ireland", "unspecified"})
CODE_APPLIES = frozenset({"england", "wales"})

TYPE_PHRASES = {
    "Policy": ("this policy", "policy statement"),
    "Guidance": ("this guidance", "staff guidance"),
    "News": ("news item", "press release"),
    "How-to": ("how to", "follow these steps"),
    "Form": ("application form", "complete this form"),
    "Record": ("decision record", "minutes of the"),
}

STOPWORDS = frozenset(
    "a an the of to for and or in on at by with from this that is are was were be staff should page".split()
)

PROHIBITED_KEYS = frozenset(
    {
        "human_approval",
        "executed",
        "actions_taken",
        "deleted",
        "unpublished",
        "moved",
        "permissions_changed",
        "sharepoint_called",
        "graph_called",
        "metadata_applied_in_tenant",
        "published_by_agent",
        "approved",
        "curation_stub",
    }
)

APPROVE = "approve_actions"
REJECT = "reject_actions"
DEFER = "defer"
DECISIONS = frozenset({APPROVE, REJECT, DEFER})
PROHIBITED_DECISIONS = frozenset(
    {
        "delete",
        "delete_page",
        "unpublish",
        "unpublish_page",
        "move",
        "move_page",
        "change_permissions",
        "publish",
        "grant_access",
    }
)


class CuratorForbidden(RuntimeError):
    """Raised when a caller asks the agent to change the site."""


def delete_page(*_args, **_kwargs) -> None:
    raise CuratorForbidden("the agent does not delete a page")


def unpublish_page(*_args, **_kwargs) -> None:
    raise CuratorForbidden("the agent does not unpublish a page")


def move_page(*_args, **_kwargs) -> None:
    raise CuratorForbidden("the agent does not move a page")


def change_permissions(*_args, **_kwargs) -> None:
    raise CuratorForbidden("the agent does not change permissions")


def _parse_as_of(value: date | datetime | str) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if not isinstance(value, str):
        raise TypeError("as_of must be a date")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("as_of must be YYYY-MM-DD") from exc


def _parse_day(value: object) -> date | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _strip_prohibited(mapping: dict) -> list[str]:
    removed = []
    for key in list(mapping):
        if key in PROHIBITED_KEYS:
            removed.append(key)
            del mapping[key]
    return removed


def _flags() -> dict:
    return {
        "deleted": False,
        "unpublished": False,
        "moved": False,
        "permissions_changed": False,
        "metadata_applied_in_tenant": False,
        "published_by_agent": False,
        "sharepoint_called": False,
        "graph_called": False,
        "stub_recorded": False,
        "approval_recorded": False,
    }


def _human_route() -> dict:
    return {
        "offered": True,
        "channel": "Site owner, outside this agent",
        "agent_deletes": False,
        "agent_unpublishes": False,
        "agent_moves": False,
        "agent_changes_permissions": False,
        "agent_curates_sensitive": False,
    }


def _force(result: dict) -> None:
    result["executed"] = False
    result["model_called"] = False
    result["network_called"] = False
    result["text_recorded"] = False
    flags = result.setdefault("flags", _flags())
    flags["deleted"] = False
    flags["unpublished"] = False
    flags["moved"] = False
    flags["permissions_changed"] = False
    flags["metadata_applied_in_tenant"] = False
    flags["published_by_agent"] = False
    flags["sharepoint_called"] = False
    flags["graph_called"] = False
    result["sharepoint_called"] = False
    result["graph_called"] = False
    regulatory = result.setdefault("regulatory", {})
    regulatory["accuracy_met"] = False
    regulatory["storage_limitation_met"] = False
    regulatory["code_complied"] = False
    regulatory["article_84b_opened"] = False
    route = result.setdefault("human_route", _human_route())
    route["offered"] = True
    route["agent_deletes"] = False
    route["agent_unpublishes"] = False
    route["agent_curates_sensitive"] = False


def _refusal(reason: str, as_of: str) -> dict:
    result = {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment_id": EXPERIMENT_ID,
        "autonomy": AUTONOMY,
        "organisation": ORGANISATION,
        "organisation_is_fictional": True,
        "site_id": "unspecified",
        "as_of": as_of,
        "outcome": "refused",
        "refusal_reason": reason,
        "human_approval": None,
        "actions_taken": [],
        "visible_count": 0,
        "withheld_count": 0,
        "withheld_ids_recorded": False,
        "proposals": [],
        "items": [],
        "flags": _flags(),
        "human_route": _human_route(),
        "regulatory": {
            "accuracy_met": False,
            "storage_limitation_met": False,
            "code_complied": False,
            "code_applied": False,
            "disposition_allowed": False,
            "article_84b_opened": False,
        },
        "reuse": {
            "experiment_12": {"called": False},
            "experiment_08": {"called": False, "values_recorded": False},
            "experiment_49": {"called": False},
            "experiment_44": {"called": False, "reason": "not_called"},
        },
    }
    _force(result)
    return result


def _short(value: object, limit: int) -> str | None:
    if not isinstance(value, str):
        return None
    cleaned = " ".join(value.split())
    if not cleaned or len(cleaned) > limit or NINO_SHAPE.search(cleaned):
        return None
    return cleaned


def _tokens(text: str) -> set[str]:
    words = re.findall(r"[a-z0-9]+", text.lower())
    return {word for word in words if len(word) > 2 and word not in STOPWORDS}


def _jaccard(left: set[str], right: set[str]) -> float:
    if not left and not right:
        return 0.0
    union = left | right
    if not union:
        return 0.0
    return len(left & right) / len(union)


def _phrase_counts(matching: str) -> dict[str, int]:
    counts = {}
    hay = matching.lower()
    for content_type, phrases in TYPE_PHRASES.items():
        counts[content_type] = sum(hay.count(phrase) for phrase in phrases)
    return counts


def _banner_not_ordinary(matching: str) -> bool:
    for line in matching.splitlines():
        token = line.strip()
        if not token or len(token) > 40:
            continue
        if token.upper() in {"OFFICIAL", "NONE", "UNMARKED"}:
            continue
        if BANNER.fullmatch(token):
            return True
    return False


def _sensitivity_value(raw: object) -> tuple[str | None, bool]:
    """Return a copyable marking, and whether the value is outside the ordinary set.

    Anything other than empty, OFFICIAL, none, or unmarked is not ordinary.
    A value that is not a short label is not copied.
    """

    if raw is None:
        return None, False
    if not isinstance(raw, str):
        return None, True
    cleaned = raw.strip()
    if cleaned.lower() in ORDINARY_SENSITIVITY:
        return "OFFICIAL" if cleaned.lower() == "official" else None, False
    if SHORT_MARKING.fullmatch(cleaned):
        return cleaned, True
    return None, True


def _call_intake(item_id: str, text: str, as_of: date, document_date: str | None) -> dict:
    module = intake_module()
    batch = {
        "synthetic": True,
        "batch_id": item_id,
        "files": [
            {
                "file_id": item_id,
                "filename": f"{item_id}.txt",
                "media_type": "text/plain",
                "content": text,
                "document_date": document_date,
            }
        ],
    }
    draft = module.intake(batch, as_of=as_of)
    row = draft["files"][0]
    return {
        "called": True,
        "experiment_id": "exp-12-document-intake",
        "catalogue_id": "O001",
        "read_status": row["read_status"],
        "intake_class": row["suggested_class"],
        "files_confirmed": False,
        "content_recorded": False,
        "char_count": row["char_count"],
    }


def _call_gateway(text: str) -> dict:
    module = gateway_module()
    proposal = module.propose(
        text,
        caller=EXPERIMENT_ID,
        apply_model_suggestions=False,
        reversible=False,
    )
    if proposal["anonymisation"]["output_is_anonymised"] or proposal["release"]["agent_may_release"]:
        raise CuratorForbidden("Experiment 08 returned an unexpected release flag")
    types: list[str] = []
    count = 0
    for finding in proposal["audit_log"]["findings"]:
        if finding.get("applied") and finding.get("method") == "deterministic":
            count += 1
            entity = finding.get("entity_type")
            if isinstance(entity, str) and entity not in types:
                types.append(entity)
    return {
        "called": True,
        "experiment_id": "exp-08-uk-pii-redaction-gateway",
        "catalogue_id": "O005",
        "finding_count": count,
        "entity_types": types,
        "output_is_anonymised": False,
        "agent_may_release": False,
        "values_recorded": False,
    }


def _call_classify(item_id: str, text: str, as_of: date, document_date: str | None, marking: str | None, jurisdiction: str) -> dict:
    module = classify_module()
    document = {
        "synthetic": True,
        "document_id": item_id,
        "filename": f"{item_id}.txt",
        "text": text,
        "jurisdiction": jurisdiction if jurisdiction in {"england", "wales", "scotland", "northern_ireland"} else "unspecified",
        "document_date": document_date,
    }
    # OFFICIAL is the ordinary tier. Passing it makes Experiment 49 treat a
    # missing file-plan match as an existing higher marking. Only a higher
    # marking is passed through.
    if marking in {"OFFICIAL-SENSITIVE", "SECRET", "TOP SECRET"}:
        document["existing_marking"] = marking
    draft = module.classify_record(document, as_of)
    reasons = [
        reason
        for reason in (draft.get("human_queue") or {}).get("reasons") or []
        if reason in SENSITIVE_CLASSIFICATION
    ]
    personal = bool((draft.get("proposals") or {}).get("personal_data", {}).get("indicated"))
    suggestion = (draft.get("proposals") or {}).get("gsc", {}).get("suggestion")
    if suggestion not in MARKINGS:
        suggestion = None
    hold = bool((draft.get("legal_hold") or {}).get("indicated"))
    return {
        "called": True,
        "experiment_id": "exp-49-records-classification",
        "catalogue_id": "M009",
        "outcome": draft.get("outcome"),
        "sensitive_reasons": reasons,
        "personal_data_indicated": personal,
        "marking_suggestion": suggestion,
        "legal_hold": hold,
        "human_approval": None,
        "text_recorded": False,
    }


def _neighbours_empty(reason: str) -> dict:
    return {
        "intake": {"called": False, "reason": reason, "content_recorded": False, "files_confirmed": False},
        "gateway": {
            "called": False,
            "reason": reason,
            "finding_count": 0,
            "entity_types": [],
            "values_recorded": False,
        },
        "classification": {"called": False, "reason": reason, "sensitive_reasons": []},
    }


def _queue_reasons(row: dict, gateway: dict, classification: dict) -> list[str]:
    reasons: list[str] = []
    if row["too_large"]:
        reasons.append("not_scanned")
    if row["sensitivity_not_ordinary"]:
        reasons.append("sensitivity_not_ordinary")
    if row["personal_data_flag"] not in (None, False):
        reasons.append("personal_data_flag")
    if row["banner"]:
        reasons.append("banner_not_ordinary")
    if gateway.get("finding_count"):
        reasons.append("identifier")
    for reason in classification.get("sensitive_reasons") or []:
        if reason not in reasons:
            reasons.append(reason)
    if classification.get("personal_data_indicated") and "personal_data" not in reasons:
        reasons.append("personal_data")
    if classification.get("legal_hold") and "legal_hold" not in reasons:
        reasons.append("legal_hold")
    suggestion = classification.get("marking_suggestion")
    if suggestion in {"OFFICIAL-SENSITIVE", "SECRET", "TOP SECRET"} and "official_sensitive" not in reasons and "existing_higher_marking" not in reasons:
        reasons.append("official_sensitive")
    return reasons


def _proposal(proposal_type: str, item_ids: list[str], confidence: str, evidence: list[dict], **extra) -> dict:
    publishing = proposal_type in {"archive", "merge", "knowledge_gap"}
    metadata = proposal_type in {"missing_metadata", "inconsistent_metadata"}
    return {
        "type": proposal_type,
        "item_ids": item_ids,
        "confidence": confidence,
        "evidence": evidence,
        "requires_approval": proposal_type != "human_queue",
        "metadata_action": metadata,
        "publishing_action": publishing,
        "curated": False,
        **extra,
    }


def _metadata_proposals(row: dict, counts: dict[str, int], day: date) -> list[dict]:
    found = []
    item_id = row["item_id"]
    for field in ("content_type", "owner", "review_date", "audience"):
        if row[field] in (None, ""):
            found.append(
                _proposal(
                    "missing_metadata",
                    [item_id],
                    "high",
                    [{"kind": "field_absent", "field": field}],
                    field=field,
                )
            )
    declared = row["content_type"] if row["content_type"] in CONTENT_TYPES else None
    leaders = [name for name, count in counts.items() if count >= 2]
    if declared and len(leaders) == 1 and leaders[0] != declared:
        found.append(
            _proposal(
                "inconsistent_metadata",
                [item_id],
                "high",
                [{"kind": "phrase_count", "content_type": leaders[0], "count": counts[leaders[0]], "declared": declared}],
                field="content_type",
            )
        )
    if isinstance(row["owner"], str) and row["owner"] and not PAGE_OWNER.fullmatch(row["owner"]):
        found.append(
            _proposal(
                "inconsistent_metadata",
                [item_id],
                "high",
                [{"kind": "owner_pattern"}],
                field="owner",
            )
        )
    if isinstance(row["audience"], str) and row["audience"] and row["audience"] not in AUDIENCES:
        found.append(
            _proposal(
                "inconsistent_metadata",
                [item_id],
                "high",
                [{"kind": "audience_not_in_starter_set"}],
                field="audience",
            )
        )
    review = row["review_day"]
    if review is not None and review < day:
        overdue = (day - review).days
        found.append(
            _proposal(
                "review_overdue",
                [item_id],
                "high",
                [{"kind": "days_overdue", "days": overdue, "window_days": REVIEW_WINDOW_DAYS, "statutory_period": False}],
                field="review_date",
            )
        )
        if overdue > REVIEW_WINDOW_DAYS and row["disposition_candidate"]:
            found.append(
                _proposal(
                    "archive",
                    [item_id],
                    "medium",
                    [{"kind": "review_window_exceeded", "days": overdue, "statutory_period": False}],
                    field="review_date",
                )
            )
    if review is not None and review > day + timedelta(days=365 * 5):
        found.append(
            _proposal(
                "inconsistent_metadata",
                [item_id],
                "medium",
                [{"kind": "review_date_far_future"}],
                field="review_date",
            )
        )
    if row["text_empty"]:
        found.append(
            _proposal(
                "empty_page",
                [item_id],
                "high",
                [{"kind": "text_empty"}],
            )
        )
    return found


def _pair_proposals(rows: list[dict]) -> list[dict]:
    found = []
    usable = [row for row in rows if not row["queued"] and row["tokens"]]
    for index, left in enumerate(usable):
        for right in usable[index + 1 :]:
            score = _jaccard(left["tokens"], right["tokens"])
            titles_equal = left["title_key"] and left["title_key"] == right["title_key"]
            if score < NEAR_DUPLICATE and not (titles_equal and score >= 0.55):
                continue
            kind = "duplicate" if score >= DUPLICATE or (titles_equal and score >= 0.55) else "near_duplicate"
            confidence = "high" if kind == "duplicate" else "medium"
            ids = sorted([left["item_id"], right["item_id"]])
            evidence = [{
                "kind": "token_overlap",
                "jaccard": round(score, 2),
                "shared_tokens": len(left["tokens"] & right["tokens"]),
                "text_recorded": False,
            }]
            found.append(_proposal(kind, ids, confidence, evidence))
            if left["disposition_ok"] and right["disposition_ok"]:
                found.append(
                    _proposal(
                        "merge",
                        ids,
                        confidence,
                        evidence,
                    )
                )
    return found


def _link_proposals(rows: list[dict]) -> list[dict]:
    by_url = {row["url"]: row["item_id"] for row in rows if row["url"]}
    inbound = {row["item_id"]: 0 for row in rows}
    found = []
    for row in rows:
        for href in row["links"]:
            target = by_url.get(href)
            if target and target != row["item_id"]:
                inbound[target] = inbound.get(target, 0) + 1
            elif not row["queued"] and href != row["url"]:
                found.append(
                    _proposal(
                        "broken_link",
                        [row["item_id"]],
                        "high",
                        [{"kind": "unresolved_in_visible_site", "href": href, "target_disclosed": False}],
                        href=href,
                    )
                )
    for row in rows:
        if row["queued"] or row["is_home"] or not row["published"]:
            continue
        if inbound.get(row["item_id"], 0) == 0:
            found.append(
                _proposal(
                    "orphaned",
                    [row["item_id"]],
                    "medium",
                    [{"kind": "no_inbound_link_in_export", "inbound": 0, "navigation_included": False}],
                )
            )
    return found


def _number(proposals: list[dict]) -> list[dict]:
    ordered = sorted(
        proposals,
        key=lambda proposal: (
            proposal["type"],
            tuple(proposal["item_ids"]),
            proposal.get("field") or "",
            proposal.get("href") or "",
            proposal.get("topic") or "",
        ),
    )
    numbered = []
    for index, proposal in enumerate(ordered, start=1):
        item = dict(proposal)
        item["proposal_id"] = f"P-{index:03d}"
        numbered.append(item)
    return numbered


def _articles_for(rows: list[dict]) -> list[dict]:
    articles = []
    for row in rows:
        if row["queued"] or row["text_empty"] or row["too_large"]:
            continue
        review = row["review_day"].isoformat() if row["review_day"] else "2020-01-01"
        modified = row["modified_day"].isoformat() if row["modified_day"] else "2020-01-01"
        title = row["title"] or "Untitled page"
        articles.append(
            {
                "id": row["item_id"],
                "title": title,
                "sector": "public_service",
                "status": "current" if row["published"] else "draft",
                "effective_from": modified,
                "review_due": review,
                "last_reviewed": modified,
                "topic": "intranet-" + row["item_id"].lower(),
                "claim": "page",
                "polarity": "affirm",
                "keywords": [[title.lower()]],
                "exclude": [],
                "body": row["matching"] or title,
            }
        )
    return articles


def _knowledge(snapshot: dict, rows: list[dict], as_of: str) -> dict:
    queries = snapshot.get("queries") or []
    if not queries:
        return {"called": False, "reason": "no_queries", "content_gaps": [], "published": False}
    pack_id = snapshot.get("knowledge_pack_id")
    if not isinstance(pack_id, str) or not PACK_ID.fullmatch(pack_id):
        return {"called": False, "reason": "pack_id", "content_gaps": [], "published": False}
    clean_queries = []
    for query in queries:
        if not isinstance(query, dict):
            return {"called": False, "reason": "query_id", "content_gaps": [], "published": False}
        query_id = query.get("id")
        text = query.get("text")
        if not isinstance(query_id, str) or not QUERY_ID.fullmatch(query_id):
            return {"called": False, "reason": "query_id", "content_gaps": [], "published": False}
        if not isinstance(text, str) or len(text) > 4000:
            return {"called": False, "reason": "query_text", "content_gaps": [], "published": False}
        clean_queries.append({"id": query_id, "text": text})
    pack = {
        "synthetic": True,
        "pack_id": pack_id,
        "sector": "public_service",
        "queries": clean_queries,
    }
    report = gaps_module().detect_gaps(pack, as_of, library=_articles_for(rows))
    if report.get("published") or report.get("articles_edited"):
        raise CuratorForbidden("Experiment 44 returned a publish flag")
    if report.get("outcome") == "refused":
        return {
            "called": True,
            "experiment_id": "exp-44-knowledge-gap-detector",
            "catalogue_id": "C005",
            "reason": report.get("refusal_reason"),
            "content_gaps": [],
            "published": False,
            "text_recorded": False,
        }
    if report.get("outcome") == "stale_sources":
        return {
            "called": True,
            "experiment_id": "exp-44-knowledge-gap-detector",
            "catalogue_id": "C005",
            "reason": "stale_sources",
            "content_gaps": [],
            "published": False,
            "text_recorded": False,
        }
    gaps = []
    for gap in report.get("gaps") or []:
        gaps.append(
            {
                "gap_id": gap.get("gap_id"),
                "topic": gap.get("topic"),
                "published": False,
                "confirmed": False,
            }
        )
    other = 0
    for finding in report.get("findings") or []:
        if finding.get("kind") != "content_gap":
            other += 1
    return {
        "called": True,
        "experiment_id": "exp-44-knowledge-gap-detector",
        "catalogue_id": "C005",
        "reason": None,
        "content_gaps": gaps,
        "other_finding_count": other,
        "outlines_copied": False,
        "published": False,
        "text_recorded": False,
    }


def _read_item(raw: dict, principals: set[str]) -> tuple[str, dict | None]:
    """Return ``withheld``, ``unreadable``, or ``visible`` plus a row.

    A withheld row is None. The title and the text are not copied out.
    """

    item_id = raw.get("item_id")
    if not isinstance(item_id, str) or not ITEM_ID.fullmatch(item_id):
        return "unreadable", None
    readers = raw.get("readers")
    if not isinstance(readers, list) or not readers:
        return "withheld", None
    allowed = {reader for reader in readers if isinstance(reader, str) and PRINCIPAL.fullmatch(reader)}
    if not allowed.intersection(principals):
        return "withheld", None
    text = raw.get("text") if isinstance(raw.get("text"), str) else ""
    too_large = len(text) > MAX_CHARS
    working = dict(raw)
    _strip_prohibited(working)
    sensitivity, not_ordinary = _sensitivity_value(working.get("sensitivity"))
    content_type = working.get("content_type")
    if content_type is not None and not isinstance(content_type, str):
        content_type = None
    if isinstance(content_type, str) and not content_type.strip():
        content_type = None
    owner = working.get("owner") if isinstance(working.get("owner"), str) and working.get("owner").strip() else None
    audience = working.get("audience") if isinstance(working.get("audience"), str) and working.get("audience").strip() else None
    review_raw = working.get("review_date")
    modified_raw = working.get("last_modified")
    links = []
    for href in working.get("links") or []:
        short = _short(href, 180)
        if short and short.startswith("/"):
            links.append(short)
    matching = ""
    injection = {"detected": False, "followed": False, "signals": []}
    if text and not too_large:
        matching, injection = prepare_text(text)
    title = _short(working.get("title"), 120)
    return "visible", {
        "item_id": item_id,
        "kind": working.get("kind") if working.get("kind") in {"page", "document"} else "page",
        "title": title,
        "title_key": title.lower() if title else "",
        "url": _short(working.get("url"), 180) if isinstance(working.get("url"), str) and working.get("url", "").startswith("/") else None,
        "content_type": content_type,
        "owner": owner,
        "audience": audience,
        "review_date": review_raw if isinstance(review_raw, str) else None,
        "review_day": _parse_day(review_raw),
        "modified_day": _parse_day(modified_raw),
        "published": working.get("published") is True,
        "is_home": working.get("is_home") is True,
        "sensitivity": sensitivity,
        "sensitivity_not_ordinary": not_ordinary,
        "personal_data_flag": working.get("personal_data_flag"),
        "links": links,
        "text_empty": text == "",
        "too_large": too_large,
        "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "matching": matching if not too_large else "",
        "tokens": _tokens(matching) if matching else set(),
        "injection": injection,
        "banner": _banner_not_ordinary(matching) if matching else False,
    }


def curate_site(snapshot: dict, as_of: date | datetime | str) -> dict:
    """Return a draft. ``human_approval`` stays null."""

    if not isinstance(snapshot, dict):
        raise TypeError("snapshot must be an object")
    day = _parse_as_of(as_of)
    as_of_text = day.isoformat()
    if snapshot.get("synthetic") is not True:
        return _refusal("not_synthetic", as_of_text)

    working = dict(snapshot)
    stripped = _strip_prohibited(working)
    age_days = (day - SOURCES_PINNED_ON).days
    rules_current = 0 <= age_days <= STALE_AFTER_DAYS
    site_id = working.get("site_id") if isinstance(working.get("site_id"), str) else ""
    if not SITE_ID.fullmatch(site_id):
        site_id = "unspecified"
    jurisdiction = working.get("jurisdiction") if working.get("jurisdiction") in JURISDICTIONS else "england"
    user = working.get("requesting_user") if isinstance(working.get("requesting_user"), dict) else {}
    user_id = user.get("id") if isinstance(user.get("id"), str) and USER_ID.fullmatch(user.get("id")) else "unspecified"
    principals = {
        principal
        for principal in (user.get("principals") or [])
        if isinstance(principal, str) and PRINCIPAL.fullmatch(principal)
    }
    items_in = working.get("items")
    if not isinstance(items_in, list):
        return _refusal("not_a_snapshot", as_of_text)
    if len(items_in) > MAX_ITEMS:
        refused = _refusal("too_many_items", as_of_text)
        refused["site_id"] = site_id
        return refused

    if not principals:
        withheld = sum(1 for item in items_in if isinstance(item, dict))
        refused = _refusal("no_principals", as_of_text)
        refused["site_id"] = site_id
        refused["withheld_count"] = withheld
        refused["withheld_ids_recorded"] = False
        return refused

    visible = []
    withheld_count = 0
    unreadable_count = 0
    try:
        for raw in items_in:
            if not isinstance(raw, dict):
                unreadable_count += 1
                continue
            status, row = _read_item(raw, principals)
            if status == "withheld":
                withheld_count += 1
                continue
            if status == "unreadable" or row is None:
                unreadable_count += 1
                continue
            text = raw.get("text") if isinstance(raw.get("text"), str) else ""
            document_date = row["modified_day"].isoformat() if row["modified_day"] and row["modified_day"] <= day else None
            neighbours = _neighbours_empty("not_called")
            if text and not row["too_large"]:
                neighbours["intake"] = _call_intake(row["item_id"], text, day, document_date)
                neighbours["gateway"] = _call_gateway(text)
                neighbours["classification"] = _call_classify(
                    row["item_id"],
                    row["matching"],
                    day,
                    document_date,
                    row["sensitivity"] if row["sensitivity"] in MARKINGS else None,
                    jurisdiction,
                )
            row["neighbours"] = neighbours
            row["queue_reasons"] = _queue_reasons(row, neighbours["gateway"], neighbours["classification"])
            row["queued"] = bool(row["queue_reasons"])
            visible.append(row)
    except NeighbourMissing as exc:
        raise CuratorForbidden(
            "A required neighbouring experiment is not beside this folder. "
            "This assistant does not invent a substitute."
        ) from exc

    disposition_allowed = jurisdiction in CODE_APPLIES and rules_current
    for row in visible:
        counts = _phrase_counts(row["matching"])
        row["detected_news"] = counts.get("News", 0) >= 1
        row["disposition_candidate"] = disposition_allowed and (
            row["content_type"] == "News" or row["detected_news"]
        )
        row["disposition_ok"] = disposition_allowed

    proposals: list[dict] = []
    signals: list[str] = []
    for row in visible:
        for signal in row["injection"]["signals"]:
            if signal["signal"] not in signals:
                signals.append(signal["signal"])
        if stripped:
            pass
        if row["queued"]:
            evidence = [{"kind": "human_queue", "reasons": list(row["queue_reasons"])}]
            if row["sensitivity_not_ordinary"] and row["sensitivity"]:
                evidence.append({"kind": "sensitivity_value", "value": row["sensitivity"]})
            gateway = row["neighbours"]["gateway"]
            if gateway.get("entity_types"):
                evidence.append({"kind": "identifier_types", "entity_types": list(gateway["entity_types"]), "values_recorded": False})
            proposals.append(
                _proposal("human_queue", [row["item_id"]], "high", evidence)
            )
            continue
        proposals.extend(_metadata_proposals(row, _phrase_counts(row["matching"]), day))
    proposals.extend(_pair_proposals(visible))
    proposals.extend(_link_proposals(visible))

    knowledge = _knowledge(working, visible, as_of_text)
    for gap in knowledge.get("content_gaps") or []:
        proposals.append(
            _proposal(
                "knowledge_gap",
                [],
                "medium",
                [{"kind": "experiment_44_content_gap", "gap_id": gap["gap_id"], "topic": gap["topic"], "published": False}],
                topic=gap["topic"],
            )
        )

    # Archive also when the page is orphaned in this export, not only when it is news.
    # The news rule is applied above. Orphan-and-overdue is applied after links exist.
    orphan_ids = {
        proposal["item_ids"][0]
        for proposal in proposals
        if proposal["type"] == "orphaned"
    }
    archive_ids = {
        tuple(proposal["item_ids"])
        for proposal in proposals
        if proposal["type"] == "archive"
    }
    if disposition_allowed:
        for row in visible:
            if row["queued"] or row["review_day"] is None:
                continue
            overdue = (day - row["review_day"]).days
            if overdue > REVIEW_WINDOW_DAYS and row["item_id"] in orphan_ids:
                key = (row["item_id"],)
                if key not in archive_ids:
                    proposals.append(
                        _proposal(
                            "archive",
                            [row["item_id"]],
                            "medium",
                            [{"kind": "overdue_and_orphaned_in_export", "days": overdue, "statutory_period": False}],
                            field="review_date",
                        )
                    )

    numbered = _number(proposals)
    queued_any = any(row["queued"] for row in visible)
    if not rules_current:
        outcome = "stale_sources"
    elif jurisdiction == "scotland":
        outcome = "outside_code_scope"
    elif queued_any:
        outcome = "human_queue"
    else:
        outcome = "ready_for_approval"

    items_out = []
    for row in visible:
        items_out.append(
            {
                "item_id": row["item_id"],
                "kind": row["kind"],
                "title": row["title"],
                "url": row["url"],
                "queued": row["queued"],
                "queue_reasons": list(row["queue_reasons"]),
                "published": row["published"],
                "reuse": {
                    "intake": row["neighbours"]["intake"],
                    "gateway": row["neighbours"]["gateway"],
                    "classification": row["neighbours"]["classification"],
                },
            }
        )

    identifier_types: list[str] = []
    finding_count = 0
    for row in visible:
        gateway = row["neighbours"]["gateway"]
        finding_count += gateway.get("finding_count") or 0
        for entity in gateway.get("entity_types") or []:
            if entity not in identifier_types:
                identifier_types.append(entity)

    result = {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment_id": EXPERIMENT_ID,
        "autonomy": AUTONOMY,
        "organisation": ORGANISATION,
        "organisation_is_fictional": True,
        "site_id": site_id,
        "requesting_user_id": user_id,
        "jurisdiction": jurisdiction,
        "as_of": as_of_text,
        "outcome": outcome,
        "human_approval": None,
        "actions_taken": [],
        "executed": False,
        "model_called": False,
        "network_called": False,
        "sharepoint_called": False,
        "graph_called": False,
        "text_recorded": False,
        "visible_count": len(visible),
        "withheld_count": withheld_count,
        "unreadable_count": unreadable_count,
        "withheld_ids_recorded": False,
        "proposals": numbered,
        "items": items_out,
        "flags": _flags(),
        "human_route": _human_route(),
        "prompt_injection": {
            "detected": bool(signals) or bool(stripped),
            "followed": False,
            "signals": signals + (["prohibited_key"] if stripped else []),
        },
        "stale": {
            "rules_current": rules_current,
            "pinned_on": SOURCES_PINNED_ON.isoformat(),
            "age_days": age_days,
            "stale_after_days": STALE_AFTER_DAYS,
            "quotes_withheld": not rules_current,
        },
        "sources": source_rows(rules_current),
        "regulatory": {
            "accuracy_met": False,
            "storage_limitation_met": False,
            "code_applied": jurisdiction in CODE_APPLIES and rules_current,
            "code_complied": False,
            "disposition_allowed": disposition_allowed,
            "article_84b_opened": False,
            "lord_chancellor_named_in_opened_code": False,
            "review_window_days": REVIEW_WINDOW_DAYS,
            "review_window_is_statutory": False,
        },
        "reuse": {
            "experiment_12": {"called": any(row["neighbours"]["intake"].get("called") for row in visible), "content_recorded": False},
            "experiment_08": {
                "called": any(row["neighbours"]["gateway"].get("called") for row in visible),
                "finding_count": finding_count,
                "entity_types": identifier_types,
                "values_recorded": False,
                "output_is_anonymised": False,
            },
            "experiment_49": {"called": any(row["neighbours"]["classification"].get("called") for row in visible)},
            "experiment_44": knowledge,
        },
        "limitations": [
            "Content type, owner, review date, and audience are starter fields. They are not sitePage properties verified on 12 November 2026.",
            "The 365-day window is configuration. It is not a GOV.UK rule for an intranet.",
            "Orphan means no inbound link in this export. Navigation is not included.",
            "An unresolved link is unresolved in the visible set. A hidden target is not confirmed.",
            "No identifier from Experiment 08 is not a finding that the page has no personal data.",
            "Article 84B was not opened. accuracy_met and storage_limitation_met stay false.",
        ],
    }
    _force(result)
    return result


def _review_refusal(result: dict, reason: str) -> dict:
    result["approval_review"] = {"refused": True, "reason": reason, "executed": False}
    result["human_approval"] = None
    result["actions_taken"] = []
    _force(result)
    return result


def record_approval(draft: dict, review: dict) -> dict:
    """Record the site owner's decision. It does not change the site."""

    if not isinstance(draft, dict) or draft.get("label") != LABEL:
        raise ValueError("draft is not a curation draft")
    if not isinstance(review, dict):
        raise TypeError("review must be an object")
    result = deepcopy(draft)
    decision = review.get("decision")
    if decision in PROHIBITED_DECISIONS:
        return _review_refusal(result, "prohibited_decision")
    if decision not in DECISIONS:
        return _review_refusal(result, "decision")
    if review.get("actor_role") != "Site owner":
        return _review_refusal(result, "actor_role")
    actor_id = review.get("actor_id")
    if not isinstance(actor_id, str) or not ACTOR_ID.fullmatch(actor_id):
        return _review_refusal(result, "actor_id")
    if review.get("site_id") != result.get("site_id"):
        return _review_refusal(result, "site_id")
    proposal_ids = review.get("proposal_ids")
    if not isinstance(proposal_ids, list) or not proposal_ids:
        return _review_refusal(result, "proposal_ids")
    if any(not isinstance(proposal_id, str) for proposal_id in proposal_ids):
        return _review_refusal(result, "proposal_ids")
    known = {proposal["proposal_id"]: proposal for proposal in result.get("proposals") or []}
    if any(proposal_id not in known for proposal_id in proposal_ids):
        return _review_refusal(result, "unknown_proposal")
    named = [known[proposal_id] for proposal_id in proposal_ids]
    if decision == APPROVE:
        if any(proposal["type"] == "human_queue" for proposal in named):
            return _review_refusal(result, "queue_is_not_a_change")
        queued = any(proposal["type"] == "human_queue" for proposal in result.get("proposals") or [])
        if queued and review.get("queue_reviewed") is not True:
            return _review_refusal(result, "queue_not_reviewed")
        if not result.get("stale", {}).get("rules_current"):
            return _review_refusal(result, "stale_sources")
        if any(proposal["publishing_action"] for proposal in named) and not result.get("regulatory", {}).get("disposition_allowed"):
            return _review_refusal(result, "disposition_not_allowed")
        result["human_approval"] = {
            "decision": APPROVE,
            "actor_role": "Site owner",
            "actor_id": actor_id,
            "proposal_ids": list(proposal_ids),
            "approved": True,
            "executed": False,
            "queue_reviewed": review.get("queue_reviewed") is True,
        }
        result["flags"]["approval_recorded"] = True
    else:
        result["human_approval"] = {
            "decision": decision,
            "actor_role": "Site owner",
            "actor_id": actor_id,
            "proposal_ids": list(proposal_ids),
            "approved": False,
            "executed": False,
        }
    result["approval_review"] = {"refused": False, "reason": None, "executed": False}
    result["actions_taken"] = []
    _force(result)
    result["flags"]["approval_recorded"] = decision == APPROVE
    return result


def apply_approved_action(draft: dict) -> dict:
    """Stub a receipt. SharePoint and Microsoft Graph are not called."""

    if not isinstance(draft, dict) or draft.get("label") != LABEL:
        raise ValueError("draft is not a curation draft")
    result = deepcopy(draft)
    approval = result.get("human_approval") or {}
    if approval.get("approved") is not True or approval.get("decision") != APPROVE:
        result["curation_stub"] = {
            "stub": False,
            "reason": "not_approved",
            "sharepoint_called": False,
            "graph_called": False,
        }
        _force(result)
        return result
    if not result.get("stale", {}).get("rules_current"):
        result["curation_stub"] = {
            "stub": False,
            "reason": "stale_sources",
            "sharepoint_called": False,
            "graph_called": False,
        }
        _force(result)
        return result
    known = {proposal["proposal_id"]: proposal for proposal in result.get("proposals") or []}
    receipts = []
    for proposal_id in approval.get("proposal_ids") or []:
        proposal = known.get(proposal_id)
        if proposal is None or proposal["type"] == "human_queue":
            result["curation_stub"] = {
                "stub": False,
                "reason": "queue_or_unknown",
                "sharepoint_called": False,
                "graph_called": False,
            }
            _force(result)
            return result
        receipts.append(
            {
                "proposal_id": proposal_id,
                "type": proposal["type"],
                "recorded": True,
                "applied_in_tenant": False,
                "sharepoint_called": False,
                "graph_called": False,
                "deleted": False,
                "unpublished": False,
                "moved": False,
                "permissions_changed": False,
            }
        )
    result["curation_stub"] = {
        "stub": True,
        "reason": "stubbed_after_approval",
        "sharepoint_called": False,
        "graph_called": False,
        "receipts": receipts,
        "note": "Not sent to SharePoint or Microsoft Graph. The page was not deleted, unpublished, moved, or re-permissioned.",
    }
    result["actions_taken"] = [
        {"proposal_id": receipt["proposal_id"], "applied_in_tenant": False}
        for receipt in receipts
    ]
    result["flags"]["stub_recorded"] = True
    _force(result)
    result["flags"]["stub_recorded"] = True
    result["flags"]["approval_recorded"] = True
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Propose SharePoint curation actions. Does not delete, unpublish, move, or change permissions."
    )
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--as-of", required=True)
    args = parser.parse_args(argv)
    try:
        snapshot = json.loads(args.input.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        print("The input could not be read.", file=sys.stderr)
        return 2
    if not isinstance(snapshot, dict):
        print("The input must be a JSON object.", file=sys.stderr)
        return 2
    try:
        draft = curate_site(snapshot, args.as_of)
    except (TypeError, ValueError, CuratorForbidden) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    json.dump(draft, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
