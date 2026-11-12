"""A judgement about a named person is not digested. The text is not copied.

The hold is not a closed performance list. A marked message goes to a person
even when no cue matches. A hospital, grievance, or safeguarding cue does too.
"""

import json

from digest import run
from support import bundle, message, review


def _held(body: str, **extra) -> dict:
    export = bundle([message("SYN-MSG-1", body, **extra)])
    produced = run(export, "2026-11-12", review())
    assert produced["digest"]["decisions"] == []
    assert produced["digest"]["actions"] == []
    withheld = produced["digest"]["withheld"]
    assert withheld[0]["text_copied"] is False
    assert body not in json.dumps(produced)
    return withheld[0]


def test_performance_comment_is_withheld():
    row = _held("Sam Quinn's performance this quarter has been poor.")
    assert row["reason"] == "judgement_about_a_named_person"


def test_evaluative_sentence_without_the_word_performance_is_withheld():
    row = _held("Jordan Hale has been difficult to work with this month.")
    assert row["reason"] == "judgement_about_a_named_person"


def test_hospital_wording_is_withheld_even_when_it_looks_like_a_decision():
    row = _held("We decided to extend hospital visiting hours.")
    assert row["reason"] == "sensitive_content"


def test_a_marked_message_is_withheld_without_a_keyword():
    row = _held("The notes are in the shared folder.", sensitivity="review")
    assert row["reason"] == "marked_for_a_person"
