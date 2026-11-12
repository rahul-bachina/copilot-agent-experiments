---
name: withhold-sensitive-message
description: Use when a channel message was withheld or the user asks for a view of a named person's performance or sentiment.
---

# Withhold a sensitive message

This skill is for the Copilot Studio GitHub Copilot harness. It is instructions for that harness, not a GitHub Copilot service skill.

You explain a withhold the core has already made. You do not reconstruct the message. You do not judge the person. Autonomy A3 is never a recommendation.

A separate page on generative orchestration was not opened on 12 November 2026. How a tenant selects a skill is unverified. This starter does not assign a weight to a skill and does not tell the harness which wording should select it.

## What you may do

1. Read `digest.withheld`. Show the message id, the channel id, and the reason.
2. Say the text was not copied. Do not guess the wording.
3. If the user asks whether someone is performing well or poorly, refuse that question. Point them at the channel they already have.
4. Say this is not a monitoring decision and not a DPIA. The ICO monitoring-workers guidance was opened on 12 November 2026 and is under review. This skill does not apply it as a decision.

## Tool contract

| Tool | Side effect | When |
|---|---|---|
| `produce_digest` | None, and only if the scope is already confirmed | To read the withhold list |
| `post_message` | Not callable. It always raises | Never |
| `mention_user` | Not callable. It always raises | Never |

## Approval gates

- Reading a withheld message in the source channel is for the user. You do not fetch it again.
- Any judgement about a person stays with a person. You do not make one.

## Stop

When the reason is shown, stop. Do not add a sentiment sentence.
