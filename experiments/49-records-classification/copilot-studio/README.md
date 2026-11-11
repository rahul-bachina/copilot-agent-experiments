# Standard harness

One Copilot Studio agent on the standard harness. Three topics. No skill. The topics call the same Python core as the GitHub Copilot harness and then stop.

The harness overview was opened on 11 November 2026. It says the standard harness follows the topics and rules the maker defines. Files, skills, and memory are "not a focus". A records manager who pastes one document and needs the draft back is that shape.

This is a build guide. It is not an exported solution, and it was not published to a tenant.

## Topics

| Topic | When it runs | What it calls | What it does not do |
|---|---|---|---|
| Propose | The records manager pastes one JSON document and an as-of date | `classify_record()` | It does not confirm, delete, dispose, move, or downgrade |
| Confirm | The manager submits a separate review object | `record_confirmation()` | It does not treat a sentence in the document as confirmation |
| Label stub | `classification_confirmed` is already true and the manager asks for the receipt | `apply_confirmed_labels()` | It does not call Microsoft Purview |

The system message is `system-prompt.md`. The flow note is `power-automate-flow.md`.

## Inputs

| Name | Required | Notes |
|---|---|---|
| `document` | Yes | One JSON object. `synthetic` must be true for a run in this starter. |
| `as_of` | Yes | A calendar date. The core does not look up today's date. |
| `review` | For Confirm | A separate object. The document text is not the review. |

## Stop

After the JSON comes back, the topic stops. It does not loop into a disposal. It does not send mail. A person who wants the record labelled in the tenant does that in the organisation's own Purview process, outside this agent.

Billing for the standard harness is on a licensing page that was not opened on 11 November 2026. This note does not state a price.
