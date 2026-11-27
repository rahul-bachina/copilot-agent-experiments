---
name: hand-to-human
description: Hand the turn to a human advisor and keep the cue text off the result. Use when the customer asks for a person, or the turn has a vulnerability, complaint, affordability, distress, or prohibited-action cue. Do not answer those turns from the knowledge base.
---

# Hand the turn to a person

This skill calls `answer()` in `src/customer.py`. The handover record uses the same fields as Experiment 13. Council triage is not called.

The `name` and `description` above are the skill fields. This file does not list phrases for selection, and it does not assign weights.

## When to use this skill

Use it when the customer asks for a person, or the message or the notes contain a vulnerability, affordability, debt, disconnection, prepayment, complaint, distress, safeguarding, whistleblowing, grievance, subject access, or freedom of information cue, including a paraphrase. A stated category does not drop a flag derived from the text.

## Tool contract: `answer`

| | |
|---|---|
| Implementation | `answer()` in `src/customer.py`. |
| Input | One synthetic request and the date the question is about. |
| Output | `outcome` of `human_handover`, `routine_queue` false, and a handover record. |
| Side effect | None. The cue text is not copied. Nothing is submitted. |
| Approval to run | The human advisor takes the turn. The agent does not decide it. |
| What it does not do | It does not add anyone to the Priority Services Register or agree a payment plan. |
