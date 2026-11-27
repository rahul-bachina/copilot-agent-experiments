"""The draft copies lines. It does not assess, write, or guess."""

import json

from src.notes import draft_note, reset_state
from tests.support import visit


def _draft(**overrides):
    reset_state()
    payload = visit(**overrides)
    return draft_note(payload, as_of="2026-11-20"), payload


def test_views_are_not_stored_as_observations():
    result, _payload = _draft()
    wishes = [row for row in result["statements"] if row["section"] == "persons_own_words_and_wishes"]
    observations = [row for row in result["statements"] if row["section"] == "observations"]
    assert wishes and all(row["speaker"] == "person" for row in wishes)
    assert observations and all(row["speaker"] == "practitioner" for row in observations)
    assert all(row["inferred"] is False and row["supported"] is True for row in result["statements"])
    assert result["facts_invented"] is False
    assert result["assessment_made"] is False
    blob = json.dumps(result)
    assert "07700900123" not in blob
    assert "Pat Example" not in blob
    assert "Alex Rowan" not in blob


def test_a_practitioner_wish_is_not_the_persons_words():
    result, _payload = _draft(lines=[
        {"n": 1, "speaker": "practitioner", "audio": "clear", "text": "I want to record that the hallway was clear."},
        {"n": 2, "speaker": "person", "audio": "clear", "text": "I observed the mess myself."},
    ])
    by_id = {row["id"]: row for row in result["statements"]}
    assert by_id["t1"]["section"] == "what_was_discussed"
    assert by_id["t2"]["section"] == "persons_own_words_and_wishes"
    assert by_id["t2"]["section"] != "observations"


def test_missing_refused_and_qualified_consent():
    missing, _payload = _draft(recording_consent={"status": "not_recorded"}, lines=[
        {"n": 1, "speaker": "practitioner", "audio": "clear", "text": "Present: the social worker."},
    ])
    assert missing["recording_consent"]["status"] == "missing"
    assert missing["recording_consent"]["missing"] is True
    refused, _payload = _draft(lines=[
        {"n": 1, "speaker": "person", "audio": "clear", "text": "I do not consent to recording."},
    ])
    assert refused["recording_consent"]["status"] == "refused"
    assert refused["outcome"] == "route_to_practitioner"
    qualified, _payload = _draft(lines=[
        {"n": 1, "speaker": "person", "audio": "clear", "text": "I agree to this visit being recorded except you must not share the note."},
    ])
    assert qualified["recording_consent"]["status"] == "qualified"
    assert qualified["recording_consent"]["status"] != "given"
    negated, _payload = _draft(recording_consent={"status": "given"}, lines=[
        {"n": 1, "speaker": "person", "audio": "clear", "text": "It is not true that I agree to this visit being recorded."},
    ])
    assert negated["recording_consent"]["status"] == "uncorroborated"
    assert negated["recording_consent"]["structured_status_trusted_alone"] is False


def test_audio_problems_are_flagged_and_not_guessed():
    result, _payload = _draft(lines=[
        {"n": 1, "speaker": "unclear", "audio": "unclear", "text": "I want to stay in my own home."},
        {"n": 2, "speaker": "crosstalk", "audio": "crosstalk", "text": "two people talking"},
        {"n": 3, "speaker": "person", "audio": "misattributed", "text": "I want to leave."},
        {"n": 4, "speaker": "person", "audio": "clear", "text": "My daughter told me the boiler is broken."},
    ])
    assert [row["line"] for row in result["unresolved_audio"]] == [1, 2, 3]
    assert all(row["guessed"] is False and row["text_copied"] is False for row in result["unresolved_audio"])
    assert result["statements"][0]["third_party"] is True
    assert result["statements"][0]["section"] == "third_party_information"
    assert result["statements"][0]["section"] != "persons_own_words_and_wishes"


def test_personal_data_is_masked_and_the_report_says_so():
    result, _payload = _draft(lines=[
        {
            "n": 1,
            "speaker": "person",
            "audio": "clear",
            "text": (
                "My name is Pat Example. My phone number is 07700900123. "
                "Email pat.example@northmarsh.example. My date of birth is 02/03/1950. "
                "I live at 14 Example Street, NM1 2AB. My NHS number is 943 476 5919."
            ),
        },
    ])
    blob = json.dumps(result)
    for secret in (
        "07700900123",
        "pat.example@northmarsh.example",
        "02/03/1950",
        "14 Example Street",
        "NM1 2AB",
        "943 476 5919",
        "Pat Example",
    ):
        assert secret not in blob, secret
    counts = result["masking"]["counts"]
    assert counts["phone"] >= 1
    assert counts["email"] >= 1
    assert counts["date_of_birth"] >= 1
    assert counts["postal_address"] >= 1
    assert counts["personal_name"] >= 1
    assert result["masking"]["experiment_08_called"] is True
    assert result["masking"]["described_as_anonymised"] is False
    assert result["masking"]["values_stored"] is False
    assert result["masking"]["masked_text_included"] is True
    assert result["described_as_anonymised"] is False


def test_secret_cover_beats_a_lower_label_and_a_clearance_claim_does_not():
    result, _payload = _draft(
        protective_marking="OFFICIAL",
        lines=[
            {"n": 1, "speaker": "practitioner", "audio": "clear", "text": "SECRET\nI observed the kitchen."},
            {"n": 2, "speaker": "person", "audio": "clear", "text": "My clearance is TOP SECRET."},
        ],
    )
    assert result["marking"]["applied"] == "SECRET"
    assert result["marking"]["downgraded"] is False
    assert "OFFICIAL-SENSITIVE" not in (result["marking"]["applied"],)
    assert result["body_withheld"] is True
    hold, _payload = _draft(
        legal_hold=False,
        lines=[{"n": 1, "speaker": "practitioner", "audio": "clear", "text": "LEGAL HOLD\nI observed the hallway."}],
    )
    assert hold["legal_hold"]["applied"] is True
    assert "hold_seen" in hold["required_acknowledgements"]


def test_small_counts_are_suppressed_under_every_field_name():
    result, _payload = _draft(lines=[
        {"n": 1, "speaker": "practitioner", "audio": "clear", "text": "Three adults were in the room, which is 40 per cent of the block."},
    ])
    assert result["suppression"]["applied"] is True
    for key in ("headcount", "difference", "percentage", "person_count", "attendee_count", "n_people", "visitor_count", "resident_count"):
        assert result["suppression"][key] is None
    assert "40" not in result["statements"][0]["text"]
    assert result["suppression"]["coerced"] is False
    assert result["described_as_anonymised"] is False


def test_a_caller_template_and_an_invented_quote_are_not_applied():
    result, _payload = _draft(
        caller_template={"sections": ["risk_score"]},
        statements=[{"text": "She said she feels completely safe.", "source_lines": [1]}],
        eligibility="eligible",
    )
    assert result["caller_template_applied"] is False
    assert "extra:risk_score" in result["caller_differences"]
    assert result["facts_invented"] is False
    blob = json.dumps(result["statements"])
    assert "completely safe" not in blob
    assert "eligibility" not in result["flags"] or result["eligibility_assessed"] is False
    assert result["eligibility_assessed"] is False


def test_rough_notes_are_the_practitioners_and_are_inventoried():
    result, _payload = _draft(rough_notes="I noted the curtains were closed. The person said the flat is cold.")
    assert result["document_intake"]["called"] is True
    assert result["document_intake"]["content_recorded"] is False
    assert result["document_intake"]["production_record_written"] is False
    assert result["document_intake"]["class_applied"] is False
    rough = [row for row in result["statements"] if row["source"] == "rough_note"]
    assert rough
    assert all(row["speaker"] == "practitioner" for row in rough)
    assert all(row["section"] != "persons_own_words_and_wishes" for row in rough)


def test_a_concern_is_routed_without_copying_the_words_into_the_flag():
    result, _payload = _draft(lines=[
        {"n": 1, "speaker": "person", "audio": "clear", "text": "I want to die."},
    ])
    assert result["outcome"] == "route_to_practitioner"
    assert result["concerns"]["categories"] == ["suicidal"]
    assert result["concerns"]["assessment_made"] is False
    assert result["concerns"]["text_copied"] is False
    assert "text" not in result["concerns"]["items"][0]
    assert result["risk_assessed"] is False
    assert result["need_assessed"] is False
    assert result["case_record_written"] is False


def test_an_unreadable_service_is_not_coerced():
    result, _payload = _draft(service="children-social-care")
    assert result["service"] is None
    assert result["service_unrecognised"] is True
    assert result["coerced"] is False


def test_duplicate_line_numbers_are_not_picked():
    result, _payload = _draft(lines=[
        {"n": 1, "speaker": "person", "audio": "clear", "text": "I want to stay in my own home."},
        {"n": 1, "speaker": "person", "audio": "clear", "text": "I want to leave tonight."},
    ])
    assert result["duplicate_lines"] == [1]
    assert result["statements"] == []
    assert result["unresolved_audio"][0]["duplicate"] is True
