"""Closed lists for the evidence pack builder. Pinned 28 October 2026.

A pack type is a label. A scope is a check on pasted items. Neither is a
search of a tenant, a disclosure, or an exemption decision.

Legislation and ICO pages were opened on 28 October 2026. The strings below
are what those pages showed. They are not a finding that an exemption applies.
"""

from __future__ import annotations

from datetime import date

SOURCES_PINNED_ON = date(2026, 10, 28)
STALE_AFTER_DAYS = 90
CATALOGUE_ID = "L004"
EXPERIMENT_ID = "exp-18-evidence-pack-builder"
INTAKE_EXPERIMENT_ID = "exp-12-document-intake"
INTAKE_CATALOGUE_ID = "O001"
GATEWAY_EXPERIMENT_ID = "exp-08-uk-pii-redaction-gateway"
GATEWAY_CATALOGUE_ID = "O005"
APPROVER_ROLE = "Evidence pack approver"

SCOPES = (
    "case_file",
    "correspondence",
    "complaints_log",
    "repairs_log",
    "audit_workpapers",
    "investigation_notes",
)

PACK_TYPES = {
    "sar_bundle": {
        "label": "Subject access request bundle",
        "intake_purpose": "sar_bundle",
        "downstream_note": (
            "Experiment 12 labels this purpose UK11 and does not call that row. "
            "This pack does not disclose anything to a data subject."
        ),
    },
    "regulator_information_request": {
        "label": "Regulator information request",
        "intake_purpose": "evidence_bundle",
        "downstream_note": (
            "Experiment 12 labels this purpose UK09 and does not call that row. "
            "Nothing is sent to a regulator."
        ),
    },
    "fos_referral": {
        "label": "Complaint referral bundle for the Financial Ombudsman Service",
        "intake_purpose": "evidence_bundle",
        "downstream_note": (
            "A label for a person preparing material. Financial Ombudsman Service "
            "evidence rules were not opened on 28 October 2026. Unverified. Nothing is sent."
        ),
    },
    "housing_ombudsman_referral": {
        "label": "Complaint referral bundle for the Housing Ombudsman",
        "intake_purpose": "evidence_bundle",
        "downstream_note": (
            "A label for a person preparing material. Housing Ombudsman evidence "
            "rules were not opened on 28 October 2026. Unverified. Nothing is sent."
        ),
    },
    "internal_investigation": {
        "label": "Internal investigation bundle",
        "intake_purpose": "evidence_bundle",
        "downstream_note": "A label. This pack does not make a finding and does not send.",
    },
    "audit_request": {
        "label": "Internal audit request",
        "intake_purpose": "evidence_bundle",
        "downstream_note": "A label. This pack does not conclude an audit and does not send.",
    },
}

# A hit is a reason for a person to look. It is not a finding that paragraph 19 applies.
PRIVILEGE_PHRASES = (
    "legal professional privilege",
    "without prejudice",
    "legally privileged",
    "solicitor's advice",
    "solicitors' advice",
    "counsel's opinion",
    "confidentiality of communications",
)

# A hit is a reason for a person to look. It is not a finding that paragraph 16 applies.
# The US spelling "neighbor" is deliberately absent. That miss is a limitation.
THIRD_PARTY_PHRASES = (
    "third party",
    "another resident",
    "the neighbour",
    "joint account holder",
    "information about another",
)

CITATIONS = (
    {
        "id": "uk_gdpr_art_15",
        "instrument": "UK GDPR Article 15",
        "url": "https://www.legislation.gov.uk/eur/2016/679/article/15",
        "retrieved": "2026-10-28",
        "read": (
            "Article 15(1) is the right to obtain confirmation whether personal data "
            "are being processed and, where that is the case, access to the personal "
            "data and the information listed in that paragraph. Article 15(1A) limits "
            "that to what the controller is able to provide based on a reasonable and "
            "proportionate search. Article 15(3) requires a copy of the personal data "
            "the data subject is entitled to under paragraph 1. Article 15(4) says the "
            "right to obtain that copy shall not adversely affect the rights and "
            "freedoms of others."
        ),
    },
    {
        "id": "dpa_sch2_para_16",
        "instrument": "Data Protection Act 2018, Schedule 2, paragraph 16",
        "url": "https://www.legislation.gov.uk/ukpga/2018/12/schedule/2/paragraph/16",
        "retrieved": "2026-10-28",
        "read": (
            "Paragraph 16(1) says Article 15(1) to (3) do not oblige a controller to "
            "disclose information to the data subject to the extent that doing so would "
            "involve disclosing information relating to another individual who can be "
            "identified from the information. Paragraph 16(2) does not remove that "
            "obligation where the other individual has consented, or where it is "
            "reasonable to disclose without consent. Paragraph 16(3) lists circumstances "
            "the controller must have regard to. Paragraph 16(4) covers information "
            "identifying another individual as the source, and identification from other "
            "information the controller reasonably believes the data subject is likely "
            "to possess or obtain."
        ),
    },
    {
        "id": "dpa_sch2_para_18",
        "instrument": "Data Protection Act 2018, Schedule 2, paragraph 18",
        "url": "https://www.legislation.gov.uk/ukpga/2018/12/schedule/2",
        "retrieved": "2026-10-28",
        "read": (
            "For Part 4 of Schedule 2, the listed UK GDPR provisions include "
            "Article 15(1) to (3). Paragraph 19 uses that definition."
        ),
    },
    {
        "id": "dpa_sch2_para_19",
        "instrument": "Data Protection Act 2018, Schedule 2, paragraph 19",
        "url": "https://www.legislation.gov.uk/ukpga/2018/12/schedule/2/paragraph/19",
        "retrieved": "2026-10-28",
        "read": (
            "The listed UK GDPR provisions do not apply to personal data that consists "
            "of information in respect of which a claim to legal professional privilege "
            "or, in Scotland, confidentiality of communications, could be maintained in "
            "legal proceedings, or information in respect of which a duty of "
            "confidentiality is owed by a professional legal adviser to a client."
        ),
    },
    {
        "id": "ico_sar_exemptions",
        "instrument": "ICO, What exemptions are relevant for SARs?",
        "url": "https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/individual-rights/right-of-access/what-exemptions-are-relevant-for-sars/",
        "retrieved": "2026-10-28",
        "read": (
            "The page's latest-update line says 8 December 2025. It says an exemption "
            "should be considered case by case, and that exemptions cannot be relied on "
            "routinely or applied in a blanket fashion. It also says reasons for relying "
            "on an exemption should be documented."
        ),
    },
    {
        "id": "ico_other_people",
        "instrument": "ICO, When can an exemption apply to information about other people in a SAR?",
        "url": "https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/individual-rights/right-of-access/when-can-an-exemption-apply-to-information-about-other-people-in-a-sar/",
        "retrieved": "2026-10-28",
        "read": (
            "The page says information need not be provided in response to a SAR to the "
            "extent that this would reveal information about another person, unless that "
            "person has consented or it is reasonable to disclose without consent. It "
            "calls this the rights of others exemption, and sometimes the third-party "
            "data exemption."
        ),
    },
)


def phrases_in(text: str, phrases: tuple[str, ...]) -> list[str]:
    """Return closed-list phrases that occur in ``text``, in list order."""

    lower = text.lower()
    return [phrase for phrase in phrases if phrase in lower]
