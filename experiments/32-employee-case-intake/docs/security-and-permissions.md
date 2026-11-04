# Security and permissions

Employee case intake, Experiment 32. Catalogue ID H009.

This note matches `agent-manifest.yaml`. If the two disagree, the manifest is the control. It is written for an employer or a public body deciding whether to try the starter, not as a completed DPIA.

## Purpose

The agent reads one synthetic or officer-supplied case and returns a proposed category, an urgency flag, a statutory or Acas time reference, and a proposed route. It calls Experiment 15, and Experiment 12 when attachments are supplied. Both of those call Experiment 08. Autonomy is A1. An HR officer confirms the classification and the routing. The agent cannot execute that step. It cannot decide an outcome, advise on merits, contact the employee or a manager, or write to an HR system.

## What the agent cannot do

These are disabled in the manifest, not merely discouraged in the prompt.

- Confirm the classification or the routing.
- Decide an outcome, or advise on the merits.
- Decide that Equality Act 2010 section 26 is met, or that a disclosure is protected.
- Contact the employee, a line manager, the subject of a disclosure, Acas, a tribunal, or a prescribed person.
- Write a production record, including an HR system, Dataverse, SharePoint, or a mailbox.
- Assert an Article 9 condition, or decide that Schedule 1 paragraph 1 is met.
- Calculate a section 80G last day or a tribunal time limit.
- Release redacted text, or describe the Experiment 08 output as anonymised.
- Re-implement Experiment 15, Experiment 12, or Experiment 08.

There is no tool whose side effect is any of the above. `record_hr_confirmation` updates a copy of the JSON in memory when a test calls it with the role "HR officer". The skills say the agent must not call it. `schema/tools.json` sets `callable_by_agent` to false. After that record, `write_hr_system` still raises `CaseForbidden`. `decide_outcome`, `advise_on_merits`, `contact_employee`, `contact_manager`, `send_external`, `approve_case`, and `reject_case` always raise. `tests/test_prohibited.py`, `tests/test_injection.py`, and `tests/test_draft.py` check that an instruction inside the narrative does not become an action.

## Data

**Read, in this starter.** The one case the HR officer supplies. The as-of date and the optional stale window. The static quotations in `src/case_sources.py`. Experiments 15, 12, and 08, called in-process.

**Not read.** HR case systems, personnel files, payroll, occupational health systems, mailboxes, tribunals, Acas early conciliation, and prescribed-person services.

The narrative may contain special-category data: health, racial or ethnic origin, religious or philosophical belief, trade union membership, or sex life or sexual orientation. A sexual-harassment keyword is not itself a finding that sex-life data is present. Whistleblowing language is not automatically Article 9 data. The manifest does **not** assert a UK GDPR Article 6 basis and does **not** assert an Article 9 condition.

UK GDPR Article 9(1), opened 4 November 2026, prohibits processing of the listed data unless paragraph 1 does not apply. Article 9(2) says paragraph 1 shall not apply if the processing is based on Article 6(1) and one of the conditions applies, including (b) employment. Those "based on Article 6(1)" words were inserted on 20 August 2025. Data Protection Act 2018 section 10(2), opened the same day as this pin, says the Article 9(2)(b) requirement is met only if a condition in Part 1 of Schedule 1 is met. Schedule 1 paragraph 1(1) requires that the processing is necessary for an employment, social security, or social protection obligation or right, and that an appropriate policy document is in place. Paragraph 39 was not opened. This starter decides neither necessity nor the policy document. `schedule_1_paragraph_1_met` stays null.

Article 5(1)(c) data minimisation is why the routing summary is a template and the narrative is not stored. No retention period is set. That is for the controller under Article 5(1)(e).

The Python starter does not persist the narrative. The draft stores a SHA-256, a character count, closed-list hits, and indicator categories. It does not store Experiment 15's matched phrases, Experiment 12's file bodies, or Experiment 08's redacted text. If the narrative is longer than 80 characters and the full narrative appears in the JSON, apart from the hash, `draft_case` raises `CaseForbidden`. A case that is not marked synthetic is refused, and the refusal does not echo the narrative.

Where whistleblowing language is present, `identity_in_routing_summary` and `narrative_in_routing_summary` are false. The summary says not to notify the employee, a line manager, or the subject of the disclosure. Section 43J is quoted when the Great Britain sources apply. The draft does not decide that a confidentiality clause is void, because it does not decide that the disclosure is protected.

Samples use fictional workplaces and synthetic worker labels. National Insurance values, where a fixture includes one, are the non-allocatable fixtures documented in Experiment 08. No real person is in the repository.

Production inference, if a team adds it later, should run in UK South or UK West and should see only text already returned by Experiment 08. Confirm the data-use terms at deployment. This folder does not create that resource.

## Prompt injection and stale data

Fixtures include instructions to ignore previous instructions, force a category, contact the employee or a manager, write to the HR system, decide that a grievance is unfounded, or disregard the pinned sources. The checker records them and does not follow them. `followed` is false. Instruction sentences are blanked before keywords are counted, so a genuine category word earlier in the line can still count. Prohibited payload keys are stripped before classification.

Sources are pinned on 4 November 2026. A gap of more than 90 days, the default, sets `sources_stale`. A gap of exactly 90 days does not. A sentence in the narrative does not clear the flag. The test helper will not record confirmation of a stale draft unless the caller passes `acknowledge_stale`. That acknowledgement is a person's argument to the function. It still does not write an HR system, and the agent is not given a tool that passes it.

## Human approval

| Decision | Who |
| --- | --- |
| Confirm the classification | HR officer |
| Confirm the routing | HR officer |
| Rely on stale pinned sources | HR officer, outside the agent |
| Decide an outcome or the merits | HR officer. Disabled here. |
| Contact the employee or a manager | Not this agent. |
| Write to the HR system | Not this agent. |
| Assert an Article 9 condition | Data protection officer. Disabled here. |

Viewing a draft and re-running it do not need a separate approval.

## Risk register

Assessed 4 November 2026 for this starter, not for a named employer. Residual risk is not all Low. The manifest holds the full rows.

| ID | Risk | Residual | Owner in the manifest |
| --- | --- | --- | --- |
| R1 | A keyword is treated as a decision | Medium | HR officer |
| R2 | Special-category detail is copied into a route, a log, or a model prompt | High | Data protection officer |
| R3 | A whistleblowing narrative is notified to the subject or a line manager | Medium | HR officer |
| R4 | An instruction sets the category, clears a stale pin, or causes a write | Medium | HR officer |
| R5 | A quoted period is read as a date this agent calculated | Low | HR officer |

R2 stays High because Experiment 08 does not redact names, email addresses, or telephone numbers, and a later host might log the narrative. This starter does not store the narrative. That does not bind a later host.

## Logging and the kill switch

This starter writes no log. Before live use, log who ran it, the case id, whether an instruction was detected, whether sources were stale, and the proposed category and route. Do not log the narrative. A stored health or whistleblowing sentence may itself be sensitive.

Turn the Copilot Studio agent off. Stop calling `draft_case()`. Remove any Foundry access. Block a later mail or HR connector in a Power Platform DLP policy.

## Tenant controls named and not configured here

Entra Agent ID, Conditional Access, Power Platform DLP, Microsoft Foundry prompt shields, Key Vault, Purview, and Application Insights. The product pages for those controls were not re-opened on 4 November 2026. Portal labels and licence requirements are unverified for this folder. Experiment 06 recorded an earlier reading of Entra Agent ID. This folder does not restate that reading as a fresh check. This starter connects none of these controls.

## Review

4 November 2026. Next review 4 May 2027, and sooner if the Acas Code is replaced, if section 80G's newer refusal test is fully in force, or if a deployment connects a mailbox, an HR system, or a model.

There is no ATRS mapping. A public body that used this pattern would consider the Algorithmic Transparency Recording Standard separately. This starter does not submit a record.
