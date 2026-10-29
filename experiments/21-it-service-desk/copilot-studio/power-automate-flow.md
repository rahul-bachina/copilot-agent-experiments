# Power Automate flow

One flow. It calls the Python desk and returns JSON. It does not write a row, call an identity system, or send a message.

## Trigger

The Copilot Studio topic, after the person has supplied the ticket and the as-of date. Not a mailbox. Not a phone webhook.

## Steps

1. Receive `ticket` and `as_of`. Reject the call if `ticket.synthetic` is not true. Do not log the text.
2. HTTP POST to the internal API that imports `triage()`. Use a managed identity if the platform allows it. A secret, if one is required, comes from Key Vault. This repository does not create that secret.
3. Return the JSON to the topic unchanged.

A second flow may call `record_review()` when the person supplies a separate review object. That flow still returns JSON. It does not call Microsoft Entra.

## Not in the flow

- Dataverse create or update.
- Microsoft Entra password reset, MFA change, or group write.
- Intune, or any remote wipe or device action.
- Outlook, SMS, or Teams send.
- A purchasing connector.
- An approval action whose outcome is "reset", "grant", or "execute".

If a later design adds any of those, update `agent-manifest.yaml` first. This file does not authorise that change.

## DLP

A deployment DLP policy should block the connectors listed above. This starter has no connector to block. The policy is the backstop if someone adds one. It is not applied in this repository. The product page for Power Platform DLP was not opened on 29 October 2026. Treat the current policy controls as unverified here.
