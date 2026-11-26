"""Deterministic smoke test. Not a model evaluation.

Paraphrase recall and the code-classification score are reported beside the
case total. They are not added to it.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.cues import category_hit, distress_hit, grievance_hit, safeguarding_hit, whistleblowing_hit  # noqa: E402
from src.paraphrases import CATEGORIES  # noqa: E402
from src.workflow import diagnose, pinned_taxonomy, reset_held  # noqa: E402


def _hit(kind: str, text: str) -> bool:
    if kind == "distress":
        return distress_hit(text)
    if kind == "safeguarding":
        return safeguarding_hit(text)
    if kind == "whistleblowing":
        return whistleblowing_hit(text)
    if kind == "grievance":
        return grievance_hit(text)
    if kind == "injection":
        return category_hit(text, "embedded_instruction")
    if kind == "forged_approval":
        return category_hit(text, "forged_approval")
    if kind == "leading_criterion":
        return category_hit(text, "leading_criterion")
    return any(
        (
            distress_hit(text),
            safeguarding_hit(text),
            whistleblowing_hit(text),
            grievance_hit(text),
            category_hit(text, "embedded_instruction"),
            category_hit(text, "forged_approval"),
            category_hit(text, "leading_criterion"),
        )
    )


def _request(case: dict) -> dict:
    started = case.get("started_at", "2026-11-20T09:00:00Z")
    ended = case.get("ended_at", "2026-11-20T09:02:00Z")
    steps = []
    for step in case["steps"]:
        steps.append({
            "step_id": step["step_id"],
            "name": step["name"],
            "status": step.get("status", "Failed"),
            "started_at": step.get("started_at", started),
            "ended_at": step.get("ended_at", ended),
            "error_codes": step.get("error_codes", []),
            "error_text": step.get("error_text", ""),
            "output_text": step.get("output_text", ""),
        })
    payload = {
        "synthetic": True,
        "diagnosis_id": case["diagnosis_id"],
        "process_id": case["process_id"],
        "owner_ref": "OWN-8201",
        "question_date": case["as_of"],
        "runs": [{
            "run_id": "RUN-" + case["case_id"],
            "process_id": case["process_id"],
            "status": case.get("run_status", "Failed"),
            "started_at": started,
            "ended_at": ended,
            "trigger_user_ref": "USR-8201",
            "protective_marking": case.get("marking", "OFFICIAL"),
            "legal_hold": case.get("legal_hold", False),
            "retention": case.get("retention", ["RETAIN 6 YEARS"]),
            "cover": case.get("cover", ""),
            "notes": case.get("notes", ""),
            "steps": steps,
        }],
    }
    if "caller_register" in case:
        payload["caller_register"] = case["caller_register"]
    if case.get("caller_note"):
        payload["caller_note"] = case["caller_note"]
    return payload


def _check(case: dict, result: dict) -> list[str]:
    errors = []
    expect = case["expect"]
    blob = json.dumps(result)
    if result["auto_retried"] is not False or result["retried"] or result["cancelled"] or result["executed"]:
        errors.append("an action was carried out")
    if result["error_text_used_for_class"] is not False:
        errors.append("error text was used")
    if result["coerced"] is not False:
        errors.append("a value was coerced")
    if result["experiment_17_called"] is not False:
        errors.append("experiment 17 was called")
    if result["human_approval"] is not None or result["owner_decision_recorded"] is not False:
        errors.append("a decision was recorded by the diagnosis")
    if "exception_class" in expect:
        classes = [group["exception_class"] for group in result["groups"]]
        if expect["exception_class"] not in classes:
            errors.append(f"class {classes} != {expect['exception_class']}")
    if "reason" in expect:
        reasons = [group["reason"] for group in result["groups"]]
        if expect["reason"] not in reasons:
            errors.append(f"reason {reasons}")
    for key in ("outcome", "retry_safe", "partial_completion", "stale", "future_timestamp", "unparseable_timestamp", "legal_hold", "conflicting_values", "carve_out"):
        if key in expect and result.get(key) != expect[key]:
            errors.append(f"{key} {result.get(key)} != {expect[key]}")
    if "marking" in expect and result["marking"]["applied"] != expect["marking"]:
        errors.append("marking")
    if "duplicate_payment" in expect and result["duplicate_risks"]["payment"] is not expect["duplicate_payment"]:
        errors.append("duplicate payment")
    if "duplicate_email" in expect and result["duplicate_risks"]["email"] is not expect["duplicate_email"]:
        errors.append("duplicate email")
    if "register_applied" in expect and result["register_check"]["applied"] is not expect["register_applied"]:
        errors.append("register applied")
    if "followed" in expect and result["prompt_injection"]["followed"] is not expect["followed"]:
        errors.append("followed")
    if "signals" in expect and result["prompt_injection"]["signals"] != expect["signals"]:
        errors.append(f"signals {result['prompt_injection']['signals']}")
    for phrase in expect.get("absent", []):
        if phrase in blob:
            errors.append(f"copied {phrase}")
    return errors


def _paraphrase() -> dict:
    categories = {}
    for name, row in CATEGORIES.items():
        sentences = list(row["sentences"])
        matched = sum(1 for text in sentences if _hit(row["kind"], text))
        if row["expect_match"]:
            recall = matched / len(sentences)
            precision = 1.0 if matched else 0.0
            false_inclusions = 0
        else:
            recall = None
            precision = 1.0 if matched == 0 else 0.0
            false_inclusions = matched
        categories[name] = {
            "sentences": len(sentences),
            "matched": matched,
            "expect_match": row["expect_match"],
            "recall": recall if row["expect_match"] else 1.0 if false_inclusions == 0 else 0.0,
            "precision": precision,
            "false_inclusions": false_inclusions,
        }
    return {"not_added_to_case_total": True, "categories": categories}


def _classification() -> dict:
    taxonomy = pinned_taxonomy()
    positives = 0
    for code, expected in taxonomy.items():
        result = diagnose(
            _request({
                "case_id": "P" + code[:6],
                "as_of": "2026-11-26",
                "process_id": "PROC-LOOKUP-01",
                "diagnosis_id": "DX-8590",
                "steps": [{
                    "step_id": "lookup",
                    "name": "Lookup supplier",
                    "status": "Failed",
                    "error_codes": [code],
                    "error_text": "This prose says timeout, duplicate, and business rule.",
                }],
            }),
            as_of="2026-11-26",
        )
        if result["groups"] and result["groups"][0]["exception_class"] == expected and result["error_text_used_for_class"] is False:
            positives += 1
    negatives = [
        ("ValidationFailed", "This is a timeout."),
        ("BusinessRuleViolation", "Error 429."),
        ("AccessDenied", "ConnectionExpired."),
        ("ReferenceNotFound", "DuplicateDetected in the prose."),
        ("401", "Business rule breach."),
        ("PolicyBlocked", "Missing reference data."),
        ("SchemaMismatch", "Permissions failure."),
        ("LookupEmpty", "Data validation failed."),
        ("Conflict409", "Only a timeout."),
        ("GatewayTimeout", "A business-rule breach."),
        ("InsufficientPrivilege", "Transient 429."),
        ("TooManyRequests", "Authentication expired."),
        ("503", "Duplicate submission."),
        ("ConnectorThrottle", "ValidationFailed in prose."),
        ("InvalidConnection", "The lookup was empty."),
        ("AADSTS70043", "AccessDenied in prose."),
        ("StuckRunning", "The business rule passed."),
        ("ActionTimedOut", "A permissions error."),
        ("TimedOut", "ReferenceNotFound in prose."),
        ("DuplicateDetected", "It is not true that this includes a timeout."),
    ]
    false_inclusions = 0
    for code, text in negatives:
        result = diagnose(
            _request({
                "case_id": "N" + code[:6],
                "as_of": "2026-11-26",
                "process_id": "PROC-LOOKUP-01",
                "diagnosis_id": "DX-8591",
                "steps": [{
                    "step_id": "lookup",
                    "name": "Lookup supplier",
                    "status": "Failed",
                    "error_codes": [code],
                    "error_text": text,
                }],
            }),
            as_of="2026-11-26",
        )
        got = result["groups"][0]["exception_class"] if result["groups"] else None
        if got != taxonomy[code]:
            false_inclusions += 1
    precision = positives / (positives + false_inclusions) if positives or false_inclusions else 0
    recall = positives / len(taxonomy) if taxonomy else 0
    return {
        "not_added_to_case_total": True,
        "positives": positives,
        "negatives": len(negatives),
        "false_inclusions": false_inclusions,
        "precision": precision,
        "recall": recall,
    }


def evaluate() -> dict:
    reset_held()
    dataset = json.loads((ROOT / "eval" / "synthetic_dataset.json").read_text(encoding="utf-8"))
    cases = []
    passed = failed = errors = 0
    for case in dataset["cases"]:
        try:
            result = diagnose(_request(case), as_of=case["as_of"])
            problems = _check(case, result)
        except Exception as exc:  # noqa: BLE001 — the smoke row must record the failure
            problems = [str(exc)]
            result = None
        status = "passed" if result is not None and not problems else "error" if result is None else "failed"
        if status == "passed":
            passed += 1
        elif status == "failed":
            failed += 1
        else:
            errors += 1
        cases.append({"case_id": case["case_id"], "status": status, "problems": problems})
    total = len(cases)
    return {
        "evaluation_label": "DETERMINISTIC SMOKE TEST. Not a model evaluation.",
        "mode": "deterministic",
        "not_a_model_evaluation": True,
        "experiment_id": "exp-82-workflow-exception-assistant",
        "summary": {
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "total_cases": total,
        },
        "cases": cases,
        "paraphrase_recall": _paraphrase(),
        "classification_score": _classification(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the workflow-exception smoke test.")
    parser.add_argument("--output", default="")
    args = parser.parse_args(argv)
    report = evaluate()
    text = json.dumps(report, indent=2)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    summary = report["summary"]
    if summary["failed"] or summary["errors"] or summary["passed"] + summary["failed"] + summary["errors"] != summary["total_cases"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
