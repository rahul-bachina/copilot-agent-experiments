# Power Automate flow

A sketch, not an exported flow.

1. Trigger: the Copilot Studio topic, with the brief JSON, the as-of date, and the optional inventory or manifest.
2. HTTP action: POST those fields to the internal host that runs `assess()`. Use a managed identity. Do not put a secret in the flow definition.
3. Return the JSON to the topic.
4. Stop.

Do not add a Dataverse row, an email, a DPIA-register update, or an approval action inside this flow. The privacy officer's approval happens outside the agent. A flow that recorded "approved" would be a different system, and it would need a new manifest first. This starter does not include it.

The host must be able to import Experiment 08. If that folder is missing, `assess()` refuses to invent a replacement. The address `dpiaconsultation@ico.org.uk` is quoted in the draft so the boundary is visible. It is not a recipient of this flow.
