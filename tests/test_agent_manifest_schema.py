"""Tests for agent manifest schema validation.

Validates that:
1. The Experiment 01 agent-manifest.yaml is valid
2. A3 autonomy level is rejected (not permitted in this catalogue)
3. Enabled high-risk actions without human approval are rejected
4. Valid A2 manifests with proper approval pass
"""

import json
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft7Validator, ValidationError, validate

REPO_ROOT = Path(__file__).parent.parent
SCHEMA_PATH = REPO_ROOT / "schemas" / "agent-manifest.schema.json"
FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def schema():
    """Load the agent manifest schema."""
    with open(SCHEMA_PATH) as f:
        return json.load(f)


@pytest.fixture
def experiment_01_manifest():
    """Load the Experiment 01 agent manifest."""
    manifest_path = REPO_ROOT / "experiments" / "01-foi-complaint-triage" / "agent-manifest.yaml"
    with open(manifest_path) as f:
        return yaml.safe_load(f)


class TestSchemaValidity:
    """Test that the schema itself is valid."""

    def test_schema_is_valid_draft7(self, schema):
        """Schema should be valid JSON Schema Draft-07."""
        Draft7Validator.check_schema(schema)


def _load_manifest(relative: str):
    manifest_path = REPO_ROOT / relative
    with open(manifest_path) as f:
        return yaml.safe_load(f)


class TestExperiment01Manifest:
    """Test the Experiment 01 FOI triage agent manifest."""

    def test_manifest_validates_against_schema(self, schema, experiment_01_manifest):
        """Experiment 01 manifest should be valid."""
        validate(instance=experiment_01_manifest, schema=schema)

    def test_manifest_has_required_sections(self, experiment_01_manifest):
        """Manifest should have all required top-level sections."""
        required = [
            "agent",
            "autonomy",
            "data_access",
            "tools",
            "human_approval",
            "uk_gdpr",
            "risk_assessment",
            "logging_and_audit",
            "kill_switch",
            "review",
            "high_risk_actions",
        ]
        for section in required:
            assert section in experiment_01_manifest, f"Missing required section: {section}"

    def test_autonomy_level_is_a1(self, experiment_01_manifest):
        """Experiment 01 should be autonomy level A1."""
        assert experiment_01_manifest["autonomy"]["level"] == "A1"

    def test_all_high_risk_actions_disabled(self, experiment_01_manifest):
        """Experiment 01 should have all high-risk actions disabled."""
        high_risk = experiment_01_manifest["high_risk_actions"]
        for action in ["approve_reject", "regulated_decision", "production_record_change",
                       "external_send", "spend_transact"]:
            assert high_risk[action]["enabled"] is False, f"{action} should be disabled"


class TestExperiment03Manifest:
    """Test the Experiment 03 inventory and assurance-pack manifest."""

    @pytest.fixture
    def experiment_03_manifest(self):
        """Load the Experiment 03 agent manifest."""
        manifest_path = (
            REPO_ROOT
            / "experiments"
            / "03-agent-inventory-atrs-assurance"
            / "agent-manifest.yaml"
        )
        with open(manifest_path) as f:
            return yaml.safe_load(f)

    def test_manifest_validates_against_schema(self, schema, experiment_03_manifest):
        """Experiment 03 manifest should be valid."""
        validate(instance=experiment_03_manifest, schema=schema)

    def test_autonomy_level_is_a1(self, experiment_03_manifest):
        """Experiment 03 should be autonomy level A1."""
        assert experiment_03_manifest["autonomy"]["level"] == "A1"

    def test_all_high_risk_actions_disabled(self, experiment_03_manifest):
        """Experiment 03 should have all high-risk actions disabled."""
        high_risk = experiment_03_manifest["high_risk_actions"]
        for action in ["approve_reject", "regulated_decision", "production_record_change",
                       "external_send", "spend_transact"]:
            assert high_risk[action]["enabled"] is False, f"{action} should be disabled"

    def test_additional_high_risk_actions_disabled(self, experiment_03_manifest):
        """Publishing an ATRS record and marking a manifest approved stay off."""
        additional = experiment_03_manifest["high_risk_actions"]["additional_high_risk"]
        assert additional
        assert all(item["enabled"] is False for item in additional)


class TestEveryExperimentManifest:
    """Every agent-manifest.yaml under experiments/ has to validate."""

    def test_all_manifests_validate(self, schema):
        manifests = sorted(Path(REPO_ROOT / "experiments").rglob("agent-manifest.yaml"))
        assert manifests, "expected at least one agent manifest"
        for manifest_path in manifests:
            with open(manifest_path) as handle:
                manifest = yaml.safe_load(handle)
            validate(instance=manifest, schema=schema)

    def test_experiment_04_is_a0_and_does_not_decide(self, schema):
        manifest = _load_manifest(
            "experiments/04-fca-cryptoasset-readiness/agent-manifest.yaml"
        )
        validate(instance=manifest, schema=schema)
        assert manifest["agent"]["id"] == "exp-04-fca-cryptoasset-readiness"
        assert manifest["autonomy"]["level"] == "A0"
        assert manifest["autonomy"]["auto_actions_enabled"] is False
        assert manifest["tools"]["writes"]["enabled"] is False
        assert manifest["tools"]["sends"]["enabled"] is False
        high_risk = manifest["high_risk_actions"]
        for action in [
            "approve_reject",
            "regulated_decision",
            "production_record_change",
            "external_send",
            "spend_transact",
        ]:
            assert high_risk[action]["enabled"] is False
        for extra in high_risk["additional_high_risk"]:
            assert extra["enabled"] is False


class TestInvalidA3Autonomy:
    """Test that A3 autonomy level is rejected."""

    def test_a3_autonomy_rejected(self, schema):
        """Manifest with A3 autonomy should fail validation."""
        invalid_path = FIXTURES_DIR / "invalid-manifest-a3-autonomy.yaml"
        with open(invalid_path) as f:
            invalid_manifest = yaml.safe_load(f)

        with pytest.raises(ValidationError) as exc_info:
            validate(instance=invalid_manifest, schema=schema)

        error_message = str(exc_info.value)
        assert "A3" in error_message or "enum" in error_message.lower(), \
            "Error should mention A3 or enum constraint"


class TestHighRiskActionsValidation:
    """Test high-risk action validation rules."""

    def test_enabled_high_risk_without_approval_rejected(self, schema):
        """High-risk action enabled without human_approval should fail."""
        invalid_path = FIXTURES_DIR / "invalid-manifest-high-risk-no-approval.yaml"
        with open(invalid_path) as f:
            invalid_manifest = yaml.safe_load(f)

        with pytest.raises(ValidationError):
            validate(instance=invalid_manifest, schema=schema)

    def test_enabled_high_risk_with_approval_valid(self, schema):
        """High-risk action enabled with proper human_approval should pass."""
        valid_path = FIXTURES_DIR / "valid-manifest-a2-with-approval.yaml"
        with open(valid_path) as f:
            valid_manifest = yaml.safe_load(f)

        validate(instance=valid_manifest, schema=schema)

    def test_valid_manifest_has_named_approver(self, schema):
        """Valid A2 manifest should have named approver for enabled high-risk action."""
        valid_path = FIXTURES_DIR / "valid-manifest-a2-with-approval.yaml"
        with open(valid_path) as f:
            valid_manifest = yaml.safe_load(f)

        external_send = valid_manifest["high_risk_actions"]["external_send"]
        assert external_send["enabled"] is True
        assert external_send["human_approval"]["required"] is True
        assert external_send["human_approval"]["approver"] == "Customer Service Manager"


class TestAutonomyLevelEnumeration:
    """Test autonomy level enumeration."""

    def test_a0_permitted(self, schema):
        """A0 autonomy level should be permitted."""
        valid_path = FIXTURES_DIR / "valid-manifest-a2-with-approval.yaml"
        with open(valid_path) as f:
            manifest = yaml.safe_load(f)

        manifest["autonomy"]["level"] = "A0"
        validate(instance=manifest, schema=schema)

    def test_a1_permitted(self, schema):
        """A1 autonomy level should be permitted."""
        valid_path = FIXTURES_DIR / "valid-manifest-a2-with-approval.yaml"
        with open(valid_path) as f:
            manifest = yaml.safe_load(f)

        manifest["autonomy"]["level"] = "A1"
        validate(instance=manifest, schema=schema)

    def test_a2_permitted(self, schema):
        """A2 autonomy level should be permitted."""
        valid_path = FIXTURES_DIR / "valid-manifest-a2-with-approval.yaml"
        with open(valid_path) as f:
            manifest = yaml.safe_load(f)

        manifest["autonomy"]["level"] = "A2"
        validate(instance=manifest, schema=schema)

    def test_a3_not_permitted(self, schema):
        """A3 autonomy level should NOT be permitted."""
        valid_path = FIXTURES_DIR / "valid-manifest-a2-with-approval.yaml"
        with open(valid_path) as f:
            manifest = yaml.safe_load(f)

        manifest["autonomy"]["level"] = "A3"
        with pytest.raises(ValidationError):
            validate(instance=manifest, schema=schema)
