"""Score one claim summary. The checker is deterministic.

Faithfulness is Experiment 29 ``score_claim``. Completeness is a closed list
of labelled lines. Unsupported coverage is a closed list of decision phrases
that are not a quote from a file this run read.

The three results are not added together. A score under a draft threshold
sets a human-escalation flag. It does not decline the claim. Thresholds are
not approved. No model is called. This is not the LLM-as-a-judge in the FCA
case study, and it is not the Microsoft Foundry groundedness evaluator.
"""

from __future__ import annotations

import importlib
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from claims_injection import line_is_hostile
else:
    from .claims_injection import line_is_hostile

DECISION_PHRASES = (
    "the claim is covered",
    "this claim is covered",
    "is not covered",
    "not covered",
    "decline the claim",
    "decline this claim",
    "claim is declined",
    "claim is accepted",
    "accept the claim",
    "accept this claim",
    "settle the claim",
    "settle this claim",
    "indemnity is due",
    "the policy responds",
    "we will pay",
)

CONDUCT_WORDS = ("fraud", "suspicious", "dishonest")
_WORD = {word: re.compile(rf"\b{word}\b", re.IGNORECASE) for word in CONDUCT_WORDS}

DRAFT_COMPLETENESS = 1.0
DRAFT_MAX_UNSUPPORTED = 0

LABELLED = (
    "Date of loss",
    "Peril",
    "Stated amount",
    "Policy number",
    "Policyholder",
    "Invoice date",
    "Invoice total",
    "Invoice to",
    "Period from",
    "Period to",
    "Report date",
)
_LABELLED_LINE = re.compile(
    r"^(" + "|".join(LABELLED) + r"):[ \t]*(\S.*?)\s*$",
    re.MULTILINE,
)
_MAX_QUOTE = 400


class ScoreForbidden(RuntimeError):
    """The scorecard has no decline, release, or model path."""


def _import_from(src: Path, module_name: str):
    inserted = str(src)
    if not src.is_dir():
        raise ScoreForbidden(
            "Experiment 29 is not beside this experiment. The scorecard will not invent a checker."
        )
    if inserted in sys.path:
        sys.path.remove(inserted)
    sys.path.insert(0, inserted)
    existing = sys.modules.get(module_name)
    if existing is not None:
        existing_file = str(getattr(existing, "__file__", ""))
        if not existing_file.startswith(inserted):
            del sys.modules[module_name]
    return importlib.import_module(module_name)


def _load_groundedness():
    src = Path(__file__).resolve().parents[2] / "29-groundedness-evaluation" / "src"
    score = _import_from(src, "score")
    thresholds = _import_from(src, "thresholds")
    if not hasattr(score, "score_claim"):
        raise ScoreForbidden("the score module is not Experiment 29")
    return score, thresholds


def phrases_in(text: str) -> list[str]:
    lower = (text or "").lower()
    found = [phrase for phrase in DECISION_PHRASES if phrase in lower]
    for word, pattern in _WORD.items():
        if pattern.search(text or ""):
            found.append(word)
    return found


def labelled_lines(content: str) -> list[dict[str, str]]:
    rows = []
    for match in _LABELLED_LINE.finditer(content or ""):
        label = match.group(1)
        value = match.group(2).strip()
        line = f"{label}: {value}"
        if len(line) > _MAX_QUOTE:
            continue
        rows.append({"label": label, "value": value, "line": line})
    return rows


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip().casefold()


def _quoted_in_source(text: str, source: str) -> bool:
    norm = _normalise(text)
    return bool(norm) and norm in _normalise(source)


def unsupported_hits(sentences: list[dict[str, str]], sources: dict[str, str]) -> list[dict[str, Any]]:
    hits = []
    for sentence in sentences:
        text = sentence.get("text") or ""
        source_id = sentence.get("source_file_id") or ""
        source = sources.get(source_id, "")
        if _quoted_in_source(text, source):
            continue
        reasons = phrases_in(text)
        if reasons:
            hits.append(
                {
                    "text": text,
                    "phrases": reasons,
                    "quoted_from_source": False,
                    "is_a_coverage_decision": False,
                }
            )
    return hits


def _passages(files: list[dict[str, Any]], as_of: str, stale_after_days: int, score) -> tuple[dict, dict]:
    passages: dict[str, dict[str, Any]] = {}
    rows: dict[str, dict[str, Any]] = {}
    for file in files:
        if file.get("read_status") != "read":
            continue
        file_id = file["file_id"]
        reviewed = file.get("document_date") or ""
        passage = {
            "source_id": file_id,
            "title": file.get("filename") or file_id,
            "text": file.get("content") or "",
            "reviewed_on": reviewed,
        }
        passages[file_id] = passage
        rows[file_id] = score.passage_currency(passage, as_of, stale_after_days)
    return passages, rows


def _faithfulness(lines: list[dict[str, Any]], files: list[dict[str, Any]], as_of: str, window: int) -> dict:
    score, _thresholds = _load_groundedness()
    if not lines:
        return {
            "method": "experiment_29_score_claim",
            "experiment_id": "exp-29-groundedness-evaluation",
            "llm_as_judge": False,
            "foundry_evaluator_called": False,
            "claim_count": 0,
            "supported_count": 0,
            "supported_rate": None,
            "non_supported_count": 0,
            "stale_claim_count": 0,
            "stale_claim_count_is_separate": True,
            "claims": [],
            "verdict_total": 0,
        }
    passages, passage_rows = _passages(files, as_of, window, score)
    claims = []
    for line in lines:
        claims.append(
            score.score_claim(
                {
                    "answer_id": "summary",
                    "claim_id": line["line_id"],
                    "question": "handler summary",
                    "text": line["text"],
                    "citations": [
                        {"source_id": line["source_file_id"], "quote": line["quote"]},
                    ],
                },
                passages,
                passage_rows,
            )
        )
    summary = score.summarise(claims)
    return {
        "method": "experiment_29_score_claim",
        "experiment_id": "exp-29-groundedness-evaluation",
        "llm_as_judge": False,
        "foundry_evaluator_called": False,
        "claim_count": summary["claim_count"],
        "supported_count": summary["supported_count"],
        "supported_rate": summary["supported_rate"],
        "non_supported_count": summary["non_supported_count"],
        "stale_claim_count": summary["stale_claim_count"],
        "stale_claim_count_is_separate": True,
        "other_failures_are_not_in_the_totals": True,
        "verdict_total": summary["verdict_total"],
        "verdicts": summary["verdicts"],
        "claims": [
            {
                "claim_id": claim["claim_id"],
                "verdict": claim["verdict"],
                "other_failures": claim["other_failures"],
                "stale_source": claim["stale_source"],
            }
            for claim in claims
        ],
    }


def completeness(files: list[dict[str, Any]], lines: list[dict[str, Any]]) -> dict[str, Any]:
    """Required labelled lines, only where the file was read and not withheld."""

    quoted = {_normalise(line["text"]) for line in lines}
    items = []

    def add(item_id: str, applicable: bool, met: bool, detail: str) -> None:
        items.append(
            {
                "id": item_id,
                "applicable": applicable,
                "met": met if applicable else None,
                "detail": detail,
            }
        )

    read_files = [file for file in files if file.get("read_status") == "read"]
    fnols = [file for file in read_files if file.get("role") == "fnol" and not file.get("withheld")]
    add(
        "fnol_read",
        True,
        bool(fnols),
        "A first notification file was read and was not withheld.",
    )
    for file in fnols:
        for row in labelled_lines(file.get("content") or ""):
            if row["label"] not in {"Date of loss", "Peril"}:
                continue
            if line_is_hostile(row["line"]) or phrases_in(row["line"]):
                add(
                    f"{file['file_id']}:{row['label']}",
                    False,
                    False,
                    "The labelled line was not required because it carries a hostile or decision phrase.",
                )
                continue
            add(
                f"{file['file_id']}:{row['label']}",
                True,
                _normalise(row["line"]) in quoted,
                "The summary quotes the labelled line.",
            )
    invoices = [file for file in read_files if file.get("role") == "invoice"]
    for file in invoices:
        if file.get("withheld"):
            add(
                f"{file['file_id']}:invoice_total",
                False,
                False,
                "The invoice was withheld because Experiment 08 reported an identifier. The total is not required in the summary.",
            )
            continue
        totals = [row for row in labelled_lines(file.get("content") or "") if row["label"] == "Invoice total"]
        if not totals:
            continue
        row = totals[0]
        add(
            f"{file['file_id']}:invoice_total",
            True,
            _normalise(row["line"]) in quoted,
            "The summary quotes the invoice total line.",
        )
    policies = [file for file in read_files if file.get("role") == "policy_wording" and not file.get("withheld")]
    listed = {line["source_file_id"] for line in lines}
    for file in policies:
        add(
            f"{file['file_id']}:policy_quoted_or_listed",
            True,
            file["file_id"] in listed,
            "A line from the policy extract is in the summary.",
        )

    applicable = [item for item in items if item["applicable"]]
    met = sum(1 for item in applicable if item["met"])
    rate = None if not applicable else round(met / len(applicable), 4)
    return {
        "items": items,
        "applicable_count": len(applicable),
        "met_count": met,
        "rate": rate,
        "met_count_is_not_added_to_faithfulness": True,
    }


def resolve_thresholds(raw: dict | None) -> dict[str, Any]:
    """Draft numbers only. The evaluation owner has not approved them."""

    score, thresholds = _load_groundedness()
    del score
    supplied = dict(raw or {})
    completeness_rate = supplied.pop("min_completeness_rate", DRAFT_COMPLETENESS)
    max_unsupported = supplied.pop("max_unsupported_coverage", DRAFT_MAX_UNSUPPORTED)
    # Keys Experiment 29 does not know are not sent to it. Stale caps are not
    # a second faithfulness test.
    grounded, ignored = thresholds.resolve(
        {
            key: value
            for key, value in supplied.items()
            if key in {"min_supported_rate", "max_non_supported_claims", "max_stale_claims", "stale_after_days"}
        }
    )
    if isinstance(completeness_rate, bool) or not isinstance(completeness_rate, (int, float)):
        raise ValueError("min_completeness_rate must be a number from 0 to 1")
    if not 0 <= float(completeness_rate) <= 1:
        raise ValueError("min_completeness_rate must be a number from 0 to 1")
    if isinstance(max_unsupported, bool) or not isinstance(max_unsupported, int) or max_unsupported < 0:
        raise ValueError("max_unsupported_coverage must be a non-negative integer")
    return {
        "min_supported_rate": grounded["min_supported_rate"],
        "min_completeness_rate": float(completeness_rate),
        "max_unsupported_coverage": max_unsupported,
        "approved_by_evaluation_owner": False,
        "source": "caller" if raw else "draft_default",
        "ignored_keys": ignored,
        "experiment_29_stale_cap_is_not_applied": True,
        "faithfulness_method": "experiment_29_score_claim",
    }


def score_lines(
    *,
    files: list[dict[str, Any]],
    lines: list[dict[str, Any]],
    prose: list[dict[str, str]],
    as_of: str,
    stale_after_days: int,
    thresholds: dict | None = None,
) -> dict[str, Any]:
    """Return a scorecard. Escalation is a flag. The claim is not declined."""

    if not isinstance(as_of, str):
        raise TypeError("as_of must be an ISO date string")
    date.fromisoformat(as_of)
    resolved = resolve_thresholds(thresholds)
    faith = _faithfulness(lines, files, as_of, stale_after_days)
    complete = completeness(files, lines)
    sources = {
        file["file_id"]: file.get("content") or ""
        for file in files
        if file.get("read_status") == "read"
    }
    hits = unsupported_hits(prose, sources)
    criteria = []
    rate = faith["supported_rate"]
    if rate is None or rate < resolved["min_supported_rate"]:
        criteria.append("faithfulness")
    comp_rate = complete["rate"]
    if comp_rate is None or comp_rate < resolved["min_completeness_rate"]:
        criteria.append("completeness")
    if len(hits) > resolved["max_unsupported_coverage"]:
        criteria.append("unsupported_coverage")
    below = bool(criteria)
    return {
        "label": "DRAFT EVALUATION SCORECARD",
        "not_an_llm_judge": True,
        "not_a_foundry_score": True,
        "foundry_evaluator_called": False,
        "llm_as_judge": False,
        "faithfulness": faith,
        "completeness": complete,
        "unsupported_coverage": {
            "count": len(hits),
            "hits": hits,
            "count_is_not_added_to_claim_count": True,
        },
        "thresholds": resolved,
        "criteria_below_threshold": criteria,
        "below_threshold": below,
        "human_escalation_required": below,
        "escalation_reason": (
            None
            if not below
            else "A draft threshold was missed. A person reviews the summary. This flag does not decline the claim."
        ),
        "escalation_does_not_decline_the_claim": True,
        "scores_are_not_summed_across_criteria": True,
        "threshold_approved_by_evaluation_owner": False,
    }


def approve_thresholds() -> None:
    raise ScoreForbidden("Thresholds are not approved by this checker.")


def call_foundry_evaluator() -> None:
    raise ScoreForbidden("This checker does not call Microsoft Foundry.")


def decline_from_score() -> None:
    raise ScoreForbidden("A score does not decline a claim.")
