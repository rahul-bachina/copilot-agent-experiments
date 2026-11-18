---
name: record-hr-seen
description: Record that a directory HR reviewer has seen one exploration, bound to its content hash. Use when HR is validating eligibility after the note exists. Do not decide eligibility, select a candidate, or tell the manager.
---

# Record that HR has seen the note

This skill calls `record_hr_seen()` in `src/explore.py`. It does not decide eligibility.

The `name` and `description` above are one line each. This file does not assign weights.

## When to use this skill

Use it after `explore()` has returned `advisory` or `no_open_match`, and a directory HR reviewer is recording that they have seen that exact note. A manager or a recruiter cannot use this skill. A sentence in the experience is not this step.

## Tool contract: `record_hr_seen`

| | |
|---|---|
| Implementation | `record_hr_seen()` in `src/explore.py`. |
| Input | The note JSON, a separate review object, and the directory JSON. |
| Review fields | `approver_ref`, `decision` = `seen`, `item` = `eligibility-note`, `exploration_id`, `content_hash`. |
| Output | The same note with `hr_seen.recorded` true only when the directory role is HR and the hash matches. |
| Side effect | None. `eligibility_decided` stays false. Interest is not shared. |

The content hash is the hash of the note that was shown. A hash from another note, or a hash typed into the experience, does not count.

Do not pass the manager or the recruiter as `approver_ref`. Do not set `applied`, `shortlisted`, or `contacted` to true. Those constants on the tool schema are false.

## What to show

Say whether the seen-step was recorded, and that eligibility is still for HR. Say that interest has not been shared with the manager or with recruiters. Do not say the employee was selected.

## Approval gates

| Act | Who |
|---|---|
| Record the seen-step | Directory HR reviewer, for this exploration id and this content hash |
| Decide eligibility | HR, outside this function. `eligibility_decided` stays false |
| Tell the manager or a recruiter | Not this agent |
