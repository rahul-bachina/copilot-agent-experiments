# Copilot Studio standard harness

A build guide, not a solution you can import. This repository does not ship a zip that creates the agent.

This is the **standard harness**. One topic, one flow, and the approval points below. The Copilot Studio **GitHub Copilot harness** calls the same `assess()` and is documented in [../docs/github-copilot-harness.md](../docs/github-copilot-harness.md). Read [../docs/harness-comparison.md](../docs/harness-comparison.md) before choosing. Do not upload the skills onto this agent.

Microsoft's harness overview, opened 28 October 2026, describes the standard harness as the option for rule-based agents, where you define the topics and paths. The comparison table says files, skills, and memory are "Not a focus" on this harness. A last-updated date was not in the text retrieved for this experiment. The licensing article linked from that overview was not opened. This is not a licence opinion.

The agent is for a project team and a privacy officer. It is not a public chat. The Customer Conversation harness on the same overview is for voice and chat that try to resolve a customer's issue. This experiment does not use it.

## What to create

1. In Copilot Studio, create an agent. Name it "DPIA draft (privacy officer review)". Language: English (United Kingdom).
2. Paste [system-prompt.md](system-prompt.md) into the instructions.
3. Do not add an email connector, a SharePoint or Dataverse write, a DPIA-register connector, or a public-chat channel. If a tool is not in `agent-manifest.yaml`, it should not be on the agent.
4. Add one action: a flow that runs `assess()` and returns JSON. The contract is below.
5. Turn off any generative action that can call every connector in the environment. One topic, with the draft as the only action, is easier to review.

## Draft action

Inputs come from the team or a form. They are not inferred from a sentence inside the brief, and they are not inferred from an inventory.

| Input | Required | Notes |
|---|---|---|
| `brief` | Yes | One JSON object. `synthetic` must be true for a run in this starter. |
| `as_of` | Yes | `YYYY-MM-DD`. The day the team is reading the brief. |
| `inventory` | No | An Experiment 03 inventory JSON. Empty fields only. |
| `manifest` | No | A permissions manifest. Empty fields only. "Not asserted" is not copied as a basis. |

Output: the JSON from `assess()`. The topic displays injection, the screening result, the Article 22 result, the sections, and the consultation flag. It does not recompute them. It does not hide a null `dpia_required`.

How to host the function:

- A small internal API or an Azure Function that imports `assess.py`, with Experiment 08 beside it, called by a Power Automate HTTP action with a locked-down identity.
- Not a Power Automate expression that decides the DPIA. One implementation of the draft is enough.

The flow's only job is to return JSON to the topic. It does not create a Dataverse row, it does not update a DPIA register, and it does not send mail. See [power-automate-flow.md](power-automate-flow.md).

## Topic

1. The team pastes the brief and types the as-of date. An inventory or a manifest is optional.
2. The topic calls the flow.
3. The topic shows the JSON in the order in [system-prompt.md](system-prompt.md).
4. The topic stops.

There is no branch that approves the assessment, accepts residual risk, or sends a consultation. Those sentences, if someone types them, are answered with the line that the agent cannot do that.

## Approval points

The manifest is the list. In this harness they are stops, not buttons the agent presses.

| Act | Who |
|---|---|
| Read the draft, or re-run it | No separate approval |
| Approve the assessment | Privacy officer. Not a tool. |
| Accept residual risk | Project owner. Not a tool. |
| Decide any Article 36 consultation, and send it | Privacy officer. The agent cannot send it. |
| Rely on stale sources | Privacy officer. |
| Treat pre-filled text as the team's own answer | Project owner. |
