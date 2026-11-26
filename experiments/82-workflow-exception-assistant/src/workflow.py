"""Diagnose a synthetic workflow run. Do not retry, cancel, edit, or re-run it.

The named process owner chooses retry, route, or cancel on a separate object
bound to the agent-held copy of the proposal and its hash. The agent does
not carry out that choice.

Autonomy is A1. Error text, a caller-supplied register, and an approval
marker inside a payload are not authoritative. This is not Experiment 17.
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
    from cues import (
        carve_out_affirmed,
        category_hit,
        role_claim,
        sensitive_categories,
    )
    from dates import as_date, calendar_hours, parse_date, parse_timestamp, with_question_date
    from marking import (
        RANK,
        above_ceiling,
        content_markings,
        higher_marking,
        legal_hold,
        metadata_markings,
        retention_labels,
    )
    from mask import add_counts, empty_mask, mask_text, people_fields, suppress_small_counts
    from negate import sentences
    from siblings import identifier_counts
    from sources import uk_context
else:
    from .cues import (
        carve_out_affirmed,
        category_hit,
        role_claim,
        sensitive_categories,
    )
    from .dates import as_date, calendar_hours, parse_date, parse_timestamp, with_question_date
    from .marking import (
        RANK,
        above_ceiling,
        content_markings,
        higher_marking,
        legal_hold,
        metadata_markings,
        retention_labels,
    )
    from .mask import add_counts, empty_mask, mask_text, people_fields, suppress_small_counts
    from .negate import sentences
    from .siblings import identifier_counts
    from .sources import uk_context

LABEL = (
    "DRAFT WORKFLOW EXCEPTION READING FOR THE NAMED PROCESS OWNER. "
    "THE AGENT DOES NOT RETRY, CANCEL, EDIT A RECORD, OR RE-RUN A FLOW."
)
CATALOGUE_ID = "O009"
EXPERIMENT_ID = "exp-82-workflow-exception-assistant"
ROOT = Path(__file__).resolve().parents[1]
DIAGNOSIS_ID = re.compile(r"^DX-\d{4}$")
REF_ID = re.compile(r"^[A-Z]+-\d{4}$")
RETRYABLE = frozenset({"transient_connector_throttling", "timeout"})
RUN_STATUS = frozenset({"Failed", "Running", "Succeeded", "Cancelled", "TimedOut"})
STEP_STATUS = frozenset({"Failed", "Running", "Succeeded", "Cancelled", "TimedOut", "Skipped"})
CAUSE = {
    "transient_connector_throttling": "The pinned taxonomy maps the cited code to a transient connector or throttling failure.",
    "authentication_or_expired_connection": "The pinned taxonomy maps the cited code to authentication or an expired connection.",
    "data_validation": "The pinned taxonomy maps the cited code to a data-validation failure.",
    "missing_reference_data": "The pinned taxonomy maps the cited code to missing reference data.",
    "permissions": "The pinned taxonomy maps the cited code to a permissions failure.",
    "business_rule_breach": "The pinned taxonomy maps the cited code to a business-rule breach.",
    "duplicate_submission": "The pinned taxonomy maps the cited code to a duplicate submission.",
    "timeout": "The pinned taxonomy maps the cited code to a timeout, or the run is still running past the pinned stuck threshold.",
    "conflicting_codes": "The cited codes do not map to one class. Neither code was chosen.",
    "unclassified": "The pinned taxonomy has no class for the cited code, or there is no structured code.",
}
_HELD: dict[str, dict] = {}
_PROHIBITED = (
    "human_approval",
    "owner_decision_recorded",
    "chosen_action",
    "approved",
    "retried",
    "cancelled",
    "auto_retried",
    "executed",
    "records_edited",
    "flow_rerun",
    "route_seen",
    "retry_safe",
    "role",
    "clearance",
    "exception_class",
)
_NESTED_APPROVAL = frozenset({
    "human_approval",
    "owner_decision_recorded",
    "approved",
    "retried",
    "auto_retried",
    "route_seen",
    "executed",
})


class WorkflowForbidden(RuntimeError):
    """The agent does not retry, cancel, edit a record, or re-run a flow."""

    __test__ = False


class NotSynthetic(ValueError):
    """The request was not marked synthetic."""


def retry_run(*_args, **_kwargs) -> None:
    raise WorkflowForbidden("The agent does not retry a run.")


def cancel_run(*_args, **_kwargs) -> None:
    raise WorkflowForbidden("The agent does not cancel a run.")


def edit_record(*_args, **_kwargs) -> None:
    raise WorkflowForbidden("The agent does not edit a record.")


def rerun_flow(*_args, **_kwargs) -> None:
    raise WorkflowForbidden("The agent does not re-run a flow.")


def triage_invoice(*_args, **_kwargs) -> None:
    raise WorkflowForbidden("The agent does not triage an invoice. That is Experiment 17.")


def reset_held() -> None:
    _HELD.clear()


def held_record(diagnosis_id: object) -> dict | None:
    if not isinstance(diagnosis_id, str):
        return None
    row = _HELD.get(diagnosis_id)
    if not isinstance(row, dict):
        return None
    return {"diagnosis_id": diagnosis_id, "content_hash": row.get("content_hash")}


def pinned_directory() -> dict:
    return json.loads((ROOT / "fixtures" / "directory.json").read_text(encoding="utf-8"))


def pinned_register() -> dict:
    return json.loads((ROOT / "fixtures" / "process_register.json").read_text(encoding="utf-8"))


def pinned_taxonomy() -> dict:
    raw = json.loads((ROOT / "fixtures" / "error_taxonomy.json").read_text(encoding="utf-8"))
    codes = raw.get("codes") if isinstance(raw, dict) else None
    if not isinstance(codes, dict):
        return {}
    return {str(key): value for key, value in codes.items() if isinstance(value, str)}


def _digest(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _projection(result: dict) -> dict:
    return {
        "diagnosis_id": result.get("diagnosis_id"),
        "process_id": result.get("process_id"),
        "owner_ref": result.get("owner_ref"),
        "deputy_refs": result.get("deputy_refs"),
        "as_of": result.get("as_of"),
        "outcome": result.get("outcome"),
        "groups": result.get("groups"),
        "options": result.get("options"),
        "retry_safe": result.get("retry_safe") is True,
        "partial_completion": result.get("partial_completion") is True,
        "partial_side_effects": result.get("partial_side_effects"),
        "duplicate_risks": result.get("duplicate_risks"),
        "marking": result.get("marking"),
        "legal_hold": result.get("legal_hold") is True,
        "legal_hold_unparseable": result.get("legal_hold_unparseable") is True,
        "retention": result.get("retention"),
        "retention_unparseable": result.get("retention_unparseable") is True,
        "conflicting_retention": result.get("conflicting_retention") is True,
        "prompt_injection": result.get("prompt_injection"),
        "suppression": result.get("suppression"),
        "required_acknowledgements": result.get("required_acknowledgements"),
        "route_seen": result.get("route_seen") is True,
        "distress": result.get("distress"),
        "leading_criteria": result.get("leading_criteria") is True,
        "register_check": result.get("register_check"),
        "taxonomy_check": result.get("taxonomy_check"),
        "dates": result.get("dates"),
        "stale": result.get("stale") is True,
        "future_timestamp": result.get("future_timestamp") is True,
        "unparseable_timestamp": result.get("unparseable_timestamp") is True,
        "owner_conflict": result.get("owner_conflict") is True,
        "carve_out": result.get("carve_out") is True,
        "conflicting_values": result.get("conflicting_values") is True,
        "excerpts": result.get("excerpts"),
        "masking": result.get("masking"),
        "uk_identifiers": result.get("uk_identifiers"),
        "owner_decision_recorded": result.get("owner_decision_recorded") is True,
        "chosen_action": result.get("chosen_action"),
        "error_text_used_for_class": False,
    }


def _hash(result: dict) -> str:
    return _digest(_projection(result))


def _force(result: dict) -> None:
    result["auto_retried"] = False
    result["retried"] = False
    result["cancelled"] = False
    result["records_edited"] = False
    result["flow_rerun"] = False
    result["executed"] = False
    result["instructions_followed"] = False
    result["approval_marker_trusted"] = False
    result["role_in_text_trusted"] = False
    result["clearance_in_text_trusted"] = False
    result["caller_register_applied"] = False
    result["caller_directory_applied"] = False
    result["caller_taxonomy_applied"] = False
    result["error_text_used_for_class"] = False
    result["coerced"] = False
    result["described_as_anonymised"] = False
    result["may_be_relied_on"] = False
    result["production_written"] = False
    result["experiment_17_called"] = False
    injection = result.get("prompt_injection")
    if isinstance(injection, dict):
        injection["followed"] = False
    register = result.get("register_check")
    if isinstance(register, dict):
        register["applied"] = False
    taxonomy = result.get("taxonomy_check")
    if isinstance(taxonomy, dict):
        taxonomy["applied"] = False


def _strip(payload: dict) -> tuple[dict, list[str]]:
    working = dict(payload)
    ignored = []
    for key in _PROHIBITED:
        if key in working:
            ignored.append(key)
            working.pop(key, None)
    return working, ignored


def _question_date(value: object) -> date:
    if not isinstance(value, str):
        raise ValueError("as_of must be a calendar date.")
    reading = parse_date(value)
    parsed = as_date(reading)
    if parsed is None or reading.get("ambiguous") or reading.get("unparseable"):
        raise ValueError("as_of must be an unambiguous calendar date.")
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


def _process(register: dict, process_id: object) -> dict | None:
    rows = register.get("processes") if isinstance(register, dict) else None
    if not isinstance(rows, list) or not isinstance(process_id, str):
        return None
    for row in rows:
        if isinstance(row, dict) and row.get("process_id") == process_id:
            return row
    return None


def _steps_by_id(process: dict | None) -> dict[str, dict]:
    if not isinstance(process, dict):
        return {}
    found = {}
    for step in process.get("steps") or []:
        if isinstance(step, dict) and isinstance(step.get("step_id"), str):
            found[step["step_id"]] = step
    return found


def _store(result: dict) -> None:
    diagnosis_id = result.get("diagnosis_id")
    if not isinstance(diagnosis_id, str):
        return
    projected = deepcopy(_projection(result))
    result["content_hash"] = _digest(projected)
    _HELD[diagnosis_id] = {"content_hash": result["content_hash"], "projection": projected}


def _remember(result: dict) -> None:
    """Hash the returned object. Replace the held copy only when the step succeeded."""

    diagnosis_id = result.get("diagnosis_id")
    projected = deepcopy(_projection(result))
    result["content_hash"] = _digest(projected)
    if result.get("blocked_reason") or not isinstance(diagnosis_id, str):
        return
    _HELD[diagnosis_id] = {"content_hash": result["content_hash"], "projection": projected}


def _walk_strings(value: object):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from _walk_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk_strings(item)


def _nested_approval(value: object, depth: int = 0) -> bool:
    if isinstance(value, dict):
        if depth > 0:
            for key in _NESTED_APPROVAL:
                if key in value and value.get(key) not in (None, False, "", [], {}):
                    return True
        for item in value.values():
            if _nested_approval(item, depth + 1):
                return True
    elif isinstance(value, list):
        for item in value:
            if _nested_approval(item, depth + 1):
                return True
    return False


def _codes(raw: object) -> tuple[list[str], bool]:
    if raw is None:
        return [], False
    if isinstance(raw, bool) or isinstance(raw, float):
        return [], True
    if isinstance(raw, (str, int)):
        raw = [raw]
    if not isinstance(raw, list):
        return [], True
    codes: list[str] = []
    bad = False
    for item in raw:
        if isinstance(item, bool) or isinstance(item, float):
            bad = True
            continue
        if isinstance(item, int):
            codes.append(str(item))
        elif isinstance(item, str) and item.strip():
            codes.append(item.strip())
        elif item not in (None, ""):
            bad = True
    return codes, bad


def _class_from_codes(codes: list[str], taxonomy: dict) -> dict:
    mapped: list[tuple[str, str]] = []
    unknown: list[str] = []
    for code in codes:
        kind = taxonomy.get(code)
        if isinstance(kind, str):
            mapped.append((code, kind))
        else:
            unknown.append(code)
    classes = {kind for _, kind in mapped}
    if unknown and mapped:
        return {
            "exception_class": "conflicting_codes",
            "reason": "known_and_unknown_codes",
            "error_codes": [code for code, _kind in mapped] + unknown,
            "error_text_used": False,
        }
    if len(classes) > 1:
        return {
            "exception_class": "conflicting_codes",
            "reason": "codes_disagree",
            "error_codes": [code for code, _kind in mapped],
            "error_text_used": False,
        }
    if len(classes) == 1:
        return {
            "exception_class": next(iter(classes)),
            "reason": "taxonomy_code",
            "error_codes": [code for code, _kind in mapped],
            "error_text_used": False,
        }
    if unknown:
        return {
            "exception_class": "unclassified",
            "reason": "code_not_on_taxonomy",
            "error_codes": unknown,
            "error_text_used": False,
        }
    return {
        "exception_class": None,
        "reason": "no_code",
        "error_codes": [],
        "error_text_used": False,
    }


def _register_diff(caller: object, pinned_process: dict | None) -> dict:
    if caller is None:
        return {"supplied": False, "differs": False, "applied": False, "fields": []}
    fields: list[str] = []
    caller_process = None
    if isinstance(caller, dict) and isinstance(caller.get("processes"), list):
        wanted = pinned_process.get("process_id") if isinstance(pinned_process, dict) else None
        for row in caller["processes"]:
            if isinstance(row, dict) and row.get("process_id") == wanted:
                caller_process = row
                break
        if caller_process is None:
            fields.append("process_missing")
    elif isinstance(caller, dict):
        caller_process = caller
    else:
        fields.append("not_an_object")
    if isinstance(caller_process, dict) and isinstance(pinned_process, dict):
        for key in ("owner_ref", "stale_after_days", "stuck_after_hours"):
            if caller_process.get(key) != pinned_process.get(key):
                fields.append(key)
        pinned_steps = _steps_by_id(pinned_process)
        caller_steps = caller_process.get("steps")
        seen: set[object] = set()
        if not isinstance(caller_steps, list):
            fields.append("steps")
        else:
            for step in caller_steps:
                if not isinstance(step, dict):
                    fields.append("steps")
                    continue
                sid = step.get("step_id")
                seen.add(sid)
                pinned_step = pinned_steps.get(sid) if isinstance(sid, str) else None
                if pinned_step is None:
                    fields.append("extra_step")
                    continue
                for key in ("idempotent", "side_effects", "qualifier"):
                    if step.get(key) != pinned_step.get(key):
                        fields.append(f"step.{key}")
            for sid in pinned_steps:
                if sid not in seen:
                    fields.append("missing_step")
    elif pinned_process is None:
        fields.append("process_not_pinned")
    return {"supplied": True, "differs": bool(fields), "applied": False, "fields": fields}


def _taxonomy_diff(caller: object, taxonomy: dict) -> dict:
    if caller is None:
        return {"supplied": False, "differs": False, "applied": False}
    if not isinstance(caller, dict):
        return {"supplied": True, "differs": True, "applied": False}
    caller_codes = caller.get("codes") if isinstance(caller.get("codes"), dict) else caller
    if not isinstance(caller_codes, dict):
        return {"supplied": True, "differs": True, "applied": False}
    return {"supplied": True, "differs": caller_codes != taxonomy, "applied": False}


def _stamp(value: object, question: date | None, compare: bool) -> dict:
    reading = parse_timestamp(value)
    if compare and question is not None:
        reading = with_question_date(reading, question)
    else:
        reading = dict(reading)
        reading["future"] = False
        reading["coerced"] = False
    reading["compared"] = compare and question is not None
    return reading


def _latest_date(readings: list[dict]) -> date | None:
    found: list[date] = []
    for reading in readings:
        if reading.get("unparseable") or reading.get("ambiguous"):
            continue
        parsed = as_date(reading)
        if parsed is not None:
            found.append(parsed)
    if not found:
        return None
    return max(found)


def _excerpt(text: object, *, withhold: bool) -> tuple[str, dict, bool]:
    if not isinstance(text, str) or not text:
        report = empty_mask()
        return "", report, False
    _masked, report = mask_text(text)
    suppressed, _sup = suppress_small_counts(_masked)
    if withhold or sensitive_categories(text):
        report["masked_text_included"] = False
        report["values_copied"] = False
        return "[withheld]", report, True
    kept = []
    for sentence in sentences(suppressed):
        if category_hit(sentence, "embedded_instruction") or category_hit(sentence, "forged_approval"):
            kept.append("[instruction withheld]")
        else:
            kept.append(sentence)
    report["masked_text_included"] = True
    report["values_copied"] = False
    report["values_stored"] = False
    report["described_as_anonymised"] = False
    return " ".join(kept), report, False


def _apply_identifiers(text: str, on: date) -> tuple[str, dict]:
    if not text:
        return text, {
            "called": False,
            "count": 0,
            "types": [],
            "output_is_anonymised": False,
            "values_stored": False,
            "redacted_text_copied": False,
        }
    counted = identifier_counts(text, on=on)
    masked = counted.pop("masked")
    counted["redacted_text_copied"] = False
    return masked, counted


def _side(step: dict | None) -> str:
    if not isinstance(step, dict):
        return "unknown"
    side = step.get("side_effects")
    if side in {"none", "payment", "email", "record_write"}:
        return side
    return "unknown"


def _retry_safe_step(
    pinned_step: dict | None,
    exception_class: str | None,
    *,
    partial_side: bool,
    carve: bool,
    time_bad: bool,
    conflict: bool,
) -> bool:
    if conflict or carve or partial_side or time_bad:
        return False
    if exception_class not in RETRYABLE:
        return False
    if not isinstance(pinned_step, dict):
        return False
    if pinned_step.get("idempotent") is not True:
        return False
    if _side(pinned_step) != "none":
        return False
    if isinstance(pinned_step.get("qualifier"), str) and pinned_step.get("qualifier").strip():
        return False
    return True


def _risks_for(
    *,
    safe: bool,
    side_effects: set[str],
    partial: bool,
    carve: bool,
    time_bad: bool,
    conflict: bool,
    unknown_process: bool,
    not_idempotent: bool,
    qualifier: bool,
    wrong_class: bool,
) -> list[str]:
    risks = []
    if "payment" in side_effects:
        risks.append("A retry may create a duplicate payment.")
    if "email" in side_effects:
        risks.append("A retry may send a duplicate email.")
    if "record_write" in side_effects:
        risks.append("A retry may write the record again.")
    if partial:
        risks.append("The run is only partly complete.")
    if qualifier:
        risks.append("The pinned step has a qualifier, so it is not treated as safe to retry.")
    elif carve:
        risks.append("A qualification in the text means the step is not treated as safe to retry.")
    if not_idempotent:
        risks.append("The pinned step is not idempotent.")
    if wrong_class:
        risks.append("The failure is not a transient connector failure or a timeout.")
    if time_bad:
        risks.append("A timestamp could not be read, is ambiguous, is in the future, or the run is stale.")
    if conflict:
        risks.append("The error codes conflict. Neither code was chosen.")
    if unknown_process:
        risks.append("The process is not on the pinned register.")
    if safe and not risks:
        risks.append("The pinned step is idempotent and has no side effect. The owner still chooses. The agent does not retry.")
    return risks


def diagnose(request: dict, *, as_of: str, directory: dict | None = None) -> dict:
    """Return a draft reading. Nothing is retried, cancelled, edited, or re-run."""

    if not isinstance(request, dict):
        raise TypeError("request must be an object.")
    if request.get("synthetic") is not True:
        raise NotSynthetic("The request was not marked synthetic.")
    question = _question_date(as_of)
    stripped, ignored = _strip(request)
    register = pinned_register()
    taxonomy = pinned_taxonomy()
    pinned_people = pinned_directory()
    _ = directory  # a directory argument is not the pinned directory
    process_id = stripped.get("process_id")
    process = _process(register, process_id)
    steps = _steps_by_id(process)
    caller_register = _register_diff(stripped.get("caller_register"), process)
    caller_taxonomy = _taxonomy_diff(stripped.get("caller_taxonomy"), taxonomy)
    caller_directory_supplied = "directory" in stripped or "caller_directory" in stripped

    payload_date = stripped.get("question_date", None)
    question_unparseable = False
    question_conflict = False
    compare_times = True
    if "question_date" in stripped:
        reading = parse_date(payload_date)
        if reading.get("unparseable") or reading.get("ambiguous") or as_date(reading) is None:
            question_unparseable = True
            compare_times = False
        elif as_date(reading) != question:
            question_conflict = True
            compare_times = False

    texts = list(_walk_strings(stripped))
    blob = "\n".join(texts)
    categories = []
    for text in texts:
        for category in sensitive_categories(text):
            if category not in categories:
                categories.append(category)
    injection_signals = []
    if category_hit(blob, "embedded_instruction"):
        injection_signals.append("embedded_instruction")
    forged = category_hit(blob, "forged_approval") or _nested_approval(stripped)
    if forged:
        injection_signals.append("forged_approval")
    leading = category_hit(blob, "leading_criterion")
    carve = any(carve_out_affirmed(text) for text in texts)
    role_in_text = any(role_claim(text) for text in texts)
    clearance_in_text = "my clearance is" in blob.casefold()

    owner_ref = process.get("owner_ref") if isinstance(process, dict) else None
    deputy_refs = []
    if isinstance(process, dict) and isinstance(process.get("deputy_refs"), list):
        deputy_refs = [item for item in process["deputy_refs"] if isinstance(item, str)]
    claimed = stripped.get("owner_ref")
    owner_conflict = isinstance(claimed, str) and claimed != owner_ref
    claimed_kept = claimed if isinstance(claimed, str) and REF_ID.fullmatch(claimed) else None

    stale_days = process.get("stale_after_days") if isinstance(process, dict) else None
    stuck_hours = process.get("stuck_after_hours") if isinstance(process, dict) else None
    if type(stale_days) is not int:
        stale_days = None
    if type(stuck_hours) is not int:
        stuck_hours = None

    runs = stripped.get("runs")
    runs_bad = not isinstance(runs, list)
    run_rows = runs if isinstance(runs, list) else []

    signatures: dict[str, str] = {}
    duplicate_run_conflict = False
    people_refs: list[str] = []
    date_rows: list[dict] = []
    excerpts: list[dict] = []
    mask_report = empty_mask()
    text_suppressed = False
    hold = False
    hold_bad = False
    retention: list[str] = []
    retention_bad = False
    marking_labels: list[str] = []
    marking_bad = False
    bodies: list[str] = []
    failures: list[dict] = []
    partial_any = False
    partial_sides: list[str] = []
    side_effects: set[str] = set()
    time_bad = question_unparseable or question_conflict
    future_any = False
    unparseable_time = question_unparseable
    ambiguous_time = False
    stale_any = False
    unknown_step = False

    seen_run_ids: list[str] = []
    for run in run_rows:
        if not isinstance(run, dict):
            unparseable_time = True
            time_bad = True
            continue
        run_id = run.get("run_id") if isinstance(run.get("run_id"), str) else None
        if isinstance(run.get("trigger_user_ref"), str):
            people_refs.append(run["trigger_user_ref"])
        if run.get("process_id") not in (None, process_id):
            failures.append({
                "run_id": run_id,
                "step_id": None,
                "step_name": None,
                "step_index": None,
                "status": None,
                "exception_class": "unclassified",
                "reason": "mixed_process",
                "error_codes": [],
                "error_text_used": False,
                "idempotent": False,
                "side_effects": "unknown",
                "qualifier": False,
                "retry_safe": False,
                "partial": False,
            })
            continue
        status = run.get("status")
        if status not in RUN_STATUS:
            unparseable_time = True
            time_bad = True
        run_stamps = []
        for field in ("started_at", "ended_at"):
            if field in run and run.get(field) not in (None, ""):
                stamped = _stamp(run.get(field), question, compare_times)
                stamped["run_id"] = run_id
                stamped["field"] = field
                date_rows.append(stamped)
                run_stamps.append(stamped)
                if stamped.get("unparseable") or stamped.get("ambiguous"):
                    unparseable_time = True
                    time_bad = True
                    if stamped.get("ambiguous"):
                        ambiguous_time = True
                if stamped.get("future"):
                    future_any = True
                    time_bad = True
        step_list = run.get("steps") if isinstance(run.get("steps"), list) else []
        if not isinstance(run.get("steps"), list):
            unknown_step = True
        cover = run.get("cover") if isinstance(run.get("cover"), str) else ""
        notes = run.get("notes") if isinstance(run.get("notes"), str) else ""
        meta_labels, meta_bad = metadata_markings(run.get("protective_marking"))
        marking_bad = marking_bad or meta_bad
        for label in meta_labels + content_markings(cover) + content_markings(notes):
            if label not in marking_labels:
                marking_labels.append(label)
        held_run, held_bad = legal_hold(run.get("legal_hold"), f"{cover}\n{notes}")
        hold = hold or held_run
        hold_bad = hold_bad or held_bad
        kept, kept_bad = retention_labels(run.get("retention"), f"{cover}\n{notes}")
        retention_bad = retention_bad or kept_bad
        for label in kept:
            if label not in retention:
                retention.append(label)
        bodies.append(cover)
        bodies.append(notes)

        prepared_steps = []
        for index, step in enumerate(step_list):
            if not isinstance(step, dict):
                unknown_step = True
                time_bad = True
                continue
            for field in ("started_at", "ended_at"):
                if field in step and step.get(field) not in (None, ""):
                    stamped = _stamp(step.get(field), question, compare_times)
                    stamped["run_id"] = run_id
                    stamped["field"] = f"step.{field}"
                    date_rows.append(stamped)
                    run_stamps.append(stamped)
                    if stamped.get("unparseable") or stamped.get("ambiguous"):
                        unparseable_time = True
                        time_bad = True
                        if stamped.get("ambiguous"):
                            ambiguous_time = True
                    if stamped.get("future"):
                        future_any = True
                        time_bad = True
            codes, codes_bad = _codes(step.get("error_codes"))
            if codes_bad:
                time_bad = True
                unparseable_time = True
            classified = _class_from_codes(codes, taxonomy)
            step_text = "\n".join(
                part for part in (step.get("error_text"), step.get("output_text")) if isinstance(part, str)
            )
            for label in content_markings(step_text):
                if label not in marking_labels:
                    marking_labels.append(label)
            step_hold, step_hold_bad = legal_hold(None, step_text)
            hold = hold or step_hold
            hold_bad = hold_bad or step_hold_bad
            step_retention, step_retention_bad = retention_labels(None, step_text)
            retention_bad = retention_bad or step_retention_bad
            for label in step_retention:
                if label not in retention:
                    retention.append(label)
            bodies.append(step_text)
            prepared_steps.append((index, step, classified))

        failed_index = None
        for index, step, _classified in prepared_steps:
            if step.get("status") in {"Failed", "TimedOut"}:
                failed_index = index
                break
        if failed_index is None and status == "TimedOut" and prepared_steps:
            failed_index = prepared_steps[-1][0]
        running_index = None
        if failed_index is None and status == "Running" and prepared_steps:
            for index, step, _classified in prepared_steps:
                if step.get("status") == "Running":
                    running_index = index
                    break
            if running_index is None:
                running_index = prepared_steps[-1][0]

        primary_index = failed_index if failed_index is not None else running_index
        succeeded_before = []
        if primary_index is not None:
            for index, step, _classified in prepared_steps:
                if index < primary_index and step.get("status") == "Succeeded":
                    succeeded_before.append(step)

        partial = bool(succeeded_before)
        partial_any = partial_any or partial
        run_sides: set[str] = set()
        for step in succeeded_before:
            pinned_step = steps.get(step.get("step_id")) if isinstance(step.get("step_id"), str) else None
            side = _side(pinned_step)
            if side not in {"none", "unknown"}:
                run_sides.add(side)
                if side not in partial_sides:
                    partial_sides.append(side)
        if primary_index is not None:
            for index, step, _classified in prepared_steps:
                if index == primary_index:
                    pinned_step = steps.get(step.get("step_id")) if isinstance(step.get("step_id"), str) else None
                    side = _side(pinned_step)
                    if side not in {"none", "unknown"}:
                        run_sides.add(side)
        side_effects.update(run_sides)

        latest = _latest_date(run_stamps)
        run_stale = False
        if compare_times and stale_days is not None and latest is not None:
            if latest <= question - timedelta(days=stale_days):
                run_stale = True
                stale_any = True
        elif compare_times and stale_days is None and isinstance(process, dict):
            time_bad = True
            unparseable_time = True

        run_time_bad = time_bad or run_stale or future_any or any(
            row.get("unparseable") or row.get("ambiguous") or row.get("future") for row in run_stamps
        )

        chosen = None
        if primary_index is not None:
            for index, step, classified in prepared_steps:
                if index == primary_index:
                    chosen = (index, step, classified)
                    break
        if chosen is None and status == "Cancelled":
            failures.append({
                "run_id": run_id,
                "step_id": None,
                "step_name": None,
                "step_index": None,
                "status": "Cancelled",
                "exception_class": "unclassified",
                "reason": "run_cancelled",
                "error_codes": [],
                "error_text_used": False,
                "idempotent": False,
                "side_effects": "unknown",
                "qualifier": False,
                "retry_safe": False,
                "partial": partial,
            })
        elif chosen is None and status == "Running":
            elapsed = {"known": False, "coerced": False, "reason": "no_timestamp"}
            started = next((row for row in run_stamps if row.get("field") == "started_at"), None)
            if started is not None and compare_times:
                elapsed = calendar_hours(started, question)
            if elapsed.get("coerced"):
                raise RuntimeError("elapsed hours were coerced")
            if (
                compare_times
                and stuck_hours is not None
                and elapsed.get("known") is True
                and isinstance(elapsed.get("hours"), int)
                and elapsed["hours"] >= stuck_hours
            ):
                classified = {
                    "exception_class": "timeout",
                    "reason": "stuck_running",
                    "error_codes": [],
                    "error_text_used": False,
                }
            else:
                classified = {
                    "exception_class": "unclassified",
                    "reason": "elapsed_not_known" if not elapsed.get("known") else "inside_stuck_threshold",
                    "error_codes": [],
                    "error_text_used": False,
                }
            failures.append({
                "run_id": run_id,
                "step_id": None,
                "step_name": None,
                "step_index": None,
                "status": status if status in RUN_STATUS else None,
                "exception_class": classified["exception_class"],
                "reason": classified["reason"],
                "error_codes": [],
                "error_text_used": False,
                "idempotent": False,
                "side_effects": "unknown",
                "qualifier": False,
                "retry_safe": False,
                "partial": partial,
            })
        elif chosen is not None:
            index, step, classified = chosen
            step_status = step.get("status")
            if step_status not in STEP_STATUS and status not in {"TimedOut", "Running"}:
                unparseable_time = True
                time_bad = True
            run_codes, run_codes_bad = _codes(run.get("error_codes"))
            if run_codes_bad:
                unparseable_time = True
            run_class = _class_from_codes(run_codes, taxonomy)
            if run_codes and (
                run_class["exception_class"] not in {None, classified["exception_class"]}
                or run_class["exception_class"] == "conflicting_codes"
            ):
                classified = {
                    "exception_class": "conflicting_codes",
                    "reason": "run_and_step_codes_disagree",
                    "error_codes": list(classified["error_codes"]) + list(run_class["error_codes"]),
                    "error_text_used": False,
                }
            if status == "TimedOut" and classified["exception_class"] is None:
                classified = {
                    "exception_class": "timeout",
                    "reason": "structured_status",
                    "error_codes": classified["error_codes"],
                    "error_text_used": False,
                }
            if status == "Running" and failed_index is None and classified["exception_class"] is None:
                started = next((row for row in run_stamps if row.get("field") == "started_at"), None)
                elapsed = calendar_hours(started, question) if started is not None and compare_times else {
                    "known": False, "coerced": False, "reason": "not_compared",
                }
                if (
                    compare_times
                    and stuck_hours is not None
                    and elapsed.get("known") is True
                    and isinstance(elapsed.get("hours"), int)
                    and elapsed["hours"] >= stuck_hours
                ):
                    classified = {
                        "exception_class": "timeout",
                        "reason": "stuck_running",
                        "error_codes": [],
                        "error_text_used": False,
                    }
                else:
                    classified = {
                        "exception_class": "unclassified",
                        "reason": "elapsed_not_known" if not elapsed.get("known") else "inside_stuck_threshold",
                        "error_codes": [],
                        "error_text_used": False,
                    }
            if classified["exception_class"] is None:
                classified = {
                    "exception_class": "unclassified",
                    "reason": "no_structured_code",
                    "error_codes": [],
                    "error_text_used": False,
                }
            pinned_step = steps.get(step.get("step_id")) if isinstance(step.get("step_id"), str) else None
            if pinned_step is None:
                unknown_step = True
            qualifier = bool(isinstance(pinned_step, dict) and str(pinned_step.get("qualifier") or "").strip())
            conflict = classified["exception_class"] == "conflicting_codes"
            safe = _retry_safe_step(
                pinned_step,
                classified["exception_class"],
                partial_side=bool(run_sides),
                carve=carve,
                time_bad=run_time_bad or not compare_times,
                conflict=conflict,
            )
            if process is None:
                safe = False
            failures.append({
                "run_id": run_id,
                "step_id": step.get("step_id") if isinstance(step.get("step_id"), str) else None,
                "step_name": step.get("name") if isinstance(step.get("name"), str) else None,
                "step_index": index,
                "status": step.get("status") if step.get("status") in STEP_STATUS else status if status in RUN_STATUS else None,
                "exception_class": classified["exception_class"],
                "reason": classified["reason"],
                "error_codes": list(classified["error_codes"]),
                "error_text_used": False,
                "idempotent": pinned_step.get("idempotent") is True if isinstance(pinned_step, dict) else False,
                "side_effects": _side(pinned_step),
                "qualifier": qualifier,
                "retry_safe": safe,
                "partial": partial,
            })
        signature = json.dumps(
            {
                "status": status,
                "steps": [
                    {
                        "id": step.get("step_id"),
                        "status": step.get("status"),
                        "codes": _codes(step.get("error_codes"))[0],
                    }
                    for _index, step, _classified in prepared_steps
                ],
            },
            sort_keys=True,
        )
        if isinstance(run_id, str):
            if run_id in signatures and signatures[run_id] != signature:
                duplicate_run_conflict = True
            signatures[run_id] = signature
            seen_run_ids.append(run_id)

    if duplicate_run_conflict:
        for row in failures:
            if row["run_id"] in signatures:
                row["exception_class"] = "conflicting_codes"
                row["reason"] = "duplicate_run_values_disagree"
                row["retry_safe"] = False

    applied = higher_marking(marking_labels)
    ceilings = []
    for ref in [owner_ref, *deputy_refs]:
        person = _person(pinned_people, ref)
        if person is None:
            ceilings.append(None)
        else:
            ceilings.append(person.get("clearance"))
    ceiling = None
    if ceilings and all(item in RANK for item in ceilings):
        ceiling = min(ceilings, key=lambda item: RANK[item])
    withhold = above_ceiling(applied, ceiling) or applied == "SECRET" or applied == "TOP SECRET"
    if applied in {"SECRET", "TOP SECRET"}:
        withhold = True
    elif above_ceiling(applied, ceiling):
        withhold = True

    identifier_total = {
        "called": False,
        "count": 0,
        "types": [],
        "output_is_anonymised": False,
        "values_stored": False,
        "redacted_text_copied": False,
    }
    for run in run_rows:
        if not isinstance(run, dict):
            continue
        run_id = run.get("run_id") if isinstance(run.get("run_id"), str) else None
        chunks = []
        if isinstance(run.get("notes"), str):
            chunks.append(("notes", None, run.get("notes")))
        if isinstance(run.get("cover"), str):
            chunks.append(("cover", None, run.get("cover")))
        for step in run.get("steps") or []:
            if not isinstance(step, dict):
                continue
            if isinstance(step.get("error_text"), str):
                chunks.append(("error_text", step.get("step_id"), step.get("error_text")))
            if isinstance(step.get("output_text"), str):
                chunks.append(("output_text", step.get("step_id"), step.get("output_text")))
        for kind, step_id, text in chunks:
            if not text:
                continue
            redacted, counted = _apply_identifiers(text, question)
            if counted.get("called"):
                identifier_total["called"] = True
                identifier_total["count"] += int(counted.get("count") or 0)
                for name in counted.get("types") or []:
                    if name not in identifier_total["types"]:
                        identifier_total["types"].append(name)
            base = redacted if not sensitive_categories(text) and not withhold else text
            excerpt, report, withheld = _excerpt(base if not withhold else text, withhold=withhold)
            if sensitive_categories(text):
                excerpt = "[withheld]"
                withheld = True
                report["masked_text_included"] = False
            mask_report = add_counts(mask_report, report)
            if people_fields(0, bool(suppress_small_counts(text)[1]["applied"]))["applied"]:
                text_suppressed = True
            excerpts.append({
                "run_id": run_id,
                "step_id": step_id if isinstance(step_id, str) else None,
                "field": kind,
                "excerpt": excerpt,
                "withheld": withheld,
                "values_copied": False,
            })

    distinct_people = sorted({ref for ref in people_refs if isinstance(ref, str)})
    suppression = people_fields(len(distinct_people), text_suppressed)
    if suppression["applied"]:
        for row in excerpts:
            if row["excerpt"] not in {"", "[withheld]", "[instruction withheld]"}:
                row["excerpt"], _report = suppress_small_counts(row["excerpt"])

    if duplicate_run_conflict:
        for row in failures:
            row["retry_safe"] = False

    groups: list[dict] = []
    group_index: dict[tuple, dict] = {}
    for failure in failures:
        if failure["reason"] in {"mixed_process"}:
            key = ("mixed", failure["run_id"])
        else:
            key = (
                failure["step_id"],
                failure["exception_class"],
                tuple(failure["error_codes"]),
                failure["reason"],
            )
        if key not in group_index:
            group = {
                "group_id": f"GRP-{len(groups) + 1}",
                "step_id": failure["step_id"],
                "step_name": failure["step_name"],
                "exception_class": failure["exception_class"],
                "reason": failure["reason"],
                "error_codes": list(failure["error_codes"]),
                "error_text_used": False,
                "idempotent_on_register": failure["idempotent"],
                "side_effects": failure["side_effects"],
                "qualifier": failure["qualifier"],
                "retry_safe": failure["retry_safe"],
                "run_ids": [],
                "citations": [],
            }
            groups.append(group)
            group_index[key] = group
        group = group_index[key]
        if failure["run_id"] and failure["run_id"] not in group["run_ids"]:
            group["run_ids"].append(failure["run_id"])
        group["retry_safe"] = bool(group["retry_safe"] and failure["retry_safe"])
        group["citations"].append({
            "run_id": failure["run_id"],
            "step_id": failure["step_id"],
            "step_name": failure["step_name"],
            "step_index": failure["step_index"],
            "status": failure["status"],
            "error_codes": list(failure["error_codes"]),
            "error_text_used": False,
        })

    real_groups = [group for group in groups if group["exception_class"] not in {None}]
    retry_safe = bool(real_groups) and all(group["retry_safe"] for group in real_groups) and process is not None
    if not compare_times or time_bad or carve or duplicate_run_conflict or runs_bad:
        retry_safe = False
        for group in groups:
            group["retry_safe"] = False

    classes = {group["exception_class"] for group in real_groups}
    wrong_class = bool(classes - RETRYABLE) or not classes
    not_idempotent = any(group["idempotent_on_register"] is not True or group["side_effects"] != "none" for group in real_groups)
    qualifier = any(group["qualifier"] for group in real_groups)
    conflict = any(group["exception_class"] == "conflicting_codes" for group in real_groups) or duplicate_run_conflict
    unknown_process = process is None
    risks = _risks_for(
        safe=retry_safe,
        side_effects=side_effects,
        partial=partial_any,
        carve=carve,
        time_bad=time_bad or not compare_times,
        conflict=conflict,
        unknown_process=unknown_process,
        not_idempotent=not_idempotent and not retry_safe,
        qualifier=qualifier,
        wrong_class=wrong_class and not retry_safe,
    )
    if "payment" in side_effects or "email" in side_effects or "record_write" in side_effects:
        cancel_risks = ["Cancelling does not reverse a payment, an email, or a record write."]
    elif partial_any:
        cancel_risks = ["Cancelling leaves the completed steps as they are."]
    else:
        cancel_risks = ["Cancelling leaves the run failed. The agent does not cancel it."]
    route_to = "process_owner"
    if categories or leading:
        route_to = "human_review"
    elif "authentication_or_expired_connection" in classes:
        route_to = "connector_admin"
    elif classes & {"data_validation", "missing_reference_data"}:
        route_to = "data_steward"
    options = [
        {"action_id": "retry", "safe": retry_safe, "risks": risks, "executes": False, "route_to": None},
        {
            "action_id": "route",
            "safe": True,
            "risks": ["The run stays as it is until a person acts. The agent does not send."],
            "executes": False,
            "route_to": route_to,
        },
        {"action_id": "cancel", "safe": False, "risks": cancel_risks, "executes": False, "route_to": None},
    ]

    mixed = any(group["reason"] == "mixed_process" for group in groups)
    if categories or leading or unknown_process or mixed or question_conflict or question_unparseable or runs_bad:
        outcome = "route_to_human"
    elif not real_groups:
        outcome = "route_to_human"
    else:
        outcome = "proposal_for_owner"

    explanations = []
    for group in real_groups:
        cause = CAUSE.get(group["exception_class"], CAUSE["unclassified"])
        cited = ", ".join(
            f"{item['run_id']} step {item['step_name']} index {item['step_index']} status {item['status']}"
            for item in group["citations"]
        )
        explanations.append(f"{cause} Error text was not used. Cited: {cited}.")

    acks = ["pins_seen", "risks_seen"]
    if stale_any or future_any or unparseable_time or ambiguous_time or question_conflict or question_unparseable:
        acks.append("dates_seen")
    if applied or hold or retention:
        acks.append("markings_seen")
    if caller_register["supplied"] or caller_taxonomy["supplied"]:
        acks.append("register_seen")
    if partial_any:
        acks.append("partial_seen")
    if suppression["applied"]:
        acks.append("suppression_seen")
    if conflict:
        acks.append("conflict_seen")

    result = {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment_id": EXPERIMENT_ID,
        "autonomy": "A1",
        "distinct_from": "Experiment 17 invoice exception triage was not called.",
        "diagnosis_id": stripped.get("diagnosis_id") if isinstance(stripped.get("diagnosis_id"), str) else None,
        "diagnosis_id_valid": bool(isinstance(stripped.get("diagnosis_id"), str) and DIAGNOSIS_ID.fullmatch(stripped.get("diagnosis_id"))),
        "process_id": process_id if isinstance(process_id, str) else None,
        "process_on_register": process is not None,
        "owner_ref": owner_ref if isinstance(owner_ref, str) else None,
        "deputy_refs": deputy_refs,
        "claimed_owner_ref": None if not owner_conflict else claimed_kept,
        "claimed_owner_applied": False,
        "as_of": question.isoformat(),
        "question_date_unparseable": question_unparseable,
        "question_date_conflict": question_conflict,
        "times_compared": compare_times,
        "outcome": outcome,
        "groups": groups,
        "explanations": explanations,
        "options": options,
        "retry_safe": retry_safe,
        "partial_completion": partial_any,
        "partial_side_effects": partial_sides,
        "duplicate_risks": {
            "payment": "payment" in side_effects,
            "email": "email" in side_effects,
            "record_write": "record_write" in side_effects,
        },
        "marking": {
            "applied": applied,
            "labels": marking_labels,
            "unparseable": marking_bad,
            "bodies_withheld": withhold,
            "clearance_from_directory": ceiling if ceiling in RANK else None,
            "self_declared_clearance_used": False,
        },
        "legal_hold": hold,
        "legal_hold_unparseable": hold_bad,
        "retention": retention,
        "retention_unparseable": retention_bad,
        "conflicting_retention": len(retention) > 1,
        "prompt_injection": {"signals": injection_signals, "followed": False, "ignored_request_keys": ignored},
        "suppression": suppression,
        "required_acknowledgements": acks,
        "route_seen": False,
        "distress": {"routed": bool(categories), "categories": categories, "cue_copied": False},
        "leading_criteria": leading,
        "leading_applied": False,
        "register_check": caller_register,
        "taxonomy_check": caller_taxonomy,
        "caller_directory_supplied": caller_directory_supplied,
        "dates": [
            {
                "run_id": row.get("run_id"),
                "field": row.get("field"),
                "iso": row.get("iso"),
                "unparseable": row.get("unparseable") is True,
                "ambiguous": row.get("ambiguous") is True,
                "future": row.get("future") is True,
                "reason": row.get("reason"),
                "coerced": False,
            }
            for row in date_rows
        ],
        "stale": stale_any,
        "future_timestamp": future_any,
        "unparseable_timestamp": unparseable_time or ambiguous_time,
        "owner_conflict": owner_conflict,
        "carve_out": carve,
        "conflicting_values": conflict or len(retention) > 1,
        "unknown_step": unknown_step,
        "runs_unparseable": runs_bad,
        "excerpts": excerpts,
        "masking": mask_report,
        "uk_identifiers": identifier_total,
        "uk_context": {
            "opened_on": uk_context()["opened_on"],
            "legal_advice": False,
            "decides_impact_tolerance": False,
            "sysc_15a_opened": False,
            "article_5_1_c_quoted": True,
            "article_22a_quoted": True,
        },
        "owner_decision_recorded": False,
        "chosen_action": None,
        "human_approval": None,
        "blocked_reason": None,
        "ignored_request_keys": ignored,
        "run_count": len([row for row in run_rows if isinstance(row, dict)]),
        "role_in_text": role_in_text,
        "clearance_in_text": clearance_in_text,
    }
    if not result["diagnosis_id_valid"]:
        result["outcome"] = "route_to_human"
    _force(result)
    if isinstance(result["diagnosis_id"], str) and result["diagnosis_id_valid"]:
        _store(result)
    else:
        result["content_hash"] = _hash(result)
    return result


def _named_owner(result: dict, directory: dict, approver_ref: object) -> tuple[dict | None, str | None]:
    pinned = pinned_directory()
    if directory != pinned:
        return None, "caller_directory_not_used"
    allowed = {result.get("owner_ref"), *list(result.get("deputy_refs") or [])}
    allowed.discard(None)
    if approver_ref not in allowed:
        return None, "not_the_named_owner"
    person = _person(pinned, approver_ref)
    if person is None or person.get("active") is not True or person.get("role") != "process_owner":
        return None, "approver_not_process_owner"
    return person, None


def _bound(result: dict, approval: dict) -> str | None:
    diagnosis_id = result.get("diagnosis_id")
    held = _HELD.get(diagnosis_id) if isinstance(diagnosis_id, str) else None
    if not isinstance(held, dict):
        return "no_agent_held_copy"
    current = _hash(result)
    if approval.get("content_hash") != held.get("content_hash"):
        return "caller_rehash_rejected"
    if result.get("content_hash") != held.get("content_hash") or current != held.get("content_hash"):
        return "content_tampered"
    if _projection(result) != held.get("projection"):
        return "content_tampered"
    return None


def _ack(result: dict, approval: dict) -> str | None:
    for key in result.get("required_acknowledgements") or []:
        if approval.get(key) is not True:
            return f"{key}_not_boolean_true"
    return None


def record_route_seen(result: dict, directory: dict, approval: dict) -> dict:
    """Record that the named owner has seen a human route. Nothing is retried."""

    updated = deepcopy(result)
    _force(updated)
    updated["human_approval"] = None
    if not isinstance(approval, dict):
        updated["blocked_reason"] = "approval_not_object"
        updated["route_seen"] = False
        _remember(updated)
        return updated
    if approval.get("item") != "route-seen" or approval.get("decision") != "seen":
        updated["blocked_reason"] = "wrong_item"
        updated["route_seen"] = False
        _remember(updated)
        return updated
    reason = _bound(result, approval)
    if reason:
        updated["blocked_reason"] = reason
        updated["route_seen"] = False
        _remember(updated)
        return updated
    _person_row, role_reason = _named_owner(result, directory, approval.get("approver_ref"))
    if role_reason:
        updated["blocked_reason"] = role_reason
        updated["route_seen"] = False
        _remember(updated)
        return updated
    if approval.get("diagnosis_id") != result.get("diagnosis_id"):
        updated["blocked_reason"] = "diagnosis_mismatch"
        updated["route_seen"] = False
        _remember(updated)
        return updated
    updated["route_seen"] = True
    updated["distress"] = {
        "routed": True,
        "categories": list((result.get("distress") or {}).get("categories") or []),
        "cue_copied": False,
        "seen": True,
    }
    updated["blocked_reason"] = None
    _force(updated)
    _remember(updated)
    return updated


def record_owner_decision(result: dict, directory: dict, decision: dict) -> dict:
    """Record the owner's choice. Do not retry, cancel, edit, or re-run."""

    updated = deepcopy(result)
    _force(updated)
    updated["human_approval"] = None
    updated["owner_decision_recorded"] = False
    updated["chosen_action"] = None
    if not isinstance(decision, dict):
        updated["blocked_reason"] = "approval_not_object"
        _remember(updated)
        return updated
    if decision.get("item") != "owner-decision" or decision.get("decision") not in {"retry", "route", "cancel"}:
        updated["blocked_reason"] = "wrong_item"
        _remember(updated)
        return updated
    reason = _bound(result, decision)
    if reason:
        updated["blocked_reason"] = reason
        _remember(updated)
        return updated
    if result.get("outcome") == "route_to_human" and result.get("route_seen") is not True:
        updated["blocked_reason"] = "route_not_seen"
        _remember(updated)
        return updated
    if result.get("owner_decision_recorded") is True:
        updated["blocked_reason"] = "already_recorded"
        _remember(updated)
        return updated
    if decision.get("diagnosis_id") != result.get("diagnosis_id"):
        updated["blocked_reason"] = "diagnosis_mismatch"
        _remember(updated)
        return updated
    action = decision.get("decision")
    if decision.get("action_id") != action:
        updated["blocked_reason"] = "action_mismatch"
        _remember(updated)
        return updated
    offered = {option.get("action_id") for option in result.get("options") or [] if isinstance(option, dict)}
    if action not in offered:
        updated["blocked_reason"] = "action_not_offered"
        _remember(updated)
        return updated
    person, role_reason = _named_owner(result, directory, decision.get("approver_ref"))
    if role_reason:
        updated["blocked_reason"] = role_reason
        _remember(updated)
        return updated
    ack_reason = _ack(result, decision)
    if ack_reason:
        updated["blocked_reason"] = ack_reason
        _remember(updated)
        return updated
    if "runs" in decision or "register" in decision or "error_text" in decision:
        updated["blocked_reason"] = "caller_rehash_rejected"
        _remember(updated)
        return updated
    held = _HELD[result["diagnosis_id"]]
    updated["owner_decision_recorded"] = True
    updated["chosen_action"] = action
    updated["human_approval"] = {
        "item": "owner-decision",
        "approver_ref": person["employee_ref"],
        "content_hash": held["content_hash"],
        "action_id": action,
        "recorded": True,
        "executes_action": False,
        "bound_to_held_copy": True,
    }
    updated["blocked_reason"] = None
    updated["outcome"] = "owner_decision_recorded"
    _force(updated)
    _remember(updated)
    return updated


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Diagnose a synthetic workflow exception.")
    parser.add_argument("--request", required=True)
    parser.add_argument("--as-of", required=True)
    args = parser.parse_args(argv)
    try:
        request = _load(Path(args.request))
    except (OSError, json.JSONDecodeError):
        print("The request could not be read.", file=sys.stderr)
        return 2
    try:
        result = diagnose(request, as_of=args.as_of)
    except (NotSynthetic, TypeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
