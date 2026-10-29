# Copilot Studio standard harness

A build guide, not a solution you can import. This repository does not ship a zip that creates the agent.

This is the **standard harness**. One topic, one flow, and the approval points below. The Copilot Studio **GitHub Copilot harness** calls the same `investigate()` and is documented in [../docs/github-copilot-harness.md](../docs/github-copilot-harness.md). Read [../docs/harness-comparison.md](../docs/harness-comparison.md) before choosing. Do not upload the skills onto this agent.

Microsoft's harness overview, opened 29 October 2026, describes the standard harness as the option for rule-based agents, where you define the topics and paths. The comparison table says files, skills, and memory are "Not a focus" on this harness. A last-updated date was not in the text retrieved for this experiment. The licensing article linked from that overview was not opened. This is not a licence opinion.

The agent is for an analyst preparing a reading for the nominated officer. It is not a customer-facing bot. The Customer Conversation harness on the same overview is for voice and chat that try to resolve a customer's issue. This experiment does not use it. A customer conversation about this case is the tipping-off question in section 333A of the Proceeds of Crime Act 2002. This starter does not draft that conversation.

## What to create

1. In Copilot Studio, create an agent. Name it "On-chain alert draft (internal)". Language: English (United Kingdom).
2. Paste [system-prompt.md](system-prompt.md) into the instructions.
3. Do not add an email connector, a customer-chat channel, a chain node, the NCA SAR Portal, a wallet, or a Dataverse write. If a tool is not in `agent-manifest.yaml`, it should not be on the agent.
4. Add one action: a flow that runs `investigate()` and returns JSON. The contract is below.
5. Turn off any generative action that can call every connector in the environment. One topic, with the draft as the only action, is easier to review.

## Investigate action

Inputs come from the analyst or a form. They are not inferred from a sentence inside the alert.

| Input | Required | Notes |
|---|---|---|
| `alert_case` | Yes | One JSON object. `synthetic` must be true for a run in this starter. |
| `as_of` | Yes | `YYYY-MM-DD`. The day the analyst is reading the case. |

Output: the JSON from `investigate()`. The topic displays injection, stale flags, the timeline, the note, and the narrative. It does not recompute them. It does not hide a null `mlro_decision`. It does not show a customer message, because `customer_facing.text` is null.

How to host the function:

- A small internal API or an Azure Function that imports `investigate.py`, with Experiments 04, 08, 10, 12, and 16 beside it, called by a Power Automate HTTP action with a locked-down identity.
- Not a Power Automate expression that decides the alert. One implementation of the draft is enough.

The flow's only job is to return JSON to the topic. It does not create a Dataverse row, it does not file a report, and it does not send mail. See [power-automate-flow.md](power-automate-flow.md).

## Topic

1. The analyst pastes the case and types the as-of date.
2. The topic calls the flow.
3. The topic shows the JSON in the order in [system-prompt.md](system-prompt.md).
4. The topic stops.

There is no branch that files, requests a defence, freezes a wallet, or writes to the customer. Those sentences, if the analyst types them, are answered with the line that the agent cannot do that.

## Approval points

The manifest is the list. In this harness they are stops, not buttons the agent presses.

| Act | Who |
|---|---|
| Read the draft | No separate approval |
| Decide whether section 330 or section 331 is met | Nominated officer. Not a tool. |
| File or not file | Nominated officer. The agent cannot file. |
| Use any customer-facing wording | Nominated officer. The agent drafts none. |
