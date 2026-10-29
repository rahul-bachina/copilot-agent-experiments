# Power Automate flow

A build note. This folder does not contain an importable solution.

## Shape

1. Trigger: the Copilot Studio topic, with the case JSON and the as-of date the analyst typed.
2. Action: HTTP call to the internal host that runs `investigate()`. The host has Experiments 04, 08, 10, 12, and 16 on disk. The identity is locked to that host.
3. Return the JSON to the topic. Stop.

## What the flow does not contain

- A connector to the NCA SAR Portal.
- A connector that sends email, Teams, or SMS to a customer.
- A chain node, a blockchain-analytics vendor, or a wallet.
- A Dataverse, SharePoint, or case-system write.
- A branch that sets `mlro_decision`, `sar_filed`, or a glossary code.
- A branch that drafts customer-facing text when `customer_facing.text` is null.

If a later editor adds one of those connectors, the flow no longer matches `agent-manifest.yaml`. Remove it.

## Failure

If the host returns the refusal object (`label` `REFUSED`, exit path for a record that is not synthetic), show that object and stop. Do not retry with `synthetic` forced to true.
