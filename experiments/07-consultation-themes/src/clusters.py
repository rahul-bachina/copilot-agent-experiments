"""Duplicate and campaign clustering.

Exact text, token Jaccard, and a repeated long sentence. Empty answers are
not clustered with each other: a blank is its own submission. Campaign copies
stay in the audit. Callers count a cluster once in the unique-voice proportion.
"""

from __future__ import annotations

import re

# Above this size the pairwise Jaccard scan is skipped. Exact hashes and
# repeated sentences still run. The output records the cap.
PAIRWISE_CAP = 800
JACCARD_THRESHOLD = 0.8
MIN_NEAR_TOKENS = 12
MIN_SENTENCE_TOKENS = 8
CAMPAIGN_MIN = 3
MIN_EXACT_CHARS = 40

_TOKEN_RE = re.compile(r"[a-z0-9']+")


def normalise(text: str) -> str:
    """Lower case, drop punctuation, collapse whitespace."""
    lowered = (text or "").lower().replace("’", "'")
    return " ".join(_TOKEN_RE.findall(lowered))


def tokens(text: str) -> list[str]:
    return _TOKEN_RE.findall(normalise(text))


def jaccard(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    union = left | right
    if not union:
        return 0.0
    return len(left & right) / len(union)


class _UnionFind:
    def __init__(self) -> None:
        self.parent: dict[str, str] = {}

    def add(self, item: str) -> None:
        self.parent.setdefault(item, item)

    def find(self, item: str) -> str:
        parent = self.parent[item]
        if parent != item:
            self.parent[item] = self.find(parent)
        return self.parent[item]

    def union(self, left: str, right: str) -> None:
        self.add(left)
        self.add(right)
        left_root = self.find(left)
        right_root = self.find(right)
        if left_root == right_root:
            return
        # Stable root: the smaller response id, so the representative does not
        # depend on input order.
        if left_root < right_root:
            self.parent[right_root] = left_root
        else:
            self.parent[left_root] = right_root


def _sentences(text: str) -> list[str]:
    parts = re.split(r"[.!?]+", text or "")
    return [normalise(part) for part in parts if normalise(part)]


def cluster_responses(rows: list[dict[str, str]]) -> dict[str, dict[str, object]]:
    """Cluster rows that have response_id and text.

    `text` should already be redacted. Returns one record per response id.
    """
    prepared: list[dict[str, object]] = []
    for row in rows:
        response_id = str(row["response_id"])
        text = str(row.get("text") or "")
        normalised = normalise(text)
        prepared.append(
            {
                "response_id": response_id,
                "raw": text,
                "normalised": normalised,
                "token_set": set(tokens(normalised)),
                "token_count": len(tokens(normalised)),
            }
        )

    union = _UnionFind()
    reasons: dict[str, set[str]] = {}
    for item in prepared:
        response_id = str(item["response_id"])
        union.add(response_id)
        reasons[response_id] = set()

    exact_groups: dict[str, list[str]] = {}
    for item in prepared:
        normalised = str(item["normalised"])
        if len(normalised) < MIN_EXACT_CHARS:
            continue
        exact_groups.setdefault(normalised, []).append(str(item["response_id"]))
    for group in exact_groups.values():
        if len(group) < 2:
            continue
        anchor = group[0]
        for other in group[1:]:
            union.union(anchor, other)
            reasons[anchor].add("exact")
            reasons[other].add("exact")

    pairwise_capped = len(prepared) > PAIRWISE_CAP
    if not pairwise_capped:
        for index, left in enumerate(prepared):
            if int(left["token_count"]) < MIN_NEAR_TOKENS:
                continue
            for right in prepared[index + 1 :]:
                if int(right["token_count"]) < MIN_NEAR_TOKENS:
                    continue
                score = jaccard(set(left["token_set"]), set(right["token_set"]))
                if score < JACCARD_THRESHOLD:
                    continue
                left_id = str(left["response_id"])
                right_id = str(right["response_id"])
                union.union(left_id, right_id)
                reasons[left_id].add("near_duplicate")
                reasons[right_id].add("near_duplicate")

    sentence_owners: dict[str, list[str]] = {}
    for item in prepared:
        response_id = str(item["response_id"])
        seen_in_row: set[str] = set()
        for sentence in _sentences(str(item["raw"])):
            if sentence in seen_in_row:
                continue
            if len(sentence.split()) < MIN_SENTENCE_TOKENS:
                continue
            seen_in_row.add(sentence)
            sentence_owners.setdefault(sentence, []).append(response_id)
    for owners in sentence_owners.values():
        unique_owners = list(dict.fromkeys(owners))
        if len(unique_owners) < CAMPAIGN_MIN:
            continue
        anchor = unique_owners[0]
        for other in unique_owners[1:]:
            union.union(anchor, other)
            reasons[anchor].add("repeated_sentence")
            reasons[other].add("repeated_sentence")

    members: dict[str, list[str]] = {}
    for item in prepared:
        response_id = str(item["response_id"])
        root = union.find(response_id)
        members.setdefault(root, []).append(response_id)

    result: dict[str, dict[str, object]] = {}
    for group in members.values():
        ordered = sorted(group)
        representative = ordered[0]
        size = len(ordered)
        group_reasons: set[str] = set()
        for response_id in ordered:
            group_reasons |= reasons[response_id]
        # A pair of identical messages is a duplicate. Three or more linked
        # messages are reported as a campaign. A single response is neither.
        campaign = size >= CAMPAIGN_MIN and bool(group_reasons)
        duplicate = size >= 2
        cluster_id = "C-" + representative
        for response_id in ordered:
            result[response_id] = {
                "cluster_id": cluster_id,
                "representative_id": representative,
                "is_representative": response_id == representative,
                "cluster_size": size,
                "duplicate": duplicate,
                "campaign_cluster": campaign,
                "cluster_reasons": sorted(group_reasons),
                "pairwise_capped": pairwise_capped,
            }
    return result
