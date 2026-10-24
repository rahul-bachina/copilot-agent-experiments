# Microsoft Foundry implementation

This is a path for a team that wants the extraction and the draft acknowledgement from a model, with the DISP clock remaining in code. It is not a deployed project. No Foundry resource is created by this repository.

Use the name Microsoft Foundry. The retired product name is not used here.

## What the model is for

The model may:

- quote the complaint and propose whether it meets the Handbook glossary definition of a complaint
- propose a product and a root cause from the firm's own taxonomy
- propose a severity, for the handler to change
- flag a vulnerability characteristic under FG21/1 (health, life events, resilience, capability) and quote the words, without calling the customer vulnerable
- propose which Consumer Duty outcome the facts appear to touch (PRIN 2A.3 to PRIN 2A.6)
- draft an acknowledgement that copies dates from the clock tool

The model may not:

- calculate a DISP date
- decide the route (general, PSD, EMD, mixed) on its own and then treat that as confirmed
- uphold, reject, close, or set a redress figure
- say the firm has breached the Consumer Duty
- send anything
- write a Dynamics 365 record

## Suggested shape

One orchestration, not a free chat.

1. **Inputs, typed by the handler.** Complaint text, receipt date, and optionally a confirmed route, a human flag for exceptional circumstances, and the provider's closed dates.
2. **Extraction call.** One chat completion with a JSON schema. Temperature low. The complaint text is a user message, not part of the system instructions. The system instructions are the ones in [../copilot-studio/system-prompt.md](../copilot-studio/system-prompt.md).
3. **Clock call.** The orchestration code, not the model, calls `calculate_disp_clock`. If the handler has not confirmed a PSD or EMD route, pass `general`. Do not pass `exceptional_circumstances=True` unless a person has set that flag in the UI.
4. **Draft call, optional.** A second completion that receives the clock JSON and is told to paste `operative_final_response_due_on` unchanged. If that field is null, the draft must say the payment-services date is not yet operative. It must not invent a substitute date.
5. **Schema check.** Reject the draft if it contains an uphold, a redress amount, a send, a breach finding, or `customer_labelled_vulnerable: true`. The same checks are in `intake.validate_intake`.
6. **Handler screen.** Show the proposal, the evidence quotes, the clock, and the draft. Nothing is filed until the handler copies it into the case system themselves.

The mock intake in `src/intake.py` is the stand-in for steps 2 and 4 when no credentials are present. Do not quote its smoke-test agreement as a Foundry score.

## Deployment choices to confirm

These are assumptions, also listed in `agent-manifest.yaml`.

- Region: UK South or UK West.
- The deployment is not used to train on the firm's complaints. Confirm the current Foundry data-use terms at build time rather than relying on this note.
- Identity: a managed identity for the orchestration, not a key in a notebook. If a key is unavoidable, keep it in Key Vault.
- Content filters and prompt shields: turn them on, and still keep the "no send, no write" tool list. Filters are not the control that stops a send. The missing tool is.
- Log the model deployment name and version, the clock inputs, and the handler's later edits. Do not log the complaint text in an application trace. The complaint belongs on the case file, under the firm's retention schedule.

## Evaluation

`eval/evaluate.py` is a mock smoke test. A real run would point the same fixtures at the Foundry deployment, keep the clock in code, and publish the report with the deployment name. Until that happens, say "not run". The synthetic fixtures include non-complaints, vulnerability wording, prompt injection, and stale dates so that a later live run has something to fail against.
