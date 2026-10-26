# Power Automate flow

One flow. It runs the checklist and returns JSON to the Copilot Studio topic. It is the Power Platform part of this starter. It is a design note, not an exported solution.

## Trigger

Copilot Studio calls the flow. There is no trigger on a mailbox, a Travel Rule gateway, or a blockchain feed. An analyst starts the topic.

## Inputs

| Name | Type | Notes |
|---|---|---|
| `transfer_json` | String | The record the analyst pasted. The flow does not edit it. |
| `as_of` | String | `YYYY-MM-DD`. |

The flow does not read `analyst_decision` from the topic. If that field is present in the JSON, the Python core strips it. The flow does not put it back.

## Steps

1. HTTP action to the internal API that imports `src/triage.py`. Managed identity. No key in the flow definition.
2. Parse the JSON response.
3. Respond to Copilot Studio with the body unchanged.

There is no step that writes Dataverse, sends mail, calls a wallet, or posts to a counterparty. There is no condition of the form "if proposed hold, then hold the transfer". `proposed` is a sentence for the analyst. It is not a branch the flow may take.

## If the API refuses the record

The core returns `label` of `REFUSED` and exit code 2 when `synthetic` is not true. The topic shows the refusal. The flow does not retry with the flag changed.

## Failure

If the HTTP action fails, the topic says the checklist did not run. It does not invent categories. It does not tell the analyst the transfer is clear.

## DLP

Put the HTTP connector in a policy the firm's Power Platform administrator already uses. Do not add the Outlook, Teams send, or a custom Travel Rule connector to this flow. Adding one is a manifest change, not a convenience.
