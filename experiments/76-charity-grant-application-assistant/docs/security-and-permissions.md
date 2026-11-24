# Security and permissions

The control is [agent-manifest.yaml](../agent-manifest.yaml). `permissions.yaml` is the same file. If this note and the manifest disagree, the manifest wins. It validates against `schemas/agent-manifest.schema.json`, the permissions schema from Experiment 03. It is written for an organisation deciding whether to try the starter, not as a completed DPIA.

## What this starter reads

The pinned funder brief, the pinned charity profile, the pinned monitoring rows, and the pinned directory. A separate approval object when the applicant approves. Experiment 12, called in-process, which does not confirm the files. Experiment 08, called in-process, which does not describe the text as anonymised.

A brief, a profile, a directory, or a criteria object inside the request is compared and not used.

## What this starter writes

One row in an in-memory synthetic store, after `record_applicant_approval` matches the named applicant and the content hash. `production_written` stays false. The row keeps the marking, the legal hold, and the retention labels. It does not keep the case-note body.

## What this starter does not do

It does not submit, contact a funder, or send. Those functions raise. Sends are off in the manifest. Passing a string that says approved does not set `human_approval`.

## Controls named for a later deployment

| Control | What this starter does |
| --- | --- |
| Entra Agent ID | Not opened on 24 November 2026. Unverified. |
| Conditional Access for agents | Not opened on 24 November 2026. Unverified. |
| Power Platform DLP | Block connectors for mail, SharePoint, and any funder portal. This starter has no such connector. A configured DLP policy was not opened. Unverified as a product setting. |
| Microsoft Foundry prompt shields | Not opened on 24 November 2026. Unverified. The Python core does not follow instructions in the documents. |
| Key Vault | No secret in this starter. |
| Purview | Not opened on 24 November 2026. Unverified. Labels in the fixtures are kept by the Python core. |
| Application Insights | Not opened on 24 November 2026. Unverified. This starter writes no log. |

## UK GDPR

Article 5(1)(c) was opened on 24 November 2026 and is quoted in `src/sources.py`. The quote is the data-minimisation principle. It is not a finding that this starter meets it. Article 6 and Article 9 were not opened. No lawful basis is asserted.

Phone numbers, email addresses, dates of birth, postal addresses, and personal names in the case notes are counted and not stored. A beneficiary count below 5 is not published. The output is not described as anonymised.

## Charity law context

Charities Act 2011 section 17(1) and section 17(5), and two passages from Charity Commission guidance CC3, are quoted for the applicant. Section 14 was not opened. PB1, PB2, and PB3 were not opened. The quotes are not a decision that the charity's trustees have had regard to the guidance.

## Kill switch

Stop using the local command by not running it. In Copilot Studio, an administrator sets the agent to Off. Times are the platform's, not a measured drill. Contacts on harbour-lane.example are placeholders.
