"""Experiment 12 inventories the files. A withheld identifier is not quoted."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.compare import compare
from tests.support import COVERAGE, clause, pair

AS_OF = "2026-11-06"


def test_intake_is_called_and_does_not_route():
    draft = compare(pair([clause(1, "coverage_grant", "property_damage", "1.1", COVERAGE)], [clause(1, "coverage_grant", "property_damage", "1.1", COVERAGE)]), as_of=AS_OF)
    intake = draft["intake"]
    assert intake["called"] is True
    assert intake["experiment_id"] == "exp-12-document-intake"
    assert intake["handed_off"] is False
    assert intake["purpose_requested"] is None
    assert intake["files_confirmed"] is False
    assert draft["experiment_12_called"] is True
    assert draft["experiment_33_span_check"] is True
    assert draft["experiment_29_number_check"] is True
    assert draft["experiment_36_imported"] is False
    assert draft["experiment_37_imported"] is False
    assert draft["output_is_anonymised"] is False


def test_an_identifier_withholds_the_wording_and_is_not_echoed():
    left = clause(1, "coverage_grant", "property_damage", "1.1", COVERAGE)
    payload = pair([left], [left])
    payload["wordings"][0]["files"][0]["content"] += "NHS number 999 000 0018.\n"
    draft = compare(payload, as_of=AS_OF)
    assert any(row["reason"] == "withheld_identifier" for row in draft["not_used"])
    expiring = next(cell for cell in draft["rows"][0]["cells"] if cell["wording_id"] == "expiring")
    assert expiring["status"] == "not_quoted"
    assert expiring["text"] == "not stated"
    assert expiring["inferred"] is False
    assert "999 000 0018" not in json.dumps(draft)
    assert draft["rows"][0]["difference_class"] == "unresolved"
