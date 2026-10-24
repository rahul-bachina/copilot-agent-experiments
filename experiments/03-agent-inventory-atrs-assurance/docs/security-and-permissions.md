# Security and permissions

The control is [agent-manifest.yaml](../agent-manifest.yaml). If this note and the manifest disagree, the manifest wins.

Autonomy **A1**. Writes disabled. Sends disabled. Approve or reject, regulated decision, production record change, external send, and spending are disabled. Publishing an ATRS record and marking a manifest approved are also disabled.

Contacts use `example.com`. They are placeholders.

## What a run may read

One inventory record the caller supplies, the static ATRS field list, and the manifest schema. The worked examples are the JSON and CSV fixtures. The Python starter does not persist them.

## What it must not read

Dataverse in a tenant, mailboxes, the ATRS submission inbox, live case files from Experiments 01 or 02, and any site at runtime. Sources were read while this experiment was written. A run does not fetch them.

## Human approval

| Decision | Who |
| --- | --- |
| Change a lifecycle status | Governance owner. Mandatory. The core applies a change only when an external decision from this role is supplied, and it still sets `approved_by_this_tool` to false. |
| Rely on a pack | Governance owner |
| Submit or publish an ATRS record | Senior responsible owner and the organisation's own clearance. Outside the agent. The [ATRS guidance](https://www.gov.uk/government/publications/guidance-for-organisations-using-the-algorithmic-transparency-recording-standard/algorithmic-transparency-recording-standard-guidance-for-public-sector-bodies) describes clearance before a record is sent to the ATRS team. |
| Accept G006 findings | Security reviewer |
| Approve the 180-day G007 threshold | Evaluation owner |
| Sign the DPIA | The organisation's sign-off, including DPO advice. The skeleton leaves the names blank. |

Viewing a draft and re-running the same record do not need a separate approval.

## UK GDPR

The manifest does not choose a lawful basis. A public body and a firm are not in the same position. The DPO confirms a basis before production use. Special-category text might appear in an inventory narrative. No Article 9 condition is asserted. The fixtures in this repository are synthetic.

The DUAA screen cites [section 80](https://www.legislation.gov.uk/ukpga/2025/18/section/80). It is not a finding that processing is lawful. This note is not a DPIA.

## Entra, Conditional Access, and DLP

[Microsoft Entra Agent ID](https://learn.microsoft.com/en-us/entra/agent-id/what-is-microsoft-entra-agent-id) is the identity and security framework Microsoft documents for agents, including a link to Conditional Access for agents. This starter does not register an agent identity, an agent identity blueprint, or a Conditional Access policy. Those would be a deployment decision. The overview was read on 24 October 2026. It does not, by itself, authorise this agent to hold a Dataverse write.

Power Platform [data loss prevention](https://learn.microsoft.com/en-us/power-platform/admin/wp-data-loss-prevention) is the control that should block mail connectors, and any Dataverse connector used for update, if someone adds one later. No policy is created in this repository.

## Key Vault, Purview, Application Insights, prompt shields

This starter has no secret and no model endpoint. [Azure Key Vault](https://learn.microsoft.com/en-us/azure/key-vault/general/overview) is the place a deployment would put a secret if a managed identity could not be used. Nothing here needs one.

Microsoft Purview audit of Copilot activity depends on the tenant's Purview solution and on which Copilot surface is in scope. Coverage for a Copilot Studio agent on either harness was **not verified** for this starter. Do not assume a pack draft is audited.

Application Insights is not wired. The manifest names it only as a possible later log destination.

[Prompt Shields](https://learn.microsoft.com/en-us/azure/ai-services/content-safety/concepts/jailbreak-detection) are a jailbreak and indirect-injection control in Azure AI Content Safety. They are relevant if a deployment adds a model. This core does not call them. G006 is a local pattern list, not Prompt Shields.

## Prompt injection and stale data

`tests/test_safety.py` checks that an instruction to approve, change status, or email does not become an action, and that a 2024 review date is stale on 24 October 2026. The residual risk in the manifest is a misleading draft. There is no autonomous action behind it.

## Kill switch

Turn the Copilot Studio agent off. Block mail and Dataverse write connectors with a DLP policy. Remove the agent's Dataverse read role if one was granted. None of these is provisioned here.

## Review

Reviewed for this starter on 24 October 2026. Next review 24 April 2027, and sooner if the ATRS template, the playbook principles, Article 22D regulations, or the manifest schema change.
