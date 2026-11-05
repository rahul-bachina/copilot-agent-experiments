#!/usr/bin/env python3
"""Deterministic smoke test of the cross-source comparison.

The dataset is synthetic. The scorer is the Python under src/. This is not a
model score and it does not call Microsoft Foundry. Case totals count cases
once. Fact counts and occurrence counts stay on each case and are not added
to total_cases.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.compare import CompareForbidden, NotSynthetic, choose_source, compare  # noqa: E402
from tests.support import document, pair  # noqa: E402

SMOKE_LABEL = (
    "DETERMINISTIC SMOKE TEST. The scorer is the Python in src/. "
    "Not a measure of model accuracy. No model was called. "
    "Not a Microsoft Foundry score. Not a correction of any record."
)
DATASET = ROOT / "eval" / "synthetic_dataset.json"
SAMPLE = ROOT / "examples" / "sample_pack.json"
AS_OF = "2026-11-05"


def load_dataset(path: Path | None = None) -> dict:
    return json.loads((path or DATASET).read_text(encoding="utf-8"))


def _sample() -> dict:
    return json.loads(SAMPLE.read_text(encoding="utf-8"))


def _safety(draft: dict) -> dict:
    return {
        "agent_chose_source": draft["agent_chose_source"],
        "records_edited": draft["records_edited"],
        "parties_contacted": draft["parties_contacted"],
        "register_queried": draft["register_queried"],
        "model_called": draft["model_called"],
        "foundry_called": draft["foundry_called"],
        "a3_recommended": draft["a3_recommended"],
        "output_is_anonymised": draft["output_is_anonymised"],
        "correct_value": draft["facts"][0]["correct_value"] if draft.get("facts") else None,
    }


def _fail_safety(draft: dict) -> list[str]:
    flags = _safety(draft)
    bad = []
    for key, value in flags.items():
        if key == "correct_value":
            if value is not None:
                bad.append(key)
        elif value is not False:
            bad.append(key)
    return bad


def score_case(case: dict) -> dict:
    mode = case["mode"]
    row = {"id": case["id"], "mode": mode, "passed": False, "fact_count": None, "occurrence_count": None}
    try:
        if mode == "pair":
            draft = compare(pair(case["field_type"], case["left"], case["right"]), AS_OF)
            fact = draft["facts"][0]
            row["fact_count"] = draft["counts"]["fact_count"]
            row["occurrence_count"] = draft["counts"]["occurrence_count"]
            row["classification"] = fact["classification"]
            row["reason"] = fact["reason"]
            row["passed"] = (
                fact["classification"] == case["expected_class"]
                and fact["reason"] == case["expected_reason"]
                and not _fail_safety(draft)
            )
        elif mode == "sample":
            draft = compare(_sample(), AS_OF)
            counts = draft["counts"]
            row["fact_count"] = counts["fact_count"]
            row["occurrence_count"] = counts["occurrence_count"]
            row["passed"] = (
                counts["match_count"] == case["expected_match"]
                and counts["immaterial_count"] == case["expected_immaterial"]
                and counts["material_count"] == case["expected_material"]
                and counts["occurrence_count"] == case["expected_occurrences"]
                and draft["awaiting_reviewer"] is True
                and draft["prompt_injection"]["followed"] is False
                and not _fail_safety(draft)
            )
        elif mode == "withheld":
            draft = compare(pair("name", "NHS number 999 123 4567", "A Example"), AS_OF)
            blob = json.dumps(draft)
            fact = draft["facts"][0]
            row["fact_count"] = 1
            row["occurrence_count"] = draft["counts"]["occurrence_count"]
            row["passed"] = (
                fact["reason"] == "identifier_withheld"
                and "999 123 4567" not in blob
                and fact["resolved"] is False
                and not _fail_safety(draft)
            )
        elif mode == "pinpoint":
            pack = {
                "synthetic": True,
                "pack_id": "pin-1",
                "facts": [{"fact_key": "fact", "field_type": "currency"}],
                "documents": [
                    document("left-doc", "form", "GBP 99.00", line="Amount: GBP 10.00"),
                    document("right-doc", "contract", "GBP 10.00"),
                ],
            }
            draft = compare(pack, AS_OF)
            row["fact_count"] = 1
            row["occurrence_count"] = draft["counts"]["occurrence_count"]
            row["passed"] = (
                draft["facts"][0]["reason"] == "pinpoint_failed"
                and "GBP 99.00" not in json.dumps(draft)
                and not _fail_safety(draft)
            )
        elif mode == "single":
            pack = {
                "synthetic": True,
                "pack_id": "one-doc",
                "facts": [{"fact_key": "fact", "field_type": "reference"}],
                "documents": [document("left-doc", "form", "NF-1001")],
            }
            draft = compare(pack, AS_OF)
            row["fact_count"] = 1
            row["occurrence_count"] = 1
            row["passed"] = draft["facts"][0]["reason"] == "fewer_than_two_sources" and draft["facts"][0]["resolved"] is False
        elif mode == "resolution":
            resolutions = {
                "role": "Reviewer",
                "reviewer_ref": "REV-1001",
                "signed_on": AS_OF,
                "items": [{"fact_key": "fact", "choice": "neither"}],
            }
            draft = compare(pair("currency", "GBP 10.00", "GBP 20.00"), AS_OF, resolutions=resolutions)
            fact = draft["facts"][0]
            row["fact_count"] = 1
            row["occurrence_count"] = 2
            row["passed"] = (
                fact["resolved"] is True
                and fact["reviewer_choice"] == "neither"
                and fact["correct_value"] is None
                and draft["records_edited"] is False
                and draft["agent_chose_source"] is False
            )
        elif mode == "buried":
            pack = pair("currency", "GBP 10.00", "GBP 20.00")
            pack["resolved"] = True
            draft = compare(pack, AS_OF)
            row["fact_count"] = 1
            row["occurrence_count"] = 2
            row["passed"] = draft["facts"][0]["resolved"] is False and draft["awaiting_reviewer"] is True
        elif mode == "stale-document":
            pack = {
                "synthetic": True,
                "pack_id": "stale-1",
                "facts": [{"fact_key": "fact", "field_type": "reference"}],
                "documents": [
                    document("left-doc", "form", "NF-1001", reviewed_on="2026-01-01"),
                    document("right-doc", "contract", "NF-1001", reviewed_on="2026-01-01"),
                ],
            }
            draft = compare(pack, AS_OF)
            row["fact_count"] = 1
            row["occurrence_count"] = 2
            row["passed"] = (
                draft["facts"][0]["classification"] == "match"
                and draft["do_not_rely"] is True
                and draft["facts"][0]["resolved"] is False
            )
        elif mode == "stale-pins":
            draft = compare(_sample(), "2027-05-05", stale_after_days=90)
            counts = draft["counts"]
            row["fact_count"] = counts["fact_count"]
            row["occurrence_count"] = counts["occurrence_count"]
            opened = [item for item in draft["sources"] if item["stale_applicable"]]
            row["passed"] = (
                counts["material_count"] == 2
                and counts["match_count"] == 1
                and draft["pins_stale"] is True
                and draft["do_not_rely"] is True
                and draft["agent_chose_source"] is False
                and opened
                and all(item["stale"] is True for item in opened)
            )
        elif mode == "not-synthetic":
            try:
                compare({"synthetic": False, "pack_id": "x"}, AS_OF)
            except NotSynthetic:
                row["passed"] = True
            row["fact_count"] = None
            row["occurrence_count"] = None
        elif mode == "prohibited":
            try:
                choose_source()
            except CompareForbidden:
                row["passed"] = True
        else:
            row["error"] = "unknown mode"
    except Exception as exc:  # noqa: BLE001 — the smoke row records the failure
        row["error"] = type(exc).__name__
        row["passed"] = False
    return row


def evaluate(dataset: dict | None = None) -> dict:
    data = dataset or load_dataset()
    cases = [score_case(case) for case in data["cases"]]
    passed = sum(1 for case in cases if case["passed"])
    total = len(cases)
    return {
        "evaluation_label": SMOKE_LABEL,
        "mode": "deterministic",
        "not_a_model_evaluation": True,
        "foundry_called": False,
        "facts_are_not_added_to_total_cases": True,
        "occurrences_are_not_added_to_total_cases": True,
        "summary": {
            "total_cases": total,
            "passed": passed,
            "failed": total - passed,
            "agreement_rate": round(100 * passed / total, 1) if total else 0,
            "facts_are_not_added_to_total_cases": True,
            "occurrences_are_not_added_to_total_cases": True,
        },
        "cases": cases,
        "note": "total_cases counts cases once. Fact counts and occurrence counts stay on each case.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Deterministic smoke test. Experiment 36.")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    report = evaluate()
    text = json.dumps(report, indent=2)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    summary = report["summary"]
    print(
        f"Smoke test: {summary['passed']}/{summary['total_cases']} "
        f"({summary['agreement_rate']}%). Not a model score.",
        file=sys.stderr,
    )
    return 0 if summary["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
