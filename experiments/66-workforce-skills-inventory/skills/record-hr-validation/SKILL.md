---
name: record-hr-validation
description: Record that HR validated one skill the employee has already confirmed or corrected, bound to that hash. Use when HR is looking at a skill the employee has decided. Do not write to an HR system or rate performance.
---

# Record HR validation

This skill calls `record_hr_validation()` in `src/inventory.py`. It does not reimplement the hash check.

The `name` and `description` above are the skill fields. This file does not list phrases for selection, and it does not assign weights. Use when the description matches a request from HR about a skill the employee has already decided.

## When to use this skill

Use it after the employee has confirmed or corrected one skill. A rejected skill cannot be validated. Validation does not write to an HR system and does not set a performance rating. The employee can still reject the skill afterwards.

## Tool contract: `record_hr_validation`

| | |
|---|---|
| Implementation | `record_hr_validation()` in `src/inventory.py`. |
| Input | The inventory JSON, the directory JSON, and a validation object. `item` is `skill-validation`. `decision` is `validate`. |
| Output | The inventory JSON with `hr_validated` true for that row, or `blocked_reason` set. |
| Side effect | None. `wrote_to_hr_system` stays false. `performance_rating` stays null. |
| Approval to run | The validation object is the approval. It is not read from the evidence. |

The approver must be HR on the directory. A manager cannot take this step. For a confirmation, the skill hash must match. For a correction, the correction hash must match.

Do not write to an HR system. Do not rate performance. Do not decide pay, promotion, redundancy, or discipline.

## Approval gates

| Act | Who |
|---|---|
| Validate one decided skill | The directory HR reviewer, for this inventory hash and the skill hash or the correction hash |
| Override a rejection | Not this agent |
| Write to an HR system | Not this agent |
