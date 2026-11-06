# Architecture

One enquiry in. One JSON draft out. The same inputs produce the same JSON.

```
Customer or handler
        |
        | one synthetic enquiry, as-of date
        v
Copilot Studio
  standard harness (one topic)
  or GitHub Copilot harness (four skills)
        |
        | no model chooses the page
        v
src/service.py  draft_reply()
        |
        +--> Experiment 08 propose()     identifiers counted, text not copied
        +--> Experiment 02 analyse()     financial-services complaint or
        |                                 vulnerability only; no DISP clock
        +--> src/catalogue.py            fixed pages, 180-day stale window
        +--> src/identity.py             portal session or not trusted
        +--> src/injection.py            instructions recorded, not followed
        |
        v
Draft
  human_approval = null
  human_route.offered = true
  record_changed = false
  message_sent = false
        |
        | separate review object
        v
record_review()
  customer confirms an address or appointment draft
  handler takes a handover
  handler approves a correspondence draft for their own channel
        |
        v
Still no write, no booking, no send.
The person acts in the organisation's own system, if they decide to.
```

## Why the core is deterministic

The page, the stale flag, the identity flag, and the empty approval are comparisons. A language model will not make the same comparison twice from the same words, and it must not be the thing that decides a record has changed. Experiment 21 uses the same split for an IT ticket. This starter uses it for a customer enquiry.

Experiment 13's warm handover is the reason every result offers a person and a non-digital counter, including a refusal. Experiment 02's complaint gate is the reason a financial-services complaint is a suggestion for a handler, not a closure. Experiment 09's correspondence approval is the reason a handler can approve a draft and the agent still cannot send it.

## What is not in the picture

Dynamics 365 is not connected. Microsoft Foundry is an optional narrative around the JSON, described in [foundry.md](foundry.md), and it is not deployed. The Customer Conversation harness is not built. See [harness-comparison.md](harness-comparison.md).

## Diagram

[architecture_diagram.png](architecture_diagram.png) is the same picture, rendered for the briefing site. `generate_diagram.py` draws it. Matplotlib is used only by that script. It is not a runtime dependency.
