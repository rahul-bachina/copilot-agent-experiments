"""Pinned synthetic sources. A caller-supplied copy is not authoritative.

Companies Act 2006 section 386 and the Accounts and Audit Regulations 2015
regulation 3 were opened on legislation.gov.uk on 26 November 2026. The
quotes are the text those pages showed. They are context. They are not a
finding that either duty was met.

The words "segregation of duties" were not on either page. That phrase, as
a statutory quotation, is unverified.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures"

CATALOGUE_ID = "O007"
EXPERIMENT_ID = "exp-81-approval-pack-coordinator"
AUTONOMY = "A1"
LABEL = "DRAFT APPROVAL PACK FOR THE NAMED APPROVER"
SOURCES_PINNED_ON = "2026-11-26"
STALE_AFTER_DAYS = 365
SMALL_NUMBER_THRESHOLD = 5
MAX_EVIDENCE = 12

OPENED_ON = "2026-11-26"

COMPANIES_ACT_386_1 = "Every company must keep adequate accounting records."

COMPANIES_ACT_386_2 = (
    "Adequate accounting records means records that are sufficient— "
    "(a) to show and explain the company's transactions, "
    "(b) to disclose with reasonable accuracy, at any time, the financial position of the company at that time, and "
    "(c) to enable the directors to ensure that any accounts required to be prepared comply with the requirements of this Act F1...."
)

ACCOUNTS_AUDIT_REG_3 = (
    "A relevant authority must ensure that it has a sound system of internal control which— "
    "(a) facilitates the effective exercise of its functions and the achievement of its aims and objectives; "
    "(b) ensures that the financial and operational management of the authority is effective; and "
    "(c) includes effective arrangements for the management of risk."
)

REQUEST_TYPES = ("spend", "policy_exception", "change")
DECISIONS = ("approve", "reject", "return")
PROHIBITED_DECISIONS = ("submit", "sign", "send", "pay", "approve-and-send", "reject-and-send")

PROHIBITED_REQUEST_KEYS = frozenset(
    {
        "approved",
        "rejected",
        "human_approval",
        "content_hash",
        "sent",
        "submitted",
        "signed",
        "paid",
        "agent_approved",
        "agent_rejected",
        "route_seen",
        "clearance",
        "guest",
        "role",
        "delegation_limit_gbp",
        "approver_role",
    }
)


def load_json(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def pinned_sources() -> dict:
    """Read the files in fixtures/. Do not accept a replacement object."""

    return {
        "matrix": load_json("approval_matrix.json"),
        "checklist": load_json("evidence_checklist.json"),
        "directory": load_json("directory.json"),
        "pinned_on": SOURCES_PINNED_ON,
    }


def uk_context() -> dict:
    return {
        "opened_on": OPENED_ON,
        "companies_act_2006": {
            "section": "386(1) and 386(2)",
            "url": "https://www.legislation.gov.uk/ukpga/2006/46/section/386",
            "subsection_1": COMPANIES_ACT_386_1,
            "subsection_2": COMPANIES_ACT_386_2,
            "page_currency_statement": (
                "The page said section 386 is up to date with all changes known to be in force "
                "on or before 25 November 2026. Subsection (2)(c) on the page ended with an F1 "
                "omission marker. The omitted words are not quoted."
            ),
        },
        "accounts_and_audit_regulations_2015": {
            "instrument": "S.I. 2015/234",
            "regulation": "3",
            "heading": "Responsibility for internal control",
            "url": "https://www.legislation.gov.uk/uksi/2015/234/regulation/3",
            "text": ACCOUNTS_AUDIT_REG_3,
            "extent_on_the_page": "E+W",
        },
        "segregation_of_duties_phrase_on_opened_pages": False,
        "segregation_of_duties_phrase": "unverified",
        "not_a_finding_that_a_duty_was_met": True,
        "matrix_thresholds_are_statutory": False,
    }


def limitations() -> list[str]:
    return [
        "The agent does not approve, reject, sign, submit, pay, or send.",
        "The pinned matrix, checklist, and directory are synthetic. A caller-supplied copy is not used.",
        "The spend bands are the pinned matrix. They are not a statutory minimum. No statutory spend threshold was on the pages opened on 26 November 2026.",
        "Section 386 and regulation 3 are quoted as context. This starter does not decide that either duty was met.",
        "The words segregation of duties were not on those pages. That phrase is unverified as a statutory quotation.",
        "The held copy lives in this process. A restart drops it. Nothing is written to a finance system.",
        "Experiment 18 supplies an evidence sha256. It does not decide the approval. Experiment 74's digest is the pack hash. paper_hash is not called.",
        "A distress sentence that uses none of the cue stems is not flagged.",
        "The small-number threshold of 5 is a starter rule. It is not a claim that the pack was anonymised.",
        "No model was called.",
    ]
