# Security and permissions

Council contact-centre front door, Experiment 13. Catalogue ID V006.

This note matches `agent-manifest.yaml`. If the two disagree, the manifest is the control. It is written for a council deciding whether to try the starter, not as a completed DPIA or an ATRS record.

## Purpose

The agent reads one enquiry and returns a draft from a fixed catalogue, or a handover. Autonomy is A1. An adviser accepts a published sentence or takes the handover. The agent cannot execute a service decision.

## What the agent cannot do

These are disabled in the manifest, not merely discouraged in the prompt.

- Decide eligibility, entitlement, or an application.
- Look up an account, a balance, or a case.
- Create, update, or close a case or a service request.
- Send an email, an SMS, a letter, or a chat message.
- Book an appointment.
- Take or refund a payment.
- Issue, cancel, or waive a penalty charge.
- Call 999, or open a safeguarding record.
- Quote a stale page, or refresh a page from the web.
- Accept its own draft. `human_approval` stays null until `record_adviser_review` receives a separate review object, and even then nothing is sent.

There is no tool whose side effect is any of the above. `tests/test_front_door.py` and `tests/test_injection.py` check that an instruction inside an enquiry does not become an action.

## Data

**Read, in this starter.** The one enquiry the adviser supplies. The as-of date and the stale threshold. The synthetic catalogue. The static source list.

**Not read.** Case systems, payment systems, enforcement systems, resident contact directories, live council websites, and other residents' enquiries.

The enquiry may contain personal data, and a resident may volunteer health, disability, or safeguarding information. That can be special-category data. The manifest does **not** assert a UK GDPR lawful basis. A candidate for the data protection officer to confirm, before any production use, is Article 6(1)(e), public task. Do not copy the legal-obligation basis from Experiment 02. No Article 9 condition is asserted. The output does not echo the enquiry. The Python starter does not persist it.

A production deployment that might receive that text needs the council's own DPIA. This note is not one.

Samples use Northmarsh Borough Council, which is invented, and pages on `northmarsh.example.gov.uk`.

Production inference, if used, should run in Microsoft Foundry in UK South or UK West. Confirm the data-use terms at deployment.

## Prompt injection and stale data

Enquiry text, the enquiry id, and the channel label are untrusted. The scanner records an instruction to ignore the rules, mark someone eligible, create a case, send an email, or override a stale flag. `followed` is false. A sentence that is only an instruction is not used to choose a page. A payload key that purports to set the decision is stripped.

The stale-data test compares `last_reviewed` and `last_verified` with the as-of date. Older than the threshold, default 180 days, is stale. Equal to the threshold is not. A stale page's body is not copied into the JSON. The checker does not download the page.

The residual risk is a misleading brief if a model is later wrapped around the JSON. The adviser is the control. There is no autonomous action behind a bad draft. The vulnerability list is short. A phrase that is not on it is not detected. Absence of a flag is not a finding that someone is safe.

## Human approval

Autonomy A1 means a person decides. The agent still has no tool that carries a service action out. Approving a sentence in the chat does not send it.

| Decision | Who |
|---|---|
| Accept a published page as fit to read out | Contact centre adviser |
| Take the handover for a vulnerable resident or an emergency | Contact centre adviser |
| Rely on a page after it is marked stale | Contact centre adviser, after someone re-opens the council's own page |
| Decide eligibility or an application | The officer who owns that decision. Outside the agent. |
| Create or update a case | Contact centre adviser, in the council's own system. Outside the agent. |
| Send a message | Contact centre adviser, in the council's own channel. Outside the agent. |
| Take a payment, book, or enforce | The officer authorised for that action. Outside the agent. |

Viewing a draft and re-running it do not need a separate approval. `accept_draft` is refused unless the outcome is a current published answer. Emergency and vulnerability drafts accept only `take_handover`.

## UK GDPR

Article 6(1)(e) is a candidate, not a decision. Special-category data may appear because the resident typed it. The starter does not ask for it and does not store it. Data subject rights are handled by the council, not by this agent.

This agent does not make a significant decision solely by automated means. Experiment 03 screens the Data (Use and Access) Act 2025 safeguards in section 80. That section was not re-opened for this experiment on 27 October 2026. This agent does not run the screen.

## ATRS

The scope policy opened on 27 October 2026 puts the mandatory duty on central government and recommends the standard for the broader public sector. A tool that directly interacts with the public is in the class that policy describes. This starter is an adviser-side draft. It does not itself talk to residents, it does not decide that a council is in mandatory scope, and it does not submit a record.

The `atrs_mapping` block in the manifest points at sections a drafter would read. Experiment 03 can draft a pack. It does not approve or submit one.

If a council later publishes a resident-facing chat, AI Playbook Principle 7, opened on the same day, asks for a clear automated-response line. The JSON field `ai_disclosure` uses the playbook's example shape: the response was written by an automated AI chatbot. Principle 4 says that where a chatbot cannot be reviewed in real time, human control has to sit at other stages. This starter keeps the adviser in the loop before a sentence is treated as fit to read out. That is not a claim that a future unattended chat would meet Principle 4.

## Accessibility

SI 2018/952, opened on 27 October 2026, requires a public-sector website or mobile application to meet the accessibility requirement and to publish an accessibility statement. This command-line starter is not that website. A Copilot Studio chat published on a council site would need the council's own assessment. Phone and face-to-face routes stay. This agent must not be the only way to make contact.

## Controls a tenant would discuss

Named here, and not configured in this repository. Product pages for these controls were not opened on 27 October 2026, except the Copilot Studio harness overview cited in the harness notes. Treat detailed behaviour as unverified.

| Control | How a council might use it |
|---|---|
| Entra Agent ID | An identity for the agent, separate from the adviser, with no case-write or mail role. |
| Conditional Access | Limit who can open the agent, and from where. |
| Power Platform DLP | Block connectors for mail, SMS, case writes, and payments. This starter has no such connector. |
| Microsoft Foundry prompt shields | On, if a model sees the enquiry. Not a substitute for the missing send tool. |
| Key Vault | Any later secret for a Foundry deployment. The front door has no secret. |
| Purview | A sensitivity label on a draft the adviser chooses to save. The starter does not apply one. |
| Application Insights | Invocation logs without the enquiry narrative. Not wired up here. |

Experiment 01 records Dynamic Permissions, Dynamic Agent Risk, and Dynamic Conditional Access as announced, with availability unverified. This folder did not re-check that announcement.

## Risk register

The scores are in the manifest. They are a starter view, not a council's risk assessment. The ones to read first are a guessed fact treated as an answer (R1), an emergency answered with a service page (R2), injection that tries to send or decide (R4), live text pasted into a test (R5), and the agent becoming the only route (R6).

## Kill switch

Turn the Copilot Studio agent off. Remove any Foundry credential. Use DLP to block a connector someone adds later. Contacts in the manifest are placeholders on `northmarsh.example.gov.uk`.
