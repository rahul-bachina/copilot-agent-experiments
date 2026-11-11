"""Fictional file plan for Merrowfield Borough Council.

Merrowfield Borough Council is invented. The periods and disposal actions are
configuration for this starter. They are not statutory retention periods, and
they are not a schedule published by The National Archives.
"""

from __future__ import annotations

SCHEME_ID = "merrowfield-bcs-synthetic-2026"
ORGANISATION = "Merrowfield Borough Council"

SCHEME_NOTE = (
    "Fictional business classification scheme. A configured period is not a "
    "statutory retention period. A configured disposal action is not authority "
    "to destroy, transfer, or move a record."
)

DISPOSAL_ACTIONS = (
    "review",
    "transfer_for_review_of_permanent_value",
    "review_then_destroy_not_executed",
    "do_not_dispose_legal_hold",
    "unspecified",
)

MARKINGS = ("OFFICIAL", "OFFICIAL-SENSITIVE", "SECRET", "TOP SECRET")

MARKING_RANK = {
    "OFFICIAL": 1,
    "OFFICIAL-SENSITIVE": 2,
    "SECRET": 3,
    "TOP SECRET": 4,
}

CATEGORIES = (
    {
        "id": "GOV-CMT",
        "title": "Corporate governance — committee papers",
        "phrases": ("cabinet minutes", "committee minutes", "council minutes"),
        "retention_entry": "GOV-CMT-R",
        "retention_label": (
            "Configured: review six years after the meeting date. Not a statutory period."
        ),
        "disposal": "transfer_for_review_of_permanent_value",
        "default_marking": "OFFICIAL",
        "sensitive": False,
    },
    {
        "id": "FIN-ACC",
        "title": "Finance — accounts and budget papers",
        "phrases": ("statement of accounts", "annual budget", "council tax setting"),
        "retention_entry": "FIN-ACC-R",
        "retention_label": (
            "Configured: review six years after the end of the financial year. "
            "Not a statutory period."
        ),
        "disposal": "review_then_destroy_not_executed",
        "default_marking": "OFFICIAL",
        "sensitive": False,
    },
    {
        "id": "IG-FOI",
        "title": "Information governance — information request case files",
        "phrases": (
            "freedom of information request",
            "foi case file",
            "environmental information request",
        ),
        "retention_entry": "IG-FOI-R",
        "retention_label": (
            "Configured: review three years after the case is closed. Not a statutory period."
        ),
        "disposal": "review",
        "default_marking": "OFFICIAL",
        "sensitive": False,
    },
    {
        "id": "CON-PROC",
        "title": "Contracts and procurement",
        "phrases": ("invitation to tender", "contract award"),
        "retention_entry": "CON-PROC-R",
        "retention_label": (
            "Configured: review six years after the contract ends. Not a statutory period."
        ),
        "disposal": "review",
        "default_marking": "OFFICIAL",
        "sensitive": False,
    },
    {
        "id": "HR-PER",
        "title": "Human resources — personnel files",
        "phrases": ("personnel file", "disciplinary hearing", "sickness absence"),
        "retention_entry": "HR-PER-R",
        "retention_label": (
            "Configured: review six years after employment ends. Not a statutory period."
        ),
        "disposal": "review",
        "default_marking": "OFFICIAL-SENSITIVE",
        "sensitive": True,
    },
    {
        "id": "HOU-TEN",
        "title": "Housing — tenancy files",
        "phrases": ("tenancy agreement", "rent account", "housing application"),
        "retention_entry": "HOU-TEN-R",
        "retention_label": (
            "Configured: review six years after the tenancy ends. Not a statutory period."
        ),
        "disposal": "review",
        "default_marking": "OFFICIAL-SENSITIVE",
        "sensitive": True,
    },
    {
        "id": "LEG-MAT",
        "title": "Legal — advice and litigation files",
        "phrases": ("legal advice", "litigation file", "counsel opinion"),
        "retention_entry": "LEG-MAT-R",
        "retention_label": (
            "Configured: review six years after the matter is closed. Not a statutory period."
        ),
        "disposal": "review",
        "default_marking": "OFFICIAL-SENSITIVE",
        "sensitive": True,
    },
    {
        "id": "ASC-SAF",
        "title": "Adult social care — safeguarding",
        "phrases": (
            "safeguarding enquiry",
            "safeguarding inquiry",
            "care plan",
            "social work assessment",
        ),
        "retention_entry": "ASC-SAF-R",
        "retention_label": (
            "Configured: review after the case is closed. The period is not stated "
            "as a number of years because this starter does not set a statutory period."
        ),
        "disposal": "review",
        "default_marking": "OFFICIAL-SENSITIVE",
        "sensitive": True,
    },
)

BY_ID = {row["id"]: row for row in CATEGORIES}
BY_RETENTION = {row["retention_entry"]: row for row in CATEGORIES}

LEGAL_HOLD_CUES = (
    "legal hold",
    "litigation hold",
    "do not destroy",
    "do not dispose",
    "public inquiry",
    "moratorium on destruction",
    "police investigation",
)

PERSONAL_CUES = (
    "date of birth",
    "personal data",
    "medical record",
    "national insurance",
)

HEALTH_CUES = (
    "medical record",
    "care plan",
    "sickness absence",
    "safeguarding enquiry",
    "safeguarding inquiry",
)

COMMERCIAL_CUE = "commercially sensitive"
