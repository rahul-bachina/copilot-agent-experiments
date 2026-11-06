"""The sample comparison cites clauses and does not rank them."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.compare import CompareForbidden, NotSynthetic, compare, interpret_favourability, record_specialist_review
from tests.support import COVERAGE, clause, load_sample, pair

AS_OF = "2026-11-06"


def test_sample_counts_and_the_flood_gap():
    draft = compare(load_sample(), as_of=AS_OF)
    summary = draft["summary"]
    assert draft["label"].startswith("DRAFT FOR THE WORDING SPECIALIST")
    assert draft["catalogue_id"] == "B008"
    assert draft["autonomy"] == "A0"
    assert summary["row_count"] == 8
    assert summary["stated_cell_count"] == 15
    assert summary["verdict_total"] == 15
    assert summary["not_stated_cell_count"] == 1
    assert summary["failure_count"] == 0
    assert summary["material_difference_count"] == 3
    assert summary["same_text_count"] == 5
    assert summary["facts_are_not_summed"] is True
    assert "grand_total" not in summary
    assert draft["checker_passed"] is True
    assert draft["do_not_rely"] is True
    assert "specialist_has_not_validated" in draft["do_not_rely_reasons"]
    flood = next(row for row in draft["rows"] if row["row_id"] == "exclusion.flood")
    assert flood["difference_class"] == "not_stated_in_one"
    renewal = next(cell for cell in flood["cells"] if cell["wording_id"] == "renewal")
    expiring = next(cell for cell in flood["cells"] if cell["wording_id"] == "expiring")
    assert renewal["status"] == "not_stated"
    assert renewal["text"] == "not stated"
    assert renewal["inferred"] is False
    assert renewal["citation"] is None
    assert expiring["quotes"][0]["citation"]["clause_ref"] == "4.2"
    assert expiring["quotes"][0]["verdict"] == "supported"
    limit = next(row for row in draft["rows"] if row["row_id"] == "limit.buildings")
    assert limit["difference_class"] == "text_differs"
    assert limit["amounts_differ"] is True
    assert limit["favourable_to"] is None
    assert "flood_extension" not in json.dumps(draft["rows"])
    assert draft["unaligned"][0]["topic"] == "not stated"
    assert draft["unaligned"][0]["inferred"] is False
    assert draft["not_used"][0]["reason"] == "intake_date_not_current"
    for key in ("favourable_to", "recommendation", "endorsement_draft", "coverage_decision", "baseline_wording"):
        assert draft[key] is None
    assert draft["broker_contacted"] is False
    assert draft["policy_admin_written"] is False
    assert draft["document_intelligence_called"] is False
    assert draft["foundry_called"] is False
    assert draft["solely_automated_decision"] is False
    assert draft["downstream_use_permitted"] is False


def test_a_matching_pair_is_still_not_validated_by_the_agent():
    draft = compare(pair([clause(1, "coverage_grant", "property_damage", "1.1", COVERAGE)], [clause(1, "coverage_grant", "property_damage", "1.1", COVERAGE)]), as_of=AS_OF)
    assert draft["summary"]["same_text_count"] == 1
    assert draft["summary"]["material_difference_count"] == 0
    assert draft["rows"][0]["difference_class"] == "same_text"
    assert draft["do_not_rely"] is True
    assert draft["do_not_rely_reasons"] == ["specialist_has_not_validated"]


def test_one_wording_and_a_live_pack_are_refused():
    one = pair([clause(1, "coverage_grant", "property_damage", "1.1", COVERAGE)], [])
    one["wordings"] = one["wordings"][:1]
    try:
        compare(one, as_of=AS_OF)
    except ValueError as exc:
        assert "two wordings" in str(exc)
    else:
        raise AssertionError("expected a refusal")
    live = load_sample()
    live["synthetic"] = False
    try:
        compare(live, as_of=AS_OF)
    except NotSynthetic:
        pass
    else:
        raise AssertionError("expected NotSynthetic")


def test_basis_words_are_not_a_finding_of_no_effect():
    text = "The proposal is declared to form the basis of the contract."
    draft = compare(
        pair(
            [clause(1, "warranty", "proposal", "6.2", text)],
            [clause(1, "warranty", "proposal", "6.2", text)],
        ),
        as_of=AS_OF,
    )
    quote = draft["rows"][0]["cells"][0]["quotes"][0]
    assert quote["basis_of_contract_words"] is True
    assert quote["basis_clause_of_no_effect"] is None
    assert draft["basis_clause_of_no_effect"] is None


def test_specialist_review_does_not_recommend():
    draft = compare(load_sample(), as_of=AS_OF)
    marks = {row["row_id"]: "read" for row in draft["rows"]}
    unaligned = {item["unaligned_id"]: "noted_unaligned" for item in draft["unaligned"]}
    reviewed = record_specialist_review(
        draft,
        role="Wording specialist",
        reviewer_ref="WS-1008",
        row_marks=marks,
        unaligned_marks=unaligned,
    )
    assert reviewed["interpretation_acknowledged"] is True
    assert reviewed["recommendation"] is None
    assert reviewed["favourable_to"] is None
    assert reviewed["endorsement_draft"] is None
    assert reviewed["downstream_use_permitted"] is False
    assert reviewed["broker_contacted"] is False
    assert "material_difference" in reviewed["do_not_rely_reasons"]
    assert "specialist_has_not_validated" not in reviewed["do_not_rely_reasons"]
    try:
        record_specialist_review(draft, role="Broker", reviewer_ref="WS-1008", row_marks=marks, unaligned_marks=unaligned)
    except CompareForbidden:
        pass
    else:
        raise AssertionError("expected a refusal")
    try:
        interpret_favourability()
    except CompareForbidden:
        pass
    else:
        raise AssertionError("expected a refusal")
