"""Tool contracts stay least-privilege, and the manifest matches permissions.yaml."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_permissions_yaml_matches_the_manifest():
    assert (ROOT / "permissions.yaml").read_text(encoding="utf-8") == (
        ROOT / "agent-manifest.yaml"
    ).read_text(encoding="utf-8")


def test_tool_schemas_do_not_allow_a_close_or_a_send():
    complete = json.loads((ROOT / "schema" / "complete_tool.schema.json").read_text(encoding="utf-8"))
    review = json.loads((ROOT / "schema" / "review_tool.schema.json").read_text(encoding="utf-8"))
    assert complete["additionalProperties"] is False
    assert review["additionalProperties"] is False
    assert "close_job" not in review["properties"]["decision"]["enum"]
    assert "raise_charge" not in review["properties"]["decision"]["enum"]
    assert "contact_customer" not in review["properties"]["decision"]["enum"]
    blob = json.dumps(complete) + json.dumps(review)
    assert "send" not in blob
