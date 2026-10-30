# Copilot Studio standard harness

A build guide, not a solution you can import. This repository does not ship a zip that creates the agent.

This is the **standard harness**. One topic, one flow, and the approval points below. The Copilot Studio **GitHub Copilot harness** calls the same `precheck()` and is documented in [../docs/github-copilot-harness.md](../docs/github-copilot-harness.md). Read [../docs/harness-comparison.md](../docs/harness-comparison.md) before choosing. Do not upload the skills onto this agent.

Microsoft's harness overview, opened 30 October 2026, describes the standard harness as the option for rule-based agents, where you define the topics and paths. The comparison table says files, skills, and memory are "Not a focus" on this harness. The licensing article linked from that overview was not opened. This is not a licence opinion.

The agent is for a compliance reviewer preparing a reading for the section 21 approver. It is not a customer-facing bot. The Customer Conversation harness on the same overview is for voice and chat that try to resolve a customer's issue. This experiment does not use it. A customer asking whether a promotion may be communicated would be asking for a compliance opinion. This starter does not give one.

## What to create

1. In Copilot Studio, create an agent. Name it "Cryptoasset promotion checklist (internal)". Language: English (United Kingdom).
2. Paste [system-prompt.md](system-prompt.md) into the instructions.
3. Do not add a CMS connector, a social-network connector, an email connector, the Financial Services Register, or a Dataverse write. If a tool is not in `agent-manifest.yaml`, it should not be on the agent.
4. Add one action: a flow that runs `precheck()` and returns JSON. The contract is below.
5. Turn off any generative action that can call every connector in the environment. One topic, with the checklist as the only action, is easier to review.

## Checklist action

Inputs come from the reviewer or a form. They are not inferred from a sentence inside the promotion.

| Input | Required | Notes |
|---|---|---|
| `promotion` | Yes | One JSON object. `synthetic` must be true for a run in this starter. |
| `as_of` | Yes | `YYYY-MM-DD`. The day the reviewer is reading the draft. |

Output: the JSON from `precheck()`. The topic displays injection, stale flags, and the checklist. It does not recompute them. It does not hide a null `s21_approver_decision`. It does not show replacement copy, because none is drafted.

How to host the function:

- A small internal API or an Azure Function that imports `precheck.py`, with Experiments 03, 04, and 08 beside it, called by a Power Automate HTTP action with a locked-down identity.
- Not a Power Automate expression that decides the promotion. One implementation of the checklist is enough.

The flow's only job is to return JSON to the topic. It does not create a Dataverse row, it does not publish, and it does not send mail. See [power-automate-flow.md](power-automate-flow.md).

## Topic

1. The reviewer pastes the draft and types the as-of date.
2. The topic calls the flow.
3. The topic shows the JSON in the order in [system-prompt.md](system-prompt.md).
4. The topic stops.

There is no branch that approves, publishes, or rewrites. Those sentences, if the reviewer types them, are answered with the line that the agent cannot do that.

## Approval points

The manifest is the list. In this harness they are stops, not buttons the agent presses.

| Act | Who |
|---|---|
| Read the checklist | No separate approval |
| Sign off the promotion, or refuse to | Section 21 approver. Not a tool. |
| Treat a flagged phrase as a breach, or as acceptable | Section 21 approver. |
| Publish | Section 21 approver. The agent cannot publish. |
