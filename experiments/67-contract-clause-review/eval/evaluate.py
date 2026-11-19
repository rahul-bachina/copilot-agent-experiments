#!/usr/bin/env python3
"""Deterministic smoke test. Not a model evaluation.

Each case is one row. Paraphrase recall is reported beside the cases and is
not added to the case total.
"""

from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

from review import record_lawyer_seen, review_contract  # noqa: E402
from test_paraphrase import score_paraphrases  # noqa: E402

PLAYBOOK = json.loads((ROOT / "fixtures" / "playbook.json").read_text(encoding="utf-8"))
DIRECTORY = json.loads((ROOT / "fixtures" / "directory.json").read_text(encoding="utf-8"))
SAMPLE = json.loads((ROOT / "examples" / "sample_request.json").read_text(encoding="utf-8"))
DATASET = json.loads((ROOT / "eval" / "synthetic_dataset.json").read_text(encoding="utf-8"))


def _request(case: dict) -> dict:
    if case.get("use_sample"):
        request = deepcopy(SAMPLE)
    else:
        request = deepcopy(SAMPLE)
        request["text"] = case["text"]
    request.update(case.get("request") or {})
    return request


def _topic(result: dict, topic: str) -> dict:
    return next(row for row in result["clauses"] if row["topic"] == topic)


def _check(case: dict, result: dict) -> list[str]:
    errors = []
    expect = case["expect"]

    def need(field, actual):
        if field in expect and actual != expect[field]:
            errors.append(f"{field}: {actual!r} != {expect[field]!r}")

    need("outcome", result["outcome"])
    need("marked_safe", result["marked_safe"])
    need("terms_accepted", result["terms_accepted"])
    need("legal_advice", result["legal_advice"])
    need("article_28_complied", result["article_28_complied"])
    need("coerced", result["coerced"])
    need("instructions_followed", result["instructions_followed"])
    need("human_approval", result["human_approval"])
    if "topic_status" in expect:
        for topic, status in expect["topic_status"].items():
            actual = _topic(result, topic)["status"]
            if actual != status:
                errors.append(f"{topic}: {actual} != {status}")
    if "quoted_text" in expect:
        for topic, quote in expect["quoted_text"].items():
            actual = _topic(result, topic)["quoted_text"]
            if actual != quote:
                errors.append(f"quote {topic}: {actual!r}")
    if expect.get("below_floor"):
        row = _topic(result, expect["below_floor"])
        if row["below_statutory_floor"] is not True or row["marked_safe"] is not False:
            errors.append("below floor not flagged")
    if expect.get("floor_source"):
        row = _topic(result, "limitation_of_liability")
        if row["statutory_floor_source"] != expect["floor_source"]:
            errors.append(f"floor source {row['statutory_floor_source']}")
    if "notice_days" in expect:
        actual = _topic(result, "termination").get("notice_days")
        if actual != expect["notice_days"]:
            errors.append(f"notice_days {actual}")
    if expect.get("absent"):
        blob = json.dumps(result)
        for word in expect["absent"]:
            if word in blob:
                errors.append(f"copied {word}")
    if "marking" in expect and result["marking"] != expect["marking"]:
        errors.append(f"marking {result['marking']}")
    if expect.get("legal_hold") is True and result["legal_hold"] is not True:
        errors.append("legal hold dropped")
    if expect.get("retention_kept"):
        for label in expect["retention_kept"]:
            if label not in result["retention_labels"]:
                errors.append(f"retention missing {label}")
    if "playbook_stale" in expect and result["playbook"]["stale"] is not expect["playbook_stale"]:
        errors.append("stale flag")
    if "not_yet_in_force" in expect and result["playbook"]["not_yet_in_force"] is not expect["not_yet_in_force"]:
        errors.append("in force flag")
    if "audience" in expect and result["audience"] != expect["audience"]:
        errors.append(f"audience {result['audience']}")
    if expect.get("pins_confirmed") is False and result["pins_confirmed"] is not False:
        errors.append("pins confirmed")
    if "may_be_relied_on" in expect and result["may_be_relied_on"] is not expect["may_be_relied_on"]:
        errors.append("relied on")
    if "outside_playbook_count" in expect and result["outside_playbook_count"] != expect["outside_playbook_count"]:
        errors.append("outside count")
    if "injection_detected" in expect and result["prompt_injection"]["detected"] is not expect["injection_detected"]:
        errors.append("injection")
    if expect.get("seen") == "guest":
        blocked = record_lawyer_seen(
            result,
            DIRECTORY,
            {
                "approver_ref": "GST-9",
                "item": "clause-review",
                "decision": "seen",
                "contract_hash": result["contract_hash"],
                "deviations_hash": result["deviations_hash"],
                "pins_seen": True,
            },
        )
        if blocked["human_approval"] is not None or blocked["terms_accepted"] is not False:
            errors.append("guest seen")
        if blocked.get("blocked_reason") != "not_lawyer":
            errors.append(blocked.get("blocked_reason"))
    if expect.get("seen") == "hash_mismatch":
        blocked = record_lawyer_seen(
            result,
            DIRECTORY,
            {
                "approver_ref": "SOL-2001",
                "item": "clause-review",
                "decision": "seen",
                "contract_hash": result["contract_hash"],
                "deviations_hash": "b" * 64,
                "pins_seen": True,
            },
        )
        if blocked.get("blocked_reason") != "deviations_hash_mismatch" or blocked["human_approval"] is not None:
            errors.append("hash was reused")
    counts = (
        result["in_playbook_count"]
        + result["deviation_count"]
        + result["lawyer_route_count"]
        + result["missing_count"]
    )
    if counts != result["topic_count"]:
        errors.append("topic rows double-count")
    return errors


def run() -> dict:
    cases = []
    passed = failed = errors = 0
    for case in DATASET["cases"]:
        try:
            result = review_contract(_request(case), PLAYBOOK, DIRECTORY, case["as_of"])
            problems = _check(case, result)
        except Exception as exc:  # noqa: BLE001
            errors += 1
            cases.append({"case_id": case["case_id"], "status": "error", "detail": str(exc)})
            continue
        if problems:
            failed += 1
            cases.append({"case_id": case["case_id"], "status": "failed", "detail": problems})
        else:
            passed += 1
            cases.append({"case_id": case["case_id"], "status": "passed"})
    total = len(DATASET["cases"])
    paraphrase = score_paraphrases()
    return {
        "evaluation_label": "DETERMINISTIC SMOKE TEST. Not a model evaluation.",
        "mode": "deterministic",
        "not_a_model_evaluation": True,
        "not_a_live_recall_rate": True,
        "summary": {
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "total_cases": total,
        },
        "cases": cases,
        "paraphrase_recall": paraphrase,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(ROOT / "eval" / "smoke_report.json"))
    args = parser.parse_args()
    report = run()
    Path(args.output).write_text(json.dumps(report, indent=2), encoding="utf-8")
    summary = report["summary"]
    print(
        f"DETERMINISTIC SMOKE TEST {summary['passed']}/{summary['total_cases']} passed, "
        f"{summary['failed']} failed, {summary['errors']} errors"
    )
    for name, row in report["paraphrase_recall"]["categories"].items():
        if row["expect_match"]:
            print(f"paraphrase {name}: recall {row['correct']}/{row['sentences']}")
        else:
            print(f"paraphrase {name}: false inclusions {row['false_inclusions']}/{row['sentences']}")
    if summary["failed"] or summary["errors"]:
        print(json.dumps([row for row in report["cases"] if row["status"] != "passed"], indent=2))
        return 1
    if summary["passed"] + summary["failed"] + summary["errors"] != summary["total_cases"]:
        print("totals do not add up")
        return 1
    for row in report["paraphrase_recall"]["categories"].values():
        if row["expect_match"] and row["recall"] != 1.0:
            return 1
        if not row["expect_match"] and row["false_inclusions"] != 0:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
