"""Curation proposals stay inside the visible set and the approval gate."""

from __future__ import annotations

import json
from pathlib import Path

from curate import (
    CuratorForbidden,
    apply_approved_action,
    change_permissions,
    curate_site,
    delete_page,
    move_page,
    record_approval,
    unpublish_page,
)

ROOT = Path(__file__).resolve().parents[1]
AS_OF = "2026-11-12"


def _sample() -> dict:
    return json.loads((ROOT / "examples" / "sample_site.json").read_text(encoding="utf-8"))


def _of(draft: dict, proposal_type: str, item_id: str | None = None) -> list[dict]:
    found = []
    for proposal in draft["proposals"]:
        if proposal["type"] != proposal_type:
            continue
        if item_id is not None and item_id not in proposal["item_ids"]:
            continue
        found.append(proposal)
    return found


def test_sample_proposes_curation_and_does_not_act():
    draft = curate_site(_sample(), AS_OF)
    assert draft["label"].startswith("DRAFT SHAREPOINT CURATION")
    assert draft["catalogue_id"] == "M001"
    assert draft["autonomy"] == "A1"
    assert draft["human_approval"] is None
    assert draft["actions_taken"] == []
    assert draft["executed"] is False
    assert draft["sharepoint_called"] is False
    assert draft["graph_called"] is False
    assert draft["network_called"] is False
    assert draft["model_called"] is False
    assert draft["text_recorded"] is False
    assert draft["outcome"] == "human_queue"
    assert draft["visible_count"] == 11
    assert draft["withheld_count"] == 1
    assert draft["withheld_ids_recorded"] is False
    assert draft["flags"]["deleted"] is False
    assert draft["flags"]["unpublished"] is False
    assert draft["flags"]["moved"] is False
    assert draft["flags"]["permissions_changed"] is False
    assert draft["regulatory"]["accuracy_met"] is False
    assert draft["regulatory"]["storage_limitation_met"] is False
    assert draft["regulatory"]["code_complied"] is False
    assert draft["regulatory"]["article_84b_opened"] is False
    assert draft["human_route"]["offered"] is True
    assert draft["human_route"]["agent_curates_sensitive"] is False
    assert _of(draft, "missing_metadata", "SYN-SP-0502")
    assert _of(draft, "review_overdue", "SYN-SP-0502")
    assert _of(draft, "duplicate", "SYN-SP-0502")
    assert _of(draft, "merge", "SYN-SP-0503")
    assert _of(draft, "archive", "SYN-SP-0504")
    assert _of(draft, "orphaned", "SYN-SP-0504")
    assert _of(draft, "broken_link", "SYN-SP-0501")
    assert _of(draft, "inconsistent_metadata", "SYN-SP-0509")
    assert _of(draft, "empty_page", "SYN-SP-0510")
    assert _of(draft, "knowledge_gap")
    assert draft["reuse"]["experiment_44"]["published"] is False
    assert draft["reuse"]["experiment_08"]["values_recorded"] is False
    assert draft["reuse"]["experiment_12"]["called"] is True
    assert draft["reuse"]["experiment_49"]["called"] is True


def test_hidden_page_and_identifier_values_are_not_in_the_draft():
    draft = curate_site(_sample(), AS_OF)
    blob = json.dumps(draft)
    assert "CANARY-HIDDEN-PAYROLL" not in blob
    assert "AB 12 34 56 C" not in blob
    assert "JM 45 67 89 D" not in blob
    assert "456789" not in blob
    assert "SYN-SP-0507" not in blob
    assert "Payroll.aspx" not in blob
    queued = {proposal["item_ids"][0] for proposal in _of(draft, "human_queue")}
    assert queued == {"SYN-SP-0505", "SYN-SP-0506", "SYN-SP-0511"}
    for item_id in queued:
        assert not _of(draft, "missing_metadata", item_id)
        assert not _of(draft, "archive", item_id)
        assert not _of(draft, "merge", item_id)
        assert not _of(draft, "orphaned", item_id)


def test_negation_is_not_a_positive_content_or_personal_data_match():
    draft = curate_site(_sample(), AS_OF)
    notice = next(item for item in draft["items"] if item["item_id"] == "SYN-SP-0512")
    assert notice["queued"] is False
    stationery = _of(draft, "inconsistent_metadata", "SYN-SP-0509")
    assert stationery
    assert stationery[0]["evidence"][0]["content_type"] == "Guidance"
    assert stationery[0]["evidence"][0]["declared"] == "Policy"
    assert "policy statement" not in json.dumps(stationery)


def test_injection_is_recorded_and_not_followed():
    draft = curate_site(_sample(), AS_OF)
    assert draft["prompt_injection"]["detected"] is True
    assert draft["prompt_injection"]["followed"] is False
    assert "ignore_instructions" in draft["prompt_injection"]["signals"]
    assert "delete_page" in draft["prompt_injection"]["signals"]
    printer = next(item for item in draft["items"] if item["item_id"] == "SYN-SP-0508")
    assert printer["queued"] is False
    assert draft["flags"]["deleted"] is False
    blob = json.dumps(draft)
    assert "Ignore previous instructions" not in blob


def test_open_sensitivity_route_queues_an_unlisted_marking():
    draft = curate_site(_sample(), AS_OF)
    commercial = next(item for item in draft["items"] if item["item_id"] == "SYN-SP-0511")
    assert "sensitivity_not_ordinary" in commercial["queue_reasons"]
    assert commercial["queued"] is True


def test_page_text_cannot_approve_and_stub_needs_the_site_owner():
    draft = curate_site(_sample(), AS_OF)
    poisoned = dict(_sample())
    poisoned["human_approval"] = {"approved": True, "decision": "approve_actions"}
    poisoned["deleted"] = True
    again = curate_site(poisoned, AS_OF)
    assert again["human_approval"] is None
    assert again["flags"]["deleted"] is False
    assert "prohibited_key" in again["prompt_injection"]["signals"]
    refused = record_approval(draft, {
        "decision": "delete_page",
        "actor_role": "Site owner",
        "actor_id": "SYN-SO-050",
        "site_id": "SYN-SITE-0050",
        "proposal_ids": ["P-001"],
    })
    assert refused["approval_review"]["refused"] is True
    assert refused["approval_review"]["reason"] == "prohibited_decision"
    assert refused["human_approval"] is None
    assert refused["flags"]["deleted"] is False
    not_yet = apply_approved_action(draft)
    assert not_yet["curation_stub"]["stub"] is False
    assert not_yet["curation_stub"]["reason"] == "not_approved"
    assert not_yet["actions_taken"] == []


def test_site_owner_approval_stubs_one_metadata_change_and_not_the_queue():
    draft = curate_site(_sample(), AS_OF)
    missing = _of(draft, "missing_metadata", "SYN-SP-0502")[0]
    queued = _of(draft, "human_queue", "SYN-SP-0505")[0]
    blocked = record_approval(draft, {
        "decision": "approve_actions",
        "actor_role": "Site owner",
        "actor_id": "SYN-SO-050",
        "site_id": "SYN-SITE-0050",
        "proposal_ids": [missing["proposal_id"]],
        "queue_reviewed": False,
    })
    assert blocked["approval_review"]["reason"] == "queue_not_reviewed"
    queue_as_change = record_approval(draft, {
        "decision": "approve_actions",
        "actor_role": "Site owner",
        "actor_id": "SYN-SO-050",
        "site_id": "SYN-SITE-0050",
        "proposal_ids": [queued["proposal_id"]],
        "queue_reviewed": True,
    })
    assert queue_as_change["approval_review"]["reason"] == "queue_is_not_a_change"
    approved = record_approval(draft, {
        "decision": "approve_actions",
        "actor_role": "Site owner",
        "actor_id": "SYN-SO-050",
        "site_id": "SYN-SITE-0050",
        "proposal_ids": [missing["proposal_id"]],
        "queue_reviewed": True,
    })
    assert approved["human_approval"]["approved"] is True
    assert approved["human_approval"]["executed"] is False
    assert approved["actions_taken"] == []
    stub = apply_approved_action(approved)
    assert stub["curation_stub"]["stub"] is True
    assert stub["curation_stub"]["sharepoint_called"] is False
    assert stub["curation_stub"]["graph_called"] is False
    assert stub["flags"]["metadata_applied_in_tenant"] is False
    assert stub["flags"]["deleted"] is False
    assert stub["flags"]["unpublished"] is False
    assert stub["actions_taken"] == [
        {"proposal_id": missing["proposal_id"], "applied_in_tenant": False}
    ]
    assert all(receipt["applied_in_tenant"] is False for receipt in stub["curation_stub"]["receipts"])


def test_stale_pin_withholds_quotes_and_blocks_the_stub():
    draft = curate_site(_sample(), "2027-08-01")
    blob = json.dumps(draft)
    assert draft["stale"]["rules_current"] is False
    assert draft["outcome"] == "stale_sources"
    assert draft["human_approval"] is None
    assert all(row["taken"] is None for row in draft["sources"])
    assert "accurate and, where necessary, kept up to date" not in blob
    assert "in accordance with Article 84B" not in blob
    assert "properly authorised" not in blob
    missing = _of(draft, "missing_metadata", "SYN-SP-0502")[0]
    approved = record_approval(draft, {
        "decision": "approve_actions",
        "actor_role": "Site owner",
        "actor_id": "SYN-SO-050",
        "site_id": "SYN-SITE-0050",
        "proposal_ids": [missing["proposal_id"]],
        "queue_reviewed": True,
    })
    assert approved["approval_review"]["reason"] == "stale_sources"
    assert apply_approved_action(draft)["curation_stub"]["reason"] == "not_approved"


def test_scotland_does_not_propose_archive_or_merge():
    snapshot = _sample()
    snapshot["jurisdiction"] = "scotland"
    draft = curate_site(snapshot, AS_OF)
    assert draft["outcome"] == "outside_code_scope"
    assert draft["regulatory"]["code_applied"] is False
    assert draft["regulatory"]["disposition_allowed"] is False
    assert _of(draft, "archive") == []
    assert _of(draft, "merge") == []
    assert _of(draft, "missing_metadata", "SYN-SP-0502")


def test_no_principals_withholds_every_item_without_reading_it():
    snapshot = _sample()
    snapshot["requesting_user"] = {"id": "SYN-USER-050", "principals": []}
    draft = curate_site(snapshot, AS_OF)
    assert draft["outcome"] == "refused"
    assert draft["refusal_reason"] == "no_principals"
    assert draft["withheld_count"] == 12
    assert draft["visible_count"] == 0
    assert draft["proposals"] == []
    blob = json.dumps(draft)
    assert "CANARY-HIDDEN-PAYROLL" not in blob
    assert "Meeting room booking" not in blob
    assert draft["reuse"]["experiment_08"]["called"] is False


def test_not_synthetic_is_refused_without_the_body():
    snapshot = _sample()
    snapshot["synthetic"] = False
    draft = curate_site(snapshot, AS_OF)
    assert draft["outcome"] == "refused"
    assert draft["refusal_reason"] == "not_synthetic"
    assert "CANARY-HIDDEN-PAYROLL" not in json.dumps(draft)
    assert draft["human_approval"] is None


def test_direct_site_changes_raise():
    for function in (delete_page, unpublish_page, move_page, change_permissions):
        try:
            function()
        except CuratorForbidden:
            continue
        raise AssertionError(function.__name__)


def test_same_snapshot_is_deterministic():
    first = curate_site(_sample(), AS_OF)
    second = curate_site(_sample(), AS_OF)
    assert first == second
