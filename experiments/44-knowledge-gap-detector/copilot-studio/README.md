# Copilot Studio standard harness

A build guide, not an importable solution. The overview opened on 10 November 2026 says the standard harness follows the topics and rules the maker defines. Files, skills, and memory are not a focus of that harness.

One topic. The knowledge manager pastes one synthetic pack and types the as-of date. A flow calls `detect_gaps` and returns the JSON. The topic stops. It does not publish.

## Topic

Name: Review knowledge gaps.

1. Ask for the pack JSON and the as-of date. Refuse to continue if `synthetic` is not true.
2. Call the Python core. Do not add a generative answer beside it.
3. Show `label`, `gaps`, `findings` (ids and reasons), `outlines` (ids and sections), and `human_route`.
4. If `prompt_injection.detected` is true, say the instruction was not followed and that a question beside it was kept.
5. Stop. Do not offer a button that publishes.

A second topic may call `record_confirmation` when the manager types a decision from the closed list: `confirm_gap`, `reject_gap`, or `defer`. Show `review.reason`. If `review.refused` is true, stop. Do not map any decision to a knowledge-article action.

This starter does not assign a weight to a topic. Where generative orchestration is on, selection is by the topic description. That behaviour was not checked in a tenant on 10 November 2026. The orchestration page was not opened.

## What the topic must not contain

- A publish, update, or delete action against a knowledge article.
- A Dynamics 365 or Microsoft Fabric write action.
- A send email action.
- A branch that treats "publish the article now" in the pack as confirmation.
- A knowledge source that is a live library without `status`, `effective_from`, and `review_due`.

The Customer Conversation harness is described on the same overview for customer voice and chat. It is not built here. An unattended publisher would sit outside this A0 design.

See [system-prompt.md](system-prompt.md) and [power-automate-flow.md](power-automate-flow.md).
