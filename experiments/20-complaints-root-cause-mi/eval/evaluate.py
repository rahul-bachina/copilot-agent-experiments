#!/usr/bin/env python3
"""Deterministic smoke test. Not a model evaluation.

The fixtures are synthetic. Agreement is the core returning the expected
fields on those fixtures. A live model has not been scored.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from report import draft_report  # noqa: E402

NINO = "QQ 12 34 56 A"
LABEL = "DETERMINISTIC SMOKE TEST. Not a model evaluation."


def base_batch() -> dict:
    return {
        "batch_id": "SYN-EVAL",
        "synthetic": True,
        "sector": "financial_services",
        "organisation_name": "Northbridge Mutual",
        "period": {"start": "2026-01-01", "end": "2026-06-30"},
        "records": [
            {
                "record_id": "FS1",
                "received_on": "2026-03-02",
                "narrative": (
                    "I am unhappy. I was charged a fee on my current account and I want a refund."
                ),
                "outcome": "open",
                "redress_gbp": 10,
            }
        ],
    }


def _merge(base: dict, override: dict) -> dict:
    merged = json.loads(json.dumps(base))
    for key, value in override.items():
        if key == "records":
            merged[key] = value
        elif isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _get(draft: dict, path: str):
    current = draft
    for part in path.split("."):
        if isinstance(current, list):
            current = current[int(part)]
        else:
            current = current[part]
    return current


def _missing(draft: dict, path: str) -> bool:
    try:
        _get(draft, path)
    except (KeyError, IndexError, TypeError):
        return True
    return False


def cases() -> list[dict]:
    dataset = json.loads((Path(__file__).parent / "synthetic_dataset.json").read_text(encoding="utf-8"))
    return dataset["cases"]


def run() -> dict:
    results = []
    for case in cases():
        batch = _merge(base_batch(), case.get("batch") or {})
        as_of = date.fromisoformat(case.get("as_of", "2026-10-29"))
        row = {"id": case["id"], "passed": False, "failures": []}
        try:
            if case.get("expect_raise") == "NotSynthetic":
                try:
                    draft_report(batch, as_of=as_of)
                except Exception as exc:  # noqa: BLE001
                    message = str(exc)
                    row["passed"] = type(exc).__name__ == "NotSynthetic" and NINO not in message
                    if not row["passed"]:
                        row["failures"].append(type(exc).__name__)
                else:
                    row["failures"].append("did_not_raise")
                results.append(row)
                continue
            draft = draft_report(batch, as_of=as_of)
            for path, expected in (case.get("expect") or {}).items():
                actual = _get(draft, path)
                if actual != expected:
                    row["failures"].append({"path": path, "expected": expected, "actual": actual})
            serialised = json.dumps(draft)
            for token in case.get("absent_from_draft") or []:
                if token in serialised:
                    row["failures"].append({"present": token})
            narrative = " ".join(item["text"] for item in draft["narrative"])
            for token in case.get("absent_from_narrative") or []:
                if token in narrative:
                    row["failures"].append({"present_in_narrative": token})
            for sentence_id in case.get("absent_sentence_ids") or []:
                if any(item["sentence_id"] == sentence_id for item in draft["narrative"]):
                    row["failures"].append({"sentence_present": sentence_id})
            for path in case.get("missing_paths") or []:
                if not _missing(draft, path):
                    row["failures"].append({"path_present": path})
            row["passed"] = not row["failures"]
        except Exception as exc:  # noqa: BLE001
            row["failures"].append(f"{type(exc).__name__}: {exc}")
        results.append(row)
    failed = [item for item in results if not item["passed"]]
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
    parser = argparse.ArgumentParser(description="Smoke-test the complaints MI draft. Not a model score.")
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
