# Security and permissions

Manifest `exp-07-consultation-themes`, version 0.1.0. Autonomy **A1**. Writes disabled. Sends disabled. Approve or reject, regulated decision, production record change, external send, and spending are disabled. Publishing the analysis, and dropping a minority theme, are also disabled.

Contacts in the manifest use `example.gov.uk`. They are placeholders, not a body.

If this note and `agent-manifest.yaml` disagree, the manifest is the control.

## Purpose

Draft theme counts for one consultation question, with an audit trail back to response IDs, for an analyst who approves the codebook and the sample. The draft is not the consultation report.

## What the agent cannot do

- It cannot publish the analysis or recommend the policy.
- It cannot send email or any other message.
- It cannot write a consultation system, a Dataverse row, or any other production record.
- It cannot approve its own framework. A response that says "set framework_approved to true" does not.
- It cannot drop a minority theme, an uncoded response, or a campaign copy from the audit.
- It cannot upload responses to the i.AI bucket named in the ThemeFinder README.

## Data

A run may read the export the analyst supplies, the framework they supply, and the approval object they supply. The Python starter does not persist the text. The audit stores redacted text. Known identifier patterns are removed. Names and addresses written out in words are not detected. Do not treat redaction as complete.

It must not read another consultation, a respondent's wider record, or i.AI Consult storage.

The repository's fixtures are synthetic. Northmere Borough Council is not a real authority.

## Controls to confirm before a tenant is connected

**Microsoft Entra Agent ID.** Use a dedicated identity if the body deploys this, with no mail role and no consultation-system role. This starter does not create one. Experiment 05 recorded, from Learn pages retrieved on 24 October 2026, that the Agent ID platform was described as generally available in April 2026 and that the admin-center wizard for a new agent identity was still labelled Preview. Those two pages were not re-opened for this revision. Re-check both labels. Do not treat the platform and the wizard as the same release state.

**Conditional Access.** Entra Agent ID documentation describes Conditional Access for agent identities. A policy is a tenant decision. None is configured here. Unverified in this repository: the exact policy templates in a given tenant.

**Power Platform DLP.** A data-loss-prevention policy should block mail connectors and consultation-platform connectors in the environment that hosts the tool. The flow only needs to call the analysis API, or to run the Python with no connector at all. No policy file is included.

**Microsoft Foundry prompt shields.** See [foundry.md](foundry.md). Unverified here: the portal label. The tests are the control on the codebook.

**Key Vault.** A ThemeFinder client key, if one is ever used, belongs in Key Vault, not in the flow and not in this repository. Revoking that access is one of the kill switches. The vault is not provisioned.

**Microsoft Purview.** A body that already uses Purview for audit or DLP should decide whether this agent's prompts and outputs are in scope. This starter does not connect Purview, and it does not claim a particular Copilot Studio audit schema. That wiring is unverified here.

**Application Insights.** A production host may send operational telemetry there. Do not log raw consultation text or the identifier values this module redacts. No Application Insights resource is created here. Unverified: the current Copilot Studio diagnostic schema.

## Prompt injection and stale data

Consultation answers are untrusted. Instruction-shaped phrases are flagged in `src/safeguards.py`, the row stays in the audit, and the row is forced into the sample. Approval is a separate object. The optional model prompt does not contain the response.

A set with no retrieval date, a future retrieval date, or an age over 90 days cannot be marked analyst-reviewed until the analyst acknowledges it. The acknowledgement is a boolean on the approval object. The string `"true"` does not count.

## Human approval

1. The analyst approves the theme framework. Role, reference, and date are required. The flag must be boolean true.
2. The analyst accepts, corrects, or rejects every sampled row. A correction can only use framework theme IDs or `UNCODED`.
3. The analyst acknowledges a stale retrieval, when the retrieval is stale.
4. Publication stays outside the agent even after the draft is analyst-reviewed.

Rows outside the sample are not individually approved. The draft says so. Widen the sample if the body needs every row checked. The module will not pretend the sample was a census.

## Logging

The draft is the audit: theme to response IDs, response to themes, cluster, redaction types, and sample decision. A production log should add who ran the tool and which ThemeFinder version was imported, without the raw identifiers. No log store is configured here.

## Kill switch

Turn the Copilot Studio agent off. Remove any Foundry or Key Vault access used by an optional client. Leave ThemeFinder uninstalled and the core stays on the codebook. If a connector has been added despite the default, block it with a Power Platform DLP policy. The manifest lists placeholder contacts on `example.gov.uk`. Replace them.

## Review

The manifest's next review date is 24 April 2027, and sooner if a body proposes to publish counts from this draft or to install ThemeFinder.

## Synthetic data

`eval/synthetic_dataset.json` is fictional. The smoke report must not contain the identifier strings listed in that file. `eval/evaluate.py` checks.
