"""Tagged advice is filed. Nothing is decided."""

import json

from src.assemble import assemble
from tests.support import AS_OF, bundle


def test_sample_files_tagged_advice_and_leaves_the_decisions_false():
    draft = assemble(bundle(), as_of=AS_OF)
    assert draft["label"] == "DRAFT FOR CASEWORKER — NOT A PLAN"
    assert draft["catalogue_id"] == "UK10"
    assert draft["autonomy"] == "A1"
    assert draft["placed_quotes"] == 7
    assert [len(draft["sections"][letter]["lines"]) for letter in ("A", "B", "C", "D", "E", "F")] == [
        1, 2, 1, 1, 1, 1,
    ]
    assert draft["sections"]["I"]["lines"] == []
    assert draft["sections"]["I"]["left_blank_in_draft"] is True
    assert len(draft["sections"]["I"]["lines_withheld"]) == 1
    assert draft["sections"]["I"]["lines_withheld"][0]["quote_copied"] is False
    assert len(draft["sections"]["K"]["advice_list"]) == 5
    assert draft["sections"]["K"]["appendices_attached"] is False
    assert draft["sections"]["F"]["provision_secured"] is False
    assert draft["sections"]["B"]["needs_decided"] is False
    assert draft["sections"]["E"]["outcomes_decided"] is False
    for flag in (
        "needs_decided",
        "provision_decided",
        "placement_decided",
        "outcomes_decided",
        "final_plan_edited",
        "sent_to_parents",
        "sent_to_school",
        "written_to_la_system",
        "provision_secured",
        "a3_recommended",
        "model_called",
        "network_called",
    ):
        assert draft[flag] is False
    assert draft["actions_taken"] == []
    assert draft["exported"] is False
    assert draft["export_blocked"] is True
    assert draft["export"] is None
    assert draft["agent_checked_template"] is False
    assert draft["timescale"]["days_since_request"] == 93
    assert draft["timescale"]["twenty_week_marker_passed"] is False
    assert draft["timescale"]["breach_found"] is False
    assert draft["timescale"]["exceptions_applied"] is False
    assert draft["do_not_rely"] is False
    assert "written into the draft" not in json.dumps(draft)
    assert "one-to-one" not in json.dumps(draft)


def test_every_placed_quote_is_the_source_paragraph_and_is_not_repeated():
    source = bundle()
    draft = assemble(source, as_of=AS_OF)
    index = {}
    for report in source["reports"]:
        for paragraph in report["paragraphs"]:
            index[(report["report_id"], paragraph["paragraph_id"])] = paragraph["text"]
    seen = []
    for letter, section in draft["sections"].items():
        for line in section["lines"]:
            citation = line["citation"]
            key = (citation["report_id"], citation["paragraph_id"])
            assert line["quote"] == index[key]
            assert line["mapping_source"] == "advice_tag"
            assert line["decided_by_agent"] is False
            seen.append(key)
    assert len(seen) == len(set(seen)) == draft["placed_quotes"]
    for line in draft["unplaced"]:
        citation = line["citation"]
        assert line["quote"] == index[(citation["report_id"], citation["paragraph_id"])]


def test_a_duplicate_report_is_dropped_and_not_counted_twice():
    source = bundle()
    source["reports"].append(json.loads(json.dumps(source["reports"][1])))
    draft = assemble(source, as_of=AS_OF)
    assert draft["placed_quotes"] == 7
    assert draft["duplicate_reports_dropped"] == ["R-EDU-01"]
    assert len(draft["sections"]["K"]["advice_list"]) == 5
    assert len(draft["sections"]["B"]["lines"]) == 2


def test_a_supported_statement_does_not_add_a_second_line():
    draft = assemble(bundle(), as_of=AS_OF)
    assert draft["supported_statements"][0]["copied_into_sections"] is False
    assert draft["supported_statements"][0]["matched"] is True
    assert len(draft["sections"]["A"]["lines"]) == 1


def test_the_same_inputs_produce_the_same_json():
    first = assemble(bundle(), as_of=AS_OF)
    second = assemble(bundle(), as_of=AS_OF)
    assert first == second
