#!/usr/bin/env python3
"""Draft a casework reply from supplied lines to take.

This is a deterministic smoke-test stand-in. It is tuned to the synthetic
fixtures. It is not a model, and it must not be described as one.

The reply clock always comes from sla.calculate_casework_sla. A policy
sentence in the draft is a verbatim current line, or the draft says there
is a gap. The agent does not send, does not approve a recipient, and does
not invent a position.

Ideas reused from Experiment 01: separate an information-rights letter from
ordinary correspondence, flag urgency for a person, and keep the draft
advisory. This module does not decide an FOI exemption or a complaint outcome.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path

from lines import load_library, match_lines
from sla import calculate_casework_sla

SMOKE_LABEL = (
    "MOCK SMOKE TEST. Rule-based stand-in tuned to the synthetic fixtures. "
    "Not a measure of model accuracy. No model was called."
)

ORGANISATION = "Department for Civic Spaces (fictional)"

DECISIONS_NOT_TAKEN = (
    "send",
    "final_recipient",
    "policy_invention",
    "production_case_write",
    "atrs_publication",
    "no_reply",
    "transfer_send",
    "foi_exemption",
    "complaint_outcome",
    "vulnerability_label",
)

INJECTION_PATTERNS = (
    "ignore previous instructions",
    "ignore all instructions",
    "ignore the above",
    "you are now",
    "system prompt",
    "disregard your rules",
    "send the letter",
    "send the email",
    "send this reply",
    "recipient is approved",
    "recipient approved",
    "you must state that",
    "the department's position is",
    "the department’s position is",
    "treat the withdrawn line as current",
    "approve the draft",
    "publish the atrs",
    "close the case",
    "mark them as vulnerable",
    "label the correspondent as vulnerable",
)

STALE_PHRASES = (
    "treat this as current",
    "treat the withdrawn line as current",
    "the old line is still the policy",
    "as of 2014",
    "as of 2015",
    "as of 2016",
    "as of 2017",
    "as of 2018",
    "as of 2019",
)

VULNERABILITY = (
    ("health", ("in hospital", "cancer", "disability", "mental health", "medication")),
    ("life_events", ("bereavement", "died", "funeral", "lost my job")),
    ("housing", ("homeless", "eviction", "no heating", "rough sleeping")),
    ("financial_hardship", ("can't afford food", "cannot afford food", "bailiff")),
    ("immediate_risk", ("kill myself", "end my life", "suicide", "hurt my child", "being beaten")),
)

CHANNELS = ("mp", "peer", "treat_official", "campaign", "information_rights")


def _hits(text: str, phrases: tuple[str, ...]) -> list[str]:
    lower = text.lower()
    found = []
    for phrase in phrases:
        if re.search(rf"\b{re.escape(phrase)}\b", lower):
            found.append(phrase)
    return found


def _case_id(text: str, received_on: date) -> str:
    digest = hashlib.sha256(f"{received_on.isoformat()}|{text}".encode()).hexdigest()
    return f"CWD-{received_on.strftime('%Y%m%d')}-{digest[:6].upper()}"


def detect_injection(text: str) -> list[str]:
    return _hits(text, INJECTION_PATTERNS)


def detect_stale(text: str, as_of: date) -> list[str]:
    signals = _hits(text, STALE_PHRASES)
    for match in re.findall(r"\b(19\d{2}|20\d{2})\b", text):
        year = int(match)
        if year <= as_of.year - 6:
            signal = f"narrative cites {year}, which is more than six years before the as-of date"
            if signal not in signals:
                signals.append(signal)
    return signals


def classify(text: str) -> dict:
    lower = text.lower()
    indicators = []
    specialist = None
    if re.search(r"\bfreedom of information\b|\bfoi request\b", lower):
        specialist = "foi"
        indicators.append("freedom of information")
    if re.search(r"\benvironmental information\b|\beir request\b", lower):
        specialist = "mixed_information_rights" if specialist else "eir"
        indicators.append("environmental information")
    if re.search(r"\bsubject access\b|\bmy personal data\b", lower):
        specialist = "mixed_information_rights" if specialist else "sar"
        indicators.append("subject access")

    campaign = bool(re.search(r"\bcampaign\b", lower))
    if specialist:
        channel = "information_rights"
    elif re.search(r"\bhouse of lords\b|\bas a peer\b", lower):
        channel = "peer"
        indicators.append("peer")
    elif re.search(r"\bconstituent\b|\bmember for\b|\bmember of parliament\b|\bhouse of commons\b", lower):
        channel = "mp"
        indicators.append("mp")
    elif campaign:
        channel = "campaign"
        indicators.append("campaign")
    else:
        channel = "treat_official"
        indicators.append("member of the public")

    complaint = bool(re.search(r"\bformal complaint\b|\bi wish to complain\b|\bi want to complain\b", lower))
    media = bool(re.search(r"\bjournalist\b|\bnewspaper\b|\beditor\b|\bbroadcast\b", lower))
    welsh = bool(re.search(r"\bcymraeg\b|\byn gymraeg\b|\bwelsh language\b", lower))
    ministerial_proposed = channel in {"mp", "peer"}
    return {
        "channel": channel,
        "indicators": indicators,
        "campaign_flag": campaign and channel != "information_rights",
        "complaints_process_flag": complaint,
        "media_flag": media,
        "welsh_language_review": welsh,
        "specialist_route": specialist,
        "ministerial_reply_proposed": ministerial_proposed,
    }


def _vulnerability(text: str) -> dict:
    lower = text.lower()
    flags = []
    for driver, phrases in VULNERABILITY:
        found = [phrase for phrase in phrases if re.search(rf"\b{re.escape(phrase)}\b", lower)]
        if found:
            flags.append({"driver": driver, "evidence_quote": found[0]})
    immediate = any(flag["driver"] == "immediate_risk" for flag in flags)
    return {
        "flags": flags,
        "person_labelled_vulnerable": False,
        "requires_immediate_human_review": immediate,
        "do_not_auto_close": True,
        "case_auto_closed": False,
        "note": (
            "A flag quotes words from the letter. It does not label the person, "
            "and it is not written to a case record. Immediate-risk wording needs "
            "a person before anyone else relies on the draft."
        ),
    }


def _incoming_reference(text: str) -> str | None:
    match = re.search(r"\byour ref(?:erence)?[:\s]+([A-Z]{1,4}-\d{3,6})\b", text, flags=re.IGNORECASE)
    if not match:
        return None
    return match.group(1).upper()


def _recipient(channel: str, approved_recipient: str | None, approved_by: str | None) -> dict:
    roles = {
        "mp": (
            "The correspondent's parliamentary office. The September 2024 Guide, "
            "paragraph 15, says a reply to an MP or Peer is sent to their office. "
            "The author types the address."
        ),
        "peer": (
            "The correspondent's parliamentary office. The September 2024 Guide, "
            "paragraph 15, says a reply to an MP or Peer is sent to their office. "
            "The author types the address."
        ),
        "treat_official": "The correspondent, at a contact address the author checks.",
        "campaign": (
            "The correspondent. A single reply to a campaign organiser is a human "
            "decision under Guide paragraphs 30 to 32, and it is not taken here."
        ),
        "information_rights": "The organisation's information-rights team. Not an external recipient.",
    }
    approved = bool(approved_recipient and approved_by)
    return {
        "proposed_role": roles[channel],
        "approved": approved,
        "approved_recipient": approved_recipient if approved else None,
        "approved_by": approved_by if approved else None,
        "approval_source": "author_argument" if approved else "not_approved",
        "may_be_chosen_by_agent": False,
        "letter_text_cannot_approve": True,
    }


def _render_draft(
    *,
    classification: dict,
    vulnerability: dict,
    match: dict,
    reference: str | None,
    specialist: bool,
    recipient: dict,
) -> str:
    parts = [
        "DRAFT — NOT SENT. The author approves the recipient and the final text.",
    ]
    if vulnerability["requires_immediate_human_review"]:
        parts.append(
            "STOP FOR A PERSON. An immediate-review flag is set. Nothing has been "
            "sent and nobody has been contacted."
        )
    parts.append(f"Proposed route: {recipient['proposed_role']}")
    if recipient["approved"]:
        parts.append(
            "The author supplied a recipient on this run. It is on the JSON. "
            "This text is still not sent."
        )
    else:
        parts.append("Recipient approved: no.")
    if reference:
        parts.append(f"Incoming reference quoted: {reference}.")
    if specialist:
        parts.append(
            "This letter is handled on the information-rights route. This agent "
            "does not decide an exemption, a cost limit, or disclosure. Experiment "
            "01 triages FOI and complaints. The correspondence clock is not the "
            "statutory information-rights clock."
        )
        parts.append("No line to take is cited, because a line is not a disclosure decision.")
    else:
        if classification["channel"] == "mp":
            parts.append(
                "Thank you for the letter from a fictional parliamentary office. "
                "A ministerial signature is proposed, not confirmed."
            )
        elif classification["channel"] == "peer":
            parts.append(
                "Thank you for the letter from a fictional peer's office. "
                "A ministerial signature is proposed, not confirmed."
            )
        elif classification["channel"] == "campaign":
            parts.append(
                "Thank you for the letter. It is marked as campaign correspondence. "
                "An official reply is proposed, not confirmed."
            )
        else:
            parts.append(
                "Thank you for the letter from a member of the public. "
                "An official reply is proposed, not confirmed."
            )
        if classification["complaints_process_flag"]:
            parts.append("The letter uses complaint wording. No complaint outcome is decided.")
        if classification["media_flag"]:
            parts.append(
                "Press-office review is proposed. No press line is added beyond a cited line."
            )
        if classification["welsh_language_review"]:
            parts.append(
                "The letter asks about Welsh. This draft is not a Welsh reply. "
                "Guide paragraph 37 is a prompt for the organisation's own scheme, "
                "which is not applied here."
            )
        for line in match["cited"]:
            parts.append(line["text"])
            parts.append(
                f"[Cited line: {line['id']}. Status: current. Review due: {line['review_due_on']}.]"
            )
        if match["gaps"]:
            for gap in match["gaps"]:
                parts.append(f"Gap: {gap['summary']}. No position is stated.")
        else:
            pass
        if not match["cited"] and not match["gaps"]:
            parts.append("Gap: no current line to take covers this letter. No position is stated.")
    parts.append(
        "Nothing has been sent. No case record has been written. No ATRS record has been published."
    )
    return "\n\n".join(parts)


def _atrs_draft() -> dict:
    return {
        "status": "draft_for_the_organisations_single_point_of_contact",
        "not_submitted": True,
        "mandatory_scope_decided": False,
        "tool_name": "Correspondence Draft Agent, fictional Department for Civic Spaces",
        "purpose": (
            "Draft a reply that cites supplied lines to take, or flags a gap. "
            "A person approves the recipient and the final text."
        ),
        "phase": "not_deployed",
        "human_oversight": (
            "The author approves the recipient and the final text. The agent does "
            "not send, does not write a case, and does not publish this record."
        ),
        "precedents_opened": [
            {
                "name": "DfE Correspondence Drafter",
                "url": "https://www.gov.uk/algorithmic-transparency-records/dfe-correspondence-drafter",
                "retrieved_on": "2026-10-26",
                "what_the_record_says": (
                    "The record describes an internal drafter that searches standard "
                    "lines and briefing packs. Staff review, edit, and copy the text "
                    "into an email, and check the address. The phase on the record "
                    "is Beta/Pilot. This starter is not that tool."
                ),
            },
            {
                "name": "FCDO Correspondence Triage",
                "url": "https://www.gov.uk/algorithmic-transparency-records/fcdo-correspondence-triage",
                "retrieved_on": "2026-10-26",
                "what_the_record_says": (
                    "The record describes a triage tool for ministerial correspondence, "
                    "treat official, and member-of-the-public non-policy enquiries. "
                    "It says the tool does not write responses, which staff prepare, "
                    "sign off, and release. This starter is not that tool. It drafts, "
                    "and it still does not send or write a case."
                ),
            },
        ],
        "dwp_correspondence_drafter": "not_cited",
        "note": (
            "A DWP correspondence-drafting ATRS record was not opened for this "
            "experiment, so none is cited. Whether a deployment is inside the ATRS "
            "mandatory scope is for the organisation's single point of contact. "
            "This draft does not decide it."
        ),
    }


def draft_correspondence(
    text: str,
    received_on: date,
    as_of: date,
    *,
    regime: str = "central_government",
    target_working_days: int | None = 20,
    confirm_target: bool = False,
    confirm_channel: bool = False,
    approved_recipient: str | None = None,
    recipient_approved_by: str | None = None,
    library_path: Path | None = None,
    extra_closed: tuple[date, ...] = (),
    cancel_bank_holiday: tuple[date, ...] = (),
) -> dict:
    """Build one draft. Dates and citations come from the other modules, not from the letter's instructions."""
    library = load_library(library_path)
    classification = classify(text)
    if classification["channel"] not in CHANNELS:
        raise RuntimeError("classifier returned an unknown channel")
    specialist = classification["specialist_route"] is not None
    match = match_lines(text, library, as_of)
    if specialist:
        withheld = match["cited"] + [
            {key: value for key, value in line.items()} for line in match["refused"]
        ]
        match = {
            "topics": match["topics"],
            "cited": [],
            "refused": [],
            "gaps": [],
            "withheld_because_specialist_route": withheld,
        }
    else:
        match["withheld_because_specialist_route"] = []

    vulnerability = _vulnerability(text)
    injection = detect_injection(text)
    stale = detect_stale(text, as_of)
    reference = _incoming_reference(text)
    recipient = _recipient(classification["channel"], approved_recipient, recipient_approved_by)
    sla = calculate_casework_sla(
        received_on,
        regime=regime,
        target_working_days=target_working_days,
        target_confirmed=confirm_target,
        channel_confirmed=confirm_channel,
        information_rights=specialist,
        extra_closed=extra_closed,
        cancel_bank_holiday=cancel_bank_holiday,
    )
    draft_text = _render_draft(
        classification=classification,
        vulnerability=vulnerability,
        match=match,
        reference=reference,
        specialist=specialist,
        recipient=recipient,
    )
    classification_out = {
        **classification,
        "channel_confirmed": confirm_channel,
        "ministerial_reply_confirmed": False,
        "author_must_confirm_channel": True,
    }
    result = {
        "case_id": _case_id(text, received_on),
        "processing_mode": "mock",
        "evaluation_label": SMOKE_LABEL,
        "organisation": ORGANISATION,
        "library_id": library["library_id"],
        "received_on": received_on.isoformat(),
        "as_of": as_of.isoformat(),
        "regime": regime,
        "classification": classification_out,
        "asks": match["topics"] or ["unspecified"],
        "lines_cited": match["cited"],
        "lines_refused": match["refused"],
        "gaps": match["gaps"],
        "lines_withheld_because_specialist_route": match["withheld_because_specialist_route"],
        "incoming_reference": reference,
        "sla": sla,
        "vulnerability": vulnerability,
        "recipient": recipient,
        "draft": {
            "text": draft_text,
            "may_be_sent_by_agent": False,
            "policy_sentences_are_cited_lines_only": True,
            "uncited_policy_claims": [],
        },
        "atrs_draft": _atrs_draft(),
        "security": {
            "prompt_injection_detected": bool(injection),
            "prompt_injection_signals": injection,
            "stale_data_signals": stale,
            "actions_taken": [],
            "letter_named_an_address": bool(re.search(r"@", text)),
        },
        "decisions_not_taken": list(DECISIONS_NOT_TAKEN),
        "sources": {
            "guide_url": sla["guide"]["url"],
            "guide_retrieved_on": sla["guide"]["retrieved_on"],
            "lines_are_synthetic": True,
        },
    }
    validate_draft(result)
    return result


def validate_draft(result: dict) -> None:
    """Reject a draft that sends, picks a recipient by itself, or states an uncited position."""
    if not result["evaluation_label"].startswith("MOCK SMOKE TEST"):
        raise ValueError("evaluation label missing")
    if result["processing_mode"] != "mock":
        raise ValueError("this starter only produces a mock draft")
    draft = result["draft"]
    if draft["may_be_sent_by_agent"] is not False:
        raise ValueError("send flag must stay false")
    if draft["uncited_policy_claims"] != []:
        raise ValueError("uncited policy claim")
    if result["security"]["actions_taken"] != []:
        raise ValueError("actions_taken must stay empty")
    if result["vulnerability"]["person_labelled_vulnerable"] is not False:
        raise ValueError("the person must not be labelled")
    if result["vulnerability"]["case_auto_closed"] is not False:
        raise ValueError("a case must not be auto-closed")
    if "vulnerable" in draft["text"].lower():
        raise ValueError("draft text must not label anyone vulnerable")
    recipient = result["recipient"]
    if recipient["may_be_chosen_by_agent"] is not False:
        raise ValueError("the agent must not choose the recipient")
    if recipient["approved"]:
        if recipient["approval_source"] != "author_argument":
            raise ValueError("only an author argument can approve a recipient")
        if not recipient["approved_recipient"] or not recipient["approved_by"]:
            raise ValueError("recipient approval is incomplete")
    else:
        if recipient["approved_recipient"] is not None:
            raise ValueError("an unapproved draft must not carry a final recipient")
    cited_ids = [line["id"] for line in result["lines_cited"]]
    if len(cited_ids) != len(set(cited_ids)):
        raise ValueError("duplicate citation")
    for line in result["lines_cited"]:
        if line["reason"] != "current":
            raise ValueError(f"cited a line that is not current: {line['id']}")
        if line["text"] not in draft["text"]:
            raise ValueError(f"cited line text missing from the draft: {line['id']}")
        marker = f"[Cited line: {line['id']}."
        if marker not in draft["text"]:
            raise ValueError(f"citation marker missing: {line['id']}")
    for line in result["lines_refused"]:
        if line["text"] in draft["text"]:
            raise ValueError(f"refused line text leaked into the draft: {line['id']}")
    for line in result["lines_withheld_because_specialist_route"]:
        if line.get("text") and line["text"] in draft["text"]:
            raise ValueError("a withheld line was pasted into an information-rights draft")
    if result["classification"]["specialist_route"] and result["lines_cited"]:
        raise ValueError("an information-rights letter must not be answered with a policy line")
    for gap in result["gaps"]:
        if "No position is stated." not in draft["text"]:
            raise ValueError("a gap must say that no position is stated")
    atrs = result["atrs_draft"]
    if atrs["not_submitted"] is not True or atrs["mandatory_scope_decided"] is not False:
        raise ValueError("ATRS draft must stay unsubmitted and undecided")
    for decision in DECISIONS_NOT_TAKEN:
        if decision not in result["decisions_not_taken"]:
            raise ValueError(f"missing decisions_not_taken entry: {decision}")
    if "DRAFT — NOT SENT" not in draft["text"]:
        raise ValueError("draft banner missing")
    invented = "parks will close permanently"
    if invented in draft["text"].lower():
        raise ValueError("invented closure position leaked into the draft")


def _parse_date(value: str) -> date:
    return date.fromisoformat(value)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Draft one synthetic casework reply. Nothing is sent.")
    parser.add_argument("--input", required=True, help="Path to the letter text")
    parser.add_argument("--received", required=True, help="Date received, YYYY-MM-DD")
    parser.add_argument("--as-of", required=True, help="Line-library as-of date, YYYY-MM-DD")
    parser.add_argument("--regime", default="central_government", choices=["central_government", "council"])
    parser.add_argument("--target-working-days", type=int, default=20)
    parser.add_argument("--confirm-target", action="store_true")
    parser.add_argument("--confirm-channel", action="store_true")
    parser.add_argument("--approve-recipient", default=None)
    parser.add_argument("--recipient-approved-by", default=None)
    parser.add_argument("--library", default=None)
    args = parser.parse_args(argv)

    text = Path(args.input).read_text(encoding="utf-8")
    result = draft_correspondence(
        text,
        _parse_date(args.received),
        _parse_date(args.as_of),
        regime=args.regime,
        target_working_days=args.target_working_days,
        confirm_target=args.confirm_target,
        confirm_channel=args.confirm_channel,
        approved_recipient=args.approve_recipient,
        recipient_approved_by=args.recipient_approved_by,
        library_path=Path(args.library) if args.library else None,
    )
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
