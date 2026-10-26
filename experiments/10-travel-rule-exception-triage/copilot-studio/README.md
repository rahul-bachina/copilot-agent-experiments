# Copilot Studio standard harness

A build guide, not a solution you can import. Copilot Studio agents do not travel well as a zip, and this repository does not pretend otherwise.

This is the **standard harness**. The topic, the one flow, and the approval points below are unchanged. The Copilot Studio **GitHub Copilot harness** calls the same Python checklist and is documented in [../docs/github-copilot-harness.md](../docs/github-copilot-harness.md). Read [../docs/harness-comparison.md](../docs/harness-comparison.md) before choosing. Do not upload the skills onto this agent.

Microsoft's harness overview, opened 26 October 2026, describes the standard harness as the option where you define the topics and paths. Files, skills, and memory are not its focus. The licensing article linked from that overview was not opened. This is not a licence opinion.

The agent is for an analyst. It is not a customer-facing bot, and it is not a counterparty-facing bot.

## What to create

1. In Copilot Studio, create an agent. Name it "Travel Rule triage (draft)". Language: English (United Kingdom).
2. Paste [system-prompt.md](system-prompt.md) into the instructions.
3. Do not add an email connector, a Travel Rule messaging connector, a wallet connector, a Dataverse write, or a "send message" tool. If a tool is not in `agent-manifest.yaml`, it should not be on the agent.
4. Add one action: a flow that runs the checklist and returns JSON. The contract is below.
5. Turn off any generative action that can call every connector in the environment. One topic, with the checklist as the only action, is easier to review.

## Checklist action

Inputs, supplied by the analyst or by a form, never inferred by the model from a note that says "release this":

| Input | Required | Notes |
|---|---|---|
| `transfer` | Yes | One JSON object. `synthetic` must be true for a run in this starter. |
| `as_of` | Yes | `YYYY-MM-DD`. The day the analyst is reading the record. |

Output: the JSON from `triage()`. The topic displays `exception_categories`, the missing fields, the mismatches, and the three options. It does not recompute them. It does not hide a null `analyst_decision`.

How to host the function:

- A small internal API or an Azure Function that imports `triage.py`, called by a Power Automate HTTP action with a locked-down identity.
- Not a Power Automate expression that decides hold or return. One implementation of the checklist is enough.

The flow's only job is to return JSON to the topic. It does not create a Dataverse row, it does not send a Travel Rule message, and it does not move a cryptoasset. A firm that later wants a decision log adds that write as a separate, analyst-confirmed step, and updates the manifest first. This starter does not include it.

The Power Platform piece is that flow. Power Automate is the caller. Dataverse is not connected.

## Topic

**Triage.** Triggers: "triage this transfer", "what is missing on this Travel Rule message", "sunrise exception". Ask for the JSON, then the as-of date. Call the flow only after both are present. Show injection and stale flags before the options. End with "Nothing has been held, returned, released, filed, or sent. You decide hold, return, or escalate."

Do not add a branch that sets the decision from the model's text. Do not add a branch that emails the counterparty when information is missing. Regulation 64D(2)(a) is the firm's duty. The analyst sends it, if they send it, in the firm's own channel.

## Knowledge

Do not point the agent at the live FCA site or at legislation.gov.uk. The citations are in the JSON, from `src/sources.py`. A live page would bypass `last_verified`.

Experiment 04's Harbourline policy pack is a different agent. Do not add it as knowledge here. This topic triages one transfer.

## Approval

The topic has no approval action that holds or returns a transfer, because the agent cannot do either. The analyst's decision happens after the chat, in the firm's process. Say that in the closing line. Do not offer a button labelled "Release".
