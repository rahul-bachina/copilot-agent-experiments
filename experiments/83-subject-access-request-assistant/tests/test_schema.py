"""Tool schemas stay least privilege. Extra keys are not accepted."""

import json
from pathlib import Path

from jsonschema import Draft7Validator

ROOT = Path(__file__).resolve().parents[1]


def test_tool_schemas_reject_unknown_fields():
    for path in sorted((ROOT / "schema").glob("*.schema.json")):
        schema = json.loads(path.read_text(encoding="utf-8"))
        Draft7Validator.check_schema(schema)
        assert schema["additionalProperties"] is False
        assert schema["type"] == "object"
