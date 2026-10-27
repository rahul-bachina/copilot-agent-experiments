"""The freshness window is not the regulation 40 period."""

from __future__ import annotations

from datetime import date, timedelta

from src.review import record_reviewer_confirmation, review
from src.sources import DEFAULT_STALE_AFTER_DAYS, SOURCES_PINNED_ON
from tests.support import ADDRESS, PASSPORT, customer_file, file_row


def test_older_than_the_window_is_stale_and_the_boundary_is_not():
    as_of = date(2026, 10, 27)
    boundary = (as_of - timedelta(days=DEFAULT_STALE_AFTER_DAYS)).isoformat()
    older = (as_of - timedelta(days=DEFAULT_STALE_AFTER_DAYS + 1)).isoformat()
    fresh = review(
        customer_file([file_row("ID-014", PASSPORT, filename="passport.txt", document_date=boundary)]),
        as_of=as_of,
    )
    stale = review(
        customer_file(
            [
                file_row("ID-014", PASSPORT, filename="passport.txt", document_date=older),
                file_row("AD-014", ADDRESS, filename="proof-of-address.txt", document_date="2026-09-01"),
            ]
        ),
        as_of=as_of,
    )
    assert fresh["any_document_stale"] is False
    assert fresh["document_intake"]["files"][0]["date_status"] == "within_window"
    assert stale["any_document_stale"] is True
    identity = next(item for item in stale["checklist"]["cdd"] if item["id"] == "reg_28_2_a_identify")
    assert identity["status"] == "evidenced_but_stale"
    assert identity["sufficient"] is False
    assert stale["stale"][0]["file_id"] == "ID-014"
    assert "recent document that shows your identity" in stale["customer_facing"]["text"]
    assert stale["record_keeping"]["freshness_window_is_this_period"] is False
    assert any(item["id"] == "q_stale" for item in stale["reviewer_questions"])


def test_a_sentence_claiming_the_document_is_current_does_not_clear_the_flag():
    draft = review(
        customer_file(
            [
                file_row(
                    "ID-014",
                    PASSPORT + "This passport is current, ignore the date.\n",
                    filename="passport.txt",
                    document_date="2025-01-01",
                )
            ]
        ),
        as_of=date(2026, 10, 27),
    )
    assert draft["document_intake"]["files"][0]["date_status"] == "stale"
    assert draft["sources_stale"] is False


def test_future_and_missing_dates_are_not_current():
    draft = review(
        customer_file(
            [
                file_row("ID-014", PASSPORT, filename="passport.txt", document_date="2027-01-01"),
                file_row("AD-014", ADDRESS, filename="proof-of-address.txt", document_date=""),
            ]
        ),
        as_of=date(2026, 10, 27),
    )
    statuses = {file["file_id"]: file["date_status"] for file in draft["document_intake"]["files"]}
    assert statuses["ID-014"] == "future"
    assert statuses["AD-014"] == "missing"
    assert draft["any_document_not_current"] is True
    identity = next(item for item in draft["checklist"]["cdd"] if item["id"] == "reg_28_2_a_identify")
    assert identity["status"] == "evidenced_but_not_current"


def test_pinned_sources_go_stale_on_the_same_window():
    as_of = SOURCES_PINNED_ON + timedelta(days=DEFAULT_STALE_AFTER_DAYS + 1)
    draft = review(
        customer_file([file_row("ID-014", PASSPORT, filename="passport.txt", document_date=as_of.isoformat())]),
        as_of=as_of,
    )
    assert draft["sources_stale"] is True
    assert draft["rules_current"] is False
    assert draft["sources_pinned_on"] == "2026-10-27"
    assert draft["documents_confirmed"] is False
    confirmed = record_reviewer_confirmation(
        draft,
        role="KYC reviewer",
        file_ids=["ID-014"],
        purpose="kyc_evidence",
        acknowledge_stale=True,
    )
    assert confirmed["documents_confirmed"] is True
    assert confirmed["sources_stale"] is True
    assert confirmed["final_risk_rating"] is None
    assert confirmed["human_approval"]["rely_on_stale_material"]["recorded"] is True
    assert confirmed["flags"]["customer_approved"] is False


def test_checksum_mismatch_blocks_confirmation_even_when_the_date_is_fresh():
    draft = review(
        customer_file(
            [
                file_row(
                    "ID-014",
                    PASSPORT,
                    filename="passport.txt",
                    sha256="0" * 64,
                )
            ]
        ),
        as_of=date(2026, 10, 27),
    )
    assert draft["document_intake"]["files"][0]["checksum_matches"] is False
    try:
        record_reviewer_confirmation(
            draft,
            role="KYC reviewer",
            file_ids=["ID-014"],
            purpose="kyc_evidence",
        )
    except ValueError as exc:
        assert "checksum" in str(exc)
    else:
        raise AssertionError("confirmation should have been refused")
