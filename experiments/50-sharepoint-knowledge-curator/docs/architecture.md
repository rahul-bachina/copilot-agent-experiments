# Architecture

The site owner pastes one synthetic snapshot. Either Copilot Studio harness calls `src/curate.py`. The core calls Experiment 12, Experiment 08, and Experiment 49 on visible text, and Experiment 44 when the snapshot includes queries. Hidden items are counted and not read. The draft comes back with proposals, evidence, and confidence. `human_approval` is null.

The site owner reviews the human queue, then approves, rejects, or defers each metadata or publishing proposal. A stale pin, or a snapshot outside the section 46 code, has to be acknowledged before a publishing proposal can proceed. The stub runs only after approval and does not call SharePoint or Microsoft Graph.

Deleting, unpublishing, moving, and changing permissions are not tools of the agent. The site owner does those, if at all, in the organisation's own process.

```text
Site owner
    |  synthetic snapshot and as-of date
    v
Either harness (standard topics, or GitHub Copilot harness skills)
    |
    v
src/curate.py
    |-- visible text only --> Experiment 12 intake
    |-- visible text only --> Experiment 08 propose
    |-- reduced matching text --> Experiment 49 classify_record
    |-- non-queued pages, if queries exist --> Experiment 44 detect_gaps
    v
Draft JSON. human_approval is null.
    |
    v
Site owner reviews the queue, then approves named proposal ids
    |
    v
Stub receipt. applied_in_tenant is false.
```

The picture is `architecture_diagram.png`, drawn by `generate_diagram.py`. Matplotlib is used only to draw it. It is not a runtime dependency.
