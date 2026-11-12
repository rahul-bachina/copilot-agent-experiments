---
name: preview-channel-scope
description: Use when a person has named Teams channels and a period and needs the scope checked before any digest is produced.
---

# Preview the channel scope

This skill is for the Copilot Studio GitHub Copilot harness. It is instructions for that harness, not a GitHub Copilot repository skill and not the GitHub Copilot service.

You call `preview_scope`, which runs `preview_scope()` in `src/digest.py`. You do not reimplement the access check. You do not produce a digest. Autonomy A3 is never a recommendation.

A separate page on generative orchestration was not opened on 12 November 2026. How a tenant selects a skill is unverified. This starter does not assign a weight to a skill and does not tell the harness which wording should select it.

## What you may do

1. Pass the synthetic export and the as-of date. Do not pass `--post`, `--reply`, `--react`, `--mention`, or `--forward`.
2. Show the label `DRAFT TEAMS CHANNEL DIGEST. NOT POSTED. NOT A MONITORING DECISION.`
3. Show each channel's status and, where the user can access it, the message count. Do not show message text.
4. Say plainly when a source is unavailable or a period has no messages. Do not invent messages.
5. State `digest_produced` is false and `scope_confirmed` is false. `human_approval` is null.

## Tool contract

| Tool | Side effect | When |
|---|---|---|
| `preview_scope` | None. Reads the export and returns JSON | When the scope has not been confirmed |
| `post_message` | Not callable. It always raises | Never |
| `reply_message` | Not callable. It always raises | Never |
| `react_message` | Not callable. It always raises | Never |
| `mention_user` | Not callable. It always raises | Never |
| `forward_message` | Not callable. It always raises | Never |

## Approval gates

- Viewing the scope does not need approval.
- Confirming the channels and the period does. You do not record that confirmation in this skill.
- Posting does. You do not post.

## Memory

Do not write the export into agent memory. The harness overview opened on 12 November 2026 says this harness supports memory. An administrator control to turn memory off was not on that page. Do not use it for this preview.

## Stop

When the scope JSON is shown, stop. The user has not confirmed the channels, and nothing has been posted.
