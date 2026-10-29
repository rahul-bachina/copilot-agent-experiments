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


class TestExperiment05Manifest:
    """Test the Experiment 05 Awaab's Law hazard-triage manifest."""

    @pytest.fixture
    def experiment_05_manifest(self):
        manifest_path = (
            REPO_ROOT / "experiments" / "05-awaabs-law-hazard-triage" / "agent-manifest.yaml"
        )
        with open(manifest_path) as handle:
            return yaml.safe_load(handle)

    def test_manifest_validates_against_schema(self, schema, experiment_05_manifest):
        """Experiment 05 manifest should be valid."""
        validate(instance=experiment_05_manifest, schema=schema)

    def test_autonomy_level_is_a1(self, experiment_05_manifest):
        """Experiment 05 should be autonomy level A1."""
        assert experiment_05_manifest["autonomy"]["level"] == "A1"

    def test_all_high_risk_actions_disabled(self, experiment_05_manifest):
        """Experiment 05 should have all high-risk actions disabled."""
        high_risk = experiment_05_manifest["high_risk_actions"]
        for action in [
            "approve_reject",
            "regulated_decision",
            "production_record_change",
            "external_send",
            "spend_transact",
        ]:
            assert high_risk[action]["enabled"] is False, f"{action} should be disabled"
        for extra in high_risk["additional_high_risk"]:
            assert extra["enabled"] is False

    def test_sends_and_writes_disabled(self, experiment_05_manifest):
        """Nothing is sent to a tenant or written to a housing system."""
        assert experiment_05_manifest["tools"]["writes"]["enabled"] is False
        assert experiment_05_manifest["tools"]["sends"]["enabled"] is False


class TestExperiment06Manifest:
    """Test the Experiment 06 NHS corporate policy Q&A manifest."""

    @pytest.fixture
    def experiment_06_manifest(self):
        manifest_path = REPO_ROOT / "experiments" / "06-nhs-policy-qa" / "agent-manifest.yaml"
        with open(manifest_path) as handle:
            return yaml.safe_load(handle)

    def test_manifest_validates_against_schema(self, schema, experiment_06_manifest):
        """Experiment 06 manifest should be valid."""
        validate(instance=experiment_06_manifest, schema=schema)

    def test_autonomy_level_is_a0(self, experiment_06_manifest):
        """Experiment 06 should be autonomy level A0."""
        assert experiment_06_manifest["autonomy"]["level"] == "A0"
        assert experiment_06_manifest["autonomy"]["auto_actions_enabled"] is False

    def test_all_high_risk_actions_disabled(self, experiment_06_manifest):
        """Experiment 06 should have all high-risk actions disabled."""
        high_risk = experiment_06_manifest["high_risk_actions"]
        for action in [
            "approve_reject",
            "regulated_decision",
            "production_record_change",
            "external_send",
            "spend_transact",
        ]:
            assert high_risk[action]["enabled"] is False, f"{action} should be disabled"
        for extra in high_risk["additional_high_risk"]:
            assert extra["enabled"] is False

    def test_sends_and_writes_disabled(self, experiment_06_manifest):
        """Nothing is sent, published, or written to a policy register."""
        assert experiment_06_manifest["tools"]["writes"]["enabled"] is False
        assert experiment_06_manifest["tools"]["sends"]["enabled"] is False

    def test_policy_owner_approves_sources(self, experiment_06_manifest):
        """The human checkpoint is the policy owner, and it is mandatory."""
        points = experiment_06_manifest["human_approval"]["approval_points"]
        source_approval = next(
            point for point in points if "authoritative register" in point["action"]
        )
        assert source_approval["approver"] == "Policy owner"
        assert source_approval["mandatory"] is True


class TestExperiment07Manifest:
    """Test the Experiment 07 consultation-theme manifest."""

    @pytest.fixture
    def experiment_07_manifest(self):
        manifest_path = (
            REPO_ROOT / "experiments" / "07-consultation-themes" / "agent-manifest.yaml"
        )
        with open(manifest_path) as handle:
            return yaml.safe_load(handle)

    def test_manifest_validates_against_schema(self, schema, experiment_07_manifest):
        """Experiment 07 manifest should be valid."""
        validate(instance=experiment_07_manifest, schema=schema)

    def test_autonomy_level_is_a1(self, experiment_07_manifest):
        """Experiment 07 should be autonomy level A1, not above."""
        level = experiment_07_manifest["autonomy"]["level"]
        assert level == "A1"
        assert level in {"A0", "A1"}

    def test_all_high_risk_actions_disabled(self, experiment_07_manifest):
        """Experiment 07 should have all high-risk actions disabled."""
        high_risk = experiment_07_manifest["high_risk_actions"]
        for action in [
            "approve_reject",
            "regulated_decision",
            "production_record_change",
            "external_send",
            "spend_transact",
        ]:
            assert high_risk[action]["enabled"] is False, f"{action} should be disabled"
        for extra in high_risk["additional_high_risk"]:
            assert extra["enabled"] is False

    def test_sends_and_writes_disabled(self, experiment_07_manifest):
        """Nothing is published, sent, or written to a consultation system."""
        assert experiment_07_manifest["tools"]["writes"]["enabled"] is False
        assert experiment_07_manifest["tools"]["sends"]["enabled"] is False
        assert experiment_07_manifest["autonomy"]["human_in_the_loop"] is True


class TestExperiment08Manifest:
    """Test the Experiment 08 UK identifier PII gateway manifest."""

    @pytest.fixture
    def experiment_08_manifest(self):
        manifest_path = (
            REPO_ROOT / "experiments" / "08-uk-pii-redaction-gateway" / "agent-manifest.yaml"
        )
        with open(manifest_path) as handle:
            return yaml.safe_load(handle)

    def test_manifest_validates_against_schema(self, schema, experiment_08_manifest):
        """Experiment 08 manifest should be valid."""
        validate(instance=experiment_08_manifest, schema=schema)

    def test_autonomy_level_is_a1(self, experiment_08_manifest):
        """Experiment 08 should be autonomy level A1."""
        assert experiment_08_manifest["autonomy"]["level"] == "A1"
        assert experiment_08_manifest["autonomy"]["auto_actions_enabled"] is False
        assert experiment_08_manifest["autonomy"]["human_in_the_loop"] is True

    def test_all_high_risk_actions_disabled(self, experiment_08_manifest):
        """Experiment 08 should have all high-risk actions disabled."""
        high_risk = experiment_08_manifest["high_risk_actions"]
        for action in [
            "approve_reject",
            "regulated_decision",
            "production_record_change",
            "external_send",
            "spend_transact",
        ]:
            assert high_risk[action]["enabled"] is False, f"{action} should be disabled"
        for extra in high_risk["additional_high_risk"]:
            assert extra["enabled"] is False

    def test_sends_and_writes_disabled(self, experiment_08_manifest):
        """Nothing is sent, released, or written to a production store."""
        assert experiment_08_manifest["tools"]["writes"]["enabled"] is False
        assert experiment_08_manifest["tools"]["sends"]["enabled"] is False

    def test_privacy_reviewer_approves_before_release(self, experiment_08_manifest):
        """The human checkpoint is a privacy reviewer, and it is mandatory."""
        points = experiment_08_manifest["human_approval"]["approval_points"]
        release = next(point for point in points if point["action"].startswith("Approve the redacted"))
        assert release["approver"] == "Privacy reviewer"
        assert release["mandatory"] is True


class TestExperiment09Manifest:
    """Test the Experiment 09 correspondence-draft manifest."""

    @pytest.fixture
    def experiment_09_manifest(self):
        manifest_path = (
            REPO_ROOT
            / "experiments"
            / "09-casework-correspondence-draft"
            / "agent-manifest.yaml"
        )
        with open(manifest_path) as handle:
            return yaml.safe_load(handle)

    def test_manifest_validates_against_schema(self, schema, experiment_09_manifest):
        """Experiment 09 manifest should be valid."""
        validate(instance=experiment_09_manifest, schema=schema)

    def test_autonomy_level_is_a1(self, experiment_09_manifest):
        """Experiment 09 should be autonomy level A1, not above."""
        level = experiment_09_manifest["autonomy"]["level"]
        assert level == "A1"
        assert level in {"A0", "A1", "A2"}

    def test_all_high_risk_actions_disabled(self, experiment_09_manifest):
        """Experiment 09 should have all high-risk actions disabled."""
        high_risk = experiment_09_manifest["high_risk_actions"]
        for action in [
            "approve_reject",
            "regulated_decision",
            "production_record_change",
            "external_send",
            "spend_transact",
        ]:
            assert high_risk[action]["enabled"] is False, f"{action} should be disabled"
        for extra in high_risk["additional_high_risk"]:
            assert extra["enabled"] is False

    def test_sends_and_writes_disabled(self, experiment_09_manifest):
        """Nothing is sent or written to a correspondence case system."""
        assert experiment_09_manifest["tools"]["writes"]["enabled"] is False
        assert experiment_09_manifest["tools"]["sends"]["enabled"] is False
        assert experiment_09_manifest["autonomy"]["human_in_the_loop"] is True

    def test_author_approves_recipient_and_final_text(self, experiment_09_manifest):
        """The author approves the recipient and the final text, and both are mandatory."""
        points = experiment_09_manifest["human_approval"]["approval_points"]
        for action in ("Approve the recipient", "Approve the final text"):
            point = next(item for item in points if item["action"] == action)
            assert point["approver"] == "Correspondence author"
            assert point["mandatory"] is True


class TestExperiment10Manifest:
    """Test the Experiment 10 Travel Rule exception-triage manifest."""

    @pytest.fixture
    def experiment_10_manifest(self):
        manifest_path = (
            REPO_ROOT
            / "experiments"
            / "10-travel-rule-exception-triage"
            / "agent-manifest.yaml"
        )
        with open(manifest_path) as handle:
            return yaml.safe_load(handle)

    def test_manifest_validates_against_schema(self, schema, experiment_10_manifest):
        """Experiment 10 manifest should be valid."""
        validate(instance=experiment_10_manifest, schema=schema)

    def test_autonomy_level_is_a1(self, experiment_10_manifest):
        """Experiment 10 should be autonomy level A1, not above."""
        level = experiment_10_manifest["autonomy"]["level"]
        assert level == "A1"
        assert level in {"A0", "A1"}
        assert experiment_10_manifest["autonomy"]["human_in_the_loop"] is True
        assert experiment_10_manifest["autonomy"]["auto_actions_enabled"] is False

    def test_all_high_risk_actions_disabled(self, experiment_10_manifest):
        """Experiment 10 should have all high-risk actions disabled."""
        high_risk = experiment_10_manifest["high_risk_actions"]
        for action in [
            "approve_reject",
            "regulated_decision",
            "production_record_change",
            "external_send",
            "spend_transact",
        ]:
            assert high_risk[action]["enabled"] is False, f"{action} should be disabled"
        for extra in high_risk["additional_high_risk"]:
            assert extra["enabled"] is False

    def test_sends_and_writes_disabled(self, experiment_10_manifest):
        """Nothing is sent, filed, or written to a transfer system."""
        assert experiment_10_manifest["tools"]["writes"]["enabled"] is False
        assert experiment_10_manifest["tools"]["sends"]["enabled"] is False

    def test_analyst_decides_hold_return_or_escalate(self, experiment_10_manifest):
        """The human checkpoint is the analyst, and it is mandatory."""
        points = experiment_10_manifest["human_approval"]["approval_points"]
        decision = next(point for point in points if point["action"].startswith("Decide hold"))
        assert decision["approver"] == "Analyst"
        assert decision["mandatory"] is True


class TestExperiment11Manifest:
    """Test the Experiment 11 Employment Rights Act 2025 HR assistant manifest."""

    @pytest.fixture
    def experiment_11_manifest(self):
        manifest_path = (
            REPO_ROOT
            / "experiments"
            / "11-era-2025-hr-assistant"
            / "agent-manifest.yaml"
        )
        with open(manifest_path) as handle:
            return yaml.safe_load(handle)

    def test_manifest_validates_against_schema(self, schema, experiment_11_manifest):
        """Experiment 11 manifest should be valid."""
        validate(instance=experiment_11_manifest, schema=schema)

    def test_autonomy_level_is_a1(self, experiment_11_manifest):
        """Experiment 11 should be autonomy level A1, not above."""
        level = experiment_11_manifest["autonomy"]["level"]
        assert level == "A1"
        assert level in {"A0", "A1"}
        assert experiment_11_manifest["autonomy"]["human_in_the_loop"] is True
        assert experiment_11_manifest["autonomy"]["auto_actions_enabled"] is False

    def test_all_high_risk_actions_disabled(self, experiment_11_manifest):
        """Experiment 11 should have all high-risk actions disabled."""
        high_risk = experiment_11_manifest["high_risk_actions"]
        for action in [
            "approve_reject",
            "regulated_decision",
            "production_record_change",
            "external_send",
            "spend_transact",
        ]:
            assert high_risk[action]["enabled"] is False, f"{action} should be disabled"
        for extra in high_risk["additional_high_risk"]:
            assert extra["enabled"] is False

    def test_sends_and_writes_disabled(self, experiment_11_manifest):
        """Nothing is sent or written to a personnel or policy record."""
        assert experiment_11_manifest["tools"]["writes"]["enabled"] is False
        assert experiment_11_manifest["tools"]["sends"]["enabled"] is False

    def test_hr_lead_treats_the_draft(self, experiment_11_manifest):
        """The human checkpoint is the HR lead, and it is mandatory."""
        points = experiment_11_manifest["human_approval"]["approval_points"]
        decision = next(point for point in points if point["action"].startswith("Treat the draft"))
        assert decision["approver"] == "HR lead"
        assert decision["mandatory"] is True


class TestExperiment12Manifest:
    """Test the Experiment 12 document-intake manifest."""

    @pytest.fixture
    def experiment_12_manifest(self):
        manifest_path = (
            REPO_ROOT / "experiments" / "12-document-intake" / "agent-manifest.yaml"
        )
        with open(manifest_path) as handle:
            return yaml.safe_load(handle)

    def test_manifest_validates_against_schema(self, schema, experiment_12_manifest):
        """Experiment 12 manifest should be valid."""
        validate(instance=experiment_12_manifest, schema=schema)

    def test_autonomy_level_is_a1(self, experiment_12_manifest):
        """Experiment 12 should be autonomy level A1, not above."""
        level = experiment_12_manifest["autonomy"]["level"]
        assert level == "A1"
        assert level in {"A0", "A1", "A2"}
        assert "A3" not in level
        assert experiment_12_manifest["autonomy"]["human_in_the_loop"] is True
        assert experiment_12_manifest["autonomy"]["auto_actions_enabled"] is False

    def test_all_high_risk_actions_disabled(self, experiment_12_manifest):
        """Experiment 12 should have all high-risk actions disabled."""
        high_risk = experiment_12_manifest["high_risk_actions"]
        for action in [
            "approve_reject",
            "regulated_decision",
            "production_record_change",
            "external_send",
            "spend_transact",
        ]:
            assert high_risk[action]["enabled"] is False, f"{action} should be disabled"
        for extra in high_risk["additional_high_risk"]:
            assert extra["enabled"] is False

    def test_sends_and_writes_disabled(self, experiment_12_manifest):
        """Nothing is sent or written to a case system."""
        assert experiment_12_manifest["tools"]["writes"]["enabled"] is False
        assert experiment_12_manifest["tools"]["sends"]["enabled"] is False

    def test_user_confirms_files_and_purpose(self, experiment_12_manifest):
        """The catalogue checkpoint is the user, and it is mandatory."""
        points = experiment_12_manifest["human_approval"]["approval_points"]
        files = next(point for point in points if point["action"].startswith("Confirm the file list"))
        purpose = next(point for point in points if point["action"].startswith("Confirm the permitted purpose"))
        assert files["approver"] == "Intake user"
        assert files["mandatory"] is True
        assert purpose["approver"] == "Intake user"
        assert purpose["mandatory"] is True
        assert experiment_12_manifest["agent"]["id"] == "exp-12-document-intake"


class TestExperiment13Manifest:
    """Test the Experiment 13 council front-door manifest."""

    @pytest.fixture
    def experiment_13_manifest(self):
        manifest_path = (
            REPO_ROOT
            / "experiments"
            / "13-council-contact-front-door"
            / "agent-manifest.yaml"
        )
        with open(manifest_path) as handle:
            return yaml.safe_load(handle)

    def test_manifest_validates_against_schema(self, schema, experiment_13_manifest):
        """Experiment 13 manifest should be valid."""
        validate(instance=experiment_13_manifest, schema=schema)

    def test_autonomy_level_is_a1(self, experiment_13_manifest):
        """Experiment 13 should be autonomy level A1, not above."""
        level = experiment_13_manifest["autonomy"]["level"]
        assert level == "A1"
        assert level in {"A0", "A1", "A2"}
        assert "A3" not in level
        assert experiment_13_manifest["autonomy"]["human_in_the_loop"] is True
        assert experiment_13_manifest["autonomy"]["auto_actions_enabled"] is False

    def test_all_high_risk_actions_disabled(self, experiment_13_manifest):
        """Experiment 13 should have all high-risk actions disabled."""
        high_risk = experiment_13_manifest["high_risk_actions"]
        for action in [
            "approve_reject",
            "regulated_decision",
            "production_record_change",
            "external_send",
            "spend_transact",
        ]:
            assert high_risk[action]["enabled"] is False, f"{action} should be disabled"
        for extra in high_risk["additional_high_risk"]:
            assert extra["enabled"] is False

    def test_sends_and_writes_disabled(self, experiment_13_manifest):
        """Nothing is sent or written to a case system."""
        assert experiment_13_manifest["tools"]["writes"]["enabled"] is False
        assert experiment_13_manifest["tools"]["sends"]["enabled"] is False

    def test_adviser_accepts_a_published_page(self, experiment_13_manifest):
        """The human checkpoint is the adviser, and it is mandatory."""
        points = experiment_13_manifest["human_approval"]["approval_points"]
        decision = next(point for point in points if point["action"].startswith("Accept a published"))
        assert decision["approver"] == "Contact centre adviser"
        assert decision["mandatory"] is True


class TestExperiment15Manifest:
    """Test the Experiment 15 vulnerability and urgency scanner manifest."""

    @pytest.fixture
    def experiment_15_manifest(self):
        manifest_path = (
            REPO_ROOT
            / "experiments"
            / "15-vulnerability-urgency-scanner"
            / "agent-manifest.yaml"
        )
        with open(manifest_path) as handle:
            return yaml.safe_load(handle)

    def test_manifest_validates_against_schema(self, schema, experiment_15_manifest):
        """Experiment 15 manifest should be valid."""
        validate(instance=experiment_15_manifest, schema=schema)

    def test_autonomy_level_is_a1(self, experiment_15_manifest):
        """Experiment 15 should be autonomy level A1, not above."""
        level = experiment_15_manifest["autonomy"]["level"]
        assert level == "A1"
        assert level in {"A0", "A1", "A2"}
        assert "A3" not in level
        assert experiment_15_manifest["autonomy"]["human_in_the_loop"] is True
        assert experiment_15_manifest["autonomy"]["auto_actions_enabled"] is False

    def test_all_high_risk_actions_disabled(self, experiment_15_manifest):
        """Experiment 15 should have all high-risk actions disabled."""
        high_risk = experiment_15_manifest["high_risk_actions"]
        for action in [
            "approve_reject",
            "regulated_decision",
            "production_record_change",
            "external_send",
            "spend_transact",
        ]:
            assert high_risk[action]["enabled"] is False, f"{action} should be disabled"
        for extra in high_risk["additional_high_risk"]:
            assert extra["enabled"] is False

    def test_sends_and_writes_disabled(self, experiment_15_manifest):
        """Nothing is sent or written to a case system."""
        assert experiment_15_manifest["tools"]["writes"]["enabled"] is False
        assert experiment_15_manifest["tools"]["sends"]["enabled"] is False

    def test_duty_officer_reviews_every_flag(self, experiment_15_manifest):
        """The human checkpoint is the duty officer, and it is mandatory."""
        points = experiment_15_manifest["human_approval"]["approval_points"]
        review = next(point for point in points if point["action"] == "Review every flag")
        assert review["approver"] == "Duty officer"
        assert review["mandatory"] is True
        assert experiment_15_manifest["agent"]["id"] == "exp-15-vulnerability-urgency-scanner"


class TestExperiment14Manifest:
    """Test the Experiment 14 architecture advisor manifest."""

    @pytest.fixture
    def experiment_14_manifest(self):
        manifest_path = (
            REPO_ROOT
            / "experiments"
            / "14-agent-architecture-advisor"
            / "agent-manifest.yaml"
        )
        with open(manifest_path) as handle:
            return yaml.safe_load(handle)

    def test_manifest_validates_against_schema(self, schema, experiment_14_manifest):
        """Experiment 14 manifest should be valid."""
        validate(instance=experiment_14_manifest, schema=schema)

    def test_autonomy_level_is_a0(self, experiment_14_manifest):
        """Experiment 14 should be autonomy level A0, not above."""
        level = experiment_14_manifest["autonomy"]["level"]
        assert level == "A0"
        assert level in {"A0", "A1", "A2"}
        assert "A3" not in level
        assert experiment_14_manifest["autonomy"]["human_in_the_loop"] is True
        assert experiment_14_manifest["autonomy"]["auto_actions_enabled"] is False

    def test_all_high_risk_actions_disabled(self, experiment_14_manifest):
        """Experiment 14 should have all high-risk actions disabled."""
        high_risk = experiment_14_manifest["high_risk_actions"]
        for action in [
            "approve_reject",
            "regulated_decision",
            "production_record_change",
            "external_send",
            "spend_transact",
        ]:
            assert high_risk[action]["enabled"] is False, f"{action} should be disabled"
        for extra in high_risk["additional_high_risk"]:
            assert extra["enabled"] is False

    def test_sends_and_writes_disabled(self, experiment_14_manifest):
        """Nothing is sent or written to a tenant."""
        assert experiment_14_manifest["tools"]["writes"]["enabled"] is False
        assert experiment_14_manifest["tools"]["sends"]["enabled"] is False

    def test_architect_confirms_the_platform(self, experiment_14_manifest):
        """The human checkpoint is the architect, and it is mandatory."""
        points = experiment_14_manifest["human_approval"]["approval_points"]
        confirm = next(point for point in points if point["action"].startswith("Confirm each platform"))
        assert confirm["approver"] == "Architect"
        assert confirm["mandatory"] is True
        assert experiment_14_manifest["agent"]["id"] == "exp-14-agent-architecture-advisor"


class TestExperiment16Manifest:
    """Test the Experiment 16 KYC evidence-intake manifest."""

    @pytest.fixture
    def experiment_16_manifest(self):
        manifest_path = (
            REPO_ROOT / "experiments" / "16-kyc-evidence-intake" / "agent-manifest.yaml"
        )
        with open(manifest_path) as handle:
            return yaml.safe_load(handle)

    def test_manifest_validates_against_schema(self, schema, experiment_16_manifest):
        """Experiment 16 manifest should be valid."""
        validate(instance=experiment_16_manifest, schema=schema)

    def test_autonomy_level_is_a1(self, experiment_16_manifest):
        """Experiment 16 should be autonomy level A1, not above."""
        level = experiment_16_manifest["autonomy"]["level"]
        assert level == "A1"
        assert level in {"A0", "A1", "A2"}
        assert "A3" not in level
        assert experiment_16_manifest["autonomy"]["human_in_the_loop"] is True
        assert experiment_16_manifest["autonomy"]["auto_actions_enabled"] is False

    def test_all_high_risk_actions_disabled(self, experiment_16_manifest):
        """Experiment 16 should have all high-risk actions disabled."""
        high_risk = experiment_16_manifest["high_risk_actions"]
        for action in [
            "approve_reject",
            "regulated_decision",
            "production_record_change",
            "external_send",
            "spend_transact",
        ]:
            assert high_risk[action]["enabled"] is False, f"{action} should be disabled"
        for extra in high_risk["additional_high_risk"]:
            assert extra["enabled"] is False

    def test_sends_and_writes_disabled(self, experiment_16_manifest):
        """Nothing is sent or written to an onboarding system."""
        assert experiment_16_manifest["tools"]["writes"]["enabled"] is False
        assert experiment_16_manifest["tools"]["sends"]["enabled"] is False

    def test_reviewer_confirms_documents_and_purpose(self, experiment_16_manifest):
        """The catalogue checkpoint is the KYC reviewer, and it is mandatory."""
        points = experiment_16_manifest["human_approval"]["approval_points"]
        decision = next(point for point in points if point["action"].startswith("Confirm the documents"))
        assert decision["approver"] == "KYC reviewer"
        assert decision["mandatory"] is True
        assert experiment_16_manifest["agent"]["id"] == "exp-16-kyc-evidence-intake"


class TestExperiment17Manifest:
    """Test the Experiment 17 invoice exception-triage manifest."""

    @pytest.fixture
    def experiment_17_manifest(self):
        manifest_path = (
            REPO_ROOT / "experiments" / "17-invoice-exception-triage" / "agent-manifest.yaml"
        )
        with open(manifest_path) as handle:
            return yaml.safe_load(handle)

    def test_manifest_validates_against_schema(self, schema, experiment_17_manifest):
        """Experiment 17 manifest should be valid."""
        validate(instance=experiment_17_manifest, schema=schema)

    def test_autonomy_level_is_a1(self, experiment_17_manifest):
        """Experiment 17 should be autonomy level A1, not above."""
        level = experiment_17_manifest["autonomy"]["level"]
        assert level == "A1"
        assert level in {"A0", "A1", "A2"}
        assert "A3" not in level
        assert experiment_17_manifest["autonomy"]["human_in_the_loop"] is True
        assert experiment_17_manifest["autonomy"]["auto_actions_enabled"] is False

    def test_all_high_risk_actions_disabled(self, experiment_17_manifest):
        """Experiment 17 should have all high-risk actions disabled."""
        high_risk = experiment_17_manifest["high_risk_actions"]
        for action in [
            "approve_reject",
            "regulated_decision",
            "production_record_change",
            "external_send",
            "spend_transact",
        ]:
            assert high_risk[action]["enabled"] is False, f"{action} should be disabled"
        for extra in high_risk["additional_high_risk"]:
            assert extra["enabled"] is False

    def test_sends_and_writes_disabled(self, experiment_17_manifest):
        """Nothing is posted, paid, or written to a finance system."""
        assert experiment_17_manifest["tools"]["writes"]["enabled"] is False
        assert experiment_17_manifest["tools"]["sends"]["enabled"] is False

    def test_ap_reviewer_approves_the_resolution(self, experiment_17_manifest):
        """The catalogue checkpoint is the AP reviewer, and it is mandatory."""
        points = experiment_17_manifest["human_approval"]["approval_points"]
        decision = next(point for point in points if point["action"].startswith("Approve, return"))
        assert decision["approver"] == "AP reviewer"
        assert decision["mandatory"] is True
        assert experiment_17_manifest["agent"]["id"] == "exp-17-invoice-exception-triage"


class TestExperiment18Manifest:
    """Test the Experiment 18 evidence pack builder manifest."""

    @pytest.fixture
    def experiment_18_manifest(self):
        manifest_path = (
            REPO_ROOT / "experiments" / "18-evidence-pack-builder" / "agent-manifest.yaml"
        )
        with open(manifest_path) as handle:
            return yaml.safe_load(handle)

    def test_manifest_validates_against_schema(self, schema, experiment_18_manifest):
        """Experiment 18 manifest should be valid."""
        validate(instance=experiment_18_manifest, schema=schema)

    def test_autonomy_level_is_a1(self, experiment_18_manifest):
        """Experiment 18 should be autonomy level A1, not above."""
        level = experiment_18_manifest["autonomy"]["level"]
        assert level == "A1"
        assert level in {"A0", "A1", "A2"}
        assert "A3" not in level
        assert experiment_18_manifest["autonomy"]["human_in_the_loop"] is True
        assert experiment_18_manifest["autonomy"]["auto_actions_enabled"] is False

    def test_all_high_risk_actions_disabled(self, experiment_18_manifest):
        """Experiment 18 should have all high-risk actions disabled."""
        high_risk = experiment_18_manifest["high_risk_actions"]
        for action in [
            "approve_reject",
            "regulated_decision",
            "production_record_change",
            "external_send",
            "spend_transact",
        ]:
            assert high_risk[action]["enabled"] is False, f"{action} should be disabled"
        for extra in high_risk["additional_high_risk"]:
            assert extra["enabled"] is False

    def test_sends_and_writes_disabled(self, experiment_18_manifest):
        """Nothing is sent or written to a case system."""
        assert experiment_18_manifest["tools"]["writes"]["enabled"] is False
        assert experiment_18_manifest["tools"]["sends"]["enabled"] is False

    def test_approver_confirms_the_exact_list(self, experiment_18_manifest):
        """The catalogue checkpoint is the evidence pack approver, and it is mandatory."""
        points = experiment_18_manifest["human_approval"]["approval_points"]
        decision = next(point for point in points if point["action"].startswith("Approve the exact list"))
        assert decision["approver"] == "Evidence pack approver"
        assert decision["mandatory"] is True
        assert experiment_18_manifest["agent"]["id"] == "exp-18-evidence-pack-builder"


class TestExperiment19Manifest:
    """Test the Experiment 19 privacy impact assessment manifest."""

    @pytest.fixture
    def experiment_19_manifest(self):
        manifest_path = (
            REPO_ROOT / "experiments" / "19-privacy-impact-assessment" / "agent-manifest.yaml"
        )
        with open(manifest_path) as handle:
            return yaml.safe_load(handle)

    def test_manifest_validates_against_schema(self, schema, experiment_19_manifest):
        """Experiment 19 manifest should be valid."""
        validate(instance=experiment_19_manifest, schema=schema)

    def test_autonomy_level_is_a1(self, experiment_19_manifest):
        """Experiment 19 should be autonomy level A1, not above."""
        level = experiment_19_manifest["autonomy"]["level"]
        assert level == "A1"
        assert level in {"A0", "A1", "A2"}
        assert "A3" not in level
        assert experiment_19_manifest["autonomy"]["human_in_the_loop"] is True
        assert experiment_19_manifest["autonomy"]["auto_actions_enabled"] is False

    def test_all_high_risk_actions_disabled(self, experiment_19_manifest):
        """Experiment 19 should have all high-risk actions disabled."""
        high_risk = experiment_19_manifest["high_risk_actions"]
        for action in [
            "approve_reject",
            "regulated_decision",
            "production_record_change",
            "external_send",
            "spend_transact",
        ]:
            assert high_risk[action]["enabled"] is False, f"{action} should be disabled"
        for extra in high_risk["additional_high_risk"]:
            assert extra["enabled"] is False

    def test_sends_and_writes_disabled(self, experiment_19_manifest):
        """Nothing is sent or written to a DPIA register."""
        assert experiment_19_manifest["tools"]["writes"]["enabled"] is False
        assert experiment_19_manifest["tools"]["sends"]["enabled"] is False

    def test_privacy_officer_approves_the_assessment(self, experiment_19_manifest):
        """The catalogue checkpoint is the privacy officer, and it is mandatory."""
        points = experiment_19_manifest["human_approval"]["approval_points"]
        decision = next(point for point in points if point["action"] == "Approve the assessment")
        assert decision["approver"] == "Privacy officer"
        assert decision["mandatory"] is True
        residual = next(point for point in points if point["action"] == "Accept residual risk")
        assert residual["approver"] == "Project owner"
        assert experiment_19_manifest["agent"]["id"] == "exp-19-privacy-impact-assessment"


class TestExperiment22Manifest:
    """Test the Experiment 22 on-chain alert SAR drafter manifest."""

    @pytest.fixture
    def experiment_22_manifest(self):
        manifest_path = (
            REPO_ROOT / "experiments" / "22-onchain-alert-sar-drafter" / "agent-manifest.yaml"
        )
        with open(manifest_path) as handle:
            return yaml.safe_load(handle)

    def test_manifest_validates_against_schema(self, schema, experiment_22_manifest):
        """Experiment 22 manifest should be valid."""
        validate(instance=experiment_22_manifest, schema=schema)

    def test_autonomy_level_is_a1(self, experiment_22_manifest):
        """Experiment 22 should be autonomy level A1, not above."""
        level = experiment_22_manifest["autonomy"]["level"]
        assert level == "A1"
        assert level in {"A0", "A1", "A2"}
        assert "A3" not in level
        assert experiment_22_manifest["autonomy"]["human_in_the_loop"] is True
        assert experiment_22_manifest["autonomy"]["auto_actions_enabled"] is False

    def test_all_high_risk_actions_disabled(self, experiment_22_manifest):
        """Experiment 22 should have all high-risk actions disabled."""
        high_risk = experiment_22_manifest["high_risk_actions"]
        for action in [
            "approve_reject",
            "regulated_decision",
            "production_record_change",
            "external_send",
            "spend_transact",
        ]:
            assert high_risk[action]["enabled"] is False, f"{action} should be disabled"
        for extra in high_risk["additional_high_risk"]:
            assert extra["enabled"] is False

    def test_sends_and_writes_disabled(self, experiment_22_manifest):
        """Nothing is filed or sent."""
        assert experiment_22_manifest["tools"]["writes"]["enabled"] is False
        assert experiment_22_manifest["tools"]["sends"]["enabled"] is False

    def test_nominated_officer_decides_whether_to_file(self, experiment_22_manifest):
        """The catalogue checkpoint is the nominated officer, and it is mandatory."""
        points = experiment_22_manifest["human_approval"]["approval_points"]
        decision = next(
            point for point in points if point["action"] == "Decide whether the section 330 or section 331 test is met"
        )
        assert decision["approver"] == "Nominated officer"
        assert decision["mandatory"] is True
        filing = next(
            point for point in points if point["action"] == "File or not file a suspicious activity report with the NCA"
        )
        assert filing["approver"] == "Nominated officer"
        assert filing["mandatory"] is True
        assert experiment_22_manifest["agent"]["id"] == "exp-22-onchain-alert-sar-drafter"


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
