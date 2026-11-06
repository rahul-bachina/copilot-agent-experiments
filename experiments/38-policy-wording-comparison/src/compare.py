"""Compare two or more synthetic policy wordings.

Every stated clause is a copy of named lines, with a pinpoint citation that
includes the clause reference. A topic and subject that one wording states and
another does not is "not stated". Nothing is inferred. The difference class is
a textual rule. It is not a favourability finding and not a recommendation.

Autonomy is A0. compare() does not interpret favourability, recommend buy, sell,
or renew, draft an endorsement, contact a broker, or write to a policy
administration system. A wording specialist validates every interpretation.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from src.citations import (  # type: ignore
        VERDICTS,
        check_quote,
        document_block_reason,
        empty_verdict_counts,
        normalise,
    )
    from src.document_intake import inventory
    from src.injection import hidden_payloads, injection_codes, prohibited_codes, strip_prohibited
    from src.siblings import CompareForbidden, load
    from src.sources import DEFAULT_STALE_AFTER_DAYS, pin_rows, regulatory_notes
else:
    from .citations import (
        VERDICTS,
        check_quote,
        document_block_reason,
        empty_verdict_counts,
        normalise,
    )
    from .document_intake import inventory
    from .injection import hidden_payloads, injection_codes, prohibited_codes, strip_prohibited
    from .siblings import CompareForbidden, load
    from .sources import DEFAULT_STALE_AFTER_DAYS, pin_rows, regulatory_notes

LABEL = "DRAFT FOR THE WORDING SPECIALIST. NOT A COVERAGE OPINION AND NOT A RECOMMENDATION."
CATALOGUE_ID = "B008"
EXPERIMENT_ID = "exp-38-policy-wording-comparison"
NOT_STATED = "not stated"
TOPICS = (
    "coverage_grant",
    "exclusion",
    "condition",
    "warranty",
    "definition",
    "limit",
    "deductible",
    "notice_provision",
)
TOPIC_INDEX = {name: index for index, name in enumerate(TOPICS)}
MARKET_LABELS = frozenset({"commercial_non_consumer", "retail"})
ROLES = frozenset({"expiring", "renewal_quote", "competing_quote", "endorsement", "schedule", "other"})
WORDING_ID = re.compile(r"^[a-z][a-z0-9-]{0,39}$")
SUBJECT_KEY = re.compile(r"^[a-z][a-z0-9_]{0,40}$")
CLAUSE_REF = re.compile(r"^[A-Za-z0-9][A-Za-z0-9.()\-]{0,39}$")
SPECIALIST_REF = re.compile(r"^WS-\d{4}$")
MIN_WORDINGS = 2
MAX_WORDINGS = 4
MAX_WORD_DIFF = 12

DIFFERENCE_FROM_36 = (
    "Experiment 36 classifies one fact across source documents as a match, an immaterial "
    "difference, or a material discrepancy, and a reviewer resolves each material row. "
    "This experiment uses the same idea of a fixed class and a human resolution, for "
    "policy clauses. It does not import Experiment 36. A class here means the normalised "
    "text differs, or a topic is absent from one wording. It does not choose which wording "
    "is right and it does not say which is more favourable."
)
DIFFERENCE_FROM_37 = (
    "Experiment 37 copies lines from one submission into a closed field list. A missing "
    "field is not stated. This experiment uses that citation rule across two or more "
    "wordings. It does not import Experiment 37. It does not summarise a submission and "
    "it does not price a risk."
)
DIFFERENCE_FROM_33 = (
    "Experiment 33's resolve_span and normalise are called for each quote. A paraphrase "
    "fails. This experiment does not summarise a case bundle and does not recommend an outcome."
)
DIFFERENCE_FROM_12 = (
    "Experiment 12 inventories the text files. No purpose is requested, so nothing is "
    "routed. A file that was not read, is outside the date window, or has a deterministic "
    "identifier finding is not quoted."
)
DIFFERENCE_FROM_29 = (
    "Experiment 29's number and date boundary check is called. Its token-overlap verdict "
    "is not used. Support is the contiguous span. There is no threshold and no release."
)


class NotSynthetic(ValueError):
    """The pack was not marked synthetic. The message does not include the body."""


def interpret_favourability(*_args: Any, **_kwargs: Any) -> None:
    raise CompareForbidden("The agent does not interpret favourability for the insured or the insurer.")


def recommend_buy_sell_renew(*_args: Any, **_kwargs: Any) -> None:
    raise CompareForbidden("The agent does not recommend buy, sell, or renew.")


def draft_endorsement(*_args: Any, **_kwargs: Any) -> None:
    raise CompareForbidden("The agent does not draft an endorsement.")


def contact_broker(*_args: Any, **_kwargs: Any) -> None:
    raise CompareForbidden("The agent does not contact the broker.")


def write_policy_admin(*_args: Any, **_kwargs: Any) -> None:
    raise CompareForbidden("The agent does not write to a policy administration system.")


def decide_coverage(*_args: Any, **_kwargs: Any) -> None:
    raise CompareForbidden("The agent does not make a coverage decision.")


def recommend_autonomy_a3(*_args: Any, **_kwargs: Any) -> None:
    raise CompareForbidden("The agent does not recommend autonomy A3.")


def release_evaluation(*_args: Any, **_kwargs: Any) -> None:
    raise CompareForbidden("The agent does not release an evaluation as a decision.")


def _parse_day(value: str, label: str) -> date:
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} is not a calendar date.") from exc


def _market_label(value: Any) -> str:
    if value is None or value == "":
        return "not_stated"
    if isinstance(value, str) and value in MARKET_LABELS:
        return value
    return "unrecognised"


def _role(value: Any) -> str:
    if value is None or value == "":
        return "not_stated"
    if isinstance(value, str) and value in ROLES:
        return value
    return "unrecognised"


def _paragraph_lines(paragraph: dict[str, Any]) -> list[dict[str, Any]] | None:
    rows = paragraph.get("lines")
    if not isinstance(rows, list) or not rows:
        return None
    parsed: list[tuple[int, str]] = []
    for row in rows:
        if not isinstance(row, dict):
            return None
        number = row.get("line")
        if isinstance(number, bool) or not isinstance(number, int):
            return None
        parsed.append((number, str(row.get("text") or "")))
    parsed.sort(key=lambda item: item[0])
    numbers = [number for number, _text in parsed]
    if numbers != list(range(numbers[0], numbers[-1] + 1)):
        return None
    return [{"line": number, "text": text} for number, text in parsed]


def _joined(lines: list[dict[str, Any]]) -> str:
    return " ".join(row["text"].strip() for row in lines if row["text"].strip())


def _decision_flags() -> dict[str, Any]:
    return {
        "favourable_to": None,
        "recommendation": None,
        "endorsement_draft": None,
        "broker_contacted": False,
        "policy_admin_written": False,
        "coverage_decision": None,
        "baseline_wording": None,
        "chosen_wording": None,
        "interpretation_acknowledged": False,
        "downstream_use_permitted": False,
        "solely_automated_decision": False,
        "market_label_decided_by_agent": False,
        "role_interpreted": False,
        "basis_clause_of_no_effect": None,
        "model_called": False,
        "network_called": False,
        "foundry_called": False,
        "document_intelligence_called": False,
        "a3_recommended": False,
        "actions_taken": [],
        "experiment_36_imported": False,
        "experiment_37_imported": False,
        "evaluation_released": False,
    }


def _index_documents(wordings: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for wording in wordings:
        for document in wording.get("documents") or []:
            document_id = str(document.get("document_id") or "").strip()
            if not document_id:
                raise ValueError("A document has no document_id.")
            if document_id in index:
                raise ValueError(f"Duplicate document id {document_id}.")
            index[document_id] = document
    return index


def _scan_hits(text: str) -> list[str]:
    codes = injection_codes(text) + [code for code in prohibited_codes(text) if code not in injection_codes(text)]
    for hidden in hidden_payloads(text):
        for code in injection_codes(hidden["text"]) + prohibited_codes(hidden["text"]):
            if code not in codes:
                codes.append(code)
    return codes


def _extract(
    wordings: list[dict[str, Any]],
    documents: dict[str, dict[str, Any]],
    as_of: str,
    stale_after_days: int,
    intake_files: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    quotes: list[dict[str, Any]] = []
    unaligned: list[dict[str, Any]] = []
    not_used: list[dict[str, Any]] = []
    injection_rows: list[dict[str, Any]] = []
    for wording in wordings:
        wording_id = wording["wording_id"]
        for document in wording.get("documents") or []:
            document_id = str(document.get("document_id") or "").strip()
            reason = document_block_reason(document, as_of, stale_after_days, intake_files)
            if reason:
                not_used.append(
                    {
                        "wording_id": wording_id,
                        "document_id": document_id,
                        "reason": reason,
                        "quoted": False,
                    }
                )
                continue
            for page in document.get("pages") or []:
                page_number = page.get("page")
                for paragraph in page.get("paragraphs") or []:
                    lines = _paragraph_lines(paragraph)
                    if lines is None:
                        not_used.append(
                            {
                                "wording_id": wording_id,
                                "document_id": document_id,
                                "reason": "line_numbers_not_contiguous",
                                "quoted": False,
                            }
                        )
                        continue
                    raw = _joined(lines)
                    hits = _scan_hits(raw)
                    if hits:
                        injection_rows.append(
                            {
                                "wording_id": wording_id,
                                "document_id": document_id,
                                "page": page_number,
                                "paragraph": paragraph.get("paragraph"),
                                "codes": hits,
                                "followed": False,
                                "copied": False,
                            }
                        )
                        continue
                    topic = paragraph.get("topic")
                    subject = paragraph.get("subject")
                    clause_ref = paragraph.get("clause_ref")
                    citation = {
                        "wording_id": wording_id,
                        "document_id": document_id,
                        "clause_ref": clause_ref if isinstance(clause_ref, str) else None,
                        "page": page_number,
                        "paragraph": paragraph.get("paragraph"),
                        "line_start": lines[0]["line"],
                        "line_end": lines[-1]["line"],
                    }
                    topic_ok = isinstance(topic, str) and topic in TOPICS
                    subject_ok = isinstance(subject, str) and bool(SUBJECT_KEY.fullmatch(subject))
                    if not topic_ok or not subject_ok:
                        if not isinstance(topic, str) or topic == "":
                            alignment = "topic_not_stated"
                        elif topic not in TOPICS:
                            alignment = "topic_not_in_closed_list"
                        else:
                            alignment = "subject_not_stated"
                        pending = {
                            "text": raw,
                            "citation": citation,
                            "topic": topic if topic_ok else NOT_STATED,
                            "subject": subject if subject_ok else NOT_STATED,
                            "alignment": alignment,
                        }
                        checked = check_quote(pending, documents, as_of, stale_after_days, intake_files)
                        checked["unaligned_id"] = f"unaligned-{len(unaligned) + 1}"
                        checked["topic"] = pending["topic"] if topic_ok else NOT_STATED
                        checked["subject"] = pending["subject"] if subject_ok else NOT_STATED
                        checked["alignment"] = pending["alignment"]
                        checked["inferred"] = False
                        if not topic_ok:
                            checked["topic"] = NOT_STATED
                        unaligned.append(checked)
                        continue
                    if not isinstance(clause_ref, str) or not CLAUSE_REF.fullmatch(clause_ref):
                        citation["clause_ref"] = None
                    quotes.append(
                        {
                            "topic": topic,
                            "subject": subject,
                            "wording_id": wording_id,
                            "text": raw,
                            "citation": citation,
                        }
                    )
    return quotes, unaligned, not_used, injection_rows


def _numbers(text: str) -> list[str]:
    return load()["score"].extract_numbers(text)


def _words_only_in(quotes_by_wording: dict[str, str]) -> list[dict[str, Any]]:
    token_sets = {wording_id: normalise_tokens(text) for wording_id, text in quotes_by_wording.items()}
    if not token_sets:
        return []
    shared = set.intersection(*(set(tokens) for tokens in token_sets.values())) if token_sets else set()
    rows = []
    for wording_id, tokens in token_sets.items():
        only = []
        seen: set[str] = set()
        for token in tokens:
            if token in shared or token in seen:
                continue
            seen.add(token)
            only.append(token)
            if len(only) >= MAX_WORD_DIFF:
                break
        rows.append({"wording_id": wording_id, "words_only_in_this_wording": only, "capped": len(only) >= MAX_WORD_DIFF})
    return rows


def normalise_tokens(text: str) -> list[str]:
    tokens = []
    for token in normalise(text).split(" "):
        cleaned = token.strip(".,;:()\"'")
        if cleaned:
            tokens.append(cleaned)
    return tokens


def _classify(cells: list[dict[str, Any]]) -> dict[str, Any]:
    stated = [cell for cell in cells if cell["status"] == "stated"]
    missing = [cell for cell in cells if cell["status"] == "not_stated"]
    failed = any(quote["verdict"] != "supported" for cell in stated for quote in cell["quotes"])
    duplicate = any(len(cell["quotes"]) > 1 for cell in stated)
    supported_texts = [
        quote["text"]
        for cell in stated
        for quote in cell["quotes"]
        if quote["verdict"] == "supported"
    ]
    folded = {" ".join(normalise_tokens(text)) for text in supported_texts}
    texts_also_differ = len(folded) > 1
    amounts = []
    for cell in stated:
        for quote in cell["quotes"]:
            if quote["verdict"] == "supported":
                amounts.append((cell["wording_id"], _numbers(quote["text"])))
    amount_sets = {frozenset(nums) for _wording, nums in amounts}
    amounts_differ = len(amount_sets) > 1
    if failed or duplicate:
        difference_class = "unresolved"
        material = True
    elif any(cell["status"] == "not_quoted" for cell in cells):
        difference_class = "unresolved"
        material = True
    elif missing and stated:
        difference_class = "not_stated_in_one"
        material = True
    elif texts_also_differ:
        difference_class = "text_differs"
        material = True
    else:
        difference_class = "same_text"
        material = False
        texts_also_differ = False
    number_rows = []
    if amounts and amounts_differ and not failed:
        shared_numbers = set.intersection(*(set(nums) for _wording, nums in amounts)) if amounts else set()
        for wording_id, nums in amounts:
            only = []
            seen: set[str] = set()
            for number in nums:
                if number in shared_numbers or number in seen:
                    continue
                seen.add(number)
                only.append(number)
            number_rows.append({"wording_id": wording_id, "numbers_only_in_this_wording": only})
    word_rows: list[dict[str, Any]] = []
    if material and not failed and not duplicate and difference_class in {"text_differs", "not_stated_in_one"} and texts_also_differ:
        by_wording = {}
        for cell in stated:
            if len(cell["quotes"]) == 1 and cell["quotes"][0]["verdict"] == "supported":
                by_wording[cell["wording_id"]] = cell["quotes"][0]["text"]
        if len(by_wording) >= 2:
            word_rows = _words_only_in(by_wording)
    return {
        "difference_class": difference_class,
        "material_difference": material,
        "texts_also_differ": texts_also_differ if difference_class == "not_stated_in_one" else texts_also_differ,
        "amounts_differ": amounts_differ if not failed else False,
        "numbers_only_in": number_rows,
        "words_only_in": word_rows,
        "favourable_to": None,
        "chosen_text": None,
    }


def _cell_for(
    wording_id: str,
    pending: list[dict[str, Any]],
    documents,
    as_of,
    stale_after_days,
    intake_files,
    *,
    fully_blocked: bool,
) -> dict[str, Any]:
    if not pending:
        status = "not_quoted" if fully_blocked else "not_stated"
        return {
            "wording_id": wording_id,
            "status": status,
            "text": NOT_STATED,
            "value": NOT_STATED,
            "inferred": False,
            "silence_inferred": False,
            "citation": None,
            "quotes": [],
            "chosen_text": None,
        }
    checked = [
        check_quote(quote, documents, as_of, stale_after_days, intake_files)
        for quote in pending
    ]
    chosen = checked[0]["text"] if len(checked) == 1 else None
    return {
        "wording_id": wording_id,
        "status": "stated",
        "text": chosen,
        "value": chosen,
        "inferred": False,
        "citation": checked[0]["citation"] if len(checked) == 1 else None,
        "quotes": checked,
        "chosen_text": None,
    }


def _fully_blocked(wordings: list[dict[str, Any]], not_used: list[dict[str, Any]]) -> set[str]:
    blocked: set[str] = set()
    for wording in wordings:
        documents = wording.get("documents") or []
        if not documents:
            continue
        unused = {
            row["document_id"]
            for row in not_used
            if row["wording_id"] == wording["wording_id"] and row.get("document_id")
        }
        if all(document.get("document_id") in unused for document in documents):
            blocked.add(wording["wording_id"])
    return blocked


def _rows_from_quotes(
    quotes,
    wordings,
    documents,
    as_of,
    stale_after_days,
    intake_files,
    not_used,
) -> list[dict[str, Any]]:
    wording_ids = [wording["wording_id"] for wording in wordings]
    blocked = _fully_blocked(wordings, not_used)
    grouped: dict[tuple[str, str], dict[str, list[dict[str, Any]]]] = {}
    for quote in quotes:
        key = (quote["topic"], quote["subject"])
        grouped.setdefault(key, {wording_id: [] for wording_id in wording_ids})
        grouped[key][quote["wording_id"]].append(quote)
    rows = []
    for topic, subject in sorted(grouped, key=lambda item: (TOPIC_INDEX[item[0]], item[1])):
        cells = [
            _cell_for(
                wording_id,
                grouped[(topic, subject)][wording_id],
                documents,
                as_of,
                stale_after_days,
                intake_files,
                fully_blocked=wording_id in blocked,
            )
            for wording_id in wording_ids
        ]
        classified = _classify(cells)
        side_by_side = [
            {
                "wording_id": cell["wording_id"],
                "status": cell["status"],
                "text": cell["text"] if cell["status"] == "stated" else NOT_STATED,
                "citation": cell["citation"],
                "inferred": False,
            }
            for cell in cells
        ]
        rows.append(
            {
                "row_id": f"{topic}.{subject}",
                "topic": topic,
                "subject": subject,
                "cells": cells,
                "side_by_side": side_by_side,
                **classified,
            }
        )
    return rows


def _summary(rows: list[dict[str, Any]], unaligned: list[dict[str, Any]], not_used: list[dict[str, Any]]) -> dict[str, Any]:
    quotes = [quote for row in rows for cell in row["cells"] if cell["status"] == "stated" for quote in cell["quotes"]]
    counts = empty_verdict_counts()
    for quote in quotes:
        counts[quote["verdict"]] += 1
    stated = len(quotes)
    not_stated_cells = sum(1 for row in rows for cell in row["cells"] if cell["status"] == "not_stated")
    not_quoted_cells = sum(1 for row in rows for cell in row["cells"] if cell["status"] == "not_quoted")
    classes = [row["difference_class"] for row in rows]
    return {
        "wording_count_is_separate": True,
        "row_count": len(rows),
        "stated_cell_count": stated,
        "not_stated_cell_count": not_stated_cells,
        "not_quoted_cell_count": not_quoted_cells,
        "verdict_total": stated,
        "verdicts": counts,
        "failure_count": stated - counts["supported"],
        "material_difference_count": sum(1 for row in rows if row["material_difference"]),
        "same_text_count": classes.count("same_text"),
        "not_stated_in_one_count": classes.count("not_stated_in_one"),
        "text_differs_count": classes.count("text_differs"),
        "unresolved_count": classes.count("unresolved"),
        "unaligned_count": len(unaligned),
        "not_used_count": len(not_used),
        "facts_are_not_summed": True,
    }


def _do_not_rely(draft_bits: dict[str, Any]) -> list[str]:
    reasons = []
    if not draft_bits["interpretation_acknowledged"]:
        reasons.append("specialist_has_not_validated")
    summary = draft_bits["summary"]
    if summary["material_difference_count"]:
        reasons.append("material_difference")
    if summary["not_stated_in_one_count"]:
        reasons.append("not_stated_in_one")
    if summary["text_differs_count"]:
        reasons.append("text_differs")
    if summary["unresolved_count"]:
        reasons.append("unresolved_row")
    if summary["failure_count"]:
        reasons.append("citation_failure")
    if summary["unaligned_count"]:
        reasons.append("unaligned_clause")
    if summary["not_used_count"]:
        reasons.append("document_not_used")
    if draft_bits["injection_detected"]:
        reasons.append("injection_detected")
    if draft_bits["pin_stale"]:
        reasons.append("source_pin_stale")
    if draft_bits["market_label"] == "not_stated":
        reasons.append("market_not_stated")
    if draft_bits["market_label"] == "unrecognised":
        reasons.append("market_unrecognised")
    return reasons


def _validate_wordings(wordings: Any) -> list[dict[str, Any]]:
    if not isinstance(wordings, list):
        raise ValueError("wordings must be a list.")
    if len(wordings) < MIN_WORDINGS:
        raise ValueError("At least two wordings are required.")
    if len(wordings) > MAX_WORDINGS:
        raise ValueError("At most four wordings are compared.")
    seen: set[str] = set()
    cleaned = []
    for wording in wordings:
        if not isinstance(wording, dict):
            raise ValueError("A wording is not an object.")
        wording_id = wording.get("wording_id")
        if not isinstance(wording_id, str) or not WORDING_ID.fullmatch(wording_id):
            raise ValueError("A wording id is missing or not a short token.")
        if wording_id in seen:
            raise ValueError(f"Duplicate wording id {wording_id}.")
        seen.add(wording_id)
        cleaned.append(wording)
    return cleaned


def compare(
    pack: dict[str, Any],
    *,
    as_of: str,
    stale_after_days: int = DEFAULT_STALE_AFTER_DAYS,
    proposed_cells: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    if not isinstance(pack, dict):
        raise ValueError("pack must be an object.")
    if pack.get("synthetic") is not True:
        raise NotSynthetic("The pack was not marked synthetic.")
    _parse_day(as_of, "as_of")
    if isinstance(stale_after_days, bool) or not isinstance(stale_after_days, int) or stale_after_days < 0:
        raise ValueError("stale_after_days must be a non-negative integer.")
    stripped, stripped_keys = strip_prohibited(pack)
    wordings = _validate_wordings(stripped.get("wordings"))
    market_label = _market_label(stripped.get("market"))
    files: list[dict[str, Any]] = []
    seen_files: set[str] = set()
    for wording in wordings:
        for row in wording.get("files") or []:
            file_id = row.get("file_id")
            if not isinstance(file_id, str) or file_id in seen_files:
                raise ValueError("Each file id must be present and unique across the pack.")
            seen_files.add(file_id)
            files.append(row)
    intake = inventory(
        files,
        batch_id=str(stripped.get("pack_id") or "pack")[:40],
        as_of=_parse_day(as_of, "as_of"),
        stale_after_days=stale_after_days,
    )
    intake_files = {row["file_id"]: row for row in intake["files"]}
    documents = _index_documents(wordings)
    if proposed_cells is None:
        quotes, unaligned, not_used, injection_rows = _extract(
            wordings, documents, as_of, stale_after_days, intake_files
        )
    else:
        quotes = []
        for cell in proposed_cells:
            if not isinstance(cell, dict):
                raise ValueError("A proposed cell is not an object.")
            topic = cell.get("topic")
            subject = cell.get("subject")
            wording_id = cell.get("wording_id")
            if topic not in TOPICS or not isinstance(subject, str) or not SUBJECT_KEY.fullmatch(subject):
                raise ValueError("A proposed cell has a topic or subject outside the closed list.")
            if wording_id not in {wording["wording_id"] for wording in wordings}:
                raise ValueError("A proposed cell names a wording that is not in the pack.")
            quotes.append(
                {
                    "topic": topic,
                    "subject": subject,
                    "wording_id": wording_id,
                    "text": str(cell.get("text") or ""),
                    "citation": cell.get("citation"),
                }
            )
        unaligned = []
        not_used = []
        injection_rows = []
        for wording in wordings:
            for document in wording.get("documents") or []:
                reason = document_block_reason(document, as_of, stale_after_days, intake_files)
                if reason:
                    not_used.append(
                        {
                            "wording_id": wording["wording_id"],
                            "document_id": document.get("document_id"),
                            "reason": reason,
                            "quoted": False,
                        }
                    )
    rows = _rows_from_quotes(
        quotes, wordings, documents, as_of, stale_after_days, intake_files, not_used
    )
    sources, pin_stale = pin_rows(as_of, stale_after_days)
    summary = _summary(rows, unaligned, not_used)
    injection_detected = bool(injection_rows) or bool(intake["prompt_injection_detected"])
    flags = _decision_flags()
    reasons = _do_not_rely(
        {
            "interpretation_acknowledged": False,
            "summary": summary,
            "injection_detected": injection_detected,
            "pin_stale": pin_stale,
            "market_label": market_label,
        }
    )
    checker_passed = summary["failure_count"] == 0
    draft = {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment_id": EXPERIMENT_ID,
        "autonomy": "A0",
        "pack_id": stripped.get("pack_id"),
        "organisation_label_is_not_a_cited_fact": True,
        "as_of": as_of,
        "stale_after_days": stale_after_days,
        "market_label": market_label,
        "wordings": [
            {
                "wording_id": wording["wording_id"],
                "role": _role(wording.get("role")),
                "caller_label_is_not_a_cited_fact": True,
            }
            for wording in wordings
        ],
        "rows": rows,
        "material_difference_ids": [row["row_id"] for row in rows if row["material_difference"]],
        "unaligned": unaligned,
        "not_used": not_used,
        "summary": summary,
        "checker_passed": checker_passed,
        "do_not_rely": bool(reasons),
        "do_not_rely_reasons": reasons,
        "regulatory_notes": regulatory_notes(market_label),
        "sources": sources,
        "prompt_injection": {
            "detected": injection_detected,
            "followed": False,
            "hits": injection_rows,
            "stripped_keys": stripped_keys,
        },
        "intake": intake,
        "experiment_12_called": True,
        "experiment_33_span_check": True,
        "experiment_29_number_check": True,
        "human_approval": {
            "specialist_validates_every_interpretation": {
                "recorded": False,
                "performed_by_this_agent": False,
            },
            "specialist_reopens_a_stale_pin": {"recorded": False, "performed_by_this_agent": False},
            "coverage_recommendation_endorsement_contact_and_write_stay_outside": {
                "recorded": False,
                "performed_by_this_agent": False,
            },
        },
        "differences": {
            "from_36": DIFFERENCE_FROM_36,
            "from_37": DIFFERENCE_FROM_37,
            "from_33": DIFFERENCE_FROM_33,
            "from_12": DIFFERENCE_FROM_12,
            "from_29": DIFFERENCE_FROM_29,
        },
        "proposed_cells_were_checked": proposed_cells is not None,
        "output_is_anonymised": False,
    }
    draft.update(flags)
    draft["prompt_injection"]["followed"] = False
    return draft


def record_specialist_review(
    draft: dict[str, Any],
    *,
    role: str,
    reviewer_ref: str,
    row_marks: dict[str, str],
    unaligned_marks: dict[str, str],
) -> dict[str, Any]:
    """Record that a wording specialist looked. This does not recommend or endorse.

    The agent path does not call this function. The command line does not expose it.
    """
    if role != "Wording specialist":
        raise CompareForbidden("Only a Wording specialist can record a review, and it is still not a recommendation.")
    if not isinstance(reviewer_ref, str) or not SPECIALIST_REF.fullmatch(reviewer_ref):
        raise CompareForbidden("reviewer_ref must match WS- and four digits.")
    if draft.get("label") != LABEL:
        raise ValueError("draft is not a policy wording comparison")
    expected_rows = {row["row_id"] for row in draft["rows"]}
    expected_unaligned = {item["unaligned_id"] for item in draft["unaligned"]}
    if set(row_marks) != expected_rows or set(unaligned_marks) != expected_unaligned:
        raise CompareForbidden("Every comparison row and every unaligned clause has to be in the review.")
    for row in draft["rows"]:
        mark = row_marks[row["row_id"]]
        failed = any(
            quote["verdict"] != "supported"
            for cell in row["cells"]
            if cell["status"] == "stated"
            for quote in cell["quotes"]
        )
        if failed and mark != "noted_issue":
            raise CompareForbidden("A row with a failed quote must be marked noted_issue.")
        if not failed and mark != "read":
            raise CompareForbidden("A row whose quotes are supported must be marked read.")
    for item in draft["unaligned"]:
        if unaligned_marks[item["unaligned_id"]] != "noted_unaligned":
            raise CompareForbidden("An unaligned clause must be marked noted_unaligned.")
    reviewed = dict(draft)
    reviewed["interpretation_reviewed"] = True
    reviewed["reviewer_role"] = "Wording specialist"
    reviewed["reviewer_ref"] = reviewer_ref
    pin_stale = "source_pin_stale" in draft["do_not_rely_reasons"]
    acknowledged = (
        draft["checker_passed"]
        and not pin_stale
        and draft["prompt_injection"]["followed"] is False
    )
    reviewed["interpretation_acknowledged"] = acknowledged
    reasons = [reason for reason in draft["do_not_rely_reasons"] if reason != "specialist_has_not_validated"]
    if not acknowledged:
        if "specialist_has_not_validated" not in reasons:
            reasons.insert(0, "specialist_has_not_validated")
    reviewed["do_not_rely_reasons"] = reasons
    reviewed["do_not_rely"] = bool(reasons)
    for key, value in _decision_flags().items():
        if key != "interpretation_acknowledged":
            reviewed[key] = value
    reviewed["interpretation_acknowledged"] = acknowledged
    reviewed["downstream_use_permitted"] = False
    reviewed["human_approval"] = {
        "specialist_validates_every_interpretation": {
            "recorded": acknowledged,
            "performed_by_this_agent": False,
        },
        "specialist_reopens_a_stale_pin": {"recorded": False, "performed_by_this_agent": False},
        "coverage_recommendation_endorsement_contact_and_write_stay_outside": {
            "recorded": False,
            "performed_by_this_agent": False,
        },
    }
    return reviewed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compare synthetic policy wordings.")
    parser.add_argument("--pack", required=True)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--stale-after-days", type=int, default=DEFAULT_STALE_AFTER_DAYS)
    parser.add_argument("--favourable", action="store_true")
    parser.add_argument("--recommend", action="store_true")
    parser.add_argument("--draft-endorsement", action="store_true")
    parser.add_argument("--contact-broker", action="store_true")
    parser.add_argument("--write-pas", action="store_true")
    parser.add_argument("--decide-coverage", action="store_true")
    args = parser.parse_args(argv)
    if any(
        (
            args.favourable,
            args.recommend,
            args.draft_endorsement,
            args.contact_broker,
            args.write_pas,
            args.decide_coverage,
        )
    ):
        return 2
    payload = json.loads(Path(args.pack).read_text(encoding="utf-8"))
    try:
        draft = compare(payload, as_of=args.as_of, stale_after_days=args.stale_after_days)
    except (NotSynthetic, ValueError, TypeError, CompareForbidden):
        return 2
    json.dump(draft, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CompareForbidden:
        raise SystemExit(2)
