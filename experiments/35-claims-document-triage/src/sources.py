"""Sentences from pages opened on 5 November 2026.

The operative words used in the draft are the ones below. A paragraph number
that was not visible in the retrieved text is not invented.
"""

from __future__ import annotations

from datetime import date

SOURCES_PINNED_ON = date(2026, 11, 5)
DEFAULT_STALE_AFTER_DAYS = 90
LAST_VERIFIED = "2026-11-05"

ICOBS_811 = (
    "An insurer must: (1) handle claims promptly and fairly; "
    "(2) provide reasonable guidance to help a policyholder make a claim and "
    "appropriate information on its progress; (3) not unreasonably reject a claim "
    "(including by terminating or avoiding a policy); and (4) settle claims promptly "
    "once settlement terms are agreed."
)

PRINCIPLE_12 = "A firm must act to deliver good outcomes for retail customers."

PRIN_2A_2_GOOD_FAITH = "A firm must act in good faith towards retail customers."

PRIN_2A_2_GOOD_FAITH_MEANING = (
    "Acting in good faith is a standard of conduct characterised by honesty, "
    "fair and open dealing and acting consistently with the reasonable expectations "
    "of retail customers."
)

PRIN_2A_2_FORESEEABLE_HARM = "A firm must avoid causing foreseeable harm to retail customers."

PRIN_2A_2_OBJECTIVES = (
    "A firm must enable and support retail customers to pursue their financial objectives."
)

PRIN_2A_2_VULNERABILITY = (
    "ensuring that no aspect of its business involves unfairly exploiting behavioural "
    "biases displayed or characteristics of vulnerability held by retail customers"
)

ARTICLE_22A_1 = (
    "For the purposes of Articles 22B and 22C— "
    "(a) a decision is based solely on automated processing if there is no meaningful "
    "human involvement in the taking of the decision, and "
    "(b) a decision is a significant decision, in relation to a data subject, if— "
    "(i) it produces a legal effect for the data subject, or "
    "(ii) it has a similarly significant effect for the data subject."
)

ARTICLE_22C_2 = (
    "The safeguards must consist of or include measures which— "
    "(a) provide the data subject with information about decisions described in "
    "paragraph 1 taken in relation to the data subject; "
    "(b) enable the data subject to make representations about such decisions; "
    "(c) enable the data subject to obtain human intervention on the part of the "
    "controller in relation to such decisions; "
    "(d) enable the data subject to contest such decisions."
)

FCA_CASE_K = (
    "One firm assessed AI-generated claims information against a structured set of "
    "criteria, including completeness, faithfulness to source information, conciseness, "
    "adequacy of reasoning, and safety. It combined checks by staff with an automated "
    "assessment, including LLM-as-a-judge."
)

SOURCES = (
    {
        "id": "icobs-8-1-1",
        "title": "ICOBS 8.1.1R",
        "url": "https://www.handbook.fca.org.uk/handbook/ICOBS/8/1.html",
        "opened_on": "2026-11-05",
        "quote": ICOBS_811,
        "note": (
            "The current handbook page was opened on 5 November 2026. The next numbered "
            "rule on that page is ICOBS 8.1.2. A point-in-time chapter view dated "
            "21 January 2025 labels the same words ICOBS 8.1.1R. The current page's "
            "retrieved text did not print the characters 8.1.1 beside the first rule."
        ),
    },
    {
        "id": "prin-2-1-principle-12",
        "title": "PRIN 2.1 Principle 12",
        "url": "https://www.handbook.fca.org.uk/handbook/PRIN/2/1.html",
        "opened_on": "2026-11-05",
        "quote": PRINCIPLE_12,
        "note": "The Principles table on the page opened on 5 November 2026.",
    },
    {
        "id": "prin-2a-2",
        "title": "PRIN 2A.2 Cross-cutting obligations",
        "url": "https://www.handbook.fca.org.uk/handbook/PRIN/2A/2.html",
        "opened_on": "2026-11-05",
        "quote": PRIN_2A_2_GOOD_FAITH,
        "note": (
            "The page shows the good-faith, foreseeable-harm, and financial-objectives "
            "sentences under those headings. The paragraph numbers beside those three "
            "rules were not in the text retrieved. They are not cited as a numbered rule."
        ),
    },
    {
        "id": "uk-gdpr-article-22",
        "title": "UK GDPR Article 22",
        "url": "https://www.legislation.gov.uk/eur/2016/679/article/22",
        "opened_on": "2026-11-05",
        "quote": "",
        "note": (
            "The article text is omitted. Textual amendment F1 says Chapter 3 Section 4A "
            "was substituted for Article 22, in force on 5 February 2026, by the Data "
            "(Use and Access) Act 2025 section 80(1) and S.I. 2026/82 regulation 2(j)."
        ),
    },
    {
        "id": "duaa-2025-section-80",
        "title": "Data (Use and Access) Act 2025 section 80",
        "url": "https://www.legislation.gov.uk/ukpga/2025/18/section/80",
        "opened_on": "2026-11-05",
        "quote": ARTICLE_22A_1,
        "note": (
            "Section 80(1) substitutes Articles 22A to 22D for Article 22. "
            "The page says there are no known outstanding effects. Commencement: "
            "in force at Royal Assent for specified purposes, and on 5 February 2026 "
            "in so far as not already in force, by S.I. 2026/82 regulation 2(j)."
        ),
    },
    {
        "id": "fca-ai-good-practice",
        "title": "FCA AI in financial services: good practice and areas for improvement",
        "url": "https://www.fca.org.uk/publications/good-poor-practice/ai-financial-services",
        "opened_on": "2026-11-05",
        "quote": FCA_CASE_K,
        "note": (
            "Published 19 October 2026. Last updated 20 October 2026. Case study K is "
            "under section 3.2 Monitoring and oversight. The glossary defines "
            "LLM-as-a-judge as using one large language model to assess the output of "
            "another AI system. This starter's checker is deterministic. It is not that judge."
        ),
    },
    {
        "id": "foundry-rag-evaluators",
        "title": "Microsoft Foundry RAG evaluators",
        "url": "https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/rag-evaluators",
        "opened_on": "2026-11-05",
        "quote": (
            "Groundedness measures how well the generated response aligns with the given "
            "context without fabricating content. Groundedness Pro is marked preview."
        ),
        "note": (
            "The page says Groundedness returns pass or fail from a 1 to 5 scale, with a "
            "default pass threshold of 3. This starter does not use that scale and does "
            "not call the evaluator. Response Completeness is marked preview on the same page."
        ),
    },
    {
        "id": "copilot-studio-harnesses",
        "title": "Harnesses in Copilot Studio",
        "url": "https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview",
        "opened_on": "2026-11-05",
        "quote": (
            "The GitHub Copilot harness is a Microsoft Copilot Studio authoring and "
            "orchestration framework, not the GitHub Copilot service."
        ),
        "note": (
            "A last-updated date was not in the text retrieved. The overview did not mark "
            "the harness itself as preview. Billing articles linked from the page were not opened."
        ),
    },
)
