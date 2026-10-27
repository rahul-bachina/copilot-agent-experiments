"""Draft one contact-centre reply from the synthetic catalogue.

The same enquiry and the same as-of date produce the same JSON. Nothing is
sent, nothing is written to a case, and eligibility is not decided.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from catalogue import (  # noqa: E402
        COUNCIL,
        STALE_AFTER_DAYS,
        age_days,
        is_stale,
        match_articles,
    )
    from injection import signals_in, strip_instruction_sentences  # noqa: E402
    from sources import source_rows  # noqa: E402
else:
    from .catalogue import (
        COUNCIL,
        STALE_AFTER_DAYS,
        age_days,
        is_stale,
        match_articles,
    )
    from .injection import signals_in, strip_instruction_sentences
    from .sources import source_rows

LABEL = "DRAFT FOR ADVISER REVIEW"
AI_DISCLOSURE = (
    "This response has been written by an automated AI chatbot. "
    "It is not a council officer. You can ask for a person, and you can use "
    "the council's phone or face-to-face route."
)
EMERGENCY_TEXT = (
    "If you or someone else is in immediate danger, call 999. "
    "This response has been written by an automated AI chatbot. "
    "It cannot take an emergency call, and it has not contacted anyone. "
    "A person at the council needs this conversation if it is about a council service."
)
VULNERABLE_TEXT = (
    "A person needs to take this conversation. "
    "This response has been written by an automated AI chatbot. "
    "It cannot decide whether you qualify for a service, and it has not contacted anyone. "
    "If you are in immediate danger, call 999. "
    "You can also use the council's phone or face-to-face route."
)
ELIGIBILITY_TEXT = (
    "A person decides whether you qualify. This assistant does not. "
    "This response has been written by an automated AI chatbot. "
    "Nothing has been sent and no case has been created."
)
STATUTORY_TEXT = (
    "A person decides applications for this service. The contact page is cited "
    "when it is inside the review window. "
    "This response has been written by an automated AI chatbot. "
    "Nothing has been sent and no case has been created."
)
STALE_TEXT = (
    "A matching page is outside the review window, so its text is not quoted. "
    "A person needs to check the council's own page. "
    "This response has been written by an automated AI chatbot. "
    "Nothing has been sent and no case has been created."
)
NOT_FOUND_TEXT = (
    "The published pages in this starter do not contain that answer. "
    "A person needs to check the council's own page. "
    "This response has been written by an automated AI chatbot. "
    "Nothing has been sent and no case has been created."
)
AMBIGUOUS_TEXT = (
    "More than one published page matched. This assistant has not chosen between them. "
    "A person needs to pick the page. "
    "This response has been written by an automated AI chatbot. "
    "Nothing has been sent."
)
ACCOUNT_TEXT = (
    "This assistant cannot see an account or a balance. "
    "A person with access to the council's own system would need to look that up. "
    "This response has been written by an automated AI chatbot. "
    "Nothing has been sent."
)
PAYMENT_TEXT = (
    "This assistant cannot take or refund a payment. "
    "This response has been written by an automated AI chatbot. "
    "Nothing has been sent."
)
ENFORCEMENT_TEXT = (
    "This assistant cannot issue, cancel, or waive a penalty charge. "
    "A person in the council decides that. "
    "This response has been written by an automated AI chatbot. "
    "Nothing has been sent."
)
TOO_LONG_TEXT = (
    "This enquiry is longer than this starter will read. "
    "A person needs to take it. "
    "This response has been written by an automated AI chatbot. "
    "Nothing has been sent."
)
REFUSAL_TEXT = (
    "This starter only reads a record marked synthetic. "
    "The enquiry text has not been stored."
)

CONFIRMATION = (
    "I have read the draft and I am not asking the agent to send, decide, or write a case"
)
ALLOWED_REVIEW = {"accept_draft", "reject_draft", "take_handover"}
PROHIBITED_REVIEW = {
    "send_message",
    "create_case",
    "decide_eligible",
    "book_appointment",
    "take_payment",
    "waive_charge",
    "release_to_resident",
    "approve_application",
}
PROHIBITED_KEYS = {
    "eligibility_decision",
    "eligibility_decided",
    "case_created",
    "message_sent",
    "human_approval",
    "adviser_decision",
    "send_email",
    "create_case",
    "appointment_booked",
    "payment_taken",
    "override_stale",
    "released_to_resident",
    "actions_taken",
    "adviser_accepted_published_text",
}
CHANNELS = {"web_chat", "phone_note", "email_paste", "adviser_desk"}
MAX_TEXT = 4000
_ENQUIRY_ID = re.compile(r"^SYN-[A-Z0-9-]{1,40}$")
_ADVISER_ID = re.compile(r"^SYN-ADV-\d{2}$")

_EMERGENCY = re.compile(
    r"("
    r"gas leak|smell of gas|smell gas|"
    r"\bon fire\b|house fire|there is a fire|"
    r"not breathing|\bunconscious\b|chest pain|heart attack|\bstroke\b|"
    r"suicid|kill myself|end my life|self-harm|self harm|hurt myself|"
    r"child abuse|hurting my child|child in danger|child at risk|"
    r"he is hitting me|she is hitting me|being assaulted|"
    r"\bcollapsed\b"
    r")",
    re.IGNORECASE,
)
_VULNERABLE = re.compile(
    r"("
    r"homeless tonight|nowhere to sleep|sleeping rough|"
    r"\bno food\b|cannot afford food|can't afford food|nothing to eat|"
    r"being evicted today|eviction today|"
    r"\bsafeguarding\b|domestic abuse|"
    r"no heating"
    r")",
    re.IGNORECASE,
)
_HEATING_RISK = re.compile(r"\b(baby|child|elderly|disabled|disability|pregnant|infant)\b", re.IGNORECASE)
_ELIGIBILITY = re.compile(
    r"("
    r"am i eligible|do i qualify|am i entitled|"
    r"will i get|approve my application|write off"
    r")",
    re.IGNORECASE,
)
_ACCOUNT = re.compile(
    r"("
    r"\bbalance\b|how much (council tax )?do i owe|what do i owe|"
    r"my account|account number|rent account|"
    r"my council tax (bill|account|balance)"
    r")",
    re.IGNORECASE,
)
_PAYMENT = re.compile(
    r"(charge my card|take (a |the )?payment|\brefund me\b|\bpay now\b)",
    re.IGNORECASE,
)
_ENFORCEMENT = re.compile(
    r"("
    r"cancel (my )?(pcn|penalty|fine)|"
    r"waive the (charge|fine|pcn)|"
    r"issue a (fine|pcn|penalty)"
    r")",
    re.IGNORECASE,
)


def _flags(**overrides: bool) -> dict:
    base = {
        "emergency": False,
        "vulnerability": False,
        "eligibility_asked": False,
        "eligibility_decided": False,
        "case_created": False,
        "message_sent": False,
        "appointment_booked": False,
        "payment_taken": False,
        "enforcement_action": False,
        "released_to_resident": False,
        "any_article_stale": False,
        "stale_article_quoted": False,
        "live_record_refused": False,
        "text_too_long": False,
    }
    base.update(overrides)
    return base


def _lock_actions(flags: dict) -> dict:
    """These cannot be turned on by the enquiry, the model, or a review."""
    for key in (
        "eligibility_decided",
        "case_created",
        "message_sent",
        "appointment_booked",
        "payment_taken",
        "enforcement_action",
        "released_to_resident",
        "stale_article_quoted",
    ):
        flags[key] = False
    return flags


def _safe_id(value) -> str:
    if isinstance(value, str) and _ENQUIRY_ID.fullmatch(value):
        return value
    return "unspecified"


def _channel(value) -> str:
    if isinstance(value, str) and value in CHANNELS:
        return value
    return "unspecified"


def _citation(
    article: dict,
    as_of: date,
    stale_after_days: int,
    *,
    include_body: bool,
    quoted_in_answer: bool = False,
) -> dict:
    reviewed = date.fromisoformat(article["last_reviewed"])
    stale = is_stale(reviewed, as_of, stale_after_days)
    row = {
        "article_id": article["id"],
        "title": article["title"],
        "url": article["url"],
        "last_reviewed": article["last_reviewed"],
        "stale": stale,
        "quoted_in_answer": bool(quoted_in_answer and include_body and not stale),
    }
    if include_body and not stale:
        row["body"] = article["body"]
    return row


def _handover(required: bool, urgency: str, queue: str | None, reason: str, summary: str) -> dict:
    return {
        "required": required,
        "urgency": urgency,
        "queue": queue,
        "reason": reason,
        "summary": summary,
    }


def _finish(
    draft: dict,
    *,
    outcome: str,
    text: str | None,
    article_id: str | None,
    sufficient: bool,
    citations: list,
    handover: dict,
    flags: dict,
) -> dict:
    draft["outcome"] = outcome
    draft["answer"] = {
        "text": text,
        "verbatim_article_id": article_id,
        "sufficient": sufficient,
    }
    draft["citations"] = citations
    draft["handover"] = handover
    draft["flags"] = _lock_actions(flags)
    draft["human_approval"] = None
    draft["actions_taken"] = []
    draft["adviser_accepted_published_text"] = False
    draft["model_called"] = False
    draft["network_called"] = False
    draft["enquiry_text_echoed"] = False
    return draft


def _vulnerability_queue(text: str) -> str:
    if re.search(r"domestic abuse|safeguarding", text, re.IGNORECASE):
        return "safeguarding"
    if re.search(r"homeless|evict", text, re.IGNORECASE):
        return "housing_options"
    return "welfare"


def _is_vulnerable(text: str) -> bool:
    if not _VULNERABLE.search(text):
        return False
    if re.search(r"no heating", text, re.IGNORECASE) and not _HEATING_RISK.search(text):
        # "no heating" alone is not enough. The other phrases still count.
        without_heating = re.sub(r"no heating", " ", text, flags=re.IGNORECASE)
        return _VULNERABLE.search(without_heating) is not None
    return True


def triage(enquiry: dict, as_of: date | str, stale_after_days: int = STALE_AFTER_DAYS) -> dict:
    if isinstance(as_of, str):
        as_of = date.fromisoformat(as_of)
    if not isinstance(enquiry, dict):
        raise TypeError("enquiry must be an object")
    if stale_after_days < 1:
        raise ValueError("stale_after_days must be at least 1")

    ignored = sorted(key for key in PROHIBITED_KEYS if key in enquiry)
    payload = {key: value for key, value in enquiry.items() if key not in PROHIBITED_KEYS}

    rows = source_rows(as_of, stale_after_days, age_days)
    any_source_stale = any(row["stale"] for row in rows)

    draft: dict = {
        "label": LABEL,
        "catalogue_id": "V006",
        "council": dict(COUNCIL),
        "enquiry_id": _safe_id(payload.get("enquiry_id")),
        "as_of": as_of.isoformat(),
        "channel": _channel(payload.get("channel")),
        "ai_disclosure": AI_DISCLOSURE,
        "stale_after_days": stale_after_days,
        "sources_and_currency": rows,
        "any_source_stale": any_source_stale,
        "rules_current": not any_source_stale,
        "prohibited_keys_ignored": ignored,
        "prompt_injection": {"detected": False, "followed": False, "signals": []},
    }

    if payload.get("synthetic") is not True:
        flags = _flags(live_record_refused=True)
        return _finish(
            draft,
            outcome="refused_not_synthetic",
            text=REFUSAL_TEXT,
            article_id=None,
            sufficient=False,
            citations=[],
            handover=_handover(True, "routine", "contact_centre", "not_synthetic", "Record was not marked synthetic. Text was not stored."),
            flags=flags,
        )

    scanned = " ".join(
        part
        for part in (
            payload.get("text") if isinstance(payload.get("text"), str) else "",
            payload.get("enquiry_id") if isinstance(payload.get("enquiry_id"), str) else "",
            payload.get("channel") if isinstance(payload.get("channel"), str) else "",
        )
        if part
    )
    found = signals_in(scanned)
    draft["prompt_injection"] = {"detected": bool(found), "followed": False, "signals": found}

    text = payload.get("text") if isinstance(payload.get("text"), str) else ""
    if len(text) > MAX_TEXT:
        return _finish(
            draft,
            outcome="handover",
            text=TOO_LONG_TEXT,
            article_id=None,
            sufficient=False,
            citations=[],
            handover=_handover(True, "routine", "contact_centre", "text_too_long", "Enquiry exceeded the length this starter will read."),
            flags=_flags(text_too_long=True),
        )

    if _EMERGENCY.search(text):
        return _finish(
            draft,
            outcome="safe_handover",
            text=EMERGENCY_TEXT,
            article_id=None,
            sufficient=False,
            citations=[],
            handover=_handover(
                True,
                "emergency",
                "contact_centre_supervisor",
                "emergency_phrase",
                "Emergency phrase matched. Fixed 999 script. No service page quoted.",
            ),
            flags=_flags(emergency=True),
        )

    if _is_vulnerable(text):
        return _finish(
            draft,
            outcome="safe_handover",
            text=VULNERABLE_TEXT,
            article_id=None,
            sufficient=False,
            citations=[],
            handover=_handover(
                True,
                "vulnerable",
                _vulnerability_queue(text),
                "vulnerability_phrase",
                "Vulnerability phrase matched. Human handover. No service page quoted.",
            ),
            flags=_flags(vulnerability=True),
        )

    usable = strip_instruction_sentences(text)
    eligibility = bool(_ELIGIBILITY.search(usable))
    account = bool(_ACCOUNT.search(usable))
    payment = bool(_PAYMENT.search(usable))
    enforcement = bool(_ENFORCEMENT.search(usable))
    matched = match_articles(usable)

    if enforcement:
        return _finish(
            draft,
            outcome="handover",
            text=ENFORCEMENT_TEXT,
            article_id=None,
            sufficient=False,
            citations=[],
            handover=_handover(True, "routine", "parking", "enforcement", "Enforcement wording matched. No charge was issued, cancelled, or waived."),
            flags=_flags(eligibility_asked=eligibility),
        )

    if payment:
        return _finish(
            draft,
            outcome="handover",
            text=PAYMENT_TEXT,
            article_id=None,
            sufficient=False,
            citations=[],
            handover=_handover(True, "routine", "revenues", "payment", "The enquiry asked the assistant to take or refund money. It cannot."),
            flags=_flags(eligibility_asked=eligibility),
        )

    if account:
        return _finish(
            draft,
            outcome="handover",
            text=ACCOUNT_TEXT,
            article_id=None,
            sufficient=False,
            citations=[],
            handover=_handover(True, "routine", "revenues", "account_lookup", "The enquiry asks for an account or a balance. This starter cannot see one."),
            flags=_flags(eligibility_asked=eligibility),
        )

    if eligibility:
        statutory = [article for article in matched if article["kind"] == "statutory_contact"]
        if len(statutory) == 1:
            article = statutory[0]
            stale = is_stale(date.fromisoformat(article["last_reviewed"]), as_of, stale_after_days)
            if stale:
                return _finish(
                    draft,
                    outcome="stale_article",
                    text=STALE_TEXT,
                    article_id=None,
                    sufficient=False,
                    citations=[_citation(article, as_of, stale_after_days, include_body=False)],
                    handover=_handover(True, "routine", article["queue"], "eligibility_not_decided", f"Eligibility was asked. Page {article['id']} is stale and was not quoted."),
                    flags=_flags(eligibility_asked=True, any_article_stale=True),
                )
            return _finish(
                draft,
                outcome="handover",
                text=ELIGIBILITY_TEXT,
                article_id=None,
                sufficient=False,
                citations=[_citation(article, as_of, stale_after_days, include_body=True)],
                handover=_handover(True, "routine", article["queue"], "eligibility_not_decided", f"Eligibility was asked. Not decided. Contact page {article['id']} cited."),
                flags=_flags(eligibility_asked=True),
            )
        if len(statutory) > 1:
            return _finish(
                draft,
                outcome="ambiguous",
                text=AMBIGUOUS_TEXT,
                article_id=None,
                sufficient=False,
                citations=[_citation(article, as_of, stale_after_days, include_body=False) for article in statutory],
                handover=_handover(True, "routine", "contact_centre", "eligibility_not_decided", "Eligibility was asked against more than one service. Not decided. No page was chosen."),
                flags=_flags(eligibility_asked=True),
            )
        return _finish(
            draft,
            outcome="handover",
            text=ELIGIBILITY_TEXT,
            article_id=None,
            sufficient=False,
            citations=[],
            handover=_handover(True, "routine", "contact_centre", "eligibility_not_decided", "Eligibility was asked. No contact page matched. Not decided."),
            flags=_flags(eligibility_asked=True),
        )

    if len(matched) > 1:
        stale_any = any(is_stale(date.fromisoformat(article["last_reviewed"]), as_of, stale_after_days) for article in matched)
        return _finish(
            draft,
            outcome="ambiguous",
            text=AMBIGUOUS_TEXT,
            article_id=None,
            sufficient=False,
            citations=[_citation(article, as_of, stale_after_days, include_body=False) for article in matched],
            handover=_handover(True, "routine", "contact_centre", "ambiguous_pages", "More than one page matched. None was quoted."),
            flags=_flags(any_article_stale=stale_any),
        )

    if len(matched) == 1:
        article = matched[0]
        stale = is_stale(date.fromisoformat(article["last_reviewed"]), as_of, stale_after_days)
        if stale:
            return _finish(
                draft,
                outcome="stale_article",
                text=STALE_TEXT,
                article_id=None,
                sufficient=False,
                citations=[_citation(article, as_of, stale_after_days, include_body=False)],
                handover=_handover(True, "routine", article["queue"], "stale_page", f"Page {article['id']} is stale. Body not quoted."),
                flags=_flags(any_article_stale=True),
            )
        if article["kind"] == "statutory_contact":
            return _finish(
                draft,
                outcome="handover",
                text=STATUTORY_TEXT,
                article_id=None,
                sufficient=False,
                citations=[_citation(article, as_of, stale_after_days, include_body=True)],
                handover=_handover(True, "routine", article["queue"], "statutory_contact", f"Contact page {article['id']} cited. A person decides the application."),
                flags=_flags(),
            )
        return _finish(
            draft,
            outcome="published_answer",
            text=article["body"],
            article_id=article["id"],
            sufficient=True,
            citations=[_citation(article, as_of, stale_after_days, include_body=True, quoted_in_answer=True)],
            handover=_handover(False, "none", None, "published_page_matched", f"Routine published page {article['id']} matched. No eligibility decision."),
            flags=_flags(),
        )

    reason = "instruction_only" if found and not usable else "no_catalogue_page"
    summary = (
        "Instruction-shaped text was recorded and not followed. No service page matched."
        if reason == "instruction_only"
        else "No catalogue page matched."
    )
    return _finish(
        draft,
        outcome="not_in_catalogue",
        text=NOT_FOUND_TEXT,
        article_id=None,
        sufficient=False,
        citations=[],
        handover=_handover(True, "routine", "contact_centre", reason, summary),
        flags=_flags(),
    )


def _refuse_review(draft: dict, reason: str) -> dict:
    cleaned = json.loads(json.dumps(draft))
    cleaned["flags"] = _lock_actions(dict(cleaned.get("flags") or {}))
    cleaned["human_approval"] = None
    cleaned["adviser_accepted_published_text"] = False
    cleaned["actions_taken"] = []
    return {"status": "refused", "refusal_reason": reason, "draft": cleaned}


def record_adviser_review(draft: dict, review: dict) -> dict:
    """Record a separate adviser review. The enquiry text is not an input.

    Accepting a published page does not send it, write a case, or decide
    eligibility. Those decisions are refused.
    """
    if not isinstance(draft, dict) or draft.get("label") != LABEL:
        raise TypeError("draft must be a front-door result")
    if not isinstance(review, dict):
        return _refuse_review(draft, "review_not_an_object")

    decision = review.get("decision")
    if decision in PROHIBITED_REVIEW or decision not in ALLOWED_REVIEW:
        return _refuse_review(draft, "prohibited_action")
    if review.get("approver_role") != "Contact centre adviser":
        return _refuse_review(draft, "approver_role")
    approver_id = review.get("approver_id")
    if not isinstance(approver_id, str) or not _ADVISER_ID.fullmatch(approver_id):
        return _refuse_review(draft, "approver_id")
    if review.get("confirmation") != CONFIRMATION:
        return _refuse_review(draft, "confirmation")

    cleaned = json.loads(json.dumps(draft))
    flags = _lock_actions(dict(cleaned.get("flags") or {}))
    cleaned["flags"] = flags
    cleaned["actions_taken"] = []
    cleaned["adviser_accepted_published_text"] = False
    cleaned["human_approval"] = None

    if decision == "accept_draft":
        published = (
            cleaned.get("outcome") == "published_answer"
            and cleaned.get("answer", {}).get("sufficient") is True
            and flags.get("emergency") is False
            and flags.get("vulnerability") is False
            and flags.get("any_article_stale") is False
            and flags.get("live_record_refused") is False
        )
        if not published:
            return _refuse_review(draft, "not_a_published_answer")
        cleaned["adviser_accepted_published_text"] = True

    cleaned["human_approval"] = {
        "decision": decision,
        "approver_role": "Contact centre adviser",
        "approver_id": approver_id,
        "effects": {
            "case_created": False,
            "message_sent": False,
            "eligibility_decided": False,
            "payment_taken": False,
            "appointment_booked": False,
            "enforcement_action": False,
            "released_to_resident": False,
        },
    }
    return {"status": "recorded", "refusal_reason": None, "draft": cleaned}


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Draft one council front-door reply.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--stale-after-days", type=int, default=STALE_AFTER_DAYS)
    parser.add_argument("--review", type=Path, help="Optional separate adviser review JSON.")
    args = parser.parse_args(argv)
    try:
        enquiry = _load(args.input)
        draft = triage(enquiry, args.as_of, args.stale_after_days)
        if args.review:
            review = _load(args.review)
            result = record_adviser_review(draft, review)
            json.dump(result, sys.stdout, indent=2, ensure_ascii=False)
        else:
            json.dump(draft, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
