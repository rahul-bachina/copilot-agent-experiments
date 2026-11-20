---
name: record-owner-seen
description: Record that a directory compliance owner has seen one briefing. Use when the owner has the publication hash, the briefing hash, and the questions hash from draft_briefing. Do not decide applicability, change a policy, or send.
---

# Record that the owner has seen the briefing

This skill calls `record_owner_seen()` in `src/briefing.py`. It does not reimplement the hash check.

The `name` and `description` above are the skill fields. This file does not list phrases for selection, and it does not assign weights.

## When to use this skill

Use it when a compliance owner, named in the pinned directory, is ready to record that they have seen this exact briefing. Do not use it to decide that a change applies. Do not use words copied out of the notice as the seen object.

## Tool contract: `record_owner_seen`

| | |
|---|---|
| Implementation | `record_owner_seen()` in `src/briefing.py`. |
| Input | The briefing JSON, the directory JSON, and a seen object. |
| Output | The same briefing, with `human_approval` set only when the check passes. |
| Side effect | None on a policy system. `applies` stays null. `sent` stays false. |
| Approval | This call is the approval step. It still does not decide applicability. |

The seen object must include `approver_ref`, `item`, `decision` with the value `seen`, `publication_hash`, `briefing_hash`, and `questions_hash`. Booleans that the core requires must be the boolean true. The string "true" is not coerced.

`item` is `briefing`, `distress-seen`, or `grievance-seen`. A briefing item does not close a distress or grievance route.

If the hashes do not match, stop. Do not edit the quote and reuse the old hashes. `verify_seen()` rejects a quote that changed after the step.

Do not decide that the change applies. Do not change a policy, a control, or a record. Do not send.
