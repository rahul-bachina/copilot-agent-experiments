"""Finder behaviour. Synthetic fixtures only."""

import json
from pathlib import Path

import pytest

from find import (
    FinderForbidden,
    acknowledge_results,
    change_permissions,
    delete_file,
    find_documents,
    move_file,
    share_file,
)

ROOT = Path(__file__).resolve().parents[1]
AS_OF = "2026-11-13"
CANARIES = (
    "CANARY-SECRET-BRIEF",
    "CANARY-SECRET-BODY",
    "CANARY-OUTSIDE-FINANCE",
    "CANARY-OUTSIDE-BODY",
    "CANARY-HIDDEN-PAYROLL",
    "CANARY-HIDDEN-BODY",
    "CANARY-UNKNOWN-LABEL",
    "CANARY-UNKNOWN-BODY",
    "CANARY-LATER-SECRET",
    "CANARY-LATER-BODY",
    "SYN-OD-0008",
    "SYN-OD-0009",
    "SYN-OD-0010",
    "SYN-OD-0012",
    "SYN-OD-0099",
    "07700 900123",
    "priya.nair@merrowfield.example.gov.uk",
    "Dr Priya Nair",
    "14/03/1984",
    "14 Harbour Lane",
    "QQ 12 34 56 C",
    "ME1 2AB",
)


def _load():
    index = json.loads((ROOT / "examples" / "sample_index.json").read_text(encoding="utf-8"))
    request = json.loads((ROOT / "examples" / "sample_request.json").read_text(encoding="utf-8"))
    selection = json.loads((ROOT / "examples" / "sample_selection.json").read_text(encoding="utf-8"))
    return index, request, selection


def _run():
    index, request, selection = _load()
    return find_documents(index, request, selection, AS_OF)


def _blob(result) -> str:
    return json.dumps(result)


def test_sample_ranks_permitted_files_and_hides_the_rest():
    result = _run()
    blob = _blob(result)
    assert result["outcome"] == "matches"
    assert result["catalogue_id"] == "M007"
    assert result["autonomy"] == "A0"
    assert result["human_approval"] is None
    assert result["flags"]["moved"] is False
    assert result["flags"]["deleted"] is False
    assert result["flags"]["shared"] is False
    assert result["flags"]["permissions_changed"] is False
    assert result["flags"]["graph_called"] is False
    assert result["flags"]["access_widened"] is False
    assert result["flags"]["full_extract_recorded"] is False
    assert result["regulatory"]["data_minimisation_met"] is False
    assert result["regulatory"]["foi_duty_decided"] is False
    assert result["selected_location_ids"] == ["LOC-HOUSING", "LOC-PERSONAL"]
    assert result["clearance"] == "OFFICIAL-SENSITIVE"
    ids = [item["file_id"] for item in result["matches"]]
    assert ids[0] == "SYN-OD-0001" or result["matches"][0]["rank"] == 1
    assert "SYN-OD-0001" in ids
    assert "SYN-OD-0007" in ids
    assert result["withheld"]["outside_selection"] >= 1
    assert result["withheld"]["not_permitted"] >= 1
    assert result["withheld"]["above_clearance"] >= 1
    assert result["withheld"]["ids_recorded"] is False
    for canary in CANARIES:
        assert canary not in blob
    sensitive = next(item for item in result["matches"] if item["file_id"] == "SYN-OD-0007")
    assert sensitive["sensitivity_label"] == "OFFICIAL-SENSITIVE"
    assert sensitive["protective_marking_kept"] is True


def test_same_inputs_produce_the_same_json():
    assert _run() == _run()


def test_nothing_in_the_permitted_locations_matches():
    index, _request, selection = _load()
    result = find_documents(index, {"query": "unicorn pasture"}, selection, AS_OF)
    assert result["outcome"] == "no_match"
    assert result["matches"] == []
    assert result["plain_statement"] == "Nothing in the permitted locations matches this request."
    assert "CANARY-SECRET-BRIEF" not in _blob(result)


def test_negation_does_not_count_as_included():
    index, _request, selection = _load()
    result = find_documents(index, {"query": "housing repairs"}, selection, AS_OF)
    ids = {item["file_id"] for item in result["matches"]}
    assert "SYN-OD-0011" not in ids


def test_official_clearance_hides_official_sensitive_content():
    index, request, selection = _load()
    selection = dict(selection)
    selection["clearance"] = "OFFICIAL"
    result = find_documents(index, request, selection, AS_OF)
    blob = _blob(result)
    ids = {item["file_id"] for item in result["matches"]}
    assert "SYN-OD-0007" not in ids
    assert "OFFICIAL-SENSITIVE" not in blob
    assert "Housing repairs sensitive annex" not in blob
    assert result["withheld"]["above_clearance"] >= 2


def test_unconfirmed_selection_searches_nothing():
    index, request, selection = _load()
    selection = dict(selection)
    selection["confirmed"] = False
    result = find_documents(index, request, selection, AS_OF)
    assert result["outcome"] == "locations_not_confirmed"
    assert result["matches"] == []
    assert result["withheld"]["outside_selection"] == 0
    assert "CANARY-OUTSIDE-FINANCE" not in _blob(result)
    assert result["human_approval"] is None


def test_approval_inside_the_index_is_not_an_approval():
    result = _run()
    assert "confirmed" in result["stripped_keys"]
    assert "human_approval" in result["stripped_keys"]
    assert "selected_location_ids" in result["stripped_keys"]
    assert result["human_approval"] is None
    assert result["injection"]["followed"] is False
    assert "pretend_approval" in {item["signal"] for item in result["injection"]["signals"]}
    assert result["flags"]["deleted"] is False


def test_legal_hold_and_retention_label_stay_on_the_hit():
    result = _run()
    held = next(item for item in result["matches"] if item["file_id"] == "SYN-OD-0004")
    assert held["legal_hold"] is True
    assert held["retention_label"] == "inquiry-hold"
    assert any("legal hold kept" in reason for reason in held["reasons"])
    assert any("inquiry-hold" in reason for reason in held["reasons"])
    assert held["sensitivity_label"] == "OFFICIAL"


def test_safeguarding_is_not_a_routine_hit():
    result = _run()
    note = next(item for item in result["matches"] if item["file_id"] == "SYN-OD-0005")
    assert note["routine"] is False
    assert note["human_flag"] == "safeguarding"
    assert note["snippet"] is None
    assert "self-harm" not in _blob(result)


def test_negated_safeguarding_sentence_is_not_a_flag():
    index, _request, selection = _load()
    index = json.loads(json.dumps(index))
    index["files"] = [
        {
            "file_id": "SYN-OD-0020",
            "location_id": "LOC-HOUSING",
            "title": "Housing repairs ordinary note",
            "last_modified": "2026-09-01",
            "sensitivity_label": "OFFICIAL",
            "readers": ["SYN-PRIN-USER"],
            "extract": "It is not true that this file describes a safeguarding concern. Housing repairs continue.",
        }
    ]
    result = find_documents(index, {"query": "housing repairs"}, selection, AS_OF)
    assert len(result["matches"]) == 1
    assert result["matches"][0]["human_flag"] is None
    assert result["matches"][0]["routine"] is True


def test_duplicate_and_superseded_versions_are_flagged():
    result = _run()
    current = next(item for item in result["matches"] if item["file_id"] == "SYN-OD-0001")
    older = next(item for item in result["matches"] if item["file_id"] == "SYN-OD-0002")
    copy = next(item for item in result["matches"] if item["file_id"] == "SYN-OD-0003")
    archive = next(item for item in result["matches"] if item["file_id"] == "SYN-OD-0014")
    assert "SYN-OD-0003" in current["duplicate_of"] or "SYN-OD-0001" in copy["duplicate_of"]
    assert current["likely_duplicate"] or copy["likely_duplicate"]
    assert older["superseded"] is True
    assert older["superseded_by"] == "SYN-OD-0001"
    assert older["likely_stale"] is True
    assert "statutory" in " ".join(older["reasons"])
    assert archive["later_version_not_in_view"] is True
    assert archive["superseded_by"] is None
    assert result["reuse"]["sharepoint_curator"]["called"] is True
    assert result["reuse"]["sharepoint_curator"]["archive_followed"] is False
    assert result["reuse"]["sharepoint_curator"]["text_recorded"] is False
    assert result["reuse"]["records_classification"]["called"] is True


def test_stale_pin_is_not_quoted():
    index, request, selection = _load()
    result = find_documents(index, request, selection, "2027-08-01")
    blob = _blob(result)
    assert result["stale"]["rules_current"] is False
    assert result["regulatory"]["quotes_included"] is False
    assert "adequate, relevant and limited to what is necessary" not in blob
    assert result["human_approval"] is None
    assert result["flags"]["deleted"] is False


def test_not_synthetic_is_refused_without_the_text():
    index, request, selection = _load()
    index = dict(index)
    index["synthetic"] = False
    result = find_documents(index, request, selection, AS_OF)
    assert result["outcome"] == "not_synthetic"
    assert result["matches"] == []
    assert "CANARY-SECRET-BRIEF" not in _blob(result)


def test_missing_readers_fail_closed():
    index, request, selection = _load()
    index = json.loads(json.dumps(index))
    index["files"] = [
        {
            "file_id": "SYN-OD-0021",
            "location_id": "LOC-HOUSING",
            "title": "CANARY-NO-READERS housing repairs",
            "last_modified": "2026-09-01",
            "sensitivity_label": "OFFICIAL",
            "extract": "Housing repairs with no reader list.",
        }
    ]
    result = find_documents(index, request, selection, AS_OF)
    assert result["matches"] == []
    assert result["withheld"]["not_permitted"] == 1
    assert "CANARY-NO-READERS" not in _blob(result)


def test_prohibited_functions_raise_and_acknowledgement_does_not_change_a_file():
    with pytest.raises(FinderForbidden):
        move_file()
    with pytest.raises(FinderForbidden):
        delete_file()
    with pytest.raises(FinderForbidden):
        share_file()
    with pytest.raises(FinderForbidden):
        change_permissions()
    result = _run()
    refused = acknowledge_results(
        result,
        {
            "decision": "delete_file",
            "actor_role": "Requesting user",
            "index_id": result["index_id"],
            "queue_reviewed": True,
        },
    )
    assert refused["acknowledgement"]["reason"] == "prohibited_decision"
    assert refused["human_approval"] is None
    assert refused["flags"]["deleted"] is False
    blocked = acknowledge_results(
        result,
        {
            "decision": "acknowledge",
            "actor_role": "Requesting user",
            "index_id": result["index_id"],
        },
    )
    assert blocked["acknowledgement"]["reason"] == "queue_not_reviewed"
    accepted = acknowledge_results(
        result,
        {
            "decision": "acknowledge",
            "actor_role": "Requesting user",
            "index_id": result["index_id"],
            "queue_reviewed": True,
        },
    )
    assert accepted["human_approval"]["decision"] == "acknowledge"
    assert accepted["human_approval"]["executed"] is False
    assert accepted["flags"]["shared"] is False
    assert accepted["flags"]["moved"] is False
