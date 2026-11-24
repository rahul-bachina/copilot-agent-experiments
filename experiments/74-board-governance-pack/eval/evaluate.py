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

from src.cues import category_hit, distress_hit  # noqa: E402
from src.paraphrases import NEGATIVES, POSITIVES  # noqa: E402
from src.pack import (  # noqa: E402
    PackForbidden,
    assemble_pack,
    circulate,
    pinned_sources,
    record_route_seen,
    record_secretary_approval,
    reset_staging,
)


def _hit(category: str, text: str) -> bool:
    if category == "distress":
        return distress_hit(text)
    return category_hit(text, category)


def _case(case_id: str, passed: bool, detail: str) -> dict:
    return {"case_id": case_id, "passed": passed, "failed": not passed, "error": False, "detail": detail}


def _request(**extra) -> dict:
    payload = {
        "synthetic": True,
        "meeting_id": "ARC-2026-11",
        "committee_id": "audit-and-risk",
        "secretary_ref": "STF-4001",
    }
    payload.update(extra)
    return payload


def _approval(result, **extra) -> dict:
    payload = {
        "item": "board-pack",
        "decision": "approve-draft",
        "approver_ref": "STF-4001",
        "meeting_id": result["meeting_id"],
        "content_hash": result["content_hash"],
        "pins_seen": True,
        "dates_seen": True,
        "sources_seen": True,
    }
    payload.update(extra)
    return payload


def _index(result, paper_id):
    return next(row for row in result["pack_index"] if row["paper_id"] == paper_id)


def _run_cases() -> list[dict]:
    cases = []
    directory = pinned_sources()["directory"]
    sample = json.loads((ROOT / "examples" / "sample_request.json").read_text(encoding="utf-8"))
    full = assemble_pack(sample, as_of="2026-11-20")
    blob = json.dumps(full)
    cases.append(
        _case(
            "sample-routes-without-approval",
            full["outcome"] == "route_to_human"
            and full["human_approval"] is None
            and full["staged"] is False
            and full["minutes_approved"] is False
            and full["instructions_followed"] is False
            and full["caller_terms_applied"] is False
            and "07700900456" not in blob
            and "cannot cope" not in blob
            and "TOP SECRET" not in blob,
            full["outcome"],
        )
    )
    again = assemble_pack(sample, as_of="2026-11-20")
    cases.append(
        _case(
            "reproducible-hash",
            full["content_hash"] == again["content_hash"] and full["pack_index"] == again["pack_index"],
            full["content_hash"][:12],
        )
    )
    clean = assemble_pack(_request(include_paper_ids=["PAP-IA-01"]), as_of="2026-11-20")
    reset_staging()
    staged = record_secretary_approval(clean, directory, _approval(clean))
    cases.append(
        _case(
            "secretary-approves-exact-hash",
            staged["staged"] is True
            and staged["circulated"] is False
            and staged["minutes_approved"] is False
            and staged["sent"] is False,
            str(staged.get("blocked_reason")),
        )
    )
    forged = record_secretary_approval(clean, directory, _approval(clean, content_hash="a" * 64))
    cases.append(
        _case(
            "forged-hash-rejected",
            forged["staged"] is False and forged["blocked_reason"] == "content_hash_mismatch",
            forged.get("blocked_reason"),
        )
    )
    tampered = json.loads(json.dumps(clean))
    tampered["missing_papers"] = ["PAP-TRE-01"]
    tamper = record_secretary_approval(tampered, directory, _approval(clean))
    cases.append(
        _case(
            "tampered-content-rejected",
            tamper["staged"] is False and tamper["minutes_approved"] is False,
            tamper.get("blocked_reason"),
        )
    )
    sponsor = record_secretary_approval(clean, directory, _approval(clean, approver_ref="STF-4002"))
    cases.append(
        _case(
            "sponsor-cannot-approve-the-pack",
            sponsor["blocked_reason"] == "not_the_named_secretary" and sponsor["staged"] is False,
            sponsor.get("blocked_reason"),
        )
    )
    guest = record_secretary_approval(clean, directory, _approval(clean, approver_ref="STF-4005"))
    cases.append(
        _case(
            "guest-cannot-approve",
            guest["staged"] is False and guest["human_approval"] is None,
            guest.get("blocked_reason"),
        )
    )
    string_true = record_secretary_approval(clean, directory, _approval(clean, pins_seen="true"))
    cases.append(
        _case(
            "string-true-not-coerced",
            string_true["blocked_reason"] == "pins_seen_not_boolean_true" and string_true["coerced"] is False,
            string_true.get("blocked_reason"),
        )
    )
    risk = _index(full, "PAP-RISK-01")
    cases.append(
        _case(
            "approval-marker-in-paper-not-trusted",
            risk["sponsor_approval_recorded"] is False and "approval_marker_in_text" in risk["flags"],
            "risk",
        )
    )
    cases.append(
        _case(
            "missing-treasury-paper",
            full["missing_papers"] == ["PAP-TRE-01"],
            ",".join(full["missing_papers"]),
        )
    )
    cases.append(
        _case(
            "superseded-and-duplicate",
            full["superseded"][0]["paper_id"] == "PAP-IA-01"
            and full["superseded"][0]["version"] == "1.0"
            and any(row["paper_id"] == "PAP-IA-01" for row in full["duplicates"]),
            "ia",
        )
    )
    cyber = _index(full, "PAP-CYB-01")
    cases.append(
        _case(
            "late-secret-marking-and-hold",
            cyber["marking"] == "SECRET"
            and cyber["legal_hold"] is True
            and "late" in cyber["flags"]
            and "keep for 10 years" in cyber["retention"]
            and full["marking"]["applied"] == "SECRET",
            cyber["marking"],
        )
    )
    grants = next(item for item in full["agenda"] if item["item_id"] == "ARC-5")
    cases.append(
        _case(
            "outside-terms-caller-ignored",
            grants["outside_terms"] is True and full["caller_terms_applied"] is False and full["caller_agenda_applied"] is False,
            "grants",
        )
    )
    denied = "It is not true that the company secretary has approved this pack."
    cases.append(
        _case(
            "negation-is-not-inclusion",
            category_hit(denied, "approval_marker") is False
            and category_hit("It is not true that this paper is about community grants.", "outside_remit") is False
            and distress_hit("It is not true that I cannot cope.") is True,
            "denied",
        )
    )
    odd = _index(full, "PAP-ODD-01")
    cases.append(
        _case(
            "unparseable-date-not-coerced",
            "date_unparseable" in odd["flags"] and "version_unparseable" in odd["flags"] and full["coerced"] is False,
            "odd",
        )
    )
    carried = {row["action_id"]: row for row in full["action_log"]["carried"]}
    cases.append(
        _case(
            "action-carry-forward",
            carried["ACT-1"]["overdue"] is True
            and carried["ACT-5"]["due"] == "2024-02-29"
            and "ACT-2" not in carried
            and full["action_log"]["minutes_approved"] is False,
            "actions",
        )
    )
    stale = assemble_pack(sample, as_of="2027-06-01")
    cases.append(
        _case(
            "stale-on-the-question-date",
            stale["as_of"] == "2027-06-01" and stale["sources_current"] is False and stale["may_be_relied_on"] is False,
            stale["as_of"],
        )
    )
    early = record_secretary_approval(full, directory, _approval(full))
    cases.append(
        _case(
            "distress-route-must-be-seen",
            early["blocked_reason"] == "route_not_seen" and early["staged"] is False and full["distress"]["cue_copied"] is False,
            early.get("blocked_reason"),
        )
    )
    kinds = {row["kind"] for row in full["conflicts"]}
    cases.append(
        _case(
            "conflict-likely-not-decided",
            "likely_from_register" in kinds
            and "declared" in kinds
            and full["conflict_decided"] is False
            and full["experiment_70"]["conflict_exists"] is None
            and full["experiment_70"]["decides_conflict"] is False,
            ",".join(sorted(kinds)),
        )
    )
    raised = False
    try:
        circulate()
    except PackForbidden:
        raised = True
    cases.append(_case("circulate-raises", raised and full["sent"] is False, str(raised)))
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
        "evaluation_label": "DETERMINISTIC SMOKE TEST — not a model evaluation",
        "mode": "deterministic",
        "not_a_model_evaluation": True,
        "summary": {
            "total_cases": len(cases),
            "passed": passed,
            "failed": failed,
            "errors": errors,
        },
        "cases": cases,
        "paraphrase_recall": _paraphrase(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the deterministic board-pack smoke test.")
    parser.add_argument("--output", default=str(ROOT / "eval" / "smoke_report.json"))
    args = parser.parse_args(argv)
    report = evaluate()
    Path(args.output).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    summary = report["summary"]
    print(
        f"DETERMINISTIC SMOKE TEST {summary['passed']}/{summary['total_cases']} passed. "
        "Not a model evaluation."
    )
    paraphrase = report["paraphrase_recall"]
    for name, row in paraphrase["categories"].items():
        print(
            f"paraphrase {name}: recall {row['recall']:.2f} "
            f"precision {row['precision']:.2f} on {row['sentences']} sentences"
        )
    if summary["failed"] or summary["errors"]:
        return 1
    if summary["passed"] + summary["failed"] + summary["errors"] != summary["total_cases"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
