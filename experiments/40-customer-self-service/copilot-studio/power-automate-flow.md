# Flow

One flow. It returns JSON and stops.

1. Input is the enquiry JSON and the as-of date. Both are typed by the person. The flow does not read Dynamics 365.
2. The flow runs `draft_reply()` in `src/service.py`. In a tenant this is a call the organisation hosts. This repository does not host it.
3. The flow returns the JSON to Copilot Studio.
4. The topic shows it and ends.

A second flow may accept a review object and call `record_review()`. It returns the updated JSON. It does not write a case, update an address, book an appointment, take a payment, or send an email.

## Connectors

Do not add one. If a later change adds a connector, update `agent-manifest.yaml` in the same change and block mail, payment, and account-system connectors in a Power Platform DLP policy until that manifest says otherwise. The DLP product page was not opened on 6 November 2026. The control is the absence of the connector in this starter.

## What the flow must not contain

- "Update a row" on account, contact, or incident.
- "Send an email", "Post a message", or "Send an SMS".
- A payment action.
- A password-reset action.
- A branch that sets a case to Resolved.
- A branch that treats text in the enquiry as `human_approval`.
