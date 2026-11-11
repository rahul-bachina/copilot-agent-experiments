"""Quotations from pages opened on 11 November 2026.

The pack cites these words when the as-of date is within the starter window.
It does not re-fetch them at runtime. A number that was not printed on the
rendering is marked, even where the sentence itself was read.
"""

from __future__ import annotations

from datetime import date

SOURCES_PINNED_ON = date(2026, 11, 11)
STALE_AFTER_DAYS = 180
SMALL_N = 30

PRIN_2A_5_URL = "https://www.handbook.fca.org.uk/handbook/PRIN/2A/5.html"
PRIN_2A_6_URL = "https://www.handbook.fca.org.uk/handbook/PRIN/2A/6.html"
PRIN_2A_8_URL = "https://www.handbook.fca.org.uk/handbook/PRIN/2A/8.html"
PRIN_2A_9_URL = "https://www.handbook.fca.org.uk/handbook/PRIN/2A/9.html"
FCA_PRODUCTS_URL = (
    "https://www.fca.org.uk/publications/good-and-poor-practice/products-services"
)
UK_GDPR_ART_4_URL = "https://www.legislation.gov.uk/eur/2016/679/article/4"
UK_GDPR_ART_5_URL = "https://www.legislation.gov.uk/eur/2016/679/article/5"

LABEL_DRAFT = (
    "DRAFT CUSTOMER SENTIMENT EVIDENCE. Not ready. "
    "The analyst has not confirmed the sample frame and the limitations."
)
LABEL_READY = (
    "CUSTOMER SENTIMENT EVIDENCE. The analyst confirmed the sample frame and "
    "the limitations. Not a board report. Not for publication. Not a finding "
    "that an outcome was met."
)
LABEL_REFUSED = (
    "REFUSED. No evidence pack was produced from this input."
)

# The handbook page, read 11 November 2026, numbers this limb PRIN 2A.5.3R(1)
# by the words "With regard to PRIN 2A.5.3R(1)" immediately after it.
PRIN_2A_5_3_1 = (
    "A firm must support retail customer understanding so that its communications: "
    "(a) meet the information needs of retail customers; "
    "(b) are likely to be understood by retail customers; and "
    "(c) equip retail customers to make decisions that are effective, timely and properly informed."
)
# Same rule, limb (2), on that page. The page calls the rule PRIN 2A.5.3R.
PRIN_2A_5_3_2 = (
    "A firm must communicate information to retail customers in a way which is "
    "clear, fair and not misleading."
)
# The page names PRIN 2A.5.10R(1) for this testing and monitoring duty.
PRIN_2A_5_10 = (
    "Where appropriate, a firm must: (a) test communications before communicating "
    "them to retail customers; and (b) (as set out in PRIN 2A.9) regularly monitor "
    "the impact of the communications once they have been communicated, to identify "
    "whether they are supporting good outcomes for retail customers."
)
# The page names PRIN 2A.6.2R for this rule, including at PRIN 2A.6.2R(4).
PRIN_2A_6_2 = (
    "A firm must design and deliver support to retail customers such that it: "
    "(1) meets the needs of retail customers, including those with characteristics "
    "of vulnerability; (2) ensures that retail customers can use their product as "
    "reasonably anticipated; (3) ensures that it includes appropriate friction in "
    "its customer journeys to mitigate the risk of harm and give retail customers "
    "sufficient opportunity to understand and assess their options, including any "
    "risks; and (4) ensures that retail customers do not face unreasonable barriers "
    "(including unreasonable additional costs) during the lifecycle of a product, "
    "such as when they want to: (a) make general enquiries or requests to the firm; "
    "or (f) make a complaint."
)
# The following sentence on the same page is about obligations in PRIN 2A.6.2R.
# The rendering did not print a separate provision number for this sentence.
PRIN_2A_6_DELAYS = (
    "A firm would be unlikely to meet its obligations in PRIN 2A.6.2R if its "
    "support to retail customers causes or would be likely to cause unreasonable "
    "delays when retail customers attempt to engage with the firm, including "
    "disproportionately longer call waiting times to cancel or make changes to an "
    "existing product than to purchase a new product."
)
# PRIN 2A.9, read the same day, calls this "the report required under PRIN 2A.8.3R".
PRIN_2A_8_3 = (
    "A firm must prepare a report for its governing body setting out the results "
    "of its monitoring under PRIN 2A.9 and any actions required as a result of "
    "the monitoring."
)
# The next paragraph on the PRIN 2A.8 page cites "PRIN 2A.8.4R(1)" for limb (1).
PRIN_2A_8_4 = (
    "At least annually, the governing body of a firm must: (1) review and approve "
    "the firm's report on the outcomes being received by retail customers; "
    "(2) confirm whether it is satisfied that the firm is complying with its "
    "obligations under the Consumer Duty; and (3) assess whether the firm's future "
    "business strategy is consistent with its obligations under the Consumer Duty."
)
# Sentence re-read on 11 November 2026. The rendering did not print "2A.8.5R"
# beside it. Experiment 20 pinned this sentence as PRIN 2A.8.5 on 29 October 2026.
PRIN_2A_8_5 = (
    "When approving the firm's report under PRIN 2A.8.4R(1), the governing body "
    "of the firm must also agree: (1) any action required to address any identified "
    "risk that retail customers may not receive good outcomes; (2) any action "
    "required to address any identified instance where retail customers have not "
    "received good outcomes; and (3) any amendments to the firm's business strategy "
    "to ensure that it remains consistent with meeting the firm's obligations under "
    "the Consumer Duty."
)
# Handbook wording, read 11 November 2026. The number PRIN 2A.9.8R is stated on
# the FCA good-practice page opened the same day (published 10 July 2026).
PRIN_2A_9_8 = (
    "A firm must regularly monitor the outcomes retail customers receive from: "
    "(1) the products the firm manufactures or distributes; (2) the communications "
    "the firm has with retail customers; and (3) the customer support the firm "
    "provides to retail customers."
)
# The following rule on the same page calls these "the outcomes listed in PRIN 2A.9.9R".
PRIN_2A_9_9_3 = (
    "whether retail customers are equipped with the right information to make "
    "effective, timely and properly informed decisions"
)
PRIN_2A_9_9_4 = "whether retail customers receive the support they need"
# The page names PRIN 2A.9.12R on the action rule that follows this sentence.
# Experiment 20 pinned this sentence as PRIN 2A.9.11 on 29 October 2026.
# The 11 November 2026 rendering did not print "2A.9.11R" beside the paragraph.
PRIN_2A_9_11 = (
    "A firm must have in place processes to identify the root causes of any "
    "failure to deliver the outcomes listed in PRIN 2A.9.9R for retail customers."
)

ART_4_1_5 = (
    "pseudonymisation means the processing of personal data in such a manner that "
    "the personal data can no longer be attributed to a specific data subject "
    "without the use of additional information, provided that such additional "
    "information is kept separately and is subject to technical and organisational "
    "measures to ensure that the personal data are not attributed to an identified "
    "or identifiable natural person"
)
# Article 4 was renumbered as Article 4(1) from 5 February 2026. Paragraphs 2 to 5
# were inserted the same day. This paragraph is Article 4(5), not point (5).
ART_4_5_STATS = (
    "References in this Regulation to the processing of personal data for the "
    "purposes of statistical purposes are references to processing for statistical "
    "surveys or for the production of statistical results where (a) the information "
    "that results from the processing is aggregate data that is not personal data, "
    "and (b) the controller does not use the personal data processed, or the "
    "information that results from the processing, in support of measures or "
    "decisions with respect to a particular data subject to whom the personal data relates."
)
ART_5_1_C = (
    "adequate, relevant and limited to what is necessary in relation to the "
    "purposes for which they are processed ('data minimisation')"
)

# number_verified is about the provision number, not the sentence.
# Sentences below were read on 11 November 2026 unless a note says otherwise.
SOURCES = (
    {
        "id": "prin_2a_5_3_1",
        "provision": "PRIN 2A.5.3R(1)",
        "url": PRIN_2A_5_URL,
        "number_verified": True,
        "number_basis": "named_on_the_page",
        "applies_to": ("financial_services",),
        "text": PRIN_2A_5_3_1,
    },
    {
        "id": "prin_2a_5_3_2",
        "provision": "PRIN 2A.5.3R(2)",
        "url": PRIN_2A_5_URL,
        "number_verified": True,
        "number_basis": "limb_2_of_the_rule_the_page_calls_PRIN_2A.5.3R",
        "applies_to": ("financial_services",),
        "text": PRIN_2A_5_3_2,
    },
    {
        "id": "prin_2a_5_10",
        "provision": "PRIN 2A.5.10R(1)",
        "url": PRIN_2A_5_URL,
        "number_verified": True,
        "number_basis": "named_on_the_page",
        "applies_to": ("financial_services",),
        "text": PRIN_2A_5_10,
    },
    {
        "id": "prin_2a_6_2",
        "provision": "PRIN 2A.6.2R",
        "url": PRIN_2A_6_URL,
        "number_verified": True,
        "number_basis": "named_on_the_page",
        "applies_to": ("financial_services",),
        "text": PRIN_2A_6_2,
    },
    {
        "id": "prin_2a_6_delays",
        "provision": "PRIN 2A.6 page, sentence about PRIN 2A.6.2R",
        "url": PRIN_2A_6_URL,
        "number_verified": False,
        "number_basis": "rendering_did_not_print_a_provision_number",
        "applies_to": ("financial_services",),
        "text": PRIN_2A_6_DELAYS,
    },
    {
        "id": "prin_2a_8_3",
        "provision": "PRIN 2A.8.3R",
        "url": PRIN_2A_8_URL,
        "number_verified": True,
        "number_basis": "named_on_the_PRIN_2A.9_page_as_the_report_required_under_PRIN_2A.8.3R",
        "applies_to": ("financial_services",),
        "text": PRIN_2A_8_3,
    },
    {
        "id": "prin_2a_8_4",
        "provision": "PRIN 2A.8.4R",
        "url": PRIN_2A_8_URL,
        "number_verified": True,
        "number_basis": "the_following_paragraph_on_the_page_cites_PRIN_2A.8.4R(1)",
        "applies_to": ("financial_services",),
        "text": PRIN_2A_8_4,
    },
    {
        "id": "prin_2a_8_5",
        "provision": "PRIN 2A.8.5R",
        "url": PRIN_2A_8_URL,
        "number_verified": False,
        "number_basis": "sentence_reread_on_2026-11-11_number_from_experiment_20_pin_of_2026-10-29",
        "applies_to": ("financial_services",),
        "text": PRIN_2A_8_5,
    },
    {
        "id": "prin_2a_9_8",
        "provision": "PRIN 2A.9.8R",
        "url": PRIN_2A_9_URL,
        "number_verified": True,
        "number_basis": "number_stated_on_the_fca_good_practice_page_opened_2026-11-11",
        "applies_to": ("financial_services",),
        "text": PRIN_2A_9_8,
    },
    {
        "id": "prin_2a_9_9_3",
        "provision": "PRIN 2A.9.9R(3)",
        "url": PRIN_2A_9_URL,
        "number_verified": True,
        "number_basis": "the_following_rule_on_the_page_calls_this_list_PRIN_2A.9.9R",
        "applies_to": ("financial_services",),
        "text": PRIN_2A_9_9_3,
    },
    {
        "id": "prin_2a_9_9_4",
        "provision": "PRIN 2A.9.9R(4)",
        "url": PRIN_2A_9_URL,
        "number_verified": True,
        "number_basis": "the_following_rule_on_the_page_calls_this_list_PRIN_2A.9.9R",
        "applies_to": ("financial_services",),
        "text": PRIN_2A_9_9_4,
    },
    {
        "id": "prin_2a_9_11",
        "provision": "PRIN 2A.9.11R",
        "url": PRIN_2A_9_URL,
        "number_verified": False,
        "number_basis": "sentence_reread_on_2026-11-11_number_from_experiment_20_pin_of_2026-10-29_page_names_PRIN_2A.9.12R_on_the_following_rule",
        "applies_to": ("financial_services",),
        "text": PRIN_2A_9_11,
    },
    {
        "id": "uk_gdpr_art_4_1_5",
        "provision": "UK GDPR Article 4(1)(5)",
        "url": UK_GDPR_ART_4_URL,
        "number_verified": True,
        "number_basis": "point_5_of_article_4_1_on_legislation_gov_uk",
        "applies_to": ("financial_services", "public_service"),
        "text": ART_4_1_5,
    },
    {
        "id": "uk_gdpr_art_4_5_stats",
        "provision": "UK GDPR Article 4(5)",
        "url": UK_GDPR_ART_4_URL,
        "number_verified": True,
        "number_basis": "paragraph_5_inserted_by_the_Data_Use_and_Access_Act_2025_section_67",
        "applies_to": ("financial_services", "public_service"),
        "text": ART_4_5_STATS,
    },
    {
        "id": "uk_gdpr_art_5_1_c",
        "provision": "UK GDPR Article 5(1)(c)",
        "url": UK_GDPR_ART_5_URL,
        "number_verified": True,
        "number_basis": "named_on_the_page",
        "applies_to": ("financial_services", "public_service"),
        "text": ART_5_1_C,
    },
)
