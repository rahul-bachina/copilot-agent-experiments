"""Shared synthetic packs. Northmere Digital Services is fictional."""

from __future__ import annotations

import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

AS_OF = "2026-11-12"


def pack(**overrides) -> dict:
    base = {
        "synthetic": True,
        "proposal_id": "SYN-BID-5201",
        "requirements": [
            {
                "id": "R1",
                "text": "Describe the staffed service desk on working days.",
            }
        ],
    }
    for key, value in overrides.items():
        base[key] = value
    return copy.deepcopy(base)


def requirement(requirement_id: str, text: str) -> dict:
    return {"id": requirement_id, "text": text}


def acceptance(**overrides) -> dict:
    base = {
        "decision": "author_accept_complete_draft",
        "actor_role": "author",
        "actor_id": "SYN-AUTH-052",
        "proposal_id": "SYN-BID-5201",
        "complete_draft_seen": True,
        "rows_acknowledged": ["R1"],
        "author_checks_seen": True,
        "gaps_seen": True,
    }
    base.update(overrides)
    return base
