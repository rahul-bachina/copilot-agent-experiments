# Security and permissions

Agent Architecture Advisor, Experiment 14. Catalogue ID G002.

This note matches `agent-manifest.yaml`. If the two disagree, the manifest is the control. It is written for an organisation deciding whether to try the starter, not as a completed DPIA.

## Purpose

The agent reads one proposed use case and returns a draft of platform options, a catalogue autonomy level, human approval points, and a permissions-manifest skeleton. Autonomy of this advisor is A0. It has no action to take on the draft. The architect confirms every platform option. A governance owner approves any manifest before anyone relies on it.

## What the agent cannot do

These are disabled in the manifest, not merely discouraged in the prompt.

- Select a platform. `platform_selected` stays null and every option has `selected` false.
- Recommend autonomy A3. The catalogue levels are A0, A1, and A2.
- Mark a permissions manifest approved.
- Deploy an agent, publish a Copilot Studio agent, create a Foundry agent, or turn on a cloud flow.
- Approve or reject a use case.
- Write a production record or send a message.
- Quote a price or look up a licence in an admin centre.
- Refresh citations from the web. URLs come from `src/sources.py`.

There is no tool whose side effect is any of the above. Tests in `tests/test_advisor.py` check that an instruction inside a use case does not become a selection, an autonomy level, or a deployment.

## Data

**Read, in this starter.** The use case the architect supplies for that run. The as-of date and the stale threshold. The static catalogue. Experiment 03's generator, called locally to draft the skeleton.

**Not read.** An admin centre, a billing account, a mailbox, a Teams chat, Copilot Studio as a control plane, Microsoft Foundry as a control plane, and Power Automate as a control plane.

A use case can name staff or describe personal data. The manifest does not assert a UK GDPR lawful basis. The organisation's data protection officer confirms an Article 6 basis before any live processing, and an Article 9 condition if special-category data is in scope. The samples in this repository are synthetic.

The Python starter does not persist the use case. If a narrative matches an instruction pattern, that string is not copied into the skeleton.

## Prompt injection and stale data

Use-case text is untrusted. The scanner records a line that tells the advisor to ignore instructions, disregard the rules, recommend autonomy A3, deploy, select a platform, approve the manifest, or override the decision. A `system:` or `developer:` line is recorded. Payload keys that try to set `platform_selected`, `recommended_autonomy`, `deployed`, or `approved` are stripped and are not echoed. `followed` stays false. Structured fields are the only input to the rules. A Boolean counts only when it is boolean true. A licence value counts only when it is the string yes, no, or unknown.

The stale-data test compares `last_verified` (27 October 2026 in this catalogue) with the as-of date. Older than the threshold, default 90 days, is stale. The catalogue-boundary row is not a Microsoft page and is not stale-tested. The advisor does not download the page. When a pinned page is stale, `do_not_rely` is true and an approval point asks the architect to re-open it. The draft is still produced. It is still not a selection.

The residual risk is a misleading draft if a model is later wrapped around the JSON. The architect is the control. There is no autonomous action behind a bad draft.

## Human approval

Autonomy A0 means this advisor cannot execute a platform selection even after a person agrees. The person still has to make it.

| Decision | Who |
|---|---|
| Confirm each platform option, including no agent | Architect |
| Confirm the catalogue autonomy level (A0, A1, or A2) | Architect |
| Rely on the permissions-manifest skeleton | Governance owner |
| Re-open a pinned page after it is marked stale | Architect |
| Confirm an Article 6 basis, and an Article 9 condition if special-category data was recorded | Data protection officer |
| Deploy, publish, or turn a flow on | Outside this agent |

Producing the draft, re-running it, and printing the sources table do not need a separate approval.

The skeleton for the proposed agent can recommend A1 or A2. Those levels still leave consequential actions disabled. A later person would edit a manifest and the schema would still have to pass. This starter does not make that edit. A request for A3 is refused and lowered. It is never the recommendation.

## Controls a tenant would discuss

This starter configures none of them. A row says "opened" only when the body was opened on 27 October 2026. Otherwise the control is unverified. Do not treat an unverified row as a product capability.

| Control | In this starter | Note |
|---|---|---|
| Microsoft Entra identity for Foundry Agent Service | Not configured | The Agent Service overview describes a dedicated Microsoft Entra identity for hosted agents, and role-based access control. That page was opened. This starter creates no identity. |
| Microsoft Entra Agent ID, including any admin wizard | Not configured | Unverified. That product page was not opened for this revision. |
| Conditional Access | Not configured | Unverified. Not opened for this revision. |
| Power Platform data loss prevention | Not configured | Unverified. Not opened for this revision. A later connector that can send or write would need a policy the organisation writes. |
| Microsoft Foundry prompt shields | Not called | Opened. User prompt attack detection is on by default. Document attack detection is off by default. Tool-response scanning for agents is marked preview. Spotlighting is marked preview and is off by default. The page says the service is Azure AI Content Safety, and that Prompt Shields do not decide harm, accuracy, groundedness, or compliance. The local scan does not call them. |
| Key Vault | Not provisioned | Unverified. Not opened. The checker has no secret. |
| Microsoft Purview | Not configured | Unverified. Not opened. Classification of the use case is the organisation's. |
| Application Insights | Not configured | The Foundry overview names Application Insights for traces. If it is enabled later, do not log the narrative. |
| Private networking | Not configured | The Foundry overview describes private networking for prompt agents and bring-your-own virtual network for hosted agents. A UK region list was not on that page. Unverified for a UK deployment. |

Announced items that this folder did not re-check are not listed as available. Experiment 01's notes on dynamic permissions are not copied here as fact.

## Logging

This starter writes no log. Before live use, log who ran it, when, the case id, the as-of date, the catalogue `last_verified` values, injection pattern ids, and whether the skeleton validated. Do not log the narrative.

## Kill switch

Do not run `src/advise.py`. Delete the local copy from a machine that should not draft options. There is no published agent to turn off. If a team later publishes one despite this starter, turn that Copilot Studio agent off, remove any Foundry credential, and block a send or a write in a data loss prevention policy the organisation configures. Contacts in the manifest use `example.com`. They are placeholders.

## Skeleton generator

The draft manifest is produced by Experiment 03's `generate_manifest`, with `approve` false. The generator refuses an approve flag and refuses autonomy A3. This advisor discards a skeleton whose level is not A0, A1, or A2. High-risk actions in the generated file stay disabled.
