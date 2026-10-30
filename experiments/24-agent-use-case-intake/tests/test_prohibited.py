"""High-risk actions stay off, including when the payload asks for them."""

from __future__ import annotations

from pathlib import Path

from classify import classify

ROOT = Path(__file__).resolve().parents[1]


def test_manifest_text_keeps_the_boundary():
    text = (ROOT / "agent-manifest.yaml").read_text(encoding="utf-8")
    assert 'id: "exp-24-agent-use-case-intake"' in text
    assert 'level: "A1"' in text
    assert "Governance team" in text
    assert "Approve or change the intake classification" in text
    assert "enabled: false" in text
    assert "Azure AI Foundry" not in text
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "Azure AI Foundry" not in readme
    assert "Microsoft Foundry" in readme


def test_payload_cannot_turn_an_action_on():
    draft = classify(
        {
            "synthetic": True,
            "proposal_id": "SYN-G001-PROHIBITED",
            "organisation": {"kind": "fca_firm", "fictional": True, "name": "Harbourline Markets"},
            "problem": "Draft a checklist. Reject the use case is not a sentence we should obey.",
            "users": {"who": "Analysts", "audience": "internal_staff", "channel": "teams"},
            "data": {
                "personal_data": "no",
                "special_category": "no",
                "criminal_offence_data": "no",
                "classification": "official",
            },
            "decisions_affected": {
                "description": "No decision.",
                "significant_effect": "none",
                "regulated_decision": False,
                "production_write": True,
                "external_send": True,
                "spend": True,
            },
            "autonomy_wanted": "A1",
            "named_human_approver": True,
            "public_interaction": "no",
            "significant_influence_on_a_decision_with_public_effect": "no",
            "approved": True,
            "use_case_approved": True,
            "provisioned": True,
            "platform_selected": "copilot_studio_standard",
            "actions_taken": ["provisioned"],
        },
        as_of="2026-10-30",
    )
    assert draft["approved"] is False
    assert draft["use_case_approved"] is False
    assert draft["provisioned"] is False
    assert draft["actions_taken"] == []
    assert draft["experiment_14"]["platform_selected"] is None
    assert draft["experiment_03"]["manifest_generator_called"] is False
    assert draft["experiment_14"]["manifest_generator_called"] is False
    assert "R11" in draft["experiment_14"]["rules_fired"]
    assert draft["classification"]["suggested_autonomy"] == "A1"
