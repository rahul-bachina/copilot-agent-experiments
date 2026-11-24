"""Answer a general benefits question from the pinned synthetic pages.

The same question and the same as-of date produce the same JSON. The agent
does not decide eligibility, estimate an entitlement, calculate an award,
complete or submit a claim, or send. A human adviser route is always offered.
The resident approves the exact summary before it is staged.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from copy import deepcopy
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from cues import (  # noqa: E402
        benefits_in,
        caller_rule_claimed,
        carve_out,
        category_hit,
        clearance_claimed,
        kinds_in,
        safety_hit,
    )
    from dates import as_date, parse_date  # noqa: E402
    from knowledge import find_pages, load_directory, load_pages, page_diff, review_status  # noqa: E402
    from marking import (  # noqa: E402
        RANK,
        above_ceiling,
        content_markings,
        higher_marking,
        legal_hold_in,
        retention_labels,
    )
    from mask import mask_text  # noqa: E402
    from negate import sentences  # noqa: E402
    from reuse import contact_route, identifier_counts  # noqa: E402
    from sources import uk_context  # noqa: E402
else:
    from .cues import (
        benefits_in,
        caller_rule_claimed,
        carve_out,
        category_hit,
        clearance_claimed,
        kinds_in,
        safety_hit,
    )
    from .dates import as_date, parse_date
    from .knowledge import find_pages, load_directory, load_pages, page_diff, review_status
    from .marking import (
        RANK,
        above_ceiling,
        content_markings,
        higher_marking,
        legal_hold_in,
        retention_labels,
    )
    from .mask import mask_text
    from .negate import sentences
    from .reuse import contact_route, identifier_counts
    from .sources import uk_context

LABEL = "BENEFITS INFORMATION FOR THE RESIDENT. NOT A DECISION."
CATALOGUE_ID = "V009"
MAX_TEXT = 4000
SAFETY = ("distress", "domestic_abuse", "safeguarding", "debt", "eviction")
PROHIBITED_KEYS = {
    "human_approval",
    "staged",
    "sent",
    "eligibility_decided",
    "eligibility_decision",
    "entitlement_estimated",
    "award_calculated",
    "award_amount",
    "claim_submitted",
    "claim_completed",
    "clearance",
    "role",
    "approved",
    "content_hash",
    "pins_seen",
    "urgent_seen",
    "stale_seen",
    "sources_seen",
    "adjustment_seen",
    "date_seen",
}
HUMAN = (
    "A human adviser route is available. This assistant does not send the summary. "
    "It is staged only after you approve this exact summary."
)
DANGER = (
    "If you or someone else is in immediate danger, call 999. "
    "This assistant has not contacted anyone."
)
REFUSAL = (
    "This assistant does not decide whether you will get a benefit, does not estimate "
    "an entitlement, and does not calculate an award. A person does that. "
    "Nothing has been sent and no claim has been completed or submitted."
)
STALE = (
    "A matching page is past its review date, so its text is not used. "
    "A person needs to check the publisher's own page."
)
NOT_FOUND = "The pinned pages do not contain that answer."
AMBIGUOUS = "More than one benefit was named. This assistant has not chosen between them."
WITHHELD = (
    "The text carries a protective marking above the clearance recorded for this "
    "resident in the synthetic directory. The body has not been copied."
)
UNREADABLE_DATE = (
    "The date the question is about could not be read. It has not been replaced with today."
)
TOO_LONG = "This question is longer than this starter will answer. A person needs to take it."
COUNT = (
    "This starter does not hold a count of people, and it does not publish a small number. "
    "No count has been replaced with zero."
)
BIASED = (
    "A leading or excluding criterion was in the question. It has not been applied. "
    "A person needs to take it."
)

_STORE: dict[str, dict] = {}


class NotSynthetic(ValueError):
    """The request is not marked synthetic."""


class BenefitsForbidden(RuntimeError):
    """Eligibility, entitlement, an award, a claim, and sending are not tools."""


def decide_eligibility() -> None:
    raise BenefitsForbidden("The agent does not decide eligibility.")


def estimate_entitlement() -> None:
    raise BenefitsForbidden("The agent does not estimate an entitlement.")


def calculate_award() -> None:
    raise BenefitsForbidden("The agent does not calculate an award.")


def submit_claim() -> None:
    raise BenefitsForbidden("The agent does not complete or submit a claim.")


def send() -> None:
    raise BenefitsForbidden("The agent does not send.")


def reset_staging() -> None:
    _STORE.clear()


def pinned_sources() -> dict:
    return {"pages": load_pages(), "directory": load_directory()}


def answer_question(request: dict, as_of: str = "") -> dict:
    """Return an information answer or a handoff. human_approval stays null."""

    if not isinstance(request, dict):
        raise TypeError("request must be an object")
    if request.get("synthetic") is not True:
        raise NotSynthetic("record is not marked synthetic")
    working, ignored_keys = _strip(request)
    question = working.get("question") if isinstance(working.get("question"), str) else ""
    pinned = pinned_sources()
    person = _resident(pinned["directory"], working.get("resident_ref"))
    ceiling = _ceiling(person)
    reading = parse_date(as_of)
    on = as_date(reading)
    masked, mask_report = mask_text(question)
    mask_report = dict(mask_report)
    mask_report["masked_text_included"] = False
    urgent = _urgent_categories(question)
    content_labels = content_markings(question)
    applied = higher_marking(content_labels) or "OFFICIAL"
    withheld = above_ceiling(applied if content_labels else None, ceiling)
    hold = legal_hold_in(question)
    retention = retention_labels(question)
    if on is None:
        identifiers = _no_identifiers()
        identifiers["reason"] = "question_date_unreadable"
        route = {
            "called": False,
            "reason": "question_date_unreadable",
            "experiment_id": "exp-13-council-contact-front-door",
            "reply_copied": False,
            "eligibility_decided": False,
            "message_sent": False,
            "human_approval": None,
        }
    else:
        identifiers = identifier_counts(question, on=on) if question else _no_identifiers()
        route = contact_route(masked or "Synthetic benefits information request.", on=on)
    caller_pages = working.get("supplied_pages")
    diffs = page_diff(caller_pages, pinned["pages"])
    rules_present = "supplied_rules" in working or caller_rule_claimed(question)
    if working.get("supplied_directory") is not None:
        diffs.append({"kind": "caller_directory_not_used", "applied": False, "text_copied": False})
    if rules_present:
        diffs.append({"kind": "caller_rules_not_used", "applied": False, "rate_text_copied": False})

    frame = _frame(
        working=working,
        ignored_keys=ignored_keys,
        reading=reading,
        person=person,
        applied=applied,
        withheld=withheld,
        hold=hold,
        retention=retention,
        urgent=urgent,
        mask_report=mask_report,
        identifiers=identifiers,
        route=route,
        diffs=diffs,
        rules_present=rules_present,
        question=question,
        masked=masked,
    )

    if not question.strip():
        return _finish(frame, outcome="unreadable_question", text=UNREADABLE_DATE + " " + HUMAN, citations=[], why="The question was missing.")
    if withheld:
        return _finish(
            frame,
            outcome="withheld",
            text=WITHHELD + " " + (DANGER + " " if urgent else "") + HUMAN,
            citations=[],
            why="The protective marking is above the directory clearance.",
            include_question=False,
        )
    if urgent:
        citations, quoted = _urgent_citations(pinned["pages"], on)
        text = DANGER
        if quoted:
            text += " " + quoted
        elif on is None:
            text += " " + UNREADABLE_DATE
        text += " " + HUMAN
        return _finish(
            frame,
            outcome="urgent_human",
            text=text,
            citations=citations,
            why="Urgent human contact.",
            include_question=False,
        )
    if reading["unparseable"] or reading["ambiguous"] or on is None:
        return _finish(frame, outcome="unreadable_date", text=UNREADABLE_DATE + " " + HUMAN, citations=[], why="The question date could not be read.")
    if len(question) > MAX_TEXT:
        return _finish(frame, outcome="too_long", text=TOO_LONG + " " + HUMAN, citations=[], why="The question is longer than this starter reads.")
    if category_hit(question, "biased") or carve_out(question):
        return _finish(frame, outcome="route_to_human", text=BIASED + " " + HUMAN, citations=[], why="A criterion was not applied.")
    if category_hit(question, "eligibility") or category_hit(question, "award") or category_hit(question, "claim") or category_hit(question, "send"):
        citations = _boundary_citations(_match(question, pinned["pages"], on))
        text = REFUSAL
        for row in citations:
            if row.get("quoted"):
                text += " " + row["boundary"]
        text += " " + HUMAN
        return _finish(frame, outcome="refused_decision", text=text, citations=citations, why="A decision or an amount was asked for.")
    if category_hit(question, "count"):
        return _finish(frame, outcome="count_withheld", text=COUNT + " " + HUMAN, citations=[], why="A count of people was asked for.", count_withheld=True)
    matched = _match(question, pinned["pages"], on)
    if matched["ambiguous"]:
        return _finish(frame, outcome="ambiguous", text=AMBIGUOUS + " " + HUMAN, citations=matched["citations"], why="More than one benefit was named.")
    if not matched["citations"]:
        return _finish(frame, outcome="not_in_knowledge_base", text=NOT_FOUND + " " + HUMAN, citations=[], why="No pinned page matched.")
    if not any(row["quoted"] for row in matched["citations"]):
        return _finish(frame, outcome="stale", text=STALE + " " + HUMAN, citations=matched["citations"], why="The matching page is past its review date.")
    text = "This is general information from the pinned page. It is not a decision about you."
    for row in matched["citations"]:
        if not row["quoted"]:
            continue
        text += (
            f" {row['title']} ({row['publisher']}). Last reviewed {row['last_reviewed']}. "
            f"Review due {row['review_due']}. {row['url']} {row['quoted_text']} {row['boundary']}"
        )
    text += " " + HUMAN
    return _finish(frame, outcome="information", text=text, citations=matched["citations"], why="General information from a current pinned page.")


def record_resident_approval(result: dict, directory: dict, approval: dict) -> dict:
    """Stage the summary only when the named resident approves this content hash."""

    updated = deepcopy(result)
    _force(updated)
    updated["human_approval"] = None
    updated["staged"] = False
    if not isinstance(approval, dict):
        updated["blocked_reason"] = "approval_not_object"
        return updated
    if approval.get("item") != "adviser-summary" or approval.get("decision") != "approve-summary":
        updated["blocked_reason"] = "wrong_item"
        return updated
    presented = _hash(result)
    if approval.get("content_hash") != result.get("content_hash") or approval.get("content_hash") != presented:
        updated["blocked_reason"] = "content_hash_mismatch"
        return updated
    if approval.get("enquiry_id") != result.get("enquiry_id"):
        updated["blocked_reason"] = "enquiry_mismatch"
        return updated
    reason = _ack(result, approval)
    if reason:
        updated["blocked_reason"] = reason
        return updated
    person, role_reason = _named_resident(result, directory, approval.get("approver_ref"))
    if role_reason:
        updated["blocked_reason"] = role_reason
        return updated
    updated["human_approval"] = {
        "item": "adviser-summary",
        "approver_ref": person["ref"],
        "content_hash": result["content_hash"],
        "recorded": True,
        "decides_eligibility": False,
    }
    updated["staged"] = True
    _force(updated)
    row = {
        "enquiry_id": result.get("enquiry_id"),
        "content_hash": result["content_hash"],
        "resident_ref": person["ref"],
        "summary": deepcopy(result.get("summary")),
        "marking": deepcopy(result.get("marking")),
        "legal_hold": result.get("legal_hold"),
        "retention": list(result.get("retention") or []),
        "eligibility_decided": False,
        "award_amount": None,
        "claim_submitted": False,
        "sent": False,
        "production_written": False,
        "store": "synthetic",
    }
    _STORE[f"{result.get('enquiry_id')}:{result['content_hash']}"] = row
    updated["staging_store"] = "synthetic"
    updated["content_hash"] = result["content_hash"]
    return updated


def staged_row(enquiry_id: str, content_hash: str) -> dict | None:
    row = _STORE.get(f"{enquiry_id}:{content_hash}")
    return deepcopy(row) if isinstance(row, dict) else None


def _match(question: str, pages: list[dict], on: date) -> dict:
    usable = _without_instructions(question)
    found = benefits_in(usable)
    if len(found) > 1:
        return {"ambiguous": True, "citations": _unquoted_benefits(found, pages, on)}
    kinds = [kind for kind in kinds_in(usable) if kind in {"what", "apply", "evidence"}]
    wanted: list[tuple[str, str]] = []
    if category_hit(usable, "advice"):
        wanted.append(("advice", "advice"))
    if category_hit(usable, "adjustment"):
        wanted.append(("adjustment", "adjustment"))
    if found:
        if not kinds:
            kinds = ["what"]
        for kind in kinds:
            wanted.append((found[0], kind))
    citations = []
    for benefit, kind in wanted:
        for page in find_pages(pages, benefit, kind):
            citations.append(_citation(page, on, part="body"))
    return {"ambiguous": False, "citations": citations}


def _urgent_citations(pages: list[dict], on: date | None) -> tuple[list[dict], str]:
    if on is None:
        return [], ""
    rows = []
    quoted = []
    for page in find_pages(pages, "urgent", "urgent"):
        row = _citation(page, on, part="body")
        rows.append(row)
        if row["quoted"]:
            quoted.append(row["quoted_text"])
    return rows, " ".join(quoted)


def _boundary_citations(matched: dict) -> list[dict]:
    rows = []
    for row in matched.get("citations") or []:
        copy = dict(row)
        if row.get("stale") or row.get("unreadable"):
            copy["quoted"] = False
            copy["quoted_text"] = None
        else:
            copy["quoted"] = True
            copy["quoted_part"] = "boundary"
            copy["quoted_text"] = row.get("boundary")
        rows.append(copy)
    return rows


def _unquoted_benefits(benefits: list[str], pages: list[dict], on: date) -> list[dict]:
    rows = []
    for benefit in benefits:
        for page in find_pages(pages, benefit, "what"):
            row = _citation(page, on, part="body")
            row["quoted"] = False
            row["quoted_text"] = None
            rows.append(row)
    return rows


def _citation(page: dict, on: date, *, part: str) -> dict:
    status = review_status(page, on)
    quoted = bool(status["quote"])
    return {
        "page_id": page.get("page_id"),
        "title": page.get("title"),
        "url": page.get("url"),
        "publisher": page.get("publisher"),
        "last_reviewed": status["last_reviewed"],
        "review_due": status["review_due"],
        "stale": status["stale"],
        "unreadable": status["unreadable"],
        "coerced": False,
        "quoted": quoted,
        "quoted_part": part if quoted else None,
        "quoted_text": page.get("body") if quoted else None,
        "boundary": page.get("boundary"),
        "synthetic_figure": page.get("synthetic_figure") is True,
        "marking": page.get("marking"),
        "legal_hold": page.get("legal_hold") is True,
        "retention": list(page.get("retention") or []),
    }


def _frame(**kwargs) -> dict:
    return kwargs


def _finish(frame: dict, *, outcome: str, text: str, citations: list[dict], why: str, include_question: bool = True, count_withheld: bool = False) -> dict:
    citations = sorted(citations, key=lambda row: str(row.get("page_id")))
    any_stale = any(row.get("stale") or row.get("unreadable") for row in citations)
    quoted = [row for row in citations if row.get("quoted")]
    sources_current = bool(quoted) and not any_stale
    if outcome in {"unreadable_date", "unreadable_question", "too_long", "withheld"}:
        sources_current = False
    if outcome == "urgent_human" and not quoted:
        sources_current = False
    retention = list(frame["retention"])
    hold = bool(frame["hold"])
    for row in citations:
        if row.get("legal_hold"):
            hold = True
        for label in row.get("retention") or []:
            if label not in retention:
                retention.append(label)
    masked = frame["masked"] if include_question and not frame["withheld"] else None
    if masked is not None:
        frame["mask_report"]["masked_text_included"] = True
    urgent = list(frame["urgent"])
    summary = {
        "enquiry_id": _safe_id(frame["working"].get("enquiry_id")),
        "resident_ref": frame["person"]["ref"] if frame["person"] else None,
        "outcome": outcome,
        "why": why,
        "question_masked": masked,
        "question_withheld": not include_question or frame["withheld"],
        "pages": [
            {
                "page_id": row["page_id"],
                "url": row["url"],
                "publisher": row["publisher"],
                "last_reviewed": row["last_reviewed"],
                "quoted": row["quoted"],
            }
            for row in citations
        ],
        "urgent_categories": urgent,
        "not_a_decision": True,
        "resident_must_approve": True,
        "values_copied": False,
    }
    acknowledgements = ["pins_seen"]
    if urgent:
        acknowledgements.append("urgent_seen")
    if any_stale or outcome in {"stale", "unreadable_date"}:
        acknowledgements.append("stale_seen")
    if frame["diffs"]:
        acknowledgements.append("sources_seen")
    if category_hit(frame["question"], "adjustment"):
        acknowledgements.append("adjustment_seen")
    if frame["reading"].get("unparseable") or frame["reading"].get("ambiguous"):
        if "date_seen" not in acknowledgements:
            acknowledgements.append("date_seen")
    if outcome == "unreadable_date" and "stale_seen" in acknowledgements:
        pass
    result = {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "autonomy": "A0",
        "council": "Northmarsh Borough Council",
        "fictional": True,
        "enquiry_id": summary["enquiry_id"],
        "resident_ref": summary["resident_ref"],
        "as_of": frame["reading"].get("iso"),
        "date_reading": {
            "reason": frame["reading"].get("reason"),
            "unparseable": frame["reading"].get("unparseable"),
            "ambiguous": frame["reading"].get("ambiguous"),
            "coerced": False,
        },
        "outcome": outcome,
        "answer_text": text,
        "summary": summary,
        "citations": citations,
        "human_route_offered": True,
        "human_approval": None,
        "staged": False,
        "sent": False,
        "claim_submitted": False,
        "claim_completed": False,
        "eligibility_decided": False,
        "entitlement_estimated": False,
        "award_calculated": False,
        "award_amount": None,
        "figures_stated_as_current": False,
        "synthetic_figure_quoted": any(row.get("quoted") and row.get("synthetic_figure") for row in citations),
        "sources_current": sources_current,
        "may_be_relied_on_as_a_decision": False,
        "instructions_followed": False,
        "caller_rules_applied": False,
        "caller_pages_applied": False,
        "caller_directory_applied": False,
        "approval_marker_trusted": False,
        "role_in_text_trusted": False,
        "clearance_in_text_trusted": False,
        "biased_criteria_applied": False,
        "marked_acceptable": False,
        "coerced": False,
        "described_as_anonymised": False,
        "further_personal_data_requested": False,
        "people_count_published": None,
        "small_number_suppressed": bool(count_withheld or category_hit(frame["question"], "count")),
        "urgent_categories": urgent,
        "cue_copied": False,
        "adjustment_requested": category_hit(frame["question"], "adjustment"),
        "duty_decided": False,
        "caller_rule_seen": frame["rules_present"],
        "approval_marker_seen": category_hit(frame["question"], "approval_marker"),
        "clearance_claimed": clearance_claimed(frame["question"]),
        "prompt_injection": {
            "signals": _signals(frame["question"]),
            "followed": False,
            "ignored_request_keys": frame["ignored_keys"],
        },
        "page_diff": frame["diffs"],
        "marking": {
            "applied": frame["applied"] if frame["withheld"] or content_markings(frame["question"]) else "OFFICIAL",
            "above_ceiling": frame["withheld"],
            "ceiling": _ceiling(frame["person"]),
            "self_declared_clearance_used": False,
        },
        "legal_hold": hold,
        "retention": retention,
        "masking": frame["mask_report"],
        "uk_identifiers": frame["identifiers"],
        "front_door": frame["route"],
        "uk_context": uk_context(),
        "required_acknowledgements": acknowledgements,
        "body_copied": False,
        "blocked_reason": None,
    }
    if frame["withheld"]:
        result["marking"]["applied"] = frame["applied"]
    _force(result)
    result["content_hash"] = _hash(result)
    return result


def _urgent_categories(text: str) -> list[str]:
    found = []
    for name in SAFETY:
        if name in {"distress", "domestic_abuse", "safeguarding"}:
            if safety_hit(text, name):
                found.append(name)
        elif category_hit(text, name):
            found.append(name)
    return found


def _signals(text: str) -> list[str]:
    found = []
    if category_hit(text, "embedded_instruction"):
        found.append("embedded_instruction")
    return found


def _without_instructions(text: str) -> str:
    kept = []
    for sentence in sentences(text):
        if category_hit(sentence, "embedded_instruction"):
            continue
        kept.append(sentence)
    return " ".join(kept)


def _resident(directory: dict, ref: object) -> dict | None:
    if not isinstance(ref, str):
        return None
    for person in directory.get("people") or []:
        if person.get("ref") == ref and person.get("role") == "resident" and person.get("guest") is not True:
            return person
    return None


def _ceiling(person: dict | None) -> str:
    if person and person.get("clearance") in RANK:
        return person["clearance"]
    return "OFFICIAL"


def _named_resident(result: dict, directory: dict, approver_ref: object) -> tuple[dict | None, str | None]:
    pinned = load_directory()
    if directory != pinned:
        return None, "caller_directory_not_used"
    if approver_ref != result.get("resident_ref"):
        return None, "not_the_named_resident"
    person = None
    for row in pinned.get("people") or []:
        if row.get("ref") == approver_ref:
            person = row
            break
    if person is None or person.get("guest") is True or person.get("role") != "resident":
        return None, "approver_not_directory_resident"
    return person, None


def _ack(result: dict, approval: dict) -> str | None:
    for key in result.get("required_acknowledgements") or []:
        if approval.get(key) is not True:
            return f"{key}_not_boolean_true"
    return None


def _strip(request: dict) -> tuple[dict, list[str]]:
    ignored = sorted(key for key in PROHIBITED_KEYS if key in request)
    return {key: value for key, value in request.items() if key not in PROHIBITED_KEYS}, ignored


def _safe_id(value: object) -> str:
    if isinstance(value, str) and value.startswith("SYN-") and len(value) <= 44:
        return value
    return "unspecified"


def _no_identifiers() -> dict:
    return {
        "called": False,
        "experiment_id": "exp-08-uk-pii-redaction-gateway",
        "count": 0,
        "types": [],
        "output_is_anonymised": False,
        "values_stored": False,
        "redacted_text_copied": False,
    }


def _force(result: dict) -> None:
    result["eligibility_decided"] = False
    result["entitlement_estimated"] = False
    result["award_calculated"] = False
    result["award_amount"] = None
    result["claim_submitted"] = False
    result["claim_completed"] = False
    result["sent"] = False
    result["figures_stated_as_current"] = False
    result["may_be_relied_on_as_a_decision"] = False
    result["instructions_followed"] = False
    result["caller_rules_applied"] = False
    result["caller_pages_applied"] = False
    result["caller_directory_applied"] = False
    result["approval_marker_trusted"] = False
    result["role_in_text_trusted"] = False
    result["clearance_in_text_trusted"] = False
    result["biased_criteria_applied"] = False
    result["marked_acceptable"] = False
    result["coerced"] = False
    result["described_as_anonymised"] = False
    result["further_personal_data_requested"] = False
    result["people_count_published"] = None
    result["cue_copied"] = False
    result["duty_decided"] = False
    result["body_copied"] = False
    injection = result.get("prompt_injection")
    if isinstance(injection, dict):
        injection["followed"] = False
    marking = result.get("marking")
    if isinstance(marking, dict):
        marking["self_declared_clearance_used"] = False


def _projection(result: dict) -> dict:
    summary = result.get("summary") or {}
    return {
        "enquiry_id": result.get("enquiry_id"),
        "resident_ref": result.get("resident_ref"),
        "as_of": result.get("as_of"),
        "outcome": result.get("outcome"),
        "answer_text": result.get("answer_text"),
        "summary": summary,
        "citations": [
            {
                "page_id": row.get("page_id"),
                "url": row.get("url"),
                "publisher": row.get("publisher"),
                "last_reviewed": row.get("last_reviewed"),
                "quoted": row.get("quoted"),
                "quoted_text": row.get("quoted_text"),
            }
            for row in result.get("citations") or []
        ],
        "urgent_categories": result.get("urgent_categories"),
        "marking": result.get("marking"),
        "legal_hold": result.get("legal_hold"),
        "retention": result.get("retention"),
        "sources_current": result.get("sources_current"),
        "eligibility_decided": False,
        "award_amount": None,
    }


def _hash(result: dict) -> str:
    raw = json.dumps(_projection(result), sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Answer one synthetic benefits question.")
    parser.add_argument("--request", required=True)
    parser.add_argument("--as-of", required=True)
    args = parser.parse_args(argv)
    result = answer_question(_load(Path(args.request)), as_of=args.as_of)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
