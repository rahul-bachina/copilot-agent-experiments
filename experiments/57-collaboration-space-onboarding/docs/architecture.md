# Architecture

Autonomy **A1**. Catalogue **M010**. The workspace owner approves membership and internal links. The sample does not call Microsoft Graph.

```
Joiner or project member
        |
        v
Synthetic space + membership request
        |
        v
prepare_onboarding()
  strip approval keys
  negation-aware justification
  higher of metadata and content
  least privilege, guest policy
  Experiment 55 key documents
  Experiment 51 channel digest (does not approve membership)
  Experiment 03 unapproved manifest draft
        |
        v
Draft JSON. human_approval is null. applied is false.
        |
        v
Workspace owner, separate approval object
  approve / defer / refuse
  owner_rights_approved boolean, only if the proposal is owner
  guest_access_approved boolean, only if the policy is owner_approval
  stale_seen, safeguarding_reviewed, links_approved
        |
        v
apply_membership()
  simulated POST /groups/{id}/members/$ref
  and, for an approved owner, POST /groups/{id}/owners/$ref
  live_graph_called false
```

External sharing, a live Graph call, and a private-channel member call are not on this path. A sentence in the request is not on the approval path.

The rendered picture is [architecture_diagram.png](architecture_diagram.png). Regenerate it with `docs/generate_diagram.py` where matplotlib is installed. The runtime does not need matplotlib.
