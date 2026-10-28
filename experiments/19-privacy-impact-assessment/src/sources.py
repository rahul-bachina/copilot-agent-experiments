"""Quotations pinned on 28 October 2026.

The strings below were copied from the pages named in each constant. A run
does not fetch them again. WP248 itself was not opened. Article 6, Article 9,
and Article 14 were not opened for this experiment. Where a sentence is the
ICO's paraphrase of a European guideline, the source is the ICO page.
"""

from __future__ import annotations

from datetime import date

SOURCES_PINNED_ON = date(2026, 10, 28)
STALE_AFTER_DAYS = 90
ARTICLE_22_FULL_COMMENCEMENT = date(2026, 2, 5)
COMMISSION_SUBSTITUTION = date(2026, 9, 30)

UK_GDPR_ARTICLE_35_URL = "https://www.legislation.gov.uk/eur/2016/679/article/35"
UK_GDPR_ARTICLE_36_URL = "https://www.legislation.gov.uk/eur/2016/679/article/36"
UK_GDPR_ARTICLE_22A_URL = "https://www.legislation.gov.uk/eur/2016/679/article/22A"
UK_GDPR_ARTICLE_22B_URL = "https://www.legislation.gov.uk/eur/2016/679/article/22B"
UK_GDPR_ARTICLE_22C_URL = "https://www.legislation.gov.uk/eur/2016/679/article/22C"
UK_GDPR_ARTICLE_22D_URL = "https://www.legislation.gov.uk/eur/2016/679/article/22D"
DUAA_SECTION_80_URL = "https://www.legislation.gov.uk/ukpga/2025/18/section/80"
DUAA_SECTION_119_URL = "https://www.legislation.gov.uk/ukpga/2025/18/section/119"
SI_2026_82_REG_2_URL = "https://www.legislation.gov.uk/uksi/2026/82/regulation/2/made"
SI_2026_82_REG_5_URL = "https://www.legislation.gov.uk/uksi/2026/82/regulation/5/made"
SI_2026_386_URL = "https://www.legislation.gov.uk/uksi/2026/386"
SI_2026_1015_REG_2_URL = "https://www.legislation.gov.uk/uksi/2026/1015/regulation/2/made"

ICO_WHEN_URL = (
    "https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/"
    "accountability-and-governance/data-protection-impact-assessments-dpias/"
    "when-do-we-need-to-do-a-dpia/"
)
ICO_LIST_URL = (
    "https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/"
    "accountability-and-governance/data-protection-impact-assessments-dpias/"
    "examples-of-processing-likely-to-result-in-high-risk/"
)
ICO_HOW_URL = (
    "https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/"
    "accountability-and-governance/data-protection-impact-assessments-dpias/"
    "how-do-we-do-a-dpia/"
)
ICO_CONSULT_URL = (
    "https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/"
    "accountability-and-governance/data-protection-impact-assessments-dpias/"
    "do-we-need-to-consult-the-ico/"
)
ICO_TRANSITION_URL = (
    "https://ico.org.uk/about-the-ico/media-centre/news-and-blogs/2026/09/"
    "ico-governance-changes-confirmed-for-30-september-2026"
)
HARNESS_URL = "https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview"

GAP_TEXT = "Not recorded in the project brief. This draft does not fill the gap."

ARTICLE_35_1 = (
    "Where a type of processing in particular using new technologies, and taking "
    "into account the nature, scope, context and purposes of the processing, is "
    "likely to result in a high risk to the rights and freedoms of natural persons, "
    "the controller shall, prior to the processing, carry out an assessment of the "
    "impact of the envisaged processing operations on the protection of personal data."
)

ARTICLE_35_3 = {
    "article_35_3_a": (
        "a systematic and extensive evaluation of personal aspects relating to "
        "natural persons which is based on automated processing, including profiling, "
        "and on which decisions are based that produce legal effects concerning the "
        "natural person or similarly significantly affect the natural person"
    ),
    "article_35_3_b": (
        "processing on a large scale of special categories of data referred to in "
        "Article 9(1), or of personal data relating to criminal convictions and "
        "offences referred to in Article 10"
    ),
    "article_35_3_c": (
        "a systematic monitoring of a publicly accessible area on a large scale"
    ),
}

ARTICLE_35_7 = {
    "a": (
        "a systematic description of the envisaged processing operations and the "
        "purposes of the processing, including, where applicable, the legitimate "
        "interest pursued by the controller"
    ),
    "b": "an assessment of the necessity and proportionality of the processing operations in relation to the purposes",
    "c": "an assessment of the risks to the rights and freedoms of data subjects referred to in paragraph 1",
    "d": (
        "the measures envisaged to address the risks, including safeguards, security "
        "measures and mechanisms to ensure the protection of personal data and to "
        "demonstrate compliance with this Regulation taking into account the rights "
        "and legitimate interests of data subjects and other persons concerned"
    ),
}

ARTICLE_35_2 = (
    "The controller shall seek the advice of the data protection officer, where "
    "designated, when carrying out a data protection impact assessment."
)

ARTICLE_36_1 = (
    "The controller shall consult the Commission prior to processing where a data "
    "protection impact assessment under Article 35 indicates that the processing "
    "would result in a high risk in the absence of measures taken by the controller "
    "to mitigate the risk."
)

ARTICLE_22A_1 = (
    "a decision is based solely on automated processing if there is no meaningful "
    "human involvement in the taking of the decision, and a decision is a "
    "significant decision, in relation to a data subject, if it produces a legal "
    "effect for the data subject, or it has a similarly significant effect for the "
    "data subject."
)

COMMENCEMENT_NOTE = (
    "UK GDPR Article 22A, as published on legislation.gov.uk, is annotated as "
    "substituted for Article 22 on 19 June 2025 for specified purposes and on "
    "5 February 2026 in so far as not already in force, by Data (Use and Access) "
    "Act 2025 sections 80(1) and 142(1) and (2)(h), and by S.I. 2026/82 "
    "regulation 2(j), with regulation 5. Section 80 of the Act carries the same "
    "commencement footnotes. Regulation 5 says the amendments made by section 80 "
    "and Schedule 6 do not apply to a decision taken before 5 February 2026 to "
    "which Article 22(3) of the UK GDPR, or section 14(1) or 50(2) of the Data "
    "Protection Act 2018, applied. This tool has not interpreted regulation 5, "
    "and it has not read any regulations made under Article 22D."
)

COMMISSION_NOTE = (
    "Article 35(4) and Article 36(1), as revised on legislation.gov.uk, say "
    "the Commission. The footnotes say the word was substituted on 30 September "
    "2026 by S.I. 2026/386, Schedule 3, paragraph 41, brought into force by "
    "S.I. 2026/1015 regulation 2(c). Data (Use and Access) Act 2025 section 119, "
    "in force on the same day by that regulation, transfers the functions of the "
    "Information Commissioner to the Information Commission. An ICO news item "
    "dated 15 September 2026, updated 17 September 2026, says the organisation "
    "will continue to be known as the ICO. The ICO DPIA pages still say ICO, and "
    "each of them carries a banner that the guidance is under review because of "
    "the Data (Use and Access) Act."
)

ICO_RESIDUAL_NOTE = (
    "The ICO page 'Do we need to consult the ICO?' says prior consultation is "
    "required where a DPIA identifies a high risk and you cannot reduce it, and "
    "that the focus is the residual risk after mitigating measures. It says that "
    "if the risk is no longer high, you need not consult. Article 36(1) uses "
    "different words: a high risk in the absence of measures taken to mitigate "
    "the risk. This tool does not reconcile those readings and does not decide "
    "that consultation is or is not required."
)

ICO_TWO_FACTORS = (
    "The ICO page 'When do we need to do a DPIA?' lists nine criteria from the "
    "WP29 guidelines and says that in most cases a combination of two of these "
    "factors indicates the need for a DPIA, but that this is not a strict rule. "
    "WP248 was not opened. The nine criteria used here are the nine bullets on "
    "that ICO page."
)

# ICO 'How do we do a DPIA?', step 5, opened 28 October 2026.
HARM_TYPES = (
    "inability to exercise rights",
    "inability to access services or opportunities",
    "loss of control over the use of personal data",
    "discrimination",
    "identity theft or fraud",
    "financial loss",
    "reputational damage",
    "physical harm",
    "loss of confidentiality",
    "re-identification of pseudonymised data",
    "any other significant economic or social disadvantage",
)

# The when-page says which of the ten list items require another European
# criterion. The examples page is the longer description. Both were opened.
ICO_LIST = (
    {
        "id": "innovative_technology",
        "title": "Innovative technology",
        "combination_required": True,
        "twin_wp248": "wp248_innovative_use",
        "exception_key": None,
        "question": (
            "Processing involving the use of new technologies, or the novel "
            "application of existing technologies (including AI). The ICO says a "
            "DPIA is required where this is combined with any other criterion "
            "from the European guidelines."
        ),
    },
    {
        "id": "denial_of_service",
        "title": "Denial of service",
        "combination_required": False,
        "twin_wp248": None,
        "exception_key": None,
        "question": (
            "Decisions about an individual's access to a product, service, "
            "opportunity or benefit which are based to any extent on automated "
            "decision-making (including profiling) or involve the processing of "
            "special-category data."
        ),
    },
    {
        "id": "large_scale_profiling",
        "title": "Large-scale profiling",
        "combination_required": False,
        "twin_wp248": None,
        "exception_key": None,
        "question": "Any profiling of individuals on a large scale.",
    },
    {
        "id": "biometric_data",
        "title": "Biometric data",
        "combination_required": True,
        "twin_wp248": None,
        "exception_key": None,
        "question": (
            "Any processing of biometric data for the purpose of uniquely "
            "identifying an individual. The examples page and the when-page both "
            "say a DPIA is required where this is combined with another criterion "
            "from the European guidelines. The when-page's short heading does not "
            "repeat the unique-identification words. This question uses the "
            "examples-page wording."
        ),
    },
    {
        "id": "genetic_data",
        "title": "Genetic data",
        "combination_required": True,
        "twin_wp248": None,
        "exception_key": "genetic_data_direct_care_by_individual_professional",
        "question": (
            "Any processing of genetic data, other than that processed by an "
            "individual GP or health professional for the provision of health care "
            "direct to the data subject. The ICO says a DPIA is required where "
            "this is combined with another criterion from the European guidelines. "
            "This tool does not decide that the exception applies."
        ),
    },
    {
        "id": "data_matching",
        "title": "Data matching",
        "combination_required": False,
        "twin_wp248": None,
        "exception_key": None,
        "question": "Combining, comparing or matching personal data obtained from multiple sources.",
    },
    {
        "id": "invisible_processing",
        "title": "Invisible processing",
        "combination_required": True,
        "twin_wp248": None,
        "exception_key": None,
        "question": (
            "Processing of personal data that has not been obtained direct from "
            "the data subject, where the controller considers that compliance with "
            "Article 14 would prove impossible or involve disproportionate effort. "
            "The examples page cites Article 14.5(b). Article 14 was not opened. "
            "The ICO says a DPIA is required where this is combined with another "
            "criterion from the European guidelines."
        ),
    },
    {
        "id": "tracking",
        "title": "Tracking",
        "combination_required": True,
        "twin_wp248": None,
        "exception_key": None,
        "question": (
            "Processing which involves tracking an individual's geolocation or "
            "behaviour, including but not limited to the online environment. The "
            "when-page says a DPIA is required where this processing is combined "
            "with any of the criteria from the European guidelines. The examples "
            "page says that for geolocation data in particular."
        ),
    },
    {
        "id": "targeting_children_or_vulnerable",
        "title": "Targeting of children or other vulnerable individuals",
        "combination_required": False,
        "twin_wp248": None,
        "exception_key": None,
        "question": (
            "The use of the personal data of children or other vulnerable "
            "individuals for marketing purposes, profiling or other automated "
            "decision-making, or offering online services directly to children."
        ),
    },
    {
        "id": "risk_of_physical_harm",
        "title": "Risk of physical harm",
        "combination_required": False,
        "twin_wp248": None,
        "exception_key": None,
        "question": (
            "Where the processing is of such a nature that a personal data breach "
            "could jeopardise the physical health or safety of individuals. The "
            "ICO page places square brackets around the word physical."
        ),
    },
)

WP248_CRITERIA = (
    ("wp248_evaluation_or_scoring", "Evaluation or scoring."),
    (
        "wp248_automated_decision_legal_or_similar",
        "Automated decision-making with legal or similar significant effect.",
    ),
    ("wp248_systematic_monitoring", "Systematic monitoring."),
    (
        "wp248_sensitive_or_highly_personal",
        "Sensitive data or data of a highly personal nature.",
    ),
    ("wp248_large_scale", "Data processed on a large scale."),
    ("wp248_matching_datasets", "Matching or combining datasets."),
    ("wp248_vulnerable_data_subjects", "Data concerning vulnerable data subjects."),
    (
        "wp248_innovative_use",
        "Innovative use or applying new technological or organisational solutions.",
    ),
    (
        "wp248_prevents_rights_or_service",
        "Preventing data subjects from exercising a right or using a service or contract.",
    ),
)

ICO_DUAA_BANNER = (
    "Due to changes made by the Data (Use and Access) Act, this guidance is "
    "under review and may be subject to change."
)
