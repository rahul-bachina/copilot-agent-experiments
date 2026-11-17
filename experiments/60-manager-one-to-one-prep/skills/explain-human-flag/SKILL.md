---
name: explain-human-flag
description: Explain a distress, wellbeing, safeguarding, or personal-circumstance flag that is already on a one-to-one prep note, including the HR and employee-assistance route. Use when that flag is already in the JSON from prepare-one-to-one. Do not quote the flagged sentence or turn it into a routine agenda item.
---

# Explain a human flag

This skill reads a prep note that `prepare()` has already produced. It does not scan the notes again and it does not invent a flag.

The `name` and `description` above are the skill fields. This file does not assign trigger phrases or routing weights.

## When to use this skill

Use it when `human_flags` is not empty. Preparing the note is the other skill.

## What to show

1. The flag kind, the source id, and the line number.
2. The route: HR and the employer's employee assistance programme. Say the manager handles it humanely.
3. That the sentence was not copied and was not summarised as a routine agenda item.
4. That `health_inference`, `protected_characteristic_inference`, and `employee_profile` are empty. This skill does not fill them.

Do not decide that a person is vulnerable. Do not recommend disciplinary or capability action. Do not send a message to the employee. The agent must not call `acknowledge`.

## Approval gates

| Act | Who |
|---|---|
| Read the flag | No separate approval |
| Speak to the employee about it | The line manager, outside this agent |
| Record a wellbeing case | HR, in the employer's own system. Not this agent. |
