# Power Automate flow

A build note. This folder does not contain an importable solution, and it does not provision a flow.

## Shape

1. Trigger: the Copilot Studio topic, with the proposal JSON and the as-of date the team typed.
2. Action: HTTP call to the internal host that runs `classify()`. The host has Experiments 03, 14, and 19 on disk. The identity is locked to that host.
3. Return the JSON to the topic. Stop.

## What the flow does not contain

- A connector that creates, publishes, or provisions a Copilot Studio agent.
- A connector that creates a cloud flow, a Dataverse table, or a Microsoft Foundry resource.
- A connector that sends email, Teams, or SMS, including to an ATRS mailbox.
- A Dataverse, SharePoint, or case-system write.
- A branch that sets `approved`, `use_case_approved`, `provisioned`, or `governance_decision`.
- A branch that sets `suggested_autonomy` to A3, or that sets `dpia_required`.

If a later editor adds one of those connectors, the flow no longer matches `agent-manifest.yaml`. Remove it.

## Failure

If the host returns the refusal object (`refused` true, the path for a proposal that is not synthetic), show that object and stop. The label is still DRAFT FOR THE GOVERNANCE TEAM. Do not retry with `synthetic` forced to true. Do not copy the refused body into the chat.
