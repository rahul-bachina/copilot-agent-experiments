"""Live-looking chain identifiers are omitted and not copied."""

import json
from datetime import date

from tests.support import load_example

from src.addresses import accept_token
from src.investigate import investigate


def test_only_synth_prefixes_are_accepted():
    assert accept_token("SYNTH-ADDR-CUSTOMER-014", "address") == "SYNTH-ADDR-CUSTOMER-014"
    assert accept_token("SYNTH-TX-0A11B2", "tx") == "SYNTH-TX-0A11B2"
    assert accept_token("0x" + "ab" * 20, "address") is None
    assert accept_token("bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kygt080", "address") is None
    assert accept_token("1BoatSLRHtKNngkdXEeobR76b53LETtpyT", "address") is None


def test_real_looking_tokens_are_absent_from_the_draft():
    case = load_example()
    eth = "0x" + "ab" * 20
    btc = "1BoatSLRHtKNngkdXEeobR76b53LETtpyT"
    case["alert"]["hops"][0]["to_address"] = eth
    case["alert"]["hops"][0]["tx_hash"] = btc
    draft = investigate(case, as_of=date(2026, 10, 29))
    blob = json.dumps(draft)
    assert eth not in blob
    assert btc not in blob
    assert draft["omitted_identifiers"]
    assert all(item["reason"] == "not_a_synthetic_token" for item in draft["omitted_identifiers"])
    assert "value" not in json.dumps(draft["omitted_identifiers"])
