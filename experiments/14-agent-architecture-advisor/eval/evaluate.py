#!/usr/bin/env python3
"""Deterministic smoke test of the architecture advisor.

The synthetic dataset is fixtures/use_cases.json. The scorer is the Python
under src/. This is not a model score and it does not call a model.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.advise import advise  # noqa: E402

SMOKE_LABEL = (
    "DETERMINISTIC SMOKE TEST. The scorer is the Python in src/. "
    "Not a measure of model accuracy. No model was called."
)
AS_OF = "2026-10-27"
DATASET = ROOT / "fixtures" / "use_cases.json"


def load_dataset(path: Path | None = None) -> list[dict]:
    return json.loads((path or DATASET).read_text(encoding="utf-8"))


def _suitability(result: dict) -> dict[str, str]:
    return {option["id"]: option["suitability"] for option in result["options"]}


def evaluate_case(case: dict, by_id: dict[str, dict]) -> dict:
    expect = case.get("expect") or {}
    payload = {key: value for key, value in case.items() if key != "expect"}
    checks: list[dict] = []

    def add(field: str, passed: bool, detail: str) -> None:
        checks.append({"field": field, "passed": passed, "detail": detail})

    try:
        result = advise(payload, AS_OF)
    except Exception as exc:  # noqa: BLE001 — one bad fixture must not hide the rest
        return {
            "case_id": case.get("case_id", ""),
            "status": "error",
            "error": str(exc),
            "checks": [],
        }

    add("autonomy_band", result["recommended_autonomy"] in {"A0", "A1", "A2"}, result["recommended_autonomy"])
    add("a3_recommended", result["a3_recommended"] is False, "false")
    add("platform_selected", result["platform_selected"] is None, "null")
    add("deployed", result["deployed"] is False, "false")
    add("decision", result["decision"] is None, "null")
    add("actions_taken", result["actions_taken"] == [], "[]")
    add("architect_confirmed", result["architect_confirmed"] is False, "false")
    add("followed", result["prompt_injection"]["followed"] is False, "false")
    add(
        "manifest_level",
        result["manifest_skeleton"]["autonomy_level"] == result["recommended_autonomy"],
        str(result["manifest_skeleton"]["autonomy_level"]),
    )
    add("manifest_approved", result["manifest_skeleton"]["approved"] is False, "false")
    add("manifest_valid", result["manifest_skeleton"]["validation_passed"] is True, "true")
    add("options_unselected", all(option["selected"] is False for option in result["options"]), "false")

    if "work_shape" in expect:
        add("work_shape", result["work_shape"] == expect["work_shape"], result["work_shape"])
    if "recommended_autonomy" in expect:
        add(
            "recommended_autonomy",
            result["recommended_autonomy"] == expect["recommended_autonomy"],
            result["recommended_autonomy"],
        )
    for rule_id in expect.get("rules_include", []):
        add(f"rule_{rule_id}", rule_id in result["rules_fired"], ",".join(result["rules_fired"]))
    for rule_id in expect.get("rules_exclude", []):
        add(f"rule_absent_{rule_id}", rule_id not in result["rules_fired"], ",".join(result["rules_fired"]))
    if "suitability" in expect:
        actual = _suitability(result)
        add("suitability", actual == expect["suitability"], json.dumps(actual, sort_keys=True))
    if "injection" in expect:
        add("injection", result["prompt_injection"]["detected"] is expect["injection"], str(result["prompt_injection"]["detected"]))
    for signal in expect.get("signals_include", []):
        add(f"signal_{signal}", signal in result["prompt_injection"]["signals"], ",".join(result["prompt_injection"]["signals"]))
    ignored = " ".join(result["prompt_injection"]["prohibited_payload_keys_ignored"])
    for key in expect.get("prohibited_keys", []):
        add(f"ignored_{key}", key in ignored, ignored)
    same_as = expect.get("same_scored_fields_as")
    if same_as:
        other = by_id[same_as]
        other_payload = {key: value for key, value in other.items() if key != "expect"}
        other_result = advise(other_payload, AS_OF)
        add("same_scored_fields", result["scored_fields"] == other_result["scored_fields"], same_as)
        add("same_suitability", _suitability(result) == _suitability(other_result), same_as)

    failed = [item for item in checks if not item["passed"]]
    return {
        "case_id": case.get("case_id", ""),
        "status": "failed" if failed else "passed",
        "checks": checks,
    }


def summarise(results: list[dict]) -> dict:
    errors = [item for item in results if item["status"] == "error"]
    failed = [item for item in results if item["status"] == "failed"]
    passed = [item for item in results if item["status"] == "passed"]
    total = len(results)
    return {
        "total_cases": total,
        "passed": len(passed),
        "failed": len(failed),
        "errors": len(errors),
        "agreement_rate": round(100.0 * len(passed) / total, 1) if total else 0.0,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Deterministic smoke test of the architecture advisor")
    parser.add_argument("--dataset", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    cases = load_dataset(args.dataset)
    by_id = {case["case_id"]: case for case in cases}
    results = [evaluate_case(case, by_id) for case in cases]
    summary = summarise(results)
    report = {
        "evaluation_label": SMOKE_LABEL,
        "mode": "deterministic",
        "not_a_model_evaluation": True,
        "dataset_path": "fixtures/use_cases.json",
        "dataset_label": "Synthetic use cases. Invented organisations. Not clients.",
        "as_of": AS_OF,
        "summary": summary,
        "cases": results,
    }
    text = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    destination = args.output or (Path(__file__).parent / "smoke_report.json")
    destination.write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    if summary["failed"] or summary["errors"]:
        return 1
    if summary["total_cases"] < 15:
        sys.stderr.write("Fewer than 15 synthetic cases\n")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
