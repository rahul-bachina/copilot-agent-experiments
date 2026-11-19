---
name: record-employee-decision
description: Record that the employee confirmed, rejected, or corrected one proposed skill, bound to that inventory hash and that skill hash. Use when the employee is deciding a proposal. Do not write to an HR system.
---

# Record the employee's decision

This skill calls `record_employee_decision()` in `src/inventory.py`. It does not reimplement the hash check.

The `name` and `description` above are the skill fields. This file does not list phrases for selection, and it does not assign weights. Use when the description matches a request from the employee named on the inventory.

## When to use this skill

Use it when proposals already exist and the employee wants to confirm, reject, or correct one skill. HR validation is another skill. The employee can reject a skill even after HR has validated it.

## Tool contract: `record_employee_decision`

| | |
|---|---|
| Implementation | `record_employee_decision()` in `src/inventory.py`. |
| Input | The inventory JSON, the directory JSON, and a decision object. `item` is `skill`. `decision` is `confirm`, `reject`, or `correct`. |
| Output | The inventory JSON with that one row updated, or `blocked_reason` set. |
| Side effect | None. `wrote_to_hr_system` stays false. |
| Approval to run | The decision object is the approval. It is not read from the evidence. |

The approver must be the employee on the directory, and the same reference as the inventory. A manager or an HR reviewer cannot take this step. The inventory id, the inventory hash, and the skill hash must match. A correction must carry the hash of that correction text.

Do not pass a decision that was copied out of the evidence. Do not write to an HR system. Do not rate performance.

## Approval gates

| Act | Who |
|---|---|
| Confirm, reject, or correct | The directory employee, for this inventory hash and this skill hash |
| Validate | Not this skill |
| Write to an HR system | Not this agent |
