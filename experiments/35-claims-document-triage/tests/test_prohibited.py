"""Outcome paths always raise. The command exits 2 and writes nothing."""

import json
from datetime import date

import pytest

from src.triage import (
    ClaimForbidden,
    NotSynthetic,
    accept_claim,
    decline_claim,
    main,
    settle_claim,
    tell_customer,
    triage,
    write_claims_system,
)
from src.scorecard import ScoreForbidden, approve_thresholds, call_foundry_evaluator, decline_from_score
from tests.support import base_pack, not_synthetic_pack, nino_pack

AS_OF = date(2026, 11, 5)


@pytest.mark.parametrize(
    "function",
    [
        accept_claim,
        decline_claim,
        settle_claim,
        tell_customer,
        write_claims_system,
        approve_thresholds,
        call_foundry_evaluator,
        decline_from_score,
    ],
)
def test_prohibited_functions_raise(function):
    with pytest.raises((ClaimForbidden, ScoreForbidden)) as caught:
        function()
    message = str(caught.value).casefold()
    assert "token-not-in-the-refusal" not in message


def test_not_synthetic_refuses_without_the_body():
    with pytest.raises(NotSynthetic) as caught:
        triage(not_synthetic_pack(), as_of=AS_OF)
    assert "TOKEN-NOT-IN-THE-REFUSAL" not in str(caught.value)


def test_identifier_is_not_copied_into_the_draft():
    draft = triage(nino_pack(), as_of=AS_OF)
    invoice = next(file for file in draft["files"] if file["file_id"] == "invoice")
    assert invoice["withheld_for_identifier"] is True
    assert invoice["pii_finding_count"] > 0
    assert "nino" in invoice["pii_entity_types"]
    blob = json.dumps(draft)
    assert "QQ 12 34 56 A" not in blob
    assert "QQ123456A" not in blob
    assert draft["output_is_anonymised"] is False
    assert draft["claim_declined"] is False
    assert not any(line["source_file_id"] == "invoice" for line in draft["summary"]["lines"])


@pytest.mark.parametrize(
    "flag",
    [
        "--accept-claim",
        "--decline-claim",
        "--settle-claim",
        "--tell-customer",
        "--write-claims-system",
        "--approve-thresholds",
    ],
)
def test_cli_prohibited_flag_exits_2(flag, capsys):
    code = main(["--pack", "examples/sample_pack.json", "--as-of", "2026-11-05", flag])
    assert code == 2
    captured = capsys.readouterr()
    assert captured.out == ""


def test_clean_cli_exits_0(capsys):
    code = main(["--pack", "examples/sample_pack.json", "--as-of", "2026-11-05"])
    assert code == 0
    draft = json.loads(capsys.readouterr().out)
    assert draft["claim_declined"] is False
    assert draft["classification"]["proposed_class"] == "escape_of_water"
