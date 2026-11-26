# Microsoft Copilot harness

The skills in `skills/` are the layout the common brief calls the GitHub Copilot harness. The harness overview opened on 26 November 2026 names this runtime the Microsoft Copilot harness. It does not use the words "GitHub Copilot harness". See [harness-comparison.md](harness-comparison.md).

Each skill has a single-line `description` that says when to use it. The files do not list trigger phrases and do not assign weights.

| Skill | Calls | Gate |
| --- | --- | --- |
| `assemble-approval-pack` | `assemble_pack` | None to read. The decision is separate. |
| `check-evidence-currency` | The evidence block already on the draft | None. Conflicting values are not chosen. |
| `draft-cover-note` | The cover note already on the draft | None. The approver reads it. |
| `record-route-seen` | `record_route_seen` | The named approver, the current hash, and a route that needs a person. |
| `record-approver-decision` | `record_approver_decision` | The named approver, not the requester, and the agent-held hash. |

The same deterministic core, the same manifest, and the same tests back this harness and the standard-harness topic guide. A skill must not add a tool that signs, submits, pays, or sends.
