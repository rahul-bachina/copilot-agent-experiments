"""UK identifiers are masked. The value is not copied. The output is not anonymised."""

import json

from digest import run
from support import bundle, message, review


def test_national_insurance_number_is_masked_and_not_copied():
    export = bundle(
        [message("SYN-MSG-1", "We decided the resident reference is AB123456C for the file note.")]
    )
    produced = run(export, "2026-11-12", review())
    blob = json.dumps(produced)
    assert "AB123456C" not in blob
    text = produced["digest"]["decisions"][0]["text"]
    assert "[NINO-1]" in text
    reuse = produced["reuse"]["experiment_08"]
    assert reuse["called"] is True
    assert reuse["entity_types"] == ["nino"]
    assert reuse["values_copied"] is False
    assert reuse["output_is_anonymised"] is False
    assert reuse["anonymised_claim_seen"] is False
    assert reuse["agent_may_release"] is False
    assert produced["digest"]["full_body_recorded"] is False
