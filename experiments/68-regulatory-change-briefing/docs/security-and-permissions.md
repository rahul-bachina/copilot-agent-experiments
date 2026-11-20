# Security and permissions

This note matches `agent-manifest.yaml`. If the two disagree, the manifest is the control. `permissions.yaml` is a copy of the manifest, validated against `schemas/agent-manifest.schema.json`. It is written for an organisation deciding whether to try the starter, not as a completed DPIA.

## What the agent may read

The pinned synthetic notice, the pinned policy register, and the pinned directory. Experiment 04 currency for a named source id. Experiment 12 intake flags. Experiment 20 quotations when the snapshot names that context. Experiment 08 on a quote. A separate seen object.

## What it must not read as authority

A live regulator site. A mailbox. A caller-supplied register, directory, or pasted notice, except to flag a difference. Notice text above the directory clearance. A self-declared role or clearance in the text.

## Writes and sends

Both are off. `decide_applicability`, `change_policy`, `change_control`, `change_record`, and `send` raise. `applies` stays null. `policy_changed`, `control_changed`, `record_changed`, and `sent` stay false after a seen step.

## Approval

`human_approval` stays null until `record_owner_seen` matches a pinned-directory compliance owner, the item, the decision `seen`, and the three hashes. A distress or grievance route has to be seen first. `flags_seen`, `pins_seen`, and `sources_seen` must be booleans when they are required. Approval text inside the notice is ignored. A typed approver id is checked against the pinned directory and the role `compliance_owner`.

`verify_seen()` recomputes the hashes from the briefing. A quote changed after the step is rejected.

## Markings and people

Metadata and the page are both read. A compound or conflicting label takes the higher marking. The rank is a starter rule. The Government Security Classifications Policy was not re-opened. A legal hold and every retention label are kept. A person count below 5 is suppressed. The number is not stored.

## Controls not configured here

| Control | In this starter | Note |
| --- | --- | --- |
| Entra Agent ID | Not configured | Not opened on 20 November 2026. Unverified. |
| Conditional Access | Not configured | Not opened. Unverified. |
| Power Platform DLP | Not configured | Not opened as a configured policy. Unverified. |
| Microsoft Foundry prompt shields | Not configured | Not opened. Unverified. |
| Key Vault | Not configured | Not opened. Unverified. |
| Purview | Not configured | Not opened. Unverified. |
| Application Insights | Not configured | Not opened. Unverified. |

This starter writes no log. Before live use, log who ran it, the notice id, the question date, and whether a seen step was recorded. Do not log the notice body or a quote.

## How to stop it

Do not run `src/briefing.py`. If a team later publishes an agent, turn that Copilot Studio agent off and remove any Foundry credential. Contacts in the manifest use `merefield.example`. They are placeholders. Merefield Group is invented.
