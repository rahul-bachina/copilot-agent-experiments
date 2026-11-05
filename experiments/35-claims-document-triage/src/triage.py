"""Draft a claim summary for one synthetic pack.

``triage`` calls Experiment 12 ``intake`` with purpose ``claims_fnol``.
That intake calls Experiment 08. Faithfulness uses Experiment 29
``score_claim``. This module does not re-implement those three.

The return value is a draft. The claims handler approves the class.
``record_handler_classification`` checks a role. It still does not accept,
decline, settle, tell the customer, or write to a claims system. Those
functions always raise.
"""

from __future__ import annotations

import argparse
import importlib
import json
import re
import sys
from copy import deepcopy
from datetime import date, datetime
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from claims_injection import line_is_hostile, merge_scans, scan_text
    from scorecard import ScoreForbidden, approve_thresholds, phrases_in, score_lines
    from scorecard import labelled_lines as extract_labelled
    from sources import DEFAULT_STALE_AFTER_DAYS, SOURCES, SOURCES_PINNED_ON
else:
    from .claims_injection import line_is_hostile, merge_scans, scan_text
    from .scorecard import ScoreForbidden, approve_thresholds, phrases_in, score_lines
    from .scorecard import labelled_lines as extract_labelled
    from .sources import DEFAULT_STALE_AFTER_DAYS, SOURCES, SOURCES_PINNED_ON

LABEL = "DRAFT FOR THE CLAIMS HANDLER"
CATALOGUE_ID = "B007"
EXPERIMENT_ID = "exp-35-claims-document-triage"
INTAKE_EXPERIMENT_ID = "exp-12-document-intake"
PURPOSE_ID = "claims_fnol"
HANDLER_ROLE = "Claims handler"
FIRM_NAME = re.compile(r"[A-Za-z0-9 '&.,-]{1,80}\Z")
FILE_ID = re.compile(r"^[A-Za-z0-9_-]{1,40}$")
ROLES = frozenset({"fnol", "invoice", "report", "policy_wording", "other"})
CLASSES = frozenset({"escape_of_water", "storm", "accidental_damage", "theft", "other"})
PERIL_CLASS = {
    "escape of water": "escape_of_water",
    "storm": "storm",
    "accidental damage": "accidental_damage",
    "theft": "theft",
}
NOT_CURRENT = frozenset({"stale", "missing", "future", "invalid"})
_INTEGER = re.compile(r"^\d+$")

PROHIBITED_KEYS = frozenset(
    {
        "claim_accepted",
        "claim_declined",
        "claim_settled",
        "customer_told",
        "claims_system_written",
        "classification_approved",
        "classification_approved_by_handler",
        "fraud",
        "fraud_indicated",
        "coverage_decided",
        "approve",
        "decline",
        "settle",
        "send",
        "tell_customer",
        "handler_signoff",
        "customer_message",
    }
)

FRAMING = (
    "Each line is a quote from a file this run read. "
    "A coverage pointer quotes the policy extract. "
    "Whether those words apply is for the handler. "
    "This draft does not choose a claims outcome and it has no message for the customer."
)

LIMITATIONS = (
    "This draft does not accept, decline, or settle a claim.",
    "It does not tell the customer anything. There is no customer message.",
    "It does not write to a claims system, including after a handler records a class.",
    "An inconsistency line is a prompt for a person to check. It is not a finding and it is not a statement about the policyholder's conduct.",
    "A coverage pointer is a quote. It is not a statement that the loss is or is not within the policy.",
    "The class is a proposal until a claims handler records one. Recording a class is not an outcome.",
    "The scorecard is a deterministic checker. It is not an LLM-as-a-judge and it is not a Microsoft Foundry score. Thresholds are not approved.",
    "A score under a draft threshold asks a person to look. It does not decline the claim.",
    "Conciseness and adequacy of reasoning, named in the FCA case study, are not scored.",
    "Document inventory and UK identifier spans come from Experiment 12 and Experiment 08. A file with an identifier is not quoted. The text is not anonymised.",
    "Faithfulness comes from Experiment 29. This module does not re-implement that checker.",
    "Only labelled lines and one policy line are quoted. Other sentences in the file are not extracted.",
    "No model was called.",
)


class ClaimForbidden(RuntimeError):
    """The triage has no accept, decline, settle, tell, or write path."""


class NotSynthetic(ValueError):
    """The pack was not marked synthetic. The message does not include the body."""


def _import_from(src: Path, module_name: str):
    inserted = str(src)
    if inserted in sys.path:
        sys.path.remove(inserted)
    sys.path.insert(0, inserted)
    existing = sys.modules.get(module_name)
    if existing is not None:
        existing_file = str(getattr(existing, "__file__", ""))
        if not existing_file.startswith(inserted):
            del sys.modules[module_name]
    return importlib.import_module(module_name)


def _load_intake():
    intake_src = Path(__file__).resolve().parents[2] / "12-document-intake" / "src"
    if not intake_src.is_dir():
        raise ClaimForbidden(
            "Experiment 12 is not beside this experiment. The triage will not invent an inventory."
        )
    module = _import_from(intake_src, "intake")
    if module.EXPERIMENT_ID != INTAKE_EXPERIMENT_ID:
        raise ClaimForbidden("the intake module is not Experiment 12")
    return module


def _strip_prohibited(mapping: dict, prefix: str) -> list[str]:
    found = []
    for key in list(mapping):
        if key in PROHIBITED_KEYS:
            found.append(f"{prefix}{key}" if prefix else key)
            del mapping[key]
    return found


def _flags() -> dict:
    return {
        "claim_accepted": False,
        "claim_declined": False,
        "claim_settled": False,
        "customer_told": False,
        "claims_system_written": False,
        "classification_approved": False,
        "fraud_indicated": False,
        "inconsistency_is_a_finding": False,
        "coverage_decided": False,
        "customer_message_present": False,
        "a3_recommended": False,
    }


def _force_inert(draft: dict) -> None:
    draft["actions_taken"] = []
    draft["model_called"] = False
    draft["network_called"] = False
    draft["customer_message"] = None
    draft["output_is_anonymised"] = False
    draft["flags"] = _flags()
    draft["claim_accepted"] = False
    draft["claim_declined"] = False
    draft["claim_settled"] = False
    draft["customer_told"] = False
    draft["claims_system_written"] = False
    draft["fraud_indicated"] = False
    draft["coverage_decided"] = False
    draft["a3_recommended"] = False
    injection = draft.get("prompt_injection") or {}
    injection["followed"] = False
    for signal in injection.get("signals") or []:
        signal["followed"] = False
    for prompt in draft.get("inconsistency_prompts") or []:
        prompt["is_a_finding"] = False
        prompt["is_a_fraud_indicator"] = False
        prompt["suggests_a_claims_outcome"] = False
    for pointer in (draft.get("summary") or {}).get("coverage_pointers") or []:
        pointer["coverage_decided"] = False
        pointer["handler_decides_whether_it_applies"] = True


def _iso(raw) -> date | None:
    if not isinstance(raw, str) or not raw:
        return None
    try:
        return date.fromisoformat(raw)
    except ValueError:
        return None


def _integer(value: str) -> int | None:
    if _INTEGER.fullmatch(value or ""):
        return int(value)
    return None


def _prompt(prompt_id: str, text: str, left: dict, right: dict) -> dict:
    if phrases_in(text):
        raise ClaimForbidden("A prompt contained a decision phrase. The draft was not returned.")
    return {
        "id": prompt_id,
        "prompt_for_handler": text,
        "left": left,
        "right": right,
        "is_a_finding": False,
        "is_a_fraud_indicator": False,
        "suggests_a_claims_outcome": False,
    }


def _comparisons(files: list[dict]) -> list[dict]:
    prompts = []
    usable = [
        file
        for file in files
        if file.get("read_status") == "read" and not file.get("withheld")
    ]
    fnol_lines = []
    invoice_lines = []
    policy_lines = []
    for file in usable:
        rows = extract_labelled(file.get("content") or "")
        bucket = {"fnol": fnol_lines, "invoice": invoice_lines, "policy_wording": policy_lines}.get(file["role"])
        if bucket is None:
            continue
        for row in rows:
            if line_is_hostile(row["line"]) or phrases_in(row["line"]):
                continue
            bucket.append({**row, "file_id": file["file_id"]})

    def first(rows: list[dict], label: str) -> dict | None:
        for row in rows:
            if row["label"] == label:
                return row
        return None

    stated = first(fnol_lines, "Stated amount")
    for invoice in invoice_lines:
        if invoice["label"] != "Invoice total":
            continue
        left = _integer(stated["value"]) if stated else None
        right = _integer(invoice["value"])
        if stated and left is not None and right is not None and left != right:
            prompts.append(
                _prompt(
                    f"amount_check:{stated['file_id']}:{invoice['file_id']}",
                    (
                        "Check whether the stated amount on the first notification and the "
                        "invoice total refer to the same figure. This is a prompt for a person "
                        "to check. It is not a finding and it is not a reason to choose a claims outcome."
                    ),
                    {"file_id": stated["file_id"], "label": "Stated amount", "value": stated["value"]},
                    {"file_id": invoice["file_id"], "label": "Invoice total", "value": invoice["value"]},
                )
            )
    loss = first(fnol_lines, "Date of loss")
    loss_date = _iso(loss["value"]) if loss else None
    if loss and loss_date is not None:
        for invoice in invoice_lines:
            if invoice["label"] != "Invoice date":
                continue
            invoice_date = _iso(invoice["value"])
            if invoice_date is not None and invoice_date < loss_date:
                prompts.append(
                    _prompt(
                        f"invoice_date_before_loss:{loss['file_id']}:{invoice['file_id']}",
                        (
                            "The invoice date is before the date of loss printed on the first "
                            "notification. Check whether the two dates refer to the same event. "
                            "This is a prompt for a person to check. It is not a finding."
                        ),
                        {"file_id": loss["file_id"], "label": "Date of loss", "value": loss["value"]},
                        {"file_id": invoice["file_id"], "label": "Invoice date", "value": invoice["value"]},
                    )
                )
        start = first(policy_lines, "Period from")
        end = first(policy_lines, "Period to")
        start_date = _iso(start["value"]) if start else None
        end_date = _iso(end["value"]) if end else None
        if start_date is not None and end_date is not None and (loss_date < start_date or loss_date > end_date):
            prompts.append(
                _prompt(
                    f"period_check:{loss['file_id']}:{start['file_id']}",
                    (
                        "Check whether the date of loss falls inside the period printed on the "
                        "policy extract. This is a prompt for a person to check. It is not a "
                        "statement that the loss is inside or outside the contract."
                    ),
                    {"file_id": loss["file_id"], "label": "Date of loss", "value": loss["value"]},
                    {
                        "file_id": start["file_id"],
                        "label": "Period",
                        "value": f"{start['value']} to {end['value']}",
                    },
                )
            )
    holder = first(fnol_lines, "Policyholder")
    for invoice in invoice_lines:
        if invoice["label"] != "Invoice to" or holder is None:
            continue
        if holder["value"].casefold() != invoice["value"].casefold():
            prompts.append(
                _prompt(
                    f"name_check:{holder['file_id']}:{invoice['file_id']}",
                    (
                        "Check whether the policyholder line and the invoice addressee refer to "
                        "the same person. This is a prompt for a person to check. It is not a finding."
                    ),
                    {"file_id": holder["file_id"], "label": "Policyholder", "value": holder["value"]},
                    {"file_id": invoice["file_id"], "label": "Invoice to", "value": invoice["value"]},
                )
            )
    perils = [row for row in fnol_lines if row["label"] == "Peril"]
    classes = []
    for row in perils:
        classes.append(PERIL_CLASS.get(row["value"].casefold()))
    distinct = {item for item in classes if item}
    if len(perils) > 1 or (perils and (None in classes or len(distinct) != 1)):
        prompts.append(
            _prompt(
                "class_not_single",
                (
                    "The first notification does not have one peril line from the closed list. "
                    "The handler chooses the class. This is a prompt for a person to check. "
                    "It is not a finding."
                ),
                {"file_id": perils[0]["file_id"] if perils else None, "label": "Peril", "value": None},
                {"file_id": None, "label": "closed list", "value": "more than one or none"},
            )
        )
    return prompts


def _propose_class(files: list[dict]) -> dict:
    perils = []
    for file in files:
        if file.get("role") != "fnol" or file.get("read_status") != "read" or file.get("withheld"):
            continue
        for row in extract_labelled(file.get("content") or ""):
            if row["label"] != "Peril":
                continue
            if line_is_hostile(row["line"]) or phrases_in(row["line"]):
                continue
            perils.append(PERIL_CLASS.get(row["value"].casefold()))
    distinct = {item for item in perils if item}
    if len(perils) == 1 and len(distinct) == 1:
        proposed = perils[0]
        note = (
            f"Proposed class: {proposed}. The peril line on the first notification matches "
            "that closed class. The handler approves or changes the class. "
            "Recording the class leaves the claims outcome untouched."
        )
    else:
        proposed = "not_proposed"
        note = (
            "No single closed class was proposed. The handler chooses the class. "
            "Recording the class leaves the claims outcome untouched."
        )
    if phrases_in(note):
        raise ClaimForbidden("The class note contained a decision phrase.")
    return {
        "proposed_class": proposed,
        "approved": False,
        "approved_class": None,
        "handler_record": None,
        "note": note,
        "closed_list": sorted(CLASSES),
    }


def _summary_lines(files: list[dict]) -> tuple[list[dict], list[dict], list[str]]:
    lines = []
    pointers = []
    gaps = []
    peril_phrase = None
    for file in files:
        if file.get("role") != "fnol" or file.get("withheld") or file.get("read_status") != "read":
            continue
        for row in extract_labelled(file.get("content") or ""):
            if row["label"] == "Peril" and not line_is_hostile(row["line"]) and not phrases_in(row["line"]):
                peril_phrase = row["value"].casefold()
                break
        if peril_phrase:
            break

    for file in files:
        file_id = file["file_id"]
        if file.get("read_status") != "read":
            gaps.append(f"{file_id}: not read ({file.get('read_status')}). That is a gap, not a clean result.")
            continue
        if file.get("withheld"):
            gaps.append(
                f"{file_id}: withheld from the summary because Experiment 08 reported a deterministic identifier. "
                "The text is not copied and is not described as anonymised."
            )
            continue
        content = file.get("content") or ""
        for index, row in enumerate(extract_labelled(content), start=1):
            if line_is_hostile(row["line"]) or phrases_in(row["line"]):
                gaps.append(f"{file_id}: a labelled line was not quoted because it carries an instruction or a decision phrase.")
                continue
            lines.append(
                {
                    "line_id": f"{file_id}-l{index}",
                    "text": row["line"],
                    "quote": row["line"],
                    "source_file_id": file_id,
                    "role": file["role"],
                }
            )
        if file.get("role") == "policy_wording" and peril_phrase:
            matched = False
            for index, raw_line in enumerate(content.splitlines(), start=1):
                line = raw_line.strip()
                if not line or peril_phrase not in line.casefold():
                    continue
                if len(line) > 400 or line_is_hostile(line):
                    gaps.append(f"{file_id}: a policy line mentioning the peril was not quoted.")
                    continue
                pointers.append(
                    {
                        "pointer_id": f"{file_id}-p{index}",
                        "text": line,
                        "quote": line,
                        "source_file_id": file_id,
                        "handler_decides_whether_it_applies": True,
                        "coverage_decided": False,
                    }
                )
                lines.append(
                    {
                        "line_id": f"{file_id}-p{index}",
                        "text": line,
                        "quote": line,
                        "source_file_id": file_id,
                        "role": "policy_wording",
                    }
                )
                matched = True
                break
            if not matched:
                gaps.append(
                    f"{file_id}: no line in the policy extract contains the peril words from the first notification. "
                    "That is a gap. It is not an outcome."
                )
    return lines, pointers, gaps


def _source_rows(as_of: date, window: int) -> tuple[list[dict], bool]:
    rows = []
    stale = False
    for source in SOURCES:
        opened = date.fromisoformat(source["opened_on"])
        age = (as_of - opened).days
        is_stale = age > window
        stale = stale or is_stale
        rows.append(
            {
                "id": source["id"],
                "title": source["title"],
                "url": source["url"],
                "opened_on": source["opened_on"],
                "age_days": age,
                "stale": is_stale,
                "quote": source["quote"],
                "note": source["note"],
            }
        )
    return rows, stale


def _prepare_files(raw_files: list, intake_files: list[dict]) -> list[dict]:
    by_id = {row["file_id"]: row for row in intake_files}
    prepared = []
    for raw in raw_files:
        file_id = raw["file_id"]
        intake_row = by_id[file_id]
        role = raw.get("role") if raw.get("role") in ROLES else "other"
        finding_count = int((intake_row.get("pii") or {}).get("finding_count") or 0)
        prepared.append(
            {
                "file_id": file_id,
                "filename": intake_row["filename"],
                "role": role,
                "media_type": intake_row["media_type"],
                "read_status": intake_row["read_status"],
                "document_date": intake_row["document_date"],
                "date_status": intake_row["date_status"],
                "age_days": intake_row["age_days"],
                "suggested_class": intake_row["suggested_class"],
                "pii_finding_count": finding_count,
                "pii_entity_types": list((intake_row.get("pii") or {}).get("entity_types") or []),
                "withheld": finding_count > 0 and intake_row["read_status"] == "read",
                "content": raw.get("content") if intake_row["read_status"] == "read" else "",
                "checksum_matches": intake_row["checksum_matches"],
            }
        )
    return prepared


def _public_files(files: list[dict]) -> list[dict]:
    public = []
    for file in files:
        public.append(
            {
                "file_id": file["file_id"],
                "filename": file["filename"],
                "role": file["role"],
                "read_status": file["read_status"],
                "document_date": file["document_date"],
                "date_status": file["date_status"],
                "age_days": file["age_days"],
                "suggested_class": file["suggested_class"],
                "pii_finding_count": file["pii_finding_count"],
                "pii_entity_types": file["pii_entity_types"],
                "withheld_for_identifier": file["withheld"],
                "content_recorded": False,
                "checksum_matches": file["checksum_matches"],
            }
        )
    return public


def triage(
    pack: dict,
    *,
    as_of: date,
    stale_after_days: int = DEFAULT_STALE_AFTER_DAYS,
    rules_as_of: date | None = None,
    thresholds: dict | None = None,
) -> dict:
    """Return a draft. Outcome flags stay false. The class is not approved."""

    if not isinstance(pack, dict):
        raise TypeError("pack must be an object")
    if not isinstance(as_of, date) or isinstance(as_of, datetime):
        raise TypeError("as_of must be a date")
    if type(stale_after_days) is not int or stale_after_days < 0:
        raise ValueError("stale_after_days must be a non-negative integer")
    if rules_as_of is not None and not isinstance(rules_as_of, date):
        raise TypeError("rules_as_of must be a date")
    if pack.get("synthetic") is not True:
        raise NotSynthetic("record is not marked synthetic")

    working = dict(pack)
    prohibited = _strip_prohibited(working, "")
    firm = working.get("firm_name", "")
    if not isinstance(firm, str) or not FIRM_NAME.fullmatch(firm):
        raise ValueError("firm_name must be a single line of at most 80 characters")
    claim_id = working.get("claim_id", "")
    if not isinstance(claim_id, str) or not FILE_ID.fullmatch(claim_id):
        raise ValueError("claim_id must be 1 to 40 letters, digits, hyphens, or underscores")
    files_in = working.get("files")
    if not isinstance(files_in, list) or not files_in:
        raise ValueError("pack has no files")

    scans = []
    intake_files = []
    for raw in files_in:
        if not isinstance(raw, dict):
            raise ValueError("each file must be an object")
        file_copy = dict(raw)
        prohibited.extend(_strip_prohibited(file_copy, f"file:{file_copy.get('file_id', '?')}:"))
        file_id = file_copy.get("file_id", "")
        if not isinstance(file_id, str) or not FILE_ID.fullmatch(file_id):
            raise ValueError("file_id must be 1 to 40 letters, digits, hyphens, or underscores")
        content = file_copy.get("content") if isinstance(file_copy.get("content"), str) else ""
        filename = file_copy.get("filename") if isinstance(file_copy.get("filename"), str) else ""
        scans.append(scan_text(filename, file_id=file_id, where="filename"))
        if content:
            scans.append(scan_text(content, file_id=file_id, where="body"))
        intake_files.append(
            {
                "file_id": file_id,
                "filename": filename,
                "media_type": file_copy.get("media_type", ""),
                "document_date": file_copy.get("document_date"),
                "content": content,
                "sha256": file_copy.get("sha256"),
            }
        )

    intake_module = _load_intake()
    intake_draft = intake_module.intake(
        {
            "synthetic": True,
            "batch_id": claim_id,
            "requested_purpose": PURPOSE_ID,
            "files": intake_files,
        },
        as_of=as_of,
        stale_after_days=stale_after_days,
        rules_as_of=rules_as_of,
    )
    prepared = _prepare_files(files_in, intake_draft["files"])
    lines, pointers, gaps = _summary_lines(prepared)
    prompts = _comparisons(prepared)
    for file in prepared:
        if file["date_status"] in NOT_CURRENT:
            prompts.append(
                _prompt(
                    f"date_not_current:{file['file_id']}",
                    (
                        "A document date is missing, in the future, unreadable, or older than the "
                        "freshness window. Check it before relying on a line from that file. "
                        "This is a prompt for a person to check. It is not a finding. "
                        "The window is not a claims time limit."
                    ),
                    {"file_id": file["file_id"], "label": "document_date", "value": file["document_date"]},
                    {"file_id": None, "label": "date_status", "value": file["date_status"]},
                )
            )
    classification = _propose_class(prepared)
    prose = (
        [{"text": line["text"], "source_file_id": line["source_file_id"]} for line in lines]
        + [{"text": item["text"], "source_file_id": item["source_file_id"]} for item in pointers]
        + [{"text": FRAMING, "source_file_id": ""}]
        + [{"text": item["prompt_for_handler"], "source_file_id": ""} for item in prompts]
        + [{"text": classification["note"], "source_file_id": ""}]
    )
    card = score_lines(
        files=prepared,
        lines=lines,
        prose=prose,
        as_of=as_of.isoformat(),
        stale_after_days=stale_after_days,
        thresholds=thresholds,
    )
    source_rows, sources_stale = _source_rows(as_of, stale_after_days)
    do_not_rely = (
        sources_stale
        or bool(intake_draft.get("catalogue_stale"))
        or bool(intake_draft.get("gateway_rules_stale"))
        or any(file["date_status"] in NOT_CURRENT for file in prepared)
    )
    draft = {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment_id": EXPERIMENT_ID,
        "autonomy": "A1",
        "firm_name": firm,
        "claim_id": claim_id,
        "as_of": as_of.isoformat(),
        "stale_after_days": stale_after_days,
        "sources_pinned_on": SOURCES_PINNED_ON.isoformat(),
        "sources_stale": sources_stale,
        "do_not_rely": do_not_rely,
        "model_called": False,
        "network_called": False,
        "output_is_anonymised": False,
        "customer_message": None,
        "actions_taken": [],
        "flags": _flags(),
        "claim_accepted": False,
        "claim_declined": False,
        "claim_settled": False,
        "customer_told": False,
        "claims_system_written": False,
        "classification_approved_by_handler": False,
        "fraud_indicated": False,
        "coverage_decided": False,
        "a3_recommended": False,
        "purpose_requested": PURPOSE_ID,
        "purpose_confirmed": False,
        "intake_experiment_id": intake_draft["experiment_id"],
        "intake_catalogue_id": intake_draft["catalogue_id"],
        "gateway_called": bool(intake_draft["gateway"]["called"]),
        "intake_files_confirmed": intake_draft["files_confirmed"],
        "intake_handed_off": intake_draft["routing"]["handed_off"],
        "prompt_injection": merge_scans(scans),
        "intake_prompt_injection_detected": bool(intake_draft["prompt_injection"]["detected"]),
        "prohibited_payload_keys": prohibited,
        "files": _public_files(prepared),
        "summary": {
            "label": "DRAFT CLAIM SUMMARY FOR THE HANDLER",
            "framing": FRAMING,
            "lines": lines,
            "coverage_pointers": pointers,
            "gaps": gaps,
        },
        "inconsistency_prompts": prompts,
        "classification": classification,
        "scorecard": card,
        "sources": source_rows,
        "human_approval": {
            "classification": {
                "required": True,
                "approver": HANDLER_ROLE,
                "recorded": False,
            },
            "score_escalation": {
                "required": bool(card["human_escalation_required"]),
                "approver": HANDLER_ROLE,
                "recorded": False,
            },
            "stale_or_not_current": {
                "required": do_not_rely,
                "approver": HANDLER_ROLE,
                "recorded": False,
            },
        },
        "automated_decision_note": (
            "UK GDPR Article 22 was substituted by Articles 22A to 22D. "
            "A decline can be a significant decision where it produces a legal effect "
            "or a similarly significant effect, and it is based solely on automated "
            "processing where there is no meaningful human involvement. "
            "This draft does not take that decision. Whether a particular decline meets "
            "the test is for the data protection officer."
        ),
        "limitations": list(LIMITATIONS),
    }
    _force_inert(draft)
    return draft


def _require_draft(draft: dict) -> dict:
    if not isinstance(draft, dict) or draft.get("label") != LABEL:
        raise ValueError("draft is not a claims triage result")
    if draft.get("experiment_id") != EXPERIMENT_ID:
        raise ValueError("draft is not a claims triage result")
    return deepcopy(draft)


def record_handler_classification(
    draft: dict,
    *,
    role: str,
    classification: str,
    file_ids: list[str],
    confirms_prompts_checked: bool,
    confirms_scorecard_read: bool,
    confirms_escalation_reviewed: bool = False,
    confirms_stale_reviewed: bool = False,
    signed_on: str,
) -> dict:
    """Record a class the handler chose.

    The agent must not call this. The record does not accept, decline, settle,
    tell the customer, or write to a claims system.
    """

    if role != HANDLER_ROLE:
        raise ValueError("only a Claims handler can record a classification")
    if classification not in CLASSES:
        raise ValueError("classification is not in the closed list")
    if confirms_prompts_checked is not True or confirms_scorecard_read is not True:
        raise ValueError("the handler must confirm the prompts and the scorecard were read")
    updated = _require_draft(draft)
    if not isinstance(file_ids, list) or [file["file_id"] for file in updated["files"]] != list(file_ids):
        raise ValueError("file_ids must match the draft, in order")
    if any(file["checksum_matches"] is False for file in updated["files"]):
        raise ValueError("a file checksum does not match; the record is refused")
    if updated["scorecard"]["human_escalation_required"] and confirms_escalation_reviewed is not True:
        raise ValueError("a score under the draft threshold needs the handler to confirm the escalation was reviewed")
    if updated["do_not_rely"] and confirms_stale_reviewed is not True:
        raise ValueError("stale or not-current material needs the handler to confirm it was reviewed")
    if signed_on != updated["as_of"]:
        raise ValueError("signed_on must equal the as-of date")
    proposed = updated["classification"]["proposed_class"]
    updated["classification"]["approved_class"] = classification
    updated["classification"]["handler_record"] = {
        "role": HANDLER_ROLE,
        "classification": classification,
        "differs_from_proposal": classification != proposed,
        "signed_on": signed_on,
        "does_not_accept": True,
        "does_not_decline": True,
        "does_not_settle": True,
        "does_not_tell_the_customer": True,
        "does_not_write_the_claims_system": True,
    }
    updated["classification_approved_by_handler"] = True
    updated["human_approval"]["classification"]["recorded"] = True
    updated["human_approval"]["score_escalation"]["recorded"] = bool(
        updated["scorecard"]["human_escalation_required"]
    )
    updated["human_approval"]["stale_or_not_current"]["recorded"] = bool(updated["do_not_rely"])
    _force_inert(updated)
    return updated


def accept_claim(*_args, **_kwargs) -> None:
    raise ClaimForbidden("This agent does not accept a claim.")


def decline_claim(*_args, **_kwargs) -> None:
    raise ClaimForbidden("This agent does not decline a claim.")


def settle_claim(*_args, **_kwargs) -> None:
    raise ClaimForbidden("This agent does not settle a claim.")


def tell_customer(*_args, **_kwargs) -> None:
    raise ClaimForbidden("This agent does not tell the customer anything.")


def write_claims_system(*_args, **_kwargs) -> None:
    raise ClaimForbidden("This agent does not write to a claims system.")


def score_supplied_summary(
    pack: dict,
    candidate: dict,
    *,
    as_of: date,
    stale_after_days: int = DEFAULT_STALE_AFTER_DAYS,
    thresholds: dict | None = None,
) -> dict:
    """Score a summary someone else wrote. The claim is not declined."""

    draft = triage(pack, as_of=as_of, stale_after_days=stale_after_days, thresholds=thresholds)
    sentences = candidate.get("sentences") if isinstance(candidate, dict) else None
    if not isinstance(sentences, list) or not sentences:
        raise ValueError("candidate summary has no sentences")
    lines = []
    # Rebuild file content is not kept on the draft. Score against the pack
    # the handler supplied, using the same read and withhold rules as triage.
    intake_module = _load_intake()
    intake_draft = intake_module.intake(
        {
            "synthetic": True,
            "batch_id": pack["claim_id"],
            "requested_purpose": PURPOSE_ID,
            "files": [
                {
                    "file_id": item["file_id"],
                    "filename": item.get("filename", ""),
                    "media_type": item.get("media_type", ""),
                    "document_date": item.get("document_date"),
                    "content": item.get("content", ""),
                }
                for item in pack["files"]
            ],
        },
        as_of=as_of,
        stale_after_days=stale_after_days,
    )
    prepared = _prepare_files(pack["files"], intake_draft["files"])
    for index, sentence in enumerate(sentences, start=1):
        if not isinstance(sentence, dict):
            raise ValueError("each sentence must be an object")
        text = sentence.get("text")
        if not isinstance(text, str) or not text.strip():
            raise ValueError("a sentence has no text")
        citations = sentence.get("citations") or []
        source_id = ""
        quote = text
        if citations:
            if not isinstance(citations, list) or not isinstance(citations[0], dict):
                raise ValueError("citations must be a list of objects")
            source_id = str(citations[0].get("source_id") or "")
            quote = str(citations[0].get("quote") or "")
        lines.append(
            {
                "line_id": sentence.get("line_id") or f"candidate-{index}",
                "text": text.strip(),
                "quote": quote,
                "source_file_id": source_id,
                "role": "candidate",
            }
        )
    prose = [{"text": line["text"], "source_file_id": line["source_file_id"]} for line in lines]
    card = score_lines(
        files=prepared,
        lines=lines,
        prose=prose,
        as_of=as_of.isoformat(),
        stale_after_days=stale_after_days,
        thresholds=thresholds,
    )
    card["scored_the_agent_summary"] = False
    card["claim_declined"] = False
    card["agent_draft_claim_declined"] = draft["claim_declined"]
    return card


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Draft a claim summary for one synthetic pack.")
    parser.add_argument("--pack", required=True)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--stale-after-days", type=int, default=DEFAULT_STALE_AFTER_DAYS)
    parser.add_argument("--accept-claim", action="store_true")
    parser.add_argument("--decline-claim", action="store_true")
    parser.add_argument("--settle-claim", action="store_true")
    parser.add_argument("--tell-customer", action="store_true")
    parser.add_argument("--write-claims-system", action="store_true")
    parser.add_argument("--approve-thresholds", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.accept_claim:
            accept_claim()
        if args.decline_claim:
            decline_claim()
        if args.settle_claim:
            settle_claim()
        if args.tell_customer:
            tell_customer()
        if args.write_claims_system:
            write_claims_system()
        if args.approve_thresholds:
            approve_thresholds()
        pack = json.loads(Path(args.pack).read_text(encoding="utf-8"))
        draft = triage(
            pack,
            as_of=date.fromisoformat(args.as_of),
            stale_after_days=args.stale_after_days,
        )
    except (ClaimForbidden, NotSynthetic, ScoreForbidden) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001 — the CLI reports the type, not a file body
        print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    json.dump(draft, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
