"""Pages opened on 17 November 2026. The core does not download them when it runs.

Article 22B(2) was not in the text returned for that article. It is not quoted.
S.I. 2026/82 regulation 5 was not opened. No regulations made under Article 22D
were read. Whether any have been made was not checked.
"""

from __future__ import annotations

from datetime import date

SOURCES_PINNED_ON = date(2026, 11, 17)
STALE_AFTER_DAYS = 180
DEFAULT_NOTE_STALE_DAYS = 180

ARTICLE_5_1_A = (
    "processed lawfully, fairly and in a transparent manner in relation to "
    "the data subject (‘lawfulness, fairness and transparency’)"
)
ARTICLE_5_1_C = (
    "adequate, relevant and limited to what is necessary in relation to the "
    "purposes for which they are processed (‘data minimisation’)"
)
ARTICLE_22A_1 = (
    "a decision is based solely on automated processing if there is no meaningful "
    "human involvement in the taking of the decision, and a decision is a "
    "significant decision, in relation to a data subject, if it produces a legal "
    "effect for the data subject, or it has a similarly significant effect for "
    "the data subject"
)
ARTICLE_22B_1 = (
    "A significant decision based entirely or partly on processing described in "
    "Article 9(1) (processing of special categories of personal data) may not be "
    "taken based solely on automated processing, unless one of the following "
    "conditions is met."
)
ARTICLE_22C_2 = (
    "The safeguards must consist of or include measures which provide the data "
    "subject with information about decisions described in paragraph 1 taken in "
    "relation to the data subject, enable the data subject to make representations "
    "about such decisions, enable the data subject to obtain human intervention "
    "on the part of the controller in relation to such decisions, and enable the "
    "data subject to contest such decisions."
)
ARTICLE_22D_1 = (
    "The Secretary of State may by regulations provide that, for the purposes of "
    "Article 22A(1)(a), there is, or is not, to be taken to be meaningful human "
    "involvement in the taking of a decision in cases described in the regulations."
)
EQUALITY_S4 = (
    "The following characteristics are protected characteristics— age; disability; "
    "gender reassignment; marriage and civil partnership; pregnancy and maternity; "
    "race; religion or belief; sex; sexual orientation."
)
EQUALITY_S39_2 = (
    "An employer (A) must not discriminate against an employee of A's (B)— "
    "as to B's terms of employment; in the way A affords B access, or by not "
    "affording B access, to opportunities for promotion, transfer or training "
    "or for receiving any other benefit, facility or service; by dismissing B; "
    "by subjecting B to any other detriment."
)

COMMENCEMENT_NOTE = (
    "UK GDPR Article 22A, as published on legislation.gov.uk on 17 November 2026, "
    "is annotated as substituted for Article 22 on 19 June 2025 for specified "
    "purposes and on 5 February 2026 in so far as not already in force, by the "
    "Data (Use and Access) Act 2025 sections 80(1) and 142(1) and (2)(h), and by "
    "S.I. 2026/82 regulation 2(j), with regulation 5. The same footnote is on "
    "Articles 22B, 22C, and 22D. Regulation 5 was not opened and is not interpreted. "
    "Article 22B(2) was not in the text returned for Article 22B and is not quoted. "
    "No regulations under Article 22D were read. Whether any have been made was "
    "not checked and is unverified."
)

ICO_AUTOMATED_NOTE = (
    "The ICO page 'What do we need to do if we use monitoring tools that use "
    "solely automated processes?' still names Article 22 of the UK GDPR. It says "
    "a similarly significant effect is likely to include a decision that "
    "significantly affects someone's financial circumstance, for example "
    "increasing or decreasing a worker's pay based on their performance at work, "
    "or that affects a worker's employment opportunities, for example dismissing "
    "someone. It says human oversight should not be a token gesture. The page "
    "carries a banner that the guidance is under review because of the Data "
    "(Use and Access) Act and may change. This starter has not reconciled that "
    "page with Articles 22A to 22D. That reconciliation is unverified."
)


def source_rows(as_of: str, *, rules_current: bool) -> list[dict]:
    """Citation rows. Quotations are omitted when the pin is stale."""
    taken = rules_current
    return [
        {
            "id": "uk-gdpr-article-5",
            "title": "UK GDPR Article 5",
            "url": "https://www.legislation.gov.uk/eur/2016/679/article/5",
            "opened_on": SOURCES_PINNED_ON.isoformat(),
            "taken": ARTICLE_5_1_A if taken else None,
            "also_taken": ARTICLE_5_1_C if taken else None,
            "note": (
                "Article 5(1)(a) and Article 5(1)(c) were read on 17 November 2026. "
                "Article 5(1)(b) and Article 5(1)(e) were not copied. Article 6 and "
                "Article 9 were not opened. A lawful basis is not asserted."
            ),
        },
        {
            "id": "uk-gdpr-article-22a",
            "title": "UK GDPR Article 22A",
            "url": "https://www.legislation.gov.uk/eur/2016/679/article/22A",
            "opened_on": SOURCES_PINNED_ON.isoformat(),
            "taken": ARTICLE_22A_1 if taken else None,
            "note": COMMENCEMENT_NOTE,
        },
        {
            "id": "uk-gdpr-article-22b",
            "title": "UK GDPR Article 22B",
            "url": "https://www.legislation.gov.uk/eur/2016/679/article/22B",
            "opened_on": SOURCES_PINNED_ON.isoformat(),
            "taken": ARTICLE_22B_1 if taken else None,
            "note": (
                "Article 22B(1), Article 22B(3), and Article 22B(4) were in the "
                "text returned on 17 November 2026. Article 22B(2) was not in that "
                "text and is not quoted. Article 22B(4) refers to Article 6(1)(ea). "
                "Article 6 was not opened. This starter does not decide that a "
                "condition is met."
            ),
        },
        {
            "id": "uk-gdpr-article-22c",
            "title": "UK GDPR Article 22C",
            "url": "https://www.legislation.gov.uk/eur/2016/679/article/22C",
            "opened_on": SOURCES_PINNED_ON.isoformat(),
            "taken": ARTICLE_22C_2 if taken else None,
            "note": (
                "Article 22C(1) and Article 22C(2) were read. Article 22C(1) refers "
                "to regulations under Article 22D(3). Those regulations were not read."
            ),
        },
        {
            "id": "uk-gdpr-article-22d",
            "title": "UK GDPR Article 22D",
            "url": "https://www.legislation.gov.uk/eur/2016/679/article/22D",
            "opened_on": SOURCES_PINNED_ON.isoformat(),
            "taken": ARTICLE_22D_1 if taken else None,
            "note": (
                "Article 22D(1) to (5) were read. Article 22D(4) says regulations "
                "under paragraph 3 may not amend Article 22C. Article 22D(5) says "
                "regulations under this Article are subject to the affirmative "
                "resolution procedure. No such regulations were read. Whether any "
                "have been made is unverified."
            ),
        },
        {
            "id": "equality-act-section-4",
            "title": "Equality Act 2010, section 4",
            "url": "https://www.legislation.gov.uk/ukpga/2010/15/section/4",
            "opened_on": SOURCES_PINNED_ON.isoformat(),
            "taken": EQUALITY_S4 if taken else None,
            "note": (
                "The page said section 4 is up to date with all changes known to "
                "be in force on or before 16 November 2026. Extent England and "
                "Wales and Scotland. The listed characteristics are not inferred "
                "about a person. Northern Ireland equality law was not opened."
            ),
        },
        {
            "id": "equality-act-section-39",
            "title": "Equality Act 2010, section 39",
            "url": "https://www.legislation.gov.uk/ukpga/2010/15/section/39",
            "opened_on": SOURCES_PINNED_ON.isoformat(),
            "taken": EQUALITY_S39_2 if taken else None,
            "note": (
                "The page said section 39 is up to date with all changes known to "
                "be in force on or before 17 November 2026. Section 39(2) prohibits "
                "discrimination against an employee. Section 39(5) says a duty to "
                "make reasonable adjustments applies to an employer. This starter "
                "does not decide that either has been met or breached. Extent "
                "England and Wales and Scotland."
            ),
        },
        {
            "id": "ico-monitoring-workers",
            "title": "Employment practices and data protection: monitoring workers",
            "url": (
                "https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/"
                "employment/monitoring-workers/"
            ),
            "opened_on": SOURCES_PINNED_ON.isoformat(),
            "taken": None,
            "note": (
                "The hub says the guidance is under review because of the Data "
                "(Use and Access) Act and may change. It says the guidance helps "
                "employers comply with the UK GDPR and the Data Protection Act 2018. "
                "This starter does not decide that preparing a one-to-one from "
                "sources a manager selected is monitoring, and it does not decide "
                "that monitoring is lawful."
            ),
        },
        {
            "id": "ico-monitoring-automated",
            "title": (
                "What do we need to do if we use monitoring tools that use "
                "solely automated processes?"
            ),
            "url": (
                "https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/"
                "employment/monitoring-workers/"
                "what-do-we-need-to-do-if-we-use-monitoring-tools-that-use-solely-automated-processes/"
            ),
            "opened_on": SOURCES_PINNED_ON.isoformat(),
            "taken": None,
            "note": ICO_AUTOMATED_NOTE,
        },
        {
            "id": "copilot-studio-harnesses",
            "title": "Harnesses in Copilot Studio",
            "url": "https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview",
            "opened_on": SOURCES_PINNED_ON.isoformat(),
            "taken": None,
            "note": (
                "Opened on 17 November 2026. The page names the Microsoft Copilot "
                "harness, the Customer Conversation harness, and the standard harness. "
                "It describes the Microsoft Copilot harness as a runtime for "
                "reasoning-heavy multi-step work, with skills, memory, file creation, "
                "and a sandbox, billed in Copilot Credits. It does not use the words "
                "GitHub Copilot harness. A price was not on the page. Any price is "
                "unverified. This starter does not call Copilot Studio."
            ),
        },
    ]
