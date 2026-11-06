# Security and permissions

The control is [agent-manifest.yaml](../agent-manifest.yaml). `permissions.yaml` is the same file. If this note and the manifest disagree, the manifest wins.

Manifest `exp-40-customer-self-service`, version 0.1.0. Autonomy **A1**. Writes disabled. Sends disabled. Approve or reject, regulated decision, production record change, external send, and spending are disabled. So are password reset, complaint closure, tariff change, contract change, and labelling a customer as vulnerable. A review can record a confirmation. It cannot perform the action.

Contacts in the manifest use `mereford.example`. They are placeholders. Mereford Customer Service is fictional. The telephone number in the draft is invented. The Ofcom numbering page was not opened on 6 November 2026.

## What a run may read

One enquiry, the as-of date, a channel identity object, a separate review object, closed structured fields, the synthetic catalogue, and the pinned sources. Free text is passed to Experiment 08 `propose()`. The redacted text is not copied into the draft. `release()` is not called. A financial-services complaint or vulnerability phrase is passed to Experiment 02 `analyse()`. Evidence quotes are not copied. The DISP clock is not calculated. The Python starter does not persist the enquiry. A record that is not marked synthetic is refused, and the refusal does not echo the text.

## What it must not read

Dynamics 365 and other production customer records, identity systems, password stores, payment systems, tariff and contract systems, mailboxes, live knowledge bases, and other customers' enquiries.

## Human approval

| Decision | Who |
| --- | --- |
| Confirm an address-update draft | The signed-in customer who is the subject of the account. Confirmation does not change the record. |
| Confirm an appointment-request draft | That same person, and only when the date, slot, and place are on the closed list. The appointment is not booked. |
| Approve a correspondence draft for the handler's own channel | A handler, after the customer confirmation, with recipient role `account-holder`. The agent does not send. |
| Reset a password, take a payment, close a complaint, or change a tariff or contract | A handler, outside the agent. A customer confirmation is refused. |
| Take a vulnerability, emergency, complaint, unverified, or third-party handover | A handler. |
| Rely on a page after it is marked stale | A handler, after someone re-opens the organisation's own page. |
| Write the account or send a message | The person authorised for that action. Outside the agent. |

Reading a published page that does not change the account, and re-running the same enquiry, do not need a separate approval. A person is still offered.

## Identity

A passed check is a field the channel supplies. It is honoured only when `method` is `portal_session`, `checked_by` is `channel`, `result` is `passed`, the customer is signed in, the channel is the portal, the check's date is the as-of date, and the customer and the subject are the same synthetic account reference. Web chat, phone, and email cannot carry it. A sentence in the enquiry cannot carry it. A passed session does not authorise a password reset or a record change. This starter does not call Microsoft Entra and does not describe a customer sign-in product.

## UK GDPR, Consumer Duty, Ofgem, and the Equality Act

No lawful basis is asserted. Article 5 was read on 6 November 2026, including Article 5(3). Article 6 and Article 9 were not opened. Articles 22A to 22D were read via Article 22A and Data (Use and Access) Act 2025 section 80. S.I. 2026/82 and Article 22D regulations were not opened. This note is not a DPIA.

PRIN 2A.1 was read for a financial-services complaint or vulnerability phrase. PRIN 2A.2 was not quoted. DISP was not re-opened. No breach is found and no customer is labelled vulnerable.

The Ofgem and Energy Ombudsman blog of 5 February 2026 was read for the energy-retail scenario. It is not treated as a verified licence condition. Fairness monitoring has not been done.

Equality Act 2010 sections 20, 29, and 149 were read. Another format is offered through a person. No duty is treated as met. Section 149 is noted only for `public_service`.

## Prompt injection, stale data, prohibited actions

Fixtures include instructions to ignore the rules, close a complaint now, and send now. The checker records them and does not follow them. `tests/test_reply.py` and `eval/synthetic_dataset.json` cover that. Older than 180 days is stale. Equal to 180 is not. The legacy tariff body is not in the JSON.

## Tenant controls named and not configured here

These product pages were not opened on 6 November 2026. Treat current names, licence requirements, and behaviour as unverified in this folder:

- Microsoft Entra Agent ID, and Conditional Access for agents
- Power Platform DLP, beyond the instruction in the flow note to block a later connector
- Microsoft Foundry prompt shields
- Key Vault
- Microsoft Purview
- Application Insights
- Copilot inside Dynamics 365 Customer Service

A production deployment should still plan for them: an agent identity rather than a shared user account, a Conditional Access policy on that identity, a DLP policy that blocks mail, payment, and account-system connectors, a secret in Key Vault if a later API needs one, a Purview boundary the organisation already uses, and an Application Insights workspace that does not store the enquiry text. None of those objects is created here.

## Logging and kill switch

This starter writes no log. Before live use, log who ran it, the enquiry id rather than the words, the as-of date, whether identity was trusted, whether a page was stale, the Experiment 08 finding count and input hash, and the later review. Do not put the enquiry text, or a raw identifier, in an application trace.

Turn the Copilot Studio agent off. Remove any Foundry access. Block a later connector in a Power Platform DLP policy.

## Review

6 November 2026. Next review 6 May 2027, and sooner if the catalogue, Article 5, Articles 22A to 22D, the Ofgem blog, PRIN 2A.1, or the Equality Act sections cited here change.
