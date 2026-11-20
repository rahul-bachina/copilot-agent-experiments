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

from map_controls import map_controls, record_owner_approval  # noqa: E402
from test_paraphrase import score_paraphrases  # noqa: E402

LIBRARY = json.loads((ROOT / "fixtures" / "library.json").read_text(encoding="utf-8"))
DIRECTORY = json.loads((ROOT / "fixtures" / "directory.json").read_text(encoding="utf-8"))
SAMPLE = json.loads((ROOT / "examples" / "sample_request.json").read_text(encoding="utf-8"))
DATASET = json.loads((ROOT / "eval" / "synthetic_dataset.json").read_text(encoding="utf-8"))


def _policy(text, **extra):
    policy = {
        "policy_id": "isp-001",
        "title": "Information security policy",
        "document_date": "2026-10-01",
        "marking": "OFFICIAL",
        "clauses": [{"clause_ref": "1.1", "text": text}],
    }
    policy.update(extra)
    return {
        "synthetic": True,
        "caller_ref": "CTL-OWN-1001",
        "policies": [policy],
    }


def _request(case: dict) -> dict:
    kind = case["kind"]
    if kind == "sample":
        return deepcopy(SAMPLE)
    if kind == "text":
        return _policy(case["text"], **case.get("policy", {}))
    if kind == "request":
        return case["request"]
    raise KeyError(kind)


def _check(case: dict, result: dict) -> list[str]:
    errors = []
    expect = case["expect"]

    def need(field, actual):
        if field in expect and actual != expect[field]:
            errors.append(f"{field}: {actual!r} != {expect[field]!r}")

    for field in (
        "outcome",
        "control_met",
        "gap_closed",
        "policy_edited",
        "grc_written",
        "instructions_followed",
        "human_approval",
        "coerced",
        "sources_current",
        "may_be_relied_on",
    ):
        need(field, result.get(field))
    if "gap_quote" in expect:
        quotes = [row["quote"] for row in result["gaps"]]
        if expect["gap_quote"] not in quotes:
            errors.append(f"gap quote missing: {quotes!r}")
    if "confidence" in expect:
        needle = expect.get("quote_contains", "")
        rows = [row for row in result["mappings"] if needle and needle in row["quote"]]
        if not rows or rows[0]["confidence"] != expect["confidence"]:
            found = rows[0]["confidence"] if rows else None
            errors.append(f"confidence {found}")
        if rows and rows[0]["control_met"] is not False:
            errors.append("mapping marked met")
    if expect.get("no_inclusion_of"):
        if any(expect["no_inclusion_of"] in row["quote"] and row.get("included") for row in result["mappings"]):
            errors.append("negation counted as included")
    if expect.get("contradiction"):
        if not result["contradictions"]:
            errors.append("no contradiction")
        elif result["contradictions"][0]["cross_source"]["facts"][0]["classification"] != "material_discrepancy":
            errors.append("cross-source class")
        elif result["contradictions"][0]["agent_chose_source"] is not False:
            errors.append("source chosen")
    if expect.get("withheld_phrase"):
        if expect["withheld_phrase"] in json.dumps(result):
            errors.append("withheld phrase copied")
    if expect.get("marking"):
        need("marking", result.get("marking"))
    if expect.get("legal_hold") is True and result.get("legal_hold") is not True:
        errors.append("legal hold dropped")
    if expect.get("people_suppressed") and result.get("people_named", {}).get("count") is not None:
        errors.append("small count published")
    if expect.get("library_not_applied") and result.get("supplied_library_applied") is not False:
        errors.append("supplied library applied")
    if expect.get("bias_not_applied"):
        if not result["biased_criteria"] or result["biased_criteria"][0]["applied"] is not False:
            errors.append("bias applied")
    if expect.get("tamper"):
        approval = {
            "approver_ref": "CTL-OWN-1001",
            "decision": "approved",
            "item": "mapping",
            "mapping_id": result["mappings"][0]["mapping_id"],
            "content_hash": result["mappings"][0]["content_hash"],
            "proposal_hash": result["proposal_hash"],
            "pins_seen": True,
        }
        tampered = deepcopy(result)
        tampered["mappings"][0]["quote"] += " tampered"
        rejected = record_owner_approval(tampered, DIRECTORY, approval)
        if rejected["human_approval"] is not None or rejected["control_met"] is not False:
            errors.append("tampered approval accepted")
    counts = result.get("counts")
    if counts:
        total = counts["controls_with_a_mapping"] + counts["gap_count"] + counts["contradiction_count"]
        if total != counts["control_count"]:
            errors.append("counts do not add up")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Deterministic smoke test for Experiment 69.")
    parser.add_argument("--output", type=Path, default=ROOT / "eval" / "smoke_report.json")
    args = parser.parse_args(argv)
    cases = []
    passed = failed = errors = 0
    for case in DATASET:
        try:
            request = _request(case)
            library = case.get("library") or LIBRARY
            result = map_controls(request, library, DIRECTORY, case.get("as_of", "2026-11-14"))
            problems = _check(case, result)
        except Exception as exc:  # noqa: BLE001 — a smoke row must record the error, not hide it
            problems = [f"{exc.__class__.__name__}: {exc}"]
            result = None
        if problems and result is None:
            status = "error"
            errors += 1
        elif problems:
            status = "failed"
            failed += 1
        else:
            status = "passed"
            passed += 1
        cases.append({"case_id": case["case_id"], "status": status, "problems": problems})
    paraphrase = score_paraphrases()
    report = {
        "evaluation_label": "DETERMINISTIC SMOKE TEST. Not a model evaluation.",
        "mode": "deterministic",
        "not_a_model_evaluation": True,
        "not_a_live_recall_rate": True,
        "summary": {
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "total_cases": len(DATASET),
        },
        "cases": [{"case_id": row["case_id"], "status": row["status"]} for row in cases],
        "case_problems": [row for row in cases if row["problems"]],
        "paraphrase_recall": paraphrase,
    }
    if report["summary"]["passed"] + report["summary"]["failed"] + report["summary"]["errors"] != report["summary"]["total_cases"]:
        raise SystemExit("smoke totals do not add up")
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        f"Smoke test {passed}/{len(DATASET)} passed. "
        "Paraphrase recall is separate and is not added to that total."
    )
    return 0 if not failed and not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
