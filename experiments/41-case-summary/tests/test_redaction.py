"""Lines Experiment 08 flags are not copied into the summary."""

import json

from src.summarise import summarise
from tests.support import case, event, four_events

AS_OF = "2026-11-09"
NINO = "TN 11 22 33 D"


def test_an_identifier_line_is_withheld_and_the_value_is_not_copied():
    events = four_events()
    events[0] = event(
        "E1",
        "2026-10-20",
        "what_happened",
        f"The tenant reported a leaking kitchen tap. NINO {NINO} was on the form.",
    )
    draft = summarise(case(events), AS_OF)
    blob = json.dumps(draft)
    assert NINO not in blob
    assert draft["pii_gateway"]["output_is_anonymised"] is False
    assert draft["pii_gateway"]["agent_may_release"] is False
    assert draft["pii_gateway"]["redacted_text_copied"] is False
    assert draft["pii_gateway"]["release_called"] is False
    assert "nino" in draft["pii_gateway"]["entity_types"]
    assert draft["summary"]["withheld_line_count"] == 1
    assert draft["withheld_lines"][0]["text_copied"] is False
    assert "identifier_withheld" in draft["do_not_rely_reasons"]
    assert all(row["fact_key"] != "what_happened" for row in draft["sentences"])
    assert any(row["fact_key"] == "next_step" for row in draft["sentences"])


def test_a_proposed_sentence_that_repeats_the_identifier_is_not_copied():
    events = four_events()
    draft = summarise(
        case(events),
        AS_OF,
        proposed_sentences=[
            {
                "sentence_id": "P1",
                "fact_key": "what_happened",
                "text": f"NINO {NINO} was on the form.",
                "citation": {"event_id": "E1", "paragraph": 1, "line_start": 1, "line_end": 1},
            }
        ],
    )
    assert NINO not in json.dumps(draft)
    assert draft["sentences"][0]["verdict"] == "identifier_withheld"
    assert draft["sentences"][0]["text"] == "[not copied: a UK identifier was in this sentence]"
    assert draft["summary"]["failure_count"] == 1
