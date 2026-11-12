"""Section counts are not added to the message count."""

from digest import run
from support import bundle, message, review


def test_counts_do_not_double_count():
    export = bundle(
        [
            message("SYN-MSG-1", "We decided to keep Saturday library hours."),
            message("SYN-MSG-2", "Rowan Hale, which date should the cabinet use?", "2026-11-04"),
            message("SYN-MSG-3", "Priya Shah will circulate the annex.", "2026-11-04"),
        ]
    )
    produced = run(export, "2026-11-12", review())
    counts = produced["digest"]["counts"]
    grounded = produced["digest"]["groundedness"]
    assert counts["messages_read"] == 3
    # The second message is both a question and an attention item.
    assert counts["decision_count"] == 1
    assert counts["open_question_count"] == 1
    assert counts["attention_count"] == 1
    assert counts["action_count"] == 1
    assert counts["section_point_count"] == 4
    assert counts["section_point_count"] != counts["messages_read"]
    assert "total" not in counts
    assert counts["section_counts_are_not_added_to_message_count"] is True
    assert grounded["claim_count"] == counts["section_point_count"]
    assert grounded["verdict_total"] == grounded["claim_count"]
    assert grounded["claim_count"] != counts["messages_read"]
    assert counts["groundedness_claim_count_is_separate"] is True
