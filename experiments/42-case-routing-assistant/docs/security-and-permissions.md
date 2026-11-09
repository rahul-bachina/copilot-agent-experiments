# Security and permissions

This note matches `agent-manifest.yaml`. If the two disagree, the manifest is the control and this note is out of date. It is written for a contact-centre lead, a queue owner, a DPO, and a security lead deciding whether to try the starter. It is not a completed DPIA and it is not an ATRS submission.

`permissions.yaml` is the same file as `agent-manifest.yaml`.

## What this starter reads

One case, the as-of date, a separate review object, the synthetic rules, and the pinned sources. Free text is passed to Experiment 15 `scan()`, which calls Experiment 08. Phrases and redacted text are not copied into the proposal. An Awaab illustration, when the fields are present, is asked of Experiment 05 with officer approval forced off. The Python starter does not persist the case. A record that is not marked synthetic is refused, and the refusal does not echo the text.

## What it does not do

It does not reroute, close, escalate, send, decide entitlement, label a person, or edit a routing rule. Confirmation does not do those things either. A confidence band cannot move a vulnerability or statutory-clock case off a human queue.

## Identity and access products

These product pages were not opened on 9 November 2026. Treat the names as unverified here:

- Microsoft Entra Agent ID
- Conditional Access for agents
- Power Platform DLP as a configured policy
- Microsoft Foundry prompt shields
- Key Vault
- Microsoft Purview
- Application Insights

None of those objects is created in this folder.

**Microsoft Entra Agent ID and Conditional Access.** Other experiments in this repository have described Conditional Access for agent identities. This experiment did not re-open that page. This starter does not register an agent identity. A passed sign-in is not an input. The adviser is the person who already has the case.

**Power Platform DLP.** If a connector to a case system, a mailbox, or a dialler is added later, a DLP policy is the place to block it. No such connector is in this folder. A policy was not configured here.

**Microsoft Foundry prompt shields.** See [foundry.md](foundry.md). The tests are the control on the deterministic core. A filter is not a substitute for having no reroute tool.

**Key Vault.** This starter has no secret. A later Foundry key should sit in a vault the organisation already runs. That wiring is unverified here.

**Microsoft Purview.** Sensitivity labels and audit of prompts were not configured. An organisation that already uses Purview should decide whether prompts and outputs are in scope. This starter does not claim an audit schema.

**Application Insights.** This starter writes no trace. Do not put the case text in an application trace if one is added later.

## Logging

This starter writes no log. Before live use, log who ran it, the case id rather than the words, the as-of date, the outcome, the queue id, the confidence band, whether a rule was stale, the Experiment 15 category ids and finding count, and the later review. Do not log phrases or raw identifiers.

## Kill switch

Turn the Copilot Studio agent off, revoke any Foundry credential, and block a later case-system connector with DLP. Times are the platform's, not a measured drill. Contacts on `northmere.example.gov.uk` are placeholders.

## Automated decisions

Section 80 of the Data (Use and Access) Act 2025 and Articles 22A to 22C were read on 9 November 2026. This starter does not take a significant decision and does not move a queue. Regulations under Article 22D were not opened. A deployment that later writes a queue needs the controller's own assessment. This note is not that assessment.

## Equality

Sections 19, 29, and 149 were read on 9 November 2026. A protected characteristic is not used as a routing feature. Section 149 due regard is not carried out here. Section 20 was not opened. No duty is marked as met.

Reviewed for this starter on 9 November 2026. Next review 9 May 2027, and sooner if section 80, Article 12A, section 10, or regulation 5 changes.
