# Power Automate flow

A sketch, not an exported flow. The flow returns JSON. It does not update a claims system and it does not send mail.

1. Trigger: the Copilot Studio topic, with `pack` and `as_of`.
2. HTTP action: POST those two fields to an internal endpoint that runs `triage()` with Experiments 12, 08, and 29 on the same machine. The identity can call that endpoint and nothing else.
3. Return the JSON body to the topic.
4. Stop. No Dataverse create. No Outlook send. No claims-system connector.

If the endpoint returns a non-zero exit, show the error line and stop. Do not retry with `synthetic` set to true in order to force a result. Do not drop a prohibited flag and try again.

The endpoint refuses a pack that is not marked synthetic. It exits 2, with no JSON body, for `--accept-claim`, `--decline-claim`, `--settle-claim`, `--tell-customer`, `--write-claims-system`, and `--approve-thresholds`.
