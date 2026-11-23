#!/usr/bin/env python3
"""Deterministic smoke test. Not a model evaluation.

Paraphrase recall is a separate block and is not added to the case total.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.advice import advise_retention, pinned_sources  # noqa: E402
from src.cues import category_match  # noqa: E402
from src.match import sentence_supports  # noqa: E402


def _check(result: dict, expect: dict) -> list[str]:
    errors = []

    def need(condition, message):
        if not condition:
            errors.append(message)

    if "outcome" in expect:
        need(result.get("outcome") == expect["outcome"], f"outcome {result.get('outcome')}")
    if "indicative_date" in expect:
        need(result.get("indicative_date") == expect["indicative_date"], f"date {result.get('indicative_date')}")
    if "line_id" in expect:
        rule = result.get("rule") or {}
        need(rule.get("line_id") == expect["line_id"], f"line {rule.get('line_id')}")
    if "line_absent" in expect:
        need(expect["line_absent"] not in json.dumps(result.get("rules_cited")), "withdrawn line cited")
    if "disposal_suggested" in expect:
        need(result.get("disposal_suggested") is expect["disposal_suggested"], "disposal flag")
    if "storage_question" in expect:
        need(result.get("uk_gdpr_storage_limitation_question") is expect["storage_question"], "storage question")
    if "human_approval" in expect:
        need(result.get("human_approval") is expect["human_approval"], "approval")
    if "ambiguous" in expect:
        need(result.get("ambiguous") is expect["ambiguous"], "ambiguous")
    if expect.get("held") is True:
        need(result.get("legal_hold", {}).get("held") is True, "hold")
    if "open" in expect:
        need(result.get("open_matters", {}).get(expect["open"]) is True, "open matter")
    if "trigger_date_status" in expect:
        need(result.get("trigger_date_status") == expect["trigger_date_status"], "trigger status")
    if "coerced" in expect:
        need(result.get("coerced") is expect["coerced"], "coerced")
    if "pra_applies" in expect:
        need(result.get("pra", {}).get("applies") is expect["pra_applies"], "pra")
    if "transfer_latest" in expect:
        need(result.get("pra", {}).get("transfer_latest") == expect["transfer_latest"], "transfer latest")
    if expect.get("finding_of_breach") is False:
        need(result.get("pra", {}).get("finding_of_breach") is False, "breach finding")
    if "below_pinned_schedule" in expect:
        need(result.get("below_pinned_schedule") is expect["below_pinned_schedule"], "below schedule")
    if "schedule_used" in expect:
        need(result.get("schedule_used") == expect["schedule_used"], "schedule used")
    if "marked_safe" in expect:
        need(result.get("marked_safe") is expect["marked_safe"], "marked safe")
    if "injection_followed" in expect:
        need(result.get("prompt_injection", {}).get("followed") is expect["injection_followed"], "injection followed")
        need(result.get("instructions_followed") is False, "instructions followed")
    if "deleted" in expect:
        need(result.get("deleted") is expect["deleted"], "deleted")
    if "sent" in expect:
        need(result.get("sent") is expect["sent"], "sent")
    if "marking" in expect:
        need(result.get("marking", {}).get("applied") == expect["marking"], "marking")
    if "clearance" in expect:
        need(result.get("marking", {}).get("caller_clearance") == expect["clearance"], "clearance")
    if "content_copied" in expect:
        need(result.get("marking", {}).get("content_copied") is expect["content_copied"], "content copied")
    if "distress" in expect:
        need(result.get("distress", {}).get("flagged") is expect["distress"], "distress")
    if "routine_advice" in expect:
        need(result.get("routine_advice") is expect["routine_advice"], "routine")
    if "text_copied" in expect:
        need(result.get("distress", {}).get("text_copied") is expect["text_copied"], "text copied")
        need("suicide" not in json.dumps(result), "distress text copied")
    if "schedule_current" in expect:
        need(result.get("schedule_current") is expect["schedule_current"], "schedule current")
    if "sources_current" in expect:
        need(result.get("sources_current") is expect["sources_current"], "sources current")
    if "may_be_relied_on" in expect:
        need(result.get("may_be_relied_on_as_a_disposal_decision") is expect["may_be_relied_on"], "relied on")
    if "as_of" in expect:
        need(result.get("as_of") == expect["as_of"], "as of")
    return errors


def _paraphrase(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    categories = {}
    for name, row in data.items():
        sentences = row["sentences"]
        if "expect_support" in row:
            matched = sum(1 for sentence in sentences if sentence_supports(sentence)["supports"])
            false_inclusions = 0 if row["expect_support"] else matched
            recalled = matched if row["expect_support"] else len(sentences) - matched
            categories[name] = {
                "sentences": len(sentences),
                "expect_match": row["expect_support"],
                "recalled": recalled,
                "recall": recalled / len(sentences),
                "false_inclusions": false_inclusions,
            }
            continue
        category = name[: -len("_negated")] if name.endswith("_negated") else name
        matched = sum(1 for sentence in sentences if category_match(sentence, category))
        if row["expect_match"]:
            recalled = matched
            false_inclusions = 0
        else:
            recalled = len(sentences) - matched
            false_inclusions = matched
        categories[name] = {
            "sentences": len(sentences),
            "expect_match": row["expect_match"],
            "recalled": recalled,
            "recall": recalled / len(sentences),
            "false_inclusions": false_inclusions,
        }
    positives = [row for name, row in categories.items() if row["expect_match"] and name.startswith("support")]
    negatives = [row for name, row in categories.items() if not row["expect_match"] and name.startswith("support")]
    true_positive = positives[0]["recalled"] if positives else 0
    false_positive = negatives[0]["false_inclusions"] if negatives else 0
    precision = true_positive / (true_positive + false_positive) if (true_positive + false_positive) else None
    return {
        "not_added_to_case_total": True,
        "categories": categories,
        "support_precision": precision,
        "support_recall": positives[0]["recall"] if positives else None,
    }


def evaluate() -> dict:
    pinned = pinned_sources()
    dataset = json.loads((ROOT / "eval" / "synthetic_dataset.json").read_text(encoding="utf-8"))
    cases = []
    passed = failed = errors = 0
    for case in dataset["cases"]:
        row = {"case_id": case["case_id"], "status": "passed", "errors": []}
        try:
            result = advise_retention(
                case["request"],
                pinned["schedule"],
                pinned["inventory"],
                pinned["directory"],
                case["as_of"],
            )
            row["errors"] = _check(result, case["expect"])
            if row["errors"]:
                row["status"] = "failed"
                failed += 1
            else:
                passed += 1
        except Exception as exc:  # noqa: BLE001 — smoke report must count errors once
            row["status"] = "error"
            row["errors"] = [type(exc).__name__]
            errors += 1
        cases.append(row)
    paraphrase = _paraphrase(ROOT / "eval" / "paraphrase_set.json")
    return {
        "evaluation_label": "DETERMINISTIC SMOKE TEST",
        "mode": "deterministic",
        "not_a_model_evaluation": True,
        "summary": {
            "total_cases": len(cases),
            "passed": passed,
            "failed": failed,
            "errors": errors,
        },
        "cases": cases,
        "paraphrase_recall": paraphrase,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(ROOT / "eval" / "smoke_report.json"))
    args = parser.parse_args(argv)
    report = evaluate()
    Path(args.output).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    summary = report["summary"]
    print(
        f"DETERMINISTIC SMOKE TEST {summary['passed']}/{summary['total_cases']} passed. "
        "Not a model evaluation."
    )
    if summary["failed"] or summary["errors"]:
        print(json.dumps(report["cases"], indent=2))
        return 1
    if summary["passed"] + summary["failed"] + summary["errors"] != summary["total_cases"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
