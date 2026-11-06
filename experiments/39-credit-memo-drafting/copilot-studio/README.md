# Standard harness

This is a build guide for the Microsoft Copilot Studio standard harness. It is not an importable solution. It is not the GitHub Copilot service.

One topic. The credit officer pastes a synthetic pack and an as-of date. A flow calls `draft_memo()` and returns the JSON. The topic stops. It does not approve or decline credit, set a limit, contact the customer or a bureau, post a core banking or CRM system, or file a SAR.

The harness overview opened on 6 November 2026 uses "standard harness" for a rule-based agent that follows topics and rules the maker defines. The generative-orchestration guidance opened the same day uses the words "Standard harness (planner)" for an LLM planning layer. Those two uses were not identified as the same component. Treating them as the same component is unverified. This topic does not list trigger phrases and does not assign routing weights. The guidance does not describe numeric routing weights.

The page describes autonomous triggers. This starter does not use them.

## Topic

1. Ask for the pack and the as-of date. Refuse a pack that is not marked synthetic.
2. Call the flow. Do not pass an approve, decline, limit, contact, post, or SAR flag.
3. Show the label `DRAFT FOR THE CREDIT OFFICER. NOT A CREDIT DECISION AND NOT A LIMIT.`
4. Show each fact with its citation and verdict, then the gaps as not stated.
5. Show the counts separately. Do not add them. Do not add comparison counts to stated facts.
6. State that `credit_decision`, `recommendation`, and `limit_set` are null, and that `sar_filed` is false.
7. Stop. The credit officer reviews every cited fact before any use. That approval is outside the topic.

Instructions to paste are in [system-prompt.md](system-prompt.md). A flow sketch is in [power-automate-flow.md](power-automate-flow.md).
