"""Shared synthetic pack for the HR checklist tests."""

from __future__ import annotations

import copy


def base_pack() -> dict:
    return {
        "synthetic": True,
        "reference": "SYN-PACK-001",
        "employer": {
            "name": "Northwharf Community Kitchen CIC",
            "jurisdiction": "england",
            "sector": "charity",
            "worker_count": 18,
        },
        "evidence": {
            "policies_reviewed": "not_evidenced",
            "standalone_sexual_harassment_policy_considered": "not_supplied",
            "reporting_routes_other_than_line_manager": "not_evidenced",
            "sexual_harassment_training_recorded": "evidenced",
            "prevention_steps_recorded": "not_evidenced",
            "third_party_risk_recorded": "not_supplied",
            "whistleblowing_policy_mentions_sexual_harassment": "not_supplied",
            "probation_wording_reviewed_for_six_month_period": "not_supplied",
            "risk_assessment_recorded": "not_evidenced",
            "policy_review_date": "2025-11-01",
        },
        "policy_excerpts": [
            {
                "id": "P1",
                "topic": "reporting",
                "title": "How to report a concern",
                "text": (
                    "Tell a manager or a fair-treatment contact. "
                    "You can also use the confidential form on the staff intranet. "
                    "This excerpt is synthetic."
                ),
                "approved_by_policy_owner": True,
                "review_date": "2025-11-01",
            }
        ],
        "question": {
            "text": "How do I report a concern?",
            "topic": "reporting",
        },
        "incident": {
            "reference": "SYN-INC-014",
            "anonymised": True,
            "narrative": (
                "Worker A reported that a visitor commented on their appearance "
                "during a shift. Worker A asked how to report it. No real person is named."
            ),
        },
    }


def pack_with(**changes) -> dict:
    pack = copy.deepcopy(base_pack())
    for key, value in changes.items():
        if value is None and key in pack:
            del pack[key]
        else:
            pack[key] = value
    return pack
