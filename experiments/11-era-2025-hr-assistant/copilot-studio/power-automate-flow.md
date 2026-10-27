# Power Automate flow

A description of the one flow the standard-harness topic calls. It is not an exported solution.

## Review pack

Trigger: the Copilot Studio topic, after the HR lead has supplied a pack and an as-of date.

Action: HTTP call to the hosted `review()` function. The request body is the pack and the as-of date. The response is the JSON. The flow returns that JSON to the topic and ends.

The flow does not:

- create or update a Dataverse row
- write to SharePoint, including a policy library
- send mail or a Teams message
- call the Acas helpline
- record a training attestation
- branch on `compliance_conclusion`, which is null

Connector set: the HTTP action to the employer's own host, and nothing else. A Power Platform DLP policy should block mail and HR-system connectors for this environment. This repository does not create that policy.

## Training attestations

The catalogue mentions Power Automate for training attestations. Recording that someone completed training is a write against the employer's own system. Writes are disabled in `agent-manifest.yaml`. This starter does not include an attestation flow. If an employer adds one later, a person confirms the row, the agent cannot call the flow, and the manifest is updated first.
