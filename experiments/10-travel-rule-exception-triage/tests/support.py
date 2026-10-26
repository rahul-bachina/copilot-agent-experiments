"""Synthetic transfer factory. Every wallet string is labelled fake."""

from __future__ import annotations

import copy


def party(**overrides) -> dict:
    base = {
        "party_type": "individual",
        "name": "Alex Quinn",
        "registered_or_trading_name": None,
        "account_number": "SYNTH-WALLET-NOT-REAL-001",
        "unique_transaction_identifier": None,
        "customer_identification_number": None,
        "address": "1 Synthetic Quay, Exampletown",
        "registered_office": None,
        "principal_place_of_business": None,
        "birth_certificate_number": None,
        "passport_number": None,
        "national_identity_card_number": None,
        "date_of_birth": None,
        "place_of_birth": None,
    }
    base.update(overrides)
    return base


def clean_inbound(**overrides) -> dict:
    """A complete UK inbound transfer under £800. No exception is expected."""
    originator = party(name="Alex Quinn", account_number="SYNTH-WALLET-ORIGIN-001")
    beneficiary = party(name="Sam Rivera", account_number="SYNTH-WALLET-BENE-001")
    record = {
        "transfer_id": "SYN-TR-1000",
        "synthetic": True,
        "firm_name": "Harbourline Markets Ltd",
        "firm_role": "beneficiary",
        "as_of": "2026-10-26",
        "value_gbp": 250,
        "linked_transfers_assessed": True,
        "all_executing_businesses_in_uk": True,
        "wallet_attribution": "hosted",
        "both_parties_cryptoasset_businesses_own_behalf": False,
        "funds_transfer_regulation_article_3_9": False,
        "same_cryptoasset_business_both_sides": False,
        "originator_information_verified_by_firm": True,
        "information_stored_by_firm": True,
        "paragraph_6_requested_by_beneficiary": False,
        "third_party_supplier_used": False,
        "unique_transaction_identifier": "SYN-UTI-1000",
        "counterparty": {
            "vasp_name": "Synthetic Ruleland Exchange",
            "jurisdiction_label": "Synthetic Ruleland",
            "jurisdiction_code": "SYN-RULE",
            "travel_rule_status": "in_force",
            "status_recorded_on": "2026-10-01",
            "can_receive_required_information": True,
            "in_united_kingdom": True,
        },
        "information_on_transfer": {
            "originator": originator,
            "beneficiary": beneficiary,
        },
        "firm_holds": {
            "originator": copy.deepcopy(originator),
            "beneficiary": copy.deepcopy(beneficiary),
        },
        "beneficiary_part3_cdd": {
            "name": "Sam Rivera",
            "account_number": "SYNTH-WALLET-BENE-001",
        },
        "batch": {"is_batch_file": False},
        "unhosted": {
            "customer_role": None,
            "information_requested_from_customer": False,
            "requested_information_received": None,
        },
        "firm_markers": {
            "suspicion_already_flagged_by_analyst": False,
            "repeated_information_failure_flagged_by_firm": False,
            "sanctions_screening_hit_recorded_by_firm": False,
        },
        "notes": "",
    }
    return _merge(record, overrides)


def _merge(base: dict, override: dict) -> dict:
    out = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _merge(out[key], value)
        else:
            out[key] = value
    return out
