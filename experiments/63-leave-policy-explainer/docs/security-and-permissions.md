# Security and permissions

`permissions.yaml` is the same file as `agent-manifest.yaml`. It validates against `schemas/agent-manifest.schema.json`. Experiment 03's manifest generator is called to validate it, and to show that the generator refuses to mark a manifest approved.

Autonomy is A0. Writes are off. Sends are off. Approve or reject, a regulated decision, a production record change, an external send, and spending are off. So are booking leave, recording leave, calculating pay, and approving a policy version.

## What this folder does

The question and the policy text are untrusted. Identifier values are counted and not stored. The question is not copied. A report of counts is not a claim that the text was anonymised. Experiment 08's redacted text is not copied.

A protective marking is read from the metadata and from the text. The higher label wins. A SECRET cover is not quoted. A legal hold and every retention label are kept, including when an instruction says to strip them.

A typed role or clearance is not trusted. The scope approver and a seen-step approver have to be an active HR id on the synthetic directory. The seen-step has to carry the hash of the explanation it saw. Words inside the question are not that step.

## Controls a deployment confirms

These products are not created by this folder. Where a page was not opened on 18 November 2026, the behaviour is unverified.

| Control | What this starter says |
|---|---|
| Microsoft Entra and Conditional Access | The employer decides who can open the agent. This folder does not create an app registration. Entra Agent ID was not configured here. |
| Power Platform DLP | A later connector for mail, SharePoint write, payroll, or leave booking should be blocked. No connector is in this folder. |
| Key Vault | A Foundry key, if a narration is added, is not stored in the repository. |
| Microsoft Purview | Sensitivity labels on a live policy library are the employer's. This starter reads labels on the synthetic files. It does not call Purview. |
| Application Insights | Not configured. Do not log the question text. |
| Microsoft Foundry prompt shields | Not opened on 18 November 2026. Unverified. The Python core does not rely on a shield. |

The kill switch is in the manifest: turn the Copilot Studio agent off, remove a Foundry credential, or block a connector with DLP.
