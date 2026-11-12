"""Pinned pages opened for Experiment 52 on 12 November 2026.

The core does not download these pages when it runs. A page that was not
opened is listed in NOT_OPENED and is not treated as decided.
"""

from __future__ import annotations

from datetime import date

PINNED_ON = date(2026, 11, 12)
SOURCE_WINDOW_DAYS = 180

SOURCES: list[dict] = [
    {
        "id": "pa2023-s21",
        "title": "Procurement Act 2023, section 21",
        "url": "https://www.legislation.gov.uk/ukpga/2023/54/section/21",
        "opened": "2026-11-12",
        "note": (
            "Section 21(1) requires a contracting authority to publish a tender "
            "notice to invite tenders in an open procedure, or, for a competitive "
            "flexible procedure, to invite a request to participate or the first "
            "or only tender. Section 21(2) defines a tender notice. Section 21(5) "
            "says the authority may not invite tenders unless the notice or "
            "associated tender documents contain enough information, including "
            "details of the goods, services or works. Section 21(6) says the "
            "requirements must be sufficiently clear and specific and must not "
            "break the technical-specification rules in section 56. Section 56 "
            "was not opened. In force at 24 February 2025 by S.I. 2024/716."
        ),
    },
    {
        "id": "pa2023-s50",
        "title": "Procurement Act 2023, section 50",
        "url": "https://www.legislation.gov.uk/ukpga/2023/54/section/50",
        "opened": "2026-11-12",
        "note": (
            "Section 50(1) requires a contract award notice before the authority "
            "enters into a public contract, with exceptions in subsection (6). "
            "Section 50(3) requires an assessment summary, before that notice, "
            "to each supplier that submitted an assessed tender, where the "
            "contract is awarded under section 19. Section 50(4) defines an "
            "assessment summary as information about the assessment of the "
            "tender and, if different, the most advantageous tender. This "
            "starter drafts a supplier response. It does not write an "
            "assessment summary. Section 19 was not opened beyond that "
            "cross-reference."
        ),
    },
    {
        "id": "ppn-026",
        "title": "PPN 026: The Social Value Model",
        "url": "https://www.gov.uk/government/publications/ppn-026-the-social-value-model/ppn-026-the-social-value-model-html",
        "opened": "2026-11-12",
        "note": (
            "Updated 28 October 2026. Paragraph 4 limits the PPN to central "
            "government departments, executive agencies and non-departmental "
            "public bodies. Paragraph 5 applies it to covered procurements of "
            "£1 million total contract value inclusive of VAT or above under "
            "the Procurement Act 2023. Paragraph 10 says in-scope organisations "
            "should apply it to procurements commenced on or after 1 January "
            "2027, and that a procurement commences when a tender notice is "
            "published. Paragraph 11 says earlier Procurement Act procurements "
            "may still use the previous edition during the transition. This "
            "starter does not decide which edition applies and does not treat "
            "a social-value weighting as met."
        ),
    },
    {
        "id": "ppn-026-guidance",
        "title": "Guidance on using PPN 026: The Social Value Model",
        "url": "https://www.gov.uk/government/publications/ppn-026-the-social-value-model/guidance-on-using-ppn-026-the-social-value-model-html",
        "opened": "2026-11-12",
        "note": (
            "Updated 28 October 2026. The guidance says PPN 026 replaces "
            "previous social-value PPNs, and that from 1 January 2027 it should "
            "be applied to new covered procurements worth £1 million or more. "
            "For a framework awarded before 1 January 2027 but on or after "
            "24 February 2025 it points to PPN 002. For a framework awarded "
            "before 24 February 2025 but on or after 1 January 2021 it points "
            "to PPN 06/20. The model outcomes named on the page are Good Jobs "
            "(1a create high-quality jobs, 1b fair working conditions, 1c fair "
            "pay) and Skills (2a training or retraining, 2b in-work progression, "
            "2c talent pipeline). Weightings on the page: 10 percent where the "
            "contract is at or above £1 million and below £5 million, and "
            "20 percent at £5 million or above, subject to the public-contract "
            "threshold note on that page. This starter does not apply a weighting."
        ),
    },
    {
        "id": "ppn-002",
        "title": "PPN 002: Taking account of social value in the award of central government contracts",
        "url": "https://www.gov.uk/government/publications/ppn-002-taking-account-of-social-value-in-the-award-of-contracts/ppn-002-taking-account-of-social-value-in-the-award-of-central-government-contracts-html",
        "opened": "2026-11-12",
        "note": (
            "Updated 5 March 2025. Still listed on the procurement policy notes "
            "collection when that page was opened on 12 November 2026. Paragraph 7 "
            "says in-scope organisations must apply it to Procurement Act "
            "procurements commenced on or after 1 October 2025, with PPN 06/20 "
            "available before that date. Paragraph 10 sets a minimum 10 percent "
            "social-value weighting. Paragraph 11 says social-value commitments "
            "made during the procurement must be reflected in the contract as "
            "contract terms, key performance indicators, or performance "
            "indicators. The PPN 026 pages describe a later model. This starter "
            "does not choose between them."
        ),
    },
    {
        "id": "ppn-014",
        "title": "PPN 014: Cyber essentials scheme",
        "url": "https://www.gov.uk/government/publications/ppn-014-cyber-essentials-scheme/ppn-014-cyber-essentials-scheme-html",
        "opened": "2026-11-12",
        "note": (
            "Published 17 February 2025. Paragraph 1 describes Cyber Essentials "
            "as a government-backed scheme. Paragraph 14 says that for the "
            "higher-risk characteristics in paragraph 12, the quickest route "
            "named is to include Cyber Essentials or Cyber Essentials Plus, "
            "and that where Cyber Essentials is required it must be renewed "
            "annually for the contract. Paragraph 15 allows equivalent controls "
            "where a supplier does not hold a certificate. Paragraph 20 says "
            "the scheme should not be applied to all contracts as a matter of "
            "course and that in-scope organisations must not take a blanket "
            "approach. Paragraph 22 describes Cyber Essentials as self-assessment "
            "verified by an independent certification body. This starter does "
            "not decide that a certificate is held."
        ),
    },
    {
        "id": "ncsc-cyber-essentials",
        "title": "NCSC Cyber Essentials overview",
        "url": "https://www.ncsc.gov.uk/cyberessentials/overview",
        "opened": "2026-11-12",
        "note": (
            "The page says Cyber Essentials is the minimum standard of cyber "
            "security recommended by the Government for organisations of all "
            "sizes, and that the scheme is aligned to five technical controls: "
            "firewalls, secure configuration, security update management, user "
            "access control, and malware protection. It says IASME is the "
            "NCSC delivery partner. It describes Cyber Essentials as a "
            "combination of self-assessment and independent audit, and Cyber "
            "Essentials Plus as the same controls with independent technical "
            "testing. A price is printed on that page. This starter does not "
            "copy a price into a bid."
        ),
    },
    {
        "id": "ppn-020",
        "title": "PPN 020: Guidance on data protection legislation",
        "url": "https://www.gov.uk/government/publications/ppn-020-guidance-on-data-protection-legislation/ppn-020-guidance-on-data-protection-legislation-html",
        "opened": "2026-11-12",
        "note": (
            "Published 24 April 2025. Paragraph 1 says the note covers data "
            "protection requirements under UK GDPR and the UK International "
            "Data Transfer Agreement. Paragraph 9 says the primary UK legal "
            "data protection framework is the UK GDPR. Paragraph 10 says the "
            "Data Protection Act 2018 contains clarifications and exemptions "
            "and that the two have to be read together. The Data Protection "
            "Act 2018 and UK GDPR Articles 6, 9 and 28 were not opened. No "
            "lawful basis is asserted."
        ),
    },
    {
        "id": "ppn-collection",
        "title": "Procurement policy notes collection",
        "url": "https://www.gov.uk/government/collections/procurement-policy-notes",
        "opened": "2026-11-12",
        "note": (
            "The page header said last updated 5 August 2026. The Procurement "
            "Act 2023 section of the same page listed later items, including "
            "PPN 014 (17 February 2025), PPN 020 (24 April 2025), PPN 002 "
            "(5 March 2025) and PPN 026 (28 October 2026). The header date and "
            "the item dates do not match. The item pages above are the ones "
            "this starter relies on. Enquiries on the collection page go to "
            "info@gca.gov.uk. PPN 014 still names the Crown Commercial Service. "
            "This starter does not decide which name a bidder should use."
        ),
    },
    {
        "id": "harness-overview",
        "title": "Harnesses in Copilot Studio",
        "url": "https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview",
        "opened": "2026-11-12",
        "note": (
            "The standard harness follows the topics and rules the maker "
            "defines. The GitHub Copilot harness is a Copilot Studio authoring "
            "and orchestration framework, not the GitHub Copilot service. The "
            "page says customer data is not sent to the GitHub Copilot service "
            "when agents run in Copilot Studio. It can create and edit Word, "
            "Excel, PowerPoint and PDF files, supports skills and memory, and "
            "uses Copilot Credits. The page states no price. The Customer "
            "Conversation harness is described for customer voice and chat. "
            "This starter does not build that third harness."
        ),
    },
    {
        "id": "word-js-body",
        "title": "Word JavaScript API, Word.Body.insertParagraph",
        "url": "https://learn.microsoft.com/en-us/javascript/api/word/word.body?view=word-js-preview",
        "opened": "2026-11-12",
        "note": (
            "insertParagraph is in API set WordApi 1.1. For the document body "
            "the insert location is Start or End. This is an Office Add-in "
            "API. This starter does not call it."
        ),
    },
    {
        "id": "graph-put-content",
        "title": "Microsoft Graph driveItem upload",
        "url": "https://learn.microsoft.com/en-us/graph/api/driveitem-put-content?view=graph-rest-1.0",
        "opened": "2026-11-12",
        "note": (
            "PUT content creates or replaces a file up to 250 MB and returns "
            "a driveItem. The least-privileged delegated permission named on "
            "the page is Files.ReadWrite. The page says Content-Type text/plain "
            "is required, and its example uploads a text file. A larger file "
            "uses an upload session, which was not opened. The page does not "
            "describe editing a Word paragraph. This starter does not call Graph."
        ),
    },
    {
        "id": "word-release-notes",
        "title": "Office Current Channel release notes",
        "url": "https://learn.microsoft.com/en-us/OfficeUpdates/current-channel",
        "opened": "2026-11-12",
        "note": (
            "Version 2602 (Build 19725.20172), dated 10 March on that page, "
            "says Agent mode in Word adds a conversational chat experience "
            "that helps create, edit and refine document content, and that "
            "natural-language requests can draft text and rewrite sections. "
            "The same page mentions Draft with Copilot in resolved issues. "
            "A dedicated Copilot in Word product overview was not opened. "
            "Licensing for Microsoft 365 Copilot was not opened."
        ),
    },
    {
        "id": "copilot-word-training",
        "title": "Draft impactful documents using AI",
        "url": "https://learn.microsoft.com/en-us/training/modules/draft-impactful-documents-using-ai/",
        "opened": "2026-11-12",
        "note": (
            "A training module, not a product contract. It says the module "
            "covers drafting with Copilot in Microsoft Word, including from "
            "referenced files, emails and meetings, and a Writing Coach agent. "
            "Behaviour in a tenant was not checked."
        ),
    },
]

NOT_OPENED: tuple[str, ...] = (
    "Procurement Act 2023 section 19, beyond the cross-reference in sections 21 and 50",
    "Procurement Act 2023 sections 12, 23 and 56",
    "The Procurement Regulations 2024, including regulation 31",
    "Public Services (Social Value) Act 2012",
    "PPN 06/20, beyond the cross-reference on the PPN 026 guidance page",
    "UK GDPR Articles 6, 9 and 28",
    "Data Protection Act 2018",
    "A dedicated Microsoft 365 Copilot in Word product overview",
    "Microsoft Graph upload-session page",
    "Microsoft 365 Copilot licensing",
    "Usage-based billing for Copilot Studio harnesses",
    "Microsoft Entra Agent ID, Conditional Access, Power Platform DLP as a configured policy, Microsoft Foundry prompt shields, Key Vault, Microsoft Purview, and Application Insights",
)
