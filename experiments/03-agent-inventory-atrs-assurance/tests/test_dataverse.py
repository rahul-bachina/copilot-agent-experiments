"""CSV fixtures round-trip into the same inventory records as the JSON."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from support import ROOT, load_record  # noqa: E402
from dataverse_csv import load_directory  # noqa: E402


def test_dataverse_csv_matches_json_for_every_fixture():
    loaded = {record["inventory_id"]: record for record in load_directory(ROOT / "fixtures" / "dataverse")}
    expected_ids = {
        "exp-01-foi-triage",
        "exp-02-consumer-duty-complaint-intake",
        "exp-04-fca-cryptoasset-readiness",
        "exp-05-awaabs-law-hazard-triage",
        "syn-harbour-benefits",
        "syn-stale-register",
        "syn-injection-note",
        "syn-a3-request",
    }
    assert set(loaded) == expected_ids
    for inventory_id in expected_ids:
        assert loaded[inventory_id] == load_record(inventory_id)


def test_fixture_events_are_unapplied_proposals():
    for inventory_id in (
        "exp-01-foi-triage",
        "exp-02-consumer-duty-complaint-intake",
        "exp-04-fca-cryptoasset-readiness",
        "exp-05-awaabs-law-hazard-triage",
    ):
        record = load_record(inventory_id)
        assert record["lifecycle_status"] == "proposed"
        assert record["recorded_events"]
        for event in record["recorded_events"]:
            assert event["applied"] is False
            assert event["approved_by_this_tool"] is False
            assert event["external_approval_id"] == ""
