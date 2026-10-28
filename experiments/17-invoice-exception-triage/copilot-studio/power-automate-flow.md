# Flow that calls the triage

The standard-harness topic calls one flow. The flow calls `triage()` and returns JSON. It does not post to a ledger.

## Shape

1. Trigger: the Copilot Studio topic, with the case JSON and the as-of date the reviewer typed.
2. Action: run the Python, or an internal HTTP call that runs the same function, with Experiments 12 and 08 beside it. No key in the topic text.
3. Return the JSON unchanged.
4. Stop. There is no Dataverse write, no finance connector, and no email.

## What the flow must not do

- Parse the invoice itself and skip `triage()`.
- Set `synthetic` to true when the caller did not.
- Pass `pay`, `post`, `hold`, or `bank_details_changed`.
- Call `record_ap_reviewer_decision` or `record_bank_route`.
- Write the draft to an accounts-payable system.

A connector added later for a finance system, a mailbox, or a supplier bank master would be a manifest change, not a setting on this flow. Power Platform DLP should block those connectors for this agent. This starter does not create the policy.
