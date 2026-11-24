# Architecture

The starter is a deterministic Python core with two Copilot Studio harness guides in front of it. Both harnesses call the same functions. Neither submits an application.

```
Pinned brief, charity profile, monitoring rows, directory
        |
        v
prepare_application()  ---- Experiment 12 intake (files not confirmed)
        |                  Experiment 08 counts (values not stored)
        v
Draft JSON: answers, impact report, gaps, checklist, deadline, hash
        |
        +-- distress or safeguarding --> record_route_seen()  (no staging)
        |
        v
record_applicant_approval()  only if the directory applicant and the hash match
        |
        v
In-memory synthetic staging row
        |
        x  submit, contact a funder, send  (not functions that succeed)
```

The question date is an argument. The core does not call `date.today()`. A deadline in the past relative to that date is flagged. An unreadable date stays unreadable.

The content hash covers the answers, the impact report, the eligibility reading, the checklist, the deadline plan, the claims, the marking, the legal hold, the retention labels, and whether the route has been seen. Changing any of those after the hash was shown makes the approval fail. An approval object that names a different applicant, or a trustee, or a guest, fails. A string `"true"` is not the boolean true.

Case-note bodies are counted for personal data and then dropped. The package cites row ids. A SECRET cover found in the page text is kept as the higher marking even when the metadata says OFFICIAL. The body of that page is not copied when it is above the applicant's directory clearance.

## Diagram

The rendered picture is [architecture_diagram.png](architecture_diagram.png). It shows four stages: pinned sources, either harness, the draft package, and the human approval. Submit, contact, and send are drawn as actions that are not tools.
