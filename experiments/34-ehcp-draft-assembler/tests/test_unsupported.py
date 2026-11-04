"""A statement that is not in the cited paragraph is not copied."""

import json

from src.assemble import assemble
from tests.support import AS_OF, bundle


def test_an_unsupported_statement_is_flagged_and_absent_from_the_draft():
    draft = assemble(bundle(), as_of=AS_OF)
    row = draft["unsupported_statements"][0]
    assert row == {
        "statement_id": "S-UNSUP",
        "reason": "not_in_cited_paragraph",
        "copied": False,
    }
    assert "one-to-one" not in json.dumps(draft)
    quotes = [line["quote"] for line in draft["sections"]["F"]["lines"]]
    assert quotes == ["A quiet space for a short instruction was described in this advice."]


def test_a_statement_with_no_citation_is_not_copied():
    source = bundle()
    source["candidate_statements"] = [
        {"statement_id": "S-NONE", "text": "Child A needs a plan written by the tool."}
    ]
    draft = assemble(source, as_of=AS_OF)
    assert draft["unsupported_statements"] == [
        {"statement_id": "S-NONE", "reason": "missing_citation", "copied": False}
    ]
    assert "written by the tool" not in json.dumps(draft)


def test_a_claim_that_is_not_in_the_paragraph_is_not_used():
    source = bundle()
    source["reports"][1]["paragraphs"][0]["claims"] = [
        {"key": "instruction_following", "value": "reads a chapter unaided"}
    ]
    draft = assemble(source, as_of=AS_OF)
    assert draft["conflicts"] == []
    assert draft["unsupported_claims"][0]["key"] == "instruction_following"
    assert "unaided" not in json.dumps(draft)
