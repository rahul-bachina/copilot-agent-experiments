"""High-risk functions always raise. Payload keys cannot set them."""

from datetime import date

from tests.support import draft_sample, load_example

from src.investigate import (
    assign_glossary_code,
    file_with_nca,
    freeze_account,
    investigate,
    move_crypto,
    record_mlro_decision,
    record_suspicion,
    request_daml,
)


def test_prohibited_keys_are_ignored():
    case = load_example()
    assert case["sar_filed"] is True
    assert case["mlro_decision"] == "file"
    draft = investigate(case, as_of=date(2026, 10, 29))
    assert "sar_filed" in draft["prompt_injection"]["prohibited_payload_keys_ignored"]
    assert "mlro_decision" in draft["prompt_injection"]["prohibited_payload_keys_ignored"]
    assert draft["sar_filed"] is False
    assert draft["mlro_decision"] is None
    assert draft["prompt_injection"]["followed"] is False


def test_every_prohibited_function_raises(tmp_path=None):
    draft = draft_sample()
    for function in (
        file_with_nca,
        request_daml,
        freeze_account,
        move_crypto,
        record_mlro_decision,
        record_suspicion,
        assign_glossary_code,
    ):
        try:
            function(draft)
        except RuntimeError:
            pass
        else:
            raise AssertionError(function.__name__)
    assert draft["sar_filed"] is False
    assert draft["glossary_codes_assigned"] is False
    assert draft["suspicion_recorded_by_agent"] is False
