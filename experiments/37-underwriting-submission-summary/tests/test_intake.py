"""Experiment 12 inventories the files. An identifier withholds the quote."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.summarise import summarise  # noqa: E402
from tests.support import load_sample, submission_with  # noqa: E402

AS_OF = "2026-11-05"
LINE = "The proposal describes a commercial warehouse used to store dry goods."


def test_the_sample_schedule_is_classed_by_experiment_12_and_not_routed():
    draft = summarise(load_sample(), as_of=AS_OF)
    classes = {row["file_id"]: row["suggested_class"] for row in draft["intake"]["files"]}
    assert classes["schedule"] == "policy_schedule"
    assert draft["intake"]["accepted_into_queue"] is False
    assert draft["intake"]["external_sent"] is False
    assert draft["intake"]["underlying_matter_approved"] is False
    assert all(row["output_is_anonymised"] is False for row in draft["intake"]["files"])


def test_an_identifier_in_the_file_withholds_the_lines():
    payload = submission_with([("risk_description", LINE)])
    payload["files"][0]["content"] += "NHS number 999 000 0018.\n"
    draft = summarise(payload, as_of=AS_OF)
    assert draft["not_used"][0]["reason"] == "withheld_identifier"
    assert draft["sections"]["risk_description"]["status"] == "not_stated"
    assert "999 000 0018" not in draft["facts"].__repr__()
    assert "withheld_identifier" in draft["do_not_rely_reasons"]
    assert draft["intake"]["files"][0]["finding_count"] > 0
    assert draft["intake"]["files"][0]["output_is_anonymised"] is False


def test_a_file_that_was_not_read_is_not_quoted():
    payload = submission_with([("risk_description", LINE)])
    payload["files"][0]["media_type"] = "application/pdf"
    draft = summarise(payload, as_of=AS_OF)
    assert draft["not_used"][0]["reason"] == "intake_not_read"
    assert draft["sections"]["risk_description"]["status"] == "not_stated"
    assert draft["network_called"] is False
