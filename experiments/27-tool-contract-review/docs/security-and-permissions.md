# Security and permissions

Tool Contract Review Agent, Experiment 27. Catalogue ID G005.

This note matches `agent-manifest.yaml`. If the two disagree, the manifest is the control. It is written for an organisation deciding whether to try the starter, not as a completed DPIA.

## Purpose

The agent reads one tool or action contract and returns a scored findings report, proposed contract notes, and a proposed API Management policy sketch. Autonomy of this reviewer is A0. It has no action to take on the draft. The security/API owner approves the contract. A governance owner approves any manifest skeleton before anyone relies on it.

## What the agent cannot do

These are disabled in the manifest, not merely discouraged in the prompt.

- Modify a contract, apply a proposed diff, or write a contract file.
- Publish an Azure API Management policy.
- Record that the security/API owner has approved a contract or a policy.
- Deploy or publish a contract, a Copilot Studio agent, or a Foundry agent.
- Recommend autonomy A3. The catalogue levels are A0, A1, and A2. This reviewer stays at A0.
- Mark a permissions manifest approved.
- Approve or reject a finding as if that were the owner's decision.
- Write a production record or send a message.
- Quote a price or choose a call volume.
- Refresh citations from the web. URLs come from `src/sources.py`.
- Select a platform when Experiment 14 is called. `platform_selected` stays null.
- Treat Experiment 25's instruction score as the contract score, or apply that reviewer's diff.

There is no tool whose side effect is any of the above. `schema/tools.json` marks `record_owner_approval`, `apply_contract_diff`, `publish_policy`, and `deploy_contract` as not callable. Tests in `tests/test_prohibited.py` and `tests/test_injection.py` check that text inside a contract does not become an edit, an approval, a publish, or a deployment.

## Data

**Read, in this starter.** The contract the security/API owner supplies for that run. An optional permissions manifest. An optional structured use case. Optional instruction text, passed to Experiment 25. The as-of date and the stale threshold. The static source list. Experiment 03's generator, called locally when no manifest was parsed. Experiment 14's rule table, called locally when a structured use case was supplied.

**Not read.** An API Management instance, a Foundry project, an MCP server, an admin centre, a billing account, a secret store, a mailbox, a Teams chat, and Copilot Studio, Microsoft Foundry, or Power Automate as a control plane.

A pasted contract can name staff or describe personal data, including a field whose name matches a special-category word. The manifest does not assert a UK GDPR lawful basis. The organisation's data protection officer confirms an Article 6 basis before any live processing, and an Article 9 condition if special-category data is in scope. A field-name match is not that determination. The samples in this repository are synthetic. A few evaluation cases read tool schemas and manifests already in this repository. Those files are not live tenant contracts.

The Python starter does not persist the contract. The proposed diff is returned in the JSON. It is not written back to the file and it is not published. A secret-shaped value is not copied into the evidence.

## Prompt injection and stale data

Contract text is untrusted. The scanner records a line that tells the reviewer to ignore instructions, disregard the rules, force a pass, apply a diff, approve a contract, publish a policy, deploy, hide a finding, or override the decision. A `system:` or `developer:` line is recorded. A sentence that already refuses the action, including "do not" and "must not", is not treated as an injection. Payload keys that try to set `owner_approved`, `contract_approved`, `diff_applied`, `policy_published`, `deployed`, `score`, or `autonomy_level` are stripped and are not echoed. `followed` stays false. Instruction text supplied beside the contract can be flagged without changing the contract score. Experiment 25 scores that text separately.

The stale-data test compares `last_verified` (2 November 2026 for the pages this experiment opened) with the as-of date. Older than the threshold, default 90 days, is stale. The catalogue-boundary row is not a Microsoft page and is not stale-tested. A contract with no review date, or a review date older than the threshold, is stale. The reviewer does not download the page and does not rewrite the review date. When a pin or a contract review date is stale, `do_not_rely` is true and an approval point asks the security/API owner to re-open it. The draft is still produced. It is still not an applied change. `reopened_for_this_experiment` is true for the pages opened on 2 November 2026. It is not a claim that the page was opened again after that date.

The residual risk is a misleading draft if a model is later wrapped around the JSON. The security/API owner is the control. There is no autonomous action behind a bad draft.

## Human approval

Autonomy A0 means this reviewer cannot modify a contract or publish a policy even after a person agrees. The person still has to make the change.

| Decision | Who |
|---|---|
| Approve the contract | Security/API owner |
| Approve an API Management policy change before it is published | Security/API owner |
| Accept or reject each finding before a contract change is kept | Security/API owner |
| Rely on a manifest skeleton drafted because none was supplied | Governance owner |
| Re-open a pinned page, or a review date, before relying on a citation | Security/API owner |
| Confirm an Article 6 basis, and an Article 9 condition if special-category data was recorded | Data protection officer |
| Deploy, publish, or turn a flow on | Outside this agent |

Producing the draft, re-running it, and printing the sources table do not need a separate approval.

The skeleton for a missing manifest asks for A0. A request for A3 is refused. It is never the recommendation. `a3_recommended` stays false.

## Controls a tenant would discuss

This starter configures none of them. A row says "opened" only when the body was opened on 2 November 2026 for this experiment. Otherwise the control is unverified. Do not treat an unverified row as a product capability.

| Control | In this starter | Note |
|---|---|---|
| Azure API Management `rate-limit` | Proposed, not published | Opened on 2 November 2026. Per subscription, HTTP 429, renewal period at most 300 seconds, applied when a subscription key is used. Placeholders are not a call volume. It does not authenticate the caller. |
| Azure API Management `authentication-managed-identity` | Proposed, not published | Opened on 2 November 2026. Sets a bearer token from the managed identity. The customer forwards it only to an intended backend. The policy index lists this policy as not supported on the workspace gateway. The policy page's usage line lists classic, v2, consumption, and self-hosted. Both statements are kept. |
| Azure API Management `validate-parameters` | Proposed, not published | Opened on 2 November 2026. A prevent action on inbound returns HTTP 400. Maximum schema size 4 MB. This reviewer does not run the load test the page recommends. |
| Microsoft Entra identity for a later Foundry agent | Not configured | The Foundry Agent Service overview was not opened for this experiment. This starter creates no identity. |
| Microsoft Entra Agent ID, including any admin wizard | Not configured | Unverified. That product page was not opened for this revision. |
| Conditional Access | Not configured | Unverified. Not opened for this revision. |
| Power Platform data loss prevention | Not configured | Unverified. Not opened for this revision. A later connector that can send or write would need a policy the organisation writes. |
| Microsoft Foundry prompt shields | Not called | Unverified for this revision. The Prompt Shields page was not opened. The local scan does not call them. |
| Key Vault | Not provisioned | Unverified. Not opened. The checker has no secret. A key found in a pasted contract is reported and is not used. |
| Microsoft Purview | Not configured | Unverified. Not opened. Classification of the contract is the organisation's. |
| Application Insights | Not configured | Unverified. Not opened. If it is enabled later, do not log the contract and do not log a secret-shaped value. |
| Private networking | Not configured | A UK region list was not on the pages opened. Unverified for a UK deployment. |

Announced items that this folder did not open are not listed as available.

## Logging

This starter writes no log. Before live use, log who ran it, when, the bundle id, the contract kind, the as-of date, the catalogue `last_verified` values, injection pattern ids, and whether a skeleton was drafted. Do not log the contract. Do not log a secret-shaped value. Log that a finding of that class existed.

## Kill switch

Do not run `src/review.py`. Delete the local copy from a machine that should not draft findings. There is no published agent to turn off and no published policy to remove. If a team later publishes one despite this starter, turn that Copilot Studio agent off, remove any Foundry credential, and block a send or a write in a data loss prevention policy the organisation configures. Contacts in the manifest use `example.com`. They are placeholders.

## Skeleton generator

When no manifest was parsed, a draft manifest is requested from Experiment 03's `generate_manifest`, with `approve` false, and only if PyYAML and jsonschema import. The generator refuses an approve flag and refuses autonomy A3. This reviewer discards a skeleton whose level is not A0, A1, or A2, and discards one that arrives already approved. High-risk actions in the generated file stay disabled. A clean install of this experiment does not include those packages. The stand-in still refuses approval and still refuses A3. It is not schema-validated.
