# Power Automate flow

A sketch of the one flow the standard-harness topic calls. It is not an exported solution, and it has not been imported into a tenant.

## Trigger

When the Copilot Studio topic calls the flow. The topic has already collected `batch` and `as_of`.

## Steps

1. Receive `batch` (string) and `as_of` (string). Do not add a step that reads a mailbox or a SharePoint library to find more files.
2. Call the internal HTTP endpoint that runs `python src/intake.py` with that JSON and that date. The identity on the action can call that endpoint and nothing else.
3. Return the response body to the topic.

There is no condition that writes a row when `files_confirmed` is true. `intake()` does not set that field. There is no condition that sends mail when `prompt_injection.detected` is true. The topic shows the flag.

## What this flow does not include

- A Dataverse "add a new row" action.
- A SharePoint "create file" or "update file" action.
- An Outlook or Teams "send" action.
- An AI Builder model. Document class and the stale comparison stay in `src/intake.py`. Azure Document Intelligence was read on 27 October 2026 and is not called from this flow. See [../docs/foundry.md](../docs/foundry.md).
- A connector to Experiment 08 as a separate service. `intake()` calls `propose()` in-process.

## If the endpoint is down

The topic stops. It does not classify the file itself and it does not tell the user the batch was accepted.

## Data loss prevention

A deployment that adds a mail, SharePoint, or Dataverse connector later should be blocked by a Power Platform DLP policy until the manifest is changed in the same change. This repository does not create that policy. The product page for DLP was not opened on 27 October 2026.
