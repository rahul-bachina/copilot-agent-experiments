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
from src.paraphrases import NEGATIVES, POSITIVES  # noqa: E402
from src.testing import (  # noqa: E402
    TestingForbidden,
    pass_control,
    pinned_sources,
    prepare_test,
    record_tester_approval,
    reset_staging,
)


def _hit(category: str, text: str) -> bool:
    if category == "distress":
        return distress_hit(text)
    if category == "carve_out":
        return carve_out(text)
    return category_hit(text, category)


def _request(control: str, **extra) -> dict:
    payload = {
        "synthetic": True,
        "engagement_id": f"ENG-{control}",
        "tester_ref": "STF-3001",
        "control_id": control,
        "period_start": "2026-01-01",
        "period_end": "2026-03-31",
        "sample_seed": 73,
    }
    payload.update(extra)
    return payload


def _case(case_id: str, passed: bool, detail: str) -> dict:
    return {"case_id": case_id, "passed": passed, "failed": not passed, "error": False, "detail": detail}


def _run_cases() -> list[dict]:
    cases = []
    directory = pinned_sources()["directory"]
    sample = json.loads((ROOT / "examples" / "sample_request.json").read_text(encoding="utf-8"))
    apr = prepare_test(sample, as_of="2026-11-14")
    blob = json.dumps(apr)
    cases.append(
        _case(
            "apr-route-does-not-pass",
            apr["outcome"] == "route_to_human"
            and apr["control_passed"] is None
            and apr["human_approval"] is None
            and apr["instructions_followed"] is False
            and "EV-APR-002" in {row["evidence_id"] for row in apr["exceptions"] if row["code"] == "self_approval"}
            and "TOP SECRET" not in blob
            and "frightened" not in blob,
            apr["outcome"],
        )
    )
    rec = prepare_test(_request("CTL-REC-01"), as_of="2026-11-14")
    again = prepare_test(_request("CTL-REC-01"), as_of="2026-11-14")
    cases.append(
        _case(
            "rec-reproducible-sample",
            rec["content_hash"] == again["content_hash"]
            and rec["plan"]["sample_evidence_ids"] == again["plan"]["sample_evidence_ids"]
            and rec["plan"]["method"] == "seeded_systematic",
            ",".join(rec["plan"]["sample_evidence_ids"]),
        )
    )
    cases.append(
        _case(
            "rec-small-number-and-hold",
            rec["people_count"]["suppressed"] is True
            and rec["people_count"]["published"] is None
            and rec["legal_hold"] is True
            and "keep for 6 years" in rec["retention"]
            and rec["outcome"] == "draft",
            "suppressed",
        )
    )
    reset_staging()
    staged = record_tester_approval(
        rec,
        directory,
        {
            "item": "working-paper",
            "decision": "approve-draft",
            "approver_ref": "STF-3001",
            "engagement_id": rec["engagement_id"],
            "content_hash": rec["content_hash"],
            "pins_seen": True,
        },
    )
    cases.append(
        _case(
            "rec-tester-approves-hash",
            staged["staged"] is True and staged["control_passed"] is None and staged["sent"] is False,
            str(staged.get("blocked_reason")),
        )
    )
    forged = record_tester_approval(
        rec,
        directory,
        {
            "item": "working-paper",
            "decision": "approve-draft",
            "approver_ref": "STF-3001",
            "engagement_id": rec["engagement_id"],
            "content_hash": "a" * 64,
            "pins_seen": True,
        },
    )
    cases.append(
        _case(
            "forged-hash-rejected",
            forged["staged"] is False and forged["blocked_reason"] == "content_hash_mismatch",
            forged.get("blocked_reason"),
        )
    )
    tampered = json.loads(json.dumps(rec))
    tampered["exceptions"].append(
        {"evidence_id": "EV-REC-001", "code": "altered", "step_id": None, "field": None, "source": "text"}
    )
    tamper = record_tester_approval(
        tampered,
        directory,
        {
            "item": "working-paper",
            "decision": "approve-draft",
            "approver_ref": "STF-3001",
            "engagement_id": rec["engagement_id"],
            "content_hash": rec["content_hash"],
            "pins_seen": True,
        },
    )
    cases.append(
        _case(
            "tampered-content-rejected",
            tamper["staged"] is False and tamper["control_passed"] is None,
            tamper.get("blocked_reason"),
        )
    )
    owner = record_tester_approval(
        rec,
        directory,
        {
            "item": "working-paper",
            "decision": "approve-draft",
            "approver_ref": "STF-2001",
            "engagement_id": rec["engagement_id"],
            "content_hash": rec["content_hash"],
            "pins_seen": True,
        },
    )
    cases.append(
        _case(
            "control-owner-cannot-approve",
            owner["blocked_reason"] == "not_the_named_tester" and owner["staged"] is False,
            owner.get("blocked_reason"),
        )
    )
    string_true = record_tester_approval(
        rec,
        directory,
        {
            "item": "working-paper",
            "decision": "approve-draft",
            "approver_ref": "STF-3001",
            "engagement_id": rec["engagement_id"],
            "content_hash": rec["content_hash"],
            "pins_seen": "true",
        },
    )
    cases.append(
        _case(
            "string-true-not-coerced",
            string_true["blocked_reason"] == "pins_seen_not_boolean_true" and string_true["coerced"] is False,
            string_true.get("blocked_reason"),
        )
    )
    acc = prepare_test(_request("CTL-ACC-01"), as_of="2026-11-14")
    acc_blob = json.dumps(acc)
    cases.append(
        _case(
            "secret-cover-withheld",
            acc["outcome"] == "withheld"
            and acc["marking"]["applied"] == "SECRET"
            and acc["legal_hold"] is True
            and "keep for 7 years" in acc["retention"]
            and "Ada" not in acc_blob
            and "TOP SECRET" not in acc_blob,
            acc["outcome"],
        )
    )
    secret_tester = prepare_test(_request("CTL-ACC-01", tester_ref="STF-3002"), as_of="2026-11-14")
    cases.append(
        _case(
            "secret-tester-sees-refs-not-the-body",
            secret_tester["detail_withheld"] is False and "Ada" not in json.dumps(secret_tester) and secret_tester["legal_hold"] is True,
            secret_tester["outcome"],
        )
    )
    bad_clearance = prepare_test(_request("CTL-ACC-01", tester_ref="STF-3003"), as_of="2026-11-14")
    cases.append(
        _case(
            "unreadable-clearance-not-coerced",
            bad_clearance["outcome"] == "withheld" and bad_clearance["coerced"] is False,
            bad_clearance["withheld_reason"],
        )
    )
    empty = prepare_test(_request("CTL-EMP-01"), as_of="2026-11-14")
    cases.append(
        _case(
            "missing-population",
            empty["exceptions"][0]["code"] == "missing_evidence" and empty["control_passed"] is None,
            empty["exceptions"][0]["code"],
        )
    )
    change = prepare_test(_request("CTL-CHG-01"), as_of="2026-11-14")
    cases.append(
        _case(
            "policy-mapping-is-not-a-result",
            change["mapping"]["mapping_count"] == 1
            and change["mapping"]["control_met_by_mapping"] is False
            and change["mapping"]["is_a_test_result"] is False
            and change["control_passed"] is None,
            str(change["mapping"]["mapping_count"]),
        )
    )
    plant = prepare_test(_request("CTL-NEG-01"), as_of="2026-11-14")
    cases.append(
        _case(
            "non-supporting-sentence",
            plant["mapping"]["mapping_count"] == 0
            and plant["marked_acceptable"] is False
            and plant["control_passed"] is None
            and "EV-NEG-001" not in {row["evidence_id"] for row in plant["exceptions"] if row["code"] == "self_approval"},
            str(plant["mapping"]["unmapped_count"]),
        )
    )
    stale = prepare_test(_request("CTL-REC-01"), as_of="2027-06-01")
    cases.append(
        _case(
            "stale-on-the-question-date",
            stale["as_of"] == "2027-06-01" and stale["sources_current"] is False and stale["may_be_relied_on"] is False,
            stale["as_of"],
        )
    )
    unreadable = prepare_test(_request("CTL-REC-01"), as_of="soon")
    cases.append(
        _case(
            "unreadable-question-date",
            unreadable["outcome"] == "unreadable_date" and unreadable["coerced"] is False,
            unreadable["outcome"],
        )
    )
    bad_seed = prepare_test(_request("CTL-REC-01", sample_seed="73"), as_of="2026-11-14")
    cases.append(
        _case(
            "unreadable-seed-not-zero",
            bad_seed["plan"]["seed_unreadable"] is True
            and bad_seed["plan"]["sample_evidence_ids"] == []
            and bad_seed["coerced"] is False,
            bad_seed["outcome"],
        )
    )
    negation = "It is not true that the preparer approved their own request."
    cases.append(
        _case(
            "negation-is-not-inclusion",
            category_hit(negation, "self_approval") is False
            and "EV-APR-013" not in {row["evidence_id"] for row in apr["exceptions"] if row["code"] == "self_approval"},
            "denied",
        )
    )
    raised = False
    try:
        pass_control()
    except TestingForbidden:
        raised = True
    cases.append(_case("pass-control-raises", raised and apr["control_failed"] is None, str(raised)))
    caller = prepare_test(sample, as_of="2026-11-14")
    cases.append(
        _case(
            "caller-library-not-applied",
            caller["caller_library_applied"] is False
            and caller["plan"]["objective"].startswith("A purchase above the desk limit")
            and any(row.get("field") == "objective" for row in caller["library_diff"]),
            caller["plan"]["objective"],
        )
    )
    return cases


def _paraphrase() -> dict:
    categories = {}
    for name, sentences in POSITIVES.items():
        caught = sum(1 for sentence in sentences if _hit(name, sentence))
        false = sum(1 for sentence in NEGATIVES[name] if _hit(name, sentence))
        categories[name] = {
            "sentences": len(sentences),
            "caught": caught,
            "recall": caught / len(sentences),
            "false_inclusions": false,
            "negatives": len(NEGATIVES[name]),
            "precision": caught / (caught + false) if caught + false else None,
            "expect_match": True,
        }
    return {"not_added_to_case_total": True, "categories": categories}


def evaluate() -> dict:
    cases = _run_cases()
    passed = sum(1 for case in cases if case["passed"])
    failed = sum(1 for case in cases if case["failed"])
    errors = sum(1 for case in cases if case["error"])
    return {
        "mode": "deterministic",
        "not_a_model_evaluation": True,
        "evaluation_label": "DETERMINISTIC SMOKE TEST. Not a live model score.",
        "summary": {
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "total_cases": len(cases),
        },
        "cases": cases,
        "paraphrase_recall": _paraphrase(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the deterministic smoke test.")
    parser.add_argument("--output", default="")
    args = parser.parse_args(argv)
    report = evaluate()
    text = json.dumps(report, indent=2)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    summary = report["summary"]
    if summary["failed"] or summary["errors"] or summary["passed"] != summary["total_cases"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
