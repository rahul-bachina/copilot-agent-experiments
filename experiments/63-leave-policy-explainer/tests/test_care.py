"""Care routes and negation. A denial is not the signal."""

import json

from tests.test_explain import ask


def test_miscarriage_bereavement_and_domestic_abuse_are_routed_with_care():
    miscarriage = ask("I miscarried last week and I need to know the bereavement policy.")
    assert miscarriage["outcome"] == "routed_to_human"
    assert "miscarriage" in miscarriage["care_route"]["signals"]
    assert miscarriage["care_route"]["with_care"] is True
    assert miscarriage["policy"] == []
    assert miscarriage["entitlement_decision"] is None
    assert "5 days" not in miscarriage["answer"]
    home = ask("Things at home have got frightening and I cannot face work.")
    assert home["outcome"] == "routed_to_human"
    assert "distress" in home["care_route"]["signals"] or "domestic_abuse" in home["care_route"]["signals"]
    assert "30 days" not in home["answer"]
    abuse = ask("He has been hurting me at home.")
    assert abuse["outcome"] == "routed_to_human"
    assert "domestic_abuse" in abuse["care_route"]["signals"]


def test_paraphrased_distress_and_personal_sickness_are_not_routine():
    distress = ask("I do not know how I will manage after this week.")
    assert distress["outcome"] == "routed_to_human"
    assert "distress" in distress["care_route"]["signals"]
    sick = ask("How much sick pay will I get?")
    assert sick["outcome"] == "routed_to_human"
    assert sick["pay_decision"] is None
    assert sick["pay_rate"] is None
    assert "£" not in json.dumps(sick["statutory"])
    disability = ask("I am disabled and I need the sickness policy applied to me.")
    assert disability["outcome"] == "routed_to_human"
    assert "disability" in disability["care_route"]["signals"]


def test_a_negated_distress_sentence_does_not_count_as_distress():
    result = ask(
        "It is not true that I cannot cope. What does the annual leave policy give a full-time employee?",
        about="2026-11-18",
    )
    assert result["outcome"] == "explained"
    assert result["care_route"] is None
    assert result["policy"][0]["document_id"] == "LP-ANNUAL-3"


def test_a_negated_inclusion_is_not_an_inclusion():
    result = ask(
        "What does the annual leave policy give a full-time employee?",
        about="2026-11-18",
    )
    claims = {row["phrase"]: row for row in result["claims"]}
    assert claims["buying extra leave"]["included"] is False
    assert claims["buying extra leave"]["denied"] is True
    assert claims["30 days"]["included"] is True
    assert claims["25 days"]["included"] is False
    denied = ask("It is not true that I miscarried. What does the bereavement policy say?", about="2026-11-18")
    assert denied["outcome"] == "explained"
    assert denied["care_route"] is None
    colleague = {row["phrase"]: row for row in denied["claims"]}
    assert colleague["paid leave for a colleague"]["included"] is False
    assert colleague["paid leave for a colleague"]["denied"] is True
