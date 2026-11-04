"""The agent does not decide. The checker fails a sentence that tries to."""

import json
from pathlib import Path

import pytest

from src.summarise import (
    SummaryForbidden,
    accept_summary,
    decide_disclosure,
    find_credibility,
    main,
    recommend_outcome,
    record_sentence_review,
    send_external,
    summarise,
    write_production_record,
)
from tests.support import (
    BLUE,
    INTERVIEW,
    JOURNEY,
    KEY,
    bundle,
    blue_document,
    cite,
    document,
    paragraph,
)


AS_OF = "2026-11-04"


@pytest.mark.parametrize(
    "function",
    [
        recommend_outcome,
        decide_disclosure,
        find_credibility,
        accept_summary,
        send_external,
        write_production_record,
    ],
)
def test_prohibited_functions_raise(function):
    with pytest.raises(SummaryForbidden):
        function()


def test_outcome_disclosure_and_credibility_sentences_fail_once_each():
    proposals = [
        ("P1", "The decision-maker should charge the suspect.", "outcome_recommendation"),
        ("P2", "Disclose all unused material to the defence.", "disclosure_decision"),
        ("P3", "The witness is credible.", "credibility_finding"),
    ]
    # Each proposal is its own draft so failure_count stays one sentence.
    for sentence_id, text, _code in proposals:
        draft = summarise(
            bundle([blue_document()], expected=["sighting"]),
            AS_OF,
            proposed_sentences=[
                {"sentence_id": sentence_id, "text": text, "citation": cite("SYN-NOTE-01", 1)}
            ],
        )
        assert draft["sentences"][0]["verdict"] == "prohibited_action"
        assert draft["summary"]["failure_count"] == 1
        assert "span_does_not_support" in draft["sentences"][0]["other_failures"]
        assert draft["case_outcome"] is None
        assert draft["disclosure_decision"] is None
        assert draft["credibility_finding"] is None
        assert draft["summary_accepted_as_reading_aid"] is False


def test_matter_type_does_not_select_an_outcome():
    asylum = document(
        "SYN-ASYLUM-01",
        [paragraph(1, JOURNEY, "journey"), paragraph(2, INTERVIEW, "interview")],
        reviewed_on="2026-10-01",
        document_date="2026-09-02",
    )
    barring = document(
        "SYN-BAR-01",
        [paragraph(1, KEY, "event")],
        reviewed_on="2026-10-02",
        document_date="2026-09-03",
    )
    asylum_draft = summarise(
        bundle(
            [asylum],
            matter_type="asylum_case_reading",
            expected=["journey", "interview"],
            organisation="Northfen Casework Unit (fictional, not the Home Office)",
            bundle_id="SYN-ASYLUM-01",
        ),
        AS_OF,
    )
    barring_draft = summarise(
        bundle(
            [barring],
            matter_type="barring_referral_reading",
            expected=["event"],
            organisation="Example Barring Desk (fictional, not the Disclosure and Barring Service)",
            bundle_id="SYN-BAR-01",
        ),
        AS_OF,
    )
    assert asylum_draft["checker_passed"] is True
    assert asylum_draft["do_not_rely"] is False
    assert asylum_draft["case_outcome"] is None
    assert barring_draft["checker_passed"] is True
    assert barring_draft["do_not_rely"] is False
    assert barring_draft["credibility_finding"] is None
    assert "grant" not in json.dumps(asylum_draft["sentences"]).casefold()
    assert "barred" not in json.dumps(barring_draft["sentences"]).casefold()


def test_non_synthetic_and_unknown_matter_type_are_refused():
    with pytest.raises(ValueError, match="synthetic"):
        summarise(bundle([blue_document()], synthetic=False), AS_OF)
    with pytest.raises(ValueError, match="matter type"):
        summarise(bundle([blue_document()], matter_type="charging_decision"), AS_OF)


def test_review_requires_the_decision_maker_and_does_not_decide_the_case():
    note = document("SYN-CLEAN-01", [paragraph(1, BLUE, "sighting")])
    draft = summarise(bundle([note], expected=["sighting"]), AS_OF)
    assert draft["do_not_rely"] is False
    with pytest.raises(SummaryForbidden):
        record_sentence_review(draft, role="Officer", name="Synthetic Reviewer R-01", reviews=[])
    with pytest.raises(SummaryForbidden):
        record_sentence_review(
            draft,
            role="Decision-maker",
            name="Decision-maker",
            reviews=[{"sentence_id": "S1", "mark": "read"}],
        )
    with pytest.raises(SummaryForbidden):
        record_sentence_review(draft, role="Decision-maker", name="Synthetic Reviewer R-01", reviews=[])
    reviewed = record_sentence_review(
        draft,
        role="Decision-maker",
        name="Synthetic Reviewer R-01",
        reviews=[{"sentence_id": draft["sentences"][0]["sentence_id"], "mark": "read"}],
    )
    assert reviewed["sentences_reviewed_by_decision_maker"] is True
    assert reviewed["summary_accepted_as_reading_aid"] is True
    assert reviewed["case_outcome"] is None
    assert reviewed["disclosure_decision"] is None
    assert reviewed["credibility_finding"] is None
    assert reviewed["outcome_recommended"] is False
    assert reviewed["summary_is_not_a_decision"] is True
    with pytest.raises(SummaryForbidden):
        recommend_outcome(reviewed)
    assert summarise(bundle([note], expected=["sighting"]), AS_OF)["summary_accepted_as_reading_aid"] is False


def test_a_failed_sentence_cannot_be_marked_as_a_reading_aid():
    draft = summarise(
        bundle([blue_document()], expected=["sighting"]),
        AS_OF,
        proposed_sentences=[
            {"sentence_id": "P1", "text": "The witness is not credible.", "citation": cite("SYN-NOTE-01", 1)}
        ],
    )
    reviewed = record_sentence_review(
        draft,
        role="Decision-maker",
        name="Synthetic Reviewer R-01",
        reviews=[{"sentence_id": "P1", "mark": "noted_failure"}],
    )
    assert reviewed["sentences_reviewed_by_decision_maker"] is True
    assert reviewed["summary_accepted_as_reading_aid"] is False
    assert reviewed["credibility_finding"] is None


def test_cli_prohibited_flags_exit_without_writing(tmp_path: Path):
    bundle_path = tmp_path / "bundle.json"
    bundle_path.write_text(
        json.dumps(bundle([blue_document()], expected=["sighting"])),
        encoding="utf-8",
    )
    for flag in (
        "--recommend-outcome",
        "--decide-disclosure",
        "--find-credible",
        "--accept-summary",
        "--send",
        "--write-record",
    ):
        code = main(["--bundle", str(bundle_path), "--as-of", AS_OF, flag])
        assert code == 2


def test_differences_name_experiment_18_and_experiment_29():
    draft = summarise(bundle([blue_document()], expected=["sighting"]), AS_OF)
    assert "index" in draft["differences"]["experiment_18"].lower() or "page order" in draft["differences"]["experiment_18"]
    assert "Experiment 18" in draft["differences"]["experiment_18"]
    assert "Experiment 29" in draft["differences"]["experiment_29"]
    assert "contiguous" in draft["differences"]["experiment_29"]
    assert draft["model_called"] is False
    assert draft["network_called"] is False
    assert draft["foundry_called"] is False
    assert draft["actions_taken"] == []
