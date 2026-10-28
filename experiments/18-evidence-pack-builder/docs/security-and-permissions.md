# Security and permissions

Evidence pack builder, Experiment 18. Catalogue ID L004.

This note matches `agent-manifest.yaml`. If the two disagree, the manifest is the control. It is written for an organisation deciding whether to try the starter, not as a completed DPIA.

## Purpose

The agent reads one synthetic set of items and returns a draft index: source, date, and hash for in-scope items, a proposed page order, duplicates, and flags for possible privilege and possible third-party personal data. Autonomy is A1. An evidence pack approver records the exact item list and the redaction decisions. The agent cannot execute that step, and it cannot send the result.

## What the agent cannot do

These are disabled in the manifest, not merely discouraged in the prompt.

- Approve the exact export list or the redaction decisions.
- Apply a Data Protection Act 2018 Schedule 2 exemption, including paragraphs 16 and 19.
- Decide that a search was reasonable and proportionate under UK GDPR Article 15(1A).
- Disclose personal data to a data subject, or send a pack to the Financial Ombudsman Service, the Housing Ombudsman, a regulator, or anyone else.
- Write a production record, including Dataverse, SharePoint, a case system, or a mailbox.
- Release redacted text, store a reversible token map, or describe the text as anonymised.
- Search a mailbox or a library. Scopes are a check on the paste, not a Microsoft 365 query.
- Widen the scopes or move the search period because an item says to.

There is no tool whose side effect is any of the above. `record_export_approval` and `produce_export` update or return a copy in memory. The export index has no document bodies. The skills say the agent must not call either function. `send_external`, `disclose_to_requester`, `write_production_record`, `apply_exemption`, and `release_redacted` raise `PackForbidden`. `tests/test_pack.py` and `tests/test_injection.py` check that an instruction inside an item does not become an action.

## Data

**Read, in this starter.** The one request the user supplies. The as-of date, the pack type, the authorised scopes, and the search period, passed as arguments. The static lists in `src/sources.py`. Experiment 12, called in-process on in-scope items. Experiment 08, called by that intake.

**Not read.** Mailboxes, SharePoint libraries, Dataverse, case systems, ombudsman portals, and registers. Out-of-scope bodies are not passed to Experiment 12 and are not hashed into the candidate manifest. The Experiment 08 reversible token vault.

Item text may contain UK identifiers, and an NHS number can sit in a health context. The manifest does **not** assert a UK GDPR lawful basis. A council handling a subject-access bundle and a firm preparing a complaint file do not share one Article 6 basis. Article 6(1)(c) or 6(1)(e) may be relevant. This file does not choose. An Article 9 condition is not asserted. The caller confirms both before production use.

The Python starter does not persist the text. The draft stores hashes, entity types, closed-list phrases, and source labels. It does not store the body, the redacted text, or the raw identifiers. A request that is not marked synthetic is refused, and the refusal does not echo the body. Titles and source labels are stored as supplied. Do not put an identifier in them. Production inference, if used, should run in Microsoft Foundry in UK South or UK West. Confirm the data-use terms at deployment.

Samples use the non-allocatable National Insurance and NHS fixtures documented in Experiment 08. Reedbank Borough Council is fictional. They are not live records.

UK GDPR Article 15 and Schedule 2 paragraphs 16, 18, and 19 were read on legislation.gov.uk on 28 October 2026. The ICO right-of-access pages named in `src/sources.py` were read the same day. Those citations are for the approver. This starter does not decide them. Article 12 was not opened, so no response deadline is encoded.

## Prompt injection and stale data

Item text is untrusted. HTML comments, form feeds, trailing blank lines, and zero-width characters are scanned. `followed` is false. An item that carries a listed phrase is not eligible for the approved list. A phrase that is not on the list is not detected. A file over 20,000 characters is not scanned. Those are limitations.

The source pin is 28 October 2026. A `rules_as_of` before that date, or an as-of date more than 90 days after it, sets `sources_stale`. Experiment 12's 90-day document window is reported as `intake_date_status`. Neither flag is cleared by a sentence in an item. Approval is refused until a person passes `acknowledge_stale`. The 90-day window is not a statutory period.

## Tenant controls that are named and not configured here

[Microsoft Entra Agent ID](https://learn.microsoft.com/en-us/entra/agent-id/what-is-microsoft-entra-agent-id) was not re-opened for this experiment on 28 October 2026. Other experiments in this repository cite it as the identity framework for agents, including a link to Conditional Access for agents. Treat the current licence names and the distinction between an agent identity and a user account as unverified here. This starter does not register an agent identity, an agent identity blueprint, or a Conditional Access policy.

Microsoft Foundry prompt shields were not re-opened on 28 October 2026. Unverified here. They would not redact UK identifiers and would not replace the missing send tool.

[Azure Key Vault](https://learn.microsoft.com/en-us/azure/key-vault/general/overview) was not re-opened on 28 October 2026. This starter has no secret and no model endpoint. A deployment that added a narrative model would put a secret there if a managed identity could not be used. Nothing here needs one.

Microsoft Purview audit of Copilot activity was not verified for this starter. Do not assume a draft index is audited. Coverage depends on the tenant and on which Copilot surface is in scope.

Power Platform DLP is the control that would block a mail, SharePoint, Dataverse, or portal connector if one were added later. This starter has no such connector. The DLP product page was not opened on 28 October 2026.

Application Insights is where a deployment would send a trace. This starter writes no log. Do not put item bodies or raw identifiers in a trace. Log the request id, the scopes, the search period, the in-scope hashes, and whether a review flag was raised.

## Logging

This starter writes no log. Before live use, log who ran it, the request id, the authorised scopes, the search period, the in-scope hashes rather than the bodies, whether injection or a review flag was raised, and the approver's later decision. The agent does not write that decision.

## Kill switch

Turn the Copilot Studio agent off. Stop the in-process call to Experiment 12. Revoke any later Foundry identity. Block a connector with DLP if one is added. Times are the platform's, not a measured drill. Contacts on `example.com` in the manifest are placeholders.

## ATRS

There is no ATRS mapping. A public body that used this builder on a subject-access bundle would consider the Algorithmic Transparency Recording Standard separately. This starter does not submit a record. Experiment 03 can draft an assurance pack. This experiment does not.

## Review

Reviewed for this starter on 28 October 2026. Next review 28 April 2027, and sooner if Article 15, Schedule 2, the ICO right-of-access guidance, or Experiment 08 or 12 changes.
