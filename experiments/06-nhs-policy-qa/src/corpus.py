"""Load the synthetic policy register and apply the approval rules.

The policy owner sets approved_by_policy_owner before a run. Nothing in this
module can change that flag. A clause whose text instructs the model is
quarantined at load and is not citable.
"""

from __future__ import annotations

import json
import re
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTER = ROOT / "fixtures" / "policies.json"

INJECTION_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"ignore (all |any |previous |prior )*instructions",
        r"disregard (the |all |any )?(rules|instructions|policies|previous)",
        r"you are now",
        r"mark .{0,80} as approved",
        r"approve (this|the) (policy|source|document)",
        r"set approved_by_policy_owner",
        r"answer clinical questions",
        r"system prompt",
        r"jailbreak",
    )
]


def parse_date(value: str) -> date:
    """Parse an ISO date. A datetime is rejected so midnight is never assumed."""
    if "T" in value:
        raise ValueError(f"Expected YYYY-MM-DD, got {value!r}")
    return datetime.strptime(value, "%Y-%m-%d").date()


def contains_injection(text: str) -> bool:
    return any(pattern.search(text) for pattern in INJECTION_PATTERNS)


def load_register(path: Path | str | None = None) -> dict:
    """Return the register with quarantine flags set. Does not write the file."""
    source = Path(path) if path else DEFAULT_REGISTER
    register = json.loads(source.read_text(encoding="utf-8"))
    if register.get("fictional") is not True:
        raise ValueError("The register must be marked fictional.")
    for policy in register["policies"]:
        for clause in policy["clauses"]:
            blob = f"{clause.get('heading', '')}\n{clause.get('text', '')}"
            if contains_injection(blob):
                clause["quarantined"] = True
                clause["quarantine_reason"] = "instruction_to_the_model"
            else:
                clause["quarantined"] = False
                clause["quarantine_reason"] = None
    return register


def staff_visible(policy: dict) -> bool:
    """Approved by the policy owner and not a draft, superseded, or withdrawn file."""
    return policy["status"] == "approved" and policy["approved_by_policy_owner"] is True


def review_due(policy: dict) -> date:
    return parse_date(policy["review_due"])


def is_in_date(policy: dict, as_of: date) -> bool:
    """In date on the review date itself. Stale from the following day."""
    return review_due(policy) >= as_of


def authoritative(policy: dict, as_of: date) -> bool:
    return staff_visible(policy) and is_in_date(policy, as_of)


def phrase_in(text: str, phrase: str) -> bool:
    pattern = r"(?<!\w)" + re.escape(phrase.lower()) + r"(?!\w)"
    return re.search(pattern, text.lower()) is not None


def iter_clauses(register: dict):
    for policy in register["policies"]:
        for clause in policy["clauses"]:
            yield policy, clause


def matching_clauses(question: str, register: dict) -> list[tuple[dict, dict]]:
    """Staff-visible, non-quarantined clauses whose phrases appear in the question.

    Stale policies are included so the caller can withhold them. Drafts,
    superseded policies, and documents the owner has not approved are not.
    """
    hits: list[tuple[dict, dict]] = []
    for policy, clause in iter_clauses(register):
        if not staff_visible(policy) or clause["quarantined"]:
            continue
        phrases = clause.get("match_phrases") or []
        if any(phrase_in(question, phrase) for phrase in phrases):
            hits.append((policy, clause))
    hits.sort(key=lambda pair: (pair[0]["policy_id"], pair[1]["clause_id"]))
    return hits


def claims_on(pairs: list[tuple[dict, dict]]) -> dict[str, dict[str, list[tuple[dict, dict, dict]]]]:
    """topic -> position -> list of (policy, clause, claim)."""
    grouped: dict[str, dict[str, list[tuple[dict, dict, dict]]]] = {}
    for policy, clause in pairs:
        for claim in clause.get("claims") or []:
            topic = claim["topic"]
            position = claim["position"]
            grouped.setdefault(topic, {}).setdefault(position, []).append((policy, clause, claim))
    return grouped


def conflicting_topics(grouped: dict[str, dict]) -> list[str]:
    return sorted(topic for topic, positions in grouped.items() if len(positions) > 1)


def in_date_clauses(register: dict, as_of: date) -> list[tuple[dict, dict]]:
    pairs = [
        (policy, clause)
        for policy, clause in iter_clauses(register)
        if authoritative(policy, as_of) and not clause["quarantined"]
    ]
    pairs.sort(key=lambda pair: (pair[0]["policy_id"], pair[1]["clause_id"]))
    return pairs


def cite(policy: dict, clause: dict, as_of: date, *, include_quote: bool) -> dict:
    return {
        "policy_id": policy["policy_id"],
        "title": policy["title"],
        "version": policy["version"],
        "clause_id": clause["clause_id"],
        "review_due": policy["review_due"],
        "stale": not is_in_date(policy, as_of),
        "status": policy["status"],
        "approved_by_policy_owner": policy["approved_by_policy_owner"],
        "quote": clause["text"] if include_quote else None,
    }
