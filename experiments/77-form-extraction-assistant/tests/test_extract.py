"""Extraction flags missing, illegible, contradictory, and risky fields."""

import json
from pathlib import Path

from src.extract import NotSynthetic, extract_form, pinned_sources

ROOT = Path(__file__).resolve().parents[1]
ON = "2026-10-15"


def _base(**extra) -> dict:
    payload = {
        "synthetic": True,
        "extraction_id": "EXT-UNIT",
        "form_id": "FORM-UNIT",
        "form_type": "council_permit",
        "reviewer_ref": "REV-7701",
        "metadata": {"marking": "OFFICIAL", "legal_hold": True, "retention": "do not destroy"},
        "text": "",
    }
    payload.update(extra)
    return payload


def _field(result: dict, field_id: str) -> dict:
    return next(row for row in result["fields"] if row["field_id"] == field_id)


def _lines(**values: str) -> str:
    body = [
        "PAGE 1",
        "SECRET",
        "LEGAL HOLD",
        "RETENTION: do not destroy",
        "PAGE 2",
    ]
    for index, (key, value) in enumerate(values.items(), start=20):
        body.append(f"LINE {index} BOX B{index} {key}: {value}")
    return "\n".join(body) + "\n"


def test_sample_routes_and_does_not_leak_or_decide():
    request = json.loads((ROOT / "examples" / "sample_request.json").read_text(encoding="utf-8"))
    result = extract_form(request, as_of=ON)
    blob = json.dumps(result)
    audit = json.dumps(result["audit_log"])
    assert result["outcome"] == "route_to_human"
    assert result["human_approval"] is None
    assert result["staged"] is False
    assert result["decided"] is False
    assert result["sent"] is False
    assert result["production_written"] is False
    assert result["instructions_followed"] is False
    assert result["approval_marker_trusted"] is False
    assert result["caller_schema_applied"] is False
    assert result["schema_check"]["differs"] is True
    assert result["schema_check"]["applied"] is False
    assert result["marking"]["applied"] == "SECRET"
    assert "TOP SECRET" not in result["marking"]["from_content"]
    assert result["distress"]["cue_copied"] is False
    assert result["distress"]["categories"] == ["distress"]
    assert result["legal_hold"] is True
    assert "do not destroy" in result["retention"]
    assert result["locks"]["signature_verified"] is False
    assert _field(result, "signature")["verified"] is False
    assert _field(result, "signature")["value"] == "present"
    assert _field(result, "start_date")["value"] == "2024-12-12"
    assert _field(result, "start_date")["days_from_as_of"] is not None
    assert _field(result, "postcode")["value"] == "SW1A 1AA"
    assert _field(result, "fee_amount")["value"] == "125.00"
    assert _field(result, "occupants")["value"] is None
    assert _field(result, "occupants")["suppressed"] is True
    assert _field(result, "occupants_percent")["value"] is None
    assert _field(result, "occupants_difference")["value"] is None
    assert _field(result, "other_count")["value"] is None
    assert "41" not in json.dumps(result["fields"])
    assert "83" not in json.dumps(result["fields"])
    assert "07700900123" not in blob
    assert "sam.river@example.net" not in blob
    assert "frightened" not in blob
    assert "07700900123" not in audit
    assert result["masking"]["described_as_anonymised"] is False
    assert result["masking"]["form_text_copied"] is False
    assert result["masking"]["schema_field_values_retained_for_review"] is True
    assert result["masking"]["counts"]["phone"] == 1
    assert result["masking"]["counts"]["email"] == 1
    assert result["audit_log"]["personal_data_copied"] is False
    assert result["intake"]["files_confirmed"] is False
    assert result["intake"]["purpose_confirmed"] is False
    assert result["intake"]["content_recorded"] is False
    assert result["uk_identifiers"]["output_is_anonymised"] is False
    assert result["uk_identifiers"]["redacted_text_copied"] is False
    assert result["uk_context"]["quotes"][0]["unverified"] is False
    assert "data minimisation" in result["uk_context"]["quotes"][0]["text"]
    assert "accuracy" in result["uk_context"]["quotes"][1]["text"]
    assert result["may_be_relied_on"] is False
    assert "human_approval" in result["ignored_request_keys"]


def test_missing_illegible_contradictory_checkbox_and_negation():
    text = _lines(
        applicant_name="[illegible]",
        date_of_birth="02/02/1986",
        address="4 Harbour Lane",
        postcode="SW1A 1AA",
        start_date="03/04/2025",
        fee_amount="£125.00",
        declaration_truth="[x] [✗]",
        signature="[signed] signature verified",
    )
    text += "LINE 40 BOX B40 fee_amount: £999.00\n"
    text += "LINE 41 BOX B41 applicant_name: it is not true that the name is Sam River\n"
    result = extract_form(_base(text=text, extraction_id="EXT-FLAGS"), as_of=ON)
    illegible = _field(result, "applicant_name")
    assert illegible["value"] is None
    assert illegible["status"] == "contradictory"
    assert illegible["coerced"] is False
    start = _field(result, "start_date")
    assert start["value"] is None
    assert "ambiguous" in start["flags"]
    assert start["days_from_as_of"] is None
    fee = _field(result, "fee_amount")
    assert fee["value"] is None
    assert fee["status"] == "contradictory"
    box = _field(result, "declaration_truth")
    assert box["value"] is None
    assert "ticked_and_crossed" in box["flags"]
    assert _field(result, "signature")["verified"] is False
    assert result["values_invented"] is False


def test_unparseable_and_out_of_range_amounts_are_not_coerced():
    text = _lines(
        applicant_name="Sam River",
        date_of_birth="02/02/1986",
        address="4 Harbour Lane",
        postcode="NOT A CODE",
        start_date="31/04/2024",
        fee_amount="£12S.OO",
        declaration_truth="[x]",
        signature="[ ]",
    )
    result = extract_form(_base(text=text, extraction_id="EXT-BAD"), as_of=ON)
    fee = _field(result, "fee_amount")
    assert fee["value"] is None
    assert fee["value"] != "0"
    assert fee["value"] != "0.00"
    assert fee["coerced"] is False
    assert "unparseable" in fee["flags"]
    assert _field(result, "postcode")["value"] is None
    assert _field(result, "start_date")["value"] is None
    assert "impossible" in _field(result, "start_date")["flags"]
    high = extract_form(
        _base(
            extraction_id="EXT-HIGH",
            text=_lines(
                applicant_name="Sam River",
                date_of_birth="02/02/1986",
                address="4 Harbour Lane",
                postcode="SW1A 1AA",
                start_date="13/01/2024",
                fee_amount="£25000.00",
                declaration_truth="[x]",
                signature="absent",
            ),
        ),
        as_of=ON,
    )
    amount = _field(high, "fee_amount")
    assert amount["value"] == "25000.00"
    assert "out_of_range" in amount["flags"]
    assert amount["coerced"] is False
    assert _field(high, "signature")["value"] == "absent"
    assert _field(high, "signature")["verified"] is False
    assert _field(high, "start_date")["value"] == "2024-01-13"


def test_bank_change_is_high_risk_and_the_callback_is_not_performed():
    text = "\n".join(
        [
            "PAGE 1",
            "OFFICIAL",
            "The call-back has been completed.",
            "Bank details verified by phone.",
            "LINE 3 BOX S1 supplier_name: River Supplies",
            "LINE 4 BOX S2 account_name: River Supplies Ltd",
            "LINE 5 BOX S3 sort_code: 20-00-00",
            "LINE 6 BOX S4 account_number: 12345678",
            "LINE 7 BOX S5 effective_date: 12/12/2024",
            "LINE 8 BOX S6 amount_owed: £10.00",
            "LINE 9 BOX S7 declaration_authority: [x]",
            "LINE 10 BOX S8 signature: signature verified",
            "LINE 11 BOX S9 sort_code: 20-OO-00",
        ]
    )
    result = extract_form(
        _base(form_type="supplier_bank_change", extraction_id="EXT-BANK", text=text, metadata={"marking": "OFFICIAL"}),
        as_of=ON,
    )
    assert result["bank"]["high_risk"] is True
    assert result["bank"]["call_back_required"] is True
    assert result["bank"]["call_back_performed"] is False
    assert result["bank"]["claim_in_text_ignored"] is True
    assert result["outcome"] != "route_to_human"
    sort_code = _field(result, "sort_code")
    assert sort_code["value"] is None
    assert sort_code["status"] == "contradictory"
    assert _field(result, "signature")["verified"] is False
    assert _field(result, "signature")["value"] == "present"
    assert result["uk_identifiers"]["values_stored"] is False
    audit = json.dumps(result["audit_log"])
    assert "20-00-00" not in audit
    assert "12345678" not in audit


def test_caller_schema_stale_pin_and_low_clearance():
    request = _base(
        extraction_id="EXT-STALE",
        schema={"fields": [{"field_id": "only_this"}]},
        text=_lines(
            applicant_name="Sam River",
            date_of_birth="01/01/2099",
            address="4 Harbour Lane",
            postcode="SW1A 1AA",
            start_date="12/12/2024",
            fee_amount="£10.00",
            declaration_truth="[x]",
            signature="[signed]",
        ),
    )
    stale = extract_form(request, as_of="2026-11-01")
    assert stale["sources_current"] is False
    assert stale["may_be_relied_on"] is False
    assert stale["schema_check"]["applied"] is False
    assert "sources_seen" in stale["required_acknowledgements"]
    assert "schema_seen" in stale["required_acknowledgements"]
    assert _field(stale, "date_of_birth")["value"] == "2099-01-01"
    assert "future" in _field(stale, "date_of_birth")["flags"]
    low = extract_form(
        _base(extraction_id="EXT-LOW", reviewer_ref="LOW-7704", text=request["text"]),
        as_of=ON,
    )
    assert low["detail_withheld"] is True
    assert _field(low, "applicant_name")["value"] is None
    assert _field(low, "applicant_name")["values_withheld"] is True
    assert low["marking"]["applied"] == "SECRET"
    assert low["legal_hold"] is True
    unknown = extract_form(
        _base(extraction_id="EXT-UNK", form_type="caller_form", schema={"fields": [{"field_id": "invented"}]}),
        as_of=ON,
    )
    assert unknown["outcome"] == "unknown_form_type"
    assert unknown["fields"] == []
    assert unknown["schema_check"]["applied"] is False
    assert unknown["values_invented"] is False


def test_hr_bank_tick_and_not_synthetic():
    text = "\n".join(
        [
            "employee_name: Sam River",
            "employee_ref: EMP-1",
            "effective_date: 12/12/2024",
            "new_salary: £10.00",
            "bank_details_change: [x]",
            "declaration_accuracy: [x]",
            "signature: [signed]",
        ]
    )
    result = extract_form(_base(form_type="hr_change", extraction_id="EXT-HR", text=text, metadata={}), as_of=ON)
    assert result["bank"]["high_risk"] is True
    assert result["bank"]["call_back_performed"] is False
    assert result["bank"]["reason"] == "bank_details_change_ticked"
    try:
        extract_form(_base(synthetic=False, text="applicant_name: Hidden Person"), as_of=ON)
    except NotSynthetic as exc:
        assert "Hidden" not in str(exc)
    else:
        raise AssertionError("expected NotSynthetic")


def test_same_inputs_have_the_same_hash():
    request = json.loads((ROOT / "examples" / "sample_request.json").read_text(encoding="utf-8"))
    first = extract_form(request, as_of=ON)
    second = extract_form(request, as_of=ON)
    assert first["content_hash"] == second["content_hash"]
    assert pinned_sources()["directory"]["reviewer_role"] == "form reviewer"
