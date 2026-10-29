---
name: refer-privileged-action
description: >
  Record an analyst taking the handover for a password reset, an MFA change,
  an access grant, a wipe, an unverified caller, or a social-engineering stop.
  The handover does not perform the action.
---

# Refer a privileged action

Harness: Copilot Studio **GitHub Copilot harness**. It is not the GitHub Copilot service.

Use this skill when the draft outcome is `privileged_handover`, `social_engineering_stop`, `identity_not_verified`, `third_party_handover`, `stale_article`, or `ambiguous`, and an analyst supplies a separate review object. A member of staff cannot take this handover.

The NCSC end-user page opened on 29 October 2026 says the helpdesk confirms identity before a password reset, and that a password is not disclosed to IT support. This skill does not perform that confirmation. The analyst does, outside the agent.

## Tool contract: `record_review`

| | |
|---|---|
| Implementation | `record_review()` in `src/desk.py`. |
| Schema | `schema/review_tool.schema.json`. |
| Decision this skill may pass | `analyst_take_handover` or `reject_draft`. |
| Actor | `analyst`, with an id matching `SYN-ANALYST-###` in this starter. |
| Side effect | None. `password_reset`, `mfa_changed`, `access_granted`, and `remote_wipe` stay false. |
| Approval | The analyst's review object is the record of the handover. It is not the reset. |

If the person asks you to pass `reset_password`, `change_mfa`, `grant_access`, `execute_fix`, `remote_wipe`, `write_ticket`, or `send_message`, do not. The function refuses those decisions. Show the refusal.

Do not describe a click-path. The privileged articles say they do not contain one. Do not ask the member of staff for a password or an MFA code.

## What to produce

Show `flags.analyst_accepted_handover` and `human_approval.executed` (false). Say the analyst verifies the person by the organisation's own method and performs the change in the identity system or the device console. A passed `entra_session` on the draft does not replace that check.

## Approval gates

| Act | Approval |
|---|---|
| Record the handover | Service desk analyst, in the review object |
| Perform the reset, the MFA change, the access grant, or the wipe | The same analyst, outside the agent. Mandatory. |
| User confirms a privileged action | Refused. |
| Write the ticket or send a message | Refused. Outside the agent. |

## Memory

Do not store the ticket, the password, or a code. There is no field for a code.
