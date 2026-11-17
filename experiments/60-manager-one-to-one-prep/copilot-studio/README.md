# Copilot Studio standard harness

A build guide. Not an importable solution. The topics call `prepare()` and return JSON. They do not rate, send, or write.

## Topics

| Topic | When | What it returns |
|---|---|---|
| Prepare the meeting | The manager has a selection object | The prep note, or a refusal |
| Human flag | `human_flags` is not empty | The route. Not the flagged sentence |
| Cannot prepare | The pack is not synthetic, the selector is not the directory manager, or a date cannot be read | The refusal or `needs_human`. No invented date |

The flow is in [power-automate-flow.md](power-automate-flow.md). The instructions for the agent are in [system-prompt.md](system-prompt.md).

## Inputs

| Name | Required | Notes |
|---|---|---|
| `pack` | Yes | One JSON object. `synthetic` must be true. |
| `as_of` | Yes | `YYYY-MM-DD`. An unreadable value is not replaced with today. |

Do not add a mail connector, a chat connector, or a Microsoft Graph connector. A deployment DLP policy should block those connectors. This starter has no connector to block.

Do not point the agent at a live mailbox. The quotations come from the sources on the selection. A live mailbox would bypass the selection.

Harbourside Instruments Ltd is invented. Do not paste a real one-to-one into this topic.
