#!/usr/bin/env python3
"""Triage one cryptoasset transfer against the pinned Travel Rule checklist.

The function does not hold, return, reject, or release a transfer. It does
not file a report and it does not contact anyone. analyst_decision is null.

No network. No model.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from injection import PROHIBITED_PAYLOAD_KEYS, signals_in_text, text_is_injection
    from sources import (
        DEFAULT_STALE_AFTER_DAYS,
        LAST_VERIFIED,
        SOURCES,
        THRESHOLD_GBP,
        UNVERIFIED,
    )
else:
    from .injection import PROHIBITED_PAYLOAD_KEYS, signals_in_text, text_is_injection
    from .sources import (
        DEFAULT_STALE_AFTER_DAYS,
        LAST_VERIFIED,
        SOURCES,
        THRESHOLD_GBP,
        UNVERIFIED,
    )

LABEL = "DRAFT FOR ANALYST REVIEW"
REFUSED = "REFUSED"
ROLES = ("originator", "beneficiary", "intermediary")
PARTY_TYPES = ("individual", "firm")

PARTY_KEYS = (
    "party_type",
    "name",
    "registered_or_trading_name",
    "account_number",
    "unique_transaction_identifier",
    "customer_identification_number",
    "address",
    "registered_office",
    "principal_place_of_business",
    "birth_certificate_number",
    "passport_number",
    "national_identity_card_number",
    "date_of_birth",
    "place_of_birth",
)

DECISIONS_NOT_TAKEN = [
    "hold",
    "return",
    "reject",
    "release",
    "file_sar",
    "contact_counterparty",
    "report_to_fca",
    "make_cryptoasset_available",
]


class TriageError(ValueError):
    """The record cannot be read. Nothing was decided."""


def _parse_date(value: str, field: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError) as exc:
        raise TriageError(f"{field} must be YYYY-MM-DD") from exc


def _stale(verified: date, as_of: date, days: int) -> bool:
    return (as_of - verified).days > days


def _norm(value: str | None) -> str:
    if not value:
        return ""
    return " ".join(value.casefold().split())


def _clean_text(value, path: str, quarantined: list[dict], signals: list[str]) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise TriageError(f"{path} must be a string or null")
    text = value.strip()
    if not text:
        return None
    found = signals_in_text(text)
    if found:
        quarantined.append({"field": path, "signals": found})
        signals.extend(found)
        return None
    return text


def _party(raw, path: str, quarantined: list[dict], signals: list[str]) -> dict:
    raw = raw or {}
    if not isinstance(raw, dict):
        raise TriageError(f"{path} must be an object")
    party = {key: None for key in PARTY_KEYS}
    party_type = raw.get("party_type")
    if party_type is not None and party_type not in PARTY_TYPES:
        raise TriageError(f"{path}.party_type must be individual, firm, or null")
    party["party_type"] = party_type
    for key in PARTY_KEYS:
        if key == "party_type":
            continue
        party[key] = _clean_text(raw.get(key), f"{path}.{key}", quarantined, signals)
    return party


def _gbp(value) -> Decimal | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        raise TriageError("value_gbp must be a number or null")
    try:
        amount = Decimal(str(value))
    except InvalidOperation as exc:
        raise TriageError("value_gbp must be a number or null") from exc
    if amount < 0:
        raise TriageError("value_gbp must be zero or greater")
    return amount


def _bool(value, field: str) -> bool | None:
    if value is None:
        return None
    if not isinstance(value, bool):
        raise TriageError(f"{field} must be true, false, or null")
    return value


def _account_present(party: dict, transfer_uti: str | None) -> bool:
    return bool(party["account_number"] or party["unique_transaction_identifier"] or transfer_uti)


def _firm_name_present(party: dict) -> bool:
    return bool(party["registered_or_trading_name"] or party["name"])


def _p6_present(party: dict) -> bool:
    if party["party_type"] == "firm":
        return bool(
            party["customer_identification_number"]
            or party["registered_office"]
            or party["principal_place_of_business"]
        )
    if party["party_type"] == "individual":
        identity_document = any(
            party[key]
            for key in (
                "customer_identification_number",
                "address",
                "birth_certificate_number",
                "passport_number",
                "national_identity_card_number",
            )
        )
        birth = bool(party["date_of_birth"] and party["place_of_birth"])
        return identity_document or birth
    return False


def _p5_gaps(originator: dict, beneficiary: dict, transfer_uti: str | None) -> list[dict]:
    gaps = []
    if not originator["name"]:
        gaps.append({"field": "originator.name", "provision": "regulation 64C(5)(a)"})
    if not beneficiary["name"]:
        gaps.append({"field": "beneficiary.name", "provision": "regulation 64C(5)(a)"})
    if originator["party_type"] == "firm" and not _firm_name_present(originator):
        gaps.append({"field": "originator.registered_or_trading_name", "provision": "regulation 64C(5)(b)"})
    elif originator["party_type"] not in PARTY_TYPES:
        gaps.append({"field": "originator.party_type", "provision": "regulation 64C(5)(b)"})
    if beneficiary["party_type"] == "firm" and not _firm_name_present(beneficiary):
        gaps.append({"field": "beneficiary.registered_or_trading_name", "provision": "regulation 64C(5)(b)"})
    elif beneficiary["party_type"] not in PARTY_TYPES:
        gaps.append({"field": "beneficiary.party_type", "provision": "regulation 64C(5)(b)"})
    if not _account_present(originator, transfer_uti):
        gaps.append({"field": "originator.account_number", "provision": "regulation 64C(5)(c)"})
    if not _account_present(beneficiary, transfer_uti):
        gaps.append({"field": "beneficiary.account_number", "provision": "regulation 64C(5)(c)"})
    return gaps


def _empty_flags() -> dict:
    return {
        "transfer_held_by_agent": False,
        "transfer_returned_by_agent": False,
        "transfer_rejected_by_agent": False,
        "transfer_released_by_agent": False,
        "sar_filed": False,
        "counterparty_contacted": False,
        "fca_report_made": False,
        "cryptoasset_made_available_by_agent": False,
        "fca_statement_treated_as_waiver": False,
        "exclusion_confirmed_by_agent": False,
        "jmlsg_euro_threshold_used": False,
    }


def _base_shell(transfer_id: str | None, synthetic: bool) -> dict:
    return {
        "label": LABEL,
        "catalogue_id": "UK05",
        "experiment": "10-travel-rule-exception-triage",
        "related_experiment": "experiments/04-fca-cryptoasset-readiness",
        "transfer_id": transfer_id,
        "synthetic": synthetic,
        "model_called": False,
        "network_called": False,
        "actions_taken": [],
        "analyst_decision": None,
        "decisions_not_taken": list(DECISIONS_NOT_TAKEN),
        "flags": _empty_flags(),
        "human_review": {
            "approver": "Analyst",
            "decision_required": ["hold", "return", "escalate"],
            "agent_recorded_decision": None,
        },
    }


def _refuse(payload: dict) -> dict:
    transfer_id = payload.get("transfer_id") if isinstance(payload, dict) else None
    if not isinstance(transfer_id, str) or text_is_injection(transfer_id) or len(transfer_id) > 80:
        transfer_id = None
    result = _base_shell(transfer_id, False)
    result["label"] = REFUSED
    result["refused"] = True
    result["reason"] = (
        "This starter accepts a record marked synthetic. A live transfer was not triaged."
    )
    result["exception_categories"] = []
    result["options"] = []
    return result


def _option(option_id: str, proposed: bool, reason: str, provisions: list[str]) -> dict:
    return {
        "id": option_id,
        "proposed": proposed,
        "reason": reason,
        "provisions": provisions,
        "agent_will_not_take": True,
    }


def _source_rows(as_of: date, stale_after_days: int) -> list[dict]:
    rows = []
    for source in SOURCES:
        verified = _parse_date(source["last_verified"], source["id"])
        rows.append(
            {
                "id": source["id"],
                "title": source["title"],
                "url": source["url"],
                "last_verified": source["last_verified"],
                "stale": _stale(verified, as_of, stale_after_days),
                "body_opened": source["body_opened"],
            }
        )
    return rows


def triage(payload: dict, *, as_of: date | None = None, stale_after_days: int = DEFAULT_STALE_AFTER_DAYS) -> dict:
    """Return a draft triage. The analyst's decision is always null."""
    if not isinstance(payload, dict):
        raise TriageError("The transfer record must be a JSON object")
    if payload.get("synthetic") is not True:
        return _refuse(payload)

    prohibited = [key for key in PROHIBITED_PAYLOAD_KEYS if key in payload]
    record = {key: value for key, value in payload.items() if key not in PROHIBITED_PAYLOAD_KEYS}

    role = record.get("firm_role")
    if role not in ROLES:
        raise TriageError("firm_role must be originator, beneficiary, or intermediary")
    transfer_id = record.get("transfer_id")
    if not isinstance(transfer_id, str) or not transfer_id.strip():
        raise TriageError("transfer_id is required")

    signals: list[str] = []
    quarantined: list[dict] = []
    transfer_id_clean = _clean_text(transfer_id, "transfer_id", quarantined, signals) or "rejected-identifier"
    notes = record.get("notes") or ""
    if not isinstance(notes, str):
        raise TriageError("notes must be a string")
    note_signals = signals_in_text(notes)
    signals.extend(note_signals)

    if as_of is None:
        as_of = _parse_date(str(record.get("as_of") or LAST_VERIFIED), "as_of")
    amount = _gbp(record.get("value_gbp"))
    linked = _bool(record.get("linked_transfers_assessed"), "linked_transfers_assessed")
    all_uk = _bool(record.get("all_executing_businesses_in_uk"), "all_executing_businesses_in_uk")
    own_behalf = _bool(record.get("both_parties_cryptoasset_businesses_own_behalf"), "both_parties_cryptoasset_businesses_own_behalf")
    article_3_9 = _bool(record.get("funds_transfer_regulation_article_3_9"), "funds_transfer_regulation_article_3_9")
    same_business = _bool(record.get("same_cryptoasset_business_both_sides"), "same_cryptoasset_business_both_sides")
    verified = _bool(record.get("originator_information_verified_by_firm"), "originator_information_verified_by_firm")
    stored = _bool(record.get("information_stored_by_firm"), "information_stored_by_firm")
    p6_requested = _bool(record.get("paragraph_6_requested_by_beneficiary"), "paragraph_6_requested_by_beneficiary")
    supplier = _bool(record.get("third_party_supplier_used"), "third_party_supplier_used")

    attribution = record.get("wallet_attribution") or "unknown"
    if attribution not in {"hosted", "unhosted", "unknown"}:
        raise TriageError("wallet_attribution must be hosted, unhosted, or unknown")

    counterparty = record.get("counterparty") or {}
    if not isinstance(counterparty, dict):
        raise TriageError("counterparty must be an object")
    status = counterparty.get("travel_rule_status") or "unknown"
    if status not in {"in_force", "not_in_force", "unknown"}:
        raise TriageError("counterparty.travel_rule_status must be in_force, not_in_force, or unknown")
    can_receive = _bool(counterparty.get("can_receive_required_information"), "counterparty.can_receive_required_information")
    status_on = counterparty.get("status_recorded_on")
    status_date = _parse_date(status_on, "counterparty.status_recorded_on") if status_on else None

    uti = _clean_text(record.get("unique_transaction_identifier"), "unique_transaction_identifier", quarantined, signals)
    on_transfer = record.get("information_on_transfer") or {}
    firm_holds = record.get("firm_holds") or {}
    originator = _party(on_transfer.get("originator"), "information_on_transfer.originator", quarantined, signals)
    beneficiary = _party(on_transfer.get("beneficiary"), "information_on_transfer.beneficiary", quarantined, signals)
    held_originator = _party((firm_holds or {}).get("originator"), "firm_holds.originator", quarantined, signals)
    held_beneficiary = _party((firm_holds or {}).get("beneficiary"), "firm_holds.beneficiary", quarantined, signals)

    cdd = record.get("beneficiary_part3_cdd") or {}
    if not isinstance(cdd, dict):
        raise TriageError("beneficiary_part3_cdd must be an object")
    cdd_name = _clean_text(cdd.get("name"), "beneficiary_part3_cdd.name", quarantined, signals)
    cdd_account = _clean_text(cdd.get("account_number"), "beneficiary_part3_cdd.account_number", quarantined, signals)

    markers = record.get("firm_markers") or {}
    if not isinstance(markers, dict):
        raise TriageError("firm_markers must be an object")
    suspicion = bool(markers.get("suspicion_already_flagged_by_analyst"))
    repeated = bool(markers.get("repeated_information_failure_flagged_by_firm"))
    sanctions = bool(markers.get("sanctions_screening_hit_recorded_by_firm"))

    batch = record.get("batch") or {}
    if not isinstance(batch, dict):
        raise TriageError("batch must be an object")
    is_batch = bool(batch.get("is_batch_file"))
    batch_outside = batch.get("beneficiary_wholly_outside_uk")
    batch_accompanied = batch.get("batch_accompanied_by_required_information")
    batch_individual = batch.get("individual_has_originator_account_or_uti")

    unhosted = record.get("unhosted") or {}
    if not isinstance(unhosted, dict):
        raise TriageError("unhosted must be an object")
    unhosted_requested = bool(unhosted.get("information_requested_from_customer"))
    unhosted_received = unhosted.get("requested_information_received")
    customer_role = unhosted.get("customer_role")

    source_rows = _source_rows(as_of, stale_after_days)
    rules_stale = any(row["stale"] for row in source_rows)
    status_future = bool(status_date and status_date > as_of)
    status_stale = bool(status_date and _stale(status_date, as_of, stale_after_days))
    status_relied_on = bool(status_date) and not status_stale and not status_future and status in {"in_force", "not_in_force"}
    sunrise = status_relied_on and status == "not_in_force"

    threshold_operative = amount is not None and linked is True
    at_or_over = bool(threshold_operative and amount >= Decimal(THRESHOLD_GBP))
    if all_uk is True:
        p6_must = False
    elif all_uk is False and threshold_operative:
        p6_must = at_or_over
    else:
        p6_must = "cannot_tell"

    exclusion_asserted = bool(own_behalf) or bool(article_3_9)
    hosted = attribution == "hosted"
    unhosted_wallet = attribution == "unhosted"

    gaps: list[dict] = []
    mismatches: list[dict] = []
    categories: list[str] = []
    firm_steps: list[dict] = []
    explanations: list[str] = []

    if exclusion_asserted:
        categories.append("possible_exclusion_64A")
        which = "regulation 64A(3)" if own_behalf else "regulation 64A(2)"
        explanations.append(
            f"The record asserts {which}. The core does not confirm it and does not release the transfer."
        )
        firm_steps.append(
            {
                "id": "analyst_confirms_scope_exclusion",
                "agent_will_not_take": True,
                "detail": "An analyst confirms the exclusion before anyone treats Part 7A as not applicable.",
            }
        )

    if attribution == "unknown" and not exclusion_asserted:
        categories.append("wallet_attribution_unresolved")
        explanations.append(
            "Wallet attribution is unknown, so regulation 64C and regulation 64G were not applied as if the wallet were known. "
            "JMLSG Annex I paragraph 39, opened 26 October 2026, says a firm should take reasonable steps to tell hosted from unhosted."
        )

    batch_blocks = False
    batch_assertion_holds = (
        is_batch
        and batch_outside is True
        and batch_accompanied is True
        and batch_individual is True
    )
    if is_batch and not exclusion_asserted and hosted:
        if batch_assertion_holds:
            categories.append("batch_file_assertion_not_read")
            batch_blocks = True
            explanations.append(
                "Regulation 64C(7) can carry individual-transfer information on the batch when the beneficiary's "
                "business is wholly outside the United Kingdom. The core did not read the batch file, so it does not treat the conditions as satisfied."
            )
        else:
            categories.append("batch_file_conditions_not_shown")
            batch_blocks = True
            gaps.extend(_p5_gaps(originator, beneficiary, uti))
            if p6_must is True and not _p6_present(originator):
                gaps.append({"field": "originator.paragraph_6", "provision": "regulation 64C(6) and 64C(4)"})
            explanations.append(
                "The record says this is a batch file, and the regulation 64C(7) conditions are not all marked true. Individual fields are checked."
            )

    check_fields = hosted and not exclusion_asserted and not (is_batch and batch_assertion_holds)
    if check_fields and not is_batch:
        gaps.extend(_p5_gaps(originator, beneficiary, uti))
        if p6_must is True and not _p6_present(originator):
            gaps.append({"field": "originator.paragraph_6", "provision": "regulation 64C(6) and 64C(4)"})
        if p6_must == "cannot_tell" and not _p6_present(originator):
            categories.append("threshold_not_operative")
            explanations.append(
                f"The £{THRESHOLD_GBP} limb was not applied. Regulation 64C(4) needs every executing business to be identified "
                "and the sterling equivalent, taken together with any linked transfer the firm has assessed. The core does not convert and does not decide linkage."
            )
            firm_steps.append(
                {
                    "id": "analyst_confirms_sterling_equivalent",
                    "agent_will_not_take": True,
                    "detail": "The analyst confirms the firm's sterling equivalent and whether linked transfers were included.",
                }
            )

    if hosted and not exclusion_asserted and all_uk is True and p6_requested is True and not _p6_present(originator):
        categories.append("paragraph_6_request_outstanding")
        explanations.append(
            "Regulation 64C(2) requires the originator's business to provide regulation 64C(6) information within three working days of a request, "
            "where every executing business is in the United Kingdom. No due date is calculated."
        )

    if role == "originator" and hosted and not exclusion_asserted and verified is not True:
        categories.append("originator_verification_not_recorded")
        explanations.append(
            "Regulation 64C(8) requires originator information to have been verified from a reliable source independent of the person. "
            "The record does not say the firm has done that. The core does not verify identity."
        )

    if role == "beneficiary" and hosted and not exclusion_asserted:
        if not cdd_name:
            categories.append("correspondence_check_not_possible")
            explanations.append(
                "Regulation 64D(1)(b) requires a check that beneficiary information corresponds with Part 3. No Part 3 name was supplied, so the check was not made."
            )
        elif beneficiary["name"] and _norm(beneficiary["name"]) != _norm(cdd_name):
            mismatches.append(
                {
                    "field": "beneficiary.name",
                    "provision": "regulation 64D(1)(b)",
                    "on_transfer": beneficiary["name"],
                    "part3": cdd_name,
                }
            )
            explanations.append(
                "The beneficiary name on the transfer does not match the Part 3 name, ignoring case and spacing. "
                "JMLSG Annex I paragraph 24 says a truncated name can have an explanation. The core does not clear the mismatch."
            )
        if cdd_account and beneficiary["account_number"] and cdd_account != beneficiary["account_number"]:
            mismatches.append(
                {
                    "field": "beneficiary.account_number",
                    "provision": "regulation 64D(1)(b)",
                    "on_transfer": beneficiary["account_number"],
                    "part3": cdd_account,
                }
            )

    if mismatches:
        categories.append("non_corresponding_information")

    sunrise_collect_gap = False
    if sunrise and role == "originator" and hosted and not exclusion_asserted:
        categories.append("sunrise_jurisdiction")
        if can_receive is False:
            hold_gaps = _p5_gaps(held_originator, held_beneficiary, uti)
            if p6_must is True and not _p6_present(held_originator):
                hold_gaps.append({"field": "firm_holds.originator.paragraph_6", "provision": "regulation 64C(6)"})
            if hold_gaps:
                sunrise_collect_gap = True
                gaps.extend({"field": f"firm_holds.{item['field']}", "provision": item["provision"]} for item in hold_gaps)
            if stored is not True:
                sunrise_collect_gap = True
                firm_steps.append(
                    {
                        "id": "store_information_before_sending",
                        "agent_will_not_take": True,
                        "detail": (
                            "The FCA statement says that if the counterparty cannot receive the information, "
                            "the UK business must still collect and verify it and should store it before making the transfer."
                        ),
                    }
                )
            explanations.append(
                "The firm's register says this jurisdiction does not have the Travel Rule. "
                "The FCA statement, last updated 6 February 2026, was opened on 26 October 2026. It is not treated as a waiver of regulation 64C(9)."
            )
        elif can_receive is None:
            sunrise_collect_gap = True
            firm_steps.append(
                {
                    "id": "establish_whether_counterparty_can_receive",
                    "agent_will_not_take": True,
                    "detail": "The FCA statement says the firm takes all reasonable steps to establish whether the counterparty can receive the information. The core does not contact them.",
                }
            )
            explanations.append(
                "Sunrise send, and the record does not say whether the counterparty can receive the information. The core does not contact the counterparty."
            )
        else:
            explanations.append(
                "Sunrise send, and the record says the counterparty can receive the information. Regulation 64C still applies to what accompanies the transfer."
            )
    elif sunrise and not exclusion_asserted:
        categories.append("sunrise_jurisdiction")
        explanations.append(
            "The firm's register says this jurisdiction does not have the Travel Rule. JMLSG Annex I paragraph 10 calls this the sunrise issue and points to FCA communications. "
            "On a receipt with missing or incomplete information, the FCA statement says the firm takes the status into account in a risk-based assessment of whether to make the cryptoassets available. "
            "The statement is not treated as a waiver of regulation 64D."
        )

    if not status_relied_on and not exclusion_asserted:
        categories.append("counterparty_travel_rule_status_not_relied_on")
        explanations.append(
            "The counterparty Travel Rule status was not relied on. It is missing, unknown, in the future, or older than the stale threshold. "
            "The analyst refreshes the firm's register before anyone uses a sunrise factor."
        )
        firm_steps.append(
            {
                "id": "analyst_refreshes_jurisdiction_register",
                "agent_will_not_take": True,
                "detail": "The status on this record is not treated as current.",
            }
        )

    if unhosted_wallet and not exclusion_asserted:
        categories.append("unhosted_wallet")
        unanswered = unhosted_requested and unhosted_received is not True
        if unanswered:
            explanations.append(
                "Regulation 64G(4) says that if information requested under regulation 64G(1) is not received, "
                "the business must not make the cryptoasset available to the beneficiary. The core does not make it available. "
                "Regulation 64G as opened has no return limb."
            )
        else:
            limb = ""
            if customer_role == "beneficiary" and at_or_over:
                limb = f" Regulation 64G(1)(b) says the business may request regulation 64C(6) information about the originator at or above £{THRESHOLD_GBP}."
            explanations.append(
                "Regulation 64G(1) says the business may request information. The core does not decide the may. "
                "Regulation 64G(4) applies after a request goes unanswered."
                + limb
            )
            firm_steps.append(
                {
                    "id": "analyst_decides_whether_to_request_unhosted_information",
                    "agent_will_not_take": True,
                    "detail": "Whether to request is the firm's risk decision under regulation 64G(2). The core does not take it.",
                }
            )

    if gaps and hosted and not exclusion_asserted:
        categories.append("missing_information")
        if role in {"beneficiary", "intermediary"}:
            provision = "regulation 64D(2)(a)" if role == "beneficiary" else "regulation 64E(2)(a)"
            firm_steps.append(
                {
                    "id": "request_missing_information_from_counterparty",
                    "agent_will_not_take": True,
                    "detail": f"{provision} requires the firm to request the missing information. The core does not contact the counterparty.",
                }
            )

    if repeated:
        categories.append("repeated_failure_marker")
        firm_steps.append(
            {
                "id": "consider_report_of_repeated_failure_to_fca",
                "agent_will_not_take": True,
                "detail": "Regulation 64D(5) or 64E(5) requires a report of repeated failure to the FCA. The core does not report. JMLSG paragraph 29 says a firm may use a risk-based view of what counts as repeated. The core does not make that judgement.",
            }
        )
    if suspicion:
        categories.append("suspicion_marker")
        firm_steps.append(
            {
                "id": "mlro_considers_sar",
                "agent_will_not_take": True,
                "detail": "The firm has already flagged suspicion. The MLRO decides whether to file. This core does not draft a suspicious activity report and does not file one. The Proceeds of Crime Act 2002 was not opened.",
            }
        )
    if sanctions:
        categories.append("sanctions_marker")
        explanations.append(
            "The firm has recorded a sanctions-screening hit. The sanctions regime was not opened. The marker is a reason to escalate, not a sanctions decision."
        )
    if rules_stale:
        categories.append("rules_stale")
        firm_steps.append(
            {
                "id": "analyst_reopens_pinned_sources",
                "agent_will_not_take": True,
                "detail": "A pinned source is older than the stale threshold. The core does not download a replacement.",
            }
        )
    if supplier is True:
        explanations.append(
            "The record says a third-party supplier is used. The FCA statement says the firm remains responsible for Travel Rule compliance."
        )
    if same_business is True:
        explanations.append(
            "JMLSG Annex I paragraph 8 says a transfer where both customers hold accounts with the same cryptoasset business is not in scope. "
            "That sentence was not in regulation 64A as opened. It is not applied."
        )

    firm_name = _clean_text(record.get("firm_name"), "firm_name", quarantined, signals) or "Harbourline Markets Ltd"

    blocking = {
        "possible_exclusion_64A",
        "wallet_attribution_unresolved",
        "missing_information",
        "non_corresponding_information",
        "correspondence_check_not_possible",
        "paragraph_6_request_outstanding",
        "originator_verification_not_recorded",
        "threshold_not_operative",
        "counterparty_travel_rule_status_not_relied_on",
        "rules_stale",
        "batch_file_assertion_not_read",
        "batch_file_conditions_not_shown",
        "repeated_failure_marker",
        "suspicion_marker",
        "sanctions_marker",
    }
    if sunrise_collect_gap:
        blocking.add("sunrise_jurisdiction")
    if unhosted_wallet and unhosted_requested and unhosted_received is not True:
        blocking.add("unhosted_wallet")
    if batch_blocks:
        blocking.add("batch_file_assertion_not_read")

    seen: list[str] = []
    for item in categories:
        if item not in seen:
            seen.append(item)
    categories = seen
    has_block = any(item in blocking for item in categories)
    if not has_block:
        categories.insert(0, "no_exception_on_these_fields")
        explanations.insert(
            0,
            "No missing or non-corresponding field was found on the checklist for this record. That is not a release, and it is not a decision to make the cryptoasset available.",
        )

    information_problem = any(
        item in categories
        for item in ("missing_information", "non_corresponding_information", "correspondence_check_not_possible")
    )
    hold_reasons: list[str] = []
    hold_provisions: list[str] = []
    if "missing_information" in categories or "non_corresponding_information" in categories or "correspondence_check_not_possible" in categories:
        if role == "originator":
            hold_reasons.append(
                "Regulation 64C(9) says the originator's cryptoasset business must not make the inter-cryptoasset business transfer before full compliance with regulation 64C. The agent does not block it."
            )
            hold_provisions.append("regulation 64C(9)")
        elif role == "beneficiary" and hosted:
            hold_reasons.append(
                "Regulation 64D(2)(c)(i) says the firm must consider whether to delay making the cryptoasset available until the information is received or any discrepancy is resolved. The agent does not delay it."
            )
            hold_provisions.append("regulation 64D(2)(c)(i)")
        elif role == "intermediary":
            hold_reasons.append(
                "Regulation 64E(2)(b)(i) says the intermediary must consider whether to delay the onward transfer until the information is received. The agent does not delay it."
            )
            hold_provisions.append("regulation 64E(2)(b)(i)")
    if "paragraph_6_request_outstanding" in categories and role == "originator":
        hold_reasons.append("Regulation 64C(2) information was requested and is not on the record.")
        hold_provisions.append("regulation 64C(2)")
    if "originator_verification_not_recorded" in categories:
        hold_reasons.append("Originator verification under regulation 64C(8) is not recorded.")
        hold_provisions.append("regulation 64C(8)")
    if "threshold_not_operative" in categories:
        hold_reasons.append("The £800 limb cannot be applied on the figures supplied, and regulation 64C(6) information is not on the record.")
        hold_provisions.append("regulation 64C(4)")
    if "possible_exclusion_64A" in categories or "wallet_attribution_unresolved" in categories:
        hold_reasons.append("Scope is not confirmed. Nothing is released while an analyst confirms it.")
        hold_provisions.append("regulation 64A")
    if "counterparty_travel_rule_status_not_relied_on" in categories or "rules_stale" in categories:
        hold_reasons.append("A status or a pinned source is not current enough to rely on.")
        hold_provisions.append("pinned catalogue")
    if sunrise_collect_gap:
        hold_reasons.append(
            "On this sunrise send, collection, verification, or storage is not recorded. The FCA statement says the information should be stored before the transfer is made where the counterparty cannot receive it."
        )
        hold_provisions.append("FCA Travel Rule statement, 6 February 2026")
    if "batch_file_assertion_not_read" in categories or "batch_file_conditions_not_shown" in categories:
        hold_reasons.append("The batch-file conditions in regulation 64C(7) are not treated as satisfied.")
        hold_provisions.append("regulation 64C(7)")
    if unhosted_wallet and unhosted_requested and unhosted_received is not True and not exclusion_asserted:
        hold_reasons.append("Regulation 64G(4) says the cryptoasset must not be made available when requested information was not received.")
        hold_provisions.append("regulation 64G(4)")

    return_proposed = (
        role in {"beneficiary", "intermediary"}
        and hosted
        and not exclusion_asserted
        and ("missing_information" in categories or "non_corresponding_information" in categories)
    )
    if return_proposed and role == "beneficiary":
        return_reason = (
            "Regulation 64D(2)(c)(ii) says the firm must consider whether, if the information is not received or the discrepancy is not resolved within a reasonable time, to return the cryptoasset. "
            "No number of days was found for a reasonable time. JMLSG Annex I paragraphs 32 and 33 discuss the operational risk of a return and say a return is not itself a Travel Rule transfer. "
            "Paragraph 33 is not applied as a statutory exclusion. The agent does not return the transfer."
        )
        return_provisions = ["regulation 64D(2)(c)(ii)"]
    elif return_proposed:
        return_reason = (
            "Regulation 64E(2)(b)(ii) says the intermediary must consider whether to return the cryptoasset if the information is not received within a reasonable time. "
            "The agent does not return it."
        )
        return_provisions = ["regulation 64E(2)(b)(ii)"]
    elif unhosted_wallet:
        return_reason = "Regulation 64G as opened has no return limb. Return is not proposed."
        return_provisions = ["regulation 64G"]
    elif role == "originator":
        return_reason = "Return in regulations 64D and 64E is a beneficiary or intermediary consideration. This record is the originator's business. Return is not proposed."
        return_provisions = ["regulation 64D", "regulation 64E"]
    else:
        return_reason = "No missing or non-corresponding information was found on which a return consideration arises. Return is not proposed, and the transfer is not released."
        return_provisions = ["regulation 64D"]

    escalate_bits: list[str] = []
    escalate_provisions: list[str] = []
    if suspicion or sanctions:
        escalate_bits.append("A suspicion marker or a sanctions-screening marker is already on the record. The agent does not assess it and does not file a report.")
        escalate_provisions.append("firm marker")
    if repeated:
        escalate_bits.append("Repeated failure is marked. A report to the FCA is a person's step under regulation 64D(5) or 64E(5).")
        escalate_provisions.append("regulation 64D(5)")
    if "rules_stale" in categories or "counterparty_travel_rule_status_not_relied_on" in categories:
        escalate_bits.append("A pinned source or the jurisdiction status needs a person to refresh it before it is relied on.")
        escalate_provisions.append("pinned catalogue")
    if "wallet_attribution_unresolved" in categories or "possible_exclusion_64A" in categories:
        escalate_bits.append("Scope is unresolved. An analyst confirms it.")
        escalate_provisions.append("regulation 64A")
    escalate_proposed = bool(escalate_bits)
    if not escalate_proposed:
        escalate_reason = "No marker on this record proposes escalation. The analyst may still escalate. The agent does not."
    else:
        escalate_reason = " ".join(escalate_bits) + " The agent does not escalate."

    if not hold_reasons:
        hold_reason = "No Travel Rule information limb on this record proposes a delay. Hold is not proposed. The agent does not release the transfer."
        hold_provisions = ["regulation 64D"]
    else:
        hold_reason = " ".join(hold_reasons)

    if information_problem and sunrise and role == "beneficiary":
        explanations.append(
            "The sunrise factor does not remove the regulation 64D request, delay, and return considerations. fca_statement_treated_as_waiver is false."
        )

    options = [
        _option("hold", bool(hold_reasons), hold_reason, hold_provisions),
        _option("return", return_proposed, return_reason, return_provisions),
        _option("escalate", escalate_proposed, escalate_reason, escalate_provisions),
    ]

    result = _base_shell(transfer_id_clean, True)
    result.update(
        {
            "firm_name": firm_name,
            "firm_role": role,
            "as_of": as_of.isoformat(),
            "catalogue_last_verified": LAST_VERIFIED,
            "threshold_gbp": THRESHOLD_GBP,
            "jmlsg_euro_threshold_used": False,
            "threshold": {
                "operative": threshold_operative,
                "value_gbp": str(amount) if amount is not None else None,
                "at_or_over_800": at_or_over,
                "paragraph_6_must_accompany": p6_must,
                "linked_transfers_assessed": linked,
            },
            "sunrise": {
                "recorded_status": status,
                "status_recorded_on": status_on,
                "relied_on": status_relied_on,
                "is_sunrise_on_relied_status": sunrise,
                "word_used_by_fca_page": "a jurisdiction without the Travel Rule",
                "word_used_by_jmlsg_paragraph_10": "sunrise issue",
            },
            "exception_categories": categories,
            "missing": gaps,
            "mismatches": mismatches,
            "options": options,
            "firm_steps_for_a_person": firm_steps,
            "explanation": explanations,
            "rules_current": not rules_stale,
            "any_source_stale": rules_stale,
            "sources_and_currency": source_rows,
            "unverified": list(UNVERIFIED),
            "prompt_injection": {
                "detected": bool(signals or prohibited),
                "followed": False,
                "signals": sorted(set(signals)),
                "quarantined_fields": quarantined,
                "prohibited_payload_keys_ignored": prohibited,
            },
            "same_business_exclusion_applied": False,
            "batch_file_read": False,
        }
    )
    result["analyst_decision"] = None
    result["actions_taken"] = []
    result["flags"] = _empty_flags()
    result["human_review"]["agent_recorded_decision"] = None
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Triage one synthetic Travel Rule transfer.")
    parser.add_argument("--input", required=True, help="Path to a transfer JSON file")
    parser.add_argument("--as-of", dest="as_of", help="YYYY-MM-DD. Defaults to the record, then the catalogue date.")
    parser.add_argument("--stale-after-days", type=int, default=DEFAULT_STALE_AFTER_DAYS)
    args = parser.parse_args(argv)
    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    as_of = _parse_date(args.as_of, "as-of") if args.as_of else None
    try:
        result = triage(payload, as_of=as_of, stale_after_days=args.stale_after_days)
    except TriageError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    if result["label"] == REFUSED:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
