"""Field lists copied as identifiers, not as the template prose.

ATRS reference numbers and field names were read from the v4.0 workbook
(sheet names "0. Metadata" through "2.5. Risks", and the "Validation" sheet)
on 24 October 2026. The workbook is the file linked from GOV.UK. Prompts in
that workbook are not reproduced here. A draft either copies an inventory
value or uses GAP_TEXT.

The principles list was read the same day from the HTML playbook. Where the
section heading on that page uses different words, both are stored.
"""

from __future__ import annotations

from dataclasses import dataclass

GAP_TEXT = "Not recorded in the inventory. This draft does not fill the gap."

ATRS_TEMPLATE_VERSION = "4.0"
ATRS_RETRIEVED_ON = "2026-10-24"
ATRS_TEMPLATE_URL = "https://www.gov.uk/government/publications/algorithmic-transparency-template"
ATRS_TEMPLATE_FILE = (
    "https://assets.publishing.service.gov.uk/media/681b8f20e26cd2f713d8705d/ATRS_V4.0__FINAL.xlsx"
)
ATRS_GUIDANCE_URL = (
    "https://www.gov.uk/government/publications/"
    "guidance-for-organisations-using-the-algorithmic-transparency-recording-standard/"
    "algorithmic-transparency-recording-standard-guidance-for-public-sector-bodies"
)
ATRS_SCOPE_URL = (
    "https://www.gov.uk/government/publications/"
    "algorithmic-transparency-recording-standard-mandatory-scope-and-exemptions-policy"
)
ATRS_REPOSITORY_URL = "https://www.gov.uk/algorithmic-transparency-records"
ATRS_CONTACT = "algorithmic-transparency@dsit.gov.uk"

# Validation sheet columns, ATRS template v4.0, read 24 October 2026.
ATRS_PHASES = (
    "Pre-deployment",
    "Private Beta",
    "Public Beta",
    "Production",
    "Retired",
)
ATRS_REGIONS = (
    "International",
    "UK",
    "Great Britain",
    "England and Wales",
    "Northern Ireland",
    "Scotland",
    "Wales",
    "England",
    "London",
    "North East",
    "North West",
    "Yorkshire and the Humber",
    "East Midlands",
    "West Midlands",
    "South East",
    "East of England",
    "South West",
)
THIRD_PARTY_CHOICES = ("Yes", "No")

PLAYBOOK_URL = (
    "https://www.gov.uk/government/publications/ai-playbook-for-the-uk-government/"
    "artificial-intelligence-playbook-for-the-uk-government-html"
)
PLAYBOOK_COLLECTION_URL = "https://www.gov.uk/government/publications/ai-playbook-for-the-uk-government"
PLAYBOOK_PUBLISHED = "2025-02-10"
PLAYBOOK_RETRIEVED_ON = "2026-10-24"

ICO_DPIA_URL = (
    "https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/"
    "accountability-and-governance/data-protection-impact-assessments-dpias/how-do-we-do-a-dpia/"
)
ICO_DPIA_RETRIEVED_ON = "2026-10-24"

DUAA_SECTION_80_URL = "https://www.legislation.gov.uk/ukpga/2025/18/section/80"
UK_GDPR_ARTICLE_6_URL = "https://www.legislation.gov.uk/eur/2016/679/article/6"
UK_GDPR_ARTICLE_22A_URL = "https://www.legislation.gov.uk/eur/2016/679/article/22A"
DUAA_RETRIEVED_ON = "2026-10-24"

FCA_AI_PRACTICE_URL = "https://www.fca.org.uk/publications/good-poor-practice/ai-financial-services"
FCA_AI_PRACTICE_PUBLISHED = "2026-10-19"
FCA_AI_PRACTICE_UPDATED = "2026-10-20"

# Draft threshold only. Catalogue item G007 says the evaluation owner approves
# thresholds. This module does not record that approval.
STALE_AFTER_DAYS = 180

GOVERNANCE_OWNER_ROLE = "Governance owner"
GENERATED_ID_PREFIX = "g010-generated-"

LIFECYCLE_STATUSES = (
    "proposed",
    "in_design",
    "pilot",
    "assurance_drafted",
    "awaiting_governance_owner",
    "approved_for_limited_use",
    "suspended",
    "retired",
)

SECTORS = ("public", "fca_firm", "other")
AUTONOMY_LEVELS = ("A0", "A1", "A2")
TRI_STATE = ("yes", "no", "unknown")
SIGNIFICANT_EFFECTS = ("legal", "similarly_significant", "none", "unknown")
PROCESSING_REGIMES = ("uk_gdpr", "law_enforcement", "intelligence_services", "unknown")


@dataclass(frozen=True)
class AtrsField:
    reference: str
    section: str
    tier: int
    name: str
    inventory_key: str
    allowed: tuple[str, ...] = ()


def _f(
    reference: str,
    section: str,
    tier: int,
    name: str,
    inventory_key: str,
    allowed: tuple[str, ...] = (),
) -> AtrsField:
    return AtrsField(reference, section, tier, name, inventory_key, allowed)


# The model-name cell in the workbook is labelled "2.4.2.1." with a trailing
# full stop. The reference used here is "2.4.2.1", without that extra stop.
ATRS_FIELDS: tuple[AtrsField, ...] = (
    _f("0.1", "Metadata and title", 0, "Title", "name"),
    _f("0.2", "Metadata and title", 0, "Organisation name", "organisation_name"),
    _f("0.3", "Metadata and title", 0, "Phase", "atrs_phase", ATRS_PHASES),
    _f("0.4", "Metadata and title", 0, "Region", "region", ATRS_REGIONS),
    _f("0.5", "Metadata and title", 0, "One sentence description", "one_sentence_description"),
    _f("1.1", "Tier 1 Summary information", 1, "Name", "name"),
    _f("1.2", "Tier 1 Summary information", 1, "Description", "public_description"),
    _f("1.3", "Tier 1 Summary information", 1, "Website URL", "website_url"),
    _f("1.4", "Tier 1 Summary information", 1, "Contact email", "contact_email"),
    _f("2.1.1", "Owner and responsibility", 2, "Organisation or department", "organisation_name"),
    _f("2.1.2", "Owner and responsibility", 2, "Team", "team"),
    _f("2.1.3", "Owner and responsibility", 2, "Senior responsible owner", "senior_responsible_owner_role"),
    _f("2.1.4", "Owner and responsibility", 2, "Third party involvement", "third_party_involvement", THIRD_PARTY_CHOICES),
    _f("2.1.4.1", "Owner and responsibility", 2, "Third party", "third_party_name"),
    _f("2.1.4.2", "Owner and responsibility", 2, "Companies House Number", "companies_house_number"),
    _f("2.1.4.3", "Owner and responsibility", 2, "Third party role", "third_party_role"),
    _f("2.1.4.4", "Owner and responsibility", 2, "Procurement procedure type", "procurement_procedure_type"),
    _f("2.1.4.5", "Owner and responsibility", 2, "Third party data access terms", "third_party_data_access_terms"),
    _f("2.2.1", "Description and rationale", 2, "Detailed description", "detailed_description"),
    _f("2.2.2", "Description and rationale", 2, "Benefits", "benefits"),
    _f("2.2.3", "Description and rationale", 2, "Previous process", "previous_process"),
    _f("2.2.4", "Description and rationale", 2, "Alternatives considered", "alternatives_considered"),
    _f("2.3.1", "Deployment context", 2, "Integration into broader operational process", "operational_process"),
    _f("2.3.2", "Deployment context", 2, "Human review", "human_review"),
    _f("2.3.3", "Deployment context", 2, "Frequency and scale of usage", "frequency_and_scale"),
    _f("2.3.4", "Deployment context", 2, "Required training", "required_training"),
    _f("2.3.5", "Deployment context", 2, "Appeals and review", "appeals_and_review"),
    _f("2.4.1.1", "Tool specification", 2, "System architecture", "system_architecture"),
    _f("2.4.1.2", "Tool specification", 2, "System-level input", "system_input"),
    _f("2.4.1.3", "Tool specification", 2, "System-level output", "system_output"),
    _f("2.4.1.4", "Tool specification", 2, "Maintenance", "maintenance"),
    _f("2.4.1.5", "Tool specification", 2, "Models", "models_summary"),
    _f("2.4.2.1", "Model specification", 2, "Model name", "model_name"),
    _f("2.4.2.2", "Model specification", 2, "Model version", "model_version"),
    _f("2.4.2.3", "Model specification", 2, "Model task", "model_task"),
    _f("2.4.2.4", "Model specification", 2, "Model input", "model_input"),
    _f("2.4.2.5", "Model specification", 2, "Model output", "model_output"),
    _f("2.4.2.6", "Model specification", 2, "Model architecture", "model_architecture"),
    _f("2.4.2.7", "Model specification", 2, "Model performance", "model_performance"),
    _f("2.4.2.8", "Model specification", 2, "Datasets and their purposes", "datasets_and_purposes"),
    _f("2.4.3.1", "Development data", 2, "Development data description", "development_data_description"),
    _f("2.4.3.2", "Development data", 2, "Data modality", "data_modality"),
    _f("2.4.3.3", "Development data", 2, "Data quantities", "data_quantities"),
    _f("2.4.3.4", "Development data", 2, "Sensitive attributes", "development_sensitive_attributes"),
    _f("2.4.3.5", "Development data", 2, "Data completeness and representativeness", "data_completeness"),
    _f("2.4.3.6", "Development data", 2, "Data cleaning", "data_cleaning"),
    _f("2.4.3.7", "Development data", 2, "Data collection", "data_collection"),
    _f("2.4.3.8", "Development data", 2, "Data access and storage", "development_data_access"),
    _f("2.4.3.9", "Development data", 2, "Data sharing agreements", "development_data_sharing"),
    _f("2.4.4.1", "Operational data", 2, "Data sources", "operational_data_sources"),
    _f("2.4.4.2", "Operational data", 2, "Sensitive attributes", "operational_sensitive_attributes"),
    _f("2.4.4.3", "Operational data", 2, "Data processing methods", "operational_data_processing"),
    _f("2.4.4.4", "Operational data", 2, "Data access and storage", "operational_data_access"),
    _f("2.4.4.5", "Operational data", 2, "Data sharing agreements", "operational_data_sharing"),
    _f("2.5.1", "Risks and impact assessments", 2, "Impact assessments", "impact_assessments"),
    _f("2.5.2", "Risks and impact assessments", 2, "Risks and mitigations", "risks_and_mitigations"),
)


@dataclass(frozen=True)
class PlaybookPrinciple:
    number: int
    title: str
    heading_variant: str | None
    evidence_keys: tuple[str, ...]


# Titles are the principles list on the HTML playbook. heading_variant is set
# only where the section heading on the same page differs.
PLAYBOOK_PRINCIPLES: tuple[PlaybookPrinciple, ...] = (
    PlaybookPrinciple(
        1,
        "You know what AI is and what its limitations are",
        None,
        ("detailed_description", "model_architecture", "model_performance"),
    ),
    PlaybookPrinciple(
        2,
        "You use AI lawfully, ethically and responsibly",
        None,
        ("lawful_basis", "impact_assessments", "public_description"),
    ),
    PlaybookPrinciple(
        3,
        "You know how to use AI securely",
        None,
        ("system_architecture", "operational_data_access", "risks_and_mitigations"),
    ),
    PlaybookPrinciple(
        4,
        "You have meaningful human control at the right stage",
        "You have meaningful human control at the right stages",
        ("human_review", "meaningful_human_involvement", "autonomy_level"),
    ),
    PlaybookPrinciple(
        5,
        "You understand how to manage the AI life cycle",
        "You understand how to manage the full AI life cycle",
        ("atrs_phase", "lifecycle_status", "maintenance"),
    ),
    PlaybookPrinciple(
        6,
        "You use the right tool for the job",
        None,
        ("alternatives_considered", "models_summary"),
    ),
    PlaybookPrinciple(
        7,
        "You are open and collaborative",
        None,
        ("website_url", "public_description"),
    ),
    PlaybookPrinciple(
        8,
        "You work with commercial colleagues from the start",
        None,
        ("third_party_involvement", "procurement_procedure_type", "third_party_role"),
    ),
    PlaybookPrinciple(
        9,
        "You have the skills and expertise needed to implement and use AI",
        "You have the skills and expertise needed to implement and use AI solutions",
        ("required_training",),
    ),
    PlaybookPrinciple(
        10,
        "You use these principles alongside your organisation\u2019s policies and have the right assurance in place",
        None,
        ("impact_assessments", "human_review"),
    ),
)


DPIA_STEPS: tuple[tuple[int, str, tuple[str, ...]], ...] = (
    (1, "Identify the need for a DPIA", ("public_description", "atrs_phase")),
    (2, "Describe the processing", ("operational_process", "system_input", "system_output", "operational_data_sources")),
    (3, "Consider consultation", ("appeals_and_review",)),
    (4, "Assess necessity and proportionality", ("benefits", "alternatives_considered", "lawful_basis")),
    (5, "Identify and assess risks", ("risks_and_mitigations",)),
    (6, "Identify measures to mitigate the risks", ("human_review", "risks_and_mitigations")),
    (7, "Sign off and record outcomes", ()),
)
