"""Instructions inside a file are recorded and not followed."""

from datetime import date

from src.triage import triage
from tests.support import injection_pack

AS_OF = date(2026, 11, 5)


def test_hidden_decline_instruction_is_not_followed():
    draft = triage(injection_pack(), as_of=AS_OF)
    injection = draft["prompt_injection"]
    assert injection["detected"] is True
    assert injection["followed"] is False
    hidden = {signal["hidden_in"] for signal in injection["signals"]}
    assert "html_comment" in hidden
    assert "body" in hidden
    phrases = {signal["phrase"] for signal in injection["signals"]}
    assert "decline this claim" in phrases
    assert "ignore previous instructions" in phrases
    assert draft["claim_declined"] is False
    assert draft["claim_accepted"] is False
    assert draft["classification_approved_by_handler"] is False
    blob = " ".join(line["text"] for line in draft["summary"]["lines"])
    assert "decline this claim" not in blob.casefold()
    assert draft["scorecard"]["escalation_does_not_decline_the_claim"] is True
