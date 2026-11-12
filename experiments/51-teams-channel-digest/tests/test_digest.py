"""Cited decisions, questions, actions, and items for the requesting user."""

from digest import run
from support import bundle, message, review


def _digest(body: str, **extra):
    export = bundle([message("SYN-MSG-1", body, **extra)])
    return run(export, "2026-11-12", review())


def test_decision_question_action_and_attention_are_cited():
    export = bundle(
        [
            message("SYN-MSG-1", "We decided to keep Saturday library hours through March 2027."),
            message("SYN-MSG-2", "Open question: which ward halls stay open on Saturday?", "2026-11-04"),
            message(
                "SYN-MSG-3",
                "Action for Priya Shah: circulate the draft by 14 November 2026.",
                "2026-11-04",
            ),
            message("SYN-MSG-4", "Rowan Hale, please confirm the cabinet date.", "2026-11-05"),
        ]
    )
    produced = run(export, "2026-11-12", review())
    digest = produced["digest"]
    assert produced["human_approval"] is None
    assert produced["flags"]["posted"] is False
    decision = digest["decisions"][0]
    assert decision["text"] == "We decided to keep Saturday library hours through March 2027."
    assert decision["message_ids"] == ["SYN-MSG-1"]
    assert decision["citation"]["event_id"] == "SYN-MSG-1"
    assert decision["citation"]["line_start"] == 1
    assert decision["exp41_verdict"] == "supported"
    assert decision["exp29_verdict"] == "supported"
    assert digest["open_questions"][0]["message_ids"] == ["SYN-MSG-2"]
    action = digest["actions"][0]
    assert action["owner"] == "Priya Shah"
    assert action["message_ids"] == ["SYN-MSG-3"]
    assert digest["attention"][0]["text"].startswith("Rowan Hale")
    assert produced["reuse"]["experiment_41"]["called"] is True
    assert produced["reuse"]["experiment_29"]["called"] is True
    assert produced["reuse"]["experiment_29"]["foundry_called"] is False
    assert digest["counts"]["messages_read"] == 4
    assert digest["counts"]["section_point_count"] == 4


def test_we_decided_not_to_is_still_a_decision():
    produced = _digest("We decided not to close the Saturday library.")
    assert produced["digest"]["decisions"][0]["text"] == "We decided not to close the Saturday library."


def test_owner_is_only_a_name_written_in_the_sentence():
    produced = _digest("The team will circulate the draft.")
    assert produced["digest"]["actions"] == []
    assert produced["digest"]["counts"]["not_classified_count"] == 1


def test_regulated_firm_label_does_not_decide_foia():
    export = bundle(
        [message("SYN-MSG-1", "We decided to keep the control log.")],
        sector="regulated_firm",
    )
    produced = run(export, "2026-11-12", review())
    regulatory = produced["regulatory"]
    assert regulatory["sector_label"] == "regulated_firm"
    assert regulatory["public_authority_decided"] is False
    assert regulatory["held_information_decided"] is False
    assert regulatory["purpose_limitation_met"] is False
    assert regulatory["data_minimisation_met"] is False
    assert regulatory["monitoring_decided"] is False
    assert regulatory["dpia_decided"] is False
