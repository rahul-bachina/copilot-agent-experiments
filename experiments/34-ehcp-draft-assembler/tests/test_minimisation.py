"""Synthetic children only. Identifiers are withheld, not anonymised."""

import json

from src.assemble import AssemblerError, evaluate
from tests.support import AS_OF, bundle


def test_a_bundle_that_is_not_synthetic_is_refused_without_the_text():
    source = bundle()
    source["synthetic"] = False
    source["reports"][0]["paragraphs"][0]["text"] = "Real child Rowan Hale lives at 1 High Street."
    draft = evaluate(source, as_of=AS_OF)
    assert draft["refused"] is True
    assert draft["text_copied"] is False
    assert "Rowan" not in json.dumps(draft)
    assert "High Street" not in json.dumps(draft)


def test_a_name_field_is_refused_without_copying_the_value():
    source = bundle()
    source["child_name"] = "Rowan Hale"
    draft = evaluate(source, as_of=AS_OF)
    assert draft["refused"] is True
    assert "Rowan" not in json.dumps(draft)


def test_a_labelled_nhs_number_is_withheld_and_the_output_is_not_anonymised():
    source = bundle()
    source["reports"][2]["paragraphs"][0]["text"] = "The NHS number 999 123 4567 was typed into this advice."
    draft = evaluate(source, as_of=AS_OF)
    assert draft["refused"] is False
    assert draft["pii_gateway"]["called"] is True
    assert draft["pii_gateway"]["output_is_anonymised"] is False
    assert draft["pii_gateway"]["agent_may_release"] is False
    assert draft["pii_gateway"]["finding_count"] >= 1
    assert draft["sections"]["C"]["lines"] == []
    blob = json.dumps(draft)
    assert "999 123 4567" not in blob
    assert "9991234567" not in blob
    assert draft["output_is_anonymised"] is False
    assert draft["do_not_rely"] is True


def test_too_many_reports_are_refused_before_a_draft_is_returned():
    source = bundle()
    while len(source["reports"]) <= 12:
        extra = json.loads(json.dumps(source["reports"][0]))
        extra["report_id"] = f"R-EXTRA-{len(source['reports'])}"
        source["reports"].append(extra)
    try:
        evaluate(source, as_of=AS_OF)
    except AssemblerError as exc:
        assert "12" in str(exc)
        assert "likes drawing" not in str(exc)
        return
    raise AssertionError("expected AssemblerError")
