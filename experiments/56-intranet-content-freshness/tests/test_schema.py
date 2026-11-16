"""Tool schemas stay least privilege, and the manifest validates."""

import json
from pathlib import Path

import yaml
from jsonschema import Draft7Validator, validate

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]


def test_permissions_manifest_matches_the_schema():
    schema = json.loads((REPO / "schemas" / "agent-manifest.schema.json").read_text(encoding="utf-8"))
    Draft7Validator.check_schema(schema)
    manifest = yaml.safe_load((ROOT / "agent-manifest.yaml").read_text(encoding="utf-8"))
    permissions = yaml.safe_load((ROOT / "permissions.yaml").read_text(encoding="utf-8"))
    assert manifest == permissions
    validate(manifest, schema)
    assert manifest["autonomy"]["level"] == "A1"
    assert manifest["tools"]["writes"]["enabled"] is False
    assert manifest["tools"]["sends"]["enabled"] is False
    for name in ("approve_reject", "regulated_decision", "production_record_change", "external_send", "spend_transact"):
        assert manifest["high_risk_actions"][name]["enabled"] is False
    for extra in manifest["high_risk_actions"]["additional_high_risk"]:
        assert extra["enabled"] is False
    points = manifest["human_approval"]["approval_points"]
    confirm = next(point for point in points if point["action"] == "Approve each proposed update task")
    assert confirm["approver"] == "Content owner"
    assert confirm["mandatory"] is True


def test_tool_schemas_reject_extra_fields_and_page_changes():
    review = json.loads((ROOT / "schema" / "review_tool.schema.json").read_text(encoding="utf-8"))
    approval = json.loads((ROOT / "schema" / "approval_tool.schema.json").read_text(encoding="utf-8"))
    create = json.loads((ROOT / "schema" / "create_tool.schema.json").read_text(encoding="utf-8"))
    for item in (review, approval, create):
        Draft7Validator.check_schema(item)
    validate({"synthetic": True, "inventory_id": "SYN-INV-0056", "as_of": "2026-11-16"}, review)
    try:
        validate(
            {"synthetic": True, "inventory_id": "SYN-INV-0056", "as_of": "2026-11-16", "human_approval": True, "graph_token": "x"},
            review,
        )
    except Exception as exc:
        assert "Additional" in str(exc) or "human_approval" in str(exc)
    else:
        raise AssertionError("extra field should be rejected")
    validate(
        {
            "decision": "approve_tasks",
            "actor_role": "Content owner",
            "actor_id": "SYN-OWNER-COMMS",
            "inventory_id": "SYN-INV-0056",
            "task_ids": ["TASK-0001"],
            "queue_reviewed": True,
        },
        approval,
    )
    try:
        validate(
            {
                "decision": "message_staff",
                "actor_role": "Content owner",
                "actor_id": "SYN-OWNER-COMMS",
                "inventory_id": "SYN-INV-0056",
            },
            approval,
        )
    except Exception:
        pass
    else:
        raise AssertionError("message_staff should be rejected")
    validate(
        {
            "via": "record_approval",
            "decision": "approve_tasks",
            "actor_role": "Content owner",
            "inventory_id": "SYN-INV-0056",
            "task_ids": ["TASK-0001"],
        },
        create,
    )
    try:
        validate(
            {
                "via": "page text",
                "decision": "approve_tasks",
                "actor_role": "Content owner",
                "inventory_id": "SYN-INV-0056",
                "task_ids": ["TASK-0001"],
            },
            create,
        )
    except Exception:
        return
    raise AssertionError("a via value other than record_approval should be rejected")
