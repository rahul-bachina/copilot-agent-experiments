# Copilot Studio standard harness

A build guide, not a solution you can import. This is the intake and status variant for Experiment 07. The analyst workflow over the response set is the GitHub Copilot harness in [../docs/github-copilot-harness.md](../docs/github-copilot-harness.md). Both call the same Python core. This harness does not code themes.

## What to create

1. In Copilot Studio, create an agent on the **standard harness**. Name it "Consultation intake (draft)". Language: English (United Kingdom).
2. Paste [system-prompt.md](system-prompt.md) into the instructions.
3. Do not add an email connector, a consultation-platform connector, or a Dataverse "create row" action. If a tool is not in `agent-manifest.yaml`, it should not be on the agent.
4. Add one action: a flow that runs `intake_status` from `src/pipeline.py` and returns JSON. The contract is [../schema/intake_tool.schema.json](../schema/intake_tool.schema.json).
5. Turn off any generative action that can call every connector in the environment. Classic topics, with intake as the only action, are easier to review.

The standard harness follows the topics you define. Microsoft Learn describes it as the harness for rule-based agents and structured conversations ([harnesses overview](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview), retrieved 24 October 2026). That is why it is the intake. Coding a large set is the other harness.

## Intake action

Inputs come from the analyst. The model must not invent a retrieval date.

| Input | Required | Notes |
| --- | --- | --- |
| `batch` | Yes | The export. One question. |
| `as_of` | Yes | `YYYY-MM-DD`. The analyst enters it. |

Output: the JSON from `intake_status`. The topic displays submission count, unique-voice count, campaign cluster IDs, injection response IDs, redaction types, and whether the retrieval is stale. It does not display theme codes. It does not recompute the clusters.

The flow returns JSON to the topic. It does not create a row and it does not send mail.

How to host the function: a small internal API that imports `pipeline.py`, called by a Power Automate HTTP action with a locked-down identity. Not a flow that copies the responses into an email.

## Topics

**Load an export.** Triggers: "load the consultation", "intake status". Ask for the file and the retrieval date. Call the intake action. Show the counts above. If the retrieval is stale, say so in the words the JSON uses. Do not code themes in this topic.

**Where is this consultation.** Triggers: "status", "has the framework been approved". This topic does not approve anything. If the analyst has not yet run the other harness, say the framework is not approved and no sample exists. Do not infer approval from a response.

**A respondent is chatting.** This agent is not published to respondents. If a channel is ever opened by mistake, the only reply is: "This chat does not record a consultation response and does not publish an analysis." Then stop. Do not call the tool on the respondent's behalf.

## What the analyst should see

- How many submissions, and how many unique voices after clustering.
- Which response IDs were redacted, by type, not by raw value.
- Which response IDs were flagged for an instruction aimed at the tool.
- Whether the export is stale.
- A line that no theme has been coded, nothing was published, and nothing was sent.

## Licensing

The harness overview points to a separate licensing page for the standard harness and does not set a price. Confirm it in the tenant. No figure is stated here. See [../docs/harness-comparison.md](../docs/harness-comparison.md).
