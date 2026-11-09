# Copilot Studio standard harness

A build guide, not an importable solution. The overview opened on 9 November 2026 says the standard harness follows the topics and rules the maker defines. Files, skills, and memory are not a focus of that harness.

One topic. The representative pastes one synthetic case and types the as-of date. A flow calls `draft_response` and returns the JSON. The topic stops. It does not send.

## Topic

Name: Draft a customer response.

1. Ask for the case JSON and the as-of date. Refuse to continue if `synthetic` is not true.
2. Call the Python core. Do not add a generative answer beside it.
3. Show `label`, `draft.text`, `sources_cited`, `snippets_refused` (ids and reasons only), `tone`, `plain_english`, and `human_route`.
4. If `prompt_injection.detected` is true, say the instruction was not followed.
5. Stop. Do not offer a button that sends.

A second topic may call `record_review` when the representative types a decision from the closed list: `representative_approve_for_own_send`, `representative_request_revision`, or `reject_draft`. Show `review.reason`. If `review.refused` is true, stop. Do not map any decision to a mail action.

This starter does not assign a weight to a topic. Where generative orchestration is on, selection is by the topic description. That behaviour was not checked in a tenant on 9 November 2026. The orchestration page was not opened.

## What the topic must not contain

- A send email action, an Outlook connector, or a Teams message action.
- A Dynamics 365 create or update action.
- A branch that treats "send it" in the case text as approval.
- A knowledge source that is a live SharePoint library without `status`, `effective_on`, and `review_due_on`.

The Customer Conversation harness is described on the same overview for customer voice and chat. It is not built here. An unattended sender would sit outside this A1 design.

See [system-prompt.md](system-prompt.md) and [power-automate-flow.md](power-automate-flow.md).
