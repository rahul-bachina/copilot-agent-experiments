---
name: propose-account-action
description: Propose a meter-reading submission, a payment-plan request, or a Priority Services Register referral. Use when the customer asks for one of those actions and no vulnerability or affordability cue is present. Do not submit the action.
---

# Propose an account action

This skill calls `answer()` in `src/customer.py`. A proposal is not a submission. The customer still has to confirm the held copy.

The `name` and `description` above are the skill fields. This file does not list phrases for selection, and it does not assign weights.

## When to use this skill

Use it when the message asks for one meter reading, one payment-plan request, or one Priority Services Register referral, and the turn has no vulnerability, affordability, debt, disconnection, or prepayment cue. Two actions at once are not chosen. A hardship cue with a plan request goes to a person.

## Tool contract: `answer`

| | |
|---|---|
| Implementation | `answer()` in `src/customer.py`. |
| Input | One synthetic request and the date the question is about. |
| Output | `outcome` of `propose_action` and one `proposed_action`, or a handover. |
| Side effect | The proposal and its hash are held in memory for this process. Nothing is submitted. |
| Approval to run | Not required. The customer's confirmation is a later step. |
| What it does not do | It does not agree a plan, add a register entry, or submit a reading. |
