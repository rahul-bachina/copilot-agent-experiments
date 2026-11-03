"""One verdict per claim. Staleness is a flag, not a second verdict.

The checks, in the order that decides the verdict, are: a citation is present,
every cited source was in the passages shown, every quote is in that source,
every number in the claim is in the cited source, every date in the claim is
in the cited source, and every content token in the claim is in the cited
source. The first failure is the verdict. Later failures are listed on the
claim and are not added to the summary.
"""

from __future__ import annotations

import re
from datetime import date
import sys
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from tokens import content_tokens
else:
    from .tokens import content_tokens

VERDICT_ORDER = (
    "supported",
    "citation_missing",
    "source_not_shown",
    "quote_not_in_source",
    "number_mismatch",
    "date_mismatch",
    "unsupported",
)

_PRIORITY = (
    "citation_missing",
    "source_not_shown",
    "quote_not_in_source",
    "number_mismatch",
    "date_mismatch",
    "unsupported",
)

_MONTHS = (
    "January|February|March|April|May|June|July|August|September|October|November|December|"
    "Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec"
)
_DATE = re.compile(rf"\b(?:\d{{4}}-\d{{2}}-\d{{2}}|\d{{1,2}}\s+(?:{_MONTHS})\s+\d{{4}})\b", re.I)
_NUMBER = re.compile(r"\d+(?:\.\d+)?")
_SENTENCE = re.compile(r"(?<=[.!?])\s+")


def normalise(text: str) -> str:
    text = (
        text.replace("\u2019", "'")
        .replace("\u2018", "'")
        .replace("\u201c", '"')
        .replace("\u201d", '"')
    )
    return re.sub(r"\s+", " ", text).strip().casefold()


def extract_numbers(text: str) -> list[str]:
    return _NUMBER.findall(text or "")


def extract_dates(text: str) -> list[str]:
    return [match.group(0) for match in _DATE.finditer(text or "")]


def number_in(number: str, text: str) -> bool:
    return re.search(rf"(?<!\d){re.escape(number)}(?!\d)", text) is not None


def passage_currency(passage: dict[str, Any], as_of: str, stale_after_days: int) -> dict[str, Any]:
    reviewed = passage.get("reviewed_on")
    try:
        reviewed_on = date.fromisoformat(reviewed)
        as_of_date = date.fromisoformat(as_of)
    except (TypeError, ValueError):
        return {
            "source_id": passage.get("source_id"),
            "title": passage.get("title"),
            "reviewed_on": reviewed,
            "stale": True,
            "stale_reason": "review_date_missing_or_invalid",
            "age_days": None,
        }
    age = (as_of_date - reviewed_on).days
    if age > stale_after_days:
        stale, reason = True, "older_than_draft_threshold"
    elif age < 0:
        stale, reason = True, "review_date_after_as_of"
    else:
        stale, reason = False, "within_draft_threshold"
    return {
        "source_id": passage.get("source_id"),
        "title": passage.get("title"),
        "reviewed_on": reviewed,
        "stale": stale,
        "stale_reason": reason,
        "age_days": age,
    }


def claims_from_answers(answers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for answer in answers:
        answer_id = str(answer.get("answer_id") or "").strip()
        if not answer_id:
            raise ValueError("An answer has no answer_id.")
        question = str(answer.get("question") or "").strip()
        inherited = answer.get("citations") or []
        explicit = answer.get("claims")
        if explicit is not None:
            if not isinstance(explicit, list) or not explicit:
                raise ValueError(f"Answer {answer_id} has an empty claims list.")
            pieces = []
            for index, claim in enumerate(explicit, start=1):
                if not isinstance(claim, dict):
                    raise ValueError(f"Answer {answer_id} has a claim that is not an object.")
                text = str(claim.get("text") or "").strip()
                if not text:
                    raise ValueError(f"Answer {answer_id} has a claim with no text.")
                citations = claim.get("citations", inherited)
                pieces.append((claim.get("claim_id") or f"{answer_id}-c{index}", text, citations))
        else:
            text = str(answer.get("text") or "").strip()
            if not text:
                raise ValueError(f"Answer {answer_id} has no text.")
            parts = [part.strip() for part in _SENTENCE.split(text) if part.strip()]
            pieces = [(f"{answer_id}-c{index}", part, inherited) for index, part in enumerate(parts, start=1)]
        for claim_id, text, citations in pieces:
            claim_id = str(claim_id)
            if claim_id in seen:
                raise ValueError(f"Duplicate claim_id {claim_id}.")
            seen.add(claim_id)
            if not isinstance(citations, list):
                raise ValueError(f"Citations on {claim_id} must be a list.")
            rows.append(
                {
                    "answer_id": answer_id,
                    "claim_id": claim_id,
                    "question": question,
                    "text": text,
                    "citations": citations,
                }
            )
    if not rows:
        raise ValueError("The bundle has no claims.")
    return rows


def score_claim(
    claim: dict[str, Any],
    passages: dict[str, dict[str, Any]],
    passage_rows: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    citations_in = claim["citations"]
    prepared: list[dict[str, Any]] = []
    failures: list[str] = []
    if not citations_in:
        failures.append("citation_missing")
    else:
        shown_texts: list[str] = []
        missing_source = False
        quote_failed = False
        for citation in citations_in:
            if not isinstance(citation, dict):
                raise ValueError(f"Citation on {claim['claim_id']} must be an object.")
            source_id = str(citation.get("source_id") or "").strip()
            quote = str(citation.get("quote") or "")
            passage = passages.get(source_id)
            quote_found = bool(passage) and bool(quote.strip()) and normalise(quote) in normalise(passage["text"])
            prepared.append(
                {
                    "source_id": source_id,
                    "quote": quote.strip(),
                    "quote_found": quote_found,
                    "source_shown": passage is not None,
                }
            )
            if passage is None:
                missing_source = True
            elif not quote_found:
                quote_failed = True
            else:
                shown_texts.append(passage["text"])
        if missing_source:
            failures.append("source_not_shown")
        if quote_failed or (not missing_source and not shown_texts):
            failures.append("quote_not_in_source")
        if shown_texts and not quote_failed and not missing_source:
            union = "\n".join(shown_texts)
            numbers = extract_numbers(claim["text"])
            dates = extract_dates(claim["text"])
            if any(not number_in(number, union) for number in numbers):
                failures.append("number_mismatch")
            if any(normalise(item) not in normalise(union) for item in dates):
                failures.append("date_mismatch")
            source_words = set(content_tokens(union))
            extra = [word for word in content_tokens(claim["text"]) if word not in source_words]
            if extra:
                failures.append("unsupported")
    if not failures:
        verdict = "supported"
        other: list[str] = []
    else:
        verdict = next(name for name in _PRIORITY if name in failures)
        other = [name for name in _PRIORITY if name in failures and name != verdict]

    cited_ids = [item["source_id"] for item in prepared if item["source_shown"]]
    stale_reasons = []
    for source_id in cited_ids:
        row = passage_rows[source_id]
        if row["stale"]:
            stale_reasons.append(row["stale_reason"])
    stale = bool(stale_reasons)
    return {
        "answer_id": claim["answer_id"],
        "claim_id": claim["claim_id"],
        "question": claim["question"],
        "text": claim["text"],
        "citations": prepared,
        "verdict": verdict,
        "other_failures": other,
        "stale_source": stale,
        "stale_reason": stale_reasons[0] if stale_reasons else None,
        "cited_source_ids": cited_ids,
        "numbers": extract_numbers(claim["text"]),
        "dates": extract_dates(claim["text"]),
    }


def summarise(claims: list[dict[str, Any]]) -> dict[str, Any]:
    verdicts = {name: 0 for name in VERDICT_ORDER}
    for claim in claims:
        verdicts[claim["verdict"]] += 1
    claim_count = len(claims)
    verdict_total = sum(verdicts.values())
    if verdict_total != claim_count:
        raise RuntimeError("Verdict totals do not match the claim count.")
    answer_ids = {claim["answer_id"] for claim in claims}
    stale_claim_count = sum(1 for claim in claims if claim["stale_source"])
    supported = verdicts["supported"]
    return {
        "claim_count": claim_count,
        "answer_count": len(answer_ids),
        "verdicts": verdicts,
        "verdict_total": verdict_total,
        "stale_claim_count": stale_claim_count,
        "supported_count": supported,
        "non_supported_count": claim_count - supported,
        "supported_rate": None if claim_count == 0 else round(supported / claim_count, 4),
        "each_claim_has_one_verdict": True,
        "stale_claim_count_is_separate": True,
        "answer_count_is_not_added_to_claim_count": True,
        "other_failures_are_not_in_the_totals": True,
    }
