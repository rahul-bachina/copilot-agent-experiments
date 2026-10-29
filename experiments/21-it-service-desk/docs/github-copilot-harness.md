# GitHub Copilot harness

This is a Copilot Studio authoring and orchestration framework. It is not the GitHub Copilot service. The harness overview, opened 29 October 2026, says customer data is not sent to or processed by the GitHub Copilot service when the agent runs in Copilot Studio.

Use it when an analyst wants to walk one ticket: which article matched, which diagnostic is missing, and why a confirmation was refused. The standard harness is the better fit when every ticket takes the same path. See [harness-comparison.md](harness-comparison.md).

## Skills

| Skill | Calls | Stops at |
|---|---|---|
| `skills/triage-it-ticket/` | `triage()` | Shows the JSON. Does not confirm and does not execute. |
| `skills/record-user-confirmation/` | `record_review()` | A signed-in member of staff confirms a standard fix or a device change. `executed` stays false. |
| `skills/refer-privileged-action/` | `record_review()` with `analyst_take_handover` | An analyst records the handover. The reset, the MFA change, and the access grant stay outside the agent. |

The `name` and `description` in each skill are the skill fields the harness overview describes. The exact upload schema was not opened on 29 October 2026. The approval rules are the manifest's rules. They are not a Microsoft schema.

## Tool contract

Both skills call the functions in `src/desk.py`. Do not reimplement the catalogue, the identity rule, or the stale window in the model.

| | |
|---|---|
| Draft schema | `schema/desk_tool.schema.json`. No reset, grant, execute, or send field. |
| Review schema | `schema/review_tool.schema.json`. Four decisions. |
| Side effect | None. |
| Approval to run `triage()` | Not required. The manifest sets `human_approval_required: false` on the draft tool. |
| Approval to rely on the output | Required. `human_approval` is null until `record_review()`. |

If `synthetic` is not true, stop. Do not flip the flag. Do not repeat the text.

If the tool is unavailable, stop. Do not invent the JSON, a click-path, or a citation.

## Sandbox file

You may write `draft-it-ticket.json` in the sandbox. It is the tool JSON, unchanged. Do not name a file `final`, `reset`, or `access-granted`. Creating that file does not need approval. It has no external effect. Copying it into an ITSM tool does, and you have no tool that performs the copy.

Microsoft's harness overview, opened 29 October 2026, says this harness can create and edit Word, Excel, PowerPoint, and PDF files. A file of the brief is still a draft. Put `ai_disclosure` on the first line.

## Memory

Do not store the ticket. The harness overview says this harness supports memory. Whether an administrator can turn memory off was not on the page opened on 29 October 2026. Do not use it.

## What this harness must not be given

A connector to Microsoft Entra, a device-management console, an ITSM write, mail, Teams send, or a purchasing system. Adding one is a manifest change, not a skill change.
