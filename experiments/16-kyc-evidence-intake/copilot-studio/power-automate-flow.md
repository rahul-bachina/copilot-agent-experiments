# Power Automate flow

A sketch, not an exported flow.

1. Trigger: the Copilot Studio topic, with the customer-file JSON and the as-of date.
2. HTTP action: POST those two fields to the internal host that runs `review()`. Use a managed identity. Do not put a secret in the flow definition.
3. Return the JSON to the topic.
4. Stop.

Do not add a Dataverse row, an email, an onboarding update, or an approval action inside this flow. The reviewer's confirmation happens outside the agent. A flow that recorded "approved" would be a different system, and it would need a new manifest first. This starter does not include it.

The host must be able to import Experiment 12 and Experiment 08. If either folder is missing, `review()` refuses to invent a replacement.
