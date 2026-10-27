# Security and permissions

Employment Rights Act 2025 HR assistant, Experiment 11. Catalogue ID UK03.

This note matches `agent-manifest.yaml`. If the two disagree, the manifest is the control. It is written for an employer deciding whether to try the starter, not as a completed DPIA.

## Purpose

The agent reads one pack and returns a draft against the pinned commencement catalogue. Autonomy is A1. An HR lead decides what the draft means. The agent cannot execute that decision.

## What the agent cannot do

These are disabled in the manifest, not merely discouraged in the prompt.

- Decide that the employer took, or failed to take, reasonable steps or all reasonable steps.
- Decide that harassment occurred, or that a third party was permitted to harass an employee.
- Make a disciplinary decision, issue a warning, suspend, or dismiss.
- Decide that a disclosure was protected, or that a dismissal was fair.
- Calculate a tribunal time limit.
- Apply the six-month qualifying period to a person.
- Publish a policy or change a handbook.
- Write a personnel, grievance, or case record, including a training attestation.
- Send a message to a worker, Acas, a tribunal, a union, or the Equality and Human Rights Commission.
- Refresh citations from the web. URLs come from `src/sources.py`.
- State Northern Ireland employment law.

There is no tool whose side effect is any of the above. `tests/test_review.py`, `tests/test_injection.py`, and `tests/test_qa.py` check that an instruction inside a pack does not become an action.

## Data

**Read, in this starter.** The one pack the HR lead supplies. The as-of date and the stale thresholds. The static catalogue.

**Not read.** The HR system, payroll, personnel files, grievance and disciplinary systems, mailboxes, Teams chats, the Acas helpline, tribunal systems, and a named worker's start date.

The manifest does **not** assert a UK GDPR lawful basis. A candidate for the employer to confirm is Article 6(1)(c), legal obligation, for the preventative duty, or Article 6(1)(f) for an internal draft. Do not copy a public-task basis from Experiment 01. Article 9 is not asserted. A live sexual-harassment report may be special-category data. This starter refuses a pack that is not marked synthetic, and it refuses a report that is not marked anonymised. The refusal does not echo the narrative.

The Python starter does not persist the pack. Production inference, if used, should run in Microsoft Foundry in UK South or UK West. Confirm the data-use terms at deployment.

Samples use Northwharf Community Kitchen CIC, an invented organisation, and role labels such as "Worker A". They are not real people.

## Prompt injection and stale data

Narratives, questions, excerpt text, and the employer name are untrusted. The scanner records an instruction to ignore the rules, dismiss or suspend a worker, email someone, update a personnel record, publish a policy, mark the employer compliant, or contact Acas. It does not follow the instruction. A payload key that purports to set the HR decision, a risk rating, or a send is stripped.

A question that asks for a claim, a disciplinary outcome, a time limit, or a compliance conclusion is refused. The handbook is quoted only from an excerpt the policy owner has already approved, on a topic the HR lead supplied. The core does not guess the topic from the words.

The stale-data test compares `last_verified` (27 October 2026 in this catalogue) with the as-of date. Older than the threshold, default 90 days, is stale. Equal to the threshold is not. A stale source is not relied on. The in-force flag is still computed, so a stale pin is not pretended to be a change in the law. The checker does not download the page.

A policy review date older than 365 days is stale. Equal to 365 is not. A stale policy is not a breach.

The residual risk is a misleading brief if a model is later wrapped around the JSON. The HR lead is the control. There is no autonomous action behind a bad draft.

## Human approval

Autonomy A1 means a person decides. The agent still has no tool that carries the decision out. Approving a sentence in the chat does not publish a policy or decide a case.

| Decision | Who |
|---|---|
| Treat the draft as the employer's assessment | HR lead |
| Publish or change a policy | HR lead |
| Complete the risk-assessment ratings | HR lead |
| Act on a confidential triage summary | Named HR role |
| Reply to a worker | HR lead or the policy owner |
| Rely on a stale source | HR lead, after someone re-opens the page |
| Rely on a stale policy excerpt | Policy owner |
| Discipline, suspend, or dismiss | A person under the employer's own process. Outside the agent. |
| Contact Acas, a tribunal, a union, or the worker | HR lead. Outside the agent. |

Viewing a draft and re-running it do not need a separate approval.

## Controls a tenant would discuss

Named here, and not configured in this repository. Product pages for these controls were not opened on 27 October 2026, except the Copilot Studio harness overview cited in the harness notes. Treat detailed behaviour as unverified.

| Control | How an employer might use it |
|---|---|
| Entra Agent ID | An identity for the agent, separate from the HR lead, with no mail or HR-system role. |
| Conditional Access | Limit who can open the agent, and from where. |
| Power Platform DLP | Block connectors for mail, Teams send, and HR-system writes. This starter has no such connector. |
| Microsoft Foundry prompt shields | On, if a model sees the pack. Not a substitute for the missing decision tool. |
| Key Vault | Any later secret for a Foundry deployment. The checklist has no secret. |
| Purview | A sensitivity label on a draft the HR lead chooses to save. The starter does not apply one. |
| Application Insights | Invocation logs without the incident narrative. Not wired up here. |

Experiment 01 records Dynamic Permissions, Dynamic Agent Risk, and Dynamic Conditional Access as announced, with availability unverified. This folder did not re-check that announcement.

## Risk register

Assessed 27 October 2026 for this starter rather than a named employer. Residual risk is not all Low. The rows match the manifest.

| ID | Risk | Residual | Owner in the manifest |
|---|---|---|---|
| R1 | Missing evidence is treated as a breach, or a complete pack is treated as proof of all reasonable steps | Medium | People and culture |
| R2 | Sections 20 to 22 are described as in force before 30 October 2026, or a timetable date is treated as commenced | Low | People and culture |
| R3 | The draft is used as a disciplinary decision or a dismissal | Low | People and culture |
| R4 | Prompt injection publishes a policy, writes a record, or emails a worker or Acas | Low | Information security |
| R5 | A live harassment report is pasted into a shared test run | Medium | Data protection officer |
| R6 | A pinned page changes and the checklist is still treated as current | Medium | People and culture |

## Logging

This starter writes no log. Before live use, log who ran it, the pack reference rather than the narrative, the as-of date, whether a source was stale, and the HR lead's later decision. Do not log the note text in an application trace.

## Kill switch

Turn the Copilot Studio agent off. Remove any Foundry access, using Key Vault or the role assignment if one was created. Block a later connector in a Power Platform DLP policy.

Contacts in the manifest use `example.com`. They are placeholders.

## Review

27 October 2026. Next review 27 April 2027, and sooner if a commencement instrument, a section 40B regulation, or the Acas page used here changes.

There is no ATRS mapping. ATRS is a public-sector standard. An employer does not complete an ATRS record by using this starter. Experiment 03 can draft an assurance pack. This experiment does not. A charity or a council that is a public body would still make its own decision about ATRS. This folder does not make it.
