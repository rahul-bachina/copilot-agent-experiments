# Security and permissions

Document intake, Experiment 12. Catalogue ID O001.

This note matches `agent-manifest.yaml`. If the two disagree, the manifest is the control. It is written for an organisation deciding whether to try the starter, not as a completed DPIA.

## Purpose

The agent reads one synthetic batch and returns a draft inventory: hashes, a keyword class, a checklist preview, injection signals, stale dates, and a redaction proposal from Experiment 08. Autonomy is A1. The user confirms the file list and the permitted purpose. An intake reviewer accepts, returns, or rejects the routing suggestion. The agent cannot execute either step.

## What the agent cannot do

These are disabled in the manifest, not merely discouraged in the prompt.

- Confirm the file list or the permitted purpose.
- Accept, return, or reject a routing suggestion.
- Accept a file into a queue, a case, or a work tray.
- Approve or reject a KYC file, a claim, a subject-access disclosure, or an evidence finding.
- Write a production record, including Dataverse, SharePoint, a case system, or a mailbox.
- Send email or any other external message.
- Release redacted text, store a reversible token map, or describe the text as anonymised.
- Call catalogue rows B004, B007, UK11, or UK09. Those ids are labels.
- Look up a person, a policy, or a case in NHS, HMRC, Companies House, or a bank directory.

There is no tool whose side effect is any of the above. `record_user_confirmation` and `record_reviewer_decision` update a copy of the JSON in memory and still do not write a queue. The skills say the agent must not call them. `commit_to_queue`, `send_external`, `write_production_record`, `approve_underlying_matter`, `reject_underlying_matter`, and `release_redacted` raise `IntakeForbidden`. `tests/test_intake.py` and `tests/test_injection.py` check that an instruction inside a document does not become an action.

## Data

**Read, in this starter.** The one batch the user supplies. The as-of date, the optional stale window, and an optional purpose id typed outside the file. The static catalogue in `src/catalogue.py`. Experiment 08, called in-process on each `text/plain` file inside the size cap.

**Not read.** Mailboxes, SharePoint libraries, Dataverse, case systems, and registers. The Experiment 08 reversible token vault. Customer or patient records beyond the pasted batch.

File text may contain UK identifiers, and an NHS number can sit in a health context. The manifest does **not** assert a UK GDPR lawful basis. A council handling a subject-access bundle and a firm handling KYC evidence do not share one Article 6 basis. Article 6(1)(c) or 6(1)(e) may be relevant. This file does not choose. An Article 9 condition is not asserted. The caller confirms both before production use.

The Python starter does not persist the text. The draft stores hashes, entity types, and closed-list phrases. It does not store the body, the redacted text, or the raw identifiers. A batch that is not marked synthetic is refused, and the refusal does not echo the body. Production inference, if used, should run in Microsoft Foundry in UK South or UK West. Confirm the data-use terms at deployment.

Samples use the non-allocatable National Insurance, NHS, postcode, and sort-code fixtures documented in Experiment 08. They are not live records.

## Prompt injection and stale data

File text is untrusted. The scanner records a phrase in the body, in an HTML comment, after a form feed, after three or more blank lines, between zero-width characters, or in the filename. The phrases include instructions to ignore previous instructions, confirm the files, set the purpose, approve the file, email the customer, pay a claim, disclose records, or ignore the document date. `followed` is false. A prohibited key on the batch, including `files_confirmed` and `permitted_purpose`, is stripped. A purpose named inside the file is not a selection.

A document date more than the threshold before the as-of date is stale. The default threshold is 90 days. Equal to 90 days is not stale. A future date, a missing date, and an unparseable date are not treated as current. The purpose catalogue is pinned on 27 October 2026. The same window applies to that pin. A sentence in the file does not clear the flag. An earlier `rules_as_of` warns that Experiment 08's rules may be stale. Detection still uses the pinned rules.

A file over 20,000 characters is not scanned. That miss is stated on the draft as `too_large`. A media type other than `text/plain` is `not_read` and is not classified and not sent to the gateway. If that file's JSON still contains a text body under the cap, the body is scanned for instructions and is still not treated as a reading of the file.

The residual risk is a misleading brief if a model is later wrapped around the JSON, and a UK identifier that Experiment 08 does not detect. The reviewer is the control. There is no autonomous send behind a bad draft. The draft does not claim the text is anonymised. Residual risk R2 in the manifest stays High for that reason.

## Human approval

Autonomy A1 means two people decide, in order. The agent still has no tool that carries either decision out. Approving a sentence in the chat does not confirm the files or accept the routing.

| Decision | Who |
|---|---|
| Confirm the file list, including each file id in order | Intake user |
| Confirm the permitted purpose from the closed list | Intake user |
| Accept, return, or reject the routing suggestion | Intake reviewer, after the user has confirmed |
| Rely on a stale, missing, future, or invalid date, or a stale catalogue | Intake reviewer, after a person has checked. `accept_routing` is refused until `acknowledge_stale` is passed. That still does not write a queue. |
| Treat an unread, empty, oversized, or checksum-failed file as examined | Intake reviewer. Confirmation is refused while a checksum does not match. |
| Release redacted text | Privacy reviewer. This agent cannot perform the release. |
| Hand the draft to a specialist agent or write it to a case | Intake reviewer. Outside this agent. |

Viewing a draft and re-running it do not need a separate approval.

## Controls a tenant would discuss

Named here, and not configured in this repository. Product pages for these controls were not opened on 27 October 2026, except the Copilot Studio harness overview and the two document-service pages cited in `docs/foundry.md`. Treat detailed behaviour as unverified.

| Control | How an organisation might use it |
|---|---|
| Entra Agent ID | An identity for the agent, separate from the user and the reviewer, with no mailbox or case-system role. |
| Conditional Access | Limit who can open the agent, and from where. |
| Power Platform DLP | Block connectors for mail, SharePoint, Dataverse, and case writes. This starter has no such connector. |
| Microsoft Foundry prompt shields | On, if a model sees the batch. Not a substitute for the missing send tool. The prompt-shields page was not re-opened on 27 October 2026. |
| Key Vault | Any later secret for a Foundry deployment. The intake has no secret. |
| Purview | A sensitivity label on a draft a person chooses to save. The starter does not apply one. |
| Application Insights | Invocation logs without the file body or the raw identifiers. Not wired up here. |

Experiment 01 records Dynamic Permissions, Dynamic Agent Risk, and Dynamic Conditional Access as announced, with availability unverified. This folder did not re-check that announcement.

## Risk register

Assessed 27 October 2026 for this starter rather than a named organisation. Residual risk is not all Low. The rows match the manifest.

| ID | Risk | Residual | Owner in the manifest |
|---|---|---|---|
| R1 | A sentence in a file confirms the files, sets the purpose, or accepts the batch | Low | Intake reviewer |
| R2 | A UK identifier reaches a later model because this draft was treated as anonymised | High | Data protection officer |
| R3 | A stale, future, or missing document date is treated as current | Medium | Intake reviewer |
| R4 | An unread PDF is treated as a clean file | Medium | Intake reviewer |
| R5 | The keyword class or the checklist is used as a KYC, claims, or disclosure decision | Medium | Intake reviewer |
| R6 | The pinned purpose list or the Experiment 08 rules drift | Medium | Intake reviewer |

## Logging

This starter writes no log. Before live use, log who ran it, the batch id, the file hashes rather than the bodies, whether injection or a stale date was flagged, and the two later human decisions. Do not log the file text or the raw identifiers in an application trace.

## Kill switch

Turn the Copilot Studio agent off. Stop calling Experiment 08, and do not then describe the intake as having redacted anything. Remove any Foundry access, using Key Vault or the role assignment if one was created. Block a later connector in a Power Platform DLP policy.

Contacts in the manifest use `example.com`. They are placeholders.

## Review

27 October 2026. Next review 27 April 2027, and sooner if the purpose list or Experiment 08's identifier rules change.

There is no ATRS mapping. A public body that used this intake on a subject-access bundle would consider the Algorithmic Transparency Recording Standard separately. This starter does not submit a record. Experiment 03 can draft an assurance pack. This experiment does not.
