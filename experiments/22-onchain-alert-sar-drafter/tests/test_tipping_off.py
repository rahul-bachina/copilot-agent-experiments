"""No customer-facing wording is drafted."""

import json
from datetime import date

from tests.support import draft_sample, load_example

from src.customer_guard import empty_customer_facing
from src.investigate import contact_customer, investigate


def test_requested_customer_message_is_not_echoed():
    draft = draft_sample()
    blob = json.dumps(draft)
    assert "CUSTOMER-LEAK-PHRASE-99" not in blob
    assert draft["customer_facing"]["drafted"] is False
    assert draft["customer_facing"]["text"] is None
    assert draft["customer_facing"]["request_echoed"] is False
    assert draft["customer_facing"]["may_be_sent_by_agent"] is False
    assert draft["customer_facing"]["message_requested"] is True
    assert draft["customer_told"] is False
    assert draft["investigation_note"]["not_for_the_customer"] is True


def test_guard_has_no_text_even_when_no_message_was_requested():
    case = load_example()
    del case["requested_customer_message"]
    draft = investigate(case, as_of=date(2026, 10, 29))
    assert draft["customer_facing"] == empty_customer_facing(message_requested=False)


def test_contact_customer_always_raises():
    draft = draft_sample()
    try:
        contact_customer(draft, "Hello")
    except RuntimeError as exc:
        assert "customer" in str(exc).lower()
    else:
        raise AssertionError("expected a refusal")
    assert draft["customer_facing"]["text"] is None
