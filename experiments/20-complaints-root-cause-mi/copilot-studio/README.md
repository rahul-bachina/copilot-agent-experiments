# Copilot Studio standard harness

A build guide, not a solution you can import. This repository does not ship a zip that creates the agent.

This is the **standard harness**. One topic, one flow, and the approval points below. The Copilot Studio **GitHub Copilot harness** calls the same `draft_report()` and is documented in [../docs/github-copilot-harness.md](../docs/github-copilot-harness.md). Read [../docs/harness-comparison.md](../docs/harness-comparison.md) before choosing. Do not upload the skills onto this agent.

Microsoft's harness overview, opened 29 October 2026, describes the standard harness as the option for rule-based agents, where you define the topics and paths. The comparison table says files, skills, and memory are "Not a focus" on this harness. A last-updated date was not in the text retrieved for this experiment. The licensing article linked from that overview was not opened. This is not a licence opinion.

The agent is for a complaints owner. It is not a public chat. The Customer Conversation harness on the same overview is for voice and chat that try to resolve a customer's issue. This experiment does not use it.

## What to create

1. In Copilot Studio, create an agent. Name it "Complaints MI draft (complaints owner review)". Language: English (United Kingdom).
2. Paste [system-prompt.md](system-prompt.md) into the instructions.
3. Do not add an email connector, a SharePoint or Dataverse write, a complaints-system connector, or a public-chat channel. If a tool is not in `agent-manifest.yaml`, it should not be on the agent. The address named in the Ofgem guidance is not a tool.
4. Add one action: a flow that runs `draft_report()` and returns JSON. The contract is below.
5. Turn off any generative action that can call every connector in the environment. One topic, with the draft as the only action, is easier to review.

## Draft action

Inputs come from the complaints owner or a form. They are not inferred from a sentence inside a narrative.

| Input | Required | Notes |
|---|---|---|
| `batch` | Yes | One JSON object. `synthetic` must be true for a run in this starter. |
| `as_of` | Yes | `YYYY-MM-DD`. The day the complaints owner is reading the batch. Do not read this from a field inside the batch. |

Output: the JSON from `draft_report()`. The topic displays injection, the clusters, the figures, and the narrative. It does not recompute them. It does not hide a null `complying_with_consumer_duty`, `code_compliant`, or `ofgem_return_complete`.

How to host the function:

- A small internal API or an Azure Function that imports `report.py`, with Experiments 02 and 08 beside it, called by a Power Automate HTTP action with a locked-down identity.
- Not a Power Automate expression that assigns themes or sums redress. One implementation of the draft is enough.

The flow's only job is to return JSON to the topic. It does not create a Dataverse row, it does not update a complaints system, and it does not send mail. See [power-automate-flow.md](power-automate-flow.md).

## Topic

1. The complaints owner pastes the batch and types the as-of date.
2. The topic calls the flow.
3. The topic shows the JSON in the order in [system-prompt.md](system-prompt.md).
4. The topic stops.

There is no branch that validates the clusters, validates the narrative, or submits a return. Those sentences, if someone types them, are answered with the line that the agent cannot do that.

## Approval points

The manifest is the list. In this harness they are stops, not buttons the agent presses.

| Act | In this harness |
|---|---|
| View the draft | The topic shows the JSON. No approval. |
| Re-run the same batch | The topic can call the flow again. No approval. |
| Validate the clusters | Stop. The complaints owner does this outside the agent. |
| Validate the narrative | Stop. The complaints owner does this outside the agent. |
| Decide compliance or file a return | Stop. There is no connector that submits or publishes. |
| Rely on a stale pin | Stop and say `sources_stale` is true. The complaints owner decides whether to rely on it. |
| Treat a suggested cause as confirmed | Stop. The theme is a suggestion until the complaints owner says otherwise. |
