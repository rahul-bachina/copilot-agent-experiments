"""Draft a cited summary of one synthetic underwriting submission.

Every stated fact is a copy of named lines, with a pinpoint citation. A field
with no usable current paragraph is "not stated". Nothing is inferred.

Autonomy is A0. summarise() does not accept or decline, suggest a price or
terms, contact the broker, or write to an underwriting system. The underwriter
owns the coverage and pricing decision.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from src.citations import (  # type: ignore
        VERDICTS,
        check_fact,
        document_block_reason,
        empty_verdict_counts,
        index_documents,
        normalise,
    )
    from src.document_intake import inventory
    from src.injection import injection_codes, prohibited_codes, scan_documents, strip_prohibited
    from src.sources import DEFAULT_STALE_AFTER_DAYS, pin_rows, regulatory_notes
else:
    from .citations import (
        VERDICTS,
        check_fact,
        document_block_reason,
        empty_verdict_counts,
        index_documents,
        normalise,
    )
    from .document_intake import inventory
    from .injection import injection_codes, prohibited_codes, scan_documents, strip_prohibited
    from .sources import DEFAULT_STALE_AFTER_DAYS, pin_rows, regulatory_notes

LABEL = "DRAFT FOR THE UNDERWRITER. NOT A COVERAGE OR PRICING DECISION."
CATALOGUE_ID = "B006"
EXPERIMENT_ID = "exp-37-underwriting-submission-summary"
NOT_STATED = "not stated"
FIELDS = (
    "insured_name",
    "risk_description",
    "sums_insured",
    "locations",
    "loss_history",
    "stated_exclusions",
    "stated_warranties",
    "inception_or_period",
)
MARKET_LABELS = frozenset({"commercial_non_consumer", "retail"})
FIELD_INDEX = {name: index for index, name in enumerate(FIELDS)}

DIFFERENCE_FROM_12 = (
    "Experiment 12 inventories text files and does not summarise them. It has no "
    "underwriting purpose. This experiment calls intake() with no purpose, so nothing "
    "is routed, and then copies lines from documents whose file was read. It does not "
    "confirm the files and it does not decide the risk."
)
DIFFERENCE_FROM_33 = (
    "Experiment 33 copies a contiguous span and checks a pinpoint for a case bundle. "
    "This experiment uses that same contiguous-span rule for submission fields. It does "
    "not import Experiment 33, because that package lives under the module name src and "
    "would collide with this one. It does not recommend a case outcome."
)
DIFFERENCE_FROM_29 = (
    "Experiment 29 can treat shared words as support, and its human gate is an evaluation "
    "owner on thresholds and a release. This experiment calls Experiment 29 only for the "
    "number and date boundary check. Support itself requires a contiguous copy of the cited "
    "lines. There is no threshold and no release. A pass is not an underwriting decision."
)
DIFFERENCE_FROM_35 = (
    "Experiment 35 is a claims evaluation harness being built separately. This folder does "
    "not import it. eval/evaluate.py mirrors the approach: labelled cases, one score per "
    "case, field results kept on the case, no model judge, and no release of a pass."
)


class SummaryForbidden(Exception):
    """A prohibited underwriting action. The draft is not a decision."""


class NotSynthetic(ValueError):
    """The submission was not marked synthetic. The message does not include the body."""


def accept_risk(*_args: Any, **_kwargs: Any) -> None:
    raise SummaryForbidden("The agent does not accept a risk.")


def decline_risk(*_args: Any, **_kwargs: Any) -> None:
    raise SummaryForbidden("The agent does not decline a risk.")


def suggest_price(*_args: Any, **_kwargs: Any) -> None:
    raise SummaryForbidden("The agent does not suggest a price.")


def suggest_terms(*_args: Any, **_kwargs: Any) -> None:
    raise SummaryForbidden("The agent does not suggest terms.")


def contact_broker(*_args: Any, **_kwargs: Any) -> None:
    raise SummaryForbidden("The agent does not contact the broker.")


def write_underwriting_system(*_args: Any, **_kwargs: Any) -> None:
    raise SummaryForbidden("The agent does not write to the underwriting system.")


def bind_cover(*_args: Any, **_kwargs: Any) -> None:
    raise SummaryForbidden("The agent does not bind cover.")


def recommend_autonomy_a3(*_args: Any, **_kwargs: Any) -> None:
    raise SummaryForbidden("The agent does not recommend autonomy A3.")


def release_evaluation(*_args: Any, **_kwargs: Any) -> None:
    raise SummaryForbidden("The agent does not release an evaluation as a decision.")


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


def _exp35_folders() -> list[str]:
    root = Path(__file__).resolve().parents[2]
    return sorted(path.name for path in root.glob("35-*") if path.is_dir())


def _decision_flags() -> dict[str, Any]:
    return {
        "coverage_decision": None,
        "price_suggested": None,
        "terms_suggested": None,
        "broker_contacted": False,
        "underwriting_system_written": False,
        "bound": False,
        "summary_accepted_as_decision": False,
        "reading_acknowledged": False,
        "solely_automated_decision": False,
        "market_label_decided_by_agent": False,
        "model_called": False,
        "network_called": False,
        "foundry_called": False,
        "a3_recommended": False,
        "actions_taken": [],
        "experiment_33_imported": False,
        "experiment_35_imported": False,
        "evaluation_released": False,
    }


def _extract(
    documents: list[dict[str, Any]],
    as_of: str,
    stale_after_days: int,
    intake_files: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    pending: list[dict[str, Any]] = []
    not_used: list[dict[str, Any]] = []
    for document in documents:
        document_id = str(document.get("document_id") or "")
        reason = document_block_reason(document, as_of, stale_after_days, intake_files)
        reviewed = str(document.get("reviewed_on") or "")
        if reason:
            not_used.append(
                {
                    "document_id": document_id,
                    "field": None,
                    "reason": reason,
                    "reviewed_on": reviewed,
                }
            )
            continue
        for page in document.get("pages") or []:
            page_number = page.get("page")
            for paragraph in page.get("paragraphs") or []:
                field = paragraph.get("fact_key")
                lines = _paragraph_lines(paragraph)
                if lines is None:
                    not_used.append(
                        {
                            "document_id": document_id,
                            "field": field,
                            "reason": "non_contiguous_lines",
                            "reviewed_on": reviewed,
                        }
                    )
                    continue
                text = " ".join(row["text"].strip() for row in lines if row["text"].strip())
                line_numbers = [row["line"] for row in lines]
                if field not in FIELD_INDEX:
                    if injection_codes(text) or prohibited_codes(text):
                        not_used.append(
                            {
                                "document_id": document_id,
                                "field": field,
                                "reason": "injection" if injection_codes(text) else "prohibited_wording",
                                "reviewed_on": reviewed,
                            }
                        )
                    continue
                if injection_codes(text) or prohibited_codes(text):
                    not_used.append(
                        {
                            "document_id": document_id,
                            "field": field,
                            "reason": "injection" if injection_codes(text) else "prohibited_wording",
                            "reviewed_on": reviewed,
                        }
                    )
                    continue
                pending.append(
                    {
                        "field": field,
                        "text": text,
                        "citation": {
                            "document_id": document_id,
                            "page": page_number,
                            "paragraph": paragraph.get("paragraph"),
                            "line_start": line_numbers[0],
                            "line_end": line_numbers[-1],
                        },
                        "reviewed_on": reviewed,
                    }
                )
    pending.sort(
        key=lambda item: (
            FIELD_INDEX[item["field"]],
            item["reviewed_on"],
            item["citation"]["document_id"],
            item["citation"]["page"] if isinstance(item["citation"]["page"], int) else 0,
            item["citation"]["paragraph"] if isinstance(item["citation"]["paragraph"], int) else 0,
            item["citation"]["line_start"],
        )
    )
    facts = []
    for index, item in enumerate(pending, start=1):
        item["fact_id"] = f"F{index}"
        facts.append(item)
    return facts, not_used


def _contradictions(facts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for fact in facts:
        grouped.setdefault(fact["field"], []).append(fact)
    rows = []
    for field, group in grouped.items():
        texts = {normalise(fact["text"]) for fact in group}
        if len(group) > 1 and len(texts) > 1:
            rows.append(
                {
                    "field": field,
                    "fact_ids": [fact["fact_id"] for fact in group],
                    "resolved": False,
                    "chosen_value": None,
                }
            )
    return rows


def _gaps(facts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    present = {fact["field"] for fact in facts}
    gaps = []
    for index, field in enumerate(FIELDS, start=1):
        if field in present:
            continue
        gaps.append(
            {
                "gap_id": f"G{index}",
                "field": field,
                "value": NOT_STATED,
                "status": "not_stated",
                "citation": None,
                "verdict": "not_stated",
                "inferred": False,
            }
        )
    return gaps


def _sections(facts: list[dict[str, Any]], gaps: list[dict[str, Any]]) -> dict[str, Any]:
    by_field: dict[str, list[dict[str, Any]]] = {field: [] for field in FIELDS}
    for fact in facts:
        by_field[fact["field"]].append(
            {
                "fact_id": fact["fact_id"],
                "value": fact["text"],
                "status": "stated",
                "citation": fact["citation"],
                "verdict": fact["verdict"],
                "other_failures": fact["other_failures"],
            }
        )
    gap_by_field = {gap["field"]: gap for gap in gaps}
    sections = {}
    for field in FIELDS:
        if by_field[field]:
            sections[field] = {"status": "stated", "items": by_field[field]}
        else:
            gap = gap_by_field[field]
            sections[field] = {
                "status": "not_stated",
                "items": [
                    {
                        "gap_id": gap["gap_id"],
                        "value": NOT_STATED,
                        "status": "not_stated",
                        "citation": None,
                        "verdict": "not_stated",
                        "inferred": False,
                    }
                ],
            }
    return sections


def _summary(facts: list[dict[str, Any]], gaps: list[dict[str, Any]], not_used: list[dict], contradictions: list) -> dict[str, Any]:
    counts = empty_verdict_counts()
    for fact in facts:
        counts[fact["verdict"]] += 1
    stated = len(facts)
    if sum(counts.values()) != stated:
        raise RuntimeError("Verdict totals do not match the stated fact count.")
    failure_count = stated - counts["supported"]
    return {
        "stated_fact_count": stated,
        "verdict_total": stated,
        "verdicts": counts,
        "failure_count": failure_count,
        "gap_count": len(gaps),
        "contradiction_count": len(contradictions),
        "not_used_count": len(not_used),
        "section_count": len(FIELDS),
        "each_stated_fact_has_one_verdict": True,
        "other_failures_are_not_in_the_totals": True,
        "gaps_are_not_verdicts": True,
        "section_count_is_not_added_to_stated_fact_count": True,
        "not_used_count_is_separate": True,
    }


def _do_not_rely(
    *,
    gaps: list[dict[str, Any]],
    contradictions: list[dict[str, Any]],
    facts: list[dict[str, Any]],
    injection_detected: bool,
    intake: dict[str, Any],
    not_used: list[dict[str, Any]],
    pins_stale: bool,
    market_label: str,
    label_differs: bool,
) -> list[str]:
    reasons = []
    if gaps:
        reasons.append("missing_information")
    if contradictions:
        reasons.append("contradiction")
    if any(fact["verdict"] != "supported" for fact in facts):
        reasons.append("stated_fact_failed")
    if injection_detected or intake["prompt_injection_detected"]:
        reasons.append("injection_detected")
    if any(row["reason"] == "withheld_identifier" for row in not_used):
        reasons.append("withheld_identifier")
    if intake["any_document_not_current"] or any(
        row["reason"] in {"intake_date_not_current", "stale", "superseded", "status_not_current", "intake_not_read", "not_in_intake"}
        for row in not_used
    ):
        reasons.append("intake_or_document_not_current")
    if intake["catalogue_stale"] or intake["gateway_rules_stale"]:
        reasons.append("intake_catalogue_or_rules_stale")
    if pins_stale:
        reasons.append("source_pin_stale")
    if market_label == "unrecognised":
        reasons.append("market_unrecognised")
    if market_label == "not_stated":
        reasons.append("market_not_stated")
    if label_differs:
        reasons.append("caller_label_differs_from_cited_name")
    return reasons


def summarise(
    submission: dict[str, Any],
    *,
    as_of: str,
    stale_after_days: int = DEFAULT_STALE_AFTER_DAYS,
    proposed_facts: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    if not isinstance(submission, dict):
        raise TypeError("submission must be an object")
    if submission.get("synthetic") is not True:
        raise NotSynthetic("submission is not marked synthetic")
    as_of_date = _parse_day(as_of, "as_of")
    if type(stale_after_days) is not int or stale_after_days < 0:
        raise ValueError("stale_after_days must be a non-negative integer")

    working, stripped = strip_prohibited(submission)
    files = working.get("files")
    documents_in = working.get("documents")
    if not isinstance(files, list) or not files:
        raise ValueError("submission has no files")
    if not isinstance(documents_in, list) or not documents_in:
        raise ValueError("submission has no documents")

    submission_id = working.get("submission_id", "unspecified")
    if not isinstance(submission_id, str) or not submission_id:
        submission_id = "unspecified"
    caller_label = working.get("organisation")
    if not isinstance(caller_label, str):
        caller_label = None

    intake = inventory(
        files,
        batch_id=submission_id,
        as_of=as_of_date,
        stale_after_days=stale_after_days,
    )
    intake_files = {row["file_id"]: row for row in intake["files"]}
    documents = index_documents(documents_in)
    document_list = list(documents.values())
    injection = scan_documents(document_list)
    if intake["prompt_injection_detected"]:
        injection = {
            "detected": True,
            "followed": False,
            "signals": injection["signals"]
            + [
                {
                    "document_id": None,
                    "code": "intake_file_signal",
                    "hidden_in": "experiment_12",
                    "followed": False,
                }
            ],
        }

    market_label = _market_label(working.get("market"))
    sources, pins_stale = pin_rows(as_of, stale_after_days)

    if proposed_facts is None:
        raw_facts, not_used = _extract(
            document_list, as_of, stale_after_days, intake_files
        )
    else:
        raw_facts = []
        not_used = []
        for index, item in enumerate(proposed_facts, start=1):
            if not isinstance(item, dict):
                raise ValueError("proposed facts must be objects")
            raw_facts.append(
                {
                    "fact_id": item.get("fact_id") or f"P{index}",
                    "field": item.get("field"),
                    "text": str(item.get("text") or ""),
                    "citation": item.get("citation"),
                }
            )

    checked = [
        check_fact(fact, documents, as_of, stale_after_days, intake_files) for fact in raw_facts
    ]
    gaps = _gaps(checked) if proposed_facts is None else []
    contradictions = _contradictions(checked) if proposed_facts is None else []
    cited_names = [
        normalise(fact["text"])
        for fact in checked
        if fact["field"] == "insured_name" and fact["verdict"] == "supported"
    ]
    label_differs = bool(
        caller_label
        and cited_names
        and all(normalise(caller_label) not in name for name in cited_names)
    )
    reasons = _do_not_rely(
        gaps=gaps,
        contradictions=contradictions,
        facts=checked,
        injection_detected=injection["detected"],
        intake=intake,
        not_used=not_used,
        pins_stale=pins_stale,
        market_label=market_label,
        label_differs=label_differs,
    )
    summary = _summary(checked, gaps, not_used, contradictions)
    flags = _decision_flags()
    checker_passed = summary["failure_count"] == 0 and all(
        fact["verdict"] == "supported" for fact in checked
    )
    draft = {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment_id": EXPERIMENT_ID,
        "autonomy": "A0",
        "submission_id": submission_id,
        "caller_organisation_label": caller_label,
        "caller_label_is_not_a_cited_fact": True,
        "caller_label_differs_from_cited_name": label_differs,
        "market_label": market_label,
        "as_of": as_of,
        "stale_after_days": stale_after_days,
        "intake": intake,
        "sections": _sections(checked, gaps) if proposed_facts is None else None,
        "facts": checked,
        "gaps": gaps,
        "contradictions": contradictions,
        "not_used": not_used,
        "summary": summary,
        "checker_passed": checker_passed,
        "do_not_rely": bool(reasons),
        "do_not_rely_reasons": reasons,
        "regulatory_notes": regulatory_notes(market_label),
        "prompt_injection": injection,
        "prohibited_payload_keys": stripped,
        "sources": sources,
        "experiment_29_number_check": True,
        "experiment_35_folders_present": _exp35_folders(),
        "human_approval": {
            "underwriter_reviews_every_cited_fact": {"recorded": False, "performed_by_this_agent": False},
            "underwriter_decides_coverage": {"recorded": False, "performed_by_this_agent": False},
            "underwriter_sets_price_and_terms": {"recorded": False, "performed_by_this_agent": False},
            "underwriter_decides_whether_to_ask_the_broker": {
                "recorded": False,
                "performed_by_this_agent": False,
            },
        },
        "differences": {
            "from_12": DIFFERENCE_FROM_12,
            "from_33": DIFFERENCE_FROM_33,
            "from_29": DIFFERENCE_FROM_29,
            "from_35": DIFFERENCE_FROM_35,
        },
        "proposed_facts_were_checked": proposed_facts is not None,
    }
    draft.update(flags)
    draft["prompt_injection"]["followed"] = False
    return draft


def record_underwriter_review(
    draft: dict[str, Any],
    *,
    role: str,
    reviewer_ref: str,
    fact_marks: dict[str, str],
    gap_marks: dict[str, str],
) -> dict[str, Any]:
    """Record that an underwriter looked. This does not decide coverage or price.

    The agent path does not call this function. The command line does not expose it.
    """
    if role != "Underwriter":
        raise SummaryForbidden("Only an Underwriter can record a review, and it is still not a decision.")
    if not isinstance(reviewer_ref, str) or not reviewer_ref.startswith("UW-"):
        raise SummaryForbidden("reviewer_ref must start with UW-.")
    if draft.get("label") != LABEL:
        raise ValueError("draft is not an underwriting summary")
    expected_facts = {fact["fact_id"] for fact in draft["facts"]}
    expected_gaps = {gap["gap_id"] for gap in draft["gaps"]}
    if set(fact_marks) != expected_facts or set(gap_marks) != expected_gaps:
        raise SummaryForbidden("Every stated fact and every gap has to be in the review.")
    for fact in draft["facts"]:
        mark = fact_marks[fact["fact_id"]]
        if fact["verdict"] == "supported" and mark != "read":
            raise SummaryForbidden("A supported fact must be marked read.")
        if fact["verdict"] != "supported" and mark != "noted_failure":
            raise SummaryForbidden("A failed fact must be marked noted_failure.")
    for gap in draft["gaps"]:
        if gap_marks[gap["gap_id"]] != "noted_gap":
            raise SummaryForbidden("A gap must be marked noted_gap.")
    reviewed = dict(draft)
    reviewed["facts_reviewed"] = True
    reviewed["reviewer_role"] = "Underwriter"
    complete = (
        reviewed["checker_passed"]
        and not reviewed["contradictions"]
        and "source_pin_stale" not in reviewed["do_not_rely_reasons"]
        and reviewed["prompt_injection"]["followed"] is False
    )
    reviewed["reading_acknowledged"] = complete
    reviewed["coverage_decision"] = None
    reviewed["price_suggested"] = None
    reviewed["terms_suggested"] = None
    reviewed["broker_contacted"] = False
    reviewed["underwriting_system_written"] = False
    reviewed["bound"] = False
    reviewed["summary_accepted_as_decision"] = False
    reviewed["solely_automated_decision"] = False
    return reviewed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Summarise one synthetic underwriting submission.")
    parser.add_argument("--submission", required=True)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--stale-after-days", type=int, default=DEFAULT_STALE_AFTER_DAYS)
    parser.add_argument("--accept", action="store_true")
    parser.add_argument("--decline", action="store_true")
    parser.add_argument("--suggest-price", action="store_true")
    parser.add_argument("--suggest-terms", action="store_true")
    parser.add_argument("--contact-broker", action="store_true")
    parser.add_argument("--write-system", action="store_true")
    parser.add_argument("--bind", action="store_true")
    args = parser.parse_args(argv)
    prohibited = {
        "--accept": args.accept,
        "--decline": args.decline,
        "--suggest-price": args.suggest_price,
        "--suggest-terms": args.suggest_terms,
        "--contact-broker": args.contact_broker,
        "--write-system": args.write_system,
        "--bind": args.bind,
    }
    if any(prohibited.values()):
        return 2
    payload = json.loads(Path(args.submission).read_text(encoding="utf-8"))
    try:
        draft = summarise(payload, as_of=args.as_of, stale_after_days=args.stale_after_days)
    except (NotSynthetic, ValueError, TypeError):
        return 2
    json.dump(draft, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SummaryForbidden:
        raise SystemExit(2)
