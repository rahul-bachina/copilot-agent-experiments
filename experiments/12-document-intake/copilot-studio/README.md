# Copilot Studio standard harness

A build guide, not a solution you can import. This repository does not ship a zip that creates the agent.

This is the **standard harness**. One topic, one flow, and the approval points below. The Copilot Studio **GitHub Copilot harness** calls the same `intake()` and is documented in [../docs/github-copilot-harness.md](../docs/github-copilot-harness.md). Read [../docs/harness-comparison.md](../docs/harness-comparison.md) before choosing. Do not upload the skills onto this agent.

Microsoft's harness overview, retrieved 27 October 2026 (page last updated 22 October 2026), describes the standard harness as the option for rule-based agents, where you define the topics and paths. The comparison table says files, skills, and memory are "Not a focus" on this harness. The licensing article linked from that overview was not opened. This is not a licence opinion.

The agent is for the person uploading files and for an intake reviewer. It is not a customer-facing bot. The Customer Conversation harness on the same overview is for voice and chat that try to resolve a customer's issue. This experiment does not use it.

## What to create

1. In Copilot Studio, create an agent. Name it "Document intake (draft)". Language: English (United Kingdom).
2. Paste [system-prompt.md](system-prompt.md) into the instructions.
3. Do not add an email connector, a SharePoint or Dataverse write, a case-system connector, or a "send message" tool. If a tool is not in `agent-manifest.yaml`, it should not be on the agent.
4. Add one action: a flow that runs `intake()` and returns JSON. The contract is below.
5. Turn off any generative action that can call every connector in the environment. One topic, with the inventory as the only action, is easier to review.

## Inventory action

Inputs come from the user or a form. They are not inferred from a sentence inside a file.

| Input | Required | Notes |
|---|---|---|
| `batch` | Yes | One JSON object. `synthetic` must be true for a run in this starter. |
| `as_of` | Yes | `YYYY-MM-DD`. The day the user is reading the batch. |
| `requested_purpose` | No | A preview only, and only if the user types a closed-list id outside the file. Omit it rather than copy it out of the document. |

Output: the JSON from `intake()`. The topic displays injection, date status, read status, the keyword class, and the checklist preview. It does not recompute them. It does not hide a false `files_confirmed`.

How to host the function:

- A small internal API or an Azure Function that imports `intake.py` and Experiment 08, called by a Power Automate HTTP action with a locked-down identity.
- Not a Power Automate expression that classifies the file or decides the purpose. One implementation of the inventory is enough.

The flow's only job is to return JSON to the topic. It does not create a Dataverse row, it does not move a file in SharePoint, and it does not send mail. A team that later wants a queue adds that write as a separate, reviewer-confirmed step, and updates the manifest first. This starter does not include it.

The Power Platform piece is that flow. Power Automate is the caller. Dataverse is not connected. See [power-automate-flow.md](power-automate-flow.md).

## Topic

**Inventory.** Triggers: "inventory this batch", "what files arrived", "which purpose checklist". Ask for the JSON, then the as-of date. Call the flow only after both are present. Show injection and unreadable files before the class suggestion. End with the closing line in the system prompt.

Do not add a branch that sets `files_confirmed` from the model's text. Do not add a branch that emails anyone when a phrase is missing. Do not add a branch that calls another experiment.

## Knowledge

Do not point the agent at a live case store, a mailbox, or the public web. The purpose list is in `src/catalogue.py`. A page fetched at run time would bypass `catalogue_pinned_on`.

Experiment 08 is a library call inside `intake()`, not a second topic that the model rephrases. Do not paste the detectors into the instructions.

## Approval

The topic has no button that accepts the batch, because the agent cannot. The user confirms the file ids and the purpose after the chat, in the organisation's process. The intake reviewer decides the routing suggestion after that. Say that in the closing line. Do not offer a button labelled "Accept" or "Send".
