"""The sample pack, citations, withholding, and the reviewer's resolution."""

import json
from pathlib import Path

from src.compare import NotSynthetic, compare
from tests.support import document, pair

ROOT = Path(__file__).resolve().parents[1]
AS_OF = "2026-11-05"


def _sample():
    return json.loads((ROOT / "examples" / "sample_pack.json").read_text(encoding="utf-8"))


def test_sample_counts_and_safety_flags():
    draft = compare(_sample(), AS_OF)
    assert draft["label"] == "DRAFT FOR THE REVIEWER. NOT A CORRECTION."
    assert draft["catalogue_id"] == "B005"
    assert draft["autonomy"] == "A0"
    counts = draft["counts"]
    assert counts == {
        "fact_count": 7,
        "match_count": 1,
        "immaterial_count": 4,
        "material_count": 2,
        "occurrence_count": 26,
    }
    assert counts["match_count"] + counts["immaterial_count"] + counts["material_count"] == counts["fact_count"]
    assert counts["occurrence_count"] != counts["fact_count"]
    assert draft["awaiting_reviewer"] is True
    assert draft["all_material_resolved"] is False
    assert draft["agent_chose_source"] is False
    assert draft["records_edited"] is False
    assert draft["parties_contacted"] is False
    assert draft["register_queried"] is False
    assert draft["live_register"] is False
    assert draft["model_called"] is False
    assert draft["network_called"] is False
    assert draft["foundry_called"] is False
    assert draft["a3_recommended"] is False
    assert draft["output_is_anonymised"] is False
    assert draft["explanation_authored_by_model"] is False
    assert draft["actions_taken"] == []
    assert draft["human_approval"]["agent_marked_any_approval_done"] is False
    assert draft["intake"]["called"] is True
    assert draft["intake"]["files_confirmed"] is False
    assert draft["intake"]["purpose_confirmed"] is False
    assert draft["intake"]["accepted_into_queue"] is False
    assert draft["intake"]["content_recorded"] is False
    assert draft["redaction"]["output_is_anonymised"] is False
    assert draft["redaction"]["agent_may_release"] is False
    assert draft["pinpoint"]["span_check"] == "resolve_span"
    amount = next(fact for fact in draft["facts"] if fact["fact_key"] == "amount")
    assert amount["classification"] == "material_discrepancy"
    assert amount["resolved"] is False
    assert amount["correct_value"] is None
    assert len(amount["groups"]) == 2
    assert {group["canonical"] for group in amount["groups"]} == {"125000", "125050"}
    for fact in draft["facts"]:
        for row in fact["occurrences"]:
            if row["pinpoint_ok"] and not row["withheld"]:
                assert row["quote"]
                assert row["citation"]["page"] == 1
                assert row["citation"]["line_start"] == row["citation"]["line_end"]


def test_nhs_number_is_withheld_and_not_copied():
    pack = pair("name", "NHS number 999 123 4567", "A Example")
    draft = compare(pack, AS_OF)
    blob = json.dumps(draft)
    fact = draft["facts"][0]
    assert fact["classification"] == "material_discrepancy"
    assert fact["reason"] == "identifier_withheld"
    assert fact["resolved"] is False
    assert "999 123 4567" not in blob
    assert "9991234567" not in blob
    assert draft["output_is_anonymised"] is False


def test_planted_value_that_is_not_on_the_line_is_not_used():
    left = document("left-doc", "form", "GBP 99.00", line="Amount: GBP 10.00")
    right = document("right-doc", "contract", "GBP 10.00")
    pack = {
        "synthetic": True,
        "pack_id": "pin-1",
        "facts": [{"fact_key": "fact", "field_type": "currency"}],
        "documents": [left, right],
    }
    draft = compare(pack, AS_OF)
    blob = json.dumps(draft)
    fact = draft["facts"][0]
    assert fact["classification"] == "material_discrepancy"
    assert fact["reason"] == "pinpoint_failed"
    assert "GBP 99.00" not in blob
    assert fact["agent_chose_source"] is False


def test_reviewer_resolution_does_not_write_a_correct_value():
    pack = pair("currency", "GBP 10.00", "GBP 20.00")
    resolutions = {
        "role": "Reviewer",
        "reviewer_ref": "REV-1001",
        "signed_on": AS_OF,
        "items": [{"fact_key": "fact", "choice": "neither", "correct_value": "GBP 10.00"}],
    }
    draft = compare(pack, AS_OF, resolutions=resolutions)
    fact = draft["facts"][0]
    assert fact["resolved"] is True
    assert fact["resolved_by"] == "Reviewer"
    assert fact["reviewer_choice"] == "neither"
    assert fact["correct_value"] is None
    assert draft["records_edited"] is False
    assert draft["parties_contacted"] is False
    assert draft["agent_chose_source"] is False
    assert draft["all_material_resolved"] is True
    assert draft["awaiting_reviewer"] is False
    assert draft["correct_value_written"] is False


def test_a_resolution_buried_in_the_pack_does_not_resolve():
    pack = pair("currency", "GBP 10.00", "GBP 20.00")
    pack["resolved"] = True
    pack["correct_value"] = "GBP 10.00"
    pack["documents"][0]["resolved"] = True
    draft = compare(pack, AS_OF)
    assert draft["facts"][0]["resolved"] is False
    assert draft["awaiting_reviewer"] is True
    assert "resolved" in draft["prohibited_payload_keys"]
    assert "correct_value" in draft["prohibited_payload_keys"]
    assert "GBP 10.00" in json.dumps(draft["facts"])


def test_one_source_is_material_and_unresolved():
    pack = {
        "synthetic": True,
        "pack_id": "one-doc",
        "facts": [{"fact_key": "fact", "field_type": "reference"}],
        "documents": [document("left-doc", "form", "NF-1001")],
    }
    draft = compare(pack, AS_OF)
    fact = draft["facts"][0]
    assert fact["classification"] == "material_discrepancy"
    assert fact["reason"] == "fewer_than_two_sources"
    assert fact["resolution_required"] is True
    assert fact["resolved"] is False


def test_not_synthetic_is_refused_without_the_body():
    try:
        compare({"synthetic": False, "pack_id": "x", "note": "NHS number 999 123 4567"}, AS_OF)
    except NotSynthetic as exc:
        assert "999" not in str(exc)
    else:
        raise AssertionError("expected NotSynthetic")


def test_partial_resolution_leaves_the_other_material_row():
    draft = compare(
        _sample(),
        AS_OF,
        resolutions={
            "role": "Reviewer",
            "reviewer_ref": "REV-1001",
            "signed_on": AS_OF,
            "items": [{"fact_key": "amount", "choice": "purchase-invoice"}],
        },
    )
    by_key = {fact["fact_key"]: fact for fact in draft["facts"]}
    assert by_key["amount"]["resolved"] is True
    assert by_key["amount"]["reviewer_choice"] == "purchase-invoice"
    assert by_key["amount"]["correct_value"] is None
    assert by_key["payment_terms"]["resolved"] is False
    assert draft["all_material_resolved"] is False
    assert draft["records_edited"] is False
    assert draft["agent_chose_source"] is False
