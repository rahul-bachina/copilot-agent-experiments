# Copilot Studio standard harness

A build guide, not a solution you can import. This repository does not ship a zip that creates the agent.

This is the **standard harness**. One topic, one flow, and the approval points below. The Copilot Studio **GitHub Copilot harness** calls the same `review()` and is documented in [../docs/github-copilot-harness.md](../docs/github-copilot-harness.md). Read [../docs/harness-comparison.md](../docs/harness-comparison.md) before choosing. Do not upload the skills onto this agent.

Microsoft's harness overview, opened 27 October 2026, describes the standard harness as the option for rule-based agents, where you define the topics and paths. The comparison table says files, skills, and memory are "Not a focus" on this harness. A last-updated date was not in the text retrieved for this experiment. The licensing article linked from that overview was not opened. This is not a licence opinion.

The agent is for a KYC reviewer. It is not a customer-facing bot. The Customer Conversation harness on the same overview is for voice and chat that try to resolve a customer's issue. This experiment does not use it. A customer conversation is where section 333A of the Proceeds of Crime Act 2002 has to be thought about before anything is said. This starter does not say it.

## What to create

1. In Copilot Studio, create an agent. Name it "KYC evidence checklist (draft)". Language: English (United Kingdom).
2. Paste [system-prompt.md](system-prompt.md) into the instructions.
3. Do not add an email connector, a SharePoint or Dataverse write, an onboarding connector, a SAR channel, or a customer-chat channel. If a tool is not in `agent-manifest.yaml`, it should not be on the agent.
4. Add one action: a flow that runs `review()` and returns JSON. The contract is below.
5. Turn off any generative action that can call every connector in the environment. One topic, with the checklist as the only action, is easier to review.

## Checklist action

Inputs come from the reviewer or a form. They are not inferred from a sentence inside a file.

| Input | Required | Notes |
|---|---|---|
| `customer_file` | Yes | One JSON object. `synthetic` must be true for a run in this starter. |
| `as_of` | Yes | `YYYY-MM-DD`. The day the reviewer is reading the file. |

Output: the JSON from `review()`. The topic displays injection, stale dates, evidenced and missing rows, the regulation 33 phrases, and the customer note. It does not recompute them. It does not hide a null `final_risk_rating`.

How to host the function:

- A small internal API or an Azure Function that imports `review.py`, with Experiments 12 and 08 beside it, called by a Power Automate HTTP action with a locked-down identity.
- Not a Power Automate expression that scores the customer. One implementation of the checklist is enough.

The flow's only job is to return JSON to the topic. It does not create a Dataverse row, it does not update an onboarding system, and it does not send mail. See [power-automate-flow.md](power-automate-flow.md).

## Topic

1. The reviewer pastes the customer file and types the as-of date.
2. The topic calls the flow.
3. The topic shows the JSON in the order in [system-prompt.md](system-prompt.md).
4. The topic stops.

There is no branch that confirms the documents, approves the customer, or sends the note. Those sentences, if the reviewer types them, are answered with the line that the agent cannot do that.

## Approval points

The manifest is the list. In this harness they are stops, not buttons the agent presses.

| Act | Who |
|---|---|
| Read the draft | No separate approval |
| Confirm the documents and the purpose | KYC reviewer. Not a tool. |
| Use the customer note | KYC reviewer. The agent cannot send it. |
| Rate, onboard, or file a report | Not this agent. |
