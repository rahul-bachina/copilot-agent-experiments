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

from briefing import draft_briefing, record_owner_seen, verify_seen  # noqa: E402
from test_paraphrase import score_paraphrases  # noqa: E402

REGISTER = json.loads((ROOT / "fixtures" / "policy_register.json").read_text(encoding="utf-8"))
DIRECTORY = json.loads((ROOT / "fixtures" / "directory.json").read_text(encoding="utf-8"))
SAMPLE = json.loads((ROOT / "examples" / "sample_request.json").read_text(encoding="utf-8"))
DATASET = json.loads((ROOT / "eval" / "synthetic_dataset.json").read_text(encoding="utf-8"))


def _request(case: dict) -> tuple[dict, dict]:
    register = deepcopy(REGISTER)
    if case.get("use_sample"):
        request = deepcopy(SAMPLE)
    else:
        request = {
            "synthetic": True,
            "publication_id": case["publication_id"],
            "caller_ref": case.get("caller_ref", "CO-1001"),
        }
    if "caller_minimum" in case:
        register["internal_consultation_minimum_days"] = case["caller_minimum"]
    return request, register


def _ids(result: dict) -> list[str]:
    return [row["policy_id"] for row in result.get("might_be_affected") or []]


def _decision(result: dict, **overrides) -> dict:
    decision = {
        "approver_ref": "CO-1001",
        "item": "briefing",
        "decision": "seen",
        "publication_hash": result["publication_hash"],
        "briefing_hash": result["briefing_hash"],
        "questions_hash": result["questions_hash"],
        "pins_seen": True,
        "sources_seen": True,
    }
    decision.update(overrides)
    return decision


def _check(case: dict, result: dict, register: dict) -> list[str]:
    errors = []
    expect = case["expect"]

    def need(field, actual):
        if field in expect and actual != expect[field]:
            errors.append(f"{field}: {actual!r} != {expect[field]!r}")

    if "outcome" in expect:
        need("outcome", result["outcome"])
    if result.get("applies") is not None:
        errors.append("applies was set")
    if result.get("sent") is not False or result.get("policy_changed") is not False:
        errors.append("consequential flag")
    if result.get("marked_applicable") is not False or result.get("marked_acceptable") is not False:
        errors.append("marked")
    if result.get("coerced") is not False:
        errors.append("coerced")
    if result.get("network_called") is not False or result.get("live_site_fetched") is not False:
        errors.append("network")
    if "human_approval" in expect:
        need("human_approval", result["human_approval"])
    elif result.get("human_approval") is not None and expect.get("seen") != "ok":
        errors.append("approval set before the seen step")
    need("effective", (result.get("dates") or {}).get("effective", {}).get("display"))
    need("close", (result.get("dates") or {}).get("consultation_close", {}).get("display"))
    if "might" in expect and _ids(result) != expect["might"]:
        errors.append(f"might {_ids(result)}")
    for policy_id in expect.get("not_might") or []:
        if policy_id in _ids(result):
            errors.append(f"{policy_id} listed")
    flags = result.get("flags") or {}
    for name in ("withdrawn", "superseded", "stale", "undated"):
        if name in expect and flags.get(name) is not expect[name]:
            errors.append(f"{name} {flags.get(name)}")
    if "marking" in expect and result.get("marking") != expect["marking"]:
        errors.append("marking")
    if "legal_hold" in expect and result.get("legal_hold") is not expect["legal_hold"]:
        errors.append("hold")
    if "quote" in expect and result.get("what_changed", {}).get("quote") != expect["quote"]:
        errors.append("quote")
    if "unparseable_effective" in expect:
        actual = result["dates"]["effective"]["unparseable"]
        if actual is not expect["unparseable_effective"]:
            errors.append("unparseable")
    if "fca_status" in expect:
        status = (result.get("related_fca_sources") or [{}])[0].get("status")
        if status != expect["fca_status"]:
            errors.append(f"fca {status}")
    if "distress" in expect and (result.get("cue") or {}).get("distress") is not expect["distress"]:
        errors.append("distress")
    if "grievance" in expect and (result.get("cue") or {}).get("grievance") is not expect["grievance"]:
        errors.append("grievance")
    if expect.get("people_suppressed"):
        groups = (result.get("people") or {}).get("groups") or []
        if not groups or groups[0].get("suppressed") is not True or groups[0].get("value") is not None:
            errors.append("people")
    if "negated" in expect:
        topics = sorted(row["topic"] for row in result.get("negated_mentions") or [])
        if topics != sorted(expect["negated"]):
            errors.append(f"negated {topics}")
    if "below_register_window" in expect and result.get("below_register_window") is not expect["below_register_window"]:
        errors.append("window")
    if "statutory_minimum_days" in expect and result.get("statutory_minimum_days") != expect["statutory_minimum_days"]:
        errors.append("statute minimum")
    if "register_minimum_days" in expect and result.get("register_minimum_days") != expect["register_minimum_days"]:
        errors.append("register minimum")
    if expect.get("register_differs") and not result.get("register_differences"):
        errors.append("register diff")
    if "role" in expect and result.get("role_from_directory") != expect["role"]:
        errors.append("role")
    if "sources_current" in expect and result.get("sources_current") is not expect["sources_current"]:
        errors.append("sources")
    if "as_of" in expect and result.get("as_of") != expect["as_of"]:
        errors.append("as_of")
    if "instructions_followed" in expect and result.get("instructions_followed") is not False:
        errors.append("followed")
    if "caller_text_used" in expect and result.get("caller_text_used") is not False:
        errors.append("caller text")
    if expect.get("leading_applied") is False and result.get("leading_criteria_applied") is not False:
        errors.append("leading applied")
    blob = json.dumps(result)
    for needle in expect.get("absent") or []:
        if needle.lower() in blob.lower():
            errors.append(f"present {needle}")
    if len(_ids(result)) != len(set(_ids(result))):
        errors.append("policy double-count")
    seen = expect.get("seen")
    if seen == "ok":
        recorded = record_owner_seen(result, DIRECTORY, _decision(result))
        if recorded.get("human_approval") is None or recorded["applies"] is not None or recorded["sent"] is not False:
            errors.append(recorded.get("blocked_reason") or "seen")
        elif verify_seen(recorded)["accepted"] is not True:
            errors.append("verify")
    elif seen == "hash_mismatch":
        blocked = record_owner_seen(result, DIRECTORY, _decision(result, briefing_hash="a" * 64))
        if blocked.get("blocked_reason") != "briefing_hash_mismatch" or blocked["human_approval"] is not None:
            errors.append("hash was reused")
    elif seen == "tamper":
        recorded = record_owner_seen(result, DIRECTORY, _decision(result))
        tampered = deepcopy(recorded)
        tampered["what_changed"]["quote"] = "tampered"
        if verify_seen(tampered)["accepted"] is not False:
            errors.append("tamper accepted")
        again = record_owner_seen(tampered, DIRECTORY, _decision(result))
        if again.get("blocked_reason") != "briefing_hash_mismatch":
            errors.append("tamper recorded")
    if case.get("caller_minimum") is not None and result.get("coerced") is not False:
        errors.append("minimum coerced")
    return errors


def run() -> dict:
    cases = []
    passed = failed = errors = 0
    for case in DATASET["cases"]:
        try:
            request, register = _request(case)
            result = draft_briefing(request, register, DIRECTORY, case["as_of"])
            problems = _check(case, result, register)
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
    Path(args.output).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    summary = report["summary"]
    print(
        f"DETERMINISTIC SMOKE TEST {summary['passed']}/{summary['total_cases']} passed, "
        f"{summary['failed']} failed, {summary['errors']} errors"
    )
    for name, row in report["paraphrase_recall"]["categories"].items():
        if row["expect_match"]:
            print(f"paraphrase {name}: recall {row['correct']}/{row['sentences']}")
        else:
            print(
                f"paraphrase {name}: false inclusions {row['false_inclusions']}/{row['sentences']}"
                f" denial recall {row['denial_recall']}"
            )
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
        if row["denial_recall"] not in (None, 1.0):
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
