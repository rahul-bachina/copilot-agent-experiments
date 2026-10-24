---
name: draft-clarification-letter
description: >
  Show the clarification letter already present in a triage result. Use when
  staff ask for the draft letter. Do not write a new letter the core did not
  produce, and do not send it.
---

# Show the draft clarification letter

Harness: Copilot Studio **GitHub Copilot harness** (the Copilot Studio framework, not the GitHub Copilot service).

Use this skill only after `run_triage` has returned JSON for this submission. The letter is a field on that JSON. It is not a new analysis.

The `name` and `description` are the skill fields Microsoft describes. The gate below is the manifest's gate. It is not a new approval step.

## Tool contract

No second tool. Read `cost_limit_assessment.draft_clarification_letter` from the JSON `run_triage` already returned.

| | |
|---|---|
| Side effect | None. No send. No write to a case system or a mailbox. |
| Input | The triage JSON for this submission. Do not pass the requester's identity, and do not open email. |
| Output | The letter string the core produced, or a statement that the core did not produce one. |
| Approval to show the draft | Not required. Viewing triage output has no external effect. |
| Approval to send | Mandatory. Approver: FOI/Complaints Officer. The action in the manifest is "Send clarification letter". You cannot record that approval, and you cannot perform the send. |

If the field is missing or empty, say: "No clarification letter was generated for this submission as it appears appropriately scoped." Do not draft a replacement. Do not ask the model, or the code interpreter, to invent one.

If the core did produce a letter, show it and mark it as a draft for the officer to edit. Do not accuse the requester of using a template or of using AI. Do not promise a response timescale. Do not give legal advice.

## Approval gates

| Act | Approval |
|---|---|
| View triage output, including this letter | Not required |
| Send clarification letter | Mandatory. Approver: FOI/Complaints Officer. Outside the agent. |
| Accept triage classification | Mandatory before anyone relies on the classification that led to the letter. Approver: FOI/Complaints Officer. Unchanged from the triage skill. |

## Sandbox file

If staff ask for a file, you may create a Word or PDF copy in the sandbox because this harness can create those files. The first line is that the letter has not been sent. Creating the file does not need approval. Emailing it or saving it into a case system does, and you have no tool for either.

## Memory

Do not store the letter or the submission for a later requester. Memory (preview) is documented for this harness. This skill does not use it.

## Stop

Stop after the draft is shown. The FOI/Complaints Officer reviews, edits, and sends through the authority's normal channel.
