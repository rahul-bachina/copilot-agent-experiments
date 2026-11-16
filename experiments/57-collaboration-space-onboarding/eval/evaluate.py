#!/usr/bin/env python3
"""Deterministic smoke test of collaboration-space onboarding.

The fixtures are synthetic. The checker is the Python under src/. This is not
a model score and it does not call a model. Each case is counted once.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from onboard import apply_membership, prepare_onboarding  # noqa: E402

SMOKE_LABEL = (
    "DETERMINISTIC SMOKE TEST. The checker is the Python in src/. "
    "Not a measure of model accuracy. No model was called."
)


def load_dataset(path: Path | None = None) -> dict:
    if path is None:
        path = Path(__file__).parent / "synthetic_dataset.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _base():
    space = json.loads((ROOT / "examples" / "sample_space.json").read_text(encoding="utf-8"))
    request = json.loads((ROOT / "examples" / "sample_request.json").read_text(encoding="utf-8"))
    approval = json.loads((ROOT / "examples" / "sample_approval.json").read_text(encoding="utf-8"))
    return space, request, approval


def _run(case: dict) -> dict:
    space, request, approval = _base()
    for key, value in (case.get("space") or {}).items():
        if key == "add_document":
            space["documents"].append(value)
        else:
            space[key] = value
    for key, value in (case.get("request") or {}).items():
        request[key] = value
    pack = prepare_onboarding(space, request, case.get("as_of", "2026-11-16"))
    if case.get("apply") is True:
        for key, value in (case.get("approval") or {}).items():
            approval[key] = value
        if case.get("approval_object") is False:
            approval = None
        pack = apply_membership(pack, approval)
    return pack


def evaluate_case(case: dict) -> dict:
    expect = case["expect"]
    checks = []

    def add(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": passed, "detail": detail})

    try:
        result = _run(case)
        blob = json.dumps(result)
        if "outcome" in expect:
            add("outcome", result.get("outcome") == expect["outcome"], str(result.get("outcome")))
        if "apply_outcome" in expect:
            add("apply_outcome", result.get("apply_outcome") == expect["apply_outcome"], str(result.get("apply_outcome")))
        if "applied" in expect:
            add("applied", result.get("applied") is expect["applied"], str(result.get("applied")))
        if expect.get("human_approval_null") is True:
            add("human_approval", result.get("human_approval") is None, "null")
        if "role_proposed" in expect:
            add("role_proposed", result.get("role_proposed") == expect["role_proposed"], str(result.get("role_proposed")))
        if "justified_label" in expect:
            add("justified_label", result.get("justified_label") == expect["justified_label"], str(result.get("justified_label")))
        if "effective_label" in expect:
            add("effective_label", result.get("effective_label") == expect["effective_label"], str(result.get("effective_label")))
        if "owner_granted" in expect:
            add("owner_granted", result.get("owner_granted") is expect["owner_granted"], str(result.get("owner_granted")))
        if "guest_granted" in expect:
            add("guest_granted", result.get("guest_granted") is expect["guest_granted"], str(result.get("guest_granted")))
        if expect.get("external_share_applied") is False:
            add("external_share", result.get("external_share_applied") is False, "false")
        if expect.get("live_graph_called") is False:
            add("live_graph", result.get("live_graph_called") is False, "false")
        if expect.get("coerced") is False:
            add("coerced", result.get("coerced") is False, "false")
        if expect.get("injection_followed") is False:
            add("injection_followed", (result.get("prompt_injection") or {}).get("followed") is False, "false")
        if "file_present" in expect:
            hits = (result.get("explanation") or {}).get("key_documents") or []
            add("file_present", any(item.get("file_id") == expect["file_present"] for item in hits), expect["file_present"])
        if "legal_hold" in expect:
            hits = (result.get("explanation") or {}).get("key_documents") or []
            focus = next((item for item in hits if item.get("file_id") == expect.get("file_present")), None)
            add("legal_hold", focus is not None and focus.get("legal_hold") is expect["legal_hold"], str(None if focus is None else focus.get("legal_hold")))
        if "absent" in expect:
            add("absent", expect["absent"] not in blob, expect["absent"])
        if "manifest_approved" in expect:
            manifest = (result.get("reuse") or {}).get("experiment_03") or {}
            add("manifest_approved", manifest.get("approved") is expect["manifest_approved"], str(manifest.get("approved")))
        if not checks:
            add("ran", True, result.get("outcome"))
    except Exception as exc:  # noqa: BLE001 — one case, one error row
        checks.append({"name": "error", "passed": False, "detail": type(exc).__name__ + ": " + str(exc)})
        return {"case_id": case["id"], "name": case.get("name", ""), "status": "error", "checks": checks}
    failed = any(not item["passed"] for item in checks)
    return {
        "case_id": case["id"],
        "name": case.get("name", ""),
        "status": "failed" if failed else "passed",
        "checks": checks,
    }


def summarise(results: list[dict]) -> dict:
    """Count each case once. Check rows are not added to the case total."""

    errors = [item for item in results if item["status"] == "error"]
    failed = [item for item in results if item["status"] == "failed"]
    passed = [item for item in results if item["status"] == "passed"]
    total = len(results)
    if len(passed) + len(failed) + len(errors) != total:
        raise RuntimeError("case statuses were counted more than once")
    return {
        "total_cases": total,
        "passed": len(passed),
        "failed": len(failed),
        "errors": len(errors),
        "agreement_rate": round(100.0 * len(passed) / total, 1) if total else 0.0,
    }


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    output: Path | None = None
    if "--output" in argv:
        index = argv.index("--output")
        output = Path(argv[index + 1])
    dataset = load_dataset()
    ids = [case["id"] for case in dataset["cases"]]
    if len(ids) != len(set(ids)):
        sys.stderr.write("Duplicate case ids\n")
        return 1
    results = [evaluate_case(case) for case in dataset["cases"]]
    summary = summarise(results)
    report = {
        "evaluation_label": SMOKE_LABEL,
        "mode": "deterministic",
        "not_a_model_evaluation": True,
        "dataset_label": dataset.get("label"),
        "organisation_in_fixtures": dataset.get("organisation"),
        "summary": summary,
        "cases": results,
    }
    text = json.dumps(report, indent=2) + "\n"
    destination = Path(__file__).parent / "smoke_report.json"
    destination.write_text(text, encoding="utf-8")
    if output is not None:
        output.write_text(text, encoding="utf-8")
    print(
        f"Smoke test: {summary['passed']} passed, {summary['failed']} failed, "
        f"{summary['errors']} errors, {summary['total_cases']} cases"
    )
    if summary["failed"] or summary["errors"]:
        for item in results:
            if item["status"] != "passed":
                print(item["case_id"], item["status"], item["checks"])
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
