# Copilot Studio, standard harness

A build guide. It is not an importable solution. There is no `.zip` in this folder.

The standard harness follows topics and rules you define. The harness overview, opened 29 October 2026, gives an internal help desk that answers common questions and routes simple requests as an example of this harness. Files, skills, and memory are "not a focus" on that page. That matches this topic. The GitHub Copilot harness, for a follow-up on the same JSON, is [docs/github-copilot-harness.md](../docs/github-copilot-harness.md). It is not the GitHub Copilot service.

## Topic

One topic. Name it `IT ticket draft`.

| Input | Required | What it is |
|---|---|---|
| `ticket` | Yes | One JSON object. `synthetic` must be true for a run in this starter. The schema is `schema/desk_tool.schema.json`. |
| `as_of` | Yes | `YYYY-MM-DD`, typed by the person. Do not copy it out of the ticket text. |

The topic calls the flow below, shows the JSON, and stops. It does not ask a follow-up that resets a password. It does not ask for an MFA code.

## What the topic says

Use [system-prompt.md](system-prompt.md) as the instructions. Show `prompt_injection` and `social_engineering` first when `detected` is true. Show `identity.reason` next. Do not read out an article whose `body_quoted` is false. Leave `human_approval` null. Say who has to confirm what, in the organisation's own systems.

`ai_disclosure` stays. It says the draft was written by an automated AI chatbot.

## Knowledge

Do not point this topic at a live SharePoint library. The articles are `src/catalogue.py`. A later deployment that swaps in the organisation's own articles has to version those articles and keep the same stale rule. That swap is not in this folder. Aldermere Shared ICT is invented.

## Flow

[power-automate-flow.md](power-automate-flow.md). The flow returns JSON. It does not write a Dataverse row, call Microsoft Entra, or send mail.

## After the draft

A signed-in member of staff may confirm a standard fix or a device change by calling `record_review` with a separate object. An analyst records `analyst_take_handover` for a privileged action. Neither call executes the change. If the tenant's topic builder has no way to pass that second object, stop at the draft and let the person act outside the agent. Do not add a connector to close the gap.
