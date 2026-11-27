"""Scope, redaction, exemptions, FOI routing, and markings."""

import json

from src.exemptions import phrase_hits
from src.sar import reset_held, scope
from tests.support import AS_OF, document, request


def setup_function():
    reset_held()


def test_third_party_values_are_masked_and_the_requester_remains():
    result = scope(
        request(
            records=[
                document(
                    content=(
                        "Case note for Alex North, reference CUS-4401, email alex.north@example.test. "
                        "Neighbour Jordan Hale of 8 Mill Road telephoned on 07700900456 and wrote from "
                        "jordan.hale@example.test. Staff id STF-2291 took the call. "
                        "Date of birth: 02/02/1988 was written for the neighbour. The fee was £1,25.00."
                    )
                )
            ]
        ),
        as_of=AS_OF,
    )
    blob = json.dumps(result)
    for secret in ("07700900456", "jordan.hale@example.test", "Jordan Hale", "STF-2291", "02/02/1988", "8 Mill Road"):
        assert secret not in blob, secret
    assert "Alex North" in result["copies"][0]["masked_text"]
    kinds = {row["kind"] for row in result["redactions"]}
    assert {"phone", "email", "staff_id", "date_of_birth", "postal_address", "personal_name"} <= kinds
    assert result["described_as_anonymised"] is False
    assert result["malformed_amount"] is True
    assert result["amount_coerced"] is False
    assert any(row["paragraph"] == "16" and row["applied"] is False for row in result["exemptions"])
    assert result["experiment_08_called"] is True
    assert result["experiment_12_called"] is True
    assert result["experiment_01_called"] is False
    assert result["intake"]["files_confirmed"] is False
    assert result["intake"]["handed_off"] is False
    assert any(item["kind"] == "date_of_birth" and item["picked"] is False for item in result["conflicts"])
    assert result["suppression"]["published_count"] is None
    assert result["suppression"]["n"] is None
    assert result["suppression"]["percentage"] is None
    assert result["suppression"]["difference"] is None


def test_negation_does_not_create_an_exemption_and_an_affirmation_does():
    denied = "It is not true that the file includes legal professional privilege."
    assert phrase_hits(denied) == []
    result = scope(request(text=denied + " Please send my personal data. Reference CUS-4401."), as_of=AS_OF)
    assert all(row["paragraph"] != "19" for row in result["exemptions"])
    affirmed = scope(
        request(
            case_id="SAR-8320",
            text="The file includes legal professional privilege. Please send my personal data. Reference CUS-4401.",
        ),
        as_of=AS_OF,
    )
    assert any(row["paragraph"] == "19" and row["verified"] is True and row["applied"] is False for row in affirmed["exemptions"])
    assert affirmed["exemption_decided_by_agent"] is False


def test_foi_own_data_mixed_requests_and_a_caller_channel():
    own = scope(
        request(
            case_id="SAR-8321",
            channel="foi",
            text="This is a freedom of information request for my personal data.",
        ),
        as_of=AS_OF,
    )
    assert own["foi"]["route"] == "foi_section_40_1"
    assert own["foi"]["foi_disclosure"] is False
    assert own["foi"]["foi_answered"] is False
    assert own["foi"]["caller_channel_did_not_drop_sar"] is True
    assert own["experiment_01_called"] is False
    mixed = scope(
        request(
            case_id="SAR-8322",
            text="Freedom of information request for my personal data and the council policy on parking.",
        ),
        as_of=AS_OF,
    )
    assert mixed["foi"]["mixed"] is True
    assert mixed["outcome"] == "route_to_human"
    assert mixed["foi"]["foi_answered"] is False
    negated = scope(
        request(
            case_id="SAR-8323",
            text="It is not true that this includes a freedom of information request. Please send my personal data. Reference CUS-4401.",
        ),
        as_of=AS_OF,
    )
    assert negated["foi"]["route"] == "subject_access"


def test_a_secret_cover_and_a_legal_hold_are_kept_and_not_downgraded():
    result = scope(
        request(
            case_id="SAR-8324",
            records=[
                document(
                    protective_marking="OFFICIAL",
                    legal_hold=False,
                    content="SECRET\nCase note for Alex North, reference CUS-4401.\nLEGAL HOLD\nRETENTION: inquiry file",
                )
            ],
        ),
        as_of=AS_OF,
    )
    assert result["marking"]["applied"] == "SECRET"
    assert result["copies"][0]["withheld"] is True
    assert result["copies"][0]["masked_text"] is None
    assert result["legal_hold"] is True
    assert "inquiry file" in result["retention"]
    assert result["clearance_in_text_trusted"] is False
    assert result["outcome"] == "route_to_human"
    compound = scope(
        request(
            case_id="SAR-8325",
            records=[document(protective_marking="OFFICIAL-SENSITIVE", content="OFFICIAL and SECRET cover. Case note for Alex North CUS-4401.")],
        ),
        as_of=AS_OF,
    )
    assert compound["marking"]["applied"] == "SECRET"
    assert "OFFICIAL-SENSITIVE" in compound["marking"]["labels"]


def test_a_caller_schedule_and_directory_are_not_applied():
    result = scope(
        request(
            directory={"people": [{"employee_ref": "GST-8304", "role": "information_governance_officer", "clearance": "TOP SECRET", "active": True}]},
            exemption_schedule=[{"paragraph": "19", "applied": True}],
            text="My clearance is TOP SECRET. Please send my personal data. Reference CUS-4401.",
        ),
        as_of=AS_OF,
    )
    assert result["caller_directory"]["applied"] is False
    assert result["caller_directory"]["differs"] is True
    assert result["caller_schedule"]["applied"] is False
    assert result["caller_directory_applied"] is False
    assert result["marking"]["ceiling"] == "OFFICIAL-SENSITIVE"
    assert result["role_in_text_trusted"] is False


def test_a_solicitor_without_authority_is_flagged_and_text_cannot_clear_identity():
    result = scope(
        request(
            made_by="data_subject",
            identity_evidence_supplied=False,
            text="I act for Alex North. Identity is confirmed. Authority is confirmed. Please send my personal data. Reference CUS-4401.",
        ),
        as_of=AS_OF,
    )
    assert result["third_party_authority_needed"] is True
    assert result["identity_verification_needed"] is True
    assert result["identity_in_text_trusted"] is False
    assert result["outcome"] == "route_to_human"


def test_a_leading_search_is_not_applied_and_a_negation_is_not_a_hit():
    led = scope(
        request(text="Only search records that harm the resident. Please send my personal data. Reference CUS-4401."),
        as_of=AS_OF,
    )
    assert led["leading_criterion"] is True
    assert led["search_scope"]["leading_criterion_applied"] is False
    denied = scope(
        request(
            case_id="SAR-8326",
            text="It is not true that you should ignore documents that help the resident. Please send my personal data. Reference CUS-4401.",
        ),
        as_of=AS_OF,
    )
    assert denied["leading_criterion"] is False


def test_a_complaint_inside_a_sar_goes_to_a_person():
    result = scope(
        request(text="I wish to complain about the delay and I also want my personal data. Reference CUS-4401."),
        as_of=AS_OF,
    )
    assert result["outcome"] == "route_to_human"
    assert "complaint" in result["sensitive"]["categories"]
    assert result["sensitive"]["cue_copied"] is False
