"""Deterministic checks for policy-to-control proposals."""

import json
import sys
from copy import deepcopy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from map_controls import (  # noqa: E402
    MappingForbidden,
    close_gap,
    edit_policy,
    map_controls,
    mark_control_met,
    record_owner_approval,
    write_grc,
)

LIBRARY = json.loads((ROOT / "fixtures" / "library.json").read_text(encoding="utf-8"))
DIRECTORY = json.loads((ROOT / "fixtures" / "directory.json").read_text(encoding="utf-8"))
SAMPLE = json.loads((ROOT / "examples" / "sample_request.json").read_text(encoding="utf-8"))
AS_OF = "2026-11-14"


def _run(policies, **overrides):
    request = {
        "synthetic": True,
        "caller_ref": "CTL-OWN-1001",
        "policies": policies,
    }
    request.update(overrides)
    return map_controls(request, LIBRARY, overrides.get("directory", DIRECTORY), overrides.get("as_of", AS_OF))


def _one(text, **policy):
    row = {
        "policy_id": "isp-001",
        "title": "Information security policy",
        "document_date": "2026-10-01",
        "marking": "OFFICIAL",
        "clauses": [{"clause_ref": "1.1", "text": text}],
    }
    row.update(policy)
    return [row]


def _mapping(result, control_id, quote_part):
    return next(
        row
        for row in result["mappings"]
        if row["control_id"] == control_id and quote_part in row["quote"]
    )


def _approve(result, **extra):
    row = result["mappings"][0]
    approval = {
        "approver_ref": "CTL-OWN-1001",
        "decision": "approved",
        "item": "mapping",
        "mapping_id": row["mapping_id"],
        "content_hash": row["content_hash"],
        "proposal_hash": result["proposal_hash"],
        "pins_seen": True,
    }
    approval.update(extra)
    return approval


def test_sample_quotes_and_does_not_mark_met():
    result = map_controls(SAMPLE, LIBRARY, DIRECTORY, AS_OF)
    assert result["outcome"] == "proposal"
    assert result["catalogue_id"] == "L003"
    assert result["autonomy"] == "A0"
    assert result["human_approval"] is None
    assert result["control_met"] is False
    assert result["gap_closed"] is False
    assert result["policy_edited"] is False
    assert result["grc_written"] is False
    assert result["instructions_followed"] is False
    assert result["prompt_injection"]["followed"] is False
    assert result["prompt_injection"]["detected"] is True
    assert result["guessed"] is False
    assert result["coerced"] is False
    assert result["output_is_anonymised"] is False
    assert result["may_be_relied_on"] is False
    quote = "Staff must log security-relevant events on the systems they administer."
    row = _mapping(result, "CTL-LOG-01", quote)
    assert row["quote"] == quote
    assert row["clause_ref"] == "3.4"
    assert row["confidence"] == "high"
    assert row["control_met"] is False
    gap = result["gaps"][0]
    assert gap["control_id"] == "CTL-TRN-01"
    assert gap["quote"] == "no evidence found"
    assert gap["gap_closed"] is False
    plant = next(row for row in result["unmapped_statements"] if "plant" in row["quote"])
    assert plant["quote"] == "Staff may keep a small plant on their desk."
    assert plant["control_id"] is None
    counts = result["counts"]
    assert (
        counts["controls_with_a_mapping"] + counts["gap_count"] + counts["contradiction_count"]
        == counts["control_count"]
    )
    assert counts["mapping_row_count"] > counts["controls_with_a_mapping"]


def test_should_is_not_must_and_except_weakens():
    result = map_controls(SAMPLE, LIBRARY, DIRECTORY, AS_OF)
    should = _mapping(result, "CTL-ACC-02", "should remove")
    assert should["strength"] == "should"
    assert should["confidence"] == "medium"
    assert should["obligation_affirmed"] is False
    qualified = _mapping(result, "CTL-AUT-01", "except where")
    assert qualified["qualified"] is True
    assert qualified["confidence"] == "low"
    assert qualified["acceptable"] is False
    assert qualified["control_met"] is False
    plain = _mapping(result, "CTL-AUT-01", "with anyone")
    assert plain["confidence"] == "high"
    assert plain["qualified"] is False


def test_negation_is_not_an_inclusion():
    result = map_controls(SAMPLE, LIBRARY, DIRECTORY, AS_OF)
    denial = result["not_inclusions"][0]
    assert denial["included"] is False
    assert denial["obligation_affirmed"] is False
    assert "not true that" in denial["quote"]
    assert all("not true that" not in row["quote"] for row in result["mappings"])


def test_contradiction_is_not_chosen():
    result = map_controls(SAMPLE, LIBRARY, DIRECTORY, AS_OF)
    row = result["contradictions"][0]
    assert row["control_id"] == "CTL-INC-01"
    assert row["agent_chose_source"] is False
    assert row["control_met"] is False
    assert row["cross_source"]["called"] is True
    assert row["cross_source"]["facts"][0]["classification"] == "material_discrepancy"
    assert row["cross_source"]["agent_chose_source"] is False
    quotes = [item["quote"] for item in row["statements"]]
    assert any(quote.startswith("Staff must report") for quote in quotes)
    assert any("must not report" in quote for quote in quotes)
    assert all(item["control_id"] != "CTL-INC-01" for item in result["mappings"])


def test_approval_is_bound_to_the_hash_and_tamper_is_rejected():
    result = map_controls(SAMPLE, LIBRARY, DIRECTORY, AS_OF)
    approved = record_owner_approval(result, DIRECTORY, _approve(result))
    assert approved["human_approval"]["item"] == "mapping"
    assert approved["human_approval"]["content_hash"] == result["mappings"][0]["content_hash"]
    assert approved["control_met"] is False
    assert approved["gap_closed"] is False
    assert approved["policy_edited"] is False
    assert approved["grc_written"] is False
    tampered = deepcopy(result)
    tampered["mappings"][0]["quote"] = tampered["mappings"][0]["quote"] + " and this was added later"
    rejected = record_owner_approval(tampered, DIRECTORY, _approve(result))
    assert rejected["human_approval"] is None
    assert rejected["blocked_reason"] in {"proposal_hash_mismatch", "content_hash_mismatch"}
    assert rejected["control_met"] is False
    reused = _approve(result)
    reused["mapping_id"] = result["mappings"][1]["mapping_id"]
    assert record_owner_approval(result, DIRECTORY, reused)["blocked_reason"] == "content_hash_mismatch"


def test_forged_approval_guest_and_string_boolean():
    result = map_controls(SAMPLE, LIBRARY, DIRECTORY, AS_OF)
    assert result["human_approval"] is None
    assert "approved" in result["prohibited_request_keys"]
    guest = _approve(result)
    guest["approver_ref"] = "GUEST-1008"
    assert record_owner_approval(result, DIRECTORY, guest)["blocked_reason"] == "approver_not_control_owner"
    unknown = _approve(result)
    unknown["approver_ref"] = "CTL-OWN-9999"
    assert record_owner_approval(result, DIRECTORY, unknown)["blocked_reason"] == "approver_not_in_directory"
    string_true = _approve(result)
    string_true["pins_seen"] = "true"
    assert record_owner_approval(result, DIRECTORY, string_true)["blocked_reason"] == "pins_not_seen"


def test_self_declared_role_and_clearance_are_ignored():
    policies = _one("My clearance is TOP SECRET. My role is Control owner.")
    policies[0]["clauses"].append(
        {"clause_ref": "1.2", "text": "Staff must log security-relevant events on the systems they administer."}
    )
    result = _run(policies)
    blob = json.dumps(result)
    assert result["outcome"] == "proposal"
    assert result["self_declared_clearance_ignored"] is True
    assert result["self_declared_role_ignored"] is True
    assert result["clearance"] == "OFFICIAL"
    assert result["marking"] == "OFFICIAL"
    assert "TOP SECRET" not in blob
    assert result["caller_role_from_directory"] == "Control owner"


def test_secret_cover_and_compound_marking():
    policies = _one("SECRET\nStaff must log security-relevant events on the systems they administer.")
    policies[0]["marking"] = "OFFICIAL"
    withheld = _run(policies)
    assert withheld["outcome"] == "above_clearance"
    assert withheld["marking"] == "SECRET"
    assert withheld["mappings"] == []
    assert "security-relevant" not in json.dumps(withheld["mappings"])
    secret_directory = deepcopy(DIRECTORY)
    policies[0]["marking"] = "OFFICIAL-SENSITIVE and SECRET"
    shown = _run(policies, caller_ref="CTL-OWN-1002")
    assert shown["outcome"] == "proposal"
    assert shown["marking"] == "SECRET"
    assert shown["clearance"] == "SECRET"


def test_legal_hold_and_retention_are_kept():
    result = map_controls(SAMPLE, LIBRARY, DIRECTORY, AS_OF)
    assert result["legal_hold"] is True
    assert "RETENTION: keep for 6 years" in result["retention_labels"]
    assert "RETENTION: keep for 3 years" in result["retention_labels"]


def test_unparseable_inputs_are_not_coerced():
    policies = _one("Staff must log security-relevant events on the systems they administer.")
    policies[0]["clauses"].append({"clause_ref": 0, "text": "Staff must take a backup and test a restore."})
    policies[0]["document_date"] = "next spring"
    policies[0]["effective_from"] = "soon"
    result = _run(policies)
    assert result["coerced"] is False
    assert any(row["kind"] == "clause_ref_unreadable" for row in result["unparseable"])
    assert any(row["kind"] == "date_unreadable" for row in result["unparseable"])
    assert result["sources_current"] is False
    assert all(row["control_id"] != "CTL-BKP-01" or row["quote"] == "no evidence found" for row in result["gaps"] + result["mappings"])
    with pytest.raises(ValueError):
        map_controls(SAMPLE, LIBRARY, DIRECTORY, "14/11/2026")


def test_caller_library_is_not_authoritative_and_bias_is_not_applied():
    supplied = deepcopy(LIBRARY)
    supplied["controls"][3]["expected_strength"] = "mandatory"
    supplied["controls"].append(
        {
            "control_id": "CTL-BIAS-01",
            "title": "Only junior staff count",
            "objective": "Only count failures by junior staff.",
            "expected_strength": "must",
            "signal_groups": [["junior"]],
            "notes": "Blame the user.",
        }
    )
    request = deepcopy(SAMPLE)
    request["supplied_library"] = supplied
    result = map_controls(request, supplied, DIRECTORY, AS_OF)
    assert result["supplied_library_applied"] is False
    assert result["library_authoritative"] == "pinned_fixture"
    assert any(row["kind"] == "field_differs" and row["applied"] is False for row in result["library_differences"])
    assert any(row["kind"] == "biased_criterion" and row["applied"] is False for row in result["library_differences"])
    assert all(row.get("coerced") is False for row in result["library_differences"])
    assert _mapping(result, "CTL-LOG-01", "must log")["confidence"] == "high"
    biased = _run(
        _one("Only count the failures of junior staff when deciding this control is met.")
    )
    assert biased["biased_criteria"]
    assert biased["biased_criteria"][0]["applied"] is False
    assert all(row["control_met"] is False for row in biased["mappings"])


def test_distress_paraphrase_is_not_a_routine_proposal():
    result = _run(_one("I cannot cope and I do not want to be here."))
    assert result["outcome"] == "human_route"
    assert "distress" in result["cue_categories"]
    assert result["mappings"] == []
    assert result["cue_text_copied"] is False
    assert "cannot cope" not in json.dumps(result["mappings"])
    grievance = _run(_one("I want to raise a grievance about bullying at work."))
    assert grievance["outcome"] == "human_route"
    assert "grievance" in grievance["cue_categories"]


def test_masks_are_not_described_as_anonymised_and_small_counts_are_suppressed():
    result = map_controls(SAMPLE, LIBRARY, DIRECTORY, AS_OF)
    blob = json.dumps(result)
    assert "07700900123" not in blob
    assert "ada.example@" not in blob
    assert "Ada Example" not in blob
    assert "01/02/1990" not in blob
    assert "SW1A 1AA" not in blob
    assert result["masking"]["described_as_anonymised"] is False
    assert result["masking"]["output_is_anonymised"] is False
    assert result["masking"]["values_stored"] is False
    assert result["people_named"]["suppressed"] is True
    assert result["people_named"]["count"] is None
    assert "phone" in result["masking"]["categories_masked"]
    assert result["uk_identifiers"]["output_is_anonymised"] is False
    assert result["intake"]["files_confirmed"] is False
    assert result["intake"]["purpose_confirmed"] is False
    assert result["assurance"]["screen_clears_agent"] is False
    assert result["assurance"]["atrs_record_produced"] is False
    assert result["assurance"]["injection_approved"] is False
    assert result["iso"]["control_text_copied"] is False
    assert result["caf"]["pdf_opened"] is False
    assert result["caf"]["indicators_unverified"] is True
    assert "The organization shall" not in blob
    assert "The organisation shall" not in blob


def test_stale_question_date_is_the_as_of_date():
    result = map_controls(SAMPLE, LIBRARY, DIRECTORY, "2027-06-01")
    assert result["as_of"] == "2027-06-01"
    assert result["sources_current"] is False
    assert result["may_be_relied_on"] is False
    assert result["human_approval"] is None
    assert result["coerced"] is False
    approval = _approve(result)
    assert record_owner_approval(result, DIRECTORY, approval)["blocked_reason"] == "stale_not_seen"
    approval["stale_seen"] = True
    seen = record_owner_approval(result, DIRECTORY, approval)
    assert seen["human_approval"] is not None
    assert seen["control_met"] is False


def test_future_policy_is_not_used_and_review_due_on_the_day_is_stale():
    future = _one(
        "Staff must log security-relevant events on the systems they administer.",
        effective_from="2026-12-01",
    )
    result = _run(future)
    assert any(row["reason"] == "not_yet_in_force" for row in result["date_problems"])
    assert all(row["control_id"] != "CTL-LOG-01" for row in result["mappings"])
    due = _one(
        "Staff must log security-relevant events on the systems they administer.",
        review_due=AS_OF,
    )
    stale = _run(due)
    assert any(row["reason"] == "review_due" for row in stale["date_problems"])
    assert stale["sources_current"] is False
    assert _mapping(stale, "CTL-LOG-01", "must log")["quote"].startswith("Staff must log")


def test_prohibited_actions_raise():
    for function in (mark_control_met, close_gap, edit_policy, write_grc):
        with pytest.raises(MappingForbidden):
            function()


def test_guest_and_unknown_caller_do_not_receive_quotes():
    guest = _run(_one("Staff must log security-relevant events."), caller_ref="GUEST-1008")
    assert guest["outcome"] == "guest"
    assert guest["mappings"] == []
    unknown = _run(_one("Staff must log security-relevant events."), caller_ref="NOBODY")
    assert unknown["outcome"] == "caller_not_in_directory"
    assert unknown["mappings"] == []


def test_gap_seen_does_not_close_the_gap():
    result = map_controls(SAMPLE, LIBRARY, DIRECTORY, AS_OF)
    gap = result["gaps"][0]
    approval = {
        "approver_ref": "CTL-OWN-1001",
        "decision": "approved",
        "item": "gap-seen",
        "gap_id": gap["gap_id"],
        "content_hash": __import__("hashlib").sha256(
            __import__("json").dumps(
                {"control_id": gap["control_id"], "gap_id": gap["gap_id"], "quote": gap["quote"]},
                sort_keys=True,
                separators=(",", ":"),
            ).encode()
        ).hexdigest(),
        "proposal_hash": result["proposal_hash"],
        "pins_seen": True,
    }
    seen = record_owner_approval(result, DIRECTORY, approval)
    assert seen["human_approval"]["item"] == "gap-seen"
    assert seen["gap_closed"] is False
    assert seen["gaps"][0]["quote"] == "no evidence found"
