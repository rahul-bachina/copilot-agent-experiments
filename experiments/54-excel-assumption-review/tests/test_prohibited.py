import pytest

from review import (
    ReviewForbidden,
    assert_assumption,
    clear_legal_hold,
    edit_workbook,
    invent_benchmark,
    strip_protective_marking,
    write_cell,
)
from support import pack, reviewed


def test_direct_calls_raise_and_do_not_change_a_report():
    for function in (
        edit_workbook,
        write_cell,
        assert_assumption,
        invent_benchmark,
        strip_protective_marking,
        clear_legal_hold,
    ):
        with pytest.raises(ReviewForbidden):
            function()
    report = reviewed()
    assert report["flags"]["workbook_modified"] is False
    assert report["flags"]["assumption_judged"] is False
    assert report["flags"]["benchmark_invented"] is False
    assert report["flags"]["marking_stripped"] is False
    assert report["flags"]["legal_hold_cleared"] is False


def test_prohibited_pack_keys_are_ignored():
    body = pack()
    body["workbook_modified"] = True
    body["human_approval"] = {"step": "confirm_workbook_ranges_and_formulas"}
    body["benchmark"] = "0.02"
    body["assumption_judged"] = True
    from review import review_workbook
    from support import AS_OF, confirmation

    report = review_workbook(body, confirmation(), AS_OF)
    assert report["outcome"] == "review_for_model_owner"
    assert report["flags"]["workbook_modified"] is False
    assert report["flags"]["assumption_judged"] is False
    assert "benchmark" in report["prohibited_keys_ignored"]
    assert "human_approval" in report["prohibited_keys_ignored"]


def test_safeguarding_text_is_not_processed_as_a_modelling_question():
    body = pack()
    body["cells"] = [
        cell if not (cell["sheet"] == "Notes" and cell["cell"] == "A1") else {**cell, "value": "I want to end my life"}
        for cell in body["cells"]
    ]
    from review import review_workbook
    from support import AS_OF, confirmation

    report = review_workbook(body, confirmation(body["cells"]), AS_OF)
    assert report["outcome"] == "safeguarding_for_human"
    assert report["routine_processing"] is False
    assert report["inventory"] == []
    assert report["questions"] == []
    assert report["sensitivity"] is None
    assert "possible_self_harm_risk" in report["safeguarding"]["categories"]
    assert report["safeguarding"]["text_copied"] is False
    assert "end my life" not in __import__("json").dumps(report)
    assert report["protective_marking"] == "OFFICIAL-SENSITIVE"


def test_a_pack_that_is_not_synthetic_is_refused_without_an_echo():
    body = pack()
    body["synthetic"] = False
    body["model_id"] = "REAL-MODEL"
    from review import review_workbook
    from support import AS_OF

    report = review_workbook(body, None, AS_OF)
    assert report["outcome"] == "refused_not_synthetic"
    assert report["cells_echoed"] is False
    blob = __import__("json").dumps(report)
    assert "REAL-MODEL" not in blob
    assert "0.025" not in blob
    assert "Jane Example" not in blob
