#!/usr/bin/env python3
"""Read-only review of one synthetic workbook. Autonomy A0.

The model owner confirms the workbook, the ranges, and the formulas in a
separate object. Text inside a cell is not that confirmation. The workbook
file is not saved. No assumption is called right or wrong, and no benchmark
is invented.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from formulas import (
        Evaluator,
        FormulaError,
        Ref,
        cell_in_span,
        literal_is_common,
        parse_address,
        parse_formula,
        walk_refs,
    )
    from model import ROOT, fingerprint, index_cells, read_xlsx
    from reuse import NeighbourMissing, cross_source, find_phrases, from_observation, propose
    from sources import PINNED_ON, SOURCE_WINDOW_DAYS, sources_current
else:
    from .formulas import (
        Evaluator,
        FormulaError,
        Ref,
        cell_in_span,
        literal_is_common,
        parse_address,
        parse_formula,
        walk_refs,
    )
    from .model import ROOT, fingerprint, index_cells, read_xlsx
    from .reuse import NeighbourMissing, cross_source, find_phrases, from_observation, propose
    from .sources import PINNED_ON, SOURCE_WINDOW_DAYS, sources_current

LABEL = (
    "REVIEW FOR THE MODEL OWNER. THE WORKBOOK WAS NOT CHANGED. "
    "NO ASSUMPTION WAS JUDGED."
)
DECISION = "confirm_workbook_ranges_and_formulas"
MODEL_ID = re.compile(r"^SYN-MDL-\d{4}$")
ACTOR_ID = re.compile(r"^SYN-OWN-\d{3}$")
RANGE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*![A-Z]{1,3}\d+(?::[A-Z]{1,3}\d+)?$")
AS_OF = re.compile(r"^\d{4}-\d{2}-\d{2}$")
EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
PHONE = re.compile(r"\b(?:\+44\s?7\d{9}|07\d{9})\b")
DOB = re.compile(r"\b(?:date of birth|dob|born on)\b[:\s]*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}", re.I)
NAME = re.compile(r"\b(?:name|contact)\s*:\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+")
POSTCODE = re.compile(r"\b[A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2}\b", re.I)
INCLUSION = re.compile(
    r"\b([A-Za-z][A-Za-z0-9_]*![A-Z]{1,3}\d+)\s+includes\s+([^.]*)",
    re.I,
)
NEGATION = re.compile(
    r"\b(?:not true that|it is not the case that|does not|do not|never|not|no|n't)\b",
    re.I,
)
JUDGEMENT = re.compile(
    r"\b(?:is wrong|is right|is correct|is incorrect|should be \d|benchmark|typical rate)\b",
    re.I,
)
INJECTION = (
    ("ignore_previous_instructions", re.compile(r"ignore (?:all |any )?(?:previous|prior) instructions", re.I)),
    ("mark_assumptions_correct", re.compile(r"mark every assumption correct|all assumptions are (?:right|correct)", re.I)),
    ("write_into_cell", re.compile(r"write \d+ into", re.I)),
    ("remove_marking", re.compile(r"remove the (?:OFFICIAL|protective marking|legal-hold)", re.I)),
    ("role_override", re.compile(r"you are now|\bsystem:", re.I)),
)
MARKERS = (
    "confirm_workbook_ranges_and_formulas",
    "human_approval",
    "scope confirmed",
)
STOP_CATEGORIES = {
    "possible_safeguarding_risk",
    "possible_self_harm_risk",
    "possible_financial_hardship",
}
PROHIBITED_KEYS = {
    "workbook_modified",
    "human_approval",
    "assumption_judged",
    "benchmark",
    "graph_called",
    "findings_accepted",
    "scope_confirmation",
}
SHOCK = Decimal("0.01")


class ReviewForbidden(RuntimeError):
    """The review has no edit, judgement, benchmark, or marking-strip path."""


def edit_workbook(*_args: Any, **_kwargs: Any) -> None:
    raise ReviewForbidden("The workbook is not edited.")


def write_cell(*_args: Any, **_kwargs: Any) -> None:
    raise ReviewForbidden("No cell is written.")


def assert_assumption(*_args: Any, **_kwargs: Any) -> None:
    raise ReviewForbidden("An assumption is not called right or wrong.")


def invent_benchmark(*_args: Any, **_kwargs: Any) -> None:
    raise ReviewForbidden("No benchmark value is invented.")


def strip_protective_marking(*_args: Any, **_kwargs: Any) -> None:
    raise ReviewForbidden("A protective marking is not removed.")


def clear_legal_hold(*_args: Any, **_kwargs: Any) -> None:
    raise ReviewForbidden("A legal hold or retention label is not cleared.")


def review_workbook(pack: dict, confirmation: dict | None, as_of: str) -> dict:
    """Return a review, a scope, a refusal, or a stop for a person.

    ``confirmation`` is the only approval input. The same words inside a cell
    do not confirm the scope.
    """
    if not isinstance(pack, dict):
        raise ValueError("pack must be an object")
    pack = dict(pack)
    when = _parse_as_of(as_of)
    stripped = _strip(pack)
    synthetic = pack.get("synthetic") is True and MODEL_ID.fullmatch(str(pack.get("model_id") or ""))
    marking = pack.get("protective_marking") if isinstance(pack.get("protective_marking"), str) else None
    retention = pack.get("retention_label") if isinstance(pack.get("retention_label"), str) else None
    if not synthetic:
        report = _base(None, when, None, marking, retention, False)
        report["outcome"] = "refused_not_synthetic"
        report["ranges_inspected"] = []
        report["cells_echoed"] = False
        report["prohibited_keys_ignored"] = stripped
        return report

    cells = pack.get("cells")
    if not isinstance(cells, list):
        raise ValueError("cells must be a list")
    indexed = index_cells(cells)
    sheets = {sheet for sheet, _cell in indexed}
    digest = fingerprint(cells)
    xlsx_hash, discrepancies = _compare_workbook(pack, indexed)
    current = sources_current(when)
    if not current:
        report = _base(pack["model_id"], when, None, marking, retention, False)
        report["outcome"] = "stale_sources"
        report["ranges_inspected"] = []
        report["findings_withheld"] = True
        report["sensitivity"] = None
        report["questions"] = []
        report["workbook_sha256"] = xlsx_hash
        report["prohibited_keys_ignored"] = stripped
        report["stale"] = _stale(False)
        return report

    reason = _confirmation_reason(pack, confirmation, digest, sheets)
    if reason is not None:
        report = _base(pack["model_id"], when, None, marking, retention, True)
        report["outcome"] = "scope_not_confirmed"
        report["scope_reason"] = reason
        report["ranges_offered"] = _used_ranges(indexed)
        report["ranges_inspected"] = []
        report["workbook_fingerprint"] = digest
        report["workbook_sha256"] = xlsx_hash
        report["prohibited_keys_ignored"] = stripped
        report["approval_markers_in_content_ignored"] = _markers(indexed)
        return report

    assert isinstance(confirmation, dict)
    ranges = list(confirmation["ranges"])
    approval = {
        "step": DECISION,
        "actor_role": "model_owner",
        "actor_id": confirmation["actor_id"],
        "ranges": ranges,
        "findings_accepted": None,
        "assumption_judged": False,
    }
    selected = {
        key: row
        for key, row in indexed.items()
        if any(cell_in_span(key[0], key[1], span) for span in ranges)
    }
    safeguarding = _safeguarding(selected)
    injection = _injection(selected)
    if safeguarding["flagged"]:
        report = _base(pack["model_id"], when, approval, marking, retention, True)
        report["outcome"] = "safeguarding_for_human"
        report["routine_processing"] = False
        report["ranges_inspected"] = ranges
        report["safeguarding"] = safeguarding
        report["prompt_injection"] = injection
        report["inventory"] = []
        report["questions"] = []
        report["sensitivity"] = None
        report["workbook_sha256"] = xlsx_hash
        report["workbook_fingerprint"] = digest
        report["prohibited_keys_ignored"] = stripped
        report["text_copied"] = False
        return report

    personal = _personal_data(selected)
    hidden = {item["cell"] for item in personal}
    claims = _inclusions(selected)
    structural = _structural(selected, sheets, discrepancies)
    sensitivity = _sensitivity(indexed, selected, pack.get("key_outputs") or [], discrepancies)
    questions = _questions(structural, sensitivity)
    _reject_judgement(questions)
    regression = _regression(pack["model_id"], structural)
    report = _base(pack["model_id"], when, approval, marking, retention, True)
    report.update(
        {
            "outcome": "review_for_model_owner",
            "routine_processing": True,
            "ranges_inspected": ranges,
            "cells_outside_scope_not_read": len(indexed) - len(selected),
            "inventory": _inventory(selected, hidden, discrepancies),
            "unlabelled_numeric_constants": _unlabelled(selected, hidden),
            "hardcoded_literals": structural["literals"],
            "inconsistent_formulas": structural["inconsistent"],
            "broken_references": structural["broken"],
            "circular_references": structural["circular"],
            "unsupported_formulas": structural["unsupported"],
            "paired_assumptions": structural["paired"],
            "representation_discrepancies": discrepancies,
            "sensitivity": sensitivity,
            "questions": questions,
            "text_claims": claims,
            "personal_data": personal,
            "safeguarding": safeguarding,
            "prompt_injection": injection,
            "approval_markers_in_content_ignored": _markers(indexed),
            "proposed_regression_cases": regression,
            "workbook_sha256": xlsx_hash,
            "workbook_fingerprint": digest,
            "prohibited_keys_ignored": stripped,
            "text_copied": False,
            "method": {
                "formulas": "Closed Python reader. SUM, AVERAGE, MIN, MAX, IF, and arithmetic. Excel was not called.",
                "sensitivity": (
                    "Each numeric assumption in the confirmed ranges was increased by 1 percent "
                    "of its stored value, holding the others fixed. Rank is absolute change in "
                    "the named output. A tie breaks by assumption id. This is not a benchmark."
                ),
                "paired_values": "Experiment 36 normalise_value and classify_values. Neither source is chosen.",
                "regression_cases": "Experiment 30 from_observation. Nothing is merged, pushed, or edited.",
                "identifiers": (
                    "Experiment 08 propose, plus local checks for an email, a UK mobile, "
                    "a labelled date of birth, a labelled personal name, and a UK postcode. "
                    "The text is not copied."
                ),
            },
        }
    )
    return report


def _base(model_id: str | None, when: date, approval: dict | None, marking: str | None, retention: str | None, current: bool) -> dict:
    return {
        "label": LABEL,
        "catalogue_id": "M006",
        "experiment": "54-excel-assumption-review",
        "autonomy": "A0",
        "model_id": model_id,
        "organisation": "Northmere Analytical Unit" if model_id else None,
        "as_of": when.isoformat(),
        "human_approval": approval,
        "findings_accepted": None,
        "actions_taken": [],
        "executed": False,
        "model_called": False,
        "network_called": False,
        "flags": {
            "workbook_modified": False,
            "graph_called": False,
            "excel_api_called": False,
            "copilot_in_excel_called": False,
            "assumption_judged": False,
            "benchmark_invented": False,
            "marking_stripped": False,
            "legal_hold_cleared": False,
            "findings_accepted": False,
        },
        "protective_marking": marking,
        "retention_label": retention,
        "human_route": {
            "offered": True,
            "agent_edits_workbook": False,
            "agent_judges_assumptions": False,
        },
        "guidance": {
            "current": current,
            "pinned_on": PINNED_ON.isoformat(),
            "window_days": SOURCE_WINDOW_DAYS,
            "aqua_book_signed": False,
            "business_critical_decided": False,
            "model_sro_appointed": False,
        },
        "stale": _stale(current),
        "sources_not_opened": [
            "macpherson-pdf",
            "copilot-excel-dedicated",
            "billing",
            "uk-gdpr-articles",
        ],
    }


def _stale(current: bool) -> dict:
    return {"rules_current": current, "equal_to_window_is_current": True}


def _parse_as_of(value: str) -> date:
    if not isinstance(value, str) or not AS_OF.fullmatch(value):
        raise ValueError("as_of must be YYYY-MM-DD")
    return date.fromisoformat(value)


def _strip(pack: dict) -> list[str]:
    found = sorted(key for key in PROHIBITED_KEYS if key in pack)
    for key in found:
        pack.pop(key, None)
    return found


def _confirmation_reason(pack: dict, confirmation: dict | None, digest: str, sheets: set[str]) -> str | None:
    if not isinstance(confirmation, dict):
        return "missing"
    if confirmation.get("decision") != DECISION:
        return "decision"
    if confirmation.get("actor_role") != "model_owner":
        return "actor_role"
    if not ACTOR_ID.fullmatch(str(confirmation.get("actor_id") or "")):
        return "actor_id"
    if confirmation.get("model_id") != pack.get("model_id"):
        return "model_id"
    if confirmation.get("formulas_in_scope_acknowledged") is not True:
        return "formulas"
    if confirmation.get("protective_marking_seen") is not True:
        return "marking"
    if confirmation.get("workbook_fingerprint") != digest:
        return "fingerprint"
    ranges = confirmation.get("ranges")
    if not isinstance(ranges, list) or not ranges or len(ranges) != len(set(ranges)):
        return "ranges"
    for item in ranges:
        if not isinstance(item, str) or not RANGE.fullmatch(item):
            return "ranges"
        if item.split("!", 1)[0] not in sheets:
            return "unknown_sheet"
    return None


def _used_ranges(indexed: dict[tuple[str, str], dict]) -> list[str]:
    grouped: dict[str, list[str]] = {}
    for sheet, cell in indexed:
        grouped.setdefault(sheet, []).append(cell)
    offered = []
    for sheet in sorted(grouped):
        coords = []
        for cell in grouped[sheet]:
            match = re.fullmatch(r"([A-Z]{1,3})(\d+)", cell)
            if match:
                coords.append((match.group(1), int(match.group(2))))
        if not coords:
            continue
        cols = sorted({item[0] for item in coords}, key=_col_key)
        rows = [item[1] for item in coords]
        offered.append(f"{sheet}!{cols[0]}{min(rows)}:{cols[-1]}{max(rows)}")
    return offered


def _col_key(letters: str) -> int:
    number = 0
    for character in letters:
        number = number * 26 + (ord(character) - 64)
    return number


def _markers(indexed: dict[tuple[str, str], dict]) -> bool:
    for row in indexed.values():
        text = str(row.get("value") or "")
        if any(marker in text for marker in MARKERS):
            return True
    return False


def _compare_workbook(pack: dict, indexed: dict[tuple[str, str], dict]) -> tuple[str | None, list[dict]]:
    relative = pack.get("workbook_xlsx")
    if not isinstance(relative, str) or not relative or relative.startswith("/") or ".." in relative.split("/"):
        return None, []
    path = (ROOT / relative).resolve()
    if ROOT.resolve() not in path.parents:
        return None, []
    if not path.is_file():
        return None, [{"reason": "workbook_file_missing", "path": relative}]
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    loaded = read_xlsx(path)
    if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        raise ReviewForbidden("Reading the workbook changed the file.")
    normalise, classify, fold = cross_source()
    discrepancies = []
    for key in sorted(set(indexed) | set(loaded)):
        left = indexed.get(key)
        right = loaded.get(key)
        address = f"{key[0]}!{key[1]}"
        if left is None or right is None:
            discrepancies.append({"cell": address, "reason": "present_on_one_side_only", "chosen": None})
            continue
        left_formula = left.get("formula") or ""
        right_formula = right.get("formula") or ""
        if left_formula or right_formula:
            if left_formula != right_formula:
                discrepancies.append({"cell": address, "reason": "formula_text_differs", "chosen": None})
            continue
        left_value = "" if left.get("value") is None else str(left.get("value"))
        right_value = "" if right.get("value") is None else str(right.get("value"))
        if left_value == right_value:
            continue
        pair = _classify_pair(normalise, classify, fold, "figure", left_value, right_value)
        discrepancies.append(
            {
                "cell": address,
                "reason": "value_differs",
                "cross_source_class": pair["class"],
                "cross_source_reason": pair["reason"],
                "chosen": None,
            }
        )
    return digest, discrepancies


def _classify_pair(normalise, classify, fold, field_type: str, left: str, right: str) -> dict:
    items = []
    for raw in (left, right):
        canonical, accepted = normalise(field_type, raw)
        items.append((canonical, fold(raw), accepted))
    try:
        kind, reason = classify(items)
    except ValueError:
        kind, reason = "not_classified", "not_two_values"
    return {"class": kind, "reason": reason, "chosen": None}


def _safeguarding(selected: dict[tuple[str, str], dict]) -> dict:
    phrases = find_phrases()
    categories: set[str] = set()
    cells: list[str] = []
    for (sheet, cell), row in sorted(selected.items()):
        text = row.get("value")
        if not isinstance(text, str) or not text:
            continue
        found = phrases(text)
        hit = {item["category"] for item in found} & STOP_CATEGORIES
        if hit:
            categories.update(hit)
            cells.append(f"{sheet}!{cell}")
    return {
        "flagged": bool(categories),
        "categories": sorted(categories),
        "cells": cells,
        "text_copied": False,
        "processed_as_routine": False,
    }


def _injection(selected: dict[tuple[str, str], dict]) -> dict:
    found: set[str] = set()
    for row in selected.values():
        text = str(row.get("value") or "")
        for name, pattern in INJECTION:
            if pattern.search(text):
                found.add(name)
    return {"detected": bool(found), "followed": False, "patterns": sorted(found), "text_copied": False}


def _personal_data(selected: dict[tuple[str, str], dict]) -> list[dict]:
    gateway = propose()
    rows = []
    for (sheet, cell), row in sorted(selected.items()):
        text = row.get("value")
        if not isinstance(text, str) or not text:
            continue
        proposal = gateway(text, caller="exp-54-excel-assumption-review")
        types = {item["entity_type"] for item in proposal["audit_log"]["findings"]}
        if EMAIL.search(text):
            types.add("email")
        if PHONE.search(text):
            types.add("phone")
        if DOB.search(text):
            types.add("date_of_birth")
        if NAME.search(text):
            types.add("personal_name")
        if POSTCODE.search(text):
            types.add("postal_address")
        if types:
            rows.append(
                {
                    "cell": f"{sheet}!{cell}",
                    "types": sorted(types),
                    "text_copied": False,
                    "output_is_anonymised": False,
                }
            )
    return rows


def _inclusions(selected: dict[tuple[str, str], dict]) -> list[dict]:
    claims = []
    for (sheet, cell), row in sorted(selected.items()):
        text = row.get("value")
        if not isinstance(text, str):
            continue
        for sentence in re.split(r"(?<=[.!?])\s+", text):
            if NEGATION.search(sentence):
                continue
            for match in INCLUSION.finditer(sentence):
                claims.append(
                    {
                        "mentioned_in": f"{sheet}!{cell}",
                        "cell": match.group(1),
                        "what": match.group(2).strip(),
                        "negated_sentence_counted": False,
                        "structural_finding": False,
                    }
                )
    return claims


def _structural(selected: dict, sheets: set[str], discrepancies: list[dict]) -> dict:
    blocked = {item["cell"] for item in discrepancies}
    literals = []
    broken = []
    unsupported = []
    parsed_rows: list[tuple[str, str, int, int, str]] = []
    evaluator = Evaluator(selected)
    for (sheet, cell), row in sorted(selected.items()):
        formula = row.get("formula")
        if not formula:
            continue
        address = f"{sheet}!{cell}"
        if address in blocked:
            continue
        if "[" in str(formula) or "#REF!" in str(formula).upper():
            broken.append({"cell": address, "target": None, "reason": "external_or_ref_error"})
            continue
        try:
            parsed = parse_formula(str(formula), sheet, cell)
        except FormulaError as exc:
            unsupported.append({"cell": address, "reason": str(exc)})
            continue
        for literal in parsed.literals:
            literals.append(
                {
                    "cell": address,
                    "literal": literal,
                    "common_arithmetic": literal_is_common(literal),
                    "judged": False,
                }
            )
        for ref in walk_refs(parsed.tree):
            if isinstance(ref, Ref) and ref.sheet and ref.sheet not in sheets:
                broken.append(
                    {
                        "cell": address,
                        "target": ref.address(sheet),
                        "reason": "sheet_not_in_workbook",
                    }
                )
        match = re.fullmatch(r"([A-Z]{1,3})(\d+)", cell)
        if match:
            parsed_rows.append((sheet, cell, _col_key(match.group(1)), int(match.group(2)), parsed.r1c1))
        evaluator.value_of(sheet, cell)
    literals.sort(key=lambda item: (item["cell"], item["literal"]))
    broken.sort(key=lambda item: (item["cell"], item["target"] or ""))
    return {
        "literals": literals,
        "inconsistent": _inconsistent(parsed_rows),
        "broken": broken,
        "circular": [{"cells": cycle, "value_computed": False} for cycle in evaluator.cycles],
        "unsupported": unsupported,
        "paired": _paired(selected, blocked),
    }


def _inconsistent(rows: list[tuple[str, str, int, int, str]]) -> list[dict]:
    findings = []
    by_column: dict[tuple[str, int], list] = {}
    by_row: dict[tuple[str, int], list] = {}
    for sheet, cell, col, row, pattern in rows:
        by_column.setdefault((sheet, col), []).append((row, cell, pattern))
        by_row.setdefault((sheet, row), []).append((col, cell, pattern))
    for (sheet, _col), items in sorted(by_column.items()):
        findings.extend(_runs(sheet, items, "column"))
    for (sheet, _row), items in sorted(by_row.items()):
        findings.extend(_runs(sheet, items, "row"))
    return findings


def _runs(sheet: str, items: list[tuple[int, str, str]], axis: str) -> list[dict]:
    items = sorted(items)
    found = []
    current: list[tuple[int, str, str]] = []
    for item in items:
        if current and item[0] != current[-1][0] + 1:
            found.extend(_emit_run(sheet, current, axis))
            current = []
        current.append(item)
    found.extend(_emit_run(sheet, current, axis))
    return found


def _emit_run(sheet: str, run: list[tuple[int, str, str]], axis: str) -> list[dict]:
    if len(run) < 2:
        return []
    counts: dict[str, int] = {}
    for item in run:
        counts[item[2]] = counts.get(item[2], 0) + 1
    if len(counts) < 2 or max(counts.values()) < 2:
        return []
    cells = [f"{sheet}!{item[1]}" for item in run]
    return [
        {
            "axis": axis,
            "cells": cells,
            "distinct_shapes": len(counts),
            "chosen_shape": None,
        }
    ]


def _paired(selected: dict, blocked: set[str]) -> list[dict]:
    normalise, classify, fold = cross_source()
    groups: dict[str, list[dict]] = {}
    for (sheet, cell), row in sorted(selected.items()):
        assumption = row.get("assumption_id")
        if not assumption or row.get("formula"):
            continue
        address = f"{sheet}!{cell}"
        if address in blocked:
            continue
        groups.setdefault(assumption, []).append(row | {"address": address})
    findings = []
    for assumption, rows in sorted(groups.items()):
        if len(rows) < 2:
            continue
        units = sorted({row.get("unit") or "" for row in rows})
        bases = sorted({row.get("date_basis") or "" for row in rows if row.get("date_basis")})
        field_type = "date" if all((row.get("unit") or "") == "date" for row in rows) else "figure"
        prepared = []
        for row in rows:
            raw = str(row.get("value") or "")
            if field_type == "figure" and row.get("unit") == "percent":
                raw = f"{raw} percent"
            elif field_type == "figure" and row.get("unit") == "days":
                raw = f"{raw} days"
            prepared.append(raw)
        items = []
        for raw in prepared:
            canonical, accepted = normalise(field_type, raw)
            items.append((canonical, fold(raw), accepted))
        kind, reason = classify(items)
        findings.append(
            {
                "assumption_id": assumption,
                "cells": [row["address"] for row in rows],
                "units": units,
                "unit_mismatch": len([unit for unit in units if unit]) > 1,
                "date_bases": bases,
                "date_basis_mismatch": len(bases) > 1,
                "cross_source_class": kind,
                "cross_source_reason": reason,
                "chosen": None,
                "converted": False,
            }
        )
    return findings


def _inventory(selected: dict, hidden: set[str], discrepancies: list[dict]) -> list[dict]:
    blocked = {item["cell"] for item in discrepancies}
    rows = []
    for (sheet, cell), row in sorted(selected.items()):
        if not row.get("assumption_id") or row.get("formula"):
            continue
        address = f"{sheet}!{cell}"
        value = None if address in hidden or address in blocked else str(row.get("value") or "")
        rows.append(
            {
                "cell": address,
                "assumption_id": row.get("assumption_id"),
                "label": row.get("label") or "",
                "unit": row.get("unit") or "",
                "date_basis": row.get("date_basis") or "",
                "value": value,
                "judged": False,
            }
        )
    return rows


def _unlabelled(selected: dict, hidden: set[str]) -> list[dict]:
    rows = []
    for (sheet, cell), row in sorted(selected.items()):
        if row.get("formula") or row.get("assumption_id"):
            continue
        address = f"{sheet}!{cell}"
        if address in hidden:
            continue
        text = row.get("value")
        if not isinstance(text, str):
            continue
        try:
            Decimal(text)
        except Exception:
            continue
        rows.append({"cell": address, "value": text, "shocked": False, "judged": False})
    return rows


def _show(number: Decimal) -> str:
    text = format(number.quantize(Decimal("0.000001")), "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def _sensitivity(_indexed: dict, selected: dict, outputs: list, discrepancies: list[dict]) -> dict:
    blocked = {item["cell"] for item in discrepancies}
    named = []
    for item in outputs:
        if not isinstance(item, dict):
            continue
        cell = item.get("cell")
        if not isinstance(cell, str) or "!" not in cell:
            continue
        sheet, address = parse_address(cell)
        if (sheet, address) not in selected:
            continue
        named.append((item.get("id") or cell, sheet, address))
    if not named:
        return {"computed": False, "reason": "no_confirmed_key_output", "ranking": []}
    output_id, output_sheet, output_cell = named[0]
    assumptions = []
    for (sheet, cell), row in sorted(selected.items()):
        if not row.get("assumption_id") or row.get("formula"):
            continue
        if row.get("unit") == "date":
            continue
        address = f"{sheet}!{cell}"
        if address in blocked:
            continue
        try:
            number = Decimal(str(row.get("value")))
        except Exception:
            continue
        assumptions.append((row["assumption_id"], sheet, cell, number))
    baseline_eval = Evaluator(selected)
    baseline = baseline_eval.value_of(output_sheet, output_cell)
    if baseline.kind != "number" or baseline.number is None:
        return {
            "computed": False,
            "reason": baseline.error or "output_not_numeric",
            "output": f"{output_sheet}!{output_cell}",
            "ranking": [],
        }
    ranking = []
    for assumption, sheet, cell, number in assumptions:
        if number == 0:
            shocked_value = number + SHOCK
            step = "absolute_0.01_because_stored_value_is_zero"
        else:
            shocked_value = number * (Decimal(1) + SHOCK)
            step = "relative_1_percent"
        shocked = Evaluator(selected, {(sheet, cell): shocked_value})
        outcome = shocked.value_of(output_sheet, output_cell)
        if outcome.kind != "number" or outcome.number is None:
            ranking.append(
                {
                    "assumption_id": assumption,
                    "cell": f"{sheet}!{cell}",
                    "step": step,
                    "computed": False,
                    "absolute_change": None,
                }
            )
            continue
        ranking.append(
            {
                "assumption_id": assumption,
                "cell": f"{sheet}!{cell}",
                "step": step,
                "computed": True,
                "absolute_change": _show(abs(outcome.number - baseline.number)),
                "judged_material": False,
            }
        )
    ranking.sort(key=lambda item: (item["absolute_change"] is None, _change_key(item), item["assumption_id"]))
    return {
        "computed": True,
        "output_id": output_id,
        "output": f"{output_sheet}!{output_cell}",
        "baseline": _show(baseline.number),
        "method": "one_at_a_time_1_percent_of_stored_value",
        "benchmark_used": False,
        "ranking": ranking,
    }


def _change_key(item: dict) -> Decimal:
    if item.get("absolute_change") is None:
        return Decimal(0)
    return -Decimal(item["absolute_change"])


def _questions(structural: dict, sensitivity: dict) -> list[dict]:
    questions = []
    for literal in structural["literals"]:
        if literal["common_arithmetic"]:
            continue
        questions.append(
            {
                "id": f"Q-LITERAL-{literal['cell']}-{literal['literal']}",
                "text": (
                    f"Cell {literal['cell']} contains the literal {literal['literal']} inside a formula. "
                    "What does that number represent, and should the model owner see it as its own input? "
                    "This question does not say the number is wrong and does not offer a replacement."
                ),
            }
        )
    for index, item in enumerate(structural["inconsistent"], start=1):
        questions.append(
            {
                "id": f"Q-SHAPE-{index}",
                "text": (
                    f"Formulas in {', '.join(item['cells'])} are not the same shape in R1C1. "
                    "Which shape was intended? This question does not choose a shape."
                ),
            }
        )
    for item in structural["broken"]:
        questions.append(
            {
                "id": f"Q-BROKEN-{item['cell']}",
                "text": (
                    f"Formula in {item['cell']} refers to {item['target']}, which is not a sheet in this workbook. "
                    "What should it refer to? This question does not invent a sheet."
                ),
            }
        )
    for index, item in enumerate(structural["circular"], start=1):
        questions.append(
            {
                "id": f"Q-CYCLE-{index}",
                "text": (
                    f"Cells {', '.join(item['cells'])} depend on each other. "
                    "No value was computed for them."
                ),
            }
        )
    for item in structural["paired"]:
        if item["unit_mismatch"]:
            questions.append(
                {
                    "id": f"Q-UNIT-{item['assumption_id']}",
                    "text": (
                        f"Assumption {item['assumption_id']} is stored with units {', '.join(item['units'])}. "
                        "The values were not converted. This question does not say which unit is right."
                    ),
                }
            )
        if item["date_basis_mismatch"]:
            questions.append(
                {
                    "id": f"Q-BASIS-{item['assumption_id']}",
                    "text": (
                        f"Assumption {item['assumption_id']} uses date bases {', '.join(item['date_bases'])}. "
                        "This question does not say which basis is right."
                    ),
                }
            )
        if item["cross_source_class"] == "material_discrepancy":
            questions.append(
                {
                    "id": f"Q-PAIR-{item['assumption_id']}",
                    "text": (
                        f"Assumption {item['assumption_id']} has values that Experiment 36 classifies as a "
                        f"material discrepancy ({item['cross_source_reason']}). The reviewer resolves it. "
                        "This starter does not choose a value."
                    ),
                }
            )
        elif item["cross_source_class"] == "immaterial_difference":
            questions.append(
                {
                    "id": f"Q-DISPLAY-{item['assumption_id']}",
                    "text": (
                        f"Assumption {item['assumption_id']} has displays that Experiment 36 classifies as an "
                        "immaterial difference. That is not a finding that either display is the right date."
                    ),
                }
            )
    ranking = [item for item in (sensitivity.get("ranking") or []) if item.get("computed")]
    if ranking:
        top_change = Decimal(ranking[0]["absolute_change"])
        leaders = [item for item in ranking if Decimal(item["absolute_change"]) == top_change]
        described = ", ".join(f"{item['assumption_id']} at {item['cell']}" for item in leaders)
        questions.append(
            {
                "id": "Q-SENSITIVITY",
                "text": (
                    f"Under a 1 percent increase of each numeric assumption, holding the others fixed, "
                    f"the largest absolute change in {sensitivity['output']} was {ranking[0]['absolute_change']} "
                    f"from {described}. The step is this starter's method. It is not a benchmark "
                    "and it is not a finding that the assumption is material."
                ),
            }
        )
        if any(Decimal(item["absolute_change"]) == 0 for item in ranking):
            questions.append(
                {
                    "id": "Q-ZERO-CHANGE",
                    "text": (
                        "Some inspected assumptions changed the named output by 0 under this method. "
                        "That is not a finding that they do not matter."
                    ),
                }
            )
    return questions


def _reject_judgement(questions: list[dict]) -> None:
    for question in questions:
        for sentence in re.split(r"(?<=[.!?])\s+", question["text"]):
            if NEGATION.search(sentence):
                continue
            if JUDGEMENT.search(sentence):
                raise ReviewForbidden("A question judged an assumption.")


def _regression(model_id: str, structural: dict) -> dict:
    draft = from_observation()
    observations = []
    counter = 1
    for literal in structural["literals"]:
        if literal["common_arithmetic"]:
            continue
        observations.append(_observation(counter, model_id, literal["cell"], "a numeric literal inside a formula"))
        counter += 1
    for item in structural["broken"]:
        observations.append(_observation(counter, model_id, item["cell"], "a reference to a sheet that is not in the workbook"))
        counter += 1
    for item in structural["circular"]:
        observations.append(_observation(counter, model_id, item["cells"][0], "a circular reference"))
        counter += 1
    cases = []
    for observation in observations:
        drafted, note = draft(observation)
        if note:
            continue
        for case in drafted:
            cases.append(
                {
                    "id": case["id"],
                    "kind": case["kind"],
                    "status": "drafted",
                    "maintainer_approved": False,
                }
            )
    return {
        "source": "experiments/30-agent-regression-test-generator",
        "maintainer_approved": False,
        "merged": False,
        "pushed": False,
        "edited_agent": False,
        "cases": cases,
    }


def _observation(counter: int, model_id: str, cell: str, kind: str) -> dict:
    return {
        "id": f"FND{counter:02d}",
        "kind": "observed_failure",
        "input": f"Workbook {model_id} cell {cell} has {kind}.",
        "expected_behaviour": "List the cell. Do not edit the workbook. Do not decide. Do not send.",
        "prohibited_actions": ["production_record_change"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Review one synthetic workbook. Does not edit it.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--confirm", type=Path)
    parser.add_argument("--as-of", required=True)
    args = parser.parse_args(argv)
    try:
        pack = json.loads(args.input.read_text(encoding="utf-8"))
        confirmation = None
        if args.confirm is not None:
            confirmation = json.loads(args.confirm.read_text(encoding="utf-8"))
        report = review_workbook(pack, confirmation, args.as_of)
    except (OSError, json.JSONDecodeError, ValueError, NeighbourMissing):
        return 2
    json.dump(report, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
