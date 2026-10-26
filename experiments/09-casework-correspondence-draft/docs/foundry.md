# Microsoft Foundry

This is a path for a team that wants a model to help read the letter, with the clock and the lines remaining in code. It is not a deployed project. No Foundry resource is created by this repository.

Use the name Microsoft Foundry. The retired product name is not used here.

The DfE Correspondence Drafter record, opened on 26 October 2026, describes that department's own tool using a retrieval index over briefing packs. This starter is not that tool. On the Copilot Studio agents page retrieved the same day, Azure AI Search is not supported on the GitHub Copilot harness. Do not design this experiment's GitHub Copilot harness around an Azure AI Search index. The citable text is the output of `src/lines.py`.

## What the model is for

The model may:

- quote the letter and propose a channel, for the author to confirm
- point at asks the keyword matcher might have missed, without stating a position on them
- repeat a line the Python matcher has already marked current, with its id
- repeat a gap the matcher has already raised

The model may not:

- calculate a reply date
- confirm the channel or the target
- approve a recipient, or copy an address out of the letter into the recipient field
- write a policy sentence that is not a verbatim current line
- paste a withdrawn, overdue, or future line
- decide an exemption, a complaint outcome, or that no reply will be sent
- send anything, or write a case
- say the ATRS note has been submitted

## Suggested shape

One orchestration, not a free chat.

1. **Inputs, typed by the author.** Letter text, receipt date, as-of date, regime, and a target. Confirmations are separate booleans a person sets.
2. **Clock and lines, in Python.** The orchestration calls `calculate_casework_sla` and `match_lines`. The model does not see a tool that can do anything else.
3. **Draft call, optional.** A completion that receives the matcher JSON and is told to paste cited line text unchanged and to say "no position is stated" for every gap. If it adds a sentence that is not in that JSON, `validate_draft` rejects the result. Temperature low. The letter is a user message, not part of the system instructions.
4. **Author screen.** Show the proposal, the line ids, the gaps, the clock, and the draft. Nothing is filed until the author copies it into the case system themselves.

The mock drafter in `src/draft.py` is the stand-in for the reading step when no credentials are present. Do not quote its smoke-test agreement as a Foundry score.

## Deployment choices to confirm

These are assumptions, also listed in `agent-manifest.yaml`.

- Region: UK South or UK West.
- The deployment is not used to train on the organisation's correspondence. Confirm the current Foundry data-use terms at build time rather than relying on this note.
- Identity: a managed identity for the orchestration, not a key in a notebook. If a key is unavoidable, keep it in Key Vault.
- Content filters and prompt shields: turn them on, and still keep the "no send, no write" tool list. The portal name of prompt shields was not re-opened on 26 October 2026. Filters are not the control that stops a send. The missing tool is.
- Log the model deployment name and version, the library id, the clock inputs, and the author's later edits. Do not log the letter in an application trace.

## Evaluation

`eval/evaluate.py` is a mock smoke test of 22 synthetic letters. A real run would point the same fixtures at the Foundry deployment, keep the clock and the lines in code, and publish the report with the deployment name. Until that happens, say "not run". The fixtures include injection, stale lines, information-rights letters, and immediate-risk wording so that a later live run has something to fail against.
