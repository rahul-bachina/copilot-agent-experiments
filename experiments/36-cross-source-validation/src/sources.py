"""Pages opened for Experiment 36. The comparison does not fetch them again.

`last_verified` is the day the page was opened. A later as-of date can mark
a row stale when `stale_applicable` is true. Rows that were not opened are
not stale-tested and are not quoted as if they had been read.
"""

from __future__ import annotations

from datetime import date

SOURCES: tuple[dict, ...] = (
    {
        "id": "uk-gdpr-article-5",
        "title": "UK GDPR Article 5",
        "url": "https://www.legislation.gov.uk/eur/2016/679/article/5",
        "last_verified": "2026-11-05",
        "stale_applicable": True,
        "opened": True,
        "note": (
            "Opened on 5 November 2026. Article 5(1)(d) says personal data shall be "
            "accurate and, where necessary, kept up to date; every reasonable step must "
            "be taken to ensure that personal data that are inaccurate, having regard to "
            "the purposes for which they are processed, are erased or rectified without "
            "delay ('accuracy'). That paragraph had no footnote marker. Footnotes on the "
            "page were on Article 5(1)(b), Article 5(1)(e), and the inserted Article 5(3). "
            "This starter does not erase or rectify anything."
        ),
    },
    {
        "id": "dpa-2018-section-205",
        "title": "Data Protection Act 2018, section 205",
        "url": "https://www.legislation.gov.uk/ukpga/2018/12/section/205",
        "last_verified": "2026-11-05",
        "stale_applicable": True,
        "opened": True,
        "note": (
            "Opened on 5 November 2026. Section 205(1) says 'inaccurate', in relation to "
            "personal data, means incorrect or misleading as to any matter of fact. The "
            "revision banner said the Act was up to date with all changes known to be in "
            "force on or before 1 November 2026, and that changes may be brought into force "
            "at a future date. Those future-change lists were not checked for an effect on "
            "this definition. A material discrepancy in this tool is not a finding that "
            "personal data is inaccurate under this section."
        ),
    },
    {
        "id": "companies-house-about",
        "title": "Companies House",
        "url": "https://www.gov.uk/government/organisations/companies-house",
        "last_verified": "2026-11-05",
        "stale_applicable": True,
        "opened": True,
        "note": (
            "Opened on 5 November 2026. The page says: 'We incorporate and dissolve "
            "limited companies. We register company information and make it available "
            "to the public.' This starter does not query that register. A document "
            "kind of register_extract is text the reviewer supplied. Company numbers "
            "in the fixtures are synthetic and were not looked up."
        ),
    },
    {
        "id": "ico-accuracy",
        "title": "ICO principle (d): accuracy",
        "url": "https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/data-protection-principles/a-guide-to-the-data-protection-principles/accuracy/",
        "last_verified": "2026-11-05",
        "stale_applicable": False,
        "opened": False,
        "note": (
            "Requested on 5 November 2026. The response was HTTP 403. The page was not "
            "opened and is not quoted. A search snippet is not treated as the page. "
            "This row is not stale-tested."
        ),
    },
    {
        "id": "harness-overview",
        "title": "Copilot Studio harnesses overview",
        "url": "https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview",
        "last_verified": "2026-11-05",
        "stale_applicable": True,
        "opened": True,
        "note": (
            "Opened on 5 November 2026. The page says the GitHub Copilot harness is a "
            "Microsoft Copilot Studio authoring and orchestration framework, not the "
            "GitHub Copilot service, and that customer data is not sent to or processed "
            "by the GitHub Copilot service when agents run in Copilot Studio. It describes "
            "that harness as reasoning-heavy and multi-step, with skills, memory, file "
            "creation, and a sandbox, using Copilot Credits. The billing overview page "
            "was not opened. No tariff is stated here. The same page describes a Customer "
            "Conversation harness and a standard harness. This experiment does not use "
            "the Customer Conversation harness."
        ),
    },
    {
        "id": "skills-overview",
        "title": "Skills overview for the GitHub Copilot harness",
        "url": "https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/skills-overview",
        "last_verified": "2026-11-05",
        "stale_applicable": True,
        "opened": True,
        "note": (
            "Opened on 5 November 2026. The page says the orchestration runtime invokes "
            "a skill when a request matches the skill's purpose, and decides from the "
            "user's message and the skill's description. It does not describe routing "
            "weights or classic-orchestration trigger phrases. This starter does not "
            "assign routing weights."
        ),
    },
    {
        "id": "exp-08-identifier-rules",
        "title": "Experiment 08 company-number prefixes and postcode shapes",
        "url": "experiments/08-uk-pii-redaction-gateway/src/identifiers.py",
        "last_verified": "2026-10-26",
        "stale_applicable": False,
        "opened": False,
        "note": (
            "Imported, not re-opened. Experiment 08 pins the Companies House URI "
            "customer guide (2011) and the ILR specification 2015-16 Annex C. Those "
            "PDFs were not opened on 5 November 2026. This row is not stale-tested."
        ),
    },
    {
        "id": "catalogue-boundary",
        "title": "Catalogue row B005",
        "url": None,
        "last_verified": "2026-11-05",
        "stale_applicable": False,
        "opened": False,
        "note": (
            "The planning catalogue row says the reviewer resolves every material "
            "discrepancy and records the stack as CS-GH + AZ. That file is not in "
            "this repository. It was read from the task brief. This row is not "
            "stale-tested. The score in that file is not repeated here."
        ),
    },
)


def source_rows(as_of: date, stale_after_days: int) -> list[dict]:
    rows = []
    for source in SOURCES:
        row = dict(source)
        if source["stale_applicable"]:
            verified = date.fromisoformat(source["last_verified"])
            age = (as_of - verified).days
            row["age_days"] = age
            row["stale"] = age > stale_after_days or age < 0
        else:
            row["age_days"] = None
            row["stale"] = False
        rows.append(row)
    return rows
