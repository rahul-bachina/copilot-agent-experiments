"""Two advice reports can disagree. The assembler does not pick a winner."""

from src.assemble import assemble
from tests.support import AS_OF, bundle


def test_different_claim_values_are_kept_and_not_resolved():
    draft = assemble(bundle(), as_of=AS_OF)
    assert len(draft["conflicts"]) == 1
    conflict = draft["conflicts"][0]
    assert conflict["id"] == "conflict:instruction_following"
    assert conflict["resolved"] is False
    assert conflict["chosen_value"] is None
    values = {row["value"] for row in conflict["values"]}
    assert values == {
        "finds it hard to follow a whole-class instruction",
        "can follow a short instruction given to them alone",
    }
    assert len(draft["sections"]["B"]["lines"]) == 2


def test_the_same_claim_value_is_not_a_conflict():
    source = bundle()
    shared = "finds it hard to follow a whole-class instruction"
    source["reports"][1]["paragraphs"][0]["text"] = shared
    source["reports"][1]["paragraphs"][0]["claims"][0]["value"] = shared
    source["reports"][3]["paragraphs"][0]["text"] = shared
    source["reports"][3]["paragraphs"][0]["claims"][0]["value"] = shared
    draft = assemble(source, as_of=AS_OF)
    assert draft["conflicts"] == []
