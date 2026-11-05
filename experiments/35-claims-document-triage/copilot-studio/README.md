# Copilot Studio standard harness

A build guide, not a solution you can import. This repository does not ship a zip that creates the agent.

This is the **standard harness**. One topic, one flow, and the approval points below. The Copilot Studio **GitHub Copilot harness** calls the same `triage()` and is documented in [../docs/github-copilot-harness.md](../docs/github-copilot-harness.md). Read [../docs/harness-comparison.md](../docs/harness-comparison.md) before choosing. Do not upload the skills onto this agent.

Microsoft's harness overview, opened 5 November 2026, describes the standard harness as the option for rule-based agents, where you define the topics and paths. The comparison table says files, skills, and memory are "Not a focus" on this harness. A last-updated date was not in the text retrieved. The licensing article linked from that overview was not opened. This is not a licence opinion. The overview says the GitHub Copilot harness is an authoring and orchestration framework, not the GitHub Copilot service. This topic is not that harness.

The agent is for a claims handler. It is not a customer-facing bot. The Customer Conversation harness on the same overview is for voice and chat. This experiment does not use it. This starter does not tell the customer anything.

Where generative orchestration is on, the topic is selected from its description. This guide does not assign a weight to a phrase. A Learn page on that behaviour was not opened on 5 November 2026. The exact behaviour is unverified.

## What to create

1. In Copilot Studio, create an agent. Name it "Claims document triage (draft)". Language: English (United Kingdom).
2. Paste [system-prompt.md](system-prompt.md) into the instructions.
3. Do not add an email connector, a claims-system connector, a Dataverse write, or a customer-chat channel. If a tool is not in `agent-manifest.yaml`, it should not be on the agent.
4. Add one action: a flow that runs `triage()` and returns JSON. The contract is below.
5. Keep the topic on the description in the instructions. Do not add a second path that accepts or declines.

## Triage action

Inputs come from the handler or a form. They are not inferred from a sentence inside a file.

| Input | Required | Notes |
|---|---|---|
| `pack` | Yes | One JSON object. `synthetic` must be true for a run in this starter. |
| `as_of` | Yes | `YYYY-MM-DD`. The day the handler is reading the pack. |

Output: the JSON from `triage()`. The topic displays it. It does not recompute the lines, the prompts, or the score.

How to host the function:

- A small internal API or an Azure Function that imports `triage.py`, with Experiments 12, 08, and 29 beside it, called by a Power Automate HTTP action with a locked-down identity.
- Not a Power Automate expression that scores the claim. One implementation of the draft is enough.

The flow's only job is to return JSON to the topic. It does not create a Dataverse row, it does not update a claims system, and it does not send mail. See [power-automate-flow.md](power-automate-flow.md).

## Topic

1. The handler pastes the pack and types the as-of date.
2. The topic calls the flow.
3. The topic shows the JSON in the order in [system-prompt.md](system-prompt.md).
4. The topic stops.

There is no branch that accepts, declines, settles, or messages the customer. Those sentences, if the handler types them, are answered with the line that the agent cannot do that.

## Approval points

The manifest is the list. In this harness they are stops, not buttons the agent presses.

| Act | Who |
|---|---|
| Read the draft | No separate approval |
| Check a prompt | Claims handler. A prompt is not a finding. |
| Review a score under a draft threshold | Claims handler. The flag does not decline the claim. |
| Approve or change the class | Claims handler. Not a tool of this topic. |
| Accept, decline, settle, tell the customer, or write the claims system | Not this agent. |
