---
name: list-material-discrepancies
description: "Use when a reviewer wants only the material discrepancies, each with a pinpoint citation, still unresolved."
---

# List material discrepancies

This skill is for the Copilot Studio GitHub Copilot harness. It is instructions for that harness, not a GitHub Copilot repository skill and not the GitHub Copilot service.

You filter the draft to rows whose class is `material_discrepancy`. You do not choose which source is right, you do not edit a record, and you do not contact anyone. Autonomy A3 is never a recommendation.

The skills overview opened on 5 November 2026 says the orchestration runtime invokes a skill when a request matches the skill's purpose, from the user's message and the skill's description. This starter does not assign routing weights. It does not use trigger phrases as the selector. A page that describes classic orchestration was not opened.

## What you may do

1. From the draft already produced, list each material fact: the reason, `other_reasons`, and every citation.
2. Say `other_reasons` are not extra facts and are not added to `material_count`.
3. Say `resolved` is false unless a Reviewer object was supplied outside this skill. You do not supply that object.
4. Say `correct_value` is null. Do not propose a replacement value.
5. If `do_not_rely` is true, say so. Do not clear it.
6. Do not drop the immaterial rows from the draft. This skill only changes what you show. The counts stay as the Python returned them.

## Tool contract

| Tool | Side effect | When |
|---|---|---|
| `list_material_discrepancies` | None. Reads the draft | When the reviewer wants the material rows only |
| `choose_source` | Not callable. It always raises | Never |
| `edit_record` | Not callable. It always raises | Never |
| `contact_party` | Not callable. It always raises | Never |
| `lookup_register` | Not callable. It always raises | Never |
| `record_reviewer_resolution` | Not an agent tool | Never |

## Approval gates

- Showing the material rows does not resolve them.
- The reviewer resolves every material discrepancy.
- A correction, a contact, and a register lookup stay outside this agent.

## Memory

Do not write material rows into agent memory. The harness overview opened on 5 November 2026 says this harness supports memory. An administrator control to turn memory off was not on that page. Do not use it for this list.

## Stop

When the material rows are shown, stop. They are still unresolved unless the reviewer recorded a choice outside this skill.
