# Power Automate flow

One flow. It runs the draft and returns JSON to the Copilot Studio topic. It is a design note, not an exported solution.

The catalogue names Power Platform for the completion update. Updating a production work order is a write against the organisation's own system. The production write is disabled in `agent-manifest.yaml`. This starter does not include that flow.

If an organisation adds a write later, a person confirms each field, the agent cannot call the flow until the manifest is updated, and the flow still must not close the job, raise a charge, order parts, or contact the customer. This folder does not include that flow.

The flow that does exist here only returns the JSON. `human_approval` is null. `stub_write.executed` is false. A second, separate call to `record_review` can approve fields. A third call can stub-write fields that were approved on the second call. Those calls are not connectors. They are the same Python functions.

Do not add a Dataverse row, a Dynamics 365 work-order update, an invoice action, a parts order, or a mail action to this flow.
