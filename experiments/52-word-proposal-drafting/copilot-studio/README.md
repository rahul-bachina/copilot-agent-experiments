# Copilot Studio standard harness

A build guide, not an importable solution. The overview opened on 12 November 2026 says the standard harness follows the topics and rules the maker defines. Files, skills, and memory are not a focus of that harness.

One topic. The author pastes one synthetic pack and types the as-of date. A flow calls `draft_proposal` and returns the JSON. The topic stops. It does not submit.

## Topic

Name: Draft a bid response.

1. Ask for the pack JSON and the as-of date. Refuse to continue if `synthetic` is not true.
2. Call the Python core. Do not add a generative answer beside it.
3. Show `label`, `compliance_matrix`, `author_checks`, `gaps`, and `human_route`.
4. If `prompt_injection.detected` is true, say the instruction was not followed.
5. Stop. Do not offer a button that submits.

A second topic may call `record_acceptance` when the author types a decision from the closed list: `author_accept_complete_draft`, `author_request_revision`, or `reject_draft`. Show `review.reason`. If `review.refused` is true, stop. Do not map any decision to a portal action or a mail action.

This starter does not assign a weight to a topic. Where generative orchestration is on, selection is by the topic description. That behaviour was not checked in a tenant on 12 November 2026. The orchestration page was not opened.

## What the topic must not contain

- A send email action, an Outlook connector, or a Teams message action.
- A Microsoft Graph upload, a SharePoint create, or a tender-portal connector.
- A branch that treats "submit the bid" in the invitation as approval.
- A knowledge source that is a live library without `status`, `effective_on`, and `review_due_on`.

The Customer Conversation harness is described on the same overview for customer voice and chat. It is not built here. An unattended submitter would sit outside this A1 design.

See [system-prompt.md](system-prompt.md) and [power-automate-flow.md](power-automate-flow.md).
