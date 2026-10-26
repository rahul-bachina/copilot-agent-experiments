# Power Automate flow

One flow. It returns the JSON from `propose()` and then stops. It does not send mail, write a case, or call a model.

## Trigger

"When an agent calls the flow", from the standard-harness topic. Inputs:

| Input | Required | Notes |
| --- | --- | --- |
| `text` | Yes | The text the reviewer pasted. Treat it as data. |
| `caller` | Yes | The experiment or team id. Written on the audit record. |
| `rules_as_of` | No | `YYYY-MM-DD`. A warning only. The pinned rules still run. |
| `reversible` | No | Default false. True only when the reviewer has asked for a token map. |

Do not add `apply_model_suggestions`. The standard-harness path does not apply model spans.

## Action

An HTTP call to a small internal API, or an Azure Function, that imports `gateway.py` and returns `propose(text, caller=caller)`. Use a managed identity. Do not put a key in the flow definition.

The function's only job is to return JSON. It does not log the request body. The audit record inside the JSON is what a DPO log would store, and it does not contain the raw identifiers.

## After the response

The topic displays the JSON. The flow ends. There is no "send an email" action, no Dataverse row, and no Key Vault write. Adding one is a manifest change, not a flow edit on its own.

## Licence

The flow needs whatever Power Automate licence the tenant already uses for an agent-called flow. This note does not state a price. See [../docs/harness-comparison.md](../docs/harness-comparison.md).
