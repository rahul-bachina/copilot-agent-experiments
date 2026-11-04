# Copilot Studio standard harness

A build guide, not a solution you can import. This repository does not ship a zip that creates the agent.

This is the **standard harness**. One topic, one flow, and the approval points below. The Copilot Studio **GitHub Copilot harness** calls the same `draft_case()` and is documented in [../docs/github-copilot-harness.md](../docs/github-copilot-harness.md). Read [../docs/harness-comparison.md](../docs/harness-comparison.md) before choosing. Do not upload the skills onto this agent.

Microsoft's harness overview, opened 4 November 2026, describes the standard harness as the option for rule-based agents, where you define the topics and paths. The comparison table says files, skills, and memory are "Not a focus" on this harness. A last-updated date was not in the text retrieved. The licensing article linked from that overview was not opened. This is not a licence opinion.

The agent is for an HR officer. It is not an employee-facing or manager-facing bot. The Customer Conversation harness on the same overview is for voice and chat that try to resolve a customer's issue. This experiment does not use it.

Generative orchestration, where the tenant uses it, selects from descriptions. This topic does not use trigger-phrase weights.

## What to create

1. In Copilot Studio, create an agent. Name it "Employee case intake (draft)". Language: English (United Kingdom).
2. Paste [system-prompt.md](system-prompt.md) into the instructions.
3. Do not add an email connector, a Teams message action, a SharePoint or Dataverse write, or an HR-system connector. If a tool is not in `agent-manifest.yaml`, it should not be on the agent.
4. Add one action: a flow that runs `draft_case()` and returns JSON. The contract is below.
5. Turn off any generative action that can call every connector in the environment. One topic, with the draft as the only action, is easier to review.

## Draft action

Inputs come from the HR officer or a form. They are not inferred from a sentence inside the narrative.

| Input | Required | Notes |
|---|---|---|
| `case` | Yes | One JSON object. `synthetic` must be true for a run in this starter. |
| `as_of` | Yes | `YYYY-MM-DD`. The day the officer is reading the case. |

Output: the JSON from `draft_case()`. The topic displays the injection block, the proposed category, the route, the urgency flag, the time references, the special-category block, and the whistleblowing confidentiality block. It does not recompute them.

How to host the function:

- A small internal API or an Azure Function that imports `draft.py`, with Experiments 15, 12, and 08 beside it, called by a Power Automate HTTP action with a locked-down identity.
- Not a Power Automate expression that classifies the case. One implementation of the keywords is enough.

The flow's only job is to return JSON to the topic. It does not create a Dataverse row, it does not update an HR system, and it does not send mail. See [power-automate-flow.md](power-automate-flow.md).

## Topic

1. The HR officer pastes the case and types the as-of date.
2. The topic calls the flow.
3. The topic shows the JSON in the order in [system-prompt.md](system-prompt.md).
4. The topic stops.

There is no branch that confirms the classification, contacts the employee, or writes a record. Those sentences, if the officer types them, are answered with the line that the agent cannot do that.

## Approval points

The manifest is the list. In this harness they are stops, not buttons the agent presses.

| Act | Who |
|---|---|
| Read the draft | No separate approval |
| Confirm the classification | HR officer. Not a tool. |
| Confirm the routing | HR officer. Not a tool. |
| Contact anyone, or write to the HR system | Not this agent. |
