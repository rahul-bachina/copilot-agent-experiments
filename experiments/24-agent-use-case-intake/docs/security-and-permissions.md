# Security and permissions

Agent use-case intake, Experiment 24. Catalogue ID G001.

This note matches `agent-manifest.yaml`. If the two disagree, the manifest is the control. It is written for an organisation deciding whether to try the starter, not as a completed DPIA.

## Purpose

The agent reads one proposed agent idea and returns a draft classification: suggested autonomy A0, A1, or A2, a risk tier, a DPIA indication, an ATRS indication, and a resemblance to an existing experiment. Autonomy of this intake agent is A1. It drafts. It does not take the action of approving the classification. The governance team approves the intake classification, or changes it.

## What the agent cannot do

These are disabled in the manifest, not merely discouraged in the prompt.

- Approve a use case, reject a use case, or record the governance team's decision.
- Provision, deploy, publish, or create a Copilot Studio agent, a Power Automate flow, a Dataverse table, or a Microsoft Foundry resource.
- Suggest autonomy A3. The catalogue levels for a suggested autonomy are A0, A1, and A2.
- Decide that Article 35 requires a DPIA. `dpia_required` stays null.
- Decide that an organisation or a tool is inside ATRS mandatory scope, or email an ATRS record.
- Select a platform. `platform_selected` stays null.
- Call Experiment 03's manifest generator, or mark a manifest approved.
- Write a production record or send a message.
- Refresh citations from the web. URLs come from `src/sources.py` and from the neighbour modules.

There is no tool whose side effect is any of the above. `approve_use_case`, `reject_use_case`, `provision_agent`, and `record_governance_decision` raise. Tests in `tests/` check that an instruction inside a proposal does not become an approval, an A3 suggestion, or a provisioned agent.

## Data

**Read, in this starter.** The proposal the team supplies for that run. The as-of date and the stale threshold. Experiments 14, 19, and 03, loaded from the neighbouring folders for `rules.score`, `screen`, and `draft_atrs`.

**Not read.** An admin centre, a billing account, a mailbox, a Teams chat, Copilot Studio as a control plane, Microsoft Foundry as a control plane, and Power Automate as a control plane. The ATRS scope and exemptions policy was not opened.

A proposal can name staff or describe personal data. The manifest does not assert a UK GDPR lawful basis. Article 6 was not opened for this experiment. The samples in this repository are synthetic. A proposal that is not marked synthetic is refused, and the body is not copied into the refusal.

The Python starter does not persist the proposal. Free text is not copied into the JSON output. System names that match an instruction pattern are omitted.

## Prompt injection and stale data

Proposal text is untrusted. The scanner records a line that tells the intake to ignore instructions, disregard the rules, force autonomy A3, approve or reject the use case, mark the classification approved, provision or deploy an agent, hide the draft from the governance team, override the classification, clear a stale flag, or skip a DPIA or an ATRS indication. A `system:` or `developer:` line is recorded. Payload keys that try to set `approved`, `suggested_autonomy`, `risk_tier`, `dpia_likely_needed`, `atrs_likely_needed`, `provisioned`, or `governance_decision` are stripped and are not echoed. `followed` stays false. Structured fields are the only input to the rules.

The stale-data test compares each pin date with the as-of date. Older than the threshold, default 90 days, is stale. The pins are this folder (30 October 2026), Experiment 14 (27 October 2026), Experiment 19 (28 October 2026), and Experiment 03 (24 October 2026). The classifier does not download the page. When a pin is stale, an approval point asks the governance team to re-open it. A sentence in the proposal does not clear the flag. The draft is still produced. It is still not an approval.

The residual risk is a misleading draft if a model is later wrapped around the JSON. The governance team is the control. There is no autonomous approval behind a bad draft.

## Human approval

| Decision | Who |
|---|---|
| Approve or change the intake classification | Governance team |
| Decide what to do with a request for autonomy A3 | Governance team |
| Treat a DPIA indication as a reason to start a DPIA | Privacy officer |
| Treat an ATRS indication as a reason to draft a record | Governance team |
| Re-open a pinned page after it is marked stale | Governance team |
| Provision, deploy, or publish | Outside this agent |

Producing the draft and re-running it do not need a separate approval. The agent does not record any of the decisions in the table. `governance_decision` stays null.

## Controls a tenant would discuss

This starter configures none of them. The pages below were not opened for this experiment. Each row is unverified. Do not treat an unverified row as a product capability.

| Control | In this starter | Note |
|---|---|---|
| Microsoft Entra Agent ID | Not configured | Unverified. That product page was not opened for this experiment. |
| Conditional Access | Not configured | Unverified. Not opened for this experiment. |
| Power Platform data loss prevention | Not configured | Unverified. Not opened for this experiment. A later connector that can send or write would need a policy the organisation writes. |
| Microsoft Foundry prompt shields | Not called | Unverified. The prompt-shields page was not opened for this experiment. The local scan does not call them. |
| Key Vault | Not provisioned | Unverified. Not opened. The classifier has no secret. |
| Microsoft Purview | Not configured | Unverified. Not opened. Classification of the proposal is the organisation's. |
| Application Insights | Not configured | Unverified. Not opened. The manifest names it as not configured. If it is enabled later, do not log the problem statement. |

Announced items that this folder did not check are not listed as available.

## Logging

This starter writes no log. Before live use, log who ran it, when, the proposal id, the as-of date, the pin dates, injection pattern ids, and whether sources were stale. Do not log the problem statement.

## Kill switch

Do not run `src/classify.py`. Delete the local copy from a machine that should not draft a classification. There is no published agent to turn off. If a team later publishes one despite this starter, turn that Copilot Studio agent off and block a send or a write in a data loss prevention policy the organisation configures. Contacts in the manifest use `example.com`. They are placeholders.
