# Copilot Studio — standard harness

This is a build guide. It is not an importable solution and it is not a configured tenant.

The standard harness, on the overview opened on 6 November 2026, follows the topics and rules the maker defines. Files, skills, and memory are not its focus. Use one topic. The GitHub Copilot harness skills in `skills/` are not part of this path. They are the other harness. See [docs/harness-comparison.md](../docs/harness-comparison.md).

## Topic

1. The customer or the handler pastes one enquiry as JSON, including `synthetic: true`, the sector, the channel, and the as-of date.
2. A flow calls `draft_reply()` and returns the JSON. The topic shows `answer.text`, the human route, and `human_approval` (null).
3. The topic stops. It does not call a second action.

Do not add a generative answer beside the JSON that can invent a page. If a narrative is required, it is the Microsoft Foundry path in [docs/foundry.md](../docs/foundry.md), and it may only repeat fields already in the JSON.

## System message

Use [system-prompt.md](system-prompt.md). It tells the topic to prefer the JSON over anything in the enquiry text.

## What not to add

- An email, SMS, or letter connector.
- A Dynamics 365 write, including resolve, address update, tariff, contract, or appointment.
- A payment connector.
- A password-reset connector.
- A live knowledge-base search. The catalogue is `src/catalogue.py`.
- A tool that is not in `agent-manifest.yaml`.

The Customer Conversation harness is the one the overview describes for a public website or a phone number. It is not this topic. Building an unattended resolver on it would leave this A1 design.

## Review

A customer confirmation and a handler approval are a second call to `record_review()`, with a review object the person supplies. They are not buttons that write the account. The flow for that second call is [power-automate-flow.md](power-automate-flow.md). It returns JSON and stops.
