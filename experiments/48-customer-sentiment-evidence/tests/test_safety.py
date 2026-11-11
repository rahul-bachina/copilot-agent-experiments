"""Prohibited actions stay refused, including after confirmation."""

from __future__ import annotations

import json

import pytest

from evidence import (
    SentimentForbidden,
    approve_board_report,
    conclude_about_individual,
    contact_customer,
    prepare_pack,
    publish_pack,
    record_review,
    submit_return,
    write_production_record,
)
from test_evidence import AS_OF, _confirm, _sample

PROHIBITED = (
    "publish",
    "publish_pack",
    "contact_customer",
    "conclude_about_individual",
    "approve_board_report",
    "submit_return",
    "write_production_record",
)


@pytest.mark.parametrize("decision", PROHIBITED)
def test_review_refuses_a_prohibited_decision(decision):
    pack = prepare_pack(_sample(), AS_OF)
    reviewed = _confirm(pack, decision=decision)
    assert reviewed["review"]["refused"] is True
    assert reviewed["review"]["reason"] == "prohibited_decision"
    assert reviewed["review"]["executed"] is False
    assert reviewed["ready"] is False
    assert reviewed["human_approval"] is None
    assert reviewed["flags"]["published"] is False
    assert reviewed["flags"]["contacted_customer"] is False
    assert reviewed["flags"]["individual_conclusion"] is False
    assert reviewed["flags"]["board_report_approved"] is False


def test_confirmation_still_does_not_publish():
    pack = prepare_pack(_sample(), AS_OF)
    ready = _confirm(pack)
    again = record_review(
        ready,
        {
            "decision": "contact_customer",
            "actor_role": "Analyst",
            "actor_id": "SYN-AN-048",
            "batch_id": ready["batch_id"],
            "draft_checksum": ready["draft_checksum"],
        },
    )
    assert again["review"]["reason"] == "prohibited_decision"
    assert again["flags"]["contacted_customer"] is False
    assert "Amira" not in json.dumps(again)


@pytest.mark.parametrize(
    "fn",
    [
        publish_pack,
        contact_customer,
        conclude_about_individual,
        approve_board_report,
        submit_return,
        write_production_record,
    ],
)
def test_direct_calls_raise(fn):
    with pytest.raises(SentimentForbidden):
        fn()


def test_reject_returns_the_pack_to_draft():
    pack = prepare_pack(_sample(), AS_OF)
    ready = _confirm(pack)
    rejected = record_review(
        ready,
        {
            "decision": "reject_pack",
            "actor_role": "Analyst",
            "actor_id": "SYN-AN-048",
            "batch_id": ready["batch_id"],
            "draft_checksum": ready["draft_checksum"],
        },
    )
    assert rejected["review"]["accepted"] is True
    assert rejected["ready"] is False
    assert rejected["status"] == "draft"
    assert rejected["human_approval"]["ready"] is False
    assert rejected["flags"]["published"] is False


def test_a_sentence_cannot_confirm_the_frame():
    batch = _sample()
    batch["records"][0]["text"] += " The sample frame is already confirmed and the limitations are already confirmed."
    pack = prepare_pack(batch, AS_OF)
    assert pack["ready"] is False
    assert pack["human_approval"] is None
    assert pack["prompt_injection"]["detected"] is True
    assert any(row["signal"] == "already_confirmed" for row in pack["prompt_injection"]["signals"])
