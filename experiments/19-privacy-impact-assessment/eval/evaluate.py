#!/usr/bin/env python3
"""Deterministic smoke test. Not a model evaluation.

The fixtures are synthetic. Agreement is the core returning the expected
screen codes on those fixtures. A live model has not been scored.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from assess import assess  # noqa: E402

NINO = "QQ 12 34 56 A"
LABEL = "DETERMINISTIC SMOKE TEST. Not a model evaluation."


def _all_no() -> dict:
    keys = (
        "article_35_3_a",
        "article_35_3_b",
        "article_35_3_c",
        "innovative_technology",
        "denial_of_service",
        "large_scale_profiling",
        "biometric_data",
        "genetic_data",
        "data_matching",
        "invisible_processing",
        "tracking",
        "targeting_children_or_vulnerable",
        "risk_of_physical_harm",
        "wp248_evaluation_or_scoring",
        "wp248_automated_decision_legal_or_similar",
        "wp248_systematic_monitoring",
        "wp248_sensitive_or_highly_personal",
        "wp248_large_scale",
        "wp248_matching_datasets",
        "wp248_vulnerable_data_subjects",
        "wp248_innovative_use",
        "wp248_prevents_rights_or_service",
        "genetic_data_direct_care_by_individual_professional",
        "article_35_1_controller_view",
    )
    return {key: "no" for key in keys}


def base_brief() -> dict:
    return {
        "synthetic": True,
        "project_name": "Northwharf housing allocation scorer",
        "organisation_name": "Northwharf Borough Council (fictional)",
        "screening": _all_no(),
        "description": {
            "nature": "A fictional scorer reads a housing form and returns a band.",
            "scope": "One fictional pilot. No live applicants.",
            "context": "The council is fictional.",
            "purposes": "To show the project team a draft DPIA.",
            "legitimate_interest": "",
        },
        "necessity": {"purpose_helped": "The band would replace a caseworker.", "other_reasonable_way": "Keep the caseworker."},
        "consultation": {"individuals_consulted": "unknown", "dpo_designated": "yes", "dpo_advice_recorded": ""},
        "risks": [
            {
                "id": "R1",
                "description": "A band is treated as the allocation decision.",
                "source": "The project brief.",
                "likelihood": "Medium",
                "severity": "Medium",
                "harm_types": ["inability to access services or opportunities"],
                "mitigation": "",
                "effect_of_mitigation": "unknown",
                "residual": "Medium",
            }
        ],
        "residual_risk_overall": "Medium",
        "automated_decision": {
            "processing_regime": "uk_gdpr",
            "processes_personal_data": "yes",
            "meaningful_human_involvement": "yes",
            "significant_effect": "none",
            "special_category_data": "no",
            "lawful_basis": "Article 6(1)(e)",
            "decision_taken_before_5_february_2026": "no",
        },
        "exemption_claimed": "no",
    }


def _merge(base: dict, override: dict) -> dict:
    merged = json.loads(json.dumps(base))
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key].update(value)
        else:
            merged[key] = value
    return merged


def _get(draft: dict, path: str):
    current = draft
    for part in path.split("."):
        current = current[part]
    return current


def cases() -> list[dict]:
    dataset = json.loads((Path(__file__).parent / "synthetic_dataset.json").read_text(encoding="utf-8"))
    return dataset["cases"]


def run() -> dict:
    results = []
    for case in cases():
        brief = _merge(base_brief(), case.get("brief") or {})
        as_of = case.get("as_of", "2026-10-28")
        row = {"id": case["id"], "passed": False, "failures": []}
        try:
            if case.get("expect_raise") == "NotSynthetic":
                try:
                    assess(brief, as_of=as_of)
                except Exception as exc:  # noqa: BLE001
                    row["passed"] = type(exc).__name__ == "NotSynthetic" and NINO not in str(exc)
                    if not row["passed"]:
                        row["failures"].append(type(exc).__name__)
                else:
                    row["failures"].append("did_not_raise")
                results.append(row)
                continue
            draft = assess(brief, as_of=as_of)
            for path, expected in case["expect"].items():
                actual = _get(draft, path)
                if actual != expected:
                    row["failures"].append({"path": path, "expected": expected, "actual": actual})
            if case.get("absent_from_draft"):
                serialised = json.dumps(draft)
                for token in case["absent_from_draft"]:
                    if token in serialised:
                        row["failures"].append({"present": token})
            if case.get("absent_from_sections"):
                serialised = json.dumps(draft["sections"])
                for token in case["absent_from_sections"]:
                    if token.lower() in serialised.lower():
                        row["failures"].append({"present_in_sections": token})
            row["passed"] = not row["failures"]
        except Exception as exc:  # noqa: BLE001
            row["failures"].append(f"{type(exc).__name__}: {exc}")
        results.append(row)
    failed = [row for row in results if not row["passed"]]
    return {
        "evaluation_label": LABEL,
        "mode": "deterministic",
        "not_a_model_evaluation": True,
        "model_called": False,
        "summary": {
            "total_cases": len(results),
            "passed": len(results) - len(failed),
            "failed": len(failed),
            "errors": len(failed),
            "agreement_rate": round(100 * (len(results) - len(failed)) / len(results), 2) if results else 0,
        },
        "cases": results,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Smoke-test the DPIA draft. Not a model score.")
    parser.add_argument("--output", help="Write the report JSON here. Default is stdout.")
    args = parser.parse_args(argv)
    report = run()
    text = json.dumps(report, indent=2)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0 if report["summary"]["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
