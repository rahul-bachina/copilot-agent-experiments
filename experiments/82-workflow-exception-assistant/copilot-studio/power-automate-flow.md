# Flow note

This note is not a flow. Nothing in this folder calls Power Automate, retries a run, cancels a run, or writes a record.

A production design would keep the Python core as the only place that classifies a code and checks the owner's decision. A flow action that retries, cancels, or updates a row would be a different system, with its own approval, and it is not built here.

The Microsoft Copilot harness page says that harness retries and finds alternative paths. This starter does not turn that on. `retry_run`, `cancel_run`, `edit_record`, and `rerun_flow` raise.

The sample runs offline on `examples/sample_request.json`.
