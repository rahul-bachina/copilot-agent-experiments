"""Post, reply, react, mention, and forward are not tools."""

import pytest

from digest import (
    DigestForbidden,
    forward_message,
    mention_user,
    post_message,
    react_message,
    reply_message,
    run,
)
from support import bundle, message, review


@pytest.mark.parametrize(
    "fn",
    [post_message, reply_message, react_message, mention_user, forward_message],
)
def test_side_effect_functions_raise(fn):
    with pytest.raises(DigestForbidden):
        fn()


def test_confirmation_cannot_ask_for_a_post():
    export = bundle([message("SYN-MSG-1", "We decided to keep the hours.")])
    asked = review()
    asked["decision"] = "post"
    refused = run(export, "2026-11-12", asked)
    assert refused["digest_produced"] is False
    assert refused["scope_confirmation"]["reason"] == "prohibited_decision"
    assert refused["flags"]["posted"] is False
    assert refused["human_approval"] is None


def test_a_payload_key_cannot_set_posted():
    export = bundle([message("SYN-MSG-1", "We decided to keep the hours.")])
    export["posted"] = True
    export["human_approval"] = {"approved": True}
    produced = run(export, "2026-11-12", review())
    assert produced["flags"]["posted"] is False
    assert produced["human_approval"] is None
    assert "posted" in produced["stripped_keys"]
