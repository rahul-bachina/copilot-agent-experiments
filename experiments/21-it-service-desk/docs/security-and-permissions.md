# Security and permissions

The control is [agent-manifest.yaml](../agent-manifest.yaml). If this note and the manifest disagree, the manifest wins.

Manifest `exp-21-it-service-desk`, version 0.1.0. Autonomy **A1**. Writes disabled. Sends disabled. Approve or reject, regulated decision, production record change, external send, and spending are disabled. So are password reset, MFA change, access grant, device change, remote wipe, and collecting a secret. A review can record a confirmation. It cannot perform the action.

Contacts in the manifest use `aldermere.example.gov.uk`. They are placeholders. Aldermere District Council is fictional.

## What a run may read

One ticket, the as-of date, a channel identity object, a separate review object, the synthetic catalogue, and the pinned sources. Free text is passed to Experiment 08 `propose()`. The redacted text is not copied into the draft. `release()` is not called. The Python starter does not persist the ticket. A record that is not marked synthetic is refused, and the refusal does not echo the text.

## What it must not read

Identity systems, device consoles, ITSM production tickets, mailboxes, licence purchasing, live knowledge bases, other people's tickets, and password or MFA stores.

## Human approval

| Decision | Who |
| --- | --- |
| Confirm a standard fix the person will try | The signed-in member of staff who raised the ticket |
| Confirm a device change | That same person, and only when the required diagnostics are present. The change is not performed. |
| Reset a password, change MFA, or grant access | Service desk analyst, outside the agent. A user confirmation is refused. |
| Take an impersonation stop, an unverified caller, or a third-party request | Service desk analyst |
| Rely on an article after it is marked stale | Service desk analyst, after someone re-opens the organisation's article |
| Write the ticket, send a message, wipe a device, or buy a licence | The person authorised for that action. Outside the agent. |

Viewing a draft and re-running it do not need a separate approval.

## Identity

A passed check is a field the channel supplies. It is honoured only when `method` is `entra_session`, `checked_by` is `channel`, `result` is `passed`, the requester is signed in, the channel is portal or Teams chat, the check's date is the as-of date, and the requester and the subject are the same synthetic staff id. A phone or email channel cannot carry it. A sentence in the ticket cannot carry it. A passed session does not authorise a password reset. This starter does not call Microsoft Entra and does not describe that product's sign-in behaviour.

The NCSC pages opened on 29 October 2026 are the reason for that shape. [Advice for End Users](https://www.ncsc.gov.uk/guidance/end-user-devices-advice-end-users), published 24 September 2016, says a person must never disclose a password to anyone, including IT support, and that the helpdesk confirms identity before a password reset. The [4 May 2025 retailers post](https://www.ncsc.gov.uk/blog-post/incidents-impacting-retailers) encourages organisations to review how the helpdesk authenticates staff before resetting passwords, especially privileged accounts. [Phishing attacks: defending your organisation](https://www.ncsc.gov.uk/guidance/phishing) says important requests should be verified using a second type of communication. This starter is not a finding that an organisation has done that review.

## UK GDPR

No lawful basis is asserted. Article 6 and Article 32 were read on 29 October 2026. Points (ea) and (f) of Article 6(1) do not apply to processing by public authorities in the performance of their tasks. Article 32(4) says a person acting under the controller's authority does not process personal data except on instructions, unless domestic law requires it. Article 9 was not opened. This note is not a DPIA.

## Prompt injection, stale data, prohibited actions

Fixtures include instructions to ignore the rules, impersonate the helpdesk, request a password, override a stale flag, and execute a fix. The checker records them and does not follow them. `tests/test_desk.py`, `tests/test_review.py`, and `eval/synthetic_dataset.json` cover that. Older than 180 days is stale. Equal to 180 is not. The legacy VPN body is not in the JSON.

## Tenant controls named and not configured here

These product pages were not opened on 29 October 2026. Treat current names, licence requirements, and behaviour as unverified in this folder:

- Microsoft Entra Agent ID, and Conditional Access for agents
- Power Platform DLP, beyond the instruction in the flow note to block a later connector
- Microsoft Foundry prompt shields
- Key Vault
- Microsoft Purview
- Application Insights

Dynamic Permissions, Dynamic Agent Risk, and Dynamic Conditional Access are recorded in Experiment 01 as announced, with availability unverified. This folder did not re-check that announcement.

A production deployment should still plan for them: an agent identity rather than a shared user account, a Conditional Access policy on that identity, a DLP policy that blocks identity, device, mail, and purchasing connectors, a secret in Key Vault if a later API needs one, a Purview boundary the organisation already uses, and an Application Insights workspace that does not store the ticket text. None of those objects is created here.

## Logging and kill switch

This starter writes no log. Before live use, log who ran it, the ticket id rather than the words, the as-of date, whether identity was trusted, whether an article was stale, the Experiment 08 finding count and input hash, and the later review. Do not put the ticket text, or a raw identifier, in an application trace.

Turn the Copilot Studio agent off. Remove any Foundry access. Block a later connector in a Power Platform DLP policy.

## Review

29 October 2026. Next review 29 April 2027, and sooner if the catalogue, the NCSC pages, or Article 6 or 32 change.
