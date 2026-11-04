# Power Automate flow

The flow calls `draft_case()` and returns JSON to the topic. That is its only job.

## Shape

1. Trigger: the Copilot Studio topic, with the case object and the as-of date.
2. Action: HTTP request to the internal host that imports `draft.py`, with Experiments 15, 12, and 08 on the same machine. The identity can call that host and nothing else.
3. Response: the JSON body, unchanged, back to the topic.

## What not to add

Do not add a Dataverse row, an email, a Teams message, an HR-system update, or an approval action inside this flow. The HR officer's confirmation happens outside the agent. A flow that recorded "confirmed" would be a different system, and it would need a new manifest first. This starter does not include it.

Do not log the request body. The narrative may contain special-category data. The draft already omits it.

## Connectors

Power Platform DLP should block mail and HR connectors on this environment. That control is described in [../docs/security-and-permissions.md](../docs/security-and-permissions.md). It is not configured here.
