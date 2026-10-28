# Copilot Studio standard harness

A build guide, not a solution you can import. This repository does not ship a zip that creates the agent.

This is the **standard harness**. One topic, one flow, and the approval points below. The Copilot Studio **GitHub Copilot harness** calls the same `build_pack()` and is documented in [../docs/github-copilot-harness.md](../docs/github-copilot-harness.md). Read [../docs/harness-comparison.md](../docs/harness-comparison.md) before choosing. Do not upload the skills onto this agent.

Microsoft's harness overview, retrieved 28 October 2026, describes the standard harness as the option for rule-based agents, where you define the topics and paths. The comparison table says files, skills, and memory are "Not a focus" on this harness. The licensing article linked from that overview was not opened. This is not a licence opinion.

The agent is for the person assembling a pack. It is not a bot for a data subject. The Customer Conversation harness on the same overview is for voice and chat that try to resolve a customer's issue. This experiment does not use it.

## What to create

1. In Copilot Studio, create an agent. Name it "Evidence pack builder (draft)". Language: English (United Kingdom).
2. Paste [system-prompt.md](system-prompt.md) into the instructions.
3. Do not add an email connector, a SharePoint or Dataverse write, a case-system connector, or a "send message" tool. If a tool is not in `agent-manifest.yaml`, it should not be on the agent.
4. Add one action: a flow that runs `build_pack()` and returns JSON. The contract is below.
5. Turn off any generative action that can call every connector in the environment. One topic, with the pack builder as the only action, is easier to review.

## Pack action

Inputs come from the user or a form. They are not inferred from a sentence inside an item.

| Input | Required | Notes |
|---|---|---|
| `request` | Yes | One JSON object. `synthetic` must be true for a run in this starter. Do not copy scopes or the search period out of the items into this object. |
| `as_of` | Yes | `YYYY-MM-DD`. The day the user is reading the items. |
| `pack_type` | Yes | A closed-list id, typed by the user. |
| `authorised_scopes` | Yes | Closed-list scopes, typed by the user. An empty list excludes every item. |
| `search_from` and `search_to` | Together, or neither | Inclusive dates. If either is missing, the draft proposes no pages. |

Output: the JSON from `build_pack()`. The topic displays injection, excluded items, held items, and the proposed index. It does not recompute them. It does not hide a false `export_approved`.

How to host the function:

- A small internal API or an Azure Function that imports `pack.py`, Experiment 12, and Experiment 08, called by a Power Automate HTTP action with a locked-down identity.
- Not a Power Automate expression that decides scope, privilege, or the page order. One implementation of the builder is enough.

The flow's only job is to return JSON to the topic. It does not create a Dataverse row, it does not move a file in SharePoint, and it does not send mail. A team that later wants to file the index adds that write as a separate, approver-confirmed step, and updates the manifest first. This starter does not include it.

The Power Platform piece is that flow. Power Automate is the caller. Dataverse is not connected. See [power-automate-flow.md](power-automate-flow.md).

## Topic

**Build the pack.** Triggers: "evidence pack", "subject access bundle", "index these items". Ask for the JSON, the as-of date, the pack type, the scopes, and the search period. Call the flow. Show the result in the order in [system-prompt.md](system-prompt.md). End the topic. Do not add a question that records approval inside the topic. Approval is a person, outside the agent.

There is no topic that sends, discloses, applies an exemption, or releases text. Do not add one.
