"""Labelled spans for the grounding score.

A positive claim is a span of the line. A negative claim adds a fact, flips
a denial, or cites a weaker sentence. The scorer does not read this list.
"""

from __future__ import annotations


def labelled_claims() -> list[dict]:
    stay = "I want to stay in my own home."
    hall = "I observed that the hallway was clear."
    move = "I do not want to move."
    tidy = "The kitchen was tidy."
    agreed = "We agreed that the social worker will phone the duty team by 19 November 2026."
    follow = "Follow up on 19 November 2026."
    present = "Present: the social worker and the person."
    record = "I agree to this visit being recorded."
    daughter = "My daughter told me the boiler is broken."
    phone = "My phone number is 07700900123."
    rows = [
        {"claim": stay, "line": stay, "supported": True},
        {"claim": "stay in my own home", "line": stay, "supported": True},
        {"claim": "I want to stay", "line": stay, "supported": True},
        {"claim": hall, "line": hall, "supported": True},
        {"claim": "the hallway was clear", "line": hall, "supported": True},
        {"claim": move, "line": move, "supported": True},
        {"claim": "do not want to move", "line": move, "supported": True},
        {"claim": tidy, "line": tidy, "supported": True},
        {"claim": "The kitchen was tidy", "line": tidy, "supported": True},
        {"claim": agreed, "line": agreed, "supported": True},
        {"claim": "phone the duty team", "line": agreed, "supported": True},
        {"claim": "19 November 2026", "line": agreed, "supported": True},
        {"claim": follow, "line": follow, "supported": True},
        {"claim": present, "line": present, "supported": True},
        {"claim": record, "line": record, "supported": True},
        {"claim": "being recorded", "line": record, "supported": True},
        {"claim": daughter, "line": daughter, "supported": True},
        {"claim": "the boiler is broken", "line": daughter, "supported": True},
        {"claim": "My phone number is 07700900123", "line": phone, "supported": True},
        {"claim": "07700900123", "line": phone, "supported": True},
        {"claim": "I want to move.", "line": move, "supported": False},
        {"claim": "want to move", "line": move, "supported": False},
        {"claim": "she is coping well", "line": tidy, "supported": False},
        {"claim": "The adult is eligible for care.", "line": stay, "supported": False},
        {"claim": "high risk of neglect", "line": hall, "supported": False},
        {"claim": "The person has dementia.", "line": tidy, "supported": False},
        {"claim": "She said she feels completely safe.", "line": stay, "supported": False},
        {"claim": "phone the duty team by 1 January 1999", "line": agreed, "supported": False},
        {"claim": "The person lacks capacity.", "line": record, "supported": False},
        {"claim": "eligibility has been confirmed", "line": present, "supported": False},
        {"claim": "I want to leave home", "line": stay, "supported": False},
        {"claim": "the hallway was blocked", "line": hall, "supported": False},
        {"claim": "the boiler is new", "line": daughter, "supported": False},
        {"claim": "Follow up on 1 January 1999.", "line": follow, "supported": False},
        {"claim": "diagnosis of depression", "line": tidy, "supported": False},
        {"claim": "low risk", "line": hall, "supported": False},
        {"claim": "has capacity to decide", "line": record, "supported": False},
        {"claim": "the kitchen was unsafe", "line": tidy, "supported": False},
        {"claim": "I do not agree to this visit being recorded.", "line": record, "supported": False},
        {"claim": "Present: a doctor and a solicitor.", "line": present, "supported": False},
    ]
    return rows
