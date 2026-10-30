"""Experiments 03, 04, and 08 are called. Their decisions are not copied."""

from tests.support import draft_sample


def test_neighbours_are_called_and_do_not_decide():
    draft = draft_sample()
    exp04 = draft["experiment_04"]
    assert exp04["called"] is True
    assert exp04["gap_register_run"] is False
    assert exp04["catalogue_id"] == "UK02"
    assert exp04["marketing_page_last_verified_by_experiment_04"] == "2026-10-24"
    gateway = draft["identifier_gateway"]
    assert gateway["catalogue_id"] == "O005"
    assert gateway["output_is_anonymised"] is False
    exp03 = draft["experiment_03"]
    assert exp03["catalogue_id"] == "G010"
    assert exp03["inventory_attached"] is True
    assert exp03["status_applied"] is False
    assert exp03["manifest_approved"] is False
    if exp03["manifest_generator_called"]:
        assert exp03["approve_true_refused"] is True
        assert exp03["manifest_autonomy"] == "A0"
    else:
        assert exp03["manifest_generator_reason"]
