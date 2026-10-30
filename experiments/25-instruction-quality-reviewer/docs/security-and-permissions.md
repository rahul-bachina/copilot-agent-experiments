# Security and permissions

Instruction Quality Reviewer, Experiment 25. Catalogue ID G003.

This note matches `agent-manifest.yaml`. If the two disagree, the manifest is the control. It is written for an organisation deciding whether to try the starter, not as a completed DPIA.

## Purpose

The agent reads one system prompt, one SKILL.md, or one topic prompt and returns a scored findings report and a proposed diff. Autonomy of this reviewer is A0. It has no action to take on the draft. The agent owner approves prompt changes. A governance owner approves any manifest skeleton before anyone relies on it.

## What the agent cannot do

These are disabled in the manifest, not merely discouraged in the prompt.

- Apply a proposed diff, or edit the instruction file.
- Record that the agent owner has approved a rewrite.
- Deploy an agent, publish a Copilot Studio agent, create a Foundry agent, or turn on a cloud flow.
- Recommend autonomy A3. The catalogue levels are A0, A1, and A2. This reviewer stays at A0.
- Mark a permissions manifest approved.
- Approve or reject a finding as if that were the owner's decision.
- Write a production record or send a message.
- Quote a price or look up a licence in an admin centre.
- Refresh citations from the web. URLs come from `src/sources.py`.
- Select a platform when Experiment 14 is called. `platform_selected` stays null.

There is no tool whose side effect is any of the above. `schema/tools.json` marks `record_owner_approval`, `apply_instruction_diff`, `deploy_agent`, and `send_findings` as not callable. Tests in `tests/test_prohibited.py` and `tests/test_injection.py` check that an instruction inside the file does not become an edit, an approval, or a deployment.

## Data

**Read, in this starter.** The instruction text the agent owner supplies for that run. An optional permissions manifest. An optional structured use case. The as-of date and the stale threshold. The static source list. Experiment 03's generator, called locally when no manifest was parsed. Experiment 14's rule table, called locally when a structured use case was supplied.

**Not read.** An admin centre, a billing account, a mailbox, a Teams chat, Copilot Studio as a control plane, Microsoft Foundry as a control plane, and Power Automate as a control plane.

An instruction file can name staff or describe personal data. The manifest does not assert a UK GDPR lawful basis. The organisation's data protection officer confirms an Article 6 basis before any live processing, and an Article 9 condition if special-category data is in scope. The samples in this repository are synthetic. A few evaluation cases read instruction files already in this repository. Those files are not live tenant prompts.

The Python starter does not persist the instruction text. The proposed diff is returned in the JSON. It is not written back to the file.

## Prompt injection and stale data

Instruction text is untrusted. The scanner records a line that tells the reviewer to ignore instructions, disregard the rules, force a pass, apply a diff, approve a rewrite, deploy, hide a finding, or override the decision. A `system:` or `developer:` line is recorded. A sentence that already refuses the action, including "do not" and "must not", is not treated as an injection. Payload keys that try to set `owner_approved`, `diff_applied`, `deployed`, `score`, or `autonomy_level` are stripped and are not echoed. `followed` stays false.

The checklist treats a negation anywhere in a sentence as a forbid. A human role before "approves" or before a write to the instructions is a checkpoint, not a command. A later clause in the same sentence can hide a command. That limit is documented. Splitting on a full stop keeps a real command in its own sentence.

The stale-data test compares `last_verified` (27 October 2026 for the Microsoft pages, stored by Experiment 14) with the as-of date. Older than the threshold, default 90 days, is stale. The catalogue-boundary row is not a Microsoft page and is not stale-tested. A document with no review date, or a review date older than the threshold, is stale. The reviewer does not download the page and does not rewrite the review date. When a pin or a document is stale, `do_not_rely` is true and an approval point asks the agent owner to re-open it. The draft is still produced. It is still not an applied change. `reopened_for_this_experiment` stays false.

The residual risk is a misleading draft if a model is later wrapped around the JSON. The agent owner is the control. There is no autonomous action behind a bad draft.

## Human approval

Autonomy A0 means this reviewer cannot edit a prompt even after a person agrees. The person still has to make the edit.

| Decision | Who |
|---|---|
| Approve prompt changes | Agent owner |
| Accept or reject each finding before a rewrite is kept | Agent owner |
| Rely on a manifest skeleton drafted because none was supplied | Governance owner |
| Re-open a pinned page, or a review date, before relying on a citation | Agent owner |
| Confirm an Article 6 basis, and an Article 9 condition if special-category data was recorded | Data protection officer |
| Deploy, publish, or turn a flow on | Outside this agent |

Producing the draft, re-running it, and printing the sources table do not need a separate approval.

The skeleton for a missing manifest asks for A0. A request in the instructions for A3 is refused. It is never the recommendation. `a3_recommended` stays false.

## Controls a tenant would discuss

This starter configures none of them. A row says "opened" only when the body was opened on 27 October 2026 by Experiment 14. Experiment 25 did not re-open the pages. Otherwise the control is unverified. Do not treat an unverified row as a product capability.

| Control | In this starter | Note |
|---|---|---|
| Microsoft Entra identity for Foundry Agent Service | Not configured | The Agent Service overview describes a dedicated Microsoft Entra identity for hosted agents, and role-based access control. That page was opened by Experiment 14. This starter creates no identity. |
| Microsoft Entra Agent ID, including any admin wizard | Not configured | Unverified. That product page was not opened for this revision. |
| Conditional Access | Not configured | Unverified. Not opened for this revision. |
| Power Platform data loss prevention | Not configured | Unverified. Not opened for this revision. A later connector that can send or write would need a policy the organisation writes. |
| Microsoft Foundry prompt shields | Not called | Opened by Experiment 14. User prompt attack detection is on by default. Document attack detection is off by default. Tool-response scanning for agents is marked preview. Spotlighting is marked preview and is off by default. The page says the service is Azure AI Content Safety, and that Prompt Shields do not decide harm, accuracy, groundedness, or compliance. The local scan does not call them. |
| Key Vault | Not provisioned | Unverified. Not opened. The checker has no secret. |
| Microsoft Purview | Not configured | Unverified. Not opened. Classification of the instruction file is the organisation's. |
| Application Insights | Not configured | The Foundry overview names Application Insights for traces. If it is enabled later, do not log the instruction text. |
| Private networking | Not configured | The Foundry overview describes private networking for prompt agents and bring-your-own virtual network for hosted agents. A UK region list was not on that page. Unverified for a UK deployment. |

Announced items that this folder did not re-check are not listed as available. Experiment 01's notes on dynamic permissions are not copied here as fact.

## Logging

This starter writes no log. Before live use, log who ran it, when, the bundle id, the as-of date, the catalogue `last_verified` values, injection pattern ids, and whether a skeleton was drafted. Do not log the instruction text.

## Kill switch

Do not run `src/review.py`. Delete the local copy from a machine that should not draft findings. There is no published agent to turn off. If a team later publishes one despite this starter, turn that Copilot Studio agent off, remove any Foundry credential, and block a send or a write in a data loss prevention policy the organisation configures. Contacts in the manifest use `example.com`. They are placeholders.

## Skeleton generator

When no manifest was parsed, a draft manifest is requested from Experiment 03's `generate_manifest`, with `approve` false, and only if PyYAML and jsonschema import. The generator refuses an approve flag and refuses autonomy A3. This reviewer discards a skeleton whose level is not A0. High-risk actions in the generated file stay disabled. A clean install of this experiment does not include those packages. The stand-in still refuses approval and still refuses A3. It is not schema-validated.
