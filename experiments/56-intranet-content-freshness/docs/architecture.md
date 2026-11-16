# Architecture

The content owner supplies one synthetic inventory and an as-of date. If the inventory names linked files, a separate location selection can be supplied for Experiment 55. The Python core returns a report. `human_approval` is null.

The content owner then approves, rejects, or defers named task ids. That decision is a separate object. Only after `approve_tasks` does the core record JSON stubs. Those stubs are not Planner tasks and not Power Automate approvals.

```
inventory + as-of date
        |
        v
review_inventory()  -->  report, proposed tasks, human queue
        |
        |  human_approval is null
        v
record_approval()   -->  content owner, named task ids
        |
        v
create_approved_tasks()  -->  JSON stubs, executed false
```

Pages the user cannot read never enter the report as titles. Higher markings, legal holds, safeguarding cues, and unparseable fields enter the human queue and do not become routine tasks. A broken link on an otherwise ordinary page can still be a task, and the unparseable field still blocks approval until the queue is reviewed.

The diagram is `architecture_diagram.png` in this folder. The docs site copies it at build time. Do not commit a second PNG.

## What a later deployment would call, and what this starter does not call

SharePoint `sitePage` properties opened on 16 November 2026 include title, name, description, contentType, createdDateTime, lastModifiedDateTime, pageLayout, publishingState, promotionKind, and webUrl. They do not include a content owner, a review interval, a last-reviewed date, or page views. Those are starter fields. This core does not call Graph. `graph_called` and `sharepoint_called` stay false.

`POST /planner/tasks` was read. Delegated Tasks.ReadWrite and application Tasks.ReadWrite.All were the least-privileged permissions on that page. `planId` has to be an existing plan. This core sets `planId` to null and `called` to false.

Power Automate "Start and wait for an approval", type "Approve/Reject - First to respond", was read. Approvers are notified. Flows are saved in Dataverse. The approvals connector is a standard connector. This core does not start a flow. A production flow, if an organisation built one, would notify only the named content owner. It would not message other staff. That flow is not in this repository.

Copilot Studio standard harness topics are the prose in `copilot-studio/`. The Microsoft Copilot harness skills are under `skills/`. See `harness-comparison.md` for the naming limit.
