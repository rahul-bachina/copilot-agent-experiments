#!/usr/bin/env python3
"""Deterministic smoke test of the instruction reviewer.

The dataset is synthetic, plus instruction files already in this repository.
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
INSTRUCTIONS = ROOT / "fixtures" / "instructions"


def load_dataset(path: Path | None = None) -> dict:
    return json.loads((path or DATASET).read_text(encoding="utf-8"))


def build_bundle(case: dict) -> dict:
    reviewed_on = case.get("reviewed_on", "2026-10-30")
    if case.get("repo_path"):
        document = {
            "path": case["repo_path"],
            "kind": "skill" if case["repo_path"].endswith("SKILL.md") else "system_prompt",
            "reviewed_on": reviewed_on,
            "repo_path": case["repo_path"],
        }
        bundle = {
            "bundle_id": case["id"],
            "title": case["id"],
            "documents": [document],
            "manifest_repo_path": case["manifest_repo_path"],
        }
        return bundle
    document = {
        "path": case["file"],
        "kind": "system_prompt",
        "reviewed_on": reviewed_on,
        "text": (INSTRUCTIONS / case["file"]).read_text(encoding="utf-8"),
    }
    bundle: dict = {"bundle_id": case["id"], "title": case["id"], "documents": [document]}
    if case.get("manifest", True):
        sends = bool(case.get("sends"))
        bundle["manifest"] = {
            "tools": {
                "allowed": [{"tool": "read_policy_file"}],
                "writes": {"enabled": False},
                "sends": {"enabled": sends},
            },
            "autonomy": {"level": "A0"},
        }
    if case.get("use_case"):
        bundle["use_case"] = {
            "case_id": "halebridge-policy",
            "title": "Halebridge policy questions",
            "organisation": {
                "name": "Halebridge Borough Council",
                "sector": "local_authority",
                "licences": {"copilot_studio": "yes"},
            },
            "users": {"audience": "internal_staff", "channel": "teams"},
            "data": {
                "description": "Published staff policies",
                "classification": "official",
                "volume": "bounded",
                "residency": "uk",
            },
            "actions": {"read": True, "draft": True},
            "risk": {
                "requested_autonomy": "A0",
                "named_approver": True,
                "approver_role": "Agent owner",
            },
        }
    if case.get("payload"):
        bundle["owner_approved"] = True
        bundle["diff_applied"] = True
        bundle["score_override"] = 100
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
    add("diff_applied", report["diff_applied"] is False, "false")
    add("deployed", report["deployed"] is False, "false")
    add("decision", report["decision"] is None, "null")
    add("actions_taken", report["actions_taken"] == [], "[]")
    add("a3_recommended", report["a3_recommended"] is False, "false")
    add("followed", report["prompt_injection"]["followed"] is False, "false")
    add("model_called", report["model_called"] is False, "false")
    add("network_called", report["network_called"] is False, "false")
    add("skeleton_approved", report["manifest_skeleton"]["approved"] is False, "false")
    add("platform_selected", report["architecture_cross_check"]["platform_selected"] is None, "null")
    results = {item["id"]: item["result"] for item in report["checks"]}
    if "band" in expect:
        add("band", report["score"]["band"] == expect["band"], report["score"]["band"])
    if "percent" in expect:
        add("percent", report["score"]["percent"] == expect["percent"], str(report["score"]["percent"]))
    if "injection" in expect:
        add("injection", report["prompt_injection"]["detected"] is expect["injection"], str(report["prompt_injection"]["detected"]))
    if "do_not_rely" in expect:
        add("do_not_rely", report["do_not_rely"] is expect["do_not_rely"], str(report["do_not_rely"]))
    for check_id, result in (expect.get("results") or {}).items():
        add(check_id, results.get(check_id) == result, results.get(check_id, ""))
    for signal in expect.get("signals") or []:
        add(signal, signal in report["prompt_injection"]["signals"], ",".join(report["prompt_injection"]["signals"]))
    if expect.get("skeleton"):
        add("skeleton_generated", report["manifest_skeleton"]["generated"] is True, str(report["manifest_skeleton"]["generated"]))
        add("skeleton_level", report["manifest_skeleton"]["autonomy_level"] == "A0", str(report["manifest_skeleton"]["autonomy_level"]))
    if expect.get("skeleton_refused"):
        add("skeleton_level_empty", report["manifest_skeleton"]["autonomy_level"] is None, str(report["manifest_skeleton"]["autonomy_level"]))
        add("skeleton_mentions_a3", any("A3" in error for error in report["manifest_skeleton"]["errors"]), " ".join(report["manifest_skeleton"]["errors"]))
    if expect.get("realistic"):
        add("manifest_parsed", report["manifest_check"]["parsed"] is True, str(report["manifest_check"]["error"]))
        add("has_checks", len(report["checks"]) == 9, str(len(report["checks"])))
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
    parser = argparse.ArgumentParser(description="Run the deterministic instruction-review smoke test.")
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
