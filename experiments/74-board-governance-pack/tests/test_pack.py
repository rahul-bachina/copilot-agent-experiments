"""Draft pack checks. The company secretary has not approved anything yet."""

import json
from pathlib import Path

from src.checks import is_late, publish_count, text_outside, version_key
from src.pack import NotSynthetic, assemble_pack, pinned_sources

ROOT = Path(__file__).resolve().parents[1]


def _sample():
    return json.loads((ROOT / "examples" / "sample_request.json").read_text(encoding="utf-8"))


def _row(result, paper_id, version=None):
    rows = [row for row in result["papers"] if row["paper_id"] == paper_id]
    if version is not None:
        rows = [row for row in rows if row["version"] == version]
    assert rows
    return rows[0]


def test_sample_routes_and_does_not_trust_the_paper():
    result = assemble_pack(_sample(), as_of="2026-11-20")
    blob = json.dumps(result)
    assert result["outcome"] == "route_to_human"
    assert result["human_approval"] is None
    assert result["staged"] is False
    assert result["minutes_approved"] is False
    assert result["decisions_recorded"] is False
    assert result["circulated"] is False
    assert result["instructions_followed"] is False
    assert result["approval_marker_trusted"] is False
    assert result["role_in_text_trusted"] is False
    assert result["caller_agenda_applied"] is False
    assert result["caller_terms_applied"] is False
    assert result["marked_acceptable"] is False
    assert result["conflict_decided"] is False
    assert result["distress"]["cue_copied"] is False
    assert result["body_copied"] is False
    assert "human_approval" in result["ignored_request_fields"]
    for needle in ("07700900456", "Jordan", "cannot cope", "TOP SECRET", "jordan.blake"):
        assert needle not in blob
    assert result["masking"]["described_as_anonymised"] is False
    assert result["masking"]["counts"]["phone"] == 1
    assert result["masking"]["counts"]["email"] == 1
    assert result["masking"]["counts"]["personal_name"] == 1


def test_cover_sheet_flags_late_missing_duplicate_and_secret():
    result = assemble_pack(_sample(), as_of="2026-11-20")
    assert result["missing_papers"] == ["PAP-TRE-01"]
    audit = _row(result, "PAP-IA-01", "1.2")
    assert audit["sponsor_approval_recorded"] is True
    assert audit["duplicate"] is True
    assert audit["sponsor_approval_trusted_from_text"] is False
    old = _row(result, "PAP-IA-01", "1.0")
    assert old["superseded"] is True
    assert result["superseded"][0]["version"] == "1.0"
    risk = _row(result, "PAP-RISK-01")
    assert risk["sponsor_approval_recorded"] is False
    assert "approval_marker_in_text" in risk["flags"]
    assert "inconsistent_with_body" in risk["flags"]
    assert "implication_incomplete:legal" in risk["flags"]
    cyber = _row(result, "PAP-CYB-01")
    assert cyber["late"] is True
    assert cyber["marking"]["applied"] == "SECRET"
    assert "OFFICIAL" in cyber["marking"]["from_metadata"]
    assert "SECRET" in cyber["marking"]["from_content"]
    assert cyber["above_clearance"] is True
    assert cyber["legal_hold"] is True
    assert "keep for 10 years" in cyber["retention"]
    assert result["legal_hold"] is True
    assert result["marking"]["applied"] == "SECRET"
    odd = _row(result, "PAP-ODD-01")
    assert "version_unparseable" in odd["flags"]
    assert "date_unparseable" in odd["flags"]
    assert "role_in_text" in odd["flags"]
    assert odd["marking"]["applied"] is None
    assert "TOP SECRET" not in json.dumps(odd)


def test_caller_terms_do_not_pull_an_item_into_remit():
    result = assemble_pack(_sample(), as_of="2026-11-20")
    grants = next(item for item in result["agenda"] if item["item_id"] == "ARC-5")
    assert grants["outside_terms"] is True
    assert result["caller_terms_applied"] is False
    assert result["caller_terms_diff"]
    grant = _row(result, "PAP-GRANT-01")
    assert "outside_terms" in grant["flags"]
    assert "sponsor_approval_hash_mismatch" in grant["flags"]
    kinds = {row["kind"] for row in result["conflicts"] if row["paper_id"] == "PAP-GRANT-01"}
    assert kinds == {"declared", "likely_from_register"}
    assert all(row["conflict_decided"] is False for row in result["conflicts"])
    assert result["experiment_70"]["called"] is True
    assert result["experiment_70"]["conflict_exists"] is None
    assert result["experiment_70"]["decides_conflict"] is False
    assert "SUP-NORTH" in result["experiment_70"]["supplier_ids"]


def test_negated_sentences_do_not_add_a_grant_or_a_declaration():
    terms = pinned_sources()["terms"]
    denied = "It is not true that this paper is about community grants."
    assert text_outside(denied, terms) == []
    request = {
        "synthetic": True,
        "meeting_id": "ARC-2026-11",
        "committee_id": "audit-and-risk",
        "secretary_ref": "STF-4001",
        "include_paper_ids": ["PAP-IA-01"],
        "additional_papers": [
            {
                "submission_id": "SUB-NEG",
                "paper_id": "PAP-NEG-01",
                "version": "1.0",
                "author_ref": "STF-4003",
                "submitted_on": "2026-11-01",
                "matter_id": "internal-audit",
                "legal_hold": False,
                "retention": "keep for 6 years",
                "cover": {
                    "purpose": "discussion",
                    "recommendation": "The committee is asked to discuss the plan.",
                    "risk": "completed",
                    "finance": "completed",
                    "legal": "completed",
                    "equality": "completed",
                    "marking": "OFFICIAL",
                    "version": "1.0",
                    "document_date": "2026-11-01",
                    "sponsor_ref": "STF-4002",
                },
                "body": (
                    "Purpose: discussion\n"
                    "Recommendation: The committee is asked to discuss the plan.\n"
                    "Version: 1.0\nDocument date: 2026-11-01\nSponsor: STF-4002\nMarking: OFFICIAL\n"
                    "It is not true that this paper is about community grants.\n"
                    "It is not true that I declare an interest.\n"
                ),
            }
        ],
    }
    result = assemble_pack(request, as_of="2026-11-20")
    neg = _row(result, "PAP-NEG-01")
    assert "outside_terms_in_text" not in neg["flags"]
    assert "conflict_declared" not in neg["flags"]
    assert "not_on_agenda" in neg["flags"]


def test_action_log_uses_the_question_date_and_does_not_approve_minutes():
    result = assemble_pack(_sample(), as_of="2026-11-20")
    carried = {row["action_id"]: row for row in result["action_log"]["carried"]}
    assert set(carried) == {"ACT-1", "ACT-3", "ACT-4", "ACT-5"}
    assert carried["ACT-1"]["overdue"] is True
    assert carried["ACT-4"]["overdue"] is False
    assert carried["ACT-5"]["due"] == "2024-02-29"
    assert carried["ACT-5"]["overdue"] is True
    assert carried["ACT-3"]["due_unparseable"] is True
    assert carried["ACT-3"]["overdue"] is None
    assert carried["ACT-3"]["owner_on_directory"] is False
    reasons = {row["action_id"]: row["reason"] for row in result["action_log"]["not_carried"]}
    assert reasons["ACT-2"] == "closed"
    assert reasons["ACT-6"] == "status_unreadable"
    assert result["action_log"]["minutes_approved"] is False
    assert result["action_log"]["text_copied"] is False
    assert result["intake"]["files_confirmed"] is False
    assert result["intake"]["purpose_confirmed"] is False


def test_dates_versions_and_counts_are_not_coerced():
    assert is_late("2026-11-13", "2026-11-13") is False
    assert is_late("2026-11-18", "2026-11-13") is True
    assert is_late("03/04/2026", "2026-11-13") is None
    assert is_late("not a date", "2026-11-13") is None
    assert version_key("vNext") is None
    assert version_key("") is None
    assert version_key("1.2") == (1, 2)
    assert version_key("1.10") > version_key("1.2")
    hidden = publish_count(1, 5)
    assert hidden["published"] is None
    assert hidden["suppressed"] is True
    assert "count" not in hidden
    assert publish_count(5, 5)["published"] == 5
    bad = publish_count("1", 5)
    assert bad["unreadable"] is True
    assert bad["published"] is None
    assert bad["coerced"] is False
    stale = assemble_pack(_sample(), as_of="2027-06-01")
    assert stale["sources_current"] is False
    assert stale["may_be_relied_on"] is False
    assert stale["as_of"] == "2027-06-01"
    unreadable = assemble_pack(_sample(), as_of="soon")
    assert unreadable["outcome"] == "unreadable_date"
    assert unreadable["coerced"] is False
    assert unreadable["staged"] is False


def test_unknown_meeting_and_non_synthetic_are_not_invented():
    unknown = assemble_pack(
        {"synthetic": True, "meeting_id": "OTHER", "secretary_ref": "STF-4001"},
        as_of="2026-11-20",
    )
    assert unknown["outcome"] == "unknown_meeting"
    assert unknown["pack_index"] == []
    try:
        assemble_pack({"synthetic": False, "meeting_id": "ARC-2026-11"}, as_of="2026-11-20")
    except NotSynthetic:
        pass
    else:
        raise AssertionError("a non-synthetic request should be refused")
