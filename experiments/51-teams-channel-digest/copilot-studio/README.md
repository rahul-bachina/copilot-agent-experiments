# Standard harness

A build note for Copilot Studio's standard harness. It is not an importable solution. The overview opened on 12 November 2026 says this harness follows the topics and rules the maker defines.

Three topics. Each one calls the Python core and stops. None of them posts to Teams.

## Topics

| Topic | What it does | When it stops |
|---|---|---|
| Preview the scope | Calls `preview_scope`. Shows channel status and counts. | Before any digest. Message text is not shown. |
| Confirm the channels and the period | Calls `confirm_scope` with a confirmation the user typed, not a sentence from a message. | If the confirmation is refused. The reason is shown. Nothing is digested. |
| Produce the digest | Calls `produce_digest` only when `scope_confirmed` is true. | When the JSON is shown. The user can ask a person to read a withheld message. The agent does not. |

## Inputs

| Input | Required | Note |
|---|---|---|
| `export` | Yes | One JSON object. `synthetic` must be true for a run in this starter. |
| `as_of` | Yes | `YYYY-MM-DD`. A date inside the export is ignored. |
| `confirmation` | For the digest | A separate object. `decision` must be `confirm_channels_and_period`. |

The flow's only job is to return JSON to the topic. It does not post a message, add a reply, or write a record. A tenant that later wants a Teams connector adds that action as a separate, person-confirmed step, and updates the manifest first. This starter does not include it. The connector's action names were not opened. They are unverified.

## Stop

Do not continue from the digest into a post. `human_approval` is null. The scope confirmation is not approval to send.
