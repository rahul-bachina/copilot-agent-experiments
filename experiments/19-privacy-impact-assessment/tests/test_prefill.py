"""An Experiment 03 inventory and a manifest pre-fill. They do not decide."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from assess import assess

INVENTORY = (
    Path(__file__).resolve().parents[2]
    / "03-agent-inventory-atrs-assurance"
    / "fixtures"
    / "inventory"
    / "syn-harbour-benefits.json"
)


def _empty() -> dict:
    return {
        "synthetic": True,
        "project_name": "",
        "organisation_name": "",
        "screening": {},
        "description": {},
        "necessity": {},
        "consultation": {},
        "risks": [],
        "automated_decision": {},
    }


def test_inventory_prefills_article_22_and_does_not_infer_article_35():
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    draft = assess(_empty(), as_of="2026-10-28", inventory=inventory)
    assert draft["screening"]["screen_result"] == "insufficient_facts"
    assert draft["prefill"]["screening_inferred"] is False
    assert draft["automated_decision_screen"]["screen_result"] == "restriction_may_apply"
    assert draft["automated_decision_screen"]["lawful"] is None
    assert draft["approved"] is False
    assert draft["prior_consultation"]["code"] == "high_residual_recorded"
    assert draft["prior_consultation"]["sent_by_agent"] is False
    assert "does not convert the inventory" in draft["agent_sections"]["inventory_note"]
    assert draft["project_name"] == "Harbour benefits priority scorer"
    assert any(note["field"] == "automated_decision.meaningful_human_involvement" for note in draft["prefill"]["inventory"])


def test_a_manifest_does_not_become_meaningful_human_involvement():
    manifest = {
        "agent": {
            "name": "Fictional library assistant",
            "description": "Drafts a reading list for a fictional library service.",
        },
        "autonomy": {"level": "A1"},
        "data_access": {"reads": [{"resource": "One synthetic project brief"}]},
        "uk_gdpr": {"lawful_basis": {"primary": "Not asserted"}},
        "high_risk_actions": {"regulated_decision": {"enabled": False}},
    }
    draft = assess(_empty(), as_of="2026-10-28", manifest=manifest)
    assert draft["project_name"] == "Fictional library assistant"
    assert draft["agent_sections"]["autonomy_level_recorded"] == "A1"
    assert draft["agent_sections"]["regulated_decision_enabled"] is False
    assert draft["agent_sections"]["meaningful_human_involvement_inferred"] is False
    assert draft["automated_decision_screen"]["screen_result"] == "insufficient_facts"
    assert draft["screening"]["screen_result"] == "insufficient_facts"
    basis = next(field for field in draft["sections"][3]["fields"] if field["name"] == "lawful_basis_considered")
    assert basis["state"] == "gap"
    assert draft["approved"] is False


def test_a_real_answer_is_not_overwritten_by_the_inventory():
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    brief = _empty()
    brief["automated_decision"] = {"meaningful_human_involvement": "yes", "significant_effect": "none"}
    brief["project_name"] = "Kept by the project team"
    draft = assess(brief, as_of="2026-10-28", inventory=inventory)
    assert draft["project_name"] == "Kept by the project team"
    assert draft["automated_decision_screen"]["recorded_facts"]["meaningful_human_involvement"] == "yes"
    assert draft["approved"] is False
