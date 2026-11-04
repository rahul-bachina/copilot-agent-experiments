"""Draft a cited reading of one synthetic case bundle, then check every sentence.

The extractive draft copies lines. It does not paraphrase. The checker fails a
sentence that has no pinpoint, cites a span that does not contain it, cites a
stale or superseded document, recommends an outcome, makes a disclosure
decision, or makes a credibility finding.

Autonomy is A0. summarise() never sets an outcome. A decision-maker reviews
every cited sentence outside this function.
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
        check_sentence,
        document_block_reason,
        empty_verdict_counts,
        index_documents,
        normalise,
        resolve_span,
    )
    from src.injection import injection_codes, prohibited_codes, scan_documents, strip_prohibited
    from src.sources import SOURCES
else:
    from .citations import (
        check_sentence,
        document_block_reason,
        empty_verdict_counts,
        index_documents,
        normalise,
        resolve_span,
    )
    from .injection import injection_codes, prohibited_codes, scan_documents, strip_prohibited
    from .sources import SOURCES

LABEL = "DRAFT FOR THE DECISION-MAKER. NOT A DECISION."
CATALOGUE_ID = "UK09"
MATTER_TYPES = frozenset(
    {"disclosure_reading", "asylum_case_reading", "barring_referral_reading"}
)

DIFFERENCE_FROM_18 = (
    "Experiment 18 builds an index of items in an authorised scope. It records a hash, "
    "a date, a proposed page order, and flags for possible privilege or third-party data. "
    "It does not write a sentence about what a document says, and it does not attach a "
    "page, paragraph, and line to such a sentence. This experiment drafts those sentences "
    "and checks each citation. It does not decide scope, build an export index, or call "
    "Experiment 12 or Experiment 18."
)
DIFFERENCE_FROM_29 = (
    "Experiment 29 scores claims in a question-and-answer bundle against passages an agent "
    "was shown. A shared word can be enough for its supported verdict, and its human gate "
    "is an evaluation owner on thresholds and a release. This experiment drafts a case-bundle "
    "reading. Support means the sentence is a contiguous span of the cited lines. The human "
    "gate is that the decision-maker reviews every cited sentence. There is no threshold and "
    "no release. Neither experiment decides a case."
)


class SummaryForbidden(Exception):
    """A prohibited action. The draft is not a decision."""


def recommend_outcome(*_args: Any, **_kwargs: Any) -> None:
    raise SummaryForbidden("The agent does not recommend an outcome.")


def decide_disclosure(*_args: Any, **_kwargs: Any) -> None:
    raise SummaryForbidden("The agent does not make a disclosure decision.")


def find_credibility(*_args: Any, **_kwargs: Any) -> None:
    raise SummaryForbidden("The agent does not make a credibility finding.")


def accept_summary(*_args: Any, **_kwargs: Any) -> None:
    raise SummaryForbidden("The agent does not accept a summary and does not decide the case.")


def send_external(*_args: Any, **_kwargs: Any) -> None:
    raise SummaryForbidden("The agent does not send anything.")


def write_production_record(*_args: Any, **_kwargs: Any) -> None:
    raise SummaryForbidden("The agent does not write a production record.")


def _parse_day(value: str, label: str) -> date:
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} is not a calendar date.") from exc


def _pin_rows(as_of: str, stale_after_days: int) -> tuple[list[dict[str, Any]], bool]:
    as_of_date = _parse_day(as_of, "as_of")
    rows: list[dict[str, Any]] = []
    any_stale = False
    for source in SOURCES:
        stale = False
        age = None
        if source["stale_applicable"]:
            verified = _parse_day(source["last_verified"], source["id"])
            age = (as_of_date - verified).days
            stale = age > stale_after_days or age < 0
        if stale:
            any_stale = True
        rows.append(
            {
                "id": source["id"],
                "title": source["title"],
                "url": source["url"],
                "last_verified": source["last_verified"],
                "stale_applicable": source["stale_applicable"],
                "reopened_for_this_experiment": source["reopened_for_this_experiment"],
                "stale": stale,
                "age_days": age,
                "note": source["note"],
            }
        )
    return rows, any_stale


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


def _extract(documents: list[dict[str, Any]], expected: list[str] | None, as_of: str, stale_after_days: int) -> tuple[list[dict], list[dict]]:
    sentences: list[dict[str, Any]] = []
    not_used: list[dict[str, Any]] = []
    expected_set = set(expected) if expected else None
    for document in documents:
        document_id = str(document.get("document_id") or "")
        reason = document_block_reason(document, as_of, stale_after_days)
        if reason:
            not_used.append({"document_id": document_id, "fact_key": None, "reason": reason})
            continue
        for page in document.get("pages") or []:
            page_number = page.get("page")
            for paragraph in page.get("paragraphs") or []:
                fact_key = paragraph.get("fact_key")
                lines = _paragraph_lines(paragraph)
                if lines is None:
                    not_used.append(
                        {
                            "document_id": document_id,
                            "fact_key": fact_key,
                            "reason": "non_contiguous_lines",
                        }
                    )
                    continue
                text = " ".join(row["text"].strip() for row in lines if row["text"].strip())
                if not fact_key:
                    if injection_codes(text) or prohibited_codes(text):
                        not_used.append(
                            {
                                "document_id": document_id,
                                "fact_key": None,
                                "reason": "injection" if injection_codes(text) else "prohibited_wording",
                            }
                        )
                    continue
                if expected_set is not None and fact_key not in expected_set:
                    not_used.append(
                        {
                            "document_id": document_id,
                            "fact_key": fact_key,
                            "reason": "unrequested_fact_key",
                        }
                    )
                    continue
                if injection_codes(text):
                    not_used.append(
                        {"document_id": document_id, "fact_key": fact_key, "reason": "injection"}
                    )
                    continue
                if prohibited_codes(text):
                    not_used.append(
                        {
                            "document_id": document_id,
                            "fact_key": fact_key,
                            "reason": "prohibited_wording",
                        }
                    )
                    continue
                sentences.append(
                    {
                        "sentence_id": f"S{len(sentences) + 1}",
                        "text": text,
                        "fact_key": fact_key,
                        "document_date": document.get("document_date"),
                        "citation": {
                            "document_id": document_id,
                            "page": page_number,
                            "paragraph": paragraph.get("paragraph"),
                            "line_start": lines[0]["line"],
                            "line_end": lines[-1]["line"],
                        },
                    }
                )
    sentences.sort(
        key=lambda row: (
            str(row.get("document_date") or ""),
            row["citation"]["document_id"],
            row["citation"]["page"] if isinstance(row["citation"]["page"], int) else 0,
            row["citation"]["paragraph"] if isinstance(row["citation"]["paragraph"], int) else 0,
            row["citation"]["line_start"] if isinstance(row["citation"]["line_start"], int) else 0,
            row["sentence_id"],
        )
    )
    for index, row in enumerate(sentences, start=1):
        row["sentence_id"] = f"S{index}"
    return sentences, not_used


def _contradictions(sentences: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in sentences:
        fact_key = row.get("fact_key")
        if not fact_key:
            continue
        grouped.setdefault(str(fact_key), []).append(row)
    found: list[dict[str, Any]] = []
    for fact_key, rows in grouped.items():
        texts = {normalise(str(row.get("text") or "")) for row in rows}
        texts.discard("")
        if len(texts) < 2:
            continue
        found.append(
            {
                "fact_key": fact_key,
                "sentence_ids": [row["sentence_id"] for row in rows],
                "resolved": False,
                "credibility_finding": None,
            }
        )
    return found


def _gaps(expected: list[str] | None, sentences: list[dict[str, Any]]) -> list[dict[str, str]]:
    if not expected:
        return []
    present = {str(row.get("fact_key")) for row in sentences if row.get("fact_key")}
    return [
        {"fact_key": key, "reason": "not_in_a_usable_current_span"}
        for key in expected
        if key not in present
    ]


def _summary(sentences: list[dict[str, Any]], extractive_count: int, gaps: list, contradictions: list, not_used: list) -> dict[str, Any]:
    counts = empty_verdict_counts()
    other = 0
    for row in sentences:
        counts[row["verdict"]] = counts.get(row["verdict"], 0) + 1
        other += len(row.get("other_failures") or [])
    failure_count = sum(count for name, count in counts.items() if name != "supported")
    return {
        "sentence_count": len(sentences),
        "extractive_sentence_count": extractive_count,
        "failure_count": failure_count,
        "verdict_total": len(sentences),
        "verdicts": counts,
        "other_failure_mentions": other,
        "gap_count": len(gaps),
        "contradiction_count": len(contradictions),
        "not_used_count": len(not_used),
    }


def _checked(raw_sentences: list[dict[str, Any]], documents: dict[str, dict], as_of: str, stale_after_days: int) -> list[dict[str, Any]]:
    checked: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, sentence in enumerate(raw_sentences, start=1):
        if not isinstance(sentence, dict):
            raise ValueError("A proposed sentence is not an object.")
        sentence_id = str(sentence.get("sentence_id") or f"P{index}")
        if sentence_id in seen:
            raise ValueError(f"Duplicate sentence id {sentence_id}.")
        seen.add(sentence_id)
        row = check_sentence(
            {**sentence, "sentence_id": sentence_id},
            documents,
            as_of=as_of,
            stale_after_days=stale_after_days,
        )
        if sentence.get("document_date"):
            row["document_date"] = sentence.get("document_date")
        checked.append(row)
    return checked


def summarise(
    bundle: dict[str, Any],
    as_of: str,
    stale_after_days: int = 90,
    *,
    proposed_sentences: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    if not isinstance(bundle, dict):
        raise ValueError("The bundle must be an object.")
    if not isinstance(stale_after_days, int) or isinstance(stale_after_days, bool) or stale_after_days < 0:
        raise ValueError("stale_after_days must be a non-negative integer.")
    _parse_day(as_of, "as_of")
    cleaned, ignored_keys = strip_prohibited(bundle)
    if cleaned.get("synthetic") is not True:
        raise ValueError("A bundle that is not marked synthetic is refused.")
    matter_type = cleaned.get("matter_type")
    if matter_type not in MATTER_TYPES:
        raise ValueError("The matter type is not one of the three reading labels.")
    documents = cleaned.get("documents")
    if not isinstance(documents, list):
        raise ValueError("The bundle has no document list.")
    indexed = index_documents(documents)
    expected = cleaned.get("expected_fact_keys")
    if expected is not None and (
        not isinstance(expected, list) or any(not isinstance(item, str) or not item for item in expected)
    ):
        raise ValueError("expected_fact_keys must be a list of fact-key strings.")
    injection = scan_documents(documents)
    injection["ignored_keys"] = ignored_keys
    injection["followed"] = False
    extractive_raw, not_used = _extract(documents, expected, as_of, stale_after_days)
    extractive = _checked(extractive_raw, indexed, as_of, stale_after_days)
    if proposed_sentences is None:
        shown_source = "extractive"
        shown = extractive
    else:
        if not isinstance(proposed_sentences, list):
            raise ValueError("proposed_sentences must be a list.")
        shown_source = "proposed"
        shown = _checked(proposed_sentences, indexed, as_of, stale_after_days)
        for row in shown:
            for code in injection_codes(str(row.get("text") or "")):
                injection["signals"].append(
                    {
                        "document_id": None,
                        "sentence_id": row["sentence_id"],
                        "code": code,
                        "hidden_in": "proposed_sentence",
                        "followed": False,
                    }
                )
                injection["detected"] = True
    gaps = _gaps(expected, shown)
    contradictions = _contradictions(shown)
    summary = _summary(shown, len(extractive), gaps, contradictions, not_used)
    pins, pins_stale = _pin_rows(as_of, stale_after_days)
    reasons: list[str] = []
    if summary["failure_count"]:
        reasons.append("sentence_checker_failed")
    if gaps:
        reasons.append("gaps")
    if contradictions:
        reasons.append("contradictions")
    if any(row["reason"] in {"stale", "superseded", "status_not_current", "review_date_missing_or_invalid", "review_date_after_as_of"} for row in not_used):
        reasons.append("stale_or_superseded_documents_in_bundle")
    if injection["detected"]:
        reasons.append("prompt_injection_detected")
    if pins_stale:
        reasons.append("pins_stale")
    if not shown:
        reasons.append("no_sentences")
    requested = cleaned.get("requested_autonomy")
    ignored_requests: list[str] = []
    if requested is not None:
        ignored_requests.append("requested_autonomy")
    chronology = [
        {
            "sentence_id": row["sentence_id"],
            "document_date": _chronology_date(row, indexed),
            "citation": row.get("citation"),
        }
        for row in sorted(shown, key=lambda item: (_chronology_date(item, indexed), item["sentence_id"]))
    ]
    return {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment": 33,
        "autonomy": "A0",
        "bundle_id": cleaned.get("bundle_id"),
        "organisation": cleaned.get("organisation"),
        "matter_type": matter_type,
        "synthetic": True,
        "as_of": as_of,
        "stale_after_days": stale_after_days,
        "shown_source": shown_source,
        "sentences": shown,
        "extractive_sentences": extractive,
        "chronology": chronology,
        "gaps": gaps,
        "contradictions": contradictions,
        "not_used": not_used,
        "summary": summary,
        "checker_passed": summary["failure_count"] == 0,
        "do_not_rely": bool(reasons),
        "do_not_rely_reasons": reasons,
        "case_outcome": None,
        "disclosure_decision": None,
        "credibility_finding": None,
        "outcome_recommended": False,
        "summary_accepted_as_reading_aid": False,
        "sentences_reviewed_by_decision_maker": False,
        "summary_is_not_a_decision": True,
        "contradiction_resolved": False,
        "actions_taken": [],
        "model_called": False,
        "network_called": False,
        "foundry_called": False,
        "a3_recommended": False,
        "ignored_requests": ignored_requests,
        "prompt_injection": injection,
        "sources": pins,
        "pins_stale": pins_stale,
        "differences": {
            "experiment_18": DIFFERENCE_FROM_18,
            "experiment_29": DIFFERENCE_FROM_29,
        },
    }


def _chronology_date(sentence: dict[str, Any], documents: dict[str, dict]) -> str:
    citation = sentence.get("citation") if isinstance(sentence.get("citation"), dict) else {}
    document = documents.get(str(citation.get("document_id") or ""))
    if document and document.get("document_date"):
        return str(document["document_date"])
    if sentence.get("document_date"):
        return str(sentence["document_date"])
    return "9999-99-99"


def record_sentence_review(
    draft: dict[str, Any],
    *,
    role: str,
    name: str,
    reviews: list[dict[str, str]],
    injection_acknowledged: bool = False,
    stale_acknowledged: bool = False,
) -> dict[str, Any]:
    """Record that a named decision-maker has read every cited sentence.

    Not a tool of the agent. A review is not an outcome, a disclosure decision,
    or a credibility finding. A hand-edited draft is not a control: this function
    trusts the verdicts already on the draft and does not re-read the bundle.
    """
    if role != "Decision-maker":
        raise SummaryForbidden("The role must be Decision-maker.")
    if not isinstance(name, str) or not name.strip():
        raise SummaryForbidden("The decision-maker's name is passed in this call.")
    if name.strip().casefold() in {"decision-maker", "the agent", "agent"}:
        raise SummaryForbidden("The role is not a person's name.")
    if not isinstance(draft, dict) or "sentences" not in draft:
        raise SummaryForbidden("There is no draft to review.")
    sentences = draft["sentences"]
    if not isinstance(sentences, list) or not isinstance(reviews, list):
        raise SummaryForbidden("The review does not match the draft.")
    by_id = {}
    for review in reviews:
        if not isinstance(review, dict):
            raise SummaryForbidden("A review entry is not an object.")
        by_id[review.get("sentence_id")] = review.get("mark")
    if set(by_id) != {row.get("sentence_id") for row in sentences}:
        raise SummaryForbidden("Every cited sentence has to be in the review, once.")
    for row in sentences:
        mark = by_id[row.get("sentence_id")]
        expected = "read" if row.get("verdict") == "supported" else "noted_failure"
        if mark != expected:
            raise SummaryForbidden("A supported sentence is marked read. A failed sentence is marked noted_failure.")
    reviewed = {
        key: value
        for key, value in draft.items()
        if key
        not in {
            "case_outcome",
            "disclosure_decision",
            "credibility_finding",
            "outcome_recommended",
            "summary_accepted_as_reading_aid",
            "sentences_reviewed_by_decision_maker",
            "summary_is_not_a_decision",
            "actions_taken",
        }
    }
    gaps = draft.get("summary", {}).get("gap_count", 1)
    contradictions = draft.get("summary", {}).get("contradiction_count", 1)
    failures = sum(1 for row in sentences if row.get("verdict") != "supported")
    injection = draft.get("prompt_injection") or {}
    not_used = draft.get("not_used") or []
    stale_present = any(
        row.get("reason") in {"stale", "superseded", "status_not_current", "review_date_missing_or_invalid", "review_date_after_as_of"}
        for row in not_used
    )
    accepted = (
        failures == 0
        and gaps == 0
        and contradictions == 0
        and bool(sentences)
        and not draft.get("pins_stale")
        and (not injection.get("detected") or injection_acknowledged)
        and (not stale_present or stale_acknowledged)
        and injection.get("followed") is False
    )
    reviewed.update(
        {
            "case_outcome": None,
            "disclosure_decision": None,
            "credibility_finding": None,
            "outcome_recommended": False,
            "summary_accepted_as_reading_aid": accepted,
            "sentences_reviewed_by_decision_maker": True,
            "summary_is_not_a_decision": True,
            "reviewer_role": role,
            "reviewer_name": name.strip(),
            "injection_acknowledged": bool(injection_acknowledged),
            "stale_acknowledged": bool(stale_acknowledged),
            "actions_taken": [],
        }
    )
    return reviewed


def _load(path: Path) -> dict[str, Any]:
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError("The bundle file must contain an object.")
    return loaded


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Draft a cited case-bundle reading. Experiment 33.")
    parser.add_argument("--bundle", type=Path)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--stale-after-days", type=int, default=90)
    parser.add_argument("--recommend-outcome", action="store_true")
    parser.add_argument("--decide-disclosure", action="store_true")
    parser.add_argument("--find-credible", action="store_true")
    parser.add_argument("--accept-summary", action="store_true")
    parser.add_argument("--send", action="store_true")
    parser.add_argument("--write-record", action="store_true")
    args = parser.parse_args(argv)
    prohibited = (
        (args.recommend_outcome, recommend_outcome),
        (args.decide_disclosure, decide_disclosure),
        (args.find_credible, find_credibility),
        (args.accept_summary, accept_summary),
        (args.send, send_external),
        (args.write_record, write_production_record),
    )
    for flagged, function in prohibited:
        if flagged:
            try:
                function()
            except SummaryForbidden as exc:
                print(str(exc), file=sys.stderr)
                return 2
    if args.bundle is None:
        print("A bundle path is required.", file=sys.stderr)
        return 1
    try:
        draft = summarise(_load(args.bundle), args.as_of, args.stale_after_days)
    except (ValueError, SummaryForbidden) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    json.dump(draft, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
