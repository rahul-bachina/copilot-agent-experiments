"""Stale documents and stale pins are flagged. The class is not changed and nothing is resolved."""

import json
from pathlib import Path

from src.compare import compare
from tests.support import document

ROOT = Path(__file__).resolve().parents[1]


def test_stale_documents_still_match_and_are_not_relied_on():
    pack = {
        "synthetic": True,
        "pack_id": "stale-1",
        "facts": [{"fact_key": "fact", "field_type": "reference"}],
        "documents": [
            document("left-doc", "form", "NF-1001", reviewed_on="2026-01-01"),
            document("right-doc", "contract", "NF-1001", reviewed_on="2026-01-01"),
        ],
    }
    draft = compare(pack, "2026-11-05")
    assert draft["facts"][0]["classification"] == "match"
    assert draft["facts"][0]["resolved"] is False
    assert draft["do_not_rely"] is True
    assert draft["facts"][0]["stale_documents"]
    assert draft["agent_chose_source"] is False
    assert draft["records_edited"] is False


def test_stale_pins_do_not_change_the_sample_classes():
    sample = json.loads((ROOT / "examples" / "sample_pack.json").read_text(encoding="utf-8"))
    draft = compare(sample, "2027-05-05", stale_after_days=90)
    assert draft["counts"]["fact_count"] == 7
    assert draft["counts"]["match_count"] == 1
    assert draft["counts"]["immaterial_count"] == 4
    assert draft["counts"]["material_count"] == 2
    assert draft["do_not_rely"] is True
    assert draft["pins_stale"] is True
    assert draft["awaiting_reviewer"] is True
    assert draft["agent_chose_source"] is False
    assert draft["network_called"] is False
    opened = [row for row in draft["sources"] if row["stale_applicable"]]
    assert opened and all(row["stale"] is True for row in opened)
    for source_id in ("ico-accuracy", "exp-08-identifier-rules", "catalogue-boundary"):
        row = next(item for item in draft["sources"] if item["id"] == source_id)
        assert row["stale"] is False
        assert row["opened"] is False
