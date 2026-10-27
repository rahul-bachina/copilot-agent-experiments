"""Closed lists for document intake. Pinned 27 October 2026.

A keyword is not a classification decision. A purpose id is not a hand-off.
B004, B007, UK11, and UK09 are named so a later agent can recognise the
label. This module does not call them.
"""

from __future__ import annotations

from datetime import date

CATALOGUE_PINNED_ON = date(2026, 10, 27)
CATALOGUE_ID = "O001"
EXPERIMENT_ID = "exp-12-document-intake"
GATEWAY_EXPERIMENT_ID = "exp-08-uk-pii-redaction-gateway"
GATEWAY_CATALOGUE_ID = "O005"
GATEWAY_CALLER = "exp-12-document-intake"
DEFAULT_STALE_AFTER_DAYS = 90

CLASSES = (
    {
        "id": "proof_of_address",
        "label": "Proof of address",
        "keywords": ("proof of address", "council tax", "utility bill"),
    },
    {
        "id": "identity_document",
        "label": "Identity document",
        "keywords": ("passport", "driving licence", "driving license"),
    },
    {
        "id": "bank_statement",
        "label": "Bank or building society statement",
        "keywords": ("sort code", "statement of account", "account number"),
    },
    {
        "id": "invoice",
        "label": "Invoice or receipt",
        "keywords": ("tax invoice", "invoice number"),
    },
    {
        "id": "correspondence",
        "label": "Correspondence",
        "keywords": ("yours sincerely", "yours faithfully"),
    },
    {
        "id": "policy_schedule",
        "label": "Policy schedule",
        "keywords": ("policy schedule", "schedule of insurance"),
    },
    {
        "id": "request_letter",
        "label": "Request letter",
        "keywords": ("subject access request", "freedom of information"),
    },
    {
        "id": "bundle_index",
        "label": "Bundle index",
        "keywords": ("bundle index", "schedule of documents"),
    },
)

PURPOSES = {
    "kyc_evidence": {
        "label": "KYC or enhanced due diligence evidence",
        "downstream_catalogue_id": "B004",
        "downstream_note": (
            "Not called. This intake does not score a customer and does not "
            "decide that the evidence is sufficient."
        ),
        "required_labels": (
            {
                "id": "identity_marker",
                "need": "An identity keyword or an identity-document class on a file that was read.",
                "any_of_classes": ("identity_document",),
                "any_of_phrases": ("passport", "driving licence", "driving license"),
            },
            {
                "id": "address_marker",
                "need": "An address keyword or a proof-of-address class on a file that was read.",
                "any_of_classes": ("proof_of_address",),
                "any_of_phrases": ("proof of address", "council tax", "utility bill"),
            },
        ),
    },
    "claims_fnol": {
        "label": "Claims first notification of loss",
        "downstream_catalogue_id": "B007",
        "downstream_note": (
            "Not called. This intake does not decide coverage, quantum, or fraud."
        ),
        "required_labels": (
            {
                "id": "incident_date_marker",
                "need": "A closed-list phrase for the incident date. The date itself is not extracted.",
                "any_of_classes": (),
                "any_of_phrases": ("date of incident", "date of loss", "incident date"),
            },
            {
                "id": "policy_reference_marker",
                "need": "A closed-list phrase for a policy reference. The reference is not looked up.",
                "any_of_classes": (),
                "any_of_phrases": ("policy number", "policy reference"),
            },
        ),
    },
    "sar_bundle": {
        "label": "Subject access request material",
        "downstream_catalogue_id": "UK11",
        "downstream_note": (
            "Not called. This intake does not scope a search and does not disclose anything."
        ),
        "required_labels": (
            {
                "id": "request_date_marker",
                "need": "A closed-list phrase for the request date. The date is not extracted.",
                "any_of_classes": (),
                "any_of_phrases": ("date of request", "request received"),
            },
            {
                "id": "requester_marker",
                "need": "A closed-list phrase for the requester's role. The person is not identified.",
                "any_of_classes": (),
                "any_of_phrases": ("data subject", "requester"),
            },
        ),
    },
    "evidence_bundle": {
        "label": "Evidence or case bundle",
        "downstream_catalogue_id": "UK09",
        "downstream_note": (
            "Not called. This intake does not summarise the bundle and does not make a finding."
        ),
        "required_labels": (
            {
                "id": "bundle_index_marker",
                "need": "A bundle-index phrase or class on a file that was read.",
                "any_of_classes": ("bundle_index",),
                "any_of_phrases": ("bundle index", "schedule of documents"),
            },
        ),
    },
    "general_records": {
        "label": "General records filing",
        "downstream_catalogue_id": None,
        "downstream_note": "No specialist catalogue row. Filing is still a person's step.",
        "required_labels": (),
    },
}


def _marker_phrases() -> tuple[str, ...]:
    found: list[str] = []
    for item in CLASSES:
        for keyword in item["keywords"]:
            if keyword not in found:
                found.append(keyword)
    for purpose in PURPOSES.values():
        for requirement in purpose["required_labels"]:
            for phrase in requirement["any_of_phrases"]:
                if phrase not in found:
                    found.append(phrase)
    return tuple(found)


MARKER_PHRASES = _marker_phrases()


def suggest_class(text: str) -> dict:
    """Suggest a class from the closed keyword list.

    Two classes with the same number of hits produce ``unresolved``. No hits
    produce ``unclassified``. Neither value is a decision that the document
    is what the label says.
    """

    lower = text.lower()
    candidates = []
    for item in CLASSES:
        keywords = [keyword for keyword in item["keywords"] if keyword in lower]
        if keywords:
            candidates.append(
                {
                    "id": item["id"],
                    "label": item["label"],
                    "keywords_found": keywords,
                }
            )
    if not candidates:
        return {"suggested_class": "unclassified", "candidate_classes": []}
    best = max(len(candidate["keywords_found"]) for candidate in candidates)
    top = [candidate for candidate in candidates if len(candidate["keywords_found"]) == best]
    suggested = top[0]["id"] if len(top) == 1 else "unresolved"
    return {"suggested_class": suggested, "candidate_classes": candidates}


def markers_in(text: str) -> list[str]:
    """Return closed-list phrases that occur in ``text``, in list order."""

    lower = text.lower()
    return [phrase for phrase in MARKER_PHRASES if phrase in lower]


def build_checklist(purpose_id: str, files: list[dict]) -> dict:
    """Phrase presence for one purpose. ``sufficient`` is always false."""

    purpose = PURPOSES[purpose_id]
    items = []
    for requirement in purpose["required_labels"]:
        met = False
        for file in files:
            if file["read_status"] != "read":
                continue
            classes = {file["suggested_class"]}
            classes.update(candidate["id"] for candidate in file["candidate_classes"])
            phrase_hit = any(phrase in file["markers_found"] for phrase in requirement["any_of_phrases"])
            if classes.intersection(requirement["any_of_classes"]) or phrase_hit:
                met = True
                break
        items.append(
            {
                "id": requirement["id"],
                "need": requirement["need"],
                "met": met,
                "sufficient": False,
            }
        )
    return {
        "purpose_id": purpose_id,
        "downstream_catalogue_id": purpose["downstream_catalogue_id"],
        "downstream_note": purpose["downstream_note"],
        "preview_only": True,
        "items": items,
        "complete": all(item["met"] for item in items),
        "sufficient": False,
    }
