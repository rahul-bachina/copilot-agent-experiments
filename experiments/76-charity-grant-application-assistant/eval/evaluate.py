"""Deterministic smoke test. Not a model evaluation.

Each case is one row. Paraphrase recall is a separate block and is not
added to the case total.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.cues import carve_out, category_hit, distress_hit  # noqa: E402
from src.grant import (  # noqa: E402
    GrantForbidden,
    contact_funder,
    pinned_sources,
    prepare_application,
    record_applicant_approval,
    record_route_seen,
    reset_staging,
    submit_application,
)
from src.mapping import supports_registered_charity  # noqa: E402
from src.paraphrases import NEGATIVES, POSITIVES  # noqa: E402


def _hit(category: str, text: str) -> bool:
    if category == "distress":
        return distress_hit(text)
    if category == "carve_out":
        return carve_out(text)
    if category == "registered_charity":
        return supports_registered_charity(text)
    return category_hit(text, category)


def _request(**extra) -> dict:
    payload = json.loads((ROOT / "examples" / "sample_request.json").read_text(encoding="utf-8"))
    payload.update(extra)
    return payload


def _case(case_id: str, passed: bool, detail: str) -> dict:
    return {"case_id": case_id, "passed": passed, "failed": not passed, "error": False, "detail": detail}


def _approval(result, **extra) -> dict:
    payload = {
        "item": "grant-package",
        "decision": "approve-draft",
        "approver_ref": "APP-7601",
        "application_id": result["application_id"],
        "content_hash": result["content_hash"],
        "pins_seen": True,
        "sources_seen": True,
        "dates_seen": True,
        "criteria_seen": True,
    }
    payload.update(extra)
    return payload


def _run_cases() -> list[dict]:
    cases = []
    directory = pinned_sources()["directory"]
    sample = prepare_application(_request(), as_of="2026-11-14")
    blob = json.dumps(sample)
    cases.append(
        _case(
            "sample-routes-without-leaking",
            sample["outcome"] == "route_to_human"
            and sample["human_approval"] is None
            and sample["submitted"] is False
            and sample["instructions_followed"] is False
            and sample["marking"]["applied"] == "SECRET"
            and sample["distress"]["cue_copied"] is False
            and "07700900111" not in blob
            and "frightened" not in blob
            and "TOP SECRET" not in blob
            and "9999" not in blob,
            sample["outcome"],
        )
    )
    again = prepare_application(_request(), as_of="2026-11-14")
    cases.append(_case("reproducible-hash", sample["content_hash"] == again["content_hash"], "same"))
    small = next(row for row in sample["impact_report"]["figures"] if row["source_ref"] == "ME-BEN-SMALL")
    cases.append(
        _case(
            "small-number-suppressed",
            small["suppressed"] is True
            and small["value"] is None
            and sample["impact_report"]["aggregate_includes_suppressed_cells"] is False,
            "suppressed",
        )
    )
    cases.append(
        _case(
            "hold-and-retention-kept",
            sample["legal_hold"] is True
            and "do not destroy while the hold applies" in sample["retention"]
            and "safeguarding note: do not destroy" in sample["retention"]
            and sample["secret_body_copied"] is False,
            "kept",
        )
    )
    by_id = {row["criterion_id"]: row for row in sample["eligibility"]}
    cases.append(_case("match-funding-gap", by_id["EL-MATCH"]["status"] == "not_met" and by_id["EL-MATCH"]["gap"] is True, "gap"))
    cases.append(
        _case(
            "safeguarding-gap",
            by_id["EL-SAFE"]["status"] == "not_met" and by_id["EL-SAFE"]["policy_date"] == "2025-01-15",
            "gap",
        )
    )
    cases.append(
        _case(
            "income-evidenced",
            by_id["EL-INC"]["status"] == "met" and by_id["EL-INC"]["value"] == 186400 and by_id["EL-INC"]["source_ref"] == "charity.income_gbp",
            "186400",
        )
    )
    quote = next(answer for answer in sample["answers"] if answer["question_id"] == "Q3")
    cases.append(
        _case(
            "quote-sourced",
            quote["within_limit"] is True and "ME-QUOTE-01" in quote["source_refs"] and "The Tuesday meal" in quote["text"],
            "quoted",
        )
    )
    claims = {row["claim_id"]: row for row in sample["claims"]}
    cases.append(_case("invented-figure-flagged", claims["C-FAKE"]["status"] == "unsupported" and claims["C-FAKE"]["used_in_draft"] is False, "unsupported"))
    cases.append(_case("invented-partner-flagged", claims["C-PARTNER"]["status"] == "unsupported" and "National High Street Bank" not in blob, "unsupported"))
    cases.append(
        _case(
            "word-limits",
            all(answer["within_limit"] is True and answer["word_count"] <= answer["word_limit"] for answer in sample["answers"]),
            "within",
        )
    )
    cases.append(
        _case(
            "caller-brief-ignored",
            sample["caller_brief_applied"] is False
            and sample["deadline_plan"]["deadline"] == "2027-03-31"
            and any(row["field"] == "income_under_gbp" and row["applied"] is False for row in sample["brief_diff"]),
            "pinned",
        )
    )
    cases.append(
        _case(
            "biased-not-applied",
            "biased_criteria" in sample["prompt_injection"]["signals"]
            and sample["criteria_applied"] is False
            and sample["marked_acceptable"] is False,
            "flagged",
        )
    )
    cases.append(
        _case(
            "text-approval-ignored",
            sample["approval_marker_trusted"] is False and "human_approval" in sample["ignored_request_keys"] and sample["human_approval"] is None,
            "ignored",
        )
    )
    cases.append(
        _case(
            "negation-not-inclusion",
            sample["eligibility_statement_supports_registered_charity"] is False and claims["C-MATCH"]["status"] == "gap_not_papered",
            "not-included",
        )
    )
    past = prepare_application(_request(), as_of="2027-04-01")
    cases.append(
        _case(
            "past-deadline",
            past["deadline_plan"]["past"] is True and past["as_of"] == "2027-04-01" and past["coerced"] is False,
            "past",
        )
    )
    unreadable = prepare_application(_request(), as_of="soon")
    cases.append(
        _case(
            "unparseable-not-coerced",
            unreadable["outcome"] == "unreadable_date" and unreadable["coerced"] is False and past["deadline_plan"]["unparseable_offset"] is True,
            "flagged",
        )
    )
    reset_staging()
    seen = record_route_seen(
        sample,
        directory,
        {"item": "route-seen", "decision": "seen", "approver_ref": "APP-7601", "content_hash": sample["content_hash"]},
    )
    staged = record_applicant_approval(seen, directory, _approval(seen))
    cases.append(
        _case(
            "approval-stages-exact-hash",
            staged["staged"] is True and staged["submitted"] is False and staged["funder_contacted"] is False and staged["human_approval"]["content_hash"] == seen["content_hash"],
            "staged",
        )
    )
    tampered = json.loads(json.dumps(seen))
    tampered["answers"][0]["text"] = "Invented impact."
    rejected = record_applicant_approval(tampered, directory, _approval(seen))
    cases.append(_case("tampered-rejected", rejected["blocked_reason"] == "content_hash_mismatch" and rejected["staged"] is False, "rejected"))
    raised = True
    try:
        submit_application()
        raised = False
    except GrantForbidden:
        pass
    try:
        contact_funder()
        raised = False
    except GrantForbidden:
        pass
    trustee = record_applicant_approval(seen, directory, _approval(seen, approver_ref="TRS-7602"))
    cases.append(
        _case(
            "prohibited-and-wrong-role",
            raised and trustee["blocked_reason"] == "not_the_named_applicant" and trustee["submitted"] is False,
            trustee["blocked_reason"],
        )
    )
    return cases


def _paraphrase() -> dict:
    categories = {}
    for name, sentences in POSITIVES.items():
        missed = [sentence for sentence in sentences if not _hit(name, sentence)]
        false = [sentence for sentence in NEGATIVES[name] if _hit(name, sentence)]
        caught = len(sentences) - len(missed)
        categories[name] = {
            "sentences": len(sentences),
            "negatives": len(NEGATIVES[name]),
            "caught": caught,
            "missed": len(missed),
            "false_inclusions": len(false),
            "recall": caught / len(sentences),
            "precision": caught / (caught + len(false)) if caught or false else 1.0,
            "expect_match": True,
        }
    return {"not_added_to_case_total": True, "categories": categories}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Deterministic smoke test for experiment 76.")
    parser.add_argument("--output", default=str(ROOT / "eval" / "smoke_report.json"))
    args = parser.parse_args(argv)
    cases = _run_cases()
    passed = sum(1 for case in cases if case["passed"])
    failed = sum(1 for case in cases if case["failed"])
    report = {
        "evaluation_label": "DETERMINISTIC SMOKE TEST. Not a model evaluation.",
        "mode": "deterministic",
        "not_a_model_evaluation": True,
        "catalogue_id": "V007",
        "experiment_id": "exp-76-charity-grant-application-assistant",
        "summary": {
            "total_cases": len(cases),
            "passed": passed,
            "failed": failed,
            "errors": 0,
        },
        "cases": cases,
        "paraphrase_recall": _paraphrase(),
    }
    Path(args.output).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        f"DETERMINISTIC SMOKE TEST {passed}/{len(cases)} passed. "
        "Paraphrase recall is not included in that total."
    )
    return 0 if failed == 0 and len(cases) == 20 else 1


if __name__ == "__main__":
    raise SystemExit(main())
