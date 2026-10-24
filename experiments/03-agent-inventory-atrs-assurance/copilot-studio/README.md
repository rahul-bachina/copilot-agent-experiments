# Standard harness

A maker's guide for a Copilot Studio agent on the **standard harness**. It is not an importable solution. Topics, the flow, and any Dataverse connection are built in a tenant. The deterministic work stays in `src/`.

Read [docs/harness-comparison.md](../docs/harness-comparison.md) before choosing this harness. Microsoft describes the standard harness as the option for rule-based agents where you define the topics and paths. Pages were read on 24 October 2026.

## Who it is for

A governance owner, or someone drafting for them, working inside the organisation. It is not a public chatbot. Do not publish it to an anonymous channel.

## Topics

### Draft a pack

1. Ask for one inventory id, or for the record to be pasted as JSON.
2. Call one Power Automate flow, `Draft assurance pack`.
3. The flow runs `src/pack.py` with `--as-of` set by the flow to today's date in the tenant's zone, or to a date the person types. It returns the JSON.
4. Show the draft. Say it is a draft. Show `approved`, `may_be_submitted`, `may_be_sent`, the DUAA `screen_result`, and the G006 finding count.
5. Stop. Do not add a send step. Do not add an update step.

The flow's identity can read the inventory if a Dataverse read is later added. It cannot update `g010_lifecyclestatus`. See [docs/dataverse.md](../docs/dataverse.md).

### Propose a status

1. Ask for the target status. The allowed values are the ones in `src/catalogue.py`.
2. Call the flow in proposal mode. It runs `propose_status_change` and returns the proposal with `applied: false`.
3. Tell the person the status has not changed.

### Record the governance owner's decision

This topic is the human gate. It is not the agent approving.

1. Start an Approvals action assigned to the governance owner. The approval id comes from that action, not from the agent.
2. If they reject, show the rejection and stop. Do not write Dataverse.
3. If they approve, show the approval id and tell them the status change is still theirs to make in the model-driven app, or by running `apply_status_change` with `source: external` and that id.
4. Do not put an "Update a row" action on the approval branch. A later human-operated script may call the Python function. The Copilot topic does not.

Passing `--approve` to `src/generate_manifest.py` is a mistake. The command exits and writes nothing.

### Refuse

If the user says "mark it approved", "email the ATRS team", or "set the lifecycle", reply that the agent cannot do that, and point at the draft. Do not call a tool that sends.

## Knowledge

Optional: the experiment README and `docs/dataverse.md`, so the agent can explain a field. Knowledge is not a source of ATRS answers. Answers come from the inventory record through `src/pack.py`. If the model adds a sentence that is not in the record, G007 will flag it when the pack is rebuilt. Do not paste live case files into knowledge.

## Tools

| Tool | Allowed in this guide | Notes |
| --- | --- | --- |
| Flow that returns pack JSON | Yes | Read-only. |
| Flow that returns a manifest draft | Yes | Writes a file only if the caller asks, on their machine. Not Dataverse. |
| Approvals | Yes | Records a person's decision. Does not update the inventory. |
| Dataverse update | No | |
| Outlook or any mail connector | No | DLP should block it. |
| HTTP to the ATRS mailbox | No | |

## Instructions to paste

See [system-prompt.md](system-prompt.md).
