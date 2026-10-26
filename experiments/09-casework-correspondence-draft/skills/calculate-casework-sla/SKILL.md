---
name: calculate-casework-sla
description: >
  Calculate one casework reply date by calling the existing Python clock.
  Use when an author has typed a receipt date and a target. Do not invent a
  deadline, and do not treat a reference date as operative.
---

# Calculate a casework reply date

Harness: Copilot Studio **GitHub Copilot harness**. That harness is an authoring and orchestration framework. It is not the GitHub Copilot service. Microsoft Learn, retrieved 26 October 2026, says customer data is not sent to the GitHub Copilot service when the agent runs in Copilot Studio.

This skill is for a correspondence author. The standard-harness clock action is in `copilot-studio/`. The boundaries below are the same ones already in `agent-manifest.yaml`. This skill does not add an approval step and it does not remove one.

The `name` and `description` above are the skill fields Microsoft describes. The approval rules below are the manifest's rules. They are not a Microsoft schema.

## When to use this skill

Use it when the author asks why a date came back, what 20 working days means, or for a count from dates they have typed. Drafting the letter is the other skill. Do not answer the correspondent.

## Tool contract: `calculate_sla`

| | |
|---|---|
| Implementation | `calculate_casework_sla()` in `src/sla.py`. Do not count working days yourself, and do not use the code interpreter as a second calendar. |
| Input | `received_on` as `YYYY-MM-DD`, typed by the author. `regime` of `central_government` or `council`. `target_working_days` as an integer the author typed, or omitted. `target_confirmed` and `channel_confirmed` only when the author has said so. `information_rights` only when the draft JSON already has a specialist route, or the author has classed the letter that way. Extra closed dates only when the author listed them. |
| Output | The JSON the function returns. |
| Side effect | None. No send. No case write. |
| Approval to run | Not required. |
| Approval to rely on an operative date | Required. A reference date is not a deadline. |

Do not set `target_confirmed` because the letter says the reply is urgent. Do not set `information_rights` to false in order to obtain a date for an FOI letter.

If the tool is unavailable, stop. Do not guess the date.

The September 2024 Guide, paragraph 9, retrieved 26 October 2026, says the deadline should not exceed 20 working days and that day 1 starts the day after receipt. The Guide does not define working day. This function uses the England and Wales calendar. A council target is not given that ceiling. Say so when `ceiling_applies` is false.

A holding reply does not clear the date. `holding_reply_clears_deadline` must be false. Transfer clocks are not calculated, because this agent does not send a transfer.

## What to produce

Show `operative`, `operative_due_on`, `reference_due_on`, and `reason`. If `operative` is false, say the date is not a deadline. Do not copy `reference_due_on` into a sentence that calls it the due date.

If `reason` is `information_rights_clock_is_separate`, say the correspondence clock does not apply and that this skill does not calculate a Freedom of Information Act deadline.

## Approval gates

These are the manifest's gates. Do not continue as if the author had agreed.

| Act | Approval |
|---|---|
| View the draft | Not required |
| Re-run the draft on the same letter | Not required |
| Calculate a reference clock from a target the author has typed | Not required. Relying on the date still needs the confirmation below. |
| Confirm the channel and whether a ministerial reply is required | Mandatory. Approver: Correspondence author |
| Confirm the reply target before the due date is treated as operative | Mandatory. Approver: Correspondence author |
| Review a vulnerability or immediate-review flag before it is recorded | Mandatory. Approver: Correspondence author |
| Approve the recipient | Mandatory. Approver: Correspondence author |
| Approve the final text | Mandatory. Approver: Correspondence author |
| Send the letter | Mandatory. Approver: Correspondence author. You do not send it. |
| Decide no-reply, a transfer, an information-rights outcome, or a complaint outcome | Mandatory, and outside the agent even after the draft is approved. Approver: Authorised casework decision-maker |

## Sandbox file

You may write `casework-clock.json` in the sandbox. It is the tool JSON, unchanged. Creating that file does not need approval.

## Memory

Do not store the letter or the correspondent. Memory on this harness is marked preview on the agents overview retrieved 26 October 2026. Do not use it.

## Stop

End when the clock JSON is shown. Say whether the date is operative. Do not send anything.
