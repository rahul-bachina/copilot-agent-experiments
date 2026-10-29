#!/usr/bin/env python3
"""Draft an internal note for one synthetic on-chain alert.

The function does not file a suspicious activity report, contact the NCA,
request a defence, freeze a wallet, move a cryptoasset, or write to a
customer. mlro_decision is null.

No network. No model. No chain query.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from copy import deepcopy
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from addresses import accept_token
    from customer_guard import assert_no_customer_text, empty_customer_facing
    from injection import PROHIBITED_PAYLOAD_KEYS, signals_in_text
    from reuse import experiment_04_pin, kyc_summary, redact_note, travel_rule_summary
    from sources import (
        DEFAULT_STALE_AFTER_DAYS,
        LAST_VERIFIED,
        NOT_OPENED,
        QUOTES,
        SOURCES_PINNED_ON,
        UKFIU_REASON_CHAR_LIMIT,
        source_rows,
    )
else:
    from .addresses import accept_token
    from .customer_guard import assert_no_customer_text, empty_customer_facing
    from .injection import PROHIBITED_PAYLOAD_KEYS, signals_in_text
    from .reuse import experiment_04_pin, kyc_summary, redact_note, travel_rule_summary
    from .sources import (
        DEFAULT_STALE_AFTER_DAYS,
        LAST_VERIFIED,
        NOT_OPENED,
        QUOTES,
        SOURCES_PINNED_ON,
        UKFIU_REASON_CHAR_LIMIT,
        source_rows,
    )

LABEL = "DRAFT FOR THE NOMINATED OFFICER"
REFUSED = "REFUSED"
TEXT_LIMIT = 4000
LABEL_WORDS = ("mixer", "tumbler", "sanctioned-cluster", "darknet", "unhosted", "ransomware")

DECISIONS_NOT_TAKEN = [
    "file_sar",
    "contact_nca",
    "request_daml",
    "record_suspicion",
    "record_mlro_decision",
    "draft_customer_content",
    "freeze_account",
    "move_crypto",
    "assign_glossary_code",
    "query_chain",
]


class InvestigationForbidden(RuntimeError):
    """There is no file, send, freeze, or decision path."""


class NotSynthetic(ValueError):
    """The case was not marked synthetic. The message does not include the body."""


def _canonical(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def _parse_moment(value):
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip().replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def _collect_signals(value, path: str, signals: list[str]) -> None:
    if isinstance(value, str):
        signals.extend(signals_in_text(value[:TEXT_LIMIT]))
        return
    if isinstance(value, dict):
        for key, item in value.items():
            _collect_signals(item, f"{path}.{key}", signals)
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _collect_signals(item, f"{path}[{index}]", signals)


def _scrub(value, path: str, signals: list[str], quarantined: list[dict], unread: list[str]):
    if isinstance(value, dict):
        for key in list(value):
            child = f"{path}.{key}" if path else str(key)
            value[key] = _scrub(value[key], child, signals, quarantined, unread)
        return value
    if isinstance(value, list):
        for index, item in enumerate(value):
            value[index] = _scrub(item, f"{path}[{index}]", signals, quarantined, unread)
        return value
    if isinstance(value, str):
        if len(value) > TEXT_LIMIT:
            signals.extend(signals_in_text(value[:TEXT_LIMIT]))
            unread.append(path)
            return None
        found = signals_in_text(value)
        if found:
            signals.extend(found)
            quarantined.append({"field": path, "signals": found})
            return None
        return value
    return value


def _amount(value) -> str | None:
    if value is None or isinstance(value, bool):
        return None
    if not isinstance(value, (int, float, str)):
        return None
    try:
        amount = Decimal(str(value))
    except InvalidOperation:
        return None
    if amount < 0:
        return None
    return format(amount, "f")


def _labels(text: str | None) -> list[str]:
    if not text:
        return []
    lower = text.casefold()
    return [word for word in LABEL_WORDS if word in lower]


def _token(value, kind: str, path: str, omitted: list[dict]) -> str | None:
    accepted = accept_token(value, kind)
    if accepted is None and isinstance(value, str) and value.strip():
        omitted.append({"field": path, "reason": "not_a_synthetic_token"})
    return accepted


def _event(at, placed: bool, future: bool, kind: str, summary: str, source: str) -> dict:
    return {
        "at": at,
        "placed": placed,
        "future": future,
        "kind": kind,
        "summary": summary,
        "source": source,
        "is_a_suspicion": False,
    }


def _place(moment: datetime | None, as_of: date) -> tuple[str | None, bool, bool]:
    if moment is None:
        return None, False, False
    future = moment.date() > as_of
    return moment.isoformat(), not future, future


def _hops(alert: dict, as_of: date, omitted: list[dict]) -> list[dict]:
    rows = alert.get("hops") if isinstance(alert, dict) else None
    if not isinstance(rows, list):
        return []
    events = []
    for index, hop in enumerate(rows):
        if not isinstance(hop, dict):
            continue
        source = f"alert.hops[{index}]"
        origin = _token(hop.get("from_address"), "address", f"{source}.from_address", omitted)
        destination = _token(hop.get("to_address"), "address", f"{source}.to_address", omitted)
        tx_hash = _token(hop.get("tx_hash"), "tx", f"{source}.tx_hash", omitted)
        moment, placed, future = _place(_parse_moment(hop.get("at")), as_of)
        direction = hop.get("direction") if hop.get("direction") in {"in", "out"} else "unspecified"
        asset = hop.get("asset") if isinstance(hop.get("asset"), str) else "unspecified"
        amount = _amount(hop.get("amount")) or "unspecified"
        label_words = _labels(hop.get("counterparty_label") if isinstance(hop.get("counterparty_label"), str) else None)
        label_text = ", ".join(label_words) if label_words else "none"
        summary = (
            f"{direction} {amount} {asset} from {origin or 'omitted'} "
            f"to {destination or 'omitted'} tx {tx_hash or 'omitted'}. "
            f"Supplied label words: {label_text}."
        )
        events.append(_event(moment, placed, future, "on_chain_hop", summary, source))
    return events


def _ledger(rows, as_of: date, omitted: list[dict]) -> list[dict]:
    if not isinstance(rows, list):
        return []
    events = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            continue
        source = f"transactions[{index}]"
        tx_hash = _token(row.get("tx_hash"), "tx", f"{source}.tx_hash", omitted)
        address = _token(row.get("address"), "address", f"{source}.address", omitted)
        moment, placed, future = _place(_parse_moment(row.get("at")), as_of)
        direction = row.get("direction") if row.get("direction") in {"in", "out"} else "unspecified"
        asset = row.get("asset") if isinstance(row.get("asset"), str) else "unspecified"
        amount = _amount(row.get("amount")) or "unspecified"
        summary = f"Ledger {direction} {amount} {asset} address {address or 'omitted'} tx {tx_hash or 'omitted'}."
        events.append(_event(moment, placed, future, "ledger_row", summary, source))
    return events


def _sort_timeline(events: list[dict]) -> list[dict]:
    placed = [event for event in events if event["at"] and event["placed"]]
    future = [event for event in events if event["future"]]
    undated = [event for event in events if not event["at"]]
    placed.sort(key=lambda event: event["at"])
    future.sort(key=lambda event: event["at"])
    return placed + undated + future


def _sum_asset(events: list[dict]) -> str | None:
    """Sum placed hop amounts when every placed hop names the same asset. Not a valuation."""

    totals: dict[str, Decimal] = {}
    for event in events:
        if event["kind"] != "on_chain_hop" or not event["placed"]:
            continue
        parts = event["summary"].split()
        if len(parts) < 3 or parts[1] == "unspecified" or parts[2] == "unspecified":
            return None
        try:
            amount = Decimal(parts[1])
        except InvalidOperation:
            return None
        totals[parts[2]] = totals.get(parts[2], Decimal("0")) + amount
    if len(totals) != 1:
        return None
    asset, total = next(iter(totals.items()))
    return f"{format(total, 'f')} {asset}"


def _indicators(alert: dict, customer: dict, events: list[dict], travel: dict | None, kyc: dict | None) -> list[dict]:
    rows = []

    def add(item_id: str, fact: str) -> None:
        rows.append(
            {
                "id": item_id,
                "fact": fact,
                "is_a_suspicion": False,
                "decided_by_agent": False,
            }
        )

    if isinstance(alert, dict) and isinstance(alert.get("rule_id"), str) and alert.get("rule_id"):
        add("alert_rule_on_the_export", f"The export names rule id {alert['rule_id']}.")
    words = []
    for event in events:
        if "Supplied label words: none" in event["summary"]:
            continue
        if "Supplied label words:" in event["summary"]:
            words.append(event["summary"].split("Supplied label words:", 1)[1].strip().rstrip("."))
    if words:
        add("supplied_counterparty_label", "The export already carried these label words: " + "; ".join(words) + ".")
    if isinstance(customer, dict) and isinstance(customer.get("stated_purpose"), str) and customer.get("stated_purpose"):
        add("stated_purpose_on_the_file", "A stated purpose is on the customer block. This draft does not decide that activity is inconsistent with it.")
    if isinstance(customer, dict) and customer.get("sanctions_marker") is True:
        add("sanctions_marker_on_the_file", "The file has sanctions_marker true. This draft does not screen a list and does not decide that a person is sanctioned.")
    if isinstance(customer, dict) and customer.get("pep_marker") is True:
        add("pep_marker_on_the_file", "The file has pep_marker true. This draft does not decide that a person is a politically exposed person.")
    if isinstance(customer, dict) and customer.get("terrorist_financing_marker") is True:
        add(
            "terrorist_financing_marker_on_the_file",
            "The file has terrorist_financing_marker true. Terrorism Act Part 3 was not opened. This draft does not write that disclosure.",
        )
    if travel and travel.get("called") and travel.get("exception_categories"):
        add(
            "travel_rule_categories",
            "Experiment 10 returned categories: " + ", ".join(travel["exception_categories"]) + ". The analyst's decision was not taken.",
        )
    if kyc and kyc.get("called"):
        missing = kyc.get("missing") or []
        add(
            "kyc_checklist",
            "Experiment 16 was called. Missing item ids: " + (", ".join(missing) if missing else "none") + ". Documents were not confirmed.",
        )
    return rows


def _paragraphs(case_id: str, alert: dict, customer: dict, events: list[dict], indicators: list[dict], travel, kyc, pii, value_gbp, asset_total, uk_nexus) -> list[str]:
    who = "unspecified"
    if isinstance(customer, dict) and isinstance(customer.get("customer_ref"), str) and customer.get("customer_ref"):
        who = customer["customer_ref"]
    firm = case_id
    paragraphs = [
        f"Internal draft for the nominated officer. Subject reference on the file: {who}. Firm label on the case: {firm}.",
        "Who is involved is taken from the customer reference supplied with the case. How they are involved is the relationship described below, and only where the case itself states it.",
    ]
    if isinstance(customer, dict) and customer.get("relationship"):
        paragraphs.append(f"The case says the relationship is {customer['relationship']}.")
    else:
        paragraphs.append("The case does not describe the relationship.")
    if uk_nexus is True:
        paragraphs.append("The case says the firm is established in the United Kingdom. That is the UK link recorded here.")
    elif uk_nexus is False:
        paragraphs.append("The case says the firm is not established in the United Kingdom. This draft does not invent another UK link.")
    else:
        paragraphs.append("The case does not say whether the firm is established in the United Kingdom. This draft does not infer a UK nexus.")
    placed = [event["summary"] for event in events if event["placed"]]
    if placed:
        paragraphs.append("Placed events, in time order: " + " ".join(placed))
    else:
        paragraphs.append("No placed on-chain event was on the case.")
    future = [event["summary"] for event in events if event["future"]]
    if future:
        paragraphs.append("Events dated after the as-of date were not treated as having happened: " + " ".join(future))
    if asset_total:
        paragraphs.append(
            f"Arithmetic on the placed hop amounts gives {asset_total}. This is not a valuation and not a sterling figure."
        )
    if value_gbp:
        paragraphs.append(f"The case supplies a sterling figure of {value_gbp} GBP. This draft did not convert a price.")
    else:
        paragraphs.append("No sterling figure was supplied. This draft does not convert a cryptoasset price into GBP.")
    if indicators:
        paragraphs.append("Facts a person may look at, none of which is a suspicion recorded by this agent: " + " ".join(item["fact"] for item in indicators))
    else:
        paragraphs.append("No extra indicator was computed. The absence of an indicator is not a decision to close the alert.")
    if travel is None:
        paragraphs.append("No Travel Rule transfer was attached. Experiment 10 was not called.")
    elif travel.get("not_read"):
        paragraphs.append("A Travel Rule transfer was attached and was not read (" + travel.get("reason", "unread") + ").")
    if kyc is None:
        paragraphs.append("No KYC file was attached. Experiment 16 was not called.")
    elif kyc.get("not_read"):
        paragraphs.append("A KYC file was attached and was not read (" + kyc.get("reason", "unread") + ").")
    if pii.get("called") and pii.get("finding_count"):
        paragraphs.append(
            "Experiment 08 detected UK identifiers in the analyst note. "
            "The excerpt is a redaction proposal and is not anonymised. The raw values are not repeated here."
        )
    paragraphs.append(
        "Section 330(2), as opened, uses these words for the first condition: "
        + QUOTES["poca_330_2"]
        + ". This draft does not decide that the condition is met."
    )
    paragraphs.append(
        "Regulation 21(5) requires the nominated officer to determine whether a disclosure made to them "
        "gives rise to knowledge or suspicion or reasonable grounds for knowledge or suspicion. "
        "This text is not that determination, and it is not itself a disclosure under section 330 or section 331."
    )
    paragraphs.append(
        "It has not been submitted to the National Crime Agency. No glossary code has been selected. "
        "No defence has been requested. UKFIU chapter 3 was not opened. "
        "Nothing in this draft is for the customer."
    )
    return paragraphs


def _force(draft: dict) -> None:
    draft["label"] = draft["label"] if draft.get("refused") else LABEL
    draft["mlro_decision"] = None
    draft["sar_filed"] = False
    draft["nca_contacted"] = False
    draft["daml_requested"] = False
    draft["customer_told"] = False
    draft["suspicion_recorded_by_agent"] = False
    draft["glossary_codes_assigned"] = False
    draft["actions_taken"] = []
    draft["model_called"] = False
    draft["network_called"] = False
    draft["chain_queried"] = False
    draft["prompt_injection"]["followed"] = False
    draft["customer_facing"]["drafted"] = False
    draft["customer_facing"]["text"] = None
    draft["customer_facing"]["request_echoed"] = False
    draft["customer_facing"]["may_be_sent_by_agent"] = False
    draft["flags"] = {
        "sar_filed": False,
        "nca_contacted": False,
        "daml_requested": False,
        "customer_contacted": False,
        "account_frozen": False,
        "crypto_moved": False,
        "suspicion_recorded_by_agent": False,
        "mlro_decision_recorded": False,
        "glossary_codes_assigned": False,
    }
    pii = draft.get("identifier_gateway") or {}
    pii["output_is_anonymised"] = False
    pii["agent_may_release"] = False
    draft["identifier_gateway"] = pii
    if draft.get("travel_rule"):
        draft["travel_rule"]["analyst_decision"] = None
        draft["travel_rule"]["injection_followed"] = False
    if draft.get("kyc"):
        draft["kyc"]["documents_confirmed"] = False
        draft["kyc"]["purpose_confirmed"] = False
        draft["kyc"]["final_risk_rating"] = None
        draft["kyc"]["sar_filed"] = False
        draft["kyc"]["customer_facing_copied"] = False
        draft["kyc"]["injection_followed"] = False
    for source in draft.get("sources") or []:
        source["applied_as_a_decision"] = False
    assert_no_customer_text(draft)


def investigate(
    case: dict,
    *,
    as_of: date,
    stale_after_days: int = DEFAULT_STALE_AFTER_DAYS,
) -> dict:
    """Return an internal draft. The officer's decision stays null."""

    if not isinstance(case, dict):
        raise TypeError("case must be an object")
    if not isinstance(as_of, date) or isinstance(as_of, datetime):
        raise TypeError("as_of must be a date")
    if type(stale_after_days) is not int or stale_after_days < 0:
        raise ValueError("stale_after_days must be a non-negative integer")
    if case.get("synthetic") is not True:
        raise NotSynthetic("record is not marked synthetic")

    original_hash = hashlib.sha256(_canonical(case).encode("utf-8")).hexdigest()
    working = deepcopy(case)
    signals: list[str] = []
    prohibited = []
    for key in list(working):
        if key in PROHIBITED_PAYLOAD_KEYS:
            prohibited.append(key)
            _collect_signals(working[key], key, signals)
            del working[key]

    message_requested = "requested_customer_message" in working
    if message_requested:
        _collect_signals(working["requested_customer_message"], "requested_customer_message", signals)
        del working["requested_customer_message"]

    quarantined: list[dict] = []
    unread: list[str] = []
    _scrub(working, "", signals, quarantined, unread)

    alert = working.get("alert") if isinstance(working.get("alert"), dict) else {}
    customer = working.get("customer") if isinstance(working.get("customer"), dict) else {}
    omitted: list[dict] = []
    events = _hops(alert, as_of, omitted)
    events.extend(_ledger(working.get("transactions"), as_of, omitted))
    raised = _parse_moment(alert.get("raised_at") if isinstance(alert, dict) else None)
    if raised is not None:
        moment, placed, future = _place(raised, as_of)
        events.append(
            _event(moment, placed, future, "alert_raised", "The export records the alert as raised at this time.", "alert.raised_at")
        )
    timeline = _sort_timeline(events)
    alert_stale = False
    if raised is not None and not (raised.date() > as_of):
        alert_stale = (as_of - raised.date()).days > stale_after_days

    sources = source_rows(as_of, stale_after_days)
    sources_stale = any(row["stale"] for row in sources)

    travel = None
    if isinstance(case.get("travel_rule_transfer"), dict):
        travel = travel_rule_summary(
            deepcopy(case["travel_rule_transfer"]),
            as_of=as_of,
            stale_after_days=stale_after_days,
        )
    kyc = None
    if isinstance(case.get("kyc_file"), dict):
        kyc = kyc_summary(
            deepcopy(case["kyc_file"]),
            as_of=as_of,
            stale_after_days=stale_after_days,
        )

    note = working.get("analyst_note") if isinstance(working.get("analyst_note"), str) else ""
    pii = redact_note(note, as_of=as_of)
    try:
        exp04 = experiment_04_pin()
    except FileNotFoundError:
        exp04 = {
            "experiment": "04-fca-cryptoasset-readiness",
            "called": False,
            "gap_register_run": False,
            "reason": "Experiment 04 is not beside this experiment.",
        }

    firm = working.get("firm_name") if isinstance(working.get("firm_name"), str) and working.get("firm_name") else "unspecified"
    value_gbp = _amount(working.get("value_gbp"))
    uk_nexus = working.get("firm_established_in_united_kingdom")
    if not isinstance(uk_nexus, bool):
        uk_nexus = None
    indicators = _indicators(alert, customer, timeline, travel, kyc)
    paragraphs = _paragraphs(firm, alert, customer, timeline, indicators, travel, kyc, pii, value_gbp, _sum_asset(timeline), uk_nexus)
    reason = "\n\n".join(paragraphs)
    over_limit = len(reason) > UKFIU_REASON_CHAR_LIMIT
    if over_limit:
        reason = reason[: UKFIU_REASON_CHAR_LIMIT - 80] + "\n\n[Truncated. The nominated officer must shorten this before any portal field is used.]"

    draft = {
        "label": LABEL,
        "catalogue_id": "UK07",
        "experiment": "22-onchain-alert-sar-drafter",
        "experiment_id": "exp-22-onchain-alert-sar-drafter",
        "autonomy": "A1",
        "synthetic": True,
        "refused": False,
        "firm_name": firm,
        "alert_id": alert.get("alert_id") if isinstance(alert.get("alert_id"), str) else None,
        "as_of": as_of.isoformat(),
        "sources_pinned_on": LAST_VERIFIED,
        "sources_stale": sources_stale,
        "rules_current": not sources_stale,
        "alert_context_stale": alert_stale,
        "input_sha256": original_hash,
        "model_called": False,
        "network_called": False,
        "chain_queried": False,
        "mlro_decision": None,
        "sar_filed": False,
        "nca_contacted": False,
        "daml_requested": False,
        "customer_told": False,
        "suspicion_recorded_by_agent": False,
        "glossary_codes_assigned": False,
        "actions_taken": [],
        "decisions_not_taken": list(DECISIONS_NOT_TAKEN),
        "evidence_timeline": timeline,
        "omitted_identifiers": omitted,
        "text_not_fully_read": unread,
        "indicators_for_a_person": indicators,
        "investigation_note": {
            "audience": "internal_nominated_officer",
            "not_for_the_customer": True,
            "paragraphs": paragraphs,
        },
        "sar_narrative": {
            "audience": "nominated_officer",
            "not_a_disclosure": True,
            "not_submitted": True,
            "glossary_codes_assigned": False,
            "daml_requested": False,
            "statutory_test_applied": False,
            "ukfiu_chapter": "2",
            "ukfiu_version": "1.1 December 2025",
            "reason_for_suspicion_draft": reason,
            "character_count": len(reason),
            "ukfiu_reason_field_limit": UKFIU_REASON_CHAR_LIMIT,
            "over_ukfiu_reason_field_limit": over_limit,
            "marc_sentence_applied": False,
            "marc_note": (
                "The 30 June 2026 regime overview narrows an on-chain monitoring "
                "requirement for large UK QCATPs under MARC. That sentence is not "
                "applied to this AML alert."
            ),
        },
        "customer_facing": empty_customer_facing(message_requested=message_requested),
        "travel_rule": travel,
        "kyc": kyc,
        "identifier_gateway": pii,
        "experiment_04": exp04,
        "fca_monitoring_expectation": {
            "source_id": "fca-mlr-application",
            "quote": QUOTES["fca_onchain_tool"],
            "rules_and_thresholds_quote": QUOTES["fca_rules_thresholds"],
            "endorsement": QUOTES["fca_no_endorsement"],
            "tool_configured_by_this_agent": False,
        },
        "sources": sources,
        "not_opened": list(NOT_OPENED),
        "prompt_injection": {
            "detected": bool(signals or prohibited),
            "followed": False,
            "signals": sorted(set(signals)),
            "quarantined_fields": quarantined,
            "prohibited_payload_keys_ignored": prohibited,
        },
        "human_approval": {
            "approver": "Nominated officer",
            "decides_whether_section_330_or_331_is_met": True,
            "agent_recorded_decision": None,
        },
    }
    _force(draft)
    return draft


def file_with_nca(_draft: dict) -> None:
    """Refuse to file with the NCA."""

    raise InvestigationForbidden("the agent does not file a suspicious activity report with the NCA")


def request_daml(_draft: dict) -> None:
    """Refuse to request a defence."""

    raise InvestigationForbidden("the agent does not request a defence against money laundering")


def contact_customer(_draft: dict, _text: str | None = None) -> None:
    """Refuse to draft or send customer-facing content."""

    raise InvestigationForbidden("the agent does not draft or send customer-facing content")


def freeze_account(_draft: dict) -> None:
    """Refuse to freeze an account or a wallet."""

    raise InvestigationForbidden("the agent does not freeze an account or a wallet")


def move_crypto(_draft: dict) -> None:
    """Refuse to move a cryptoasset."""

    raise InvestigationForbidden("the agent does not move a cryptoasset")


def record_mlro_decision(_draft: dict, _decision: str | None = None) -> None:
    """Refuse to record the officer's decision."""

    raise InvestigationForbidden("the agent does not record the nominated officer's decision")


def record_suspicion(_draft: dict) -> None:
    """Refuse to record that anyone knows or suspects."""

    raise InvestigationForbidden("the agent does not record that anyone knows or suspects money laundering")


def assign_glossary_code(_draft: dict, _code: str | None = None) -> None:
    """Refuse to assign a glossary code."""

    raise InvestigationForbidden("the agent does not assign a SAR glossary code")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Draft an internal SAR narrative. Does not file.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--stale-after-days", type=int, default=DEFAULT_STALE_AFTER_DAYS)
    args = parser.parse_args(argv)
    case = json.loads(args.input.read_text(encoding="utf-8"))
    as_of = date.fromisoformat(args.as_of)
    try:
        draft = investigate(case, as_of=as_of, stale_after_days=args.stale_after_days)
    except NotSynthetic as exc:
        print(json.dumps({"label": REFUSED, "refused": True, "reason": str(exc), "sar_filed": False}))
        return 2
    json.dump(draft, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
