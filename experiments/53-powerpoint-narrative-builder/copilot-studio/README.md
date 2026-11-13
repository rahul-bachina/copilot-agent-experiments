# Copilot Studio standard harness

A build guide, not an importable solution. The overview opened on 13 November 2026 says the standard harness follows the topics and rules the maker defines. Files, skills, and memory are not a focus of that harness.

One topic. The presenter pastes one synthetic pack and types the as-of date. A flow calls `propose_outline` and returns the JSON. The topic stops. It does not share.

## Topic

Name: Propose a slide outline.

1. Ask for the pack JSON and the as-of date. Refuse to continue if `synthetic` is not true.
2. Call the Python core. Do not add a generative answer beside it.
3. Show `label`, `key_message`, `claims`, `gaps`, `accessibility`, `markings`, and `human_route`.
4. If `prompt_injection.detected` is true, say the instruction was not followed.
5. If `safeguarding.flagged` is true, say a person has to see that point. Do not put it on a slide.
6. Stop. Do not offer a button that publishes or shares.

A second topic may call `record_presenter_approval` when the presenter types a decision from the closed list: `presenter_approve_outline_and_citations`, `presenter_request_revision`, or `reject_outline`. Show `review.reason`. If `review.refused` is true, stop. Do not map any decision to a mail action or a site action. A recorded approval does not produce slides.

A third topic may call `produce_slides` only after that record, and only when the presenter asks for the local file. Tell them the file is not shared.

This starter does not assign a weight to a topic. Where generative orchestration is on, selection is by the topic description. That behaviour was not checked in a tenant on 13 November 2026. The orchestration page was not opened.

## What the topic must not contain

- A send email action, an Outlook connector, or a Teams message action.
- A Microsoft Graph upload, a SharePoint create, or a publish-to-site connector.
- A branch that treats "share the deck" in the briefing as approval.
- A knowledge source that is a live briefing without a review date.

The Customer Conversation harness is described on the same overview for customer voice and chat. It is not built here. An unattended sender would sit outside this A1 design.

See [system-prompt.md](system-prompt.md) and [power-automate-flow.md](power-automate-flow.md).
