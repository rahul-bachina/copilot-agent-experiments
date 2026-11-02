# Security and permissions

Prompt Injection Test Agent, Experiment 28. Catalogue ID G006.

This note matches `agent-manifest.yaml`. If the two disagree, the manifest is the control. It is written for an organisation deciding whether to try the starter, not as a completed DPIA and not as a penetration test.

## Purpose

The agent loads one versioned suite of synthetic prompt-injection fixtures, scores a sandbox target, and returns a findings report mapped to pinned OWASP titles. Autonomy is A0. It has no action to take on the draft. A security reviewer assesses the findings and decides remediation. A governance owner approves any manifest skeleton before anyone relies on it.

## What the agent cannot do

These are disabled in the manifest, not merely discouraged in the prompt.

- Target a production system, a tenant, a model endpoint, or any URL.
- Assess the findings. `reviewer_assessed` stays false.
- Apply remediation, edit a prompt, or deploy an agent. `remediation_applied` stays false.
- Publish the report or a fixture beyond the synthetic files in this folder. `published` stays false.
- Recommend autonomy A3. The catalogue levels are A0, A1, and A2. This runner stays at A0.
- Mark a permissions manifest approved.
- Write a production record or send a message.
- Call Microsoft Foundry, Prompt Shields, PyRIT, or the network.
- Compute an Attack Success Rate.
- Quote a price or look up a licence in an admin centre.
- Refresh citations from the web. URLs come from `src/sources.py`.

There is no tool whose side effect is any of the above. `schema/tools.json` marks `record_security_assessment`, `apply_remediation`, and `publish_findings` as not callable. Tests in `tests/test_prohibited.py` and `tests/test_injection.py` check that fixture text does not become an assessment, a remediation, or a publication.

## Data

**Read, in this starter.** The sandbox bundle for that run. An allow-listed instruction file, tool schema, or manifest already in this repository, when the instruction-surface adapter is named. The as-of date and the stale threshold. The static source list and the OWASP titles. Experiment 08, Experiment 25, or Experiment 03, called locally when that adapter is named. One synthetic identifier shape already published in Experiment 08. The report does not repeat the value.

**Not read.** An admin centre, a billing account, a mailbox, a Teams chat, a production agent, Copilot Studio as a control plane, Microsoft Foundry as a control plane, and Power Automate as a control plane.

The samples in this repository are synthetic. The instruction-surface adapter can read system prompts already committed in this repository. Those files are not live tenant prompts. The manifest does not assert a UK GDPR lawful basis. The organisation's data protection officer confirms an Article 6 basis before any live processing, and an Article 9 condition if special-category data is in scope. Live data is outside this starter.

The Python starter does not persist the bundle. Findings name case ids. They do not repeat probe text.

## Prompt injection and stale data

The runner is itself a reader of untrusted fixture text. The scanner records a line that tells the runner to ignore instructions, mark every case as pass, assess the findings, apply remediation, publish, target production, or set autonomy A3. A sentence that already refuses the action, including "do not" and "must not", is not treated as an injection. Payload keys that try to set `reviewer_assessed`, `remediation_applied`, `published`, `passed`, `failed`, or `score` are stripped and are not echoed. `followed` stays false.

The instruction-surface rules look for a negation in the same scope as the verb. A markdown heading that contains a negation keeps the following lines until the next heading. A paraphrase is missed. One matching verb covers the whole class. That limit is documented in the README. A pass means the file contains the wording. It does not mean a live model would refuse.

The stale-data test compares `last_verified` (2 November 2026 for the pages this experiment opened) with the as-of date. Older than the threshold, default 90 days, is stale. The catalogue-boundary row is not a Microsoft page and is not stale-tested. The runner does not download the page and does not rewrite the review date. When a pin is stale, `do_not_rely` is true. The draft is still produced. It is still not an assessment. `reopened_for_this_experiment` stays as stored.

The residual risk is a misleading draft if a model is later wrapped around the JSON, or if a reader treats a wording pass as evidence a deployed agent is safe. The security reviewer is the control. There is no autonomous action behind a bad draft. Residual risk R3 in the manifest is High for the wording rules.

## Human approval

Autonomy A0 means this runner cannot remediate even after a person agrees. The person still has to make the change.

| Decision | Who |
|---|---|
| Assess the findings | Security reviewer |
| Decide remediation | Security reviewer |
| Re-open a pinned page before relying on a citation | Security reviewer |
| Rely on a manifest skeleton drafted because none was supplied | Governance owner |
| Point a hosted red-team tool at an agent | Security reviewer, and only outside this starter |
| Confirm an Article 6 basis, and an Article 9 condition if special-category data was recorded | Data protection officer |
| Deploy, publish, or turn a flow on | Outside this agent |

Producing the draft and printing the sources table do not need a separate approval.

The skeleton for a missing manifest asks for A0. A request for autonomy A3 is refused. It is never the recommendation. `a3_recommended` stays false. Assumption id A3 in the manifest is an assumption about disabled high-risk actions. It is not autonomy level A3.

## Controls a tenant would discuss

This starter configures none of them. A row says "opened" only when the body was opened on 2 November 2026 for this experiment. Otherwise the control is unverified. Do not treat an unverified row as a product capability.

| Control | In this starter | Note |
|---|---|---|
| Microsoft Foundry AI Red Teaming Agent | Not called | Opened on 2 November 2026. Uses PyRIT and Foundry Risk and Safety Evaluations. Attack Success Rate can be non-deterministic. Review before mitigation. Supported targets named on the page are Foundry-hosted prompt agents and container agents with Azure tool calls. Non-Foundry agents are not supported. Cloud regions named: East US 2, France Central, Sweden Central, Switzerland West, US North Central. A UK region was not in that list. |
| Microsoft Foundry prompt shields | Not called | Opened on 2 November 2026. User prompt attack detection is on by default. Document attack detection is off by default. Tool-response scanning for agents, and Spotlighting, are marked preview. The page says the service is powered by Azure AI Content Safety. The local scan does not call them. |
| Microsoft Entra identity for Foundry Agent Service | Not configured | Unverified. That page was not opened for this experiment. |
| Microsoft Entra Agent ID | Not configured | Unverified. Not opened for this experiment. |
| Conditional Access | Not configured | Unverified. Not opened for this experiment. |
| Power Platform data loss prevention | Not configured | Unverified. Not opened for this experiment. A later connector that can send or write would need a policy the organisation writes. |
| Key Vault | Not provisioned | Unverified. Not opened. The runner has no secret. |
| Microsoft Purview | Not configured | Unverified. Not opened. Classification of any later report is the organisation's. |
| Application Insights | Not configured | Unverified. Not opened for this experiment. If a later deployment logs traces, do not log fixture text or canaries. |
| Private networking and a UK region for Foundry red teaming | Not configured | Unverified. The red-teaming page did not name a UK region. |

Announced items that this folder did not open are not listed as available.

## Logging

This starter writes no log. Before live use, log who ran it, when, the bundle id, the adapter, the suite version, the as-of date, the pass count and the fail count, and whether a prompt-injection pattern was detected in the bundle. Do not log fixture text or a canary.

## Kill switch

Do not run `src/run.py`. Delete the local copy from a machine that should not draft findings. There is no published agent to turn off. If a team later publishes one despite this starter, turn that Copilot Studio agent off, remove any Foundry credential, and block a send or a write in a data loss prevention policy the organisation configures. The contact in the manifest is `prompt-injection-test@example.com`. It is a placeholder.

## Skeleton generator

When the caller asks and no manifest was parsed, a draft manifest is requested from Experiment 03's `generate_manifest`, with `approve` false, and only if PyYAML and jsonschema import. The generator refuses an approve flag and refuses autonomy A3. This runner discards a skeleton whose level is not A0, and discards one that comes back approved. High-risk actions in the generated file stay disabled. A clean install of this experiment does not include those packages. The stand-in still refuses approval and still refuses A3. It is not schema-validated.
