# Security and permissions

Cross-Source Validation Agent, Experiment 36. Catalogue ID B005. Autonomy A0.

This note matches `agent-manifest.yaml`. `permissions.yaml` is the same file. If the note and the manifest disagree, the manifest is the control. It is written for an organisation deciding whether to try the starter, not as a completed DPIA and not as a finding that personal data is inaccurate.

## What a run may read

The synthetic pack the reviewer supplies, an optional resolutions object the reviewer supplies, the pinned notes in `src/sources.py`, and Experiments 08, 12, and 33, by calling them. The Python starter does not persist the pack. A call that is not marked synthetic is refused, and the refusal does not echo the body.

## What a run must not do

Choose a source, edit a record, contact anyone, query Companies House, or call Microsoft Foundry. Writes and sends are disabled. `correct_value` stays null.

## Controls named for a deployment

These product controls were not opened for this experiment. They are unverified here. A deployment that uses them should confirm the current portal label.

**Microsoft Entra Agent ID.** Use a dedicated identity if the organisation deploys this, with no mail role and no register role. This starter does not create one. Whether the Agent ID platform or an admin-center wizard is generally available was not re-checked on 5 November 2026.

**Conditional Access.** A deployed agent identity should sit behind the organisation's Conditional Access policies. This starter does not configure a policy. Unverified here.

**Data Loss Prevention.** The pack should not be pasted into a channel that the organisation's DLP policy would block. This starter does not connect a DLP policy. Unverified here.

**Microsoft Foundry prompt shields.** The comparison does not call a model, so no prompt-shield control is enabled by this folder. The product control was not opened. Unverified here. The injection tests in `tests/test_injection.py` are the control on the local command.

**Key Vault.** This starter has no secret to store. A later host that stored a key would use the organisation's Key Vault. Unverified here.

**Microsoft Purview.** An organisation that already uses Purview for audit or DLP should decide whether this agent's prompts and outputs are in scope. This starter does not connect Purview, and it does not claim a particular Copilot Studio audit schema. Unverified here.

**Application Insights.** This starter writes no log. A later host would choose a UK log store and would not log field values. Application Insights was not opened. Unverified here.

## UK GDPR

Article 5(1)(d) was opened on 5 November 2026. It requires accuracy and, where necessary, that data are kept up to date, and reasonable steps to erase or rectify inaccurate data without delay. This tool does not take those steps.

Data Protection Act 2018 section 205(1) was opened the same day. "Inaccurate" means incorrect or misleading as to any matter of fact. A material discrepancy is not that finding.

The ICO accuracy page was requested and returned HTTP 403. It was not opened and is not quoted.

Article 22 was not re-opened for this experiment. This starter does not take a significant decision. It does not claim a reading of the current automated-decision provisions.

No Article 6 basis is asserted. The data protection officer confirms one before any live file.

## Companies House

The organisation page was opened on 5 November 2026. It says Companies House registers company information and makes it available to the public. This tool does not query that register. Fixture company numbers are synthetic and were not looked up.

## Kill switch

Do not run the command. There is no published agent to switch off.
