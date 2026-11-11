#!/usr/bin/env python3
"""Propose a records classification for one synthetic document.

The records manager confirms or changes every field. ``apply_confirmed_labels``
records a stub only after that confirmation. The stub does not call Microsoft
Purview. Nothing in this module deletes, disposes, moves, or downgrades a
record, and nothing reads the network.
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
    from guards import prepare_text
    from reuse import NeighbourMissing, gateway_module, intake_module, screening_module
    from scheme import (
        BY_ID,
        BY_RETENTION,
        CATEGORIES,
        COMMERCIAL_CUE,
        DISPOSAL_ACTIONS,
        HEALTH_CUES,
        LEGAL_HOLD_CUES,
        MARKING_RANK,
        MARKINGS,
        ORGANISATION,
        PERSONAL_CUES,
        SCHEME_ID,
        SCHEME_NOTE,
    )
    from sources import (
        QUOTE_ARTICLE_84B,
        QUOTE_STORAGE,
        QUOTE_THREE_TIERS,
        QUOTE_TWENTY_YEARS,
        SOURCES_PINNED_ON,
        STALE_AFTER_DAYS,
        source_rows,
    )
else:
    from .guards import prepare_text
    from .reuse import NeighbourMissing, gateway_module, intake_module, screening_module
    from .scheme import (
        BY_ID,
        BY_RETENTION,
        CATEGORIES,
        COMMERCIAL_CUE,
        DISPOSAL_ACTIONS,
        HEALTH_CUES,
        LEGAL_HOLD_CUES,
        MARKING_RANK,
        MARKINGS,
        ORGANISATION,
        PERSONAL_CUES,
        SCHEME_ID,
        SCHEME_NOTE,
    )
    from .sources import (
        QUOTE_ARTICLE_84B,
        QUOTE_STORAGE,
        QUOTE_THREE_TIERS,
        QUOTE_TWENTY_YEARS,
        SOURCES_PINNED_ON,
        STALE_AFTER_DAYS,
        source_rows,
    )

LABEL = "DRAFT RECORDS CLASSIFICATION FOR RECORDS MANAGER CONFIRMATION"
CATALOGUE_ID = "M009"
EXPERIMENT_ID = "exp-49-records-classification"
AUTONOMY = "A1"
MANAGER_ROLE = "Records manager"
MAX_CHARS = 20_000
ACTOR_ID = re.compile(r"^SYN-[A-Z0-9-]{1,24}$")
DOCUMENT_ID = re.compile(r"^SYN-[A-Z0-9-]{1,32}$")
FILE_ID = re.compile(r"^[A-Za-z0-9_-]{1,40}$")
CONFIRM = "confirm_classification"
CHANGE = "change_classification"
REJECT = "reject_proposal"
DECISIONS = frozenset({CONFIRM, CHANGE, REJECT})
PROHIBITED_DECISIONS = frozenset(
    {
        "dispose",
        "delete",
        "move",
        "downgrade",
        "destroy",
        "apply_labels",
        "approve",
        "reject",
    }
)
PROHIBITED_KEYS = frozenset(
    {
        "deleted",
        "disposed",
        "moved",
        "downgraded",
        "labels_applied",
        "labels_applied_in_tenant",
        "human_approval",
        "classification_confirmed",
        "files_confirmed",
        "approve",
        "reject",
        "purge",
    }
)
JURISDICTIONS = frozenset({"england", "wales", "scotland", "northern_ireland", "unspecified"})

LIMITATIONS = (
    "This draft does not confirm a classification. The records manager confirms or changes every field.",
    "A keyword match is not a decision that the record belongs in that category.",
    "Configured retention periods are not statutory periods and are not a National Archives schedule.",
    "The agent does not delete, dispose of, move, or downgrade a record, including after confirmation.",
    "The label action is a stub. It does not call Microsoft Purview and it does not apply a tenant label.",
    "OFFICIAL-SENSITIVE is the policy's written form of the -SENSITIVE marking on OFFICIAL. It is not a fourth tier. Suggesting it is not a decision that the marking is required.",
    "Absence of a personal-data indicator is not a finding that the text contains no personal data. Names and email addresses are not detected.",
    "Experiment 08 does not release text. This output is not anonymised.",
    "Experiment 19 does not decide that a DPIA is required. dpia_required stays null.",
    "The Public Records Act First Schedule was not opened. This starter does not decide that a record is a public record.",
    "Article 84B, Article 6, Article 9, and Freedom of Information Act 2000 section 48 were not opened.",
    "The section 46 code does not apply to bodies subject to the Freedom of Information (Scotland) Act 2002. This starter does not state Scots law.",
    "A file over 20,000 characters is not scanned. An instruction in it is not detected.",
    "The 180-day window is a stale flag for this starter. It is not a statutory review period.",
    "No model was called.",
)


class RecordsForbidden(RuntimeError):
    """The assistant has no delete, dispose, move, or downgrade path."""


class NotSynthetic(ValueError):
    """The document was not marked synthetic. The message does not include the body."""


def delete_record(*_args, **_kwargs) -> None:
    raise RecordsForbidden("the agent does not delete a record")


def dispose_record(*_args, **_kwargs) -> None:
    raise RecordsForbidden("the agent does not dispose of a record")


def move_record(*_args, **_kwargs) -> None:
    raise RecordsForbidden("the agent does not move a record")


def downgrade_record(*_args, **_kwargs) -> None:
    raise RecordsForbidden("the agent does not downgrade a record")


def _parse_as_of(value: date | datetime | str) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError as exc:
            raise ValueError("as_of must be a calendar date") from exc
    raise TypeError("as_of must be a date")


def _parse_day(value: object) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        try:
            return date.fromisoformat(value)
        except ValueError:
            return None
    return None


def _safe_line(value: object, pattern: re.Pattern[str], fallback: str) -> str:
    if isinstance(value, str) and pattern.fullmatch(value):
        return value
    return fallback


def _hits(text: str, phrases: tuple[str, ...]) -> list[str]:
    lower = text.lower()
    return [phrase for phrase in phrases if phrase in lower]


def _confidence(count: int, unique: bool) -> str:
    if unique and count >= 2:
        return "high"
    if unique and count == 1:
        return "medium"
    return "low"


def _strip_prohibited(mapping: dict) -> list[str]:
    found = []
    for key in list(mapping):
        if key in PROHIBITED_KEYS:
            found.append(key)
            del mapping[key]
    return found


def _refusal() -> dict:
    result = {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment_id": EXPERIMENT_ID,
        "autonomy": AUTONOMY,
        "outcome": "refused",
        "reason": "not_synthetic",
        "text_recorded": False,
        "human_approval": None,
        "actions_taken": [],
        "executed": False,
        "model_called": False,
        "network_called": False,
        "human_route": _human_route(),
        "flags": _flags(),
        "limitations": list(LIMITATIONS),
    }
    _force(result)
    return result


def _flags() -> dict:
    return {
        "deleted": False,
        "disposed": False,
        "moved": False,
        "downgraded": False,
        "labels_applied_in_tenant": False,
        "labels_stubbed": False,
        "classification_confirmed": False,
        "downgrade_proposed": False,
    }


def _human_route() -> dict:
    return {
        "offered": True,
        "agent_disposes": False,
        "agent_deletes": False,
        "publishes_a_telephone_number": False,
        "note": (
            "A records manager can classify the record in the organisation's own "
            "system. This starter does not publish a telephone number."
        ),
    }


def _force(result: dict) -> None:
    result["executed"] = False
    result["model_called"] = False
    result["network_called"] = False
    result["text_recorded"] = False
    result["actions_taken"] = []
    flags = result.setdefault("flags", _flags())
    flags["deleted"] = False
    flags["disposed"] = False
    flags["moved"] = False
    flags["downgraded"] = False
    flags["labels_applied_in_tenant"] = False
    flags["downgrade_proposed"] = False
    route = result.setdefault("human_route", _human_route())
    route["offered"] = True
    route["agent_disposes"] = False
    route["agent_deletes"] = False
    regulatory = result.get("regulatory")
    if isinstance(regulatory, dict):
        regulatory["public_record_decided"] = False
        regulatory["pra_transfer_due_decided"] = False
        regulatory["code_complied"] = False
        regulatory["storage_limitation_met"] = False
        regulatory["gsc_applied_by_agent"] = False
        regulatory["disposal_executed"] = False
    proposals = result.get("proposals")
    if isinstance(proposals, dict):
        gsc = proposals.get("gsc")
        if isinstance(gsc, dict):
            gsc["downgrade_proposed"] = False
            gsc["decided"] = False
        for key in ("file_plan", "retention", "disposal", "personal_data"):
            block = proposals.get(key)
            if isinstance(block, dict):
                block["decided"] = False
    screening = (result.get("reuse") or {}).get("screening") if isinstance(result.get("reuse"), dict) else None
    if isinstance(screening, dict):
        screening["dpia_required"] = None
        screening["dpia_required_decided_by_this_tool"] = False
    gateway = (result.get("reuse") or {}).get("gateway") if isinstance(result.get("reuse"), dict) else None
    if isinstance(gateway, dict):
        gateway["output_is_anonymised"] = False
        gateway["agent_may_release"] = False
        gateway["values_recorded"] = False
    injection = result.get("prompt_injection")
    if isinstance(injection, dict):
        injection["followed"] = False
        for signal in injection.get("signals", []):
            if isinstance(signal, dict):
                signal["followed"] = False
    purview = result.get("purview")
    if isinstance(purview, dict):
        purview["called"] = False
        purview["disposition_review_executed"] = False


def _rank(marking: str | None) -> int:
    if marking is None:
        return 0
    return MARKING_RANK.get(marking, 0)


def _match_categories(matching: str) -> list[dict]:
    rows = []
    for category in CATEGORIES:
        phrases = _hits(matching, category["phrases"])
        if phrases:
            rows.append({"category": category, "phrases": phrases, "count": len(phrases)})
    return rows


def _call_intake(document_id: str, filename: str, text: str, as_of: date, document_date: str | None) -> dict:
    module = intake_module()
    file_id = document_id if FILE_ID.fullmatch(document_id) else "record"
    batch = {
        "synthetic": True,
        "batch_id": document_id if len(document_id) <= 80 else "unspecified",
        "files": [
            {
                "file_id": file_id,
                "filename": filename,
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
        "catalogue_stale": bool(draft["catalogue_stale"]),
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
        "rules_pinned_on": proposal["audit_log"].get("rules_pinned_on"),
        "output_is_anonymised": False,
        "agent_may_release": False,
        "values_recorded": False,
    }


def _call_screen(answers: dict | None) -> dict:
    module = screening_module()
    block = answers if isinstance(answers, dict) else {}
    result = module.screen(block, article_35_1_view="unknown")
    if result.get("dpia_required") is not None or result.get("dpia_required_decided_by_this_tool") is not False:
        raise RecordsForbidden("Experiment 19 returned a DPIA determination. This assistant will not use it.")
    return {
        "called": True,
        "experiment_id": "exp-19-privacy-impact-assessment",
        "catalogue_id": "L006",
        "screen_result": result.get("screen_result"),
        "indicated_on_recorded_answers": bool(result.get("indicated_on_recorded_answers")),
        "dpia_required": None,
        "dpia_required_decided_by_this_tool": False,
        "answers_supplied": bool(block),
        "note": (
            "Passed through Experiment 19. A screen result is the recorded "
            "answers, not a decision that a DPIA is required."
        ),
    }


def _empty_neighbours(reason: str) -> dict:
    return {
        "intake": {
            "called": False,
            "experiment_id": "exp-12-document-intake",
            "catalogue_id": "O001",
            "read_status": reason,
            "files_confirmed": False,
            "content_recorded": False,
        },
        "gateway": {
            "called": False,
            "experiment_id": "exp-08-uk-pii-redaction-gateway",
            "catalogue_id": "O005",
            "finding_count": 0,
            "entity_types": [],
            "output_is_anonymised": False,
            "agent_may_release": False,
            "values_recorded": False,
        },
        "screening": {
            "called": False,
            "experiment_id": "exp-19-privacy-impact-assessment",
            "catalogue_id": "L006",
            "screen_result": None,
            "dpia_required": None,
            "dpia_required_decided_by_this_tool": False,
        },
    }


def classify_record(document: dict, as_of: date | datetime | str) -> dict:
    """Return a draft classification. ``human_approval`` stays null."""

    if not isinstance(document, dict):
        raise TypeError("document must be an object")
    day = _parse_as_of(as_of)
    if document.get("synthetic") is not True:
        return _refusal()

    working = dict(document)
    stripped = _strip_prohibited(working)
    text = working.get("text", "")
    if not isinstance(text, str):
        raise ValueError("text must be a string")
    document_id = _safe_line(working.get("document_id"), DOCUMENT_ID, "unspecified")
    filename = working.get("filename", "record.txt")
    if not isinstance(filename, str) or not filename or len(filename) > 120 or "\n" in filename:
        filename = "record.txt"
    jurisdiction = working.get("jurisdiction", "unspecified")
    if jurisdiction not in JURISDICTIONS:
        jurisdiction = "unspecified"
    existing = working.get("existing_marking")
    if existing not in MARKINGS:
        existing = None
    raw_date = working.get("document_date")
    parsed_date = _parse_day(raw_date) if raw_date not in (None, "") else None
    screening_answers = working.get("screening_answers")
    answers_rejected = screening_answers is not None and not isinstance(screening_answers, dict)

    age_days = (day - SOURCES_PINNED_ON).days
    rules_current = 0 <= age_days <= STALE_AFTER_DAYS
    too_large = len(text) > MAX_CHARS
    empty = text == ""
    matching = ""
    injection = {"detected": False, "followed": False, "signals": [], "body_marking": None}
    if not too_large and not empty:
        matching, injection = prepare_text(text)

    gaps: list[str] = []
    if document_id == "unspecified":
        gaps.append("document_id_unusable")
    if raw_date in (None, ""):
        gaps.append("document_date_missing")
    elif parsed_date is None:
        gaps.append("document_date_unparseable")
    elif parsed_date > day:
        gaps.append("document_date_future")

    queue: list[str] = []
    if too_large:
        queue.append("too_large")
    if empty:
        queue.append("empty_text")
    if not rules_current:
        queue.append("stale_sources")
    if "document_date_future" in gaps or "document_date_unparseable" in gaps:
        queue.append("document_date_not_usable")
    if jurisdiction == "scotland":
        queue.append("outside_code_scope")
    elif jurisdiction == "northern_ireland":
        queue.append("northern_ireland_not_applied")
    if "Freedom of Information (Scotland) Act" in text and not too_large:
        queue.append("scotland_statute_mentioned")

    reuse = _empty_neighbours("not_called")
    if not too_large and not empty:
        try:
            reuse["intake"] = _call_intake(
                document_id,
                filename,
                text,
                day,
                parsed_date.isoformat() if parsed_date else None,
            )
            reuse["gateway"] = _call_gateway(text)
            reuse["screening"] = _call_screen(None if answers_rejected else screening_answers)
        except NeighbourMissing as exc:
            raise RecordsForbidden(
                "A required neighbouring experiment is not beside this folder. "
                "This assistant does not invent a substitute."
            ) from exc

    matched = _match_categories(matching) if matching else []
    leader_count = max((row["count"] for row in matched), default=0)
    leaders = [row for row in matched if row["count"] == leader_count and leader_count > 0]
    unique = len(leaders) == 1
    confidence = _confidence(leader_count, unique)
    category = leaders[0]["category"] if unique else None
    evidence = leaders[0]["phrases"] if unique else []
    candidates = [row["category"]["id"] for row in matched]

    hold_cues = _hits(matching, LEGAL_HOLD_CUES) if matching else []
    personal_cues = _hits(matching, PERSONAL_CUES) if matching else []
    health_cues = _hits(matching, HEALTH_CUES) if matching else []
    commercial = bool(matching) and COMMERCIAL_CUE in matching.lower()
    entity_types = list(reuse["gateway"].get("entity_types") or [])
    personal_indicated = bool(entity_types) or bool(personal_cues) or bool(health_cues)
    if personal_indicated:
        queue.append("personal_data")

    if hold_cues:
        disposal = "do_not_dispose_legal_hold"
        disposal_confidence = "high"
        disposal_evidence = hold_cues
        queue.append("legal_hold")
    elif category is None:
        disposal = "unspecified"
        disposal_confidence = "low"
        disposal_evidence = []
    else:
        disposal = category["disposal"]
        disposal_confidence = confidence
        disposal_evidence = list(evidence)

    body_marking = injection.get("body_marking")
    kept_existing = existing
    if body_marking and _rank(body_marking) > _rank(kept_existing):
        kept_existing = body_marking
    scheme_marking = None if category is None else category["default_marking"]
    if commercial and _rank("OFFICIAL-SENSITIVE") > _rank(scheme_marking):
        scheme_marking = "OFFICIAL-SENSITIVE"
    if personal_indicated and _rank("OFFICIAL-SENSITIVE") > _rank(scheme_marking):
        scheme_marking = "OFFICIAL-SENSITIVE"
    if kept_existing and _rank(kept_existing) > _rank(scheme_marking):
        suggestion = kept_existing
        marking_basis = "existing_marking"
        marking_confidence = "high"
        queue.append("existing_higher_marking")
    else:
        suggestion = scheme_marking
        if personal_indicated and category is not None and category["default_marking"] != "OFFICIAL-SENSITIVE":
            marking_basis = "starter_caution"
        elif commercial and (category is None or category["default_marking"] != "OFFICIAL-SENSITIVE"):
            marking_basis = "starter_caution"
        elif category is None:
            marking_basis = "no_match"
        else:
            marking_basis = "scheme_default"
        marking_confidence = "low" if suggestion is None else confidence

    if suggestion == "OFFICIAL-SENSITIVE":
        queue.append("official_sensitive")
    if suggestion in {"SECRET", "TOP SECRET"} and "existing_higher_marking" not in queue:
        queue.append("existing_higher_marking")
    if confidence == "low" or category is None:
        queue.append("low_confidence")
    if category is not None and category["sensitive"] and "official_sensitive" not in queue:
        queue.append("official_sensitive")

    if personal_cues or entity_types:
        personal_confidence = "high" if entity_types else "medium"
    elif health_cues:
        personal_confidence = "medium"
    else:
        personal_confidence = "medium"

    # Stable, de-duplicated queue, with sensitive reasons kept even when confidence is high.
    queue_reasons: list[str] = []
    for reason in queue:
        if reason not in queue_reasons:
            queue_reasons.append(reason)

    if not rules_current:
        outcome = "stale_sources"
    elif queue_reasons:
        outcome = "human_queue"
    else:
        outcome = "ready_for_confirmation"

    sensitive_scope = jurisdiction in {"scotland", "northern_ireland"}
    result = {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment_id": EXPERIMENT_ID,
        "autonomy": AUTONOMY,
        "organisation": ORGANISATION,
        "organisation_is_fictional": True,
        "document_id": document_id,
        "filename": filename,
        "jurisdiction": jurisdiction,
        "as_of": day.isoformat(),
        "outcome": outcome,
        "text_recorded": False,
        "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "human_approval": None,
        "actions_taken": [],
        "executed": False,
        "model_called": False,
        "network_called": False,
        "scheme": {
            "id": SCHEME_ID,
            "note": SCHEME_NOTE,
            "statutory_periods": False,
        },
        "proposals": {
            "file_plan": {
                "category_id": None if category is None else category["id"],
                "title": None if category is None else category["title"],
                "candidates": candidates,
                "evidence": evidence,
                "confidence": confidence,
                "decided": False,
            },
            "retention": {
                "entry_id": None if category is None else category["retention_entry"],
                "label": None if category is None else category["retention_label"],
                "statutory_period": False,
                "evidence": evidence,
                "confidence": "low" if category is None else confidence,
                "decided": False,
            },
            "disposal": {
                "action": disposal,
                "executed": False,
                "evidence": disposal_evidence,
                "confidence": disposal_confidence,
                "decided": False,
            },
            "gsc": {
                "suggestion": suggestion,
                "existing_marking": existing,
                "body_marking": body_marking,
                "basis": marking_basis,
                "downgrade_proposed": False,
                "sensitive_marking_is_a_fourth_tier": False,
                "evidence": evidence,
                "confidence": marking_confidence,
                "decided": False,
            },
            "personal_data": {
                "indicated": personal_indicated,
                "identifier_types": entity_types,
                "keyword_cues": personal_cues,
                "health_cues": health_cues,
                "special_category_possible": bool(health_cues),
                "special_category_decided": False,
                "absence_is_not_a_finding": not personal_indicated,
                "values_recorded": False,
                "evidence": personal_cues or entity_types,
                "confidence": personal_confidence,
                "decided": False,
            },
        },
        "human_queue": {"required": outcome != "ready_for_confirmation", "reasons": queue_reasons},
        "legal_hold": {"indicated": bool(hold_cues), "cues": hold_cues},
        "gaps": gaps,
        "flags": _flags(),
        "reuse": reuse,
        "prompt_injection": injection,
        "prohibited_payload_keys": stripped,
        "screening_answers_rejected": answers_rejected,
        "stale": {
            "rules_current": rules_current,
            "pinned_on": SOURCES_PINNED_ON.isoformat(),
            "age_days": age_days,
            "stale_after_days": STALE_AFTER_DAYS,
            "quotes_withheld": not rules_current,
        },
        "sources": source_rows(rules_current),
        "regulatory": {
            "public_record_decided": False,
            "pra_transfer_due_decided": False,
            "code_applied": jurisdiction not in {"scotland", "northern_ireland"} and rules_current,
            "code_complied": False,
            "storage_limitation_engaged_as_a_reading": personal_indicated and rules_current,
            "storage_limitation_met": False,
            "article_84b_opened": False,
            "gsc_applied_by_agent": False,
            "disposal_executed": False,
            "welsh_public_record_decided": False,
            "outside_code_scope": sensitive_scope,
        },
        "purview": {
            "called": False,
            "retention_label_suggested_name": None
            if category is None
            else f"synthetic:{category['retention_entry']}",
            "sensitivity_label_suggested_name": suggestion,
            "disposition_review_executed": False,
            "note": (
                "Microsoft Purview retention labels and sensitivity labels are the "
                "described Microsoft 365 route. This stub does not call Purview."
            ),
        },
        "human_route": _human_route(),
        "limitations": list(LIMITATIONS),
    }
    _force(result)
    return result


def _review_refusal(result: dict, reason: str) -> dict:
    result["review"] = {
        "decision": None,
        "accepted": False,
        "refused": True,
        "reason": reason,
        "executed": False,
    }
    result["human_approval"] = None
    result["flags"]["classification_confirmed"] = False
    result["flags"]["labels_stubbed"] = False
    _force(result)
    return result


def _confirmed_fields(review: dict) -> dict | None:
    required = (
        "file_plan_category",
        "retention_entry",
        "disposal_action",
        "gsc_marking",
        "personal_data_indicated",
    )
    if any(key not in review for key in required):
        return None
    if review.get("every_field_confirmed") is not True:
        return None
    category = review["file_plan_category"]
    retention = review["retention_entry"]
    disposal = review["disposal_action"]
    marking = review["gsc_marking"]
    personal = review["personal_data_indicated"]
    if category is not None and category not in BY_ID:
        return None
    if retention is not None and retention not in BY_RETENTION:
        return None
    if category is not None and retention is not None and BY_ID[category]["retention_entry"] != retention:
        return None
    if category is None and retention is not None:
        return None
    if disposal not in DISPOSAL_ACTIONS:
        return None
    if marking is not None and marking not in MARKINGS:
        return None
    if not isinstance(personal, bool):
        return None
    return {
        "file_plan_category": category,
        "retention_entry": retention,
        "disposal_action": disposal,
        "gsc_marking": marking,
        "personal_data_indicated": personal,
    }


def _proposed_fields(result: dict) -> dict:
    proposals = result["proposals"]
    return {
        "file_plan_category": proposals["file_plan"]["category_id"],
        "retention_entry": proposals["retention"]["entry_id"],
        "disposal_action": proposals["disposal"]["action"],
        "gsc_marking": proposals["gsc"]["suggestion"],
        "personal_data_indicated": proposals["personal_data"]["indicated"],
    }


def _needs_queue(result: dict, fields: dict) -> bool:
    if result["human_queue"]["required"]:
        return True
    category = BY_ID.get(fields["file_plan_category"])
    if category is not None and category["sensitive"]:
        return True
    if fields["gsc_marking"] in {"OFFICIAL-SENSITIVE", "SECRET", "TOP SECRET"}:
        return True
    if fields["personal_data_indicated"] is True:
        return True
    if result["legal_hold"]["indicated"]:
        return True
    return False


def record_confirmation(proposal: dict, review: dict) -> dict:
    """Record the records manager's confirmation. It does not apply a label."""

    if not isinstance(proposal, dict) or proposal.get("label") != LABEL:
        raise ValueError("proposal is not a classification draft")
    if not isinstance(review, dict):
        raise TypeError("review must be an object")
    result = deepcopy(proposal)
    if result.get("outcome") == "refused":
        return _review_refusal(result, "refused_document")
    if result.get("human_approval") is not None:
        return _review_refusal(result, "already_recorded")
    decision = review.get("decision")
    if decision in PROHIBITED_DECISIONS:
        return _review_refusal(result, "prohibited_decision")
    if decision not in DECISIONS:
        return _review_refusal(result, "decision_not_recognised")
    if review.get("actor_role") != MANAGER_ROLE:
        return _review_refusal(result, "actor_role_rejected")
    actor = review.get("actor_id")
    if not isinstance(actor, str) or not ACTOR_ID.fullmatch(actor):
        return _review_refusal(result, "actor_id_rejected")
    if review.get("document_id") != result.get("document_id") or result.get("document_id") == "unspecified":
        return _review_refusal(result, "document_id_rejected")
    if decision == REJECT:
        result["review"] = {
            "decision": REJECT,
            "accepted": True,
            "refused": False,
            "reason": "rejected_by_records_manager",
            "executed": False,
        }
        result["human_approval"] = {
            "approver_role": MANAGER_ROLE,
            "actor_id": actor,
            "decision": REJECT,
            "recorded": True,
            "executed": False,
        }
        result["flags"]["classification_confirmed"] = False
        _force(result)
        return result

    fields = _confirmed_fields(review)
    if fields is None:
        return _review_refusal(result, "field_not_confirmed")
    proposed = _proposed_fields(result)
    differs = fields != proposed
    if decision == CONFIRM and differs:
        return _review_refusal(result, "values_differ_use_change")
    if decision == CHANGE and not differs:
        return _review_refusal(result, "values_match_use_confirm")
    existing = result["proposals"]["gsc"].get("existing_marking") or result["proposals"]["gsc"].get("body_marking")
    if _rank(fields["gsc_marking"]) < _rank(existing):
        return _review_refusal(result, "downgrade_refused")
    if result["legal_hold"]["indicated"] and fields["disposal_action"] == "review_then_destroy_not_executed":
        return _review_refusal(result, "legal_hold_blocks_destroy")
    if result["gaps"] and review.get("acknowledge_gaps") is not True:
        return _review_refusal(result, "gaps_not_acknowledged")
    if result["stale"]["rules_current"] is False and review.get("acknowledge_stale") is not True:
        return _review_refusal(result, "stale_not_acknowledged")
    if _needs_queue(result, fields) and review.get("queue_reviewed") is not True:
        return _review_refusal(result, "queue_not_reviewed")

    result["confirmed_fields"] = fields
    result["review"] = {
        "decision": decision,
        "accepted": True,
        "refused": False,
        "reason": "classification_confirmed" if decision == CONFIRM else "classification_changed",
        "executed": False,
    }
    result["human_approval"] = {
        "approver_role": MANAGER_ROLE,
        "actor_id": actor,
        "decision": decision,
        "every_field_confirmed": True,
        "queue_reviewed": review.get("queue_reviewed") is True,
        "fields": fields,
        "recorded": True,
        "executed": False,
    }
    result["flags"]["classification_confirmed"] = True
    result["flags"]["labels_stubbed"] = False
    _force(result)
    return result


def apply_confirmed_labels(confirmed: dict) -> dict:
    """Stub a label receipt. Purview is not called. Nothing is deleted or moved."""

    if not isinstance(confirmed, dict) or confirmed.get("label") != LABEL:
        raise ValueError("proposal is not a classification draft")
    result = deepcopy(confirmed)
    if result.get("flags", {}).get("classification_confirmed") is not True:
        result["label_stub"] = {"stub": False, "purview_called": False, "reason": "not_confirmed"}
        _force(result)
        return result
    if result["human_approval"]["decision"] == REJECT:
        result["label_stub"] = {"stub": False, "purview_called": False, "reason": "rejected"}
        result["flags"]["labels_stubbed"] = False
        _force(result)
        return result
    if result["regulatory"]["outside_code_scope"]:
        result["label_stub"] = {"stub": False, "purview_called": False, "reason": "outside_code_scope"}
        result["flags"]["labels_stubbed"] = False
        _force(result)
        return result
    if result["stale"]["rules_current"] is False:
        result["label_stub"] = {"stub": False, "purview_called": False, "reason": "stale_sources"}
        result["flags"]["labels_stubbed"] = False
        _force(result)
        return result
    fields = result["confirmed_fields"]
    existing = result["proposals"]["gsc"].get("existing_marking") or result["proposals"]["gsc"].get("body_marking")
    if _rank(fields["gsc_marking"]) < _rank(existing):
        result["label_stub"] = {"stub": False, "purview_called": False, "reason": "downgrade_refused"}
        result["flags"]["labels_stubbed"] = False
        _force(result)
        return result
    if result["legal_hold"]["indicated"] and fields["disposal_action"] == "review_then_destroy_not_executed":
        result["label_stub"] = {"stub": False, "purview_called": False, "reason": "legal_hold_blocks_destroy"}
        result["flags"]["labels_stubbed"] = False
        _force(result)
        return result
    result["label_stub"] = {
        "stub": True,
        "purview_called": False,
        "reason": "stubbed_after_confirmation",
        "retention_label_name": None
        if fields["retention_entry"] is None
        else f"synthetic:{fields['retention_entry']}",
        "sensitivity_label_name": fields["gsc_marking"],
        "disposal_action_named": fields["disposal_action"],
        "disposal_executed": False,
        "note": "Not sent to Microsoft Purview. Not a tenant label. The record was not deleted, moved, or downgraded.",
    }
    result["flags"]["labels_stubbed"] = True
    _force(result)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Propose a records classification. Does not delete, dispose, move, or downgrade."
    )
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--as-of", required=True)
    args = parser.parse_args(argv)
    try:
        document = json.loads(args.input.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        print("The input could not be read.", file=sys.stderr)
        return 2
    if not isinstance(document, dict):
        print("The input must be a JSON object.", file=sys.stderr)
        return 2
    try:
        draft = classify_record(document, args.as_of)
    except (TypeError, ValueError, RecordsForbidden) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    json.dump(draft, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
