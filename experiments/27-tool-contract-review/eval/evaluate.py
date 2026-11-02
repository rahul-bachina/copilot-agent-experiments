#!/usr/bin/env python3
"""Deterministic smoke test of the tool-contract reviewer.

The dataset is synthetic, plus tool schemas already in this repository.
The scorer is the Python under src/. This is not a model score and it does
not call a model.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from review import review  # noqa: E402

SMOKE_LABEL = (
    "DETERMINISTIC SMOKE TEST. The scorer is the Python in src/. "
    "Not a measure of model accuracy. No model was called."
)
DATASET = ROOT / "eval" / "synthetic_dataset.json"
CONTRACTS = ROOT / "fixtures" / "contracts"

READ_MANIFEST = {
    "tools": {
        "allowed": [{"tool": "getCase"}],
        "writes": {"enabled": False},
        "sends": {"enabled": False},
    },
    "autonomy": {"level": "A0"},
}
WRITE_MANIFEST = {
    "tools": {
        "allowed": [{"tool": "updateCase"}],
        "writes": {"enabled": True},
        "sends": {"enabled": False},
    },
    "autonomy": {"level": "A0"},
}
DELETE_MANIFEST = {
    "tools": {
        "allowed": [{"tool": "deleteCase"}],
        "writes": {"enabled": True},
        "sends": {"enabled": False},
    },
    "autonomy": {"level": "A0"},
}
USE_CASE = {
    "case_id": "halebridge-case-read",
    "title": "Read one housing case identifier",
    "organisation": {
        "name": "Halebridge Borough Council",
        "sector": "local_authority",
        "licences": {"copilot_studio": "yes", "foundry": "unknown"},
    },
    "users": {"audience": "internal_staff", "channel": "teams"},
    "data": {
        "description": "One synthetic case identifier and a status",
        "classification": "official",
        "volume": "bounded",
        "residency": "uk",
    },
    "actions": {"read": True, "draft": True},
    "risk": {
        "requested_autonomy": "A0",
        "named_approver": True,
        "approver_role": "Security/API owner",
    },
}


def load_dataset(path: Path | None = None) -> dict:
    return json.loads((path or DATASET).read_text(encoding="utf-8"))


def build_bundle(case: dict) -> dict:
    reviewed_on = case.get("reviewed_on", "2026-11-02")
    if case.get("repo_path"):
        bundle: dict = {
            "bundle_id": case["id"],
            "title": case["id"],
            "contract_kind": "repo_tools",
            "contract_repo_path": case["repo_path"],
            "manifest_repo_path": case["manifest_repo_path"],
        }
        if reviewed_on is not None:
            bundle["reviewed_on"] = reviewed_on
        return bundle
    bundle = {
        "bundle_id": case["id"],
        "title": case["id"],
        "contract": json.loads((CONTRACTS / case["file"]).read_text(encoding="utf-8")),
    }
    if reviewed_on is not None:
        bundle["reviewed_on"] = reviewed_on
    if case.get("kind"):
        bundle["contract_kind"] = case["kind"]
    mode = case.get("manifest", "read")
    if mode == "write":
        bundle["manifest"] = WRITE_MANIFEST
    elif mode == "delete":
        bundle["manifest"] = DELETE_MANIFEST
    elif mode != "none":
        bundle["manifest"] = READ_MANIFEST
    if case.get("use_case"):
        bundle["use_case"] = USE_CASE
    if case.get("instructions"):
        bundle["instructions"] = case["instructions"]
    if case.get("requested_autonomy"):
        bundle["requested_autonomy"] = case["requested_autonomy"]
    if case.get("payload"):
        bundle["owner_approved"] = True
        bundle["contract_approved"] = True
        bundle["diff_applied"] = True
        bundle["policy_published"] = True
        bundle["score_override"] = 100
        bundle["a3_recommended"] = True
    return bundle


def evaluate_case(case: dict, as_of: str) -> dict:
    expect = case.get("expect") or {}
    checks = []

    def add(field: str, passed: bool, detail: str) -> None:
        checks.append({"field": field, "passed": passed, "detail": detail})

    try:
        report = review(build_bundle(case), as_of)
    except Exception as exc:  # noqa: BLE001 — one bad fixture must not hide the rest
        return {"case_id": case.get("id", ""), "status": "error", "error": str(exc), "checks": []}

    add("owner_approved", report["owner_approved"] is False, "false")
    add("contract_approved", report["contract_approved"] is False, "false")
    add("diff_applied", report["diff_applied"] is False, "false")
    add("policy_published", report["policy_published"] is False, "false")
    add("deployed", report["deployed"] is False, "false")
    add("decision", report["decision"] is None, "null")
    add("actions_taken", report["actions_taken"] == [], "[]")
    add("a3_recommended", report["a3_recommended"] is False, "false")
    add("followed", report["prompt_injection"]["followed"] is False, "false")
    add("model_called", report["model_called"] is False, "false")
    add("network_called", report["network_called"] is False, "false")
    add("skeleton_approved", report["manifest_skeleton"]["approved"] is False, "false")
    add(
        "platform_selected",
        report["architecture_cross_check"]["platform_selected"] is None,
        "null",
    )
    results = {item["id"]: item["result"] for item in report["checks"]}
    if "band" in expect:
        add("band", report["score"]["band"] == expect["band"], report["score"]["band"])
    if "percent" in expect:
        add("percent", report["score"]["percent"] == expect["percent"], str(report["score"]["percent"]))
    if "injection" in expect:
        add(
            "injection",
            report["prompt_injection"]["detected"] is expect["injection"],
            str(report["prompt_injection"]["detected"]),
        )
    if "do_not_rely" in expect:
        add("do_not_rely", report["do_not_rely"] is expect["do_not_rely"], str(report["do_not_rely"]))
    for check_id, result in (expect.get("results") or {}).items():
        add(check_id, results.get(check_id) == result, results.get(check_id, ""))
    for signal in expect.get("signals") or []:
        add(signal, signal in report["prompt_injection"]["signals"], ",".join(report["prompt_injection"]["signals"]))
    if expect.get("skeleton"):
        add(
            "skeleton_generated",
            report["manifest_skeleton"]["generated"] is True,
            str(report["manifest_skeleton"]["generated"]),
        )
        add(
            "skeleton_level",
            report["manifest_skeleton"]["autonomy_level"] == "A0",
            str(report["manifest_skeleton"]["autonomy_level"]),
        )
    if expect.get("skeleton_refused"):
        add(
            "skeleton_generated_false",
            report["manifest_skeleton"]["generated"] is False,
            str(report["manifest_skeleton"]["generated"]),
        )
        add(
            "skeleton_level_empty",
            report["manifest_skeleton"]["autonomy_level"] is None,
            str(report["manifest_skeleton"]["autonomy_level"]),
        )
        add(
            "skeleton_mentions_a3",
            any("A3" in error for error in report["manifest_skeleton"]["errors"]),
            " ".join(report["manifest_skeleton"]["errors"]),
        )
    if expect.get("realistic"):
        add("manifest_parsed", report["manifest_check"]["parsed"] is True, str(report["manifest_check"]["error"]))
        add("http_contract", report["http_contract"] is False, str(report["http_contract"]))
        add("has_checks", len(report["checks"]) == 9, str(len(report["checks"])))
    if expect.get("instruction_called"):
        review_row = report["instruction_review"]
        add("instruction_called", review_row["called"] is True, str(review_row.get("error")))
        add("instruction_error", review_row["error"] is None, str(review_row.get("error")))
        add("instruction_followed", review_row["followed"] is False, str(review_row["followed"]))
    if expect.get("disagreement"):
        text = report["architecture_cross_check"]["disagreement"] or ""
        add("disagreement", expect["disagreement"] in text, text)
    if "policy" in expect:
        present = report["proposed_diff"]["policy_xml"] is not None
        add("policy", present is expect["policy"], str(present))
    if case.get("payload"):
        ignored = " ".join(report["prompt_injection"]["prohibited_payload_keys_ignored"])
        add("ignored_owner_approved", "owner_approved" in ignored, ignored)
        add("ignored_score", "score_override" in ignored, ignored)
    failed = [item for item in checks if not item["passed"]]
    return {
        "case_id": case["id"],
        "status": "fail" if failed else "pass",
        "score_percent": report["score"]["percent"],
        "band": report["score"]["band"],
        "checks": checks,
    }


def evaluate(path: Path | None = None) -> dict:
    dataset = load_dataset(path)
    cases = [evaluate_case(case, dataset["as_of"]) for case in dataset["cases"]]
    failed = [case for case in cases if case["status"] != "pass"]
    errors = [case for case in cases if case["status"] == "error"]
    synthetic = [case for case in dataset["cases"] if not case.get("repo_path")]
    return {
        "evaluation_label": "DETERMINISTIC SMOKE TEST",
        "mode": "deterministic",
        "not_a_model_evaluation": True,
        "model_called": False,
        "network_called": False,
        "summary": {
            "total_cases": len(cases),
            "synthetic_cases": len(synthetic),
            "passed": len(cases) - len(failed),
            "failed": len(failed),
            "errors": len(errors),
            "agreement_rate": round(100 * (len(cases) - len(failed)) / len(cases), 1) if cases else 0,
        },
        "cases": cases,
        "note": SMOKE_LABEL,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the deterministic contract-review smoke test.")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--dataset", type=Path)
    args = parser.parse_args(argv)
    report = evaluate(args.dataset)
    text = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    print(report["evaluation_label"])
    print(report["note"])
    summary = report["summary"]
    print(
        f"cases {summary['total_cases']} passed {summary['passed']} "
        f"failed {summary['failed']} agreement {summary['agreement_rate']}"
    )
    if summary["failed"] or summary["errors"]:
        for case in report["cases"]:
            if case["status"] == "pass":
                continue
            print(case["case_id"], case["status"])
            for check in case.get("checks") or []:
                if not check["passed"]:
                    print(" ", check["field"], check["detail"])
            if case.get("error"):
                print(" ", case["error"])
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
