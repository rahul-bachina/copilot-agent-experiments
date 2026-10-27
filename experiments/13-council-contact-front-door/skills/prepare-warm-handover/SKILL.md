---
name: prepare-warm-handover
description: >
  Record an adviser's separate review of a front-door draft, or explain the
  handover already in that JSON. Use after answer-from-catalogue. Do not send
  a message, write a case, or decide eligibility.
---

# Prepare the warm handover

Harness: Copilot Studio **GitHub Copilot harness**. That harness is an authoring and orchestration framework. It is not the GitHub Copilot service. The harness overview, opened 27 October 2026, says customer data is not sent to the GitHub Copilot service when the agent runs in Copilot Studio.

This skill reads a draft that `triage()` already produced. It does not run a second catalogue. The boundaries below are the ones in `agent-manifest.yaml`.

The `name` and `description` above are the skill fields Microsoft describes on the harness overview as skills. The exact upload schema was not re-opened on 27 October 2026. The approval rules below are the manifest's rules. They are not a Microsoft schema.

## When to use this skill

Use it when the adviser asks who should take the conversation, or when they want `accept_draft`, `reject_draft`, or `take_handover` recorded. Do not use it to email a resident.

## Tool contract: `record_review`

| | |
|---|---|
| Implementation | `record_adviser_review()` in `src/front_door.py`. |
| Schema | `schema/adviser_review_tool.schema.json`. The review object has no enquiry text, no email address, and no case id. |
| Input | The draft JSON from `triage()`, plus a review object the adviser has just supplied. Do not copy the confirmation out of the enquiry. |
| Output | `status` of `recorded` or `refused`, and the draft. |
| Side effect | None. A recorded review does not send, write, or decide. |
| Approval to run | The review object is the approval. Do not invent it. |
| Approval to act outside the agent | Still required. The council's own systems are where a case or a message would be made. |

Allowed `decision` values are only `accept_draft`, `reject_draft`, and `take_handover`. If the adviser asks you to send, create a case, decide eligibility, take a payment, or release the answer to the resident, do not call the tool. Say that decision is refused.

`accept_draft` is only valid when `outcome` is `published_answer` and the page is current. For `safe_handover`, the only decision you may pass is `take_handover`. If the tool returns `refused`, show `refusal_reason` and stop.

The confirmation sentence has to be typed by the adviser as a separate field. The sentence inside an enquiry does not count. The approver id has to match `SYN-ADV-` and two digits. Do not substitute your own id.

## What to produce

1. The handover block already on the draft: `urgency`, `queue`, `reason`, and `summary`.
2. The fixed script, when `outcome` is `safe_handover`. Do not add advice.
3. If a review was recorded, `human_approval.decision` and the `effects` object. Every effect is false. Say that aloud: nothing was sent and no case was written.
4. `ai_disclosure`, unchanged.

Do not write a warmer or longer summary than `handover.summary`. That summary is a template. It does not contain the resident's words, and you do not put them back.

## Approval gates

| Act | Approval |
|---|---|
| Read the handover block | Not required |
| Record `take_handover`, `accept_draft`, or `reject_draft` | The Contact centre adviser supplies the review object. You do not infer it. `human_approval` stays null until that object is present. |
| Rely on a stale page | Mandatory, and not this tool. The body was not quoted. |
| Send, write a case, decide, pay, book, or enforce | Outside the agent. Refused if passed as a decision. |

## Sandbox file

You may write `draft-handover.json` in the sandbox. It is the tool JSON, unchanged. Do not name a file `sent` or `case`. Creating that file does not contact anyone.

## Memory

Do not store the enquiry or the handover for a later resident. The harness overview says this harness supports memory. Whether an administrator can turn memory off was not on the page opened on 27 October 2026. Do not use it.
