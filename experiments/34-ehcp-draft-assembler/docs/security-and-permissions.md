# Security and permissions

EHCP Draft Assembler, Experiment 34. Catalogue ID UK10.

This note matches `agent-manifest.yaml`. `permissions.yaml` is the same file. If the note and the manifest disagree, the manifest is the control. It is written for a local authority deciding whether to try the starter, not as a completed DPIA and not as a SEND decision.

## Purpose

The agent reads one synthetic advice bundle and returns a draft under the regulation 12 headings, with citations, gaps, conflicts, and unsupported statements. Autonomy is A1. The caseworker authors the final education, health and care plan. A local copy can be included only after the sign-off gate. Nothing is sent.

## What the agent cannot do

These are disabled in the manifest, not merely discouraged in the prompt.

- Decide needs, provision, placement, or outcomes.
- Edit the final plan or write the final text.
- Send the draft to a parent, a young person, a school, or a local authority system.
- Secure provision under Children and Families Act 2014 s.42.
- Fill section I. Quotes tagged I are withheld.
- Mark the output anonymised. `output_is_anonymised` stays false.
- Recommend autonomy A3. The catalogue levels are A0, A1, and A2. This draft stays at A1.
- Read a live case system, a mailbox, or a Microsoft Foundry resource.
- Refresh citations from the web. URLs come from `src/sources.py`.

There is no tool whose side effect is a decision or a send. `schema/tools.json` marks those tools as not callable. The local export tool is not callable by the agent. Tests in `tests/test_injection.py` and `tests/test_prohibited.py` check that fixture text and command flags do not become a decision or a send.

## Data

**Read, in this starter.** The advice bundle for that run. The as-of date and the stale threshold. The static source list. A sign-off object only when a local export is requested, and that object is not stored.

**Not read.** A live plan, a case-management system, a mailbox, a parent portal, a school system, Copilot Studio as a control plane, Microsoft Foundry as a control plane, and Azure as a control plane.

The samples in this repository are synthetic. Northfen Borough Council is fictional. Child A is not a real child. The child reference is the words "Child" and one letter. A forbidden identity field refuses the bundle and the value is not copied.

The manifest does not assert a UK GDPR lawful basis. Health text in advice would be special category data under Article 9. No Article 9(2) condition is claimed. Article 8 was opened on 4 November 2026. It applies where Article 6(1)(a) consent is the basis for an information society service offered directly to a child. This starter does not offer a service to a child. The ICO Children's code page returned 403 and was not opened. Scope is for the data protection officer.

The Python starter does not persist the files. A sentence that matches an instruction pattern is not copied into a section.

## Prompt injection and stale data

The assembler reads untrusted advice. The scanner records a sentence that tells it to ignore instructions, decide needs or placement, send, export, or edit the final plan. A sentence that already refuses the action, including "do not" and "must not", is not treated as an instruction. Payload keys that try to set the control flags are stripped and are not echoed. `followed` stays false.

A sign-off buried in a report does not pass the gate. The gate reads only the separate sign-off argument, and only when export was requested.

A paraphrase can be missed. A negation in the same sentence can hide an instruction. Residual risk R2 in the manifest is Low for the sentences the tests name. A missed paraphrase does not grant a tool the agent does not have.

The stale-data test compares each report date, and `last_verified` on the pages that were opened (4 November 2026), with the as-of date. Older than the threshold, default 90 days, is stale. The 90-day window is not a statutory expiry. The catalogue-boundary row and the ICO row are not stale-tested. The runner does not download the page. When a pin or a report is stale, `do_not_rely` is true. The draft is still produced. It is still not a plan.

## Human approval

Autonomy A1 means the caseworker authors the final text. The agent can show the filing. It cannot record that the caseworker accepted a need, a provision, a placement, or an outcome.

| Decision | Who |
|---|---|
| Author the final plan, including needs, provision, placement, and outcomes | Caseworker |
| Resolve conflicts and gaps | Caseworker |
| Check headings against the local authority template | Caseworker |
| Sign off before a local export copy | Caseworker |
| Re-open stale advice or a stale pinned page before relying on it | Caseworker |
| Send the plan to a parent, a school, or the local authority system | Caseworker, outside this agent |
| Confirm an Article 6 basis and any Article 9(2) condition before any live file | Data protection officer |
| Decide whether the Children's code applies to a later portal | Data protection officer. The page was not opened. Unverified. |

Producing the draft does not need a separate approval. Including a local copy does. The gate is deterministic. The string "true" fails. The signed-on date must equal the as-of date. That date rule is this starter's gate, not a statutory rule.

Assumption ids in the manifest are AS1 to AS6. None of them is autonomy level A3.

## Controls a tenant would discuss

This starter configures none of them. A row says "opened" only when the body was opened on 4 November 2026 for this experiment. Otherwise the control is unverified. Do not treat an unverified row as a product capability.

| Control | In this starter | Note |
|---|---|---|
| Microsoft Foundry prompt shields | Not called | Unverified. The page was not opened for this experiment. The local scan is not a shield result. |
| Microsoft Entra Agent ID | Not configured | Unverified. Not opened for this experiment. |
| Conditional Access | Not configured | Unverified. Not opened for this experiment. |
| Power Platform data loss prevention | Not configured | Unverified. Not opened for this experiment. A later connector that can send or write a case would need a policy the organisation writes. |
| Key Vault | Not provisioned | Unverified. Not opened. The draft has no secret. |
| Microsoft Purview | Not configured | Unverified. Not opened. Classification of any later draft is the local authority's. |
| Application Insights | Not configured | Unverified. Not opened. This starter writes no log. |

## Review

Last reviewed 4 November 2026. Next review 4 May 2027, and sooner if a pinned page is re-opened and has changed.
