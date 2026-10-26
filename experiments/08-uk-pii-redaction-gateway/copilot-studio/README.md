# Copilot Studio standard harness

A build guide, not a solution you can import. Copilot Studio agents do not travel well as a zip, and this repository does not pretend otherwise.

This is the **standard harness**. The topic and the approval points below are unchanged. The Copilot Studio **GitHub Copilot harness** calls the same Python gateway and is documented in [../docs/github-copilot-harness.md](../docs/github-copilot-harness.md). Read [../docs/harness-comparison.md](../docs/harness-comparison.md) before choosing. Do not upload the skills onto this agent. Microsoft's harness overview, retrieved 26 October 2026, describes the standard harness as the option where you define the topics and paths. The same page says skills and memory are "Not a focus" there.

The agent is for a privacy reviewer, or for a colleague preparing a proposal for that reviewer. It is not a customer-facing bot.

## What to create

1. In Copilot Studio, create an agent on the standard harness. Name it "UK identifier redaction (draft)". Language: English (United Kingdom).
2. Paste [system-prompt.md](system-prompt.md) into the instructions.
3. Do not add an email connector, a "send message" tool, or an action that posts the text to a public endpoint. If a tool is not in `agent-manifest.yaml`, it should not be on the agent.
4. Add one action: a flow that runs `propose()` and returns JSON. The contract is in [power-automate-flow.md](power-automate-flow.md).
5. Turn off any generative action that can call every connector in the environment. One topic, with this flow as the only action, is easier to review.

## Topic

**Propose redaction.** Triggers: "redact this", "check for an NHS number", "UK identifier check". Ask for the text. Call the flow. Show the banner, the findings, the limitations, and the injection signals. End with "Nothing has been released or sent. A privacy reviewer approves the redacted output before anyone releases it."

Do not add a branch that sends the proposal. Do not add a branch that says the text is anonymised when the JSON says otherwise. If `output_is_anonymised` is not false, stop and say the core failed.

## Approval

The topic stops before release. The privacy reviewer approves outside the agent. Viewing the proposal and running the flow again do not need a separate approval. The four mandatory points are in the manifest and in the system prompt.

## What this guide does not include

An importable solution, a tenant, a Key Vault, a Purview label, or a live model. Those are deployment choices. The Python gateway runs without them.
