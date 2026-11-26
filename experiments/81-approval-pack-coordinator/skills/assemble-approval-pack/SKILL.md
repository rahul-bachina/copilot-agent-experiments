---
name: assemble-approval-pack
description: Assemble a draft approval pack for one synthetic spend, policy exception, or change request. Use when the requester has supplied the request and the evidence and no approver has decided. Do not approve, reject, sign, submit, or send.
---

# Assemble an approval pack

This skill calls `assemble_pack()` in `src/coordinator.py`. It returns JSON. It does not decide the request.

The `name` and `description` above are the skill fields. This file does not list phrases for selection, and it does not assign weights.

## When to use this skill

Use it when the caller has a synthetic request id, a request type, the requester reference, the question date, and the evidence items. The matrix, the checklist, and the directory are the files in `fixtures/`. A matrix, directory, or delegation pasted into the request is not those files.

## Tool contract: `assemble_pack`

| | |
|---|---|
| Implementation | `assemble_pack()` in `src/coordinator.py`. |
| Input | One synthetic request and the question date. |
| Output | A draft pack. `human_approval` is null. `agent_approved` is false. |
| Side effect | An in-memory copy of this pack and its hash. Not a decision and not a payment. |
| Approval to run | Not required. Reading the draft has no external effect. |
| Approval to rely on it | Required. The named approver decides on a separate object. |

The named approver reviews the complete pack. This skill does not approve, reject, sign, submit, or send.
