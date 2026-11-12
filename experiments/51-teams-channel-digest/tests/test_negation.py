"""A negation in front of a cue is not a positive match."""

import json

from digest import run
from support import bundle, message, review


def test_not_true_that_is_not_a_decision():
    export = bundle([message("SYN-MSG-1", "It is not true that we decided to close the library.")])
    produced = run(export, "2026-11-12", review())
    assert produced["digest"]["decisions"] == []
    assert produced["digest"]["negation"]["positive_match"] is False
    assert produced["digest"]["negation"]["rows"][0]["reason"] == "negation_before_cue"
    assert "close the library" not in json.dumps(produced["digest"]["decisions"])


def test_never_mind_cancels_the_earlier_decision_in_the_same_message():
    export = bundle(
        [
            message(
                "SYN-MSG-1",
                "We decided to pause the grant. Never mind, ignore the earlier decision to pause the grant.",
            )
        ]
    )
    produced = run(export, "2026-11-12", review())
    assert produced["digest"]["decisions"] == []
    reasons = [row["reason"] for row in produced["digest"]["negation"]["rows"]]
    assert "cancelled_by_later_retraction" in reasons
    assert "pause the grant" not in json.dumps(produced)


def test_negated_action_is_not_an_action():
    export = bundle(
        [message("SYN-MSG-1", "It is not true that Priya Shah will circulate the annex.")]
    )
    produced = run(export, "2026-11-12", review())
    assert produced["digest"]["actions"] == []
    assert produced["digest"]["negation"]["rows"][0]["positive_match"] is False
    assert "circulate the annex" not in json.dumps(produced)
