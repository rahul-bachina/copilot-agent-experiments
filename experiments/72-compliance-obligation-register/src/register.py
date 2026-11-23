#!/usr/bin/env python3
"""Propose obligation-register changes. Stage one only after approval.

The compliance owner approves the exact change. The agent does not interpret
the law as final advice, does not assign accountability, and does not send.
A caller-supplied register, directory, or control library is not the pin.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from copy import deepcopy
from pathlib import Path

if __package__ in {None, ""}:
    from cues import (
        cue_categories,
        injection_signals,
        people_mentions,
        self_declared,
    )
    from dates import in_force, parse_as_of, parse_date_token, review_stale
    from marking import (
        above_ceiling,
        content_markings,
        higher_marking,
        legal_hold,
        metadata_markings,
        retention_labels,
    )
    from mask import mask_text
    from match import addresses, interval_months, relation, theme_reading
    from reuse import (
        cross_check_date,
        experiment_69_reading,
        intake_extracts,
        redact_note,
    )
    from sources import context_pins
else:
    from .cues import (
        cue_categories,
        injection_signals,
        people_mentions,
        self_declared,
    )
    from .dates import in_force, parse_as_of, parse_date_token, review_stale
    from .marking import (
        above_ceiling,
        content_markings,
        higher_marking,
        legal_hold,
        metadata_markings,
        retention_labels,
    )
    from .mask import mask_text
    from .match import addresses, interval_months, relation, theme_reading
    from .reuse import (
        cross_check_date,
        experiment_69_reading,
        intake_extracts,
        redact_note,
    )
    from .sources import context_pins

ROOT = Path(__file__).resolve().parents[1]
LABEL = "OBLIGATION REGISTER PROPOSAL FOR A COMPLIANCE OWNER"
CATALOGUE_ID = "L008"
EXPERIMENT_ID = "72-compliance-obligation-register"
STAGING_TABLE = "cr72_obligation_staging"
PRODUCTION_TABLE = "cr72_obligation_register"
INTERNAL_MINIMUM_MONTHS = 12
_STORE: dict[str, dict] = {}
_QUIET = {
    ("included", None, True),
    ("qualified", None, False),
    ("in_force", None, True),
    ("review_stale", None, False),
    ("below_internal_minimum", None, False),
}
_VIEW_KEYS = (
    "obligation_id",
    "source_id",
    "provision",
    "obligation_text",
    "applicability",
    "proposed_owner_ref",
    "review_date",
    "review_stale",
    "linked_controls",
    "covered",
    "included",
    "qualified",
    "in_force",
    "status",
    "possible_duplicate_of",
    "below_internal_minimum",
)


class NotSynthetic(ValueError):
    """The payload is not marked synthetic."""


class RegisterForbidden(RuntimeError):
    """A consequential action this agent does not take."""


def interpret_law(*_args, **_kwargs) -> None:
    raise RegisterForbidden("The agent does not interpret the law as final advice.")


def assign_accountability(*_args, **_kwargs) -> None:
    raise RegisterForbidden("The agent does not assign accountability.")


def send(*_args, **_kwargs) -> None:
    raise RegisterForbidden("The agent does not send anything.")


def write_production(*_args, **_kwargs) -> None:
    raise RegisterForbidden("The agent does not write the production register.")


def mark_covered(*_args, **_kwargs) -> None:
    raise RegisterForbidden("The agent does not mark an obligation covered.")


def reset_staging() -> None:
    _STORE.clear()


def staging_rows() -> list[dict]:
    return [deepcopy(_STORE[key]) for key in sorted(_STORE)]


def _sha(payload: object) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _load(name: str) -> dict:
    payload = json.loads((ROOT / "fixtures" / name).read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("synthetic") is not True:
        raise NotSynthetic(name)
    return payload


def pinned_sources() -> dict:
    return {
        "extracts": _load("extracts.json"),
        "register": _load("register.json"),
        "directory": _load("directory.json"),
        "controls": _load("controls.json"),
    }


def _people(directory: dict) -> list[dict]:
    rows = directory.get("people") if isinstance(directory, dict) else None
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict) and isinstance(row.get("ref"), str)]


def _names(directory: dict) -> list[str]:
    return [row["name"] for row in _people(directory) if isinstance(row.get("name"), str)]


def _owner_ref(directory: dict) -> str | None:
    owners = [
        row["ref"]
        for row in _people(directory)
        if row.get("role") == "compliance owner" and row.get("guest") is not True
    ]
    if len(owners) == 1:
        return owners[0]
    return None


def _ceiling(directory: dict, ref: object) -> str | None:
    if not isinstance(ref, str):
        return None
    for row in _people(directory):
        if row.get("ref") == ref and row.get("guest") is not True:
            clearance = row.get("clearance")
            return clearance if isinstance(clearance, str) else None
    return None


def _dated(value: object) -> dict:
    local = parse_date_token(value)
    if local["not_stated"]:
        local["experiment_68"] = {"called": False, "iso": None}
        local["disagreement"] = False
        return local
    token = value if isinstance(value, str) else ""
    neighbour = cross_check_date(token) if token else {"called": False, "iso": None}
    local["experiment_68"] = {"called": neighbour.get("called"), "iso": neighbour.get("iso")}
    disagree = bool(neighbour.get("called")) and neighbour.get("iso") != local["iso"]
    local["disagreement"] = False
    local["disagreement_kind"] = None
    if disagree and local["iso"] and neighbour.get("iso") and neighbour.get("iso") != local["iso"]:
        refused = parse_date_token("unreadable")
        refused["unparseable"] = True
        refused["ambiguous"] = True
        refused["not_stated"] = False
        refused["display"] = "unparseable"
        refused["iso"] = None
        refused["chosen"] = False
        refused["disagreement"] = True
        refused["disagreement_kind"] = "two_dates"
        refused["experiment_68"] = local["experiment_68"]
        return refused
    if disagree and local["iso"] and neighbour.get("iso") is None:
        local["disagreement_kind"] = "neighbour_unparseable"
    return local


def _applicability(scope: object, reading: dict, force: dict, profile: dict) -> str:
    if force["in_force"] is False and force["reason"] == "not_yet_in_force":
        return "not_yet_in_force"
    if force["in_force"] is False and force["reason"] in {"superseded", "effective_to_passed"}:
        return "superseded"
    if reading["qualified"]:
        return "qualified_candidate"
    if reading["denied"] and not reading["included"]:
        return "out_of_scope_candidate"
    if not reading["included"]:
        return "undecided"
    if not isinstance(scope, str) or not scope:
        return "undecided"
    value = profile.get(scope, None)
    if value is True:
        return "in_scope_candidate"
    if value is False:
        return "out_of_scope_candidate"
    return "undecided"


def _view(**kwargs: object) -> dict:
    row = {key: kwargs.get(key) for key in _VIEW_KEYS}
    controls = row.get("linked_controls") or []
    row["linked_controls"] = sorted(controls) if isinstance(controls, list) else []
    return row


def _diff(before: dict | None, after: dict) -> list[dict]:
    if before is None:
        return [
            {"field": key, "before": None, "after": after.get(key)}
            for key in _VIEW_KEYS
            if after.get(key) is not None
        ]
    rows = []
    for key in _VIEW_KEYS:
        left = before.get(key)
        right = after.get(key)
        if left == right:
            continue
        if not isinstance(left, (list, dict)) and not isinstance(right, (list, dict)):
            if (key, left, right) in _QUIET:
                continue
        rows.append({"field": key, "before": left, "after": right})
    return rows


def _material(rows: list[dict]) -> bool:
    return bool(rows)


def _differs(caller: object, pinned: object) -> bool:
    if caller is None:
        return False
    return _sha(caller) != _sha(pinned)


def _blank_result(as_of: str) -> dict:
    return {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment_id": EXPERIMENT_ID,
        "autonomy": "A1",
        "as_of": as_of,
        "outcome": "proposal",
        "human_approval": None,
        "staged": False,
        "sent": False,
        "production_written": False,
        "final_advice": False,
        "law_interpreted_as_final": False,
        "applicability_decided": False,
        "accountability_assigned_by_agent": False,
        "owner_chosen": False,
        "marked_acceptable": False,
        "instructions_followed": False,
        "coerced": False,
        "routine_processing": True,
        "note_copied": False,
        "pins_confirmed": False,
        "may_be_relied_on": False,
        "statutory_minimum_stated": False,
        "internal_minimum_months": INTERNAL_MINIMUM_MONTHS,
        "internal_minimum_source": "Pinned synthetic policy. Not a statute.",
        "dataverse": {
            "staging_table": STAGING_TABLE,
            "production_table": PRODUCTION_TABLE,
            "production_written": False,
        },
    }


def _coverage(text: str, reading: dict, controls: list[dict], below: bool | None, force: dict) -> dict:
    related = []
    covering = []
    for control in controls:
        if control.get("biased") is True or reading.get("biased"):
            continue
        verdict = addresses(control.get("text") or "", reading["affirmed"])
        if control.get("control_id") and verdict["biased"]:
            continue
        if not reading["affirmed"]:
            continue
        theme_hit = verdict["addresses"] or (
            verdict["strength"] == "must" and not verdict["qualified"] and False
        )
        if verdict["addresses"]:
            related.append(control["control_id"])
            covering.append(control["control_id"])
        elif set(reading["affirmed"]) & set(verdict["affirmed"]):
            related.append(control["control_id"])
        theme_hit = theme_hit
    if (
        reading["qualified"]
        or not reading["included"]
        or below is True
        or force["in_force"] is not True
        or force.get("dates_unparseable") is True
    ):
        return {"covered": False, "linked_controls": [], "related_controls": sorted(set(related))}
    return {
        "covered": bool(covering),
        "linked_controls": sorted(set(covering)),
        "related_controls": sorted(set(related)),
    }


def _after_from_extract(
    extract: dict,
    obligation_id: str,
    *,
    as_of,
    owner: str | None,
    controls: list[dict],
    profile: dict,
    withhold: bool,
) -> tuple[dict, dict, list[str]]:
    text = extract.get("text") if isinstance(extract.get("text"), str) else ""
    reading = theme_reading(text)
    start = _dated(extract.get("effective_from"))
    end = _dated(extract.get("effective_to"))
    review = _dated(extract.get("review_due"))
    status = extract.get("status") if isinstance(extract.get("status"), str) else ""
    force = in_force(start, end, status, as_of)
    stale = review_stale(review, as_of)
    interval = interval_months(text)
    if interval["months"] is None:
        below = None
    else:
        below = interval["months"] > INTERNAL_MINIMUM_MONTHS
    force["dates_unparseable"] = bool(review["unparseable"] or start["unparseable"] or end["unparseable"])
    if reading["denied"] and not reading["included"]:
        force = {**force, "in_force": False, "reason": "negation"}
    cover = _coverage(text, reading, controls, below, force)
    flags: list[str] = []
    if reading["qualified"]:
        flags.append("qualified")
    if reading["denied"] and not reading["included"]:
        flags.append("negation")
    if stale["stale"] is True:
        flags.append("review_stale")
    if review["unparseable"] or start["unparseable"] or end["unparseable"]:
        flags.append("unparseable_date")
    if review["ambiguous"] or start["ambiguous"] or end["ambiguous"]:
        flags.append("ambiguous_date")
    if below is True:
        flags.append("below_internal_minimum")
    if force["reason"] == "not_yet_in_force":
        flags.append("not_yet_in_force")
    if force["in_force"] is False and force["reason"] in {"superseded", "effective_to_passed"}:
        flags.append("superseded")
    if review["disagreement"] or start["disagreement"] or end["disagreement"]:
        flags.append("date_disagreement")
    shown = "not copied" if withhold else text
    record_status = "active"
    if force["in_force"] is False and force["reason"] in {"superseded", "effective_to_passed"}:
        record_status = "retired"
    elif force["reason"] == "not_yet_in_force":
        record_status = "not_yet_in_force"
    elif reading["denied"] and not reading["included"]:
        record_status = "not_an_obligation"
    review_display: object
    if review["not_stated"]:
        review_display = "not stated"
    elif review["unparseable"]:
        review_display = "unparseable"
    else:
        review_display = review["iso"]
    after = _view(
        obligation_id=obligation_id,
        source_id=extract.get("source_id"),
        provision=extract.get("provision"),
        obligation_text=shown,
        applicability=_applicability(extract.get("scope"), reading, force, profile),
        proposed_owner_ref=owner,
        review_date=review_display,
        review_stale=stale["stale"],
        linked_controls=[] if withhold else cover["linked_controls"],
        covered=False if withhold else cover["covered"],
        included=False if withhold else reading["included"],
        qualified=reading["qualified"],
        in_force=force["in_force"],
        status=record_status,
        possible_duplicate_of=None,
        below_internal_minimum=below,
    )
    meta = {
        "verbatim": shown == text and not withhold,
        "related_controls": cover["related_controls"],
        "acceptable": False,
        "final_advice": False,
        "applicability_decided": False,
        "owner_chosen": False,
        "accountability_assigned_by_agent": False,
        "coerced": False,
        "interval_months": interval["months"],
        "dates": {"effective_from": start, "effective_to": end, "review_due": review},
    }
    return after, meta, flags


def _before_from_row(row: dict) -> dict:
    return _view(
        obligation_id=row.get("obligation_id"),
        source_id=row.get("source_id"),
        provision=row.get("provision"),
        obligation_text=row.get("obligation_text"),
        applicability=row.get("applicability"),
        proposed_owner_ref=row.get("owner_ref"),
        review_date=row.get("review_date"),
        review_stale=row.get("review_stale"),
        linked_controls=row.get("linked_controls") or [],
        covered=row.get("covered"),
        included=row.get("included"),
        qualified=row.get("qualified"),
        in_force=row.get("in_force"),
        status=row.get("status"),
        possible_duplicate_of=row.get("possible_duplicate_of"),
        below_internal_minimum=row.get("below_internal_minimum"),
    )


def _after_from_row(row: dict, *, as_of, owner: str | None, controls: list[dict], withhold: bool) -> tuple[dict, dict, list[str]]:
    text = row.get("obligation_text") if isinstance(row.get("obligation_text"), str) else ""
    reading = theme_reading(text)
    review = _dated(row.get("review_date"))
    stale = review_stale(review, as_of)
    interval = interval_months(text)
    below = None if interval["months"] is None else interval["months"] > INTERNAL_MINIMUM_MONTHS
    force = {
        "in_force": True if reading["included"] and not reading["qualified"] else False,
        "reason": "row_without_extract",
    }
    if reading["denied"] and not reading["included"]:
        force = {"in_force": False, "reason": "negation"}
    cover = _coverage(text, reading, controls, below, force if reading["included"] else {"in_force": False, "reason": "negation"})
    flags: list[str] = []
    if reading["qualified"]:
        flags.append("qualified")
    if reading["denied"] and not reading["included"]:
        flags.append("negation")
    if stale["stale"] is True:
        flags.append("review_stale")
    if review["unparseable"]:
        flags.append("unparseable_date")
    if below is True:
        flags.append("below_internal_minimum")
    status = "active"
    if reading["denied"] and not reading["included"]:
        status = "not_an_obligation"
    elif reading["qualified"]:
        status = "active"
    shown = "not copied" if withhold else text
    stored_covered = row.get("covered") is True
    covered = False if withhold or reading["qualified"] or not reading["included"] or below is True else cover["covered"]
    if stored_covered and covered is False:
        flags.append("coverage_claim_rejected")
    claimed = row.get("linked_controls") if isinstance(row.get("linked_controls"), list) else []
    if stored_covered and any(item not in cover["linked_controls"] for item in claimed):
        if "coverage_claim_rejected" not in flags:
            flags.append("coverage_claim_rejected")
    after = _view(
        obligation_id=row.get("obligation_id"),
        source_id=row.get("source_id"),
        provision=row.get("provision"),
        obligation_text=shown,
        applicability="out_of_scope_candidate" if status == "not_an_obligation" else (
            "qualified_candidate" if reading["qualified"] else row.get("applicability")
        ),
        proposed_owner_ref=owner,
        review_date=review["display"] if not review["not_stated"] else row.get("review_date"),
        review_stale=stale["stale"],
        linked_controls=[] if not covered else cover["linked_controls"],
        covered=covered,
        included=False if withhold else reading["included"],
        qualified=reading["qualified"],
        in_force=bool(reading["included"] and not reading["qualified"]),
        status=status,
        possible_duplicate_of=None,
        below_internal_minimum=below,
    )
    meta = {"verbatim": not withhold, "related_controls": cover["related_controls"], "acceptable": False, "dates": {"review_due": review}}
    return after, meta, flags


def _change(action: str, before: dict | None, after: dict, flags: list[str], meta: dict) -> dict:
    dates = meta.get("dates")
    payload = {
        "action": action,
        "obligation_id": after["obligation_id"],
        "before": before,
        "after": after,
        "dates": dates,
    }
    rows = _diff(before, after)
    return {
        "change_id": f"CHG-{after['obligation_id']}",
        "action": action,
        "obligation_id": after["obligation_id"],
        "source_id": after.get("source_id"),
        "provision": after.get("provision"),
        "before": before,
        "after": after,
        "dates": dates,
        "diff": rows,
        "flags": sorted(set(flags)),
        "change_hash": _sha(payload),
        "acceptable": False,
        "final_advice": False,
        "accountability_assigned_by_agent": False,
        "related_controls": meta.get("related_controls") or [],
        "verbatim": meta.get("verbatim"),
        "stageable": True,
    }


def propose_register(request: dict, as_of: str) -> dict:
    if not isinstance(request, dict) or request.get("synthetic") is not True:
        raise NotSynthetic("request")
    questioned = parse_as_of(as_of)
    pinned = pinned_sources()
    extracts = pinned["extracts"]
    register = pinned["register"]
    directory = pinned["directory"]
    controls_doc = pinned["controls"]
    profile = extracts.get("firm_profile") if isinstance(extracts.get("firm_profile"), dict) else {}
    note = request.get("note") if isinstance(request.get("note"), str) else ""
    pack = "\n".join(
        part
        for part in (
            note,
            request.get("cover") if isinstance(request.get("cover"), str) else "",
        )
        if part
    )
    result = _blank_result(questioned.isoformat())
    cues = cue_categories(pack)
    result["cues"] = {"categories": cues, "copied": False, "routed": bool(cues)}
    result["prompt_injection"] = {
        "signals": injection_signals(pack),
        "followed": False,
    }
    result["self_declared_ignored"] = self_declared(pack)
    result["caller_sources"] = {
        "register_differs": _differs(request.get("register"), register),
        "directory_differs": _differs(request.get("directory"), directory),
        "controls_differs": _differs(request.get("controls"), controls_doc),
        "used_caller": False,
    }
    names = _names(directory)
    _masked, mask_info = mask_text(pack, names)
    mask_info["note_copied"] = False
    result["mask"] = mask_info
    result["people_count"] = people_mentions(pack)
    result["people_count"]["directory_count_published"] = None
    result["people_count"]["directory_suppressed"] = len(_people(directory)) < 5
    meta_marks, meta_bad = metadata_markings(request.get("marking"))
    content_marks = content_markings(pack)
    applied = higher_marking(meta_marks + content_marks)
    held, hold_bad = legal_hold(request.get("legal_hold"), pack)
    labels, retention_bad = retention_labels(request.get("retention"), pack)
    ceiling = _ceiling(directory, request.get("caller_ref"))
    withhold = above_ceiling(applied, ceiling)
    result["marking"] = {
        "metadata": meta_marks,
        "content": content_marks,
        "applied": applied,
        "metadata_unparseable": meta_bad,
        "above_clearance": withhold,
        "clearance_from_directory": ceiling,
        "self_declared_clearance_ignored": True,
    }
    result["legal_hold"] = {"held": held, "kept": True, "unparseable": hold_bad}
    result["retention"] = {"labels": labels, "kept": True, "unparseable": retention_bad, "dropped": False}
    result["context_pins"] = context_pins()
    owner = _owner_ref(directory)
    result["proposed_owner_ref"] = owner
    result["proposed_owner_role"] = "compliance owner" if owner else None
    result["owner_name_copied"] = False

    sentences: list[str] = []
    files = []
    for extract in extracts.get("extracts") or []:
        if not isinstance(extract, dict):
            continue
        text = extract.get("text") if isinstance(extract.get("text"), str) else ""
        sentences.append(text)
        document_date = extract.get("effective_from")
        if not isinstance(document_date, str) or len(document_date) != 10:
            document_date = None
        files.append(
            {
                "file_id": str(extract.get("source_id") or "extract"),
                "filename": f"{extract.get('source_id')}.txt",
                "media_type": "text/plain",
                "content": text,
                "document_date": document_date,
            }
        )
    for control in controls_doc.get("controls") or []:
        if isinstance(control, dict) and isinstance(control.get("text"), str):
            sentences.append(control["text"])
    qualified_must = 0
    neighbour_called = False
    for sentence in sentences:
        reading = experiment_69_reading(sentence)
        neighbour_called = neighbour_called or bool(reading.get("called"))
        if reading.get("qualified") and reading.get("strength") == "must":
            qualified_must += 1
    try:
        intake = intake_extracts(files, as_of=questioned)
    except Exception as exc:  # neighbour contract drift is a flag, not a guess
        intake = {"called": False, "error": type(exc).__name__, "files_confirmed": None, "purpose_confirmed": None}
    try:
        redaction = redact_note(note, rules_as_of=questioned)
    except Exception as exc:
        redaction = {"called": False, "error": type(exc).__name__, "output_is_anonymised": None, "note_copied": False}
    result["reused"] = {
        "experiment_68": "Date tokens are cross-checked. A second calendar date is not chosen.",
        "experiment_69": {
            "called": neighbour_called,
            "qualified_must_not_treated_as_support": qualified_must,
            "note": (
                "Experiment 69 assess_sentence can set support true on a qualified "
                "must. This starter sets supports true only when addresses() does."
            ),
        },
        "experiment_12": intake,
        "experiment_08": redaction,
    }
    if intake.get("files_confirmed") is not False and intake.get("called") is True:
        raise RegisterForbidden("Experiment 12 confirmed a file. This starter will not use that result.")
    if redaction.get("output_is_anonymised") not in {False, None}:
        raise RegisterForbidden("Experiment 08 reported anonymised output.")

    biased_ids = [
        row.get("control_id")
        for row in controls_doc.get("controls") or []
        if isinstance(row, dict) and row.get("biased") is True
    ]
    result["biased_controls"] = [item for item in biased_ids if item]
    result["biased_controls_applied"] = False

    if cues:
        result["outcome"] = "route_to_human"
        result["routine_processing"] = False
        result["changes"] = []
        result["unchanged"] = []
        result["excluded_readings"] = []
        result["proposal_hash"] = _sha({"as_of": result["as_of"], "outcome": "route_to_human", "changes": []})
        result["required_acknowledgements"] = ["pins_seen", "route_seen"]
        result["route_hash"] = _sha({"categories": cues, "as_of": result["as_of"]})
        return result

    by_source = {}
    for row in register.get("obligations") or []:
        if isinstance(row, dict) and isinstance(row.get("source_id"), str):
            by_source[row["source_id"]] = row
    controls = [row for row in controls_doc.get("controls") or [] if isinstance(row, dict)]
    prepared: dict[str, dict] = {}
    excluded = []
    for extract in extracts.get("extracts") or []:
        if not isinstance(extract, dict):
            continue
        source_id = extract.get("source_id")
        existing = by_source.get(source_id)
        obligation_id = existing.get("obligation_id") if existing else f"OBL-{source_id}"
        after, meta, flags = _after_from_extract(
            extract,
            obligation_id,
            as_of=questioned,
            owner=owner,
            controls=controls,
            profile=profile,
            withhold=withhold,
        )
        if existing is None and after["status"] == "not_an_obligation":
            excluded.append(
                {
                    "source_id": source_id,
                    "provision": extract.get("provision"),
                    "included": False,
                    "reason": "negation",
                    "quote_copied": False,
                }
            )
            continue
        if existing is None and after["status"] == "retired":
            excluded.append(
                {
                    "source_id": source_id,
                    "provision": extract.get("provision"),
                    "included": False,
                    "reason": "superseded_not_added",
                    "quote_copied": False,
                }
            )
            continue
        stored_covered = bool(existing and existing.get("covered") is True)
        claimed = existing.get("linked_controls") if existing and isinstance(existing.get("linked_controls"), list) else []
        if stored_covered and after["covered"] is False:
            flags.append("coverage_claim_rejected")
        if claimed and any(item not in after["linked_controls"] for item in claimed):
            if stored_covered or after["covered"] is False:
                if "coverage_claim_rejected" not in flags and stored_covered:
                    flags.append("coverage_claim_rejected")
        prepared[obligation_id] = {
            "before": _before_from_row(existing) if existing else None,
            "after": after,
            "flags": flags,
            "meta": meta,
            "existed": existing is not None,
        }
    seen = set(prepared)
    for row in register.get("obligations") or []:
        if not isinstance(row, dict):
            continue
        obligation_id = row.get("obligation_id")
        if obligation_id in seen:
            continue
        after, meta, flags = _after_from_row(
            row,
            as_of=questioned,
            owner=owner,
            controls=controls,
            withhold=withhold,
        )
        prepared[obligation_id] = {
            "before": _before_from_row(row),
            "after": after,
            "flags": flags,
            "meta": meta,
            "existed": True,
        }

    ordered = sorted(prepared)
    for later in ordered:
        later_text = prepared[later]["after"]["obligation_text"]
        if later_text == "not copied":
            continue
        for earlier in ordered:
            if earlier >= later:
                break
            earlier_text = prepared[earlier]["after"]["obligation_text"]
            if earlier_text == "not copied":
                continue
            kind = relation(earlier_text, later_text)
            if kind in {"exact", "near", "qualified_near"}:
                prepared[later]["after"]["possible_duplicate_of"] = earlier
                prepared[later]["flags"].append("possible_duplicate")
                prepared[later]["meta"]["duplicate_relation"] = kind
                break

    changes = []
    unchanged = []
    for obligation_id in ordered:
        item = prepared[obligation_id]
        before = item["before"]
        after = item["after"]
        flags = sorted(set(item["flags"]))
        if after["status"] == "retired":
            action = "retired"
        elif before is None:
            action = "new"
        else:
            action = "changed"
        if action == "changed" and not _material(_diff(before, after)):
            unchanged.append(obligation_id)
            continue
        if action == "new" and after["status"] == "not_an_obligation":
            continue
        changes.append(_change(action, before, after, flags, item["meta"]))
    result["changes"] = changes
    result["unchanged"] = unchanged
    result["excluded_readings"] = excluded
    result["proposal_hash"] = _sha(
        {
            "as_of": result["as_of"],
            "outcome": "proposal",
            "caller_sources_differ": any(result["caller_sources"][key] for key in (
                "register_differs",
                "directory_differs",
                "controls_differs",
            )),
            "changes": [
                {"change_id": change["change_id"], "change_hash": change["change_hash"], "action": change["action"]}
                for change in changes
            ],
        }
    )
    acks = ["pins_seen"]
    if any(result["caller_sources"][key] for key in ("register_differs", "directory_differs", "controls_differs")):
        acks.append("sources_seen")
    if any(change["flags"] for change in changes) or result["biased_controls"]:
        acks.append("flags_seen")
    result["required_acknowledgements"] = acks
    return result


def _blocked(reason: str) -> dict:
    return {
        "staged": False,
        "human_approval": None,
        "sent": False,
        "production_written": False,
        "final_advice": False,
        "law_interpreted_as_final": False,
        "accountability_assigned_by_agent": False,
        "owner_chosen": False,
        "blocked_reason": reason,
        "table": STAGING_TABLE,
    }


def _approver(ref: object) -> dict | None:
    if not isinstance(ref, str):
        return None
    for row in _people(pinned_sources()["directory"]):
        if row.get("ref") == ref:
            return row
    return None


def stage_approved_change(proposal: dict, approval: object) -> dict:
    """Write one change to the synthetic staging register. Production stays untouched."""

    if not isinstance(proposal, dict) or proposal.get("label") != LABEL:
        return _blocked("not_a_proposal")
    if proposal.get("outcome") == "route_to_human":
        return _blocked("route_not_staged")
    if not isinstance(approval, dict):
        return _blocked("approval_missing")
    if approval.get("decision") != "approve":
        return _blocked("decision")
    person = _approver(approval.get("approver_ref"))
    if person is None or person.get("role") != "compliance owner" or person.get("guest") is True:
        return _blocked("approver")
    change_id = approval.get("item")
    change = next((row for row in proposal.get("changes") or [] if row.get("change_id") == change_id), None)
    if change is None:
        return _blocked("change_not_in_proposal")
    payload = {
        "action": change.get("action"),
        "obligation_id": change.get("obligation_id"),
        "before": change.get("before"),
        "after": change.get("after"),
        "dates": change.get("dates"),
    }
    recomputed = _sha(payload)
    if approval.get("change_hash") != recomputed or change.get("change_hash") != recomputed:
        return _blocked("change_hash_mismatch")
    expected_proposal = _sha(
        {
            "as_of": proposal.get("as_of"),
            "outcome": proposal.get("outcome"),
            "caller_sources_differ": any(
                (proposal.get("caller_sources") or {}).get(key)
                for key in ("register_differs", "directory_differs", "controls_differs")
            ),
            "changes": [
                {
                    "change_id": row.get("change_id"),
                    "change_hash": row.get("change_hash"),
                    "action": row.get("action"),
                }
                for row in proposal.get("changes") or []
            ],
        }
    )
    if approval.get("proposal_hash") != expected_proposal or proposal.get("proposal_hash") != expected_proposal:
        return _blocked("proposal_hash_mismatch")
    for ack in proposal.get("required_acknowledgements") or []:
        if ack == "route_seen":
            continue
        if approval.get(ack) is not True:
            return _blocked(ack)
    if change_id in _STORE and _STORE[change_id]["change_hash"] != recomputed:
        return _blocked("staging_conflict")
    row = {
        "table": STAGING_TABLE,
        "production_table": PRODUCTION_TABLE,
        "production_written": False,
        "sent": False,
        "final_advice": False,
        "law_interpreted_as_final": False,
        "accountability_assigned_by_agent": False,
        "owner_set_by": "named compliance owner approved this change",
        "owner_chosen_by_agent": False,
        "approver_ref": person["ref"],
        "approver_role": person["role"],
        "change_id": change_id,
        "change_hash": recomputed,
        "proposal_hash": expected_proposal,
        "record": deepcopy(change.get("after")),
        "already_staged": change_id in _STORE,
    }
    _STORE[change_id] = row
    return {
        "staged": True,
        "already_staged": row["already_staged"],
        "human_approval": {
            "approver_ref": person["ref"],
            "approver_role": person["role"],
            "item": change_id,
            "decision": "approve",
            "change_hash": recomputed,
            "proposal_hash": expected_proposal,
        },
        "sent": False,
        "production_written": False,
        "final_advice": False,
        "law_interpreted_as_final": False,
        "accountability_assigned_by_agent": False,
        "owner_chosen": False,
        "blocked_reason": None,
        "table": STAGING_TABLE,
        "record": row["record"],
    }


def record_route_seen(proposal: dict, approval: object) -> dict:
    if not isinstance(proposal, dict) or proposal.get("outcome") != "route_to_human":
        return _blocked("not_a_route")
    if not isinstance(approval, dict):
        return _blocked("approval_missing")
    if approval.get("decision") != "seen" or approval.get("item") != "route-seen":
        return _blocked("decision")
    person = _approver(approval.get("approver_ref"))
    if person is None or person.get("role") != "compliance owner" or person.get("guest") is True:
        return _blocked("approver")
    if approval.get("route_hash") != proposal.get("route_hash"):
        return _blocked("route_hash_mismatch")
    if approval.get("pins_seen") is not True:
        return _blocked("pins_seen")
    return {
        "staged": False,
        "human_approval": {
            "approver_ref": person["ref"],
            "item": "route-seen",
            "decision": "seen",
            "route_hash": proposal.get("route_hash"),
        },
        "sent": False,
        "production_written": False,
        "routine_processing": False,
        "blocked_reason": None,
    }


def _main() -> int:
    parser = argparse.ArgumentParser(description="Propose obligation register changes.")
    parser.add_argument("--request", required=True, type=Path)
    parser.add_argument("--as-of", required=True)
    args = parser.parse_args()
    try:
        request = json.loads(args.request.read_text(encoding="utf-8"))
        result = propose_register(request, args.as_of)
    except (OSError, json.JSONDecodeError, NotSynthetic, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    json.dump(result, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
