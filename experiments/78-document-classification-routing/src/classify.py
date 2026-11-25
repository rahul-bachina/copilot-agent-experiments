#!/usr/bin/env python3
"""Propose a document class and a destination. Do not file it.

The named reviewer confirms the class and the destination. Only then is the
routing written to the synthetic staging store. The agent does not file,
move, delete, or send. An approval marker inside the document is not the
approval step. The approved bytes are the agent-held copy.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from copy import deepcopy
from datetime import date
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from clocks import empty_clock, foi_clock, sar_clock
    from cues import (
        approval_signals,
        concerns_in,
        instruction_signals,
        is_instruction,
        load_taxonomy,
        match_classes,
        normalise,
        visible_text,
        without_instructions,
    )
    from dates import annotate, as_date, parse_date
    from marking import above_ceiling, derive
    from mask import mask_counts
    from reuse import NeighbourMissing, identifier_counts, intake_document, marking_rank
    from sources import PINNED_ON, REVIEW_DUE, uk_context
else:
    from .clocks import empty_clock, foi_clock, sar_clock
    from .cues import (
        approval_signals,
        concerns_in,
        instruction_signals,
        is_instruction,
        load_taxonomy,
        match_classes,
        normalise,
        visible_text,
        without_instructions,
    )
    from .dates import annotate, as_date, parse_date
    from .marking import above_ceiling, derive
    from .mask import mask_counts
    from .reuse import NeighbourMissing, identifier_counts, intake_document, marking_rank
    from .sources import PINNED_ON, REVIEW_DUE, uk_context

LABEL = "DOCUMENT CLASS AND ROUTE FOR THE NAMED REVIEWER"
CATALOGUE_ID = "O003"
EXPERIMENT_ID = "exp-78-document-classification-routing"
ROOT = Path(__file__).resolve().parents[1]
MAX_CHARS = 20_000
DOCUMENT_ID = re.compile(r"^SYN-[A-Z0-9-]{1,32}$")
_HELD: dict[str, dict] = {}
_STORE: dict[str, dict] = {}
_PROHIBITED = (
    "human_approval",
    "approved",
    "approval",
    "staged",
    "filed",
    "moved",
    "deleted",
    "sent",
    "selected_class",
    "destination",
    "confidence",
    "clearance",
    "role",
    "forced_class",
)
_COUNT_KEYS = {
    "people",
    "people_count",
    "residents",
    "complainants",
    "individuals",
    "headcount",
    "persons",
    "beneficiaries",
    "children",
    "count",
    "total",
    "n",
    "percent",
    "percentage",
    "pct",
    "proportion",
    "difference",
    "delta",
    "share",
}
_PERSON_COUNT = re.compile(
    r"\b(?:[1-4]|one|two|three|four)\s+"
    r"(?:people|residents|complainants|individuals|persons|children)\b",
    re.I,
)
_RECEIVED = re.compile(r"\breceived on\s+(\d{4}-\d{2}-\d{2})\b", re.I)
_RETENTION = re.compile(r"RETENTION:\s*([^\n.;]+)", re.I)
_HOLD = re.compile(r"\b(?:legal hold|litigation hold|do not destroy|do not dispose)\b", re.I)
_MISSING = object()


class RoutingForbidden(RuntimeError):
    """The agent does not file, move, delete, or send."""

    __test__ = False


class NotSynthetic(ValueError):
    """The document is not marked synthetic. The message does not include the body."""


def file_document(*_args, **_kwargs) -> None:
    raise RoutingForbidden("The agent does not file a document.")


def move_document(*_args, **_kwargs) -> None:
    raise RoutingForbidden("The agent does not move a document.")


def delete_document(*_args, **_kwargs) -> None:
    raise RoutingForbidden("The agent does not delete a document.")


def send_document(*_args, **_kwargs) -> None:
    raise RoutingForbidden("The agent does not send a document.")


def reset_state() -> None:
    _HELD.clear()
    _STORE.clear()


def _load_json(name: str) -> dict:
    return json.loads((ROOT / "fixtures" / name).read_text(encoding="utf-8"))


def pinned_sources() -> dict:
    return {
        "taxonomy": _load_json("taxonomy.json"),
        "routing": _load_json("routing.json"),
        "directory": _load_json("directory.json"),
    }


def _digest(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _projection(result: dict) -> dict:
    return {
        "document_id": result.get("document_id"),
        "as_of": result.get("as_of"),
        "outcome": result.get("outcome"),
        "proposal": result.get("proposal"),
        "destination": result.get("destination"),
        "route_seen": result.get("route_seen"),
        "queue_reasons": result.get("queue_reasons"),
        "marking": result.get("marking"),
        "legal_hold": result.get("legal_hold"),
        "legal_hold_conflict": result.get("legal_hold_conflict"),
        "legal_hold_unparseable": result.get("legal_hold_unparseable"),
        "retention": result.get("retention"),
        "retention_unparseable": result.get("retention_unparseable"),
        "prompt_injection": result.get("prompt_injection"),
        "concerns": result.get("concerns"),
        "clocks": result.get("clocks"),
        "required_acknowledgements": result.get("required_acknowledgements"),
        "suppression": result.get("suppression"),
        "dates": result.get("dates"),
        "caller_sources": result.get("caller_sources"),
        "above_clearance": result.get("above_clearance"),
        "locks": result.get("locks"),
    }


def content_hash(result: dict) -> str:
    return _digest(_projection(result))


def _locks() -> dict:
    return {
        "forced_class": False,
        "classification_decided": False,
        "instructions_followed": False,
        "approval_marker_trusted": False,
        "caller_taxonomy_applied": False,
        "caller_routing_applied": False,
        "caller_directory_applied": False,
        "described_as_anonymised": False,
        "coerced": False,
        "role_in_text_trusted": False,
        "clearance_in_text_trusted": False,
        "filed": False,
        "moved": False,
        "deleted": False,
        "sent": False,
    }


def _force(result: dict) -> None:
    result["locks"] = _locks()
    result["forced_class"] = False
    result["classification_decided"] = False
    result["may_be_relied_on"] = False
    result["instructions_followed"] = False
    result["approval_marker_trusted"] = False
    result["caller_taxonomy_applied"] = False
    result["caller_routing_applied"] = False
    result["caller_directory_applied"] = False
    result["described_as_anonymised"] = False
    result["coerced"] = False
    result["role_in_text_trusted"] = False
    result["clearance_in_text_trusted"] = False
    result["filed"] = False
    result["moved"] = False
    result["deleted"] = False
    result["sent"] = False
    injection = result.get("prompt_injection")
    if isinstance(injection, dict):
        injection["followed"] = False


def _parse_as_of(value: object) -> date:
    if isinstance(value, date):
        return value
    reading = parse_date(value)
    parsed = as_date(reading)
    if parsed is None:
        raise ValueError("as_of must be an unambiguous calendar date")
    return parsed


def _people(directory: dict) -> list[dict]:
    rows = directory.get("people") if isinstance(directory, dict) else None
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict)]


def _person(directory: dict, ref: object) -> dict | None:
    if not isinstance(ref, str) or not ref:
        return None
    for row in _people(directory):
        if row.get("employee_ref") == ref:
            return row
    return None


def _reviewer_ok(person: dict | None) -> bool:
    if not isinstance(person, dict):
        return False
    if person.get("guest") is True:
        return False
    return person.get("role") == "document_reviewer"


def _differs(caller: object, pinned: dict) -> bool:
    if not isinstance(caller, dict):
        return True
    return caller != pinned


def _date_fact(raws: list, *, on: date) -> dict:
    if not raws:
        return {
            "present": False,
            "iso": None,
            "conflict": False,
            "unparseable": False,
            "ambiguous": False,
            "future": False,
            "impossible": False,
            "coerced": False,
        }
    readings = [annotate(parse_date(item), on=on) for item in raws]
    isos = [item["iso"] for item in readings if item.get("iso") and not item.get("ambiguous")]
    unique = set(isos)
    ambiguous = any(item.get("ambiguous") for item in readings)
    impossible = any(item.get("impossible") for item in readings)
    conflict = len(unique) > 1 or (len(raws) > 1 and (ambiguous or any(item.get("unparseable") for item in readings)))
    if len(raws) > 1 and len(unique) != 1:
        conflict = True
    chosen = None if conflict or len(unique) != 1 else next(iter(unique))
    future = False
    if chosen is not None:
        future = any(item.get("future") and item.get("iso") == chosen for item in readings)
    return {
        "present": True,
        "iso": chosen,
        "conflict": conflict,
        "unparseable": any(item.get("unparseable") for item in readings) or (chosen is None and not ambiguous and not conflict),
        "ambiguous": ambiguous,
        "future": future,
        "impossible": impossible,
        "coerced": False,
    }


def _raw_dates(metadata: dict, keys: tuple[str, ...]) -> list:
    raws: list = []
    for key in keys:
        if key not in metadata:
            continue
        value = metadata[key]
        if isinstance(value, list):
            raws.extend(value)
        else:
            raws.append(value)
    return raws


def _received_from_text(text: str, *, on: date) -> list:
    found = []
    for sentence in text.split("\n"):
        if is_instruction(sentence):
            continue
        for match in _RECEIVED.finditer(sentence):
            if re.search(r"\b(?:not|never|no)\b(?:\s+\S+){0,6}\s+received on\b", sentence, re.I):
                continue
            found.append(match.group(1))
    return found


def _hold_and_retention(metadata: dict, text: str) -> dict:
    hold_values = []
    unparseable_hold = False
    if "legal_hold" in metadata:
        value = metadata.get("legal_hold")
        if isinstance(value, bool):
            hold_values.append(value)
        elif value not in (None, ""):
            unparseable_hold = True
    text_hold = False
    labels: list[str] = []
    retention_bad = False
    meta_retention = metadata.get("retention")
    if isinstance(meta_retention, str) and meta_retention.strip():
        labels.append(meta_retention.strip())
    elif isinstance(meta_retention, list):
        for item in meta_retention:
            if isinstance(item, str) and item.strip() and item.strip() not in labels:
                labels.append(item.strip())
            elif item not in (None, ""):
                retention_bad = True
    elif meta_retention not in (None, "", []):
        retention_bad = True
    for sentence in text.splitlines():
        if is_instruction(sentence):
            continue
        if _HOLD.search(sentence):
            text_hold = True
        for match in _RETENTION.finditer(sentence):
            label = match.group(1).strip()
            if label and label not in labels:
                labels.append(label)
    if any(_HOLD.search(label) for label in labels):
        text_hold = True
    explicit_true = any(item is True for item in hold_values) or text_hold
    explicit_false = any(item is False for item in hold_values)
    conflict = explicit_true and explicit_false
    if explicit_true:
        held = True
    elif unparseable_hold and not explicit_false:
        held = None
    else:
        held = False
    return {
        "legal_hold": held,
        "legal_hold_conflict": conflict,
        "legal_hold_unparseable": unparseable_hold,
        "retention": labels,
        "retention_unparseable": retention_bad,
    }


def _suppress(metadata: dict, text: str) -> dict:
    fields: list[str] = []
    unparseable = False

    def walk(node: object, prefix: str) -> None:
        nonlocal unparseable
        if isinstance(node, dict):
            for key, value in node.items():
                path = f"{prefix}.{key}" if prefix else str(key)
                folded = str(key).casefold()
                count_like = folded in _COUNT_KEYS or folded.endswith(
                    ("_count", "_total", "_percent", "_percentage")
                )
                if count_like:
                    fields.append(path)
                    if isinstance(value, bool) or not isinstance(value, (int, float)):
                        if not isinstance(value, str):
                            unparseable = True
                        elif not value.isdigit():
                            unparseable = True
                    continue
                walk(value, path)
        elif isinstance(node, list):
            for index, item in enumerate(node):
                walk(item, f"{prefix}[{index}]")

    if isinstance(metadata, dict):
        walk(metadata, "")
    return {
        "fields": sorted(set(fields)),
        "in_text": bool(_PERSON_COUNT.search(text or "")),
        "values_stored": False,
        "difference_published": False,
        "percent_published": False,
        "unparseable": unparseable,
        "coerced": False,
    }


def _proposal(rows: list[dict]) -> dict:
    multi = len(rows) >= 2
    carve = any(row["carve_out"] for row in rows)
    if not rows:
        confidence = "none"
        selected = None
    elif multi or carve:
        confidence = "multi" if multi else "carve_out"
        selected = None
    else:
        row = rows[0]
        if len(row["strong"]) >= 2:
            confidence = "high"
            selected = row["class_id"]
        elif len(row["strong"]) == 1:
            confidence = "medium"
            selected = row["class_id"]
        else:
            confidence = "low"
            selected = None
    ranked = []
    for row in rows[:2]:
        ranked.append(
            {
                "class_id": row["class_id"],
                "title": row["title"],
                "strong": list(row["strong"]),
                "weak": list(row["weak"]),
                "carve_out": row["carve_out"],
            }
        )
    alternative = ranked[1] if len(ranked) > 1 else None
    evidence = []
    for row in rows:
        for strength, phrases in (("strong", row["strong"]), ("weak", row["weak"])):
            for phrase in phrases:
                evidence.append({"class_id": row["class_id"], "phrase": phrase, "strength": strength})
    return {
        "selected_class": selected,
        "class_proposed": selected is not None,
        "forced_class": False,
        "confidence": confidence,
        "evidence": evidence,
        "alternative": alternative,
        "ranked": ranked,
        "multi_type": multi,
        "carve_out": carve,
        "candidate_count": len(rows),
    }


def _queue_for(routing: dict, class_id: str | None) -> dict:
    queues = routing.get("queues") or {}
    if class_id and class_id in queues:
        row = queues[class_id]
        return {
            "queue": row.get("queue"),
            "library": row.get("library"),
            "human_required": row.get("human_required") is True,
        }
    human = queues.get("human_review") or {}
    return {"queue": human.get("queue"), "library": None, "human_required": True}


def _metadata_strings(metadata: dict) -> str:
    parts: list[str] = []

    def walk(node: object) -> None:
        if isinstance(node, str):
            parts.append(node)
        elif isinstance(node, dict):
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(metadata)
    return "\n".join(parts)


def _empty_neighbours() -> dict:
    return {
        "intake": {
            "called": False,
            "experiment_id": "exp-12-document-intake",
            "files_confirmed": False,
            "purpose_confirmed": False,
            "content_recorded": False,
        },
        "uk_identifiers": {
            "called": False,
            "experiment_id": "exp-08-uk-pii-redaction-gateway",
            "count": 0,
            "types": [],
            "output_is_anonymised": False,
            "values_stored": False,
            "redacted_text_copied": False,
        },
    }


def classify_document(document: dict, as_of: date | str) -> dict:
    """Propose a class and a destination for one synthetic document."""

    if not isinstance(document, dict):
        raise TypeError("document must be an object")
    if document.get("synthetic") is not True:
        raise NotSynthetic("The document is not marked synthetic.")
    on = _parse_as_of(as_of)
    working = dict(document)
    ignored = [key for key in _PROHIBITED if key in working]
    for key in _PROHIBITED:
        working.pop(key, None)
    pinned = pinned_sources()
    caller_taxonomy = working.pop("taxonomy", None)
    caller_routing = working.pop("routing_table", None)
    caller_directory = working.pop("directory", None)
    caller_sources = {
        "taxonomy_supplied": caller_taxonomy is not None,
        "taxonomy_differs": caller_taxonomy is not None and _differs(caller_taxonomy, pinned["taxonomy"]),
        "routing_supplied": caller_routing is not None,
        "routing_differs": caller_routing is not None and _differs(caller_routing, pinned["routing"]),
        "directory_supplied": caller_directory is not None,
        "directory_differs": caller_directory is not None and _differs(caller_directory, pinned["directory"]),
        "applied": False,
    }
    document_id = working.get("document_id")
    id_ok = isinstance(document_id, str) and DOCUMENT_ID.fullmatch(document_id) is not None
    reviewer_ref = working.get("reviewer_ref")
    person = _person(pinned["directory"], reviewer_ref)
    reviewer_ok = _reviewer_ok(person)
    metadata = working.get("metadata") if isinstance(working.get("metadata"), dict) else {}
    raw_text = working.get("text") if isinstance(working.get("text"), str) else ""
    text_unreadable = not isinstance(working.get("text"), str)
    too_large = isinstance(working.get("text"), str) and len(working.get("text")) > MAX_CHARS
    cleaned, zero_signals = normalise(raw_text if not too_large else "")
    visible, hidden_signals = visible_text(cleaned)
    meta_text = _metadata_strings(metadata)
    signal_text = visible + "\n" + meta_text
    signals = []
    for signal in zero_signals + hidden_signals + instruction_signals(signal_text):
        if signal not in signals:
            signals.append(signal)
    approvals = approval_signals(signal_text)
    classes = pinned["taxonomy"]["classes"]
    rows = [] if too_large or text_unreadable else match_classes(visible, classes)
    proposal = _proposal(rows)
    concern_source = signal_text if not too_large else ""
    concern_flags = concerns_in(concern_source)
    type_values = metadata.get("document_type")
    type_conflict = isinstance(type_values, list) and len({str(item) for item in type_values}) > 1
    received_raw = _raw_dates(metadata, ("received_on", "date_received", "received_date"))
    if not too_large:
        received_raw = list(received_raw) + _received_from_text(visible, on=on)
    received = _date_fact(received_raw, on=on)
    document_date = _date_fact(_raw_dates(metadata, ("document_date",)), on=on)
    stated_deadline = _date_fact(_raw_dates(metadata, ("stated_deadline", "reply_by")), on=on)
    dates = {
        "received": received,
        "document_date": document_date,
        "stated_deadline": stated_deadline,
        "coerced": False,
    }
    if too_large or text_unreadable:
        marking = {
            "applied": None,
            "from_metadata": [],
            "from_content": [],
            "from_experiment_49": None,
            "conflict": False,
            "unparseable": False,
            "self_declared_clearance_ignored": True,
            "higher_taken": True,
            "rank_source": "exp-49-records-classification MARKING_RANK",
            "coerced": False,
            "experiment_49_file_plan_used": False,
            "not_scanned": True,
        }
        held_info = {
            "legal_hold": None,
            "legal_hold_conflict": False,
            "legal_hold_unparseable": False,
            "retention": [],
            "retention_unparseable": False,
        }
    else:
        marking_input = metadata.get("marking", metadata.get("protective_marking", metadata.get("classification")))
        marking = derive(marking_input, visible)
        held_info = _hold_and_retention(metadata, without_instructions(visible))
    rank = marking_rank()
    ceiling = person.get("clearance") if reviewer_ok and isinstance(person, dict) else None
    if reviewer_ok:
        above = above_ceiling(marking.get("applied"), ceiling if isinstance(ceiling, str) else None, rank)
    else:
        above = marking.get("applied") in {"SECRET", "TOP SECRET"}
    suppression = _suppress(metadata, "" if too_large else visible)
    foi = any(row["class_id"] == "foi_request" for row in rows)
    sar = any(row["class_id"] == "subject_access_request" for row in rows)
    received_day = None
    if received.get("iso") and not received.get("conflict"):
        received_day = date.fromisoformat(received["iso"])
    clocks = {
        "foi": foi_clock(received_day, working.get("stated_response_working_days")) if foi else empty_clock(),
        "sar": sar_clock(received_day, working.get("stated_response_days")) if sar else empty_clock(),
    }
    if foi:
        clocks["foi"]["recognised"] = True
    if sar:
        clocks["sar"]["recognised"] = True
    table = _queue_for(pinned["routing"], proposal["selected_class"])
    queue = table["queue"]
    library = table["library"]
    overridden = False
    if concern_flags["safeguarding"] or proposal["selected_class"] == "safeguarding_referral":
        queue = pinned["routing"]["queues"]["safeguarding_referral"]["queue"]
        library = None
        overridden = True
    elif concern_flags["distress"] or concern_flags["whistleblowing"] or concern_flags["urgent"]:
        queue = pinned["routing"]["queues"]["human_review"]["queue"]
        library = None
        overridden = True
    elif above or held_info["legal_hold"] is True or marking.get("applied") in {"SECRET", "TOP SECRET"}:
        queue = pinned["routing"]["queues"]["human_review"]["queue"]
        library = None
        overridden = True
    destination = {
        "queue": queue,
        "library": library,
        "table_queue": table["queue"],
        "human_required": True if overridden else table["human_required"] or proposal["selected_class"] is None,
        "overridden_to_human": overridden,
    }
    reasons: list[str] = []
    if text_unreadable:
        reasons.append("unreadable_input")
    if too_large:
        reasons.append("too_large")
    if not text_unreadable and not too_large and not raw_text.strip():
        reasons.append("empty_text")
    if proposal["multi_type"]:
        reasons.append("multi_type")
    if proposal["confidence"] == "low":
        reasons.append("low_confidence")
    if proposal["confidence"] == "none":
        reasons.append("unknown")
    if proposal["carve_out"]:
        reasons.append("carve_out")
    if concern_flags["distress"]:
        reasons.append("distress")
    if concern_flags["safeguarding"]:
        reasons.append("safeguarding")
    if concern_flags["whistleblowing"]:
        reasons.append("whistleblowing")
    if concern_flags["urgent"]:
        reasons.append("urgent")
    if foi or sar:
        reasons.append("statutory_clock")
    if table["human_required"] and proposal["selected_class"] is not None:
        reasons.append("routing_table_human")
    if above:
        reasons.append("above_clearance")
    if marking.get("applied") in {"SECRET", "TOP SECRET"}:
        reasons.append("high_marking")
    if held_info["legal_hold"] is True or held_info["legal_hold_unparseable"]:
        reasons.append("legal_hold")
    if signals or approvals:
        reasons.append("injection")
    stale = on >= REVIEW_DUE
    not_yet = on < PINNED_ON
    if stale:
        reasons.append("stale_sources")
    if not_yet:
        reasons.append("sources_not_yet_pinned")
    if any(dates[name].get("conflict") for name in dates if name != "coerced"):
        reasons.append("date_conflict")
    if any(dates[name].get("unparseable") for name in ("received", "document_date", "stated_deadline")):
        reasons.append("date_unparseable")
    if any(dates[name].get("ambiguous") for name in ("received", "document_date", "stated_deadline")):
        reasons.append("date_ambiguous")
    if any(dates[name].get("future") for name in ("received", "document_date", "stated_deadline")):
        reasons.append("date_future")
    if any(dates[name].get("impossible") for name in ("received", "document_date", "stated_deadline")):
        reasons.append("date_impossible")
    if caller_sources["taxonomy_differs"] or caller_sources["routing_differs"] or caller_sources["directory_differs"]:
        reasons.append("caller_source_differs")
    if suppression["fields"] or suppression["in_text"] or suppression["unparseable"]:
        reasons.append("suppression")
    if type_conflict:
        reasons.append("type_conflict")
    if not reviewer_ok:
        reasons.append("needs_named_reviewer")
    deduped: list[str] = []
    for reason in reasons:
        if reason not in deduped:
            deduped.append(reason)
    if not reviewer_ok:
        outcome = "needs_named_reviewer"
    elif deduped:
        outcome = "human_queue"
    else:
        outcome = "ready_for_confirmation"
    neighbours = _empty_neighbours()
    masking = mask_counts("" if too_large or text_unreadable else raw_text)
    if not too_large and not text_unreadable and id_ok:
        try:
            filename = working.get("filename")
            if not isinstance(filename, str) or not filename or len(filename) > 120 or "\n" in filename:
                filename = "document.txt"
            neighbours["intake"] = intake_document(document_id, filename, raw_text, on=on)
            neighbours["uk_identifiers"] = identifier_counts(raw_text, on=on)
        except NeighbourMissing as exc:
            raise RoutingForbidden(
                "A required neighbouring experiment is not beside this folder."
            ) from exc
    acknowledgements = ["pins_seen"]
    if stale or not_yet or caller_sources["taxonomy_differs"] or caller_sources["routing_differs"] or caller_sources["directory_differs"]:
        acknowledgements.append("sources_seen")
    if any(reason.startswith("date_") for reason in deduped):
        acknowledgements.append("dates_seen")
    if foi or sar:
        acknowledgements.append("clocks_seen")
    if marking.get("conflict") or marking.get("unparseable") or marking.get("applied") not in {None, "OFFICIAL"}:
        acknowledgements.append("marking_seen")
    if held_info["legal_hold"] is True or held_info["retention"] or held_info["retention_unparseable"]:
        acknowledgements.append("hold_seen")
    if suppression["fields"] or suppression["in_text"] or suppression["unparseable"]:
        acknowledgements.append("suppression_seen")
    result = {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment_id": EXPERIMENT_ID,
        "autonomy": "A1",
        "organisation": "Northwharf Borough Council",
        "organisation_is_fictional": True,
        "document_id": document_id if id_ok else None,
        "reviewer_ref": reviewer_ref if reviewer_ok else None,
        "reviewer_on_directory": reviewer_ok,
        "as_of": on.isoformat(),
        "outcome": outcome,
        "human_approval": None,
        "staged": False,
        "route_seen": False,
        "human_route_required": outcome == "human_queue",
        "sources_current": not stale and not not_yet,
        "proposal": proposal,
        "destination": destination,
        "queue_reasons": deduped,
        "marking": marking,
        "above_clearance": above,
        "legal_hold": held_info["legal_hold"],
        "legal_hold_conflict": held_info["legal_hold_conflict"],
        "legal_hold_unparseable": held_info["legal_hold_unparseable"],
        "retention": held_info["retention"],
        "retention_unparseable": held_info["retention_unparseable"],
        "prompt_injection": {
            "followed": False,
            "signals": signals,
            "approval_markers": approvals,
            "marker_trusted": False,
        },
        "concerns": {
            "distress": concern_flags["distress"],
            "safeguarding": concern_flags["safeguarding"],
            "whistleblowing": concern_flags["whistleblowing"],
            "urgent": concern_flags["urgent"],
            "cue_copied": False,
            "seen": False,
        },
        "clocks": clocks,
        "dates": dates,
        "caller_sources": caller_sources,
        "suppression": suppression,
        "masking": masking,
        "neighbours": neighbours,
        "ignored_request_keys": ignored,
        "type_conflict": type_conflict,
        "metadata_class_used": False,
        "text_recorded": False,
        "required_acknowledgements": acknowledgements,
        "uk_context": uk_context(),
        "distinct_from": "Experiment 49 classifies a record against a file plan and a retention schedule. This experiment classifies incoming correspondence against the pinned taxonomy.",
    }
    _force(result)
    result["content_hash"] = content_hash(result)
    if id_ok:
        _HELD[document_id] = deepcopy(result)
    return deepcopy(result)


def _held_for(result: dict) -> dict | None:
    document_id = result.get("document_id") if isinstance(result, dict) else None
    if not isinstance(document_id, str):
        return None
    held = _HELD.get(document_id)
    return held if isinstance(held, dict) else None


def _blocked(held: dict | None, reason: str) -> dict:
    if held is None:
        return {
            "blocked_reason": reason,
            "human_approval": None,
            "staged": False,
            "filed": False,
            "moved": False,
            "deleted": False,
            "sent": False,
            "route_seen": False,
        }
    updated = deepcopy(held)
    _force(updated)
    updated["human_approval"] = None
    updated["staged"] = False
    updated["blocked_reason"] = reason
    updated["content_hash"] = content_hash(updated)
    return updated


def _named_reviewer(held: dict, directory: dict, approver_ref: object) -> str | None:
    pinned = pinned_sources()["directory"]
    if directory != pinned:
        return "caller_directory_not_used"
    if approver_ref != held.get("reviewer_ref"):
        return "not_the_named_reviewer"
    person = _person(pinned, approver_ref)
    if not _reviewer_ok(person):
        return "approver_not_directory_reviewer"
    return None


def _ack(held: dict, approval: dict) -> str | None:
    for key in held.get("required_acknowledgements") or []:
        if approval.get(key) is not True:
            return f"{key}_not_boolean_true"
    return None


def _same_held(result: dict, held: dict) -> bool:
    return content_hash(result) == held.get("content_hash")


def record_route_seen(result: dict, directory: dict, approval: dict) -> dict:
    """Record that the named reviewer has seen the human route. Nothing is staged."""

    held = _held_for(result)
    if held is None:
        return _blocked(None, "not_held")
    if not isinstance(result, dict) or not _same_held(result, held):
        return _blocked(held, "content_hash_mismatch")
    if not isinstance(approval, dict):
        return _blocked(held, "approval_not_object")
    if approval.get("item") != "route-seen" or approval.get("decision") != "seen":
        return _blocked(held, "wrong_item")
    if approval.get("content_hash") != held.get("content_hash"):
        return _blocked(held, "content_hash_mismatch")
    if held.get("human_route_required") is not True:
        return _blocked(held, "route_not_required")
    reason = _named_reviewer(held, directory, approval.get("approver_ref"))
    if reason:
        return _blocked(held, reason)
    updated = deepcopy(held)
    updated["route_seen"] = True
    updated["concerns"] = dict(updated.get("concerns") or {})
    updated["concerns"]["seen"] = True
    updated["concerns"]["cue_copied"] = False
    _force(updated)
    updated["human_approval"] = None
    updated["staged"] = False
    updated["content_hash"] = content_hash(updated)
    _HELD[updated["document_id"]] = deepcopy(updated)
    return deepcopy(updated)


def record_routing_confirmation(result: dict, directory: dict, approval: dict) -> dict:
    """Stage the routing only when the named reviewer confirms this held copy."""

    held = _held_for(result)
    if held is None:
        return _blocked(None, "not_held")
    if not isinstance(result, dict) or not _same_held(result, held):
        return _blocked(held, "content_hash_mismatch")
    if not isinstance(approval, dict):
        return _blocked(held, "approval_not_object")
    if approval.get("decision") in {"file", "move", "delete", "send"} or approval.get("filed") is True:
        return _blocked(held, "file_is_not_this_step")
    if approval.get("item") != "routing" or approval.get("decision") != "confirm-routing":
        return _blocked(held, "wrong_item")
    if held.get("outcome") == "needs_named_reviewer" or held.get("reviewer_on_directory") is not True:
        return _blocked(held, "reviewer_not_on_directory")
    if held.get("human_route_required") is True and held.get("route_seen") is not True:
        return _blocked(held, "route_not_seen")
    if approval.get("content_hash") != held.get("content_hash"):
        return _blocked(held, "content_hash_mismatch")
    if approval.get("document_id") != held.get("document_id"):
        return _blocked(held, "document_mismatch")
    if approval.get("class_id", _MISSING) != (held.get("proposal") or {}).get("selected_class"):
        return _blocked(held, "class_mismatch")
    if approval.get("destination_queue") != (held.get("destination") or {}).get("queue"):
        return _blocked(held, "destination_mismatch")
    reason = _ack(held, approval)
    if reason:
        return _blocked(held, reason)
    role_reason = _named_reviewer(held, directory, approval.get("approver_ref"))
    if role_reason:
        return _blocked(held, role_reason)
    updated = deepcopy(held)
    _force(updated)
    updated["human_approval"] = {
        "item": "routing",
        "approver_ref": approval.get("approver_ref"),
        "content_hash": held["content_hash"],
        "class_id": (held.get("proposal") or {}).get("selected_class"),
        "destination_queue": (held.get("destination") or {}).get("queue"),
        "recorded": True,
        "files": False,
    }
    updated["staged"] = True
    updated["content_hash"] = held["content_hash"]
    row = {
        "document_id": held.get("document_id"),
        "content_hash": held["content_hash"],
        "reviewer_ref": held.get("reviewer_ref"),
        "proposal": deepcopy(held.get("proposal")),
        "destination": deepcopy(held.get("destination")),
        "marking": deepcopy(held.get("marking")),
        "legal_hold": held.get("legal_hold"),
        "retention": list(held.get("retention") or []),
        "prompt_injection": deepcopy(held.get("prompt_injection")),
        "concerns": deepcopy(held.get("concerns")),
        "queue_reasons": list(held.get("queue_reasons") or []),
        "suppression": deepcopy(held.get("suppression")),
        "route_seen": held.get("route_seen") is True,
        "required_acknowledgements": list(held.get("required_acknowledgements") or []),
        "filed": False,
        "moved": False,
        "deleted": False,
        "sent": False,
        "store": "synthetic",
    }
    _STORE[f"{held.get('document_id')}:{held['content_hash']}"] = row
    _HELD[held["document_id"]] = deepcopy(updated)
    return deepcopy(updated)


def staged_row(document_id: object, content_hash_value: object) -> dict | None:
    if not isinstance(document_id, str) or not isinstance(content_hash_value, str):
        return None
    row = _STORE.get(f"{document_id}:{content_hash_value}")
    return deepcopy(row) if isinstance(row, dict) else None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Propose a class and a destination for one synthetic document.")
    parser.add_argument("--document", required=True)
    parser.add_argument("--as-of", required=True)
    args = parser.parse_args(argv)
    try:
        document = json.loads(Path(args.document).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        print("The document could not be read.", file=sys.stderr)
        return 2
    try:
        result = classify_document(document, as_of=args.as_of)
    except (NotSynthetic, TypeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
