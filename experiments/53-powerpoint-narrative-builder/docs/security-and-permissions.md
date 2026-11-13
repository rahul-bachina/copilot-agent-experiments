# Security and permissions

The control is [agent-manifest.yaml](../agent-manifest.yaml). `permissions.yaml` is the same file. If this note and the manifest disagree, the manifest wins. It validates against `schemas/agent-manifest.schema.json`, the permissions schema from Experiment 03. It is written for an organisation deciding whether to try the starter, not as a completed DPIA and not as an accessibility certificate.

## What the core is allowed to do

- Read one synthetic pack: a briefing note, an approved figures sheet, and a short policy extract.
- Quote a passage that Experiment 29 calls supported and that is inside the review window.
- Compare figure values with Experiment 36, and withhold a number that is not on the approved sheet or that disagrees with another value for the same figure.
- Record a presenter approval that does not produce slides and does not share the deck.
- Write a local `.pptx` only after that approval, when the presenter asks for the file.

## What it is not allowed to do

- Publish, send, or share. `tools.sends` and `tools.writes` are disabled.
- Produce slides before the approval step.
- Call Microsoft Graph or the PowerPoint JavaScript API. `graph_called` and `powerpoint_api_called` stay false.
- Mark a claim sourced without a citation quote that Experiment 29 calls supported.
- Invent a figure, a logo, a customer, or an outcome.
- Strip a protective marking or a legal-hold label.
- Decide that the accessibility regulations or WCAG 2.2 AA were met.

## Human approval

Autonomy A1. The presenter approves the outline and every citation before slides are produced or shared. That approval is `record_presenter_approval()`. It is refused until every sourced citation, every gap, the accessibility checklist, and the markings have been acknowledged. A safeguarding flag has to be acknowledged too. `slides_produced` and `shared` stay false after the record. `produce_slides()` may then write a local file. Sharing stays with the presenter.

A person is offered on every result, including a refusal. A distress or safeguarding sentence is flagged for a person. It is not copied onto a slide. Unrecognised text is a gap. It is not marked sourced and it is not copied.

## Controls named, and what was opened

Opened on 13 November 2026, and described only as far as those pages went:

- The Accessibility Regulations 2018, regulations 3, 4, and 6. Regulation 7 and regulation 9 were not opened.
- The GOV.UK accessibility-requirements page, the publishing-accessible-documents page, and the plain-English entry in the GOV.UK style guide.
- The Government Security Classifications Policy HTML edition.
- The Copilot Studio harness overview, the Microsoft 365 Copilot overview, and the Work IQ overview.

These product pages were not opened. Treat the names as unverified here: Microsoft Entra Agent ID, Conditional Access for agents, Power Platform DLP as a configured policy, Microsoft Foundry prompt shields, Key Vault, Microsoft Purview, and Application Insights. None of those objects is created in this folder.

UK GDPR Articles 6, 9, and 28, and the Data Protection Act 2018, were not opened. No lawful basis is asserted.

## Prompt injection and stale sources

Pack text is untrusted. A sentence that instructs the agent is not matched. A sentence that negates a claim is not treated as a request to cite it. A prohibited key such as `human_approval` or `presenter_approved` is stripped. Only `record_presenter_approval()` counts.

The pinned pages are not refreshed from the web. More than 180 days after 13 November 2026, no passage is quoted. Equal to 180 days is still inside that window. Experiment 29's review-stamp window is applied as well. A passage whose age is 90 days is current. A passage whose age is 91 days is not quoted.

## Kill switch

Turn the Copilot Studio agent off, remove any Foundry credential used for an optional narrative, or block a later connector for mail, Graph, or a site with Power Platform DLP. Times in the manifest are the platform's, not a measured drill. The contacts on `northmere.example` are placeholders.
