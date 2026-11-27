"""The customer's confirmation is bound to the agent-held copy."""

import json

from src.customer import _hash, answer, confirm_action, held_record, reset_held


def _proposal():
    reset_held()
    return answer(
        {
            "synthetic": True,
            "conversation_id": "CV-3001",
            "account_ref": "ACC-8401",
            "message": "Please submit my meter reading 12345 dated 2026-11-01.",
            "account_notes": "",
        },
        "2026-11-27",
    )


def _confirmation(result, **overrides):
    payload = {
        "customer_ref": "CUS-8401",
        "content_hash": result["content_hash"],
        "explicit_confirm": True,
        "confirmed_action": json.loads(json.dumps(result["proposed_action"])),
        "disclosure_seen": True,
        "human_route_seen": True,
        "retention_seen": True,
    }
    payload.update(overrides)
    return payload


def test_a_matching_confirmation_is_recorded_and_nothing_is_submitted():
    result = _proposal()
    assert result["outcome"] == "propose_action"
    assert held_record("CV-3001")["content_hash"] == result["content_hash"]
    confirmed = confirm_action(result, _confirmation(result))
    assert confirmed["confirmation_recorded"] is True
    assert confirmed["action_submitted"] is False
    assert confirmed["tariff_changed"] is False
    assert confirmed["payment_plan_agreed"] is False
    assert confirmed["psr_added"] is False
    assert confirmed["rejection_reason"] is None
    assert confirmed["held_copy_replaced"] is False


def test_eight_post_confirmation_edits_are_refused():
    result = _proposal()
    original_hash = result["content_hash"]

    def attempt(mutator):
        edited = json.loads(json.dumps(result))
        mutator(edited)
        confirmation = _confirmation(edited)
        confirmation["content_hash"] = original_hash
        confirmation["confirmed_action"] = edited["proposed_action"]
        outcome = confirm_action(edited, confirmation)
        assert outcome["confirmation_recorded"] is False
        assert outcome["action_submitted"] is False
        assert outcome["tariff_changed"] is False
        assert outcome["rejection_reason"] == "post_confirmation_edit"

    attempt(lambda item: item["proposed_action"].__setitem__("kind", "tariff_change"))
    attempt(lambda item: item["proposed_action"].__setitem__("meter_reading", "54321"))
    attempt(lambda item: item["proposed_action"].__setitem__("account_ref", "ACC-8402"))
    attempt(lambda item: item["proposed_action"].__setitem__("amount", "10.00"))
    attempt(lambda item: item["proposed_action"].__setitem__("exact_text", "Submit a different reading."))
    attempt(lambda item: item["proposed_action"].__setitem__("reading_date", "2024-01-01"))
    attempt(lambda item: item.__setitem__("legal_hold", True))
    attempt(lambda item: item.__setitem__("retention", []))
    attempt(lambda item: item["prompt_injection"].__setitem__("detected", True))
    attempt(lambda item: item["vulnerability"].append("medical_equipment"))

    edited = json.loads(json.dumps(result))
    edited["proposed_action"]["exact_text"] = "A caller re-hashed this."
    recomputed = _hash(edited)
    assert recomputed != original_hash
    confirmation = _confirmation(edited, content_hash=recomputed)
    confirmation["confirmed_action"] = edited["proposed_action"]
    refused = confirm_action(edited, confirmation)
    assert refused["confirmation_recorded"] is False
    assert refused["rejection_reason"] == "post_confirmation_edit"
    assert held_record("CV-3001")["content_hash"] == original_hash


def test_a_string_true_and_the_wrong_customer_are_refused():
    result = _proposal()
    string_true = confirm_action(result, _confirmation(result, explicit_confirm="true"))
    assert string_true["confirmation_recorded"] is False
    assert string_true["rejection_reason"] == "explicit_confirm_not_true"
    other = confirm_action(result, _confirmation(result, customer_ref="CUS-8402"))
    assert other["confirmation_recorded"] is False
    inactive = confirm_action(result, _confirmation(result, customer_ref="CUS-8499"))
    assert inactive["confirmation_recorded"] is False
    missing = _confirmation(result)
    missing["retention_seen"] = False
    ack = confirm_action(result, missing)
    assert ack["confirmation_recorded"] is False
    assert ack["rejection_reason"] == "acknowledgement_missing"


def test_a_payment_plan_request_and_a_psr_referral_still_need_confirmation():
    reset_held()
    plan = answer(
        {
            "synthetic": True,
            "conversation_id": "CV-3002",
            "account_ref": "ACC-8401",
            "message": "Please request a payment plan.",
            "account_notes": "",
        },
        "2026-11-27",
    )
    assert plan["proposed_action"]["kind"] == "payment_plan_request"
    assert plan["payment_plan_agreed"] is False
    assert plan["confirmation_recorded"] is False
    reset_held()
    referral = answer(
        {
            "synthetic": True,
            "conversation_id": "CV-3003",
            "account_ref": "ACC-8401",
            "message": "Please refer me to the priority services register.",
            "account_notes": "",
        },
        "2026-11-27",
    )
    assert referral["proposed_action"]["kind"] == "psr_referral"
    assert referral["psr_added"] is False
    hardship = answer(
        {
            "synthetic": True,
            "conversation_id": "CV-3004",
            "account_ref": "ACC-8401",
            "message": "I cannot afford the bill. Please request a payment plan.",
            "account_notes": "",
        },
        "2026-11-27",
    )
    assert hardship["outcome"] == "human_handover"
    assert hardship["proposed_action"] is None
    personal = answer(
        {
            "synthetic": True,
            "conversation_id": "CV-3005",
            "account_ref": "ACC-8401",
            "message": "I am disabled. Please refer me to the priority services register.",
            "account_notes": "",
        },
        "2026-11-27",
    )
    assert "disability" in personal["vulnerability"]
    assert personal["proposed_action"] is None
    assert personal["psr_added"] is False
