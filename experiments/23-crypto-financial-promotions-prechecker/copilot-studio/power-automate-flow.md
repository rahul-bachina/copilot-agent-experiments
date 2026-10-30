# Power Automate flow

A build note. This folder does not contain an importable solution.

## Shape

1. Trigger: the Copilot Studio topic, with the promotion JSON and the as-of date the reviewer typed.
2. Action: HTTP call to the internal host that runs `precheck()`. The host has Experiments 03, 04, and 08 on disk. The identity is locked to that host.
3. Return the JSON to the topic. Stop.

## What the flow does not contain

- A connector to a CMS, an app store, or a social network.
- A connector that sends email, Teams, or SMS.
- The Financial Services Register or FCA Connect.
- A Dataverse, SharePoint, or approvals-register write.
- A branch that sets `s21_approver_decision`, `promotion_approved`, or `published`.
- A branch that drafts replacement copy when `rewrite_drafted` is false.

If a later editor adds one of those connectors, the flow no longer matches `agent-manifest.yaml`. Remove it.

## Failure

If the host returns the refusal object (`refused` true, for a record that is not synthetic), show that object and stop. Do not retry with `synthetic` forced to true. Do not echo the body.
