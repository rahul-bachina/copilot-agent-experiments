from review import review_workbook
from support import AS_OF, confirmation, pack, reviewed


def test_negation_does_not_count_as_an_inclusion():
    report = reviewed()
    assert report["text_claims"] == []
    assert all(row["cell"] != "Inputs!C2" for row in report["hardcoded_literals"])


def test_a_positive_sentence_is_not_a_structural_finding():
    body = pack()
    for cell in body["cells"]:
        if cell["sheet"] == "Cover" and cell["cell"] == "A3":
            cell["value"] = "Inputs!C2 includes a hard-coded number."
    report = review_workbook(body, confirmation(body["cells"]), AS_OF)
    assert report["text_claims"] == [
        {
            "mentioned_in": "Cover!A3",
            "cell": "Inputs!C2",
            "what": "a hard-coded number",
            "negated_sentence_counted": False,
            "structural_finding": False,
        }
    ]
    assert all(row["cell"] != "Inputs!C2" for row in report["hardcoded_literals"])


def test_it_is_not_true_that_a_citation_includes_a_duty():
    body = pack()
    for cell in body["cells"]:
        if cell["sheet"] == "Cover" and cell["cell"] == "A3":
            cell["value"] = "It is not true that the AQuA Book includes a duty to edit the workbook."
    report = review_workbook(body, confirmation(body["cells"]), AS_OF)
    assert report["text_claims"] == []
    assert report["guidance"]["aqua_book_signed"] is False
    assert report["flags"]["workbook_modified"] is False


def test_injection_is_recorded_and_not_followed():
    report = reviewed()
    assert report["prompt_injection"]["detected"] is True
    assert report["prompt_injection"]["followed"] is False
    assert "ignore_previous_instructions" in report["prompt_injection"]["patterns"]
    assert report["prompt_injection"]["text_copied"] is False
    assert report["protective_marking"] == "OFFICIAL-SENSITIVE"
    assert report["flags"]["marking_stripped"] is False
    assert report["flags"]["workbook_modified"] is False
    blob = __import__("json").dumps(report)
    assert "Ignore previous instructions" not in blob
