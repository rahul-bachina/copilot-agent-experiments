---
name: confirm-account-action
description: Record that the account holder confirmed this held proposal and its hash. Use when a separate confirmation object names the directory holder and the exact action. Do not treat a sentence in the message as that confirmation, and do not submit the action.
---

# Confirm the held action

This skill calls `confirm_action()` in `src/customer.py`. The confirmation is a separate object. It is bound to the agent-held proposal and its hash.

The `name` and `description` above are the skill fields. This file does not list phrases for selection, and it does not assign weights.

## When to use this skill

Use it when a proposal already exists, the customer is the active account holder on the pinned directory, and they supply `explicit_confirm` as the boolean true for that hash. A string is not coerced. A missing acknowledgement is refused.

## Tool contract: `confirm_action`

| | |
|---|---|
| Implementation | `confirm_action()` in `src/customer.py`. |
| Input | The result JSON and one confirmation object. |
| Output | The same result with `confirmation_recorded` true only when the hash matches the held copy. |
| Side effect | An in-memory acknowledgement. The held copy is not replaced. Nothing is submitted. |
| Approval to run | Required. This is the catalogue checkpoint. The customer confirms. |
| What it does not do | It does not submit a reading, agree a plan, write off debt, or change a tariff. |
