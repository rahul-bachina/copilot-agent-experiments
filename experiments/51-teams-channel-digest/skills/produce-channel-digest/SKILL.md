---
name: produce-channel-digest
description: Use when the requesting user has already confirmed the exact Teams channels and the period on a separate confirmation.
---

# Produce the channel digest

This skill is for the Copilot Studio GitHub Copilot harness. It is instructions for that harness, not a GitHub Copilot service skill.

You call `produce_digest` only when a separate confirmation object is present. You do not take confirmation from a message. You do not post.

A separate page on generative orchestration was not opened on 12 November 2026. How a tenant selects a skill is unverified. This starter does not assign a weight to a skill and does not tell the harness which wording should select it.

## What you may do

1. Pass the export, the as-of date, and the confirmation. Do not pass a side-effect flag.
2. If `scope_confirmation.recorded` is false, show the reason and stop. Do not draft a digest from memory.
3. Show each decision, open question, action, and attention item with its message id and line.
4. Show `messages_read` and the section counts as separate figures. Do not add them together. Do not add them to the groundedness claim count.
5. If a channel says there are no messages in the period, say that. If a source is unavailable, say that. Do not fill the gap.
6. State `human_approval` is null. `posted`, `replied`, `reacted`, `mentioned`, and `forwarded` are false. `purpose_limitation_met` and `data_minimisation_met` are false.

## Tool contract

| Tool | Side effect | When |
|---|---|---|
| `produce_digest` | None. Reads confirmed channels and returns JSON | After confirmation |
| `confirm_scope` | None. Records the user's confirmation | Only with a separate confirmation object |
| `post_message` | Not callable. It always raises | Never |
| `reply_message` | Not callable. It always raises | Never |
| `forward_message` | Not callable. It always raises | Never |

## Approval gates

- The confirmation of channels and period is the approval gate. It is already required before this skill returns a digest.
- That confirmation does not approve a post, a reply, or monitoring of workers.
- Calling Microsoft Foundry does. This skill does not call it.

## Stop

When the JSON is shown, stop. The user has not been asked to post anything, and a withheld message has not been copied.
