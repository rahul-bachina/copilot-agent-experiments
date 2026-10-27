# Power Automate flow

One flow. It calls the Python front door and returns JSON. It does not write a row and it does not send a message.

## Trigger

The Copilot Studio topic, after the adviser has supplied the enquiry and the as-of date. Not a resident webhook. Not a mailbox.

## Steps

1. Receive `enquiry` and `as_of`. Reject the call if `enquiry.synthetic` is not true. Do not log the text.
2. HTTP POST to the internal API that imports `triage()`. Use a managed identity if the platform allows it. A secret, if one is required, comes from Key Vault. This repository does not create that secret.
3. Return the JSON to the topic unchanged.

## Not in the flow

- Dataverse create or update.
- Outlook, SMS, or Teams send.
- A payment connector.
- A housing, council tax, or social-care connector.
- An approval action whose outcome is "send" or "create case".

If a later design adds any of those, update `agent-manifest.yaml` first. This file does not authorise that change.

## DLP

A deployment DLP policy should block the connectors listed above. This starter has no connector to block. The policy is the backstop if someone adds one. It is not applied in this repository.
