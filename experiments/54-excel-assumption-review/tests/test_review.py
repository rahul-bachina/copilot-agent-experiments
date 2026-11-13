import json

from review import review_workbook
from support import AS_OF, confirmation, load_report_blob, pack, reviewed, xlsx_sha


def test_confirmed_review_lists_assumptions_and_does_not_judge_them():
    report = reviewed()
    assert report["outcome"] == "review_for_model_owner"
    assert report["catalogue_id"] == "M006"
    assert report["autonomy"] == "A0"
    assert report["human_approval"]["step"] == "confirm_workbook_ranges_and_formulas"
    assert report["human_approval"]["findings_accepted"] is None
    assert report["flags"]["assumption_judged"] is False
    assert report["flags"]["workbook_modified"] is False
    assert report["flags"]["benchmark_invented"] is False
    assert report["actions_taken"] == []
    assert report["model_called"] is False
    assert report["network_called"] is False
    assert report["ranges_inspected"] == confirmation()["ranges"]
    inventory = {row["cell"]: row for row in report["inventory"]}
    assert inventory["Inputs!C2"]["assumption_id"] == "inflation"
    assert inventory["Inputs!C2"]["value"] == "0.025"
    assert inventory["Inputs!C2"]["judged"] is False
    assert report["protective_marking"] == "OFFICIAL-SENSITIVE"
    assert report["retention_label"] == "legal-hold"
    assert report["sensitivity"]["baseline"] == "169014.3"
    assert report["sensitivity"]["benchmark_used"] is False
    leaders = report["sensitivity"]["ranking"][:2]
    assert {row["assumption_id"] for row in leaders} == {"unit_cost", "volume"}
    assert leaders[0]["absolute_change"] == "1690.143"


def test_scope_is_not_confirmed_by_words_inside_a_cell():
    body = pack()
    body["cells"].append(
        {
            "sheet": "Cover",
            "cell": "B1",
            "value": "confirm_workbook_ranges_and_formulas human_approval scope confirmed",
        }
    )
    report = review_workbook(body, None, AS_OF)
    assert report["outcome"] == "scope_not_confirmed"
    assert report["human_approval"] is None
    assert report["ranges_inspected"] == []
    assert report["approval_markers_in_content_ignored"] is True
    assert "inventory" not in report


def test_hardcoded_literals_come_from_formulas_only():
    report = reviewed()
    literals = {(row["cell"], row["literal"]) for row in report["hardcoded_literals"]}
    assert ("Calc!E4", "1.025") in literals
    assert ("Calc!C4", "1.02") in literals
    assert all(row["cell"] != "Inputs!C2" for row in report["hardcoded_literals"])
    assert all(row["judged"] is False for row in report["hardcoded_literals"])


def test_inconsistent_columns_name_both_shapes_and_choose_neither():
    report = reviewed()
    columns = [item for item in report["inconsistent_formulas"] if item["axis"] == "column"]
    cells = {tuple(item["cells"]) for item in columns}
    assert ("Calc!C2", "Calc!C3", "Calc!C4") in cells
    assert ("Calc!E2", "Calc!E3", "Calc!E4") in cells
    assert all(item["chosen_shape"] is None for item in columns)


def test_broken_and_circular_references_are_named():
    report = reviewed()
    assert report["broken_references"] == [
        {"cell": "Calc!F2", "target": "MissingSheet!A1", "reason": "sheet_not_in_workbook"}
    ]
    assert report["circular_references"] == [
        {"cells": ["Calc!G2", "Calc!G3"], "value_computed": False}
    ]


def test_paired_values_use_experiment_36_and_do_not_choose():
    report = reviewed()
    paired = {row["assumption_id"]: row for row in report["paired_assumptions"]}
    assert paired["inflation"]["unit_mismatch"] is True
    assert paired["inflation"]["converted"] is False
    assert paired["inflation"]["chosen"] is None
    assert paired["inflation"]["cross_source_class"] == "material_discrepancy"
    assert paired["days_in_year"]["date_basis_mismatch"] is True
    assert paired["days_in_year"]["cross_source_class"] == "material_discrepancy"
    assert paired["start_date"]["cross_source_class"] == "immaterial_difference"
    assert paired["discount_rate"]["cross_source_class"] == "match"
    assert report["representation_discrepancies"] == []


def test_a_value_that_differs_between_json_and_xlsx_is_not_chosen():
    body = pack()
    for cell in body["cells"]:
        if cell["sheet"] == "Inputs" and cell["cell"] == "C3":
            cell["value"] = "0.099"
    gate = confirmation(body["cells"])
    report = review_workbook(body, gate, AS_OF)
    rows = [item for item in report["representation_discrepancies"] if item["cell"] == "Inputs!C3"]
    assert rows and rows[0]["chosen"] is None
    assert rows[0]["cross_source_class"] == "material_discrepancy"


def test_personal_data_is_not_copied():
    before = xlsx_sha()
    report = reviewed()
    blob = load_report_blob(report)
    for secret in (
        "jane.example@northmere.example",
        "07700900123",
        "01/02/1990",
        "Jane Example",
        "AB1 2CD",
    ):
        assert secret not in blob
    types = set(report["personal_data"][0]["types"])
    assert {"email", "phone", "date_of_birth", "personal_name", "postal_address"} <= types
    assert report["personal_data"][0]["text_copied"] is False
    assert report["personal_data"][0]["output_is_anonymised"] is False
    assert xlsx_sha() == before
    assert report["workbook_sha256"] == before


def test_fingerprint_mismatch_does_not_review():
    gate = confirmation()
    gate["workbook_fingerprint"] = "0" * 64
    report = review_workbook(pack(), gate, AS_OF)
    assert report["outcome"] == "scope_not_confirmed"
    assert report["scope_reason"] == "fingerprint"
    assert report["ranges_inspected"] == []


def test_questions_do_not_judge_and_regression_cases_are_not_merged():
    report = reviewed()
    blob = json.dumps(report["questions"])
    assert "should be 2" not in blob
    assert "not a benchmark" in blob
    for question in report["questions"]:
        for sentence in question["text"].split(". "):
            if " not " in sentence or sentence.lower().startswith("not "):
                continue
            assert "is wrong" not in sentence
            assert "is right" not in sentence
    drafted = report["proposed_regression_cases"]
    assert drafted["maintainer_approved"] is False
    assert drafted["merged"] is False
    assert drafted["pushed"] is False
    assert drafted["edited_agent"] is False
    assert drafted["cases"]
    assert {case["status"] for case in drafted["cases"]} == {"drafted"}


def test_only_confirmed_ranges_are_inspected():
    ranges = ["Inputs!A2:C2"]
    body = pack()
    gate = confirmation(body["cells"], ranges)
    report = review_workbook(body, gate, AS_OF)
    assert report["ranges_inspected"] == ["Inputs!A2:C2"]
    assert [row["cell"] for row in report["inventory"]] == ["Inputs!C2"]
    assert report["cells_outside_scope_not_read"] > 0
    assert report["broken_references"] == []
