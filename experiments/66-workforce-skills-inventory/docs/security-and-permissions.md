# Security and permissions

This note matches `agent-manifest.yaml`. If the two disagree, the manifest is the control. `permissions.yaml` is the same file. It is written for an organisation deciding whether to try the starter, not as a completed DPIA.

## What the core reads

The evidence pack, the example framework, the directory row (role, clearance, team only), the Article 13 booleans, and a separate decision object. Experiment 08 is called on a cited sentence. Experiment 61 is called only after the employee confirms a skill. Experiment 62 is called only from experience the employee states, not from inferred skills.

Age, disability, and health fields on the directory are not read. Monitoring, mailbox, absence, manager-note, and health-record items are skipped. A body above the directory clearance is not copied. The higher marking, the legal hold, and every retention label are kept.

## What it does not do

It does not write to an HR system, rate performance, set pay, decide promotion, select for redundancy, or make a disciplinary decision. It does not decide Article 6, Article 13, Article 21, or Article 22A. It does not decide a Data Protection Act 2018 section 10 condition. `output_is_anonymised` stays false.

Confirmation is `record_employee_decision()`, keyed to the employee on the directory and to the inventory hash and the skill hash. A marker inside the evidence does not count. HR validation is a second object, after the employee step, and it does not survive a later rejection.

## Platform controls this starter does not configure

| Control | In this starter | Note |
| --- | --- | --- |
| Microsoft Entra Agent ID and Conditional Access for agents | Not configured | Not opened on 19 November 2026. Unverified. |
| Power Platform DLP as a configured policy | Not configured | Not opened. Unverified. |
| Microsoft Foundry prompt shields | Not configured | Not opened. Unverified. |
| Key Vault | Not configured | Not opened. Unverified. |
| Microsoft Purview | Not configured | The Fabric overview says Purview provides protection for supported Fabric data. A policy was not configured or tested. Unverified as a control on this starter. |
| Application Insights | Not configured | Not opened. This starter writes no log. Unverified. |

## Kill switch

Turn the Copilot Studio agent off, and revoke any Foundry credential used for an optional note. Contacts in the manifest use `ashcombe.example.gov.uk`. They are placeholders. Ashcombe Borough Council is invented.
