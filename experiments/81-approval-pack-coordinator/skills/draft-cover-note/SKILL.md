---
name: draft-cover-note
description: Draft the cover note that lists what is present, missing, or stale and what was checked. Use when the named approver is about to read the pack. Do not decide the request.
---

# Draft the cover note

This skill reads `cover_note` on the draft. It does not add a decision.

The `name` and `description` above are the skill fields. This file does not list phrases for selection, and it does not assign weights.

## When to use this skill

Use it when the draft has been assembled and the approver needs one note of what is present, what is missing or stale, and which checks ran. The note is part of the held hash.

## Tool contract

| | |
|---|---|
| Implementation | `cover_note` inside `assemble_pack()`. |
| Input | The draft JSON. |
| Output | The cover note already on the draft. |
| Side effect | None. |
| Approval to run | Not required. |
| Approval to rely on it | Required. The named approver reads the note before deciding. |

Phone numbers, email addresses, dates of birth, postal addresses, and personal names in an excerpt are masked. The raw excerpt is not stored. The output is not described as anonymised.
