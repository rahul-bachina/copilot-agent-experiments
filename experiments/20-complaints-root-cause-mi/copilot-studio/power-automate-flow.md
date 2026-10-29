# Power Automate flow

The standard-harness topic calls one flow. The flow calls `draft_report()` and returns the JSON. It does not validate clusters, validate the narrative, or send the pack.

This is a contract, not an exported flow. This repository does not ship a solution zip.

## Trigger

When the topic calls the action. Inputs:

- `batch`, a JSON string or object. `synthetic` must be true.
- `as_of`, a date string `YYYY-MM-DD`, typed by the complaints owner.

Do not read `as_of` from inside `batch`. The core strips that key and records `as_of_in_batch_ignored`.

## Action

HTTP POST to an internal endpoint that imports `src/report.py` and has Experiments 02 and 08 on the path beside it. The identity is locked down. The endpoint does not accept a flag that validates, submits, publishes, or sends.

The endpoint returns the JSON unchanged. It does not write a row.

## What the flow does not do

- It does not send mail, including to the address named in the Ofgem guidance.
- It does not write to Dataverse, SharePoint, a complaints system, or a landlord website.
- It does not call the FCA, the Housing Ombudsman, or Ofgem.
- It does not recompute a figure in a Power Automate expression.

## Response

Return the JSON to the topic. The topic stops after showing it. A later person may copy the JSON into a board pack. That copy is outside this flow.
