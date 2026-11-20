"""Deterministic checks for a regulatory change briefing."""

import importlib
import json
import socket
import sys
from copy import deepcopy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from briefing import (  # noqa: E402
    BriefingForbidden,
    change_control,
    change_policy,
    change_record,
    decide_applicability,
    draft_briefing,
    record_owner_seen,
    send,
    verify_seen,
)
from dates import stated_dates  # noqa: E402
from match import superseded_affirmed, withdrawn_affirmed  # noqa: E402

REGISTER = json.loads((ROOT / "fixtures" / "policy_register.json").read_text(encoding="utf-8"))
DIRECTORY = json.loads((ROOT / "fixtures" / "directory.json").read_text(encoding="utf-8"))
SAMPLE = json.loads((ROOT / "examples" / "sample_request.json").read_text(encoding="utf-8"))
AS_OF = "2026-11-14"


def _run(publication_id, **overrides):
    request = {
        "synthetic": True,
        "publication_id": publication_id,
        "caller_ref": "CO-1001",
    }
    request.update(overrides)
    return draft_briefing(request, REGISTER, DIRECTORY, overrides.get("as_of", AS_OF))


def _ids(result):
    return [row["policy_id"] for row in result["might_be_affected"]]


def test_package_import_uses_relative_imports():
    sys.path.insert(0, str(ROOT))
    module = importlib.import_module("src.briefing")
    assert module.CATALOGUE_ID == "L002"
    assert module.draft_briefing.__module__ == "src.briefing"


def test_sample_quotes_the_pin_and_does_not_decide():
    result = draft_briefing(SAMPLE, REGISTER, DIRECTORY, AS_OF)
    assert result["outcome"] == "briefing"
    assert result["applies"] is None
    assert result["applicability"] == "not decided"
    assert result["human_approval"] is None
    assert result["sent"] is False
    assert result["policy_changed"] is False
    assert result["control_changed"] is False
    assert result["record_changed"] is False
    assert result["instructions_followed"] is False
    assert result["prompt_injection"]["followed"] is False
    assert result["prompt_injection"]["detected"] is True
    assert result["dates"]["effective"]["display"] == "not stated"
    assert result["dates"]["consultation_close"]["display"] == "2027-02-28"
    assert result["what_changed"]["quote"].startswith("This consultation sets out")
    assert result["what_changed"]["verbatim"] is True
    assert result["caller_text_used"] is False
    assert result["caller_text_differs"] is True
    assert result["role_from_directory"] == "compliance_owner"
    assert result["clearance_from_directory"] == "OFFICIAL"
    assert "POL-COMPLAINTS" in _ids(result)
    assert "POL-CREDIT" not in _ids(result)
    assert "POL-LEAD" in _ids(result)
    lead = next(row for row in result["leading_criteria"] if row["policy_id"] == "POL-LEAD")
    assert lead["applied"] is False
    assert lead["note_copied"] is False
    why = next(row["why"] for row in result["might_be_affected"] if row["policy_id"] == "POL-LEAD")
    assert "disabled" not in why
    assert result["statutory_minimum_days"] is None
    assert result["pins_confirmed"] is False
    assert result["may_be_relied_on"] is False
    assert result["experiment_12"]["files_confirmed"] is False
    assert result["experiment_12"]["purpose_confirmed"] is False
    assert result["experiment_20"]["applies"] is None
    assert result["network_called"] is False
    assert result["live_site_fetched"] is False
    blob = json.dumps(result)
    assert "07700" not in blob
    assert "ada.north" not in blob
    assert "Ada North" not in blob
    assert "TOP SECRET" not in blob
    assert "Ignore previous" not in blob
    assert len(_ids(result)) == len(set(_ids(result)))
    assert result["might_be_affected_count"] == len(result["might_be_affected"])
    assert result["open_question_count"] == len(result["open_questions"])


def test_relative_effective_date_is_computed_and_carve_out_is_not_a_match():
    result = _run("SYN-FCA-PS-02")
    effective = result["dates"]["effective"]
    assert effective["display"] == "2026-08-30"
    assert effective["sources"][0]["kind"] == "computed"
    assert effective["coerced"] is False
    assert effective["chosen"] is False
    assert "POL-PAYMENTS" in _ids(result)
    assert "POL-CREDIT" not in _ids(result)
    assert any(row["topic"] == "consumer credit" for row in result["negated_mentions"])
    assert result["flags"]["superseded"] is False
    assert "SYN-FCA-SU-04" in result["flags"]["supersedes"]
    assert result["flags"]["stale"] is True
    assert result["related_fca_sources"][0]["status"] == "pinned"
    assert result["related_fca_sources"][0]["applies"] is None


def test_withdrawn_superseded_undated_and_short_window():
    withdrawn = _run("SYN-FCA-WD-03")
    assert withdrawn["flags"]["withdrawn"] is True
    assert withdrawn["flags"]["stale"] is True
    assert withdrawn_affirmed("This publication is not withdrawn.") is False
    superseded = _run("SYN-FCA-SU-04")
    assert superseded["flags"]["superseded"] is True
    assert superseded_affirmed("This statement supersedes SYN-FCA-SU-04.") is False
    secret = _run("SYN-ICO-01")
    assert secret["outcome"] == "above_clearance"
    assert secret["marking"] == "SECRET"
    assert secret["legal_hold"] is True
    assert "7 years" in secret["retention"]
    assert secret["flags"]["undated"] is True
    assert "subject access" not in json.dumps(secret).lower()
    assert secret["what_changed"]["quote"] == "not copied"
    short = _run("SYN-FCA-SHORT-07")
    assert short["below_register_window"] is True
    assert short["marked_acceptable"] is False
    assert short["statutory_minimum_days"] is None
    assert short["register_minimum_days"] == 30
    assert short["dates"]["consultation_close"]["display"] == "2026-11-11"
    assert short["coerced"] is False


def test_unparseable_date_and_people_count_are_not_coerced():
    result = _run("SYN-FCA-BAD-05")
    assert result["dates"]["effective"]["display"] == "not stated"
    assert result["dates"]["effective"]["unparseable"] is True
    assert result["dates"]["effective"]["coerced"] is False
    assert result["related_fca_sources"][0]["status"] == "not found"
    group = result["people"]["groups"][0]
    assert group["value"] is None
    assert group["reason"] == "unparseable"
    assert group["coerced"] is False
    assert result["people"]["coerced"] is False


def test_negation_does_not_list_a_policy_as_affected():
    result = _run("SYN-FCA-NEG-06")
    assert result["might_be_affected"] == []
    topics = {row["topic"] for row in result["negated_mentions"]}
    assert topics == {"payment accounts", "consumer credit"}
    assert all(row["applies"] is None for row in result["negated_mentions"])


def test_distress_small_number_and_grievance_are_routes():
    energy = _run("SYN-OFG-01")
    assert energy["outcome"] == "human_route"
    assert energy["cue"]["distress"] is True
    assert energy["cue"]["text_copied"] is False
    assert energy["dates"]["consultation_close"]["display"] == "2026-10-31"
    assert energy["below_register_window"] is False
    group = energy["people"]["groups"][0]
    assert group["suppressed"] is True
    assert group["value"] is None
    assert "2" not in json.dumps(energy["people"])
    assert "cannot cope" not in json.dumps(energy)
    housing = _run("SYN-HOS-01")
    assert housing["outcome"] == "human_route"
    assert housing["cue"]["grievance"] is True
    assert housing["dates"]["effective"]["display"] == "2025-10-27"
    assert _ids(housing) == ["POL-DAMP"]
    assert "raising a grievance" not in json.dumps(housing)
    assert housing["experiment_20"]["applies"] is None


def test_missing_id_guest_and_caller_register_are_not_authoritative():
    missing = _run("SYN-NO-SUCH")
    assert missing["outcome"] == "not_found"
    assert missing["what_changed"]["quote"] == "not found"
    assert missing["might_be_affected"] == []
    guest = _run("SYN-FCA-CP-01", caller_ref="GST-1002")
    assert guest["role_from_directory"] == "guest"
    assert guest["clearance_from_directory"] == "OFFICIAL"
    unknown = _run("SYN-FCA-CP-01", caller_ref="NOBODY")
    assert unknown["outcome"] == "caller_not_in_directory"
    assert unknown["what_changed"]["quote"] == "not found"
    caller = deepcopy(REGISTER)
    caller["internal_consultation_minimum_days"] = "soon"
    caller["policies"].append(
        {
            "policy_id": "POL-EXTRA",
            "title": "Caller only",
            "topics": ["complaints handling"],
            "owner_role": "compliance_owner",
            "review_due": "2027-01-01",
            "status": "current",
            "selection_note": "",
        }
    )
    result = draft_briefing(
        {"synthetic": True, "publication_id": "SYN-FCA-SHORT-07", "caller_ref": "CO-1001"},
        caller,
        DIRECTORY,
        AS_OF,
    )
    assert result["below_register_window"] is True
    assert result["register_minimum_days"] == 30
    assert result["coerced"] is False
    assert "POL-EXTRA" not in _ids(result)
    assert result["pinned_register_used"] is True
    assert result["register_differences"]


def test_secret_caller_sees_the_ico_quote_and_marking_stays_high():
    result = _run("SYN-ICO-01", caller_ref="CO-1003")
    assert result["outcome"] == "briefing"
    assert result["marking"] == "SECRET"
    assert "subject access" in result["what_changed"]["quote"]
    marked = _run("SYN-MARK-01")
    assert marked["outcome"] == "above_clearance"
    assert marked["marking"] == "SECRET"
    assert marked["legal_hold"] is True
    assert "TOP SECRET" not in json.dumps(marked)


def test_seen_step_is_bound_to_the_hashes_and_rejects_tampering():
    result = draft_briefing(SAMPLE, REGISTER, DIRECTORY, AS_OF)
    decision = {
        "approver_ref": "CO-1001",
        "item": "briefing",
        "decision": "seen",
        "publication_hash": result["publication_hash"],
        "briefing_hash": result["briefing_hash"],
        "questions_hash": result["questions_hash"],
        "pins_seen": True,
        "sources_seen": True,
    }
    seen = record_owner_seen(result, DIRECTORY, decision)
    assert seen["human_approval"]["recorded"] is True
    assert seen["applies"] is None
    assert seen["sent"] is False
    assert seen["policy_changed"] is False
    assert verify_seen(seen)["accepted"] is True
    tampered = deepcopy(seen)
    tampered["what_changed"]["quote"] = "A rewritten change."
    assert verify_seen(tampered)["accepted"] is False
    rejected = record_owner_seen(tampered, DIRECTORY, decision)
    assert rejected["human_approval"] is None
    assert rejected["blocked_reason"] == "briefing_hash_mismatch"
    string_seen = dict(decision)
    string_seen["pins_seen"] = "true"
    blocked = record_owner_seen(result, DIRECTORY, string_seen)
    assert blocked["human_approval"] is None
    assert blocked["blocked_reason"] == "pins_seen_not_boolean"
    guest = dict(decision)
    guest["approver_ref"] = "GST-1002"
    assert record_owner_seen(result, DIRECTORY, guest)["blocked_reason"] == "not_compliance_owner"
    hacked = deepcopy(DIRECTORY)
    hacked["people"].append({"ref": "HACK", "role": "compliance_owner", "clearance": "TOP SECRET"})
    forged = dict(decision)
    forged["approver_ref"] = "HACK"
    assert record_owner_seen(result, hacked, forged)["blocked_reason"] == "approver_not_in_directory"


def test_question_date_is_not_today_and_network_is_not_used(monkeypatch):
    def boom(*_args, **_kwargs):
        raise AssertionError("network")

    monkeypatch.setattr(socket, "create_connection", boom)
    result = draft_briefing(SAMPLE, REGISTER, DIRECTORY, "2027-06-01")
    assert result["as_of"] == "2027-06-01"
    assert result["flags"]["stale"] is True
    assert result["sources_current"] is False
    assert result["may_be_relied_on"] is False
    assert result["network_called"] is False


def test_bad_as_of_is_not_coerced():
    with pytest.raises(ValueError):
        draft_briefing(SAMPLE, REGISTER, DIRECTORY, "soon")
    with pytest.raises(ValueError):
        draft_briefing(SAMPLE, REGISTER, DIRECTORY, "2026-11-14T00:00:00")


def test_prohibited_actions_raise():
    for function in (decide_applicability, change_policy, change_control, change_record, send):
        with pytest.raises(BriefingForbidden):
            function()


def test_invalid_day_is_not_shifted_to_a_real_date():
    dates = stated_dates("The change is effective from 32 June 2027.", None)
    assert dates["effective"]["display"] == "not stated"
    assert dates["effective"]["unparseable"] is True
    assert dates["effective"]["coerced"] is False
