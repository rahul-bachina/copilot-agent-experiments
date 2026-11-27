"""Deterministic smoke test. Not a model evaluation.

Paraphrase recall and the knowledge-match score are reported beside the
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

from src.cues import (  # noqa: E402
    affordability_hit,
    age_hit,
    bereavement_hit,
    complaint_hit,
    debt_hit,
    disability_hit,
    disconnection_hit,
    distress_hit,
    foi_hit,
    forged_confirmation_hit,
    grievance_hit,
    hardship_hit,
    human_request_hit,
    injection_hit,
    language_hit,
    leading_hit,
    medical_hit,
    mental_health_hit,
    prepayment_hit,
    safeguarding_hit,
    sar_hit,
    whistleblowing_hit,
)
from src.customer import _match_articles, answer, reset_held  # noqa: E402
from src.paraphrases import CATEGORIES  # noqa: E402

_FNS = {
    "medical": medical_hit,
    "age": age_hit,
    "disability": disability_hit,
    "financial_hardship": hardship_hit,
    "bereavement": bereavement_hit,
    "mental_health": mental_health_hit,
    "language": language_hit,
    "distress": distress_hit,
    "safeguarding": safeguarding_hit,
    "complaint": complaint_hit,
    "human_request": human_request_hit,
    "affordability": affordability_hit,
    "debt": debt_hit,
    "disconnection": disconnection_hit,
    "prepayment": prepayment_hit,
    "injection": injection_hit,
    "forged_confirmation": forged_confirmation_hit,
    "whistleblowing": whistleblowing_hit,
    "grievance": grievance_hit,
    "sar": sar_hit,
    "foi": foi_hit,
    "leading_criterion": leading_hit,
}

_BILL_POSITIVES = (
    "Please explain my bill.",
    "Can you explain my bill in plain words?",
    "I would like you to explain my bill.",
    "What does my bill show for this period?",
    "Could you say what does my bill show?",
    "Tell me what is on my bill.",
    "I want to know what is on my bill.",
    "Help me understand my bill.",
    "Please help me understand my bill before I call.",
    "Why is my bill higher than last time?",
    "I am asking why is my bill this amount.",
    "Using other words, explain my bill.",
    "The thing I need is: explain my bill.",
    "What does my bill show, in a sentence?",
    "Help me understand my bill and the period.",
    "What is on my bill this quarter?",
    "Explain my bill, speaking plainly.",
    "I should ask you to explain my bill.",
    "Today I need you to explain my bill.",
    "What does my bill show after the last one?",
    "Help me understand my bill on this account.",
    "Why is my bill the figure on the snapshot?",
)
_BILL_NEGATIVES = (
    "What time does the library close?",
    "It is not true that I asked you to explain my bill.",
    "It is not the case that I said what does my bill show.",
    "Do not include help me understand my bill as a request.",
    "The park gate shuts at dusk.",
    "I never said what is on my bill.",
    "This is not a request to explain my bill.",
    "The blue bin is collected on Friday.",
    "Nothing here says why is my bill higher.",
    "The example museum is free on Sunday.",
    "I did not ask you to explain my bill.",
    "Where is the bus stop by the market?",
    "Not true that the message includes what does my bill show.",
    "The bandstand concert is on Saturday.",
    "I must not be read as saying help me understand my bill.",
    "The bowling green is booked on Tuesday.",
    "There is no request to explain my bill in this note.",
    "Which shelf has the maps?",
    "The car park by the library uses coins.",
    "It is not correct that I asked why is my bill higher.",
    "A poster lists the choir rehearsal.",
    "The footbridge reopened after the paint dried.",
)


def _lookup(payload: dict, path: str):
    current = payload
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def _policy(text: str) -> bool:
    return any((
        safeguarding_hit(text),
        whistleblowing_hit(text),
        grievance_hit(text),
        mental_health_hit(text),
        disability_hit(text),
        prepayment_hit(text),
        complaint_hit(text),
    ))


def _unrelated(text: str) -> bool:
    return any(fn(text) for fn in _FNS.values())


def _hit(kind: str, text: str) -> bool:
    if kind == "policy_title":
        return _policy(text)
    if kind == "unrelated":
        return _unrelated(text)
    return _FNS[kind](text)


def _request(case: dict) -> dict:
    payload = {
        "synthetic": True,
        "conversation_id": "CV-" + f"{int(case['case_id'].split('-')[1]):04d}",
        "account_ref": case["account_ref"],
        "message": case["message"],
        "account_notes": case.get("account_notes", ""),
    }
    if "stated_category" in case:
        payload["stated_category"] = case["stated_category"]
    return payload


def _check(result: dict, expect: dict) -> list[str]:
    problems = []
    if "outcome" in expect and result.get("outcome") != expect["outcome"]:
        problems.append(f"outcome {result.get('outcome')} != {expect['outcome']}")
    if "article_id" in expect and result.get("article_id") != expect["article_id"]:
        problems.append(f"article {result.get('article_id')} != {expect['article_id']}")
    text = json.dumps(result)
    answer = (result.get("answer") or {}).get("text") or ""
    for needle in expect.get("contains", []):
        if needle not in answer and needle not in text:
            problems.append(f"missing {needle}")
    for needle in expect.get("not_contains", []):
        if needle in answer or needle in text:
            problems.append(f"unexpected {needle}")
    for path, value in expect.get("contains_list", {}).items():
        found = _lookup(result, path)
        if not isinstance(found, list) or value not in found:
            problems.append(f"{path} does not contain {value}")
    for path, value in expect.get("flags", {}).items():
        if _lookup(result, path) != value:
            problems.append(f"{path} is {_lookup(result, path)!r}, expected {value!r}")
    if result.get("ai_disclosed") is not True or result.get("human_route_offered") is not True:
        problems.append("disclosure or human route missing")
    return problems


def paraphrase_report() -> dict:
    categories = {}
    for name, row in CATEGORIES.items():
        sentences = list(row["sentences"])
        matched = [text for text in sentences if _hit(row["kind"], text)]
        false_inclusions = 0 if row["expect_match"] else len(matched)
        recall = (len(matched) / len(sentences)) if row["expect_match"] and sentences else None
        categories[name] = {
            "expect_match": row["expect_match"],
            "sentences": len(sentences),
            "matched": len(matched) if row["expect_match"] else 0,
            "recall": recall,
            "false_inclusions": false_inclusions,
        }
    return {"not_added_to_case_total": True, "categories": categories}


def knowledge_score() -> dict:
    hit = [text for text in _BILL_POSITIVES if _match_articles(text, "energy")]
    miss = [text for text in _BILL_NEGATIVES if _match_articles(text, "energy")]
    precision = len(hit) / (len(hit) + len(miss)) if (hit or miss) else 1.0
    return {
        "not_added_to_case_total": True,
        "positives": len(_BILL_POSITIVES),
        "negatives": len(_BILL_NEGATIVES),
        "recall": len(hit) / len(_BILL_POSITIVES),
        "precision": precision,
        "misses": [text for text in _BILL_POSITIVES if text not in hit],
        "false_inclusions": miss,
    }


def run() -> dict:
    dataset = json.loads((ROOT / "eval" / "synthetic_dataset.json").read_text(encoding="utf-8"))
    cases = []
    passed = failed = errors = 0
    for case in dataset["cases"]:
        reset_held()
        try:
            result = answer(_request(case), dataset["as_of"])
            problems = _check(result, case["expect"])
        except Exception as exc:  # noqa: BLE001 — one row, not a crash of the report
            errors += 1
            cases.append({"case_id": case["case_id"], "status": "error", "error": str(exc)})
            continue
        if problems:
            failed += 1
            cases.append({"case_id": case["case_id"], "status": "failed", "problems": problems})
        else:
            passed += 1
            cases.append({"case_id": case["case_id"], "status": "passed"})
    return {
        "evaluation_label": "DETERMINISTIC SMOKE TEST. Not a model evaluation.",
        "mode": "deterministic",
        "not_a_model_evaluation": True,
        "summary": {
            "total_cases": len(dataset["cases"]),
            "passed": passed,
            "failed": failed,
            "errors": errors,
        },
        "cases": cases,
        "paraphrase_recall": paraphrase_report(),
        "knowledge_score": knowledge_score(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the Experiment 84 smoke test.")
    parser.add_argument("--output", default=str(ROOT / "eval" / "smoke_report.json"))
    args = parser.parse_args(argv)
    report = run()
    Path(args.output).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    summary = report["summary"]
    print(f"Smoke test {summary['passed']}/{summary['total_cases']} passed")
    return 0 if summary["failed"] == 0 and summary["errors"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
