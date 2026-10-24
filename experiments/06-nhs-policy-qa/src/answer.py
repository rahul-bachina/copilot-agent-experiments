"""Answer one corporate-policy question from the approved register.

The answer is a quotation, a refusal, or "I don't know". It is not a paraphrase
and it is not a decision about a person.
"""

from __future__ import annotations

import argparse
import json
import re
import sys

from corpus import (
    cite,
    claims_on,
    conflicting_topics,
    contains_injection,
    in_date_clauses,
    is_in_date,
    load_register,
    matching_clauses,
    parse_date,
)
from review import build_change_notes

SIGNPOST = (
    "This assistant answers corporate services policies only: HR, finance, "
    "procurement, IT, and estates. It does not give clinical advice, interpret "
    "clinical guidance, or answer questions about patient care. Ask the "
    "organisation's clinical guidance owner, the on-call clinician for the "
    "service, or the clinical librarian. This is not a medical device and it "
    "is not a substitute for clinical judgement."
)

CLINICAL_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\bpatients?\b",
        r"\bdiagnos\w*",
        r"\bprescrib\w*",
        r"\bantibiotic\w*",
        r"\bsepsis\b",
        r"\bward round\b",
        r"\bnice guideline\b",
        r"\bclinical guideline\b",
        r"\bdischarge summary\b",
        r"\bsymptoms?\b",
        r"\btreatment plan\b",
        r"\bmedication\b",
        r"\bdosage\b",
        r"\bdose\b",
        r"\btablet\b",
        r"\bclinical advice\b",
        r"\bhow should i treat\b",
        r"\bwhat treatment\b",
    )
]

DECISION_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"how many days (do i|have i)",
        r"\bmy (remaining |annual leave )?balance\b",
        r"\bam i entitled\b",
        r"\bapprove (this|my) (order|purchase|claim|expense)\b",
        r"\bshould we award\b",
        r"\baward the contract\b",
        r"\bdismiss\b",
        r"\bwhat is my pay\b",
        r"\bcalculate my\b",
        r"\bmy remaining\b",
    )
]

POLICY_QUOTE = re.compile(
    r"what does the policy say|according to the policy|in the policy",
    re.IGNORECASE,
)

DECISIONS_NOT_TAKEN = [
    "clinical_advice",
    "individual_entitlement",
    "procurement_award_or_spend",
    "policy_approval_or_publication",
    "external_send",
    "production_record_change",
]


def is_clinical(question: str) -> bool:
    return any(pattern.search(question) for pattern in CLINICAL_PATTERNS)


def is_personal_decision(question: str) -> bool:
    if POLICY_QUOTE.search(question):
        return False
    return any(pattern.search(question) for pattern in DECISION_PATTERNS)


def _base(question: str, register: dict, as_of) -> dict:
    return {
        "question": question,
        "as_of": as_of.isoformat(),
        "corpus_id": register["corpus_id"],
        "organisation": register["organisation"],
        "fictional": True,
        "processing_mode": "deterministic",
        "model_called": False,
        "actions_taken": [],
        "may_send": False,
        "may_publish": False,
        "may_approve_source": False,
        "clinical_advice_given": False,
        "approved_flags_changed": False,
        "decisions_not_taken": list(DECISIONS_NOT_TAKEN),
        "signpost": None,
        "change_note": None,
        "unanswered_log_entry": None,
        "also_matched_stale": [],
    }


def _log(question: str, outcome: str, as_of) -> dict:
    return {
        "persisted": False,
        "question": question,
        "outcome": outcome,
        "as_of": as_of.isoformat(),
    }


def _finish(result: dict, *, outcome: str, answer: str, citations: list, may_be_relied_on: bool) -> dict:
    result["outcome"] = outcome
    result["answer"] = answer
    result["citations"] = citations
    result["may_be_relied_on"] = may_be_relied_on
    return result


def _topics_touched(pairs: list[tuple[dict, dict]]) -> set[str]:
    topics: set[str] = set()
    for _policy, clause in pairs:
        for claim in clause.get("claims") or []:
            topics.add(claim["topic"])
    return topics


def _conflict_pairs(register: dict, as_of, topics: set[str]) -> list[tuple[dict, dict]]:
    """Every in-date clause that carries one of these claim topics."""
    if not topics:
        return []
    selected = []
    for policy, clause in in_date_clauses(register, as_of):
        if any(claim["topic"] in topics for claim in clause.get("claims") or []):
            selected.append((policy, clause))
    return selected


def answer_question(question: str, register: dict, as_of) -> dict:
    result = _base(question, register, as_of)
    result["injection_detected"] = contains_injection(question)

    if is_clinical(question):
        result["signpost"] = SIGNPOST
        return _finish(
            result,
            outcome="refused_clinical",
            answer=SIGNPOST,
            citations=[],
            may_be_relied_on=False,
        )

    if result["injection_detected"]:
        return _finish(
            result,
            outcome="refused_injection",
            answer=(
                "This question asks to override the register. It has been refused. "
                "No approval flag, review date, or policy text was changed."
            ),
            citations=[],
            may_be_relied_on=False,
        )

    if is_personal_decision(question):
        return _finish(
            result,
            outcome="refused_decision",
            answer=(
                "This assistant quotes published policy. It does not decide a person's "
                "entitlement, pay, or request, and it does not approve spend or an award. "
                "Ask the relevant manager or policy owner."
            ),
            citations=[],
            may_be_relied_on=False,
        )

    hits = matching_clauses(question, register)
    current = [(policy, clause) for policy, clause in hits if is_in_date(policy, as_of)]
    stale = [(policy, clause) for policy, clause in hits if not is_in_date(policy, as_of)]
    result["also_matched_stale"] = sorted({policy["policy_id"] for policy, _clause in stale})

    if not hits:
        return _finish(
            result,
            outcome="i_dont_know",
            answer=(
                "I don't know. No approved, in-date clause in the corporate policy "
                "register matches this question. The question is logged for the policy "
                "owner. Nothing is guessed."
            ),
            citations=[],
            may_be_relied_on=False,
        ) | {"unanswered_log_entry": _log(question, "i_dont_know", as_of)}

    touched = _topics_touched(current)
    wider = _conflict_pairs(register, as_of, touched)
    conflict_topics = conflicting_topics(claims_on(wider))
    if conflict_topics:
        notes = build_change_notes(register, as_of, set(conflict_topics))
        citations = []
        for note in notes:
            citations.extend(note["sources"])
        result["change_note"] = notes
        return _finish(
            result,
            outcome="conflict",
            answer=(
                "I don't know which rule applies. Approved policies disagree, and this "
                "assistant will not choose between them. A draft change note has been "
                "prepared for the policy owner. It has not been published."
            ),
            citations=citations,
            may_be_relied_on=False,
        )

    if not current:
        citations = [
            cite(policy, clause, as_of, include_quote=False) for policy, clause in stale
        ]
        listed = "; ".join(
            f"{item['policy_id']} version {item['version']}, review due {item['review_due']}"
            for item in citations
        )
        result["unanswered_log_entry"] = _log(question, "stale_withheld", as_of)
        return _finish(
            result,
            outcome="stale_withheld",
            answer=(
                "I don't know. The only matching approved policy is past its review date "
                f"({listed}). It cannot be used until a policy owner reviews it. "
                "The clause text is not given as an answer."
            ),
            citations=citations,
            may_be_relied_on=False,
        )

    citations = [cite(policy, clause, as_of, include_quote=True) for policy, clause in current]
    lines = [
        (
            f"From {item['title']} version {item['version']}, clause {item['clause_id']} "
            f"(review due {item['review_due']}): {item['quote']}"
        )
        for item in citations
    ]
    lines.append(
        "This quotes an approved policy. It is a quotation, not a decision about any "
        "person, and it does not change the policy."
    )
    return _finish(
        result,
        outcome="answered",
        answer="\n".join(lines),
        citations=citations,
        may_be_relied_on=True,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Answer one question from the policy register.")
    parser.add_argument("--question", required=True)
    parser.add_argument("--as-of", required=True, help="YYYY-MM-DD")
    parser.add_argument("--register", default=None)
    args = parser.parse_args(argv)
    result = answer_question(args.question, load_register(args.register), parse_date(args.as_of))
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
