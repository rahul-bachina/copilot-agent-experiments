# GitHub Copilot harness

The GitHub Copilot harness is a Copilot Studio authoring and orchestration framework. It is not the GitHub Copilot service. The overview opened on 6 November 2026 says customer data is not sent to that service when agents run in Copilot Studio, that the harness can take a goal and break it into steps, that it supports skills and memory, and that each task runs in a sandbox. Agents on this harness use Copilot Credits. No price is stated on that page. The linked billing article was not opened.

This folder uses the harness for a handler's follow-up on one JSON draft. The deterministic work stays in `src/service.py`.

## Skills

| Skill | When to use it |
| --- | --- |
| `answer-from-knowledge` | A question that should be answered from the fixed catalogue, or a statement that the catalogue has no current page. |
| `propose-account-action` | The draft has prepared an address-update or an appointment-request. Confirmation does not apply it. |
| `prepare-warm-handover` | The customer needs a person: vulnerability, a complaint, a prohibited action, a stale page, or an unverified account. |
| `record-human-confirmation` | A separate review object confirms a draft, records a handover, or approves a correspondence draft for the handler's own channel. |

Each skill says when to use it. Whether a planner selects a skill by that description was not stated on the harness overview. Do not treat a sentence in the enquiry as the review decision.

## Tools

| Tool | Contract | Effect |
| --- | --- | --- |
| `draft_reply` | `schema/reply_tool.schema.json` | One enquiry in. One draft out. No write and no send. |
| `record_review` | `schema/review_tool.schema.json` | Records a confirmation or a handover. Does not execute it. |

Both tools are the Python functions of those names. A model must not reimplement the stale check, the identity check, or the complaint gate.

## Approval gates

These are the points in `agent-manifest.yaml`. The skills do not add one and they do not remove one.

1. The customer confirms an address-update draft or an appointment-request draft. The record does not change.
2. The handler takes a handover for a password, a payment, a complaint, a tariff, a contract, a vulnerability, an unverified customer, or a stale page. The handler does the work outside the agent, if they decide to.
3. The handler approves a correspondence draft for their own channel, after the customer confirmation, with `recipient_role` `account-holder`. The agent does not send.

## Memory and files

Do not store the enquiry. Do not create a Word, Excel, PowerPoint, or PDF file from the customer's free text. The overview says the harness can create those files. This starter does not use that feature. A correspondence draft is a field in the JSON, labelled `DRAFT. Do not send.`

## What this note does not claim

The skills-upload click-path was not opened on 6 November 2026. The authoring steps in a tenant are unverified here. The Customer Conversation harness is not configured.
