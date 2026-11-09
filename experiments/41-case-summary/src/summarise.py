"""Draft a cited reading of one synthetic contact-centre case, then check every sentence.

The extractive draft copies lines. It does not paraphrase. Lines that Experiment
08 flags are not copied. The checker fails a sentence that has no pinpoint, cites
a span that does not contain it, cites a stale or superseded event, contacts the
customer, changes the record, closes a complaint, or offers redress.

Autonomy is A0. summarise() never contacts the customer and never changes the
record. A service representative checks accuracy outside this function.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from copy import deepcopy
from datetime import date
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from src.citations import (  # type: ignore
        check_sentence,
        empty_verdict_counts,
        event_block_reason,
        index_events,
        normalise,
    )
    from src.injection import prohibited_codes, scan_text, strip_prohibited
    from src.sources import PIN_WINDOW_DAYS, SOURCES
else:
    from .citations import (
        check_sentence,
        empty_verdict_counts,
        event_block_reason,
        index_events,
        normalise,
    )
    from .injection import prohibited_codes, scan_text, strip_prohibited
    from .sources import PIN_WINDOW_DAYS, SOURCES

LABEL = (
    "DRAFT FOR THE SERVICE REPRESENTATIVE. "
    "NOT A CUSTOMER CONTACT. NOT A RECORD CHANGE."
)
CATALOGUE_ID = "C002"
AUTONOMY = "A0"
CALLER = "exp-41-case-summary"
SERVICE_ROLE = "Service representative"
DEFAULT_STALE_DAYS = 90

SECTORS = ("council", "utility", "housing", "financial_services")
FACT_KEYS = (
    "what_happened",
    "customer_ask",
    "action_taken",
    "next_step",
    "vulnerability_note",
)
DEFAULT_FACT_KEYS = (
    "what_happened",
    "customer_ask",
    "action_taken",
    "next_step",
)
KINDS = {"note", "call", "letter", "email", "system"}
AUTHOR_ROLES = {"adviser", "team_leader", "system"}
CASE_ID_PATTERN_PREFIX = "SYN-"
EVENT_ID_OK = re.compile(r"^[A-Z][A-Z0-9-]{0,40}$")
CUSTOMER_REF_OK = re.compile(r"^SYN-[A-Z0-9-]{1,40}$")

SECTOR_NOTES = {
    "council": (
        "Council contact-centre case. This starter does not decide eligibility and does not "
        "write a council case. Experiment 13 drafts a front-door reply. This folder does not call it."
    ),
    "utility": (
        "Utility contact-centre case. This starter does not submit a meter reading and does not "
        "change a tariff or a contract. The Ofgem AI blog was not opened for this experiment on "
        "9 November 2026. Experiment 40 opened it on 6 November 2026. This folder does not call Experiment 40."
    ),
    "housing": (
        "Housing contact-centre case. This starter does not start a statutory repair clock and "
        "does not write a housing system. Experiment 05 holds the Awaab's Law clock. This folder "
        "does not call it. The Awaab's Law guidance was not re-opened on 9 November 2026."
    ),
    "financial_services": (
        "Financial-services contact-centre case. This starter does not calculate a DISP clock, "
        "does not close a complaint, and does not offer redress. Experiment 02 holds the DISP clock. "
        "This folder does not call it. PRIN 2A was not opened for this experiment on 9 November 2026."
    ),
}

DIFFERENCES = {
    "experiment_33": (
        "Experiment 33 cites a document, a page, a paragraph, and a line on a legal bundle "
        "for a decision-maker. This starter cites an event, a paragraph, and a line on a "
        "contact-centre case for a service representative. Support means the sentence, after "
        "case and whitespace are folded, is a contiguous part of the cited lines. A paraphrase "
        "fails. This folder does not import Experiment 33. It does not recommend a case outcome either."
    ),
    "experiment_08": (
        "Experiment 08 propose() is called in-process. redacted_text is not copied into the draft. "
        "output_is_anonymised stays false. release() is not called."
    ),
    "experiment_40": (
        "Experiment 40 answers a customer. This starter is read by a service representative. "
        "It does not contact the customer."
    ),
}

_propose = None


class CaseSummaryForbidden(RuntimeError):
    """A contact, a record change, a closure, redress, or an outcome was requested."""


def contact_customer(*_args: Any, **_kwargs: Any) -> None:
    raise CaseSummaryForbidden("The summariser does not contact the customer.")


def write_case_record(*_args: Any, **_kwargs: Any) -> None:
    raise CaseSummaryForbidden("The summariser does not change the case record.")


def close_complaint(*_args: Any, **_kwargs: Any) -> None:
    raise CaseSummaryForbidden("The summariser does not close a complaint.")


def offer_redress(*_args: Any, **_kwargs: Any) -> None:
    raise CaseSummaryForbidden("The summariser does not offer redress.")


def decide_outcome(*_args: Any, **_kwargs: Any) -> None:
    raise CaseSummaryForbidden("The summariser does not decide a case outcome.")


def send_external(*_args: Any, **_kwargs: Any) -> None:
    raise CaseSummaryForbidden("The summariser does not send.")


def accept_summary(*_args: Any, **_kwargs: Any) -> None:
    raise CaseSummaryForbidden(
        "The summariser does not accept the summary. "
        "A service representative checks accuracy outside the agent."
    )


def _load_propose():
    gateway_src = Path(__file__).resolve().parents[2] / "08-uk-pii-redaction-gateway" / "src"
    if not gateway_src.is_dir():
        raise RuntimeError(
            "Experiment 08 is required at experiments/08-uk-pii-redaction-gateway. "
            "This summariser does not carry its own copy."
        )
    inserted = str(gateway_src)
    if inserted not in sys.path:
        sys.path.insert(0, inserted)
    from gateway import propose

    return propose


def _gateway():
    global _propose
    if _propose is None:
        _propose = _load_propose()
    return _propose


def _parse_as_of(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("as_of must be YYYY-MM-DD") from exc


def _flags() -> dict[str, Any]:
    return {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment": "41-case-summary",
        "autonomy": AUTONOMY,
        "human_approval": None,
        "accuracy_checked": False,
        "case_outcome": None,
        "customer_contacted": False,
        "record_changed": False,
        "complaint_closed": False,
        "redress_offered": False,
        "customer_labelled_vulnerable": False,
        "actions_taken": [],
        "model_called": False,
        "network_called": False,
        "foundry_called": False,
        "a3_recommended": False,
        "summary_is_not_a_customer_contact": True,
    }


def _refusal(reason: str) -> dict[str, Any]:
    draft = _flags()
    draft.update(
        {
            "refused": True,
            "reason": reason,
            "text_copied": False,
            "checker_passed": False,
            "do_not_rely": True,
            "do_not_rely_reasons": ["refused"],
            "sentences": [],
            "summary": {
                "sentence_count": 0,
                "extractive_sentence_count": 0,
                "verdict_total": 0,
                "failure_count": 0,
                "verdicts": empty_verdict_counts(),
                "gap_count": 0,
                "contradiction_count": 0,
                "not_used_count": 0,
                "withheld_line_count": 0,
            },
        }
    )
    return draft


def _regulatory() -> dict[str, Any]:
    return {
        "article_5_read": True,
        "article_22_shown_as_omitted": True,
        "article_22a_read": True,
        "duaa_section_80_read": True,
        "articles_22b_to_22d_read_inside_section_80": True,
        "article_22d_regulations_opened": False,
        "si_2026_82_opened": False,
        "significant_decision_taken": False,
        "meaningful_human_involvement_certified": False,
        "lawful_basis_chosen": False,
        "accuracy_principle_met": False,
        "ico_ai_accuracy_page_opened": False,
        "ico_ai_accuracy_quoted": False,
        "disp_clock_calculated": False,
        "awaabs_clock_calculated": False,
    }


def _source_rows(as_of: str) -> tuple[list[dict[str, Any]], list[str]]:
    as_of_date = _parse_as_of(as_of)
    rows = []
    stale_ids = []
    for source in SOURCES:
        stale = False
        if source["stale_applicable"] and source["last_verified"]:
            verified = date.fromisoformat(source["last_verified"])
            if (as_of_date - verified).days > PIN_WINDOW_DAYS:
                stale = True
                stale_ids.append(source["id"])
        rows.append(
            {
                "id": source["id"],
                "title": source["title"],
                "url": source["url"],
                "last_verified": source["last_verified"],
                "opened": source["opened"],
                "stale": stale,
            }
        )
    return rows, stale_ids


def _normalise_lines(raw_lines: Any) -> list[dict[str, Any]]:
    lines = []
    if not isinstance(raw_lines, list):
        raise ValueError("Paragraph lines must be a list.")
    for index, line in enumerate(raw_lines, start=1):
        if isinstance(line, str):
            lines.append({"line": index, "text": line})
        elif isinstance(line, dict):
            number = line.get("line", index)
            if isinstance(number, bool) or not isinstance(number, int):
                raise ValueError("A line number must be an integer.")
            lines.append({"line": number, "text": str(line.get("text") or "")})
        else:
            raise ValueError("A line must be a string or an object.")
    return lines


def _normalise_events(raw_events: Any) -> list[dict[str, Any]]:
    if not isinstance(raw_events, list):
        raise ValueError("events must be a list.")
    events = []
    for raw in raw_events:
        if not isinstance(raw, dict):
            raise ValueError("An event must be an object.")
        event_id = str(raw.get("event_id") or "").strip()
        if not EVENT_ID_OK.fullmatch(event_id):
            raise ValueError("event_id is not in the synthetic shape.")
        paragraphs = []
        raw_paragraphs = raw.get("paragraphs")
        if raw_paragraphs is None and "text" in raw:
            raw_paragraphs = [
                {
                    "paragraph": 1,
                    "fact_key": raw.get("fact_key"),
                    "lines": [raw.get("text") or ""],
                }
            ]
        if not isinstance(raw_paragraphs, list):
            raise ValueError("paragraphs must be a list.")
        for para in raw_paragraphs:
            if not isinstance(para, dict):
                raise ValueError("A paragraph must be an object.")
            number = para.get("paragraph", 1)
            if isinstance(number, bool) or not isinstance(number, int):
                raise ValueError("A paragraph number must be an integer.")
            fact_key = para.get("fact_key") or raw.get("fact_key")
            paragraphs.append(
                {
                    "paragraph": number,
                    "fact_key": fact_key,
                    "lines": _normalise_lines(para.get("lines") or []),
                }
            )
        kind = raw.get("kind") or "note"
        events.append(
            {
                "event_id": event_id,
                "kind": kind,
                "recorded_on": raw.get("recorded_on"),
                "status": raw.get("status") or "current",
                "superseded_by": raw.get("superseded_by") or None,
                "fact_key": raw.get("fact_key"),
                "paragraphs": paragraphs,
                "author_role_known": raw.get("author_role") in AUTHOR_ROLES,
            }
        )
    return events


def _scan_case(events: list[dict[str, Any]], organisation: str) -> dict[str, Any]:
    parts = [organisation, "\n"]
    cursor = len(organisation) + 1
    located = []
    signals: list[dict] = []
    seen: set[tuple] = set()
    zero_width = 0
    for event in events:
        for para in event["paragraphs"]:
            for line in para["lines"]:
                text = line["text"]
                start = cursor
                end = start + len(text)
                located.append(
                    {
                        "event_id": event["event_id"],
                        "paragraph": para["paragraph"],
                        "line": line["line"],
                        "start": start,
                        "end": end,
                    }
                )
                found, removed = scan_text(text, event_id=event["event_id"])
                zero_width += removed
                for row in found:
                    key = (row["event_id"], row["code"], row["hidden_in"])
                    if key not in seen:
                        seen.add(key)
                        signals.append(row)
                parts.append(text)
                parts.append("\n")
                cursor = end + 1
    blob = "".join(parts)
    proposal = _gateway()(blob, caller=CALLER)
    withheld: set[tuple[str, int, int]] = set()
    withheld_rows: list[dict[str, Any]] = []
    entity_types: set[str] = set()
    org_withheld = False
    for finding in proposal["audit_log"]["findings"]:
        if not finding.get("applied"):
            continue
        entity_types.add(finding["entity_type"])
        start = finding["start"]
        end = finding["end"]
        if start < len(organisation):
            org_withheld = True
        for line in located:
            if start < line["end"] and end > line["start"]:
                key = (line["event_id"], line["paragraph"], line["line"])
                if key not in withheld:
                    withheld.add(key)
                    withheld_rows.append(
                        {
                            "event_id": line["event_id"],
                            "paragraph": line["paragraph"],
                            "line": line["line"],
                            "entity_types": [],
                            "text_copied": False,
                        }
                    )
                row = next(
                    item
                    for item in withheld_rows
                    if item["event_id"] == line["event_id"]
                    and item["paragraph"] == line["paragraph"]
                    and item["line"] == line["line"]
                )
                if finding["entity_type"] not in row["entity_types"]:
                    row["entity_types"].append(finding["entity_type"])
    for row in withheld_rows:
        row["entity_types"] = sorted(row["entity_types"])
    gateway = {
        "gateway": "exp-08-uk-pii-redaction-gateway",
        "caller": CALLER,
        "output_is_anonymised": False,
        "agent_may_release": False,
        "release_called": False,
        "redacted_text_copied": False,
        "finding_count": len(proposal["audit_log"]["findings"]),
        "entity_types": sorted(entity_types),
        "input_sha256": proposal["audit_log"]["input_sha256"],
    }
    if "redacted_text" in gateway:
        raise CaseSummaryForbidden("redacted_text must not be stored on the draft.")
    return {
        "withheld": withheld,
        "withheld_rows": withheld_rows,
        "signals": signals,
        "zero_width_removed": zero_width,
        "gateway": gateway,
        "organisation_withheld": org_withheld,
        "line_signals": {
            (row["event_id"],): row for row in signals
        },
    }


def _line_signal_keys(signals: list[dict]) -> set[str]:
    return {row["event_id"] for row in signals}


def _paragraph_blocked(
    event_id: str,
    paragraph: dict[str, Any],
    withheld: set[tuple[str, int, int]],
    signal_event_ids: set[str],
) -> str | None:
    for line in paragraph["lines"]:
        if (event_id, paragraph["paragraph"], line["line"]) in withheld:
            return "identifier_withheld"
        if signal_event_ids and event_id in signal_event_ids:
            found, _removed = scan_text(line["text"], event_id=event_id)
            if found:
                return "untrusted_instruction"
        if prohibited_codes(line["text"]):
            return "prohibited_wording"
    return None


def _extract(
    events: list[dict[str, Any]],
    *,
    as_of: str,
    stale_after_days: int,
    expected: list[str],
    scan: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    sentences: list[dict[str, Any]] = []
    not_used: list[dict[str, Any]] = []
    signal_events = _line_signal_keys(scan["signals"])
    ordered = sorted(events, key=lambda item: (str(item.get("recorded_on") or ""), item["event_id"]))
    for event in ordered:
        reason = event_block_reason(event, as_of, stale_after_days)
        if event["kind"] not in KINDS:
            not_used.append(
                {
                    "event_id": event["event_id"],
                    "reason": "kind_not_in_list",
                    "text_copied": False,
                }
            )
            continue
        if reason:
            not_used.append(
                {
                    "event_id": event["event_id"],
                    "reason": reason,
                    "text_copied": False,
                }
            )
            continue
        for para in sorted(event["paragraphs"], key=lambda item: item["paragraph"]):
            fact_key = para.get("fact_key")
            if fact_key not in FACT_KEYS:
                not_used.append(
                    {
                        "event_id": event["event_id"],
                        "paragraph": para["paragraph"],
                        "reason": "fact_key_not_in_list",
                        "text_copied": False,
                    }
                )
                continue
            if fact_key not in expected:
                not_used.append(
                    {
                        "event_id": event["event_id"],
                        "paragraph": para["paragraph"],
                        "reason": "fact_key_not_requested",
                        "text_copied": False,
                    }
                )
                continue
            blocked = _paragraph_blocked(event["event_id"], para, scan["withheld"], signal_events)
            if blocked:
                not_used.append(
                    {
                        "event_id": event["event_id"],
                        "paragraph": para["paragraph"],
                        "reason": blocked,
                        "text_copied": False,
                    }
                )
                continue
            usable = [line for line in para["lines"] if str(line["text"]).strip()]
            if not usable:
                continue
            runs: list[list[dict[str, Any]]] = []
            current: list[dict[str, Any]] = []
            for line in usable:
                if current and line["line"] != current[-1]["line"] + 1:
                    runs.append(current)
                    current = []
                current.append(line)
            if current:
                runs.append(current)
            for run in runs:
                sentences.append(
                    {
                        "text": " ".join(line["text"].strip() for line in run),
                        "fact_key": fact_key,
                        "citation": {
                            "event_id": event["event_id"],
                            "recorded_on": event.get("recorded_on"),
                            "paragraph": para["paragraph"],
                            "line_start": run[0]["line"],
                            "line_end": run[-1]["line"],
                        },
                    }
                )
    for index, sentence in enumerate(sentences, start=1):
        sentence["sentence_id"] = f"S{index}"
    return sentences, not_used, scan["withheld_rows"]


def _gaps(expected: list[str], sentences: list[dict[str, Any]]) -> list[dict[str, str]]:
    present = {row["fact_key"] for row in sentences}
    return [
        {"fact_key": key, "reason": "no_current_span"}
        for key in expected
        if key not in present
    ]


def _contradictions(sentences: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for sentence in sentences:
        grouped.setdefault(sentence["fact_key"], []).append(sentence)
    rows = []
    for fact_key, group in grouped.items():
        folded = {normalise(row["text"]) for row in group}
        if len(folded) > 1:
            rows.append(
                {
                    "fact_key": fact_key,
                    "sentence_ids": [row["sentence_id"] for row in group],
                    "resolved": False,
                }
            )
    return rows


def _sentence_has_identifier(text: str) -> bool:
    if not text:
        return False
    proposal = _gateway()(text, caller=CALLER)
    return any(finding.get("applied") for finding in proposal["audit_log"]["findings"])


def _check_all(
    raw_sentences: list[dict[str, Any]],
    events: dict[str, dict[str, Any]],
    *,
    as_of: str,
    stale_after_days: int,
    withheld: set[tuple[str, int, int]],
) -> list[dict[str, Any]]:
    checked = []
    for sentence in raw_sentences:
        checked.append(
            check_sentence(
                sentence,
                events,
                as_of=as_of,
                stale_after_days=stale_after_days,
                withheld=withheld,
                sentence_has_identifier=_sentence_has_identifier(str(sentence.get("text") or "")),
            )
        )
    return checked


def _expected_keys(case: dict[str, Any]) -> list[str]:
    raw = case.get("expected_fact_keys", list(DEFAULT_FACT_KEYS))
    if not isinstance(raw, list) or not raw:
        raise ValueError("expected_fact_keys must be a non-empty list.")
    keys = []
    for key in raw:
        if key not in FACT_KEYS:
            raise ValueError("expected_fact_keys contains a key that is not in the closed list.")
        if key not in keys:
            keys.append(key)
    return keys


def _customer_ref(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if CUSTOMER_REF_OK.fullmatch(text):
        return text
    return None


def summarise(
    case: dict[str, Any],
    as_of: str,
    stale_after_days: int = DEFAULT_STALE_DAYS,
    proposed_sentences: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Return one draft. The same case and the same as-of date produce the same JSON."""
    _parse_as_of(as_of)
    if isinstance(stale_after_days, bool) or not isinstance(stale_after_days, int) or stale_after_days < 0:
        raise ValueError("stale_after_days must be a non-negative integer.")
    if not isinstance(case, dict):
        raise ValueError("The case must be an object.")
    cleaned, ignored_keys = strip_prohibited(case)
    if cleaned.get("synthetic") is not True:
        return _refusal("not_synthetic")
    sector = cleaned.get("sector")
    if sector not in SECTORS:
        return _refusal("sector_not_in_list")
    case_id = str(cleaned.get("case_id") or "")
    if not case_id.startswith(CASE_ID_PATTERN_PREFIX):
        return _refusal("case_id_not_synthetic_shape")
    events = _normalise_events(cleaned.get("events"))
    index_events(events)
    expected = _expected_keys(cleaned)
    organisation = str(cleaned.get("organisation") or "")
    if len(organisation) > 80 or "\n" in organisation:
        organisation = ""
        organisation_too_long = True
    else:
        organisation_too_long = False
    scan = _scan_case(events, organisation)
    extracted, not_used, withheld_rows = _extract(
        events,
        as_of=as_of,
        stale_after_days=stale_after_days,
        expected=expected,
        scan=scan,
    )
    shown_raw = extracted if proposed_sentences is None else proposed_sentences
    if proposed_sentences is not None:
        prepared = []
        for index, sentence in enumerate(proposed_sentences, start=1):
            if not isinstance(sentence, dict):
                raise ValueError("A proposed sentence must be an object.")
            row = {
                "sentence_id": sentence.get("sentence_id") or f"P{index}",
                "text": sentence.get("text") or "",
                "fact_key": sentence.get("fact_key"),
                "citation": sentence.get("citation"),
            }
            prepared.append(row)
        shown_raw = prepared
    checked = _check_all(
        shown_raw,
        index_events(events),
        as_of=as_of,
        stale_after_days=stale_after_days,
        withheld=scan["withheld"],
    )
    gaps = _gaps(expected, extracted)
    # Contradictions are about the extract, not about a caller's proposed sentences.
    if proposed_sentences is None:
        supported_extract = [row for row in checked if row["verdict"] == "supported"]
    else:
        extracted_checked = _check_all(
            extracted,
            index_events(events),
            as_of=as_of,
            stale_after_days=stale_after_days,
            withheld=scan["withheld"],
        )
        supported_extract = [row for row in extracted_checked if row["verdict"] == "supported"]
    contradictions = _contradictions(supported_extract)

    counts = empty_verdict_counts()
    for row in checked:
        counts[row["verdict"]] += 1
    sentence_count = len(checked)
    failure_count = sentence_count - counts["supported"]
    source_rows, stale_pins = _source_rows(as_of)
    reasons = []
    if gaps:
        reasons.append("gaps")
    if contradictions:
        reasons.append("contradiction")
    if any(row["reason"] in {"stale", "superseded", "status_not_current", "recorded_date_missing_or_invalid", "recorded_date_after_as_of"} for row in not_used):
        reasons.append("stale_or_superseded_not_used")
    if scan["signals"]:
        reasons.append("untrusted_instruction")
    if stale_pins:
        reasons.append("pins_stale")
    if sentence_count == 0:
        reasons.append("empty_reading")
    if withheld_rows:
        reasons.append("identifier_withheld")
    if failure_count:
        reasons.append("checker_failed")
    organisation_out = None if scan["organisation_withheld"] or organisation_too_long or not organisation else organisation
    draft = _flags()
    draft.update(
        {
            "refused": False,
            "case_id": case_id,
            "sector": sector,
            "sector_note": SECTOR_NOTES[sector],
            "organisation": organisation_out,
            "organisation_withheld": organisation_out is None and bool(cleaned.get("organisation")),
            "customer_ref": _customer_ref(cleaned.get("customer_ref")),
            "customer_ref_kept": _customer_ref(cleaned.get("customer_ref")) is not None,
            "synthetic": True,
            "as_of": as_of,
            "stale_after_days": stale_after_days,
            "pin_window_days": PIN_WINDOW_DAYS,
            "checker_passed": failure_count == 0,
            "do_not_rely": bool(reasons),
            "do_not_rely_reasons": reasons,
            "pins_stale": bool(stale_pins),
            "sources": source_rows,
            "regulatory": _regulatory(),
            "pii_gateway": scan["gateway"],
            "prompt_injection": {
                "detected": bool(scan["signals"]),
                "followed": False,
                "zero_width_removed": scan["zero_width_removed"],
                "signals": scan["signals"],
                "ignored_keys": ignored_keys,
            },
            "sentences": checked,
            "gaps": gaps,
            "contradictions": contradictions,
            "not_used": not_used,
            "withheld_lines": withheld_rows,
            "summary": {
                "sentence_count": sentence_count,
                "extractive_sentence_count": len(extracted),
                "verdict_total": sentence_count,
                "failure_count": failure_count,
                "verdicts": counts,
                "gap_count": len(gaps),
                "contradiction_count": len(contradictions),
                "not_used_count": len(not_used),
                "withheld_line_count": len(withheld_rows),
            },
            "differences": DIFFERENCES,
        }
    )
    return draft


def record_accuracy_check(draft: dict[str, Any], review: dict[str, Any]) -> dict[str, Any]:
    """Record a service representative's accuracy check. Not an agent tool.

    The returned object still does not contact the customer and does not change
    the record. accuracy_checked can become true only for a complete, supported,
    current reading.
    """
    updated = deepcopy(draft)
    updated["customer_contacted"] = False
    updated["record_changed"] = False
    updated["complaint_closed"] = False
    updated["redress_offered"] = False
    updated["customer_labelled_vulnerable"] = False
    updated["case_outcome"] = None
    updated["accuracy_checked"] = False
    updated["human_approval"] = None
    updated["actions_taken"] = []
    decision = review.get("decision")
    if decision in {
        "contact_customer",
        "write_case_record",
        "close_complaint",
        "offer_redress",
        "decide_outcome",
        "send_external",
        "accept_summary",
    }:
        updated["review"] = {"refused": True, "reason": "prohibited_decision", "recorded_by_agent": False}
        return updated
    if review.get("role") != SERVICE_ROLE:
        updated["review"] = {"refused": True, "reason": "role", "recorded_by_agent": False}
        return updated
    name = review.get("name")
    if not isinstance(name, str) or len(name.strip()) < 2 or "agent" in name.casefold():
        updated["review"] = {"refused": True, "reason": "name", "recorded_by_agent": False}
        return updated
    shown = {row["sentence_id"]: row for row in draft.get("sentences") or []}
    marks = review.get("sentences") or []
    if not isinstance(marks, list) or {row.get("sentence_id") for row in marks if isinstance(row, dict)} != set(shown):
        updated["review"] = {"refused": True, "reason": "incomplete_review", "recorded_by_agent": False}
        return updated
    for mark in marks:
        expected = "read" if shown[mark["sentence_id"]]["verdict"] == "supported" else "noted_failure"
        if mark.get("mark") != expected:
            updated["review"] = {
                "refused": True,
                "reason": "mark_does_not_match_verdict",
                "recorded_by_agent": False,
            }
            return updated
    if (
        not draft.get("checker_passed")
        or draft.get("do_not_rely")
        or draft.get("refused")
        or not shown
    ):
        updated["review"] = {
            "refused": True,
            "reason": "not_a_complete_current_reading",
            "recorded_by_agent": False,
        }
        return updated
    updated["accuracy_checked"] = True
    updated["human_approval"] = {
        "role": SERVICE_ROLE,
        "name": name.strip(),
        "effect": (
            "The service representative recorded that they checked the cited sentences. "
            "The case record was not changed. The customer was not contacted."
        ),
    }
    updated["review"] = {"refused": False, "reason": "checked", "recorded_by_agent": False}
    return updated


def _load(path: Path) -> dict[str, Any]:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("The case file could not be read.") from exc
    if not isinstance(loaded, dict):
        raise ValueError("The case file must contain an object.")
    return loaded


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Draft a cited contact-centre case summary. Experiment 41.")
    parser.add_argument("--case", type=Path)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--stale-after-days", type=int, default=DEFAULT_STALE_DAYS)
    parser.add_argument("--contact-customer", action="store_true")
    parser.add_argument("--write-record", action="store_true")
    parser.add_argument("--close-complaint", action="store_true")
    parser.add_argument("--offer-redress", action="store_true")
    parser.add_argument("--decide-outcome", action="store_true")
    parser.add_argument("--send", action="store_true")
    parser.add_argument("--accept-summary", action="store_true")
    args = parser.parse_args(argv)
    prohibited = (
        (args.contact_customer, contact_customer),
        (args.write_record, write_case_record),
        (args.close_complaint, close_complaint),
        (args.offer_redress, offer_redress),
        (args.decide_outcome, decide_outcome),
        (args.send, send_external),
        (args.accept_summary, accept_summary),
    )
    for flagged, function in prohibited:
        if flagged:
            try:
                function()
            except CaseSummaryForbidden as exc:
                print(str(exc), file=sys.stderr)
                return 2
    if args.case is None:
        print("A case path is required.", file=sys.stderr)
        return 2
    try:
        draft = summarise(_load(args.case), args.as_of, args.stale_after_days)
    except CaseSummaryForbidden as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    json.dump(draft, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
