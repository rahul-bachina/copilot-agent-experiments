"""Policy-owner view of the register: coverage, stale policies, conflicts, change notes.

Every change note is a draft. accepted_by_policy_owner and published stay false.
"""

from __future__ import annotations

import argparse
import json
import sys

from corpus import (
    authoritative,
    cite,
    claims_on,
    conflicting_topics,
    in_date_clauses,
    is_in_date,
    iter_clauses,
    load_register,
    parse_date,
    staff_visible,
)

# Topics a corporate-services library is expected to cover. Missing means no
# document lists the topic. A draft does not count as cover.
EXPECTED_TOPICS = (
    "hr.annual_leave",
    "hr.sickness_absence",
    "hr.flexible_working",
    "finance.expenses.receipts",
    "finance.expenses.alcohol",
    "finance.purchase_cards",
    "procurement.purchase_orders",
    "procurement.conflicts_of_interest",
    "it.acceptable_use",
    "it.passwords",
    "estates.room_booking",
    "estates.lone_working",
    "estates.parking",
    "hr.cycle_to_work",
)


def _policies_for(register: dict, topic: str) -> list[dict]:
    found = [policy for policy in register["policies"] if topic in (policy.get("topics") or [])]
    found.sort(key=lambda policy: policy["policy_id"])
    return found


def _conflict_on_topic(register: dict, as_of, topic: str) -> bool:
    pairs = []
    for policy, clause in in_date_clauses(register, as_of):
        if topic not in (policy.get("topics") or []):
            continue
        for claim in clause.get("claims") or []:
            if claim["topic"] == topic:
                pairs.append((policy, clause))
                break
    return bool(conflicting_topics(claims_on(pairs)))


def coverage(register: dict, as_of) -> list[dict]:
    rows = []
    for topic in EXPECTED_TOPICS:
        related = _policies_for(register, topic)
        current = [policy for policy in related if authoritative(policy, as_of)]
        stale = [
            policy
            for policy in related
            if staff_visible(policy) and not is_in_date(policy, as_of)
        ]
        not_authoritative = [policy for policy in related if not staff_visible(policy)]
        if current and _conflict_on_topic(register, as_of, topic):
            status = "conflict"
        elif current:
            status = "covered_in_date"
        elif stale:
            status = "stale_only"
        elif not_authoritative:
            status = "draft_or_unapproved_only"
        else:
            status = "missing"
        rows.append(
            {
                "topic": topic,
                "status": status,
                "policy_ids": [policy["policy_id"] for policy in current],
                "also_stale": [policy["policy_id"] for policy in stale],
                "also_unapproved": [policy["policy_id"] for policy in not_authoritative],
            }
        )
    return rows


def stale_policies(register: dict, as_of) -> list[dict]:
    rows = []
    for policy in register["policies"]:
        if staff_visible(policy) and not is_in_date(policy, as_of):
            rows.append(
                {
                    "policy_id": policy["policy_id"],
                    "title": policy["title"],
                    "version": policy["version"],
                    "review_due": policy["review_due"],
                }
            )
    rows.sort(key=lambda row: row["policy_id"])
    return rows


def quarantined_clauses(register: dict) -> list[dict]:
    rows = []
    for policy, clause in iter_clauses(register):
        if clause["quarantined"]:
            rows.append(
                {
                    "policy_id": policy["policy_id"],
                    "clause_id": clause["clause_id"],
                    "reason": clause["quarantine_reason"],
                }
            )
    rows.sort(key=lambda row: (row["policy_id"], row["clause_id"]))
    return rows


def register_conflicts(register: dict, as_of) -> list[dict]:
    """Disagreements among in-date approved clauses, across the whole register."""
    grouped = claims_on(in_date_clauses(register, as_of))
    conflicts = []
    for topic in conflicting_topics(grouped):
        sources = []
        for position in sorted(grouped[topic]):
            for policy, clause, _claim in grouped[topic][position]:
                cited = cite(policy, clause, as_of, include_quote=True)
                cited["position"] = position
                sources.append(cited)
        sources.sort(key=lambda row: (row["policy_id"], row["clause_id"], row["position"]))
        conflicts.append({"topic": topic, "sources": sources})
    return conflicts


def _note_text(topic: str, sources: list[dict]) -> str:
    parts = [
        "Draft change note for the policy owner. Not published and not applied.",
        f"Topic {topic}.",
    ]
    for source in sources:
        parts.append(
            f"{source['policy_id']} version {source['version']} clause {source['clause_id']} "
            f"(review due {source['review_due']}) position {source['position']}."
        )
    parts.append(
        "The policy owner decides which rule stands. This note does not amend either policy."
    )
    return " ".join(parts)


def build_change_notes(register: dict, as_of, topics: set[str] | None = None) -> list[dict]:
    notes = []
    for conflict in register_conflicts(register, as_of):
        if topics is not None and conflict["topic"] not in topics:
            continue
        topic = conflict["topic"]
        notes.append(
            {
                "change_note_id": f"CN-{topic}",
                "topic": topic,
                "status": "draft",
                "accepted_by_policy_owner": False,
                "published": False,
                "may_be_applied": False,
                "sources": conflict["sources"],
                "text": _note_text(topic, conflict["sources"]),
            }
        )
    return notes


def review_register(register: dict, as_of) -> dict:
    notes = build_change_notes(register, as_of)
    return {
        "corpus_id": register["corpus_id"],
        "organisation": register["organisation"],
        "fictional": True,
        "as_of": as_of.isoformat(),
        "processing_mode": "deterministic",
        "model_called": False,
        "actions_taken": [],
        "published": False,
        "accepted_by_policy_owner": False,
        "coverage": coverage(register, as_of),
        "stale_policies": stale_policies(register, as_of),
        "conflicts": register_conflicts(register, as_of),
        "change_notes": notes,
        "quarantined_clauses": quarantined_clauses(register),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Review the corporate policy register.")
    parser.add_argument("--as-of", required=True, help="YYYY-MM-DD")
    parser.add_argument("--register", default=None)
    args = parser.parse_args(argv)
    report = review_register(load_register(args.register), parse_date(args.as_of))
    json.dump(report, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
