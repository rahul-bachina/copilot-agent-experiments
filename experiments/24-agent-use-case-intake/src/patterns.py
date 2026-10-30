"""Which experiment already in this repository a proposal resembles.

A recorded hint is repeated. Otherwise one keyword hit is reported. Two
hits are listed and not ranked. This is not a similarity score.
"""

from __future__ import annotations

import re

PATTERNS: tuple[dict, ...] = (
    {
        "id": "foi",
        "catalogue_id": "UK00",
        "experiment": "01-foi-complaint-triage",
        "name": "FOI and complaint triage",
        "keywords": ("freedom of information", "foi request", "environmental information regulations"),
    },
    {
        "id": "consumer_duty",
        "catalogue_id": "C006",
        "experiment": "02-consumer-duty-complaint-intake",
        "name": "Consumer Duty complaint intake",
        "keywords": ("consumer duty", "disp complaint", "final response letter"),
    },
    {
        "id": "assurance_pack",
        "catalogue_id": "G010",
        "experiment": "03-agent-inventory-atrs-assurance",
        "name": "Agent inventory and ATRS assurance pack",
        "keywords": ("atrs record", "algorithmic transparency recording", "assurance pack"),
    },
    {
        "id": "crypto_authorisation",
        "catalogue_id": "UK02",
        "experiment": "04-fca-cryptoasset-readiness",
        "name": "FCA cryptoasset authorisation readiness",
        "keywords": ("cryptoasset authorisation", "fca crypto", "registration does not convert"),
    },
    {
        "id": "housing_hazard",
        "catalogue_id": "UK01",
        "experiment": "05-awaabs-law-hazard-triage",
        "name": "Awaab's Law hazard triage",
        "keywords": ("awaab", "damp and mould", "statutory hazard clock"),
    },
    {
        "id": "policy_qa",
        "catalogue_id": "M003",
        "experiment": "06-nhs-policy-qa",
        "name": "Policy questions for NHS corporate services",
        "keywords": ("corporate policy question", "policy q&a", "nhs corporate policy"),
    },
    {
        "id": "consultation",
        "catalogue_id": "V010",
        "experiment": "07-consultation-themes",
        "name": "Consultation themes",
        "keywords": ("consultation response", "essay to data", "consultation theme"),
    },
    {
        "id": "pii_gateway",
        "catalogue_id": "O005",
        "experiment": "08-uk-pii-redaction-gateway",
        "name": "UK identifier PII gateway",
        "keywords": ("national insurance number", "redact an identifier", "uk identifier"),
    },
    {
        "id": "correspondence",
        "catalogue_id": "O008",
        "experiment": "09-casework-correspondence-draft",
        "name": "Correspondence draft",
        "keywords": ("ministerial correspondence", "mp enquiry", "lines to take"),
    },
    {
        "id": "travel_rule",
        "catalogue_id": "UK05",
        "experiment": "10-travel-rule-exception-triage",
        "name": "Travel Rule exception triage",
        "keywords": ("travel rule", "sunrise jurisdiction", "originator information"),
    },
    {
        "id": "employment_rights",
        "catalogue_id": "UK03",
        "experiment": "11-era-2025-hr-assistant",
        "name": "Employment Rights Act 2025 HR assistant",
        "keywords": ("employment rights act", "sexual harassment duty", "all reasonable steps"),
    },
    {
        "id": "document_intake",
        "catalogue_id": "O001",
        "experiment": "12-document-intake",
        "name": "Document intake",
        "keywords": ("document intake", "file batch", "permitted purpose"),
    },
    {
        "id": "contact_centre",
        "catalogue_id": "V006",
        "experiment": "13-council-contact-front-door",
        "name": "Council contact-centre front door",
        "keywords": ("contact centre", "resident enquiry", "warm handover"),
    },
    {
        "id": "architecture",
        "catalogue_id": "G002",
        "experiment": "14-agent-architecture-advisor",
        "name": "Agent Architecture Advisor",
        "keywords": ("which platform", "architecture option", "no agent"),
    },
    {
        "id": "vulnerability",
        "catalogue_id": "UK06",
        "experiment": "15-vulnerability-urgency-scanner",
        "name": "Vulnerability and urgency scanner",
        "keywords": ("vulnerability flag", "whitemail", "self-harm indicator"),
    },
    {
        "id": "kyc",
        "catalogue_id": "B004",
        "experiment": "16-kyc-evidence-intake",
        "name": "KYC evidence intake",
        "keywords": ("know your customer", "enhanced due diligence", "customer due diligence file"),
    },
    {
        "id": "invoice",
        "catalogue_id": "F004",
        "experiment": "17-invoice-exception-triage",
        "name": "Invoice exception triage",
        "keywords": ("invoice exception", "three-way match", "3-way match"),
    },
    {
        "id": "evidence_pack",
        "catalogue_id": "L004",
        "experiment": "18-evidence-pack-builder",
        "name": "Evidence pack builder",
        "keywords": ("evidence pack", "disclosure schedule", "exemption schedule"),
    },
    {
        "id": "dpia",
        "catalogue_id": "L006",
        "experiment": "19-privacy-impact-assessment",
        "name": "Privacy impact assessment assistant",
        "keywords": ("data protection impact", "dpia"),
    },
    {
        "id": "complaints_mi",
        "catalogue_id": "UK04",
        "experiment": "20-complaints-root-cause-mi",
        "name": "Complaints root-cause and regulatory MI",
        "keywords": ("complaints mi", "root cause of complaints", "root-cause"),
    },
    {
        "id": "service_desk",
        "catalogue_id": "Q009",
        "experiment": "21-it-service-desk",
        "name": "IT service desk",
        "keywords": ("password reset", "service desk", "mfa reset"),
    },
    {
        "id": "sar_onchain",
        "catalogue_id": "UK07",
        "experiment": "22-onchain-alert-sar-drafter",
        "name": "On-chain alert and SAR narrative",
        "keywords": ("suspicious activity report", "on-chain alert", "nominated officer"),
    },
    {
        "id": "financial_promotion",
        "catalogue_id": "UK08",
        "experiment": "23-crypto-financial-promotions-prechecker",
        "name": "Cryptoasset financial promotions pre-checker",
        "keywords": ("cryptoasset promotion", "financial promotion", "section 21 approver"),
    },
    {
        "id": "use_case_intake",
        "catalogue_id": "G001",
        "experiment": "24-agent-use-case-intake",
        "name": "Agent use-case intake",
        "keywords": ("use-case intake", "agent idea intake", "intake classification"),
    },
)

_BY_ID = {row["id"]: row for row in PATTERNS}


def _public(row: dict, basis: str) -> dict:
    return {
        "id": row["id"],
        "catalogue_id": row["catalogue_id"],
        "experiment": row["experiment"],
        "name": row["name"],
        "basis": basis,
    }


def _hits(text: str) -> list[dict]:
    folded = text.lower()
    found = []
    for row in PATTERNS:
        for keyword in row["keywords"]:
            if re.search(r"\b" + re.escape(keyword.lower()) + r"\b", folded):
                found.append(row)
                break
    return found


def match_pattern(hint: str | None, text: str) -> dict:
    """Return a primary resemblance, or candidates when the text hits several."""

    if isinstance(hint, str) and hint.strip():
        row = _BY_ID.get(hint.strip())
        if row is not None:
            chosen = _public(row, "recorded_hint")
            return {
                "resembles": chosen,
                "candidates": [chosen],
                "hint_rejected": False,
            }
        rejected = True
    else:
        rejected = False

    hits = _hits(text)
    if len(hits) == 1:
        chosen = _public(hits[0], "keyword")
        return {"resembles": chosen, "candidates": [chosen], "hint_rejected": rejected}
    candidates = [_public(row, "keyword") for row in hits]
    return {
        "resembles": None,
        "candidates": candidates,
        "hint_rejected": rejected,
        "reason": "more_than_one_pattern" if len(hits) > 1 else "no_close_pattern",
    }
