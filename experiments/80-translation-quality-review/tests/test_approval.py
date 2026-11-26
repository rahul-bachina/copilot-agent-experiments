"""Ownership is bound to the agent-held copy. A later edit is refused."""

import json

from src.review import (
    ReviewForbidden,
    _hash,
    approve_translation,
    held_record,
    overwrite_document,
    pinned_directory,
    prepare_review,
    publish_translation,
    record_high_risk_validated,
    record_route_seen,
    record_translation_owned,
    reset_held,
    send_translation,
)

AS_OF = "2026-11-26"


def setup_function():
    reset_held()


def _clean():
    return prepare_review(
        {
            "synthetic": True,
            "review_id": "TRN-8301",
            "reviewer_ref": "REV-8001",
            "source_language": "en",
            "target_language": "en",
            "document_kind": "guidance",
            "source": {"segments": [{"segment_id": "s1", "number": "1", "text": "The office opens at nine."}]},
            "target": {"segments": [{"segment_id": "s1", "number": "1", "text": "The office opens at nine."}]},
        },
        as_of=AS_OF,
    )


def _risky():
    text = "You must apply for housing benefit."
    return prepare_review(
        {
            "synthetic": True,
            "review_id": "TRN-8302",
            "reviewer_ref": "REV-8001",
            "source_language": "en",
            "target_language": "en",
            "document_kind": "public_information",
            "source": {"segments": [{"segment_id": "s1", "number": "1", "text": text}]},
            "target": {"segments": [{"segment_id": "s1", "number": "1", "text": text}]},
        },
        as_of=AS_OF,
    )


def _own(result, **extra):
    approval = {
        "item": "translation-owned",
        "decision": "own",
        "approver_ref": "REV-8001",
        "review_id": result["review_id"],
        "content_hash": result["content_hash"],
        "source_document_hash": result["document_hashes"]["source"],
        "target_document_hash": result["document_hashes"]["target"],
        "translation_owned_by_reviewer": True,
    }
    for key in result["required_acknowledgements"]:
        approval[key] = True
    approval.update(extra)
    return record_translation_owned(result, pinned_directory(), approval)


def _see(result):
    return record_route_seen(
        result,
        pinned_directory(),
        {
            "item": "route-seen",
            "decision": "seen",
            "approver_ref": "REV-8001",
            "review_id": result["review_id"],
            "content_hash": result["content_hash"],
        },
    )


def _validate(result):
    return record_high_risk_validated(
        result,
        pinned_directory(),
        {
            "item": "high-risk",
            "decision": "validated",
            "approver_ref": "REV-8001",
            "review_id": result["review_id"],
            "content_hash": result["content_hash"],
            "source_document_hash": result["document_hashes"]["source"],
            "target_document_hash": result["document_hashes"]["target"],
            "validated_by_reviewer": True,
        },
    )


def test_a_clean_ownership_does_not_publish():
    result = _clean()
    owned = _own(result)
    assert owned["blocked_reason"] is None
    assert owned["translation_owned"] is True
    assert owned["published"] is False
    assert owned["sent"] is False
    assert owned["overwritten"] is False
    assert owned["translation_approved_by_agent"] is False
    assert owned["human_approval"]["approves_translation"] is False
    assert owned["human_approval"]["content_hash"] == result["content_hash"]


def test_high_risk_needs_the_route_and_the_validation_before_ownership():
    result = _risky()
    refused = _own(result)
    assert refused["translation_owned"] is False
    assert refused["blocked_reason"] == "route_not_seen"
    seen = _see(result)
    assert seen["route_seen"] is True
    assert seen["published"] is False
    too_soon = _own(seen)
    assert too_soon["blocked_reason"] == "high_risk_not_validated"
    validated = _validate(seen)
    assert validated["high_risk_validated"] is True
    assert validated["human_approval"]["approves_translation"] is False
    owned = _own(validated)
    assert owned["translation_owned"] is True
    assert owned["published"] is False
    assert owned["sent"] is False
    assert owned["overwritten"] is False


def test_eight_post_review_edits_are_refused():
    original = _clean()
    held_before = held_record(original["review_id"])["content_hash"]
    edits = {
        "excerpt": lambda row: row["excerpts"][0].__setitem__("excerpt", "tampered"),
        "flags": lambda row: row.__setitem__("flags", [{"type": "tampered"}]),
        "legal_hold": lambda row: row.__setitem__("legal_hold", not row["legal_hold"]),
        "retention": lambda row: row.__setitem__("retention", ["tampered label"]),
        "marking": lambda row: row["marking"].__setitem__("applied", "SECRET"),
        "injection": lambda row: row["prompt_injection"].__setitem__("signals", ["tampered"]),
        "suppression": lambda row: row["suppression"].__setitem__("applied", not row["suppression"]["applied"]),
        "route_seen": lambda row: row.__setitem__("route_seen", True),
        "acknowledgements": lambda row: row.__setitem__("required_acknowledgements", []),
        "no_issues": lambda row: row.__setitem__("no_issues", False),
        "glossary": lambda row: row["glossary_report"].__setitem__("applied", True),
    }
    assert len(edits) >= 8
    for name, edit in edits.items():
        tampered = json.loads(json.dumps(original))
        edit(tampered)
        tampered["content_hash"] = _hash(tampered)
        assert tampered["content_hash"] != held_before, name
        refused = _own(tampered)
        assert refused["translation_owned"] is False, name
        assert refused["blocked_reason"] in {"caller_rehash_rejected", "content_tampered"}, name
        assert refused["published"] is False
        assert held_record(original["review_id"])["content_hash"] == held_before
        refused_old = _own(tampered, content_hash=original["content_hash"])
        assert refused_old["translation_owned"] is False, name


def test_a_string_acknowledgement_is_not_true():
    result = _clean()
    refused = _own(result, segments_seen="true")
    assert refused["translation_owned"] is False
    assert refused["blocked_reason"] == "segments_seen_not_boolean_true"


def test_a_guest_an_inactive_reviewer_and_a_language_gap_cannot_own_it():
    result = _clean()
    assert _own(result, approver_ref="GST-8003")["translation_owned"] is False
    assert _own(result, approver_ref="INA-8004")["translation_owned"] is False
    welsh = prepare_review(
        {
            "synthetic": True,
            "review_id": "TRN-8303",
            "reviewer_ref": "ENG-8005",
            "source_language": "en",
            "target_language": "cy",
            "document_kind": "guidance",
            "source": {"segments": [{"segment_id": "s1", "number": "1", "text": "The office opens at nine."}]},
            "target": {"segments": [{"segment_id": "s1", "number": "1", "text": "Mae'r swyddfa ar agor am naw."}]},
        },
        as_of=AS_OF,
    )
    seen = _see(welsh) if False else record_route_seen(
        welsh,
        pinned_directory(),
        {
            "item": "route-seen",
            "decision": "seen",
            "approver_ref": "ENG-8005",
            "review_id": welsh["review_id"],
            "content_hash": welsh["content_hash"],
        },
    )
    assert seen["blocked_reason"] == "language_not_on_directory"


def test_a_caller_directory_is_not_the_pinned_directory():
    result = _clean()
    forged = {"people": [{"employee_ref": "REV-8001", "role": "bilingual_reviewer", "languages": ["en"], "clearance": "TOP SECRET", "active": True, "guest": False}]}
    refused = record_translation_owned(
        result,
        forged,
        {
            "item": "translation-owned",
            "decision": "own",
            "approver_ref": "REV-8001",
            "review_id": result["review_id"],
            "content_hash": result["content_hash"],
            "source_document_hash": result["document_hashes"]["source"],
            "target_document_hash": result["document_hashes"]["target"],
            "translation_owned_by_reviewer": True,
            "pins_seen": True,
            "segments_seen": True,
        },
    )
    assert refused["translation_owned"] is False
    assert refused["blocked_reason"] == "caller_directory_not_used"
    assert refused["caller_directory_applied"] is False


def test_a_rehash_after_ownership_does_not_replace_the_held_copy():
    result = _clean()
    owned = _own(result)
    held_after = held_record(owned["review_id"])["content_hash"]
    tampered = json.loads(json.dumps(owned))
    tampered["published"] = True
    tampered["content_hash"] = _hash(tampered)
    refused = _own(tampered)
    assert refused["translation_owned"] is False
    assert refused["published"] is False
    assert held_record(owned["review_id"])["content_hash"] == held_after


def test_prohibited_actions_raise():
    for fn in (publish_translation, send_translation, overwrite_document, approve_translation):
        try:
            fn()
        except ReviewForbidden:
            continue
        raise AssertionError(fn.__name__)
